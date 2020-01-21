# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

setup(
    name="twitchcancer",
    version="0.6.0",
    author="Benjamin Maisonnas",
    author_email="ben@wainei.net",
    description="Suite of tools to monitor and analyze chat cancer in Twitch chatrooms.",
    long_description=readme,
    license="GPLv3",
    keywords="twitch",
    url="https://github.com/benzhaomin/twitchcancer",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=("tests", "docs")),
    package_data={
        "twitchcancer": ['config.default.yml'],
    },
    include_package_data=True,
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "twitchcancer-expose = twitchcancer.cli.expose:main",
            "twitchcancer-monitor = twitchcancer.cli.monitor:main",
            "twitchcancer-record = twitchcancer.cli.record:main",
        ],
    },
    install_requires=[
        "autobahn==20.1.2",
        "irc==18.0.0",
        "requests==2.22.0",
        "pymongo==3.10.1",
        "PyYAML==5.3",
        "pyzmq==18.1.1",
    ],
    extras_require={
        "dev": [
            "coverage",
            "flake8",
            "ipython",
            "nose",
            "pep8-naming",
        ],
    },
)
