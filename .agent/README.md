# .agent Documentation Index

**version:** v1.0.0

## Purpose

This directory contains comprehensive documentation for the Outlook Daily Briefing project, organized for optimal AI agent context management. The documentation is structured to help both human developers and AI assistants understand the system, implement features, and resolve issues efficiently.

## Documentation Structure

```
.agent/
├── README.md                         # This file - documentation index
├── system/                           # System architecture and technical details
│   ├── architecture.md              # System design, data flow, component interactions
│   ├── tech-stack.md                # Technology dependencies and requirements
│   ├── data-models.md               # EmailItem and CalendarItem dataclasses
│   └── configuration.md             # Config file structure and options
├── sops/                            # Standard Operating Procedures
│   ├── adding-feature.md            # How to implement new features
│   ├── running-tests.md             # Manual testing procedures (no automated tests yet)
│   ├── configuration-changes.md     # How to modify config.yaml
│   ├── scheduling-setup.md          # Windows Task Scheduler setup
│   └── troubleshooting-com-errors.md # COM automation error handling
└── tasks/                           # Feature implementation documentation
    └── (Task files will be created as features are implemented)
```

## Quick Links

### System Documentation

| Document | Description | When to Read |
|----------|-------------|--------------|
| [architecture.md](system/architecture.md) | System design, data flow, module interactions | Before implementing features |
| [tech-stack.md](system/tech-stack.md) | Python dependencies, Windows requirements | During setup or debugging |
| [data-models.md](system/data-models.md) | EmailItem and CalendarItem structures | When modifying data collection |
| [configuration.md](system/configuration.md) | Config file reference and priority rules | When changing behavior or rules |

### Standard Operating Procedures (SOPs)

| SOP | Description | When to Use |
|-----|-------------|-------------|
| [adding-feature.md](sops/adding-feature.md) | Step-by-step feature implementation guide | Implementing new functionality |
| [running-tests.md](sops/running-tests.md) | Manual testing with dry-run and validation | Testing changes before deployment |
| [configuration-changes.md](sops/configuration-changes.md) | How to modify rules and settings | Adding VIP domains, keyword rules |
| [scheduling-setup.md](sops/scheduling-setup.md) | Windows Task Scheduler configuration | Setting up automated briefings |
| [troubleshooting-com-errors.md](sops/troubleshooting-com-errors.md) | Handling Outlook COM automation errors | Debugging ReceivedTime errors, etc. |

### Tasks

Task documentation will be created automatically via `/update-doc` after feature implementations.

**Directory:** `.agent/tasks/`

**Naming Convention:** `[feature-name].md` (e.g., `sentiment-analysis-feature.md`)

**Purpose:** Document implementation details, decisions, and lessons learned for each feature.

## Project Overview

**Outlook Daily Briefing** is a Windows-based Python automation tool that:
- Connects to Outlook via COM automation (Windows-only)
- Collects and prioritizes emails from Inbox and Sent Items
- Includes calendar events for today (and tomorrow's first meeting in morning mode)
- Generates HTML reports using Jinja2 templates
- Sends briefings twice daily (8:30 AM and 4:30 PM) via Windows Task Scheduler

**Key Technologies:**
- Python 3.10+ (dataclasses, type hints)
- pywin32 (COM automation)
- Jinja2 (HTML templating)
- PyYAML (configuration)
- Windows Task Scheduler

**Current State:**
- No automated tests (manual testing with --dry-run)
- No database or web API
- No GUI (CLI only)
- See README.md roadmap for planned enhancements

## AI Agent Workflow

### For New Features

1. **Read** `.agent/system/architecture.md` to understand system design
2. **Read** `.agent/system/data-models.md` if modifying data structures
3. **Follow** `.agent/sops/adding-feature.md` step-by-step
4. **Test** using `.agent/sops/running-tests.md` procedures
5. **Document** by running `/update-doc` to create task documentation

### For Configuration Changes

1. **Read** `.agent/system/configuration.md` for config reference
2. **Follow** `.agent/sops/configuration-changes.md` for specific changes
3. **Test** with dry-run before deploying

### For Troubleshooting

1. **Check** `.agent/sops/troubleshooting-com-errors.md` for COM issues
2. **Use** verbose logging: `--verbose` flag
3. **Review** known issues section in README.md

### For Scheduling Setup

1. **Follow** `.agent/sops/scheduling-setup.md` for Windows Task Scheduler
2. **Test** manually before automating

## Documentation Statistics

**Last Updated:** October 27, 2025
**Version:** v1.0.0
**Total Documents:** 11

### By Category
- **System Docs:** 4 files
- **SOPs:** 5 files
- **Tasks:** 0 files (will grow as features are implemented)
- **Commands:** 1 file (update-doc.md)
- **Root:** 1 file (CLAUDE.md)

## Maintenance

### Updating Documentation

After implementing features or fixing issues:

```bash
/update-doc
```

This command will:
1. Review recent work
2. Create or update task documentation
3. Update or create SOPs for repeatable processes
4. Increment version numbers
5. Commit and push changes to Git

### Creating New SOPs

When you discover a new repeatable process:

```bash
/update-doc generate SOP for [process name]
```

This will:
1. Create new SOP in `.agent/sops/`
2. Update this README index
3. Increment version
4. Commit and push changes

### Version Control

- Documentation uses semantic versioning (v1.0.0, v1.1.0, etc.)
- Increment patch version (v1.0.X) for minor doc updates
- Increment minor version (v1.X.0) for new docs or significant updates
- Increment major version (vX.0.0) for restructuring

## File Locations

### Configuration
- **Main:** `config/config.yaml`
- **Template:** `config/config.template.yaml`

### Source Code
- **Entry point:** `src/run_summary.py`
- **Modules:** `src/briefing/*.py`

### Templates
- **Report:** `templates/report.html.j2`

### Documentation
- **Main README:** `README.md` (project root)
- **AI Guide:** `CLAUDE.md` (project root)
- **Agent Docs:** `.agent/` (this directory)

## Common Questions

### Q: Where do I start as a new developer?
**A:** Read this README, then `CLAUDE.md`, then `.agent/system/architecture.md`

### Q: How do I add a new VIP domain?
**A:** Follow `.agent/sops/configuration-changes.md` → "Add New VIP Domain"

### Q: How do I test my changes?
**A:** Follow `.agent/sops/running-tests.md` → start with dry-run tests

### Q: What if I get a ReceivedTime COM error?
**A:** See `.agent/sops/troubleshooting-com-errors.md` → "Error 1: ReceivedTime Property Access Error"

### Q: How do I set up automated scheduling?
**A:** Follow `.agent/sops/scheduling-setup.md` → "Method 1: GUI Setup"

### Q: Where are the automated tests?
**A:** No automated tests exist yet (see README roadmap). Use manual testing procedures in `.agent/sops/running-tests.md`

## Related Resources

### External Documentation
- [Outlook Object Model Reference](https://learn.microsoft.com/office/vba/api/overview/outlook/object-model)
- [Items.Restrict Filter Syntax](https://learn.microsoft.com/office/vba/api/outlook.items.restrict)
- [MailItem Properties](https://learn.microsoft.com/office/vba/api/outlook.mailitem)
- [pywin32 Documentation](https://pywin32.readthedocs.io)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)

### Project Files
- **Main README:** `../README.md`
- **CLAUDE Guide:** `../CLAUDE.md`
- **License:** `../LICENSE`
- **Requirements:** `../requirements.txt`

## Contributing to Documentation

When creating or updating documentation:

1. **Use consistent formatting:**
   - Markdown headers for sections
   - Code blocks for examples
   - Tables for reference data

2. **Include version headers:**
   ```markdown
   # Document Title

   **version:** v1.0.0
   ```

3. **Cross-reference related docs:**
   - Link to other `.agent/` documents
   - Reference specific files with paths
   - Use "See also" sections

4. **Provide examples:**
   - Code snippets
   - Command examples
   - Expected outputs

5. **Update this README index:**
   - Add new documents to Quick Links
   - Update statistics
   - Increment version

6. **Commit with conventional commits:**
   ```bash
   git commit -m "docs: add SOP for [topic]"
   ```

## Archive

Unused or deprecated files are moved to `../archive/` rather than deleted, preserving project history and allowing recovery if needed.

**Archive Location:** `../archive/`

## Contact & Support

- **Issues:** Report bugs or request features via GitHub issues
- **Documentation:** This `.agent/` directory is the source of truth
- **Updates:** Use `/update-doc` command to maintain documentation

---

*This documentation system was implemented to optimize AI agent context management and improve developer onboarding. For questions or suggestions, please open an issue.*
