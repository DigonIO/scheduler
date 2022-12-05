import pdb

import pytest

from scheduler.threading.job import Job

from ...helpers import job_args, job_args_utc, job_reprs, job_reprs_utc


@pytest.mark.parametrize(
    "job_kwargs, result",
    [(args, reprs) for args, reprs in zip(job_args, job_reprs)]
    + [(args, reprs) for args, reprs in zip(job_args_utc, job_reprs_utc)],
)
def test_job_repr(
    job_kwargs,
    result,
):
    rep = repr(Job(**job_kwargs))
    for substring in result:
        assert substring in rep
        rep = rep.replace(substring, "", 1)

    # result is broken into substring at every address. Address string is 12 long
    assert len(rep) == (len(result) - 1) * 12
