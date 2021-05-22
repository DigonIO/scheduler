from __future__ import annotations
from typing import Callable, Optional
from enum import Enum, auto
from abc import ABC, abstractmethod
import datetime as dt

from scheduler.exceptions import SchedulerError


class Job(ABC):
    class Type(Enum):
        ONESHOT = auto()
        ROUTINE = auto()

    def __init__(
        self,
        job_type: Job.Type,
        handle: Callable,
        weight: int,
        max_attempts: int,
    ):
        self.__type = job_type
        self.__handle = handle
        self.__weight = weight
        self.__max_attempts = max_attempts

        self.__attempts = 0
        self.__exec_dt_stamp: Optional[dt.datetime] = None

    @property
    def _next_exec_dt_stamp(self, dt_stamp: dt.datetime) -> None:
        """
        Set the `dt.datetime` stamp the`Job` execution
        will be scheduled.

        Parameters
        ----------
        dt_stamp : dt.datetime
            `dt.datetime` stamp of the next `Job` execution.

        """
        self.__exec_dt_stamp = dt_stamp

    def _exec(self) -> None:
        """Execute the callback function."""
        self.__handle()
        self.__attempts += 1

    @property
    def has_attempts(self) -> bool:
        """
        Check if a `Job` executed all its execution attempts.

        Returns
        -------
        bool
            True if the `Job` has no free execution attempts.
        """
        if self.__max_attempts == 0:
            return True
        return self.__attempts >= self.__max_attempts

    @property
    def weight(self) -> int:
        """
        Return the weight of the job instance.

        Returns
        -------
        int
            Job weight.
        """
        return self.__weight

    def timedelta(self, dt_stamp: dt.datetime) -> dt.timedelta:
        """
        Get the `timedelta` until the next execution of this `Job`.

        Returns
        -------
        timedelta
            `timedelta` to the next execution.
        """

        if self.__exec_dt_stamp is None:
            raise SchedulerError("Job execution datetime stamp was not set.")
        return self.__exec_dt_stamp - dt.datetime
