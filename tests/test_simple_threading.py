import datetime as dt
import time
import threading

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.util import Weekday


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
    start_time = time.process_time_ns()
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()
    total_time = time.process_time_ns() - start_time
    assert total_time * 1e9 > duration * 2
