# -*- coding: utf-8 -*-
"""
    flask_bitmapist.utils
    ~~~~~~~~~~~~~~~~~~~~~
    Generic utility functions.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

from urlparse import urlparse


def _get_redis_connection(redis_url=None):
    url = urlparse(redis_url)
    return url.hostname, url.port
