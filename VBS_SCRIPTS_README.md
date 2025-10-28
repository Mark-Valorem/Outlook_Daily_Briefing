# VBS Scripts for Outlook Briefing

## Overview

These VBS (Visual Basic Script) files provide easy ways to run the Outlook Daily Briefing on Windows without needing to open a command prompt. They automatically use the virtual environment Python.

## Available Scripts

### 1. `run_briefing_dryrun.vbs` (Testing)
**Purpose**: Test the briefing without sending emails

**What it does**:
- Runs in dry-run mode (no emails sent)
- Generates HTML report in `docs/samples/example-summary.html`
- Shows completion message when done
- Uses morning mode by default

**How to use**:
- Double-click the file
- Wait for completion message
- Open `docs/samples/example-summary.html` to review the report

---

### 2. `run_briefing_morning.vbs` (Production)
**Purpose**: Send morning briefing email via Outlook

**What it does**:
- Collects VIP emails from the last 14 days
- Analyzes flagged emails with AI
- Sends HTML email report through Outlook
- Runs silently (no console window)

**How to use**:
- Double-click to run manually, OR
- Use in Windows Task Scheduler (recommended)

---

### 3. `run_briefing_evening.vbs` (Production)
**Purpose**: Send evening briefing email via Outlook

**What it does**:
- Same as morning briefing but runs in evening mode
- Collects VIP emails from the last 14 days
- Analyzes flagged emails with AI
- Sends HTML email report through Outlook

**How to use**:
- Double-click to run manually, OR
- Use in Windows Task Scheduler (recommended)

---

## Setting Up Windows Task Scheduler

### For Morning Briefing (8:30 AM, Weekdays)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Task** (not "Create Basic Task")
3. **General tab**:
   - Name: `Outlook Morning Briefing`
   - Description: `Send morning VIP email briefing`
   - Run whether user is logged on or not: **Unchecked**
   - Run with highest privileges: **Checked** (if needed)

4. **Triggers tab**:
   - Click **New**
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start: `8:30 AM`
   - Recur every: `1 days`
   - Advanced settings: Check **"Enabled"**
   - Also check: `Stop task if it runs longer than: 30 minutes`
   - At bottom: Select days `Monday, Tuesday, Wednesday, Thursday, Friday`

5. **Actions tab**:
   - Click **New**
   - Action: `Start a program`
   - Program/script: Browse to `run_briefing_morning.vbs`
   - Start in: `C:\Users\MarkAnderson\Valorem\Project Hub - Documents\Coding Projects\2508_Daily Email Review`

6. **Conditions tab**:
   - Uncheck: `Start the task only if the computer is on AC power`
   - Check: `Wake the computer to run this task` (optional)

7. **Settings tab**:
   - Check: `Allow task to be run on demand`
   - Check: `Run task as soon as possible after a scheduled start is missed`
   - If the task fails, restart every: `1 minute`, Attempt to restart up to: `3 times`

8. Click **OK** to save

### For Evening Briefing (4:30 PM, Weekdays)

Follow the same steps as morning briefing, but:
- Name: `Outlook Evening Briefing`
- Start time: `4:30 PM`
- Program/script: Browse to `run_briefing_evening.vbs`

---

## Troubleshooting

### Script doesn't run
**Check:**
1. Outlook is open when the script runs
2. Virtual environment is set up (`.venv` folder exists)
3. `anthropic` package is installed in venv: `.venv\Scripts\pip.exe show anthropic`

### No email sent
**Check:**
1. Remove `--dry-run` flag (production scripts don't have this)
2. Outlook is open and logged in
3. Check Windows Event Viewer for errors

### AI analysis not working
**Check:**
1. `ANTHROPIC_API_KEY` environment variable is set
2. Config has `ai_analysis.enabled: true`
3. Run dry-run script and check `docs/samples/example-summary.html` for 🤖 emoji

### Scheduled task not running
**Check:**
1. Task Scheduler shows task as **Ready** (not Disabled)
2. "Last Run Result" shows `0x0` (success)
3. Computer is logged in at scheduled time
4. Outlook is open at scheduled time

---

## Technical Details

### How the VBS scripts work:
1. Get the script's directory (project root)
2. Set working directory to project root
3. Execute `.venv\Scripts\python.exe` with full paths
4. Pass `--config`, `--mode` flags to the Python script
5. Run silently with no console window (`0` parameter)
6. Wait for completion (`True` parameter)

### Script parameters explained:
- `0` = Hide console window (silent mode)
- `True` = Wait for script to complete before exiting
- `--mode morning/evening` = Determines which briefing mode
- `--dry-run` = Test mode, doesn't send emails

---

## Editing the Scripts

If you need to modify the scripts:

1. Right-click the `.vbs` file
2. Select **Edit** (opens in Notepad)
3. Modify the command line arguments
4. Save and test

**Example modifications:**
- Change mode: Replace `--mode morning` with `--mode evening`
- Add verbose logging: Add `--verbose` flag
- Change lookback period: Add `--since 7d` flag

---

## Security Note

These scripts use the currently logged-in user's credentials and environment. They do NOT store passwords or API keys in the script. The `ANTHROPIC_API_KEY` must be set as a system or user environment variable separately.

---

## Getting Help

If you encounter issues:
1. Test with `run_briefing_dryrun.vbs` first
2. Check the log output in Task Scheduler history
3. Run manually from command prompt to see errors:
   ```cmd
   .venv\Scripts\python.exe src\run_summary.py --config config\config.yaml --verbose --dry-run
   ```
