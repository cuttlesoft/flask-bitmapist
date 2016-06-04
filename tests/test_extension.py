# -*- coding: utf-8 -*-

from datetime import datetime

from flask import request
from flask_bitmapist import MonthEvents, WeekEvents


now = datetime.utcnow()


def test_redis_url(app, bitmap):
    assert bitmap.redis_url == app.config['BITMAPIST_REDIS_URL']


def test_redis_system_name(app, bitmap):
    assert 'default' in bitmap.SYSTEMS.keys()


def test_track_hourly(app, bitmap):
    assert bitmap.TRACK_HOURLY is False


def test_index(app, bitmap, client):
    with app.test_request_context('/bitmapist/'):
        assert request.endpoint == 'bitmapist.index'


def test_events(app, bitmap, client):
    with app.test_request_context('/bitmapist/events'):
        assert request.endpoint == 'bitmapist.events'


def test_mark_decorator(app, client):
    client.get('/', follow_redirects=True)

    # month events
    assert 1 in MonthEvents('test', now.year, now.month)
    assert 2 not in MonthEvents('test', now.year, now.month)

    # week events
    assert 1 in WeekEvents('test', now.year, now.isocalendar()[1])
    assert 2 not in WeekEvents('test', now.year, now.isocalendar()[1])

    # day events
    # assert 1 in DayEvents('test', now.year, now.month, now.day)
    # assert 2 not in DayEvents('test', now.year, now.month, now.day)

    # hour events
    # assert 123 in HourEvents('test', now.year, now.month, now.day, now.hour)
    # assert 124 not in HourEvents('test', now.year, now.month, now.day, now.hour)
    # assert 124 not in HourEvents('test', now.year, now.month, now.day, now.hour-1)
