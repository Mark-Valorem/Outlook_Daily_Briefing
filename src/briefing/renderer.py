from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import os
import logging
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
                     grouped_emails: Dict[str, List[EmailItem]], 
                     calendar_items: List[CalendarItem],
                     config: Dict[str, Any],
                     mode: str = "morning") -> str:
        
        template = self.env.get_template("report.html.j2")
        
        # Prepare context
        context = {
            "timestamp": datetime.now(),
            "timestamp_local": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": mode,
            "grouped_emails": grouped_emails,
            "calendar_items": calendar_items,
            "config": config,
            "sections": config.get("report", {}).get("include_sections", []),
            "max_items": config.get("report", {}).get("max_items_per_section", 20)
        }
        
        # Count total items
        total_emails = sum(len(items) for items in grouped_emails.values())
        context["total_emails"] = total_emails
        context["total_calendar"] = len(calendar_items)
        
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
                                                    "Daily Outlook Briefing - {{ timestamp_local }}")
        
        # Simple template replacement
        timestamp_local = datetime.now().strftime("%Y-%m-%d %H:%M")
        subject = template_str.replace("{{ timestamp_local }}", timestamp_local)
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