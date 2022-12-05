import datetime as dt

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
def test_sch_init(max_exec, tzinfo, priority_function, jobs, err):
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
