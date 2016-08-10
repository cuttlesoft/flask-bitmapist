# -*- coding: utf-8 -*-
"""
    flask_bitmapist.utils
    ~~~~~~~~~~~~~~~~~~~~~
    Generic utility functions.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from urlparse import urlparse

from dateutil.relativedelta import relativedelta

from bitmapist import (DayEvents, WeekEvents, MonthEvents, YearEvents,
                       BitOpAnd, delete_runtime_bitop_keys)


def _get_redis_connection(redis_url=None):
    url = urlparse(redis_url)
    return url.hostname, url.port


def get_event_data(event_name, time_group='days', now=None, system='default'):
    now = now or datetime.utcnow()
    return _events_fn(time_group)(event_name, now, system)


def _events_fn(time_group='days'):
    if time_group == 'days':
        return _day_events_fn
    elif time_group == 'weeks':
        # return _weeks_events_fn
        return _week_events_fn
    elif time_group == 'months':
        return _month_events_fn
    elif time_group == 'years':
        return _year_events_fn


# def get_cohort(...):
def get_dates_data(event_filters, time_group='days', system='default',
                   as_percent=1, num_results=25, num_of_rows=12):
    """
    Fetch the data from bitmapist.
    :param :event_filters List of event names by which to filter
    :param :time_group What is the data grouped by? Can be `days`, `weeks`, `months`, `years`
    :param :system What bitmapist should be used?
    :param :as_percent Whether to calculate and show percents
    :param :num_results ...
    :param :num_of_rows ...
    :return A list of day data, formated like `[[datetime, count], ...]`
    """

    fn_get_events = _events_fn(time_group)

    # diff from bitmapist: if 'days'/'weeks'/'months'/'years' each; only two
    #     time/group-specific adjustments differentiate conditions after
    #     switching 'days' from `timedelta` to `relativedelta` like the rest

    if time_group == 'years':
        # Three shall be the number thou shalt count, and the number of the
        # counting shall be three. Four shalt thou not count, neither count thou
        # two, excepting that thou then proceed to three. Five is right out.
        num_results = 3

    num_results = int(num_results)
    date_range = num_results

    now = datetime.utcnow() - relativedelta(**{ time_group: num_results - 1 })
    timedelta_inc = lambda t: relativedelta(**{ time_group: t })

    if time_group == 'months':
        # unsure of reasoning for this...
        now -= relativedelta(days=now.day - 1)

    # WIP ~ REFACTORED TO HERE

    dates = []

    for i in range(0, date_range):
        result = [now]

        # TEMPORARY ASSIGNMENTS
        select1 = event_filters[0]
        select2 = event_filters[1]
        select1b = event_filters[2] if len(event_filters) >= 3 else None
        select2b = event_filters[3] if len(event_filters) >= 4 else None
        # END TEMP ASSIGNMENTS

        # events for select1 (+select1b)
        select1_events = fn_get_events(select1, now, system)
        if select1b:
            select1b_events = fn_get_events(select1b, now, system)
            select1_events = BitOpAnd(system, select1_events, select1b_events)

        select1_count = len(select1_events)
        result.append(select1_count)

        # Move in time
        for t_delta in range(0, num_of_rows+1):
            if select1_count == 0:
                result.append('')
                continue

            delta_now = now + timedelta_inc(t_delta)

            # events for select2 (+select2b)
            select2_events = fn_get_events(select2, delta_now, system)
            if select2b:
                select2b_events = fn_get_events(select2b, delta_now, system)
                select2_events = BitOpAnd(system, select2_events, select2b_events)

            if not select2_events.has_events_marked():
                result.append('')
                continue

            both_events = BitOpAnd(system, select1_events, select2_events)
            both_count = len(both_events)

            # Append to result
            if both_count == 0:
                result.append(float(0.0))
            else:
                if as_percent:
                    result.append((float(both_count) / float(select1_count)) * 100)
                else:
                    result.append(both_count)

        dates.append(result)
        now = now + timedelta_inc(1)

    # clean up results of BitOps
    delete_runtime_bitop_keys()

    return dates


# PRIVATE methods: copied directly from Bitmapist because you can't import
# from bitmapist.cohort without also having mako for the cohort __init__

def _dispatch(key, cls, cls_args):
    # ignoring CUSTOM_HANDLERS
    return cls(key, *cls_args)


def _day_events_fn(key, date, system):
    cls = DayEvents
    cls_args = (date.year, date.month, date.day, system)
    return _dispatch(key, cls, cls_args)


def _week_events_fn(key, date, system):
    cls = WeekEvents
    cls_args = (date.year, date.isocalendar()[1], system)
    return _dispatch(key, cls, cls_args)


def _month_events_fn(key, date, system):
    cls = MonthEvents
    cls_args = (date.year, date.month, system)
    return _dispatch(key, cls, cls_args)


def _year_events_fn(key, date, system):
    cls = YearEvents
    cls_args = (date.year, system)
    return _dispatch(key, cls, cls_args)
