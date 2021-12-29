"""
Implementation of a `BaseScheduler`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from scheduler.base.job import BaseJob
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)


def select_jobs_by_tag(
    jobs: set[BaseJob],
    tags: set[str],
    any_tag: bool,
) -> set[BaseJob]:
    r"""
    Select |BaseJob|\ s by matching `tags`.

    Parameters
    ----------
    jobs : set[BaseJob]
        Unfiltered set of |BaseJob|\ s.
    tags : set[str]
        Tags to filter |BaseJob|\ s.
    any_tag : bool
        False: To match a |BaseJob| all tags have to match.
        True: To match a |BaseJob| at least one tag has to match.

    Returns
    -------
    set[BaseJob]
        Selected |BaseJob|\ s.
    """
    if any_tag:
        return {job for job in jobs if tags & job.tags}
    return {job for job in jobs if tags <= job.tags}


class BaseScheduler(ABC):  # NOTE maybe a typing Protocol class is better than an ABC class
    """
    Interface definition of an abstract scheduler.

    Author: Jendrik A. Potyka, Fabian A. Preiss
    """

    @abstractmethod
    def delete_job(self, job: BaseJob) -> None:
        """Delete a |BaseJob| from the `BaseScheduler`."""

    @abstractmethod
    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""Delete a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[BaseJob]:
        r"""Get a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @property
    @abstractmethod
    def jobs(self) -> set[BaseJob]:
        r"""Get the set of all |BaseJob|\ s."""

    @abstractmethod
    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs) -> BaseJob:
        """Schedule a cyclic |BaseJob|."""

    @abstractmethod
    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> BaseJob:
        """Schedule a minutely |BaseJob|."""

    @abstractmethod
    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> BaseJob:
        """Schedule an hourly |BaseJob|."""

    @abstractmethod
    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> BaseJob:
        """Schedule a daily |BaseJob|."""

    @abstractmethod
    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs) -> BaseJob:
        """Schedule a weekly |BaseJob|."""

    @abstractmethod
    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> BaseJob:
        """Schedule a oneshot |BaseJob|."""
