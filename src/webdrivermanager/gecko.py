# -*- coding: utf-8 -*-
import requests
import os
from urllib.parse import urlparse
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error


class GeckoDriverManager(WebDriverManagerBase):
    """Class for downloading the Gecko (Mozilla Firefox) WebDriver.
    """

    gecko_driver_releases_url = 'https://api.github.com/repos/mozilla/geckodriver/releases/'
    fallback_url = 'https://github.com/mozilla/geckodriver/releases/'
    driver_filenames = {
        'win': 'geckodriver.exe',
        'mac': 'geckodriver',
        'linux': 'geckodriver',
    }

    def get_download_path(self, version='latest'):
        if version == 'latest':
            ver = self._get_latest_version_with_github_page_fallback(self.gecko_driver_releases_url, self.fallback_url, version)
        else:
            ver = version
        return os.path.join(self.download_root, 'gecko', ver)

    def get_download_url(self, version='latest'):
        """
        Method for getting the download URL for the Gecko (Mozilla Firefox) driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v0.20.1".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Gecko (Mozilla Firefox) driver binary.
        """
        if version == 'latest':
            gecko_driver_version_release_url = self.gecko_driver_releases_url + version
        else:
            gecko_driver_version_release_url = self.gecko_driver_releases_url + 'tags/' + version
        LOGGER.debug('Attempting to access URL: %s', gecko_driver_version_release_url)
        response = requests.get(gecko_driver_version_release_url)
        if response.ok:
            url = self._parse_github_api_response(version, response)
        elif response.status_code == 403:
            url = self._parse_github_page(version)
        else:
            raise_runtime_error('Error, unable to get info for gecko driver {0} release. Status code: {1}. Error message: {2}'.format(version, response.status_code, response.text))

        return (url, os.path.split(urlparse(url).path)[1])
