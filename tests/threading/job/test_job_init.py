import datetime as dt
from typing import Optional

import pytest

import scheduler.trigger as trigger
from scheduler import SchedulerError
from scheduler.base.definition import JobType
from scheduler.base.timingtype import TimingJobUnion
from scheduler.threading.job import Job

from ...helpers import _TZ_ERROR_MSG, START_STOP_ERROR, TZ_ERROR_MSG, utc


@pytest.mark.parametrize(
    "job_type, timing, start, stop, tzinfo, err",
    (
        [JobType.WEEKLY, [trigger.Monday()], None, None, None, None],
        [
            JobType.WEEKLY,
            [trigger.Monday(), trigger.Thursday()],
            None,
            None,
            None,
            None,
        ],
        [JobType.WEEKLY, [trigger.Monday(dt.time(tzinfo=utc))], None, None, utc, None],
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
            [trigger.Monday(dt.time(tzinfo=utc))],
            dt.datetime.now(utc),
            dt.datetime.now(utc) - dt.timedelta(hours=1),
            utc,
            START_STOP_ERROR,
        ],
    ),
)
def test_job_init(
    job_type: JobType,
    timing: TimingJobUnion,
    start: Optional[dt.datetime],
    stop: Optional[dt.datetime],
    tzinfo: Optional[dt.tzinfo],
    err: Optional[str],
) -> None:
    if err:
        with pytest.raises(SchedulerError, match=err):
            Job(
                job_type=job_type,
                timing=timing,
                handle=lambda: None,
                kwargs={},
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
            kwargs={},
            max_attempts=1,
            weight=20,
            start=start,
            stop=stop,
            tzinfo=tzinfo,
        )
