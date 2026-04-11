import logging
import re
import json
import os
import time
import datetime
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration variables
max_timeout = int(os.getenv("DEFAULT_TIMEOUT", 20))
element_timeout = int(os.getenv("ELEMENT_TIMEOUT", 10))
screenshot_dir = os.getenv("SCREENSHOTS_DIRECTORY", "screenshots")
llm_responses_dir = os.getenv("LLM_RESPONSES_DIRECTORY", os.path.join(parent_dir, "logs", "helper_llm_responses"))

# Additional configuration from environment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s - %(levelname)s - %(message)s"

def setup_logging():
    """Configure logging for web automation."""
    logger = logging.getLogger(__name__)

    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Create logs directory in parent folder
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(parent_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, "helper_functions.log")

        # File handler
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler - show INFO and above in terminal for HTML report capture
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logging()

# Ensure screenshot directory exists
os.makedirs(screenshot_dir, exist_ok=True)

def wait_for_page_load(driver, timeout=max_timeout):
    """
    Wait for page to be fully loaded using JavaScript ready state.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("Page loaded completely")
        return True
    except TimeoutException:
        logger.warning(f"Page load timeout after {timeout} seconds")
        return False

def take_screenshot(driver, step_name, test_case_id):
    """
    Take a screenshot and save it with a descriptive filename.
    
    Args:
        driver: WebDriver instance
        step_name: Name of the current step
        test_case_id: Test case identifier
    """
    try:
        # Ensure screenshot directory exists
        os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove last 3 digits of microseconds
        # Clean step name for filename
        clean_step_name = re.sub(r'[^\w\s-]', '', step_name).strip()
        clean_step_name = re.sub(r'[-\s]+', '_', clean_step_name)
        
        filename = f"{test_case_id}_{clean_step_name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)
        
        driver.save_screenshot(filepath)
        logger.info(f"[{test_case_id}] Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"[{test_case_id}] Failed to take screenshot: {e}")
        return None

def find_element_robust(driver, locators, element_name="Element", timeout=element_timeout):
    """
    Find element using multiple locator strategies with robust error handling.
    
    Args:
        driver: WebDriver instance
        locators: Either a list of (locator_type, locator_value) tuples or a dict of locators
        element_name: Name for logging
        timeout: Timeout for each attempt
        
    Returns:
        WebElement or None
    """
    by_mapping = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css_selector": By.CSS_SELECTOR,
        "css selector": By.CSS_SELECTOR,
        "class_name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    
    # Convert dict format to list format for processing
    if isinstance(locators, dict):
        # Priority order for dict format
        locator_priority = ["id", "name", "css_selector", "xpath", "class_name", "tag_name", "link_text", "partial_link_text"]
        locator_list = []
        for key in locator_priority:
            if key in locators:
                locator_list.append((key, locators[key]))
    else:
        # Already in list format
        locator_list = locators
    
    for by_type, value in locator_list:
        selenium_by = by_mapping.get(by_type.lower())
        if not selenium_by:
            logger.warning(f"Unknown locator type: {by_type}")
            continue
            
        try:
            logger.info(f"Trying {by_type} for '{element_name}': {value}")
            
            # Try multiple waiting strategies for better compatibility
            element = None
            try:
                # First try: element to be clickable (good for buttons, links)
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((selenium_by, value))
                )
            except TimeoutException:
                try:
                    # Second try: presence of element (good for input fields, form elements)
                    element = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((selenium_by, value))
                    )
                    # Check if element is actually interactable
                    if element.is_displayed() and element.is_enabled():
                        logger.info(f"Found element using presence_of_element_located for '{element_name}'")
                    else:
                        element = None
                except TimeoutException:
                    try:
                        # Third try: visibility of element (good for elements that need to be visible)
                        element = WebDriverWait(driver, timeout).until(
                            EC.visibility_of_element_located((selenium_by, value))
                        )
                        logger.info(f"Found element using visibility_of_element_located for '{element_name}'")
                    except TimeoutException:
                        element = None
                        
            if element:
                logger.info(f"Successfully found '{element_name}' using {by_type}")
                return element
                
        except TimeoutException:
            logger.warning(f"Timeout finding '{element_name}' with {by_type}: {value}")
        except Exception as e:
            logger.warning(f"Error finding '{element_name}' with {by_type}: {e}")
    
    logger.error(f"Could not find '{element_name}' using any provided locator")
    return None

def login(driver, username, password, test_case_id, timeout=15):
    """
    Logs into the application and validates successful login.
    
    Args:
        driver: WebDriver instance
        username: Login username
        password: Login password
        test_case_id: Test case identifier for logging
        timeout: Maximum wait time for elements
        
    Returns:
        bool: True if login successful, False otherwise
    """
    logger.info(f"[{test_case_id}] Attempting login to application")
    
    try:
        # Take initial screenshot
        take_screenshot(driver, "login_page_loaded", test_case_id)
        
        # Locators for login elements
        USERNAME_LOCATORS = [
            ("name", "j_username"),
            ("id", "j_username"),
            ("xpath", "//input[@name='j_username']"),
            ("xpath", "//input[@type='text'][1]")
        ]
        
        PASSWORD_LOCATORS = [
            ("name", "j_password"),
            ("id", "j_password"),
            ("xpath", "//input[@name='j_password']"),
            ("xpath", "//input[@type='password']")
        ]
        
        LOGIN_BUTTON_LOCATORS = [
            ("xpath", "//button[@type='submit']"),
            ("xpath", "//button[contains(text(), 'Login')]"),
            ("xpath", "//input[@type='submit']"),
            ("css_selector", "button.btn.btn-primary"),
            ("css_selector", "input[value*='Login']")
        ]
        
        # Find and fill username
        username_input = find_element_robust(driver, USERNAME_LOCATORS, "Username input", timeout)
        if not username_input:
            logger.error(f"[{test_case_id}] Username input field not found")
            return False
            
        username_input.clear()
        username_input.send_keys(username)
        logger.info(f"[{test_case_id}] Username entered")
        take_screenshot(driver, "username_entered", test_case_id)
        
        # Find and fill password
        password_input = find_element_robust(driver, PASSWORD_LOCATORS, "Password input", timeout)
        if not password_input:
            logger.error(f"[{test_case_id}] Password input field not found")
            return False
            
        password_input.clear()
        password_input.send_keys(password)
        logger.info(f"[{test_case_id}] Password entered")
        take_screenshot(driver, "password_entered", test_case_id)
        
        # Click login button
        login_button = find_element_robust(driver, LOGIN_BUTTON_LOCATORS, "Login button", timeout)
        if not login_button:
            logger.error(f"[{test_case_id}] Login button not found")
            return False
            
        login_button.click()
        logger.info(f"[{test_case_id}] Login button clicked")
        take_screenshot(driver, "login_submitted", test_case_id)
        
        # Wait for page transition
        wait_for_page_load(driver, timeout=10)
        
        # Validate successful login - look for dashboard elements
        DASHBOARD_LOCATORS = [
            ("xpath", "//a[contains(text(), 'Home')]"),
            ("xpath", "//iframe"),
            ("xpath", "//*[contains(text(), 'Welcome')]"),
            ("xpath", "//*[@class='navbar' or @class='nav']"),
            ("css_selector", ".navbar, .nav, .dashboard")
        ]
        
        dashboard_element = find_element_robust(driver, DASHBOARD_LOCATORS, "Dashboard element", timeout)
        if dashboard_element:
            logger.info(f"[{test_case_id}] Login successful - dashboard loaded")
            take_screenshot(driver, "login_successful", test_case_id)
            return True
        else:
            logger.error(f"[{test_case_id}] Login failed - dashboard not found")
            take_screenshot(driver, "login_failed", test_case_id)
            return False
            
    except Exception as e:
        logger.error(f"[{test_case_id}] Login process failed with exception: {e}")
        take_screenshot(driver, "login_exception", test_case_id)
        return False

def scroll_to_element(driver, element):
    """
    Scroll to make an element visible in the viewport.
    
    Args:
        driver: WebDriver instance
        element: WebElement to scroll to
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # Wait for scroll animation
        logger.info("Scrolled to element")
    except Exception as e:
        logger.warning(f"Failed to scroll to element: {e}")

def safe_click(driver, element, element_name="Element"):
    """
    Safely click an element with multiple strategies.
    
    Args:
        driver: WebDriver instance
        element: WebElement to click
        element_name: Name for logging
        
    Returns:
        bool: True if click successful
    """
    try:
        # First try regular click
        element.click()
        logger.info(f"Successfully clicked {element_name}")
        return True
    except Exception as e:
        logger.warning(f"Regular click failed for {element_name}: {e}")
        
        try:
            # Try JavaScript click
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"Successfully clicked {element_name} using JavaScript")
            return True
        except Exception as e2:
            logger.warning(f"JavaScript click failed for {element_name}: {e2}")
            
            try:
                # Try ActionChains click
                ActionChains(driver).move_to_element(element).click().perform()
                logger.info(f"Successfully clicked {element_name} using ActionChains")
                return True
            except Exception as e3:
                logger.error(f"All click methods failed for {element_name}: {e3}")
                return False

def safe_send_keys(element, text, element_name="Element"):
    """
    Safely send keys to an element with error handling.
    
    Args:
        element: WebElement to send keys to
        text: Text to send
        element_name: Name for logging
        
    Returns:
        bool: True if successful
    """
    try:
        element.clear()
        element.send_keys(text)
        logger.info(f"Successfully sent keys to {element_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send keys to {element_name}: {e}")
        return False

def get_element_text(element, element_name="Element"):
    """
    Get text from an element with error handling.
    
    Args:
        element: WebElement to get text from
        element_name: Name for logging
        
    Returns:
        str: Element text or empty string if failed
    """
    try:
        text = element.text.strip()
        if not text:
            text = element.get_attribute("value") or ""
        logger.info(f"Got text from {element_name}: '{text}'")
        return text
    except Exception as e:
        logger.error(f"Failed to get text from {element_name}: {e}")
        return ""

def wait_and_click(driver, locators, element_name, timeout=element_timeout):
    """
    Wait for element and click it safely.
    
    Args:
        driver: WebDriver instance
        locators: Either a list of locator tuples or a dict of locators
        element_name: Name for logging
        timeout: Wait timeout
        
    Returns:
        bool: True if successful
    """
    element = find_element_robust(driver, locators, element_name, timeout)
    if element:
        scroll_to_element(driver, element)
        return safe_click(driver, element, element_name)
    return False

def close_browser_safely(driver, test_case_id):
    """
    Safely close browser with proper cleanup.
    
    Args:
        driver: WebDriver instance
        test_case_id: Test case identifier
    """
    try:
        logger.info(f"[{test_case_id}] Closing browser")
        take_screenshot(driver, "test_completed", test_case_id)
        driver.quit()
        logger.info(f"[{test_case_id}] Browser closed successfully")
    except Exception as e:
        logger.error(f"[{test_case_id}] Error closing browser: {e}")
        try:
            driver.quit()
        except:
            pass

def launch_browser(base_url=None):
    try:
        # Fresh profile directory so no previous credentials exist
        user_data_dir = tempfile.mkdtemp()

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-data-dir=" + user_data_dir)

        # Kill ALL Safe Browsing / password checks
        chrome_options.add_argument("--safebrowsing-disable-download-protection")
        chrome_options.add_argument("--safebrowsing-disable-auto-update")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-features=SafeBrowsingEnhancedProtection,PasswordLeakDetection,PasswordCheck,SecurityInterstitials,SafeBrowsingUrlClassifier,SyncPasswordLeakDetection")
        
        # Suppress GCM/Cloud Messaging logs
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-gpu-logging")

        # Turn off password manager completely
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Use ChromeDriver (ChromeDriverManager will handle driver installation)
        service = ChromeService(log_path=os.devnull)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Hide automation flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        if base_url:
            driver.get(base_url)
            wait_for_page_load(driver)

        return driver

    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        raise