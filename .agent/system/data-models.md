# Data Models

**version:** v1.0.0

## Overview

The Outlook Daily Briefing uses Python dataclasses to represent emails and calendar items. These dataclasses provide type safety, immutability, and clean interfaces for the prioritization and rendering pipeline.

**Location:** `src/briefing/collector.py`

## EmailItem

**Purpose:** Represents a single email message from Inbox or Sent Items

**Definition:**
```python
@dataclass
class EmailItem:
    entry_id: str
    subject: str
    sender_name: str
    sender_email: str
    received_time: datetime
    importance: int
    is_flagged: bool
    is_unread: bool
    has_attachments: bool
    categories: List[str] = field(default_factory=list)
    folder_name: str = "Inbox"
    body_preview: str = ""
    priority_score: int = 0
    priority_reason: str = ""
    group_label: str = ""
```

### Field Descriptions

#### Core Properties (from Outlook COM)

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `entry_id` | `str` | Unique Outlook item ID | `item.EntryID` |
| `subject` | `str` | Email subject line | `item.Subject` |
| `sender_name` | `str` | Display name of sender | `item.SenderName` |
| `sender_email` | `str` | Email address of sender | `item.SenderEmailAddress` |
| `received_time` | `datetime` | When email was received | `item.ReceivedTime` |
| `importance` | `int` | Outlook importance level | `item.Importance` |
| `is_flagged` | `bool` | Has follow-up flag | `item.FlagRequest != ""` |
| `is_unread` | `bool` | Unread status | `item.UnRead` |
| `has_attachments` | `bool` | Contains attachments | `item.Attachments.Count > 0` |
| `categories` | `List[str]` | Outlook categories | `item.Categories.split(',')` |
| `folder_name` | `str` | Source folder | "Inbox" or "Sent Items" |
| `body_preview` | `str` | First 200 chars of body | `item.Body[:200]` |

#### Prioritization Properties (computed)

| Field | Type | Description | Set By |
|-------|------|-------------|--------|
| `priority_score` | `int` | Calculated priority (0-50+) | `EmailPrioritiser` |
| `priority_reason` | `str` | Human-readable reason | `EmailPrioritiser` |
| `group_label` | `str` | Group classification | `EmailPrioritiser` |

### Importance Levels (Outlook Constants)

```python
0 = Low
1 = Normal (default)
2 = High
```

### Example Usage

```python
# Creating an EmailItem from Outlook COM object
item = EmailItem(
    entry_id=outlook_item.EntryID,
    subject=outlook_item.Subject,
    sender_name=outlook_item.SenderName,
    sender_email=outlook_item.SenderEmailAddress,
    received_time=outlook_item.ReceivedTime,
    importance=outlook_item.Importance,
    is_flagged=(outlook_item.FlagRequest != ""),
    is_unread=outlook_item.UnRead,
    has_attachments=(outlook_item.Attachments.Count > 0),
    folder_name="Inbox"
)

# After prioritization
item.priority_score = 25
item.priority_reason = "VIP domain + urgent keyword"
item.group_label = "high_priority"
```

## CalendarItem

**Purpose:** Represents a single calendar event or meeting

**Definition:**
```python
@dataclass
class CalendarItem:
    entry_id: str
    subject: str
    start_time: datetime
    end_time: datetime
    location: str
    organizer: str
    is_all_day: bool
    is_recurring: bool
    attendees_count: int
    response_status: int
    body_preview: str = ""
```

### Field Descriptions

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `entry_id` | `str` | Unique Outlook item ID | `item.EntryID` |
| `subject` | `str` | Meeting/event title | `item.Subject` |
| `start_time` | `datetime` | Start date/time | `item.Start` |
| `end_time` | `datetime` | End date/time | `item.End` |
| `location` | `str` | Meeting location | `item.Location` |
| `organizer` | `str` | Organizer name | `item.Organizer` |
| `is_all_day` | `bool` | All-day event flag | `item.AllDayEvent` |
| `is_recurring` | `bool` | Recurring event flag | `item.IsRecurring` |
| `attendees_count` | `int` | Number of attendees | `item.Recipients.Count` |
| `response_status` | `int` | User's response status | `item.ResponseStatus` |
| `body_preview` | `str` | First 200 chars of body | `item.Body[:200]` |

### Response Status Values

```python
0 = None (no response)
1 = Organizer
2 = Tentative
3 = Accepted
4 = Declined
5 = Not Responded
```

### Example Usage

```python
# Creating a CalendarItem from Outlook COM object
item = CalendarItem(
    entry_id=outlook_item.EntryID,
    subject=outlook_item.Subject,
    start_time=outlook_item.Start,
    end_time=outlook_item.End,
    location=outlook_item.Location or "",
    organizer=outlook_item.Organizer,
    is_all_day=outlook_item.AllDayEvent,
    is_recurring=outlook_item.IsRecurring,
    attendees_count=outlook_item.Recipients.Count,
    response_status=outlook_item.ResponseStatus
)
```

## Data Transformation Pipeline

### Stage 1: Collection (collector.py)
```
Outlook COM Objects
        ↓
EmailCollector.collect_all()
        ↓
Dict[str, List[EmailItem | CalendarItem]]
```

**Structure:**
```python
{
    'inbox': [EmailItem, EmailItem, ...],
    'sent': [EmailItem, EmailItem, ...],
    'calendar_today': [CalendarItem, CalendarItem, ...],
    'calendar_tomorrow': [CalendarItem, ...],
    'overdue': [EmailItem, ...]
}
```

### Stage 2: Prioritization (prioritiser.py)
```
List[EmailItem]
        ↓
EmailPrioritiser.prioritise_and_group()
        ↓
Dict[str, List[EmailItem]]
```

**Structure:**
```python
{
    'high_priority': [EmailItem, ...],
    'customers_direct': [EmailItem, ...],
    'customers_team': [EmailItem, ...],
    'internal': [EmailItem, ...],
    'overdue_month': [EmailItem, ...]
}
```

**Note:** Each `EmailItem` is mutated to include:
- `priority_score`
- `priority_reason`
- `group_label`

### Stage 3: Rendering (renderer.py)
```
Dict[str, List[EmailItem]] + List[CalendarItem]
        ↓
ReportRenderer.render_report()
        ↓
HTML string
```

## Known Issues with COM Objects

### ReceivedTime Error

**Symptom:**
```
ERROR - Error converting mail item: <unknown>.ReceivedTime
```

**Cause:**
- Certain Outlook item types (drafts, meeting requests, corrupted items)
- Malformed timestamps or COM access issues

**Current Handling:**
- Try-except block in `EmailCollector._convert_mail_item()`
- Log error and skip problematic item
- Continue processing remaining items

**Impact:**
- One or more emails may be skipped
- Report generation continues successfully

**Workaround:**
```bash
# Use shorter time ranges to avoid problematic items
python src\run_summary.py --config config\config.yaml --since 6h --dry-run
```

**See:** `.agent/sops/troubleshooting-com-errors.md`

## Type Hints and Validation

### Type Safety
All dataclass fields use type hints for IDE support and runtime validation.

### Default Values
- `categories: List[str] = field(default_factory=list)` - Empty list by default
- `folder_name: str = "Inbox"` - Defaults to Inbox
- `body_preview: str = ""` - Empty string by default

### Immutability
Dataclasses are mutable by default. To make immutable, use:
```python
@dataclass(frozen=True)
class EmailItem:
    ...
```

**Current State:** Mutable (to allow prioritizer to set scores)

## Future Enhancements

### Planned Additions
- `attachment_names: List[str]` - List of attachment filenames
- `conversation_id: str` - Thread grouping
- `sla_deadline: Optional[datetime]` - Per-sender SLA tracking
- `sentiment: str` - Message tone analysis

### Validation
- Add `__post_init__` validation for required fields
- Validate email address format
- Validate datetime ranges

## Related Documentation

- **Architecture:** `.agent/system/architecture.md`
- **Collection Logic:** `src/briefing/collector.py`
- **Prioritization Logic:** `src/briefing/prioritiser.py`
- **Outlook Object Model:** [Microsoft Docs](https://learn.microsoft.com/office/vba/api/overview/outlook/object-model)
