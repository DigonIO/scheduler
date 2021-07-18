"""
Trigger implementations.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class Weekday:
    """Weekday object with time."""

    __value = -1
    time: dt.time

    @property
    def value(self) -> int:
        """
        Return value of the given Weekday.

        Notes
        -----
        Enumeration analogous to datetime library (0: Monday, ... 6: Sunday).

        Returns
        -------
        int
            Value
        """
        return self.__value


# NOTE: pylint too-few-public-methods does not see the time property of the dataclass
# NOTE: pylint missing-class-docstring is just silly here, given functionality and usuage of parent
# NOTE: pylint invalid-name is our simple hack to avoid lots of boilerplate and external access
class Monday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 0  # pylint: disable=invalid-name


class Tuesday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 1  # pylint: disable=invalid-name


class Wednesday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 2  # pylint: disable=invalid-name, too-few-public-methods


class Thursday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 3  # pylint: disable=invalid-name


class Friday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 4  # pylint: disable=invalid-name


class Saturday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 5  # pylint: disable=invalid-name


class Sunday(
    Weekday
):  # pylint: disable=missing-class-docstring, too-few-public-methods  # noqa: D101
    def __init__(self, time=dt.time()):
        super().__init__(time)
        self._Weekday__value = 6  # pylint: disable=invalid-name


_weekday_mapping = {
    0: Monday,
    1: Tuesday,
    2: Wednesday,
    3: Thursday,
    4: Friday,
    5: Saturday,
    6: Sunday,
}


def weekday(value: int, time=dt.time()) -> Weekday:
    """
    Return Weekday from given value with optional time.

    Notes
    -----
    Enumeration analogous to datetime library (0: Monday, ... 6: Sunday).

    Parameters
    ----------
    value : int
        Integer representation of Weekday
    time : datetime.time
        Time on the clock at the specific weekday.

    Returns
    -------
    Weekday
        Weekday object with given time.
    """
    return _weekday_mapping[value](time)
