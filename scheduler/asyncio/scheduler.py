"""
Implementation of a `asyncio` compatible in-process scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

import asyncio as aio
import datetime as dt
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg

from scheduler.asyncio.job import AsyncJob
from scheduler.base.definition import JOB_TYPE_MAPPING, JobType
from scheduler.base.scheduler import BaseScheduler, select_jobs_by_tag
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)
from scheduler.error import SchedulerError
from scheduler.message import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    ONCE_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)


class AsyncScheduler(BaseScheduler):
    r"""
    Implementation of an asyncio scheduler.

    This implementation enables the planning of |AsyncJob|\ s depending on time
    cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

    Notes
    -----
    Due to the support of `datetime` objects, the |AsyncScheduler| is able to work
    with timezones.

    Parameters
    ----------
    loop : asyncio.selector_events.BaseSelectorEventLoop
        Set a AsyncIO event loop, default is the global event loop
    tzinfo : datetime.tzinfo
        Set the timezone of the |Scheduler|.
    """

    def __init__(
        self,
        *,
        loop: Optional[aio.selector_events.BaseSelectorEventLoop] = None,
        tzinfo: Optional[dt.tzinfo] = None,
    ):
        self.__loop = loop if loop else aio.get_event_loop()
        self.__tzinfo = tzinfo
        self.__tz_str = dt.datetime.now(tzinfo).tzname()

        self.__jobs: dict[AsyncJob, aio.Task] = dict()
        self.__update_jobs = aio.Event()

    async def __supervise_job(self, job: AsyncJob) -> None:
        try:
            while job.has_attempts_remaining:
                sleep_seconds: float = job.timedelta().total_seconds()
                await aio.sleep(sleep_seconds)

                await job._exec()  # pylint: disable=protected-access

                reference_dt = dt.datetime.now(tz=self.__tzinfo)
                job._calc_next_exec(reference_dt)  # pylint: disable=protected-access

        except aio.CancelledError:
            pass

        else:
            self.delete_job(job)

    @property
    def jobs(self) -> set[AsyncJob]:
        r"""
        Get the set of all `AsyncJob`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled |AsyncJob|\ s.
        """
        return set(self.__jobs.keys())

    def __schedule(
        self,
        job_type: JobType,
        timing: Union[TimingCyclic, TimingDailyUnion, TimingWeeklyUnion],
        handle: Callable[..., None],
        **kwargs,
    ) -> AsyncJob:
        """Encapsulate the `AsyncJob` and add the `AioScheduler`'s timezone."""
        if not isinstance(timing, list):
            timing_list = cast(TimingJobUnion, [timing])
        else:
            timing_list = cast(TimingJobUnion, timing)

        job = AsyncJob(
            job_type=job_type,
            timing=timing_list,
            handle=handle,
            tzinfo=self.__tzinfo,
            **kwargs,
        )

        task = self.__loop.create_task(self.__supervise_job(job))
        self.__jobs[job] = task

        return job

    def delete_job(self, job: AsyncJob) -> None:
        """
        Delete a `AsyncJob` from the `AsyncScheduler`.

        Parameters
        ----------
        job : AsyncJob
            |AsyncJob| instance to delete.

        Returns
        -------
        bool
            True if deleted
        """
        task: aio.Task = self.__jobs.pop(job)
        _: bool = task.cancel()  # has to be true, because pop should raise

    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""
        Delete a set of |AsyncJob|\ s from the |AioScheduler| by tags.

        If no tags or an empty set of tags are given defaults to the deletion
        of all |AsyncJob|\ s.

        Parameters
        ----------
        tags : Optional[set[str]]
            Set of tags to identify target |AsyncJob|\ s.
        any_tag : bool
            False: To delete a |AsyncJob| all tags have to match.
            True: To delete a |AsyncJob| at least one tag has to match.
        """
        all_jobs: set[AsyncJob] = set(self.__jobs.keys())
        jobs_to_delete: set[AsyncJob]

        if tags is None or tags == {}:
            jobs_to_delete = all_jobs
        else:
            jobs_to_delete = select_jobs_by_tag(all_jobs, tags, any_tag)

        for job in jobs_to_delete:
            self.delete_job(job)

        return len(jobs_to_delete)

    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingCyclic)
        except TypeError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.CYCLIC, timing=timing, handle=handle, **kwargs)

    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.MINUTELY, timing=timing, handle=handle, **kwargs)

    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.HOURLY, timing=timing, handle=handle, **kwargs)

    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.DAILY, timing=timing, handle=handle, **kwargs)

    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingWeeklyUnion)
        except TypeError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.WEEKLY, timing=timing, handle=handle, **kwargs)

    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> AsyncJob:
        try:
            tg.check_type("timing", timing, TimingOnceUnion)
        except TypeError as err:
            raise SchedulerError(ONCE_TYPE_ERROR_MSG) from err
        if isinstance(timing, dt.datetime):
            return self.__schedule(
                job_type=JobType.CYCLIC,
                timing=dt.timedelta(),
                handle=handle,
                args=args,
                kwargs=kwargs,
                max_attempts=1,
                tags=tags,
                delay=False,
                start=timing,
            )
        return self.__schedule(
            job_type=JOB_TYPE_MAPPING[type(timing)],
            timing=timing,
            handle=handle,
            args=args,
            kwargs=kwargs,
            max_attempts=1,
            tags=tags,
        )
