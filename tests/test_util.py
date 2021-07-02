import datetime as dt

import pytest

from scheduler.util import (
    SchedulerError,
    Weekday,
    days_to_weekday,
    next_weekday_occurrence,
    next_weekday_time_occurrence,
    next_daily_occurrence,
    next_hourly_occurrence,
    next_minutely_occurrence,
    str_cutoff,
)

err_msg = "Weekday enumeration interval: [0,6] <=> [Monday, Sunday]"


@pytest.mark.parametrize(
    "wkdy_src, wkdy_dest, days, err_msg",
    (
        [Weekday.MONDAY, Weekday.THURSDAY, 3, None],
        [Weekday.WEDNESDAY, Weekday.SUNDAY, 4, None],
        [Weekday.FRIDAY, Weekday.FRIDAY, 7, None],
        [Weekday.SATURDAY, Weekday.THURSDAY, 5, None],
        [Weekday.SUNDAY, Weekday.SATURDAY, 6, None],
        [3, 8, 0, err_msg],
        [4, -1, 0, err_msg],
        [8, 4, 0, err_msg],
        [-1, 2, 0, err_msg],
    ),
)
def test_days_to_weekday(wkdy_src, wkdy_dest, days, err_msg):
    if err_msg:
        with pytest.raises(SchedulerError) as err:
            days_to_weekday(wkdy_src, wkdy_dest)
            assert err_msg == str(err.value)
    else:
        assert days_to_weekday(wkdy_src.value, wkdy_dest.value) == days


@pytest.mark.parametrize(
    "now, wkdy, target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.FRIDAY,
            dt.datetime(year=2021, month=5, day=28),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.WEDNESDAY,
            dt.datetime(year=2021, month=6, day=2),
        ],
        [
            dt.datetime(year=2021, month=5, day=27),
            Weekday.THURSDAY,
            dt.datetime(year=2021, month=6, day=3),
        ],
        [
            dt.datetime(year=2021, month=5, day=27, tzinfo=dt.timezone.utc),
            Weekday.THURSDAY,
            dt.datetime(year=2021, month=6, day=3, tzinfo=dt.timezone.utc),
        ],
    ),
)
def test_next_weekday_occurrence(now, wkdy, target):
    assert next_weekday_occurrence(now, wkdy) == target


@pytest.mark.parametrize(
    "now, wkdy, timestamp, target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.FRIDAY,
            dt.time(hour=0, minute=0),
            dt.datetime(year=2021, month=5, day=28),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.WEDNESDAY,
            dt.time(hour=12, minute=3, second=1),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=3, second=1),
        ],
        [
            dt.datetime(
                year=2021, month=5, day=26, hour=11, minute=39, tzinfo=dt.timezone.utc
            ),
            Weekday.THURSDAY,
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
            Weekday.WEDNESDAY,
            dt.time(hour=2),
            dt.datetime(year=2021, month=6, day=16, hour=2),
        ],
    ),
)
def test_next_weekday_time_occurrence(now, wkdy, timestamp, target):
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
def test_next_daily_occurence(now, target_time, target_datetime):
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
def test_next_hourly_occurence(now, target_time, target_datetime):
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
def test_next_minutely_occurence(now, target_time, target_datetime):
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
def test_str_cutoff(string, max_length, cut_tail, result, err):
    if err:
        with pytest.raises(ValueError, match=err) as execinfo:
            str_cutoff(string, max_length, cut_tail)
    else:
        assert str_cutoff(string, max_length, cut_tail) == result
