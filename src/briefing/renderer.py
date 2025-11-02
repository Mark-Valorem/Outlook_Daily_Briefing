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

        # Get all emails (should all be flagged now)
        all_emails = [email for day_emails in grouped_by_day.values() for email in day_emails]

        # Sort all flagged emails by received time, newest first
        flagged_emails = sorted(all_emails, key=lambda x: -x.received_time.timestamp())

        # Prepare simplified context - no daily groupings, no top 3
        context = {
            "timestamp_local": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": mode,
            "flagged_emails": flagged_emails,
            "total_emails": len(flagged_emails)
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
        # Use fixed subject for 31-day flagged review
        today = datetime.now().strftime("%Y-%m-%d")
        return f"31-day Flagged Email Review – {today}"
        
    @staticmethod
    def _format_time(dt: datetime) -> str:
        return dt.strftime("%H:%M")
        
    @staticmethod
    def _format_date(dt: datetime) -> str:
        return dt.strftime("%d %b %Y")
        
    @staticmethod
    def _truncate_subject(subject: str, max_length: int = 60) -> str:
        if len(subject) <= max_length:
            return subject
        return subject[:max_length-3] + "..."