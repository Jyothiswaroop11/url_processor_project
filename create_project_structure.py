import os

def create_project_structure():
    # Project root directory
    project_root = "url_processor_project"

    # Directory structure with files
    structure = {
        "tests": ["__init__.py", "test_url_processor.py", "conftest.py"],
        "utils": ["__init__.py", "web_handler.py", "config_handler.py", "excel_handler.py",
                  "report_handler.py", "url_handler.py"],
        "resources": [],
        "reports": ["screenshots", "allure-results", "ExtentReport", "backup"],
        "logs": []
    }

    # Root level files
    root_files = ["config.json", "requirements.txt", "setup.py", "pytest.ini"]

    try:
        # Create root directory
        os.makedirs(project_root, exist_ok=True)

        # Create directories and files
        for directory, files in structure.items():
            dir_path = os.path.join(project_root, directory)
            os.makedirs(dir_path, exist_ok=True)

            # Create files in directory
            for file in files:
                # If it's a directory within reports
                if directory == "reports" and file in ["screenshots", "allure-results", "ExtentReport", "backup"]:
                    os.makedirs(os.path.join(dir_path, file), exist_ok=True)
                else:
                    file_path = os.path.join(dir_path, file)
                    if not os.path.exists(file_path):
                        with open(file_path, 'w') as f:
                            pass

        # Create root level files
        for file in root_files:
            file_path = os.path.join(project_root, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass

        print("Project structure created successfully!")

    except Exception as e:
        print(f"Error creating project structure: {str(e)}")


if __name__ == "__main__":
    create_project_structure()