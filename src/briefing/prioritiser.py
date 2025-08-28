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
        grouped = {
            "high_priority": [],
            "customers_direct": [],
            "customers_team": [],
            "internal": [],
            "low_priority": [],
            "ignored": []
        }
        
        for item in items:
            # Skip if from ignored domain
            if self._is_ignored(item):
                item.priority_reason = "Ignored domain"
                grouped["ignored"].append(item)
                continue
                
            # Calculate priority score
            score, reason = self._calculate_priority(item)
            item.priority_score = score
            item.priority_reason = reason
            
            # Assign group
            group = self._assign_group(item)
            item.group_label = group
            
            # Place in appropriate bucket
            if score >= 90:
                grouped["high_priority"].append(item)
            elif group in self.group_mappings.values():
                grouped["customers_team"].append(item)
            elif self._is_customer_email(item):
                grouped["customers_direct"].append(item)
            elif self._is_internal_email(item):
                grouped["internal"].append(item)
            else:
                grouped["low_priority"].append(item)
                
        # Sort each group by priority score and time
        for key in grouped:
            grouped[key].sort(key=lambda x: (-x.priority_score, -x.received_time.timestamp()))
            
        return grouped
        
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