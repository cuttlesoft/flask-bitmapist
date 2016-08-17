.. flask-bitmapist documentation master file, created by
   sphinx-quickstart on Mon Aug 15 15:57:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Bitmapist's documentation!
===========================================

Contents:

.. toctree::
   :maxdepth: 2


Flask extension that creates a simple interface to the Bitmapist analytics library.

Flask-Bitmapist is a flexible system which allow easy tracking of user activity
such as logging in/out, being created/updated/deleted.

It creates events using an event name and the user id.

There are four different ways to mark events in your Flask app:

Use a decorator above a function::

  >>> @mark('user:logged_in', user.id)

Use the `Bitmapistable` ORM mixin (current support only for SQLAlchemy) `may
need more explanation on how this works??`::

  >>> class User(db.Model, Bitmapistable):

The flask_login extension automatically marks login/logout events::

  >>> flask_login.login_user(user)

Or just call the mark_event function directly::

  >>> mark_event('user:logged_in', user.id)

Quickstart
==========

Installation
------------

Install the extension using pip::

  $ pip install flask_bitmapist

Initialization
--------------
Marking a user-based event is very simple with the flask_bitmapist module.

Begin by importing the FlaskBitmapist class and initializing the app as a
flask_bitmapist application (this will need to be a flask application)::

  from flask import Flask
  from flask_bitmapist import FlaskBitmapist

  # create Flask app object
  app = Flask(__name__)

  # initialize bitmapist with the app object
  flaskbitmapist = FlaskBitmapist()
  flaskbitmapist.init_app(app)

You are then free to use the method best suited for your application to start
marking events.

Usage
-----

Decorator
^^^^^^^^^

Usage of the @mark() decorator can be useful when you want to track
interaction with a certain function that does not deal directly with the model
(like a view or api ??).

To use the decorator, import the mark function::

  from flask_bitmapist import mark

Then, put the decorator above any function you wish to track, along with the
event name and the user id::

  @mark('index:visited', current_user.id)
  def index():
    return render_template('index.html')

Mixin
^^^^^

The mixin can be used to track when the user is created, updated, or deleted. It
interacts directly with the ORM to register events on insert, update, or delete.

To use the mixin, import the Bitmapistable class::

  from flask_bitmapist import Bitmapistable

Then insert it into the User class::

  class User(db.Model, Bitmapistable):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

The event 'user:created' will then be registered when a new user is instantiated
and committed to the db::

  user = User(name='Test User')
  db.session.add(user)
  db.session.commit()

Flask Login
^^^^^^^^^^^

mark_event Function
^^^^^^^^^^^^^^^^^^^

.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.


Small Example App
=================

Let's start by creating a simple app::

  from flask import Flask
  from flask_bitmapist import FlaskBitmapist, mark

  app = Flask(__name__)

  flaskbitmapist = FlaskBitmapist()
  flaskbitmapist.init_app(app)

  @app.route('/')
  @mark('index:visited', 1)
  def index():
    """using the mark decorator, the first argument is the event and the second is the id of the current_user"""
    return 'hello world'

  if __name__ == '__main__':
    app.run()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
