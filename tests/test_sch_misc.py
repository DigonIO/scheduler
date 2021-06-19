import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday, AbstractJob

from helpers import utc, TZ_ERROR_MSG, foo


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


@pytest.mark.parametrize(
    "n_jobs",
    [
        0,
        1,
        2,
        3,
        10,
    ],
)
def test_exec_all_jobs_and_jobs(n_jobs):
    sch = Scheduler()

    assert len(sch.jobs) == 0
    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs

    exec_job_count = sch.exec_all_jobs()
    assert exec_job_count == n_jobs
    assert len(sch.jobs) == 0


@pytest.mark.parametrize(
    "n_jobs",
    [
        0,
        1,
        2,
        3,
        10,
    ],
)
def test_delete_jobs(n_jobs):
    sch = Scheduler()

    assert len(sch.jobs) == 0
    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs
    sch.delete_jobs()
    assert len(sch.jobs) == 0
