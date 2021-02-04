# -*- coding: utf-8 -*-

import re
import abc
import sys
import stat
import shutil
import tarfile
import zipfile
import platform
import tqdm
import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from appdirs import AppDirs

from .misc import LOGGER, _inside_virtualenv, raise_runtime_error


class WebDriverManagerBase:
    """Abstract Base Class for the different web driver downloaders"""

    __metaclass__ = abc.ABCMeta
    fallback_url = None
    driver_filenames = None

    def _get_basepath(self):
        if self.os_name in ["mac", "linux"] and os.geteuid() == 0:
            return Path(self.dirs.site_data_dir)
        if _inside_virtualenv():
            return Path(sys.prefix) / "WebDriverManager"
        return Path(self.dirs.user_data_dir)

    def __init__(self, download_root=None, link_path=None, os_name=None, bitness=None):
        """
        Initializer for the class.  Accepts two optional parameters.

        :param download_root: Path where the web driver binaries will be downloaded.  If running as root in macOS or
                              Linux, the default will be '/usr/local/webdriver', otherwise python appdirs module will
                              be used to determine appropriate location if no value given.
        :param link_path: Path where the link to the web driver binaries will be created.  If running as root in macOS
                          or Linux, the default will be 'usr/local/bin', otherwise appdirs python module will be used
                          to determine appropriate location if no value give. If set "AUTO", link will be created into
                          first writeable directory in PATH. If set "SKIP", no link will be created.
        """

        if not bitness:
            self.bitness = "64" if sys.maxsize > 2 ** 32 else "32"  # noqa: KEK100
        else:
            self.bitness = bitness

        self.os_name = os_name or self.get_os_name()
        self.dirs = AppDirs("WebDriverManager", "rasjani")
        base_path = self._get_basepath()
        self.download_root = Path(download_root or base_path)

        if link_path in [None, "AUTO"]:
            bin_location = "bin"
            if _inside_virtualenv():
                if self.os_name == "win" and "CYGWIN" not in platform.system():
                    bin_location = "Scripts"
                self.link_path = Path(sys.prefix) / bin_location
            else:
                if self.os_name in ["mac", "linux"] and os.geteuid() == 0:
                    self.link_path = Path("/usr/local/bin")
                else:
                    dir_in_path = None
                    if link_path == "AUTO":
                        dir_in_path = self._find_bin()
                    self.link_path = dir_in_path or base_path / bin_location
        elif link_path == "SKIP":
            self.link_path = None
        else:
            self.link_path = Path(link_path)

        try:
            self.download_root.mkdir(parents=True, exist_ok=True)
            LOGGER.info("Created download root directory: %s", self.download_root)
        except OSError:
            pass

        if self.link_path:
            try:
                self.link_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info("Created symlink directory: %s", self.link_path)
            except OSError:
                pass

    def _find_bin(self):
        dirs = os.environ["PATH"].split(os.pathsep)
        for directory in dirs:
            if os.access(directory, os.W_OK):
                return Path(directory)
        return None

    def get_os_name(self):
        platform_name = platform.system()
        namelist = {"Darwin": "mac", "Windows": "win", "Linux": "linux"}
        if "CYGWIN" in platform_name:
            return "win"

        return namelist[platform_name]

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

    @abc.abstractmethod
    def get_latest_version(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_compatible_version(self):
        raise NotImplementedError

    def get_driver_filename(self):
        return self.driver_filenames[self.os_name]

    def _parse_version(self, version):
        method = version.strip().lower()

        # Attempt to match webdriver to current browser version, if supported
        if method == "compatible":
            try:
                return self.get_compatible_version()
            except NotImplementedError:
                pass
            except Exception as exc:
                LOGGER.warning("Failed to parse compatible version: %s", exc)
            method = "latest"

        if method == "latest":
            return self.get_latest_version()
        else:
            return version

    def _get_latest_version_with_github_page_fallback(self, url, fallback_url, required_version):
        version = None
        info = requests.get(f"{url}{required_version}")

        if info.ok:
            version = info.json()["tag_name"]
        elif info.status_code == 403:
            response = requests.get(fallback_url)
            tree = BeautifulSoup(response.text, "html.parser")
            latest_release = tree.find("div", {"class", "release-header"}).findAll("a")[0]
            version = latest_release.text
        else:
            raise_runtime_error(f"Error attempting to get version info, got status code: {info.status_code}")

        return version  # noqa: R504

    def _parse_github_api_response(self, version, response):
        filenames = [asset["name"] for asset in response.json()["assets"]]
        filename = [name for name in filenames if self.os_name in name]
        if not filename:
            raise_runtime_error(f"Error, unable to find a download for os: {self.os_name}")

        if len(filename) > 1:
            filename = [name for name in filenames if self.os_name + self.bitness in name and not name.endswith(".asc")]
            if len(filename) != 1:
                raise_runtime_error(f"Error, unable to determine correct filename for {self.bitness}bit {self.os_name}")

        filename = filename[0]

        url = response.json()["assets"][filenames.index(filename)]["browser_download_url"]
        LOGGER.info("Download URL: %s", url)
        return url

    def _parse_github_page(self, version):
        if version == "latest":
            release_url = f"{self.fallback_url}latest"
            matcher = r".*\/releases\/download\/.*{}".format(self.os_name)
        else:
            release_url = f"{self.fallback_url}tag/{version}"
            matcher = r".*\/releases\/download\/{}\/.*{}".format(version, self.os_name)

        response = requests.get(release_url)
        if response.status_code != 200:
            return None

        tree = BeautifulSoup(response.text, "html.parser")
        links = tree.find_all("a", href=re.compile(matcher))
        if len(links) == 2:
            matcher = f"{matcher}.*{self.bitness}"
            links = tree.find_all("a", href=re.compile(matcher))

        if links:
            return f"https://github.com{links[0]['href']}"

        return None

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
        (download_url, filename) = self.get_download_url(version)

        dl_path = Path(self.get_download_path(version))
        filename_with_path = dl_path / filename
        dl_path.mkdir(parents=True, exist_ok=True)
        if filename_with_path.exists():
            LOGGER.info("Skipping download. File %s already on filesystem.", filename_with_path)
            return filename_with_path
        # TODO: Extra the downloading ?
        data = requests.get(download_url, stream=True)
        if data.status_code == 200:
            LOGGER.debug("Starting download of %s to %s", download_url, filename_with_path)
            with open(filename_with_path, mode="wb") as fileobj:
                chunk_size = 1024
                if show_progress_bar:
                    expected_size = int(data.headers["Content-Length"])
                    for chunk in tqdm.tqdm(data.iter_content(chunk_size), total=int(expected_size / chunk_size), unit="kb"):
                        fileobj.write(chunk)
                else:
                    for chunk in data.iter_content(chunk_size):
                        fileobj.write(chunk)
            LOGGER.debug("Finished downloading %s to %s", download_url, filename_with_path)
            return filename_with_path

        raise_runtime_error(f"Error downloading file {filename}, got status code: {data.status_code}")
        return None

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
            raise_runtime_error(f"Error, unable to find appropriate drivername for {self.os_name}.")

        filename_with_path = self.download(version, show_progress_bar=show_progress_bar)
        filename = filename_with_path.name
        dl_path = Path(self.get_download_path(version))
        archive_type = 0

        if filename.lower().endswith(".tar.gz"):
            extract_dir = dl_path / filename[:-7]
            archive_type = 1
        elif filename.lower().endswith(".zip"):
            extract_dir = dl_path / filename[:-4]
            archive_type = 2
        elif filename.lower().endswith(".exe"):
            extract_dir = dl_path / filename[:-4]
            archive_type = 3
        else:
            raise_runtime_error(f"Unknown archive format: {filename}")

        if not extract_dir.exists():
            extract_dir.mkdir(parents=True, exist_ok=True)
            LOGGER.debug("Created directory: %s", extract_dir)

        if archive_type == 1:
            with tarfile.open(dl_path / filename, mode="r:*") as tar:
                tar.extractall(extract_dir)
                LOGGER.debug("Extracted files: %s", ", ".join(tar.getnames()))
        elif archive_type == 2:
            with zipfile.ZipFile(dl_path / filename, mode="r") as driver_zipfile:
                driver_zipfile.extractall(extract_dir)
                # TODO: Get filenames and log debug
        elif archive_type == 3:
            shutil.copy2(dl_path / filename, extract_dir / filename)

        actual_driver_filename = None

        # TODO: Clean up
        for root, _, files in os.walk(extract_dir):
            for curr_file in files:
                if curr_file in driver_filename:
                    actual_driver_filename = Path(root) / curr_file
                    break

        if not actual_driver_filename:
            LOGGER.warning("Cannot locate binary %s from the archive", driver_filename)
            return None

        if not self.link_path:
            return (actual_driver_filename, None)

        if self.os_name in ["mac", "linux"]:
            symlink_src = actual_driver_filename
            symlink_target = self.link_path / driver_filename
            if symlink_target.is_symlink() or symlink_target.exists():
                if symlink_src.samefile(symlink_target):
                    LOGGER.info("Symlink already exists: %s -> %s", symlink_target, symlink_src)
                    return (symlink_src, symlink_target)

                LOGGER.warning("Symlink target %s already exists and will be overwritten.", symlink_target)
                os.unlink(symlink_target)

            symlink_target.symlink_to(symlink_src)
            LOGGER.info("Created symlink: %s -> %s", symlink_target, symlink_src)
            try:
                symlink_stat = os.stat(symlink_src)
                os.chmod(symlink_src, symlink_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except:
                pass
                # TODO: add error handling
            return (symlink_src, symlink_target)

        # self.os_name == 'win':
        src_file = actual_driver_filename
        dest_file = self.link_path / actual_driver_filename.name

        try:
            if dest_file.is_file():
                LOGGER.info("File %s already exists and will be overwritten.", dest_file)
        except OSError:
            pass
        shutil.copy2(src_file, dest_file)
        try:
            dest_stat = os.stat(dest_file)
            os.chmod(dest_file, dest_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except:
            pass
            # TODO: add error handling

        return (src_file, dest_file)
