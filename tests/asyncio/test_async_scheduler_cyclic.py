"""
Tests for scheduler.asyncio.scheduler considering asyncio.sleep behaviour

Heavy use of monkey-patching with the following behaviour:

* `dt.datetime.now()` increments the returned datetime by one second with each call
* `dt.datetime.last_now()` gives the most recent value returned by `dt.datetime.now()`
* `asyncio.sleep(delay)` will never sleep real time, but simply block until the next
  event loop is executed, effectively behaving as `asyncio.sleep(0)`

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import asyncio
import datetime as dt
import logging
from asyncio.selector_events import BaseSelectorEventLoop
from typing import Any, NoReturn

import pytest

from scheduler.asyncio.scheduler import Scheduler

from ..helpers import T_2021_5_26__3_55, fail

samples_secondly = [T_2021_5_26__3_55 + dt.timedelta(seconds=x) for x in range(12)]
async_real_sleep = asyncio.sleep


async def fake_sleep(delay: float, result: None = None) -> None:
    """Fake asyncio.sleep, depends on monkeypatch `patch_datetime_now`"""
    t_start = dt.datetime.last_now()
    while True:
        await asyncio.tasks.__sleep0()
        if (dt.datetime.last_now() - t_start).total_seconds() >= delay:
            break
        else:
            _ = dt.datetime.now()
    return result


async def bar() -> None: ...


@pytest.mark.parametrize(
    "patch_datetime_now",
    [samples_secondly],
    indirect=["patch_datetime_now"],
)
def test_async_scheduler_cyclic1s(
    monkeypatch: pytest.MonkeyPatch, patch_datetime_now: Any, event_loop: BaseSelectorEventLoop
) -> None:
    async def main() -> None:
        with monkeypatch.context() as m:
            m.setattr(asyncio, "sleep", fake_sleep)
            schedule = Scheduler()

            # schedule.__schedule calls: now, async: [now, async_sleep]
            cyclic_job = schedule.cyclic(dt.timedelta(seconds=1), bar)
            assert dt.datetime.last_now() == samples_secondly[0]
            assert cyclic_job.datetime == samples_secondly[1]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[1]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[2]
            assert cyclic_job.attempts == 1

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[3]
            assert cyclic_job.attempts == 2

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[4]
            assert cyclic_job.attempts == 3

            schedule.delete_jobs()
            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[4]
            assert cyclic_job.attempts == 3

    event_loop.run_until_complete(main())


# NOTE: In the following test `sch.delete_jobs()` is run to suppress
# the asyncio Warning "Task was destroyed but it is pending!" during testing


@pytest.mark.parametrize(
    "patch_datetime_now",
    [samples_secondly],
    indirect=["patch_datetime_now"],
)
def test_async_scheduler_cyclic2s(
    monkeypatch: pytest.MonkeyPatch, patch_datetime_now: Any, event_loop: BaseSelectorEventLoop
) -> None:
    async def main() -> None:
        with monkeypatch.context() as m:
            m.setattr(asyncio, "sleep", fake_sleep)
            schedule = Scheduler()

            # schedule.__schedule calls: now, async: [now, async_sleep]
            cyclic_job = schedule.cyclic(dt.timedelta(seconds=2), bar, max_attempts=3)
            assert dt.datetime.last_now() == samples_secondly[0]
            assert cyclic_job.datetime == samples_secondly[2]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[1]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[2]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[3]
            assert cyclic_job.attempts == 1

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[4]
            assert cyclic_job.attempts == 1

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[5]
            assert cyclic_job.attempts == 2
            schedule.delete_jobs()

    event_loop.run_until_complete(main())


async def async_fail() -> NoReturn:
    fail()


@pytest.mark.parametrize(
    "patch_datetime_now",
    [samples_secondly],
    indirect=["patch_datetime_now"],
)
def test_asyncio_fail(
    monkeypatch: pytest.MonkeyPatch,
    patch_datetime_now: Any,
    event_loop: BaseSelectorEventLoop,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG, logger="scheduler")

    async def main() -> None:
        with monkeypatch.context() as m:
            m.setattr(asyncio, "sleep", fake_sleep)
            schedule = Scheduler()
            cyclic_job = schedule.cyclic(dt.timedelta(seconds=1), async_fail)
            assert dt.datetime.last_now() == samples_secondly[0]
            assert cyclic_job.datetime == samples_secondly[1]
            assert cyclic_job.attempts == 0

            RECORD = (
                "scheduler",
                logging.ERROR,
                "Unhandled exception in `%r`!" % (cyclic_job,),
            )

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[1]
            assert cyclic_job.attempts == 0

            await asyncio.sleep(0)
            assert dt.datetime.last_now() == samples_secondly[2]
            assert cyclic_job.attempts == 1
            assert cyclic_job.failed_attempts == 1
            assert caplog.record_tuples == [RECORD]

            await asyncio.sleep(0)
            assert cyclic_job.attempts == 2
            assert cyclic_job.failed_attempts == 2
            assert caplog.record_tuples == [RECORD, RECORD]

    event_loop.run_until_complete(main())
