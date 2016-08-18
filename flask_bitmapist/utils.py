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


def get_cohort(primary_event_name, secondary_event_name,
               additional_events=[], time_group='days',
               num_rows=10, num_cols=10, system='default'):
    """
    Fetch the data from bitmapist for the cohort.
    :param :primary_event_name Name of primary event for defining cohort
    :param :secondary_event_name Name of secondary event for defining cohort
    :param :additional_events List of additional event names + operations by which to filter cohort
    :param :time_group Time scale by which to group results; can be `days`, `weeks`, `months`, `years`
    :param :num_rows How many results rows to get; corresponds to how far back to get results from current time
    :param :num_cols How many results cols to get; corresponds to how far forward to get results from each time point
    :param :system Which bitmapist should be used
    :return Tuple of (list of lists of cohort results, list of dates for cohort, primary event total for each date)
    """

    cohort = []
    dates = []
    primary_event_totals = []  # for percents

    fn_get_events = _events_fn(time_group)

    # TIMES

    event_time = datetime.utcnow() - relativedelta(**{ time_group: num_rows - 1 })  # - 1 for deltas between time points (?)
    increment_delta = lambda t: relativedelta(**{ time_group: t })

    if time_group == 'months':
        event_time -= relativedelta(days=event_time.day - 1)  # (?)

    # COHORT

    for i in range(num_rows):
        # get results for each date interval from current time point for the row
        row = []
        primary_event = fn_get_events(primary_event_name, event_time, system)

        primary_total = len(primary_event)
        primary_event_totals.append(primary_total)

        dates.append(event_time)

        if not primary_total:
            row = [None] * num_cols
            continue

        for j in range(num_cols):
            # get results for each event chain for current incremented time
            incremented = event_time + increment_delta(j)

            chained_events = chain_events(secondary_event_name,
                                          additional_events,
                                          incremented, time_group, system)

            if chained_events:
                combined_events = BitOpAnd(chained_events, primary_event)
                combined_total = len(combined_events)
            else:
                combined_total = None

            row.append(combined_total)

        cohort.append(row)
        event_time += increment_delta(1)

    # Clean up results of BitOps
    delete_runtime_bitop_keys()

    return cohort, dates, primary_event_totals


def chain_events(base_event_name, events_to_chain, time_point, time_group,
                 system='default'):
    """
    Chain additional events with base set of events
    :param :base_event_name Name of event to chain additional events to/with
    :param :events_to_chain List of additional event names to chain
    :param :time_point Point in time at which to get events (i.e., `now` argument)
    :param :time_group Time scale by which to group results; can be `days`, `weeks`, `months`, `years`
    :param :system Which bitmapist should be used
    :return
    """

    fn_get_events = _events_fn(time_group)
    base_event = fn_get_events(base_event_name, time_point, system)

    if not base_event.has_events_marked():
        return ''

    if events_to_chain:
        chain_events = []

        # for idx, event_to_chain in enumerate(events_to_chain):
        for event_to_chain in events_to_chain:
            event_name = event_to_chain.get('name')
            chain_event = fn_get_events(event_name, time_point, system)
            chain_events.append(chain_event)

        # Each OR should operate only on its immediate predecessor, e.g.,
        #     `A && B && C || D` should be handled as ~ `A && B && (C || D)`,
        #     and
        #     `A && B || C && D` should be handled as ~ `A && (B || C) && D`.
        op_or_indices = [idx for idx, e in enumerate(events_to_chain) if e['op'] == 'or']

        # Work backwards; least impact on operator combos + list indexing
        for idx in reversed(op_or_indices):
            # If first of events to chain, OR will just operate on base event
            if idx > 0:
                prev_event = chain_events[idx - 1]
                or_event = chain_events.pop(idx)

                # OR events should not be re-chained below
                events_to_chain.pop(idx)

                chain_events[idx - 1] = BitOpOr(prev_event, or_event)


        for idx, name_and_op in enumerate(events_to_chain):
            if name_and_op.get('op') == 'or':
                base_event = BitOpOr(base_event, chain_events[idx])
            else:
                base_event = BitOpAnd(base_event, chain_events[idx])

    return base_event


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
