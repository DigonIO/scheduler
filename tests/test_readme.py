import datetime as dt
import doctest
import sys
from typing import Any

import pytest

from .helpers import T_2021_5_26__3_55


# NOTE: We cannot test for the full table, as some Jobs depend on the time of execution
#       e.g. a Job supposed to run on Weekday.MONDAY. The ordering between the Jobs scheduled
#       at 0:09:59 can be guaranteed though, as they differ on the milliseconds level.
# NOTE: Currently when updating the example in the README.md file, the changes should be applied
#       manually in this file as well.
# NOTE: The same example and doctest can be found in `doc/examples/general_job_scheduling.rst`,
#       however here the test is more granular, wheras in `doc/examples` the focus is more on
#       readability and additional comments.
@pytest.mark.parametrize(
    "patch_datetime_now",
    [[T_2021_5_26__3_55 + dt.timedelta(microseconds=x) for x in range(17)]],
    indirect=["patch_datetime_now"],
)
def test_general_readme(patch_datetime_now: Any) -> None:
    r"""
    >>> import datetime as dt
    >>> from scheduler import Scheduler
    >>> from scheduler.trigger import Monday, Tuesday

    >>> def foo():
    ...     print("foo")

    >>> schedule = Scheduler()

    >>> schedule.cyclic(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, [datetime.timedelta(seconds=600)], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.minutely(dt.time(second=15), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.MINUTELY...>, [datetime.time(0, 0, 15)], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.hourly(dt.time(minute=30, second=15), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.HOURLY...>, [datetime.time(0, 30, 15)], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.daily(dt.time(hour=16, minute=30), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.DAILY...>, [datetime.time(16, 30)], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.weekly(Monday(), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, [Monday(time=datetime.time(0, 0))], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.weekly(Monday(dt.time(hour=16, minute=30)), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, [Monday(time=datetime.time(16, 30))], <function foo at 0x...>, (), {}, 0, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.once(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, [datetime.timedelta(seconds=600)], <function foo at 0x...>, (), {}, 1, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.once(Tuesday(), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, [Tuesday(time=datetime.time(0, 0))], <function foo at 0x...>, (), {}, 1, 1, True, datetime.datetime(...), None, False, None, None)

    >>> schedule.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, [datetime.timedelta(0)], <function foo at 0x...>, (), {}, 1, 1, False, datetime.datetime(2022, 2, 15, 0, 45), None, False, None, None)


    >>> print(schedule)  # doctest:+ELLIPSIS
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=9
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    MINUTELY foo()            2021-05-26 03:55:15   0:00:14         0/inf      1
    CYCLIC   foo()            2021-05-26 04:05:00   0:09:59         0/inf      1
    ONCE     foo()            2021-05-26 04:05:00   0:09:59           0/1      1
    HOURLY   foo()            2021-05-26 04:30:15   0:35:14         0/inf      1
    DAILY    foo()            2021-05-26 16:30:00  12:34:59         0/inf      1
    WEEKLY   foo()            2021-05-31 00:00:00    4 days         0/inf      1
    WEEKLY   foo()            2021-05-31 16:30:00    5 days         0/inf      1
    ONCE     foo()            2021-06-01 00:00:00    5 days           0/1      1
    ONCE     foo()            2022-02-15 00:45:00  264 days           0/1      1
    <BLANKLINE>


    >>> import time
    >>> while True:  # doctest:+SKIP
    ...     schedule.exec_jobs()
    ...     time.sleep(1)
    """
    DP = doctest.DocTestParser()
    assert test_general_readme.__doc__
    dt_readme = DP.get_doctest(test_general_readme.__doc__, globals(), "README", None, None)
    DTR = doctest.DocTestRunner()
    if sys.version_info < (3, 13):
        assert doctest.TestResults(failed=0, attempted=16) == DTR.run(dt_readme)
    else:
        assert doctest.TestResults(failed=0, attempted=17, skipped=1) == DTR.run(dt_readme)
