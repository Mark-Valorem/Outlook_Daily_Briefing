# SOP: Setting Up Windows Task Scheduler

**version:** v1.0.0

## When to Use

Use this SOP when you need to:
- Set up automated twice-daily briefings
- Create or modify scheduled tasks for the Outlook briefing
- Troubleshoot scheduled execution issues
- Change briefing times (8:30 AM / 4:30 PM)
- Set up tasks on a new machine

## Prerequisites

- Windows 10 or 11
- Administrator access or ability to create scheduled tasks
- Python 3.10+ installed and on PATH
- Virtual environment created (`.venv`)
- Configuration file ready (`config/config.yaml`)
- Outlook for Windows installed

## Overview

Windows Task Scheduler will run the Python script twice daily:
- **Morning briefing:** 08:30, Monday-Friday
- **Evening briefing:** 16:30, Monday-Friday

Both tasks run in your user context and require Outlook to be open.

## Steps

### Method 1: GUI Setup (Recommended for First-Time Setup)

#### 1. Open Task Scheduler

```
Press Win+R
Type: taskschd.msc
Press Enter
```

Or search for "Task Scheduler" in Start menu.

#### 2. Create New Task

1. Click **"Create Task"** (not "Create Basic Task")
2. **General Tab:**
   - **Name:** `OutlookDailyBriefing_Morning`
   - **Description:** `Automated Outlook morning briefing at 8:30 AM`
   - **Security options:**
     - Select **"Run only when user is logged on"** (important!)
     - Check **"Run with highest privileges"** (if needed for Outlook COM access)
   - **Configure for:** Windows 10 or Windows 11

#### 3. Configure Triggers Tab

1. Click **"New..."**
2. **Settings:**
   - **Begin the task:** On a schedule
   - **Settings:** Weekly
   - **Start:** Set to today's date at 08:30:00
   - **Recur every:** 1 weeks
   - **Days:** Check Mon, Tue, Wed, Thu, Fri
   - **Enabled:** Checked
3. Click **"OK"**

#### 4. Configure Actions Tab

1. Click **"New..."**
2. **Action:** Start a program
3. **Program/script:**
   ```
   C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\python.exe
   ```
   *(Adjust path to your Python installation)*

4. **Add arguments:**
   ```
   "C:\path\to\outlook-daily-briefing\src\run_summary.py" --mode morning --config "C:\path\to\outlook-daily-briefing\config\config.yaml"
   ```
   *(Use full absolute paths)*

5. **Start in (optional):**
   ```
   C:\path\to\outlook-daily-briefing
   ```

6. Click **"OK"**

#### 5. Configure Conditions Tab

1. **Power:**
   - Uncheck **"Start the task only if the computer is on AC power"** (laptops)
   - Uncheck **"Stop if the computer switches to battery power"**

2. **Network:**
   - (Leave default settings)

#### 6. Configure Settings Tab

1. **Settings:**
   - Check **"Allow task to be run on demand"**
   - Uncheck **"Stop the task if it runs longer than"**
   - **If the task is already running:** Do not start a new instance

2. Click **"OK"**

#### 7. Enter Your Windows Password

When prompted, enter your Windows account password to save the task.

#### 8. Create Evening Briefing Task

Repeat steps 2-7 with these changes:
- **Name:** `OutlookDailyBriefing_Evening`
- **Description:** `Automated Outlook evening briefing at 4:30 PM`
- **Trigger time:** 16:30:00
- **Arguments:** `--mode evening` (instead of morning)

#### 9. Test Tasks Manually

1. Right-click on `OutlookDailyBriefing_Morning`
2. Click **"Run"**
3. Verify email is received
4. Check **"Last Run Result"** column shows `The operation completed successfully (0x0)`

### Method 2: Command-Line Setup (PowerShell)

**Note:** Run PowerShell as Administrator

#### Create Morning Briefing Task

```powershell
$Action = New-ScheduledTaskAction -Execute "C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\python.exe" `
    -Argument '"C:\path\to\outlook-daily-briefing\src\run_summary.py" --mode morning --config "C:\path\to\outlook-daily-briefing\config\config.yaml"' `
    -WorkingDirectory "C:\path\to\outlook-daily-briefing"

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 8:30AM

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "OutlookDailyBriefing_Morning" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Automated Outlook morning briefing at 8:30 AM"
```

#### Create Evening Briefing Task

```powershell
$Action = New-ScheduledTaskAction -Execute "C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\python.exe" `
    -Argument '"C:\path\to\outlook-daily-briefing\src\run_summary.py" --mode evening --config "C:\path\to\outlook-daily-briefing\config\config.yaml"' `
    -WorkingDirectory "C:\path\to\outlook-daily-briefing"

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:30PM

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "OutlookDailyBriefing_Evening" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Automated Outlook evening briefing at 4:30 PM"
```

### Method 3: Legacy schtasks Command

#### Morning Briefing

```batch
schtasks /create /tn "OutlookDailyBriefing_Morning" /tr "\"C:\Python311\python.exe\" \"C:\path\to\outlook-daily-briefing\src\run_summary.py\" --mode morning --config \"C:\path\to\outlook-daily-briefing\config\config.yaml\"" /sc WEEKLY /d MON,TUE,WED,THU,FRI /st 08:30 /ru "%USERNAME%"
```

#### Evening Briefing

```batch
schtasks /create /tn "OutlookDailyBriefing_Evening" /tr "\"C:\Python311\python.exe\" \"C:\path\to\outlook-daily-briefing\src\run_summary.py\" --mode evening --config \"C:\path\to\outlook-daily-briefing\config\config.yaml\"" /sc WEEKLY /d MON,TUE,WED,THU,FRI /st 16:30 /ru "%USERNAME%"
```

## Verification

### Check Task Exists

```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "*OutlookDaily*"}
```

### View Task Details

```powershell
Get-ScheduledTask -TaskName "OutlookDailyBriefing_Morning" | Get-ScheduledTaskInfo
```

### Test Manual Execution

```powershell
Start-ScheduledTask -TaskName "OutlookDailyBriefing_Morning"
```

### Check Last Run Status

Open Task Scheduler GUI and check:
- **Last Run Time:** Should show most recent execution
- **Last Run Result:** Should show `0x0` (success)
- **Next Run Time:** Should show next scheduled time

## Related Documentation

- **Testing:** `.agent/sops/running-tests.md`
- **Configuration:** `.agent/system/configuration.md`
- **Troubleshooting:** `.agent/sops/troubleshooting-com-errors.md`

## Common Mistakes

### Mistake: Using relative paths in task
**Solution:** Always use full absolute paths for Python executable, script, and config file.

**Incorrect:**
```
python.exe src\run_summary.py --config config\config.yaml
```

**Correct:**
```
C:\Python311\python.exe "C:\full\path\to\src\run_summary.py" --config "C:\full\path\to\config\config.yaml"
```

### Mistake: Not setting "Run only when user is logged on"
**Solution:** Task must run in user context to access Outlook COM. Select "Run only when user is logged on" in General tab.

### Mistake: Forgetting to quote paths with spaces
**Solution:** Paths containing spaces must be quoted:
```
"C:\Users\Mark Anderson\Documents\outlook-daily-briefing\src\run_summary.py"
```

### Mistake: Using virtual environment activation in scheduled task
**Solution:** Don't use `.venv\Scripts\activate` in task. Instead, use full path to Python in virtual environment:
```
C:\path\to\outlook-daily-briefing\.venv\Scripts\python.exe
```

### Mistake: Not testing with "Run" before scheduling
**Solution:** Always test task manually first by right-clicking and selecting "Run" to verify it works.

### Mistake: Outlook not running at scheduled time
**Solution:** Ensure Outlook is configured to start automatically with Windows, or open it manually before scheduled times.

## Examples

### Example 1: Find Python Installation Path

```powershell
# PowerShell
where.exe python

# Or
(Get-Command python).Source
```

Output example:
```
C:\Users\MarkAnderson\AppData\Local\Programs\Python\Python311\python.exe
```

### Example 2: Verify Task Arguments

After creating task, verify arguments are correct:

1. Open Task Scheduler
2. Double-click task name
3. Go to Actions tab
4. Double-click the action
5. Verify:
   - Program/script points to correct Python
   - Arguments include full paths and correct mode
   - All paths are quoted if they contain spaces

### Example 3: Change Briefing Time

To change morning briefing from 8:30 to 9:00:

1. Open Task Scheduler
2. Find `OutlookDailyBriefing_Morning`
3. Right-click → Properties
4. Go to Triggers tab
5. Double-click trigger
6. Change start time to 09:00:00
7. Click OK

## Troubleshooting

### Issue: Task shows "Running" but never completes
**Cause:** Script is waiting for user input or stuck
**Solution:**
1. Check script works with manual execution
2. Review script logs
3. Kill the task and fix script issue
4. Ensure scheduler_guard.py isn't blocking execution

### Issue: Task fails with "The operator or administrator has refused the request (0x800710E0)"
**Cause:** User password changed or task credentials invalid
**Solution:**
1. Right-click task → Properties
2. Change User or Group
3. Re-enter password

### Issue: Task runs but no email received
**Cause:** Outlook not running or script error
**Solution:**
1. Check Outlook is open at scheduled time
2. View task history: Task Scheduler → Enable All Tasks History
3. Check Python script logs if configured
4. Run script manually to test:
   ```bash
   C:\path\.venv\Scripts\python.exe src\run_summary.py --config config\config.yaml
   ```

### Issue: Task shows "Success" but email not sent
**Cause:** Script exited quietly (Outlook not open, scheduler guard)
**Solution:**
1. Check script logic: `behaviour.only_when_outlook_open`
2. Verify time windows in `scheduler_guard.py`
3. Use `--mode force` in task arguments to bypass guard temporarily for testing

### Issue: "Cannot find file" error
**Cause:** Paths are incorrect or not absolute
**Solution:**
1. Verify all paths in task are absolute
2. Test paths manually in PowerShell
3. Ensure config file exists at specified path

### Issue: Task doesn't run on battery power (laptop)
**Cause:** Default power condition prevents execution
**Solution:**
1. Task Properties → Conditions tab
2. Uncheck "Start the task only if the computer is on AC power"

## Notes

- Tasks run in user context, so you must be logged in
- Outlook must be running when task executes
- Use Task Scheduler history to debug failures
- Test manually before relying on scheduled execution
- Consider creating a log file for debugging:
  ```python
  logging.basicConfig(filename='C:\\path\\to\\briefing.log')
  ```

## Advanced: Using Virtual Environment Python

To use Python from virtual environment:

**Program/script:**
```
C:\path\to\outlook-daily-briefing\.venv\Scripts\python.exe
```

**Arguments:**
```
"C:\path\to\outlook-daily-briefing\src\run_summary.py" --mode morning --config "C:\path\to\outlook-daily-briefing\config\config.yaml"
```

This ensures the correct Python with installed dependencies is used.
