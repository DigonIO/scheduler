.. _examples.tags:

Tags
====

The `scheduler` library provides a tagging system for |Job| categorization. This
allows for collective selection and deletion of |Job|\ s.

Create a number of tagged |Job|\ s using the :attr:`~scheduler.job.Job.tags` attribute.
For demonstration we mix the `tags` ``spam``, ``eggs``, ``ham`` and ``sausage``, where
``spam`` is a tag of every |Job|:

.. code-block:: pycon

   >>> import datetime as dt

   >>> from scheduler import Scheduler

   >>> def foo():
   ...     print("foo")

   >>> schedule = Scheduler()

   >>> dish1 = schedule.once(dt.timedelta(), foo, tags = {"spam", "eggs"})
   >>> dish2 = schedule.once(dt.timedelta(), foo, tags = {"spam", "ham"})
   >>> dish3 = schedule.once(dt.timedelta(), foo, tags = {"spam", "ham", "eggs"})
   >>> dish4 = schedule.once(dt.timedelta(), foo, tags = {"spam", "sausage", "eggs"})

The default behaviour of |Job| selection by tags require a |Job| to contain all of the
targeted tags for a match. If the `any_tag` flag is set to ``True``, only one of the targeted
tags has to exist in the |Job| for a match.
|Scheduler| currently supports the tagging system for the functions

:py:meth:`~scheduler.core.Scheduler.get_jobs` and
:py:meth:`~scheduler.core.Scheduler.delete_jobs`.

.. note:: If an empty `set` of tags is be passed to above functions, no filter is applied
    and all |Job|\ s are selected.

Match all tags
--------------
This is the default behavior.

.. code-block:: pycon

   >>> dishes = schedule.get_jobs({"ham", "eggs"})
   >>> dishes == {dish3}
   True

   >>> dishes = schedule.get_jobs({"eggs"})
   >>> dishes == {dish1, dish3, dish4}
   True

Match any tag
-------------
With the `any_tag` flag set to ``True``, one matching tag is sufficient:

.. code-block:: pycon

   >>> dishes = schedule.get_jobs({"sausage", "ham"}, any_tag=True)
   >>> dishes == {dish2, dish3, dish4}
   True

   >>> dishes = schedule.get_jobs({"eggs"}, any_tag=True)
   >>> dishes == {dish1, dish3, dish4}
   True

.. note:: Additionally the tagging system is supported by the
    :py:meth:`~scheduler.core.Scheduler.delete_jobs` method.
