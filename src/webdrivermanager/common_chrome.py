# common_base.py
from .base import WebDriverManagerBase

class CommonWebDriverManager(WebDriverManagerBase):
    json_url_for_binaries = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    driver_filenames = {
        "win": "chromedriver.exe",
        "mac": "chromedriver",
        "linux": "chromedriver",
    }

    def get_download_url(self, version="latest"):
        raise NotImplementedError("get_download_url must be implemented in the subclass.")
