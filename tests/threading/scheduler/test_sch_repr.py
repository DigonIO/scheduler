import pytest
from helpers import (
    T_2021_5_26__3_55,
    T_2021_5_26__3_55_UTC,
    job_args,
    job_args_utc,
    job_reprs,
    job_reprs_utc,
    utc,
)

from scheduler.threading.job import Job
from scheduler.threading.scheduler import Scheduler

patch_samples = [T_2021_5_26__3_55] * 7
patch_samples_utc = [T_2021_5_26__3_55_UTC] * 11

sch_repr = (
    "scheduler.Scheduler(0, None, <function linear_priority_function at 0x",
    ">, jobs={",
    "})",
)
sch_repr_utc = (
    "scheduler.Scheduler(0, datetime.timezone.utc, <function linear_priority_function at 0x",
    ">, jobs={",
    "})",
)


@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, tzinfo, j_results, s_results",
    [
        (patch_samples, job_args, None, job_reprs, sch_repr),
        (patch_samples_utc, job_args_utc, utc, job_reprs_utc, sch_repr_utc),
    ],
    indirect=["patch_datetime_now"],
)
def test_sch_repr(patch_datetime_now, job_kwargs, tzinfo, j_results, s_results):
    jobs = [Job(**kwargs) for kwargs in job_kwargs]
    sch = Scheduler(tzinfo=tzinfo, jobs=jobs)
    rep = repr(sch)
    n_j_addr = 0  # number of address strings in jobs
    for j_result in j_results:
        n_j_addr += len(j_result) - 1
        for substring in j_result:
            assert substring in rep
            rep = rep.replace(substring, "", 1)
    for substring in s_results:
        assert substring in rep
        rep = rep.replace(substring, "", 1)

    # Addr str of priority_function: 12
    # ", " seperators between jobs: (len(j_results) - 1) * 2
    assert len(rep) == 12 + n_j_addr * 12 + (len(j_results) - 1) * 2
