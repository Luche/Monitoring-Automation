# BINUS Lecture Monitoring Automation

This tool fills in **Lecture Monitoring** for you. It goes through every class that is not at 100% yet, on every page and for every campus you choose. You start it and watch it work.

**You need:** a Mac, Windows or Linux computer, an internet connection, and your BINUS staff email and password.

You **don't** need to install Python or anything else. The start file sets everything up the first time you run it.

---

## Step 1: Download

1. Download the ZIP: **https://github.com/Luche/Monitoring-Automation/archive/refs/heads/main.zip**
2. Unzip it:
   - **Windows:** right-click the ZIP, choose **Extract All…**, then click **Extract**.
   - **Mac:** double-click the ZIP.
3. You now have a folder called `Monitoring-Automation-main`. You can move it anywhere, for example to Documents.

> ⚠️ **Windows:** always extract the ZIP first. Running the files from inside the ZIP will not work.

---

## Step 2: Choose the term and campus

Open the file `config.py` in a plain text editor:

- **Windows:** right-click `config.py`, choose **Open with**, then **Notepad**.
- **Mac:** right-click `config.py`, choose **Open With**, then **TextEdit**.

It looks like this:

```python
TERM = "2025, Compact Semester"

CAMPUSES = [
    "Binus Kemanggisan",
]
```

- Change the words **between the quote marks**. They must match the **TERM** and **CAMPUS** dropdowns on the BINUS Lecture Monitoring page exactly.
- To add another campus, copy a whole line (including its quotes and comma), paste it below, and change the name.
- Save the file and close it.

> 💡 Don't type new quote marks yourself. Copy existing ones instead, because TextEdit on a Mac can turn `"` into curly quotes `“ ”`, which breaks the file.

---

## Step 3: Start it

| Your computer | What to do |
|---|---|
| **Mac** | Double-click **`Start (Mac).command`** |
| **Windows** | Double-click **`Start (Windows).bat`** |
| **Linux** | Open a terminal in the folder and type `bash start.sh` |

A text window opens.

**The first time**, it downloads what it needs (about 150 MB). This takes a few minutes, so let it run. Then it asks for your login:

```
🔑 Enter your BINUS login (it will be saved on this computer for next time)
   BINUS email: yourname@binus.ac.id
   Password (nothing shows while you type, that's normal):
```

Type your password and press **Enter**. Nothing appears while you type it. That is normal.

Next, a browser window opens and the tool does the work.
**Don't click inside that browser while it is running.** The BINUS site can be slow, so be patient.

When it finishes, the text window shows a summary. Press **Enter** to close it.

### Every time after that

Double-click the same file again. It skips the downloads and remembers your login, so you only press **Enter** to continue.

### Changing your saved login (for example, after a password change)

When it starts, it shows `Saved login: ...`. Type **C** and press **Enter**, then enter your new email and password.

---

## If something goes wrong

**Mac: "cannot be opened because it is from an unidentified developer" or "Apple could not verify…"**
Click **Done**. Open **System Settings**, go to **Privacy & Security**, scroll down, and click **Open Anyway** next to `Start (Mac).command`. You only have to do this once.

**Mac: "could not be executed because you do not have appropriate access privileges"**
Open the **Terminal** app. Type `bash ` (with a space after it), drag the file `start.sh` from the folder into the Terminal window, and press **Enter**.

**Mac: "python wants to use your confidential information stored in binus-monitoring-automation in your keychain"**
This is the tool reading your saved password. Type your **Mac login password** and click **Always Allow**.

**Windows: a blue "Windows protected your PC" box**
Click **More info**, then **Run anyway**.

**Windows: an office or school laptop blocks the setup**
Ask IT to install **uv** (https://docs.astral.sh/uv/), then double-click the start file again.

**Linux: it asks for a password the first time**
Enter your computer password. It is needed once, to install the browser's system libraries (this works automatically on Ubuntu and Debian). On other Linux versions, if the browser does not open, run `uv run playwright install-deps webkit` yourself or install the libraries it lists.

**It stops at the Microsoft login page**
Your email or password is probably wrong. Close the window, start again, type **C**, and enter them again.

**Error about the term or campus (for example `did not find some options`)**
The text in `config.py` doesn't match the dropdown exactly. Check spelling, spaces and commas (see Step 2).

**Error mentioning `config.py` and `SyntaxError`**
A quote mark or comma in `config.py` is broken. Compare it with the example in Step 2.

**It looks stuck**
The BINUS website is often very slow, and the tool waits as long as it needs to. Leave it running.

---

## Security

- Your **password** is saved in your computer's own password store, the same place your browser and email passwords are kept: **Keychain** on Mac, **Credential Manager** on Windows, and the system keyring on Linux. It is never written to a file in this folder.
- Your **email** is saved in a file called `.env` inside this folder. On Mac and Linux this file is hidden.
- Linux without a password store (for example, a server with no desktop): the password goes into `.env` instead, readable only by your user account. The tool tells you when this happens.

---

## For developers

<details>
<summary>Running manually, settings, and other files</summary>

**With uv:**

```bash
git clone https://github.com/Luche/Monitoring-Automation.git
cd Monitoring-Automation
uv sync
uv run playwright install webkit
uv run binus_automation.py
```

**With plain Python and pip:**

```bash
pip install -r requirements.txt
python -m playwright install webkit
python binus_automation.py
```

**Credentials:** by default the email goes in `.env` and the password in the OS keyring (service `binus-monitoring-automation`, via the `keyring` package). You can also set the environment variables `BINUS_USERNAME` and `BINUS_PASSWORD`, or put both in `.env` (see `.env.example`). `BINUS_PASSWORD` takes priority over the keyring. A password found in `.env` is moved into the keyring the next time the tool runs.

**Browser options** are in `binus_automation.py`, on the line `browser = p.webkit.launch(...)`:

```python
browser = p.webkit.launch(headless=False, slow_mo=1000)  # slow down each step by 1 second
browser = p.webkit.launch(headless=True)                 # run without a visible window
```

**Selectors not working:** the BINUS site may have changed. Inspect the page and update the selector in the function that fails.

**Files:**

| File | Purpose |
|---|---|
| `binus_automation.py` | The automation script |
| `config.py` | Term and campus settings |
| `start.sh`, `Start (Mac).command`, `Start (Windows).bat` | Launchers that install uv, Python 3.14 and WebKit if missing, then run the script |
| `bookmarklet.js` | Manual alternative: save its contents as a bookmark URL and click it on a Monitoring Log page to tick every box, fill in "ok", and save |

</details>
