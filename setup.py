#! /usr/bin/env python3

# Core
from setuptools import setup, find_packages

setup(
    name='canonicalwebteam.gsa',
    version='2.0.1',
    author='Canonical webteam',
    author_email='robin+pypi@canonical.com',
    url='https://github.com/canonicalwebteam/gsa',
    packages=find_packages(),
    description=(
        'A client for communicating with the Google Search Appliance.'
    ),
    long_description=open('README.rst').read(),
    install_requires=[
        "requests>=2.10.0",
        "lxml>=3.3.0"
    ],
)
