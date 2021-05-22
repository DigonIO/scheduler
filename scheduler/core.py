from __future__ import annotations
from typing import Callable, Union, Tuple, Sequence
from enum import Enum, auto
import datetime as dt

from scheduler.weekday import Weekday
from scheduler.job import Job
from scheduler.oneshot import Oneshot
from scheduler.routine import Routine


class Scheduler:
    """
    A simple pythonic scheduler build on top the `datetime` standard library.
    Supporting timezones.

    Two different `Job` types are defined,
    the `Oneshot` where the callback function will be executed once
    and a `Routine` with cyclic callback function execution.
    """

    def __init__(self, tzinfo=dt.timezone.utc, max_exec: int = 0):
        self.__tzinfo = tzinfo
        self.__max_exec = max_exec

        self.__jobs = set()

    def _add_job(self, job: Job) -> None:
        """
        Add a `Job` to the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to add to the `Scheduler`.
        """
        self.__jobs.add(job)

    def _delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to delete.
        """
        self.__jobs.remove(job)

    def exec_jobs(self) -> None:
        """
        Check the `Job`\ s that are overdue and carry them out.

        If there is a limit to the number of `Job`\ s that can be
        performed in an exam, the weighting is relevant.
        """

        # get all jobs with overtime in seconds and weight
        if self.__tzinfo is None:
            dt_stamp = dt.datetime.now()
        else:
            dt_stamp = dt.datetime.now(tz=self.__tzinfo)

        overtime_jobs = {}
        for job in self.__jobs:
            delta_seconds = job.timedelta(dt_stamp).total_seconds()
            if delta_seconds < 0:
                overtime_jobs[job] = delta_seconds * job.weight

        # sort the overtime jobs depending their weight * overtime
        sorted_overtime_jobs = sorted(overtime_jobs, key=overtime_jobs.get)

        # execute the sorted overtime jobs and delete the ones with no attemps left
        for job, _ in zip(sorted_overtime_jobs, range(0, self.__max_exec)):
            job._exec()
            if not job.has_attempts:
                self._delete_job(job)

    def oneshot(
        self,
        job: Callable,
        weight: int = 1,
        t_delta: dt.timedelta = None,
        tw_stamp: Union[Weekday, dt.time, Tuple[Weekday, dt.time], None] = None,
        dt_stamp: dt.datetime = None,
        wkdy: Weekday = None,
    ) -> None:
        """
        Create a `Job` as `Oneshot` that runs at a specific timestamp.

        Parameters
        ----------
        job : Callable
            Handle to a callback function.
        weight : int
            Relativ job weight against other jobs.
        t_delta : dt.timedelta
            After creation the job will wait this duration to its execution.
        tw_stamp : Union[Weekday, dt.time, Tuple[Weekday, dt.time], None]
            Next time at this hour the job will be executed.
        dt_stamp : dt.datetime
            Combination of t_stamp and d_stamp.
        """
        job = Oneshot(
            job,
            weight=weight,
            t_delta=t_delta,
            tw_stamp=tw_stamp,
            dt_stamp=dt_stamp,
        )
        self._add_job(job)
        return job

    def routine(
        self,
        job: Callable,
        weight: int = 1,
        t_delta: dt.timedelta = None,
        tw_stamps: Union[
            Sequence[Union[Weekday, dt.time, Tuple[Weekday, dt.time]]],
            Weekday,
            dt.time,
            Tuple[Weekday, dt.time],
            None,
        ] = None,
        auto_start: Union[bool, dt.datetime] = False,
        max_attempts: int = 0,
    ):
        """
        Create a repeating `Job` as `Routine` that will be executed in a given interval.

        Parameters
        ----------
        job : Callable
            Handle to a callback function.
        weight : int
            Relativ weight against other `Job`\ s.
        t_delta : dt.timedelta
            After creation the `Routine` will wait this duration to its execution.
        tw_stamp : Union[Sequence[Union[Weekday, dt.time, Tuple[Weekday, dt.time]]], Weekday, dt.time, Tuple[Weekday, dt.time], None]
            Times with weekdays at which the job will be executed.
        auto_start : Union[bool, dt.datetime]
            Set `True` to start the `Routine`
        max_attempts : int
            Number of times the Job will be executed. 0 <=> inf
        """
        job = Routine(
            job,
            weight=weight,
            t_delta=t_delta,
            tw_stamps=tw_stamps,
            max_attempts=max_attempts,
        )
        self._add_job(job)
        if auto_start:
            if isinstance(auto_start, dt.datetime):
                job._next_exec_dt_stamp(auto_start)
            else:
                job._next_exec_dt_stamp(dt.datetime.now(self.__tzinfo))
        return job
