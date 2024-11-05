from setuptools import setup, find_packages

setup(
    name="url_processor_project",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'selenium>=4.16.0',
        'webdriver-manager>=4.0.1',
        'pytest>=7.4.3',
        'allure-pytest>=2.13.2',
        'openpyxl>=3.1.2',
    ],
)