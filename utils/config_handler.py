import os
import allure


class Configuration:
    @staticmethod
    def get_config():
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return {
            "excel_path": os.path.join(project_root, "resources", "links.xlsx"),
            "screenshots_dir": os.path.join(project_root, "reports", "screenshots"),
            "reports_dir": os.path.join(project_root, "reports", "allure-results"),
            "logs_dir": os.path.join(project_root, "logs"),
            "sheet_name": "Sheet1",
            "page_load_timeout": 60,
            "max_retries": 2,
            "retry_delay": 2,
            "wait_between_urls": 2
        }

    @staticmethod
    def get_path(path_name):
        paths = {
            "excel": Configuration.get_config()["excel_path"],
            "screenshots": Configuration.get_config()["screenshots_dir"],
            "reports": Configuration.get_config()["reports_dir"],
            "logs": Configuration.get_config()["logs_dir"]
        }
        return paths.get(path_name)

    @staticmethod
    @allure.step("Ensuring directories exist")
    def ensure_directories():
        directories = [
            Configuration.get_path("screenshots"),
            Configuration.get_path("reports"),
            Configuration.get_path("logs")
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                allure.attach(
                    body=f"Created directory: {directory}",
                    name="Directory Creation",
                    attachment_type=allure.attachment_type.TEXT
                )