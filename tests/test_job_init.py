import datetime as dt

import pytest

from scheduler import SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday

T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
utc = dt.timezone.utc

_TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together for {0}."
TZ_ERROR_MSG = _TZ_ERROR_MSG[:-9] + "."


@pytest.mark.parametrize(
    "job_type, timing, start, stop, tzinfo, err",
    (
        [JobType.WEEKLY, Weekday.MONDAY, None, None, None, None],
        [JobType.WEEKLY, [Weekday.MONDAY, Weekday.TUESDAY], None, None, None, None],
        [JobType.WEEKLY, Weekday.MONDAY, None, None, utc, None],
        [
            JobType.DAILY,
            dt.time(tzinfo=utc),
            dt.datetime.now(utc),
            None,
            utc,
            None,
        ],
        [
            JobType.DAILY,
            dt.time(tzinfo=utc),
            None,
            dt.datetime.now(utc),
            utc,
            None,
        ],
        [
            JobType.DAILY,
            dt.time(tzinfo=None),
            dt.datetime.now(utc),
            None,
            utc,
            TZ_ERROR_MSG,
        ],
        [
            JobType.DAILY,
            dt.time(tzinfo=None),
            None,
            dt.datetime.now(utc),
            utc,
            TZ_ERROR_MSG,
        ],
        [
            JobType.DAILY,
            dt.time(),
            dt.datetime.now(utc),
            None,
            None,
            _TZ_ERROR_MSG.format("start"),
        ],
        [
            JobType.DAILY,
            dt.time(),
            None,
            dt.datetime.now(utc),
            None,
            _TZ_ERROR_MSG.format("stop"),
        ],
    ),
)
def test_job_init(
    job_type,
    timing,
    start,
    stop,
    tzinfo,
    err,
):
    if err:
        with pytest.raises(SchedulerError, match=err):
            Job(
                job_type=job_type,
                timing=timing,
                handle=lambda: None,
                params={},
                max_attempts=1,
                weight=20,
                start=start,
                stop=stop,
                tzinfo=tzinfo,
            )
    else:
        Job(
            job_type=job_type,
            timing=timing,
            handle=lambda: None,
            params={},
            max_attempts=1,
            weight=20,
            start=start,
            stop=stop,
            tzinfo=tzinfo,
        )
