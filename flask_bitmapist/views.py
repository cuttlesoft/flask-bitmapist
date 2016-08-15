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

from .utils import get_cohort, get_event_data



root = os.path.abspath(os.path.dirname(__file__))

bitmapist_bp = Blueprint('bitmapist', 'flask_bitmapist',
                         template_folder=os.path.join(root, 'templates'),
                         static_folder=os.path.join(root, 'static'),
                         url_prefix='/bitmapist')


@bitmapist_bp.context_processor
def inject_version():
    from . import __version__
    return dict(version=__version__)


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


@bitmapist_bp.route('/cohort', methods=['GET', 'POST'])
def cohort():
    if request.method == 'GET':
        now = datetime.utcnow()
        event_names = get_event_names()
        # TEMPORARY? for display niceness
        event_options = []
        for event_name in event_names:
            if 'user_' in event_name:
                formatted = event_name.replace('user_', '').replace('_', ' ')
                # such hackery
                formatted = ('were ' + formatted).replace('were logged', 'logged')
                # /hackery
                event_options.append([formatted, event_name])
        event_options = sorted(event_options)
        # user_events = [e for e in event_names if 'user' in e]
        # event_options = [u.replace('user_', '') for u in user_events]

        # TEMPORARY: for listing of totals per event
        events = {}
        for event_name in event_names:
            # TODO: + hourly
            day = len(DayEvents(event_name, now.year, now.month, now.day))
            week = len(WeekEvents(event_name, now.year, now.isocalendar()[1]))
            month = len(MonthEvents(event_name, now.year, now.month))
            year = len(YearEvents(event_name, now.year))
            event = (year, month, week, day)
            events[event_name] = event
        # END TEMP

        time_groups = ['day', 'week', 'month', 'year']
        return render_template('bitmapist/cohort.html', event_options=event_options, time_groups=time_groups, events=events)

    elif request.method == 'POST':

        data = json.loads(request.data)
        time_group = data.get('time_group', 'days')
        primary_event = data.get('primary_event', '')
        secondary_event = data.get('secondary_event', '')
        additional_events = data.get('additional_events', [])

        event_filters = [primary_event, secondary_event]
        if additional_events:
            for additional_event in additional_events:
                event_filters.append(additional_event.get('name'))

        # TEMPORARY
        as_percent = True
        # results & rows seem switched
        num_results = 10  # 25
        num_of_rows = 9  # num_of_rows + 1 columns are produced.
        # END TEMP

        # TODO: this?
        # dates_data = get_dates(time_group, num_rows, num_cols)
        # cohort_data = get_cohort(primary, secondary, additional, dates)
        cohort, dates = get_cohort(primary_event, secondary_event,
                                   additional_events=additional_events,
                                   time_group=time_group,
                                   # as_percent=as_percent,
                                   num_rows=num_results,
                                   num_cols=num_of_rows)

        row_totals = [0] * num_rows
        col_totals = [0] * num_cols
        for i, row in enumerate(cohort):
            for j, val in enumerate(row):
                row_totals[i] += val
                col_totals[j] += val

        averages = [float(total) / num_rows for total in col_totals]

        return render_template('bitmapist/_heatmap.html',
                       cohort=cohort,
                       dates=dates,
                       totals=row_totals,
                       averages=averages,
                       time_group=time_group,
                       num_rows=num_rows,
                       num_cols=num_cols,
                       as_percent=as_percent
                     )
