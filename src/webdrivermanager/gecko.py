# -*- coding: utf-8 -*-
import requests
import os
import re
from urllib.parse import urlparse
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error, get_output


class GeckoDriverManager(WebDriverManagerBase):
    """Class for downloading the Gecko (Mozilla Firefox) WebDriver."""

    gecko_driver_releases_url = "https://api.github.com/repos/mozilla/geckodriver/releases/"
    fallback_url = "https://github.com/mozilla/geckodriver/releases/"

    driver_filenames = {
        "win": "geckodriver.exe",
        "mac": "geckodriver",
        "linux": "geckodriver",
    }

    firefox_version_pattern = r"(\d+)(\.\d+)"
    firefox_version_commands = {
        "win": ["reg", "query", r"HKEY_CURRENT_USER\Software\Mozilla\Mozilla Firefox", "/v", "CurrentVersion"],
        "linux": ["firefox", "--version"],
        "mac": ["/Applications/Firefox.app/Contents/MacOS/firefox-bin", "--version"],
    }

    def get_download_path(self, version="latest"):
        version = self._parse_version(version)
        return self.download_root / "gecko" / version

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Gecko (Mozilla Firefox) driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v0.20.1".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Gecko (Mozilla Firefox) driver binary.
        """
        version = self._parse_version(version)
        releases_url = f"{self.gecko_driver_releases_url}tags/{version}"

        LOGGER.debug("Attempting to access URL: %s", releases_url)
        response = requests.get(releases_url)
        if response.ok:
            url = self._parse_github_api_response(version, response)
        elif response.status_code == 403:
            url = self._parse_github_page(version)
        else:
            raise_runtime_error(
                f"Error, unable to get info for gecko driver {version} release. Status code: {response.status_code}. Error message: {response.text}"  # NOQA: C812
            )

        return (url, os.path.split(urlparse(url).path)[1])

    def get_latest_version(self):
        return self._get_latest_version_with_github_page_fallback(self.gecko_driver_releases_url, self.fallback_url, "latest")

    def get_compatible_version(self):
        # Map browser version to webdriver version
        # https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
        browser_version = self._get_browser_version()
        version_map = [(60, "v0.29.0"), (57, "v0.25.0"), (55, "v0.20.1"), (53, "v0.18.0"), (52, "v0.17.0")]

        for browser_minimum, driver_version in version_map:
            if browser_version >= browser_minimum:
                return driver_version

        raise_runtime_error(f"Unsupported Firefox version: {browser_version}")

    def _get_browser_version(self):
        cmd = self.firefox_version_commands.get(self.os_name)
        if not cmd:
            raise NotImplementedError("Unsupported system: %s", self.os_name)

        output = get_output(cmd)
        if not output:
            raise_runtime_error("Error, unable to read current browser version")

        version = re.search(self.firefox_version_pattern, output)
        if not version:
            raise_runtime_error("Error, browser version does not match known pattern")

        return int(version.group(1))
