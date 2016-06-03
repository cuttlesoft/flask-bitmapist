# -*- coding: utf-8 -*-
"""
    flask_bitmapist.decorators
    ~~~~~~~~~~~~~~~~~~~~
    Function decorators for bitmapist.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

from functools import wraps

from bitmapist import mark_event


def mark(event_name, uuid, system='default', now=None, track_hourly=None, use_pipeline=True):
    """
    A wrapper around bitmapist.mark_event

    Marks an event for hours, days, weeks and months.

    :param :event_name The name of the event, could be "active" or "new_signups"

    :param :uuid An unique id, typically user id. The id should not be huge,
        read Redis documentation why (bitmaps)

    :param :system The Redis system to use (string, Redis instance, or Pipeline
        instance).

    :param :now Which date should be used as a reference point, default is
        `datetime.utcnow()`

    :param :track_hourly Should hourly stats be tracked, defaults to
        bitmapist.TRACK_HOURLY

    :param :use_pipeline Boolean flag indicating if the command should use
        pipelines or not. You may want to avoid using pipeline within the
        command if you provide the pipeline object in `system` argument and
        want to manage the pipe execution yourself.
    """

    # print('called with', event_name)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            mark_event(event_name, uuid, system, now, track_hourly, use_pipeline)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
