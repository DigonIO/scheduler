<p align="center">
  <a href="https://gitlab.com/DigonIO/scheduler"><img alt="scheduler" src="https://gitlab.com/DigonIO/scheduler/-/raw/master/doc/_assets/logo_name.svg" width="60%"></a>
</p>
<p>A simple in-process python scheduler library with timezone and threading support. Schedule tasks by their
time cycles, fixed times, weekdays, dates, weights, offsets and execution counts and automate Jobs.</p>

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/scheduler)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/scheduler)
[![license](https://img.shields.io/badge/license-LGPLv3-orange)](https://gitlab.com/DigonIO/scheduler/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/scheduler/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/scheduler/badges/master/coverage.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![Documentation Status](https://readthedocs.org/projects/python-scheduler/badge/?version=latest)](https://python-scheduler.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![pkgversion](https://img.shields.io/pypi/v/scheduler)](https://pypi.org/project/scheduler/)
[![versionsupport](https://img.shields.io/pypi/pyversions/scheduler)](https://pypi.org/project/scheduler/)
[![Downloads Week](https://pepy.tech/badge/scheduler/week)](https://pepy.tech/project/scheduler)
[![Downloads Total](https://pepy.tech/badge/scheduler)](https://pepy.tech/project/scheduler)
---


## Features

* Easy and user friendly in-process `Job` scheduling
[(Quick Start)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/quick_start.html)
  * Create recurring `Job`s by given date, time, datetime, weekday, ...
  * Create recurring `Job`s with a given timedelta
  * Oneshot `Job`s
  * Passing of parameters to `Job`
    [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/parameters.html)
* Timezone compatibility
  [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/timezones.html)
* Parallel `Job` execution with `threading` [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/threading.html)
* `Job` prioritization
  * Default linear prioritization
    [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/weights.html)
  * User definable prioritization functions
    [(Guide)](https://python-scheduler.readthedocs.io/en/latest/pages/guides/custom_prioritization.html)
* `Job` tagging
  [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/tags.html)
* `Job` batching
  [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/job_batching.html)
* `Job` metadata
  [(Example)](https://python-scheduler.readthedocs.io/en/latest/pages/examples/metrics.html)
* Lightweight
* High test coverage
* [Online documentation](https://python-scheduler.readthedocs.io/en/latest/index.html)

## Installation

`scheduler` can be installed using pip with the following command:

```bash
pip install scheduler
```

Alternatively clone the [repository](https://gitlab.com/DigonIO/scheduler) and install with:

```bash
git clone https://gitlab.com/DigonIO/scheduler.git
cd scheduler
pip install .
```

## Example: *How to schedule Jobs*

The following example shows how the `Scheduler` is instantiated and how basic `Job`s are created.
For advanced scheduling examples please visit the online
[documentation](https://python-scheduler.readthedocs.io/en/latest/examples.html).

[//]: # (This example is not directly included in the testing environment. Make sure to also update the corresponding test in tests/test_readme.py when updating the following example.)

```py
import datetime as dt
from scheduler import Scheduler
import scheduler.trigger as trigger

def foo():
    print("foo")

schedule = Scheduler()

schedule.cyclic(dt.timedelta(minutes=10), foo)

schedule.minutely(dt.time(second=15), foo)
schedule.hourly(dt.time(minute=30, second=15), foo)
schedule.daily(dt.time(hour=16, minute=30), foo)
schedule.weekly(trigger.Monday(), foo)
schedule.weekly(trigger.Monday(dt.time(hour=16, minute=30)), foo)

schedule.once(dt.timedelta(minutes=10), foo)
schedule.once(trigger.Monday(), foo)
schedule.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)
```

A human readable overview of the scheduled jobs can be created with a simple `print` statement:

```py
print(schedule)
```

```text
max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=9

type     function / alias due at                 due in      attempts weight
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
import time

while True:
    schedule.exec_jobs()
    time.sleep(1)
```

## Documentation

The API documentation can either be viewed
[online](https://python-scheduler.readthedocs.io/en/latest/index.html)
or generated using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
formatting. To build, run:

```bash
sphinx-build -b html doc/ doc/_build/html
```

## Testing

Testing is done using [pytest](https://pypi.org/project/pytest/). With
[pytest-cov](https://pypi.org/project/pytest-cov/) and
[coverage](https://pypi.org/project/coverage/) a report for the test coverage can be generated:

```bash
pytest --cov=scheduler/ tests/
coverage html
```

To test the examples in the documentation run:

```bash
pytest --doctest-modules doc/pages/*/*
```

## License

This software is published under the [LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).
