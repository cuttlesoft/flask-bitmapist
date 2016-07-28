# -*- coding: utf-8 -*-

from datetime import datetime

from flask import request
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

from flask_bitmapist import (mark, MonthEvents, WeekEvents, DayEvents, HourEvents,
                             mark_event, unmark_event)
from flask_bitmapist.extensions.flask_login import mark_login, mark_logout


# import necessary for test_user_login/logout, but unused fails pyflakes
mark_login
mark_logout

now = datetime.utcnow()


class User(UserMixin):
    id = None


def test_user_login(app):
    # LoginManager could be set up in app fixture in conftest.py instead
    login_manager = LoginManager()
    login_manager.init_app(app)

    # TODO: once event is marked, user id exists in MonthEvents and test will
    #       continue to pass, regardless of continued success; set to current
    #       microsecond to temporarily circumvent, but there should be a better
    #       way to fix user_id assignment (or tear down redis or something)
    user_id = datetime.now().microsecond
    # user_id = 1
    # print user_id

    with app.test_request_context():
        # set up and log in user
        user = User()
        user.id = user_id
        login_user(user)

        # test that user was logged in
        assert current_user.is_active
        assert current_user.is_authenticated
        assert current_user == user

        # test that user id was marked with 'user_logged_in' event
        assert user_id in MonthEvents('user_logged_in', now.year, now.month)


def test_user_logout(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    user_id = datetime.now().microsecond

    with app.test_request_context():
        # set up, log in, and log out user
        user = User()
        user.id = user_id
        login_user(user)
        logout_user()

        # test that user was logged out
        assert not current_user.is_active
        assert not current_user.is_authenticated
        assert not current_user == user

        # test that user id was marked with 'user_logged_out' event
        assert user_id in MonthEvents('user_logged_out', now.year, now.month)


def test_redis_url_config(app, bitmap):
    assert bitmap.redis_url == app.config['BITMAPIST_REDIS_URL']


def test_redis_system_name_config(app, bitmap):
    assert 'default' in bitmap.SYSTEMS.keys()


def test_track_hourly_config(app, bitmap):
    assert bitmap.TRACK_HOURLY is False


def test_index(app, bitmap, client):
    with app.test_request_context('/bitmapist/'):
        assert request.endpoint == 'bitmapist.index'


def test_events(app, bitmap, client):
    with app.test_request_context('/bitmapist/events'):
        assert request.endpoint == 'bitmapist.events'


def test_mark_decorator(app, client):

    @app.route('/')
    @mark('test', 1)
    def index():
        return ''

    @app.route('/hourly')
    @mark('test_hourly', 2, track_hourly=True)
    def index_hourly():
        return ''

    client.get('/', follow_redirects=True)

    # month events
    assert 1 in MonthEvents('test', now.year, now.month)
    assert 2 not in MonthEvents('test', now.year, now.month)

    # week events
    assert 1 in WeekEvents('test', now.year, now.isocalendar()[1])
    assert 2 not in WeekEvents('test', now.year, now.isocalendar()[1])

    # day events
    assert 1 in DayEvents('test', now.year, now.month, now.day)
    assert 2 not in DayEvents('test', now.year, now.month, now.day)

    client.get('/hourly', follow_redirects=True)

    # hour events
    assert 1 not in HourEvents('test', now.year, now.month, now.day, now.hour)
    assert 2 in HourEvents('test_hourly', now.year, now.month, now.day, now.hour)
    assert 1 not in HourEvents('test_hourly', now.year, now.month, now.day, now.hour)
    assert 1 not in HourEvents('test_hourly', now.year, now.month, now.day, now.hour - 1)


def test_mark_function(app, client):
    mark_event('active', 125)
    assert 125 in MonthEvents('active', now.year, now.month)


def test_unmark_function(app, client):
    mark_event('active', 126)
    assert 126 in MonthEvents('active', now.year, now.month)

    unmark_event('active', 126)
    assert 126 not in MonthEvents('active', now.year, now.month)
