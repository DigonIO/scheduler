# scheduler

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/scheduler)
[![license](https://img.shields.io/pypi/l/imgreg)](https://gitlab.com/DigonIO/imgreg/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/scheduler/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/scheduler/badges/master/coverage.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-scheduler/badge/?version=latest)](https://python-scheduler.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

A simple in-process python scheduler library, designed to be integrated seamlessly with the `datetime` standard library. Due to the support of `datetime` objects, `scheduler` is able to work with time zones. This implementation enables the planning of `Job` s depending on time cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

---

## Features

+ Easy and user friendly in-process `Job` scheduling [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#general-job-scheduling)
  + Create recurring `Job`s by given date, time, weekday, ...
  + Create recurring `Job`s with a given timedelta
  + Oneshot `Job`s
  + Passing of parameters to `Job`
+ Timezone compatibility [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#how-to-use-time-zones)
+ `Job` prioritization with linear weighting [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#weights)
+ Limit and track the `Job` execution count [(example)](https://python-scheduler.readthedocs.io/en/latest/examples.html#how-to-use-time-zones)
+ `datetime` compatibility
+ Lightweight
+ High test coverage
+ [Online documentation](https://python-scheduler.readthedocs.io/en/latest/index.html)

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

---

## Example: *How to schedule Jobs*

Some basics are presented here. For advanced scheduling examples please visit the online [documentation](https://python-scheduler.readthedocs.io/en/latest/examples.html). The following example shows how the `Scheduler` is instantiated and how cyclic `Job`s are created:

[//]: # (This example is not directly included in the testing environment. Make sure to also update the corresponding test in tests/test_readme.py when updating the following example.)

```py
import time
import datetime as dt
from scheduler import Scheduler, Weekday

def foo(msg = "bar"):
    print(msg)

sch = Scheduler()

sch.schedule(foo, dt.timedelta(minutes=10))  # every 10 minutes
sch.schedule(foo, dt.time(hour=16, minute=45))  # every day at 16:45
sch.schedule(foo, Weekday.MONDAY)  # every monday at 00:00

# every monday at 16:45
sch.schedule(
    foo,
    (Weekday.MONDAY, dt.time(hour=16, minute=45)),
)

# every friday at 00:00, every 10 minutes and every monday at 16:45
sch.schedule(
    foo,
    [
        Weekday.FRIDAY,
        dt.timedelta(minutes=10),
        (Weekday.MONDAY, dt.time(hour=16, minute=45)),
    ],
)
```

Besides cyclic `Job`s, oneshot `Job`s can also be easily created:

```py
sch.once(foo, dt.datetime(year=2021, month=2, day=11))  # at given datetime
sch.once(foo, dt.timedelta(minutes=10))  # in 10 minutes
```

`Scheduler` has support for calling scheduled functions with parameters:

```py
sch.once(foo, dt.timedelta(seconds=10000), params={"msg": "fizz"})
sch.schedule(foo, dt.timedelta(minutes=1), params={"msg": "buzz"})
```

A human readable overview of the scheduled jobs can be created by a simple `print` statement:

```py
print(sch)
```

```text
max_exec=inf, timezone=None, #jobs=9, weight_function=linear_weight_function

function               due at        timezone        due in      attempts weight
---------------- ------------------- ------------ --------- ------------- ------
foo              2021-02-11 00:00:00 None         -122 days           0/1      1
foo              2021-06-12 23:30:01 None           0:00:59         0/inf      1
foo              2021-06-12 23:39:01 None           0:09:59         0/inf      1
foo              2021-06-12 23:39:01 None           0:09:59         0/inf      1
foo              2021-06-12 23:39:01 None           0:09:59           0/1      1
foo              2021-06-13 02:15:41 None           2:46:39           0/1      1
foo              2021-06-13 16:45:00 None          17:15:58         0/inf      1
foo              2021-06-14 00:00:00 None             1 day         0/inf      1
foo              2021-06-14 16:45:00 None             1 day         0/inf      1
```

Executing pending `Job`s periodically can be achieved with a simple loop:

```py
while True:
    sch.exec_jobs()
    time.sleep(1)
```

---

## Build the documentation

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
pytest --doctest-modules doc/examples.rst
```

## TODO

+ Features
  + Support of monthly recurring `Job`s (e.g. every second Monday in June and October)
  + Add `__repr__` and `__str__` methods to `Scheduler`
  + Optional `Job` flag: Discard missed executions befor the last pending execution
  + Execute a `Job` until a certain datetime stamp
  + Thread safety and background tasks
+ Documentation
  + Notes on performance
  + Comparison to [APScheduler](https://github.com/agronholm/apscheduler) and [schedule](https://github.com/dbader/schedule)
  + where to get help
  + FAQ

---

## License

This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
