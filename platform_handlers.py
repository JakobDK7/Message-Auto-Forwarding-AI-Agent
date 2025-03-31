import logging
import time
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class BasePlatformHandler(ABC):
    """Base class for all platform handlers"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.last_check = None
    
    @abstractmethod
    def get_messages(self, filters=None):
        """
        Get messages from the platform
        
        Args:
            filters: Dictionary of filters to apply
        
        Returns:
            List of messages
        """
        pass
    
    @abstractmethod
    def send_message(self, message):
        """
        Send a message to the platform
        
        Args:
            message: Message to send
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def cleanup(self):
        """Clean up resources"""
        pass

class SeleniumBasedHandler(BasePlatformHandler):
    """Base class for platform handlers that use Selenium"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def cleanup(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


class TelegramHandler(SeleniumBasedHandler):
    """Handler for Telegram platform"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self._login()
    
    def _login(self):
        """Login to Telegram Web"""
        try:
            self.driver.get("https://web.telegram.org/")
            
            # Check if already logged in
            if self._is_logged_in():
                logger.info("Already logged in to Telegram")
                return True
            
            # Enter phone number
            logger.info("Logging in to Telegram...")
            phone_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='phone']"))
            )
            phone_input.send_keys(self.credentials.get("phone"))
            
            # Click next
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
            next_button.click()
            
            # Wait for code input (manual step - notification will be shown)
            logger.info("Waiting for user to enter verification code...")
            
            # Here we would need manual intervention for the verification code
            # In a real implementation, we might use a different approach like API-based authentication
            
            # For demo purposes, we'll just wait a long time
            WebDriverWait(self.driver, 300).until(self._is_logged_in)
            
            logger.info("Successfully logged in to Telegram")
            return True
            
        except Exception as e:
            logger.exception(f"Error logging in to Telegram: {str(e)}")
            return False
    
    def _is_logged_in(self):
        """Check if logged in to Telegram"""
        try:
            # Look for an element that is present when logged in
            self.driver.find_element(By.CSS_SELECTOR, ".chat-list")
            return True
        except NoSuchElementException:
            return False
    
    def get_messages(self, filters=None):
        """Get messages from Telegram"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return []
        
        messages = []
        try:
            # Navigate to specified chat if provided in filters
            if filters and 'chat' in filters:
                chat_name = filters['chat']
                search_input = self.driver.find_element(By.CSS_SELECTOR, ".search-input input")
                search_input.clear()
                search_input.send_keys(chat_name)
                time.sleep(2)  # Wait for search results
                
                chat_items = self.driver.find_elements(By.CSS_SELECTOR, ".chat-list .chat-item")
                for chat in chat_items:
                    title = chat.find_element(By.CSS_SELECTOR, ".user-title").text
                    if title.lower() == chat_name.lower():
                        chat.click()
                        break
            
            # Get message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message")
            
            # Set last check time if not set
            if not self.last_check:
                self.last_check = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago
            
            # Extract messages
            for msg_elem in message_elements[-15:]:  # Get latest 15 messages
                try:
                    # Extract message text and time
                    text = msg_elem.find_element(By.CSS_SELECTOR, ".text-content").text
                    time_str = msg_elem.find_element(By.CSS_SELECTOR, ".time").text
                    
                    # Apply keyword filters if specified
                    if filters and 'keywords' in filters:
                        keywords = filters['keywords']
                        if not any(keyword.lower() in text.lower() for keyword in keywords):
                            continue
                    
                    messages.append(text)
                    
                except Exception as e:
                    logger.error(f"Error extracting message: {str(e)}")
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.exception(f"Error getting messages from Telegram: {str(e)}")
        
        return messages
    
    def send_message(self, message):
        """Send a message on Telegram"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return False
        
        try:
            # Make sure chat is open and text input is available
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".composer .composer-input"))
            )
            
            # Enter message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-send")
            send_button.click()
            
            # Wait for message to be sent
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.exception(f"Error sending message on Telegram: {str(e)}")
            return False


class WhatsAppHandler(SeleniumBasedHandler):
    """Handler for WhatsApp platform"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self._login()
    
    def _login(self):
        """Login to WhatsApp Web"""
        try:
            self.driver.get("https://web.whatsapp.com/")
            
            # Check if already logged in
            if self._is_logged_in():
                logger.info("Already logged in to WhatsApp")
                return True
            
            # Display QR code and wait for user to scan it
            logger.info("Please scan the QR code to login to WhatsApp...")
            
            # Wait for login to complete (10 minutes timeout)
            WebDriverWait(self.driver, 600).until(self._is_logged_in)
            
            logger.info("Successfully logged in to WhatsApp")
            return True
            
        except Exception as e:
            logger.exception(f"Error logging in to WhatsApp: {str(e)}")
            return False
    
    def _is_logged_in(self):
        """Check if logged in to WhatsApp"""
        try:
            # Look for an element that is present when logged in
            self.driver.find_element(By.CSS_SELECTOR, ".app")
            return True
        except NoSuchElementException:
            return False
    
    def get_messages(self, filters=None):
        """Get messages from WhatsApp"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return []
        
        messages = []
        try:
            # Navigate to specified chat if provided in filters
            if filters and 'chat' in filters:
                chat_name = filters['chat']
                search_input = self.driver.find_element(By.CSS_SELECTOR, ".copyable-text.selectable-text[data-tab='3']")
                search_input.clear()
                search_input.send_keys(chat_name)
                time.sleep(2)  # Wait for search results
                
                chat_items = self.driver.find_elements(By.CSS_SELECTOR, ".chat")
                for chat in chat_items:
                    title = chat.find_element(By.CSS_SELECTOR, ".chat-title span").text
                    if title.lower() == chat_name.lower():
                        chat.click()
                        break
            
            # Get message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message-in, .message-out")
            
            # Set last check time if not set
            if not self.last_check:
                self.last_check = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago
            
            # Extract messages
            for msg_elem in message_elements[-15:]:  # Get latest 15 messages
                try:
                    # Extract message text and time
                    text = msg_elem.find_element(By.CSS_SELECTOR, ".copyable-text").text
                    time_str = msg_elem.find_element(By.CSS_SELECTOR, ".copyable-text > .selectable-text").get_attribute("data-pre-plain-text")
                    
                    # Apply keyword filters if specified
                    if filters and 'keywords' in filters:
                        keywords = filters['keywords']
                        if not any(keyword.lower() in text.lower() for keyword in keywords):
                            continue
                    
                    messages.append(text)
                    
                except Exception as e:
                    logger.error(f"Error extracting message: {str(e)}")
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.exception(f"Error getting messages from WhatsApp: {str(e)}")
        
        return messages
    
    def send_message(self, message):
        """Send a message on WhatsApp"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return False
        
        try:
            # Make sure chat is open and text input is available
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".copyable-text.selectable-text[data-tab='9']"))
            )
            
            # Enter message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "span[data-icon='send']")
            send_button.click()
            
            # Wait for message to be sent
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.exception(f"Error sending message on WhatsApp: {str(e)}")
            return False


class SlackHandler(SeleniumBasedHandler):
    """Handler for Slack platform"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self._login()
    
    def _login(self):
        """Login to Slack Web"""
        try:
            self.driver.get("https://slack.com/signin")
            
            # Check if already logged in
            if self._is_logged_in():
                logger.info("Already logged in to Slack")
                return True
            
            # Enter email
            logger.info("Logging in to Slack...")
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#email"))
            )
            email_input.send_keys(self.credentials.get("email"))
            
            # Enter password
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input#password")
            password_input.send_keys(self.credentials.get("password"))
            
            # Click sign in button
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR, "button#signin_btn")
            sign_in_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 30).until(self._is_logged_in)
            
            logger.info("Successfully logged in to Slack")
            return True
            
        except Exception as e:
            logger.exception(f"Error logging in to Slack: {str(e)}")
            return False
    
    def _is_logged_in(self):
        """Check if logged in to Slack"""
        try:
            # Look for an element that is present when logged in
            self.driver.find_element(By.CSS_SELECTOR, ".p-workspace__sidebar")
            return True
        except NoSuchElementException:
            return False
    
    def get_messages(self, filters=None):
        """Get messages from Slack"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return []
        
        messages = []
        try:
            # Navigate to specified channel if provided in filters
            if filters and 'channel' in filters:
                channel_name = filters['channel']
                channel_links = self.driver.find_elements(By.CSS_SELECTOR, ".p-channel_sidebar__channel a")
                
                for link in channel_links:
                    if channel_name.lower() in link.text.lower():
                        link.click()
                        break
            
            # Get message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".c-message")
            
            # Set last check time if not set
            if not self.last_check:
                self.last_check = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago
            
            # Extract messages
            for msg_elem in message_elements[-15:]:  # Get latest 15 messages
                try:
                    # Extract message text and time
                    text = msg_elem.find_element(By.CSS_SELECTOR, ".c-message__body").text
                    
                    # Apply keyword filters if specified
                    if filters and 'keywords' in filters:
                        keywords = filters['keywords']
                        if not any(keyword.lower() in text.lower() for keyword in keywords):
                            continue
                    
                    messages.append(text)
                    
                except Exception as e:
                    logger.error(f"Error extracting message: {str(e)}")
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.exception(f"Error getting messages from Slack: {str(e)}")
        
        return messages
    
    def send_message(self, message):
        """Send a message on Slack"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return False
        
        try:
            # Make sure text input is available
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor"))
            )
            
            # Enter message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send message (Enter key)
            message_input.send_keys(u'\ue007')  # Unicode for ENTER key
            
            # Wait for message to be sent
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.exception(f"Error sending message on Slack: {str(e)}")
            return False


class DiscordHandler(SeleniumBasedHandler):
    """Handler for Discord platform"""
    
    def __init__(self, credentials):
        super().__init__(credentials)
        self._login()
    
    def _login(self):
        """Login to Discord Web"""
        try:
            self.driver.get("https://discord.com/login")
            
            # Check if already logged in
            if self._is_logged_in():
                logger.info("Already logged in to Discord")
                return True
            
            # Enter email and password
            logger.info("Logging in to Discord...")
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
            )
            email_input.send_keys(self.credentials.get("email"))
            
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            password_input.send_keys(self.credentials.get("password"))
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 30).until(self._is_logged_in)
            
            logger.info("Successfully logged in to Discord")
            return True
            
        except Exception as e:
            logger.exception(f"Error logging in to Discord: {str(e)}")
            return False
    
    def _is_logged_in(self):
        """Check if logged in to Discord"""
        try:
            # Look for an element that is present when logged in
            self.driver.find_element(By.CSS_SELECTOR, ".guilds-1SWlCJ")
            return True
        except NoSuchElementException:
            return False
    
    def get_messages(self, filters=None):
        """Get messages from Discord"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return []
        
        messages = []
        try:
            # Navigate to specified channel if provided in filters
            if filters and 'channel' in filters:
                # Would need to implement navigation to specific channel
                pass
            
            # Get message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message-2qnXI6")
            
            # Set last check time if not set
            if not self.last_check:
                self.last_check = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago
            
            # Extract messages
            for msg_elem in message_elements[-15:]:  # Get latest 15 messages
                try:
                    # Extract message text
                    text = msg_elem.find_element(By.CSS_SELECTOR, ".messageContent-2qWWxC").text
                    
                    # Apply keyword filters if specified
                    if filters and 'keywords' in filters:
                        keywords = filters['keywords']
                        if not any(keyword.lower() in text.lower() for keyword in keywords):
                            continue
                    
                    messages.append(text)
                    
                except Exception as e:
                    logger.error(f"Error extracting message: {str(e)}")
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.exception(f"Error getting messages from Discord: {str(e)}")
        
        return messages
    
    def send_message(self, message):
        """Send a message on Discord"""
        if not self._is_logged_in():
            self._login()
            if not self._is_logged_in():
                return False
        
        try:
            # Make sure text input is available
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-slate-editor='true']"))
            )
            
            # Enter message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send message (Enter key)
            message_input.send_keys(u'\ue007')  # Unicode for ENTER key
            
            # Wait for message to be sent
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.exception(f"Error sending message on Discord: {str(e)}")
            return False


def get_platform_handler(platform_type, credentials):
    """
    Factory function to create a platform handler based on platform type
    
    Args:
        platform_type: Type of platform (telegram, whatsapp, slack, etc.)
        credentials: Dictionary of credentials for the platform
    
    Returns:
        Platform handler instance
    """
    handlers = {
        'telegram': TelegramHandler,
        'whatsapp': WhatsAppHandler,
        'slack': SlackHandler,
        'discord': DiscordHandler
    }
    
    if platform_type not in handlers:
        raise ValueError(f"Unsupported platform type: {platform_type}")
    
    return handlers[platform_type](credentials)
