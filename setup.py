# -*- coding: utf-8 -*-
"""
    Flask-Bitmapist Setup
    ~~~~~~~~~~~~~~~~~~~~~
    setup.py for Flask-Bitmapist

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def get_requirements(suffix=''):
    with open('requirements%s.txt' % suffix) as f:
        rv = f.read().splitlines()
    return rv


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


setup(
    name='Flask-Bitmapist',
    version='0.1.0',
    url='http://github.com/cuttlesoft/flask-bitmapist',
    download_url='https://github.com/cuttlesoft/flask-bitmapist/tarball/0.1.0',
    license='MIT',
    author='Cuttlesoft, LLC',
    author_email='engineering@cuttlesoft.com',
    description='Flask extension that creates a simple interface to Bitmapist analytics library',
    long_description=open('README.md').read() + '\n\n' + open('HISTORY.rst').read(),
    packages=find_packages(),
    keywords=['Flask', 'Bitmapist'],
    py_modules=['flask_bitmapist'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'bitmapist>=3.97'
    ],
    tests_require=get_requirements('-dev'),
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
