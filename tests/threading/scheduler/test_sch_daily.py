import datetime as dt
from typing import Any, Optional

import pytest

import scheduler.trigger as trigger
from scheduler import Scheduler, SchedulerError

from ...helpers import (
    DAILY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    foo,
    samples_days,
    samples_days_utc,
    utc,
)


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [
            dt.time(hour=4, minute=30),
            [1, 2, 3, 4, 5, 6, 6, 6],
            samples_days,
            None,
            None,
        ],
        [
            dt.time(hour=16, minute=45),
            [1, 1, 2, 3, 4, 5, 6, 6],
            samples_days,
            None,
            None,
        ],
        [
            dt.time(hour=14, tzinfo=utc),
            [1, 1, 2, 3, 4, 5, 6, 6],
            samples_days_utc,
            utc,
            None,
        ],
        [dt.time(hour=2), [], samples_days_utc, utc, TZ_ERROR_MSG],
        [trigger.Monday(), [], samples_days, None, DAILY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_daily(
    timing: dt.timedelta,
    counts: list[int],
    patch_datetime_now: Any,
    tzinfo: Optional[dt.tzinfo],
    err_msg: Optional[str],
) -> None:
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job = sch.daily(timing=timing, handle=foo)
    else:
        job = sch.daily(timing=timing, handle=foo)
        for count in counts:
            sch.exec_jobs()
            assert job.attempts == count
