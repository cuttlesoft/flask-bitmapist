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
                       BitOpAnd, BitOpOr, delete_runtime_bitop_keys)


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


def get_cohort(primary, secondary, additional=[], time_group='days',
               num_rows=10, num_cols=10, as_percent=True,
               system='default'):
    """
    Fetch the data from bitmapist for the cohort.
    :param :primary Name of primary event for defining cohort
    :param :secondary Name of secondary event for defining cohort
    :param :additional List of additional event names by which to filter cohort
    :param :time_group Time scale by which to group results; can be `days`, `weeks`, `months`, `years`
    :param :num_rows How many results rows to get; corresponds to how far back to get results from current time
    :param :num_cols How many results cols to get; corresponds to how far forward to get results from each time point
    :param :as_percent Whether to calculate and show percents
    :param :system Which bitmapist should be used
    :return A list of lists, not unlike a matrix, containing the cohort results
    # :return A list of day data, formated like `[[datetime, total, event counts...], ...]`
    # :return Dict with four lists (with matching indices); time point dates, time point totals, time point averages, and cohort data
    """

    cohort = []
    dates = []
    row_totals = []  # totals for each row
    col_totals = []  # totals for each col; sum through loops, used for averages
    # averages = []

    fn_get_events = _events_fn(time_group)

    # TIMES

    if time_group == 'years':
        # Three shall be the number thou shalt count, and the number of the
        # counting shall be three. Four shalt thou not count, neither count thou
        # two, excepting that thou then proceed to three. Five is right out.
        num_rows = 3

    event_time = datetime.utcnow() - relativedelta(**{ time_group: num_rows - 1 })  # WHY - 1 # maybe counting deltas between time points?
    increment_delta = lambda t: relativedelta(**{ time_group: t })

    if time_group == 'months':
        event_time -= relativedelta(days=event_time.day - 1) # WHY

    # COHORT

    for i in range(num_rows):
        # get results for each date interval from current time point for the row
        row = []
        primary_events = fn_get_events(primary, event_time, system)
        primary_total = len(primary_events)

        dates.append(event_time)
        row_totals.append(primary_total)

        if not len(primary_events):
            row = [''] * cols
            continue

        for j in range(num_cols):
            # get results for each event chain for current incremented time
            incremented = event_time + increment_delta(j)

            chained_events = chain_events(secondary, additional,
                                          incremented, time_group, system)

            combined_events = BitOpAnd(primary_events, chained_events,
                                      'and', system)

            combined_total = len(combined_events)
            # if as_percent:
            #     combined_total = float(combined_total) / primary_total * 100

            row.append(combined_total)

        cohort.append(row)
        event_time += increment_delta(1)

    # Clean up results of BitOps
    delete_runtime_bitop_keys()

    return cohort, dates


def chain_events(base, additional, time_pt, time_group, system='default'):
    """
    Chain additional events with base set of events
    :param :base Name of event to chain additional events to/with
    :param :additional_events List of additional event names to chain
    :param :time_pt Point in time at which to get events (i.e., `now` argument)
    :param :time_group Time scale by which to group results; can be `days`, `weeks`, `months`, `years`
    :param :system Which bitmapist should be used
    :return
    """

    fn_get_events = _events_fn(time_group)
    base_events = fn_get_events(base, time_pt, system)

    if not base_events.has_events_marked():
        return ''

    if additional:
        for idx, additional_event in enumerate(additional):
            event_name = additional_event.get('name')
            bitmapist_events = fn_get_events(event_name, time_pt, system)
            additional[idx]['events'] = bitmapist_events

        # Each OR should operate only on its immediate predecessor, e.g.,
        #     `A && B && C || D` should be handled as ~ `A && B && (C || D)`,
        #     and
        #     `A && B || C && D` should be handled as ~ `A && (B || C) && D`.
        or_event_indices = [idx for idx, e in enumerate(additional) if e['op'] == 'or']

        for idx in reversed(or_event_indices):
            # If first event, OR will operate on base event as normal
            if idx > 0:
                prev_event = additional[idx - 1].get('events')
                or_event = additional.pop(idx).get('events')

                combined_events = BitOpOr(system, prev_event, or_event)
                additional[idx - 1]['events'] = combined_events

        for additional_event in additional:
            events = additional_event.get('events')
            if additional_event.get('op') == 'or':
                base_events = BitOpOr(system, base_events, events)
            else:
                base_events = BitOpAnd(system, base_events, events)

    return base_events


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
