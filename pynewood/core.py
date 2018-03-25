"""
Core classes for pynewood
"""
import itertools
import pickle
import random
from typing import List, Sequence, Hashable

import numpy as np
import pandas as pd


class Tournament:
    """ Base class for a tournament model """
    # a dict for storing all subclasses of Tournament
    registered_tournaments = {}

    def __init_subclass__(cls, **kwargs):
        name = cls.__name__
        Tournament.registered_tournaments[name] = cls

    def save(self, path):
        """ Save the tournament object to path """
        with open(path, 'wb') as fi:
            pickle.dump(self, fi)

    def load(self, path):
        with open(path, 'rb') as fi:
            return pd.read_pickle(fi)


def missing_time(df):
    """ return True if df time column has any null values in it """
    return df.time.isnull().any()


def player_list(df):
    return list(df.player)


class LimitedRound(Tournament):
    """ Class to run each participant a certain number of times """

    def __init__(self, players: Sequence[Hashable], players_at_once: int = 4,
                 number_of_plays: int = 4):
        """

        Parameters
        ----------
        players
            A sequence of str ids for each player
        players_at_once
            The number of players that participate in a round simultaneously
        number_of_plays
            The number of times each player should participate
        """
        assert isinstance(players, Sequence) and not isinstance(players, str)

        # store init state
        self.players_at_once = players_at_once
        self.number_of_plays = number_of_plays

        # get randomized play sequence and flatten
        nested_player_order = ([random.sample(players, len(players))
                                for _ in range(number_of_plays)])
        player_list = tuple(itertools.chain.from_iterable(nested_player_order))

        # dataframe to keep track of round, heat, time
        cols = ['player', 'round', 'heat', 'time']
        df = pd.DataFrame(index=np.arange(len(player_list)), columns=cols)
        df.loc[:, 'player'] = player_list
        df.loc[:, 'round'] = np.arange(len(df)) // len(players)
        df.loc[:, 'heat'] = np.arange(len(df)) // players_at_once
        self.df = df

    def __getitem__(self, item):
        return self.rounds[item]

    def set_time(self, player, score, round=None):
        """ set a players score for a given round """
        df = self.df
        if not round:  # try to guess round based on first with un-entered time
            ndf = df[(self.df.player == player) & (df.time.isnull())]
            if not len(ndf):
                msg = f'player {player} has no un-entered times!'
                raise ValueError(msg)
            round = ndf['round'].iloc[0]
        # set values
        entry = (df['player'] == player) & (df['round'] == round)
        self.df.loc[entry, 'time'] = score

    def get_next_matchups(self, next_n: int
                          ) -> List[List[str]]:
        """ get the next n match-ups"""
        # get a dataframe with any heats missing times
        group = self.df.groupby('heat')
        df = group.filter(missing_time)
        return list(df.groupby('heat').apply(player_list)[: next_n])

    def save(self, path='.limited_save.txt'):
        self.df.to_csv(path, index=False)


def get_tournaments():
    """ return a dictionary of supported tournament names and class
    definitions """
    return Tournament.registered_tournaments
