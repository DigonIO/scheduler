import datetime as dt
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Optional

import scheduler.messages as messages
import scheduler.timing_types as timing_types
import scheduler.trigger as trigger
import scheduler.util as util


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
        "type": timing_types._TimingCyclicList,
        "err": messages.CYCLIC_TYPE_ERROR_MSG,
    },
    JobType.MINUTELY: {
        "type": timing_types._TimingDailyList,
        "err": messages.MINUTELY_TYPE_ERROR_MSG,
    },
    JobType.HOURLY: {
        "type": timing_types._TimingDailyList,
        "err": messages.HOURLY_TYPE_ERROR_MSG,
    },
    JobType.DAILY: {
        "type": timing_types._TimingDailyList,
        "err": messages.DAILY_TYPE_ERROR_MSG,
    },
    JobType.WEEKLY: {
        "type": timing_types._TimingWeeklyList,
        "err": messages.WEEKLY_TYPE_ERROR_MSG,
    },
}

JOB_NEXT_DAYLIKE_MAPPING = {
    JobType.MINUTELY: util.next_minutely_occurrence,
    JobType.HOURLY: util.next_hourly_occurrence,
    JobType.DAILY: util.next_daily_occurrence,
}


class BaseJob(ABC):
    """
    Abstract definition of the `Job` class.

    Notes
    -----
    Needed to provide linting and typing in the :mod:`~scheduler.util` module.
    """

    @property
    @abstractmethod
    def type(self) -> JobType:
        """Return the `JobType` of the `Job` instance."""

    @property
    @abstractmethod
    def handle(self) -> Callable[..., None]:
        """Get the callback function handle."""

    @property
    @abstractmethod
    def kwargs(self) -> dict[str, Any]:
        r"""Get the payload arguments to pass to the function handle within a `Job`."""

    @property
    @abstractmethod
    def delay(self) -> bool:
        """Return ``True`` if the first `Job` execution will wait for the next scheduled time."""

    @property
    @abstractmethod
    def start(self) -> Optional[dt.datetime]:
        """Get the timestamp at which the `JobTimer` starts."""

    @property
    @abstractmethod
    def stop(self) -> Optional[dt.datetime]:
        """Get the timestamp after which no more executions of the `Job` should be scheduled."""

    @property
    @abstractmethod
    def max_attempts(self) -> int:
        """Get the execution limit for a `Job`."""

    @property
    @abstractmethod
    def skip_missing(self) -> bool:
        """Return ``True`` if `Job` will only schedule it's newest planned execution."""

    @property
    @abstractmethod
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""Get the timezone of the `Job`'s next execution."""

    @property
    @abstractmethod
    def _tzinfo(self) -> Optional[dt.tzinfo]:
        """Get the timezone of the `Scheduler` in which the `Job` is living."""

    @property
    @abstractmethod
    def has_attempts_remaining(self) -> bool:
        """Check if a `Job` has remaining attempts."""

    @property
    @abstractmethod
    def attempts(self) -> int:
        """Get the number of executions for a `Job`."""

    @property
    @abstractmethod
    def datetime(self) -> dt.datetime:
        """Give the `datetime.datetime` object for the planed execution."""

    @abstractmethod
    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        """Get the `datetime.timedelta` until the next execution of this `Job`."""


class BaseScheduler(ABC):
    pass
