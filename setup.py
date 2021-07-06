from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="scheduler",
    version="0.5.0",
    description=(
        "A simple in-process python scheduler library with seamless integration of "
        "the `datetime` standard library. Time zone support and planning of `Job`s "
        "depending on time cycles, fixed times, weekdays, dates, weights, offsets "
        "and execution counts."
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Jendrik A. Potyka, Fabian A. Preiss",
    author_email="devops@digon.io",
    license="LGPLv3",
    packages=[
        "scheduler",
    ],
    keywords="scheduler schedule datetime date time timedelta timezone timing",
    install_requires=[
        "typeguard>=2.6.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    url="https://gitlab.com/DigonIO/scheduler",
    project_urls={
        "Documentation": "https://python-scheduler.readthedocs.io/en/latest/",
        "Source Code": "https://gitlab.com/DigonIO/scheduler",
        "Bug Tracker": "https://gitlab.com/DigonIO/scheduler/-/issues",
        "Changelog": "https://gitlab.com/DigonIO/scheduler/-/blob/master/CHANGELOG.md",
    },
)
