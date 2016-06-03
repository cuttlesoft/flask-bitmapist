import unittest
from mock import MagicMock
from flask_bitmapist import FlaskBitmapist

app = MagicMock()
app.config = {}
app.config['TESTING'] = True
app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6379'


class FlaskBitmapistTest(unittest.TestCase):

    def setUp(self):
        self.bitmap = FlaskBitmapist(app)

    def test_redis_url(self):
        self.assertEqual(self.bitmap.redis_url, app.config['BITMAPIST_REDIS_URL'])
