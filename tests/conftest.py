# -*- coding: utf-8 -*-

import pytest

from flask import Flask
from flask_bitmapist import FlaskBitmapist

from datastore import SQLAlchemyUserDatastore
# from mixins import Bitmapistable


@pytest.fixture
def app(request):
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'
    app.config['TESTING'] = True
    app.config['BITMAPIST_REDIS_URL'] = 'redis://localhost:6379'
    app.config['SECRET_KEY'] = 'verysecret'
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


@pytest.fixture()
def sqlalchemy_datastore(request, app, tmpdir):
    import os, tempfile
    from flask_sqlalchemy import SQLAlchemy

    f, path = tempfile.mkstemp(prefix='flask-security-test-db', suffix='.db', dir=str(tmpdir))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path
    db = SQLAlchemy(app)

    roles_users = db.Table(
        'roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

    class Role(db.Model):
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(80), unique=True)
        description = db.Column(db.String(255))

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True)
        username = db.Column(db.String(255))
        password = db.Column(db.String(255))
        last_login_at = db.Column(db.DateTime())
        current_login_at = db.Column(db.DateTime())
        last_login_ip = db.Column(db.String(100))
        current_login_ip = db.Column(db.String(100))
        login_count = db.Column(db.Integer)
        active = db.Column(db.Boolean())
        confirmed_at = db.Column(db.DateTime())
        roles = db.relationship('Role', secondary=roles_users,
                                backref=db.backref('users', lazy='dynamic'))

    with app.app_context():
        db.create_all()

    request.addfinalizer(lambda: os.remove(path))

    return SQLAlchemyUserDatastore(db, User, Role)
