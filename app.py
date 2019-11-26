from flask import Flask
import nflgame
from flask import request
from heapq import nlargest
from flask import render_template, redirect
from controllers import *
from forms import *
from config import Config
from util import *

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/leaders", methods = ['GET', 'POST'])
def index():
    form = LeadersForm()
    if form.validate_on_submit():
        season = form.season.data
        number_results = form.numberResults.data
        wrs = api_leaders(season, number_results, 'wr')
        rbs = api_leaders(season, number_results, 'rb')
        tes = api_leaders(season, number_results, 'te')
        qbs = api_leaders(season, number_results, 'qb')
    else:
        wrs = api_leaders(2018, 10, 'wr')
        rbs = api_leaders(2018, 10, 'rb')
        tes = api_leaders(2018, 10, 'te')
        qbs = api_leaders(2018, 10, 'qb')
    return render_template('leaders.html', title='Leaders', wrs=wrs, rbs=rbs, tes=tes, qbs=qbs, form=form)

@app.route('/playerProjection', methods = ['GET', 'POST'])
def weeklyStart():
    form = PlayerProjectionForm()
    if form.validate_on_submit():
        name = form.playerName.data
        full_name = sanitize_player_name(name)

        season = form.season.data
        week = form.week.data

        if full_name not in all_valid_players() or len(full_name.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=full_name)
        else:
            stats = api_player_projection(season, week, full_name)
            return render_template('playerProjectionData.html', title='playerProjectionData', stats=stats,name=full_name, year=season, week=week)
    return render_template('playerProjection.html', title='playerProjection', form=form)

@app.route('/playerComparison', methods = ['GET', 'POST'])
def comparison():
    form = PlayerComparisonForm()
    if form.validate_on_submit():
        name_one = form.playerNameOne.data
        full_name_one = sanitize_player_name(name_one)
        name_two = form.playerNameTwo.data
        full_name_two = sanitize_player_name(name_two)

        season = form.season.data
        week = form.week.data

        if full_name_one not in all_valid_players() or len(full_name_one.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=full_name_one)
        elif full_name_two not in all_valid_players() or len(full_name_two.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=full_name_two)
        else:

            statsFirstPlayer = api_player_projection(season, week, full_name_one)
            statsSecondPlayer = api_player_projection(season, week, full_name_two)
            return render_template('playerComparisonData.html', title='playerProjectionData',
                                statsFirstPlayer=statsFirstPlayer, statsSecondPlayer=statsSecondPlayer,
                                nameOne=full_name_one, nameTwo=full_name_two, year=season, week=week)
    return render_template('playerComparison.html', title='playerProjection', form=form)

@app.route('/api/playerProjection', methods = ['GET'])
def player():

    year = request.args.get('year')
    week_number = request.args.get('week')
    player_name = request.args.get('player_name')
    player_name = player_name.split('*', 1)[0]
    player_name = player_name.split('+', 1)[0]
    player_name = player_name.split('\\', 1)[0]
    strippedPlayerName = player_name.replace("'", "")

    return api_player_projection(year, week_number, strippedPlayerName)

@app.route('/api/leaders', methods = ['GET'])
def leaders():
    year = request.args.get('year')
    number_players = request.args.get('number_players')
    position = request.args.get('position').upper()

    return api_leaders(year, number_players, position)

if __name__ == "__main__":
    app.run()
