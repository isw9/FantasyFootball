from flask import Blueprint, jsonify, request
from flaskext.mysql import MySQL
from flask import Flask
from util import *

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_DATABASE_USER'] = 'secret'
app.config['MYSQL_DATABASE_PASSWORD'] = 'secret'
app.config['MYSQL_DATABASE_DB'] = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'secret'


def iter_row(cursor, size=100):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

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
        print(row[0])
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
                    #print(split_stats[0])

                    teamDict['rushing_yards'] = int(split_stats[18])
                    teamDict['passing_yards'] = int(split_stats[12])
                    teamDict['passing_scores'] = int(split_stats[13])
                    teamDict['rushing_scores'] = int(split_stats[19])
                    teamDict['fumbles'] = int(split_stats[8])
                    teamDict['interceptions'] = int(split_stats[14])
                    full_name = split_stats[1]
                    abbreviation = abbreviation_dictionary[full_name]
                    print(abbreviation)
                    teamDict['abbreviation'] = abbreviation



                    for i in teamDict:
                        print (i)
                        print(teamDict[i])

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
