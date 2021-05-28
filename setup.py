from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="scheduler",
    version="0.1.0",
    description="A simple pythonic Scheduler, designed to be integrated seamlessly with the datetime standard library. Due to the support of datetime objects, scheduler is able to work with time zones. ",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Jendrik A. Potyka, Fabian A. Preiss",
    author_email="devops@digon.io, devops@digon.io",
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
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ],
)
