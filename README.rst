``webdriverdownloader``
=======================

Python module to facilitate downloading and deploying `WebDriver <https://www.w3.org/TR/webdriver/>`_ binaries.  The classes in this module can be used to automatically search for and download the latest version (or a specific version) of a WebDriver binary (will download to ``$HOME/webdriver`` or ``/usr/local/webdriver`` if run with ``sudo``), extract the binary from the downloaded archive and create a symlink in either ``/usr/local/bin`` (if run with ``sudo``) or ``$HOME/bin``.

Status
------

Currently, base functionality is mostly in place for download and deploying for `geckodriver <https://github.com/mozilla/geckodriver>`_.

Currently being developed/tested using Python 3.6.5 on macOS.

Example Usage
-------------

Example::

   >>> from webdriverdownloader import GeckoDriverDownloader
   >>> gdd = GeckoDriverDownloader()
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


TODOs
-----

- Finish up base functionality for ``GeckoDriverDownloader`` class.
- Test on Linux
- Test on Windows
- Work on `ChromeDriver <https://sites.google.com/a/chromium.org/chromedriver/downloads>`_
- Work on `OperaChromiumDriver <https://github.com/operasoftware/operachromiumdriver>`_
- Write a command-line wrapper
- Test with Python 2

License
-------

This is released under an MIT license.  See the ``LICENSE`` file in this repository for more information.
