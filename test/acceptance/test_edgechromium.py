import sys
from flaky import flaky
from unittest import skipUnless
from .tools import SRC_ROOT, AutomaticBaseTest, ExplicitBaseTest, NO_FILE, NO_LINK_FILE

sys.path.append(SRC_ROOT)
import webdrivermanager  # noqa: E402 I001


class EdgeChromiumDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeChromiumDriverManager

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER()
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(filename.is_file(), NO_FILE)

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER()
        driver_link_target, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(driver_binary.is_file(), NO_FILE)
        self.assertTrue(driver_link_target.is_file(), NO_LINK_FILE)


class EdgeChromiumDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeChromiumDriverManager

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(filename.is_file(), NO_FILE)

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path)
        driver_link_target, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(driver_binary.is_file(), NO_FILE)
        self.assertTrue(driver_link_target.is_file(), NO_LINK_FILE)
