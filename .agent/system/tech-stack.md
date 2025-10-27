# Technology Stack

**version:** v1.0.0

## Platform Requirements

### Operating System
- **Windows 10 or 11** (required)
- No macOS or Linux support (COM automation is Windows-only)

### Python Version
- **Python 3.10+** (required)
- Type hints and dataclasses used throughout
- f-strings and modern Python syntax

### Microsoft Outlook
- **Outlook for Windows** with COM automation support
- Must be running when script executes
- MAPI interface access required
- Office 365 or standalone Outlook for Windows

**Note:** Outlook for Mac does not support COM automation

## Core Dependencies

### pywin32 (>=306)
**Purpose:** Windows COM automation for Outlook

**Key Modules Used:**
- `win32com.client` - COM object creation
- `pythoncom` - COM error handling
- `GetActiveObject()` - Connect to running Outlook
- `CreateItem()` - Create new mail items

**Installation:**
```bash
pip install pywin32>=306
# Or use: python -m pip install pywin32
```

**Common Issues:**
- Some environments require explicit post-install: `python Scripts/pywin32_postinstall.py -install`

### python-dateutil (>=2.9)
**Purpose:** Robust date/time parsing and manipulation

**Usage:**
- Parsing Outlook date/time COM objects
- Relative date calculations (today, yesterday, 30 days ago)
- Timezone-aware datetime handling

### tzlocal (>=5.2)
**Purpose:** Local timezone detection

**Usage:**
- Convert Outlook UTC times to local display times
- Timezone-aware report timestamps
- Calendar event time formatting

### PyYAML (>=6.0)
**Purpose:** YAML configuration file parsing

**Usage:**
- Primary config format: `config/config.yaml`
- Supports JSON as fallback
- Safe loading with `yaml.safe_load()`

**Alternative:** JSON with built-in `json` module

### Jinja2 (>=3.1)
**Purpose:** HTML template rendering

**Usage:**
- Report template: `templates/report.html.j2`
- Supports loops, conditionals, filters
- Auto-escaping for HTML safety

**Template Features:**
- Email grouping sections
- Calendar item formatting
- Priority indicators
- Action suggestions

### rich (>=13.7)
**Purpose:** Enhanced console output (optional)

**Usage:**
- Pretty-print logging during development
- Colored output for dry-run mode
- Table formatting for debug info

**Note:** Optional dependency, can be removed if not needed

## Development Tools

### Version Control
- **Git** - Version control system
- Repository on GitHub
- Conventional commit messages: `docs:`, `feat:`, `fix:`

### Code Editor
- Any Python IDE or text editor
- Recommended: VS Code with Python extension

### Testing Tools
**Current State:** No automated tests (see roadmap)

**Manual Testing:**
- `--dry-run` flag for non-destructive testing
- `--verbose` flag for detailed logging
- Preview HTML output in `docs/samples/example-summary.html`

## Scheduling Technology

### Windows Task Scheduler
**Purpose:** Automated twice-daily execution

**Configuration:**
- Triggers: 08:30 and 16:30, Monday-Friday
- Action: Run Python script with config path
- User context: Logged-in user with Outlook open

**Command Examples:**
```bash
# Morning briefing task
python.exe "C:\path\to\src\run_summary.py" --mode morning --config "C:\path\to\config\config.yaml"

# Evening briefing task
python.exe "C:\path\to\src\run_summary.py" --mode evening --config "C:\path\to\config\config.yaml"
```

**See:** `.agent/sops/scheduling-setup.md` for detailed setup

## File Formats

### Configuration Files
- **YAML** - Primary format (`config.yaml`)
- **JSON** - Alternative format (`.json` extension)

### Templates
- **Jinja2** - HTML template (`.html.j2` extension)

### Output
- **HTML** - Email body (generated, not saved)
- **HTML** - Preview file (optional, for testing)

## Dependencies File

**requirements.txt:**
```
pywin32>=306
python-dateutil>=2.9
tzlocal>=5.2
PyYAML>=6.0
jinja2>=3.1
rich>=13.7
```

**Installation:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Runtime Environment

### Virtual Environment
- **Recommended:** Use `.venv` for isolation
- Create: `python -m venv .venv`
- Activate: `.venv\Scripts\activate`
- Deactivate: `deactivate`

### Environment Variables
- None required (all config in YAML file)

### File Permissions
- Read access to config files
- Read/write access to logs (if logging to file)
- Outlook COM access (user context)

## Windows COM Interface

### MAPI Namespace
**Outlook Object Model Reference:**
- [Outlook Object Model](https://learn.microsoft.com/office/vba/api/overview/outlook/object-model)
- [MailItem Properties](https://learn.microsoft.com/office/vba/api/outlook.mailitem)
- [Items.Restrict Filter Syntax](https://learn.microsoft.com/office/vba/api/outlook.items.restrict)

### Folder Constants
```python
INBOX = 6           # olFolderInbox
SENT_ITEMS = 5      # olFolderSentMail
CALENDAR = 9        # olFolderCalendar
```

### Mail Item Constants
```python
MAIL_ITEM = 0       # olMailItem
IMPORTANCE_HIGH = 2
IMPORTANCE_LOW = 0
```

## Performance Characteristics

### Execution Time
- Typical: 2-5 seconds
- Depends on: Number of emails, Outlook response time

### Memory Usage
- Python process: ~50MB
- Includes pywin32 COM bridge

### Network
- No external API calls
- All communication via local COM to Outlook
- Outlook handles MAPI/Exchange connections

## Security & Privacy

### Data Location
- All processing happens locally on Windows machine
- No cloud services or external APIs
- Configuration file is local

### Access Requirements
- User context with Outlook session
- COM automation permissions (may require IT approval)

### Credentials
- No credentials stored by this script
- Uses existing Outlook session authentication

## Known Limitations

### Platform
- Windows-only (COM automation requirement)
- Cannot run on Linux, macOS, or containers

### Outlook
- Requires Outlook to be running
- Only works with Outlook for Windows (not Outlook for Mac or web)

### COM Errors
- Some Outlook items cause `ReceivedTime` COM errors
- Workaround: Use shorter time ranges (`--since 6h`)

## Future Enhancements (Roadmap)

- Unit tests and integration tests
- GUI for rule editing
- Support for multiple Outlook profiles
- Bundle size optimization
- Alternative scheduling (systemd-like for Windows)

## Related Documentation

- **Architecture:** `.agent/system/architecture.md`
- **Configuration:** `.agent/system/configuration.md`
- **Troubleshooting:** `.agent/sops/troubleshooting-com-errors.md`
- **Setup:** README.md
