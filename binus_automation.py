"""
BINUS Academic Services Automation - Lecture Monitoring
Automates lecture monitoring for https://acadservices.apps.binus.ac.id/

Workflow:
1. Login via Microsoft SSO
2. Switch to Staff role
3. Navigate to Lecture Monitoring
4. Filter by term and campus
5. Process each class that needs monitoring
6. Handle pagination
7. Switch campus and repeat
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# JavaScript to execute on monitoring log page
MONITORING_SCRIPT = """
const checkboxes = document.querySelectorAll('input[type="checkbox"].isMonitoring');
checkboxes.forEach(checkbox => checkbox.checked = true);
const textareas = document.querySelectorAll(
    '.CourseLogMessageToLecturer, .CourseLogNotesToLecturer, .AttendanceMessageToLecturer, .AttendanceNotesToLecturer'
);
textareas.forEach(textarea => textarea.value = "ok");
const submitButton = document.querySelector('#btnSave');
if (submitButton) {
    submitButton.click();
} else {
    console.error("Submit button not found!");
}
"""


def login_microsoft_sso(page: Page, username: str, password: str):
    """Handle Microsoft SSO login"""
    print("  Clicking LOGIN button...")
    page.click('text=LOGIN')

    # Wait for email input to appear
    print("  Waiting for email input...")
    page.wait_for_selector('input[type="email"], input[name="loginfmt"]')

    print("  Entering email...")
    page.fill('input[type="email"], input[name="loginfmt"]', username)
    page.click('input[type="submit"], button:has-text("Next")')

    # Wait for password input to appear
    print("  Waiting for password input...")
    page.wait_for_selector('input[type="password"], input[name="passwd"]')

    print("  Entering password...")
    page.fill('input[type="password"], input[name="passwd"]', password)
    page.click('input[type="submit"], button:has-text("Sign in")')

    # Handle "Stay signed in?" dialog
    print("  Waiting for 'Stay signed in?' dialog...")
    yes_button = page.locator('#idSIButton9, input[value="Yes"], input[type="submit"][value="Yes"]')
    yes_button.wait_for(state='visible')
    print("  Clicking 'Yes' button...")
    yes_button.click()

    # Wait for main page to load by checking for "Login As" selector
    print("  Waiting for main page to load...")
    page.wait_for_selector('text=Login As')


def switch_to_staff_role(page: Page):
    """Switch from Lecturer to Staff role"""
    print("  Switching to Staff role...")

    # Wait for and select Staff from dropdown
    page.wait_for_load_state('networkidle')
    page.select_option('select', label='Staff')

    # Wait for page to fully reload after role change
    print("  Waiting for page to reload as Staff...")
    page.wait_for_load_state('networkidle')

    print("  Switched to Staff role")


def navigate_to_lecture_monitoring(page: Page):
    """Navigate directly to Lecture Monitoring page"""
    print("  Navigating to Lecture Monitoring page...")
    page.goto('https://acadservices.apps.binus.ac.id/newStaff/#/Monitoring/LectureMonitoring')

    # Wait for filter page to load
    print("  Waiting for filters page...")
    page.wait_for_selector('text=TERM', timeout=0)


def apply_filters(page: Page, term: str, campus: str):
    """Apply term and campus filters"""
    print(f"  Setting filters - Term: {term}, Campus: {campus}")

    # Wait for filter elements to be visible
    page.wait_for_selector('select', timeout=0)

    # Select term
    print(f"    Setting term to {term}...")
    term_selector = page.locator('text=TERM').locator('..').locator('select')
    term_selector.wait_for(state='visible', timeout=0)
    term_selector.select_option(label=term)

    # Select campus
    print(f"    Setting campus to {campus}...")
    campus_selector = page.locator('text=CAMPUS').locator('..').locator('select')
    campus_selector.wait_for(state='visible', timeout=0)
    campus_selector.select_option(label=campus)

    # Wait 5 seconds before clicking search
    print("    Waiting 5 seconds before search...")
    page.wait_for_timeout(4000)

    # Click SEARCH button
    print("    Clicking SEARCH...")
    page.click('#btnSearch, input[value="Search"]')

    # Wait for results table to appear (this can be very slow)
    print("    Waiting for results table to load...")
    page.wait_for_selector('table tbody tr', timeout=0)
    print("    Results loaded")


def process_monitoring_logs(page: Page, context: BrowserContext) -> int:
    """Process all monitoring logs on current page that need monitoring"""
    monitored_count = 0

    # Wait for table to be loaded
    page.wait_for_selector('table tbody tr')

    # Each page has exactly 10 rows
    MAX_ROWS_PER_PAGE = 10

    for i in range(MAX_ROWS_PER_PAGE):
        try:
            # Get the current row (using nth instead of getting all rows)
            row = page.locator('table tbody tr').nth(i)

            # Check if row exists
            if row.count() == 0:
                break

            # Check if monitoring complete percentage is not 100%
            monitoring_complete = row.locator('td').nth(-1).text_content().strip()

            if monitoring_complete != '' and monitoring_complete != "100.00%":
                print(f"    Row {i+1}: Monitoring at {monitoring_complete}, processing...")

                # Click Monitoring Log button
                monitoring_log_btn = row.locator('a:has-text("Monitoring Log")')

                # Wait for new tab to open
                with context.expect_page() as new_page_info:
                    monitoring_log_btn.click()

                new_page = new_page_info.value

                # Wait for form elements to appear
                print(f"      Waiting for monitoring form...")
                new_page.wait_for_selector('#btnSave')

                print(f"      Executing monitoring script...")
                new_page.evaluate(MONITORING_SCRIPT)

                # Wait for success message
                print(f"      Waiting for 'Data has been saved' message...")
                new_page.wait_for_selector('text=Data has been saved')
                print(f"      ✓ Data saved!")

                # Click OK button to dismiss
                print(f"      Clicking OK button...")
                new_page.click('input[value="Ok"], button:has-text("OK")')

                # Close the tab
                new_page.close()
                monitored_count += 1

                # Wait before processing next row to avoid database overload
                print(f"      Waiting before next row...")
                page.wait_for_timeout(1000)
            else:
                print(f"    Row {i+1}: Already at 100%, skipping")

        except Exception as e:
            print(f"    ⚠ Error processing row {i+1}: {e}")
            continue

    return monitored_count


def has_next_page(page: Page) -> bool:
    """Check if there is a next page by checking row count or all 100%"""
    try:
        # Count actual rows in table
        row_count = page.locator('table tbody tr').count()

        # If less than 10 rows, definitely last page
        if row_count < 10:
            print(f"  Only {row_count} rows found - last page")
            return False

        # If exactly 10 rows, check if all are at 100%
        if row_count == 10:
            all_complete = True
            for i in range(10):
                row = page.locator('table tbody tr').nth(i)
                monitoring_complete = row.locator('td').nth(-1).text_content().strip()
                if monitoring_complete != "100.00%":
                    all_complete = False
                    break

            # If all are 100%, might be last page, but check next button state
            if all_complete:
                return False

        # If we have 10 rows and some need monitoring, there might be next page
        return True

    except Exception as e:
        print(f"  Error checking next page: {e}")
        return False

def go_to_next_page(page: Page):
    """Navigate to next page"""
    print("  Going to next page...")
    page.click('a:has-text("›"), a:has-text("Next"), .pagination .next')

    # Wait for table to reload
    page.wait_for_selector('table tbody tr')

def process_campus(page: Page, context: BrowserContext, campus: str, term: str):
    """Process all monitoring for a specific campus"""
    print(f"\n{'='*60}")
    print(f"Processing Campus: {campus}")
    print(f"{'='*60}")

    apply_filters(page, term, campus)

    page_num = 1
    total_monitored = 0

    while True:
        print(f"\n  📄 Page {page_num}")
        print(f"  {'-'*50}")

        monitored = process_monitoring_logs(page, context)
        total_monitored += monitored
        print(f"  Monitored {monitored} classes on this page")

        # Check for next page
        if has_next_page(page):
            go_to_next_page(page)
            page_num += 1
        else:
            print(f"\n  ✓ No more pages for {campus}")
            break

    print(f"\n  ✅ Campus {campus} complete: {total_monitored} classes monitored across {page_num} page(s)")
    return total_monitored


def main():
    # Configuration
    BASE_URL = "https://acadservices.apps.binus.ac.id/"

    # Get credentials from environment variables (loaded from .env file)
    USERNAME = os.getenv('BINUS_USERNAME')
    PASSWORD = os.getenv('BINUS_PASSWORD')

    # Validate credentials
    if not USERNAME or not PASSWORD:
        print("❌ ERROR: Credentials not found!")
        print("\nPlease create a .env file with:")
        print("  BINUS_USERNAME=your_email@binus.ac.id")
        print("  BINUS_PASSWORD=your_password")
        print("\nOr copy from .env.example:")
        print("  cp .env.example .env")
        print("  # then edit .env with your credentials\n")
        return

    print(f"✅ Credentials loaded for: {USERNAME}")

    # Configuration
    TERM = "2025, Even Semester"  # Change this to current term
    CAMPUSES = [
        "Binus Kemanggisan",
        "Binus Alam Sutera"
    ]

    with sync_playwright() as p:
        # Launch WebKit browser (native macOS support)
        print("🚀 Launching WebKit browser...")
        browser = p.webkit.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the website
            print(f"\n📍 Navigating to {BASE_URL}")
            page.goto(BASE_URL)

            # Wait for LOGIN button to appear
            page.wait_for_selector('text=LOGIN')

            # Step 1: Login via Microsoft SSO
            print("\n🔐 Step 1: Logging in via Microsoft SSO...")
            login_microsoft_sso(page, USERNAME, PASSWORD)

            # Step 2: Switch to Staff role
            print("\n👤 Step 2: Switching to Staff role...")
            switch_to_staff_role(page)

            # Step 3: Navigate to Lecture Monitoring
            print("\n🧭 Step 3: Navigating to Lecture Monitoring...")
            navigate_to_lecture_monitoring(page)

            # Step 4: Process each campus
            print("\n📊 Step 4: Processing monitoring for each campus...")
            total_classes = 0

            for campus in CAMPUSES:
                classes_monitored = process_campus(page, context, campus, TERM)
                total_classes += classes_monitored

            # Final summary
            print(f"\n{'='*60}")
            print(f"✅ AUTOMATION COMPLETE!")
            print(f"{'='*60}")
            print(f"Total classes monitored: {total_classes}")
            print(f"Campuses processed: {len(CAMPUSES)}")
            print(f"Term: {TERM}")
            print(f"{'='*60}\n")

            # Keep browser open for inspection
            input("Press Enter to close browser...")

        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to close browser...")

        finally:
            browser.close()
            print("\n👋 Browser closed. Goodbye!")


if __name__ == "__main__":
    main()
