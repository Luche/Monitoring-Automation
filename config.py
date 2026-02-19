"""
Configuration for BINUS Monitoring Automation

You can either:
1. Set environment variables (recommended for security)
2. Update the values below directly (not recommended for production)
"""

# Term configuration
# Update this to match current academic term
TERM = "2025, Even Semester"

# Campuses to monitor
CAMPUSES = [
    "Binus Kemanggisan",
    "Binus Alam Sutera"
]

# Credentials (use environment variables instead if possible)
# Set BINUS_USERNAME and BINUS_PASSWORD in your environment
# Or uncomment and fill these (but don't commit to git!)
# USERNAME = "your_email@binus.ac.id"
# PASSWORD = "your_password"
