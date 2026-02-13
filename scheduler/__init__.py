"""
A simple in-process python `scheduler` library for `datetime` objects.

Author: Jendrik Potyka, Fabian Preiss
"""

__version__ = "0.8.10"
__author__ = "Jendrik Potyka, Fabian Preiss"

from scheduler.error import SchedulerError
from scheduler.threading.scheduler import Scheduler

__all__ = ["SchedulerError", "Scheduler"]
