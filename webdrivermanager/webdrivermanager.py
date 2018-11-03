# -*- coding: utf-8 -*-

import abc
import logging
import os
import os.path
import platform
import requests
import shutil
import stat
import sys
import tarfile
import re

try:
    from urlparse import urlparse  # Python 2.x import
except ImportError:
    from urllib.parse import urlparse  # Python 3.x import
import zipfile

import tqdm
import lxml
import lxml.html


logger = logging.getLogger(__name__)


class WebDriverManagerBase:
    """Abstract Base Class for the different web driver downloaders
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, download_root=None, link_path=None, os_name=None):
        """
        Initializer for the class.  Accepts two optional parameters.

        :param download_root: Path where the web driver binaries will be downloaded.  If running as root in macOS or
                              Linux, the default will be '/usr/local/webdriver', otherwise will be '$HOME/webdriver'.
        :param link_path: Path where the link to the web driver binaries will be created.  If running as root in macOS
                          or Linux, the default will be 'usr/local/bin', otherwise will be '$HOME/bin'.  On macOS and
                          Linux, a symlink will be created.
        """

        self.platform = platform.system()
        self.bitness = "64" if sys.maxsize > 2 ** 32 else "32"
        self.os_name = os_name or self.get_os_name()

        if self.platform in ['Darwin', 'Linux'] and os.geteuid() == 0:
            base_path = "/usr/local"
        else:
            if 'VIRTUAL_ENV' in os.environ:
                base_path = os.environ['VIRTUAL_ENV']
            else:
                base_path = os.path.expanduser("~")

        if download_root is None:
            self.download_root = os.path.join(base_path, "webdriver")
        else:
            self.download_root = download_root

        if link_path is None:
            bin_location = "bin"
            if 'VIRTUAL_ENV' in os.environ and self.platform == "Windows":
                bin_location = "Scripts"
            self.link_path = os.path.join(base_path, bin_location)
        else:
            self.link_path = link_path

        if not os.path.isdir(self.download_root):
            os.makedirs(self.download_root)
            logger.info("Created download root directory: {0}".format(self.download_root))
        if not os.path.isdir(self.link_path):
            os.makedirs(self.link_path)
            logger.info("Created symlink directory: {0}".format(self.link_path))

    def get_os_name(self):
        namelist = {"Darwin": "mac", "Windows": "win", "Linux": "linux"}

        return namelist[self.platform]

    @abc.abstractmethod
    def get_download_path(self, version="latest"):
        """
        Method for getting the download path for a web driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.38".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.

        :returns: The download path of the web driver binary.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for a web driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.38".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the web driver binary.
        """
        raise NotImplementedError

    def get_driver_filename(self):
        return self.DRIVER_FILENAMES[self.os_name]

    def _get_latest_version_with_github_page_fallback(self, url, fallback_url, required_version):
        version = None
        info = requests.get( url + required_version)
        if info.ok:
            version = info.json()['tag_name']
        elif info.status_code == 403:
            r = requests.get(fallback_url)
            tree = lxml.html.fromstring(r.text)
            latest_release = tree.xpath(".//div[@class='release-header']")[0]
            version = latest_release.xpath(".//div/a")[0].text
        else:
            error_message = "Error attempting to get version info, got status code: {0}".format(info.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)
        return version

    def _parse_github_api_response(self, version, response):
        filenames = [asset['name'] for asset in response.json()['assets']]
        filename = [name for name in filenames if self.os_name in name]
        if len(filename) == 0:
            error_message = "Error, unable to find a download for os: {0}".format(self.os_name)
            logger.error(error_message)
            raise RuntimeError(error_message)
        if len(filename) > 1:
            filename = [name for name in filenames if self.os_name + self.bitness in name]
            if len(filename) != 1:
                error_message = "Error, unable to determine correct filename for {0}bit {1}".format(
                    self.bitness, self.os_name)
                logger.error(error_message)
                raise RuntimeError(error_message)
        filename = filename[0]

        result = response.json()["assets"][filenames.index(filename)]["browser_download_url"]
        logger.info("Download URL: {0}".format(result))
        return result

    def _parse_github_page(self, version):
        r = requests.get(self.fallback_url)
        tree = lxml.html.fromstring(r.text)
        next_page = tree.xpath(".//div[@class='pagination']/*[normalize-space(.)='Next']")[0]
        while next_page.tag != "span":
            releases = tree.xpath(".//div[@class='release-header']")
            for release in releases:
                release_version = release.xpath(".//div/a")[0].text
                if release_version in version or version == "latest":
                    for a in release.xpath("./following-sibling::details//a"):
                        link = a.attrib["href"]
                        if self.os_name in link and self.bitness in link:
                            break
                        # "os_name" should be "macos" for geckodriver but we are
                        # just checking "mac" for now ...
                        elif self.os_name in link and self.os_name == "mac":
                            break
                    else:
                        error_message = ("Error, unable to determine correct filename "
                                         "for {0}bit {1}".format(self.bitness, self.os_name))
                        logger.error(error_message)
                        raise RuntimeError(error_message)
                    return "https://github.com{}".format(link)
            next_page_url = next_page.attrib["href"]
            r = requests.get(next_page_url)
            tree = lxml.html.fromstring(r.text)
            next_page = tree.xpath(".//div[@class='pagination']/*[normalize-space(.)='Next']")[0]

    def download(self, version="latest", show_progress_bar=True):
        """
        Method for downloading a web driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.38".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.  Prior to downloading, the method
                        will check the local filesystem to see if the driver has been downloaded already and will
                        skip downloading if the file is already present locally.
        :param show_progress_bar: Boolean (default=install_requires) indicating if a progress bar should be shown in the console.
        :returns: The path + filename to the downloaded web driver binary.
        """
        download_url = self.get_download_url(version)
        filename = os.path.split(urlparse(download_url).path)[1]
        dl_path = self.get_download_path(version)
        filename_with_path = os.path.join(dl_path, filename)
        if not os.path.isdir(dl_path):
            os.makedirs(dl_path)
        if os.path.isfile(filename_with_path):
            logger.info("Skipping download. File {0} already on filesystem.".format(filename_with_path))
            return filename_with_path
        data = requests.get(download_url, stream=True)
        if data.status_code == 200:
            logger.debug("Starting download of {0} to {1}".format(download_url, filename_with_path))
            with open(filename_with_path, mode="wb") as fileobj:
                chunk_size = 1024
                if show_progress_bar:
                    expected_size = int(data.headers['Content-Length'])
                    for chunk in tqdm.tqdm(data.iter_content(chunk_size), total=int(expected_size / chunk_size), unit='kb'):
                        fileobj.write(chunk)
                else:
                    for chunk in data.iter_content(chunk_size):
                        fileobj.write(chunk)
            logger.debug("Finished downloading {0} to {1}".format(download_url, filename_with_path))
            return filename_with_path
        else:
            error_message = "Error downloading file {0}, got status code: {1}".format(filename, data.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)

    def download_and_install(self, version="latest", show_progress_bar=True):
        """
        Method for downloading a web driver binary, extracting it into the download directory and creating a symlink
        to the binary in the link directory.

        :param version: String representing the version of the web driver binary to download.  For example, "2.38".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :param show_progress_bar: Boolean (default=install_requires) indicating if a progress bar should be shown in
                                  the console.
        :returns: Tuple containing the path + filename to [0] the extracted binary, and [1] the symlink to the
                  extracted binary.
        """
        driver_filename = self.get_driver_filename()
        if driver_filename is None:
            error_message = "Error, unable to find appropriate drivername for {0}.".format(self.os_name)
            logger.error(error_message)
            raise RuntimeError(error_message)
        filename_with_path = self.download(version, show_progress_bar=show_progress_bar)
        filename = os.path.split(filename_with_path)[1]
        dl_path = self.get_download_path(version)
        if filename.lower().endswith(".tar.gz"):
            extract_dir = os.path.join(dl_path, filename[:-7])
        elif filename.lower().endswith(".zip"):
            extract_dir = os.path.join(dl_path, filename[:-4])
        elif filename.lower().endswith(".exe"):
            extract_dir = os.path.join(dl_path, filename[:-4])
        else:
            error_message = "Unknown archive format: {0}".format(filename)
            logger.error(error_message)
            raise RuntimeError(error_message)
        if not os.path.isdir(extract_dir):
            os.makedirs(extract_dir)
            logger.debug("Created directory: {0}".format(extract_dir))
        if filename.lower().endswith(".tar.gz"):
            with tarfile.open(os.path.join(dl_path, filename), mode="r:*") as tar:
                tar.extractall(extract_dir)
                logger.debug("Extracted files: {0}".format(", ".join(tar.getnames())))
        elif filename.lower().endswith(".zip"):
            with zipfile.ZipFile(os.path.join(dl_path, filename), mode="r") as driver_zipfile:
                driver_zipfile.extractall(extract_dir)
        elif filename.lower().endswith(".exe"):
            shutil.copy2(os.path.join(dl_path, filename), os.path.join(extract_dir, filename))

        for root, dirs, files in os.walk(extract_dir):
            for curr_file in files:
                if curr_file == driver_filename:
                    actual_driver_filename = os.path.join(root, curr_file)
                    break

        if not actual_driver_filename:
            logger.warn("Cannot locate binary {0} from the archive".format(driver_filename))
            return None

        if self.platform in ['Darwin', 'Linux']:
            symlink_src = actual_driver_filename
            symlink_target = os.path.join(self.link_path, driver_filename)
            if os.path.islink(symlink_target):
                if os.path.samefile(symlink_src, symlink_target):
                    logger.info("Symlink already exists: {0} -> {1}".format(symlink_target, symlink_src))
                    return tuple([symlink_src, symlink_target])
                else:
                    logger.warning("Symlink {0} already exists and will be overwritten.".format(symlink_target))
                    os.unlink(symlink_target)
            os.symlink(symlink_src, symlink_target)
            logger.info("Created symlink: {0} -> {1}".format(symlink_target, symlink_src))
            st = os.stat(symlink_src)
            os.chmod(symlink_src, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return tuple([symlink_src, symlink_target])
        elif self.platform == "Windows":
            src_file = actual_driver_filename
            dest_file = os.path.join(self.link_path, driver_filename)
            if os.path.isfile(dest_file):
                logger.info("File {0} already exists and will be overwritten.".format(dest_file))
            shutil.copy2(src_file, dest_file)
            return tuple([src_file, dest_file])


class GeckoDriverManager(WebDriverManagerBase):
    """Class for downloading the Gecko (Mozilla Firefox) WebDriver.
    """

    gecko_driver_releases_url = "https://api.github.com/repos/mozilla/geckodriver/releases/"
    fallback_url = "https://github.com/mozilla/geckodriver/releases/"
    DRIVER_FILENAMES = {
        "win": "geckodriver.exe",
        "mac": "geckodriver",
        "linux": "geckodriver"
    }

    def get_download_path(self, version="latest"):
        if version == "latest":
            ver = self._get_latest_version_with_github_page_fallback(self.gecko_driver_releases_url, self.fallback_url, version)
        else:
            ver = version
        return os.path.join(self.download_root, "gecko", ver)

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Gecko (Mozilla Firefox) driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v0.20.1".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Gecko (Mozilla Firefox) driver binary.
        """
        if version == "latest":
            gecko_driver_version_release_url = self.gecko_driver_releases_url + version
        else:
            gecko_driver_version_release_url = self.gecko_driver_releases_url + "tags/" + version
        logger.debug("Attempting to access URL: {0}".format(gecko_driver_version_release_url))
        response = requests.get(gecko_driver_version_release_url)
        if response.ok:
            result = self._parse_github_api_response(version, response)
        elif response.status_code == 403:
            result = self._parse_github_page(version)
        else:
            error_message = ("Error, unable to get info for gecko driver {0} release. "
                             "Status code: {1}. Error message: {2}")
            error_message = error_message.format(version, response.status_code, response.text)
            logger.error(error_message)
            raise RuntimeError(error_message)
        return result


class ChromeDriverManager(WebDriverManagerBase):
    """Class for downloading the Google Chrome WebDriver.
    """

    chrome_driver_base_url = 'https://www.googleapis.com/storage/v1/b/chromedriver'

    def _get_latest_version_number(self):
        resp = requests.get(self.chrome_driver_base_url + '/o/LATEST_RELEASE')
        if resp.status_code != 200:
            error_message = "Error, unable to get version number for latest release, got code: {0}".format(resp.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)
        latest_release = requests.get(resp.json()['mediaLink'])
        return latest_release.text

    DRIVER_FILENAMES = {
        "win": "chromedriver.exe",
        "mac": "chromedriver",
        "linux": "chromedriver"
    }

    def get_download_path(self, version="latest"):
        if version == "latest":
            ver = self._get_latest_version_number()
        else:
            ver = version
        return os.path.join(self.download_root, "chrome", ver)

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Google Chome driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Google Chrome driver binary.
        """
        if version == "latest":
            version = self._get_latest_version_number()

        logger.debug("Detected OS: {0}bit {1}".format(self.bitness, self.os_name))

        chrome_driver_objects = requests.get(self.chrome_driver_base_url + '/o')
        matching_versions = [item for item in chrome_driver_objects.json()['items'] if item['name'].startswith(version)]
        os_matching_versions = [item for item in matching_versions if self.os_name in item['name']]
        if not os_matching_versions:
            error_message = "Error, unable to find appropriate download for {0}.".format(self.os_name + self.bitness)
            logger.error(error_message)
            raise RuntimeError(error_message)
        elif len(os_matching_versions) == 1:
            result = os_matching_versions[0]['mediaLink']
        elif len(os_matching_versions) == 2:
            result = [item for item in matching_versions if self.os_name + self.bitness in item['name']][0]['mediaLink']

        return result


class OperaChromiumDriverManager(WebDriverManagerBase):
    """Class for downloading the Opera Chromium WebDriver.
    """

    opera_chromium_driver_releases_url = "https://api.github.com/repos/operasoftware/operachromiumdriver/releases/"
    fallback_url = "https://github.com/operasoftware/operachromiumdriver/releases"
    DRIVER_FILENAMES = {
        "win": "operadriver.exe",
        "mac": "operadriver",
        "linux": "operadriver"
    }

    def get_download_path(self, version="latest"):
        if version == "latest":
            ver = self._get_latest_version_with_github_page_fallback(self.opera_chromium_driver_releases_url, self.fallback_url, version)
        else:
            ver = version
        return os.path.join(self.download_root, "operachromium", ver)


    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Opera Chromium driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v2.36".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Opera Chromium driver binary.
        """
        if version == "latest":
            opera_chromium_driver_version_release_url = self.opera_chromium_driver_releases_url + version
        else:
            opera_chromium_driver_version_release_url = self.opera_chromium_driver_releases_url + "tags/" + version
        logger.debug("Attempting to access URL: {0}".format(opera_chromium_driver_version_release_url))
        response = requests.get(opera_chromium_driver_version_release_url)
        if response.ok:
            result = self._parse_github_api_response(version, response)
        elif response.status_code == 403:
            result = self._parse_github_page(version)
        else:
            error_message = ("Error, unable to get info for opera chromium driver {0} release. "
                             "Status code: {1}. Error message: {2}")
            error_message = error_message.format(version, response.status_code, response.text)
            logger.error(error_message)
            raise RuntimeError(error_message)
        return result



class EdgeDriverManager(WebDriverManagerBase):
    """Class for downloading the Edge WebDriver.
    """
    DRIVER_FILENAMES = {
        "win": "MicrosoftWebDriver.exe",
        "mac": None,
        "linux": None
    }

    edge_driver_base_url = 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/'


    def _get_download_url(self, body, version):
        try:
            tree = lxml.html.fromstring(body.text)
            link = tree.xpath("//li[contains(@class,'driver-download')]/p[contains(@class,'driver-download__meta')]/a/../../p[contains(text(),'6.17134')]/../a")[0]
            return link.get('href')
        except lxml.etree.ParserError:
            return None

    def _get_version_number(self, body):
        try:
            tree = lxml.html.fromstring(body.text)
            li_text = tree.xpath("//li[contains(@class, 'driver-download')]/p[contains(@class, 'driver-download__meta')]/a/..")[0].text
            results = re.findall(r"Version: ([\d\.]+) |", li_text)[0]
            if bool(results and results[0]):
                return results[0]
            else:
                return None
        except lxml.etree.ParserError:
            return None

    def _get_latest_version_number(self):
        resp = requests.get(self.edge_driver_base_url)
        if resp.status_code != 200:
            error_message = "Error, unable to get version number for latest release, got code: {0}".format(resp.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)
        return self._get_version_number(resp)

    def get_download_path(self, version="latest"):
        if version == "latest":
            ver = self._get_latest_version_number()
        else:
            ver = version
        return os.path.join(self.download_root, "edge", ver)

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Google Chome driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "2.39".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Google Chrome driver binary.
        """
        if version == "latest":
            version = self._get_latest_version_number()

        logger.debug("Detected OS: {0}bit {1}".format(self.bitness, self.os_name))

        resp = requests.get(self.edge_driver_base_url)
        if resp.status_code != 200:
            error_message = "Error, unable to get version number for latest release, got code: {0}".format(resp.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)

        return self._get_download_url(resp, version)

