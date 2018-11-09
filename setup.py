#!/usr/bin/env python3

from setuptools import setup
import os  

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='zenoh',
    version='0.1.2',
    packages=['zenoh', ],
    author='kydos',
    description="Python client API for zenoh",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url='https://github.com/atolab/zenoh-python',
    classifiers=[
        "Programming Language :: Python :: 3",        
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: System :: Networking",
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)',        
        "Operating System :: OS Independent"]
    )
