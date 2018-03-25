"""
Routes for running pynewood as a flask app
"""

import ast


import wtforms
from flask import render_template, redirect, flash, url_for
from flask.ext.wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange

import pynewood as pn
from app import app

TOURNAMENT = {}  # a dict for holding a tournament object (keys are names)
TOUR_TYPE = {}  # a dict storing types of tournaments for each name


def make_up_first_form(matches):
    """ return a form for entering times of those who are up """

    class UpNowForm(FlaskForm):
        submit = wtforms.SubmitField(label='Submit')

    for num, name in enumerate(matches[0]):
        num = wtforms.IntegerField(label=name,
                                   validators=[NumberRange(min=0)])
        setattr(UpNowForm, name, num)

    return UpNowForm()


# --------------------- Forms


class NewTournamentForm(FlaskForm):
    """ A form for making a new tournament """
    name = wtforms.StringField(label='Name', default='pine',
                               validators=[DataRequired()])
    # get a list of tuples (name, name) for each tournament type
    tour_choices = [(x, x) for x in pn.get_tournaments()]
    tour_type = wtforms.SelectField(label='type', choices=tour_choices)
    # submit button
    new_tournament = wtforms.SubmitField(label='Create New Tournament')


class LoadTournamentForm(FlaskForm):
    """ A form for creating a new tournament """
    choices = [('zoom zoom', 'zoom')]
    name = wtforms.SelectField(label='Saved Tournaments', choices=choices)
    load_tournament = wtforms.SubmitField(label='Load Tournament')


class CreateTournament(FlaskForm):
    """ a simple form for text area input of the team """
    players = wtforms.TextAreaField(label='player list')
    create_tournament = wtforms.SubmitField(label='Create Tournament')


# -------------------- Routes


@app.route('/tournament_<tour_name>_<players>')
def run_tournament(tour_name, players='', results=None):

    # check it tournament is in memory, it not load it.
    player_list = ast.literal_eval(players)

    if not tour_name in TOURNAMENT:
        cls = pn.get_tournaments()[TOUR_TYPE[tour_name]]
        TOURNAMENT[tour_name] = cls(players=player_list)

    tour = TOURNAMENT[tour_name]
    # get the next 3 groups
    matches = tour.get_next_matchups(3)
    form = make_up_first_form(matches)
    return render_template('run_tournamnet.html', matches=matches, form=form,
                           tour_name=tour_name, players=player_list)


@app.route('/create_tournament_<tour_type>_<tour_name>', methods=['GET', 'POST'])
def create_tournament(tour_type, tour_name):
    """ create a tournament of specified type """

    form = CreateTournament()

    if form.validate_on_submit():
        players = form.players.data.splitlines()
        kwargs = dict(players=players, tour_name=tour_name,)
        # cache tour type
        TOUR_TYPE[tour_name] = tour_type
        if len(players) < 2:
            flash('You must input at least two players!')

        else:
            return redirect(url_for('run_tournament', **kwargs))

    return render_template('create_tournament.html', form=form,
                           tour_type=tour_type, tour_name=tour_name)


@app.route('/load_tournament/<name>')
def load_tournament(name):
    return f'loading tournament: {name}'
    render_template('create_tournament.html')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    new_form = NewTournamentForm()
    load_form = LoadTournamentForm()

    # launch into loading new tournament
    if new_form.validate_on_submit():
        flash(f'creating new tournament: {new_form.name.data}')
        kwargs = dict(tour_type=new_form.tour_type.data,
                      tour_name=new_form.name.data)
        return redirect(url_for('create_tournament', **kwargs))

    if load_form.validate_on_submit():
        if load_form.load_tournament.data:
            flash(f'loading tournament: {new_form.name.data}')
            return redirect(url_for('load_tournament'))

    return render_template('index.html', new_form=new_form,
                           load_form=load_form)
