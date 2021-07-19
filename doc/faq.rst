Frequently Asked Questions
==========================

When to use `scheduler`?
   `scheduler` is designed to get you starting with scheduling of your |Job|\ s in no time without
   bothering you to learn a complex syntax. The API is aimed to be expressive and provides feedback
   in what you are doing.

   Integrating the python standard `datetime` library allows for simple yet powerful scheduling
   options including recurring and oneshot |Job|\ s and timezone support while being lightweight.

When to look for other solutions?
   As the development for `scheduler` started fairly recently, the userbase is still small. While
   we are aiming at a high test coverage there might still be some undetected issues.
   With additional features still under development, there is no guarantee for
   future releases not to break current APIs.

   Currently `scheduler` is purely implemented as an in-process `scheduler` and does not run standalone
   or with a command line interface.

   As of now there is neither support for asynchronous tasks nor threading. Backends for |Job|
   storing have to be implemented by the user.

   When you rely on accurate timings within a few microseconds.

Implementation details
----------------------

Why is there no `datetime.date` support?
   Because of the ambiguity and missing timezone support. Use `datetime.datetime` instead.

Why are you not using the `python-dateutil` library?
   We believe that the additional flexibility comes with a cost in complexity that does not
   pay off for the intended use of the `scheduler` library.
