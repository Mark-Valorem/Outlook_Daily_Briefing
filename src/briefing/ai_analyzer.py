import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not installed. AI analysis will be disabled.")


@dataclass
class AIAnalysisResult:
    """Result from AI email analysis."""
    summary: str
    recommended_action: str
    urgency_level: str  # "Critical", "High", "Medium"
    success: bool = True
    error_message: str = ""


class EmailAnalyzer:
    """AI-powered email analyzer using Anthropic Claude."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ai_config = config.get('ai_analysis', {})
        self.enabled = self.ai_config.get('enabled', False)
        self.client = None

        if self.enabled and ANTHROPIC_AVAILABLE:
            api_key_env = self.ai_config.get('api_key_env', 'ANTHROPIC_API_KEY')
            api_key = os.environ.get(api_key_env)

            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.model = self.ai_config.get('model', 'claude-3-5-sonnet-20241022')
                logger.info(f"AI analyzer initialized with model: {self.model}")
            else:
                logger.warning(f"AI analysis enabled but {api_key_env} environment variable not set")
                self.enabled = False
        elif self.enabled and not ANTHROPIC_AVAILABLE:
            logger.error("AI analysis enabled but Anthropic SDK not available")
            self.enabled = False

    def is_enabled(self) -> bool:
        """Check if AI analysis is enabled and available."""
        return self.enabled and self.client is not None

    def should_analyze(self, email_item) -> bool:
        """Determine if this email should be analyzed by AI."""
        if not self.is_enabled():
            return False

        criteria = self.ai_config.get('analyze_criteria', 'flagged_high')

        if criteria == 'flagged_high':
            # Only flagged + high importance
            return email_item.is_flagged and email_item.importance == 2
        elif criteria == 'all_vip':
            # All VIP emails (domain or sender)
            return True
        elif criteria == 'top_priority':
            # All flagged emails regardless of importance
            return email_item.is_flagged
        elif criteria == 'flagged_or_vip':
            # Flagged emails OR emails from VIP senders
            return email_item.is_flagged or email_item.is_vip_sender

        return False

    def analyze_email(self, email_item) -> AIAnalysisResult:
        """
        Analyze an email using Claude AI.

        Returns AIAnalysisResult with summary and recommended action.
        Falls back to empty result on error.
        """
        if not self.is_enabled():
            return AIAnalysisResult(
                summary="",
                recommended_action="",
                urgency_level="",
                success=False,
                error_message="AI analysis not enabled"
            )

        try:
            # Build the analysis prompt
            prompt = self._build_prompt(email_item)

            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            result_text = response.content[0].text
            return self._parse_response(result_text)

        except Exception as e:
            logger.error(f"AI analysis failed for email '{email_item.subject}': {e}")
            return AIAnalysisResult(
                summary="",
                recommended_action="",
                urgency_level="",
                success=False,
                error_message=str(e)
            )

    def _build_prompt(self, email_item) -> str:
        """Build the analysis prompt for Claude."""
        return f"""Analyze this business email and provide:
1. One-sentence summary (max 15 words)
2. Recommended action (max 8 words)
3. Urgency level: Critical, High, or Medium

Email Details:
From: {email_item.sender_name} <{email_item.sender_email}>
Subject: {email_item.subject}
Preview: {email_item.body_preview}
Importance: {"High" if email_item.importance == 2 else "Normal" if email_item.importance == 1 else "Low"}
Flagged: {"Yes" if email_item.is_flagged else "No"}

Respond in this exact format:
SUMMARY: [your one-sentence summary]
ACTION: [your recommended action]
URGENCY: [Critical/High/Medium]"""

    def _parse_response(self, response_text: str) -> AIAnalysisResult:
        """Parse Claude's response into structured data."""
        summary = ""
        action = ""
        urgency = "Medium"

        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('ACTION:'):
                action = line.replace('ACTION:', '').strip()
            elif line.startswith('URGENCY:'):
                urgency = line.replace('URGENCY:', '').strip()

        return AIAnalysisResult(
            summary=summary,
            recommended_action=action,
            urgency_level=urgency,
            success=True
        )

    def analyze_batch(self, email_items: list) -> Dict[str, AIAnalysisResult]:
        """
        Analyze multiple emails in batch.

        Returns dict mapping entry_id to AIAnalysisResult.
        """
        results = {}

        for email in email_items:
            if self.should_analyze(email):
                logger.info(f"Analyzing email: {email.subject[:50]}")
                result = self.analyze_email(email)
                results[email.entry_id] = result
            else:
                logger.debug(f"Skipping AI analysis for: {email.subject[:50]}")

        logger.info(f"AI analyzed {len(results)} emails")
        return results
