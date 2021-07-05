import datetime as dt

import pytest
import pdb


from scheduler import Scheduler
from scheduler.job import Job, JobType

from helpers import samples_days, sample_seconds_interference_lag


@pytest.mark.parametrize(
    "patch_datetime_now, counts, job",
    [
        (
            samples_days[:1] + samples_days,
            [1, 1, 2, 2, 3, 4, 5, 5, 5, 5],  # should
            # [1, 2, 3, 4, 5, 6, 7, 8, 8, 8],  # BUG: is
            Job(
                JobType.DAILY,
                [t.time() for t in samples_days[:2]],
                print,
                start=samples_days[0] - dt.timedelta(days=1),
                skip_missing=True,
            ),
        ),
        (
            samples_days[:1] + samples_days,
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            Job(
                JobType.DAILY,
                [t.time() for t in samples_days[:2]],
                print,
                start=samples_days[0] - dt.timedelta(days=1),
                skip_missing=False,
            ),
        ),
        (
            sample_seconds_interference_lag,
            [0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6],
            Job(
                JobType.CYCLIC,
                dt.timedelta(seconds=4),
                print,
                start=sample_seconds_interference_lag[0],
                skip_missing=False,
            ),
        ),
        (
            sample_seconds_interference_lag,
            [0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5],
            Job(
                JobType.CYCLIC,
                dt.timedelta(seconds=4),
                print,
                start=sample_seconds_interference_lag[0],
                skip_missing=True,
            ),
        ),
    ],
    indirect=["patch_datetime_now"],
)
def test_sch_skip_missing(patch_datetime_now, counts, job):
    sch = Scheduler(jobs={job})
    attempts = []
    for _ in counts:
        sch.exec_jobs()
        attempts.append(job.attempts)

    assert attempts == counts
