# -*- coding: utf-8 -*-
"""
    flask_bitmapist
    ~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details
"""

from core import FlaskBitmapist
from decorators import mark
from utils import chain_events, get_cohort, get_event_data

from bitmapist import (mark_event, unmark_event,
                       MonthEvents, WeekEvents, DayEvents, HourEvents,
                       BitOpAnd, BitOpOr, get_event_names)


__version__ = '0.1.0'
__versionfull__ = __version__

__all__ = ['FlaskBitmapist', 'mark', 'mark_event', 'unmark_event',
           'MonthEvents', 'WeekEvents', 'DayEvents', 'HourEvents',
           'BitOpAnd', 'BitOpOr', 'get_event_names',
           'chain_events', 'get_cohort', 'get_event_data']
