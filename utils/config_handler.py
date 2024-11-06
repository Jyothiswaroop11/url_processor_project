import os
import json
import shutil
import allure
from datetime import datetime


class Configuration:
    @staticmethod
    def load_config():
        """Load configuration from config.json"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config.json'
        )
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
            return {}

    @staticmethod
    def get_config():
        """Get combined configuration with defaults"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load custom config
        custom_config = Configuration.load_config()

        # Default config
        default_config = {
            "excel_path": os.path.join(project_root, "resources", "links.xlsx"),
            "screenshots_dir": os.path.join(project_root, "reports", "screenshots"),
            "reports_dir": os.path.join(project_root, "reports", "allure-results"),
            "extent_report_dir": os.path.join(project_root, "reports", "ExtentReport"),
            "backup_dir": os.path.join(project_root, "reports", "backup"),
            "logs_dir": os.path.join(project_root, "logs"),
            "chrome_driver_path": custom_config.get("chrome_driver_path", ""),
            "sheet_name": "Sheet1",
            "page_load_timeout": 60,
            "max_retries": 2,
            "retry_delay": 2,
            "wait_between_urls": 2
        }

        # Update default config with custom config
        default_config.update(custom_config)
        return default_config

    @staticmethod
    def get_path(path_name):
        """Get specific path from configuration"""
        paths = {
            "excel": Configuration.get_config()["excel_path"],
            "screenshots": Configuration.get_config()["screenshots_dir"],
            "reports": Configuration.get_config()["reports_dir"],
            "extent_report": Configuration.get_config()["extent_report_dir"],
            "backup": Configuration.get_config()["backup_dir"],
            "logs": Configuration.get_config()["logs_dir"],
            "chrome_driver": Configuration.get_config()["chrome_driver_path"]
        }
        return paths.get(path_name)

    @staticmethod
    @allure.step("Ensuring directories exist")
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        directories = [
            Configuration.get_path("screenshots"),
            Configuration.get_path("reports"),
            Configuration.get_path("extent_report"),
            Configuration.get_path("backup"),
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

    @staticmethod
    def backup_previous_reports():
        """Backup previous reports to timestamped directory"""
        try:
            extent_report_dir = Configuration.get_path("extent_report")
            backup_dir = Configuration.get_path("backup")

            # Check if there are any files to backup
            if not os.path.exists(extent_report_dir) or not os.listdir(extent_report_dir):
                return

            # Create timestamp for backup folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(backup_dir, f"Backup_Report_{timestamp}")

            # Create backup folder if it doesn't exist
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            # Move all files from extent report directory to backup folder
            for item in os.listdir(extent_report_dir):
                item_path = os.path.join(extent_report_dir, item)
                if os.path.isfile(item_path):
                    shutil.move(item_path, os.path.join(backup_folder, item))

            print(f"Previous reports backed up to: {backup_folder}")

        except Exception as e:
            print(f"Error during backup: {str(e)}")
            allure.attach(
                body=f"Error during backup: {str(e)}",
                name="Backup Error",
                attachment_type=allure.attachment_type.TEXT
            )