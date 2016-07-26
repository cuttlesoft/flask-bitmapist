# -*- coding: utf-8 -*-

# from flask.ext.login import user_logged_in
from flask.ext.user import user_logged_in

from flask_bitmapist import mark_event


@user_logged_in.connect_via(app)
def _after_login_hook(sender, user, **extra):
    print 'HOOK'
    mark_event('user_logged_in', user.id)
