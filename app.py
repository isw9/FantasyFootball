from flask import Flask
from flask import request
from flask_bootstrap import Bootstrap
from flask import render_template, redirect
from controllers import *
from forms import *
from config import Config
from util import *
from flask_table import Table, Col
from tables import *

application = Flask(__name__)
application.config.from_object(Config)
bootstrap = Bootstrap(application)
application_dB = dB = DataBuilder(Config.MYSQL_DATABASE_USER, Config.MYSQL_DATABASE_PASSWORD,
                     Config.MYSQL_DATABASE_DB, Config.MYSQL_DATABASE_HOST)
application_dB.db_get_minmax()


@application.route("/", methods = ['GET', 'POST'])
def home():
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
        season = 2018
    wrs_table = leaders_table(wrs)
    rbs_table = leaders_table(rbs)
    tes_table = leaders_table(tes)
    qbs_table = leaders_table(qbs)
    return render_template('leaders.html', title='Leaders', wrs=wrs, rbs=rbs, tes=tes,
                            qbs=qbs, form=form, year=season, wrs_table=wrs_table,
                            rbs_table=rbs_table, tes_table=tes_table, qbs_table=qbs_table)
@application.route("/leaders", methods = ['GET', 'POST'])
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
        season = 2018
    wrs_table = leaders_table(wrs)
    rbs_table = leaders_table(rbs)
    tes_table = leaders_table(tes)
    qbs_table = leaders_table(qbs)
#    analyze_prediction_model(wrs, rbs, tes, qbs, 5.0, 2018)
    return render_template('leaders.html', title='Leaders', wrs=wrs, rbs=rbs, tes=tes,
                            qbs=qbs, form=form, year=season, wrs_table=wrs_table,
                            rbs_table=rbs_table, tes_table=tes_table, qbs_table=qbs_table)

@application.route('/playerProjection', methods = ['GET', 'POST'])
def weeklyStart():
    s_2019 = False
    form = PlayerProjectionForm()
    if form.validate_on_submit():
        name = form.playerName.data
        full_name = sanitize_player_name(name)

        season = form.season.data
        week = form.week.data
        if full_name not in all_valid_players() or len(full_name.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=name)
        else:
            if season == 2019:
                season = 2018
                s_2019 = True
            if not player_played_in_season(full_name, season, week):
                return render_template('playerYearError.html', title='playerYearError.html', name=name, year=season)
            stats = api_player_projection(season, week, full_name, application_dB)
            items = []
            for stat in stats:
                if stat != 'name':
                    to_add = dict(stat=stat, value=stats[stat])
                    items.append(to_add)
            projection_table = PlayerProjectionTable(items)
            projection_table.border = True

            historic_stats = historic_fantasy_scores(season, week, full_name)
            historic_items = []
            for stat in historic_stats:
                to_add = dict(week=stat, score=historic_stats[stat])
                historic_items.append(to_add)
            historic_table = HistoricTable(historic_items)
            historic_table.border=True

            if season == 2018 and s_2019 is True:
                season = 2019
            return render_template('playerProjectionData.html', title='playerProjectionData',
                                    stats=stats,name=full_name, year=season, week=week, historic_stats=historic_stats,
                                    projection_table=projection_table, historic_table=historic_table)
    return render_template('playerProjection.html', title='playerProjection', form=form)

@application.route('/playerComparison', methods = ['GET', 'POST'])
def comparison():
    s_2019 = False
    form = PlayerComparisonForm()
    if form.validate_on_submit():
        name_one = form.playerNameOne.data
        full_name_one = sanitize_player_name(name_one)
        name_two = form.playerNameTwo.data
        full_name_two = sanitize_player_name(name_two)

        season = form.season.data
        week = form.week.data

        if full_name_one not in all_valid_players() or len(full_name_one.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=name_one)
        elif full_name_two not in all_valid_players() or len(full_name_two.split()) != 2:
            return render_template('playerError.html', title='playerError.html', name=name_two)
        else:
            if season == 2019:
                season = 2018
                s_2019 = True
            if not player_played_in_season(full_name_one, season, week):
                return render_template('playerYearError.html', title='playerYearError.html', name=full_name_one, year=season)
            statsFirstPlayer = api_player_projection(season, week, full_name_one, application_dB)
            items_one = []
            for stat in statsFirstPlayer:
                if stat != 'name':
                    to_add = dict(stat=stat, value=statsFirstPlayer[stat])
                    items_one.append(to_add)
            player_one_table = PlayerProjectionTable(items_one)
            player_one_table.border = True

            if not player_played_in_season(full_name_two, season, week):
                return render_template('playerYearError.html', title='playerYearError.html', name=full_name_two, year=season)
            statsSecondPlayer = api_player_projection(season, week, full_name_two, application_dB)
            items_two = []
            for stat in statsSecondPlayer:
                if stat != 'name':
                    to_add = dict(stat=stat, value=statsSecondPlayer[stat])
                    items_two.append(to_add)
            player_two_table = PlayerProjectionTable(items_two)
            player_two_table.border = True

            if season == 2018 and s_2019 is True:
                season = 2019
            return render_template('playerComparisonData.html', title='playerProjectionData',
                                statsFirstPlayer=statsFirstPlayer, statsSecondPlayer=statsSecondPlayer,
                                nameOne=full_name_one, nameTwo=full_name_two, year=season, week=week,
                                player_one_table=player_one_table, player_two_table=player_two_table)
    return render_template('playerComparison.html', title='playerProjection', form=form)

@application.route('/api/playerProjection', methods = ['GET'])
def player():

    year = request.args.get('year')
    week_number = request.args.get('week_number')
    player_name = request.args.get('player_name')
    player_name = player_name.split('*', 1)[0]
    player_name = player_name.split('+', 1)[0]
    player_name = player_name.split('\\', 1)[0]
    strippedPlayerName = player_name.replace("'", "")

    if not player_played_in_season(player_name, year, week_number):
        return render_template('playerYearError.html', title='playerYearError.html', name=name, year=season)
    return api_player_projection(int(year), int(week_number), strippedPlayerName, application_dB)

@application.route('/api/leaders', methods = ['GET'])
def leaders():
    year = request.args.get('year')
    number_players = request.args.get('number_players')
    position = request.args.get('position').upper()

    return api_leaders(int(year), int(number_players), position)


if __name__ == "__main__":
    application.run()
