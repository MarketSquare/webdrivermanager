from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory

NO_FILE = "Actual webdriver artifact is not available"
NO_LINK_FILE = "Link to webdriver artifact is not available"
SRC_ROOT = str(Path(__file__).absolute().parent.parent.parent / "src")


class AutomaticBaseTest(TestCase):
    DRIVER_MANAGER = None

    def setUp(self):
        self.assertIsNot(self.DRIVER_MANAGER, None, "DRIVER_MANAGER should not be none")


class ExplicitBaseTest(TestCase):
    DRIVER_MANAGER = None

    def setUp(self):
        self.assertIsNot(self.DRIVER_MANAGER, None, "DRIVER_MANAGER should not be none")
        self.temp_dir = TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_link_dir(self):
        link_path = Path(self.temp_dir.name) / "bin"
        link_path.mkdir(parents=True, exist_ok=True)
        return link_path
