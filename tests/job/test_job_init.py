import datetime as dt

import pytest

from scheduler import SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday

from helpers import (
    utc,
    _TZ_ERROR_MSG,
    TZ_ERROR_MSG,
    START_STOP_ERROR,
)


@pytest.mark.parametrize(
    "job_type, timing, start, stop, tzinfo, err",
    (
        [JobType.WEEKLY, [Weekday.MONDAY], None, None, None, None],
        [JobType.WEEKLY, [Weekday.MONDAY, Weekday.TUESDAY], None, None, None, None],
        [JobType.WEEKLY, [Weekday.MONDAY], None, None, utc, None],
        [
            JobType.DAILY,
            [dt.time(tzinfo=utc)],
            dt.datetime.now(utc),
            None,
            utc,
            None,
        ],
        [
            JobType.DAILY,
            [dt.time(tzinfo=utc)],
            dt.datetime.now(utc),
            None,
            utc,
            None,
        ],
        [
            JobType.DAILY,
            [dt.time(tzinfo=None)],
            dt.datetime.now(utc),
            None,
            utc,
            TZ_ERROR_MSG,
        ],
        [
            JobType.DAILY,
            [dt.time(tzinfo=None)],
            None,
            None,
            utc,
            TZ_ERROR_MSG,
        ],
        [
            JobType.DAILY,
            [dt.time(tzinfo=None)],
            None,
            dt.datetime.now(utc),
            utc,
            TZ_ERROR_MSG,
        ],
        [
            JobType.DAILY,
            [dt.time()],
            dt.datetime.now(utc),
            None,
            None,
            _TZ_ERROR_MSG.format("start"),
        ],
        [
            JobType.DAILY,
            [dt.time()],
            None,
            dt.datetime.now(utc),
            None,
            _TZ_ERROR_MSG.format("stop"),
        ],
        [
            JobType.WEEKLY,
            [Weekday.MONDAY],
            dt.datetime.now(utc),
            dt.datetime.now(utc) - dt.timedelta(hours=1),
            utc,
            START_STOP_ERROR,
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
