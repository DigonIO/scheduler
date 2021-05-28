import pytest
import datetime as dt

from scheduler.util import (
    SchedulerError,
    Weekday,
    days_to_weekday,
    next_time_occurrence,
    next_weekday_occurrence,
    next_weekday_time_occurrence,
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
    "now, timestamp, target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.time(hour=0, minute=0),
            dt.datetime(year=2021, month=5, day=27),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.time(hour=12, minute=3, second=1),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=3, second=1),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.time(hour=11, minute=39),
            dt.datetime(year=2021, month=5, day=27, hour=11, minute=39),
        ],
        [
            dt.datetime(
                year=2021, month=5, day=26, hour=11, minute=39, tzinfo=dt.timezone.utc
            ),
            dt.time(hour=12, minute=3, second=1, tzinfo=dt.timezone.utc),
            dt.datetime(
                year=2021,
                month=5,
                day=26,
                hour=12,
                minute=3,
                second=1,
                tzinfo=dt.timezone.utc,
            ),
        ],
    ),
)
def test_next_time_occurrence(now, timestamp, target):
    assert next_time_occurrence(now, timestamp) == target


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
            dt.datetime(year=2021, month=6, day=2, hour=12, minute=3, second=1),
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
    ),
)
def test_next_weekday_time_occurrence(now, wkdy, timestamp, target):
    assert next_weekday_time_occurrence(now, wkdy, timestamp) == target
