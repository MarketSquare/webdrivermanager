# -*- coding: utf-8 -*-
import requests
import re
import os
from bs4 import BeautifulSoup
from .base import WebDriverManagerBase
from .misc import LOGGER, raise_runtime_error, versiontuple


class EdgeChromiumDriverManager(WebDriverManagerBase):
    """Class for downloading Edge Chromium WebDriver.
    """

    edgechromium_driver_base_url = 'https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?maxresults=1000&comp=list&timeout=60000'
    _drivers = None
    _versions = None

    def _extract_ver(self, s):
        matcher = r".*\/edgewebdriver\/([\d.]+)\/edgedriver_.*\.zip"
        ret = re.match(matcher, s)
        return ret.group(1)

    def _populate_cache(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise_runtime_error('Error, unable to get version number for latest release, got code: {0}'.format(resp.status_code))

        soup = BeautifulSoup(resp.text, 'lxml')

        arch_matcher = "{}{}".format(self.os_name, self.bitness)
        drivers = filter(lambda entry: 'edgedriver_{}'.format(arch_matcher) in entry.contents[0], soup.find_all('url'))
        self._drivers = list(map(lambda entry: entry.contents[0], drivers))
        self._versions = set(map(lambda entry: versiontuple(self._extract_ver(entry)), self._drivers))

    def _get_latest_version_number(self):
        if self._drivers is None or self._versions is None:
            self._populate_cache(self.edgechromium_driver_base_url)
        return ".".join(map(str, max(self._versions)))

    driver_filenames = {
        'win': 'msedgedriver.exe',
        'mac': 'msedgedriver',
        'linux': None,
    }

    def get_download_path(self, version='latest'):
        if version == 'latest':
            ver = self._get_latest_version_number()
        else:
            ver = version
        return os.path.join(self.download_root, 'edgechromium', ver)

    def get_download_url(self, version='latest'):
        """
        Method for getting the download URL for the Google Chome driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Internet Explorer driver binary.
        """
        if version == 'latest':
            version = self._get_latest_version_number()

        if not self._drivers:
            self._populate_cache(self.edgechromium_driver_base_url)

        LOGGER.debug('Detected OS: %sbit %s', self.bitness, self.os_name)
        local_osname = self.os_name
        matcher = r'.*/{0}/edgedriver_{1}{2}'.format(version, local_osname, self.bitness)
        entry = [entry for entry in self._drivers if re.match(matcher, entry)]
        if not entry:
            raise_runtime_error('Error, unable to find appropriate download for {0}{1}.'.format(self.os_name, self.bitness))

        url = entry[0]
        filename = os.path.basename(entry[0])
        return (url, filename)
