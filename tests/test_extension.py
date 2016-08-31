# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import mock

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
        'and_o': {'name': 'user:logged_out', 'op': 'and'},
        'and_c': {'name': 'user:created',    'op': 'and'},
        'and_u': {'name': 'user:updated',    'op': 'and'},
        'and_d': {'name': 'user:deleted',    'op': 'and'},
        'or_o':  {'name': 'user:logged_out', 'op': 'or'},
        'or_c':  {'name': 'user:created',    'op': 'or'},
        'or_u':  {'name': 'user:updated',    'op': 'or'},
        'or_d':  {'name': 'user:deleted',    'op': 'or'}
    }
    return setup_users(), addons


@mock.patch('flask_bitmapist.utils.BitOpAnd')
@mock.patch('flask_bitmapist.utils.BitOpOr')
@mock.patch('flask_bitmapist.utils.BitOpXor')
@mock.patch('flask_bitmapist.utils.chain_events')
@mock.patch('flask_bitmapist.utils.YearEvents')
@mock.patch('flask_bitmapist.utils.MonthEvents')
@mock.patch('flask_bitmapist.utils.WeekEvents')
def test_get_cohort(mock_week_events, mock_month_events,
                    mock_year_events, mock_chain_events,
                    mock_bit_op_xor, mock_bit_op_or, mock_bit_op_and):
    # test cohort returns
    from random import randint

    # Generate list of ints to act as user ids;
    # - between calls, should have some duplicate and some distinct
    # - temporarily convert to a set to force unique list items

    def e():
        return list(set([randint(1, 25) for n in range(10)]))

    def ee():
        return [e() for n in range(100)]

    mock_week_events.side_effect = ee()
    mock_month_events.side_effect = ee()
    mock_year_events.side_effect = ee()
    mock_chain_events.side_effect = ee()

    # Simulate BitOpAnd & BitOpOr returns but with lists
    mock_bit_op_and.side_effect = lambda x, y: list(set(x) & set(y))
    mock_bit_op_or.side_effect = lambda x, y: list(set(x) | set(y))
    mock_bit_op_xor.side_effect = lambda x, y: list(set(x) ^ set(y))

    c1, d1, t1 = get_cohort('A', 'B', time_group='weeks', num_rows=4, num_cols=4)
    c2, d2, t2 = get_cohort('A', 'B', time_group='months', num_rows=6, num_cols=5)
    c3, d3, t3 = get_cohort('A', 'B', time_group='years', num_rows=2, num_cols=3)

    # Assert cohort (+ date and total) lengths based on num_rows
    assert len(c1) == 4
    assert len(c1) == len(d1)
    assert len(c1) == len(t1)
    assert len(c2) == 6
    assert len(c2) == len(d2)
    assert len(c2) == len(t2)
    assert len(c3) == 2
    assert len(c3) == len(d3)
    assert len(c3) == len(t3)
    # Assert cohort row lengths based on num_cols
    assert len(c1[0]) == 4
    assert len(c2[0]) == 5
    assert len(c3[0]) == 3

    # Assert date values based on time_group given
    #     - dates are old->new, so use num_rows-1 to adjust index for timedelta

    def _week(x):
        return (x.year, x.month, x.day, x.isocalendar()[1])

    def _month(x):
        return (x.year, x.month)

    def _year(x):
        return (x.year)

    # 1 - weeks
    for idx, d in enumerate(d1):
        assert _week(d) == _week(now - timedelta(weeks=3-idx))
    # 2 - months
    for idx, d in enumerate(d2):
        this_month = now.replace(day=1)  # work with first day of month
        months_ago = (5 - idx) * 365 / 12  # no 'months' arg for timedelta
        assert _month(d) == _month(this_month - timedelta(months_ago))
    # 3 - years
    for idx, d in enumerate(d3):
        this_year = now.replace(month=1, day=1)  # work with first day of year
        years_ago = (1 - idx) * 365  # no 'years' arg for timedelta
        assert _year(d) == _year(this_year - timedelta(years_ago))


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
    one_event = [addons['and_o']]
    two_events = [addons['and_o'], addons['and_c']]
    three_events = [addons['and_o'], addons['and_c'], addons['and_d']]

    one = chain_events(base, one_event, now, time_group)
    two = chain_events(base, two_events, now, time_group)
    three = chain_events(base, three_events, now, time_group)

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
    one_event = [addons['or_o']]
    two_events = [addons['or_o'], addons['or_u']]
    three_events = [addons['or_o'], addons['or_u'], addons['or_d']]

    one = chain_events(base, one_event, now, time_group)
    two = chain_events(base, two_events, now, time_group)
    three = chain_events(base, three_events, now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    one_u = ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'od']
    two_u = ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od']
    three_u = ['iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd']

    one_users = [u for u in users if u[0] in one_u]
    two_users = [u for u in users if u[0] in two_u]
    three_users = [u for u in users if u[0] in three_u]

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
    and_or_events = [addons['and_o'], addons['or_c']]
    or_and_events = [addons['or_o'], addons['and_c']]

    and_or = chain_events(base, and_or_events, now, time_group)
    or_and = chain_events(base, or_and_events, now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    and_or_u = ['iocud', 'iocd', 'iou', 'icd', 'io']
    or_and_u = ['iocud', 'iocd', 'icd', 'ocud']

    and_or_users = [u for u in users if u[0] in and_or_u]
    or_and_users = [u for u in users if u[0] in or_and_u]

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
    and_and_or_events = [addons['and_o'], addons['and_c'], addons['or_d']]
    and_or_and_events = [addons['and_o'], addons['or_c'], addons['and_d']]
    or_and_and_events = [addons['or_o'], addons['and_c'], addons['and_d']]

    and_and_or = chain_events(base, and_and_or_events, now, time_group)
    and_or_and = chain_events(base, and_or_and_events, now, time_group)
    or_and_and = chain_events(base, or_and_and_events, now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    and_and_or_u = ['iocud', 'iocd']
    and_or_and_u = ['iocud', 'iocd', 'icd']
    or_and_and_u = ['iocud', 'iocd', 'icd', 'ocud']

    and_and_or_users = [u for u in users if u[0] in and_and_or_u]
    and_or_and_users = [u for u in users if u[0] in and_or_and_u]
    or_and_and_users = [u for u in users if u[0] in or_and_and_u]

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
    or_or_and_events = [addons['or_u'], addons['or_c'], addons['and_d']]
    or_and_or_events = [addons['or_u'], addons['and_c'], addons['or_d']]
    and_or_or_events = [addons['and_u'], addons['or_c'], addons['or_d']]

    or_or_and = chain_events(base, or_or_and_events, now, time_group)
    or_and_or = chain_events(base, or_and_or_events, now, time_group)
    and_or_or = chain_events(base, and_or_or_events, now, time_group)

    # out of: 'iocud', 'iocd', 'iou', 'icd', 'io', 'ocud', 'cud', 'od', 'd'
    or_or_and_u = ['iocud', 'iocd', 'icd', 'ocud', 'cud']
    or_and_or_u = ['iocud', 'iocd', 'icd', 'ocud', 'cud']
    and_or_or_u = ['iocud', 'iocd', 'iou', 'icd']

    or_or_and_users = [u for u in users if u[0] in or_or_and_u]
    or_and_or_users = [u for u in users if u[0] in or_and_or_u]
    and_or_or_users = [u for u in users if u[0] in and_or_or_u]

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
