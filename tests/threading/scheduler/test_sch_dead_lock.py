import datetime as dt
import time

from scheduler import Scheduler
from scheduler.threading.job import Job

tags = {"to_delete"}
n_execs = {0: 2, 1: 2, 2: 2, 3: 0}


def useful():
    ...


def scheduler_in_handle(scheduler: Scheduler, counter: dict[str, int]) -> None:
    _ = str(scheduler)
    assert len(scheduler.get_jobs()) == 2
    assert len(scheduler.get_jobs(tags=tags)) == 2
    assert len(scheduler.jobs) == 2

    if counter["val"] == 2:
        rnd_job = scheduler.jobs.pop()
        scheduler.delete_job(rnd_job)
        scheduler.delete_jobs(tags=tags)
        assert len(scheduler.jobs) == 0


def test_dead_lock():
    counter = {"val": 0}

    schedule = Scheduler()
    schedule.cyclic(dt.timedelta(seconds=0.01), useful, tags=tags)
    schedule.cyclic(
        dt.timedelta(seconds=0.01),
        scheduler_in_handle,
        tags=tags,
        args=(schedule, counter),
    )

    for i in range(4):
        time.sleep(0.01)
        counter["val"] = i
        assert n_execs[i] == schedule.exec_jobs()
