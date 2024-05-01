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

from .helpers import samples, samples_utc


def test_trigger_misc() -> None:
    for sample in samples + samples_utc:
        for day, wkday in zip(
            range(7), (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
        ):

            res = weekday(value=day, time=sample.time())
            assert isinstance(res, wkday)
            assert res.value == day
            assert res.time == sample.time()
