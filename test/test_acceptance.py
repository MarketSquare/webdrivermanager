
from unittest import TestCase
from unittest import main as run_tests
import sys
from os.path import abspath, join, dirname, isfile
from os import mkdir
CWD = abspath(dirname(__file__))
sys.path.append(join(CWD,".."))
from webdrivermanager import GeckoDriverManager, ChromeDriverManager, OperaChromiumDriverManager
try:
    from tempfile import TemporaryDirectory
except:
    from backports.tempfile import TemporaryDirectory


class  BaseTest(TestCase):
    DRIVER_MANAGER=None
    def setUp(self):
        self.assertIsNot(self.DRIVER_MANAGER, None, "DRIVER_MANAGER should not be none")
        self.temp_dir = TemporaryDirectory()
    def tearDown(self):
        self.temp_dir.cleanup()

    def make_link_dir(self):
        link_path = join(self.temp_dir.name, "bin")
        mkdir(link_path)
        return link_path

class ChromeDriverManagerTests(BaseTest):
    DRIVER_MANAGER=ChromeDriverManager
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), "Downloading and saving seems to have failed")

    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path )
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), "Downloading and saving seems to have failed")
        self.assertTrue(isfile(driver_directory), "Downloading and saving seems to have failed")


class GeckoDriverManagerTests(BaseTest):
    DRIVER_MANAGER=GeckoDriverManager
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), "Downloading and saving seems to have failed")

    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path )
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), "Downloading and saving seems to have failed")
        self.assertTrue(isfile(driver_directory), "Downloading and saving seems to have failed")

class OperaChromiumDriverManagerTests(BaseTest):
    DRIVER_MANAGER=OperaChromiumDriverManager
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), "Downloading and saving seems to have failed")

    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path )
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), "Downloading and saving seems to have failed")
        self.assertTrue(isfile(driver_directory), "Downloading and saving seems to have failed")

if __name__ == '__main__':
    run_tests()


