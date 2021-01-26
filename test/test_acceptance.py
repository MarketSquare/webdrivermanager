# pylint: disable=attribute-defined-outside-init
import sys
import tarfile  # noqa: E402
from os import mkdir
from os.path import join, isfile, abspath, dirname
from unittest import TestCase
from unittest import skipUnless
from unittest import main as run_tests
from flaky import flaky

from xmlrunner import XMLTestRunner

CWD = abspath(dirname(__file__))  # noqa: I003
sys.path.append(join(CWD, '..'))
import webdrivermanager  # noqa: E402 I001


try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory   # pylint: disable=import-error


class AutomaticBaseTest(TestCase):
    DRIVER_MANAGER = None

    def setUp(self):
        self.assertIsNot(self.DRIVER_MANAGER, None, 'DRIVER_MANAGER should not be none')


class ExplicitBaseTest(TestCase):
    DRIVER_MANAGER = None

    def setUp(self):
        self.assertIsNot(self.DRIVER_MANAGER, None, 'DRIVER_MANAGER should not be none')
        self.temp_dir = TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_link_dir(self):
        link_path = join(self.temp_dir.name, 'bin')
        mkdir(link_path)
        return link_path


class GeneralWebDriverManagerTests(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.WebDriverManagerBase

    def test_available_drivers(self):
        self.assertTrue(isinstance(webdrivermanager.AVAILABLE_DRIVERS, dict), 'available_drivers doesnt seem to be exported correctly')


class ChromeDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.ChromeDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER()
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER()
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class ChromeDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.ChromeDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path)
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class GeckoDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.GeckoDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER()
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER()
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class GeckoDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.GeckoDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path)
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class OperaChromiumDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.OperaChromiumDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER()
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER()
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class OperaChromiumDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.OperaChromiumDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path)
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class EdgeDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(os_name='win')
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER(os_name='win')
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class EdgeDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, os_name='win')
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path, os_name='win')
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class IEDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.IEDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(os_name='win', bitness="64")
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER(os_name='win', bitness="64")
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class IEDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.IEDriverManager

    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, os_name='win', bitness="64")
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path, os_name='win', bitness="64")
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class EdgeChromiumDriverManagerTestsWithAutomaticLocations(AutomaticBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeChromiumDriverManager

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER()
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download_and_install(self):
        self.instance = self.DRIVER_MANAGER()
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


class EdgeChromiumDriverManagerTestsWithExplicitLocations(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.EdgeChromiumDriverManager

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download(self):
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name)
        filename = self.instance.download(show_progress_bar=False)
        self.assertTrue(isfile(filename), 'Downloading and saving seems to have failed')

    @skipUnless(sys.platform.startswith("win"), "No EdgeChromium on this platform")
    @flaky
    def test_download_and_install(self):
        link_path = self.make_link_dir()
        self.instance = self.DRIVER_MANAGER(download_root=self.temp_dir.name, link_path=link_path)
        driver_directory, driver_binary = self.instance.download_and_install(show_progress_bar=False)
        self.assertTrue(isfile(driver_binary), 'Downloading and saving seems to have failed')
        self.assertTrue(isfile(driver_directory), 'Downloading and saving seems to have failed')


if __name__ == '__main__':
    with open('acceptance_tests.xml', 'wb') as output:
        run_tests(
            testRunner=XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)
