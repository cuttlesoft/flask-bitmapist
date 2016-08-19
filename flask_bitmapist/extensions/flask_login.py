# -*- coding: utf-8 -*-

from flask.ext.login import user_logged_in, user_logged_out

from bitmapist import mark_event


@user_logged_in.connect
def mark_login(sender, user, **extra):
    mark_event('user:logged_in', user.id)


@user_logged_out.connect
def mark_logout(sender, user, **extra):
    mark_event('user:logged_out', user.id)
