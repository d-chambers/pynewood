"""
Pynewood utilities.
"""
import inspect
import wtforms
from flask_wtf import FlaskForm

import pynewood as pn

_TOURNAMENT_OPTION_FACTORIES = {}


def _make_kwargs(callable, kwargs):
    """ Determine which kwargs callable can accept and return sub-dict. """
    # if we are working with a class grab info from the init
    if hasattr(callable, "__init__"):
        callable = callable.__init__
    sig = inspect.signature(callable)
    wants_args = set(sig.parameters)
    overlap = wants_args & set(kwargs)
    return {x: kwargs[x] for x in overlap}


# register pynewood classes and return a form for their specific options

# TODO come back to this for tournament specific options
# def _tournament_options_factory(tournament_type):
#     """ Register a tournament and type. """
#     assert tournament_type in pn.Tournament.registered_tournament_types
#
#     def _wrap(func):
#         _TOURNAMENT_OPTION_FACTORIES[tournament_type] = func
#         return func
#
#     return _wrap
#
#
# @_tournament_options_factory('LimitedRound')
# def _limited_round(parent=FlaskForm):
#
#     class LimitedRoundOptions(parent):
#         players_per_round = wtforms.IntegerField(default=4)
#         _agg_options = [(x, x) for x in pn.core.AGGS]
#         rank_stat = wtforms.SelectField(choices=_agg_options)
#
#     return LimitedRoundOptions
#
#
# def get_tournament_options_form(tournament_type: str, parent=FlaskForm):
#     """
#     Return a wtform for collecting the class specific options.
#     """
#     assert tournament_type in _TOURNAMENT_OPTION_FACTORIES
#     func = _TOURNAMENT_OPTION_FACTORIES[tournament_type]
#     return func(parent)
