# utils/web_handler.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import time
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
            time.sleep(2)
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

        try:
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

            # Additional checks for common error indicators
            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'error')]")
            for element in error_elements:
                element_text = element.text.lower()
                if any(err in element_text for err in ['404', '403', '500', 'not found', 'forbidden']):
                    return f"Error message found: {element.text}"

            return None

        except Exception as e:
            return f"Error checking page content: {str(e)}"

    @staticmethod
    def save_screenshot(driver, url, row_number):
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
                    driver.save_screenshot(filepath)
                    print(f"Screenshot saved: {filepath}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Screenshot attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)

            allure.attach(
                body=driver.get_screenshot_as_png(),
                name=f"Screenshot_{url_name}",
                attachment_type=allure.attachment_type.PNG
            )

            return filepath
        except Exception as e:
            print(f"Error saving screenshot: {str(e)}")
            allure.attach(
                body=f"Error saving screenshot: {str(e)}",
                name="Screenshot Error",
                attachment_type=allure.attachment_type.TEXT
            )
            return None

    @staticmethod
    def process_url(url, row_number):
        """Process a single URL with new browser instance"""
        driver = None
        start_time = time.time()
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

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver = WebDriverSetup.create_driver()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Driver creation attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)

            result['steps'].append({
                'status': 'SUCCESS',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': "Chrome WebDriver initialized successfully"
            })

            # Navigate to URL
            formatted_url = URLHandler.format_url(url)
            print(f"Navigating to: {formatted_url}")
            driver.get(formatted_url)

            # Wait for page load
            if WebAutomation.check_page_loaded(driver):
                # Check for errors on the page
                error = WebAutomation.check_page_errors(driver)
                if error:
                    result['steps'].append({
                        'status': 'FAIL',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Page loaded but encountered error: {error}"
                    })
                    result['error'] = error
                else:
                    end_time = time.time()
                    load_time = (end_time - start_time) * 1000
                    result.update({
                        'status': 'Success',
                        'load_time': load_time
                    })
                    result['steps'].append({
                        'status': 'SUCCESS',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Page loaded successfully in {load_time:.2f}ms"
                    })

                # Take screenshot regardless of error status
                screenshot_path = WebAutomation.save_screenshot(driver, url, row_number)
                if screenshot_path:
                    result['screenshot'] = screenshot_path
                    result['steps'].append({
                        'status': 'SUCCESS',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': "Screenshot captured successfully"
                    })
            else:
                result['steps'].append({
                    'status': 'FAIL',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': "Page failed to load completely"
                })
                result['error'] = "Page load timeout"

        except Exception as e:
            error_msg = str(e)
            print(f"Error processing URL: {error_msg}")
            result['steps'].append({
                'status': 'FATAL',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Error: {error_msg}"
            })
            result['error'] = error_msg

        finally:
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