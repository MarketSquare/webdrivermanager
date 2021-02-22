# -*- coding: utf-8 -*-
import requests
import re
from pathlib import Path
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error, get_output


class ChromeDriverManager(WebDriverManagerBase):
    """Class for downloading the Google Chrome WebDriver."""

    chrome_driver_base_url = "https://www.googleapis.com/storage/v1/b/chromedriver"

    driver_filenames = {
        "win": "chromedriver.exe",
        "mac": "chromedriver",
        "linux": "chromedriver",
    }

    chrome_version_pattern = r"(\d+\.\d+.\d+)(\.\d+)"
    chrome_version_commands = {
        "win": [
            ["reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"],
            ["reg", "query", r"HKEY_CURRENT_USER\Software\Chromium\BLBeacon", "/v", "version"],
        ],
        "linux": [
            ["chromium", "--version"],
            ["chromium-browser", "--version"],
            ["google-chrome", "--version"],
        ],
        "mac": [
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
            ["/Applications/Chromium.app/Contents/MacOS/Chromium", "--version"],
        ],
    }

    def get_download_path(self, version="latest"):
        version = self._parse_version(version)
        return self.download_root / "chrome" / version

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Google Chome driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Google Chrome driver binary.
        """
        version = self._parse_version(version)
        LOGGER.debug("Detected OS: %sbit %s", self.bitness, self.os_name)

        chrome_driver_objects = requests.get(self.chrome_driver_base_url + "/o").json()
        # chromedriver only has 64 bit versions of mac and 32bit versions of windows. For now.
        if self.os_name == "win":
            local_bitness = "32"
        elif self.os_name == "mac":
            local_bitness = "64"
        else:
            local_bitness = self.bitness

        matcher = r"{0}/.*{1}{2}.*".format(version, self.os_name, local_bitness)

        entry = [obj for obj in chrome_driver_objects["items"] if re.match(matcher, obj["name"])]
        if not entry:
            raise_runtime_error(f"Error, unable to find appropriate download for {self.os_name}{self.bitness}.")

        url = entry[0]["mediaLink"]
        filename = Path(entry[0]["name"]).name
        return (url, filename)

    def get_latest_version(self):
        resp = requests.get(self.chrome_driver_base_url + "/o/LATEST_RELEASE")
        if resp.status_code != 200:
            raise_runtime_error(f"Error, unable to get version number for latest release, got code: {resp.status_code}")

        latest_release = requests.get(resp.json()["mediaLink"])
        return latest_release.text

    def get_compatible_version(self):
        browser_version = self._get_browser_version()
        resp = requests.get(self.chrome_driver_base_url + "/o/LATEST_RELEASE_" + browser_version)

        if resp.status_code != 200:
            raise_runtime_error(
                f"Error, unable to get version number for release {browser_version}, got code: {resp.status_code}"  # NOQA: C812
            )

        latest_release = requests.get(resp.json()["mediaLink"])
        return latest_release.text

    def _get_browser_version(self):
        commands = self.chrome_version_commands.get(self.os_name)
        if not commands:
            raise NotImplementedError("Unsupported system: %s", self.os_name)

        for cmd in commands:
            output = get_output(cmd)
            if not output:
                continue

            version = re.search(self.chrome_version_pattern, output)
            if not version:
                continue

            return version.group(1)

        raise_runtime_error("Error, unable to read current browser version")
