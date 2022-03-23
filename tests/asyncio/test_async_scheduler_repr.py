import copy

import pytest
from helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    job_args,
    job_args_utc,
    utc,
)

from scheduler.asyncio.scheduler import Scheduler
from scheduler.asyncio.job import Job

patch_samples = [T_2021_5_26__3_55] * 7
patch_samples_utc = [T_2021_5_26__3_55_UTC] * 11

async_job_args = copy.deepcopy(job_args)
for ele in async_job_args:
    ele.pop("weight")

async_job_args_utc = copy.deepcopy(job_args_utc)
for ele in async_job_args_utc:
    ele.pop("weight")

async_sch_repr = (
    "scheduler.asyncio.scheduler.Scheduler(None, jobs={",
    "})",
)
async_sch_repr_utc = (
    "scheduler.asyncio.scheduler.Scheduler(datetime.timezone.utc, jobs={",
    "})",
)

async_job_reprs = (
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

async_job_reprs_utc = (
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
    "patch_datetime_now, job_kwargs, tzinfo, j_results, s_results",
    [
        (patch_samples, async_job_args, None, async_job_reprs, async_sch_repr),
        (patch_samples_utc, async_job_args_utc, utc, async_job_reprs_utc, async_sch_repr_utc),
    ],
    indirect=["patch_datetime_now"],
)
def test_async_scheduler_repr(patch_datetime_now, job_kwargs, tzinfo, j_results, s_results):
    jobs = [Job(**kwargs) for kwargs in job_kwargs]
    sch = Scheduler(tzinfo=tzinfo)
    for job in jobs:
        sch._Scheduler__jobs[job] = None
    rep = repr(sch)
    n_j_addr = 0  # number of address strings in jobs
    for j_result in j_results:
        n_j_addr += len(j_result) - 1
        for substring in j_result:
            assert substring in rep
            rep = rep.replace(substring, "", 1)
    for substring in s_results:
        assert substring in rep
        rep = rep.replace(substring, "", 1)

    # ", " seperators between jobs: (len(j_results) - 1) * 2
    assert len(rep) == n_j_addr * 12 + (len(j_results) - 1) * 2
