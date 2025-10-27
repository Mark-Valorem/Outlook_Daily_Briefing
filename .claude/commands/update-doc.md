# Update Documentation Command

**version:** v1.0.0

## Purpose
Automate creation and maintenance of the .agent documentation system with version control and archival management.

## Commands

### Initialize (Already Complete)
This command has been run to set up the initial structure.

### Update After Feature Implementation
```
/update-doc
```

**Actions:**
1. Review recent conversation for completed work
2. If implementation plan exists, save to `tasks/[feature-name].md` with incremented version
3. Identify repeatable processes, create/update SOPs in `sops/` with version updates
4. Update `.agent/README.md` and increment version number
5. Update `CLAUDE.md` version if significant changes made
6. Move any unused files/folders to `archive/` preserving directory structure
7. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "docs: update documentation system to v${version}"
   git push origin main
   ```

### Generate Specific SOP
```
/update-doc generate SOP for [process name]
```

**Actions:**
1. Create SOP document in `sops/[process-name].md` with version v1.0.0
2. Include:
   - **When to Use** - Trigger conditions
   - **Prerequisites** - Required setup or tools
   - **Step-by-Step Instructions** - Numbered, actionable steps
   - **Related Documentation** - Cross-references to system docs
   - **Common Mistakes and Pitfalls** - Known issues and how to avoid
   - **Examples** - Code snippets or command examples when helpful
   - **Troubleshooting** - Error scenarios and solutions
3. Update `.agent/README.md` index and increment its version
4. Move any deprecated docs to `archive/[timestamp]/`
5. Commit and push changes to GitHub

## SOP Document Structure Template

```markdown
# SOP: [Process Name]

**version:** v1.0.0

## When to Use
[Description of when this SOP applies]

## Prerequisites
- [Required tools, access, or setup]

## Steps

1. [First step with specific commands or actions]
2. [Second step]
   - [Sub-step if needed]
3. [Continue...]

## Related Documentation
- [Links to .agent/system/ docs]
- [Links to other relevant SOPs]

## Common Mistakes
- **Mistake:** [Description]
  - **Solution:** [How to fix or avoid]

## Examples

### Example 1: [Scenario Name]
\`\`\`bash
# Command examples
\`\`\`

## Troubleshooting

**Issue:** [Problem description]
- **Cause:** [Root cause]
- **Solution:** [Steps to resolve]
```

## Rules for Creating Documentation

### Content Guidelines
- Keep documentation concise and action-oriented
- Use markdown formatting for readability
- Include specific file paths and command examples (use Windows paths with backslashes)
- Cross-reference related documentation within `.agent/`
- Add version headers to all documentation files

### File Management
- Archive outdated or unused files to `/archive/[timestamp]/`
- Preserve directory structure when archiving
- Never delete files - always archive instead
- Document what was archived and why in commit message

### Version Control
- Use semantic versioning (v1.0.0, v1.1.0, v2.0.0)
- Increment patch version (v1.0.X) for minor doc updates
- Increment minor version (v1.X.0) for new SOPs or system docs
- Increment major version (vX.0.0) for restructuring or breaking changes
- Commit and push changes after each `/update-doc` execution

### Git Commit Messages
- Use conventional commit format: `docs: description`
- Include version number in message: `docs: update documentation system to v1.2.0`
- List major changes in commit body if significant
- Reference archived files if applicable

## Version History

- **v1.0.0** - Initial documentation system setup with all core files

## Examples

### Update After Feature Implementation

**Scenario:** You just implemented a new email filtering feature.

```
/update-doc
```

**Expected Actions:**
1. Creates `tasks/email-filtering-feature.md` documenting the implementation
2. Updates `sops/adding-feature.md` if new patterns were discovered
3. Increments `.agent/README.md` to v1.1.0
4. Commits: `docs: update documentation system to v1.1.0`

### Create New SOP

**Scenario:** You discovered a new troubleshooting procedure for COM errors.

```
/update-doc generate SOP for COM error recovery
```

**Expected Actions:**
1. Creates `sops/com-error-recovery.md` at v1.0.0
2. Updates `.agent/README.md` index to v1.2.0
3. Commits: `docs: add SOP for COM error recovery to v1.2.0`

## Notes

- Always run this command after completing significant work
- The command automates both documentation updates AND version control
- Archives are timestamped to track when files were deprecated
- Never skip the git push step - keeps remote repository in sync
