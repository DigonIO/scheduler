import random
import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday, AbstractJob

from helpers import foo, DELETION_MODE_ERROR


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


@pytest.mark.parametrize(
    "job_tags, delete_tags, n_deleted, mode",
    [
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "1"}], {"a", "1"}, 3, any],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "2"}], {"b", "1"}, 2, any],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "1"}], {"3"}, 1, any],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "2"}], {"2", "3"}, 2, any],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "1"}], {"a", "1"}, 1, all],
        [[{"a", "b"}, {"1", "2", "3"}, {"a", "2"}], {"b", "1"}, 0, all],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "1"}], {"1", "3"}, 1, all],
        [[{"a", "b"}, {"1", "2", "3"}, {"b", "2"}], {"2", "3"}, 1, all],
    ],
)
def test_delete_tagged_jobs(job_tags, delete_tags, n_deleted, mode):
    sch = Scheduler()

    for tags in job_tags:
        sch.once(dt.timedelta(), lambda: None, tags=tags)

    assert sch.delete_jobs(tags=delete_tags, mode=mode) == n_deleted


@pytest.mark.parametrize(
    "mode",
    [
        None,
        True,
        "foo",
        4,
        Scheduler,
        Scheduler(),
        print,
    ],
)
def test_corrupt_deletion_mode(mode):
    sch = Scheduler()
    with pytest.raises(SchedulerError) as msg:
        sch.delete_jobs(tags={"foo"}, mode=mode)
        assert msg == DELETION_MODE_ERROR
