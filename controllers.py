from flask import Blueprint, jsonify, request
from flaskext.mysql import MySQL
from flask import Flask
from heapq import nlargest
from util import *
from config import Config
#from ML.FF_LSTM import *

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def api_player_projection(year, week, player):
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = statement = "SELECT * FROM player WHERE playerName = (\'{}\');".format(player)

    cursor.execute(statement)
    row = cursor.fetchone()


    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        code = 400
        msg = " player with name {} could not be found;".format(player)
        return msg, code

    cursor.close()
    conn.commit()
    conn.close()

    name = row[2]
    playerID = row[0]


    # u = 'secret'
    # p = 'secret'
    # db = 'secret'
    # h = 'secret'
    #
    #
    # model = load_model("ML/testModel")

    # michael pick up here
    # need something like
    # predicted_dictionary = prediction(playerID, week, year)

#     dB = DataBuilder(u, p, db, h)
#     dB.db_get_minmax()
#
#     test_df = dB.get_Xweeks_from(playerID, 11, year, week)
# #     # Get set of weeks to test:
# #     test_df = dB.get_Xweeks_from(521, 11, 2015, 4)
# #     print(test_df)
# #     print(test_df.iloc[10:])
# #     predict and compare to truth
#     predict_and_compare(model, test_df, 0.05, dB)

    projection = {
        "name": row[2],
        "fantasy points": 22.7,
        "passing yards": 223,
        "rushing yards": 18,
        "recieving yards": 0,
        "passing touchdowns": 2,
        "rushing touchdowns": 1,
        "receiving touchdowns": 0,
        "fumbles": 0,
        "interceptions": 1
    }

    return projection

def api_leaders(year, number_players, position):
    position = position.upper()

    valid_positions = {'WR', 'QB', 'RB', 'TE'}

    if position not in valid_positions:
        code = 400
        msg = " position {} is not valid;".format(position)
        return msg, code

    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "SELECT * FROM game, player WHERE game.playerID = player.playerID AND player.position = (\'{}\') AND game.season = {};".format(position, year)
    cursor.execute(statement)

    playerIDToCumulativeScore = dict()
    playerIDToGamesPlayed = dict()
    seenPlayers = set()

    for record in iter_row(cursor, 100):
        playerID = record[25]

        if playerID in seenPlayers:
            current_score = playerIDToCumulativeScore[playerID]
            game_score = fantasy_points_from_game_stats(record)
            playerIDToCumulativeScore[playerID] = current_score + game_score

            playerIDToGamesPlayed[playerID] += 1
        else:
            seenPlayers.add(playerID)
            game_score = fantasy_points_from_game_stats(record)
            playerIDToCumulativeScore[playerID] = game_score

            playerIDToGamesPlayed[playerID] = 1


    for player in playerIDToCumulativeScore:
        games_played = playerIDToGamesPlayed[player]
        cumulative_score = playerIDToCumulativeScore[player]
        per_game_score = round(cumulative_score / games_played, 1)
        playerIDToCumulativeScore[player] = per_game_score

    number_players = int(number_players)
    if number_players >= len(playerIDToCumulativeScore):
        highest_scores = nlargest(len(playerIDToCumulativeScore), playerIDToCumulativeScore, key = playerIDToCumulativeScore.get)
    else:
        highest_scores = nlargest(number_players, playerIDToCumulativeScore, key = playerIDToCumulativeScore.get)

    return_dictionary = dict()

    for player_id in highest_scores:
        player_name = player_name_from_player_id(player_id)
        return_dictionary[player_name] = playerIDToCumulativeScore.get(player_id)


    if record is None:
        cursor.close()
        conn.commit()
        conn.close()
        code = 400
        msg = "leaders could not be found for year {}".format(year)
        return msg, code


    cursor.close()
    conn.commit()
    conn.close()

    return return_dictionary
