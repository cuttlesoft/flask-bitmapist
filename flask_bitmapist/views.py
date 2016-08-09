# -*- coding: utf-8 -*-
"""
    flask_bitmapist.views
    ~~~~~~~~~~~~~~~~~~~~~
    This module provides the views for Flask-Bitmapist's web interface.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import json, os

from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from bitmapist import get_event_names, DayEvents, WeekEvents, MonthEvents, YearEvents  # BitOpAnd, BitOpOr


root = os.path.abspath(os.path.dirname(__file__))

bitmapist_bp = Blueprint('bitmapist', 'flask_bitmapist',
                         template_folder=os.path.join(root, 'templates'),
                         static_folder=os.path.join(root, 'static'),
                         url_prefix='/bitmapist')


@bitmapist_bp.context_processor
def inject_version():
    from . import __version__
    return dict(version=__version__)


# @bitmapist_bp.route('/')
# def index():
#     return render_template('bitmapist/index.html', events=get_event_names())


@bitmapist_bp.route('/')
def index():
    now = datetime.utcnow()

    day_events = len(list(DayEvents('user_logged_in', now.year, now.month, now.day)))
    week_events = len(list(WeekEvents('user_logged_in', now.year, now.isocalendar()[1])))
    month_events = len(list(MonthEvents('user_logged_in', now.year, now.month)))
    year_events = len(list(YearEvents('user_logged_in', now.year)))
    # return render_template('bitmapist/data.html', ...
    return render_template('bitmapist/index.html', events=get_event_names(), day_events=day_events, week_events=week_events, month_events=month_events, year_events=year_events)


@bitmapist_bp.route('/events')
def events():
    now = datetime.utcnow()
    event_names = get_event_names()

    # For temporary listing of totals per event
    events = {}
    for event_name in event_names:
        # TODO: + hourly
        day = len(DayEvents(event_name, now.year, now.month, now.day))
        week = len(WeekEvents(event_name, now.year, now.isocalendar()[1]))
        month = len(MonthEvents(event_name, now.year, now.month))
        year = len(YearEvents(event_name, now.year))
        event = (year, month, week, day)
        events[event_name] = event

    intervals = ['year', 'month', 'week', 'day']
    return render_template('bitmapist/events.html', event_names=event_names, intervals=intervals, events=events)

@bitmapist_bp.route('/cohort', methods=['POST'])
def cohort():
    data = json.loads(request.data)

    # SO RUFF... UoxoU
    event = data.get('event')
    ops = data.get('ops')

    cohort = bitmapist_events(event.get('name'), event.get('range'))

    if ops:
        for op in ops:
            if op.get('operation') == 'and':
                cohort = cohort & bitmapist_events(op.get('name'), op.get('range'))
            elif op.get('operation') == 'or':
                cohort = cohort | bitmapist_events(op.get('name'), op.get('range'))

    # print list(cohort)
    return jsonify(list(cohort))

def bitmapist_events(event_name, date_range):
    now = datetime.utcnow()

    # TODO: + hourly
    if date_range == 'year':
        return YearEvents(event_name, now.year)
    elif date_range == 'month':
        return MonthEvents(event_name, now.year, now.month)
    elif date_range == 'week':
        return WeekEvents(event_name, now.year, now.isocalendar()[1])
    elif date_range == 'day':
        return DayEvents(event_name, now.year, now.month, now.day)
