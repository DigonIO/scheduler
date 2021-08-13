import pytest
from helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    job_args,
    job_args_utc,
    utc,
)

from scheduler.core import Scheduler
from scheduler.job import Job

patch_samples = [T_2021_5_26__3_55] * 7
patch_samples_utc = [T_2021_5_26__3_55_UTC] * 11

table = (
    "max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=3\n"
    "\n"
    "type     function / alias due at                 due in      attempts weight\n"
    "-------- ---------------- ------------------- --------- ------------- ------\n"
    "MINUTELY bar(..)          2021-05-26 03:54:15  -0:00:45          0/20      0\n"
    "ONCE     foo()            2021-05-26 04:55:00   1:00:00           0/1      1\n"
    "DAILY    foo()            2021-05-26 07:05:00   3:10:00           0/7      1\n"
)

table_utc = (
    "max_exec=inf, tzinfo=UTC, priority_function=linear_priority_function, #jobs=4\n"
    "\n"
    "type     function / alias due at              tzinfo          due in      attempts weight\n"
    "-------- ---------------- ------------------- ------------ --------- ------------- ------\n"
    "WEEKLY   bar(..)          2021-05-25 03:55:00 UTC             -1 day         0/inf      1\n"
    "CYCLIC   foo()            2021-05-26 03:54:59 UTC           -0:00:00         0/inf 0.333#\n"
    "HOURLY   print(?)         2021-05-26 03:55:00 UTC            0:00:00         0/inf     20\n"
    "ONCE     print(?)         2021-06-08 23:45:59 UTC            13 days           0/1      1\n"
)


@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, tzinfo, res",
    [
        (patch_samples, job_args, None, table),
        (patch_samples_utc, job_args_utc, utc, table_utc),
    ],
    indirect=["patch_datetime_now"],
)
def test_sch_repr(patch_datetime_now, job_kwargs, tzinfo, res):
    jobs = [Job(**kwargs) for kwargs in job_kwargs]
    sch = Scheduler(tzinfo=tzinfo, jobs=jobs)
    assert str(sch) == res
