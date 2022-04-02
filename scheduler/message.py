"""
Information and error messages.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

DUPLICATE_EFFECTIVE_TIME = "Times that are effectively identical are not allowed."

CYCLIC_TYPE_ERROR_MSG = "Wrong input for Cyclic! Expected input type:\n" + "datetime.timedelta"
_DAILY_TYPE_ERROR_MSG = (
    "Wrong input for {0}! Select one of the following input types:\n"
    + "datetime.time | list[datetime.time]"
)
MINUTELY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Minutely")
HOURLY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Hourly")
DAILY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Daily")
WEEKLY_TYPE_ERROR_MSG = (
    "Wrong input for Weekly! Select one of the following input types:\n"
    + "DAY | list[DAY]\n"
    + "where `DAY = Weekday`"
)

TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together."
_TZ_ERROR_MSG = TZ_ERROR_MSG[:-1] + " for {0}."

START_STOP_ERROR = "Start argument must be smaller than the stop argument."

ONCE_TYPE_ERROR_MSG = (
    "Wrong input for Once! Select one of the following input types:\n"
    + "dt.datetime | dt.timedelta | Weekday | dt.time"
)
