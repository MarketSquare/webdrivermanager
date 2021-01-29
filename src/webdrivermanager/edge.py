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
        "mac": None,
        "linux": None,
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
        :returns: The download URL for the Google Chrome driver binary.
        """
        version = self._parse_version(version)
        LOGGER.debug("Detected OS: %sbit %s", self.bitness, self.os_name)

        # TODO: handle error 500 by sleep & retry here
        resp = requests.get(self.edge_driver_base_url)
        if resp.status_code != 200:
            raise_runtime_error(f"Error, unable to get version number for latest release, got code: {resp.status_code}")

        url = self._get_download_url(resp, version)
        return (url, os.path.split(urlparse(url).path)[1])

    def get_latest_version(self):
        # TODO: handle error 500 by sleep & retry here
        resp = requests.get(self.edge_driver_base_url)
        if resp.status_code != 200:
            raise_runtime_error(f"Error, unable to get version number for latest release, got code: {resp.status_code}")

        return self._get_version_number(resp)

    def get_compatible_version(self):
        raise NotImplementedError

    def _get_download_url(self, body, version):
        try:
            tree = BeautifulSoup(body.text, "html.parser")
            mstr = f"Release {version}"
            link_texts = tree.find_all("a", string=re.compile(mstr))
            if "index.html" in link_texts[0]["href"]:
                local_bitness = self.bitness
                if local_bitness == "32":
                    local_bitness = "86"
                mstr = f"WebDriver for release number {version} x{local_bitness}"
                link_texts = tree.find_all("a", {"aria-label": re.compile(mstr)})
            return link_texts[0]["href"]
        except Exception:
            return None

    def _get_version_number(self, body):
        try:
            tree = BeautifulSoup(body.text, "html.parser")
            link_texts = tree.find_all("a", string=re.compile("Release "))
            results = re.findall(r"\"WebDriver for release number ([\d\.]+)\"", str(link_texts[0]))
            if bool(results and results[0]):
                return results[0]

            return None
        except Exception:
            return None
