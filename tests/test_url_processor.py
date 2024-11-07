# tests/test_url_processor.py
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
        config = Configuration.get_config()
        excel_path = config["excel_path"]
        sheet_name = config["sheet_name"]

        rows = ExcelHandler.get_row_count(excel_path, sheet_name)
        urls = []

        # Start from row 2 to skip header
        for row in range(2, rows + 1):
            url = ExcelHandler.read_data(excel_path, sheet_name, row, 1)
            if url:
                urls.append((url, row))

        return urls

    @allure.story("Process URLs from Excel with Error Detection")
    def test_process_excel_urls(self, excel_urls):
        """Test processing URLs from Excel file with error detection"""
        try:
            # Initialize Configuration and backup previous reports
            Configuration.ensure_directories()
            Configuration.backup_previous_reports()

            results = []
            total_urls = len(excel_urls)
            print(f"\nTotal URLs to process: {total_urls}")

            # Process each URL
            for url, row_number in excel_urls:
                with allure.step(f"Processing URL {row_number - 1} of {total_urls}: {url}"):
                    print(f"\nProcessing URL {row_number - 1} of {total_urls}: {url}")

                    result = WebAutomation.process_url(url, row_number - 1)
                    results.append(result)

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

                    # Wait between URLs
                    if row_number < total_urls:
                        wait_time = Configuration.get_config()["wait_between_urls"]
                        print(f"Waiting {wait_time} seconds before next URL...")
                        time.sleep(wait_time)

            # Generate summary
            successful = sum(1 for r in results if r['status'] == 'Success')
            failed = len(results) - successful

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