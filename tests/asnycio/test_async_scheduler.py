import asyncio
import datetime as dt

import pytest

from scheduler.asyncio.scheduler import AsyncScheduler
from scheduler.trigger import Monday

async def foo():
    await asyncio.sleep(0)

def test_async_scheduler_init(event_loop):
    _ = AsyncScheduler(loop = event_loop)

@pytest.mark.asyncio
async def test_async_scheduler_exec(event_loop):
    sch = AsyncScheduler(loop = event_loop)
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
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo)
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo)

    assert len(sch.jobs) == 2
    sch.delete_jobs()
    assert len(sch.jobs) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tags, any_tag, length",
    [
        ({"foo"}, False, 1),
        ({"bar"}, False, 1),
        ({"foo", "bar"}, True, 0),
    ]
)
async def test_delete_jobs_with_tags(event_loop, tags, any_tag, length):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"foo"})
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"bar"})

    assert len(sch.jobs) == 2
    sch.delete_jobs(tags, any_tag)
    assert len(sch.jobs) == length

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tags, any_tag, length",
    [
        ({}, False, 2),
        (None, False, 2),
        (None, True, 2),
        ({"foo"}, False, 1),
        ({"bar"}, False, 1),
    ]
)
async def test_get_jobs_with_tags(event_loop, tags, any_tag, length):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"foo"})
    job1 = sch.cyclic(dt.timedelta(seconds=1), foo, tags={"bar"})

    jobs = sch.get_jobs(tags, any_tag)
    assert len(jobs) == length

@pytest.mark.asyncio
async def test_async_minutely(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.minutely(dt.time(second=30), foo)
    job1 = sch.minutely([dt.time(second=30), dt.time(second=45)], foo)

@pytest.mark.asyncio
async def test_async_hourly(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.hourly(dt.time(minute=30), foo)

@pytest.mark.asyncio
async def test_async_daily(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.daily(dt.time(hour=12), foo)

@pytest.mark.asyncio
async def test_async_weekly(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.weekly(Monday(dt.time(hour=12)), foo)

@pytest.mark.asyncio
async def test_async_once(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.once(dt.time(hour=12), foo)

@pytest.mark.asyncio
async def test_async_once_datetime(event_loop):
    sch = AsyncScheduler(loop = event_loop)
    job0 = sch.once(dt.datetime.now(), foo)