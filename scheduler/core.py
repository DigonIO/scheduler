"""
Implementation of a `Job` as callback function represention.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
import datetime as dt

from typing import Callable, Optional, Any

import typeguard as tg

from scheduler.job import (
    TimingTypeCyclic,
    TimingTypeDaily,
    TimingTypeWeekly,
    TimingJobUnion,
    TimingTypeOnce,
    CYCLIC_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    JobType,
    Job,
)
from scheduler.util import SchedulerError, AbstractJob, linear_weight_function

ONCE_TYPE_ERROR_MSG = (
    "Wrong input for Once! Select one of the following input types:\n" + ""
)

# NOTE new API design
# advantages are easier and understandable use,
# further you can create hourly and minutely as well as weekly jobs
# Also it is easy to note months and years by the architecture
# The disadvantage is that it is not possible to combine e.g. minute
# and cyclic timings in one job.

# Maybe rename offset to start(_at), for preparing a stop(_at)
# Change exec_at to timing, change JobExecTimer to JobTimer


class Scheduler:  # in core
    r"""
    Implementation of a `Scheduler` for callback functions.

    This implementation enables the planning of `Job`\ s depending on time
    cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

    Notes
    -----
    Due to the support of `datetime` objects, `scheduler` is able to work
    with time zones.

    Parameters
    ----------
    tzinfo : datetime.timezone
        Set the time zone of the `Scheduler`.
    max_exec : int
        Limits the number of overdue `Job`\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    weight_function : Callable[[float, Job, int, int], float]
        A function handle to compute the effective weight of a `Job` depending
        on the time it is overdue and its respective weight. Defaults to a linear
        weight function.
    jobs : set[Job]
        A collection of job instances.
    """

    def __init__(
        self,
        max_exec: int = 0,
        tzinfo: Optional[dt.timezone] = None,
        weight_function: Callable[
            [float, AbstractJob, int, int],
            float,
        ] = linear_weight_function,
        jobs: Optional[set[Job]] = None,
    ):
        self.__max_exec = max_exec
        self.__tzinfo = tzinfo
        self.__weight_function = weight_function
        self.__jobs: set[Job] = set() if jobs is None else jobs
        for job in self.__jobs:
            if job.tzinfo != self.__tzinfo:
                raise SchedulerError(TZ_ERROR_MSG)

        self.__tz_str = dt.datetime.now(tzinfo).timetz().tzname()

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to delete.
        """
        self.__jobs.remove(job)

    def delete_jobs(self) -> None:
        r"""Delete all `Job`\ s from the `Scheduler`."""
        self.__jobs = set()

    def __exec_job(self, job: Job, ref_dt: dt.datetime) -> None:
        """
        Execute a `Job` and handle it's deletion or new scheduling.

        Parameters
        ----------
        job : Job
            Instance of a `Job` to execute.
        ref_dt : datetime:datetime
            Reference time when the `Job` will be executed.

        """
        job._exec()
        if not job._has_attempts_remaining:
            self.delete_job(job)
        else:
            job._calc_next_exec(ref_dt)

    def exec_pending_jobs(self) -> int:
        r"""
        Check the `Job`\ s that are overdue and carry them out.

        The `Job`\ s are prioritized by calculating their effective weights dependant
        on the `Job`'s weight and the amount of time it is overdue.

        If there is a limit to the number of `Job`\ s that can be
        performed in one call, the effective weight is relevant.

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        # get all jobs with overtime in seconds and weight
        ref_dt = dt.datetime.now(tz=self.__tzinfo)

        effective_weight: dict[Job, float] = {}
        for job in self.__jobs:
            delta_seconds = job.timedelta(ref_dt).total_seconds()
            effective_weight[job] = -self.__weight_function(
                -delta_seconds,
                job,
                self.__max_exec,
                len(self.__jobs),
            )
        # sort the overtime jobs depending their weight * overtime
        sorted_jobs = sorted(effective_weight, key=effective_weight.get)  # type: ignore

        # execute the sorted overtime jobs and delete the ones with no attemps left
        exec_job_count = 0
        for idx, job in enumerate(sorted_jobs):
            if (self.__max_exec == 0 or idx < self.__max_exec) and effective_weight[
                job
            ] < 0:
                self.__exec_job(job, ref_dt)
                exec_job_count += 1
            else:
                break
        return exec_job_count

    def exec_all_jobs(self) -> int:
        r"""
        Execute all scheduled `Job`\ s independent of the planned execution time.

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        ref_dt = dt.datetime.now(tz=self.__tzinfo)
        n_jobs = len(self.__jobs)
        for job in self.__jobs:
            self.__exec_job(job, ref_dt)
        return n_jobs

    @property
    def jobs(self) -> set[Job]:
        r"""
        Get the set of all `Job`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled `Job`\ s.
        """
        return self.__jobs.copy()

    def __schedule(  # this function encapsulates the job and add the scheduler timezone
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]],
        max_attempts: int,
        weight: float,
        delay: bool,
        start: Optional[dt.datetime],
        stop: Optional[dt.datetime],
        skip_missing: bool,
    ) -> Job:
        job = Job(
            job_type=job_type,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
            tzinfo=self.__tzinfo,
        )
        self.__jobs.add(job)
        return job

    def cyclic(
        self,
        timing: TimingTypeCyclic,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        try:
            tg.check_type("timing", timing, TimingTypeCyclic)
        except TypeError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.CYCLIC,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def minutely(
        self,
        timing: TimingTypeDaily,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.MINUTELY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def hourly(
        self,
        timing: TimingTypeDaily,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.HOURLY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def daily(
        self,
        timing: TimingTypeDaily,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.DAILY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def weekly(
        self,
        timing: TimingTypeWeekly,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        try:
            tg.check_type("timing", timing, TimingTypeWeekly)
        except TypeError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.WEEKLY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    # TODO check for type list and throw error to user
    def once(
        self,
        timing: TimingTypeOnce,
        handle: Callable,
        params: Optional[dict[str, Any]] = None,
        weight: float = 1,
    ):
        # use the same trick to support datetime.datetime objects like in the old API
        # So JobType.ONCE is only an alias for JobType.CYCLIC
        # TODO: fix by wrapping the above functions within a switch case

        for type_option in [TimingTypeCyclic, TimingTypeDaily, dt.datetime]:
            try:
                tg.check_type("timing", timing, type_option)
            except TypeError:
                pass
            else:
                if type_option == dt.datetime:
                    return self.__schedule(
                        job_type=type_option,
                        timing=dt.timedelta(),
                        handle=handle,
                        params=params,
                        max_attempts=1,
                        weight=weight,
                        delay=False,
                        start=timing,
                        stop=None,
                        skip_missing=False,
                    )
                return self.__schedule(
                    job_type=type_option,
                    timing=timing,
                    handle=handle,
                    params=params,
                    max_attempts=1,
                    weight=weight,
                    delay=True,
                    start=None,
                    stop=None,
                    skip_missing=False,
                )

        raise SchedulerError(ONCE_TYPE_ERROR_MSG)
