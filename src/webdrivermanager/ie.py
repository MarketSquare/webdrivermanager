# -*- coding: utf-8 -*-
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error, versiontuple


class IEDriverManager(WebDriverManagerBase):
    """Class for downloading Internet Explorer WebDriver."""

    ie_driver_base_url = "https://selenium-release.storage.googleapis.com"
    _drivers = None
    _versions = None

    driver_filenames = {
        "win": "IEDriverServer.exe",
        "mac": None,
        "linux": None,
    }

    def get_download_path(self, version="latest"):
        version = self._parse_version(version)
        return self.download_root / "ie" / version

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Google Chome driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Internet Explorer driver binary.
        """
        version = self._parse_version(version)

        if not self._drivers:
            self._populate_cache(self.ie_driver_base_url)

        LOGGER.debug("Detected OS: %sbit %s", self.bitness, self.os_name)
        local_osname = self.os_name
        if self.bitness == "64":
            local_osname = "x"
        elif self.bitness == "32":
            local_osname = "Win"
        matcher = r".*/.*_{0}{1}_{2}".format(local_osname, self.bitness, version)
        entry = [entry for entry in self._drivers if re.match(matcher, entry)]

        if not entry:
            raise_runtime_error(f"Error, unable to find appropriate download for {self.os_name}{self.bitness}.")

        url = f"{self.ie_driver_base_url}/{entry[0]}"
        filename = Path(entry[0]).name
        return (url, filename)

    def get_latest_version(self):
        if self._drivers is None or self._versions is None:
            self._populate_cache(self.ie_driver_base_url)
        return ".".join(map(str, max(self._versions)))

    def get_compatible_version(self):
        raise NotImplementedError

    def _extract_ver(self, s):
        matcher = r".*\/IEDriverServer_(x64|Win32)_(\d+\.\d+\.\d+)\.zip"
        ret = re.match(matcher, s)
        return ret.group(2)

    def _populate_cache(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise_runtime_error(f"Error, unable to get version number for latest release, got code: {resp.status_code}")

        soup = BeautifulSoup(resp.text, "lxml")
        drivers = filter(lambda entry: "IEDriverServer_" in entry.contents[0], soup.find_all("key"))
        self._drivers = list(map(lambda entry: entry.contents[0], drivers))
        self._versions = set(map(lambda entry: versiontuple(self._extract_ver(entry)), self._drivers))
