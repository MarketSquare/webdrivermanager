import abc
import logging
import os
import os.path
import platform
import requests
import sys
import tarfile
from urllib.parse import urlparse
import zipfile

import tqdm


logger = logging.getLogger(__name__)


class WebDriverDownloaderBase:
    """Abstract Base Class for the different web driver downloaders
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, download_path=None, link_path=None):
        """
        Initializer for the class.  Accepts two optional parameters.

        :param download_path: Path where the web driver binaries will be downloaded.  If running as root in macOS or
                              Linux, the default will be '/usr/local/webdriver', otherwise will be '$HOME/webdriver'.
        :param link_path: Path where the link to the web driver binaries will be created.  If running as root in macOS
                          or Linux, the default will be 'usr/local/bin', otherwise will be '$HOME/bin'.  On macOS and
                          Linux, a symlink will be created.
        """

        if platform.system() in ['Darwin', 'Linux'] and os.geteuid() == 0:
            base_path = "/usr/local"
        else:
            base_path = os.path.expanduser("~")

        if download_path is None:
            self.download_path = os.path.join(base_path, "webdriver")
        else:
            self.download_path = download_path

        if link_path is None:
            self.link_path = os.path.join(base_path, "bin")
        else:
            self.link_path = link_path

        if not os.path.isdir(self.download_path):
            os.makedirs(self.download_path)
            logger.info("Created download directory: {0}".format(self.download_path))
        if not os.path.isdir(self.link_path):
            os.makedirs(self.link_path)
            logger.info("Created symlink directory: {0}".format(self.link_path))

    @abc.abstractmethod
    def get_driver_filename(self):
        """
        Method for getting the filename of the web driver binary.

        :returns: The filename of the web driver binary.
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
        filename_with_path = os.path.join(self.download_path, filename)
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
        filename_with_path = self.download(version, show_progress_bar=True)
        filename = os.path.split(filename_with_path)[1]
        if filename.lower().endswith(".tar.gz"):
            extract_dir = os.path.join(self.download_path, filename[:-7])
        elif filename.lower().endswith(".zip"):
            extract_dir = os.path.join(self.download_path, filename[:-4])
        else:
            error_message = "Unknown archive format: {0}".format(filename)
            logger.error(error_message)
            raise RuntimeError(error_message)
        if not os.path.isdir(extract_dir):
            os.makedirs(extract_dir)
            logger.debug("Created directory: {0}".format(extract_dir))
        if filename.lower().endswith(".tar.gz"):
            with tarfile.open(os.path.join(self.download_path, filename), mode="r:*") as tar:
                tar.extractall(extract_dir)
                logger.debug("Extracted files: {0}".format(", ".join(tar.getnames())))
        elif filename.lower().endswith(".zip"):
            with zipfile.ZipFile(os.path.join(self.download_path, filename), mode="r") as driver_zipfile:
                driver_zipfile.extractall(extract_dir)
        driver_filename = self.get_driver_filename()
        if platform.system() in ['Darwin', 'Linux']:
            symlink_src = os.path.join(extract_dir, driver_filename)
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
            return tuple([symlink_src, symlink_target])
        elif platform.system() == "Windows":
            driver_filename_with_path = os.path.join(extract_dir, driver_filename)
            wrapper_filename = os.path.join(self.link_path, os.path.splitext(driver_filename)[0] + ".cmd")
            if os.path.isfile(wrapper_filename):
                logger.info("Wrapper script {0} already exists and will be overwritten.".format(wrapper_filename))
            with open(wrapper_filename, mode="w") as fileobj:
                fileobj.write("@" + driver_filename_with_path + " %*")
            logger.info("Created wrapper script: {0} -> {1}".format(wrapper_filename, driver_filename_with_path))
            return tuple([driver_filename_with_path, wrapper_filename])


class GeckoDriverDownloader(WebDriverDownloaderBase):
    """Class for downloading the Gecko (Mozilla Firefox) WebDriver.
    """

    def get_driver_filename(self):
        if platform.system() == "Windows":
            return "geckodriver.exe"
        else:
            return "geckodriver"

    def get_download_url(self, version="latest"):
        """
        Method for getting the download URL for the Gecko (Mozilla Firefox) driver binary.

        :param version: String representing the version of the web driver binary to download.  For example, "v0.20.1".
                        Default if no version is specified is "latest".  The version string should match the version
                        as specified on the download page of the webdriver binary.
        :returns: The download URL for the Gecko (Mozilla Firefox) driver binary.
        """
        gecko_driver_releases_url = "https://api.github.com/repos/mozilla/geckodriver/releases/"
        if version == "latest":
            gecko_driver_version_release_url = gecko_driver_releases_url + version
        else:
            gecko_driver_version_release_url = gecko_driver_releases_url + "tags/" + version
        logger.debug("Attempting to access URL: {0}".format(gecko_driver_version_release_url))
        info = requests.get(gecko_driver_version_release_url)
        if info.status_code != 200:
            error_message = "Error, unable to get info for gecko driver {0} release. Status code: {1}".format(
                    version, info.status_code)
            logger.error(error_message)
            raise RuntimeError(error_message)

        os_name = platform.system()
        if os_name == "Darwin":
            os_name = "macos"
        elif os_name == "Windows":
            os_name = "win"
        elif os_name == "Linux":
            os_name = "linux"
        bitness = "64" if sys.maxsize > 2 ** 32 else "32"
        logger.debug("Detected OS: {0}bit {1}".format(bitness, os_name))

        filenames = [asset['name'] for asset in info.json()['assets']]
        filename = [name for name in filenames if os_name in name]
        if len(filename) == 0:
            error_message = "Error, unable to find a download for os: {0}".format(os_name)
            logger.error(error_message)
            raise RuntimeError(error_message)
        if len(filename) > 1:
            filename = [name for name in filenames if os_name + bitness in name]
            if len(filename) != 1:
                error_message = "Error, unable to determine correct filename for {0}bit {1}".format(bitness, os_name)
                logger.error(error_message)
                raise RuntimeError(error_message)
        filename = filename[0]

        result = info.json()['assets'][filenames.index(filename)]['browser_download_url']
        logger.info("Download URL: {0}".format(result))
        return result
