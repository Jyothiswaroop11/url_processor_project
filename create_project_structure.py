# create_project.py
import os
import pandas as pd


def create_project_structure():
    # Project root directory
    project_root = os.getcwd()  # Use current directory as project root

    # Directory structure
    directories = [
        'tests',
        'utils',
        'resources',
        'reports/screenshots',
        'reports/allure-results',
        'reports/ExtentReport',
        'reports/backup',
        'logs'
    ]

    # Create directories
    for directory in directories:
        dir_path = os.path.join(project_root, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

    # Create sample Excel file with URLs
    urls_data = {
        'URL': [
            'google.com',
            'github.com',
            'python.org',
            'stackoverflow.com'
        ]
    }
    df = pd.DataFrame(urls_data)
    excel_path = os.path.join(project_root, 'resources', 'links.xlsx')
    df.to_excel(excel_path, index=False, sheet_name='Sheet1')
    print(f"Created Excel file: {excel_path}")

    # Create config.json
    config_content = {
        "excel_path": excel_path,
        "chrome_driver_path": "C:\\Users\\Jyothiswaroop\\OneDrive\\Desktop\\chromedriver-win32\\chromedriver.exe",  # Update this with your chromedriver path
        "sheet_name": "Sheet1",
        "page_load_timeout": 60,
        "max_retries": 2,
        "retry_delay": 2,
        "wait_between_urls": 2
    }

    import json
    config_path = os.path.join(project_root, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config_content, f, indent=4)
    print(f"Created config file: {config_path}")


if __name__ == "__main__":
    create_project_structure()