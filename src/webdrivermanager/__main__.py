# -*- coding: utf-8 -*-

import os
import sys
import argparse
from requests import ConnectionError

from ._version import get_versions
from webdrivermanager import AVAILABLE_DRIVERS as DOWNLOADERS


OS_NAMES = ["mac", "win", "linux"]
BITNESS = ["32", "64"]


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="Tool for downloading and installing WebDriver binaries. Version: {get_versions()['version']}",
    )
    parser.add_argument(
        "browser",
        help=f"Browser to download the corresponding WebDriver binary.  Valid values are: {' '.join(DOWNLOADERS.keys())}. Optionally specify a version number of the WebDriver binary as follows: 'browser:version' e.g. 'chrome:2.39'.  If no version number is specified, the latest available version of the WebDriver binary will be downloaded.",
        nargs="+",
    )
    parser.add_argument(
        "--downloadpath",
        "-d",
        action="store",
        dest="downloadpath",
        metavar="F",
        default=None,
        help="Where to download the webdriver binaries",
    )
    parser.add_argument(
        "--linkpath",
        "-l",
        action="store",
        dest="linkpath",
        metavar="F",
        default=None,
        help='Where to link the webdriver binary to. Set to "AUTO" if you need some intelligense to decide where to place the final webdriver binary. If set to "SKIP", no link/copy done.',
    )
    parser.add_argument(
        "--os",
        "-o",
        action="store",
        dest="os_name",
        choices=OS_NAMES,
        metavar="OSNAME",
        default=None,
        help=f"Overrides os detection with given os name. Values: {' '.join(OS_NAMES)}",
    )
    parser.add_argument(
        "--bitness",
        "-b",
        action="store",
        dest="bitness",
        choices=BITNESS,
        metavar="BITS",
        default=None,
        help=f"Overrides bitness detection with given value. Values: {' '.join(BITNESS)}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_versions()['version']}")
    return parser.parse_args()


def main():
    args = parse_command_line()
    for browser in args.browser:

        if ":" in browser:
            browser, version = browser.split(":")
        else:
            version = "compatible"

        if browser.lower() in DOWNLOADERS.keys():
            print(f'Downloading WebDriver for browser: "{browser}"')
            downloader = DOWNLOADERS[browser](args.downloadpath, args.linkpath, args.os_name, args.bitness)

            try:
                extracted_binary, link = downloader.download_and_install(version)
            except ConnectionError:
                print("Unable to download webdriver's at this time due to network connectivity error")
                sys.exit(1)

            print(f'Driver binary downloaded to: "{extracted_binary}"')
            if link:
                if link.is_symlink():
                    print(f"Symlink created: {link}")
                else:
                    print(f"Driver copied to: {link}")
                link_path = link.parent
                if str(link_path) not in os.environ["PATH"].split(os.pathsep):
                    print(f'WARNING: Path "{link_path}" is not in the PATH environment variable.')
            else:
                print("Linking webdriver skipped")
        else:
            print('Unrecognized browser: "{browser}".  Ignoring...')
        print("")


if __name__ == "__main__":
    main()
