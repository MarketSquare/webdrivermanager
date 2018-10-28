# -*- coding: utf-8 -*-

try:
    from webdrivermanager import ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager
except ImportError:
    from .webdrivermanager import ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager

__all__ = ['ChromeDriverManager', 'GeckoDriverManager', 'OperaChromiumDriverManager']
