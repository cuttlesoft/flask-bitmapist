# -*- coding: utf-8 -*-
"""
    flask_bitmapist.mixins
    ~~~~~~~~~~~~~~~~~~~~
    Mixins for bitmapist.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

# JUST FOR NOW
# try:
#     import SQLAlchemy
# except ImportError:
#     print('uh oh')
# from sqlalchemy.ext.declarative import declared_attr
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event

from bitmapist import mark_event

db = SQLAlchemy()


class Bitmapistable(db.Model):
    """A mixin class to make a model Bitmapist-ready."""

    __abstract__ = True

    def bitmapist_before_insert(self, *args, **kwargs):
        # mark_event(event_name, uuid, system, now, track_hourly, use_pipeline)
        mark_event('insert %s' % self.__name__, self.primary_key)

    def bitmapist_before_update(self, *args, **kwargs):
        # mark_event(event_name, uuid, system, now, track_hourly, use_pipeline)
        mark_event('update %s' % self.__name__, self.primary_key)

    def bitmapist_before_delete(self, *args, **kwargs):
        # mark_event(event_name, uuid, system, now, track_hourly, use_pipeline)
        mark_event('delete %s' % self.__name__, self.primary_key)

    def __declare_last__(self):
        event.listen(self, 'before_insert', self.bitmapist_before_insert)
        event.listen(self, 'before_update', self.bitmapist_before_update)
        event.listen(self, 'before_delete', self.bitmapist_before_delete)


# @event.listens_for(Bitmappable, 'before_insert', propagate=True)
# def bitmapist_before_insert(self, *args, **kwargs):
#     # mark_event(event_name, uuid, system, now, track_hourly, use_pipeline)
#     mark_event('insert %s' % self.__class__.__name__, self.primary_key)
