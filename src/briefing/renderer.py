from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import os
import logging
from tzlocal import get_localzone
from .collector import EmailItem, CalendarItem

logger = logging.getLogger(__name__)


class ReportRenderer:
    def __init__(self, template_dir: str = None, config: Dict[str, Any] = None):
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")

        self.config = config
        self.email_color_map = self._build_email_color_map(config)

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False  # Changed to False since we're manually creating safe HTML
        )

        # Add custom filters
        self.env.filters['format_time'] = self._format_time
        self.env.filters['format_date'] = self._format_date
        self.env.filters['truncate_subject'] = self._truncate_subject
        self.env.filters['email_color'] = self._email_color_filter
        
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

    def _build_email_color_map(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Build a mapping of email addresses/domains to colors.

        Args:
            config: Configuration dict containing email_categories section

        Returns:
            Dict mapping email addresses and domains to hex color codes
        """
        color_map = {}

        if not config or 'email_categories' not in config:
            return color_map

        categories = config['email_categories']

        # Process each category
        for category_name, category_data in categories.items():
            color = category_data.get('color', '#3B3B3B')

            # Add specific email addresses (e.g., vip_senders)
            if 'addresses' in category_data:
                for address in category_data['addresses']:
                    color_map[address.lower()] = color

            # Add domains (e.g., critical_customers)
            if 'domains' in category_data:
                for domain in category_data['domains']:
                    color_map[domain.lower()] = color

        logger.debug(f"Built email color map with {len(color_map)} entries")
        return color_map

    def _get_email_color(self, email_address: str) -> str:
        """Get the color for a given email address.

        Priority: exact email match → domain match → default color

        Args:
            email_address: Email address to look up

        Returns:
            Hex color code string
        """
        default_color = "#3B3B3B"

        if not email_address or not self.email_color_map:
            return default_color

        email_lower = email_address.lower()

        # Check for exact email match first (vip_senders)
        if email_lower in self.email_color_map:
            return self.email_color_map[email_lower]

        # Check domain match
        if '@' in email_lower:
            domain = email_lower.split('@')[1]
            if domain in self.email_color_map:
                return self.email_color_map[domain]

        return default_color

    def _email_color_filter(self, email_address: str) -> str:
        """Jinja2 filter to wrap email address in colored span.

        Args:
            email_address: Email address to colorize

        Returns:
            HTML span with inline color styling
        """
        color = self._get_email_color(email_address)
        # Escape the email address for safety
        safe_email = email_address.replace('<', '&lt;').replace('>', '&gt;')
        return f'<span style="color: {color}; font-weight: bold;">{safe_email}</span>'

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