# CLAUDE.md - AI Agent Guide for Outlook Daily Briefing

**version:** v1.0.0

## Documentation Structure

This project uses the `.agent/` folder system for AI agent context management:

- **`.agent/README.md`** - Index of all documentation with quick links
- **`.agent/system/`** - Architecture, data models, tech stack, configuration
- **`.agent/sops/`** - Standard operating procedures for common tasks
- **`.agent/tasks/`** - Feature implementation documentation and plans
- **`archive/`** - Deprecated files and unused code

## Rules for AI Agent

1. **Before planning implementations:** Always read `.agent/README.md` and relevant system docs
2. **After implementing features:** Update or create task documentation in `.agent/tasks/[feature-name].md`
3. **When correcting mistakes:** Generate or update SOPs in `.agent/sops/` to prevent recurrence
4. **For research-heavy features:** Use sub-agents to explore the codebase efficiently
5. **Update documentation versions:** Increment version numbers when making significant doc changes
6. **Archive unused files:** Move deprecated or unused files to `archive/` rather than deleting

## Code Style Guidelines

**Python Conventions:**
- Use Python 3.10+ features (type hints, dataclasses)
- Follow PEP 8 style guidelines
- Use `dataclass` for data structures (see `EmailItem`, `CalendarItem`)
- Type hints required for function signatures
- Docstrings for public classes and methods

**Logging:**
- Use Python `logging` module, not print statements
- Logger naming: `logger = logging.getLogger(__name__)`
- Log levels: DEBUG for detailed traces, INFO for operations, WARNING for issues, ERROR for failures

**Error Handling:**
- Graceful degradation for COM automation errors
- Exit quietly (sys.exit(0)) when Outlook is not running
- Log exceptions with `exc_info=True` for debugging

**Configuration:**
- Support both YAML and JSON config files
- Validate config structure at load time
- Provide sensible defaults in code

## Testing Requirements

**Current State:** No automated tests exist (see README roadmap)

**Testing Approach:**
- Use `--dry-run` flag to test without sending emails
- Review generated HTML in `docs/samples/example-summary.html`
- Test with various `--since` time ranges (e.g., `6h`, `1d`)
- Validate against different Outlook item types

**Future:** Unit tests and integration tests planned (see README)

## Common Commands

```bash
# Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Test run (no email sent)
python src\run_summary.py --config config\config.yaml --dry-run

# Morning briefing
python src\run_summary.py --config config\config.yaml --mode morning

# Evening briefing
python src\run_summary.py --config config\config.yaml --mode evening

# Custom time range
python src\run_summary.py --config config\config.yaml --since 6h --dry-run

# Update documentation
/update-doc
```

## Project-Specific Conventions

**Windows Platform:**
- This project is Windows-only (requires COM automation)
- Use Windows path separators in documentation examples
- Task scheduling via Windows Task Scheduler

**COM Automation:**
- Always use `GetActiveObject` to connect to running Outlook
- Handle `pythoncom.com_error` for graceful exits
- Never start Outlook programmatically

**Configuration Management:**
- Primary config: `config/config.yaml`
- Template: `config/config.template.yaml`
- Never commit personal email addresses or sensitive data

**Known Issues:**
- ReceivedTime COM error for certain Outlook items (see `.agent/sops/troubleshooting-com-errors.md`)
- Use shorter time ranges (`--since 6h`) to avoid problematic items

## Entry Points

- **Main script:** `src/run_summary.py`
- **Core modules:** `src/briefing/` (outlook_client, collector, prioritiser, renderer, scheduler_guard)
- **Templates:** `templates/report.html.j2`
- **Configuration:** `config/config.yaml`

## Workflow for Feature Implementation

1. Read relevant `.agent/system/` documentation
2. Review existing code patterns in `src/briefing/`
3. Update dataclasses in `collector.py` if new fields needed
4. Test with `--dry-run` before live execution
5. Update `.agent/tasks/` with implementation notes
6. Run `/update-doc` to refresh documentation

## References

- See `.agent/README.md` for comprehensive documentation index
- See README.md for detailed setup and usage instructions
- See `.agent/sops/` for step-by-step procedures
