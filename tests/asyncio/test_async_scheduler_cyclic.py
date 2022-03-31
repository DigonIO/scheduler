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
import traceback

import pytest
from helpers import T_2021_5_26__3_55, stack_logger

from scheduler.asyncio.scheduler import Scheduler

samples_secondly = [T_2021_5_26__3_55 + dt.timedelta(seconds=x) for x in range(12)]
async_real_sleep = asyncio.sleep


async def bar(delay=-0.1):
    st = traceback.format_stack()
    stack_logger.append(st[-2:-1])
    stack_logger.append(f"{delay}\n\n")
    with open("./sleep_stack.log", "w") as fh:
        for stack in stack_logger:
            fh.writelines(stack)
    ...


async def fake_sleep(delay, result=None):
    """Fake asyncio.sleep, depends on monkeypatch `patch_datetime_now`"""
    st = traceback.format_stack()
    stack_logger.append(st[-2:-1])
    stack_logger.append(f"{delay}\n\n")
    with open("./sleep_stack.log", "w") as fh:
        for stack in stack_logger:
            fh.writelines(stack)
    t_start = dt.datetime.last_now()
    while True:
        await asyncio.tasks.__sleep0()
        if (dt.datetime.last_now() - t_start).total_seconds() >= delay:  # TODO: offset yes/no?
            break
        else:
            _ = dt.datetime.now()
    return result


@pytest.mark.parametrize(
    "patch_datetime_now",
    [samples_secondly],
    indirect=["patch_datetime_now"],
)
def test_async_scheduler_cyclic1s(monkeypatch, patch_datetime_now, event_loop):
    async def main():
        with monkeypatch.context() as m:
            m.setattr(asyncio, "sleep", fake_sleep)
            schedule = Scheduler()

            # schedule.__schedule calls: now, async: [now, async_sleep]
            cyclic_job = schedule.cyclic(dt.timedelta(seconds=1), bar, args=(-0.01,))
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


@pytest.mark.parametrize(
    "patch_datetime_now",
    [samples_secondly],
    indirect=["patch_datetime_now"],
)
def test_async_scheduler_cyclic2s(monkeypatch, patch_datetime_now, event_loop):
    async def main():
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

    event_loop.run_until_complete(main())
