# -*- coding: utf-8 -*-

import os
import sys
import os.path
import argparse
from requests import ConnectionError

try:
    from ._version import get_versions
except ImportError:
    from _version import get_versions
try:
    from .webdrivermanager import AVAILABLE_DRIVERS as DOWNLOADERS
except ImportError:
    from webdrivermanager import AVAILABLE_DRIVERS as DOWNLOADERS


OS_NAMES = ['mac', 'win', 'linux']
BITNESS = ["32", "64"]


def parse_command_line():
    parser = argparse.ArgumentParser(
        description='Tool for downloading and installing WebDriver binaries. Version: {}'.format(get_versions()["version"]),
    )
    parser.add_argument('browser', help='Browser to download the corresponding WebDriver binary.  Valid values are: {0}. Optionally specify a version number of the WebDriver binary as follows: \'browser:version\' e.g. \'chrome:2.39\'.  If no version number is specified, the latest available version of the WebDriver binary will be downloaded.'.format(', '.join(DOWNLOADERS.keys())), nargs='+')
    parser.add_argument('--downloadpath', '-d', action='store', dest='downloadpath', metavar='F', default=None, help='Where to download the webdriver binaries')
    parser.add_argument('--linkpath', '-l', action='store', dest='linkpath', metavar='F', default=None, help='Where to link the webdriver binary to. Set to "AUTO" if you need some intelligense to decide where to place the final webdriver binary. If set to "SKIP", no link/copy done.')
    parser.add_argument('--os', '-o', action='store', dest='os_name', choices=OS_NAMES, metavar='OSNAME', default=None, help='Overrides os detection with given os name. Values: {0}'.format(', '.join(OS_NAMES)))
    parser.add_argument('--bitness', '-b', action='store', dest='bitness', choices=BITNESS, metavar='BITS', default=None, help='Overrides bitness detection with given value. Values: {0}'.format(', '.join(BITNESS)))
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(get_versions()["version"]))
    return parser.parse_args()


def main():
    args = parse_command_line()
    for browser in args.browser:
        if ':' in browser:
            browser, version = browser.split(':')
        else:
            version = 'latest'
        if browser.lower() in DOWNLOADERS.keys():
            print('Downloading WebDriver for browser: "{0}"'.format(browser))
            downloader = DOWNLOADERS[browser](args.downloadpath, args.linkpath, args.os_name, args.bitness)
            try:
                extracted_binary, link = downloader.download_and_install(version)
            except ConnectionError:
                print("Unable to download webdriver's at this time due to network connectivity error")
                sys.exit(1)
            print('Driver binary downloaded to: "{0}"'.format(extracted_binary))
            if link is not None:
                if os.path.islink(link):
                    print('Symlink created: {0}'.format(link))
                else:
                    print('Driver copied to: {0}'.format(link))
                link_path = os.path.split(link)[0]
                if link_path not in os.environ['PATH'].split(os.pathsep):
                    print('WARNING: Path "{0}" is not in the PATH environment variable.'.format(link_path))
            else:
                print('Linking webdriver skipped')
        else:
            print('Unrecognized browser: "{0}".  Ignoring...'.format(browser))
        print('')


if __name__ == '__main__':
    main()
