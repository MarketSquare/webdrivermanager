"""Unit tests for version.py"""
import unittest
from webdrivermanager.version import get_version, VERSION


class TestVersion(unittest.TestCase):
    """Unit Tests for version.py"""

    def test_get_version(self):
        """This test verifies that the version stored in VERSION is returned when get_version
        is called."""
        result = get_version()
        self.assertEqual(result, VERSION)
