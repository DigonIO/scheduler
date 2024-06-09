import datetime as dt
from typing import Any, Optional

import pytest

import scheduler.trigger as trigger
from scheduler.base.definition import JobType
from scheduler.base.timingtype import TimingJobUnion
from scheduler.threading.job import Job

from ...helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    foo,
    samples_minutes_utc,
    samples_weeks_utc,
    utc,
    utc2,
)


def test_misc_properties(recwarn: pytest.WarningsRecorder) -> None:
    job = Job(
        job_type=JobType.CYCLIC,
        timing=[dt.timedelta()],
        handle=foo,
        args=(8, "bar"),
        kwargs={"abc": 123},
        tags={"test", "misc"},
        weight=1 / 3,
        delay=False,
        start=T_2021_5_26__3_55_UTC,
        stop=T_2021_5_26__3_55_UTC + dt.timedelta(seconds=1),
        skip_missing=True,
        tzinfo=utc2,
    )
    assert job.type == JobType.CYCLIC
    assert job.handle == foo
    assert job.args == (8, "bar")
    assert job.kwargs == {"abc": 123}
    assert job.tags == {"test", "misc"}
    assert job.weight == 1 / 3
    assert job.start == T_2021_5_26__3_55_UTC
    assert job.stop == T_2021_5_26__3_55_UTC + dt.timedelta(seconds=1)
    assert job.tzinfo == utc
    assert job.skip_missing == True
    assert job._tzinfo == utc2

    assert job.delay == False
    warn = recwarn.pop(DeprecationWarning)
    assert (
        str(warn.message)
        == "Using the `delay` property is deprecated and will be removed in the next minor release."
    )


@pytest.mark.parametrize(
    "start_1, start_2, tzinfo, result",
    (
        [T_2021_5_26__3_55, T_2021_5_26__3_55, None, False],
        [T_2021_5_26__3_55, T_2021_5_26__3_55 + dt.timedelta(hours=1), None, True],
        [T_2021_5_26__3_55, T_2021_5_26__3_55 + dt.timedelta(hours=-1), None, False],
        [T_2021_5_26__3_55_UTC, T_2021_5_26__3_55_UTC, utc, False],
        [
            T_2021_5_26__3_55_UTC,
            T_2021_5_26__3_55_UTC + dt.timedelta(hours=1),
            utc,
            True,
        ],
        [
            T_2021_5_26__3_55_UTC,
            T_2021_5_26__3_55_UTC + dt.timedelta(hours=-1),
            utc,
            False,
        ],
    ),
)
def test_job__lt__(
    start_1: dt.datetime,
    start_2: dt.datetime,
    tzinfo: Optional[dt.tzinfo],
    result: bool,
) -> None:
    job_1 = Job(
        job_type=JobType.CYCLIC,
        timing=[dt.timedelta()],
        handle=lambda: None,
        start=start_1,
        tzinfo=tzinfo,
    )
    job_2 = Job(
        job_type=JobType.CYCLIC,
        timing=[dt.timedelta()],
        handle=lambda: None,
        start=start_2,
        tzinfo=tzinfo,
    )
    assert (job_1 < job_2) == result


@pytest.mark.parametrize(
    "job_type, timing, base, offset, tzinfo, patch_datetime_now",
    (
        [
            JobType.CYCLIC,
            [dt.timedelta(minutes=2)],
            T_2021_5_26__3_55_UTC,
            dt.timedelta(minutes=2, seconds=8),
            utc,
            samples_minutes_utc,
        ],
        [
            JobType.CYCLIC,
            [dt.timedelta(weeks=2)],
            T_2021_5_26__3_55_UTC,
            dt.timedelta(minutes=2, seconds=8),
            utc,
            samples_minutes_utc,
        ],
        [
            JobType.WEEKLY,
            [trigger.Sunday(dt.time(tzinfo=utc))],
            T_2021_5_26__3_55_UTC,
            dt.timedelta(minutes=2, seconds=8),
            utc,
            samples_weeks_utc,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_start_with_no_delay(
    job_type: JobType,
    timing: TimingJobUnion,
    base: dt.datetime,
    offset: dt.timedelta,
    tzinfo: dt.tzinfo,
    patch_datetime_now: Any,
) -> None:
    job = Job(
        job_type=job_type,
        timing=timing,
        handle=lambda: None,
        start=base + offset,
        delay=False,
        tzinfo=tzinfo,
    )

    assert job.datetime == base + offset
    assert job.timedelta() == offset
