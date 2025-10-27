import sys
import pythoncom
import win32com.client
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OutlookClient:
    def __init__(self, only_when_open: bool = True):
        self.only_when_open = only_when_open
        self.outlook = None
        self.namespace = None
        
    def connect(self) -> bool:
        try:
            self.outlook = win32com.client.GetActiveObject("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            logger.info("Successfully connected to Outlook")
            return True
        except pythoncom.com_error:
            if self.only_when_open:
                logger.info("Outlook not running, exiting quietly")
                return False
            else:
                try:
                    self.outlook = win32com.client.Dispatch("Outlook.Application")
                    self.namespace = self.outlook.GetNamespace("MAPI")
                    logger.info("Started new Outlook instance")
                    return True
                except Exception as e:
                    logger.error(f"Failed to start Outlook: {e}")
                    return False
                    
    def get_inbox_items(self, lookback_days: int = 7, unread_or_flagged_only: bool = True) -> List[Any]:
        if not self.namespace:
            return []

        inbox = self.namespace.GetDefaultFolder(6)  # 6 = olFolderInbox
        items = inbox.Items
        items.Sort("[ReceivedTime]", True)  # Sort by newest first

        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        date_filter = f"[ReceivedTime] >= '{cutoff_date.strftime('%m/%d/%Y')}'"

        # Build filter string with status and message class
        if unread_or_flagged_only:
            # Status filter: Unread OR Flagged (FlagStatus = 2 means flagged)
            status_filter = "([UnRead] = True) OR ([FlagStatus] = 2)"
            # MessageClass filter: Only email messages (IPM.Note)
            filter_str = f"({date_filter}) AND ({status_filter}) AND ([MessageClass] = 'IPM.Note')"
        else:
            filter_str = f"{date_filter} AND ([MessageClass] = 'IPM.Note')"

        try:
            filtered_items = items.Restrict(filter_str)
            logger.info(f"MAPI filter applied: {filter_str}")
            return list(filtered_items)
        except Exception as e:
            logger.error(f"Error filtering inbox items: {e}")
            return []
            
    def get_sent_items(self, lookback_days: int = 2) -> List[Any]:
        if not self.namespace:
            return []
            
        sent = self.namespace.GetDefaultFolder(5)  # 5 = olFolderSentMail
        items = sent.Items
        items.Sort("[SentOn]", True)
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        filter_str = f"[SentOn] >= '{cutoff_date.strftime('%m/%d/%Y')}'"
        
        try:
            filtered_items = items.Restrict(filter_str)
            return list(filtered_items)
        except Exception as e:
            logger.error(f"Error filtering sent items: {e}")
            return []
            
    def get_calendar_items(self, start_date: datetime = None, end_date: datetime = None) -> List[Any]:
        if not self.namespace:
            return []
            
        calendar = self.namespace.GetDefaultFolder(9)  # 9 = olFolderCalendar
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")
        
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = start_date + timedelta(days=1)
            
        filter_str = f"[Start] >= '{start_date.strftime('%m/%d/%Y')}' AND [Start] < '{end_date.strftime('%m/%d/%Y %H:%M')}'"
        
        try:
            filtered_items = items.Restrict(filter_str)
            return list(filtered_items)
        except Exception as e:
            logger.error(f"Error filtering calendar items: {e}")
            return []
            
    def get_overdue_items(self, overdue_days: int = 30) -> List[Any]:
        if not self.namespace:
            return []
            
        inbox = self.namespace.GetDefaultFolder(6)
        items = inbox.Items
        
        cutoff_date = datetime.now() - timedelta(days=overdue_days)
        
        # Get flagged items
        flagged_filter = f"[FlagStatus] = 1 OR [FlagStatus] = 2"
        unread_filter = f"[UnRead] = True"
        date_filter = f"[ReceivedTime] < '{cutoff_date.strftime('%m/%d/%Y')}'"
        
        overdue_items = []
        
        try:
            # Get old flagged items
            filter_str = f"({flagged_filter}) AND {date_filter}"
            flagged_items = items.Restrict(filter_str)
            overdue_items.extend(list(flagged_items))
            
            # Get old unread items
            filter_str = f"{unread_filter} AND {date_filter}"
            unread_items = items.Restrict(filter_str)
            overdue_items.extend(list(unread_items))
            
            # Remove duplicates based on EntryID
            seen = set()
            unique_items = []
            for item in overdue_items:
                if item.EntryID not in seen:
                    seen.add(item.EntryID)
                    unique_items.append(item)
                    
            return unique_items
        except Exception as e:
            logger.error(f"Error getting overdue items: {e}")
            return []
            
    def send_email(self, to: str, subject: str, html_body: str, attachments: List[str] = None):
        if not self.outlook:
            raise RuntimeError("Not connected to Outlook")
            
        mail = self.outlook.CreateItem(0)  # 0 = MailItem
        mail.To = to
        mail.Subject = subject
        mail.HTMLBody = html_body
        
        if attachments:
            for attachment in attachments:
                mail.Attachments.Add(attachment)
                
        mail.Send()
        logger.info(f"Email sent to {to} with subject: {subject}")