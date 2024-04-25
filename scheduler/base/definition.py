"""
Basic definitions for a abstract `BaseJob` and `BaseScheduler`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import datetime as dt
from enum import Enum, auto

from scheduler.base.timingtype import (
    _TimingCyclicList,
    _TimingDailyList,
    _TimingWeeklyList,
)
from scheduler.message import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)
from scheduler.trigger import (
    Friday,
    Monday,
    Saturday,
    Sunday,
    Thursday,
    Tuesday,
    Wednesday,
)


class JobType(Enum):
    """Indicate the `JobType` of a |BaseJob|."""

    CYCLIC = auto()
    MINUTELY = auto()
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()


JOB_TYPE_MAPPING = {
    dt.timedelta: JobType.CYCLIC,
    dt.time: JobType.DAILY,
    Monday: JobType.WEEKLY,
    Tuesday: JobType.WEEKLY,
    Wednesday: JobType.WEEKLY,
    Thursday: JobType.WEEKLY,
    Friday: JobType.WEEKLY,
    Saturday: JobType.WEEKLY,
    Sunday: JobType.WEEKLY,
}

JOB_TIMING_TYPE_MAPPING = {
    JobType.CYCLIC: {
        "type": _TimingCyclicList,
        "err": CYCLIC_TYPE_ERROR_MSG,
    },
    JobType.MINUTELY: {
        "type": _TimingDailyList,
        "err": MINUTELY_TYPE_ERROR_MSG,
    },
    JobType.HOURLY: {
        "type": _TimingDailyList,
        "err": HOURLY_TYPE_ERROR_MSG,
    },
    JobType.DAILY: {
        "type": _TimingDailyList,
        "err": DAILY_TYPE_ERROR_MSG,
    },
    JobType.WEEKLY: {
        "type": _TimingWeeklyList,
        "err": WEEKLY_TYPE_ERROR_MSG,
    },
}
