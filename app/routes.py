"""
Routes for running pynewood as a flask app
"""

from pathlib import Path

import wtforms
from flask import render_template, redirect, flash, url_for, request
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange

import pynewood as pn
from pynewood.utils import get_saved_tournament_names, load_tournament
from app import app
from app.utils import _make_kwargs

TOURNAMENT = {}  # {tournament_name: tournament}
TOUR_TYPE = {}  # {tournament_name: tournament_type}
DEFAULT_PLAYER_PATH = Path(__file__).parent.parent / "default_players.txt"

DEFAULT_PLAYER_LIST = open(DEFAULT_PLAYER_PATH).read().split("\n")
here = Path(".")
tournament_path = here / "tournaments"

# map tournament name to file
SAVED_TOURNAMENTS = {x.name.split(".")[0]: str(x) for x in tournament_path.glob("*pkl")}


# ------------------ Form factories


def make_up_first_form(current_players):
    """ return a form for entering times of those who are up """

    class UpNowForm(FlaskForm):
        submit = wtforms.SubmitField(label="Submit")

    for num, player in enumerate(current_players):
        name = f"player{num}"
        num = wtforms.DecimalField(
            label=player, validators=[NumberRange(min=0), DataRequired()]
        )
        setattr(UpNowForm, name, num)

    return UpNowForm()


# --------------------- Forms


class NewTournamentForm(FlaskForm):
    """ A form for making a new tournament """

    name = wtforms.StringField(
        label="Name", default="pine", validators=[DataRequired()]
    )
    # get a list of tuples (name, name) for each tournament type
    tour_choices = [(x, x) for x in pn.get_tournament_types()]
    tour_type = wtforms.SelectField(label="type", choices=tour_choices)
    # submit button
    new_tournament = wtforms.SubmitField(label="Create New Tournament")


class LoadTournamentForm(FlaskForm):
    """ A form for creating a new tournament """

    choices = [(x, x) for x in get_saved_tournament_names()]
    name = wtforms.SelectField(label="Saved Tournaments", choices=choices)
    load_tournament = wtforms.SubmitField(label="Load Tournament")


class CreateTournament(FlaskForm):
    """ a simple form for text area input of the team """

    _default_players = "\n".join(DEFAULT_PLAYER_LIST)
    players = wtforms.TextAreaField(label="player list", default=_default_players)
    players_per_round = wtforms.IntegerField(default=4)
    number_of_plays = wtforms.IntegerField(default=2)
    _agg_options = [(x, x) for x in pn.core.AGGS]
    rank_stat = wtforms.SelectField(choices=_agg_options, default="min")
    create_tournament = wtforms.SubmitField(label="Create Tournament")


# -------------------- Routes


@app.route("/tournament_<name>", methods=["GET", "POST"])
def run_tournament(name):
    """ page for running the tournament """

    # if tournament is not loaded decide to load or create
    if name in TOURNAMENT:
        tour = TOURNAMENT[name]
    elif name in get_saved_tournament_names():
        return redirect(url_for("load_tournament", name=name))
    else:
        return redirect(url_for("index"))

    matches = tour.get_next_matchups(2)

    # create form
    form = make_up_first_form(matches[0] if len(matches) else [])

    # data is being submitted
    if request.method == "POST":
        if form.validate_on_submit():
            # set values
            if len(matches):
                for num, player in enumerate(matches[0]):
                    name = f"player{num}"
                    val = float(getattr(form, name).data)
                    tour.set_time(player, val)
                # redirect to input to clear form state
                kwargs = dict(name=name)
                tour.save(str(tournament_path / (name + ".pkl")))
                return redirect(url_for("run_tournament", **kwargs))
            else:
                flash("Tournament complete!")
        else:
            flash("All fields must be numbers greater than 0")

    # get table to display
    df = tour.get_ratings().round(decimals=3)
    car_table = df.to_html(classes="aTable")

    kwargs = dict(matches=matches, form=form, name=name, car_table=car_table)
    return render_template("run_tournament.html", **kwargs)


@app.route("/create_tournament_<tour_type>_<name>", methods=["GET", "POST"])
def create_tournament(tour_type, name):
    """ create a tournament of specified type """
    form = CreateTournament()

    if form.validate_on_submit():
        data = form.data
        # get players from form
        data["players"] = form.players.data.splitlines()
        data["name"] = name
        # cache tour type
        TOUR_TYPE[name] = tour_type
        # create tournament, stash, and save
        cls = pn.get_tournament_types()[TOUR_TYPE[name]]
        kwargs = _make_kwargs(cls, data)
        tour = cls(**kwargs)
        TOURNAMENT[name] = tour
        tour.save()

        return redirect(url_for("run_tournament", name=name))

    return render_template(
        "create_tournament.html", form=form, tour_type=tour_type, name=name
    )


@app.route("/load_tournament/<name>")
def load_tournament(name):
    """ load the tournament, head over to run_tournament """
    if name not in TOURNAMENT:
        TOURNAMENT[name] = load_tournament(name)
    return redirect(url_for("run_tournament", name=name))


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
def index():
    new_form = NewTournamentForm()
    load_form = LoadTournamentForm()

    # launch into loading new tournament
    if new_form.validate_on_submit():
        # flash(f"creating new tournament: {new_form.name.data}")
        kwargs = dict(tour_type=new_form.tour_type.data, name=new_form.name.data)
        return redirect(url_for("create_tournament", **kwargs))

    # load tournament
    if load_form.validate_on_submit():
        if load_form.load_tournament.data:
            name = load_form.name.data
            # flash(f"loading tournament: {name}")
            return redirect(url_for("load_tournament", name=name))

    return render_template("index.html", new_form=new_form, load_form=load_form)
