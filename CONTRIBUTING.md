# Contributing

Contributions to scheduler are highly appreciated.

## Code of Conduct

When participating in this project, please treat other people respectfully.
Generally the guidelines pointed out in the
[Python Community Code of Conduct](https://www.python.org/psf/conduct/)
are a good standard we aim to uphold.

## Feedback and feature requests

We'd like to hear from you if you are using `scheduler`.

For suggestions and feature requests feel free to submit them to our
[issue tracker](https://gitlab.com/DigonIO/scheduler/-/issues).

## Bugs

Found a bug? Please report back to our
[issue tracker](https://gitlab.com/DigonIO/scheduler/-/issues).

If possible include:

* Operating system name and version
* python and `scheduler` version
* Steps needed to reproduce the bug

## Development Setup

Clone the `scheduler` repository with `git` and enter the directory:

```bash
git clone https://gitlab.com/DigonIO/scheduler.git
cd scheduler
```

Create and activate a virtual environment:

```bash
python -m venv venv
source ./venv/bin/activate
```

Install the project with the development requirements and install
[pre-commit](https://pre-commit.com/) for the repository:

```bash
pip install -e .
pip install -r requirements.txt
pre-commit install
```

## Running tests

Testing is done using [pytest](https://pypi.org/project/pytest/). With
[pytest-cov](https://pypi.org/project/pytest-cov/) and
[coverage](https://pypi.org/project/coverage/) a report for the test coverage can be generated:

```bash
pytest --cov=scheduler/ tests/
coverage html
```

To test the examples in the documentation run:

```bash
pytest --doctest-modules doc/pages/*/*
```

## Building the documentation

To build the documentation locally, run:

```bash
sphinx-build -b html doc/ doc/_build/html
```

We are using Sphinx with [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
formatting. Additionally the documentation is tested with `pytest`.

## Pull requests

1. Fork the repository and check out on the `development` branch.
2. Enable and install [pre-commit](https://pre-commit.com/) to ensure style-guides.
3. Utilize the the static code analysis tools
   `pylint`, `pydocstyle`, `bandit` and `mypy` on the codebase in `scheduler/` and check the
   output to avoid introduction of regressions.
4. Create a commit with a descriptive summary of your changes.
5. Create a [pull request](https://gitlab.com/DigonIO/scheduler/-/merge_requests)
   on the official repository.
