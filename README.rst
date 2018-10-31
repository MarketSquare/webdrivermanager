``webdrivermanager``
=======================

Python module to facilitate downloading and deploying `WebDriver <https://www.w3.org/TR/webdriver/>`_ binaries.  The classes in this module can be used to automatically search for and download the latest version (or a specific version) of a WebDriver binary (by default, will download to ``$HOME/webdriver`` or ``/usr/local/webdriver`` if run with ``sudo``. If virtualenv is activated when running webdrivermanager, download is stored within it), extract the binary from the downloaded archive and create a symlink in either ``/usr/local/bin`` (if run with ``sudo``) or ``$HOME/bin``.


This project is a fork of https://github.com/leonidessaguisagjr/webdriverdownloader


Installation
------------

This module is available on the Python Package Index (PyPI) and can be installed as follows:

``pip install webdrivermanager``


Dependencies
------------

This module is dependent on the following additional packages:

- `requests <https://pypi.org/project/requests/>`_
- `tqdm <https://pypi.org/project/tqdm/>`_
- `lxml <https://pypi.org/project/lxml/>`_


Classes
-------

The following classes are available:

- ``ChromeDriverManager`` for downloading and installing `chromedriver <https://sites.google.com/a/chromium.org/chromedriver/downloads>`_ (for Google Chrome).
- ``GeckoDriverManager`` for downloading and installing `geckodriver <https://github.com/mozilla/geckodriver>`_ (for Mozilla Firefox).
- ``OperaChromiumDriverManager`` for downloading and installing `operadriver <https://github.com/operasoftware/operachromiumdriver>`_ (for Chromium based Opera browsers).


Status
------

Currently being developed/tested using Python 2.7.15 and 3.6.5 on macOS and Windows 10.


Example module usage
--------------------

Example::

   >>> from webdrivermanager import GeckoDriverManager
   >>> gdd = GeckoDriverManager()
   >>> gdd.download_and_install()
   1524kb [00:00, 1631.24kb/s]
   ('/Users/lsaguisag/webdriver/geckodriver-v0.20.1-macos/geckodriver', '/Users/lsaguisag/bin/geckodriver')
   >>> gdd.download_and_install("v0.20.0")
   1501kb [00:02, 678.92kb/s]
   Symlink /Users/lsaguisag/bin/geckodriver already exists and will be overwritten.
   ('/Users/lsaguisag/webdriver/geckodriver-v0.20.0-macos/geckodriver', '/Users/lsaguisag/bin/geckodriver')
   >>> gdd.download_and_install()
   Symlink /Users/lsaguisag/bin/geckodriver already exists and will be overwritten.
   ('/Users/lsaguisag/webdriver/geckodriver-v0.20.1-macos/geckodriver', '/Users/lsaguisag/bin/geckodriver')
   >>>


Command line tool
-----------------

There is a command-line tool that is also available.  After installing the package, it can be used as follows (Windows example)::

   > webdrivermanager chrome:2.38 firefox opera:v.2.35
   Downloading WebDriver for browser: 'chrome'
   3300kb [00:00, 11216.38kb/s]
   Driver binary downloaded to: C:\Users\lsaguisag\webdriver\chrome\2.38\2.38%2Fchromedriver_win32\chromedriver.exe
   Driver copied to: C:\Users\lsaguisag\bin\chromedriver.exe

   Downloading WebDriver for browser: 'firefox'
   3031kb [00:01, 2253.64kb/s]
   Driver binary downloaded to: C:\Users\lsaguisag\webdriver\gecko\v0.20.1\geckodriver-v0.20.1-win64\geckodriver.exe
   Driver copied to: C:\Users\lsaguisag\bin\geckodriver.exe

   Downloading WebDriver for browser: 'opera'
   3548kb [00:02, 1239.02kb/s]
   Driver binary downloaded to: C:\Users\lsaguisag\webdriver\operachromium\v.2.35\operadriver_win64\operadriver_win64\operadriver.exe
   Driver copied to: C:\Users\lsaguisag\bin\operadriver.exe

   WARNING: Path 'C:\Users\lsaguisag\bin' is not in the PATH environment variable.

In the above example, a version was specified for Chrome and Opera while no version was specified for Firefox so the latest version of ``geckodriver`` was implicitly downloaded.

Command line options
--------------------

    usage: webdrivermanager [-h] [--downloadpath F] [--linkpath F] browser [browser ...]

    Tool for downloading and installing WebDriver binaries.

    positional arguments:
      browser               Browser to download the corresponding WebDriver
                            binary. Valid values are: "chrome", "firefox",
                            "gecko", "mozilla", "opera". Optionally specify a
                            version number of the WebDriver binary as follows:
                            "browser:version" e.g. "chrome:2.39". If no version
                            number is specified, the latest available version of
                            the WebDriver binary will be downloaded.

    optional arguments:
      -h, --help            show this help message and exit
      --downloadpath F, -d F
                            Where to download the webdriver binaries
      --linkpath F, -l F    Where to link the webdriver binary to. Defaults to


TODOs
-----

- Test on Linux


RELEASES
--------

* 0.2
    * Initial release, support for installing package directly to python virtualenv directory
    * Added support to set install location via --downloadpath and --linkpath options
* 0.3
    * Prevent unnecessary calls to webdriver provides when calculating download urls and paths to store them.
    * various code cleanups
* 0.4
    * Workaround to download firefox & opera webdriver when hitting github api rate limits.
    * Fixed a bug introduced in 0.3: on mac one couldnt download chrome & opera webdriver
    * setup.py fetches requirements from requirements.txt
* 0.4.1
    * bug fix for dependency installation

License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.

Consult the license terms of the providers of the WebDriver downloads prior to downloading / using the WebDrivers.
