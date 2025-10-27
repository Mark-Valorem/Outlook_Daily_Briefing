import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from .collector import EmailItem

logger = logging.getLogger(__name__)


class EmailPrioritiser:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.priorities = config.get("priorities", {})
        self.vip_domains = [d.lower() for d in self.priorities.get("vip_domains", [])]
        self.vip_senders = [s.lower() for s in self.priorities.get("vip_senders", [])]
        self.ignore_domains = [d.lower() for d in self.priorities.get("ignore_domains", [])]
        self.downrank_domains = [d.lower() for d in self.priorities.get("downrank_domains", [])]
        self.group_mappings = {k.lower(): v for k, v in self.priorities.get("group_mappings", {}).items()}
        self.keyword_rules = self.priorities.get("keyword_rules", [])
        
    def prioritise_and_group(self, items: List[EmailItem]) -> Dict[str, List[EmailItem]]:
        # Calculate scores and derive fields for all items
        for item in items:
            score, reason = self._calculate_priority(item)
            item.priority_score = score
            item.priority_reason = reason
            item.priority_label = self._get_priority_label(item.importance)
            # VIP senders get "VIP" status, otherwise "Flagged" or "Unread"
            if item.is_vip_sender:
                item.status_label = "VIP"
            else:
                item.status_label = "Flagged" if item.is_flagged else "Unread"
            item.recommended_action = self._derive_action(item)
            item.why_it_matters = self._derive_why_matters(item)

        # Sort: Flagged first (by importance desc, then time desc), then Unread (by time desc)
        items_sorted = sorted(items, key=lambda x: (
            not x.is_flagged,  # Flagged first (False comes before True)
            -x.importance if x.is_flagged else 0,  # High > Normal > Low for flagged
            -x.received_time.timestamp()  # Newest first
        ))

        # Group by day
        # NOTE: Outlook COM returns ReceivedTime in local timezone but marked as UTC.
        # We use the date directly without conversion to match Outlook's display.
        grouped_by_day = {}
        for item in items_sorted:
            # Use date directly from ReceivedTime (already in local/display timezone)
            item_date = item.received_time.date()

            day_key = item_date.strftime('%Y-%m-%d')
            if day_key not in grouped_by_day:
                grouped_by_day[day_key] = []
            grouped_by_day[day_key].append(item)

        logger.info(f"Grouped {len(items)} items into {len(grouped_by_day)} days")
        return grouped_by_day
        
    def _is_ignored(self, item: EmailItem) -> bool:
        sender_domain = self._get_domain(item.sender_email)
        return sender_domain in self.ignore_domains
        
    def _calculate_priority(self, item: EmailItem) -> Tuple[int, str]:
        score = 50  # Base score
        reasons = []
        
        # Check if from VIP sender
        if item.sender_email.lower() in self.vip_senders:
            score += 40
            reasons.append("VIP sender")
            
        # Check if from VIP domain
        sender_domain = self._get_domain(item.sender_email)
        if sender_domain in self.vip_domains:
            score += 30
            reasons.append("VIP domain")
            
        # Check importance flag
        if item.importance == 2:  # High importance
            score += 20
            reasons.append("High importance")
            
        # Check if flagged
        if item.is_flagged:
            score += 15
            reasons.append("Flagged")
            
        # Check if unread
        if item.is_unread:
            score += 10
            reasons.append("Unread")
            
        # Check keyword rules
        for rule in self.keyword_rules:
            pattern = rule.get("pattern", "")
            if pattern and re.search(pattern, item.subject + " " + item.body_preview, re.IGNORECASE):
                if rule.get("priority") == "critical":
                    score += 50
                    reasons.append(f"Critical keyword: {rule.get('suggest', 'Match')}")
                elif rule.get("priority") == "high":
                    score += 25
                    reasons.append(f"High priority keyword: {rule.get('suggest', 'Match')}")
                    
        # Downrank if from downrank domain
        if sender_domain in self.downrank_domains:
            score -= 20
            reasons.append("Downranked domain")
            
        # Cap score at 100
        score = min(score, 100)
        
        return score, ", ".join(reasons) if reasons else "Normal priority"
        
    def _assign_group(self, item: EmailItem) -> str:
        sender_domain = self._get_domain(item.sender_email)
        
        # Check group mappings
        for domain, group in self.group_mappings.items():
            if sender_domain == domain:
                return group
                
        return ""
        
    def _get_domain(self, email: str) -> str:
        if "@" in email:
            return email.split("@")[1].lower()
        return ""
        
    def _is_customer_email(self, item: EmailItem) -> bool:
        # Simple heuristic: external email that's not from a known internal domain
        sender_domain = self._get_domain(item.sender_email)
        
        # Get company domain from config
        company_domain = self._get_domain(self.config.get("report", {}).get("to", ""))
        
        # If sender is not from company domain and not in ignore list
        if company_domain and sender_domain != company_domain:
            return sender_domain not in self.ignore_domains
            
        return False
        
    def _is_internal_email(self, item: EmailItem) -> bool:
        # Check if from company domain
        sender_domain = self._get_domain(item.sender_email)
        company_domain = self._get_domain(self.config.get("report", {}).get("to", ""))

        return sender_domain == company_domain

    def _get_priority_label(self, importance: int) -> str:
        """Convert Outlook importance value to readable label."""
        return {2: "High", 1: "Normal", 0: "Low"}.get(importance, "Normal")

    def _derive_action(self, item: EmailItem) -> str:
        """Derive recommended action based on item properties and keywords."""
        # Check keyword rules for specific suggestions
        for rule in self.keyword_rules:
            pattern = rule.get('pattern', '')
            if pattern and re.search(pattern, item.subject + ' ' + item.body_preview, re.IGNORECASE):
                return rule.get('suggest', 'Review and respond')

        # Default actions based on status and importance
        if item.is_flagged and item.importance == 2:
            return "Urgent - respond today"
        elif item.is_flagged:
            return "Follow up required"
        elif item.importance == 2:
            return "Review urgently"
        else:
            return "Review and respond"

    def _derive_why_matters(self, item: EmailItem) -> str:
        """Derive why this email matters based on VIP status, keywords, and importance."""
        reasons = []

        sender_domain = self._get_domain(item.sender_email)

        # Check VIP status
        if item.sender_email.lower() in [s.lower() for s in self.vip_senders]:
            reasons.append("VIP sender")
        elif sender_domain in self.vip_domains:
            reasons.append("Key customer/partner")

        # Check importance
        if item.importance == 2:
            reasons.append("marked urgent")

        # Check flagged status
        if item.is_flagged:
            reasons.append("flagged for follow-up")

        # Check for critical keywords in subject and body
        critical_keywords = ['urgent', 'asap', 'contract', 'invoice', 'payment', 'tender', 'proposal']
        text = (item.subject + ' ' + item.body_preview).lower()
        matched = [kw for kw in critical_keywords if kw in text]
        if matched:
            reasons.append(f"contains: {', '.join(matched)}")

        return "; ".join(reasons) if reasons else "Requires attention"