import unittest
from flask import Flask, request
from flask_bitmapist import FlaskBitmapist


class DefaultConfig(object):
    TESTING = True
    BITMAPIST_REDIS_URL = 'redis://localhost:6379'


class FlaskBitmapistBaseTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(DefaultConfig)
        self.bitmap = FlaskBitmapist(self.app)

    def test_redis_url(self):
        self.assertEqual(self.bitmap.redis_url, self.app.config['BITMAPIST_REDIS_URL'])

    def test_redis_system_name(self):
        assert 'default' in self.bitmap.SYSTEMS.keys()

    def test_track_hourly(self):
        assert self.bitmap.TRACK_HOURLY is False


class FlaskBitmapistBlueprintTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(DefaultConfig)
        self.bitmap = FlaskBitmapist(self.app)

    def test_index(self):
        with self.app.test_request_context('/bitmapist/'):
            self.assertEquals(request.endpoint, 'bitmapist.index')

    def test_events(self):
        with self.app.test_request_context('/bitmapist/events'):
            self.assertEquals(request.endpoint, 'bitmapist.events')
