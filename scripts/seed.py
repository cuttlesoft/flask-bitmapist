# -*- coding: utf-8 -*-

""" Seed redis database with 10,000 entries.

Entries consist of random user id between 0-99, event of "user_logged_in",
and timestamp between now and 3 years ago.

Redis server must be running.
"""

import random
import time
import datetime
from random import choice, randint

from bitmapist import mark_event

now = datetime.datetime.now()
days_in_year = 364.24
years = 3
years_ago = now - datetime.timedelta(days=(days_in_year*3))


def str_time_prop(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(start.timetuple())
    etime = time.mktime(end.timetuple())

    ptime = stime + prop * (etime - stime)

    return datetime.datetime.strptime(time.strftime(format, time.localtime(ptime)), format)



def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y/%m/%d %I:%M:%S', prop)


for _ in range(10000):
    rand_date = random_date(now, years_ago, random.random())
    user_id = randint(0, 99)

    events = ['user_logged_in', 'user_logged_out',
              'user_inserted', 'user_updated', 'user_deleted',
              'note_inserted']

    mark_event(choice(events), user_id, now=rand_date)
