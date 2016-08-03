# -*- coding: utf-8 -*-
"""
    flask_bitmapist.mixins
    ~~~~~~~~~~~~~~~~~~~~
    Mixins for bitmapist.

    :copyright: (c) 2016 by Cuttlesoft, LLC.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy import event

from bitmapist import mark_event


class Bitmapistable(object):
    """A mixin class to make a model Bitmapist-ready."""

    @staticmethod
    def bitmapist_after_insert(mapper, connection, target):
        mark_event('%s_inserted' % target.__class__.__name__.lower(), target.id)

    @staticmethod
    def bitmapist_before_update(mapper, connection, target):
        mark_event('%s_updated' % target.__class__.__name__.lower(), target.id)

    @staticmethod
    def bitmapist_before_delete(mapper, connection, target):
        mark_event('%s_deleted' % target.__class__.__name__.lower(), target.id)

    @classmethod
    def __declare_last__(self):
        event.listen(self, 'after_insert', self.bitmapist_after_insert)
        event.listen(self, 'before_update', self.bitmapist_before_update)
        event.listen(self, 'before_delete', self.bitmapist_before_delete)
