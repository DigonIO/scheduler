import datetime as dt

import pytest

T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday


@pytest.fixture
def patch_datetime_now(monkeypatch, request):
    class DatetimePatch:
        it = iter(request.param)

        @classmethod
        def now(cls, tz=None):
            return next(cls.it)

    monkeypatch.setattr(dt, "datetime", DatetimePatch)


samples = [
    T_2021_5_26__3_55,  # scheduler init
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(hours=1, minutes=3),  # t4
    T_2021_5_26__3_55 + dt.timedelta(hours=2, minutes=2),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=1, minutes=2),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=7),  # t7
    T_2021_5_26__3_55 + dt.timedelta(days=10, minutes=7),  # t8
]

samples_once_datetime = [
    T_2021_5_26__3_55,  # scheduler init
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=6),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=7),  # t3
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t4
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=1),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=2),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=7),  # t7
]

samples_seconds = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(seconds=11),  # t4
    T_2021_5_26__3_55 + dt.timedelta(seconds=14.999),  # t5
    T_2021_5_26__3_55 + dt.timedelta(seconds=15),  # t6
    T_2021_5_26__3_55 + dt.timedelta(seconds=15.001),  # t7
    T_2021_5_26__3_55 + dt.timedelta(seconds=15.002),  # t8
]

samples_days = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(days=1, seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(days=1, seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(days=3, seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(days=4, seconds=11),  # t4
    T_2021_5_26__3_55 + dt.timedelta(days=10, seconds=5.999),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=10, seconds=6),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=10, seconds=6.001),  # t7
    T_2021_5_26__3_55 + dt.timedelta(days=11, seconds=6.002),  # t8
]

samples_job_creation = [
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
    T_2021_5_26__3_55,
]
