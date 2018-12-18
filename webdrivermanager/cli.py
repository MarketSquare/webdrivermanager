# -*- coding: utf-8 -*-

import argparse
import os
import os.path

from webdrivermanager import ChromeDriverManager, GeckoDriverManager, OperaChromiumDriverManager, EdgeDriverManager


os_names = ["mac","win","linux"]

downloaders = {
    "chrome": ChromeDriverManager,
    "firefox": GeckoDriverManager,
    "gecko": GeckoDriverManager,
    "mozilla": GeckoDriverManager,
    "opera": OperaChromiumDriverManager,
    "edge": EdgeDriverManager,
}


def parse_command_line():
    parser = argparse.ArgumentParser(
        description=u"Tool for downloading and installing WebDriver binaries."
    )
    parser.add_argument(
        u"browser",
        help=(u"Browser to download the corresponding WebDriver binary.  Valid values are: {0}.  "
              u"Optionally specify a version number of the WebDriver binary as follows: \"browser:version\" "
              u"e.g. \"chrome:2.39\".  If no version number is specified, the latest available version of the "
              u"WebDriver binary will be downloaded.").format(
            ", ".join(['"' + browser + '"' for browser in downloaders.keys()])
        ),
        nargs="+",
    )
    parser.add_argument('--downloadpath', '-d', action='store', dest='downloadpath', metavar='F', default=None, help='Where to download the webdriver binaries')
    parser.add_argument('--linkpath', '-l', action='store', dest='linkpath', metavar='F', default=None, help='Where to link the webdriver binary to.')
    parser.add_argument('--os', '-o', action='store', dest='os_name', choices=os_names, metavar='OSNAME', default=None, help='Overrides os detection with given os name. Values: {0}'.format(", ".join(os_names)))
    return parser.parse_args()


def main():
    args = parse_command_line()
    for browser in args.browser:
        if ":" in browser:
            browser, version = browser.split(":")
        else:
            version = "latest"
        if browser.lower() in downloaders.keys():
            print("Downloading WebDriver for browser: '{0}'".format(browser))
            downloader = downloaders[browser](args.downloadpath, args.linkpath, args.os_name)
            extracted_binary, link = downloader.download_and_install(version)
            print("Driver binary downloaded to: {0}".format(extracted_binary))
            if os.path.islink(link):
                print("Symlink created: {0}".format(link))
            else:
                print("Driver copied to: {0}".format(link))

            link_path = os.path.split(link)[0]
            if link_path not in os.environ['PATH'].split(os.pathsep):
                print("WARNING: Path '{0}' is not in the PATH environment variable.".format(link_path))
        else:
            print("Unrecognized browser: '{0}'.  Ignoring...".format(browser))
        print("")


if __name__ == "__main__":
    main()
