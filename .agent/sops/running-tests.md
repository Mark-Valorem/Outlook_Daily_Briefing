# SOP: Running Tests

**version:** v1.0.0

## When to Use

Use this SOP when you need to:
- Verify the system is working correctly
- Test configuration changes
- Validate new features before deployment
- Troubleshoot issues
- Run scheduled task validation

## Prerequisites

- Python 3.10+ environment
- Dependencies installed (`pip install -r requirements.txt`)
- Outlook for Windows running
- Configuration file created (`config/config.yaml`)

## Current Testing Approach

**Note:** This project currently has **no automated unit or integration tests** (see README roadmap). Testing is done manually using the `--dry-run` flag and various command-line options.

## Steps

### 1. Activate Virtual Environment

```bash
# Navigate to project root
cd "C:\path\to\outlook-daily-briefing"

# Activate virtual environment
.venv\Scripts\activate
```

### 2. Basic Dry Run Test

**Command:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run
```

**What it does:**
- Connects to Outlook
- Collects emails and calendar items
- Prioritizes and groups emails
- Generates HTML report
- **Does NOT send email**
- Prints summary to console

**Expected Output:**
```
INFO - Starting Outlook Daily Briefing
INFO - Running in auto mode
INFO - Configuration loaded from config\config.yaml
INFO - Connected to Outlook
INFO - DRY RUN MODE - Email not sent
INFO - Subject: Daily Outlook Briefing - 2025-10-27 16:30
INFO - To: marka@valorem.com.au
INFO - Total emails processed: 42
INFO - Total calendar items: 5
INFO - Outlook Daily Briefing completed successfully
```

### 3. Verbose Dry Run Test

**Command:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose
```

**What it does:**
- Same as basic dry run
- Enables DEBUG-level logging
- Shows detailed processing steps

**Use When:**
- Debugging priority scoring issues
- Understanding why emails are grouped certain ways
- Investigating COM errors
- Validating new feature logic

**Expected Output:**
```
DEBUG - Collecting inbox items...
DEBUG - Found 38 items in inbox
DEBUG - Collecting sent items...
DEBUG - Found 12 items in sent
DEBUG - Processing email: "Urgent: Payment Required"
DEBUG - Priority score: 25 (VIP domain + urgent keyword)
DEBUG - Assigned to group: high_priority
...
```

### 4. Test with Short Time Range

**Command:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --since 6h
```

**What it does:**
- Overrides `lookback_days_inbox` to 6 hours
- Reduces number of emails processed
- Faster execution

**Use When:**
- Testing quickly without processing many emails
- Avoiding problematic old emails (see Known Issues in README)
- Debugging recent email handling

**Other Time Ranges:**
```bash
--since 1d   # Last 1 day
--since 2d   # Last 2 days
--since 12h  # Last 12 hours
```

### 5. Test Specific Mode

**Command:**
```bash
# Force morning briefing mode
python src\run_summary.py --config config\config.yaml --dry-run --mode morning

# Force evening briefing mode
python src\run_summary.py --config config\config.yaml --dry-run --mode evening
```

**What it does:**
- Overrides automatic mode detection (based on time)
- Tests mode-specific logic (e.g., tomorrow's first meeting in morning mode)

**Use When:**
- Testing morning-specific features outside of morning hours
- Validating evening briefing logic in the morning

### 6. Test with HTML Preview

**Setup:**
Ensure your `config.yaml` has:
```yaml
report:
  preview_html: "docs/samples/example-summary.html"
```

**Command:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run
```

**What it does:**
- Generates HTML report
- Saves to `docs/samples/example-summary.html`
- Allows visual inspection in browser

**Use When:**
- Validating template changes
- Checking HTML formatting
- Reviewing report layout before sending

**How to Review:**
```bash
# Open in default browser (Windows)
start docs\samples\example-summary.html
```

### 7. Test Real Email Send (Caution!)

**Command:**
```bash
python src\run_summary.py --config config\config.yaml --mode force
```

**What it does:**
- Actually sends the email via Outlook
- Use `--mode force` to bypass scheduler guard

**⚠️ Caution:**
- This will send a real email to the address in `config.yaml`
- Ensure `report.to` is set to your own email first
- Review with `--dry-run` first

**Use When:**
- Final validation before scheduling
- Testing email delivery
- Verifying Outlook integration

### 8. Test Scheduler Guard

**Command:**
```bash
# Without force mode
python src\run_summary.py --config config\config.yaml --mode auto
```

**What it does:**
- Checks if current time is within briefing windows
- Exits quietly if outside schedule

**Use When:**
- Validating scheduled task behavior
- Testing time-based execution logic

**Expected Behavior:**
- **08:00 - 09:00:** Runs in morning mode
- **16:00 - 17:00:** Runs in evening mode
- **Other times:** Exits quietly

### 9. Test Configuration Validation

**Command:**
```bash
# Test with invalid config path
python src\run_summary.py --config config\nonexistent.yaml
```

**Expected Output:**
```
ERROR - Configuration file error: Configuration file not found: config\nonexistent.yaml
```

**Test Invalid Config Structure:**
- Remove required field from config.yaml
- Run with --dry-run
- Should see KeyError or similar error

**Use When:**
- Validating error handling
- Testing config validation logic

### 10. Test Outlook Not Running

**Command:**
```bash
# Close Outlook first
# Then run:
python src\run_summary.py --config config\config.yaml --dry-run
```

**Expected Output:**
```
INFO - Starting Outlook Daily Briefing
INFO - Running in auto mode
INFO - Configuration loaded from config\config.yaml
WARNING - Could not connect to Outlook
# Script exits with code 0 (success - graceful exit)
```

**Use When:**
- Validating graceful exit behavior
- Testing scheduled task behavior when Outlook is closed

## Test Checklist for New Features

When adding a new feature, run through this checklist:

- [ ] Dry run completes without errors
- [ ] Verbose mode shows expected debug logs
- [ ] HTML preview displays correctly
- [ ] Priority scoring works as expected
- [ ] Grouping logic assigns emails correctly
- [ ] Configuration changes are respected
- [ ] Test with both `--mode morning` and `--mode evening`
- [ ] Test with short time range (`--since 6h`)
- [ ] Test real email send to yourself
- [ ] Review HTML in email client

## Related Documentation

- **Configuration:** `.agent/system/configuration.md`
- **Adding Features:** `.agent/sops/adding-feature.md`
- **Troubleshooting:** `.agent/sops/troubleshooting-com-errors.md`
- **Main README:** `README.md`

## Common Mistakes

### Mistake: Not using --dry-run first
**Solution:** Always test with `--dry-run` before sending real emails. This prevents sending broken or malformed reports to yourself.

### Mistake: Testing without Outlook open
**Solution:** Ensure Outlook is running before testing. The script will exit quietly if Outlook is closed.

### Mistake: Not checking preview HTML
**Solution:** Always review the generated HTML in `docs/samples/example-summary.html` to catch formatting issues.

### Mistake: Testing outside briefing windows
**Solution:** Use `--mode force` or specific modes (`morning`, `evening`) to bypass scheduler guard during testing.

### Mistake: Not using verbose mode when debugging
**Solution:** Use `--verbose` to see detailed logs when troubleshooting issues. It shows priority scores, grouping decisions, and collection details.

## Examples

### Example 1: Test Configuration Changes

**Scenario:** You added new VIP domains to config.yaml

**Steps:**
```bash
# 1. Dry run with verbose to see priority scoring
python src\run_summary.py --config config\config.yaml --dry-run --verbose

# 2. Check logs for new VIP domain matches
# Look for: "Priority score: +10 (VIP domain)"

# 3. Review HTML preview
start docs\samples\example-summary.html

# 4. Verify emails from new VIP domains appear in "High Priority" section
```

### Example 2: Test New Priority Rule

**Scenario:** You added a new keyword rule for "invoice"

**Steps:**
```bash
# 1. Run dry run with verbose
python src\run_summary.py --config config\config.yaml --dry-run --verbose --since 7d

# 2. Search logs for keyword matches
# Look for: "Matched keyword rule: invoice"

# 3. Verify priority scores increased for matching emails

# 4. Check HTML preview shows correct grouping
```

### Example 3: Test Scheduling

**Scenario:** Validate scheduled task will work correctly

**Steps:**
```bash
# 1. Test auto mode at different times of day
python src\run_summary.py --config config\config.yaml --dry-run --mode auto

# 2. Test morning mode explicitly
python src\run_summary.py --config config\config.yaml --dry-run --mode morning

# 3. Test evening mode explicitly
python src\run_summary.py --config config\config.yaml --dry-run --mode evening

# 4. Verify tomorrow's first meeting only shows in morning mode
```

## Troubleshooting

### Issue: Script exits immediately with no output
**Cause:** Outlook not running or scheduler guard prevented execution
**Solution:**
1. Check Outlook is open
2. Use `--mode force` to bypass scheduler guard
3. Use `--verbose` to see why it exited

### Issue: "ReceivedTime" COM error
**Cause:** Problematic Outlook items (drafts, corrupted emails)
**Solution:** Use shorter time range: `--since 6h`
**See:** `.agent/sops/troubleshooting-com-errors.md`

### Issue: No emails in report
**Cause:** Time range too short or no emails match filters
**Solution:**
1. Increase time range: `--since 7d`
2. Check `ignore_domains` isn't filtering everything
3. Use `--verbose` to see collection details

### Issue: Wrong emails prioritized
**Cause:** Config rules not matching as expected
**Solution:**
1. Use `--verbose` to see priority scoring
2. Review VIP domains and keyword rules in config
3. Check for typos in domain names

## Future Testing Enhancements (Roadmap)

See README for planned improvements:
- [ ] Unit tests for prioritizer logic
- [ ] Integration tests for Outlook COM interaction
- [ ] Automated test suite with pytest
- [ ] Mock Outlook objects for testing without Outlook
- [ ] CI/CD pipeline for automated testing

## Notes

- Dry run is your friend - use it liberally
- Verbose mode provides invaluable debugging information
- Always review HTML preview before sending real emails
- Test both morning and evening modes if feature affects them differently
- Short time ranges (`--since 6h`) help avoid COM errors
