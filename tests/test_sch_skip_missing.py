import datetime as dt
import time

import pytest
import pdb


from scheduler import Scheduler
from scheduler.job import Job, JobType

from helpers import (
    samples_days,
    samples_seconds,
    sample_seconds_interference,
    sample_seconds_interference_lag,
)


@pytest.mark.skip()
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
        # (
        #    samples_seconds[:1] + samples_seconds,
        #    [0, 0, 1, 1, 2, 2, 2, 3, 3, 3],  # should
        #    # [0, 0, 1, 2, 3, 4, 5, 6, 6, 6],  # BUG: is
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=samples_seconds[0],
        #        skip_missing=True,
        #    ),
        # ),
        # (
        #    samples_seconds[:1] + samples_seconds,
        #    [0, 0, 1, 2, 3, 4, 5, 6, 6, 6],
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=samples_seconds[0],
        #        skip_missing=False,
        #    ),
        # ),
        # (
        #    sample_seconds_interference[:1] + sample_seconds_interference,
        #    [None],  # NotImplemented
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=sample_seconds_interference[0],
        #        skip_missing=True,
        #    ),
        # ),
        # (
        #    sample_seconds_interference[:1] + sample_seconds_interference,
        #    [None],  # NotImplemented
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=sample_seconds_interference[0],
        #        skip_missing=False,
        #    ),
        # ),
        # (
        #    sample_seconds_interference_lag[:1] + sample_seconds_interference_lag,
        #    [None],  # NotImplemented
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=sample_seconds_interference_lag[0],
        #        skip_missing=True,
        #    ),
        # ),
        # (
        #    sample_seconds_interference_lag[:1] + sample_seconds_interference_lag,
        #    [None],  # NotImplemented
        #    Job(
        #        JobType.CYCLIC,
        #        [dt.timedelta(seconds=4), dt.timedelta(seconds=5)],
        #        print,
        #        start=sample_seconds_interference_lag[0],
        #        skip_missing=False,
        #    ),
        # ),
    ],
    indirect=["patch_datetime_now"],
)
def test_sch_skip_missing_batch(patch_datetime_now, counts, job):
    sch = Scheduler(jobs={job})
    for count in counts:
        sch.exec_jobs()
        assert job.attempts == count
