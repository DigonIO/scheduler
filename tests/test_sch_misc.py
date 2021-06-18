import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday, AbstractJob

from helpers import (
    utc,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_utc,
    TZ_ERROR_MSG,
)


def foo():
    pass


def weight_function_dummy(
    seconds: float, job: AbstractJob, max_exec: int, job_count: int
) -> float:
    _ = seconds
    _ = job
    _ = max_exec
    _ = job_count

    return 1


@pytest.mark.parametrize(
    "max_exec, tzinfo, weight_function, jobs, err",
    (
        [0, None, None, None, None],
        [10, utc, weight_function_dummy, None, None],
        [
            1,
            utc,
            weight_function_dummy,
            {Job(JobType.CYCLIC, dt.timedelta(seconds=1), foo, tzinfo=utc)},
            None,
        ],
        [
            1,
            utc,
            weight_function_dummy,
            {Job(JobType.CYCLIC, dt.timedelta(seconds=1), foo, tzinfo=None)},
            TZ_ERROR_MSG,
        ],
    ),
)
def test_sch_init(max_exec, tzinfo, weight_function, jobs, err):
    if err:
        with pytest.raises(SchedulerError, match=err):
            Scheduler(
                max_exec=max_exec,
                tzinfo=tzinfo,
                weight_function=weight_function,
                jobs=jobs,
            )
    else:
        Scheduler(
            max_exec=max_exec, tzinfo=tzinfo, weight_function=weight_function, jobs=jobs
        )
