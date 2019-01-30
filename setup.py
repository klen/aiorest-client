#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import re

from setuptools import setup


def _read(fname):
    with open(fname) as f:
        return f.read()


_readme = _read('README.rst')
_history = _read('HISTORY.rst')

_meta = _read('aiorest_client.py')
_license = re.search(r'^__license__\s*=\s*"(.*)"', _meta, re.M).group(1)
_version = re.search(r'^__version__\s*=\s*"(.*)"', _meta, re.M).group(1)
_author = re.search(r'^__author__\s*=\s*"(.*)"', _meta, re.M).group(1)
_author_email = re.search(r'^__author_email__\s*=\s*"(.*)"', _meta, re.M).group(1)

setup(
    author="Kirill Klenov",
    author_email='horneds@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A helper to call REST API from aiohttp",
    license="MIT license",
    long_description=_readme + '\n\n' + _history,
    include_package_data=True,
    keywords='aiorest_client',
    name='aiorest_client',
    py_modules=['aioauth_client'],
    url='https://github.com/klen/aiorest_client',
    version='0.1.0',
    zip_safe=False,
    install_requires=[
        l for l in _read('requirements.txt').split('\n') if l and not l.startswith('#')
    ],
)
