# SOP: Troubleshooting COM Errors

**version:** v1.0.0

## When to Use

Use this SOP when encountering:
- "Error converting mail item: <unknown>.ReceivedTime" errors
- Python COM errors (pythoncom.com_error)
- Outlook connection failures
- Property access issues on Outlook objects
- Intermittent failures when accessing email properties

## Prerequisites

- Basic understanding of COM automation
- Access to Python error logs
- Outlook for Windows running
- Ability to run Python scripts with --verbose flag

## Overview

COM (Component Object Model) is the technology that allows Python to interact with Outlook on Windows. COM errors can occur due to:
- Malformed Outlook items (corrupted emails, drafts)
- Invalid property access on certain item types
- Outlook not running or not accessible
- Security restrictions on COM automation
- Race conditions during Outlook operations

## Common COM Errors

### Error 1: ReceivedTime Property Access Error

**Symptom:**
```
briefing.collector - ERROR - Error converting mail item: <unknown>.ReceivedTime
```

**Description:**
- Most common COM error in this project
- Occurs when trying to access `.ReceivedTime` property on certain Outlook items
- Script continues to run and processes other emails

**Root Cause:**
- Some Outlook item types don't have `ReceivedTime` property:
  - Draft emails
  - Meeting requests (in some states)
  - Corrupted or malformed items
  - Items with invalid timestamps

**Impact:**
- One or more emails are skipped during collection
- Report is still generated successfully
- Missing problematic items from report

**Solutions:**

#### Solution 1: Use Shorter Time Range (Quickest)
```bash
# Scan only last 6 hours
python src\run_summary.py --config config\config.yaml --dry-run --since 6h

# Or last 12 hours
python src\run_summary.py --config config\config.yaml --dry-run --since 12h
```

**Why it works:** Reduces likelihood of encountering problematic old items

#### Solution 2: Clean Up Outlook
1. Open Outlook
2. Check for draft emails in Inbox
3. Move drafts to Drafts folder
4. Check for corrupted items (items with no date)
5. Delete or repair problematic items

#### Solution 3: Improve Error Handling (Code Fix)

**File:** `src/briefing/collector.py`

**Locate the conversion method:**
```python
def _convert_mail_item(self, item) -> Optional[EmailItem]:
    try:
        # ... existing code ...
        received_time=item.ReceivedTime,
        # ... rest of code ...
    except Exception as e:
        logger.error(f"Error converting mail item: {e}")
        return None
```

**Enhanced version with specific property handling:**
```python
def _convert_mail_item(self, item) -> Optional[EmailItem]:
    try:
        # Try to get ReceivedTime, fallback to SentOn or current time
        try:
            received_time = item.ReceivedTime
        except AttributeError:
            logger.warning(f"ReceivedTime not available for item: {item.Subject}, using SentOn")
            try:
                received_time = item.SentOn
            except AttributeError:
                logger.warning(f"Neither ReceivedTime nor SentOn available, skipping item")
                return None

        return EmailItem(
            entry_id=item.EntryID,
            subject=item.Subject or "(No Subject)",
            received_time=received_time,
            # ... rest of fields ...
        )

    except Exception as e:
        logger.error(f"Error converting mail item '{getattr(item, 'Subject', 'unknown')}': {e}")
        return None
```

### Error 2: Outlook Not Running

**Symptom:**
```python
pythoncom.com_error: (-2147221021, 'Operation unavailable', None, None)
```

**Description:**
- Occurs when trying to connect to Outlook but it's not running
- Script should exit gracefully

**Root Cause:**
- Outlook is closed when script runs
- Outlook is starting up (not fully loaded)

**Solutions:**

#### Solution 1: Ensure Outlook is Running
```bash
# Check if Outlook is running (PowerShell)
Get-Process | Where-Object {$_.Name -eq "OUTLOOK"}

# Start Outlook if needed
Start-Process outlook
```

#### Solution 2: Wait for Outlook to Load
If running immediately after Windows startup, add delay:
```python
import time
time.sleep(10)  # Wait 10 seconds for Outlook to fully load
outlook = win32com.client.GetActiveObject("Outlook.Application")
```

#### Solution 3: Verify Graceful Exit
**File:** `src/briefing/outlook_client.py`

Ensure connection method handles error:
```python
def connect(self) -> bool:
    try:
        self.app = win32com.client.GetActiveObject("Outlook.Application")
        self.namespace = self.app.GetNamespace("MAPI")
        logger.info("Connected to Outlook")
        return True
    except pythoncom.com_error:
        if self.only_when_open:
            logger.warning("Could not connect to Outlook (not running)")
            return False
        else:
            raise
```

### Error 3: Property Access Denied

**Symptom:**
```python
pythoncom.com_error: (-2147352567, 'Exception occurred.', ...)
```

**Description:**
- Occurs when trying to access a property that requires additional permissions
- Some properties are restricted by Outlook security

**Root Cause:**
- Corporate security policies restrict COM automation
- Outlook trust center settings block programmatic access
- Anti-virus or security software interferes

**Solutions:**

#### Solution 1: Check Outlook Trust Center Settings
1. Open Outlook
2. File → Options → Trust Center → Trust Center Settings
3. **Programmatic Access:**
   - Ensure "Warn me about suspicious activity when my antivirus is inactive or out-of-date" is checked
   - But not overly restrictive

#### Solution 2: Add Exception for Python Script
Speak to IT department to:
- Whitelist Python.exe for Outlook COM access
- Add exception for your user account
- Disable security prompts for trusted applications

#### Solution 3: Wrap Property Access in Try-Except
```python
def safe_get_property(item, property_name, default=None):
    """Safely access Outlook item property with fallback"""
    try:
        return getattr(item, property_name)
    except (AttributeError, pythoncom.com_error):
        logger.debug(f"Could not access property: {property_name}")
        return default

# Usage
sender_email = safe_get_property(item, "SenderEmailAddress", "unknown@unknown.com")
```

### Error 4: Items.Restrict Filter Error

**Symptom:**
```python
pythoncom.com_error: (-2147352567, 'Exception occurred.', ...)
```
When using `.Restrict()` method

**Description:**
- Error in filter syntax for Items.Restrict()
- Invalid date format or comparison

**Root Cause:**
- Incorrect filter string syntax
- Date format doesn't match Outlook expectations

**Solutions:**

#### Solution 1: Verify Filter Syntax
**Correct date filter format:**
```python
cutoff_date = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y %H:%M %p")
filter_str = f"[ReceivedTime] >= '{cutoff_date}'"
```

**See:** [Outlook Items.Restrict documentation](https://learn.microsoft.com/office/vba/api/outlook.items.restrict)

#### Solution 2: Use Sort Before Restrict
```python
items = folder.Items
items.Sort("[ReceivedTime]", True)  # Sort descending
filtered = items.Restrict(filter_str)
```

### Error 5: Attachment Access Error

**Symptom:**
```python
pythoncom.com_error when accessing item.Attachments
```

**Description:**
- Some items have attachments that can't be accessed
- Embedded objects or special attachment types

**Solutions:**

#### Wrap Attachment Access
```python
try:
    attachment_count = item.Attachments.Count
except (AttributeError, pythoncom.com_error):
    attachment_count = 0
```

## Diagnostic Steps

### Step 1: Run with Verbose Logging

```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose
```

**What to look for:**
- Exact error message
- Which item caused the error (subject line if available)
- How many items processed before error

### Step 2: Test Outlook Connection Manually

```python
# test_outlook.py
import win32com.client
import pythoncom

try:
    outlook = win32com.client.GetActiveObject("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)
    print(f"Successfully connected. Inbox has {inbox.Items.Count} items")
except pythoncom.com_error as e:
    print(f"Connection failed: {e}")
```

### Step 3: Inspect Problematic Items

If specific emails cause errors:

```python
# inspect_item.py
import win32com.client

outlook = win32com.client.GetActiveObject("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
inbox = namespace.GetDefaultFolder(6)

for item in inbox.Items:
    try:
        print(f"Subject: {item.Subject}")
        print(f"ReceivedTime: {item.ReceivedTime}")
        print(f"Class: {item.Class}")  # Item type
        print("---")
    except Exception as e:
        print(f"ERROR on item: {e}")
        print(f"Class: {getattr(item, 'Class', 'unknown')}")
        break
```

### Step 4: Check Outlook Item Class

Different Outlook item types:
- `43` = MailItem (normal email)
- `45` = TaskItem
- `53` = ReportItem
- `26` = MeetingItem

Filter to only process MailItems:
```python
if item.Class == 43:  # Only MailItem
    # Process item
```

## Prevention Strategies

### Strategy 1: Validate Item Type Before Processing

```python
def _convert_mail_item(self, item) -> Optional[EmailItem]:
    # Check if it's actually a mail item
    if item.Class != 43:  # Not a MailItem
        logger.debug(f"Skipping non-mail item (class {item.Class})")
        return None

    # Continue processing...
```

### Strategy 2: Use Shorter Default Lookback

In `config.yaml`:
```yaml
behaviour:
  lookback_days_inbox: 1  # Reduce from 2 to 1
```

Shorter lookback = fewer problematic items encountered

### Strategy 3: Implement Retry Logic

```python
def get_items_with_retry(folder, filter_str, max_retries=3):
    for attempt in range(max_retries):
        try:
            return folder.Items.Restrict(filter_str)
        except pythoncom.com_error:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise
```

### Strategy 4: Log Problematic Item Details

Help identify patterns:
```python
except Exception as e:
    logger.error(f"Error on item: {e}")
    logger.error(f"  Entry ID: {getattr(item, 'EntryID', 'unknown')}")
    logger.error(f"  Subject: {getattr(item, 'Subject', 'unknown')}")
    logger.error(f"  Class: {getattr(item, 'Class', 'unknown')}")
    logger.error(f"  Size: {getattr(item, 'Size', 'unknown')}")
```

## Related Documentation

- **Architecture:** `.agent/system/architecture.md`
- **Data Models:** `.agent/system/data-models.md`
- **Testing:** `.agent/sops/running-tests.md`
- **Microsoft Outlook Object Model:** [Outlook VBA Reference](https://learn.microsoft.com/office/vba/api/overview/outlook/object-model)

## Common Mistakes

### Mistake: Assuming all properties are always available
**Solution:** Use try-except around property access, especially for optional properties.

### Mistake: Not checking Outlook item type before processing
**Solution:** Check `item.Class == 43` to ensure it's a MailItem before accessing email-specific properties.

### Mistake: Using long lookback periods unnecessarily
**Solution:** Use shorter time ranges (`--since 6h`) to reduce exposure to problematic items.

### Mistake: Not logging enough detail when errors occur
**Solution:** Log item details (EntryID, Subject, Class) when exceptions are caught to help identify patterns.

## Examples

### Example 1: Handling ReceivedTime Gracefully

**Before (causes errors):**
```python
received_time = item.ReceivedTime
```

**After (handles errors):**
```python
try:
    received_time = item.ReceivedTime
except AttributeError:
    # Try alternative timestamp
    try:
        received_time = item.SentOn
    except AttributeError:
        # Skip this item
        logger.warning(f"No timestamp available for item: {item.Subject}")
        return None
```

### Example 2: Safe Property Access Helper

```python
def safe_get(item, prop_name, default=None):
    """Safely get property from Outlook COM object"""
    try:
        value = getattr(item, prop_name)
        return value if value is not None else default
    except (AttributeError, pythoncom.com_error):
        return default

# Usage
subject = safe_get(item, "Subject", "(No Subject)")
sender = safe_get(item, "SenderName", "Unknown")
```

## Troubleshooting Quick Reference

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| "ReceivedTime" error | Draft or corrupted item | Use `--since 6h` |
| "Operation unavailable" | Outlook not running | Start Outlook |
| "Access denied" | Security restriction | Check Trust Center settings |
| "Invalid filter" | Restrict() syntax error | Verify date format |
| Script hangs | Waiting for COM response | Kill process, check Outlook state |

## Notes

- COM errors are often intermittent and hard to reproduce
- Shorter time ranges are the most reliable workaround
- Always log detailed information when errors occur
- Consider adding metrics: how many items failed, how many succeeded
- Future enhancement: Add `--skip-problematic` flag to automatically retry with shorter ranges
