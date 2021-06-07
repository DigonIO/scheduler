"""
A simple in-process python `scheduler` library for `datetime` objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

__version__ = "0.4.0"
__author__ = "Jendrik A. Potyka, Fabian A. Preiss"

import scheduler.job
import scheduler.util
from scheduler.core import Scheduler
from scheduler.util import SchedulerError, Weekday
