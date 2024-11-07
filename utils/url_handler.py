#utils/url_handler
from urllib.parse import urlparse
import re
import allure

class URLHandler:
    @staticmethod
    def is_ip_address(url):
        """Check if URL is an IP address"""
        ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        return bool(re.match(ip_pattern, url))

    @staticmethod
    def format_url(url):
        """Format URL with proper protocol"""
        if not url:
            return ""
        if not url.startswith(("https://", "http://")):
            return f"https://{url}"
        return url

    @staticmethod
    def extract_host_from_url(url):
        """Extract host from URL"""
        parsed_url = urlparse(URLHandler.format_url(url))
        return parsed_url.netloc or parsed_url.path.split("/")[0] or url

    @staticmethod
    def get_clean_filename(url):
        """Convert URL to a clean filename"""
        clean_url = url.lower()
        clean_url = re.sub(r'https?://', '', clean_url)
        clean_url = re.sub(r'www\.', '', clean_url)
        clean_url = re.sub(r'[^a-z0-9]', '_', clean_url)
        clean_url = re.sub(r'_+', '_', clean_url)
        clean_url = clean_url.strip('_')
        return clean_url