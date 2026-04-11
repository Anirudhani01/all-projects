#!/usr/bin/env python3
"""
OpenCRX Web Application Locator Extractor

This script automates the process of logging into the openCRX web application,
navigating through all accessible pages, and extracting web element locators
to generate a comprehensive locators.json file for test automation.

Features:
- Automated login to openCRX system
- Systematic page discovery and navigation
- Multiple locator strategy generation (ID, name, XPath, CSS)
- JSON output following sample_locators.json structure
- Robust error handling and wait strategies

Author: Claude Code Assistant
Date: 2025-08-11
"""

import json
import os
import time
import logging
import re
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

class OpenCRXLocatorExtractor:
    """Main class for extracting web element locators from OpenCRX application."""
    
    def __init__(self):
        """Initialize the locator extractor with configuration."""
        self.setup_logging()
        self.load_environment()
        self.driver = None
        self.wait = None
        self.visited_urls = set()
        self.page_queue = deque()
        self.locators_data = defaultdict(dict)
        self.session_urls = set()
        self.session_cookies = []
        self.failed_urls = set()  # Track URLs that consistently fail
        self.failed_attempts = defaultdict(int)  # Track failure counts per URL
        
        # Element type mappings for categorization
        self.element_categories = {
            'input': ['input', 'textarea'],
            'button': ['button', 'input[type="submit"]', 'input[type="button"]', 'input[type="reset"]'],
            'navigation': ['a', 'nav', 'ul[class*="nav"]', 'ul[class*="menu"]'],
            'form': ['form', 'fieldset', 'label'],
            'table': ['table', 'thead', 'tbody', 'tr', 'td', 'th'],
            'modal': ['div[class*="modal"]', 'div[class*="dialog"]', 'div[class*="popup"]'],
            'message': ['div[class*="alert"]', 'div[class*="message"]', 'div[class*="notification"]']
        }
    
    def setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('opencrx_locator_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_environment(self):
        """Load configuration from environment variables."""
        load_dotenv()
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8080/opencrx-core-CRX')
        self.username = os.getenv('APP_USERNAME', 'admin-Standard')
        self.password = os.getenv('APP_PASSWORD', 'admin-Standard')
        
        self.logger.info(f"Configuration loaded - Base URL: {self.base_url}")
    
    def setup_webdriver(self, headless: bool = False) -> webdriver.Chrome:
        """Initialize and configure Chrome WebDriver with session management."""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        # Enhanced session management options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        
        # Windows-compatible temp directory
        import tempfile
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Setup Chrome driver with automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(15)  # Increased wait time
        
        # Execute script to hide automation flags
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def safe_wait_and_find(self, by: By, value: str, timeout: int = 10) -> Optional[WebElement]:
        """Safely wait for and find an element with error handling."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found within {timeout}s: {by} = {value}")
            return None
    
    def is_logged_in(self) -> bool:
        """Check if the user is currently logged in."""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for login indicators
            login_indicators = [
                "Login.jsp" in current_url,
                "loginFailed" in current_url,
                "j_username" in page_source,
                "j_password" in page_source,
                "login" in self.driver.title.lower()
            ]
            
            # If any login indicators are present, user is not logged in
            if any(login_indicators):
                return False
                
            # Check for logged-in indicators
            logged_in_indicators = [
                "logout" in page_source,
                "admin-standard" in page_source,
                "objectinspectorservlet" in current_url.lower(),
                "home" in page_source or "dashboard" in page_source
            ]
            
            return any(logged_in_indicators)
            
        except Exception as e:
            self.logger.debug(f"Error checking login status: {str(e)}")
            return False
    
    def ensure_logged_in(self) -> bool:
        """Ensure user is logged in, re-authenticate if necessary."""
        if self.is_logged_in():
            return True
        
        self.logger.info("Session expired or not logged in, attempting to login...")
        return self.login_to_opencrx()
    
    def login_to_opencrx(self) -> bool:
        """Perform login to the OpenCRX application with enhanced session handling."""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                attempt += 1
                self.logger.info(f"Starting login attempt {attempt}/{max_attempts}...")
                
                # Navigate to base URL
                self.driver.get(self.base_url)
                
                # Wait for page to stabilize
                time.sleep(3)
                current_url = self.driver.current_url
                self.logger.info(f"Current URL after navigation: {current_url}")
                
                # Check if already logged in
                if self.is_logged_in():
                    self.logger.info("Already logged in!")
                    return True
                
                # Find username field with multiple strategies
                username_field = None
                for selector in [("name", "j_username"), ("id", "j_username"), ("xpath", "//input[@type='text']")]:
                    username_field = self.safe_wait_and_find(By.__dict__[selector[0].upper()], selector[1], 10)
                    if username_field:
                        break
                
                if not username_field:
                    self.logger.error("Username field not found")
                    continue
                
                # Find password field with multiple strategies
                password_field = None
                for selector in [("name", "j_password"), ("id", "j_password"), ("xpath", "//input[@type='password']")]:
                    password_field = self.safe_wait_and_find(By.__dict__[selector[0].upper()], selector[1], 10)
                    if password_field:
                        break
                
                if not password_field:
                    self.logger.error("Password field not found")
                    continue
                
                # Clear and fill credentials
                self.logger.info("Entering credentials...")
                username_field.clear()
                time.sleep(0.5)
                username_field.send_keys(self.username)
                time.sleep(0.5)
                
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(self.password)
                time.sleep(1)
                
                # Find and click login button
                login_button = None
                for selector in [
                    ("xpath", "//button[@type='submit']"),
                    ("xpath", "//input[@type='submit']"),
                    ("xpath", "//button[contains(text(), 'Login')]"),
                    ("css_selector", ".btn-primary")
                ]:
                    login_button = self.safe_wait_and_find(By.__dict__[selector[0].upper()], selector[1], 5)
                    if login_button:
                        break
                
                if not login_button:
                    self.logger.error("Login button not found")
                    continue
                
                self.logger.info("Clicking login button...")
                login_button.click()
                
                # Wait for navigation and check login status
                time.sleep(5)
                
                # Wait for potential redirects to complete
                for i in range(10):  # Wait up to 10 seconds
                    if self.is_logged_in():
                        break
                    time.sleep(1)
                
                if self.is_logged_in():
                    final_url = self.driver.current_url
                    self.logger.info(f"Login successful! Redirected to: {final_url}")
                    
                    # Save cookies for session persistence
                    self.session_cookies = self.driver.get_cookies()
                    return True
                else:
                    self.logger.warning(f"Login attempt {attempt} failed")
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Login attempt {attempt} failed with exception: {str(e)}")
                time.sleep(2)
        
        self.logger.error("All login attempts failed")
        return False
    
    def extract_opencrx_navigation_links(self) -> Dict[str, List[str]]:
        """Extract OpenCRX-specific navigation links organized by menu sections."""
        navigation_structure = {
            'home': [],
            'manage_accounts': [],
            'manage_activities': [],
            'sales': [],
            'products': [],
            'depots': [],
            'folders_documents': [],
            'admin': [],
            'wizards': [],
            'other': []
        }
        
        try:
            # Ensure we're logged in
            if not self.ensure_logged_in():
                return navigation_structure
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Extract main navigation menu links
            main_nav_selectors = [
                ".navbar-nav a",
                ".nav-link",
                "#nav a",
                ".nav a",
                "ul.navbar-nav a",
                ".navigation a"
            ]
            
            found_links = []
            for selector in main_nav_selectors:
                try:
                    nav_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in nav_elements:
                        try:
                            href = element.get_attribute("href")
                            text = element.text.strip().lower()
                            
                            if href and self.is_valid_internal_link(href) and href not in self.visited_urls:
                                found_links.append((href, text))
                        except StaleElementReferenceException:
                            continue
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {str(e)}")
                    continue
            
            # Categorize links based on text content
            for href, text in found_links:
                if any(keyword in text for keyword in ['home', 'dashboard']):
                    navigation_structure['home'].append(href)
                elif any(keyword in text for keyword in ['account', 'contact', 'customer']):
                    navigation_structure['manage_accounts'].append(href)
                elif any(keyword in text for keyword in ['activit', 'task', 'event']):
                    navigation_structure['manage_activities'].append(href)
                elif any(keyword in text for keyword in ['sales', 'opportunity', 'lead', 'contract']):
                    navigation_structure['sales'].append(href)
                elif any(keyword in text for keyword in ['product', 'catalog', 'inventory']):
                    navigation_structure['products'].append(href)
                elif any(keyword in text for keyword in ['depot', 'warehouse', 'stock']):
                    navigation_structure['depots'].append(href)
                elif any(keyword in text for keyword in ['folder', 'document', 'file']):
                    navigation_structure['folders_documents'].append(href)
                elif any(keyword in text for keyword in ['admin', 'setting', 'config', 'user']):
                    navigation_structure['admin'].append(href)
                elif any(keyword in text for keyword in ['wizard', 'helper', 'tool']):
                    navigation_structure['wizards'].append(href)
                else:
                    navigation_structure['other'].append(href)
            
            # Also extract wizard and utility links
            wizard_selectors = [
                "a[href*='wizard']",
                "a[href*='helper']",
                "a[href*='tool']"
            ]
            
            for selector in wizard_selectors:
                try:
                    wizard_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in wizard_elements:
                        try:
                            href = element.get_attribute("href")
                            if href and self.is_valid_internal_link(href) and href not in self.visited_urls:
                                navigation_structure['wizards'].append(href)
                        except StaleElementReferenceException:
                            continue
                except Exception:
                    continue
            
            # Remove duplicates from each category
            for category in navigation_structure:
                navigation_structure[category] = list(set(navigation_structure[category]))
            
            total_links = sum(len(links) for links in navigation_structure.values())
            self.logger.info(f"Extracted {total_links} navigation links across {len(navigation_structure)} categories")
            
            return navigation_structure
            
        except Exception as e:
            self.logger.error(f"Error extracting OpenCRX navigation links: {str(e)}")
            return navigation_structure
    
    def extract_page_links(self) -> List[str]:
        """Extract all unique links from the current page with session validation."""
        links = []
        try:
            # Ensure we're still logged in
            if not self.ensure_logged_in():
                return links
            
            # Find all anchor tags
            anchor_elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for anchor in anchor_elements:
                try:
                    href = anchor.get_attribute("href")
                    if href and self.is_valid_internal_link(href):
                        full_url = urljoin(self.driver.current_url, href)
                        if full_url not in self.visited_urls:
                            links.append(full_url)
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error extracting link: {str(e)}")
                    continue
                    
            # Find navigation items that might not be anchor tags
            nav_elements = self.driver.find_elements(By.XPATH, 
                "//nav//li | //ul[contains(@class,'nav')]//li | //ul[contains(@class,'menu')]//li")
            
            for nav_item in nav_elements:
                try:
                    # Look for clickable elements within nav items
                    clickable = nav_item.find_element(By.XPATH, ".//a | .//button")
                    href = clickable.get_attribute("href")
                    if href and self.is_valid_internal_link(href):
                        full_url = urljoin(self.driver.current_url, href)
                        if full_url not in self.visited_urls:
                            links.append(full_url)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error extracting page links: {str(e)}")
        
        return list(set(links))  # Remove duplicates
    
    def is_valid_internal_link(self, href: str) -> bool:
        """Check if a link is valid for crawling."""
        if not href or href.startswith('#') or href.startswith('javascript:'):
            return False
            
        if href.startswith('mailto:') or href.startswith('tel:'):
            return False
            
        # Check if it's an internal link or relative link
        parsed = urlparse(href)
        base_parsed = urlparse(self.base_url)
        
        if parsed.netloc and parsed.netloc != base_parsed.netloc:
            return False
            
        # Exclude certain file types
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png', '.gif', '.zip']
        if any(href.lower().endswith(ext) for ext in excluded_extensions):
            return False
            
        return True
    
    def generate_element_locators(self, element: WebElement, page_context: str) -> Dict[str, Any]:
        """Generate multiple locator strategies for a web element."""
        locators = {
            "alternatives": [],
            "description": ""
        }
        
        try:
            # Get element attributes
            tag_name = element.tag_name.lower()
            element_id = element.get_attribute("id")
            element_name = element.get_attribute("name")
            element_class = element.get_attribute("class")
            element_type = element.get_attribute("type")
            placeholder = element.get_attribute("placeholder")
            text_content = element.text.strip()
            
            # Primary locator (most reliable)
            primary_locator = None
            
            if element_id:
                primary_locator = {"by": "id", "value": element_id}
                locators["alternatives"].append({"by": "css_selector", "value": f"#{element_id}"})
                
            elif element_name:
                primary_locator = {"by": "name", "value": element_name}
                locators["alternatives"].append({"by": "css_selector", "value": f"[name='{element_name}']"})
                
            elif element_class:
                classes = element_class.split()
                if classes:
                    primary_locator = {"by": "class_name", "value": classes[0]}
                    locators["alternatives"].append({"by": "css_selector", "value": f".{classes[0]}"})
            
            # If no primary locator found, use tag name
            if not primary_locator:
                primary_locator = {"by": "tag_name", "value": tag_name}
            
            locators["by"] = primary_locator["by"]
            locators["value"] = primary_locator["value"]
            
            # Generate XPath alternatives
            xpath_strategies = []
            
            if element_id:
                xpath_strategies.append(f"//{tag_name}[@id='{element_id}']")
            
            if element_name:
                xpath_strategies.append(f"//{tag_name}[@name='{element_name}']")
                
            if element_type:
                xpath_strategies.append(f"//{tag_name}[@type='{element_type}']")
                
            if placeholder:
                xpath_strategies.append(f"//{tag_name}[@placeholder='{placeholder}']")
                
            if text_content and len(text_content) < 50:
                xpath_strategies.append(f"//{tag_name}[contains(text(), '{text_content}')]")
            
            # Add XPath alternatives
            for xpath in xpath_strategies[:3]:  # Limit to top 3 XPath strategies
                locators["alternatives"].append({"by": "xpath", "value": xpath})
            
            # Generate CSS selector alternatives
            css_strategies = []
            
            if element_type:
                css_strategies.append(f"{tag_name}[type='{element_type}']")
                
            if placeholder:
                css_strategies.append(f"{tag_name}[placeholder*='{placeholder}']")
                
            if element_class:
                classes = element_class.split()
                for cls in classes[:2]:  # Use first 2 classes
                    css_strategies.append(f"{tag_name}.{cls}")
            
            # Add CSS alternatives
            for css in css_strategies[:2]:  # Limit to top 2 CSS strategies
                locators["alternatives"].append({"by": "css_selector", "value": css})
            
            # Generate description
            description_parts = []
            if element_type:
                description_parts.append(f"{element_type} {tag_name}")
            else:
                description_parts.append(tag_name)
                
            if placeholder:
                description_parts.append(f"with placeholder '{placeholder}'")
            elif text_content and len(text_content) < 30:
                description_parts.append(f"containing '{text_content}'")
                
            description_parts.append(f"on {page_context} page")
            
            locators["description"] = " ".join(description_parts)
            
        except Exception as e:
            self.logger.debug(f"Error generating locators for element: {str(e)}")
            locators["description"] = f"Unknown {tag_name} element"
        
        return locators
    
    def extract_page_elements(self, page_name: str) -> Dict[str, Dict[str, Any]]:
        """Extract all relevant elements from the current page with OpenCRX-specific focus."""
        page_elements = {}
        
        try:
            # Ensure we're still logged in
            if not self.ensure_logged_in():
                return page_elements
            
            # Define OpenCRX-specific element selectors
            selectors = {
                # OpenCRX specific input elements
                'input_fields': "//input[@type='text' or @type='email' or @type='number' or @type='search' or not(@type)]",
                'password_fields': "//input[@type='password']",
                'textarea_fields': "//textarea",
                'select_fields': "//select",
                'checkbox_fields': "//input[@type='checkbox']",
                'radio_fields': "//input[@type='radio']",
                'hidden_fields': "//input[@type='hidden' and @name]",  # OpenCRX uses many hidden fields
                
                # OpenCRX specific buttons and controls
                'buttons': "//button | //input[@type='submit'] | //input[@type='button'] | //input[@type='reset']",
                'action_buttons': "//button[contains(@class,'btn')] | //a[contains(@class,'btn')]",
                'toolbar_buttons': "//div[contains(@class,'toolbar')]//button | //div[contains(@class,'toolbar')]//a",
                
                # OpenCRX navigation elements
                'navigation_links': "//a[@href and contains(@class,'nav-link')]",
                'menu_links': "//ul[contains(@class,'navbar-nav')]//a | //ul[contains(@class,'nav')]//a",
                'breadcrumb_links': "//ol[contains(@class,'breadcrumb')]//a | //li[contains(@class,'breadcrumb-item')]//a",
                'tab_links': "//ul[contains(@class,'nav-tabs')]//a | //ul[contains(@class,'nav-pills')]//a",
                
                # OpenCRX content areas
                'content_areas': "//div[@id='content'] | //div[@id='inspContent'] | //div[contains(@class,'tab-content')]",
                'form_sections': "//fieldset | //div[contains(@class,'form-group')] | //div[contains(@class,'field-group')]",
                'data_tables': "//table[contains(@class,'table')] | //table[contains(@class,'data-table')] | //table[@class='fieldGroup']",
                
                # OpenCRX specific interface elements
                'search_controls': "//form[@id='SearchInput'] | //input[@id='searchExpression'] | //div[contains(@class,'search')]",
                'dropdown_menus': "//div[contains(@class,'dropdown')] | //select[contains(@class,'form-control')]",
                'modal_dialogs': "//div[contains(@class,'modal')] | //div[contains(@class,'dialog')]",
                
                # OpenCRX headers and labels
                'page_headers': "//h1 | //h2 | //h3 | //div[contains(@class,'page-header')]",
                'field_labels': "//label | //td[contains(@class,'label')] | //span[contains(@class,'label')]",
                
                # OpenCRX forms
                'forms': "//form",
                'form_controls': "//div[contains(@class,'form-control')] | //div[contains(@class,'input-group')]",
                
                # OpenCRX specific UI components
                'workspace_elements': "//div[contains(@class,'workspace')] | //table[contains(@class,'workspaceDashboard')]",
                'inspector_elements': "//div[contains(@class,'inspContent')] | //div[contains(@class,'inspector')]",
                'wizard_elements': "//div[contains(@class,'wizard')] | //form[contains(@action,'wizard')]",
                
                # Error and message elements
                'alert_messages': "//div[contains(@class,'alert')] | //div[contains(@class,'message')] | //div[contains(@class,'notification')]"
            }
            
            element_counter = defaultdict(int)
            processed_elements = set()  # To avoid duplicates
            
            for element_type, xpath_selector in selectors.items():
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    
                    for element in elements:
                        try:
                            # Skip if element is not displayed or already processed
                            if not element.is_displayed():
                                continue
                            
                            # Create a unique identifier for the element
                            element_id = f"{element.tag_name}_{element.get_attribute('id') or element.get_attribute('name') or element.get_attribute('class') or 'unnamed'}"
                            if element_id in processed_elements:
                                continue
                            processed_elements.add(element_id)
                                
                            element_counter[element_type] += 1
                            count = element_counter[element_type]
                            
                            # Generate a unique key for this element
                            element_key = self.generate_element_key(element, element_type, count)
                            
                            # Skip if we already have this element key
                            if element_key in page_elements:
                                continue
                            
                            # Generate locators with enhanced strategies
                            locators = self.generate_element_locators(element, page_name)
                            
                            # Add element only if we could generate meaningful locators
                            if locators and locators.get('by') and locators.get('value'):
                                page_elements[element_key] = locators
                            
                        except StaleElementReferenceException:
                            continue
                        except Exception as e:
                            self.logger.debug(f"Error processing element: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Error finding elements with selector {xpath_selector}: {str(e)}")
                    continue
            
            # Filter out login elements if we're not on the login page
            if 'login' not in page_name.lower():
                filtered_elements = {}
                for key, value in page_elements.items():
                    # Skip obvious login-related elements
                    if not any(login_term in key.lower() for login_term in ['j_username', 'j_password', 'login']):
                        filtered_elements[key] = value
                page_elements = filtered_elements
            
            self.logger.info(f"Extracted {len(page_elements)} unique elements from {page_name}")
            
        except Exception as e:
            self.logger.error(f"Error extracting elements from page {page_name}: {str(e)}")
        
        return page_elements
    
    def generate_element_key(self, element: WebElement, element_type: str, count: int) -> str:
        """Generate a unique key for an element based on its attributes."""
        try:
            element_id = element.get_attribute("id")
            element_name = element.get_attribute("name")
            placeholder = element.get_attribute("placeholder")
            text_content = element.text.strip()
            
            # Priority order for key generation
            if element_id:
                return f"{element_id}"
            elif element_name:
                return f"{element_name}_{element_type}"
            elif placeholder:
                clean_placeholder = re.sub(r'[^a-zA-Z0-9_]', '_', placeholder.lower())
                return f"{clean_placeholder}_{element_type}"
            elif text_content and len(text_content) < 30:
                clean_text = re.sub(r'[^a-zA-Z0-9_]', '_', text_content.lower())
                return f"{clean_text}_{element_type}"
            else:
                return f"{element_type}_{count}"
                
        except:
            return f"{element_type}_{count}"
    
    def get_page_category(self, url: str, page_title: str) -> str:
        """Determine the category/section for a page based on OpenCRX URL patterns and content."""
        url_lower = url.lower()
        title_lower = page_title.lower()
        
        # OpenCRX-specific URL patterns
        if 'login' in url_lower or 'signin' in url_lower:
            return 'login_page'
        elif 'userhome' in url_lower or 'home' in url_lower:
            return 'home_dashboard'
        elif 'account' in url_lower and 'manage' not in url_lower:
            return 'manage_accounts'
        elif 'activity' in url_lower:
            return 'manage_activities'
        elif 'contract' in url_lower or 'opportunity' in url_lower or 'lead' in url_lower:
            return 'sales_contracts'
        elif 'product' in url_lower:
            return 'products_catalog'
        elif 'depot' in url_lower or 'warehouse' in url_lower:
            return 'depots_inventory'
        elif 'document' in url_lower or 'folder' in url_lower:
            return 'folders_documents'
        elif 'wizard' in url_lower or 'helper' in url_lower:
            return 'wizards_tools'
        elif 'admin' in url_lower or 'setting' in url_lower or 'config' in url_lower:
            return 'admin_settings'
        elif 'report' in url_lower:
            return 'reports'
        elif 'objectinspectorservlet' in url_lower:
            return 'object_inspector'
        elif 'workspace' in url_lower:
            return 'workspaces'
        elif 'search' in url_lower:
            return 'search_results'
        
        # Check page content for more accurate categorization
        try:
            if self.driver:
                page_source = self.driver.page_source.lower()
                
                # Check for specific OpenCRX content patterns
                if 'manage accounts' in page_source or 'account management' in page_source:
                    return 'manage_accounts'
                elif 'manage activities' in page_source or 'activity management' in page_source:
                    return 'manage_activities'
                elif 'sales' in page_source and ('contract' in page_source or 'opportunity' in page_source):
                    return 'sales_contracts'
                elif 'product catalog' in page_source or 'product management' in page_source:
                    return 'products_catalog'
                elif 'depot' in page_source or 'inventory' in page_source:
                    return 'depots_inventory'
                elif 'document' in page_source and 'folder' in page_source:
                    return 'folders_documents'
                elif 'admin' in page_source and ('user' in page_source or 'setting' in page_source):
                    return 'admin_settings'
                elif 'wizard' in page_source or 'tool' in page_source:
                    return 'wizards_tools'
        except Exception:
            pass
        
        # Check title patterns for fallback categorization
        if any(word in title_lower for word in ['login', 'sign in', 'authentication']):
            return 'login_page'
        elif any(word in title_lower for word in ['dashboard', 'home', 'main']):
            return 'home_dashboard'
        elif any(word in title_lower for word in ['account', 'contact', 'customer']):
            return 'manage_accounts'
        elif any(word in title_lower for word in ['activity', 'task', 'event']):
            return 'manage_activities'
        elif any(word in title_lower for word in ['sales', 'contract', 'opportunity']):
            return 'sales_contracts'
        elif 'product' in title_lower:
            return 'products_catalog'
        elif any(word in title_lower for word in ['depot', 'warehouse', 'inventory']):
            return 'depots_inventory'
        elif any(word in title_lower for word in ['document', 'folder', 'file']):
            return 'folders_documents'
        elif any(word in title_lower for word in ['admin', 'setting', 'configuration']):
            return 'admin_settings'
        elif any(word in title_lower for word in ['wizard', 'helper', 'tool']):
            return 'wizards_tools'
        elif 'report' in title_lower:
            return 'reports'
        
        # Extract meaningful category from URL structure
        path_parts = urlparse(url).path.strip('/').split('/')
        for part in path_parts:
            if part and len(part) > 3:
                clean_part = re.sub(r'[^a-zA-Z0-9_]', '_', part.lower())
                if clean_part not in ['opencrx', 'core', 'crx', 'jsp', 'servlet']:
                    return clean_part
        
        return 'general_page'
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for OpenCRX page to fully load with multiple indicators."""
        try:
            # Wait for basic page ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Wait for OpenCRX specific elements to be present
            opencrx_indicators = [
                (By.ID, "content"),
                (By.ID, "nav"),
                (By.CLASS_NAME, "container-fluid"),
                (By.CSS_SELECTOR, ".navbar"),
                (By.XPATH, "//div[contains(@class, 'content')]")
            ]
            
            for by, selector in opencrx_indicators:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            # Small additional wait for dynamic content
            time.sleep(1)
            return True
            
        except Exception as e:
            self.logger.debug(f"Page load wait failed: {str(e)}")
            return False
    
    def should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped due to repeated failures."""
        if url in self.failed_urls:
            return True
        if self.failed_attempts[url] >= 2:  # Max 2 attempts per URL
            self.failed_urls.add(url)
            return True
        return False
    
    def try_access_page(self, url: str, max_retries: int = 1) -> bool:
        """Try to access a page with proper error handling."""
        for attempt in range(max_retries + 1):
            try:
                # Check if we should skip this URL
                if self.should_skip_url(url):
                    return False
                
                # Ensure we're still logged in
                if not self.ensure_logged_in():
                    self.logger.warning("Cannot ensure login, skipping page")
                    return False
                
                # Navigate to the page
                self.driver.get(url)
                
                # Wait for page to load
                if not self.wait_for_page_load():
                    self.logger.warning(f"Page load timeout for {url}")
                    self.failed_attempts[url] += 1
                    continue
                
                # Check if we got redirected to login
                if not self.is_logged_in():
                    self.logger.warning(f"Redirected to login for {url}, attempt {attempt + 1}")
                    self.failed_attempts[url] += 1
                    
                    # Try to re-login if this is not the last attempt
                    if attempt < max_retries:
                        if self.ensure_logged_in():
                            continue
                    return False
                
                # Success - reset failure count
                if url in self.failed_attempts:
                    del self.failed_attempts[url]
                return True
                
            except Exception as e:
                self.logger.error(f"Exception accessing {url}: {str(e)}")
                self.failed_attempts[url] += 1
                
        return False
    
    def extract_main_menu_links(self) -> List[str]:
        """Extract main navigation menu links (not wizard links)."""
        main_links = []
        try:
            # Focus on main navigation elements, not wizard/utility links
            main_nav_selectors = [
                ".navbar-nav a[href*='ObjectInspectorServlet']",  # Main navigation
                "a[href*='segment'][href*='Standard']",            # Standard segment links
                ".nav-link[href*='ObjectInspectorServlet']"       # Navigation links
            ]
            
            for selector in main_nav_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        text = element.text.strip()
                        
                        # Skip wizard and utility links
                        if href and not any(skip_word in href.lower() for skip_word in ['wizard', 'helper', 'tool']):
                            if self.is_valid_internal_link(href) and href not in main_links:
                                main_links.append(href)
                                self.logger.debug(f"Found main nav link: {text} -> {href}")
                        
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {str(e)}")
                    continue
            
            return main_links[:20]  # Limit to reasonable number
            
        except Exception as e:
            self.logger.error(f"Error extracting main menu links: {str(e)}")
            return []
    
    def crawl_pages_hierarchically(self, max_pages: int = 50) -> None:
        """Hierarchically crawl OpenCRX pages with improved failure handling."""
        try:
            # Ensure we're logged in
            if not self.ensure_logged_in():
                self.logger.error("Cannot proceed with crawling - login failed")
                return
            
            # Start with current page (dashboard)
            current_url = self.driver.current_url
            self.logger.info(f"Starting crawl from dashboard: {current_url}")
            
            pages_crawled = 0
            
            # First, extract elements from the current dashboard page
            if self.try_access_page(current_url):
                self.visited_urls.add(current_url)
                page_title = self.driver.title
                page_category = self.get_page_category(current_url, page_title)
                page_elements = self.extract_page_elements(page_category)
                
                if page_elements:
                    self.locators_data[page_category] = page_elements
                    self.logger.info(f"Added {len(page_elements)} elements to {page_category} category")
                
                pages_crawled += 1
            
            # Extract main navigation links (avoid wizard links that keep failing)
            self.logger.info("Extracting main navigation links...")
            main_nav_links = self.extract_main_menu_links()
            self.logger.info(f"Found {len(main_nav_links)} main navigation links")
            
            # Process main navigation links
            for url in main_nav_links:
                if pages_crawled >= max_pages:
                    break
                    
                if url in self.visited_urls or self.should_skip_url(url):
                    continue
                
                self.logger.info(f"Crawling main nav page {pages_crawled + 1}: {url}")
                
                if self.try_access_page(url):
                    self.visited_urls.add(url)
                    pages_crawled += 1
                    
                    # Get page information
                    page_title = self.driver.title
                    page_category = self.get_page_category(url, page_title)
                    
                    self.logger.info(f"Processing page as category: {page_category}")
                    
                    # Extract elements
                    page_elements = self.extract_page_elements(page_category)
                    
                    if page_elements:
                        if page_category in self.locators_data:
                            existing_elements = self.locators_data[page_category]
                            new_count = 0
                            for element_key, element_data in page_elements.items():
                                if element_key not in existing_elements:
                                    existing_elements[element_key] = element_data
                                    new_count += 1
                            if new_count > 0:
                                self.logger.info(f"Added {new_count} new elements to existing {page_category} category")
                        else:
                            self.locators_data[page_category] = page_elements
                            self.logger.info(f"Added {len(page_elements)} elements to new {page_category} category")
                    
                    # Extract secondary links from this page
                    additional_links = self.extract_page_links()
                    secondary_links = [link for link in additional_links 
                                     if link not in self.visited_urls and 
                                     not self.should_skip_url(link) and
                                     'wizard' not in link.lower()][:5]  # Limit secondary links
                    
                    # Process some secondary links
                    for secondary_url in secondary_links:
                        if pages_crawled >= max_pages:
                            break
                            
                        self.logger.info(f"Crawling secondary page {pages_crawled + 1}: {secondary_url}")
                        
                        if self.try_access_page(secondary_url):
                            self.visited_urls.add(secondary_url)
                            pages_crawled += 1
                            
                            sec_page_title = self.driver.title
                            sec_page_category = self.get_page_category(secondary_url, sec_page_title)
                            sec_page_elements = self.extract_page_elements(sec_page_category)
                            
                            if sec_page_elements:
                                if sec_page_category in self.locators_data:
                                    existing_elements = self.locators_data[sec_page_category]
                                    new_count = 0
                                    for element_key, element_data in sec_page_elements.items():
                                        if element_key not in existing_elements:
                                            existing_elements[element_key] = element_data
                                            new_count += 1
                                    if new_count > 0:
                                        self.logger.info(f"Added {new_count} new elements to {sec_page_category}")
                                else:
                                    self.locators_data[sec_page_category] = sec_page_elements
                                    self.logger.info(f"Added {len(sec_page_elements)} elements to new {sec_page_category} category")
                    
                    time.sleep(1)  # Small delay between pages
                else:
                    self.logger.warning(f"Failed to access page: {url}")
            
            # Log summary of failed URLs
            if self.failed_urls:
                self.logger.info(f"Skipped {len(self.failed_urls)} consistently failing URLs")
                for failed_url in list(self.failed_urls)[:5]:  # Log first 5 failed URLs
                    self.logger.debug(f"Failed URL: {failed_url}")
            
            self.logger.info(f"Hierarchical crawling completed. Visited {pages_crawled} pages, discovered {len(self.locators_data)} categories")
            
        except Exception as e:
            self.logger.error(f"Error during hierarchical page crawling: {str(e)}")
    
    def crawl_pages(self, max_pages: int = 50) -> None:
        """Main entry point for page crawling - uses hierarchical approach."""
        self.crawl_pages_hierarchically(max_pages)
    
    def save_locators_json(self, output_file: str = "locators.json") -> None:
        """Save the extracted locators to a JSON file."""
        try:
            # Add metadata
            output_data = {
                "_metadata": {
                    "generated_on": datetime.now().isoformat(),
                    "base_url": self.base_url,
                    "total_pages_crawled": len(self.visited_urls),
                    "total_elements": sum(len(elements) for elements in self.locators_data.values()),
                    "categories": list(self.locators_data.keys()),
                    "extraction_tool": "OpenCRX Locator Extractor v1.0"
                }
            }
            
            # Add extracted locators
            output_data.update(dict(self.locators_data))
            
            # Save to file
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Locators saved to {output_path}")
            print(f"\nLocators successfully saved to: {output_path}")
            print(f"Total categories: {len(self.locators_data)}")
            print(f"Total pages crawled: {len(self.visited_urls)}")
            print(f"Total elements extracted: {sum(len(elements) for elements in self.locators_data.values())}")
            
        except Exception as e:
            self.logger.error(f"Error saving locators to JSON: {str(e)}")
            raise
    
    def run_extraction(self, headless: bool = False, max_pages: int = 50) -> bool:
        """Main method to run the complete extraction process."""
        success = False
        
        try:
            self.logger.info("Starting OpenCRX locator extraction...")
            print("Starting OpenCRX locator extraction...")
            
            # Initialize WebDriver
            self.driver = self.setup_webdriver(headless=headless)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("WebDriver initialized successfully")
            
            # Perform login
            if not self.login_to_opencrx():
                raise Exception("Login failed")
            
            print("Login successful")
            
            # Start crawling pages
            print(f"Starting page crawling (max {max_pages} pages)...")
            self.crawl_pages(max_pages=max_pages)
            
            # Save results
            print("Saving locators to JSON file...")
            self.save_locators_json()
            
            success = True
            print("Extraction completed successfully!")
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}")
            print(f"Extraction failed: {str(e)}")
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("WebDriver closed")
                except:
                    pass
        
        return success
    
    def print_summary(self) -> None:
        """Print a summary of the extraction results."""
        if not self.locators_data:
            print("No locators extracted.")
            return
            
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        
        for category, elements in self.locators_data.items():
            print(f"\n{category.upper().replace('_', ' ')}")
            print(f"   Elements: {len(elements)}")
            
            # Show sample elements
            sample_elements = list(elements.keys())[:3]
            for element in sample_elements:
                locator = elements[element]
                print(f"   - {element}: {locator.get('by', 'unknown')}='{locator.get('value', 'unknown')}'")
            
            if len(elements) > 3:
                print(f"   - ... and {len(elements) - 3} more elements")
        
        print(f"\nTotal Elements: {sum(len(elements) for elements in self.locators_data.values())}")
        print(f"Total Categories: {len(self.locators_data)}")
        print(f"Pages Visited: {len(self.visited_urls)}")
        print("="*60)


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract web element locators from OpenCRX application')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum number of pages to crawl (default: 50)')
    parser.add_argument('--output', type=str, default='locators.json', help='Output JSON file name (default: locators.json)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create extractor instance
    extractor = OpenCRXLocatorExtractor()
    
    # Run extraction
    success = extractor.run_extraction(headless=args.headless, max_pages=args.max_pages)
    
    if success:
        extractor.print_summary()
        print(f"\nAll locators saved to {args.output}")
    else:
        print("\nExtraction failed. Check the logs for details.")
        exit(1)


if __name__ == "__main__":
    main()