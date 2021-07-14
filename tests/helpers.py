import datetime as dt

from scheduler.job import JobType
from scheduler.util import Weekday


utc = dt.timezone.utc
utc2 = dt.timezone(dt.timedelta(hours=2))
T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
T_2021_5_26__3_55_UTC = dt.datetime(2021, 5, 26, 3, 55, tzinfo=utc)

CYCLIC_TYPE_ERROR_MSG = (
    "Wrong input for Cyclic! Expected input type:\n" + "datetime.timedelta"
)
_DAILY_TYPE_ERROR_MSG = (
    "Wrong input for {0}! Select one of the following input types:\n"
    + "datetime.time | list[datetime.time]"
)
MINUTELY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Minutely")
HOURLY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Hourly")
DAILY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Daily")
WEEKLY_TYPE_ERROR_MSG = (
    "Wrong input for Weekly! Select one of the following input types:\n"
    + "DAY | list[DAY]\n"
    + "where `DAY = Weekday | tuple[Weekday, dt.time]`"
)

ONCE_TYPE_ERROR_MSG = (
    "Wrong input for Once! Select one of the following input types:\n"
    + "dt.datetime | dt.timedelta | Weekday | dt.time | tuple[Weekday, dt.time]"
)

DELETION_MODE_ERROR = "Unknown deletion mode, chose 'any' or 'all'"

DUPLICATE_EFFECTIVE_TIME = "Times that are effectively identical are not allowed."

_TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together for {0}."
TZ_ERROR_MSG = _TZ_ERROR_MSG[:-9] + "."

START_STOP_ERROR = "Start argument must be smaller than the stop argument."

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

samples_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler init
    T_2021_5_26__3_55_UTC,  # job creation
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=1, minutes=3),  # t4
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=2, minutes=2),  # t5
    T_2021_5_26__3_55_UTC + dt.timedelta(days=1, minutes=2),  # t6
    T_2021_5_26__3_55_UTC + dt.timedelta(days=9, minutes=7),  # t7
    T_2021_5_26__3_55_UTC + dt.timedelta(days=10, minutes=7),  # t8
]

sample_seconds_interference = [
    T_2021_5_26__3_55,  # scheduler init
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=4),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=4.1),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t3
    T_2021_5_26__3_55 + dt.timedelta(seconds=5.1),  # t4
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t5
    T_2021_5_26__3_55 + dt.timedelta(seconds=8.1),  # t6
    T_2021_5_26__3_55 + dt.timedelta(seconds=10),  # t7
    T_2021_5_26__3_55 + dt.timedelta(seconds=10.1),  # t8
    T_2021_5_26__3_55 + dt.timedelta(seconds=12),  # t9
    T_2021_5_26__3_55 + dt.timedelta(seconds=12.1),  # t10
    T_2021_5_26__3_55 + dt.timedelta(seconds=15),  # t11
    T_2021_5_26__3_55 + dt.timedelta(seconds=15.1),  # t12
    T_2021_5_26__3_55 + dt.timedelta(seconds=16),  # t13
    T_2021_5_26__3_55 + dt.timedelta(seconds=16.1),  # t14
    T_2021_5_26__3_55 + dt.timedelta(seconds=20),  # t15
    T_2021_5_26__3_55 + dt.timedelta(seconds=20.1),  # t16
    T_2021_5_26__3_55 + dt.timedelta(seconds=24),  # t17
    T_2021_5_26__3_55 + dt.timedelta(seconds=24.1),  # t18
    T_2021_5_26__3_55 + dt.timedelta(seconds=25.1),  # t19
    T_2021_5_26__3_55 + dt.timedelta(seconds=25.1),  # t20
]

sample_seconds_interference_lag = [
    T_2021_5_26__3_55,  # scheduler init
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=4),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=4.1),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t3
    T_2021_5_26__3_55 + dt.timedelta(seconds=5.1),  # t4
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t5
    T_2021_5_26__3_55 + dt.timedelta(seconds=8.1),  # t6
    T_2021_5_26__3_55 + dt.timedelta(seconds=13),  # t7
    T_2021_5_26__3_55 + dt.timedelta(seconds=13.1),  # t8
    T_2021_5_26__3_55 + dt.timedelta(seconds=15),  # t11
    T_2021_5_26__3_55 + dt.timedelta(seconds=15.1),  # t12
    T_2021_5_26__3_55 + dt.timedelta(seconds=16),  # t13
    T_2021_5_26__3_55 + dt.timedelta(seconds=16.1),  # t14
    T_2021_5_26__3_55 + dt.timedelta(seconds=20),  # t15
    T_2021_5_26__3_55 + dt.timedelta(seconds=20.1),  # t16
    T_2021_5_26__3_55 + dt.timedelta(seconds=24),  # t17
    T_2021_5_26__3_55 + dt.timedelta(seconds=24.1),  # t18
    T_2021_5_26__3_55 + dt.timedelta(seconds=25.1),  # t19
    T_2021_5_26__3_55 + dt.timedelta(seconds=25.1),  # t20
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

samples_seconds_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler creation
    T_2021_5_26__3_55_UTC,  # job creation
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=11),  # t4
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=14.999),  # t5
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=15),  # t6
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=15.001),  # t7
    T_2021_5_26__3_55_UTC + dt.timedelta(seconds=15.002),  # t8
]

samples_half_minutes = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(minutes=0, seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(minutes=0, seconds=10),  # t2
    T_2021_5_26__3_55 + dt.timedelta(minutes=0, seconds=30),  # t3
    T_2021_5_26__3_55 + dt.timedelta(minutes=1, seconds=10),  # t4
    T_2021_5_26__3_55 + dt.timedelta(minutes=1, seconds=40),  # t5
    T_2021_5_26__3_55 + dt.timedelta(minutes=2, seconds=0),  # t6
    T_2021_5_26__3_55 + dt.timedelta(minutes=2, seconds=20),  # t7
    T_2021_5_26__3_55 + dt.timedelta(minutes=2, seconds=40),  # t8
    T_2021_5_26__3_55 + dt.timedelta(minutes=3, seconds=5),  # t9
]

samples_minutes = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(minutes=1, seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(minutes=2, seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(minutes=3, seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(minutes=4, seconds=31),  # t4
    T_2021_5_26__3_55 + dt.timedelta(minutes=5, seconds=38.999),  # t5
    T_2021_5_26__3_55 + dt.timedelta(minutes=5, seconds=39),  # t6
    T_2021_5_26__3_55 + dt.timedelta(minutes=5, seconds=39.001),  # t7
    T_2021_5_26__3_55 + dt.timedelta(minutes=5, seconds=39.002),  # t8
]

samples_minutes_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler creation
    T_2021_5_26__3_55_UTC,  # job creation
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=1, seconds=5),  # t1
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=2, seconds=8),  # t2
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=3, seconds=11),  # t3
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=4, seconds=31),  # t4
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=5, seconds=38.999),  # t5
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=5, seconds=39),  # t6
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=5, seconds=39.001),  # t7
    T_2021_5_26__3_55_UTC + dt.timedelta(minutes=5, seconds=39.002),  # t8
]

samples_hours = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(hours=1, minutes=5),  # t1 05:00
    T_2021_5_26__3_55 + dt.timedelta(hours=2, minutes=8),  # t2 06:03
    T_2021_5_26__3_55 + dt.timedelta(hours=3, minutes=11),  # t3 07:06
    T_2021_5_26__3_55 + dt.timedelta(hours=4, minutes=31),  # t4 08:26
    T_2021_5_26__3_55 + dt.timedelta(hours=5, minutes=38.999),  # t5
    T_2021_5_26__3_55 + dt.timedelta(hours=5, minutes=39),  # t6
    T_2021_5_26__3_55 + dt.timedelta(hours=5, minutes=39.001),  # t7
    T_2021_5_26__3_55 + dt.timedelta(hours=5, minutes=39.002),  # t8
]

samples_hours_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler creation
    T_2021_5_26__3_55_UTC,  # job creation
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=1, minutes=5),  # t1
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=2, minutes=8),  # t2
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=3, minutes=11),  # t3
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=4, minutes=31),  # t4
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=5, minutes=38.999),  # t5
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=5, minutes=39),  # t6
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=5, minutes=39.001),  # t7
    T_2021_5_26__3_55_UTC + dt.timedelta(hours=5, minutes=39.002),  # t8
]


samples_days = [
    T_2021_5_26__3_55,  # scheduler creation
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(days=1, hours=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(days=1, hours=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(days=3, hours=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(days=4, hours=11),  # t4
    T_2021_5_26__3_55 + dt.timedelta(days=5, hours=14.999),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=5, hours=14),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=5, hours=14.001),  # t7
    T_2021_5_26__3_55 + dt.timedelta(days=5, hours=14.002),  # t8
]

samples_days_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler creation
    T_2021_5_26__3_55_UTC,  # job creation
    T_2021_5_26__3_55_UTC + dt.timedelta(days=1, hours=5),  # t1
    T_2021_5_26__3_55_UTC + dt.timedelta(days=1, hours=8),  # t2
    T_2021_5_26__3_55_UTC + dt.timedelta(days=3, hours=11),  # t3
    T_2021_5_26__3_55_UTC + dt.timedelta(days=4, hours=11),  # t4
    T_2021_5_26__3_55_UTC + dt.timedelta(days=5, hours=14.999),  # t5
    T_2021_5_26__3_55_UTC + dt.timedelta(days=5, hours=14),  # t6
    T_2021_5_26__3_55_UTC + dt.timedelta(days=5, hours=14.001),  # t7
    T_2021_5_26__3_55_UTC + dt.timedelta(days=5, hours=14.002),  # t8
]


samples_weeks = [
    T_2021_5_26__3_55,  # scheduler creation WEDNESDAY
    T_2021_5_26__3_55,  # job creation WEDNESDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=1, days=1),  # t1 THURSDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=1, days=2),  # t2 FRIDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=1, days=2, minutes=5),  # t3 FRIDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=2, days=1),  # t4 THURSDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=2, days=2),  # t5 FRIDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=3, days=1),  # t6 THURSDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=3, days=2),  # t7 FRIDAY
    T_2021_5_26__3_55 + dt.timedelta(weeks=3, days=3),  # t8 SATURDAY
]

samples_weeks_utc = [
    T_2021_5_26__3_55_UTC,  # scheduler creation WEDNESDAY
    T_2021_5_26__3_55_UTC,  # job creation WEDNESDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=1, days=1),  # t1 THURSDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=1, days=2),  # t2 FRIDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=1, days=2, minutes=5),  # t3 FRIDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=2, days=1),  # t4 THURSDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=2, days=2),  # t5 FRIDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=3, days=1),  # t6 THURSDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=3, days=2),  # t7 FRIDAY
    T_2021_5_26__3_55_UTC + dt.timedelta(weeks=3, days=3),  # t8 SATURDAY
]


def foo():
    print("foo")


def bar(msg="bar"):
    print(msg)


job_args = (
    {
        "job_type": JobType.CYCLIC,
        "timing": [dt.timedelta(hours=1)],
        "handle": foo,
        "params": None,
        "max_attempts": 1,
        "weight": 1,
        "delay": True,
        "start": T_2021_5_26__3_55,
        "stop": None,
        "skip_missing": True,
        "tzinfo": None,
    },
    {
        "job_type": JobType.MINUTELY,
        "timing": [dt.time(second=20)],
        "handle": bar,
        "params": {"msg": "foobar"},
        "max_attempts": 20,
        "weight": 0,
        "delay": False,
        "start": T_2021_5_26__3_55 - dt.timedelta(seconds=45),
        "stop": T_2021_5_26__3_55 + dt.timedelta(minutes=10),
        "skip_missing": False,
        "tzinfo": None,
    },
    {
        "job_type": JobType.DAILY,
        "timing": [dt.time(hour=7, minute=5)],
        "handle": foo,
        "params": None,
        "max_attempts": 7,
        "weight": 1,
        "delay": True,
        "start": T_2021_5_26__3_55,
        "stop": None,
        "skip_missing": True,
        "tzinfo": None,
    },
)

job_reprs = (
    [
        "scheduler.Job(<JobType.CYCLIC: 1>, [datetime.timedelta(seconds=3600)], <function foo at 0x",
        ">, {}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
    ],
    [
        "scheduler.Job(<JobType.MINUTELY: 2>, [datetime.time(0, 0, 20)], <function bar at 0x",
        (
            ">, {'msg': 'foobar'}, 20, 0, False, datetime.datetime(2021, 5, 26, 3, 54, 15),"
            " datetime.datetime(2021, 5, 26, 4, 5), False, None)"
        ),
    ],
    [
        "scheduler.Job(<JobType.DAILY: 4>, [datetime.time(7, 5)], <function foo at 0x",
        ">, {}, 7, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
    ],
)

job_args_utc = (
    {
        "job_type": JobType.CYCLIC,
        "timing": [dt.timedelta(hours=1)],
        "handle": foo,
        "params": None,
        "max_attempts": 0,
        "weight": 1 / 3,
        "delay": False,
        "start": T_2021_5_26__3_55_UTC - dt.timedelta(microseconds=10),
        "stop": None,
        "skip_missing": True,
        "tzinfo": utc,
    },
    {
        "job_type": JobType.HOURLY,
        "timing": [dt.time(hour=7, minute=5, tzinfo=utc)],
        "handle": print,
        "params": None,
        "max_attempts": 0,
        "weight": 20,
        "delay": False,
        "start": T_2021_5_26__3_55_UTC,
        "stop": T_2021_5_26__3_55_UTC + dt.timedelta(hours=20),
        "skip_missing": False,
        "tzinfo": utc,
    },
    {
        "job_type": JobType.WEEKLY,
        "timing": [Weekday.MONDAY],
        "handle": bar,
        "params": None,
        "max_attempts": 0,
        "weight": 1,
        "delay": False,
        "start": T_2021_5_26__3_55_UTC - dt.timedelta(days=1),
        "stop": None,
        "skip_missing": True,
        "tzinfo": utc,
    },
    {
        "job_type": JobType.WEEKLY,
        "timing": [
            Weekday.WEDNESDAY,
            (Weekday.TUESDAY, dt.time(23, 45, 59, tzinfo=utc)),
        ],
        "handle": print,
        "params": {"end": "FOO\n"},
        "max_attempts": 1,
        "weight": 1,
        "delay": True,
        "start": T_2021_5_26__3_55_UTC + dt.timedelta(days=7),
        "stop": T_2021_5_26__3_55_UTC + dt.timedelta(days=60),
        "skip_missing": False,
        "tzinfo": utc,
    },
)

job_reprs_utc = (
    [
        "scheduler.Job(<JobType.CYCLIC: 1>, [datetime.timedelta(seconds=3600)], <function foo at 0x",
        (
            ">, {}, 0, 0.3333333333333333, False, datetime.datetime(2021, 5, 26, 3, 54, 59, 999990"
            ", tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc)"
        ),
    ],
    [
        (
            "scheduler.Job(<JobType.HOURLY: 3>, [datetime.time(0, 5, tzinfo=datetime.timezone.utc)],"
            " <built-in function print>, {}, 0, 20, False, datetime.datetime(2021, 5, 26, 3, 55,"
            " tzinfo=datetime.timezone.utc), datetime.datetime(2021, 5, 26, 23, 55, "
            "tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)"
        )
    ],
    [
        "scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.MONDAY: 0>], <function bar at 0x",
        (
            ">, {}, 0, 1, False, datetime.datetime(2021, 5, 25, 3, 55, "
            "tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc)"
        ),
    ],
    [
        (
            "scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.WEDNESDAY: 2>, (<Weekday.TUESDAY: 1>,"
            " datetime.time(23, 45, 59, tzinfo=datetime.timezone.utc))], <built-in function print>"
            ", {'end': 'FOO\\n'}, 1, 1, True, "
            "datetime.datetime(2021, 6, 2, 3, 55, tzinfo=datetime.timezone.utc),"
            " datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc),"
            " False, datetime.timezone.utc)"
        )
    ],
)
