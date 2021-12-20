from __future__ import annotations

import asyncio as aio
import datetime as dt
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg

from scheduler.base.definition import JOB_TYPE_MAPPING, JobType
from scheduler.base.job import BaseJob
from scheduler.error import SchedulerError
from scheduler.message import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    ONCE_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)
from scheduler.timing_type import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)
from scheduler.util_job import select_jobs_by_tag


class AsyncJob(BaseJob):
    r"""
    |AsyncJob| class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingWeekly
        Desired execution time(s).
    handle : Callable[..., None]
        Handle to a callback function.
    args : tuple[Any]
        Positional argument payload for the function handle within a |AsyncJob|.
    kwargs : Optional[dict[str, Any]]
        Keyword arguments payload for the function handle within a |AsyncJob|.
    tags : Optional[set[str]]
        The tags of the |AsyncJob|.
    delay : Optional[bool]
        If ``True`` wait with the execution for the next scheduled time.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the |AsyncJob|
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a |AsyncJob| will be stopped
        and deleted.
    max_attempts : Optional[int]
        Number of times the |AsyncJob| will be executed where ``0 <=> inf``.
        A |AsyncJob| with no free attempt will be deleted.
    skip_missing : Optional[bool]
        If ``True`` a |AsyncJob| will only schedule it's newest planned
        execution and drop older ones.
    alias : Optional[str]
        Overwrites the function handle name in the string representation.
    tzinfo : Optional[datetime.tzinfo]
        Set the timezone of the |Scheduler| the |AsyncJob|
        is scheduled in.

    Returns
    -------
    AsyncJob
        Instance of a scheduled |AsyncJob|.
    """

    async def _exec(self):
        coroutine = self._BaseJob__handle(*self._BaseJob__args, **self._BaseJob__kwargs)
        await coroutine
        self._BaseJob__attempts += 1
