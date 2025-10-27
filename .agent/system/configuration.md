# Configuration Reference

**version:** v1.0.0

## Overview

Outlook Daily Briefing uses YAML (or JSON) configuration files to define behavior, priority rules, and report settings. Configuration is loaded at runtime and validated against expected structure.

**Location:** `config/config.yaml`
**Template:** `config/config.template.yaml`

## Configuration File Structure

### Top-Level Sections

```yaml
report:         # Report generation and delivery settings
behaviour:      # Execution behavior and filters
priorities:     # Email prioritization rules
calendar:       # Calendar inclusion settings
```

## report Section

**Purpose:** Controls report generation and delivery

```yaml
report:
  to: "your-email@company.com"
  subject_template: "Daily Outlook Briefing - {{ timestamp_local }}"
  include_sections:
    - high_priority
    - customers_direct
    - customers_team
    - internal
    - calendar_today
    - overdue_month
  max_items_per_section: 20
  preview_html: "docs/samples/example-summary.html"  # Optional
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to` | string | Yes | Recipient email address (typically your own) |
| `subject_template` | string | Yes | Jinja2 template for email subject line |
| `include_sections` | list | Yes | Which sections to include in report |
| `max_items_per_section` | int | Yes | Maximum emails per section (prevents huge reports) |
| `preview_html` | string | No | Path to save preview HTML (for --dry-run testing) |

### Available Sections

- `high_priority` - VIP senders, urgent keywords, high importance
- `customers_direct` - Direct customer domains
- `customers_team` - Team-managed customer domains
- `internal` - Internal company emails
- `calendar_today` - Today's calendar events
- `overdue_month` - Flagged/unread emails 30+ days old

### Subject Template Variables

- `{{ timestamp_local }}` - Current timestamp in local timezone
- `{{ mode }}` - "morning" or "evening"
- `{{ date }}` - Current date

**Example:**
```yaml
subject_template: "📧 {{ mode|title }} Briefing - {{ date }}"
# Output: "📧 Morning Briefing - 2025-10-27"
```

## behaviour Section

**Purpose:** Controls execution behavior and filtering

```yaml
behaviour:
  only_when_outlook_open: true
  lookback_days_inbox: 2
  overdue_days: 30
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `only_when_outlook_open` | bool | Yes | Exit quietly if Outlook is not running |
| `lookback_days_inbox` | int | Yes | How many days back to scan Inbox/Sent Items |
| `overdue_days` | int | Yes | Threshold for "overdue" items (flagged/unread) |

### Notes

- `lookback_days_inbox` can be overridden with `--since` CLI flag
- `overdue_days` scans last N days for flagged or unread items
- Setting `only_when_outlook_open: false` will cause script to fail if Outlook is closed

## priorities Section

**Purpose:** Defines email prioritization and grouping rules

```yaml
priorities:
  vip_domains:
    - "keycustomer.com"
    - "board.example"

  vip_senders:
    - "ceo@yourcompany.com"
    - "cfo@yourcompany.com"

  ignore_domains:
    - "newsletter.example"
    - "noreply.example"

  downrank_domains:
    - "orders.example"

  group_mappings:
    "globallubricant.com": "Jason's Clients"
    "anothercompany.com": "Sarah's Clients"

  keyword_rules:
    - pattern: "(?i)\\burgent\\b|\\bASAP\\b|\\bimmediate\\b"
      priority: critical
      suggest: "Reply today"

    - pattern: "(?i)\\binvoice\\b|\\bpayment\\b"
      priority: high
      suggest: "Review and respond"

    - pattern: "(?i)\\bmeeting\\b|\\bcalendar\\b|\\binvite\\b"
      priority: high
      suggest: "Confirm or propose time"
```

### vip_domains

**Type:** List of strings
**Purpose:** Domains that always get high priority

**Matching:** Sender email address ends with domain
```python
sender_email = "john@keycustomer.com"
if any(sender_email.endswith(domain) for domain in vip_domains):
    priority_score += 10
```

**Use Case:** Key customers, board members, regulatory contacts

### vip_senders

**Type:** List of strings
**Purpose:** Specific email addresses that get highest priority

**Matching:** Exact email address match
```python
if sender_email in vip_senders:
    priority_score += 15
```

**Use Case:** CEO, CFO, direct manager, key stakeholders

### ignore_domains

**Type:** List of strings
**Purpose:** Domains to exclude from report entirely

**Matching:** Sender email address ends with domain
**Effect:** Email is filtered out during collection

**Use Case:** Newsletters, automated notifications, spam-like senders

### downrank_domains

**Type:** List of strings
**Purpose:** Domains that should be deprioritized

**Matching:** Sender email address ends with domain
**Effect:** Moved to lower priority group

**Use Case:** Orders managed by team inbox, low-priority automated emails

### group_mappings

**Type:** Dictionary (domain → group label)
**Purpose:** Assign specific domains to team members for grouping

**Matching:** Sender email domain
**Effect:** Creates separate sections in report

**Use Case:** Distribute customer accounts among team members

**Example Report Section:**
```
Jason's Clients (3)
- Email from john@globallubricant.com
- Email from sarah@globallubricant.com
```

### keyword_rules

**Type:** List of rule objects
**Purpose:** Pattern matching for urgency detection

**Fields:**
- `pattern` (string, required) - Regex pattern to match in subject/body
- `priority` (string, required) - `critical`, `high`, `medium`, or `low`
- `suggest` (string, optional) - Action suggestion to display

**Pattern Syntax:**
- Use Python regex syntax
- `(?i)` flag for case-insensitive
- `\\b` for word boundaries
- `|` for OR logic

**Priority Values:**
- `critical` - Adds +20 to priority score
- `high` - Adds +10 to priority score
- `medium` - Adds +5 to priority score
- `low` - No change or negative adjustment

**Examples:**
```yaml
# Urgent keywords
- pattern: "(?i)\\burgent\\b|\\bASAP\\b|\\bimmediate\\b|\\bemergency\\b"
  priority: critical
  suggest: "Reply today"

# Invoice/payment tracking
- pattern: "(?i)\\binvoice\\b|\\bpayment\\b|\\boverdue\\b"
  priority: high
  suggest: "Review and respond"

# Meeting coordination
- pattern: "(?i)\\bmeeting\\b|\\bcalendar\\b|\\bschedule\\b"
  priority: high
  suggest: "Confirm or propose time"

# Out of office (downrank)
- pattern: "(?i)out of office|away from desk|on vacation"
  priority: low
  suggest: ""
```

## calendar Section

**Purpose:** Controls calendar item inclusion

```yaml
calendar:
  include_today: true
  include_tomorrow_first_meeting: true
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include_today` | bool | Yes | Include today's calendar events |
| `include_tomorrow_first_meeting` | bool | Yes | Include first meeting of next day (morning briefing only) |

### Behavior

- If `include_tomorrow_first_meeting: true` and mode is `morning`, the first event from tomorrow is added to the report
- If mode is `evening`, only today's events are shown
- Calendar items are sorted by start time

## Priority Scoring Algorithm

### Base Score
```python
if item.importance == 2:  # High
    score = 3
elif item.importance == 0:  # Low
    score = -1
else:  # Normal
    score = 0
```

### Adjustments
```python
# VIP domain
if sender_domain in vip_domains:
    score += 10

# VIP sender
if sender_email in vip_senders:
    score += 15

# Urgent keywords (critical)
if keyword_match and priority == "critical":
    score += 20

# Follow-up flag
if item.is_flagged:
    score += 5

# Unread
if item.is_unread:
    score += 2
```

### Grouping Logic
```python
if score >= 15:
    group = "high_priority"
elif sender_domain in direct_customers:
    group = "customers_direct"
elif sender_domain in group_mappings:
    group = "customers_team"
else:
    group = "internal"
```

## Configuration Loading

**File Detection:**
```python
if config_path.endswith('.yaml') or config_path.endswith('.yml'):
    config = yaml.safe_load(file)
else:
    config = json.load(file)
```

**Validation:**
- Required sections checked at runtime
- Missing fields cause `KeyError` exceptions
- No schema validation yet (future enhancement)

## Command-Line Overrides

### --since Flag
Overrides `behaviour.lookback_days_inbox`

**Examples:**
```bash
# Last 6 hours
python src\run_summary.py --config config\config.yaml --since 6h

# Last 1 day
python src\run_summary.py --config config\config.yaml --since 1d

# Last 3 days
python src\run_summary.py --config config\config.yaml --since 3d
```

### --mode Flag
Overrides automatic mode detection

**Values:**
- `auto` - Detect from current time (default)
- `morning` - Force morning briefing
- `evening` - Force evening briefing
- `force` - Run regardless of scheduler guard

## Security Considerations

### Sensitive Data
- **Never commit** `config.yaml` with real email addresses
- Use `config.template.yaml` with placeholder values
- Add `config/config.yaml` to `.gitignore`

### Example .gitignore
```
config/config.yaml
config/*.local.yaml
```

## Troubleshooting

### Report is empty
- Check `lookback_days_inbox` value (might be too short)
- Verify Outlook has emails in the time range
- Use `--verbose` flag to see collection details

### Too many emails in report
- Reduce `max_items_per_section`
- Reduce `lookback_days_inbox`
- Add more entries to `ignore_domains`

### Wrong grouping
- Check `vip_domains` and `group_mappings` for typos
- Verify domain matching (should be suffix match)
- Use `--dry-run --verbose` to debug priority scores

### Missing calendar events
- Check `calendar.include_today` is `true`
- Verify events exist in Outlook calendar
- Check time zone settings if events appear at wrong times

## Related Documentation

- **Priority Logic:** `src/briefing/prioritiser.py`
- **Collection Logic:** `src/briefing/collector.py`
- **SOP:** `.agent/sops/configuration-changes.md`
- **Example Config:** `config/config.template.yaml`
