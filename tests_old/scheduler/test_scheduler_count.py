import datetime as dt

import pytest
from helpers import patch_datetime_now, samples_days, samples_seconds

from scheduler import Scheduler, Weekday


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now",
    (
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds],
        [dt.timedelta(seconds=2), [1, 2, 3, 4, 5, 6, 7, 7], samples_seconds],
        [
            [Weekday.THURSDAY, Weekday.SATURDAY],
            [1, 1, 2, 2, 3, 4, 4, 4],
            samples_days,
        ],
        [
            (Weekday.SATURDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 1, 1, 1, 2, 2, 2],
            samples_days,
        ],
        [
            [
                dt.timedelta(days=4),
                (Weekday.SATURDAY, dt.time(hour=3, minute=55, second=6)),
            ],
            [0, 0, 1, 2, 3, 4, 4, 4],
            samples_days,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_schedule_count(patch_datetime_now, exec_at, exec_counts):
    sch = Scheduler()
    job = sch.schedule(lambda: None, exec_at)

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count
