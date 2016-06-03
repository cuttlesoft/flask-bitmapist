# -*- coding: utf-8 -*-
"""
    Flask-Bitmapist Setup
    ~~~~~~~~~~~~~~~~~~~~~
    setup.py for Flask-Bitmapist

    :copyright: (c) 2016 by Frank Valcarcel.
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup


setup(
    name='Flask-Bitmapist',
    version='0.1.0',
    url='http://github.com/cuttlesoft/flask-bitmapist',
    download_url='https://github.com/cuttlesoft/flask-bitmapist/tarball/0.1.0',
    license='MIT',
    author='Frank Valcarcel',
    author_email='frank@cuttlesoft.com',
    description='Flask extension that creates a simple interface to Bitmapist analytics library',
    long_description=open('README.md').read() + '\n\n' + open('HISTORY.rst').read(),
    keywords=['Flask', 'Bitmapist'],
    py_modules=['flask_bitmapist'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'bitmapist>=3.97'
    ],
    test_suite="tests",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules']
)
