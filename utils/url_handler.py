from urllib.parse import urlparse
import re
import allure

class URLHandler:
    @staticmethod
    def is_ip_address(url):
        ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        return bool(re.match(ip_pattern, url))

    @staticmethod
    def format_url(url):
        if not url:
            return ""
        if not url.startswith(("https://", "http://")):
            return f"https://{url}"
        return url

    @staticmethod
    def extract_host_from_url(url):
        parsed_url = urlparse(URLHandler.format_url(url))
        return parsed_url.netloc or parsed_url.path.split("/")[0] or url

    @staticmethod
    def get_clean_filename(url):
        """Convert URL to a clean filename"""
        # Remove protocol and www
        clean_url = url.lower()
        clean_url = re.sub(r'https?://', '', clean_url)
        clean_url = re.sub(r'www\.', '', clean_url)
        # Remove special characters and spaces
        clean_url = re.sub(r'[^a-z0-9]', '_', clean_url)
        # Remove multiple underscores
        clean_url = re.sub(r'_+', '_', clean_url)
        # Trim underscores from ends
        clean_url = clean_url.strip('_')
        return clean_url