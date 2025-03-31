import logging
import json
from datetime import datetime
from app import db
from models import MessageLog, Platform
from platform_handlers import get_platform_handler

logger = logging.getLogger(__name__)

class MessageForwarder:
    """Main class to handle message forwarding between platforms"""
    
    def __init__(self):
        self.handlers = {}
    
    def forward_message(self, rule):
        """
        Forward messages based on a forwarding rule
        
        Args:
            rule: ForwardingRule object containing source, destination, and filters
        """
        logger.info(f"Executing rule: {rule.name}")
        
        # Get source and destination platforms
        source_platform = Platform.query.get(rule.source_id)
        destination_platform = Platform.query.get(rule.destination_id)
        
        if not source_platform or not destination_platform:
            error_msg = "Source or destination platform not found"
            logger.error(error_msg)
            self._log_message(rule, None, None, "error", error_msg)
            return False
        
        try:
            # Get or create handlers for source and destination
            source_handler = self._get_handler(source_platform)
            destination_handler = self._get_handler(destination_platform)
            
            # Parse filters if they exist
            filters = json.loads(rule.filters) if rule.filters else {}
            
            # Get messages from source
            logger.debug(f"Getting messages from {source_platform.name}")
            messages = source_handler.get_messages(filters)
            
            if not messages:
                logger.info("No messages to forward")
                return True
            
            # Forward each message to destination
            success_count = 0
            for message in messages:
                try:
                    logger.debug(f"Forwarding message to {destination_platform.name}")
                    result = destination_handler.send_message(message)
                    
                    if result:
                        success_count += 1
                        self._log_message(rule, message, message, "success")
                    else:
                        self._log_message(rule, message, None, "error", "Failed to send message")
                        
                except Exception as e:
                    logger.exception(f"Error forwarding message: {str(e)}")
                    self._log_message(rule, message, None, "error", str(e))
            
            logger.info(f"Forwarded {success_count}/{len(messages)} messages")
            return success_count > 0
            
        except Exception as e:
            error_msg = f"Error in message forwarding: {str(e)}"
            logger.exception(error_msg)
            self._log_message(rule, None, None, "error", error_msg)
            return False
        
    def _get_handler(self, platform):
        """
        Get or create a platform handler for the given platform
        
        Args:
            platform: Platform object
        
        Returns:
            A platform handler instance
        """
        # Check if handler already exists
        if platform.id in self.handlers:
            return self.handlers[platform.id]
        
        # Create new handler
        credentials = json.loads(platform.credentials)
        handler = get_platform_handler(platform.type, credentials)
        
        # Store handler for reuse
        self.handlers[platform.id] = handler
        
        return handler
    
    def _log_message(self, rule, source_message, destination_message, status, error_message=None):
        """
        Log a message forwarding action
        
        Args:
            rule: ForwardingRule object
            source_message: Source message content
            destination_message: Destination message content
            status: Status of the forwarding (success/error)
            error_message: Error message if status is error
        """
        log_entry = MessageLog(
            rule_id=rule.id,
            user_id=rule.user_id,
            source_message=str(source_message) if source_message else None,
            destination_message=str(destination_message) if destination_message else None,
            status=status,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        for handler in self.handlers.values():
            if hasattr(handler, 'cleanup'):
                handler.cleanup()
        
        self.handlers = {}
