"""

"""

import pytest

from pynewood import LimitedRound


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




