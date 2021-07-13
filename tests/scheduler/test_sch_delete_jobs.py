import random
import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday, AbstractJob

from helpers import foo


@pytest.mark.parametrize(
    "n_jobs",
    [
        1,
        2,
        3,
        10,
    ],
)
def test_delete_job(n_jobs):
    sch = Scheduler()
    assert len(sch.jobs) == 0

    jobs = []
    for _ in range(n_jobs):
        jobs.append(sch.once(dt.datetime.now(), foo))
    assert len(sch.jobs) == n_jobs

    job = random.choice(jobs)
    sch.delete_job(job)
    assert job not in sch.jobs
    assert len(sch.jobs) == n_jobs - 1


@pytest.mark.parametrize(
    "empty_set",
    [
        False,
        True,
    ],
)
@pytest.mark.parametrize(
    "mode",
    [
        None,
        all,
        any,
    ],
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
def test_delete_jobs(n_jobs, mode, empty_set):
    sch = Scheduler()
    assert len(sch.jobs) == 0

    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs

    if empty_set:
        if mode is None:
            num_del = sch.delete_jobs()
        else:
            num_del = sch.delete_jobs(mode=mode)
    else:
        if mode is None:
            num_del = sch.delete_jobs(tags={})
        else:
            num_del = sch.delete_jobs(tags={}, mode=mode)

    assert len(sch.jobs) == 0
    assert num_del == n_jobs
