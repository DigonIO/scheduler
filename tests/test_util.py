import datetime as dt
from typing import Optional, Union

import pytest

import scheduler.trigger as trigger
from scheduler.base.scheduler_util import str_cutoff
from scheduler.error import SchedulerError
from scheduler.trigger.core import Weekday, _Weekday
from scheduler.util import (
    days_to_weekday,
    next_daily_occurrence,
    next_hourly_occurrence,
    next_minutely_occurrence,
    next_weekday_time_occurrence,
)

err_msg = r"Weekday enumeration interval: \[0,6\] <=> \[Monday, Sunday\]"


@pytest.mark.parametrize(
    "wkdy_src, wkdy_dest, days, err_msg",
    (
        [trigger.Monday(), trigger.Thursday(), 3, None],
        [trigger.Wednesday(), trigger.Sunday(), 4, None],
        [trigger.Friday(), trigger.Friday(), 7, None],
        [trigger.Saturday(), trigger.Thursday(), 5, None],
        [trigger.Sunday(), trigger.Saturday(), 6, None],
        [3, 8, 0, err_msg],
        [4, -1, 0, err_msg],
        [8, 4, 0, err_msg],
        [-1, 2, 0, err_msg],
    ),
)
def test_days_to_weekday(
    wkdy_src: Union[int, _Weekday], wkdy_dest: int, days: int, err_msg: Optional[str]
) -> None:
    if err_msg:
        assert isinstance(wkdy_src, int)
        with pytest.raises(SchedulerError, match=err_msg):
            days_to_weekday(wkdy_src, wkdy_dest)
    else:
        assert isinstance(wkdy_src, Weekday)
        assert isinstance(wkdy_dest, Weekday)

        assert days_to_weekday(wkdy_src.value, wkdy_dest.value) == days


@pytest.mark.parametrize(
    "now, wkdy, timestamp, target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            trigger.Friday(),
            dt.time(hour=0, minute=0),
            dt.datetime(year=2021, month=5, day=28),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            trigger.Wednesday(),
            dt.time(hour=12, minute=3, second=1),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=3, second=1),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=dt.timezone.utc),
            trigger.Thursday(),
            dt.time(hour=12, minute=3, second=1, tzinfo=dt.timezone.utc),
            dt.datetime(
                year=2021,
                month=5,
                day=27,
                hour=12,
                minute=3,
                second=1,
                tzinfo=dt.timezone.utc,
            ),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            trigger.Wednesday(),
            dt.time(hour=2),
            dt.datetime(year=2021, month=6, day=16, hour=2),
        ],
    ),
)
def test_next_weekday_time_occurrence(
    now: dt.datetime, wkdy: _Weekday, timestamp: dt.time, target: dt.datetime
) -> None:
    assert next_weekday_time_occurrence(now, wkdy, timestamp) == target


@pytest.mark.parametrize(
    "now, target_time, target_datetime",
    (
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(hour=2),
            dt.datetime(year=2021, month=6, day=16, hour=2),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(hour=13, second=45),
            dt.datetime(year=2021, month=6, day=16, hour=13, second=45),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(second=45),
            dt.datetime(year=2021, month=6, day=17, second=45),
        ],
    ),
)
def test_next_daily_occurence(
    now: dt.datetime, target_time: dt.time, target_datetime: dt.datetime
) -> None:
    assert next_daily_occurrence(now, target_time) == target_datetime


@pytest.mark.parametrize(
    "now, target_time, target_datetime",
    (
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(minute=7, second=3),
            dt.datetime(year=2021, month=6, day=16, hour=2, minute=7, second=3),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=23, minute=53, second=45),
            dt.time(minute=7, second=3),
            dt.datetime(year=2021, month=6, day=17, hour=0, minute=7, second=3),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(hour=4),
            dt.datetime(year=2021, month=6, day=16, hour=2),
        ],
    ),
)
def test_next_hourly_occurence(
    now: dt.datetime, target_time: dt.time, target_datetime: dt.datetime
) -> None:
    assert next_hourly_occurrence(now, target_time) == target_datetime


@pytest.mark.parametrize(
    "now, target_time, target_datetime",
    (
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(second=3),
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=54, second=3),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=23, minute=59, second=45),
            dt.time(second=44),
            dt.datetime(year=2021, month=6, day=17, hour=0, minute=0, second=44),
        ],
        [
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=53, second=45),
            dt.time(hour=4, minute=8, second=25),
            dt.datetime(year=2021, month=6, day=16, hour=1, minute=54, second=25),
        ],
    ),
)
def test_next_minutely_occurence(
    now: dt.datetime, target_time: dt.time, target_datetime: dt.datetime
) -> None:
    assert next_minutely_occurrence(now, target_time) == target_datetime


@pytest.mark.parametrize(
    "string, max_length, cut_tail, result, err",
    [
        ("abcdefg", 10, False, "abcdefg", None),
        ("abcdefg", 4, False, "#efg", None),
        ("abcdefg", 2, True, "a#", None),
        ("abcdefg", 1, True, "#", None),
        ("abcdefg", 0, True, "", "max_length < 1 not allowed"),
    ],
)
def test_str_cutoff(
    string: str, max_length: int, cut_tail: bool, result: str, err: Optional[str]
) -> None:
    if err:
        with pytest.raises(ValueError, match=err):
            str_cutoff(string, max_length, cut_tail)
    else:
        assert str_cutoff(string, max_length, cut_tail) == result
