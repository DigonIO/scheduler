import datetime as dt
import random

import pytest
from helpers import foo

from scheduler import Scheduler, SchedulerError
from scheduler.base.definition import JobType
from scheduler.threading.job import Job


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
    "any_tag",
    [
        None,
        False,
        True,
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
def test_delete_jobs(n_jobs, any_tag, empty_set):
    sch = Scheduler()
    assert len(sch.jobs) == 0

    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs

    if empty_set:
        if any_tag is None:
            num_del = sch.delete_jobs()
        else:
            num_del = sch.delete_jobs(any_tag=any_tag)
    else:
        if any_tag is None:
            num_del = sch.delete_jobs(tags={})
        else:
            num_del = sch.delete_jobs(tags={}, any_tag=any_tag)

    assert len(sch.jobs) == 0
    assert num_del == n_jobs


@pytest.mark.parametrize(
    "job_tags, delete_tags, any_tag, n_deleted",
    [
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "1"}], {"a", "1"}, True, 3],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "2"}], {"b", "1"}, True, 2],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "1"}], {"3"}, True, 1],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "2"}], {"2", "3"}, True, 2],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "1"}], {"a", "1"}, False, 1],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "2"}], {"b", "1"}, False, 0],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "1"}], {"1", "3"}, False, 1],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "2"}], {"2", "3"}, False, 1],
    ],
)
def test_delete_tagged_jobs(job_tags, delete_tags, any_tag, n_deleted):
    sch = Scheduler()

    for tags in job_tags:
        sch.once(dt.timedelta(), lambda: None, tags=tags)

    assert sch.delete_jobs(tags=delete_tags, any_tag=any_tag) == n_deleted
