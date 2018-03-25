"""
tests for pynewood
"""
import os

from os.path import dirname, join
import sys


# path jiggering so pynewood is importable
up_two = dirname(dirname(__file__))

sys.path.insert(0, up_two)
