Parameter Forwarding
====================

It is possible to forward positional and keyword arguments to the the scheduled callback function
via the arguments `args` and `kwargs`. Positional arguments are passed by a `tuple`, keyword
arguments are passed as a `dictionary` with strings referencing the callback function's
arguments.
|Scheduler| supports both types of argument passing for all of the scheduling functions

:func:`~scheduler.core.Scheduler.once`,
:func:`~scheduler.core.Scheduler.cyclic`,
:func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`,
:func:`~scheduler.core.Scheduler.daily` and
:func:`~scheduler.core.Scheduler.weekly`.

In the following example we schedule two |Job|\ s via
:func:`~scheduler.core.Scheduler.once`. The first |Job| exhibits the function's default behaviour.
Whereas the second |Job| prints the modified message defined in the `kwargs` argument.

For function with a positional argument use the `args` tuple as follows:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo(msg):
    ...     print(msg)

    >>> schedule = Scheduler()

    >>> schedule.once(dt.timedelta(), foo, args=('foo',))  # doctest:+ELLIPSIS
    scheduler.Job(...function foo..., ('foo',)...)

    >>> n_exec = schedule.exec_jobs()
    foo

Defining a function `bar` with the keyword argument `msg`, we can observe the default behaviour
when the `kwargs` dictionary is ommited. Given a `kwargs` argument as in the second example, we
observe the expected behaviour with the modified message.

.. code-block:: pycon

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> schedule.once(dt.timedelta(), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...bar...)

    >>> n_exec = schedule.exec_jobs()
    bar

    >>> schedule.once(dt.timedelta(), bar, kwargs={"msg": "Hello World"})
    scheduler.Job(...function bar...{'msg': 'Hello World'}...)

    >>> n_exec = schedule.exec_jobs()
    Hello World

It is possible to schedule functions with both, positional and keyword arguments, as demonstrated
below when specifying `args` and `kwargs` together:

.. code-block:: pycon

    >>> def foobar(foo, bar = "bar"):
    ...     print(foo, bar)

    >>> schedule.once(dt.timedelta(), foobar, args=("foo",), kwargs={"bar": "123"})
    scheduler.Job(...function foobar...('foo',), {'bar': '123'}...)

    >>> n_exec = schedule.exec_jobs()
    foo 123
