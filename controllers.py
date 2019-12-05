from flask import Blueprint, jsonify, request
from flaskext.mysql import MySQL
from flask import Flask
from heapq import nlargest
from util import *
from config import Config
#from ML.FF_LSTM import *
from keras import backend as K

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)


def api_player_projection(year, week, player, dB):
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

    K.clear_session()


    # # Load model by name
    model = load_model("3by50")
    # # set wiggle %
    w_norm = 0.05
    prediction = predict_next_week(playerID, week + 1, year, model, dB, w_norm)


    predicted_passing_yards = round(max(prediction.iloc[0]['passingYards'], 0), 1)
    predicted_rushing_yards = round(max(prediction.iloc[0]['rushingYards'], 0), 1)
    predicted_receiving_yards = round(max(prediction.iloc[0]['receivingYards'], 0), 1)
    predicted_receptions = round(max(prediction.iloc[0]['receptions'], 0), 1)
    predicted_passing_scores = round(max(prediction.iloc[0]['passingScores'], 0), 1)
    predicted_rushing_scores = round(max(prediction.iloc[0]['rushingScores'], 0), 1)
    predicted_receiving_scores = round(max(prediction.iloc[0]['receivingScores'], 0), 1)
    predicted_fumbles_lost = round(max(prediction.iloc[0]['fumblesLost'], 0), 1)
    predicted_interceptions = round(max(prediction.iloc[0]['interceptionsThrown'], 0), 1)


    predicted_score = 0.0

    predicted_score += (predicted_passing_yards * .04)
    predicted_score += (predicted_rushing_yards * .1)
    predicted_score += (predicted_receiving_yards * .1)
    predicted_score += (predicted_receptions * 1)
    predicted_score += (predicted_rushing_scores * 6)
    predicted_score += (predicted_passing_scores * 4)
    predicted_score += (predicted_receiving_scores * 6)
    predicted_score -= (predicted_fumbles_lost * 2)
    predicted_score -= (predicted_interceptions * 2)

    projected_score_final = round(predicted_score, 1)

    projection = {
        "name": row[2],
        "fantasy points": projected_score_final,
        "passing yards": predicted_passing_yards,
        "rushing yards": predicted_rushing_yards,
        "receiving yards": predicted_receiving_yards,
        "receptions": predicted_receptions,
        "passing touchdowns": predicted_passing_scores,
        "rushing touchdowns": predicted_rushing_scores,
        "receiving touchdowns": predicted_receiving_scores,
        "fumbles": predicted_fumbles_lost,
        "interceptions": predicted_interceptions
    }

    projection = massage_prediction(projection, row[1])
    projection['fantasy points'] = fantasy_points_from_projection(projection)
    K.clear_session()
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
    in_clause = "(SELECT player.playerID FROM game, player WHERE game.playerID = player.playerID AND fantasyfootball.player.position = (\'{}\') AND fantasyfootball.game.season = {} GROUP BY player.playerID HAVING COUNT(player.playerID) > 5)".format(position, year)
    statement = "SELECT * FROM game, player WHERE game.playerID = player.playerID AND player.position = (\'{}\') AND game.season = {} AND player.playerID IN {};".format(position, year, in_clause)
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
