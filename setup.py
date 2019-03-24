#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from obsplus.version import __version__
from os.path import join, abspath, dirname, exists, isdir
from setuptools import setup
import glob

HERE = dirname(abspath(__file__))


# --- get version
with open(join(HERE, "pynewood", "version.py"), "r") as fi:
    content = fi.read().split("=")[-1].strip()
    __version__ = content.replace('"', "").replace("'", "")

# --- get readme
with open("README.rst") as readme_file:
    readme = readme_file.read()


requirements = ["numpy", "pandas", "networkx", "flask-wtf"]

test_requirements = ["pytest", "pytest-flask"]

setup_requirements = ["pytest-runner", "nbsphinx", "numpydoc"]

setup(
    name="pynewood",
    version=__version__,
    description="A pinewood derby tournament manager",
    long_description=readme,
    author="Derrick Chambers",
    author_email="djachambeador@gmail.com",
    url="https://github.com/d-chambers/pynewood",
    package_dir={"pynewood": "pynewood"},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords="racing",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
