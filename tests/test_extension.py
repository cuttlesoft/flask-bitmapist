# -*- coding: utf-8 -*-

from datetime import datetime

from flask import request
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

from flask_bitmapist import (chain_events, get_cohort, get_event_data,
                             mark, mark_event, unmark_event,
                             MonthEvents, WeekEvents, DayEvents, HourEvents)
from flask_bitmapist.extensions.flask_login import mark_login, mark_logout


# import necessary for test_user_login/logout, but unused fails pyflakes
mark_login
mark_logout

now = datetime.utcnow()


# COHORTS

def setup_users(now=None):
    now = now or datetime.utcnow()

    # mark specific events for single user with user_string as user_id
    event_mappings = {
        'i': 'user:logged_in',
        'o': 'user:logged_out',
        'c': 'user:created',
        'u': 'user:updated',
        'd': 'user:deleted',
    }

    users = [
        ('iocud', 11),
        ('iocd',  22),
        ('iou',   33),
        ('icd',   44),
        ('io',    55),
        ('ocud',  66),
        ('cud',   77),
        ('od',    88),
        ('d',     99)
    ]

    for user in users:
        for u in user[0]:
            event_name = event_mappings.get(u, None)
            if event_name:
                mark_event(event_name, user[1])

    return users


def setup_chain_events(time_group='days'):
    addons = {
        'and_o': { 'name': 'user:logged_out', 'op': 'and' },
        'and_c': { 'name': 'user:created',    'op': 'and' },
        'and_u': { 'name': 'user:updated',    'op': 'and' },
        'and_d': { 'name': 'user:deleted',    'op': 'and' },
        'or_o':  { 'name': 'user:logged_out', 'op': 'or' },
        'or_c':  { 'name': 'user:created',    'op': 'or' },
        'or_u':  { 'name': 'user:updated',    'op': 'or' },
        'or_d':  { 'name': 'user:deleted',    'op': 'or' }
    }
    return setup_users(), addons


def test_get_cohort():
    pass


def test_chain_events():
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from no additional events
    logged_in_events = chain_events('user:logged_in', [], now, time_group)

    # which users should have 'user:logged_in' events marked
    logged_in_users = [u for u in users if 'i' in u[0]]  # iocud/iocd/iou/icd/io

    assert len(logged_in_events) == len(logged_in_users)
    for u in logged_in_users:
        assert u[1] in get_event_data('user:logged_in', time_group, now)


def test_chain_events_with_and():
    base = 'user:logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 1-3 additional event with AND operator(s)
    one = chain_events(base, [addons['and_o']], now, time_group)
    two = chain_events(base, [addons['and_o'], addons['and_c']], now, time_group)
    three = chain_events(base, [addons['and_o'], addons['and_c'], addons['and_d']], now, time_group)

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    one_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'io']]
    two_users = [u for u in users if u[0] in ['iocud', 'iocd']]
    three_users = [u for u in users if u[0] in ['iocud', 'iocd']]

    # check lengths
    assert len(one) == len(one_users)
    assert len(two) == len(two_users)
    assert len(three) == len(three_users)

    # check contents
    for user in one_users:
        assert user[1] in one
    for user in two_users:
        assert user[1] in two
    for user in three_users:
        assert user[1] in three


def test_chain_events_with_or():
    base = 'user:logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 1-3 additional event with OR operator(s)
    one = chain_events(base, [addons['or_o']], now, time_group)
    two = chain_events(base, [addons['or_o'], addons['or_u']], now, time_group)
    three = chain_events(base, [addons['or_o'], addons['or_u'], addons['or_d']], now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    one_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'od']]
    two_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od']]
    three_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd']]

    # check lengths
    assert len(one) == len(one_users)
    assert len(two) == len(two_users)
    assert len(three) == len(three_users)

    # check contents
    for user in one_users:
        assert user[1] in one
    for user in two_users:
        assert user[1] in two
    for user in three_users:
        assert user[1] in three


def test_chain_events_with_1_and_1_or():
    base = 'user:logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 2 additional events with 1 'and' + 1 'or' operator(s)
    and_or = chain_events(base, [addons['and_o'], addons['or_c']], now, time_group)
    or_and = chain_events(base, [addons['or_o'], addons['and_c']], now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    and_or_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'icd', 'io']]
    or_and_users = [u for u in users if u[0] in ['iocud', 'iocd', 'icd', 'ocud']]

    # check lengths
    assert len(and_or) == len(and_or_users)
    assert len(or_and) == len(or_and_users)

    # check contents
    for user in and_or_users:
        assert user[1] in and_or
    for user in or_and_users:
        assert user[1] in or_and


def test_chain_events_with_2_and_1_or():
    base = 'user:logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 3 additional events with 2 'and' + 1 'or' operator(s)
    and_and_or = chain_events(base, [addons['and_o'], addons['and_c'], addons['or_d']], now, time_group)
    and_or_and = chain_events(base, [addons['and_o'], addons['or_c'], addons['and_d']], now, time_group)
    or_and_and = chain_events(base, [addons['or_o'], addons['and_c'], addons['and_d']], now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    and_and_or_users = [u for u in users if u[0] in ['iocud', 'iocd']]
    and_or_and_users = [u for u in users if u[0] in ['iocud', 'iocd', 'icd']]
    or_and_and_users = [u for u in users if u[0] in ['iocud', 'iocd', 'icd', 'ocud']]

    # check lengths
    assert len(and_and_or) == len(and_and_or_users)
    assert len(and_or_and) == len(and_or_and_users)
    assert len(or_and_and) == len(or_and_and_users)

    # check contents
    for user in and_and_or_users:
        assert user[1] in and_and_or
    for user in and_or_and_users:
        assert user[1] in and_or_and
    for user in or_and_and_users:
        assert user[1] in or_and_and


def test_chain_events_with_1_and_2_or():
    base = 'user:logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 3 additional events with 1 'and' + 2 'or' operator(s)
    or_or_and = chain_events(base, [addons['or_u'], addons['or_c'], addons['and_d']], now, time_group)
    or_and_or = chain_events(base, [addons['or_u'], addons['and_c'], addons['or_d']], now, time_group)
    and_or_or = chain_events(base, [addons['and_u'], addons['or_c'], addons['or_d']], now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    or_or_and_users = [u for u in users if u[0] in ['iocud', 'iocd', 'icd', 'ocud', 'cud']]
    or_and_or_users = [u for u in users if u[0] in ['iocud', 'iocd', 'icd', 'ocud', 'cud']]
    and_or_or_users = [u for u in users if u[0] in ['iocud', 'iocd', 'iou', 'icd']]

    # check lengths
    assert len(or_or_and) == len(or_or_and_users)
    assert len(or_and_or) == len(or_and_or_users)
    assert len(and_or_or) == len(and_or_or_users)

    # check contents
    for user in or_or_and_users:
        assert user[1] in or_or_and
    for user in or_and_or_users:
        assert user[1] in or_and_or
    for user in and_or_or_users:
        assert user[1] in and_or_or


# FLASK LOGIN

class User(UserMixin):
    id = None

def test_flask_login_user_login(app):
    # LoginManager could be set up in app fixture in conftest.py instead
    login_manager = LoginManager()
    login_manager.init_app(app)

    # TODO: once event is marked, user id exists in MonthEvents and test will
    #       continue to pass, regardless of continued success; set to current
    #       microsecond to temporarily circumvent, but there should be a better
    #       way to fix user_id assignment (or tear down redis or something)
    user_id = datetime.now().microsecond

    with app.test_request_context():
        # set up and log in user
        user = User()
        user.id = user_id
        login_user(user)

        # test that user was logged in
        assert current_user.is_active
        assert current_user.is_authenticated
        assert current_user == user

        # test that user id was marked with 'user:logged_in' event
        assert user_id in MonthEvents('user:logged_in', now.year, now.month)


def test_flask_login_user_logout(app):
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

        # test that user id was marked with 'user:logged_out' event
        assert user_id in MonthEvents('user:logged_out', now.year, now.month)


# SQLALCHEMY

# TODO: Instead of sqlalchemy fixture (return: db, User),
#       each test could use sqlalchemy fixture (return:
#       db) and sqlalchemy_user fixture (return: User);
#       tests should use whichever is better practice.

def test_sqlalchemy_after_insert(sqlalchemy):
    db, User = sqlalchemy

    with db.app.test_request_context():
        # set up and save user
        user = User(name='Test User')
        db.session.add(user)
        db.session.commit()

        # test that user was saved
        assert user.id is not None

        # test that user id was marked with 'user:created' event
        assert user.id in MonthEvents('user:created', now.year, now.month)


def test_sqlalchemy_before_update(sqlalchemy):
    db, User = sqlalchemy

    with db.app.test_request_context():
        # set up and save user
        user = User(name='Test User')
        db.session.add(user)
        db.session.commit()

        # update user, and test that user is updated
        user.name = 'New Name'
        assert db.session.is_modified(user)

        db.session.add(user)
        db.session.commit()
        assert not db.session.is_modified(user)

        # test that user id was marked with 'user:updated' event
        assert user.id in MonthEvents('user:updated', now.year, now.month)


def test_sqlalchemy_before_delete(sqlalchemy):
    db, User = sqlalchemy

    with db.app.test_request_context():
        # set up and save user
        user = User(name='Test User')
        db.session.add(user)
        db.session.commit()

        # grab user id before we delete
        user_id = user.id

        # delete user, and test that user is deleted
        db.session.delete(user)
        db.session.commit()
        user_in_db = db.session.query(User).filter(User.id == user_id).first()
        assert not user_in_db

        # test that user id was marked with 'user:deleted' event
        assert user_id in MonthEvents('user:deleted', now.year, now.month)


# GENERAL (redis, decorator, marking events, etc.)

def test_redis_url_config(app, bitmap):
    assert bitmap.redis_url == app.config['BITMAPIST_REDIS_URL']


def test_redis_system_name_config(app, bitmap):
    assert 'default' in bitmap.SYSTEMS.keys()


def test_track_hourly_config(app, bitmap):
    assert bitmap.TRACK_HOURLY is False


def test_index(app, bitmap, client):
    with app.test_request_context('/bitmapist/'):
        assert request.endpoint == 'bitmapist.index'


def test_cohort(app, bitmap, client):
    with app.test_request_context('/bitmapist/cohort'):
        assert request.endpoint == 'bitmapist.cohort'


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
