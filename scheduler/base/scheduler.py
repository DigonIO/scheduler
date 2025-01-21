"""Implementation of a `BaseScheduler`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import wraps
from logging import Logger, getLogger
from typing import Any, Callable, Generic, List, Optional, TypeVar

from scheduler.base.job import BaseJobType
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)

# TODO:
# import sys
# if sys.version_info < (3, 10):
#     from typing_extensions import ParamSpec
# else:
#     from typing import ParamSpec


LOGGER = getLogger("scheduler")


def select_jobs_by_tag(
    jobs: set[BaseJobType],
    tags: set[str],
    any_tag: bool,
) -> set[BaseJobType]:
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


def deprecated(fields: List[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for marking specified function arguments as deprecated.

    Parameters
    ----------
    fields : List[str]
        A list of strings representing the names of the function arguments that are deprecated.

    Examples
    --------
    .. code-block:: python

        @deprecated(["old_arg"])
        def some_function(new_arg, old_arg=None):
            pass

    Calling `some_function(new_arg=5, old_arg=3)` generates a deprecation warning for using 'old_arg'.
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def real_wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
            for f in fields:
                if f in kwargs and kwargs[f] is not None:
                    # keep it in kwargs
                    warnings.warn(
                        (
                            f"Using the `{f}` argument is deprecated and will "
                            "be removed in the next minor release."
                        ),
                        DeprecationWarning,
                        stacklevel=3,
                    )
            return func(*args, **kwargs)

        return real_wrapper

    return wrapper


T = TypeVar("T", bound=Callable[[], Any])


class BaseScheduler(
    ABC, Generic[BaseJobType, T]
):  # NOTE maybe a typing Protocol class is better than an ABC class
    """
    Interface definition of an abstract scheduler.

    Author: Jendrik A. Potyka, Fabian A. Preiss
    """

    _logger: Logger

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger if logger else LOGGER

    @abstractmethod
    def delete_job(self, job: BaseJobType) -> None:
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
    ) -> set[BaseJobType]:
        r"""Get a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def cyclic(self, timing: TimingCyclic, handle: T, **kwargs) -> BaseJobType:
        """Schedule a cyclic |BaseJob|."""

    @abstractmethod
    def minutely(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a minutely |BaseJob|."""

    @abstractmethod
    def hourly(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule an hourly |BaseJob|."""

    @abstractmethod
    def daily(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a daily |BaseJob|."""

    @abstractmethod
    def weekly(self, timing: TimingWeeklyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a weekly |BaseJob|."""

    @abstractmethod
    def once(
        self,
        timing: TimingOnceUnion,
        handle: T,
        *,
        args: Optional[tuple[Any]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        alias: Optional[str] = None,
    ) -> BaseJobType:
        """Schedule a oneshot |BaseJob|."""

    @property
    @abstractmethod
    def jobs(self) -> set[BaseJobType]:
        r"""Get the set of all |BaseJob|\ s."""
