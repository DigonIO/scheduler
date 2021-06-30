import datetime as dt

import pytest

from scheduler.job import Job, JobType
from scheduler.util import Weekday


from helpers import T_2021_5_26__3_55, utc, foo, bar


# @pytest.mark.parametrize(
#     "job_types",
#     (JobType.CYCLIC,),
#     (JobType.MINUTELY),
#     (JobType.HOURLY),
#     (JobType.DAILY),
#     (JobType.WEEKLY),
# )
# @pytest.mark.parametrize(
#     "timing",
#     (
#         Weekday.MONDAY,
#         [Weekday.MONDAY, (Weekday.TUESDAY, dt.time(1, 2, 3))],
#         [Weekday.MONDAY, (Weekday.TUESDAY, dt.time(1, 2, 3))],
#     ),
# )
# @pytest.mark.parametrize(
#     "handle, params",
#     (
#         (foo, {}),
#         (bar, {}),
#         (bar, {"msg": "foobar"}),
#     ),
# )
# @pytest.mark.parametrize("max_attempts", (0, 1, 20))
# @pytest.mark.parametrize("start, stop, tzinfo", ())
# @pytest.mark.parametrize("skip_missing", (True, False))
# @pytest.mark.parametrize("delay", (True, False))
# @pytest.mark.parametrize("weight", (0, 1 / 3, 1))
# def test_job_repr(
#     job_type,
#     timing,
#     handle,
#     params,
#     max_attempts,
#     weight,
#     delay,
#     start,
#     stop,
#     skip_missing,
#     tzinfo,
# ):
#     pass
