import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError

WRONG_INPUT_MSG = (
    "Wrong input! Select one of the following input types:\n"
    + "Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time] or \n"
    + "list[Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]]"
)


@pytest.mark.parametrize(
    "exec_at, exception_message",
    [
        ("3min", WRONG_INPUT_MSG),
        (dt.timedelta(seconds=5), None),
        (3.1, WRONG_INPUT_MSG),
        (1, WRONG_INPUT_MSG),
    ],
)
def test_invalid_exec_at(exec_at, exception_message):
    sch = Scheduler()
    if exception_message:
        with pytest.raises(SchedulerError, match=exception_message) as excinfo:
            sch.schedule(lambda: None, exec_at)
    else:
        sch.schedule(lambda: None, exec_at)
