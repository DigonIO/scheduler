import datetime as dt

import pytest
from helpers import patch_datetime_now, samples_job_creation

from scheduler import Scheduler


@pytest.mark.parametrize(
    "max_exec, job_count, exec_counts, patch_datetime_now",
    (
        [2, 5, 2, samples_job_creation],
        [2, 2, 2, samples_job_creation],
        [3, 2, 2, samples_job_creation],
        [5, 6, 5, samples_job_creation],
    ),
    indirect=["patch_datetime_now"],
)
def test_schedule_max_exec(patch_datetime_now, max_exec, job_count, exec_counts):
    sch = Scheduler(max_exec)

    for _ in range(job_count):
        sch.schedule(lambda: None, dt.timedelta())

    count = sch.exec_jobs()
    assert count == exec_counts
