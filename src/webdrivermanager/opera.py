# -*- coding: utf-8 -*-
import requests
import os
from urllib.parse import urlparse
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error


class OperaChromiumDriverManager(WebDriverManagerBase):
    """Class for downloading the Opera Chromium WebDriver."""

    opera_chromium_driver_releases_url = "https://api.github.com/repos/operasoftware/operachromiumdriver/releases/"
    fallback_url = "https://github.com/operasoftware/operachromiumdriver/releases/"
    driver_filenames = {
        "win": "operadriver.exe",
        "mac": "operadriver",
        "linux": "operadriver",
    }

    def get_download_path(self, version="latest"):
        if version == "latest":
            ver = self._get_latest_version_with_github_page_fallback(
                self.opera_chromium_driver_releases_url, self.fallback_url, version  # NOQA: C812
            )
        else:
            ver = version
        return self.download_root / "operachromium" / ver

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Opera Chromium driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v2.36".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Opera Chromium driver binary.
        """
        version = self._parse_version(version)
        releases_url = f"{self.opera_chromium_driver_releases_url}tags/{version}"

        LOGGER.debug("Attempting to access URL: %s", releases_url)
        response = requests.get(releases_url)
        if response.ok:
            url = self._parse_github_api_response(version, response)
        elif response.status_code == 403:
            url = self._parse_github_page(version)
        else:
            raise_runtime_error(
                f"Error, unable to get info for opera chromium driver {version} release. Status code: {response.status_code}. Error message: {response.text}"  # NOQA: C812
            )

        return (url, os.path.split(urlparse(url).path)[1])

    def get_latest_version(self):
        return self._get_latest_version_with_github_page_fallback(
            self.opera_chromium_driver_releases_url, self.fallback_url, "latest"  # NOQA: C812
        )

    def get_compatible_version(self):
        raise NotImplementedError
