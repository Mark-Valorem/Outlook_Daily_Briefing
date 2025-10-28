from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import os
import logging
from tzlocal import get_localzone
from .collector import EmailItem, CalendarItem

logger = logging.getLogger(__name__)


class ReportRenderer:
    def __init__(self, template_dir: str = None):
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
            
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # Add custom filters
        self.env.filters['format_time'] = self._format_time
        self.env.filters['format_date'] = self._format_date
        self.env.filters['truncate_subject'] = self._truncate_subject
        
    def render_report(self,
                     grouped_by_day: Dict[str, List[EmailItem]],
                     config: Dict[str, Any],
                     mode: str = "morning") -> str:

        template = self.env.get_template("report.html.j2")

        # Get all emails for Top 3 calculation
        all_emails = [email for day_emails in grouped_by_day.values() for email in day_emails]

        # Top 3 Next Actions: Flagged + High Importance, newest first
        top_3 = [e for e in all_emails if e.is_flagged and e.importance == 2]
        top_3 = sorted(top_3, key=lambda x: -x.received_time.timestamp())[:3]

        # All Flagged Emails: For consolidated block at top, newest first
        flagged_emails = [e for e in all_emails if e.is_flagged]
        flagged_emails = sorted(flagged_emails, key=lambda x: -x.received_time.timestamp())

        # Convert day keys to formatted date strings
        days_formatted = {}
        for day_key, emails in sorted(grouped_by_day.items(), reverse=True):
            date_obj = datetime.strptime(day_key, '%Y-%m-%d').date()
            day_label = date_obj.strftime('%A %d %b %Y')  # "Friday 24 Oct 2025"
            days_formatted[day_label] = emails

        # Prepare context
        context = {
            "timestamp_local": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": mode,
            "grouped_by_day": days_formatted,
            "top_3_actions": top_3,
            "flagged_emails": flagged_emails,
            "max_items_per_day": config.get("report", {}).get("max_items_per_day", 50),
            "total_emails": len(all_emails),
            "total_days": len(grouped_by_day)
        }

        # Render HTML
        html = template.render(**context)

        # Optionally save preview
        preview_path = config.get("report", {}).get("preview_html")
        if preview_path:
            try:
                os.makedirs(os.path.dirname(preview_path), exist_ok=True)
                with open(preview_path, "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info(f"Preview saved to {preview_path}")
            except Exception as e:
                logger.error(f"Failed to save preview: {e}")

        return html
        
    def render_subject(self, config: Dict[str, Any], mode: str = "morning") -> str:
        template_str = config.get("report", {}).get("subject_template",
                                                    "7-day Outlook Smart Review – {{ today }} {{ scheduled_time }}")

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Map mode to scheduled time
        scheduled_time = "09:00" if mode == "morning" else "17:00"

        # Replace template variables
        subject = template_str.replace("{{ today }}", today)
        subject = subject.replace("{{ scheduled_time }}", scheduled_time)
        subject = subject.replace("{{ mode }}", mode.capitalize())

        return subject
        
    @staticmethod
    def _format_time(dt: datetime) -> str:
        return dt.strftime("%H:%M")
        
    @staticmethod
    def _format_date(dt: datetime) -> str:
        return dt.strftime("%d %b")
        
    @staticmethod
    def _truncate_subject(subject: str, max_length: int = 60) -> str:
        if len(subject) <= max_length:
            return subject
        return subject[:max_length-3] + "..."