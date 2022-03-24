import datetime as dt

import pytest

import scheduler
from scheduler.prioritization import (
    constant_weight_prioritization,
    linear_priority_function,
    random_priority_function,
)


@pytest.mark.parametrize(
    "timedelta, executions",
    [
        [dt.timedelta(seconds=0), 1],
        [dt.timedelta(seconds=100), 0],
    ],
)
@pytest.mark.parametrize(
    "priority_function",
    [
        constant_weight_prioritization,
        linear_priority_function,
    ],
)
def test_deprecated_prioritization(timedelta, executions, priority_function):
    schedule = scheduler.Scheduler(max_exec=3, priority_function=priority_function)
    schedule.once(
        dt.datetime.now() + timedelta,
        print,
    )
    assert schedule.exec_jobs() == executions


@pytest.mark.parametrize(
    "timedelta, weight, executions",
    [
        [dt.timedelta(seconds=0), 1, 1],
        [dt.timedelta(seconds=0), 0, 0],
        [dt.timedelta(seconds=100), 1, 1],
    ],
)
def test_deprecated_rnd_prioritization(timedelta, weight, executions):
    schedule = scheduler.Scheduler(max_exec=3, priority_function=random_priority_function)
    schedule.once(dt.datetime.now() + timedelta, print, weight=weight)
    assert schedule.exec_jobs() == executions
