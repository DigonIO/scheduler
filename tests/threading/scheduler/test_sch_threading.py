import datetime as dt
import threading
import time

import pytest

from scheduler import Scheduler


def wrap_sleep(secs: float) -> None:
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
def test_thread_safety(duration: float) -> None:
    sch = Scheduler()
    sch.cyclic(dt.timedelta(), wrap_sleep, kwargs={"secs": duration}, skip_missing=True)
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
def test_worker_count(n_threads: int, max_exec: int, n_jobs: int, res_n_exec: list[int]) -> None:
    sch = Scheduler(n_threads=n_threads, max_exec=max_exec)

    for _ in range(n_jobs):
        sch.once(dt.timedelta(), lambda: None)

    results = []
    for _ in range(len(res_n_exec)):
        results.append(sch.exec_jobs())

    assert results == res_n_exec


@pytest.mark.parametrize(
    "job_sleep, n_threads, max_exec, n_jobs, res_n_exec",
    [
        (0.0005, 1, 0, 2, [2, 2, 2, 2]),  # simple case: no threading
        (0.0005, 2, 0, 2, [2, 2, 2, 2]),  # simple case: 2 threads, 2 slow jobs
        (0.0005, 2, 0, 4, [4, 4, 4, 4]),  # 2 threads, 4 slow jobs
        (0.0005, 4, 0, 2, [2, 2, 2, 2]),  # 4 threads, 2 slow jobs
        (0.0005, 4, 2, 3, [2, 2, 2, 2]),  # 4 threads, exec limit, 3 slow jobs
        (0.0005, 4, 4, 3, [3, 3, 3, 3]),  # 4 threads, exec limit, 3 slow jobs
    ],
)
def test_threading_slow_jobs(
    job_sleep: float,
    n_threads: int,
    max_exec: int,
    n_jobs: int,
    res_n_exec: list[int],
    recwarn: pytest.WarningsRecorder,
) -> None:
    sch = Scheduler(n_threads=n_threads, max_exec=max_exec)

    for _ in range(n_jobs):
        sch.cyclic(
            dt.timedelta(),
            wrap_sleep,
            kwargs={"secs": job_sleep},
            delay=False,
        )
    warn = recwarn.pop(DeprecationWarning)
    assert (
        str(warn.message)
        == "Using the `delay` argument is deprecated and will be removed in the next minor release."
    )

    results = []
    for _ in range(len(res_n_exec)):
        results.append(sch.exec_jobs())
    assert results == res_n_exec
