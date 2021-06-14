import datetime as dt

import pytest

from scheduler import Scheduler


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_delete_all_jobs(n_jobs):
    sch = Scheduler()
    assert len(sch.jobs) == 0
    for i in range(n_jobs):
        job = sch.schedule(
            lambda: None,
            dt.timedelta(seconds=1),
        )
    assert len(sch.jobs) == n_jobs
    sch.delete_job(job)
    assert len(sch.jobs) == n_jobs - 1
    sch.delete_jobs()
    assert len(sch.jobs) == 0


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_exec_all_jobs(n_jobs):
    sch = Scheduler()
    for _ in range(n_jobs):
        _ = sch.schedule(
            lambda: None,
            dt.timedelta(),
        )
    assert sch.exec_all_jobs() == n_jobs
