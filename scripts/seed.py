# -*- coding: utf-8 -*-

""" Seed Redis database with ~10,000 entries.

Entries consist of random user id between 0-99, user event,
and timestamp between now and 3 years ago.

Redis server must be running.
"""

import calendar
from datetime import date, datetime, timedelta
from random import choice, randint
import time

from bitmapist import mark_event


now = datetime.utcnow()
earliest = now - timedelta(days=(365 * 3))


class TimeTravelError(Exception):
    pass


def mark_user_event(user_event, user_id, event_date):
    # to abstract out naming convention, easily prevent future events, and debug
    if event_date > now.date():
        raise TimeTravelError('date has not yet come to pass (%s)' % event_date)

    event_name = 'user:%s' % user_event
    mark_event(event_name, user_id, now=event_date)
    # print '#%s - %s @ %s' % (user_id, event_name, event_date)


def likelihood(n):
    return randint(1, 10) <= n


def probably():
    return likelihood(7)


def maybe():
    return likelihood(5)


def probably_not():
    return likelihood(3)


def random_date(starting_date=None):
    starting_date = starting_date or earliest
    # ordinal dates are easier to pick random between
    start_date = starting_date.toordinal()
    end_date = now.toordinal()
    return date.fromordinal(randint(start_date, end_date))


def time_hop(event_date, minutes=None, days=None, months=None):
    # add random minutes/days/months up to the number of each provided  # kwargs
    if minutes:
        event_date = event_date + timedelta(minutes=randint(1, minutes))
    if days:
        event_date = event_date + timedelta(days=randint(1, days))
    if months:
        days_for_months = randint(1, months) * 365 / 12
        event_date = event_date + timedelta(days=days_for_months)
    return event_date


def hop_times():
    hop_times = {'minutes': randint(0, 3000), 'days': randint(0, 30)}
    hop_times['months'] = randint(1, 3) if probably_not() else 0
    return hop_times


def random_action(user_id, event_date):
    # TODO: super rudimentary... make less so?
    hop_date = time_hop(event_date, **hop_times())

    door_number = randint(0, 8)

    if door_number <= 4:
        # simulate simple, single events
        simple_events = [
            'updated',
            'updated_profile',
            'reset_password',
            'created_comment',
            'uploaded_avatar'
        ]
        mark_user_event(simple_events[door_number], user_id, hop_date)

    elif door_number == 5:
        # simulate user potentially reading product reviews, adding product
        # to cart, and potentially purchasing product
        if maybe():
            mark_user_event('product - read reviews', user_id, hop_date)
            hop_date = time_hop(hop_date, minutes=300)

        mark_user_event('product - added to cart', user_id, hop_date)

        if maybe():
            hop_date = time_hop(hop_date, minutes=300)
            mark_user_event('product - purchased', user_id, hop_date)


    elif door_number == 6:
        # simulate user looking for answers to an issue they are having;
        # all, some, or none of these events might occur
        potential_events = ['searched_faq',
                            'submitted_bug_report',
                            'contacted_support']
        hop_date = independent(user_id, hop_date, potential_events)

    elif door_number == 7:
        # simulate user progressing some distance through tracks with increasing
        # difficulty (sequence not necessarily completed)
        sequence_steps = ['completed_introductory_track',
                          'completed_beginner_track',
                          'completed_intermediate_track',
                          'completed_advanced_track',
                          'completed_expert_track']
        hop_date = sequence(user_id, hop_date, sequence_steps)

    elif door_number == 8:
        # simulate user logging out and, later, logging in again
        sequence_steps = ['logged_out', 'logged_in']
        hop_date = sequence(user_id, hop_date, sequence_steps, required=True)

    return hop_date


# random action (6)
def independent(user_id, action_date, potential_events, required=False):
    for event_name in potential_events:
        if required or probably():
            sub_date = time_hop(action_date, minutes=300)
            mark_user_event(event_name, user_id, sub_date)
    return action_date


# random action (7, 8)
def sequence(user_id, action_date, sequence_steps, required=False):
    mark_user_event(sequence_steps[0], user_id, action_date)
    for step in sequence_steps[1:]:
        if required or maybe():
            action_date = time_hop(action_date, **hop_times())
            mark_user_event(step, user_id, action_date)
        else:
            return action_date
    return action_date


# # for fun (completion-required sequence)
# def stop_drop_and_roll(user_id, action_date):
#     sequence_steps = ['stopped', 'dropped', 'rolled']
#     return sequence(user_id, action_date, sequence_steps, required=True)


def create_user_from_campaign(user_id, event_date):
    campaigns = ['adwords', 'facebook', 'twitter']
    campaign = 'signed_up_via_%s' % choice(campaigns)
    mark_user_event(campaign, user_id, event_date)


def tell_user_story(user_id):
    event_date = random_date()

    try:
        # signed up
        mark_user_event('created', user_id, event_date)
        if maybe():
            # probably signed up via ad campaign
            create_user_from_campaign(user_id, event_date)

        # logged in soon after
        event_date = time_hop(event_date, minutes=300)
        mark_user_event('logged_in', user_id, event_date)

        # took some number of actions over time
        for i in range(randint(10, 100)):
            event_date = random_action(user_id, event_date)

        # probably logged out
        if probably():
            event_date = time_hop(event_date)
            mark_user_event('logged_out', user_id, event_date)

        # probably not - but maybe - deleted
        if likelihood(1):
            event_date = time_hop(event_date)
            mark_user_event('deleted', user_id, event_date)

    except TimeTravelError as e:
        # print 'TimeTravelError: %s' % e
        pass


for i in range(1000):
    tell_user_story(i + 1)
