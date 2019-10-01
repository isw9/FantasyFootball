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

@app.route("/")
def main():

    #tests connecting to the mysql database that's setup on AWS when the configs are provided
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * from player;")

    data = cursor.fetchone()
    print(data)

    cursor.close()
    conn.close()


    games = nflgame.games(2013, week=1)
    players = nflgame.combine_game_stats(games)
    for p in players.rushing().sort('rushing_yds').limit(5):
        msg = '%s %d carries for %d yards and %d TDs'
        print(msg % (p, p.rushing_att, p.rushing_yds, p.rushing_tds))
    return "Hello"


if __name__ == "__main__":
    app.run()
