

``webdrivermanager``
=======================

Python module to facilitate downloading and deploying `WebDriver <https://www.w3.org/TR/webdriver/>`_ binaries.  The classes in this module can be used to automatically search for and download the latest version (or a specific version) of a WebDriver binary and then extract it and place it by copying or symlinking it to the location where Selenium or other tools should be able to find it then.


Installation
------------

This module is available on the Python Package Index (PyPI) and can be installed as follows:

``pip install webdrivermanager``


Dependencies
------------

This module is dependent on the following additional packages:

- `requests <https://pypi.org/project/requests/>`_
- `tqdm <https://pypi.org/project/tqdm/>`_
- `BeautifulSoup4 <https://pypi.org/project/beautifulsoup4/>`_
- `appdirs <https://pypi.org/project/appdirs/>`_


Classes
-------

The following classes are available:

- ``ChromeDriverManager`` for downloading and installing `chromedriver <https://sites.google.com/a/chromium.org/chromedriver/downloads>`_ (for Google Chrome).
- ``GeckoDriverManager`` for downloading and installing `geckodriver <https://github.com/mozilla/geckodriver>`_ (for Mozilla Firefox).
- ``OperaChromiumDriverManager`` for downloading and installing `operadriver <https://github.com/operasoftware/operachromiumdriver>`_ (for Chromium based Opera browsers).
- ``EdgeDriverManager`` for downloading and installing `edgedriver <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>`_ (for Microsoft Edge).
- ``EdgeChromiumDriverManager`` for downloading and installing Edge Chromium based webdrivers
- ``IeDriverManager`` for downloading and installing Internet Explorer based webdrivers


Status
------

Currently being developed/tested using Python 2.7.15 and 3.7  on macOS, Windows & Linux


Example module usage
--------------------

Example::

   >>> from webdrivermanager import GeckoDriverManager
   >>> gdd = GeckoDriverManager()
   >>> gdd.download_and_install()
   1524kb [00:00, 1631.24kb/s]
   ('/Users/rasjani/webdriver/geckodriver-v0.20.1-macos/geckodriver', '/Users/rasjani/bin/geckodriver')
   >>> gdd.download_and_install("v0.20.0")
   1501kb [00:02, 678.92kb/s]
   Symlink /Users/rasjani/bin/geckodriver already exists and will be overwritten.
   ('/Users/rasjani/webdriver/geckodriver-v0.20.0-macos/geckodriver', '/Users/rasjani/bin/geckodriver')
   >>> gdd.download_and_install()
   Symlink /Users/rasjani/bin/geckodriver already exists and will be overwritten.
   ('/Users/rasjani/webdriver/geckodriver-v0.20.1-macos/geckodriver', '/Users/rasjani/bin/geckodriver')
   >>>


Command line tool
-----------------

There is a command-line tool that is also available.  After installing the package, it can be used as follows (Windows example)::

   > webdrivermanager chrome:2.38 firefox opera:v.2.35
   Downloading WebDriver for browser: 'chrome'
   3300kb [00:00, 11216.38kb/s]
   Driver binary downloaded to: C:\Users\rasjani\webdriver\chrome\2.38\2.38%2Fchromedriver_win32\chromedriver.exe
   Driver copied to: C:\Users\rasjani\bin\chromedriver.exe

   Downloading WebDriver for browser: 'firefox'
   3031kb [00:01, 2253.64kb/s]
   Driver binary downloaded to: C:\Users\rasjani\webdriver\gecko\v0.20.1\geckodriver-v0.20.1-win64\geckodriver.exe
   Driver copied to: C:\Users\rasjani\bin\geckodriver.exe

   Downloading WebDriver for browser: 'opera'
   3548kb [00:02, 1239.02kb/s]
   Driver binary downloaded to: C:\Users\rasjani\webdriver\operachromium\v.2.35\operadriver_win64\operadriver_win64\operadriver.exe
   Driver copied to: C:\Users\rasjani\bin\operadriver.exe

   WARNING: Path 'C:\Users\rasjani\bin' is not in the PATH environment variable.

In the above example, a version was specified for Chrome and Opera while no version was specified for Firefox so the latest version of ``geckodriver`` was implicitly downloaded.

Command line options
--------------------

    usage: webdrivermanager [-h] [--downloadpath F] [--linkpath F] [--os OSNAME]
              browser [browser ...]

        Tool for downloading and installing WebDriver binaries.

	positional arguments:
	   browser               Browser to download the corresponding WebDriver
				 binary. Valid values are: chrome, firefox, gecko,
				 mozilla, opera, edge. Optionally specify a version
				 number of the WebDriver binary as follows:
				 'browser:version' e.g. 'chrome:2.39'. If no version
				 number is specified, the latest available version of
				 the WebDriver binary will be downloaded.

        optional arguments:
            -h, --help            show this help message and exit
            --downloadpath F, -d F
                                  Where to download the webdriver binaries
            --linkpath F, -l F    Where to link the webdriver binary to. Set to "AUTO"
                                  if you need some intelligence to decice where to place
                                  the final webdriver binary
            --linkpath F, -l F    Where to link the webdriver binary to. Set to "AUTO"
                                  if you need some intelligense to decide where to place
                                  the final webdriver binary. If set to "SKIP", no
                                  link/copy done
            --os OSNAME, -o OSNAME
                                  Overrides os detection with given os name


Do note that `--downloadpath`/`-d` flag location is used for storing the whole downloaded and then `--linkpath`/`-l` path location is where the final binary is either symlinled or copied to.  Linkpath should be the directory you either already have in PATH or you should place there since tools using these webdrivers usually locate the appropriate webdriver binary from PATH environment variable.

If linkpath flag is set to *AUTO*, tool will iterate over your current PATH environment variable and tries to find the first writeable directory within it and place the copy or symlink into it. If linkpath is set to *SKIP*, only download is done, linking/copying is skipped.

License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.

Consult the license terms of the providers of the WebDriver downloads prior to downloading / using the WebDrivers.
