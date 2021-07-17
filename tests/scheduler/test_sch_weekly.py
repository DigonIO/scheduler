import datetime as dt

import pytest
from helpers import (
    DUPLICATE_EFFECTIVE_TIME,
    TZ_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
    foo,
    samples_weeks,
    samples_weeks_utc,
    utc,
)

from scheduler import Scheduler, SchedulerError
from scheduler.trigger import Trigger

MONDAY_23_UTC = Trigger.Weekly.Monday(dt.time(hour=23, tzinfo=dt.timezone.utc))
MONDAY_23_UTC_AS_SUNDAY = Trigger.Weekly.Sunday(
    dt.time(
        hour=23,
        minute=30,
        tzinfo=dt.timezone(-dt.timedelta(hours=23, minutes=30)),
    )
)
MONDAY_23_UTC_AS_TUESDAY = Trigger.Weekly.Thursday(
    dt.time(hour=1, tzinfo=dt.timezone(dt.timedelta(hours=2))),
)
FRIDAY_4 = Trigger.Weekly.Friday(dt.time(hour=4, tzinfo=None))
FRIDAY_4_UTC = Trigger.Weekly.Friday(dt.time(hour=4, tzinfo=utc))


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [
            Trigger.Weekly.Friday(),
            [1, 2, 2, 2, 3, 3, 4, 4],
            samples_weeks,
            None,
            None,
        ],
        [
            FRIDAY_4_UTC,
            [1, 1, 2, 2, 2, 3, 3, 4],
            samples_weeks_utc,
            utc,
            None,
        ],
        [
            Trigger.Weekly.Sunday(),
            [1, 1, 1, 2, 2, 3, 3, 3],
            samples_weeks,
            None,
            None,
        ],
        [
            [Trigger.Weekly.Wednesday(), Trigger.Weekly.Wednesday()],
            [],
            samples_weeks_utc,
            None,
            DUPLICATE_EFFECTIVE_TIME,
        ],
        [
            [MONDAY_23_UTC_AS_SUNDAY, MONDAY_23_UTC],
            [],
            samples_weeks_utc,
            None,
            DUPLICATE_EFFECTIVE_TIME,
        ],
        [
            [MONDAY_23_UTC, MONDAY_23_UTC_AS_TUESDAY],
            [],
            samples_weeks_utc,
            None,
            DUPLICATE_EFFECTIVE_TIME,
        ],
        [
            [MONDAY_23_UTC_AS_SUNDAY, MONDAY_23_UTC_AS_TUESDAY],
            [],
            samples_weeks_utc,
            None,
            DUPLICATE_EFFECTIVE_TIME,
        ],
        [
            [Trigger.Weekly.Wednesday(), Trigger.Weekly.Sunday()],
            [1, 2, 2, 3, 4, 5, 6, 6],
            samples_weeks_utc,
            None,
            None,
        ],
        [
            [FRIDAY_4_UTC, FRIDAY_4],
            [],
            samples_weeks_utc,
            utc,
            TZ_ERROR_MSG,
        ],
        [dt.time(), [], samples_weeks, None, WEEKLY_TYPE_ERROR_MSG],
        [dt.timedelta(), [], samples_weeks, None, WEEKLY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_weekly(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.weekly(timing=timing, handle=foo)
            assert msg == err_msg
    else:
        job = sch.weekly(timing=timing, handle=foo)
        for count in counts:
            sch.exec_jobs()
            assert job.attempts == count
