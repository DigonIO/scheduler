<p align="center">
  <a href="https://gitlab.com/DigonIO/scheduler"><img alt="scheduler" src="https://gitlab.com/DigonIO/scheduler/-/raw/master/doc/_assets/logo_name.svg" width="60%"></a>
</p>
<p>A simple in-process python scheduler library with asyncio, threading and timezone support.
Schedule tasks by their time cycles, fixed times, weekdays, dates, weights, offsets and execution
counts and automate Jobs.</p>

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/scheduler)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/scheduler)
[![license](https://img.shields.io/badge/license-LGPLv3-orange)](https://gitlab.com/DigonIO/scheduler/-/blob/master/LICENSE)
[![pipeline status](https://gitlab.com/DigonIO/scheduler/badges/master/pipeline.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/scheduler/badges/master/coverage.svg)](https://gitlab.com/DigonIO/scheduler/-/pipelines)
[![Code style: black](https://gitlab.com/DigonIO/scheduler/-/raw/master/doc/_assets/code_style_black.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/scheduler)](https://pypi.org/project/scheduler/)
[![versionsupport](https://img.shields.io/pypi/pyversions/scheduler)](https://pypi.org/project/scheduler/)
[![Downloads Week](https://pepy.tech/badge/scheduler/week)](https://pepy.tech/project/scheduler)
[![Downloads Total](https://pepy.tech/badge/scheduler)](https://pepy.tech/project/scheduler)
[![Documentation](https://img.shields.io/badge/Docs-HostYourDocs-blue)](https://digon.io/hyd/project/scheduler/t/master)

---

If you find the scheduler library beneficial, please consider supporting the project by [starring it on GitHub](https://github.com/DigonIO/scheduler).

[![GitHub Repo stars](https://img.shields.io/github/stars/digonio/scheduler)](https://github.com/DigonIO/scheduler)

## Features

* Easy and user friendly in-process Job scheduling
[(Quick Start)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/quick_start.html)
* Asyncio scheduler [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/asyncio.html)
* Threading scheduler [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/threading.html)
* Timezone compatibility [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/timezones.html)
* Passing of parameters
  [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/parameters.html)
* Job prioritization
  * Default linear prioritization
    [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/job_prioritization.html)
  * User definable prioritization functions
    [(Guide)](https://digon.io/hyd/project/scheduler/t/master/pages/guides/custom_prioritization.html)
* Job tagging
  [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/tags.html)
* Job batching
  [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/job_batching.html)
* Job metadata
  [(Example)](https://digon.io/hyd/project/scheduler/t/master/pages/examples/metrics.html)
* Lightweight
* High test coverage
* [Online documentation](https://digon.io/hyd/project/scheduler/t/master/readme.html)

## Installation

### pip

`scheduler` can be installed directly from the PyPI repositories with:

```bash
pip install scheduler
```

Alternatively install `scheduler` from the `git`
[repository](https://gitlab.com/DigonIO/scheduler) with:

```bash
git clone https://gitlab.com/DigonIO/scheduler.git
cd scheduler
pip install .
```

### Arch Linux

The `PKGBUILD` file can be utilized from the
[Arch Build System](https://wiki.archlinux.org/title/Arch_Build_System).
Download the `PKGBUILD` file and from within the containing folder run

```console
makepkg -i
```

## Example: *How to schedule Jobs*

The following example shows how the `Scheduler` is instantiated and how basic `Job`s are created.
For advanced scheduling examples please visit the online
[documentation](https://digon.io/hyd/project/scheduler/t/master/examples.html).

[//]: # (This example is not directly included in the testing environment. Make sure to also update the corresponding test in tests/test_readme.py when updating the following example.)

```py
import datetime as dt

from scheduler import Scheduler
from scheduler.trigger import Monday, Tuesday

def foo():
    print("foo")

schedule = Scheduler()

schedule.cyclic(dt.timedelta(minutes=10), foo)

schedule.minutely(dt.time(second=15), foo)
schedule.hourly(dt.time(minute=30, second=15), foo)
schedule.daily(dt.time(hour=16, minute=30), foo)
schedule.weekly(Monday(), foo)
schedule.weekly(Monday(dt.time(hour=16, minute=30)), foo)

schedule.once(dt.timedelta(minutes=10), foo)
schedule.once(Tuesday(), foo)
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
MINUTELY foo()            2021-05-26 03:55:15   0:00:14         0/inf      1
CYCLIC   foo()            2021-05-26 04:05:00   0:09:59         0/inf      1
ONCE     foo()            2021-05-26 04:05:00   0:09:59           0/1      1
HOURLY   foo()            2021-05-26 04:30:15   0:35:14         0/inf      1
DAILY    foo()            2021-05-26 16:30:00  12:34:59         0/inf      1
WEEKLY   foo()            2021-05-31 00:00:00    4 days         0/inf      1
WEEKLY   foo()            2021-05-31 16:30:00    5 days         0/inf      1
ONCE     foo()            2021-06-01 00:00:00    5 days           0/1      1
ONCE     foo()            2022-02-15 00:45:00  264 days           0/1      1
```

Executing pending `Job`s periodically can be achieved with a simple loop:

```py
import time

while True:
    schedule.exec_jobs()
    time.sleep(1)
```

## Documentation

View the API documentation [online](https://digon.io/hyd/project/scheduler/t/master/readme.html).

## Sponsor

<br>
<div align="center">
  <a href="https://digon.io">
    <img alt="Digon.IO GmbH - Fine-Tuned AI services for developers" src="https://digon.io/static/modules/img/digon_name_right_grey.svg" width="35%">
  </a>
</div>
<br>
<div align="center">
At Digon.IO, we provide your developer team with our knowledge and experience in the field of Large Language Models (LLMs).

We specialize in consulting, data engineering, and data science to fine-tune AI services for seamless integration into your projects.
</div>

## License

This free and open source software (FOSS) is published under the [LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html).
