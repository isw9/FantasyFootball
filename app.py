from flask import Flask
from flaskext.mysql import MySQL
import nflgame
from flask import request

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_DATABASE_USER'] = 'secret'
app.config['MYSQL_DATABASE_PASSWORD'] = 'secret'
app.config['MYSQL_DATABASE_DB'] = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'secret'
mysql.init_app(app)

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


@app.route("/")
def main():
    return "this will be the home page that shows the leaders"

@app.route('/weeklyStart')
def weeklyStart():
    return "this is where we set up the weekly start page"

@app.route("/leaders/<number_of_players>")
def leaders (number_of_players):
    return "this will be a GET endpoint to show season stats for the top {0} players at each position".format(number_of_players)


@app.route('/player/', methods = ['GET'])
def player():
    player_name = request.args.get('player_name')
    conn = mysql.connect()
    cursor = conn.cursor()
    statement = statement = "SELECT * FROM player WHERE playerName = (\'{}\');".format(player_name)

    cursor.execute(statement)
    row = cursor.fetchone()


    if row == None:
        cursor.close()
        conn.commit()
        conn.close()
        code = 400
        msg = " player with name {} could not be found;".format(player_name)
        return msg, code


    cursor.close()
    conn.commit()
    conn.close()
    print(row)
    name = row[2]
    player = {
        "name": row[2],
        "average points scored": 10.0
    }
    print(name)
    return player




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
            print(split_player_stats[1])

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
                    print(split_line[1])
                    position = split_line[3]
                    age = int(split_line[4])
                    print(position)


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

if __name__ == "__main__":
    app.run()
