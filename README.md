Flask-Bitmapist
==============

Flask extension that creates a simple interface to the Bitmapist analytics library.


About
------------

[Bitmapist](https://github.com/Doist/bitmapist) is,
> [A] Python library makes it possible to implement real-time, highly scalable analytics that can answer following questions:
    <br>
    - Has user 123 been online today? This week? This month? <br>
    - Has user 123 performed action "X"? <br>
    - How many users have been active have this month? This hour? <br>
    - How many unique users have performed action "X" this week? <br>
    - How many % of users that were active last week are still active? <br>
    - How many % of users that were active last month are still active this month? <br>
    - What users performed action "X"? <br>


Installation
------------

    pip install flask-bitmapist


Usage
-----

example app;

```Python
from flask import Flask
from flask_bitmapist import FlaskBitmapist, mark

app = Flask(__name__)

flaskbitmapist = FlaskBitmapist()
flaskbitmapist.init_app(app)

@app.route('/')
@mark('index:visited', 1)
def index():
    """using the mark decoarator, the first argument is the event and the second is the id of the current_user"""
    return 'hello world'

if __name__ == '__main__':
    app.run()
```

For documentation on the `mark` decorator, look at the [`mark_event`](https://github.com/Doist/bitmapist#examples) function of Bitmapist.


Config
-----

| Name                     | Type      | Description        |
| ----                     | -------   | -------------------|
| `BITMAPIST_REDIS_SYSTEM` | `string`  | Name of Redis System, defaults to `system` |
| `BITMAPIST_REDIS_URL`    | `string`  | URL to connect to Redis server, defaults to `redis://localhost:6379` |
| `BITMAPIST_TRACK_HOURLY` | `boolean` | tells Bitmapist to track hourly, can also be passed to `mark`,<br> ex: `@mark('active', 1, track_hourly=False)` |


Cohort Blueprint
-----

One of the nice things about Bitmapist is it's simple bit operations API and the data cohort that you get.
For more information about the cohort, visit the [Bitmapist README](https://github.com/Doist/bitmapist#bitmapist-cohort)

When you initialize the `flask-bitmapist` extension a blueprint is registered with the application.

| Name     | Path                 | Description        |
| ----     | -------              | -------------------|
| `index`  | `/bitmapist/`        | returns bitmapist index |
| `events` | `/bitmapist/events`  | returns all bitmapist events |