"""
tests for flasky components
"""
import random
import string

import pytest

from pynewood.utils import (
    get_saved_tournament_names,
    load_tournament,
    delete_tournament,
)


@pytest.fixture
def tourn_name():
    """ return a random tournament name. """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture
def tournament(client, tourn_name):
    """ Create the north 40 tournament, return loaded object. """
    delete_tournament(tourn_name)
    assert tourn_name not in get_saved_tournament_names()
    tour_type = "LimitedRound"
    url = f"/create_tournament_{tour_type}_{tourn_name}"
    data = dict(players_per_round=4, number_of_plays=2)
    client.post(url, data=data, follow_redirects=True)
    assert tourn_name in get_saved_tournament_names()
    yield load_tournament(tourn_name)
    delete_tournament(tourn_name)


class TestIndex:
    def test_base_rount(self, client):
        """ Make sure the client gets a good response. """
        rv = client.get("/")
        assert "200" in str(rv)


class TestCreateTournament:
    def test_create_new_tournament(self, tournament):
        """ Create a new tournament with a different default name. """
        assert tournament.name in get_saved_tournament_names()


class TestRunStandardTournmant:
    """ Tests for running basic tournament """

    # utility functions

    @staticmethod
    def current_df(tournament_name):
        """ return the current state of the tournament dataframe. """
        return load_tournament(tournament_name).df

    @staticmethod
    def submit_times(tournament_name, client, match_ups=1):
        """ Use the client to submit times for df """
        tournament = load_tournament(tournament_name)
        url = f"/tournament_{tournament_name}"
        # get next n matchups and iterate through them
        match_ups = tournament.get_next_matchups(match_ups)
        for match_up in match_ups:
            data = {}
            for num, name in enumerate(match_up):
                player_name = f"player{num}"
                data[player_name] = 2.0
            client.post(url, data=data, follow_redirects=True)

    # fixtures

    @pytest.fixture
    def run_tournament(self, client, tournament):
        """ start running the tournament. """
        url = f"/tournament_{tournament.name}"
        rv = client.get(url)
        assert "200" in str(rv)
        assert rv

    # tests

    def test_run_tournament_scenario_1(self, client, tournament):
        """ First scenario for running a tournament """
        name = tournament.name
        players_per_round = tournament.players_per_round
        # first make sure the df has no time values
        df = self.current_df(name)
        assert df["time"].isnull().all()
        # now submit times for first round, make sure correct number of rows
        # were updated.
        self.submit_times(name, client)
        df = self.current_df(name)
        non_null_count = (~df.loc[:, "time"].isnull()).sum()
        assert non_null_count == players_per_round
        # next run tournament to completed
        remaining_rounds = (df["time"].isnull().sum() // players_per_round) + 1
        self.submit_times(name, client, remaining_rounds)
        # make sure all times are filled out
        df = self.current_df(name)
        assert not df["time"].isnull().any()
