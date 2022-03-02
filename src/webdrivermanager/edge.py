# -*- coding: utf-8 -*-
import requests
import re
import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error


class EdgeDriverManager(WebDriverManagerBase):
    """Class for downloading the Edge WebDriver."""

    driver_filenames = {
        "win": ["MicrosoftWebDriver.exe", "msedgedriver.exe"],
        "mac": "msedgedriver",
        "linux": "msedgedriver",
    }

    edge_driver_base_url = "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"

    def get_download_path(self, version="latest"):
        version = self._parse_version(version)
        return self.download_root / "edge" / version

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the MSEdge WebDriver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the MSEdge driver binary.
        """
        version = self._parse_version(version)
        LOGGER.debug("Detected OS: %sbit %s", self.bitness, self.os_name)

        # TODO: handle error 500 by sleep & retry here
        resp = requests.get(self.edge_driver_base_url)
        if resp.status_code != 200:
            raise_runtime_error(f"Error, unable to get version number for latest release, got code: {resp.status_code}")

        url = self._get_download_url(resp, version)
        return url, os.path.split(urlparse(url).path)[1]

    def get_latest_version(self):
        return "latest"

    def get_compatible_version(self):
        raise NotImplementedError

    def _get_download_url(self, body, version):
        try:
            latest_stable_download_urls = {
                "mac": "https://msedgedriver.azureedge.net/98.0.1108.62/edgedriver_mac64.zip",
                "win": {"32": "https://msedgedriver.azureedge.net/98.0.1108.62/edgedriver_win32.zip",
                        "86": "https://msedgedriver.azureedge.net/98.0.1108.62/edgedriver_win64.zip",
                        "ARM64": "https://msedgedriver.azureedge.net/98.0.1108.62/edgedriver_arm64.zip"},
                "linux": "https://msedgedriver.azureedge.net/98.0.1108.62/edgedriver_linux64.zip"
            }
            os_name = self.os_name

            if version == "latest":
                if os_name in ["mac", "linux"]:
                    return latest_stable_download_urls[os_name]

                # TODO: Add support for Windows ARM
                if os_name == "win" and self.bitness == "32":
                    return latest_stable_download_urls["win"]["32"]

                return latest_stable_download_urls["win"]["86"]

            driver_files = {
                "mac": "edgedriver_mac64.zip",
                "win": {"32": "edgedriver_win32.zip",
                        "86": "edgedriver_win64.zip",
                        "ARM64": "edgedriver_arm64.zip"},
                "linux": "edgedriver_linux64.zip"
            }
            driver_file = ''
            if os_name == "mac":
                driver_file = driver_files["mac"]
            elif os_name == "linux":
                driver_file = driver_files["linux"]
            elif os_name == "win":
                # TODO: Add support for Windows ARM
                if self.bitness == "32":
                    driver_file = driver_files["win"]["32"]
                else:
                    driver_file = driver_files["win"]["86"]

            return f"https://msedgedriver.azureedge.net/{version}/{driver_file}"
        except Exception:
            return None
