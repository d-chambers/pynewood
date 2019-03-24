"""
tests for pynewood
"""
import sys
from os.path import dirname

import pytest

from app import app

# path jiggering so pynewood is importable
up_two = dirname(dirname(__file__))

sys.path.insert(0, up_two)


@pytest.fixture(scope="session")
def client():
    """ return a client for testing. """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()
