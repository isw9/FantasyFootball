import sys
import math
import sklearn as skl
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler
import pymysql

CH = "[ML/DataBuilder] "  # Comment head


class DataBuilder:  # Object to request and format training data sets from MySQL DB
    def __init__(self, user, password, db, host):
        # Initialize DB Connection
        self.setup_connection(user, password, db, host)
        # Set MIN/MAX values for all attributes (allows for relative normalization)
        self.get_minmax()

    def setup_connection(self, u, p, db, h): #  Connect to DB, set object
        self.db_connection_str = 'mysql+pymysql://' + u + ':' + p + '@' + h + '/' + db
        self.db_connection = create_engine(self.db_connection_str)
        return True

    def query_to_df(self, query):
        df = pd.read_sql(query, con=self.db_connection)
        return df

    def get_minmax(self):
        self.gameMinMax = {} ; self.playerMinMax= {}
        list_gameAttr = [
            'gameID', 'passingYards', 'rushingYards', 'receivingYards',
            'receptions', 'receivingTargets', 'rushingAttempts', 'rushingScores',
            'passingScores', 'receivingScores', 'fumblesLost',
            'interceptionsThrown', 'specialTeamsScores', 'sacks', 'fumblesGained',
            'interceptionsGained', 'pointsAllowed', 'rushingYardsAllowed',
            'defensiveTouchdowns', 'defensiveSafeties', 'fieldGoalsMade',
            'fieldGoalsMissed', 'extraPointsMade', 'extraPointsMissed', 'season',
            'playerID', 'opponentTeamID', 'ageDuringGame', 'weekNumber',
            'passingCompletions', 'passingAttempts' ]
        list_playerAttr = [
            'playerID', 'yearBorn'
        ]

        for a in list_gameAttr:
            a_min = self.query_to_df("select MIN("+a+") from fantasyfootball.game;").values[0][0]
            a_max = self.query_to_df("select MAX("+a+") from fantasyfootball.game;").values[0][0]
            self.gameMinMax[a] = (a_min, a_max)

        for a in list_playerAttr:
            a_min = self.query_to_df("select MIN("+a+") from fantasyfootball.player;").values[0][0]
            a_max = self.query_to_df("select MAX("+a+") from fantasyfootball.player;").values[0][0]
            self.playerMinMax[a] = (a_min, a_max)
        return True

    def df_drop_zeroattr(self, df):
        for col in df.columns:
            try:
                mn, mx = self.gameMinMax[col]
                if mn == 0 and mx == 0:
                    df = df.drop(columns=[col])
            except KeyError:
                mn, mx = self.playerMinMax[col]
                if mn == 0 and mx == 0:
                    df = df.drop(columns=[col])
        return df

    def wiggle_norm_df(self, df, wiggle):  # Normalize columns of DataFrame based on attribute MinMax w/ wiggle% margins
        w = wiggle
        for col in df.columns:
            if col == "playerID":
                mn, mx = self.playerMinMax["playerID"]
            else:
                mn, mx = self.gameMinMax[col]
            print(col, mn, mx)
            if not (mn == 0 & mx == 0):
                wiggle_norm = lambda x: (x + ((0 - mn) + (w * (mx - mn)))) / (mx + ((mn - 0) + 2 * (w * (mx - mn))))
                df[col] = df[col].apply(wiggle_norm)
        return df


    def build_series_set(self, df, steps, train_perc):  # Return RNN training series from DataFrame  #TODO





        return 0

 #   def normalize_df(self, df):



if __name__ == "__main__":  # DB Connection Test

    u = sys.argv[1] ; p = sys.argv[2] ; db = sys.argv[3] ; h = sys.argv[4]
    print(CH+"u: " + u)
    print(CH+"p: " + p)
    print(CH+"db: " + db)
    print(CH+"h: " + h)

    dB = DataBuilder(u, p, db, h)

    df = dB.query_to_df("select * from fantasyfootball.game where playerID=666")
    print(dB.playerMinMax)
    print(dB.gameMinMax)

    print(df.columns)
    df = dB.df_drop_zeroattr(df)
    print(df.columns)

"""
    T = dB.build_series_set(df, 5, 0.6)
    print(T[0])
    print(T[1])

    print(CH+"Testing Connection . . . ")
    print()
    testB = DataBuilder(u, p, db, h)
    testdf = testB.query_to_df("SELECT * FROM fantasyfootball.game where gameID=1;")
    print(testdf)
    print(CH+"Success!")
"""
