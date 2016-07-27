# -*- coding: utf-8 -*-

from flask.ext.login import user_logged_in

from flask_bitmapist import mark_event


@user_logged_in.connect  # vs .connect_via(app)
def mark_login(sender, user, **extra):
    mark_event('user_logged_in', user.id)
