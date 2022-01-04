import asyncio
import datetime as dt

import pytest

from scheduler.base.definition import JobType
from scheduler.asyncio.scheduler import AsyncJob

async def foo():
    await asyncio.sleep(0.01)

@pytest.mark.asyncio
async def test_async_job():
    job = AsyncJob(
        JobType.CYCLIC,
        [dt.timedelta(seconds=0.01)],
        foo,
        max_attempts=2,
        )
    assert job.attempts == 0

    await job._exec()
    assert job.attempts == 1

    await job._exec()
    assert job.attempts == 2

    assert job.has_attempts_remaining == False