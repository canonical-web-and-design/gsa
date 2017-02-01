#! /usr/bin/env python3

# Core
from setuptools import setup

setup(
    name='ubuntudesign.gsa',
    version='1.0.4',
    author='Canonical webteam',
    author_email='robin+pypi@canonical.com',
    url='https://github.com/ubuntudesign/python-gsa',
    packages=[
        'ubuntudesign',
        'ubuntudesign.gsa',
    ],
    description=(
        'A client for communicating with the Google Search Appliance.'
    ),
    long_description=open('README.rst').read(),
    install_requires=[
        "requests>=2.10.0",
        "lxml>=3.3.0"
    ],
)
