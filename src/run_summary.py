#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
import json
import yaml
import tempfile

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from briefing.outlook_client import OutlookClient
from briefing.collector import EmailCollector
from briefing.prioritiser import EmailPrioritiser
from briefing.renderer import ReportRenderer
from briefing.scheduler_guard import SchedulerGuard
from briefing.ai_analyzer import EmailAnalyzer


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Outlook Daily Briefing - Email Summary Generator")
    parser.add_argument('--config', type=str, required=True, help='Path to configuration file')
    parser.add_argument('--mode', type=str, choices=['auto', 'morning', 'evening', 'force'], 
                       default='auto', help='Briefing mode')
    parser.add_argument('--dry-run', action='store_true', help='Generate report without sending email')
    parser.add_argument('--since', type=str, help='Time range (e.g., "1d" for 1 day, "12h" for 12 hours)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting Outlook Daily Briefing")
    
    # Check scheduler guard
    guard = SchedulerGuard()
    if not guard.should_run(args.mode):
        logger.info("Scheduler guard prevented execution")
        sys.exit(0)
        
    # Determine actual mode if auto
    if args.mode == 'auto':
        actual_mode = guard.get_mode_from_time()
    else:
        actual_mode = args.mode if args.mode != 'force' else guard.get_mode_from_time()
        
    logger.info(f"Running in {actual_mode} mode")
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Configuration loaded from {args.config}")
        
        # Override lookback if --since is provided
        if args.since:
            if args.since.endswith('d'):
                days = int(args.since[:-1])
                config.setdefault('behaviour', {})['lookback_days_inbox'] = days
                logger.info(f"Overriding lookback to {days} days")
            elif args.since.endswith('h'):
                hours = int(args.since[:-1])
                days = max(1, hours // 24)
                config.setdefault('behaviour', {})['lookback_days_inbox'] = days
                logger.info(f"Overriding lookback to {days} days (from {hours} hours)")
                
        # Connect to Outlook
        outlook = OutlookClient(only_when_open=config.get('behaviour', {}).get('only_when_outlook_open', True))
        if not outlook.connect():
            logger.warning("Could not connect to Outlook")
            sys.exit(0)
            
        # Collect items (only VIP inbox emails now)
        collector = EmailCollector(outlook)
        collected = collector.collect_all(config)
        all_emails = collected.get('inbox', [])

        logger.info(f"Collected {len(all_emails)} VIP emails")

        # Prioritise and group by day
        prioritiser = EmailPrioritiser(config)
        grouped_by_day = prioritiser.prioritise_and_group(all_emails)

        # AI-powered analysis (if enabled)
        analyzer = EmailAnalyzer(config)
        if analyzer.is_enabled():
            logger.info("AI analysis enabled - analyzing qualifying emails")
            ai_results = analyzer.analyze_batch(all_emails)

            # Update emails with AI-generated summaries and actions
            for email in all_emails:
                if email.entry_id in ai_results:
                    result = ai_results[email.entry_id]
                    if result.success:
                        email.ai_summary = result.summary
                        # Replace recommended_action with AI version
                        email.recommended_action = result.recommended_action
                        logger.debug(f"AI updated: {email.subject[:40]}")
        else:
            logger.debug("AI analysis disabled or not available")

        # Render report
        renderer = ReportRenderer()
        html_report = renderer.render_report(grouped_by_day, config, actual_mode)
        subject = renderer.render_subject(config, actual_mode)
        
        # Send or display report
        if args.dry_run:
            logger.info("DRY RUN MODE - Email not sent")
            logger.info(f"Subject: {subject}")
            logger.info(f"To: {config['report']['to']}")

            # Save preview if configured
            preview_path = config.get('report', {}).get('preview_html')
            if preview_path:
                logger.info(f"Report preview saved to: {preview_path}")

            # Print summary stats
            total_emails = sum(len(emails) for emails in grouped_by_day.values())
            logger.info(f"\nTotal VIP emails: {total_emails}")
            logger.info(f"Days with emails: {len(grouped_by_day)}")

            # Print sample from each day
            for day_key, emails in list(grouped_by_day.items())[:3]:
                logger.info(f"\n{day_key}: {len(emails)} emails")
                for email in emails[:2]:
                    logger.info(f"  - [{email.status_label}] {email.subject[:60]}")
                    
        else:
            # Create temporary HTML file for attachment
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_report)
                temp_path = temp_file.name

            try:
                # Send the email with HTML attachment
                outlook.send_email(
                    to=config['report']['to'],
                    subject=subject,
                    html_body=html_report,
                    attachments=[temp_path]
                )
                logger.info(f"Report sent successfully to {config['report']['to']} with HTML attachment")
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_path}: {e}")
            
    except FileNotFoundError as e:
        logger.error(f"Configuration file error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
        
    logger.info("Outlook Daily Briefing completed successfully")


if __name__ == "__main__":
    main()