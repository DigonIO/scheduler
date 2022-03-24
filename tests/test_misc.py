import datetime as dt

import pytest
from helpers import samples, samples_utc

from scheduler.trigger import (
    Friday,
    Monday,
    Saturday,
    Sunday,
    Thursday,
    Tuesday,
    Wednesday,
    weekday,
)


def test_trigger_misc():
    for sample in samples + samples_utc:
        for day, wkday in zip(
            range(7), (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
        ):
            res = weekday(day, sample)
            assert isinstance(res, wkday)
            assert res.value == day
            assert res.time == sample
