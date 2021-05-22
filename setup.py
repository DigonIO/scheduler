from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="scheduler",
    version="1.0.0",
    description="A simple pythonic scheduler build on top the datetime standard library and supporting timezones.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Fabian A. Preiss, Jendrik A. Potyka",
    author_email="devops@digon.io",
    license="GPLv3",
    packages=[
        "scheduler",
    ],
    keywords="scheduler schedule datetime date time timedelta timezone timing",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Operating System :: Unix",
        "Operating System :: POSIX",
    ],
)
