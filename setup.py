# -*- coding: utf-8 -*-
"""
    Flask-Bitmapist Setup
    ~~~~~~~~~~~~~~~~~~~~~
    setup.py for Flask-Bitmapist

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import ast
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand



def get_requirements(suffix=''):
    with open('requirements%s.txt' % suffix) as f:
        rv = f.read().splitlines()
    return rv


def get_version():
    _version_re = re.compile(r'__version__\s+=\s+(.*)')

    with open('flask_bitmapist/__init__.py', 'rb') as f:
        version = str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))

    return version


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '-xrs',
            '--cov', 'flask_bitmapist',
            '--cov-report', 'term-missing',
            '--pep8',
            '--flakes',
            '--cache-clear'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

_version = get_version()


setup(
    name='Flask-Bitmapist',
    version=_version,
    url='http://github.com/cuttlesoft/flask-bitmapist',
    download_url='https://github.com/cuttlesoft/flask-bitmapist/tarball/' + _version,
    license='MIT',
    author='Cuttlesoft, LLC',
    author_email='engineering@cuttlesoft.com',
    description='Flask extension that creates a simple interface to Bitmapist analytics library',
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    packages=find_packages(),
    keywords=['Flask', 'Bitmapist'],
    py_modules=['flask_bitmapist'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'bitmapist>=3.97'
    ],
    tests_require=get_requirements('-test'),
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules']
)
