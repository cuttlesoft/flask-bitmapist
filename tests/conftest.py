# -*- coding: utf-8 -*-

import pytest
import redis
import os

from flask import Flask
# from flask_login import LoginManager

from flask_bitmapist import FlaskBitmapist
from flask_bitmapist.mixins import Bitmapistable


@pytest.fixture(scope='session')
def app(request):
    app = Flask(__name__)
    app.debug = True
    app.config['TESTING'] = True
    # app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6379'
    app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6399'
    app.config['SECRET_KEY'] = 'secret'
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


# REDIS

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


# SQLALCHEMY

@pytest.fixture
def sqlalchemy_db(app):
    from flask_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(app)
    return db


@pytest.fixture
def sqlalchemy_user(sqlalchemy_db):
    db = sqlalchemy_db

    class User(db.Model, Bitmapistable):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))

    return User


@pytest.fixture
def sqlalchemy(app, request, sqlalchemy_db, sqlalchemy_user):
    db = sqlalchemy_db

    TESTS_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    TESTDB = 'test.sqlite'
    TESTDB_PATH = os.path.join(os.path.join(TESTS_PATH, 'tests/db'), TESTDB)
    TESTDB_URI = 'sqlite:///' + TESTDB_PATH

    app.config['SQLALCHEMY_DATABASE_URI'] = TESTDB_URI
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def teardown():
        db.drop_all()
        os.unlink(TESTDB_PATH)

    # if os.path.exists(TESTDB_PATH):
    #     os.unlink(TESTDB_PATH)

    with app.test_request_context():
        db.create_all()

    request.addfinalizer(teardown)
    # TODO: may return just db with tests using sqlalchemy_user fixture directly
    return db, sqlalchemy_user
