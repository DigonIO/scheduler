import datetime as dt
import time
import threading

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.util import Weekday
from helpers import foo


def wrap_sleep(secs: float):
    time.sleep(secs)


@pytest.mark.parametrize(
    "duration",
    (
        0.000001,
        0.0001,
        0.01,
        0.02,
    ),
)
def test_thread_safety(duration):
    sch = Scheduler()
    sch.cyclic(dt.timedelta(), wrap_sleep, params={"secs": duration}, skip_missing=True)
    thread_1 = threading.Thread(target=sch.exec_jobs)
    thread_2 = threading.Thread(target=sch.exec_jobs)
    thread_1.daemon = True
    thread_2.daemon = True
    start_time = time.perf_counter()
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()
    total_time = time.perf_counter() - start_time
    assert total_time > duration * 2


@pytest.mark.parametrize(
    "n_threads, max_exec, n_jobs, res_n_exec",
    [
        (1, 0, 2, [2]),  # no threading
        (2, 0, 10, [10]),
        (0, 0, 10, [10]),
        (3, 0, 10, [10]),
        (3, 3, 10, [3, 3, 3, 1]),
        (3, 2, 10, [2, 2, 2, 2, 2]),
    ],
)
def test_worker_count(n_threads, max_exec, n_jobs, res_n_exec):
    sch = Scheduler(n_threads=n_threads, max_exec=max_exec)

    for _ in range(n_jobs):
        sch.once(dt.timedelta(), lambda: None)

    results = []
    for _ in range(len(res_n_exec)):
        results.append(sch.exec_jobs())

    assert results == res_n_exec
