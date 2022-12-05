import datetime as dt

import pytest

from scheduler import Scheduler

from ...helpers import foo


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
def test_exec_all_jobs(n_jobs):
    sch = Scheduler()

    assert len(sch.jobs) == 0
    for _ in range(n_jobs):
        sch.once(dt.datetime.now(), foo)
    assert len(sch.jobs) == n_jobs

    exec_job_count = sch.exec_jobs(force_exec_all=True)
    assert exec_job_count == n_jobs
    assert len(sch.jobs) == 0
