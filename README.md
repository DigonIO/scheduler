# scheduler

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/scheduler)
[![license](https://img.shields.io/pypi/l/scheduler)](https://gitlab.com/DigonIO/scheduler/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/scheduler/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/scheduler/badges/master/coverage.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-scheduler/badge/?version=latest)](https://python-scheduler.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

A simple in-process python scheduler library, designed to be integrated seamlessly with the `datetime` standard library. Due to the support of `datetime` objects, `scheduler` is able to work with time zones. This implementation enables the planning of `Job` s depending on time cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

## Features

1. Easy and user friendly in-process `Job` scheduling [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#general-job-scheduling)
  1. Create recurring `Job`s by given date, time, datetime, weekday, ...
  2. Create recurring `Job`s with a given timedelta
  3. Oneshot `Job`s
  4. Passing of parameters to `Job`
2. Timezone compatibility [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#how-to-use-time-zones)
3. `Job` prioritization with linear weighting [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#weights)
4. Limit and track the `Job` execution count [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#how-to-use-time-zones)
5. Lightweight
6. High test coverage
7. [Online documentation](https://python-scheduler.readthedocs.io/en/latest/index.html)

## Installation

`scheduler` can be installed using pip with the following command:

```bash
pip install git+https://gitlab.com/DigonIO/scheduler.git
```

Alternatively clone the [repository](https://gitlab.com/DigonIO/scheduler) and install with:

```bash
git clone https://gitlab.com/DigonIO/scheduler.git
cd scheduler
pip install .
```

## Example: *How to schedule Jobs*

Some basics are presented here. For advanced scheduling examples please visit the online [documentation](https://python-scheduler.readthedocs.io/en/latest/examples.html). The following example shows how the `Scheduler` is instantiated and how cyclic `Job`s are created:

[//]: # (This example is not directly included in the testing environment. Make sure to also update the corresponding test in tests/test_readme.py when updating the following example.)

```py
import time
import datetime as dt
from scheduler import Scheduler, Weekday

def foo():
    print("foo")

def bar(msg = "bar"):
    print(msg)

sch = Scheduler()

sch.cyclic(dt.timedelta(minutes=10), foo)

sch.minutely(dt.time(second=15), bar)
sch.hourly(dt.time(minute=30, second=15), foo)
sch.daily(dt.time(hour=16, minute=30), bar)
sch.weekly(Weekday.MONDAY, foo)
sch.weekly((Weekday.MONDAY, dt.time(hour=16, minute=30)), bar)

sch.once(dt.timedelta(minutes=10), foo)
sch.once(Weekday.MONDAY, bar)
sch.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)
```

A human readable overview of the scheduled jobs can be created with a simple `print` statement:

```py
print(sch)
```

```text
max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=9

type     function         due at                 due in      attempts weight
-------- ---------------- ------------------- --------- ------------- ------
MINUTELY bar(..)          2021-06-18 00:37:15   0:00:14         0/inf      1
CYCLIC   foo()            2021-06-18 00:46:58   0:09:58         0/inf      1
ONCE     foo()            2021-06-18 00:46:59   0:09:58           0/1      1
HOURLY   foo()            2021-06-18 01:30:15   0:53:14         0/inf      1
DAILY    bar(..)          2021-06-18 16:30:00  15:52:59         0/inf      1
WEEKLY   foo()            2021-06-21 00:00:00    2 days         0/inf      1
ONCE     bar(..)          2021-06-21 00:00:00    2 days           0/1      1
WEEKLY   bar(..)          2021-06-21 16:30:00    3 days         0/inf      1
ONCE     foo()            2022-02-15 00:45:00  242 days           0/1      1
```

Executing pending `Job`s periodically can be achieved with a simple loop:

```py
while True:
    sch.exec_jobs()
    time.sleep(1)
```

## Documentation

The API documentation can either be viewed [online](https://python-scheduler.readthedocs.io/en/latest/index.html) or be generated using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) formatting. To build, run:

```bash
sphinx-build -b html doc/ doc/_build/html
```

## Testing

Testing is done using [pytest](https://pypi.org/project/pytest/). Using [pytest-cov](https://pypi.org/project/pytest-cov/) and [coverage](https://pypi.org/project/coverage/) a report for the tests can be generated with:

```bash
pytest --cov=scheduler/ tests/
coverage html
```

To test the examples in the documentation run:

```bash
pytest --doctest-modules doc/examples/*
```

## TODO

1. Features
  1. Support of monthly recurring `Job`s (e.g. every second Monday in June and October)
  2. Execute a `Job` until a certain datetime stamp
  3. Thread safety and background tasks
2. Documentation
  1. Notes on performance
  2. Comparison to [APScheduler](https://github.com/agronholm/apscheduler) and [schedule](https://github.com/dbader/schedule)
  3. where to get help
  4. FAQ

## License

This software is published under the [LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).
