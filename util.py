from flask import Blueprint, jsonify, request
from flaskext.mysql import MySQL
from flask import Flask
from heapq import nlargest
from config import Config
import re
from util import *
from tables import *
from ML.FF_LSTM import *

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

offensive_players = set()
bad_abbreviation_set = {'TAM', 'GNB', 'NOR', 'KAN', 'NWE', 'SFO', 'STL', 'SDG'}

bad_abbreviation_dict = {
'TAM': 'TB',
'GNB': 'GB',
'NOR': 'NO',
'KAN': 'KC',
'NWE': 'NE',
'SFO': 'SF',
'STL': 'LAR',
'SDG': 'LAC'
}

abbreviation_dictionary = {'Arizona Cardinals': 'ARI',
'Atlanta Falcons': 'ATL',
'Baltimore Ravens': 'BAL',
'Buffalo Bills': 'BUF',
'Carolina Panthers': 'CAR',
'Chicago Bears': 'CHI',
'Cincinnati Bengals': 'CIN',
'Cleveland Browns': 'CLE',
'Dallas Cowboys': 'DAL',
'Denver Broncos': 'DEN',
'Detroit Lions': 'DET',
'Green Bay Packers': 'GB',
'Houston Texans': 'HOU',
'Indianapolis Colts': 'IND',
'Jacksonville Jaguars': 'JAX',
'Kansas City Chiefs': 'KC',
'San Diego Chargers':'LAC',
'Los Angeles Chargers': 'LAC',
'St. Louis Rams': 'LAR',
'Los Angeles Rams': 'LAR',
'Miami Dolphins': 'MIA',
'Minnesota Vikings': 'MIN',
'New England Patriots': 'NE',
'New Orleans Saints': 'NO',
'New York Giants': 'NYG',
'New York Jets': 'NYJ',
'Oakland Raiders': 'OAK',
'Philadelphia Eagles':'PHI',
'Pittsburgh Steelers': 'PIT',
'Seattle Seahawks': 'SEA',
'San Francisco 49ers': 'SF',
'Tampa Bay Buccaneers': 'TB',
'Tennessee Titans': 'TEN',
'Washington Redskins': 'WAS'}

def analyze_prediction_model(wrs, rbs, tes, qbs, margin, season):
    number_within_margin = 0


    # How to predict a player's next score from week X season Y to week X+1
    # need to import DataBuilder.py and FF_LSTM.py
    # Create DataBuilder:
    dB = DataBuilder(Config.MYSQL_DATABASE_USER, Config.MYSQL_DATABASE_PASSWORD,
                     Config.MYSQL_DATABASE_DB, Config.MYSQL_DATABASE_HOST)
    # # Get MinMax (necessary for normalization, do it once for a DB object)
    dB.db_get_minmax()
    # # Load model by name
    model = load_model("3by50")
    # # set wiggle %
    w_norm = 0.05
    # # Predict the week after week 4, 2018 for playerID = 666
    prediction = predict_next_week(666, 4, 2018, model, dB, w_norm)

    game_ids = []
    for wr in wrs:
        game_ids.extend(game_ids_season(wr, season))

    for rb in rbs:
        game_ids.extend(game_ids_season(rb, season))

    for qb in qbs:
        game_ids.extend(game_ids_season(qb, season))

    for te in tes:
        game_ids.extend(game_ids_season(te, season))

    total_counter = 0
    close_counter = 0
    for game_id in game_ids:
        game_metadata = week_number_and_player_id_from_game_id(game_id)
        week_number = game_metadata[1]
        player_id = game_metadata[0]

        if week_number > 1:
            actual_score = round(fantasy_points_from_game_skill_player(game_id), 1)

            predicted_score = 0.0
            try:
                prediction = predict_next_week(player_id, week_number, season, model, dB, w_norm)
                total_counter += 1
                predicted_passing_yards = prediction.iloc[0]['passingYards']
                predicted_rushing_yards = prediction.iloc[0]['rushingYards']
                predicted_receiving_yards = prediction.iloc[0]['receivingYards']
                predicted_receptions = prediction.iloc[0]['receptions']
                predicted_passing_scores = prediction.iloc[0]['passingScores']
                predicted_rushing_scores = prediction.iloc[0]['rushingScores']
                predicted_receiving_scores = prediction.iloc[0]['receivingScores']
                projected_fumbles_lost = prediction.iloc[0]['fumblesLost']
                projected_interceptions = prediction.iloc[0]['interceptionsThrown']

                predicted_score += (predicted_passing_yards * .04)
                predicted_score += (predicted_rushing_yards * .1)
                predicted_score += (predicted_receiving_yards * .1)
                predicted_score += (predicted_receptions * 1)
                predicted_score += (predicted_rushing_scores * 6)
                predicted_score += (predicted_passing_scores * 4)
                predicted_score += (predicted_receiving_scores * 6)
                predicted_score -= (projected_fumbles_lost * 2)
                predicted_score -= (projected_interceptions * 2)

                projected_score_final = round(predicted_score, 1)

                print('actual')
                print(actual_score)
                print('predicted')
                print(projected_score_final)

                if abs(projected_score_final - actual_score) <= 10.0:
                    close_counter += 1
            except ValueError:
                print("Projection could not be computed")


    print('total counter')
    print(total_counter)
    print('close counter')
    print(close_counter)

def game_ids_season(player_name, season):
    player_id = player_id_from_name(player_name)

    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT gameID FROM game WHERE playerID = (\'{}\') AND season = {};".format(player_id, season)
    cursor.execute(statement)
    rows = cursor.fetchall()

    to_return = []
    for row in rows:
        to_return.append(row[0])

    cursor.close()
    conn.commit()
    conn.close()
    return to_return

def leaders_table(stats):
    items = []
    for stat in stats:
        if stat != 'name':
            to_add = dict(name=stat, score=stats[stat])
            items.append(to_add)
    table = LeaderTable(items)
    table.border = True
    return table

def massage_prediction(projection, pos):
    if pos == 'QB':
        projection['passing yards'] += 150
    if pos == 'RB':
        projection['rushing yards'] += 60
        projection['receiving yards'] += 20
    if pos == 'WR':
        projection['receiving yards'] += 50
        projection['receptions'] += 3.5
    if pos == 'TE':
        projection['receiving yards'] += 40
        projection['receptions'] += 2.5
    return projection

def historic_fantasy_scores(season, week, player_name):
    player_id = player_id_from_name(player_name)

    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT gameID FROM game WHERE playerID = (\'{}\') AND season = {} AND weekNumber < {};".format(player_id, season, week)
    cursor.execute(statement)
    rows = cursor.fetchall()
    game_ids = set()

    for row in rows:
        game_ids.add(row[0])

    game_scores = dict()

    for game_id in game_ids:
        week_number = week_number_from_game_id(game_id)
        fantasy_score = round(fantasy_points_from_game_skill_player(game_id), 1)
        game_scores[week_number] = fantasy_score

    return_dictionary = dict()
    for week in sorted(game_scores.keys()):
        return_dictionary[week] = game_scores[week]


    cursor.close()
    conn.commit()
    conn.close()
    return return_dictionary

def week_number_from_game_id(game_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT weekNumber FROM game WHERE gameId = (\'{}\');".format(game_id)

    cursor.execute(statement)
    row = cursor.fetchone()
    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return 0
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return row[0]

def iter_row(cursor, size=100):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row
def fantasy_points_from_projection(projection):
    predicted_score = 0.0

    predicted_score += (projection['passing yards'] * .04)
    predicted_score += (projection['rushing yards'] * .1)
    predicted_score += (projection['receiving yards'] * .1)
    predicted_score += (projection['receptions'] * 1)
    predicted_score += (projection['passing touchdowns'] * 6)
    predicted_score += (projection['rushing touchdowns'] * 4)
    predicted_score += (projection['receiving touchdowns'] * 6)
    predicted_score -= (projection['fumbles'] * 2)
    predicted_score -= (projection['interceptions'] * 2)

    return round(predicted_score, 1)
def fantasy_points_from_game_stats(game):

    passing_yards = game[1]
    rusing_yards = game[2]
    receiving_yards = game[3]
    receptions = game[4]
    rushing_scores = game[7]
    passing_scores = game[8]
    receiving_scores = game[9]
    fumbles_lost = game[10]
    interceptions_thrown = game[11]
    special_teams_scores = game[12]

    fantasy_points = 0.0

    fantasy_points += (passing_yards * .04)
    fantasy_points += (rusing_yards * .1)
    fantasy_points += (receiving_yards * .1)
    fantasy_points += (receptions * 1)
    fantasy_points += (rushing_scores * 6)
    fantasy_points += (passing_scores * 4)
    fantasy_points += (receiving_scores * 6)
    fantasy_points -= (fumbles_lost * 2)
    fantasy_points -= (interceptions_thrown * 2)
    fantasy_points += (special_teams_scores * 6)

    return fantasy_points

def week_number_and_player_id_from_game_id(game_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT playerID, weekNumber FROM game WHERE gameID = (\'{}\');".format(game_id)

    cursor.execute(statement)
    row = cursor.fetchone()
    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return [0, 0]
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return [row[0], row[1]]

def player_name_from_player_id(player_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT playerName FROM player WHERE playerID = (\'{}\');".format(player_id)

    cursor.execute(statement)
    row = cursor.fetchone()
    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return 0
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return row[0]

def opponent_id_for_game(abbreviation, year, opponentPosition):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT teamID FROM team WHERE abbreviation = \'{}\' AND position = \'{}\' AND season = {};".format(abbreviation, opponentPosition, year)

    cursor.execute(statement)
    row = cursor.fetchone()
    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return 0
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return row[0]

def add_team_stats_for_year(filename, year, position):
    try:
        input_file = open(filename, 'r')
        for line in input_file:
            teamDict = {}
            split_stats = line.split(',')
            try:
                team_rank = int(split_stats[0])
                if 0 <= team_rank and team_rank <= 32:

                    teamDict['rushing_yards'] = int(split_stats[18])
                    teamDict['passing_yards'] = int(split_stats[12])
                    teamDict['passing_scores'] = int(split_stats[13])
                    teamDict['rushing_scores'] = int(split_stats[19])
                    teamDict['fumbles'] = int(split_stats[8])
                    teamDict['interceptions'] = int(split_stats[14])
                    full_name = split_stats[1]
                    abbreviation = abbreviation_dictionary[full_name]
                    teamDict['abbreviation'] = abbreviation

                    add_team_stats_to_database(teamDict, year, position)
            except ValueError:
                pass
        input_file.close()
    except FileNotFoundError:
        print("please enter a valid team data file")

def fantasy_points_from_game_stats(game):

    passing_yards = game[1]
    rusing_yards = game[2]
    receiving_yards = game[3]
    receptions = game[4]
    rushing_scores = game[7]
    passing_scores = game[8]
    receiving_scores = game[9]
    fumbles_lost = game[10]
    interceptions_thrown = game[11]
    special_teams_scores = game[12]

    fantasy_points = 0.0

    fantasy_points += (passing_yards * .04)
    fantasy_points += (rusing_yards * .1)
    fantasy_points += (receiving_yards * .1)
    fantasy_points += (receptions * 1)
    fantasy_points += (rushing_scores * 6)
    fantasy_points += (passing_scores * 4)
    fantasy_points += (receiving_scores * 6)
    fantasy_points -= (fumbles_lost * 2)
    fantasy_points -= (interceptions_thrown * 2)
    fantasy_points += (special_teams_scores * 6)

    return fantasy_points

def fantasy_points_from_game_skill_player(gameID):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT * FROM game WHERE gameID = \'{}\';".format(gameID)
    cursor.execute(statement)

    row = cursor.fetchone()

    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return -100
    else:
        cursor.close()
        conn.commit()
        conn.close()
        passing_yards = row[1]
        rusing_yards = row[2]
        receiving_yards = row[3]
        receptions = row[4]
        rushing_scores = row[7]
        passing_scores = row[8]
        receiving_scores = row[9]
        fumbles_lost = row[10]
        interceptions_thrown = row[11]
        special_teams_scores = row[12]

        fantasy_points = 0.0

        fantasy_points += (passing_yards * .04)
        fantasy_points += (rusing_yards * .1)
        fantasy_points += (receiving_yards * .1)
        fantasy_points += (receptions * 1)
        fantasy_points += (rushing_scores * 6)
        fantasy_points += (passing_scores * 4)
        fantasy_points += (receiving_scores * 6)
        fantasy_points -= (fumbles_lost * 2)
        fantasy_points -= (interceptions_thrown * 2)
        fantasy_points += (special_teams_scores * 6)

        return fantasy_points

def player_id_from_name(player_name):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT playerID FROM player WHERE playerName = (\'{}\');".format(player_name)

    cursor.execute(statement)
    row = cursor.fetchone()
    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        return 0
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return row[0]

def add_weekly_game_stats_to_database(filename, year, opponentSideOfBall):
    stats = {
    'passingYards': 0,
    'rushingYards': 0,
    'receivingYards': 0,
    'receptions': 0,
    'receivingTargets': 0,
    'rushingAttempts': 0,
    'rushingScores': 0,
    'passingScores': 0,
    'receivingScores': 0,
    'fumblesLost': 0,
    'interceptionsThrown': 0,
    'specialTeamsScores': 0,
    'sacks': 0,
    'fumblesGained': 0,
    'interceptionsGained': 0,
    'pointsAllowed': 0,
    'rushingYardsAllowed': 0,
    'defensiveTouchdownsAllowed': 0,
    'defensiveTouchdowns': 0,
    'defensiveSafeties': 0,
    'fieldGoalsMade': 0,
    'fieldGoalsMissed': 0,
    'extraPointsMade': 0,
    'extraPointsMissed': 0,
    'season': year,
    'ageDuringGame': 0,
    'weekNumber': 0,
    'passingCompletions': 0,
    'passingAttempts': 0,
    'playerID': 0,
    'opponentTeamID': 0
    }
    try:
        input_file = open(filename, 'r')
        conn = mysql.connect()
        for player in input_file:
            split_player_stats = player.split(',')
            stats['passingYards'] = int(split_player_stats[16])
            stats['rushingYards'] = int(split_player_stats[25])
            stats['receivingYards'] = int(split_player_stats[30])

            stats['receptions'] = int(split_player_stats[29])
            stats['receivingTargets'] = int(split_player_stats[28])
            stats['rushingAttempts'] = int(split_player_stats[24])
            stats['rushingScores'] = int(split_player_stats[27])
            stats['passingScores'] = int(split_player_stats[17])
            stats['receivingScores'] = int(split_player_stats[32])
            stats['fumblesLost'] = split_player_stats[39]
            stats['interceptionsThrown'] = split_player_stats[18]
            stats['passingCompletions'] = split_player_stats[13]
            stats['passingAttempts'] = split_player_stats[14]
            stats['weekNumber'] = split_player_stats[11]

            fullAge = split_player_stats[3]
            firstTwoAge = fullAge[:2]
            stats['ageDuringGame'] = int(firstTwoAge)

            playerName = split_player_stats[1]
            playerName = playerName.split('*', 1)[0]
            playerName = playerName.split('+', 1)[0]
            playerName = playerName.split('\\', 1)[0]
            strippedPlayerName = playerName.replace("'", "")

            stats['playerID'] = player_id_from_name(strippedPlayerName)

            opponentAbbreviation = split_player_stats[8]
            if opponentAbbreviation in bad_abbreviation_set:
                opponentAbbreviation = bad_abbreviation_dict[opponentAbbreviation]

            stats['opponentTeamID'] = opponent_id_for_game(opponentAbbreviation, year, opponentSideOfBall)


            cursor = conn.cursor()
            statement = """INSERT INTO game (passingYards, rushingYards, receivingYards,
                        receptions, receivingTargets, rushingAttempts, rushingScores, passingScores,
                        receivingScores, fumblesLost, interceptionsThrown, specialTeamsScores, sacks,
                        fumblesGained, interceptionsGained, pointsAllowed, rushingYardsAllowed, defensiveTouchdowns,
                        defensiveSafeties, fieldGoalsMade, fieldGoalsMissed, extraPointsMade, extraPointsMissed,
                        season, playerID, opponentTeamID, ageDuringGame, weekNumber, passingCompletions, passingAttempts)
            VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11},
            {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23},
            {24}, {25}, {26}, {27}, {28}, {29});""".format(stats['passingYards'], stats['rushingYards'], stats['receivingYards'],
            stats['receptions'], stats['receivingTargets'], stats['rushingAttempts'], stats['rushingScores'],
            stats['passingScores'], stats['receivingScores'], stats['fumblesLost'], stats['interceptionsThrown'],
            stats['specialTeamsScores'], stats['sacks'], stats['fumblesGained'], stats['interceptionsGained'],
            stats['pointsAllowed'], stats['rushingYardsAllowed'], stats['defensiveTouchdowns'],
            stats['defensiveSafeties'], stats['fieldGoalsMade'], stats['fieldGoalsMissed'],
            stats['extraPointsMade'], stats['extraPointsMissed'], stats['season'],
            stats['playerID'], stats['opponentTeamID'], stats['ageDuringGame'], stats['weekNumber'],
            stats['passingCompletions'], stats['passingAttempts'])

            if (stats['playerID'] != 0):
                cursor.execute(statement)
            cursor.close()
            conn.commit()


    except FileNotFoundError:
        print("please enter a valid weekly stats file")
    conn.close()

def add_players_to_database(filename, year):
    try:
        input_file = open(filename, 'r')
        for line in input_file:
            split_line = line.split(',')
            try:
                if (split_line[1] != 'Player'):
                    player_name = split_line[1]
                    position = split_line[3]
                    age = int(split_line[4])

                    player_name = player_name.split('*', 1)[0]
                    player_name = player_name.split('+', 1)[0]
                    player_name = player_name.split('\\', 1)[0]
                    stripped_player_name = player_name.replace("'", "")

                    if player_name not in offensive_players:
                        offensive_players.add(player_name)
                        year_born = year - age
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        statement = "INSERT INTO player (position, playerName, yearBorn) VALUES (\'{}\', \'{}\', {});".format(position, stripped_player_name, year_born)

                        cursor.execute(statement)
                        cursor.close()
                        conn.commit()
                        conn.close()
            except ValueError:
                pass


        input_file.close()
    except FileNotFoundError:
        print("please enter a valid passing data file")

def add_team_stats_to_database(seasonValues, year, position):
    passingYardsAverage = round(seasonValues['passing_yards'] / 16.0, 1)
    rushingYardsAverage = round(seasonValues['rushing_yards'] / 16.0, 1)
    passingScoresAverage = round(seasonValues['passing_scores'] / 16.0, 1)
    rushingScoresAverage = round(seasonValues['rushing_scores'] / 16.0, 1)
    interceptionsThrownAverage = round(seasonValues['interceptions'] / 16.0, 1)
    fumblesAverage = round(seasonValues['fumbles'] / 16.0, 1)
    abbreviation = seasonValues['abbreviation']

    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "INSERT INTO team (rushingYardsAverage, rushingScoresAverage, passingYardsAverage, passingScoresAverage, fumblesAverage, interceptionsAverage, season, abbreviation, position) VALUES ({}, {}, {}, {}, {}, {}, {}, \'{}\', \'{}\');".format(rushingYardsAverage, rushingScoresAverage, passingYardsAverage, passingScoresAverage, fumblesAverage, interceptionsThrownAverage, year, abbreviation, position)

    cursor.execute(statement)

    cursor.close()
    conn.commit()
    conn.close()

def all_valid_players():
    valid_players = set()
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT playerName FROM player;"

    cursor.execute(statement)

    players = cursor.fetchall()

    for player in players:
        valid_players.add(player[0])

    return valid_players

def sanitize_player_name(name):
    full_name = name.split()
    if len(full_name) != 2:
        return "name {} is an improper length".format(name)
    else:
        first_name = full_name[0]
        last_name = full_name[1]
        first_name = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), first_name, 1)
        last_name = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), last_name, 1)
        full_name = "{} {}".format(first_name, last_name)
        return full_name
