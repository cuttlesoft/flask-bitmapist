# -*- coding: utf-8 -*-
"""
    flask_bitmapist.views
    ~~~~~~~~~~~~~~~~~~~~~
    This module provides the views for Flask-Bitmapist's web interface.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import json
import os

from datetime import datetime

from flask import Blueprint, render_template, request

from bitmapist import get_event_names

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

    day_events = len(list(get_event_data('user:logged_in', 'days', now)))
    week_events = len(list(get_event_data('user:logged_in', 'weeks', now)))
    month_events = len(list(get_event_data('user:logged_in', 'months', now)))
    year_events = len(list(get_event_data('user:logged_in', 'years', now)))
    return render_template('bitmapist/index.html', events=get_event_names(),
                           day_events=day_events, week_events=week_events,
                           month_events=month_events, year_events=year_events)


@bitmapist_bp.route('/cohort', methods=['GET', 'POST'])
def cohort():
    if request.method == 'GET':
        event_names = get_event_names()
        # FOR DEMO PURPOSES:
        # Nicely format event names for dropdown selection; remove 'user:',
        # convert '_' to ' ', and prepend 'created/updated/deleted' with 'were'
        # for readability/grammar.
        event_options = []
        for event_name in event_names:
            if 'user:' in event_name:
                formatted = event_name.replace('user:', '').replace('_', ' ')
                if formatted in ['created', 'updated', 'deleted']:
                    formatted = 'were %s' % formatted
                event_options.append([formatted, event_name])
        event_options = sorted(event_options)

        # FOR DEMO PURPOSES: list of totals per event
        now = datetime.utcnow()
        events = {}
        for event_name in event_names:
            # TODO: + hourly
            day = len(get_event_data(event_name, 'days', now))
            week = len(get_event_data(event_name, 'weeks', now))
            month = len(get_event_data(event_name, 'months', now))
            year = len(get_event_data(event_name, 'years', now))
            event = (year, month, week, day)
            events[event_name] = event

        time_groups = ['day', 'week', 'month', 'year']  # singular for display
        return render_template('bitmapist/cohort.html',
                               event_options=event_options,
                               time_groups=time_groups,
                               events=events)

    elif request.method == 'POST':
        data = json.loads(request.data)

        # Cohort events
        primary_event = data.get('primary_event')
        secondary_event = data.get('secondary_event')
        additional_events = data.get('additional_events', [])
        # Cohort settings
        time_group = data.get('time_group', 'days')
        as_percent = data.get('as_percent', False)
        with_replacement = data.get('with_replacement', False)
        num_rows = int(data.get('num_rows', 20))
        num_cols = int(data.get('num_cols', 10))

        if time_group == 'years':
            # Three shall be the number thou shalt count, and the number of the
            # counting shall be three. Four shalt thou not count, neither count thou
            # two, excepting that thou then proceed to three. Five is right out.
            num_rows = 3

        # Columns > rows would extend into future and thus would just be empty
        num_cols = num_rows if num_cols > num_rows else num_cols

        # Get cohort data and associated dates
        cohort_data = get_cohort(primary_event, secondary_event,
                                 additional_events=additional_events,
                                 time_group=time_group,
                                 num_rows=num_rows, num_cols=num_cols,
                                 with_replacement=with_replacement)
        cohort, dates, row_totals = cohort_data

        # Format dates for table
        if time_group == 'years':
            dt_format = '%Y'
        elif time_group == 'months':
            dt_format = '%b %Y'
        elif time_group == 'weeks':
            dt_format = 'Week %U - %d %b %Y'
        else:
            dt_format = '%d %b %Y'

        date_strings = [dt.strftime(dt_format) for dt in dates]

        # Get overall total
        overall_total = sum(row_totals)

        # Get column totals (pre-percent)
        col_counts = []
        col_totals = []
        for j in range(num_cols):
            col = [row[j] for row in cohort if row[j] is not None]
            col_counts.append(len(col))
            col_totals.append(sum(col))

        # Get each cohort value as percents if as_percent
        if as_percent:
            for i, row in enumerate(cohort):
                if row_totals[i]:
                    # calculate percent value for each (unless None)
                    cohort[i] = [float(r) / row_totals[i] if r is not None else r for r in row]

        # Get column averages (post-percent)
        # TODO: do not loop range(num_cols) twice, but necessary as-is so that,
        #       if getting results as percents, col totals are calculated with
        #       numbers of users (always) but col averages are calculated with
        #       percent values
        averages = []
        for j in range(num_cols):
            col = [row[j] for row in cohort if row[j] is not None]
            average = float(sum(col)) / col_counts[j] if col_counts[j] else 0
            averages.append(average)

        # TODO: remove unnecessary keys from json return
        cohort_data = {
            'cohort': cohort,
            'dates': date_strings,
            'total': overall_total,
            'row_totals': row_totals,
            'col_totals': col_totals,
            'averages': averages,
            'time_group': time_group,
            'as_percent': as_percent,
            'num_rows': num_rows,
            'num_cols': num_cols
        }

        if request.args.get('json'):
            return json.dumps(cohort_data, indent=4)
        else:
            return render_template('bitmapist/_heatmap.html', **cohort_data)
