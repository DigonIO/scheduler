import datetime as dt

import pytest
from helpers import patch_datetime_now, samples

from scheduler import Scheduler, Weekday


@pytest.mark.parametrize(
    "exec_at, exec_counts, delta, patch_datetime_now",
    (
        [
            dt.timedelta(seconds=5),
            [1, 1, 2, 3, 4, 5, 6],
            dt.timedelta(seconds=-864385.0),
            samples,
        ],
        [
            dt.timedelta(hours=1, minutes=1),
            [0, 0, 0, 1, 2, 3, 4],
            dt.timedelta(seconds=-846120),
            samples,
        ],
        [
            Weekday.THURSDAY,
            [0, 0, 0, 0, 0, 1, 2],
            dt.timedelta(days=4, seconds=71880),
            samples,
        ],
        [
            dt.time(hour=3, minute=55, second=6),
            [0, 1, 1, 1, 1, 2, 3],
            dt.timedelta(days=-8, seconds=85986),
            samples,
        ],
        [
            (Weekday.THURSDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 0, 0, 0, 1, 2],
            dt.timedelta(days=4, seconds=85986),
            samples,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_schedule_general(patch_datetime_now, exec_at, exec_counts, delta):
    sch = Scheduler()
    job = sch.schedule(lambda: None, exec_at)

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count

    assert job.max_attemps == 0
    assert job._has_attempts_remaining is True
    assert job.handle() is None
    assert job.timedelta() == delta
