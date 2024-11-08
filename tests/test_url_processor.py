import pytest
import allure
import os
import time
import sys
from datetime import datetime

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
                raise FileNotFoundError(f"Excel file not found at: {excel_path}")

            # Load the Excel file
            workbook = ExcelHandler.load_workbook(excel_path)
            sheet = ExcelHandler.get_sheet(workbook, sheet_name)

            # Get the data in the expected format
            urls = []
            for row in range(2, sheet.max_row + 1):  # Start from row 2 to skip header
                url = sheet.cell(row=row, column=1).value
                if url:
                    urls.append((url, row))
                else:
                    print(f"Warning: Empty URL found in row {row}")

            if not urls:
                raise ValueError("No valid URLs found in Excel file")

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
        start_time = datetime.now()
        try:
            # Initialize Configuration and backup previous reports
            Configuration.ensure_directories()
            Configuration.backup_previous_reports()
            ExcelHandler.backup_previous_report()

            results = []
            total_urls = len(excel_urls)
            successful = 0
            failed = 0

            print(f"\nStarting URL processing at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total URLs to process: {total_urls}")

            # Process each URL
            for url, row_number in excel_urls:
                with allure.step(f"Processing URL {row_number - 1} of {total_urls}: {url}"):
                    print(f"\nProcessing URL {row_number - 1} of {total_urls}: {url}")

                    # Process URL and get result
                    result = WebAutomation.process_url(url, row_number - 1)
                    results.append(result)

                    # Update counters
                    if result['status'] == 'Success':
                        successful += 1
                    else:
                        failed += 1

                    # Add detailed Allure report
                    status_color = "green" if result['status'] == 'Success' else "red"
                    allure.attach(
                        body=f"""
                        URL: {url}
                        Status: {result['status']}
                        Error: {result['error'] if result['error'] else 'None'}
                        Load Time: {result.get('load_time', 0):.2f}ms
                        """,
                        name=f"URL Test Result {row_number - 1}",
                        attachment_type=allure.attachment_type.TEXT
                    )

                    # Wait between URLs if not the last URL
                    if row_number < total_urls:
                        wait_time = Configuration.get_config()["wait_between_urls"]
                        print(f"Waiting {wait_time} seconds before next URL...")
                        time.sleep(wait_time)

            # Generate summary
            summary = f"""
            Processing Summary:
            Total URLs processed: {len(results)}
            Successfully loaded: {successful}
            Failed to load: {failed}
            Success rate: {(successful / len(results) * 100 if results else 0):.2f}%

            Failed URLs:
            {self._format_failed_urls(results)}
            """
            print("\n" + summary)

            # Generate Excel report
            excel_report_path = ExcelHandler.generate_report(results)
            print(f"\nExcel Report generated: {excel_report_path}")

            # Generate HTML report
            report_path = ReportHandler.generate_html_report(results)
            print(f"\nHTML Report generated: {report_path}")

            # Attach summary to Allure report
            allure.attach(
                body=summary,
                name="Test Summary",
                attachment_type=allure.attachment_type.TEXT
            )

            # Add assertions for test validation
            assert len(results) == total_urls, "All URLs should be processed"

            # Check if any critical errors occurred
            critical_errors = [r for r in results if r['error'] and any(
                critical in r['error'].lower()
                for critical in ['connection refused', 'timeout', 'dns']
            )]

            if critical_errors:
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
            f"- {r['url']}: {r['error']}"
            for r in failed_urls
        )


if __name__ == "__main__":
    pytest.main(["-v", "--alluredir=./allure-results"])
