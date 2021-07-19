Parameter Forwarding
====================

It is possible to forward positional and keyword arguments to the the scheduled callback function
via the arguments `args` and `kwargs`. Positional arguments are passed by a `tuple`, keyword
arguments are passed as a `dictionary` with strings referencing the callback function's
arguments.
Both types of argument passing are available for all of the scheduling functions in |Scheduler|:

:func:`~scheduler.core.Scheduler.once`,
:func:`~scheduler.core.Scheduler.cyclic`,
:func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`,
:func:`~scheduler.core.Scheduler.daily`,
:func:`~scheduler.core.Scheduler.weekly`

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

    >>> sch = Scheduler()

    >>> sch.once(dt.timedelta(), foo, args=('foo',))  # doctest:+ELLIPSIS
    scheduler.Job(...function foo..., ('foo',)...)

    >>> n_exec = sch.exec_jobs()
    foo

Defining a function `bar` with the keyword argument `msg`, we can observe the default behaviour
when the `kwargs` dictionary is ommited. Given a `kwargs` argument as in the second example, we
observe the expected behaviour with the modified message.

.. code-block:: pycon

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> sch.once(dt.timedelta(), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...bar...)

    >>> n_exec = sch.exec_jobs()
    bar

    >>> sch.once(dt.timedelta(), bar, kwargs={"msg": "Hello World"})
    scheduler.Job(...function bar...{'msg': 'Hello World'}...)

    >>> n_exec = sch.exec_jobs()
    Hello World

It is possible to schedule functions with both, positional and keyword arguments, as demonstrated
below when specifying `args` and `kwargs` together:

.. code-block:: pycon

    >>> def foobar(foo, bar = "bar"):
    ...     print(foo, bar)

    >>> sch.once(dt.timedelta(), foobar, args=("foo",), kwargs={"bar": "123"})
    scheduler.Job(...function foobar...('foo',), {'bar': '123'}...)

    >>> n_exec = sch.exec_jobs()
    foo 123
