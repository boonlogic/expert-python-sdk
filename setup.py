# Setup file for building the package using setuptools.
# From np8's answer on https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944

from setuptools import setup, find_packages

setup(name='myproject', version='1.0', packages=find_packages())
