import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_delete_all_jobs(n_jobs):
    sch = Scheduler()
    assert len(sch.jobs) == 0
    for i in range(n_jobs):
        job = sch.schedule(
            lambda: None,
            dt.timedelta(seconds=1),
        )
    assert len(sch.jobs) == n_jobs
    sch.delete_job(job)
    assert len(sch.jobs) == n_jobs - 1
    sch.delete_jobs()
    assert len(sch.jobs) == 0


@pytest.mark.parametrize(
    "n_jobs",
    [5, 10, 3],
)
def test_exec_all_jobs(n_jobs):
    sch = Scheduler()
    for _ in range(n_jobs):
        _ = sch.schedule(
            lambda: None,
            dt.timedelta(),
        )
    assert sch.exec_all_jobs() == n_jobs


TZ_SCHED_JOB_ERR_MSG = "Job internal timezone does not match scheduler timezone."


@pytest.mark.parametrize(
    "j_tz, s_tz, err_msg",
    (
        [None, None, None],
        [dt.timezone.utc, None, TZ_SCHED_JOB_ERR_MSG],
        [None, dt.timezone.utc, TZ_SCHED_JOB_ERR_MSG],
        [dt.timezone.utc, dt.timezone.utc, None],
        [dt.timezone(dt.timedelta(hours=1)), None, TZ_SCHED_JOB_ERR_MSG],
        [None, dt.timezone(dt.timedelta(hours=1)), TZ_SCHED_JOB_ERR_MSG],
        [dt.timezone.utc, dt.timezone(dt.timedelta(hours=1)), TZ_SCHED_JOB_ERR_MSG],
        [dt.timezone(dt.timedelta(hours=1)), dt.timezone.utc, TZ_SCHED_JOB_ERR_MSG],
        [dt.timezone(dt.timedelta(hours=1)), dt.timezone(dt.timedelta(hours=1)), None],
    ),
)
def test_pass_job(j_tz, s_tz, err_msg):
    job = Job(lambda: None, dt.timedelta(), tzinfo=j_tz)
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg) as execinfo:
            sch = Scheduler(jobs=[job], tzinfo=s_tz)
    else:
        sch = Scheduler(jobs=[job], tzinfo=s_tz)
