# -*- coding: utf-8 -*-

from .base import WebDriverManagerBase
from .chrome import ChromeDriverManager
from .gecko import GeckoDriverManager
from .opera import OperaChromiumDriverManager
from .edge import EdgeDriverManager
from .ie import IEDriverManager
from .edgechromium import EdgeChromiumDriverManager

from ._version import get_versions

AVAILABLE_DRIVERS = {
    "chrome": ChromeDriverManager,
    "firefox": GeckoDriverManager,
    "gecko": GeckoDriverManager,
    "mozilla": GeckoDriverManager,
    "opera": OperaChromiumDriverManager,
    "edge": EdgeDriverManager,
    "edgechromium": EdgeChromiumDriverManager,
    "ie": IEDriverManager,
}

__all__ = [
    "WebDriverManagerBase",
    "ChromeDriverManager",
    "GeckoDriverManager",
    "OperaChromiumDriverManager",
    "EdgeDriverManager",
    "IEDriverManager",
    "EdgeChromiumDriverManager",
    "get_version",
    "AVAILABLE_DRIVERS",
]

__version__ = get_versions()["version"]


def get_version():
    return get_versions()["version"]
