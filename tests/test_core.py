import copy
import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError, Weekday

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
    T_2021_5_26__3_55 + dt.timedelta(days=10, minutes=7),  # t8
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
    "exec_at, exec_counts, delta, patch_datetime_now",
    (
        [
            dt.timedelta(seconds=5),
            [1, 1, 2, 3, 4, 5, 6],
            dt.timedelta(seconds=-864385.0),
            samples,
        ],
        [
            dt.timedelta(hours=1, minutes=1),
            [0, 0, 0, 1, 2, 3, 4],
            dt.timedelta(seconds=-846120),
            samples,
        ],
        [
            Weekday.THURSDAY,
            [0, 0, 0, 0, 0, 1, 2],
            dt.timedelta(days=4, seconds=71880),
            samples,
        ],
        [
            dt.time(hour=3, minute=55, second=6),
            [0, 1, 1, 1, 1, 2, 3],
            dt.timedelta(days=-8, seconds=85986),
            samples,
        ],
        [
            (Weekday.THURSDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 0, 0, 0, 1, 2],
            dt.timedelta(days=4, seconds=85986),
            samples,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_general_schedule(patch_datetime_now, exec_at, exec_counts, delta):
    sch = Scheduler()
    job = sch.schedule(lambda: None, exec_at)

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count

    assert job.max_attemps == 0
    assert job._has_attempts_remaining == True
    assert job.handle() is None
    assert job.timedelta() == delta


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
    (
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
        assert job._has_attempts_remaining == (True if count == 0 else False)

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


@pytest.mark.parametrize(
    "max_exec, job_count, exec_counts, patch_datetime_now",
    (
        [2, 5, 2, samples_job_creation],
        [2, 2, 2, samples_job_creation],
        [3, 2, 2, samples_job_creation],
        [5, 6, 5, samples_job_creation],
    ),
    indirect=["patch_datetime_now"],
)
def test_schedule_job_limit(patch_datetime_now, max_exec, job_count, exec_counts):
    sch = Scheduler(max_exec)

    for i in range(job_count):
        _ = sch.schedule(lambda: None, dt.timedelta())

    count = sch.exec_jobs()
    assert count == exec_counts


wrong_input_msg = (
    "Wrong input! Select one of the following input types:\n"
    + "Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time] or \n"
    + "list[Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]]"
)


@pytest.mark.parametrize(
    "exec_at, exceptionMessage",
    [
        ("3min", wrong_input_msg),
        (dt.timedelta(seconds=5), None),
        (3.1, wrong_input_msg),
        (1, wrong_input_msg),
    ],
)
def test_invalid_exec_at(exec_at, exceptionMessage):
    sch = Scheduler()
    if exceptionMessage:
        with pytest.raises(SchedulerError) as excinfo:
            sch.schedule(lambda: None, exec_at)
            assert None in str(excinfo.value)
    else:
        sch.schedule(lambda: None, exec_at)


def kwargs_to_collection(collection: list, **kwargs):
    for key, value in kwargs.items():
        collection.append((key, value))


default_kwargs = {"collection": [], "a": 1, "p": "QWERTY"}


@pytest.mark.parametrize(
    "oneshot",
    [
        [True],
        [False],
    ],
)
def test_handle_params(oneshot):

    kwargs = copy.deepcopy(default_kwargs)

    sch = Scheduler()
    if oneshot:
        sch.once(kwargs_to_collection, dt.datetime.now(), params=kwargs)
    else:
        sch.schedule(
            kwargs_to_collection, dt.timedelta(seconds=5), params=kwargs, delay=False
        )

    sch.exec_jobs()

    for key, value in kwargs["collection"]:
        assert kwargs[key] == value


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_delete_all_jobs(n_jobs):
    sch = Scheduler()
    for i in range(n_jobs):
        job = sch.schedule(
            lambda: None,
            dt.timedelta(seconds=1),
        )
    assert len(sch.jobs) == n_jobs
    sch.delete_job(job)
    assert len(sch.jobs) == n_jobs - 1
    sch.delete_jobs()
    assert len(sch.jobs) == 0


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_exec_all_jobs(n_jobs):
    sch = Scheduler()
    for _ in range(n_jobs):
        _ = sch.schedule(
            lambda: None,
            dt.timedelta(),
        )
    assert sch.exec_all_jobs() == n_jobs
