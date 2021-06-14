import copy
import datetime as dt

import pytest

from scheduler import Scheduler


def kwargs_to_collection(collection: list, **kwargs):
    for key, value in kwargs.items():
        collection.append((key, value))


default_kwargs = {"collection": [], "a": 1, "p": "QWERTY"}


@pytest.mark.parametrize(
    "oneshot",
    [
        [True],
        [False],
    ],
)
def test_handle_params(oneshot):

    kwargs = copy.deepcopy(default_kwargs)

    sch = Scheduler()
    if oneshot:
        sch.once(kwargs_to_collection, dt.datetime.now(), params=kwargs)
    else:
        sch.schedule(
            kwargs_to_collection, dt.timedelta(seconds=5), params=kwargs, delay=False
        )

    sch.exec_jobs()

    for key, value in kwargs["collection"]:
        assert kwargs[key] == value
