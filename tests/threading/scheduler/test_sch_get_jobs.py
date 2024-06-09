import datetime as dt
import random
from typing import Optional

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.base.definition import JobType
from scheduler.threading.job import Job

from ...helpers import foo


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
def test_get_all_jobs(n_jobs: int, any_tag: Optional[bool], empty_set: bool) -> None:
    sch = Scheduler()
    assert len(sch.jobs) == 0

    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs

    if empty_set:
        if any_tag is None:
            jobs = sch.get_jobs()
        else:
            jobs = sch.get_jobs(any_tag=any_tag)
    else:
        if any_tag is None:
            jobs = sch.get_jobs(tags=set())
        else:
            jobs = sch.get_jobs(tags=set(), any_tag=any_tag)

    assert len(jobs) == n_jobs


@pytest.mark.parametrize(
    "job_tags, select_tags, any_tag, returned",
    [
        [
            [{"a", "b"}, {"1", "2", "3"}, {"a", "1"}],
            {"a", "1"},
            True,
            [True, True, True],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"a", "2"}],
            {"b", "1"},
            True,
            [True, True, False],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"b", "1"}],
            {"3"},
            True,
            [False, True, False],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"b", "2"}],
            {"2", "3"},
            True,
            [False, True, True],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"a", "1"}],
            {"a", "1"},
            False,
            [False, False, True],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"a", "2"}],
            {"b", "1"},
            False,
            [False, False, False],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"b", "1"}],
            {"1", "3"},
            False,
            [False, True, False],
        ],
        [
            [{"a", "b"}, {"1", "2", "3"}, {"b", "2"}],
            {"2", "3"},
            False,
            [False, True, False],
        ],
    ],
)
def test_get_tagged_jobs(
    job_tags: list[set[str]], select_tags: set[str], any_tag: bool, returned: list[bool]
) -> None:
    sch = Scheduler()

    jobs = [sch.once(dt.timedelta(), lambda: None, tags=tags) for tags in job_tags]

    res = sch.get_jobs(tags=select_tags, any_tag=any_tag)
    for job, ret in zip(jobs, returned):
        if ret:
            assert job in res
        else:
            assert job not in res
