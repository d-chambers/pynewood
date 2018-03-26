"""

"""

import pytest
import numpy as np

from pynewood import LimitedRound
import pandas as pd

random_state = np.random.RandomState(13)

# an array of simulated times
randon_times = random_state.rand(1000) + 4.0


@pytest.fixture
def player_list():
    """ return a list of players """
    return ('jared', 'jeff', 'topher', 'ryan', 'don', 'maria', 'miguel', 'joe')


class TestLimitedRound1:

    number_of_plays = 3
    players_at_once = 4

    @pytest.fixture
    def limited_round(self, player_list):
        """ return a limited round instance """
        return LimitedRound(player_list, players_at_once=self.players_at_once,
                            number_of_plays=self.number_of_plays)

    @pytest.fixture
    def lr_with_times(self, player_list):
        """ return a limited round instance with times filled in """
        lr = LimitedRound(player_list, players_at_once=self.players_at_once,
                          number_of_plays=self.number_of_plays)
        lr.df.loc[:, 'time'] = randon_times[:len(lr.df)]
        return lr

    @pytest.fixture
    def lr_partial_times(self, player_list):
        """ return a limited round instance some times filled in """
        lr = LimitedRound(player_list, players_at_once=self.players_at_once,
                          number_of_plays=self.number_of_plays)


        lr.df.loc[:10, 'time'] = randon_times[:11]
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
        limited_round.set_time('jeff', .121, round=2)
        selected = (df['player'] == 'jeff') & (df['round'] == 2)
        assert (df.loc[selected, 'time'] == .121).all()

        # set with no explicit round
        limited_round.set_time('jeff', .15)
        selected = (df['player'] == 'jeff') & (df['round'] == 0)
        assert (df.loc[selected, 'time'] == .15).all()

        # set last and assert 3rd raises
        limited_round.set_time('jeff', .5)

        with pytest.raises(ValueError):
            limited_round.set_time('jeff', .4)

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
        fi = tmpdir.mkdir("sub").join('saved.pkl')
        lr1.save(fi)
        lr2 = lr1.load(fi)
        # ensure the dataframes are equal, skip null
        dfs_equal = (lr1.df == lr2.df) | (lr1.df.isnull() | lr2.df.isnull())
        assert (dfs_equal).all().all()
        # ensure other attrs are equal
        assert lr1.players == lr2.players
