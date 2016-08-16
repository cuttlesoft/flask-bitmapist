.. flask-bitmapist documentation master file, created by
   sphinx-quickstart on Mon Aug 15 15:57:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to flask-bitmapist's documentation!
===========================================

Contents:

.. toctree::
   :maxdepth: 2

General Description
-------------------

Flask extension that creates a simple interface to the Bitmapist analytics library.

Flask-Bitmapist allows easy tracking of user activity such as logging in/out,
being created/updated/deleted.

Quick Start
-----------

Installation
^^^^^^^^^^^^

Install the extension using pip::

  $ pip install flask-bitmapist

Usage
^^^^^

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
