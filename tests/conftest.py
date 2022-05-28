import datetime as dt

import pytest


@pytest.fixture
def one():
    return 1


@pytest.fixture
def two(one):
    return one, 2


@pytest.fixture
def patch_datetime_now(monkeypatch, request):
    class DatetimePatch(dt.datetime):
        it = iter(request.param)
        cached_time = None

        @classmethod
        def now(cls, tz=None):
            time = next(cls.it)
            cls.cached_time = time
            return time

        @classmethod
        def last_now(cls):
            return cls.cached_time

        def __repr__(self):
            s = super().__repr__()
            return s.replace("DatetimePatch", "datetime.datetime")

    monkeypatch.setattr(dt, "datetime", DatetimePatch)
