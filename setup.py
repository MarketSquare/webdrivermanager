# -*- coding: utf-8 -*-

from codecs import open
from os.path import join, abspath, dirname

from setuptools import setup
import versioneer

CWD = abspath(dirname(__file__))
PACKAGE_NAME = "webdrivermanager"

# Get the long description from the README file
with open(join(CWD, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

# Get version
CWD = abspath(dirname(__file__))

with open(join(CWD, "requirements.txt"), encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

CLASSIFIERS = """
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: Information Technology
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Software Development :: Libraries
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Topic :: Utilities
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Operating System :: POSIX :: Other
""".strip().splitlines()

setup(
    name=PACKAGE_NAME,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Module for facilitating download and deploy of WebDriver binaries.",
    long_description=long_description,
    classifiers=CLASSIFIERS,
    url="https://github.com/rasjani/webdrivermanager",
    author="Jani Mikkonen",
    author_email="jani.mikkonen@gmail.com",
    license="MIT",
    packages=[PACKAGE_NAME],
    package_dir={"": "src"},
    install_requires=REQUIREMENTS,
    include_package_data=True,
    platforms="any",
    keywords="webdriver chromedriver geckodriver edgechromiumdriver selenium",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "webdrivermanager = webdrivermanager.__main__:main",
        ],
    },
)
