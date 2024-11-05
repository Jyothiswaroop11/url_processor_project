import pytest
import allure
import os
import time
from utils.config_handler import Configuration
from utils.excel_handler import ExcelHandler
from utils.url_handler import URLHandler
from utils.web_handler import WebAutomation
from utils.report_handler import ReportHandler


@allure.epic("URL Processing")
@allure.feature("URL Validation and Screenshot Capture")
class TestURLProcessor:

    @allure.story("Process URLs from Excel")
    @allure.description("Test processing URLs from Excel file and capturing screenshots")
    def test_process_urls(self):
        try:
            config = Configuration.get_config()
            excel_path = config["excel_path"]
            sheet_name = config["sheet_name"]

            Configuration.ensure_directories()
            rows = ExcelHandler.get_row_count(excel_path, sheet_name)
            assert rows > 1, "No data found in Excel file"

            results = []
            total_urls = rows - 1
            print(f"\nTotal URLs to process: {total_urls}")

            # Process each URL
            for r in range(2, rows + 1):
                url = ExcelHandler.read_data(excel_path, sheet_name, r, 1)
                if not url:
                    print(f"Empty URL found in row {r}, skipping...")
                    continue

                current_url_number = r - 1  # Calculate the current URL number
                print(f"\nProcessing URL {current_url_number} of {total_urls}")
                with allure.step(f"Processing URL {current_url_number} of {total_urls}"):
                    # Pass current_url_number instead of r
                    result = WebAutomation.process_url(url, current_url_number)
                    results.append(result)

                # Wait between URLs
                if r < rows:
                    print("Waiting before next URL...")
                    time.sleep(2)

            # Generate summary
            successful = sum(1 for r in results if r['status'] == 'Success')
            failed = len(results) - successful

            summary = f"""
            Processing Summary:
            Total URLs processed: {len(results)}
            Successfully loaded: {successful}
            Failed to load: {failed}
            Success rate: {(successful / len(results) * 100 if results else 0):.2f}%
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

        except Exception as e:
            error_msg = f"Error in test execution: {str(e)}"
            print(f"\nError: {error_msg}")
            allure.attach(
                body=error_msg,
                name="Test Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise