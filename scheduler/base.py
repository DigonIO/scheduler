import datetime as dt
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Optional

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


class BaseJob(ABC):
    """
    Abstract definition basic interface for a job class.

    Notes
    -----
    Needed to provide linting and typing in the :mod:`~scheduler.util` module.
    """

    @property
    @abstractmethod
    def type(self) -> JobType:
        """Return the `JobType` of the `BaseJob` instance."""

    @property
    @abstractmethod
    def handle(self) -> Callable[..., None]:
        """Get the callback function handle."""

    @property
    @abstractmethod
    def kwargs(self) -> dict[str, Any]:
        r"""Get the payload arguments to pass to the function handle within a `BaseJob`."""

    @property
    @abstractmethod
    def delay(self) -> bool:
        """Return ``True`` if the first `BaseJob` execution will wait for the next scheduled time."""

    @property
    @abstractmethod
    def start(self) -> Optional[dt.datetime]:
        """Get the timestamp at which the `JobTimer` starts."""

    @property
    @abstractmethod
    def stop(self) -> Optional[dt.datetime]:
        """Get the timestamp after which no more executions of the `BaseJob` should be scheduled."""

    @property
    @abstractmethod
    def max_attempts(self) -> int:
        """Get the execution limit for a `BaseJob`."""

    @property
    @abstractmethod
    def skip_missing(self) -> bool:
        """Return ``True`` if `BaseJob` will only schedule it's newest planned execution."""

    @property
    @abstractmethod
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""Get the timezone of the `BaseJob`'s next execution."""

    @property
    @abstractmethod
    def _tzinfo(self) -> Optional[dt.tzinfo]:
        """Get the timezone of the `Scheduler` in which the `BaseJob` is living."""

    @property
    @abstractmethod
    def has_attempts_remaining(self) -> bool:
        """Check if a `BaseJob` has remaining attempts."""

    @property
    @abstractmethod
    def attempts(self) -> int:
        """Get the number of executions for a `BaseJob`."""

    @property
    @abstractmethod
    def datetime(self) -> dt.datetime:
        """Give the `datetime.datetime` object for the planed execution."""

    @abstractmethod
    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        """Get the `datetime.timedelta` until the next execution of this `BaseJob`."""


class BaseScheduler(ABC):
    @abstractmethod
    def delete_job(self, job: BaseJob) -> None:
        """Delete a `BaseJob` from the `BaseScheduler`."""

    @abstractmethod
    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        """Delete a set of `BaseJob`\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[BaseJob]:
        """Get a set of `BaseJob`\ s from the `BaseScheduler` by tags."""

    @property
    @abstractmethod
    def jobs(self) -> set[BaseJob]:
        """Get the set of all `BaseJob`\ s."""

    @abstractmethod
    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs):
        """Schedule a cyclic `BaseJob`."""

    @abstractmethod
    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        """Schedule a minutely `BaseJob`."""

    @abstractmethod
    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        """Schedule an hourly `BaseJob`."""

    @abstractmethod
    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        """Schedule a daily `BaseJob`."""

    @abstractmethod
    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs):
        """Schedule a weekly `BaseJob`."""

    @abstractmethod
    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,  # TODO check collision with **kwargs
        tags: Optional[list[str]] = None,
    ):
        """Schedule a oneshot `BaseJob`."""
