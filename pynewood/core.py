"""
Core classes for pynewood
"""
import itertools
import pickle
import random
from pathlib import Path
from typing import List, Sequence, Hashable

import numpy as np
import pandas as pd

from pynewood.constants import DEFAULT_SAVE_PATH, AGGS
from pynewood.exceptions import InvalidTournamentError

# a list of aggregations to perform
from pynewood.utils import missing_time, player_list, load_tournament, TournamentOption


# --------- Tournament classes


class Tournament:
    """ Base class for a tournament model """

    # a dict for storing all subclasses of Tournament
    registered_tournament_types = {}

    def __init__(self, name):
        self.name = name

    def __init_subclass__(cls, **kwargs):
        # register subclass
        tournament_type = cls.__name__
        Tournament.registered_tournament_types[tournament_type] = cls

    def save(self, path=None):
        """ Pickle the tournament object to path or default path. """
        path = Path(path or DEFAULT_SAVE_PATH) / f"{self.name}.pkl"
        with open(path, "wb") as fi:
            pickle.dump(self, fi)

    @staticmethod
    def load(name, path=None):
        """ Loads a tournament into memory. """
        return load_tournament(name, path=path)


class LimitedRound(Tournament):
    """ Class to run each participant a certain number of times """

    players_per_round = TournamentOption(type=int, valid_values=range(1, 10))
    number_of_plays = TournamentOption(type=int, valid_values=range(1, 100))
    rank_stat = TournamentOption(type=str, valid_values=AGGS)

    _shake_ups = 100  # max number of times to shuffle players to avoid

    def __init__(
        self,
        players: Sequence[Hashable],
        name,
        players_at_once: int = 4,
        number_of_plays: int = 4,
        rank_stat="min",
    ):
        """

        Parameters
        ----------
        players
            A sequence of str ids for each player
        players_at_once
            The number of players that participate in a round simultaneously
        number_of_plays
            The number of times each player should participate
        rank_stat
            The statistic to rank players
        """
        assert isinstance(players, Sequence) and not isinstance(players, str)
        assert len(set(players)) == len(players)

        super().__init__(name)

        # store init state
        self.players_per_round = players_at_once
        self.number_of_plays = number_of_plays
        self.players = players
        self.rank_stat = rank_stat

        # dataframe to keep track of round, heat, time
        self.df = self._create_df(players, players_at_once, number_of_plays)

        # Because each player participates more than once it is possible that,
        # on an overlap round, that player is assigned to race his or her self.
        # This is uniquely to happen, so just recreate the instance until it
        # does not.
        unique = self.get_next_matchups(100)
        while any([len(x) != len(set(x)) for x in unique]):
            if self._shake_ups < 1:
                msg = (
                    f"After {self._shake_ups} tries A tournament configuration"
                    f"which does not require a player to play against him/her"
                    f"self could not be found."
                )
                raise InvalidTournamentError(msg)
            self.df = self._create_df(players, players_at_once, number_of_plays)
            self._shake_ups -= 1
            unique = self.get_next_matchups(100)

    def _create_df(self, players, players_at_once, number_of_plays) -> pd.DataFrame:
        """
        Create the dataframe which keeps track of the tournaments
        """
        # get randomized play sequence and flatten
        nested_player_order = [
            random.sample(players, len(players)) for _ in range(number_of_plays)
        ]
        player_list = tuple(itertools.chain.from_iterable(nested_player_order))

        cols = ["player", "round", "heat", "time"]
        dtypes = {"time": float, "round": int, "heat": int}
        df = pd.DataFrame(index=np.arange(len(player_list)), columns=cols)
        df.loc[:, "player"] = player_list
        df.loc[:, "round"] = np.arange(len(df)) // len(players)
        df.loc[:, "heat"] = np.arange(len(df)) // players_at_once
        df: pd.DataFrame = df.astype(dtype=dtypes)
        return df

    def __getitem__(self, item):
        # TODO this is a bad idea, remove it in favor of explicit methods
        if isinstance(item, int):
            return self.df[self.df["round"] == item]
        elif isinstance(item, str):
            return self.df[self.df["player"] == item]

    def set_time(self, player, score, round=None):
        """ set a players score for a given round """
        df = self.df
        if not round:  # try to guess round based on first with un-entered time
            ndf = df[(self.df.player == player) & (df.time.isnull())]
            if not len(ndf):
                msg = f"player {player} has no un-entered times!"
                raise ValueError(msg)
            round = ndf["round"].iloc[0]
        # set values
        entry = (df["player"] == player) & (df["round"] == round)
        self.df.loc[entry, "time"] = score

    def get_next_matchups(self, next_n: int) -> List[List[str]]:
        """ get the next n match-ups"""
        # get a dataframe with any heats missing times
        group = self.df.groupby("heat")
        df = group.filter(missing_time)
        return list(df.groupby("heat").apply(player_list)[:next_n])

    def get_ratings(self):
        """ Return a table of current ranks for each player """
        # filter df to only include rows with times defined
        valid = self.df[~self.df["time"].isnull()]
        df = valid.groupby("player")["time"].agg(AGGS)
        df.sort_values(self.rank_stat, inplace=True)
        df.insert(0, column="rank", value=range(1, len(df) + 1))
        return df.rename(columns={"size": "races"})

    def save(self, path=None):
        super().save(path)
        self.df.to_csv("backup.csv")


def get_tournament_types():
    """ return a dictionary of supported tournament names and class
    definitions """
    return Tournament.registered_tournament_types
