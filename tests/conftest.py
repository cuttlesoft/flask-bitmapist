# -*- coding: utf-8 -*-

import pytest
import redis

from flask import Flask
# from flask_login import LoginManager
from flask_bitmapist import FlaskBitmapist


@pytest.fixture
def app(request):
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'
    app.config['TESTING'] = True
    # app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6379'
    app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6399'
    app.config['SECRET_KEY'] = 'verysecret'
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    return app


@pytest.fixture
def config(app):
    return app.config


@pytest.fixture
def bitmap(request, app):
    bitmap = FlaskBitmapist(app)
    return bitmap


@pytest.yield_fixture
def client(app):
    """Flask test client. An instance of :class:`flask.testing.TestClient` by default."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def client_class(request, client):
    """Uses to set a ``client`` class attribute to current Flask test client::
        @pytest.mark.usefixtures('client_class')
        class TestView:
            def login(self, email, password):
                credentials = {'email': email, 'password': password}
                return self.client.post(url_for('login'), data=credentials)
            def test_login(self):
                assert self.login('vital@example.com', 'pass').status_code == 200
    """
    if request.cls is not None:
        request.cls.client = client


@pytest.fixture
def request_context(request, app):
    return app.test_request_context()


# REDIS (a la Bitmapist)


@pytest.fixture(scope='session', autouse=True)
def setup_redis_for_bitmapist():
    from bitmapist import SYSTEMS

    SYSTEMS['default'] = redis.Redis(host='localhost', port=6399)
    SYSTEMS['default_copy'] = redis.Redis(host='localhost', port=6399)


@pytest.fixture(autouse=True)
def clean_redis():
    cli = redis.Redis(host='localhost', port=6399)
    keys = cli.keys('trackist_*')
    if len(keys) > 0:
        cli.delete(*keys)
