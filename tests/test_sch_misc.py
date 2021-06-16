import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday, AbstractJob

utc = dt.timezone.utc
T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
T_2021_5_26__3_55_utc = dt.datetime(2021, 5, 26, 3, 55, tzinfo=utc)

_TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together for {0}."
TZ_ERROR_MSG = _TZ_ERROR_MSG[:-9] + "."


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
