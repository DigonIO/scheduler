import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class Weekday:
    """Weekday object with time."""

    __value = -1
    time: dt.time

    @property
    def value(self):
        return self.__value


class Monday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 0


class Tuesday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 1


class Wednesday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 2


class Thursday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 3


class Friday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 4


class Saturday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 5


class Sunday(Weekday):
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 6


_weekday_mapping = {
    0: Monday,
    1: Tuesday,
    2: Wednesday,
    3: Thursday,
    4: Friday,
    5: Saturday,
    6: Sunday,
}


def weekday(value, time=dt.time()):
    return _weekday_mapping[value](time)
