import datetime as dt

import pdb
from scheduler.core import Scheduler
import pytest

from scheduler.job import Job, JobType
from scheduler.util import Weekday


from helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    utc,
    job_args,
    job_args_utc,
)


patch_samples = [T_2021_5_26__3_55] * 7
patch_samples_utc = [T_2021_5_26__3_55_UTC] * 11

sch_repr = (
    "scheduler.Scheduler(0, None, <function linear_priority_function at 0x",
    ">, [scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
    ">, {}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None), scheduler.Job(<JobType.MINUTELY: 2>, datetime.time(0, 0, 20), <function bar at 0x",
    ">, {'msg': 'foobar'}, 20, 0, False, datetime.datetime(2021, 5, 26, 3, 54, 15), datetime.datetime(2021, 5, 26, 4, 5), False, None), scheduler.Job(<JobType.DAILY: 4>, datetime.time(7, 5), <function foo at 0x",
    ">, {}, 7, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)], jobs={scheduler.Job(<JobType.MINUTELY: 2>, datetime.time(0, 0, 20), <function bar at 0x",
    ">, {'msg': 'foobar'}, 20, 0, False, datetime.datetime(2021, 5, 26, 3, 54, 15), datetime.datetime(2021, 5, 26, 4, 5), False, None), scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
    ">, {}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None), scheduler.Job(<JobType.DAILY: 4>, datetime.time(7, 5), <function foo at 0x",
    ">, {}, 7, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)})",
)
sch_repr_utc = (
    "scheduler.Scheduler(0, datetime.timezone.utc, <function linear_priority_function at 0x",
    ">, [scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
    ">, {}, 0, 0.3333333333333333, False, datetime.datetime(2021, 5, 26, 3, 54, 59, 999990, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc), scheduler.Job(<JobType.HOURLY: 3>, datetime.time(7, 5, tzinfo=datetime.timezone.utc), <built-in function print>, {}, 0, 20, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 5, 26, 23, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc), scheduler.Job(<JobType.WEEKLY: 5>, <Weekday.MONDAY: 0>, <function bar at 0x",
    ">, {}, 0, 1, False, datetime.datetime(2021, 5, 25, 3, 55, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc), scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.WEDNESDAY: 2>, (<Weekday.TUESDAY: 1>, datetime.time(23, 45, 59, tzinfo=datetime.timezone.utc))], <built-in function print>, {'end': 'FOO\\n'}, 1, 1, True, datetime.datetime(2021, 6, 2, 3, 55, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)], jobs={scheduler.Job(<JobType.WEEKLY: 5>, <Weekday.MONDAY: 0>, <function bar at 0x",
    ">, {}, 0, 1, False, datetime.datetime(2021, 5, 25, 3, 55, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc), scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
    ">, {}, 0, 0.3333333333333333, False, datetime.datetime(2021, 5, 26, 3, 54, 59, 999990, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc), scheduler.Job(<JobType.HOURLY: 3>, datetime.time(7, 5, tzinfo=datetime.timezone.utc), <built-in function print>, {}, 0, 20, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 5, 26, 23, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc), scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.WEDNESDAY: 2>, (<Weekday.TUESDAY: 1>, datetime.time(23, 45, 59, tzinfo=datetime.timezone.utc))], <built-in function print>, {'end': 'FOO\\n'}, 1, 1, True, datetime.datetime(2021, 6, 2, 3, 55, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)})",
)


@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, tzinfo, res, rem_len",
    [
        (patch_samples, job_args, None, sch_repr, 84),
        (patch_samples_utc, job_args_utc, utc, sch_repr_utc, 60),
    ],
    indirect=["patch_datetime_now"],
)
def test_sch_repr(patch_datetime_now, job_kwargs, tzinfo, res, rem_len):
    jobs = [Job(**kwargs) for kwargs in job_kwargs]
    sch = Scheduler(tzinfo=tzinfo, jobs=jobs)
    rep = repr(sch)
    # pdb.set_trace()
    for substring in res:
        assert substring in rep
        rep = rep.replace(substring, "", 1)
    assert len(rep) == rem_len
