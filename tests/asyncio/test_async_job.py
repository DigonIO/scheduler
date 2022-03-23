import asyncio
import copy
import datetime as dt

import pytest
from helpers import job_args, job_args_utc, T_2021_5_26__3_55, T_2021_5_26__3_55_UTC

from scheduler.base.definition import JobType
from scheduler.asyncio.scheduler import Job

async_job_args = copy.deepcopy(job_args)
for ele in async_job_args:
    ele.pop("weight")

async_job_args_utc = copy.deepcopy(job_args_utc)
for ele in async_job_args_utc:
    ele.pop("weight")


async def foo():
    await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_async_job():
    job = Job(
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


job_reprs = (
    [
        "scheduler.asyncio.job.Job(<JobType.CYCLIC: 1>, [datetime.timedelta(seconds=3600)], <function foo at 0x",
        ">, (), {}, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None, None)",
    ],
    [
        "scheduler.asyncio.job.Job(<JobType.MINUTELY: 2>, [datetime.time(0, 0, 20)], <function bar at 0x",
        (
            ">, (), {'msg': 'foobar'}, 20, False, datetime.datetime(2021, 5, 26, 3, 54, 15),"
            " datetime.datetime(2021, 5, 26, 4, 5), False, None, None)"
        ),
    ],
    [
        "scheduler.asyncio.job.Job(<JobType.DAILY: 4>, [datetime.time(7, 5)], <function foo at 0x",
        ">, (), {}, 7, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None, None)",
    ],
)

job_reprs_utc = (
    [
        "scheduler.asyncio.job.Job(<JobType.CYCLIC: 1>, [datetime.timedelta(seconds=3600)], <function foo at 0x",
        (
            ">, (), {}, 0, False, datetime.datetime(2021, 5, 26, 3, 54, 59, 999990"
            ", tzinfo=datetime.timezone.utc), None, True, None, datetime.timezone.utc)"
        ),
    ],
    [
        (
            "scheduler.asyncio.job.Job(<JobType.HOURLY: 3>, [datetime.time(0, 5, tzinfo=datetime.timezone.utc)],"
            " <built-in function print>, (), {}, 0, False, datetime.datetime(2021, 5, 26, 3, 55,"
            " tzinfo=datetime.timezone.utc), datetime.datetime(2021, 5, 26, 23, 55, "
            "tzinfo=datetime.timezone.utc), False, None, datetime.timezone.utc)"
        )
    ],
    [
        (
            "scheduler.asyncio.job.Job(<JobType.WEEKLY: 5>, [Monday(time=datetime.time(0, 0, "
            "tzinfo=datetime.timezone.utc))], <function bar at 0x"
        ),
        (
            ">, (), {}, 0, False, datetime.datetime(2021, 5, 25, 3, 55, "
            "tzinfo=datetime.timezone.utc), None, True, None, datetime.timezone.utc)"
        ),
    ],
    [
        (
            "scheduler.asyncio.job.Job(<JobType.WEEKLY: 5>, [Wednesday(time=datetime.time(0, 0, "
            "tzinfo=datetime.timezone.utc)), Tuesday(time=datetime.time(23, 45, 59, "
            "tzinfo=datetime.timezone.utc))], <built-in function print>"
            ", (), {'end': 'FOO\\n'}, 1, True, "
            "datetime.datetime(2021, 6, 2, 3, 55, tzinfo=datetime.timezone.utc),"
            " datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc),"
            " False, None, datetime.timezone.utc)"
        )
    ],
)


@pytest.mark.parametrize(
    "job_kwargs, result",
    [(args, reprs) for args, reprs in zip(async_job_args, job_reprs)]
    + [(args, reprs) for args, reprs in zip(async_job_args_utc, job_reprs_utc)],
)
def test_async_job_repr(
    job_kwargs,
    result,
):
    rep = repr(Job(**job_kwargs))
    for substring in result:
        assert substring in rep
        rep = rep.replace(substring, "", 1)

    # result is broken into substring at every address. Address string is 12 long
    assert len(rep) == (len(result) - 1) * 12


@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, results",
    [
        (
            [T_2021_5_26__3_55] * 3,
            async_job_args,
            [
                "ONCE, foo(), at=2021-05-26 04:55:00, tz=None, in=1:00:00, #0/1",
                "MINUTELY, bar(..), at=2021-05-26 03:54:15, tz=None, in=-0:00:45, #0/20",
                "DAILY, foo(), at=2021-05-26 07:05:00, tz=None, in=3:10:00, #0/7",
            ],
        ),
        (
            [T_2021_5_26__3_55_UTC] * 4,
            async_job_args_utc,
            [
                "CYCLIC, foo(), at=2021-05-26 03:54:59, tz=UTC, in=-0:00:00, #0/inf",
                "HOURLY, print(?), at=2021-05-26 03:55:00, tz=UTC, in=0:00:00, #0/inf",
                "WEEKLY, bar(..), at=2021-05-25 03:55:00, tz=UTC, in=-1 day, #0/inf",
                "ONCE, print(?), at=2021-06-08 23:45:59, tz=UTC, in=13 days, #0/1",
            ],
        ),
    ],
    indirect=["patch_datetime_now"],
)
def test_job_str(
    patch_datetime_now,
    job_kwargs,
    results,
):
    for kwargs, result in zip(job_kwargs, results):
        assert result == str(Job(**kwargs))
