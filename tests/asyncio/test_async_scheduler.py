import asyncio
import datetime as dt

import pytest

from scheduler.asyncio.scheduler import Scheduler
from scheduler.error import SchedulerError
from scheduler.trigger import Monday

from ..helpers import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    DELETE_NOT_SCHEDULED_ERROR,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    MISSING_EVENT_LOOP_ERROR,
    ONCE_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)


async def foo():
    await asyncio.sleep(0)


def test_async_scheduler_init(event_loop):
    _ = Scheduler(loop=event_loop)


@pytest.mark.asyncio
async def test_async_scheduler_exec(event_loop):
    sch = Scheduler(loop=event_loop)
    job = sch.cyclic(dt.timedelta(seconds=0.01), foo, max_attempts=3)

    assert len(sch.jobs) == 1

    await asyncio.sleep(0.011)
    assert job.attempts == 1

    await asyncio.sleep(0.011)
    assert job.attempts == 2

    await asyncio.sleep(0.011)
    assert job.attempts == 3
    assert len(sch.jobs) == 0


@pytest.mark.asyncio
async def test_delete_jobs(event_loop):
    sch = Scheduler(loop=event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo)
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo)

    assert len(sch.jobs) == 2
    sch.delete_jobs()
    assert len(sch.jobs) == 0


@pytest.mark.asyncio
async def test_delete_job(event_loop):
    sch = Scheduler(loop=event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo)
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo)

    sch.delete_job(job0)
    sch.delete_job(job1)

    # test error if the job is not scheduled
    with pytest.raises(SchedulerError, match=DELETE_NOT_SCHEDULED_ERROR):
        sch.delete_job(job1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tags, any_tag, length",
    [
        ({"foo"}, False, 1),
        ({"bar"}, False, 1),
        ({"foo", "bar"}, True, 0),
    ],
)
async def test_delete_jobs_with_tags(event_loop, tags, any_tag, length):
    sch = Scheduler(loop=event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"foo"})
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"bar"})

    assert len(sch.jobs) == 2
    sch.delete_jobs(tags, any_tag)
    assert len(sch.jobs) == length
    sch.delete_jobs()


# NOTE: In the following tests `sch.delete_jobs()` is run to suppress
# the asyncio Warning "Task was destroyed but it is pending!" during testing


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tags, any_tag, length",
    [
        (set(), False, 2),
        (None, False, 2),
        (None, True, 2),
        ({"foo"}, False, 1),
        ({"bar"}, False, 1),
    ],
)
async def test_get_jobs_with_tags(event_loop, tags, any_tag, length):
    sch = Scheduler(loop=event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"foo"})
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"bar"})

    jobs = sch.get_jobs(tags, any_tag)
    assert len(jobs) == length
    sch.delete_jobs()


@pytest.mark.asyncio
async def test_async_list_timing(event_loop):
    sch = Scheduler(loop=event_loop)
    job0 = sch.minutely([dt.time(second=30), dt.time(second=45)], foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (dt.timedelta(seconds=30), None),
        (dt.datetime.now(), CYCLIC_TYPE_ERROR_MSG),
    ],
)
async def test_async_cyclic(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.cyclic(timing, foo)
    else:
        job0 = sch.cyclic(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (dt.time(second=30), None),
        (dt.datetime.now(), MINUTELY_TYPE_ERROR_MSG),
    ],
)
async def test_async_minutely(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.minutely(timing, foo)
    else:
        job0 = sch.minutely(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (dt.time(minute=30), None),
        (dt.datetime.now(), HOURLY_TYPE_ERROR_MSG),
    ],
)
async def test_async_hourly(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.hourly(timing, foo)
    else:
        job0 = sch.hourly(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (dt.time(hour=12), None),
        (dt.datetime.now(), DAILY_TYPE_ERROR_MSG),
    ],
)
async def test_async_daily(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.daily(timing, foo)
    else:
        job0 = sch.daily(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (Monday(dt.time(second=30)), None),
        (dt.datetime.now(), WEEKLY_TYPE_ERROR_MSG),
    ],
)
async def test_async_weekly(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.weekly(timing, foo)
    else:
        job0 = sch.weekly(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timing, err_msg",
    [
        (dt.time(second=30), None),
        ([dt.time(second=30)], ONCE_TYPE_ERROR_MSG),
    ],
)
async def test_async_once(event_loop, timing, err_msg):
    sch = Scheduler(loop=event_loop)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job0 = sch.once(timing, foo)
    else:
        job0 = sch.once(timing, foo)
    sch.delete_jobs()


@pytest.mark.asyncio
async def test_async_once_datetime(event_loop):
    sch = Scheduler(loop=event_loop)
    job0 = sch.once(dt.datetime.now(), foo)
    sch.delete_jobs()


def test_async_scheduler_without_running_loop():
    with pytest.raises(SchedulerError, match=MISSING_EVENT_LOOP_ERROR):
        sch = Scheduler()
