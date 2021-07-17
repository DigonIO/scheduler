import datetime as dt


class Weekday:
    """Abstract class for a weekday object."""

    __value: int

    def __init__(self, time: dt.time = dt.time()):
        self.__time = time

    @property
    def value(self) -> int:
        return self.__value

    @property
    def time(self) -> dt.time:
        return self.__time


class Trigger:
    """Container for all types of triggers"""

    class Weekly:
        """
        Container of all weekday representations.

        Notes
        -----
        The weekday enumeration is based on the enumeration of
        weekdays in the `datetime` standard library.
        """

        class Monday(Weekday):
            _Weekday__value = 0

        class Tuesday(Weekday):
            _Weekday__value = 1

        class Wednesday(Weekday):
            _Weekday__value = 2

        class Thursday(Weekday):
            _Weekday__value = 3

        class Friday(Weekday):
            _Weekday__value = 4

        class Saturday(Weekday):
            _Weekday__value = 5

        class Sunday(Weekday):
            _Weekday__value = 6
