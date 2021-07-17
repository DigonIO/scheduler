import datetime as dt

import pytest
from helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    foo,
    samples_minutes_utc,
    samples_weeks_utc,
    utc,
    utc2,
)

from scheduler.job import Job, JobType
from scheduler.trigger import Trigger


def test_misc_properties():
    job = Job(
        job_type=JobType.CYCLIC,
        timing=[dt.timedelta()],
        handle=foo,
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
    assert job.kwargs == {"abc": 123}
    assert job.tags == {"test", "misc"}
    assert job.weight == 1 / 3
    assert job.delay == False
    assert job.start == T_2021_5_26__3_55_UTC
    assert job.stop == T_2021_5_26__3_55_UTC + dt.timedelta(seconds=1)
    assert job.tzinfo == utc
    assert job.skip_missing == True
    assert job._tzinfo == utc2


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
    start_1,
    start_2,
    tzinfo,
    result,
):
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


@pytest.mark.skip("Currently under redesign")
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
            [Trigger.Weekly.Sunday()],
            T_2021_5_26__3_55_UTC,
            dt.timedelta(minutes=2, seconds=8),
            utc,
            samples_weeks_utc,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_start_with_no_delay(
    job_type,
    timing,
    base,
    offset,
    tzinfo,
    patch_datetime_now,
):
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
