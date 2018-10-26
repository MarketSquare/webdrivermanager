from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='webdrivermanager',
      version='0.1.dev2',
      description='Module for facilitating download and deploy of WebDriver binaries.',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Libraries",
            "Topic :: Software Development :: Quality Assurance",
            "Topic :: Software Development :: Testing",
            "Topic :: Utilities",
      ],
      url='https://github.com/rasjani/webdrivermanager',
      author='Jani Mikkonen'
      author_email='jani.mikkonen@gmail.com',
      license='MIT',
      packages=['webdrivermanager'],
      install_requires=['requests', 'tqdm'],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'webdrivermanager = webdrivermanager.cli:main',
          ],
      })
