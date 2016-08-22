.. flask-bitmapist documentation master file, created by
   sphinx-quickstart on Mon Aug 15 15:57:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===============
Flask-Bitmapist
===============

.. toctree::
  :maxdepth: 2


Flask-Bitmapist is a Flask extension that creates a simple interface to the `Bitmapist <https://github.com/Doist/bitmapist>`_ analytics library.

Events are registered with the name of the event (e.g., "user:logged_in") and the object id (e.g., the logged in user's id).

There are four different ways to register events from your Flask app:
 * Call a function decorated with the ``@mark()`` decorator
 * Use the ``Bitmapistable`` mixin (note: current ORM support is limited to SQLAlchemy)
 * With the Flask-Login extension, user login/logout will register corresponding events automatically
 * Call the ``mark_event()`` function directly

To use the ``@mark()`` decorator::

  @mark('user:reset_password', user.id)
  def reset_password():
      pass


To use the ``Bitmapistable`` mixin::

  from flask_bitmapist import Bitmapistable

  class User(db.Model, Bitmapistable):
      pass

.. from flask_bitmapist import SQLAlchemyBitmapistable as Bitmapistable


If you are using Flask-Login, "user:logged_in" and "user:logged_out" events will be registered automatically on user login and user logout, respectively::

  >>> flask_login.login_user(user)
  >>> flask_login.logout_user(current_user)


You can also call the ``mark_event()`` function directly::

  >>> mark_event('user:action_taken', user.id)


Installation
============

Install the extension using pip::

  $ pip install flask_bitmapist


Quickstart
==========


Initialization
--------------
Marking a user-based event is very simple with Flask-Bitmapist.

Begin by importing FlaskBitmapist and initializing the FlaskBitmapist application (this will need to be a Flask app)::

  from flask import Flask
  from flask_bitmapist import FlaskBitmapist

  # create Flask app object
  app = Flask(__name__)

  # initialize flask_bitmapist with the app object
  flaskbitmapist = FlaskBitmapist()
  flaskbitmapist.init_app(app)


You are then free to use whichever method(s) you find best suited to your application for marking and registering events.


Configuration Options
---------------------

===========================   ========================================================   ========================
Configuration Options         Description                                                Default
===========================   ========================================================   ========================
BITMAPIST_REDIS_URL           Location where Redis server is running                     "redis://localhost:6379"
BITMAPIST_REDIS_SYSTEM        Name of Redis system to use for Bitmapist                  "default"
BITMAPIST_TRACK_HOURLY        Whether to track events down to the hour                   False
BITMAPIST_DISABLE_BLUEPRINT   Whether to disable registration of the default blueprint   False
===========================   ========================================================   ========================


Usage
-----

Decorator
^^^^^^^^^

Usage of the ``@mark()`` decorator can be useful when you want to track interactions that do not deal directly with the database model.

To use, import the decorator and attach it to the function, providing the event name and user id::

  from flask_bitmapist import mark

  @mark('index:visited', current_user.id)
  def index():
    return render_template('index.html')


Mixin
^^^^^

The mixin can be used to track when a user object is created, updated, or deleted. It interacts directly with the ORM to register events on insert, update, or delete.

To use, import the mixin and extend the desired class with it::

  from flask_bitmapist import Bitmapistable

  class User(db.Model, Bitmapistable):
    id = db.Column(db.Integer, primary_key=True)

The event "user:created" will then be registered when a new user is instantiated and committed to the database::

  user = User()
  db.session.add(user)
  db.session.commit()

Similarly, "user:updated" and "user:deleted" will be registered for a given user on updating and deleting, respectively.


Flask-Login
^^^^^^^^^^^

The Flask-Login extension is a common means of user management for many Flask applications. Flask-Bitmapist integrates with this extension to track user login/logout events automatically via its LoginManager and UserMixin::

  from flask_login import LoginManager, UserMixin

  class User(UserMixin):
      id = None

  login_manager = LoginManager()
  login_manager.init_app(app)

Create and log in the user, and the event "user:logged_in" will be registered automatically; the same works for logging out a user and the "user:logged_out" event::

  from flask_login import current_user, login_user, logout_user

  user = User(id=user_id)

  # login user
  login_user(user)

  # logout user
  logout_user(current_user)


Function Call
^^^^^^^^^^^^^

The most raw way to use Flask-Bitmapist is to directly call ``mark_event()``::

  from flask_bitmapist import mark_event

  mark_event('event:completed', current_user.id)



Small Example App
-----------------

Let's start by creating a simple app::

  from flask import Flask
  from flask_bitmapist import FlaskBitmapist, mark

  app = Flask(__name__)

  flaskbitmapist = FlaskBitmapist()
  flaskbitmapist.init_app(app)

  @app.route('/')
  @mark('index:visited', 1)  # current_user.id
  def index():
    """using the mark decorator, the first argument is the event
       and the second is the id of the current_user
    """
    return 'Hello, world!'

  if __name__ == '__main__':
    app.run()

API
===

.. .. automodule:: flask_bitmapist.utils
..  :members:

.. autofunction:: flask_bitmapist.utils.get_event_data
.. autofunction:: flask_bitmapist.utils.get_cohort
.. autofunction:: flask_bitmapist.utils.chain_events


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
