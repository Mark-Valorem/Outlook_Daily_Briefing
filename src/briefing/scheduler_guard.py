import os
import sys
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class SchedulerGuard:
    def __init__(self):
        self.current_time = datetime.now()
        self.current_day = self.current_time.weekday()  # 0=Monday, 6=Sunday
        
    def should_run(self, mode: str = "auto") -> bool:
        # Force mode bypasses all checks (weekday, time windows, etc.)
        if mode == "force":
            logger.info("Running in force mode - bypassing all checks")
            return True

        # If specific mode is set (morning/evening), allow manual execution any day
        if mode in ["morning", "evening"]:
            logger.info(f"Running in {mode} mode (manual execution allowed)")
            return True

        # Auto mode: apply weekday and time window restrictions
        if mode == "auto":
            # Check if it's a weekday (Monday=0 to Friday=4)
            if self.current_day > 4:  # Saturday=5, Sunday=6
                logger.info(f"Auto mode: Weekend detected ({self._day_name()}), skipping")
                return False

            hour = self.current_time.hour
            minute = self.current_time.minute

            # Morning window: 9:00 - 10:00
            if 9 <= hour < 10:
                logger.info("Auto mode: Morning briefing time detected")
                return True

            # Evening window: 17:00 - 18:00
            if 17 <= hour < 18:
                logger.info("Auto mode: Evening briefing time detected")
                return True

            logger.info(f"Auto mode: Outside briefing windows (current time: {hour:02d}:{minute:02d})")
            return False

        return True
        
    def _day_name(self) -> str:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[self.current_day]
        
    def get_mode_from_time(self) -> str:
        hour = self.current_time.hour
        
        if hour < 12:
            return "morning"
        else:
            return "evening"