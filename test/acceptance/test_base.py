# pylint: disable=attribute-defined-outside-init
import sys

from .tools import SRC_ROOT, ExplicitBaseTest

sys.path.append(SRC_ROOT)
import webdrivermanager  # noqa: E402 I001


class GeneralWebDriverManagerTests(ExplicitBaseTest):
    DRIVER_MANAGER = webdrivermanager.WebDriverManagerBase

    def test_available_drivers(self):
        self.assertIsInstance(webdrivermanager.AVAILABLE_DRIVERS, dict, "available_drivers doesnt seem to be exported correctly")
        self.assertIsNotNone(webdrivermanager.AVAILABLE_DRIVERS, "No exported drivers found")
        self.assertGreater(len(webdrivermanager.AVAILABLE_DRIVERS), 1, "Not enough drivers found")
