import asyncio as aio
import datetime as dt
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg

from scheduler.core import JOB_TYPE_MAPPING, ONCE_TYPE_ERROR_MSG, select_jobs_by_tag
from scheduler.job import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
    JobType,
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)
from scheduler.util import JobType

from scheduler.job_asyncio import AioJob

class AioScheduler:
    def __init__(
        self,
        *,
        loop: aio.unix_events._UnixSelectorEventLoop = None, # TODO verify typing
        tzinfo: Optional[dt.tzinfo] = None,
    ):
        self.__loop = loop if loop else aio.get_event_loop()
        self.__tzinfo = tzinfo
        self.__tz_str = dt.datetime.now(tzinfo).tzname()

        self.__jobs: dict[AioJob, aio.Task] = dict()
        self.__update_jobs= aio.Event()

    async def __supervise_job(self, job: AioJob) -> None:
        try:
            while job.has_attempts_remaining:
                sleep_seconds: float = job.timedelta().total_seconds()
                await aio.sleep(sleep_seconds)

                await job._exec()

                reference_dt = dt.datetime.now(tz=self.__tzinfo)
                job._calc_next_exec(reference_dt)

        except aio.CancelledError:
            pass # NOTE will be called if the job will be deleted by the public library API

        else:
            self.delete_job(job)

    @property
    def jobs(self) -> set[AioJob]:
        r"""
        Get the set of all `AioJob`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled |AioJob|\ s.
        """
        return set(self.__jobs.keys())

    def __schedule(
        self,
        job_type: JobType,
        timing: Union[TimingCyclic, TimingDailyUnion, TimingWeeklyUnion],
        handle: Callable[..., None],
        **kwargs,
    ) -> AioJob:
        """Encapsulate the `AioJob` and add the `AioScheduler`'s timezone."""
        if not isinstance(timing, list):
            timing_list = cast(TimingJobUnion, [timing])
        else:
            timing_list = cast(TimingJobUnion, timing)

        job = AioJob(
            job_type=job_type,
            timing=timing_list,
            handle=handle,
            tzinfo=self.__tzinfo,
            **kwargs,
        )

        task = self.__loop.create_task(self.__supervise_job(job))
        self.__jobs[job] = task

        return job

    def delete_job(self, job: AioJob) -> None:
        """
        Delete a `AioJob` from the `AioScheduler`.

        Parameters
        ----------
        job : AioJob
            |AioJob| instance to delete.

        Returns
        -------
        bool
            True if deleted
        """
        task = self.__jobs.pop(job)
        _ = task.cancel() # has to be true, because pop should raise

    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""
        Delete a set of |AioJob|\ s from the |AioScheduler| by tags.

        If no tags or an empty set of tags are given defaults to the deletion
        of all |AioJob|\ s.

        Parameters
        ----------
        tags : Optional[set[str]]
            Set of tags to identify target |AioJob|\ s.
        any_tag : bool
            False: To delete a |AioJob| all tags have to match.
            True: To delete a |AioJob| at least one tag has to match.
        """
        all_jobs: set[AoiJob] = set(self.__jobs.keys())
        jobs_to_delete: set[AoiJob]

        if tags is None or tags == {}:
            jobs_to_delete = all_jobs
        else:
            jobs_to_delete = select_jobs_by_tag(all_jobs, tags, any_tag)

        for job in jobs_to_delete:
            self.delete_job(job)

        return len(jobs_to_delete)


    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs):
        try:
            tg.check_type("timing", timing, TimingCyclic)
        except TypeError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.CYCLIC, timing=timing, handle=handle, **kwargs
        )

    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.MINUTELY, timing=timing, handle=handle, **kwargs
        )

    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.HOURLY, timing=timing, handle=handle, **kwargs
        )

    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs):
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.DAILY, timing=timing, handle=handle, **kwargs
        )

    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs):
        try:
            tg.check_type("timing", timing, TimingWeeklyUnion)
        except TypeError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.WEEKLY, timing=timing, handle=handle, **kwargs
        )

    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        weight: float = 1,
    ):
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
                weight=weight,
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
            weight=weight,
        )
