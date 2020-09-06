# -*- coding: utf-8 -*-

from .webdrivermanager import WebDriverManagerBase, ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager, EdgeDriverManager, IEDriverManager, EdgeChromiumDriverManager, AVAILABLE_DRIVERS
from ._version import get_versions

__all__ = ['WebDriverManagerBase', 'ChromeDriverManager', 'GeckoDriverManager', 'OperaChromiumDriverManager', 'EdgeDriverManager', 'IEDriverManager', 'EdgeChromiumDriverManager', 'get_version', 'AVAILABLE_DRIVERS']

from ._version import get_versions
__version__ = get_versions()['version']


def get_version():
    return get_versions()["version"]

__version__ = get_version()
