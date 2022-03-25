Frequently Asked Questions
==========================

When to use `scheduler`?
   `scheduler` is designed to get you started with scheduling of |Job|\ s in no time.
   The API is aimed to be expressive and provides feedback in what you are doing.

   Integrating the python standard `datetime` library allows for simple yet powerful scheduling
   options including recurring and oneshot jobs and timezone support while being lightweight.

   Parallel execution is integrated for `asyncio <https://docs.python.org/3/library/asyncio.html>`_
   and `threading <https://docs.python.org/3/library/threading.html>`_.

When to look for other solutions?
   As the development for `scheduler` started fairly recently, the userbase is still small. While
   we are aiming to provide high quality code there might still be some undetected issues.
   With additional features still under development, there is no guarantee for
   future releases not to break current APIs.

   Currently `scheduler` is purely implemented as an in-process scheduler and does not
   run standalone or with a command line interface.

   Backends for job storing have to be implemented by the user.

   When you rely on accurate timings for real-time applications.

Implementation details
----------------------

Why is there no monthly scheduling implementation?
   As the scheduler currently does not preserve its state after a restart, we believe
   planning of long time intervals has to be a conscious choice of the user.
   Use :py:func:`~scheduler.threading.scheduler.Scheduler.once` to schedule your job
   for a specific day and time using a `datetime.datetime` object.

Why is there no `datetime.date` support?
   Because of the ambiguity and missing timezone support. Use `datetime.datetime` instead.

Why are you not using the `python-dateutil` library?
   We believe that the additional flexibility comes with a cost in complexity that does not
   pay off for the intended use of the `scheduler` library.
