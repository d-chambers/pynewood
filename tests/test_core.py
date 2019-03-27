"""
Tests for core structures.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pynewood import LimitedRound
from pynewood.exceptions import InvalidTournamentError

random_state = np.random.RandomState(13)

# an array of simulated times
randon_times = random_state.rand(1000) + 4.0


@pytest.fixture
def player_list():
    """ return a list of players """
    return "jared", "jeff", "topher", "ryan", "don", "maria", "miguel", "joe"


@pytest.fixture
def basic_limited_round(player_list):
    """ return a limited round instance """
    return LimitedRound(player_list, name="test_limited_basic")


class TestBasics:
    """ Basic tournament tests. """

    def test_bad_tournament(self):
        """ make sure the InvalidTournamentError is raised on bad configs. """
        with pytest.raises(InvalidTournamentError):
            # it is not possible not to have one player playing him/her self
            players = ["bob", "bill", "sue"]
            LimitedRound(players=players, name="sometest", players_at_once=4)

    def test_get_item(self, basic_limited_round, player_list):
        """ Tests for get items. """
        # and int should return a df of a particular round
        df = basic_limited_round[0]
        unique_round = df["round"].unique()
        assert len(unique_round) == 1
        assert unique_round[0] == 0
        # a str should return a players df
        df = basic_limited_round[player_list[0]]
        unique_players = df["player"].unique()
        assert len(unique_players) == 1
        assert unique_players[0] == player_list[0]


class TestLimitedRound1:
    number_of_plays = 3
    players_at_once = 4

    @pytest.fixture
    def limited_round(self, player_list):
        """ return a limited round instance """
        return LimitedRound(
            player_list,
            name="limited_round_test_1",
            players_at_once=self.players_at_once,
            number_of_plays=self.number_of_plays,
        )

    @pytest.fixture
    def lr_with_times(self, player_list):
        """ return a limited round instance with times filled in """
        lr = LimitedRound(
            player_list,
            name="test_limited_with_times",
            players_at_once=self.players_at_once,
            number_of_plays=self.number_of_plays,
        )
        lr.df.loc[:, "time"] = randon_times[: len(lr.df)]
        return lr

    @pytest.fixture
    def lr_partial_times(self, player_list):
        """ return a limited round instance some times filled in """
        lr = LimitedRound(
            player_list,
            name="test_limited_partial_time",
            players_at_once=self.players_at_once,
            number_of_plays=self.number_of_plays,
        )

        lr.df.loc[:10, "time"] = randon_times[:11]
        return lr

    # tests
    def test_each_player_shows_up_n_times(self, limited_round):
        """ each player should show up number_of_plays times """
        df = limited_round.df
        # each player should show up
        assert (df.player.value_counts() == self.number_of_plays).all()

    def test_next_matchups(self, limited_round):
        """ test the next matchups are returned in a list of names """
        matches = limited_round.get_next_matchups(3)
        assert isinstance(matches, list)
        assert len(matches) == 3

    def test_set_score(self, limited_round):
        """ ensure the setting score works """
        # set with an explicit round
        df = limited_round.df
        limited_round.set_time("jeff", .121, round=2)
        selected = (df["player"] == "jeff") & (df["round"] == 2)
        assert (df.loc[selected, "time"] == .121).all()

        # set with no explicit round
        limited_round.set_time("jeff", .15)
        selected = (df["player"] == "jeff") & (df["round"] == 0)
        assert (df.loc[selected, "time"] == .15).all()

        # set last and assert 3rd raises
        limited_round.set_time("jeff", .5)

        with pytest.raises(ValueError):
            limited_round.set_time("jeff", .4)

    def test_empty_ratings(self, limited_round):
        """ ratings with no input times should return an empty list """
        ranks = limited_round.get_ratings()
        assert not len(ranks)
        assert isinstance(ranks, pd.DataFrame)

    def test_ratings(self, lr_with_times):
        """ return a ranking table """
        ranks = lr_with_times.get_ratings()
        assert len(ranks)
        assert isinstance(ranks, pd.DataFrame)

    def test_partial_ratings(self, lr_partial_times):
        """ test that partially filled out ratings still works """
        ranks = lr_partial_times.get_ratings()
        assert len(ranks)
        assert isinstance(ranks, pd.DataFrame)

    def test_save_and_load(self, limited_round, tmpdir):
        """ ensure limited_round can be saved and loaded """
        lr1 = limited_round
        directory_path = Path(tmpdir.mkdir("sub"))
        lr1.save(path=directory_path)
        lr2 = lr1.load(lr1.name, path=directory_path)
        # ensure the dataframes are equal, skip null
        dfs_equal = (lr1.df == lr2.df) | (lr1.df.isnull() | lr2.df.isnull())
        assert (dfs_equal).all().all()
        # ensure other attrs are equal
        assert lr1.players == lr2.players

    def test_undo(self, lr_with_times):
        """ tests for undoing last entry. """
        df1 = lr_with_times.df.copy()
        assert not df1.time.isnull().any()
        lr_with_times.undo(1)
        df2 = lr_with_times.df.copy()
        inds = df2.index[-4:]
        assert df2.loc[inds, "time"].isnull().all()

    def test_rounds(self, lr_with_times):
        df = lr_with_times.df.copy()
        heat = lr_with_times.heat
        assert heat == df.heat.max() + 1
        assert lr_with_times.total_heats == df.heat.max() + 1
        # now undo one, make sure heat is one less
        lr_with_times.undo()
        assert lr_with_times.heat == heat - 1
