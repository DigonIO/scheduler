import datetime as dt

import pytest
import asyncio
from helpers import stack_logger

import traceback


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
            st = traceback.format_stack()
            stack_logger.append(st[-2:-1])
            time = next(cls.it)
            cls.cached_time = time
            stack_logger.append(f"{time}\n\n")
            with open("./sleep_stack.log", "w") as fh:
                for stack in stack_logger:
                    fh.writelines(stack)
            return time

        @classmethod
        def last_now(cls):
            return cls.cached_time

    monkeypatch.setattr(dt, "datetime", DatetimePatch)
