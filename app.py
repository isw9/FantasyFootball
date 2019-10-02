from flask import Flask
from flaskext.mysql import MySQL
import nflgame

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_DATABASE_USER'] = 'secret'
app.config['MYSQL_DATABASE_PASSWORD'] = 'secret'
app.config['MYSQL_DATABASE_DB'] = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'secret'
print(app.config['MYSQL_DATABASE_USER'])
mysql.init_app(app)

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
    add_offense_stats_for_year('2011Offense.csv', 2011)
    add_offense_stats_for_year('2012Offense.csv', 2012)
    add_offense_stats_for_year('2013Offense.csv', 2013)
    add_offense_stats_for_year('2014Offense.csv', 2014)
    add_offense_stats_for_year('2015Offense.csv', 2015)
    add_offense_stats_for_year('2016Offense.csv', 2016)
    add_offense_stats_for_year('2017Offense.csv', 2017)
    add_offense_stats_for_year('2018Offense.csv', 2018)

    return "Hello"


def add_team_stats_to_database(seasonValues, year):
    passingYardsAverage = round(seasonValues['passing_yards'] / 16.0, 1)
    rushingYardsAverage = round(seasonValues['rushing_yards'] / 16.0, 1)
    passingScoresAverage = round(seasonValues['passing_scores'] / 16.0, 1)
    rushingScoresAverage = round(seasonValues['rushing_scores'] / 16.0, 1)
    interceptionsThrownAverage = round(seasonValues['interceptions'] / 16.0, 1)
    fumblesAverage = round(seasonValues['fumbles'] / 16.0, 1)
    abbreviation = seasonValues['abbreviation']
    print(passingYardsAverage)
    print(rushingYardsAverage)
    print(passingScoresAverage)
    print(rushingScoresAverage)
    print(interceptionsThrownAverage)
    print(fumblesAverage)
    print(abbreviation)


    conn = mysql.connect()
    cursor = conn.cursor()
    statement = "INSERT INTO team (rushingYardsAverage, rushingScoresAverage, passingYardsAverage, passingScoresAverage, fumblesAverage, interceptionsAverage, season, abbreviation) VALUES ({}, {}, {}, {}, {}, {}, {}, \'{}\');".format(rushingYardsAverage, rushingScoresAverage, passingYardsAverage, passingScoresAverage, fumblesAverage, interceptionsThrownAverage, year, abbreviation)

    print(statement)
    cursor.execute(statement)
    #
    #cursor.execute("SELECT * from team;")

    # while True:
    #     row = cursor.fetchone()
    #     if row == None:
    #         break
    #     print(row)
    #
    # data = cursor.fetchone()
    # print(data)
    #
    cursor.close()
    conn.commit()
    conn.close()

def add_offense_stats_for_year(filename, year):
    try:
        input_file = open(filename, 'r')
        for line in input_file:
            offenseDict = {}
            split_stats = line.split(',')
            try:
                team_rank = int(split_stats[0])
                if 0 <= team_rank and team_rank <= 32:
                    #print(split_stats[0])

                    offenseDict['rushing_yards'] = int(split_stats[18])
                    offenseDict['passing_yards'] = int(split_stats[12])
                    offenseDict['passing_scores'] = int(split_stats[13])
                    offenseDict['rushing_scores'] = int(split_stats[19])
                    offenseDict['fumbles'] = int(split_stats[8])
                    offenseDict['interceptions'] = int(split_stats[14])
                    full_name = split_stats[1]
                    abbreviation = abbreviation_dictionary[full_name]
                    print(abbreviation)
                    offenseDict['abbreviation'] = abbreviation



                    for i in offenseDict:
                        print (i)
                        print(offenseDict[i])

                    add_team_stats_to_database(offenseDict, year)
            except ValueError:
                pass
        input_file.close()
    except FileNotFoundError:
        print("please enter a valid team offense data file")
if __name__ == "__main__":
    app.run()
