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


# def get_dates_data(event_filters, time_group='days', system='default',
#                    as_percent=True, num_cols=10, num_rows=20):
def get_cohort(primary_event, secondary_event, additional_events=[],
               time_group='days', system='default',
               as_percent=True, num_cols=10, num_rows=20):
    """
    Fetch the data from bitmapist.
    :param :primary_event Name of primary event for defining cohort
    :param :secondary_event Name of secondary event for defining cohort
    :param :additional_events List of additional event names by which to filter cohort
    :param :time_group Time scale by which to group results; can be `days`, `weeks`, `months`, `years`
    :param :system Which bitmapist should be used
    :param :as_percent Whether to calculate and show percents
    :param :num_cols How many results cols to get; corresponds to how far forward to get results from each time point
    :param :num_rows How many results rows to get; corresponds to how far back to get results from current time
    :return A list of day data, formated like `[[datetime, total, event counts...], ...]`
    # :return Dict with four lists (with matching indices); time point dates, time point totals, time point averages, and cohort data
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

    num_cols = int(num_cols)
    num_rows = int(num_rows)
    time_points = num_rows

    event_time = datetime.utcnow() - relativedelta(**{ time_group: time_points - 1 })  # WHY - 1 # maybe counting deltas between time points?
    increment_delta = lambda t: relativedelta(**{ time_group: t })

    if time_group == 'months':
        event_time -= relativedelta(days=event_time.day - 1) # WHY

    # WIP ~ REFACTORED TO HERE

    # TEMPORARY ASSIGNMENTS
    # select1 = event_filters[0]
    # select2 = event_filters[1]
    # select1b = event_filters[2] if len(event_filters) >= 3 else None
    # select2b = event_filters[3] if len(event_filters) >= 4 else None
    # END TEMP ASSIGNMENTS
    # primary = event_filters[0]
    # secondary = event_filters[1]
    # additional = event_filters[2:]

    dates = []
    # date_totals = []
    # date_averages = []
    # cohort = []

    for i in range(time_points):

        # Events for primary event name
        primary_events = fn_get_events(primary_event, event_time, system)
        # if select1b:
        #     select1b_events = fn_get_events(select1b, event_time, system)
        #     primary_events = BitOpAnd(system, primary_events, select1b_events)
        primary_total = len(primary_events)

        # `result` will be an array including event counts at each interval from the current time point:
        #     result[0]  = datetime for the current time point
        #     result[1]  = event total for the current time point
        #     result[2:] = [event results for each col/step from current time point]
        result = [event_time, primary_total]

        # Move in time
        for j in range(0, num_cols + 1):  # WHY + 1 # maybe to include the initial time point + num_cols additional time points
            if primary_total == 0:
                # no events for current time point
                # TODO: move this to outside loop so loop can be skipped if none
                result.append('')
                continue

            incremented_time = event_time + increment_delta(j)

            # Events for secondary event name
            secondary_events = fn_get_events(secondary_event, incremented_time, system)
            # if select2b:
            #     select2b_events = fn_get_events(select2b, delta_now, system)
            #     select2_events = BitOpAnd(system, select2_events, select2b_events)


            # TODO: chain events here maybe?


            if not secondary_events.has_events_marked():
                result.append('')
                continue

            both_events = BitOpAnd(system, primary_events, secondary_events)
            both_total = len(both_events)

            # Append to result
            if as_percent:
                both_percent = float(both_total) / primary_total * 100
                result.append(both_percent)
            else:
                result.append(both_total)

        dates.append(result)
        event_time += increment_delta(1)

    # Clean up results of BitOps
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
