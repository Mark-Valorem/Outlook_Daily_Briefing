from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


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
    priority_label: str = ""  # "High", "Normal", "Low"
    status_label: str = ""    # "Flagged", "Unread", or "VIP"
    recommended_action: str = ""
    why_it_matters: str = ""
    is_vip_sender: bool = False  # True if from vip_senders list
    ai_summary: str = ""  # AI-generated summary (optional)
    

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
    

class EmailCollector:
    def __init__(self, outlook_client):
        self.outlook = outlook_client

    def collect_all(self, config: Dict[str, Any]) -> Dict[str, List[Any]]:
        behaviour = config.get("behaviour", {})
        lookback_days = behaviour.get("lookback_days_inbox", 7)
        unread_or_flagged_only = behaviour.get("include_unread_or_flagged_only", True)

        collected = {
            "inbox": []
        }

        # Collect inbox items with MAPI filtering
        inbox_items = self.outlook.get_inbox_items(lookback_days, unread_or_flagged_only)

        # Convert and apply VIP post-filtering
        vip_filtered = []
        for item in inbox_items:
            email_item = self._convert_mail_item(item, "Inbox", config)
            if email_item:  # None means filtered out
                vip_filtered.append(email_item)

        collected["inbox"] = vip_filtered
        logger.info(f"Collected {len(inbox_items)} inbox items, {len(vip_filtered)} after VIP filtering")

        return collected
        
    def _convert_mail_item(self, item, folder: str = "Inbox", config: Dict[str, Any] = None) -> Optional[EmailItem]:
        try:
            # Get sender information
            try:
                sender_name = item.SenderName
                sender_email = item.SenderEmailAddress
            except:
                sender_name = "Unknown"
                sender_email = "unknown@unknown.com"
                
            # Apply VIP filtering if config provided
            if config:
                # Skip VIP filter for flagged emails - user explicitly wants to see them
                is_flagged = item.FlagStatus > 0

                if not is_flagged:  # Only filter non-flagged emails
                    # Check if sender is VIP
                    if not self._is_vip(sender_email, config):
                        logger.debug(f"Filtered out non-VIP unread: {sender_email}")
                        return None

                    # Check if subject matches ignore patterns
                    subject_text = item.Subject or ""
                    if self._matches_ignore_patterns(subject_text, config):
                        logger.debug(f"Filtered out by ignore pattern: {subject_text}")
                        return None
                else:
                    logger.debug(f"Including flagged email from: {sender_email}")

            # Get body preview (first 140 chars)
            body_preview = ""
            try:
                if hasattr(item, "Body") and item.Body:
                    body_preview = item.Body[:140].replace("\n", " ").replace("\r", " ")
            except:
                pass
                
            # Get categories
            categories = []
            try:
                if hasattr(item, "Categories") and item.Categories:
                    categories = [cat.strip() for cat in item.Categories.split(",")]
            except:
                pass
                
            return EmailItem(
                entry_id=item.EntryID,
                subject=item.Subject or "(No subject)",
                sender_name=sender_name,
                sender_email=sender_email,
                received_time=item.ReceivedTime,
                importance=item.Importance,
                is_flagged=item.FlagStatus > 0,
                is_unread=item.UnRead,
                has_attachments=item.Attachments.Count > 0,
                categories=categories,
                folder_name=folder,
                body_preview=body_preview,
                is_vip_sender=self._is_vip_sender(sender_email, config) if config else False
            )
        except Exception as e:
            logger.error(f"Error converting mail item: {e}")
            # Return a minimal item
            return EmailItem(
                entry_id="error",
                subject="(Error reading item)",
                sender_name="Unknown",
                sender_email="unknown@unknown.com",
                received_time=datetime.now(),
                importance=0,
                is_flagged=False,
                is_unread=False,
                has_attachments=False,
                folder_name=folder,
                body_preview=body_preview
            )

    def _is_vip(self, email: str, config: Dict[str, Any]) -> bool:
        """Check if email is from VIP domain or VIP sender."""
        priorities = config.get('priorities', {})
        vip_domains = [d.lower() for d in priorities.get('vip_domains', [])]
        vip_senders = [s.lower() for s in priorities.get('vip_senders', [])]

        email_lower = email.lower()

        # Check if email is in VIP senders list
        if email_lower in vip_senders:
            return True

        # Check if domain is in VIP domains list
        if '@' in email_lower:
            domain = email_lower.split('@')[1]
            if domain in vip_domains:
                return True

        return False

    def _is_vip_sender(self, email: str, config: Dict[str, Any]) -> bool:
        """Check if email is from VIP senders list (individual people, not domains)."""
        priorities = config.get('priorities', {})
        vip_senders = [s.lower() for s in priorities.get('vip_senders', [])]
        email_lower = email.lower()
        return email_lower in vip_senders

    def _matches_ignore_patterns(self, subject: str, config: Dict[str, Any]) -> bool:
        """Check if subject matches any ignore patterns."""
        priorities = config.get('priorities', {})
        ignore_patterns = priorities.get('ignore_match', [])

        subject_lower = subject.lower()
        for pattern in ignore_patterns:
            if pattern.lower() in subject_lower:
                return True

        return False
            
    def _convert_calendar_item(self, item) -> CalendarItem:
        try:
            # Get attendees count
            attendees_count = 0
            try:
                if hasattr(item, "Recipients"):
                    attendees_count = item.Recipients.Count
            except:
                pass
                
            # Get body preview
            body_preview = ""
            try:
                if hasattr(item, "Body") and item.Body:
                    body_preview = item.Body[:200].replace("\n", " ").replace("\r", " ")
            except:
                pass
                
            return CalendarItem(
                entry_id=item.EntryID,
                subject=item.Subject or "(No subject)",
                start_time=item.Start,
                end_time=item.End,
                location=item.Location or "",
                organizer=item.Organizer if hasattr(item, "Organizer") else "",
                is_all_day=item.AllDayEvent,
                is_recurring=item.IsRecurring,
                attendees_count=attendees_count,
                response_status=item.ResponseStatus if hasattr(item, "ResponseStatus") else 0,
                body_preview=body_preview
            )
        except Exception as e:
            logger.error(f"Error converting calendar item: {e}")
            # Return a minimal item
            return CalendarItem(
                entry_id="error",
                subject="(Error reading item)",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                location="",
                organizer="",
                is_all_day=False,
                is_recurring=False,
                attendees_count=0,
                response_status=0
            )