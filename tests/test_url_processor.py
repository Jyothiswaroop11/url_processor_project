# tests/test_url_processor.py
import pytest
import allure
import os
import time
from datetime import datetime
import sys
from time import time as current_time

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.config_handler import Configuration
from utils.excel_handler import ExcelHandler
from utils.url_handler import URLHandler
from utils.web_handler import WebAutomation
from utils.report_handler import ReportHandler


@allure.epic("URL Processing")
@allure.feature("URL Validation and Error Detection")
class TestURLProcessor:

    @pytest.fixture(scope="class")
    def excel_urls(self):
        """Fixture to read URLs from Excel file"""
        try:
            config = Configuration.get_config()
            excel_path = config["excel_path"]
            sheet_name = config["sheet_name"]

            if not os.path.exists(excel_path):
                error_msg = f"Excel file not found at: {excel_path}"
                allure.attach(body=error_msg, name="Missing File Error", attachment_type=allure.attachment_type.TEXT)
                raise FileNotFoundError(error_msg)

            rows = ExcelHandler.get_row_count(excel_path, sheet_name)
            if rows < 2:  # Accounting for header row
                error_msg = "Excel file is empty or contains only headers"
                allure.attach(body=error_msg, name="Empty File Error", attachment_type=allure.attachment_type.TEXT)
                raise ValueError(error_msg)

            urls = []
            # Start from row 2 to skip header
            for row in range(2, rows + 1):
                url = ExcelHandler.read_data(excel_path, sheet_name, row, 1)
                if url:
                    urls.append((url.strip(), row))
                else:
                    print(f"Warning: Empty URL found in row {row}")
                    allure.attach(
                        body=f"Empty URL in row {row}",
                        name="Warning",
                        attachment_type=allure.attachment_type.TEXT
                    )

            if not urls:
                error_msg = "No valid URLs found in Excel file"
                allure.attach(body=error_msg, name="No URLs Error", attachment_type=allure.attachment_type.TEXT)
                raise ValueError(error_msg)

            return urls

        except Exception as e:
            error_msg = f"Error reading Excel file: {str(e)}"
            print(f"\nError: {error_msg}")
            allure.attach(
                body=error_msg,
                name="Excel Reading Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

    @allure.story("Process URLs from Excel with Error Detection")
    def test_process_excel_urls(self, excel_urls):
        """Test processing URLs from Excel file with error detection"""
        test_start_time = datetime.now()
        execution_start_time = current_time()

        try:
            # Initialize Configuration and backup previous reports
            Configuration.ensure_directories()
            Configuration.backup_previous_reports()
            ExcelHandler.backup_previous_report()

            results = []
            total_urls = len(excel_urls)
            successful = 0
            failed = 0

            print(f"\nStarting URL processing at: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total URLs to process: {total_urls}")

            # Process each URL
            for url, row_number in excel_urls:
                url_start_time = current_time()
                with allure.step(f"Processing URL {row_number - 1} of {total_urls}: {url}"):
                    print(f"\nProcessing URL {row_number - 1} of {total_urls}: {url}")

                    try:
                        # Process URL and get result
                        result = WebAutomation.process_url(url, row_number - 1)

                        # Calculate processing time if not set
                        if not result.get('load_time'):
                            url_end_time = current_time()
                            result['load_time'] = (url_end_time - url_start_time) * 1000

                        results.append(result)

                        # Update counters
                        if result['status'] == 'Success':
                            successful += 1
                        else:
                            failed += 1

                        # Add detailed Allure report
                        allure.attach(
                            body=f"""
                            URL: {url}
                            Status: {result['status']}
                            Error: {result.get('error', 'None')}
                            Load Time: {result.get('load_time', 0):.2f}ms
                            Screenshot: {'Captured' if result.get('screenshot') else 'Failed'}
                            """,
                            name=f"URL Test Result {row_number - 1}",
                            attachment_type=allure.attachment_type.TEXT
                        )

                        # Attach screenshot to Allure if available
                        if result.get('screenshot') and os.path.exists(result['screenshot']):
                            with open(result['screenshot'], 'rb') as screenshot:
                                allure.attach(
                                    screenshot.read(),
                                    name=f"Screenshot_{row_number - 1}",
                                    attachment_type=allure.attachment_type.PNG
                                )

                    except Exception as e:
                        error_msg = f"Error processing URL {url}: {str(e)}"
                        print(error_msg)
                        allure.attach(
                            body=error_msg,
                            name=f"URL Processing Error {row_number - 1}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        # Add failed result
                        results.append({
                            'url': url,
                            'status': 'Failed',
                            'error': str(e),
                            'load_time': (current_time() - url_start_time) * 1000,
                            'start_time': url_start_time,
                            'end_time': current_time()
                        })
                        failed += 1

                    # Wait between URLs if not the last URL
                    if row_number < total_urls:
                        wait_time = Configuration.get_config()["wait_between_urls"]
                        print(f"Waiting {wait_time} seconds before next URL...")
                        time.sleep(wait_time)

            # Calculate total execution time
            execution_time = (current_time() - execution_start_time) * 1000

            # Generate summary
            summary = f"""
            Test Execution Summary:
            Start Time: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}
            Total Execution Time: {execution_time:.2f}ms
            Total URLs processed: {len(results)}
            Successfully loaded: {successful}
            Failed to load: {failed}
            Success rate: {(successful / len(results) * 100 if results else 0):.2f}%

            Failed URLs:
            {self._format_failed_urls(results)}
            """
            print("\n" + summary)

            # Generate reports
            try:
                excel_report_path = ExcelHandler.generate_report(results)
                print(f"\nExcel Report generated: {excel_report_path}")
            except Exception as e:
                print(f"Error generating Excel report: {str(e)}")

            try:
                report_path = ReportHandler.generate_html_report(results)
                print(f"\nHTML Report generated: {report_path}")
            except Exception as e:
                print(f"Error generating HTML report: {str(e)}")

            # Attach summary to Allure report
            allure.attach(
                body=summary,
                name="Test Summary",
                attachment_type=allure.attachment_type.TEXT
            )

            # Add assertions for test validation
            assert len(results) == total_urls, "All URLs should be processed"

            # Check for truly critical errors (excluding DNS and common network issues)
            critical_errors = [r for r in results if r.get('error') and any(
                critical in str(r['error']).lower()
                for critical in [
                    'connection refused',
                    'internal server error',
                    'fatal error',
                    'chrome crashed',
                    'session not created'
                ]
            )]

            # Log DNS and network-related issues separately
            network_errors = [r for r in results if r.get('error') and any(
                network_error in str(r['error']).lower()
                for network_error in [
                    'err_name_not_resolved',
                    'dns',
                    'timeout',
                    'net::err_',
                    'network unreachable'
                ]
            )]

            if network_errors:
                network_summary = "\n".join(
                    f"- {r['url']}: {r['error']}"
                    for r in network_errors
                )
                allure.attach(
                    body=f"Network/DNS Issues Found:\n{network_summary}",
                    name="Network Issues",
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"\nNetwork/DNS issues encountered in {len(network_errors)} URLs")

            if critical_errors:
                critical_summary = "\n".join(
                    f"- {r['url']}: {r['error']}"
                    for r in critical_errors
                )
                allure.attach(
                    body=f"Critical Errors Found:\n{critical_summary}",
                    name="Critical Errors",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.fail(f"Critical errors encountered in {len(critical_errors)} URLs")

        except Exception as e:
            error_msg = f"Error in test execution: {str(e)}"
            print(f"\nError: {error_msg}")
            allure.attach(
                body=error_msg,
                name="Test Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

    def _format_failed_urls(self, results):
        """Format failed URLs for summary report"""
        failed_urls = [r for r in results if r['status'] == 'Failed']
        if not failed_urls:
            return "None"

        return "\n".join(
            f"- {r['url']}: {r.get('error', 'Unknown error')}"
            for r in failed_urls
        )


if __name__ == "__main__":
    pytest.main(["-v", "--alluredir=./allure-results"])
