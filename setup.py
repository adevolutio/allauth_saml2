#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from allauth_saml2/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("allauth_saml2", "__init__.py")
readme = open('README.rst').read()
requirements = open('requirements.txt').readlines()

setup(
    name='allauth_saml2',
    version=version,
    description="""Django- AllAuth Saml2 provider""",
    long_description=readme,
    author='David Vaz',
    author_email='dvaz@evolutio.pt',
    url='https://github.com/davidmgvaz/allauth_saml2',
    packages=[
        'allauth_saml2',
    ],
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='allauth_saml2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)
