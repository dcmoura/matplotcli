#!/usr/bin/env python

from setuptools import setup

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    author="Daniel C. Moura",
    author_email="daniel.c.moura@gmail.com",
    python_requires=">=2.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Utilities",
    ],
    description="MatplotCLI: create matplotlib visualizations from the command-line",
    entry_points={
        "console_scripts": [
            "plt=matplotcli:main",
        ],
    },
    install_requires=["matplotlib", "numpy"],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="visualization plots json",
    name="matplotcli",
    url="https://github.com/dcmoura/matplotcli",
    project_urls={
        "Source": "https://github.com/dcmoura/matplotcli",
    },
    version="0.1.0-3",
)
