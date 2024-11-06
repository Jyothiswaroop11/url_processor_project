# utils/config_handler.py
import os
import json
import shutil
import allure
from datetime import datetime


class Configuration:
    @staticmethod
    def load_config():
        """Load configuration from config.json"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
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

        # Convert relative paths to absolute paths
        if 'excel_path' in custom_config and not os.path.isabs(custom_config['excel_path']):
            custom_config['excel_path'] = os.path.join(project_root, custom_config['excel_path'])

        # Default config with absolute paths
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
        config = Configuration.get_config()
        paths = {
            "excel": config["excel_path"],
            "screenshots": config["screenshots_dir"],
            "reports": config["reports_dir"],
            "extent_report": config["extent_report_dir"],
            "backup": config["backup_dir"],
            "logs": config["logs_dir"],
            "chrome_driver": config["chrome_driver_path"]
        }
        path = paths.get(path_name)
        return os.path.abspath(path) if path else None

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
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
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

            if not extent_report_dir or not os.path.exists(extent_report_dir):
                return

            if not os.listdir(extent_report_dir):
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(backup_dir, f"Backup_Report_{timestamp}")

            os.makedirs(backup_folder, exist_ok=True)

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