# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint

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
        'i': 'user_logged_in',
        'o': 'user_logged_out',
        'c': 'user_inserted',  # created
        'u': 'user_updated',
        'd': 'user_deleted',
    }

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od'
    users = [
        ('iocud', randint(1, 100)),
        ('iocd',  randint(1, 100)),
        ('iou',   randint(1, 100)),
        ('icd',   randint(1, 100)),
        ('io',    randint(1, 100)),
        ('ocud',  randint(1, 100)),
        ('cud',   randint(1, 100)),
        ('od',    randint(1, 100)),
        ('d',     randint(1, 100))
    ]

    for user in users:
        for u in user[0]:
            event_name = event_mappings.get(u, None)
            if event_name:
                mark_event(event_name, user[1])

    return users


def setup_chain_events(time_group='days'):
    addons = {
        'and_o': { 'name': 'user_logged_out', 'op': 'and' },
        'and_c': { 'name': 'user_inserted',   'op': 'and' },
        'and_u': { 'name': 'user_updated',    'op': 'and' },
        'and_d': { 'name': 'user_deleted',    'op': 'and' },
        'or_o':  { 'name': 'user_logged_out', 'op': 'or' },
        'or_c':  { 'name': 'user_inserted',   'op': 'or' },
        'or_u':  { 'name': 'user_updated',    'op': 'or' },
        'or_d':  { 'name': 'user_deleted',    'op': 'or' }
    }
    return setup_users(), addons

# # For use with 'or', could get 'and' lists and use `list(set(a).union(b))`?
# def target_users(users, chars):
#     target_users = []
#     for user in users:
#         matched_chars = [c for c in chars if c in user[0]]
#         if len(matched_chars) == len(chars):
#             target_users.append(user)
#     return target_users

def test_get_cohort():
    # test results from simple 2 event &

    # test
    pass


def test_chain_events():
    time_group = 'days'
    # base, addons, users = setup_chain_events(time_group)
    users, addons = setup_chain_events(time_group)

    # test results from no additional events
    logged_in_events = chain_events('user_logged_in', [], now, time_group)

    # which users should have 'user_logged_in' events marked
    logged_in_users = [u for u in users if 'i' in u[0]]  # iocud/iocd/iou/icd/io
    # logged_in_users = target_users(users, 'i')


    assert len(logged_in_events) == len(logged_in_users)
    for u in logged_in_users:
        assert u[1] in get_event_data('user_logged_in', time_group, now)


def test_chain_events_with_and():
    base = 'user_logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 1-3 additional event with AND operator(s)
    i_and_o = chain_events(base, [addons['and_o']], now, time_group)
    i_and_o_and_c = chain_events(base, [addons['and_o'], addons['and_c']], now, time_group)
    i_and_o_and_c_and_d = chain_events(base, [addons['and_o'], addons['and_c'], addons['and_d']], now, time_group)

    # o_users = target_users(users, 'io')  # iocud/iocd/iou/io
    # oc_users = target_users(users, 'ioc')  # iocud/iocd
    # ocd_users = target_users(users, 'iocd')  # iocud/iocd

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    assert len(i_and_o) == len(['iocud', 'iocd', 'iou', 'io'])
    assert len(i_and_o_and_c) == len(['iocud', 'iocd'])
    assert len(i_and_o_and_c_and_d) == len(['iocud', 'iocd'])

def test_chain_events_with_or():
    base = 'user_logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 1-3 additional event with OR operator(s)
    i_or_o = chain_events(base, [addons['or_o']], now, time_group)
    i_or_o_or_u = chain_events(base, [addons['or_o'], addons['or_u']], now, time_group)
    i_or_o_or_u_or_d = chain_events(base, [addons['or_o'], addons['or_u'], addons['or_d']], now, time_group)

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    assert len(i_or_o) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'od'])
    assert len(i_or_o_or_u) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od'])
    assert len(i_or_o_or_u_or_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])

def test_chain_events_with_1_and_1_or():
    base = 'user_logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 2 additional events with 1 'and' + 1 'or' operator(s)
    i_and_o_or_c = chain_events(base, [addons['and_o'], addons['or_c']], now, time_group)  # & |
    i_or_o_and_c = chain_events(base, [addons['or_o'], addons['and_c']], now, time_group)  # | &

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    assert len(i_and_o_or_c) == len(['iocud', 'iocd', 'iou', 'icd', 'io'])
    assert len(i_or_o_and_c) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?

def test_chain_events_with_2_and_1_or():
    base = 'user_logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 3 additional events with 2 'and' + 1 'or' operator(s)
    i_and_o_and_c_or_d = chain_events(base, [addons['and_o'], addons['and_c'], addons['or_d']], now, time_group)  # & & |
    i_and_o_or_c_and_d = chain_events(base, [addons['and_o'], addons['or_c'], addons['and_d']], now, time_group)  # & | &
    i_or_o_and_c_and_d = chain_events(base, [addons['or_o'], addons['and_c'], addons['and_d']], now, time_group)  # | & &

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    assert len(i_and_o_and_c_or_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?
    assert len(i_and_o_or_c_and_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?
    assert len(i_or_o_and_c_and_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?


def test_chain_events_with_1_and_2_or():
    base = 'user_logged_in'
    time_group = 'days'
    users, addons = setup_chain_events(time_group)

    # test results from 3 additional events with 1 'and' + 2 'or' operator(s)
    i_or_o_or_c_and_d = chain_events(base, [addons['or_o'], addons['or_c'], addons['and_d']], now, time_group)  # | | &
    i_or_o_and_c_or_d = chain_events(base, [addons['or_o'], addons['and_c'], addons['or_d']], now, time_group)  # | & |
    i_and_o_or_c_or_d = chain_events(base, [addons['and_o'], addons['or_c'], addons['or_d']], now, time_group)  # & | |

    # 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    assert len(i_or_o_or_c_and_d) == len(['iocud', 'iocd', 'icd', 'ocud', 'cud', 'od', 'd'])  # ?
    assert len(i_or_o_and_c_or_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?
    assert len(i_and_o_or_c_or_d) == len(['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'])  # ?


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

        # test that user id was marked with 'user_logged_in' event
        assert user_id in MonthEvents('user_logged_in', now.year, now.month)


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

        # test that user id was marked with 'user_logged_out' event
        assert user_id in MonthEvents('user_logged_out', now.year, now.month)


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

        # test that user id was marked with 'user_inserted' event
        assert user.id in MonthEvents('user_inserted', now.year, now.month)


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

        # test that user id was marked with 'user_updated' event
        assert user.id in MonthEvents('user_updated', now.year, now.month)


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

        # test that user id was marked with 'user_deleted' event
        assert user_id in MonthEvents('user_deleted', now.year, now.month)


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
