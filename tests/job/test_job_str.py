import pytest
from helpers import T_2021_5_26__3_55, T_2021_5_26__3_55_UTC, job_args, job_args_utc

from scheduler.job import Job


@pytest.mark.parametrize(
    "patch_datetime_now, job_kwargs, results",
    [
        (
            [T_2021_5_26__3_55] * 3,
            job_args,
            [
                "ONCE, foo(), at=2021-05-26 04:55:00, tz=None, in=1:00:00, #0/1, w=1.000",
                "MINUTELY, bar(..), at=2021-05-26 03:54:15, tz=None, in=-0:00:45, #0/20, w=0.000",
                "DAILY, foo(), at=2021-05-26 07:05:00, tz=None, in=3:10:00, #0/7, w=1.000",
            ],
        ),
        (
            [T_2021_5_26__3_55_UTC] * 4,
            job_args_utc,
            [
                "CYCLIC, foo(), at=2021-05-26 03:54:59, tz=UTC, in=-0:00:00, #0/inf, w=0.333",
                "HOURLY, print(?), at=2021-05-26 03:55:00, tz=UTC, in=0:00:00, #0/inf, w=20.000",
                "WEEKLY, bar(..), at=2021-05-25 03:55:00, tz=UTC, in=-1 day, #0/inf, w=1.000",
                "ONCE, print(?), at=2021-06-08 23:45:59, tz=UTC, in=13 days, #0/1, w=1.000",
            ],
        ),
    ],
    indirect=["patch_datetime_now"],
)
def test_job_str(
    patch_datetime_now,
    job_kwargs,
    results,
):
    for kwargs, result in zip(job_kwargs, results):
        assert result == str(Job(**kwargs))
