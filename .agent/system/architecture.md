# System Architecture

**version:** v1.0.0

## Overview

Outlook Daily Briefing is a Windows-based automation system that interfaces with Microsoft Outlook via COM automation to generate prioritized email and calendar briefings twice daily.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Windows Task Scheduler                          │
│       (08:30 & 16:30, Monday-Friday)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ Triggers
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  run_summary.py                              │
│  - Argument parsing (mode, config, dry-run)                 │
│  - Orchestrates workflow                                     │
│  - Error handling and logging                                │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              scheduler_guard.py                              │
│  - Validates execution time windows                          │
│  - Determines mode (morning/evening) from time               │
└────────────┬────────────────────────────────────────────────┘
             │ If should run
             ▼
┌─────────────────────────────────────────────────────────────┐
│              outlook_client.py                               │
│  - COM connection: GetActiveObject("Outlook.Application")   │
│  - MAPI namespace access                                     │
│  - Folder access (Inbox, Sent Items, Calendar)              │
│  - Email sending via Outlook.CreateItem(0)                   │
└────────────┬────────────────────────────────────────────────┘
             │ Connected
             ▼
┌─────────────────────────────────────────────────────────────┐
│              collector.py                                    │
│  - Collects Inbox items (last N days)                       │
│  - Collects Sent Items (last N days)                        │
│  - Collects Calendar items (today + optional tomorrow)      │
│  - Collects overdue items (flagged/unread, 30+ days)        │
│  - Converts COM objects to dataclasses (EmailItem, CalendarItem) │
└────────────┬────────────────────────────────────────────────┘
             │ Raw items
             ▼
┌─────────────────────────────────────────────────────────────┐
│              prioritiser.py                                  │
│  - Applies VIP domain rules                                 │
│  - Applies VIP sender rules                                 │
│  - Keyword pattern matching (urgent, invoice, etc.)         │
│  - Groups items: high_priority, customers_direct,           │
│    customers_team, internal, overdue_month                  │
│  - Assigns priority scores and reasons                       │
└────────────┬────────────────────────────────────────────────┘
             │ Grouped & scored items
             ▼
┌─────────────────────────────────────────────────────────────┐
│              renderer.py                                     │
│  - Loads Jinja2 template (templates/report.html.j2)        │
│  - Renders HTML report with grouped emails + calendar       │
│  - Generates subject line with timestamp                    │
└────────────┬────────────────────────────────────────────────┘
             │ HTML report
             ▼
┌─────────────────────────────────────────────────────────────┐
│          outlook_client.send_email()                         │
│  - Creates MailItem via Outlook COM                         │
│  - Sets recipient, subject, HTMLBody                        │
│  - Sends via mail.Send()                                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Entry Point: run_summary.py
**Responsibility:** Main orchestration and CLI interface

**Key Functions:**
- `setup_logging()` - Configures Python logging
- `load_config()` - Loads YAML/JSON configuration
- `main()` - Orchestrates entire workflow

**Flow:**
1. Parse command-line arguments
2. Check scheduler guard
3. Load configuration
4. Connect to Outlook
5. Collect items
6. Prioritize and group
7. Render report
8. Send or display (dry-run)

### scheduler_guard.py
**Responsibility:** Time-based execution control

**Features:**
- Validates current time is within acceptable briefing windows
- Determines mode (morning/evening) based on time
- Prevents duplicate executions (future enhancement)

### outlook_client.py
**Responsibility:** COM automation interface to Outlook

**Key Methods:**
- `connect()` - Establishes COM connection or exits gracefully
- `get_namespace()` - Returns MAPI namespace
- `get_folder()` - Access Inbox, Sent Items, Calendar
- `send_email()` - Creates and sends email via Outlook

**COM Objects Used:**
- `Outlook.Application` - Main application object
- `Namespace("MAPI")` - MAPI interface
- `GetDefaultFolder(6)` - Inbox
- `GetDefaultFolder(5)` - Sent Items
- `GetDefaultFolder(9)` - Calendar
- `CreateItem(0)` - New MailItem

### collector.py
**Responsibility:** Data collection and transformation

**Key Classes:**
- `EmailItem` - Dataclass for email properties
- `CalendarItem` - Dataclass for calendar properties
- `EmailCollector` - Main collection logic

**Collection Strategy:**
- Uses time-based filters (ReceivedTime >= cutoff)
- Handles COM property access errors gracefully
- Extracts relevant properties from COM objects
- Groups items by source (inbox, sent, calendar, overdue)

**Known Issues:**
- Some Outlook items (drafts, malformed) cause `ReceivedTime` COM errors
- Current workaround: catch and skip problematic items

### prioritiser.py
**Responsibility:** Email scoring and grouping

**Priority Levels:**
1. **Critical** - Urgent keywords, high-importance VIP senders
2. **High** - VIP domains, flagged items, important keywords
3. **Medium** - Direct customers, follow-up requests
4. **Low** - Internal emails, team-managed customers

**Grouping Logic:**
```
high_priority      → VIP domains/senders + urgent keywords
customers_direct   → Direct customer domains
customers_team     → Team-managed customer domains (group_mappings)
internal           → Internal company emails
overdue_month      → Flagged/unread 30+ days old
```

**Score Calculation:**
- Base score from importance (High = +3, Normal = 0, Low = -1)
- VIP domain: +10
- VIP sender: +15
- Urgent keywords: +20
- Follow-up flag: +5
- Unread: +2

### renderer.py
**Responsibility:** HTML report generation

**Template Engine:** Jinja2

**Template Location:** `templates/report.html.j2`

**Data Passed to Template:**
- `grouped_emails` - Dict of email groups
- `calendar_items` - List of CalendarItem objects
- `mode` - morning/evening
- `timestamp` - Report generation time
- `config` - Configuration options

**Output:**
- Styled HTML email with sections for each group
- Calendar events with time/location
- Priority indicators and action suggestions

## Data Flow

```
Outlook (COM)
    ↓
OutlookClient (connects)
    ↓
EmailCollector (fetches items via COM)
    ↓
Raw COM objects → Python dataclasses
    ↓
EmailPrioritiser (applies rules, scores)
    ↓
Grouped dictionaries {group_name: [EmailItem, ...]}
    ↓
ReportRenderer (Jinja2 template)
    ↓
HTML string
    ↓
OutlookClient.send_email() (COM)
    ↓
Sent via Outlook
```

## Error Handling Strategy

1. **Outlook Not Running:** Exit quietly with sys.exit(0)
2. **COM Errors:** Log and skip problematic items, continue processing
3. **Config Errors:** Log error and exit with sys.exit(1)
4. **Unexpected Errors:** Log with traceback, exit with sys.exit(1)

## Security Considerations

- Runs in user context with existing Outlook session
- No credentials stored or transmitted
- Local configuration file only
- No external network calls (except Outlook's own MAPI)
- Sends to configured recipient (default: self)

## Performance Characteristics

- Typical execution time: 2-5 seconds
- Depends on number of emails in lookback window
- COM automation is synchronous (blocking)
- Memory footprint: ~50MB (mostly Python + pywin32)

## Extensibility Points

See `.agent/sops/adding-feature.md` for how to extend:

1. **New priority rules** - Extend `prioritiser.py`
2. **New data sources** - Add methods to `collector.py`
3. **Custom report sections** - Modify template and renderer
4. **Additional schedulers** - Extend `scheduler_guard.py`

## Related Documentation

- **Data Models:** `.agent/system/data-models.md`
- **Configuration:** `.agent/system/configuration.md`
- **Tech Stack:** `.agent/system/tech-stack.md`
- **Adding Features:** `.agent/sops/adding-feature.md`
