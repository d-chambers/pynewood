"""
Utility tests
"""
from pathlib import Path

import pytest

import pynewood
from pynewood.utils import (
    load_tournament,
    delete_tournament,
    get_saved_tournament_names,
)


name = "utiltourn"
players = ["bob", "sue", "larry", "jake", "will"]


@pytest.fixture
def tournament_util(tmpdir):
    """ simple tournament for testing utils """
    tourn = pynewood.LimitedRound(players, name=name)
    yield tourn
    delete_tournament(tourn.name)


class TestUtils:
    """ Test for basic util stuff. """

    def test_save(self, tournament_util, tmpdir):
        """ ensure the tournament can be saved. """
        path = Path(tmpdir)
        tournament_util.save(path=path)
        assert tournament_util.name in get_saved_tournament_names(path)

    def test_load(self, tournament_util, tmpdir):
        """ ensure the tournament can be saved and loaded """
        path = Path(tmpdir)
        tournament_util.save(path=path)
        loaded = load_tournament(tournament_util.name, path=path)
        assert loaded is not None
        assert type(loaded) == type(tournament_util)

    def test_bad_load(self):
        """ ensure load raises file not found error for bad tournament. """
        with pytest.raises(FileNotFoundError):
            load_tournament("this_doesnt_exist")
