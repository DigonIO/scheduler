import pytest
import time
import datetime as dt

from scheduler import Scheduler, Weekday, SchedulerError


T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday


def test_scheduler_instantiation():
    sch = Scheduler()
    assert len(sch.jobs) == 0


samples = [
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(hours=1, minutes=3),  # t4
    T_2021_5_26__3_55 + dt.timedelta(hours=2, minutes=2),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=1, minutes=2),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=7),  # t7
]


@pytest.fixture
def patch_datetime_now(monkeypatch, request):
    class datetime_patch:
        it = iter(request.param)

        @classmethod
        def now(cls, tz=None):
            return next(cls.it)

    monkeypatch.setattr(dt, "datetime", datetime_patch)


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now",
    (
        [dt.timedelta(seconds=5), [1, 1, 2, 3, 4, 5, 6], samples],
        [dt.timedelta(hours=1, minutes=1), [0, 0, 0, 1, 2, 3, 4], samples],
        [Weekday.THURSDAY, [0, 0, 0, 0, 0, 1, 2], samples],
        [dt.time(hour=3, minute=55, second=6), [0, 1, 1, 1, 1, 2, 3], samples],
        [
            (Weekday.THURSDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 0, 0, 0, 1, 2],
            samples,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_general_schedule(patch_datetime_now, exec_at, exec_counts):
    sch = Scheduler()
    job = sch.schedule(lambda: None, exec_at)

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count

    assert job.max_attemps == 0
    assert job.has_attempts == True
    assert job.handle() is None


error_msg = (
    'Wrong input for "once"! Select one of the following input types:\n'
    + "dt.datetime, Weekday, dt.time, dt.timedelta, tuple[Weekday, dt.time]"
)


# @pytest.mark.skip(reason="in way of debugging test_once_datetime")
@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now, err_msg",
    (
        [dt.timedelta(seconds=5), [1, 1, 1, 1, 1, 1, 1], samples, None],
        [dt.timedelta(hours=1, minutes=1), [0, 0, 0, 1, 1, 1, 1], samples, None],
        [Weekday.THURSDAY, [0, 0, 0, 0, 0, 1, 1], samples, None],
        [dt.time(hour=3, minute=55, second=6), [0, 1, 1, 1, 1, 1, 1], samples, None],
        [
            (Weekday.THURSDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 0, 0, 0, 1, 1],
            samples,
            None,
        ],
        [234, [], samples, error_msg],
        [25.1, [], samples, error_msg],
        ["foo bar", [], samples, error_msg],
        [{Weekday.FRIDAY}, [], samples, error_msg],
    ),
    indirect=["patch_datetime_now"],
)
def test_once(patch_datetime_now, exec_at, exec_counts, err_msg):
    sch = Scheduler()
    if err_msg:
        with pytest.raises(SchedulerError) as err:
            sch.once(lambda: None, exec_at)
            assert error_msg == str(err.value)
    else:
        job = sch.once(lambda: None, exec_at)

        for count in exec_counts:
            sch.exec_jobs()
            assert job.attemps == count


samples_once_datetime = [
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=6),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=7),  # t3
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t4
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=1),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=2),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=7),  # t7
]


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now",
    (  #                                       t1 t2 t3 t4 t5
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=6),
            [0, 1, 1, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=7),
            [0, 0, 1, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=8),
            [0, 0, 0, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=2),
            [0, 0, 0, 0, 0, 1, 1],
            samples_once_datetime,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_once_with_datetime_over_schedule(exec_at, exec_counts, patch_datetime_now):
    sch = Scheduler()
    job = sch.schedule(
        lambda: None,
        dt.timedelta(seconds=1),
        delay=False,
        offset=exec_at,
        max_attempts=1,
    )

    assert job.datetime == exec_at

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count
        assert job.has_attempts == (True if count == 0 else False)

    assert job.datetime == exec_at + dt.timedelta(seconds=1)


samples_seconds = [
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


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now",
    (
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds],
        [dt.timedelta(seconds=2), [1, 2, 3, 4, 5, 6, 7, 7], samples_seconds],
        [
            [Weekday.THURSDAY, Weekday.SATURDAY],
            [1, 1, 2, 2, 3, 4, 4, 4],
            samples_days,
        ],
        [
            (Weekday.SATURDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 1, 1, 1, 2, 2, 2],
            samples_days,
        ],
        [
            [
                dt.timedelta(days=4),
                (Weekday.SATURDAY, dt.time(hour=3, minute=55, second=6)),
            ],
            [0, 0, 1, 2, 3, 4, 4, 4],
            samples_days,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_schedule(patch_datetime_now, exec_at, exec_counts):
    sch = Scheduler()
    job = sch.schedule(lambda: None, exec_at)

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count
