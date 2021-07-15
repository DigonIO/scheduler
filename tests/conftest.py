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

        @classmethod
        def now(cls, tz=None):
            return next(cls.it)

    monkeypatch.setattr(dt, "datetime", DatetimePatch)
