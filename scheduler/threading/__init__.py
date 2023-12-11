"""
Implementation of a `threading` compatible in-process scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from scheduler.error import SchedulerError
from scheduler.threading.scheduler import Scheduler

__all__ = ["SchedulerError", "Scheduler"]
