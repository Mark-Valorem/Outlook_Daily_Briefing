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
        lookback_days = behaviour.get("lookback_days_inbox", 2)
        overdue_days = behaviour.get("overdue_days", 30)
        
        collected = {
            "inbox": [],
            "sent": [],
            "calendar_today": [],
            "calendar_tomorrow": [],
            "overdue": []
        }
        
        # Collect inbox items
        inbox_items = self.outlook.get_inbox_items(lookback_days)
        collected["inbox"] = [self._convert_mail_item(item) for item in inbox_items]
        logger.info(f"Collected {len(collected['inbox'])} inbox items")
        
        # Collect sent items
        sent_items = self.outlook.get_sent_items(lookback_days)
        collected["sent"] = [self._convert_mail_item(item, "Sent") for item in sent_items]
        logger.info(f"Collected {len(collected['sent'])} sent items")
        
        # Collect calendar items for today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        calendar_today = self.outlook.get_calendar_items(today_start, today_end)
        collected["calendar_today"] = [self._convert_calendar_item(item) for item in calendar_today]
        logger.info(f"Collected {len(collected['calendar_today'])} calendar items for today")
        
        # Collect calendar items for tomorrow (if configured)
        if config.get("calendar", {}).get("include_tomorrow_first_meeting", False):
            tomorrow_start = today_end
            tomorrow_end = tomorrow_start + timedelta(days=1)
            calendar_tomorrow = self.outlook.get_calendar_items(tomorrow_start, tomorrow_end)
            collected["calendar_tomorrow"] = [self._convert_calendar_item(item) for item in calendar_tomorrow]
            logger.info(f"Collected {len(collected['calendar_tomorrow'])} calendar items for tomorrow")
        
        # Collect overdue items
        overdue_items = self.outlook.get_overdue_items(overdue_days)
        collected["overdue"] = [self._convert_mail_item(item, "Overdue") for item in overdue_items]
        logger.info(f"Collected {len(collected['overdue'])} overdue items")
        
        return collected
        
    def _convert_mail_item(self, item, folder: str = "Inbox") -> EmailItem:
        try:
            # Get sender information
            try:
                sender_name = item.SenderName
                sender_email = item.SenderEmailAddress
            except:
                sender_name = "Unknown"
                sender_email = "unknown@unknown.com"
                
            # Get body preview (first 200 chars)
            body_preview = ""
            try:
                if hasattr(item, "Body") and item.Body:
                    body_preview = item.Body[:200].replace("\n", " ").replace("\r", " ")
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
                body_preview=body_preview
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
                folder_name=folder
            )
            
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