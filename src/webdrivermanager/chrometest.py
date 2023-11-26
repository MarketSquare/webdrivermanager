# -*- coding: utf-8 -*-
import requests
import re
from pathlib import Path
from .base import WebDriverManagerBase
from .common_chrome import CommonWebDriverManager
from .misc import LOGGER, raise_runtime_error, get_output
import json
import sys
import platform



class ChromeDriverForTest(CommonWebDriverManager):
    json_url_for_binaries = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

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
        json_data = self.fetch_chromedriver_json_data()
        target_channel="Stable"
        if json_data is None:
            LOGGER.error("Failed to fetch chromedriver JSON data.")
            return None
        json_obj = json.loads(json_data)
        target_channel="Stable"
        channels = json_obj.get("channels", {})
        if target_channel in channels:
            target_channel_info = channels.get(target_channel, {})
            version = target_channel_info.get("version", "")
        print(version)
        return self.download_root / "chrome" / version
    
    def get_download_url(self, version="latest"):
        target_version = self._get_browser_version().split('.')[0]
        print(target_version)
        json_data = self.fetch_chromedriver_json_data()
        target_channel="Stable"
        if json_data is None:
            LOGGER.error("Failed to fetch chromedriver JSON data.")
            return None
        json_obj = json.loads(json_data)
        channels = json_obj.get("channels", {})
        LOGGER.debug(f"Channels: {channels}")
        print("got it sidhant")
        print("channel:", channels)
        print("target channel:",target_channel)
        if target_channel in channels:
            target_channel_info = channels.get(target_channel, {})
            version = target_channel_info.get("version", "")
            print("version", version)
            print("target channel ifo",target_channel_info)
            target_version_channel = target_channel_info.get("version", "").split('.')[0]
            print(target_version_channel)
            downloads = target_channel_info.get("downloads", {})
            print("target info", target_version)
            if target_version_channel == target_version:
                os_platform = sys.platform.lower()
                if  os_platform == "darwin":
                    os_platform = self.get_architecture()
                    filename = "chromedriver-" + os_platform + ".zip"
                print("os",os_platform)
                chromedriver_urls = downloads.get("chromedriver", [])
                for entry in chromedriver_urls:
                    print("entry",entry)
                    if entry.get("platform", "").lower() == os_platform:
                        print(entry.get("url", ""), version)
                        return entry.get("url", ""), filename
        LOGGER.warning("No valid download URL found for chromedriver.")
        return None


    def get_architecture(self):
        arch = platform.architecture()[0]
        system = platform.system()
    
        if system == "Darwin":
            # macOS
            if arch == "64bit":
                return "mac-arm64" if "arm" in platform.processor().lower() else "mac-x64"
        return "Unknown"

    def fetch_chromedriver_json_data(self):
        url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        response = requests.get(url)
        if response.status_code == 200:
            jsondata = json.dumps(response.json())
            return jsondata
        else:
            print(f"Error fetching data. Status code: {response.status_code}")
            return None
 
    

    def _get_browser_version(self):
        commands = self.chrome_version_commands.get(self.os_name)
        if not commands:
            raise NotImplementedError("Unsupported system: %s", self.os_name)

        for cmd in commands:
            output = get_output(cmd)
            if not output:
                continue

            version = re.search(self.chrome_version_pattern, output)
            print(version)
            if not version:
                continue

            return version.group(1)

        raise RuntimeError("Unable to read current browser version")

