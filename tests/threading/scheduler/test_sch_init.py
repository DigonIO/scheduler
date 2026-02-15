import datetime as dt
from typing import Callable, Optional
from zoneinfo import ZoneInfo

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.base.definition import JobType
from scheduler.threading.job import Job

from ...helpers import TZ_ERROR_MSG, foo, utc


def priority_function_dummy(seconds: float, job: Job, max_exec: int, job_count: int) -> float:
    _ = seconds
    _ = job
    _ = max_exec
    _ = job_count

    return 1


@pytest.mark.parametrize(
    "max_exec, tzinfo, priority_function, jobs, err",
    (
        [0, None, None, None, None],
        [10, utc, priority_function_dummy, None, None],
        [
            1,
            utc,
            priority_function_dummy,
            {Job(JobType.CYCLIC, [dt.timedelta(seconds=1)], foo, tzinfo=utc)},
            None,
        ],
        [
            1,
            utc,
            priority_function_dummy,
            {Job(JobType.CYCLIC, [dt.timedelta(seconds=1)], foo, tzinfo=None)},
            TZ_ERROR_MSG,
        ],
    ),
)
def test_sch_init(
    max_exec: int,
    tzinfo: dt.tzinfo,
    priority_function: Callable[
        [float, Job, int, int],
        float,
    ],
    jobs: set[Job],
    err: Optional[str],
) -> None:
    if err:
        with pytest.raises(SchedulerError, match=err):
            Scheduler(
                max_exec=max_exec,
                tzinfo=tzinfo,
                priority_function=priority_function,
                jobs=jobs,
            )
    else:
        Scheduler(
            max_exec=max_exec,
            tzinfo=tzinfo,
            priority_function=priority_function,
            jobs=jobs,
        )


def test_zoneinfo_vs_timezone() -> None:
    tz_berlin = ZoneInfo("Europe/Berlin")
    tz_const = dt.timezone(offset=dt.timedelta(hours=1))

    sch = Scheduler(tzinfo=tz_berlin)

    trigger0 = dt.datetime.now(tz_berlin)
    job0 = sch.once(trigger0, foo)

    trigger1 = dt.datetime.now(tz_const)
    job1 = sch.once(trigger1, foo)

    sch.delete_jobs()
