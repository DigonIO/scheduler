import datetime as dt
from collections.abc import Iterator
from typing import Optional

import pytest


@pytest.fixture
def one() -> int:
    return 1


@pytest.fixture
def two(one: int) -> tuple[int, int]:
    return one, 2


@pytest.fixture
def patch_datetime_now(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    class DatetimePatch(dt.datetime):
        _it: Iterator["DatetimePatch"] = iter(request.param)
        cached_time: Optional["DatetimePatch"] = None

        @classmethod
        def now(cls, tz: Optional[dt.tzinfo] = None) -> "DatetimePatch":
            time = next(cls._it)
            cls.cached_time = time
            return time

        @classmethod
        def last_now(cls) -> Optional["DatetimePatch"]:
            return cls.cached_time

        def __repr__(self) -> str:
            s = super().__repr__()
            return s.replace("DatetimePatch", "datetime.datetime")

    monkeypatch.setattr(dt, "datetime", DatetimePatch)
