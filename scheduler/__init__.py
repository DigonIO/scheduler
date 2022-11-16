"""
A simple in-process python `scheduler` library for `datetime` objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.8.1"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from scheduler.error import SchedulerError
from scheduler.threading.scheduler import Scheduler
