import datetime as dt
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from scheduler.base.job import BaseJob
from scheduler.timing_type import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)


class BaseScheduler(ABC):
    @abstractmethod
    def delete_job(self, job: BaseJob) -> None:
        """Delete a |BaseJob| from the `BaseScheduler`."""

    @abstractmethod
    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        """Delete a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[BaseJob]:
        """Get a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @property
    @abstractmethod
    def jobs(self) -> set[BaseJob]:
        """Get the set of all |BaseJob|\ s."""

    @abstractmethod
    def cyclic(
        self, timing: TimingCyclic, handle: Callable[..., None], **kwargs
    ) -> BaseJob:
        """Schedule a cyclic |BaseJob|."""

    @abstractmethod
    def minutely(
        self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs
    ) -> BaseJob:
        """Schedule a minutely |BaseJob|."""

    @abstractmethod
    def hourly(
        self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs
    ) -> BaseJob:
        """Schedule an hourly |BaseJob|."""

    @abstractmethod
    def daily(
        self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs
    ) -> BaseJob:
        """Schedule a daily |BaseJob|."""

    @abstractmethod
    def weekly(
        self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs
    ) -> BaseJob:
        """Schedule a weekly |BaseJob|."""

    @abstractmethod
    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,  # TODO check collision with **kwargs
        tags: Optional[list[str]] = None,
    ) -> BaseJob:
        """Schedule a oneshot |BaseJob|."""
