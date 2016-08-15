# -*- coding: utf-8 -*-
"""
    flask_bitmapist.core
    ~~~~~~~~~~~~~~~~~~~~
    Implements the core integration from flask to bitmapist

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import bitmapist as _bitmapist

from .utils import _get_redis_connection
from .views import bitmapist_bp


class FlaskBitmapist(object):
    """
    This class is used to initialize the Flask Bitmapist extension
    """

    app = None
    redis_url = None
    SYSTEMS = _bitmapist.SYSTEMS
    TRACK_HOURLY = _bitmapist.TRACK_HOURLY

    def __init__(self, app=None, config=None, **opts):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("config must be an instance of dict or None")
        self.config = config

        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        "This is used to initialize bitmapist with your app object"
        self.app = app
        self.redis_url = app.config.get('BITMAPIST_REDIS_URL', 'redis://localhost:6379')

        if self.redis_url not in _bitmapist.SYSTEMS.values():
            host, port = _get_redis_connection(self.redis_url)
            _bitmapist.setup_redis(
                app.config.get('BITMAPIST_REDIS_SYSTEM', 'default'),
                host,
                port)

        _bitmapist.TRACK_HOURLY = app.config.get('BITMAPIST_TRACK_HOURLY', False)

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['bitmapist'] = self

        if not app.config.get('DISABLE_BLUEPRINT'):
            app.register_blueprint(bitmapist_bp)
