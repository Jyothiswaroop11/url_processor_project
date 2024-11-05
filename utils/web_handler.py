from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--start-maximized")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            allure.attach(
                body=f"Error creating Chrome WebDriver: {str(e)}",
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

            # Wait for document.readyState to be complete
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait for dynamic content
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
    def save_screenshot(driver, url, row_number):
        """Takes and saves screenshot with URL name"""
        try:
            # Extract clean filename from URL
            url_name = URLHandler.get_clean_filename(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{url_name}_{timestamp}.png"

            # Ensure screenshots directory exists
            screenshots_dir = Configuration.get_path("screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            filepath = os.path.join(screenshots_dir, filename)
            driver.save_screenshot(filepath)

            print(f"Screenshot saved: {filepath}")

            # Attach screenshot to Allure report
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
            # Initial step
            result['steps'].append({
                'status': 'SUCCESS',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Report will Run on Chrome Browser"
            })

            # Create new driver instance
            driver = WebDriverSetup.create_driver()
            result['steps'].append({
                'status': 'SUCCESS',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Starting to process URL: {url}"
            })

            # Navigate to URL
            formatted_url = URLHandler.format_url(url)
            driver.get(formatted_url)

            # Wait for page load
            if WebAutomation.check_page_loaded(driver):
                end_time = time.time()
                load_time = (end_time - start_time) * 1000

                result['steps'].append({
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f"Page load completed in {load_time:.2f}ms"
                })

                # Take screenshot
                screenshot_path = WebAutomation.save_screenshot(driver, url, row_number)
                if screenshot_path:
                    result['steps'].append({
                        'status': 'INFO',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': "Screenshot captured:",
                        'screenshot': screenshot_path
                    })

                result.update({
                    'status': 'Success',
                    'load_time': load_time,
                    'screenshot': screenshot_path
                })

            else:
                result['steps'].append({
                    'status': 'FAIL',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': "Page failed to load completely"
                })
                result['error'] = "Page load timeout"

        except Exception as e:
            result['steps'].append({
                'status': 'FATAL',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Error: {str(e)}"
            })
            result['error'] = str(e)

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    result['steps'].append({
                        'status': 'FAIL',
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': f"Error closing browser: {str(e)}"
                    })

        return result