#!/usr/bin/env python3

from setuptools import setup

setup(
    name='zenoh',
    version='0.1.0',
    packages=['zenoh', ],
    author='kydos',
    description="Python client API for zenoh",
    long_description='README.md',
    long_description_content_type="text/markdown",
    url='https://github.com/atolab/zenoh-python',
    classifiers=[
        "Programming Language :: Python :: 3",        
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)',        
        "Operating System :: OS Independent"]
    )
