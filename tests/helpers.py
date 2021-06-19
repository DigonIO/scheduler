import datetime as dt


utc = dt.timezone.utc
T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
T_2021_5_26__3_55_UTC = dt.datetime(2021, 5, 26, 3, 55, tzinfo=utc)

CYCLIC_TYPE_ERROR_MSG = (
    "Wrong input for Cyclic! Select one of the following input types:\n"
    + "datetime.timedelta | list[datetime.timedelta]"
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

_TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together for {0}."
TZ_ERROR_MSG = _TZ_ERROR_MSG[:-9] + "."


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
