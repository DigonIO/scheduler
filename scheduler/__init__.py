"""
A simple in-process python `scheduler` library for `datetime` objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.6.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

from scheduler.core import Scheduler
from scheduler.trigger import Trigger
from scheduler.util import SchedulerError
