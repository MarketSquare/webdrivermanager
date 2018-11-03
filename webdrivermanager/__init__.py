# -*- coding: utf-8 -*-

try:
    from webdrivermanager import ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager, EdgeDriverManager
except ImportError:
    from .webdrivermanager import ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager, EdgeDriverManager

__all__ = ['ChromeDriverManager', 'GeckoDriverManager', 'OperaChromiumDriverManager', 'EdgeDriverManager']
