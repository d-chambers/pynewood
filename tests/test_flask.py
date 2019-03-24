"""
tests for flasky components
"""
from pathlib import Path

import pytest

from pynewood.utils import (
    get_saved_tournament_names,
    load_tournament,
    delete_tournament,
)

from app import app
from app.routes import create_tournament


class TestIndex:
    def test_base_rount(self, client):
        """ Make sure the client gets a good response. """
        rv = client.get("/")
        assert "200" in rv._status


class TestCreateTournament:
    name = "north40"

    @pytest.fixture
    def north_40_tourn(self, client):
        """ Create the north 40 tournament, return loaded object. """
        delete_tournament(self.name)
        assert self.name not in get_saved_tournament_names()
        tour_type = "LimitedRound"
        url = f"/create_tournament_{tour_type}_{self.name}"
        data = dict(players_per_round=4, number_of_plays=2)
        client.post(url, data=data, follow_redirects=True)
        assert self.name in get_saved_tournament_names()
        yield load_tournament(self.name)
        delete_tournament(self.name)

    def test_create_new_tournament(self, north_40_tourn):
        """ Create a new tournament with a different default name. """
        assert north_40_tourn.name in get_saved_tournament_names()
