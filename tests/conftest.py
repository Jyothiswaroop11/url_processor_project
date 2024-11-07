# tests/conftest.py
import pytest
import allure
from datetime import datetime
import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

@pytest.fixture(scope="session", autouse=True)
def setup_teardown():
    """Setup and teardown for the entire test session."""
    allure.attach(
        body="Test session started",
        name="Session Start",
        attachment_type=allure.attachment_type.TEXT
    )
    yield
    allure.attach(
        body="Test session ended",
        name="Session End",
        attachment_type=allure.attachment_type.TEXT
    )

@pytest.fixture(scope="function", autouse=True)
def test_case_setup(request):
    """Setup and teardown for each test case."""
    test_name = request.node.name
    allure.attach(
        body=f"Starting test: {test_name}",
        name="Test Start",
        attachment_type=allure.attachment_type.TEXT
    )

    start_time = datetime.now()
    yield
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    allure.attach(
        body=f"Test duration: {duration:.2f} seconds",
        name="Test Duration",
        attachment_type=allure.attachment_type.TEXT
    )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if report.failed:
            allure.attach(
                body=str(report.longrepr),
                name="Error Details",
                attachment_type=allure.attachment_type.TEXT
            )