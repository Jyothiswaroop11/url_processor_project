# URL Validation and Testing Framework

## Overview
A comprehensive Python-based testing framework designed for automated URL validation, screenshot capture, and detailed reporting. The framework provides a robust solution for validating multiple URLs, capturing their status, and generating detailed HTML and Excel reports.

## Features
- **URL Validation**: Automated testing of multiple URLs from an Excel sheet
- **Screenshot Capture**: Automatic screenshot capture of tested URLs
- **Comprehensive Reporting**: 
  - HTML reports with interactive UI
  - Excel report generation
  - Detailed test steps logging
  - Screenshot viewing capability
  - Test data visualization
- **Error Detection**: Smart error detection and classification
- **Filtering & Search**: Dynamic URL filtering and search functionality in reports
- **Statistics Dashboard**: Real-time test statistics and metrics

## Prerequisites
```bash
Python 3.x
Chrome Browser
ChromeDriver (compatible with your Chrome version)
```

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd url-validation-framework
```

2. Install required packages
```bash
pip install -r requirements.txt
```

## Configuration

### config.json
```json
{
    "excel_path": "resources/links.xlsx",
    "chrome_driver_path": "path/to/chromedriver",
    "sheet_name": "Sheet1",
    "page_load_timeout": 60,
    "max_retries": 2,
    "retry_delay": 2,
    "wait_between_urls": 2
}
```

## Project Structure
```
url-validation-framework/
├── utils/
│   ├── __init__.py
│   ├── config_handler.py
│   ├── excel_handler.py
│   ├── report_handler.py
│   ├── url_handler.py
│   └── web_handler.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_url_processor.py
├── resources/
│   └── links.xlsx
├── reports/
│   ├── screenshots/
│   ├── TestReport/
│   ├── Output-Excel/
│   └── Backup/
├── config.json
├── requirements.txt
└── README.md
```

## Usage

1. Prepare your URL list in an Excel file (default: resources/links.xlsx)
2. Update the config.json with appropriate paths
3. Run the tests:
```bash
pytest tests/test_url_processor.py -v --alluredir=./allure-results
```

## Features in Detail

### 1. URL Processing
- Validates URLs from Excel sheet
- Handles various protocols (HTTP/HTTPS)
- Smart error detection and classification
- Configurable timeouts and retries

### 2. Screenshot Capture
- Automatic screenshot capture for each URL
- Error state capture
- Base64 encoding for HTML report integration

### 3. Reporting System

#### HTML Report
- Interactive UI with filtering capabilities
- Real-time statistics
- Screenshot viewer
- Detailed test steps
- Error details and logs
- Test data viewer

#### Excel Report
- Comprehensive test results
- Status summary
- Timing information
- Error details

### 4. Error Handling
- Connection errors
- DNS resolution failures
- Timeout handling
- SSL/TLS errors
- HTTP error codes

## Recent Updates

### Version 1.1.0
- Fixed screenshot display issue in HTML reports
- Enhanced test step logging
- Improved error handling and reporting
- Added base64 encoding optimization
- Updated CSS styling for better UI
- Fixed screenshot toggle functionality

### Version 1.0.0
- Initial release with basic functionality
- URL validation
- Screenshot capture
- Report generation

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing
Run the test suite:
```bash
pytest -v
```

Generate Allure reports:
```bash
allure serve allure-results
```

## Acknowledgments
- Selenium WebDriver
- pytest
- Allure Reports
- Font Awesome
- Inter Font Family
