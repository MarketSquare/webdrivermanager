"""Unit tests for version.py"""
import unittest
from webdrivermanager.version import get_version, VERSION


class TestVersion(unittest.TestCase):
    """Unit Tests for version.py"""

    def test_get_version(self):
        result = get_version()
        self.assertEqual(result, VERSION)
