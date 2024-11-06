from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    def verify_page_content(driver):
        """
        Verifies if the page has loaded with actual content.
        Returns tuple of (bool, str) indicating success/failure and details.
        """
        try:
            # Check if body exists and has content
            body = driver.find_element(By.TAG_NAME, "body")
            if not body.text.strip():
                return False, "Page body is empty"

            # Check for common error indicators
            error_texts = [
                "404 not found",
                "page not found",
                "404 error",
                "403 forbidden",
                "access denied",
                "500 internal server error",
                "503 service unavailable",
                "502 bad gateway",
                "this page isn't working",
                "unable to connect",
                "connection refused",
                "err_connection_refused"
            ]

            page_text = body.text.lower()
            for error in error_texts:
                if error in page_text:
                    return False, f"Error detected: {error}"

            # Check if page has main content areas
            content_indicators = [
                "//main",
                "//article",
                "//div[contains(@class, 'content')]",
                "//div[contains(@class, 'main')]",
                "//div[contains(@id, 'content')]",
                "//div[contains(@id, 'main')]"
            ]

            content_found = False
            for xpath in content_indicators:
                try:
                    content = driver.find_elements(By.XPATH, xpath)
                    if content and any(elem.is_displayed() and elem.text.strip() for elem in content):
                        content_found = True
                        break
                except:
                    continue

            if not content_found:
                return False, "No main content areas found"

            # Check for minimal interactive elements (links, buttons, forms)
            interactive_elements = driver.find_elements(By.CSS_SELECTOR, 'a, button, input, form')
            if not any(elem.is_displayed() for elem in interactive_elements):
                return False, "No interactive elements found"

            return True, "Page content verified successfully"

        except Exception as e:
            return False, f"Error verifying content: {str(e)}"

    @staticmethod
    def check_page_loaded(driver, timeout=30):
        """Checks if page is completely loaded and has valid content"""
        try:
            print(f"Waiting for page to load (timeout: {timeout}s)...")

            # Wait for document ready state
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait for dynamic content
            time.sleep(2)

            # Verify page content
            content_valid, details = WebAutomation.verify_page_content(driver)

            if content_valid:
                print("Page loaded successfully with valid content")
                return True, "Page loaded successfully"
            else:
                print(f"Page load issue: {details}")
                return False, details

        except TimeoutException:
            return False, "Page load timeout"
        except Exception as e:
            error_msg = f"Error during page load: {str(e)}"
            print(error_msg)
            return False, error_msg

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

            max_retries = Configuration.get_config()["max_retries"]
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

            # Check page load and content
            is_loaded, load_details = WebAutomation.check_page_loaded(driver)
            end_time = time.time()
            load_time = (end_time - start_time) * 1000  # Convert to milliseconds

            if is_loaded:
                result['steps'].append({
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f"Page loaded successfully in {load_time:.2f}ms"
                })

                # Take screenshot
                screenshot_path = WebAutomation.save_screenshot(driver, url, row_number)
                if screenshot_path:
                    result.update({
                        'status': 'Success',
                        'load_time': load_time,
                        'screenshot': screenshot_path
                    })
                    result['steps'].append({
                        'status': 'SUCCESS',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': "Screenshot captured successfully"
                    })
            else:
                result['steps'].append({
                    'status': 'FAIL',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f"Page load issue: {load_details}"
                })
                result['error'] = load_details

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