#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009 Christopher Lenz
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from distutils.cmd import Command
import doctest
from glob import glob
import os
import sys
try:
    from setuptools import setup, find_packages
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False
import sys


setup(
    name = 'CouchDB+Schematics',
    version = '0.1beta',
    description = 'Python library for working with CouchDB w/ Schematics Mapping & Validation',
    long_description = \
"""This is a Python library for CouchDB. It provides a convenient high level
interface for the CouchDB server.""",
    license = 'BSD',
    url = 'https://github.com/ryanolson/couchdb-python-schematics',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages = ['couchdb', 'couchdb.tools', 'couchdb.tests'],

    dependency_links = [
        'git+https://github.com/ryanolson/schematics.git/tarball/master.tar.gz#egg=schematics-0.5.1alpha'
    ],

    install_requires = [
        'simplejson',
        'schematics>=0.5.1alpha'
    ]
)
