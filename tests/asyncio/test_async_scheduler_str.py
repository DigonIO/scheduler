import copy
import datetime as dt
from typing import Any, Optional

import pytest

from scheduler.asyncio.job import Job
from scheduler.asyncio.scheduler import Scheduler

from ..helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    job_args,
    job_args_utc,
    utc,
)

patch_samples = [T_2021_5_26__3_55] * 4
patch_samples_utc = [T_2021_5_26__3_55_UTC] * 5

async_job_args = copy.deepcopy(job_args)
for ele in async_job_args:
    ele.pop("weight")
    ele["alias"] = "test"

async_job_args_utc = copy.deepcopy(job_args_utc)
for ele in async_job_args_utc:
    ele.pop("weight")

table = (
    "tzinfo=None, #jobs=3\n"
    "\n"
    "type     function / alias due at                 due in      attempts\n"
    "-------- ---------------- ------------------- --------- -------------\n"
    "MINUTELY test             2021-05-26 03:54:15  -0:00:45          0/20\n"
    "ONCE     test             2021-05-26 04:55:00   1:00:00           0/1\n"
    "DAILY    test             2021-05-26 07:05:00   3:10:00           0/7\n"
)

table_utc = (
    "tzinfo=UTC, #jobs=4\n"
    "\n"
    "type     function / alias due at              tzinfo          due in      attempts\n"
    "-------- ---------------- ------------------- ------------ --------- -------------\n"
    "WEEKLY   bar(..)          2021-05-25 03:55:00 UTC             -1 day         0/inf\n"
    "CYCLIC   foo()            2021-05-26 03:54:59 UTC           -0:00:00         0/inf\n"
    "HOURLY   print(?)         2021-05-26 03:55:00 UTC            0:00:00         0/inf\n"
    "ONCE     print(?)         2021-06-08 23:45:59 UTC            13 days           0/1\n"
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, tzinfo, res",
    [
        (patch_samples, async_job_args, None, table),
        (patch_samples_utc, async_job_args_utc, utc, table_utc),
    ],
    indirect=["patch_datetime_now"],
)
async def test_async_scheduler_str(
    patch_datetime_now: Any,
    job_kwargs: tuple[dict[str, Any], ...],
    tzinfo: Optional[dt.tzinfo],
    res: str,
) -> None:
    jobs = [Job(**kwargs) for kwargs in job_kwargs]

    sch = Scheduler(tzinfo=tzinfo)
    for job in jobs:
        sch._jobs[job] = None
    assert str(sch) == res
