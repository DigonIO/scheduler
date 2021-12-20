import datetime as dt
from enum import Enum, auto

import scheduler.trigger as trigger
import scheduler.util as util
from scheduler.message import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)
from scheduler.timing_type import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
    _TimingCyclicList,
    _TimingDailyList,
    _TimingWeeklyList,
)


class JobType(Enum):
    """Indicate the `JobType` of a |Job|."""

    CYCLIC = auto()
    MINUTELY = auto()
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()


JOB_TYPE_MAPPING = {
    dt.timedelta: JobType.CYCLIC,
    dt.time: JobType.DAILY,
    trigger.Monday: JobType.WEEKLY,
    trigger.Tuesday: JobType.WEEKLY,
    trigger.Wednesday: JobType.WEEKLY,
    trigger.Thursday: JobType.WEEKLY,
    trigger.Friday: JobType.WEEKLY,
    trigger.Saturday: JobType.WEEKLY,
    trigger.Sunday: JobType.WEEKLY,
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

JOB_NEXT_DAYLIKE_MAPPING = {
    JobType.MINUTELY: util.next_minutely_occurrence,
    JobType.HOURLY: util.next_hourly_occurrence,
    JobType.DAILY: util.next_daily_occurrence,
}
