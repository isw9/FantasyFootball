import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

CH = "[ML/DataBuilder] "  # Comment head


class DataBuilder:  # Object to request and format training data sets from MySQL DB
    def __init__(self, user, password, db, host):
        # Initialize DB Connection
        self.setup_connection(user, password, db, host)
        # Set MIN/MAX values for all attributes (allows for relative normalization)
        self.db_get_minmax()

    def setup_connection(self, u, p, db, h): #  Connect to DB, set object
        self.db_connection_str = 'mysql+pymysql://' + u + ':' + p + '@' + h + '/' + db
        self.db_connection = create_engine(self.db_connection_str)
        return True

    def query_to_df(self, query):  # Read SQL query as DataFrame
        df = pd.read_sql(query, con=self.db_connection)
        return df

    def db_get_minmax(self): # Check for unfilled attributes in db
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

    def df_drop_zeroattr(self, df):  # Drop unfilled attributes from df
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

    def df_wiggle_norm(self, df, wiggle):  # Normalize columns of DataFrame based on attribute MinMax w/ wiggle% margins
        w = wiggle
        for col in df.columns:
            if col == "playerID":
                mn, mx = self.playerMinMax["playerID"]
            else:
                mn, mx = self.gameMinMax[col]
            if not (mn == 0 & mx == 0):
                wiggle_norm = lambda x: (x + ((0 - mn) + (w * (mx - mn)))) / (mx + ((mn - 0) + 2 * (w * (mx - mn))))
                df[col] = df[col].apply(wiggle_norm)
        return df

    def get_player_stats(self, playerID):  # Return all non 0 player stats as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + ";"
        P_df = self.query_to_df(query)
        P_df = P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True])
        return P_df

    def get_player_stats_LIMgames(self, playerID, limit):  # Return non 0 player stats w/limit as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + " LIMIT " + str(limit) +";"
        P_df = self.query_to_df(query)
        P_df = P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True])
        return P_df

    def get_player_stats_LIMseason(self, playerID, season):  # Return non 0 player stats w/limit as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + " and season = " + str(season) + ";"
        P_df = self.query_to_df(query)
        P_df = P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True])
        return P_df

    def build_series_set(self, df, time_steps, train_percentage, slide=False):  # Return RNN training series from DataFrame
        n_rows = len(df)
        n_cols = len(df.columns)

        if not slide:   # Standard reshape
            df = df[n_rows % time_steps:]  # cut off beginning of df so n_rows % time_steps = 0
            n_rows = len(df)
            data = df.values
            data = data.reshape(int(n_rows/time_steps), time_steps, n_cols)
            return data

        else:   # Expand series by "sliding" across data rather than stepping #TODO: FIX
            data=df.values
            exp_data = np.zeros((((n_rows-time_steps+1)*time_steps), n_cols))
            for i in range(0,len(data) - time_steps + 1):
                exp_data[i*time_steps: (i+1)*time_steps] = data[i:i+time_steps]
            data = exp_data.reshape(int(len(exp_data)/time_steps), time_steps, n_cols)
            return data


if __name__ == "__main__":  # DB Connection Test

    u = sys.argv[1] ; p = sys.argv[2] ; db = sys.argv[3] ; h = sys.argv[4]
    print(CH+" u: " + u)
    print(CH+" p: " + p)
    print(CH+"db: " + db)
    print(CH+" h: " + h)

    dB = DataBuilder(u, p, db, h)
    df = dB.get_player_stats_LIMgames(666,21)

    data = dB.build_series_set(df, 10, 1, slide=True)
    print(data)
