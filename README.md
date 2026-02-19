# BINUS Lecture Monitoring Automation - Quick Start

## 🎯 What This Does

Automatically monitors lecture attendance for BINUS courses by:
- Logging in via Microsoft SSO
- Switching to Staff role
- Navigating to Lecture Monitoring
- Processing all classes across multiple campuses
- Handling pagination automatically

## 🚀 Quick Start

### 1. Set Up Credentials

Create a `.env` file in this directory:

```bash
cp .env.example .env
```

Then edit `.env` and add your BINUS credentials:

```
BINUS_USERNAME=your_email@binus.ac.id
BINUS_PASSWORD=your_password
```

**Or** set environment variables:

```bash
export BINUS_USERNAME="your_email@binus.ac.id"
export BINUS_PASSWORD="your_password"
```

### 2. Update Configuration

Edit `config.py` if you need to:
- Change the term (currently "2025, Even Semester")
- Modify campus list
- Adjust any other settings

### 3. Run the Automation

Note that this folder is using uv as python dependency manager (https://github.com/astral-sh/uv).
```bash
uv run binus_automation.py
```
If you use normal python, then run the script with:
```bash
python binus_automation.py
```

The browser will open and you can watch the automation run!

## ⚙️ Configuration

### Current Settings

- **Term**: 2025, Even Semester
- **Campuses**:
  - Binus Kemanggisan
  - Binus Alam Sutera

### Changing Settings

Open `binus_automation.py` and look for the `main()` function:

```python
TERM = "2025, Even Semester"  # Change this
CAMPUSES = [
    "Binus Kemanggisan",  # Add/remove campuses
    "Binus Alam Sutera"
]
```

## 🐛 Troubleshooting

### Browser runs too fast
Increase `slow_mo` value in the script (line with `browser = p.webkit.launch(...)`):
```python
browser = p.webkit.launch(headless=False, slow_mo=1000)  # 1 second delay
```

### Timeouts
Majority of the script has no timeouts because slow website. Add timeouts if needed.

### Selectors not working
The website may have changed. You'll need to:
1. Inspect elements in browser
2. Update selectors in the function that's failing

### Run in headless mode
For running without GUI (faster):
```python
browser = p.webkit.launch(headless=True)
```

## 📊 Output

The script will print:
- ✅ Progress for each step
- 📄 Page numbers being processed
- 📊 Number of classes monitored
- 🎉 Final summary

## 🔒 Security

- Never commit `.env` file or credentials
- Use environment variables in production
- The `.gitignore` already excludes `.env` files

## 📝 Notes

- The script keeps the browser open at the end - press Enter to close
- Each class monitoring opens a new tab temporarily
- Loading can be slow - this is normal for the BINUS system
