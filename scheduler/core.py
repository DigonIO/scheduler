"""
`Scheduler` implementation for `Job` based callback function execution.

Author: Jendrik A. Potyka
"""
from __future__ import annotations

import datetime as dt
from typing import Callable, Optional, Any

import typeguard as tg

from scheduler.job import ExecOnceTimeType, ExecTimeType, Job
from scheduler.util import SchedulerError


class Scheduler:
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
    """

    def __init__(self, tzinfo: Optional[dt.timezone] = None, max_exec: int = 0):
        self.__tzinfo = tzinfo
        self.__max_exec = max_exec

        self.__jobs: set[Job] = set()

    def _add_job(self, job: Job) -> None:
        """
        Add a `Job` to the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance that has to be added to the `Scheduler`.
        """
        self.__jobs.add(job)

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to delete.
        """
        self.__jobs.remove(job)

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

    def exec_jobs(self) -> int:
        r"""
        Check the `Job`\ s that are overdue and carry them out.

        If there is a limit to the number of `Job`\ s that can be
        performed in one call, the weighting is relevant.

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        # get all jobs with overtime in seconds and weight
        dt_stamp = dt.datetime.now(tz=self.__tzinfo)

        overtime_jobs: dict[Job, float] = {}
        for job in self.__jobs:
            delta_seconds = job.timedelta(dt_stamp).total_seconds()
            if delta_seconds <= 0:
                overtime_jobs[job] = delta_seconds * job.weight
        # sort the overtime jobs depending their weight * overtime
        sorted_overtime_jobs = sorted(overtime_jobs, key=overtime_jobs.get)

        # execute the sorted overtime jobs and delete the ones with no attemps left
        exec_job_count = 0
        for idx, job in enumerate(sorted_overtime_jobs):
            if self.__max_exec == 0 or idx < self.__max_exec:
                job._exec()
                if not job.has_attempts:
                    self.delete_job(job)
                else:
                    job._gen_next_exec_dt()
                exec_job_count += 1
            else:
                break
        return exec_job_count

    def schedule(
        self,
        handle: Callable[..., Any],
        exec_at: ExecTimeType,
        weight: float = 1,
        delay: bool = True,
        offset: Optional[dt.datetime] = None,
        max_attempts: int = 0,
    ) -> Job:
        r"""
        Create a repeating `Job` that will be executed in a given cycle.

        Parameters
        ----------
        handle : Callable[..., Any]
            Handle to a callback function.
        exec_on : Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time] | list[Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]]
            Desired execution time(s).
        weight : float
            Relative weight against other `Job`\ s.
        delay : bool
            If `False` the `Job` will executed instantly or at a given offset.
        offset : Optional[datetime.datetime]
            Set the reference `datetime.datetime` stamp the `Job` will be
            scheduled against. Default value is `datetime.datetime.now()`.
        max_attempts : int
            Number of times the `Job` will be executed. 0 <=> inf

        Returns
        -------
        Job
            Reference to the created `Job`.
        """
        job = Job(
            handle=handle,
            exec_at=exec_at,
            weight=weight,
            delay=delay,
            offset=offset,
            max_attempts=max_attempts,
            tzinfo=self.__tzinfo,
        )
        self._add_job(job)
        return job

    def once(
        self,
        handle: Callable[..., Any],
        exec_at: ExecOnceTimeType,
        weight: float = 1,
    ) -> Job:
        r"""
        Create a `Job` that runs once at a specific timestamp.

        Parameters
        ----------
        handle : Callable[..., Any]
            Handle to a callback function.
        exec_at : datetime.datetime | Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]
            Execution time.
        weight : float
            Relativ job weight against other `Job`\ s.

        Returns
        -------
        Job
            Reference to the created `Job`.
        """
        try:
            tg.check_type("exec_at", exec_at, ExecOnceTimeType)
        except TypeError as err:
            raise SchedulerError(
                'Wrong input for "once"! Select one of the following input types:\n'
                + "datetime.datetime | Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]"
            ) from err

        # hack to support dt.datetime objects as exec time
        if isinstance(exec_at, dt.datetime):
            # not testable with simple monkey patching because
            # patching of dt.datetime will corrupt the if statement
            job = Job(
                handle=handle,
                exec_at=dt.timedelta(days=1),  # dummy
                weight=weight,
                delay=False,
                offset=exec_at,
                max_attempts=1,
                tzinfo=self.__tzinfo,
            )
        else:
            job = Job(
                handle=handle,
                exec_at=exec_at,
                weight=weight,
                max_attempts=1,
                tzinfo=self.__tzinfo,
            )

        self._add_job(job)
        return job
