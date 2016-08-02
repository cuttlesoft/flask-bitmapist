# -*- coding: utf-8 -*-
"""
    flask_bitmapist.views
    ~~~~~~~~~~~~~~~~~~~~~
    This module provides the views for Flask-Bitmapist's web interface.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

import os

from datetime import datetime

from bitmapist import get_event_names, DayEvents, WeekEvents, MonthEvents, YearEvents

from flask import Blueprint, render_template


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
    return render_template('bitmapist/data.html', events=get_event_names(), day_events=day_events, week_events=week_events, month_events=month_events, year_events=year_events)


@bitmapist_bp.route('/events')
def events():
    return str(get_event_names())
