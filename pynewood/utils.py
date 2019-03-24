"""
Utils for pynewood
"""
import pickle
from pathlib import Path

import pynewood as pn
import pynewood.constants


def missing_time(df):
    """ return True if df time column has any null values in it """
    return df.time.isnull().any()


def player_list(df):
    return list(df.player)


def get_saved_tournament_names(path=None):
    """ return a list of all the saved tournaments. """
    path = Path(path or pynewood.constants.DEFAULT_SAVE_PATH)
    return sorted([x.name.replace(".pkl", "") for x in path.glob("*.pkl")])


def load_tournament(tournament_name: str, path=None):
    """ Load a tournament by its name. """
    path = Path(path or pynewood.constants.DEFAULT_SAVE_PATH)
    tournies = list(path.glob(f"{tournament_name}.pkl"))
    if tournament_name not in get_saved_tournament_names(path):
        msg = f"{tournament_name} not found in {path}"
        raise FileNotFoundError(msg)

    with tournies[0].open("rb") as fi:
        return pickle.load(fi)


def delete_tournament(tournament_name: str, path=None):
    """ Delete a tournament if it exists. """
    base = Path(path or pynewood.constants.DEFAULT_SAVE_PATH)
    path = base / f"{tournament_name}.pkl"
    if path.exists():
        path.unlink()


class TournamentOption:
    """ A descriptor for defining options tournament can accept on init. """

    def __init__(self, type=None, valid_values=None, validator=None):
        self.type = type
        self.valid_values = valid_values
        self.validator = validator

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        # do validity checks
        if self.type is not None:
            assert isinstance(value, self.type)
        if self.valid_values:
            assert value in self.valid_values
        if self.validator is not None and callable(self.validator):
            assert self.validator(value, instance=instance)
        # set attr if they pass or are not applicable
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.name)
