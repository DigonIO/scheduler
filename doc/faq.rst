Frequently Asked Questions
==========================

When to use `scheduler`?
   `scheduler` is designed to get you starting with scheduling of your |Job|\ s in no time without
   bothering you to learn a complex syntax. The API is aimed to be expressive and provides feedback
   in what you are doing.

   Integrating the python standard `datetime` library allows for simple yet powerful scheduling
   options including recurring and oneshot jobs and timezone support while being lightweight.

   Parallel execution is integrated for `asyncio <https://docs.python.org/3/library/asyncio.html>`_
   and `threading <https://docs.python.org/3/library/threading.html>`_.

When to look for other solutions?
   As the development for `scheduler` started fairly recently, the userbase is still small. While
   we are aiming at a high test coverage there might still be some undetected issues.
   With additional features still under development, there is no guarantee for
   future releases not to break current APIs.

   Currently `scheduler` is purely implemented as an in-process scheduler and does not
   standalone or with a command line interface.

   Backends for job storing have to be implemented by the user.

   When you rely on accurate timings below milliseconds.

Implementation details
----------------------

Why is there no `datetime.date` support?
   Because of the ambiguity and missing timezone support. Use `datetime.datetime` instead.

Why are you not using the `python-dateutil` library?
   We believe that the additional flexibility comes with a cost in complexity that does not
   pay off for the intended use of the `scheduler` library.
