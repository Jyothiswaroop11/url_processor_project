# utils/web_handler.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
from time import time, sleep
import os
from datetime import datetime
from .config_handler import Configuration
from .url_handler import URLHandler


class WebDriverSetup:
    @staticmethod
    def create_driver():
        """Creates a new instance of Chrome driver"""
        try:
            chrome_options = Options()
            # Basic Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--start-maximized")

            # Additional stability options
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")

            # Get Chrome driver path from configuration
            chrome_driver_path = Configuration.get_path("chrome_driver")

            if not os.path.exists(chrome_driver_path):
                raise FileNotFoundError(f"Chrome driver not found at: {chrome_driver_path}")

            print(f"Using Chrome driver from: {chrome_driver_path}")

            service = Service(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(Configuration.get_config()["page_load_timeout"])

            print("Chrome WebDriver initialized successfully")
            return driver

        except Exception as e:
            error_msg = f"Error creating Chrome WebDriver: {str(e)}"
            print(error_msg)
            allure.attach(
                body=error_msg,
                name="Driver Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


class WebAutomation:
    @staticmethod
    def check_page_loaded(driver, timeout=30):
        """Checks if page is completely loaded"""
        try:
            print(f"Waiting for page to load (timeout: {timeout}s)...")
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            sleep(2)
            print("Page load complete")
            return True
        except Exception as e:
            print(f"Error during page load: {str(e)}")
            allure.attach(
                body=f"Error checking page load: {str(e)}",
                name="Page Load Error",
                attachment_type=allure.attachment_type.TEXT
            )
            return False

    @staticmethod
    def check_page_errors(driver):
        """Check for common error patterns on the page"""
        error_patterns = {
            '404': ['404', 'page not found', 'not found', '404 error'],
            '403': ['403', 'forbidden', 'access denied', '403 error'],
            '500': ['500', 'internal server error', 'server error', '500 error'],
            '502': ['502', 'bad gateway', '502 error'],
            '503': ['503', 'service unavailable', '503 error'],
            '504': ['504', 'gateway timeout', '504 error']
        }

        error_mappings = {
            'ERR_NAME_NOT_RESOLVED': 'DNS resolution failed - Unable to resolve domain name',
            'ERR_CONNECTION_REFUSED': 'Connection refused by the server',
            'ERR_CONNECTION_TIMED_OUT': 'Connection timed out',
            'ERR_NETWORK_UNREACHABLE': 'Network is unreachable',
            'ERR_CONNECTION_RESET': 'Connection was reset',
            'ERR_SSL_PROTOCOL_ERROR': 'SSL/TLS protocol error',
            'ERR_CERT_AUTHORITY_INVALID': 'Invalid SSL certificate',
            'ERR_BAD_SSL_CLIENT_AUTH_CERT': 'Invalid client SSL certificate',
            'ERR_TUNNEL_CONNECTION_FAILED': 'Failed to establish tunnel connection',
            'ERR_NO_SUPPORTED_PROXIES': 'No supported proxies',
            'ERR_EMPTY_RESPONSE': 'Server returned empty response',
            'ERR_RESPONSE_HEADERS_TRUNCATED': 'Response headers truncated',
            'ERR_CONTENT_DECODING_FAILED': 'Content decoding failed'
        }

        try:
            # Check for Chrome error codes in page source
            page_source = driver.page_source.lower()
            for error_key, error_message in error_mappings.items():
                if error_key.lower() in page_source:
                    return error_message

            # Get page title and body text
            page_title = driver.title.lower()
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

            # Check response code from browser
            navigation_entry = driver.execute_script("return window.performance.getEntriesByType('navigation')[0];")
            if navigation_entry:
                response_status = navigation_entry.get('responseStatus')
                if response_status and response_status >= 400:
                    return f"HTTP {response_status} Error"

            # Check for error patterns in content
            for error_code, patterns in error_patterns.items():
                for pattern in patterns:
                    if pattern in page_title or pattern in body_text:
                        return f"HTTP {error_code} Error detected in page content"

            return None

        except Exception as e:
            error_str = str(e).lower()
            # Check for Selenium/Chrome specific errors
            for error_key, error_message in error_mappings.items():
                if error_key.lower() in error_str:
                    return error_message
            return f"Error checking page content: {str(e)}"

    @classmethod
    def save_screenshot(cls, driver, url, row_number):
        """Takes and saves screenshot with URL name"""
        try:
            url_name = URLHandler.get_clean_filename(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{url_name}_{timestamp}.png"

            screenshots_dir = Configuration.get_path("screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            filepath = os.path.join(screenshots_dir, filename)

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Add a small delay before taking screenshot
                    sleep(1)  # Using imported sleep instead of time.sleep
                    driver.save_screenshot(filepath)
                    print(f"Screenshot saved: {filepath}")

                    # Attach to Allure report
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        name=f"Screenshot_{url_name}",
                        attachment_type=allure.attachment_type.PNG
                    )

                    return filepath
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Screenshot attempt {attempt + 1} failed, retrying...")
                    sleep(1)  # Using imported sleep instead of time.sleep

        except Exception as e:
            print(f"Error saving screenshot: {str(e)}")
            allure.attach(
                body=f"Error saving screenshot: {str(e)}",
                name="Screenshot Error",
                attachment_type=allure.attachment_type.TEXT
            )
            return None

    @classmethod
    def process_url(cls, url, row_number):
        driver = None
        start_time = time()
        result = {
            'url': url,
            'status': 'Failed',
            'load_time': 0,
            'screenshot': None,
            'error': None,
            'start_time': start_time,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'steps': []
        }

        try:
            print(f"\nProcessing URL: {url}")
            result['steps'].append({
                'status': 'INFO',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Starting to process URL: {url}"
            })

            driver = WebDriverSetup.create_driver()

            # Navigate to URL
            formatted_url = URLHandler.format_url(url)
            print(f"Navigating to: {formatted_url}")
            driver.get(formatted_url)

            # Always try to take a screenshot, regardless of page load status
            screenshot_path = cls.save_screenshot(driver, url, row_number)
            if screenshot_path:
                result['screenshot'] = screenshot_path
                result['steps'].append({
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': "Screenshot captured successfully"
                })

            # Continue with page load check and other processing
            if cls.check_page_loaded(driver):
                error = cls.check_page_errors(driver)
                if error:
                    result['error'] = error
                    result['steps'].append({
                        'status': 'FAIL',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Page loaded but encountered error: {error}"
                    })
                else:
                    result['status'] = 'Success'
                    end_time = time()
                    result['load_time'] = (end_time - start_time) * 1000
                    result['steps'].append({
                        'status': 'SUCCESS',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Page loaded successfully in {result['load_time']:.2f}ms"
                    })
            else:
                result['error'] = "Page load timeout"
                result['steps'].append({
                    'status': 'FAIL',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': "Page failed to load completely"
                })

        except Exception as e:
            error_msg = str(e)
            print(f"Error processing URL: {error_msg}")
            result['error'] = error_msg
            result['steps'].append({
                'status': 'FATAL',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Error: {error_msg}"
            })

            # Try to take screenshot even if there was an error
            if driver:
                try:
                    screenshot_path = cls.save_screenshot(driver, url, row_number)
                    if screenshot_path:
                        result['screenshot'] = screenshot_path
                        result['steps'].append({
                            'status': 'SUCCESS',
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'message': "Screenshot captured after error"
                        })
                except Exception as screenshot_error:
                    print(f"Failed to capture error screenshot: {str(screenshot_error)}")

        finally:
            # Always set end time and calculate load time
            result['end_time'] = time()
            if not result.get('load_time'):
                result['load_time'] = (result['end_time'] - result['start_time']) * 1000

            if driver:
                try:
                    driver.quit()
                    result['steps'].append({
                        'status': 'INFO',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': "Browser closed successfully"
                    })
                except Exception as e:
                    result['steps'].append({
                        'status': 'FAIL',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Error closing browser: {str(e)}"
                    })

        return result
