import datetime as dt

import pytest

from scheduler import SchedulerError
from scheduler.job import Job, JobType
from scheduler.util import Weekday

utc = dt.timezone.utc
T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
T_2021_5_26__3_55_utc = dt.datetime(2021, 5, 26, 3, 55, tzinfo=utc)
