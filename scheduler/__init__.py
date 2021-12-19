"""
A simple in-process python `scheduler` library for `datetime` objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.7.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from scheduler.error import SchedulerError
from scheduler.sched_asyncio import AioScheduler
from scheduler.sched_threading import Scheduler
