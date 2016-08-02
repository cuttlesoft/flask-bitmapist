# -*- coding: utf-8 -*-

import pytest
import os
import subprocess
import atexit
import socket
import time

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
# TODO: currently, redis server must be manually started on port 6399 to work

@pytest.yield_fixture(scope='session', autouse=True)
def redis_server():
    """
    Fixture starting the Redis server
    """
    redis_host = '127.0.0.1'
    redis_port = 6399
    if is_socket_open(redis_host, redis_port):
        yield None
    else:
        proc = start_redis_server(redis_port)
        wait_for_socket(redis_host, redis_port)
        yield proc
        proc.terminate()


@pytest.fixture(scope='session', autouse=True)
def setup_redis_for_bitmapist():
    from bitmapist import setup_redis

    setup_redis('default', 'localhost', 6399)
    setup_redis('default_copy', 'localhost', 6399)


@pytest.fixture(autouse=True)
def clean_redis():
    from bitmapist import get_redis

    cli = get_redis('default')
    keys = cli.keys('trackist_*')
    if len(keys) > 0:
        cli.delete(*keys)


def start_redis_server(port):
    """
    Helper function starting Redis server
    """
    devzero = open(os.devnull, 'r')
    devnull = open(os.devnull, 'w')

    # TODO: better handling of redis-server installation location variation
    try:
        proc = subprocess.Popen(['/usr/bin/redis-server', '--port', str(port)],
                                stdin=devzero, stdout=devnull, stderr=devnull,
                                close_fds=True)
    except OSError:
        proc = subprocess.Popen(['/usr/local/bin/redis-server', '--port', str(port)],
                                stdin=devzero, stdout=devnull, stderr=devnull,
                                close_fds=True)
    # end todo

    atexit.register(lambda: proc.terminate())
    return proc


def is_socket_open(host, port):
    """
    Helper function which tests is the socket open
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    return sock.connect_ex((host, port)) == 0


def wait_for_socket(host, port, seconds=3):
    """
    Check if socket is up for :param:`seconds` sec, raise an error otherwise
    """
    polling_interval = 0.1
    iterations = int(seconds / polling_interval)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    for _ in range(iterations):
        result = sock.connect_ex((host, port))
        if result == 0:
            sock.close()
            break
        time.sleep(polling_interval)
    else:
        raise RuntimeError('Service at %s:%d is unreachable' % (host, port))
