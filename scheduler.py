import logging
import threading
import time
import schedule
from datetime import datetime

logger = logging.getLogger(__name__)

class ScheduleManager:
    """Manage scheduled tasks for message forwarding"""
    
    def __init__(self, forwarder):
        self.forwarder = forwarder
        self.jobs = {}  # Dictionary to track scheduled jobs by rule ID
        self.running = False
        self.thread = None
    
    def add_rule(self, rule):
        """
        Add a rule to the scheduler
        
        Args:
            rule: ForwardingRule object
        """
        # Remove existing job if it exists
        self.remove_rule(rule)
        
        # Skip if rule is not active
        if not rule.is_active:
            return
        
        # Parse schedule string
        if not rule.schedule:
            # Default to every 15 minutes if no schedule is specified
            job = schedule.every(15).minutes.do(self._execute_rule, rule)
        else:
            # Parse cron-like schedule
            schedule_parts = rule.schedule.split()
            
            if len(schedule_parts) == 1:
                # Simple interval: "5" (every 5 minutes)
                try:
                    minutes = int(schedule_parts[0])
                    job = schedule.every(minutes).minutes.do(self._execute_rule, rule)
                except ValueError:
                    logger.error(f"Invalid schedule format for rule {rule.id}: {rule.schedule}")
                    return
            elif len(schedule_parts) == 2:
                # Time of day: "14 30" (14:30)
                try:
                    hour = int(schedule_parts[0])
                    minute = int(schedule_parts[1])
                    job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._execute_rule, rule)
                except ValueError:
                    logger.error(f"Invalid schedule format for rule {rule.id}: {rule.schedule}")
                    return
            else:
                logger.error(f"Unsupported schedule format for rule {rule.id}: {rule.schedule}")
                return
        
        # Store job
        self.jobs[rule.id] = job
        logger.info(f"Added rule {rule.id} to scheduler with schedule: {rule.schedule or '15 minutes'}")
    
    def remove_rule(self, rule):
        """
        Remove a rule from the scheduler
        
        Args:
            rule: ForwardingRule object
        """
        if rule.id in self.jobs:
            schedule.cancel_job(self.jobs[rule.id])
            del self.jobs[rule.id]
            logger.info(f"Removed rule {rule.id} from scheduler")
    
    def _execute_rule(self, rule):
        """
        Execute a forwarding rule
        
        Args:
            rule: ForwardingRule object
        """
        logger.info(f"Executing scheduled rule: {rule.id} - {rule.name}")
        try:
            self.forwarder.forward_message(rule)
        except Exception as e:
            logger.exception(f"Error executing rule {rule.id}: {str(e)}")
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
