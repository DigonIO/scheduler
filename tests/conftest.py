import datetime as dt
import pytest


@pytest.fixture
def patch_datetime_now(monkeypatch, request):
    class DatetimePatch:
        it = iter(request.param)

        @classmethod
        def now(cls, tz=None):
            return next(cls.it)

    monkeypatch.setattr(dt, "datetime", DatetimePatch)
