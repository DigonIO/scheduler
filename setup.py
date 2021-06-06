from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="scheduler",
    version="0.3.0",
    description="A simple in-process python scheduler library, designed to be integrated seamlessly with the datetime standard library. Due to the support of datetime objects, scheduler is able to work with time zones. ",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Jendrik A. Potyka, Fabian A. Preiss",
    author_email="devops@digon.io",
    license="GPLv3",
    packages=[
        "scheduler",
    ],
    keywords="scheduler schedule datetime date time timedelta timezone timing",
    install_requires=[
        "typeguard",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
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
