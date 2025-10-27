# SOP: Making Configuration Changes

**version:** v1.0.0

## When to Use

Use this SOP when you need to:
- Add new VIP domains or senders
- Create or modify priority keyword rules
- Adjust report settings (sections, item limits)
- Change timing or lookback behavior
- Add customer group mappings
- Modify calendar settings

## Prerequisites

- Text editor or IDE
- Basic understanding of YAML or JSON syntax
- Access to `config/config.yaml`
- Ability to test changes with dry-run

## Steps

### 1. Locate Configuration File

**Primary Config:**
```
config/config.yaml
```

**Template (for reference):**
```
config/config.template.yaml
```

**Note:** Never commit your personal `config.yaml` with real email addresses or sensitive data to the repository.

### 2. Backup Current Configuration

Before making changes:
```bash
# Create backup
copy config\config.yaml config\config.yaml.backup

# Or with timestamp
copy config\config.yaml config\config.yaml.%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

### 3. Open Configuration File

```bash
# With default text editor
notepad config\config.yaml

# Or with VS Code
code config\config.yaml
```

### 4. Make Changes Based on Need

See specific sections below for common change scenarios.

### 5. Validate YAML Syntax

**Common YAML Issues:**
- Indentation must use spaces (not tabs)
- Lists use `- ` prefix
- Strings with special characters should be quoted
- Colons require space after them (`: `)

**Online Validator:**
- Use https://www.yamllint.com/ if unsure about syntax

**Python Validation:**
```bash
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
# No output = valid YAML
# Error = syntax issue
```

### 6. Test Changes with Dry Run

```bash
# Activate virtual environment
.venv\Scripts\activate

# Test configuration
python src\run_summary.py --config config\config.yaml --dry-run --verbose
```

**What to Check:**
- Script runs without errors
- Configuration loads successfully
- Changes are reflected in output
- Priority scores adjust as expected

### 7. Review HTML Preview

```bash
# Open preview HTML
start docs\samples\example-summary.html
```

**What to Check:**
- Report sections appear correctly
- Emails are grouped as expected
- Priority indicators are correct
- No formatting issues

### 8. Test Real Send (Optional)

⚠️ Only after dry-run validation!

```bash
python src\run_summary.py --config config\config.yaml --mode force
```

## Common Configuration Changes

### Change 1: Add New VIP Domain

**Use Case:** Add a new key customer domain that should always be high priority

**File Section:** `priorities.vip_domains`

**Steps:**
```yaml
priorities:
  vip_domains:
    - "existing-customer.com"
    - "another-customer.com"
    - "new-vip-customer.com"  # Add this line
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose --since 7d
```

**Verify:** Look for priority score increase (+10) for emails from new domain

### Change 2: Add VIP Sender

**Use Case:** Specific person should always get highest priority

**File Section:** `priorities.vip_senders`

**Steps:**
```yaml
priorities:
  vip_senders:
    - "ceo@company.com"
    - "board-member@company.com"  # Add this line
```

**Test:** Send yourself a test email from that address, then run dry-run

**Verify:** Email appears in "High Priority" section with score +15

### Change 3: Add Keyword Rule

**Use Case:** Emails mentioning "contract" should be high priority

**File Section:** `priorities.keyword_rules`

**Steps:**
```yaml
priorities:
  keyword_rules:
    # ... existing rules ...

    # New rule for contracts
    - pattern: "(?i)\\bcontract\\b|\\bagreement\\b|\\bterms\\b"
      priority: high
      suggest: "Review and forward to legal team"
```

**Pattern Tips:**
- `(?i)` = case insensitive
- `\\b` = word boundary (matches whole words only)
- `|` = OR (matches any of the alternatives)

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose --since 7d
```

**Verify:** Emails with those keywords get score boost and show suggestion

### Change 4: Add Group Mapping

**Use Case:** Assign specific customer domains to team members

**File Section:** `priorities.group_mappings`

**Steps:**
```yaml
priorities:
  group_mappings:
    "customer-a.com": "Sarah's Clients"
    "customer-b.com": "Jason's Clients"
    "customer-c.com": "Alex's Clients"  # Add this line
```

**Test:** Run dry-run and check report sections

**Verify:** New section appears in report: "Alex's Clients (N)"

### Change 5: Ignore Noisy Domain

**Use Case:** Stop showing newsletters or automated notifications

**File Section:** `priorities.ignore_domains`

**Steps:**
```yaml
priorities:
  ignore_domains:
    - "newsletter.example.com"
    - "noreply@notifications.com"
    - "spam-source.com"  # Add this line
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose
```

**Verify:** Emails from ignored domains don't appear in report at all

### Change 6: Adjust Report Recipient

**Use Case:** Change who receives the daily briefing

**File Section:** `report.to`

**Steps:**
```yaml
report:
  to: "new-email@company.com"  # Change this
```

**⚠️ Important:** Test with dry-run first, then use `--mode force` to send test email

### Change 7: Adjust Lookback Period

**Use Case:** Change how many days back to scan Inbox

**File Section:** `behaviour.lookback_days_inbox`

**Steps:**
```yaml
behaviour:
  lookback_days_inbox: 7  # Was 2, now 7 days
```

**Note:** Longer lookback = more emails = larger report

**Alternative:** Use command-line override:
```bash
python src\run_summary.py --config config\config.yaml --since 7d
```

### Change 8: Adjust Max Items per Section

**Use Case:** Reduce report length

**File Section:** `report.max_items_per_section`

**Steps:**
```yaml
report:
  max_items_per_section: 10  # Was 20, now 10
```

**Test:** Check preview HTML to ensure important emails aren't cut off

### Change 9: Disable Tomorrow's First Meeting

**Use Case:** Don't show tomorrow's first meeting in morning briefing

**File Section:** `calendar.include_tomorrow_first_meeting`

**Steps:**
```yaml
calendar:
  include_tomorrow_first_meeting: false  # Was true
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --mode morning
```

**Verify:** Tomorrow's first meeting doesn't appear

### Change 10: Customize Report Subject

**Use Case:** Change email subject line format

**File Section:** `report.subject_template`

**Steps:**
```yaml
report:
  subject_template: "Daily Briefing - {{ mode|title }} - {{ timestamp_local }}"
```

**Available Variables:**
- `{{ timestamp_local }}` - Full timestamp
- `{{ mode }}` - morning/evening
- `{{ date }}` - Date only

**Test:** Check subject line in dry-run output

## Related Documentation

- **Configuration Reference:** `.agent/system/configuration.md`
- **Priority Scoring:** `.agent/system/architecture.md`
- **Testing:** `.agent/sops/running-tests.md`

## Common Mistakes

### Mistake: Using tabs instead of spaces for indentation
**Solution:** YAML requires spaces. Use 2 spaces per indent level. Configure your editor to insert spaces when Tab is pressed.

### Mistake: Forgetting `:` after key or missing space after `:`
**Solution:** YAML syntax requires `key: value` with space after colon.

**Incorrect:**
```yaml
report:to: "email@example.com"
```

**Correct:**
```yaml
report:
  to: "email@example.com"
```

### Mistake: Not quoting strings with special characters
**Solution:** Quote strings containing `:`, `@`, `#`, etc.

**Incorrect:**
```yaml
pattern: (?i)\btest\b
```

**Correct:**
```yaml
pattern: "(?i)\\btest\\b"
```

### Mistake: Testing without dry-run first
**Solution:** Always test with `--dry-run` before sending real emails.

### Mistake: Adding VIP domain without subdomain consideration
**Solution:** Domain matching is suffix-based. `customer.com` will match `john@customer.com` and `john@mail.customer.com`.

### Mistake: Case-sensitive keyword patterns
**Solution:** Always use `(?i)` flag at start of pattern for case-insensitive matching.

## Examples

### Example 1: Prioritize Urgent Financial Emails

**Goal:** Emails with invoice/payment keywords from accounting should be critical priority

**Configuration Changes:**
```yaml
priorities:
  # Add accounting domain as VIP
  vip_domains:
    - "accounting-firm.com"

  # Add financial keywords as critical
  keyword_rules:
    - pattern: "(?i)\\binvoice\\b|\\bpayment\\b|\\boverdue\\b|\\bAP\\b"
      priority: critical
      suggest: "Review payment status immediately"
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose --since 7d
```

**Expected:** Emails from accounting-firm.com with those keywords score 30+ and appear at top

### Example 2: Separate Customer Accounts by Salesperson

**Goal:** Group customers by assigned salesperson

**Configuration Changes:**
```yaml
priorities:
  group_mappings:
    "customerA.com": "Sarah's Accounts"
    "customerB.com": "Sarah's Accounts"
    "customerC.com": "Jason's Accounts"
    "customerD.com": "Jason's Accounts"
    "customerE.com": "Alex's Accounts"
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run
```

**Expected:** Report shows separate sections:
- Sarah's Accounts (5 emails)
- Jason's Accounts (3 emails)
- Alex's Accounts (2 emails)

### Example 3: Reduce Noise from Automated Systems

**Goal:** Filter out automated notifications and newsletters

**Configuration Changes:**
```yaml
priorities:
  ignore_domains:
    - "noreply@company.com"
    - "notifications.external-system.com"
    - "newsletter.industry-group.org"
    - "alerts.monitoring-service.com"
```

**Test:**
```bash
python src\run_summary.py --config config\config.yaml --dry-run --verbose
```

**Expected:** Console logs show "Ignoring email from [domain]", and those emails don't appear in report

## Troubleshooting

### Issue: "YAML parse error" when loading config
**Cause:** Syntax error in YAML file
**Solution:**
1. Use online YAML validator
2. Check indentation (spaces only, no tabs)
3. Check for unquoted special characters
4. Restore from backup and redo changes

### Issue: Changes not reflected in report
**Cause:** Using old config file or not saved changes
**Solution:**
1. Verify you saved the file
2. Check you're using correct config path in command
3. Use `--verbose` to see loaded configuration values

### Issue: Keyword pattern not matching
**Cause:** Incorrect regex syntax or escaping
**Solution:**
1. Test regex online (e.g., regex101.com)
2. Remember to escape backslashes in YAML: `\\b` not `\b`
3. Use `(?i)` flag for case-insensitive matching

### Issue: VIP domain matches too many emails
**Cause:** Domain suffix matching catches subdomains
**Solution:** This is expected behavior. Use `ignore_domains` or `downrank_domains` to exclude specific subdomains if needed.

## Notes

- Keep a backup before major configuration changes
- Test incrementally (one change at a time for complex updates)
- Use verbose mode to understand priority scoring
- Document why you made changes (especially for team environments)
- Consider creating multiple config files for different scenarios (e.g., `config.work.yaml`, `config.test.yaml`)
