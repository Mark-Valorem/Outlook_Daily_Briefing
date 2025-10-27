# SOP: Adding a New Feature

**version:** v1.0.0

## When to Use

Use this SOP when adding new functionality to the Outlook Daily Briefing system, such as:
- New priority rules or scoring logic
- Additional data collection from Outlook
- New report sections or formatting
- Integration with external services
- Enhanced filtering or grouping

## Prerequisites

- Python 3.10+ development environment
- Project dependencies installed (`pip install -r requirements.txt`)
- Familiarity with the codebase structure (read `.agent/system/architecture.md`)
- Outlook for Windows running (for testing)
- Git repository access

## Steps

### 1. Research and Planning

Read relevant documentation:
```bash
# Understand the architecture
Read: .agent/system/architecture.md

# Understand data models
Read: .agent/system/data-models.md

# Review existing code patterns
Read: src/briefing/*.py
```

**Questions to Answer:**
- Which module(s) need modification? (collector, prioritiser, renderer, etc.)
- Do data models need new fields?
- Does configuration need new settings?
- Will this affect the report template?

### 2. Update Configuration Schema (if needed)

If your feature requires new configuration options:

**File:** `config/config.template.yaml`

**Steps:**
1. Add new configuration section or fields
2. Document the field purpose and type in comments
3. Provide example values

**Example:**
```yaml
# New feature: sentiment analysis
sentiment:
  enabled: true
  threshold: 0.7
  keywords_positive:
    - "thank you"
    - "appreciate"
  keywords_negative:
    - "disappointed"
    - "frustrated"
```

### 3. Update Data Models (if needed)

If your feature requires new data fields:

**File:** `src/briefing/collector.py`

**Steps:**
1. Add new fields to `EmailItem` or `CalendarItem` dataclass
2. Include type hints
3. Provide default values if optional
4. Update docstring

**Example:**
```python
@dataclass
class EmailItem:
    # ... existing fields ...

    # New field for sentiment analysis
    sentiment_score: float = 0.0
    sentiment_label: str = ""
```

### 4. Implement Collection Logic (if needed)

If your feature collects new data from Outlook:

**File:** `src/briefing/collector.py`

**Add Method to EmailCollector:**
```python
def collect_new_data_source(self, config: Dict[str, Any]) -> List[DataType]:
    """
    Collect new data from Outlook.

    Args:
        config: Configuration dictionary

    Returns:
        List of DataType items
    """
    try:
        # Access Outlook folder or data source
        folder = self.outlook.get_folder(folder_id)

        # Filter and collect items
        items = folder.Items
        filtered = items.Restrict(filter_string)

        # Convert to dataclass
        results = []
        for item in filtered:
            results.append(self._convert_to_dataclass(item))

        return results

    except Exception as e:
        logger.error(f"Error collecting new data: {e}")
        return []
```

### 5. Implement Prioritization Logic (if needed)

If your feature affects email scoring or grouping:

**File:** `src/briefing/prioritiser.py`

**Add Method to EmailPrioritiser:**
```python
def _apply_new_rule(self, item: EmailItem, config: Dict) -> int:
    """
    Apply new prioritization rule.

    Args:
        item: Email item to score
        config: Configuration dictionary

    Returns:
        Additional score points
    """
    score = 0

    # Your logic here
    if self._check_new_condition(item, config):
        score += 10
        item.priority_reason += " + new rule match"

    return score
```

**Integrate into `_calculate_priority_score()`:**
```python
def _calculate_priority_score(self, item: EmailItem, config: Dict) -> int:
    # ... existing logic ...

    # Add new rule
    score += self._apply_new_rule(item, config)

    return score
```

### 6. Update Report Template (if needed)

If your feature adds new display elements:

**File:** `templates/report.html.j2`

**Add Template Section:**
```jinja2
{% if new_section_items %}
<div class="section">
  <h2>New Section ({{ new_section_items|length }})</h2>
  {% for item in new_section_items %}
  <div class="email-item">
    <strong>{{ item.subject }}</strong>
    <p>{{ item.new_field_display }}</p>
  </div>
  {% endfor %}
</div>
{% endif %}
```

### 7. Update Renderer (if needed)

If template needs new data:

**File:** `src/briefing/renderer.py`

**Modify `render_report()` to pass new data:**
```python
def render_report(self, grouped_emails, calendar_items, config, mode):
    # ... existing code ...

    # Add new data for template
    template_data = {
        # ... existing data ...
        'new_section_items': self._process_new_section(grouped_emails),
    }

    return self.template.render(**template_data)
```

### 8. Test with Dry Run

**Command:**
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run with dry-run to test without sending email
python src\run_summary.py --config config\config.yaml --dry-run --verbose

# Test with short time range to limit data
python src\run_summary.py --config config\config.yaml --dry-run --since 6h
```

**What to Check:**
- No Python exceptions or errors
- New feature logic executes correctly
- Log messages show expected behavior
- Preview HTML (if configured) displays correctly

### 9. Test with Real Execution

**Command:**
```bash
# Send real email to yourself
python src\run_summary.py --config config\config.yaml --mode morning
```

**What to Check:**
- Email arrives successfully
- New feature data appears in email
- Formatting is correct
- No errors in console

### 10. Update Documentation

**Actions:**
1. Document the new feature in `.agent/tasks/[feature-name].md`
2. Update `.agent/system/architecture.md` if architecture changed
3. Update `.agent/system/configuration.md` if new config options added
4. Update `CLAUDE.md` if development workflow changed
5. Update main `README.md` with user-facing changes

**Run:**
```bash
/update-doc
```

### 11. Commit Changes

**Command:**
```bash
git add .
git commit -m "feat: add [feature name]

- Describe what was added
- List affected modules
- Note any breaking changes"
git push origin main
```

## Related Documentation

- **Architecture:** `.agent/system/architecture.md`
- **Data Models:** `.agent/system/data-models.md`
- **Configuration:** `.agent/system/configuration.md`
- **Testing:** `.agent/sops/running-tests.md`

## Common Mistakes

### Mistake: Not testing with dry-run first
**Solution:** Always use `--dry-run` before sending real emails. This prevents sending malformed or incorrect reports.

### Mistake: Forgetting to update config.template.yaml
**Solution:** If you add new config fields, update the template so other users know what options are available.

### Mistake: Not handling COM errors gracefully
**Solution:** Wrap Outlook COM calls in try-except blocks and log errors. COM can fail for various reasons (item access, property errors, etc.).

### Mistake: Hard-coding values instead of using config
**Solution:** Make new features configurable via `config.yaml` rather than hard-coding values in the code.

### Mistake: Not updating documentation
**Solution:** Run `/update-doc` after completing the feature to keep documentation in sync.

## Examples

### Example 1: Add "Attachment Count" Display

**Step 1:** EmailItem already has `has_attachments` field, but we want count.

**Modify data model:**
```python
@dataclass
class EmailItem:
    # ... existing ...
    attachment_count: int = 0
```

**Step 2:** Update collection logic:
```python
# In collector.py _convert_mail_item()
attachment_count=outlook_item.Attachments.Count,
```

**Step 3:** Update template:
```jinja2
{% if item.attachment_count > 0 %}
  📎 {{ item.attachment_count }} attachment(s)
{% endif %}
```

**Step 4:** Test with dry-run and commit.

### Example 2: Add "Reply Time SLA" Feature

**Step 1:** Add config:
```yaml
# config.yaml
sla:
  vip_reply_hours: 4
  normal_reply_hours: 24
```

**Step 2:** Add field to EmailItem:
```python
sla_deadline: Optional[datetime] = None
is_sla_overdue: bool = False
```

**Step 3:** Implement in prioritiser:
```python
def _calculate_sla_deadline(self, item: EmailItem, config: Dict):
    if item.sender_email in config['priorities']['vip_senders']:
        hours = config.get('sla', {}).get('vip_reply_hours', 4)
    else:
        hours = config.get('sla', {}).get('normal_reply_hours', 24)

    item.sla_deadline = item.received_time + timedelta(hours=hours)
    item.is_sla_overdue = datetime.now() > item.sla_deadline
```

**Step 4:** Update template to show SLA status with color coding.

**Step 5:** Test and commit.

## Troubleshooting

### Issue: COM error when accessing new Outlook property
**Cause:** Not all Outlook items support all properties
**Solution:** Use try-except around property access and provide default values

**Example:**
```python
try:
    value = outlook_item.NewProperty
except AttributeError:
    value = None
```

### Issue: Template rendering error
**Cause:** New template variable not passed from renderer
**Solution:** Check `render_report()` passes all required data to template

### Issue: Feature works in dry-run but fails when sending email
**Cause:** HTML rendering issue or email size too large
**Solution:** Check generated HTML validity, reduce `max_items_per_section`

## Notes

- Always read the architecture doc before starting
- Test incrementally (collection → prioritization → rendering)
- Use `--verbose` flag to see detailed logging
- Keep features configurable rather than hard-coded
- Document as you go (don't wait until the end)
