import sys
import random
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

CH = "[ML/DataBuilder] "  # Comment head


class DataBuilder:  # Object to request and format training data sets from MySQL DB
    def __init__(self, user, password, db, host):
        # Initialize DB Connection
        self.setup_connection(user, password, db, host)

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
            if col == "opponentTeamID":
                mn, mx = self.gameMinMax[col]
                norm = lambda x: (x - mn) / (mx - mn)
                df[col] = df[col].apply(norm)
            elif col != "gameID":
                mn, mx = self.gameMinMax[col]
                if not (mn == 0 and mx == 0):
                    if (mn == 0):
                        wiggle_norm = lambda x: x / (mx + w * mx)
                    else:
                        s = (mx - mn) * w
                        mx = mx + s ; mn = mn - s
                        wiggle_norm = lambda x: (x - mn) / (mx - mn)
                df[col] = df[col].apply(wiggle_norm)

        return df

    def denormalize_prediction(self, predictionData, wiggle):
        w = wiggle
        df = pd.DataFrame(predictionData, columns=["passingYards", "rushingYards", "receivingYards", "receptions", "receivingTargets", "rushingAttempts", "rushingScores",
                                          "passingScores", "receivingScores", "fumblesLost", "interceptionsThrown", "passingCompletions", "passingAttempts"])

        for col in df.columns:
            if col == "opponentTeamID":
                mn, mx = self.gameMinMax[col]
                norm = lambda x: (x - mn) / (mx - mn)
                df[col] = df[col].apply(norm)
            elif col != "gameID":
                mn, mx = self.gameMinMax[col]
                if not (mn == 0 and mx == 0):
                    if (mn == 0):
                        DEwiggle_norm = lambda x: x * (mx + w * mx)
                    else:
                        s = (mx - mn) * w
                        mx = mx + s ; mn = mn - s
                        DEwiggle_norm = lambda x: (x * (mx - mn)) + mn
                df[col] = df[col].apply(DEwiggle_norm)

        return df

    def get_player_stats(self, playerID):  # Return all non 0 player stats as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        orderBy = " ORDER BY season ASC, weekNumber ASC, gameID ASC;"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + orderBy
        P_df = self.query_to_df(query)
        P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return P_df.reset_index(drop=True)

    def get_player_stats_LIMweeks(self, playerID, limit):  # Return non 0 player stats w/limit as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        orderBy = " ORDER BY season ASC, weekNumber ASC, gameID ASC"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + orderBy + " LIMIT " + str(limit) + ""
        P_df = self.query_to_df(query)
        P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return P_df.reset_index(drop=True)

    def get_player_stats_LIMseason(self, playerID, season):  # Return non 0 player stats w/limit as DataFrame
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        orderBy = " ORDER BY season ASC, weekNumber ASC, gameID ASC"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + " and season = " + str(season) + orderBy + ";"
        P_df = self.query_to_df(query)
        P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return P_df.reset_index(drop=True)

    def get_player_stats_Latest(self, playerID, limit):
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        orderBy = " ORDER BY season ASC, weekNumber ASC, gameID ASC"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) + orderBy + " LIMIT " + str(limit) + ""
        P_df = self.query_to_df(query)
        P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return P_df.reset_index(drop=True)

    def df_add_0Weeks(self, df):
        l_week = int(df.iloc[0]['weekNumber']) ; l_season = int(df.iloc[0]['season'])
        zero_stats = np.zeros(18)

        for i in range(1, len(df)):
            # Set current week
            c_week = int(df.iloc[i]['weekNumber']) ; c_season = int(df.iloc[i]['season'])
            if int(c_season) == int(l_season):  # Add weeks into same season
                dif_week = c_week - l_week
                if dif_week > 1:  # add dif_week-1 weeks w/"weekNumber" = [l_week+1 ... c_week -1]
                    zero_stats[1] = c_season ; zero_stats[4] = int((df.iloc[i]['ageDuringGame']))
                    for w in range(l_week+1, c_week):
                        zero_stats[0] = i*10000 + w ; zero_stats[2] = w
                        zero_stats[3] = random.randrange(self.gameMinMax["opponentTeamID"][0], self.gameMinMax["opponentTeamID"][1])
                        df = df.append(pd.DataFrame( zero_stats.reshape(-1, len(zero_stats)), columns=df.columns))

            else: # Add weeks between seasons
                dif_week = 17 - l_week
                if dif_week != 0:
                    for w in range(l_week, 17):
                        zero_stats[0] = i*10000 + w ; zero_stats[1] = l_season
                        zero_stats[2] = w+1 ; zero_stats[3] = random.randrange(self.gameMinMax["opponentTeamID"][0], self.gameMinMax["opponentTeamID"][1])
                        zero_stats[4] = int((df.iloc[i]['ageDuringGame']))
                        df = df.append(pd.DataFrame(zero_stats.reshape(-1, len(zero_stats)), columns=df.columns))
            l_week = c_week ; l_season = c_season

        df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return df.reset_index(drop=True)

    def build_series_set(self, df, time_steps, train_percentage, slide=True):  # Return RNN training series from DataFrame #
        # Input: [info + stats] x time_steps
        # Output [stats]
        # Return X_train, X_test, Y_train, Y_test

        df.drop(columns=["gameID"], inplace=True)
        n_rows = len(df)
        n_cols = len(df.columns)

        if not slide:   # Standard reshape
            print(CH+" ! Use Slide Instead !")
            return False
            # n_rows = len(df)
            # data = df.values
            # X = data.reshape(int(n_rows/time_steps), time_steps, n_cols)

        else:   # Expand series by "sliding" across data rather than stepping, basically numpy shift
            Y = df.drop(columns=["season", "weekNumber", "opponentTeamID", "ageDuringGame"])[time_steps:].values
            X = np.zeros(((n_rows - 1 - time_steps + 1) * time_steps, n_cols))
            in_data = df.values[0 : n_rows - 1]

            for i in range(0, len(in_data) - time_steps + 1):
                X[i*time_steps: (i+1) * time_steps] = in_data[i: i + time_steps]

            X = X.reshape(int(len(X)/time_steps), time_steps, n_cols)
            X_train = X[0: int(len(X)*train_percentage)] ; X_test = X[int(len(X)*train_percentage):]
            Y_train = Y[0: int(len(Y) * train_percentage)] ; Y_test = Y[int(len(Y) * train_percentage):]
            return X_train, Y_train, X_test, Y_test

    def get_top10_players(self, position, season, FS = False):
        info = "season"

        # Get all playerID's for position
        pos_playerIDs_query = "Select distinct fantasyfootball.player.playerID "\
                              "from fantasyfootball.game, fantasyfootball.player "\
                              "where position = \""+position+"\" and season = " + str(season)+ " "\
                              "and fantasyfootball.game.playerID = fantasyfootball.player.playerID"
        pos_playerIDs = self.query_to_df(pos_playerIDs_query).values

        # Get average stats values for player by season
        if not FS:
            stats_avg = " AVG(passingYards), AVG(rushingYards), AVG(receivingYards), AVG(receptions), " \
                        " AVG(rushingScores), AVG(passingScores), AVG(receivingScores), AVG(fumblesLost), " \
                        "AVG(interceptionsThrown),  "
        else:
            stats_avg = " AVG(passingYards)*0.04, AVG(rushingYards)*0.1, AVG(receivingYards)*0.1, AVG(receptions), " \
                        " AVG(rushingScores)*6, AVG(passingScores)*4, AVG(receivingScores)*6, AVG(fumblesLost)*2, " \
                        "AVG(interceptionsThrown)*2,  "

        avg_fantasyscore = " AVG(passingYards)*0.04 + AVG(rushingYards)*0.1 + AVG(receivingYards)*0.1 + AVG(receptions) +" \
                           " AVG(rushingScores)*6 + AVG(passingScores)*4 + AVG(receivingScores)*6 - AVG(fumblesLost)*2 -" \
                           " AVG(interceptionsThrown)*2 as FSAvg "

        avgs_df = pd.DataFrame()

        for i in range(0, len(pos_playerIDs-1)):
            player_season_avg_query = "Select playerID," + stats_avg + avg_fantasyscore + " from fantasyfootball.game where playerID=" \
                                      + str(pos_playerIDs[i][0]) + " and season=" + str(season)
            playerID_avg = self.query_to_df(player_season_avg_query)
            avgs_df = pd.concat((avgs_df, playerID_avg))

        avgs_df.sort_values(["FSAvg"], ascending=[False], inplace=True)

        return avgs_df[0:10].sort_values(["FSAvg"], ascending=[True])

    def get_Xweeks_from(self, playerID, X,  season, week):
        info = "gameID, season, weekNumber, opponentTeamID, ageDuringGame"
        stats = "passingYards, rushingYards, receivingYards, receptions, receivingTargets, " \
                "rushingAttempts, rushingScores, passingScores, receivingScores, fumblesLost, " \
                "interceptionsThrown, passingCompletions, passingAttempts"
        orderBy = " ORDER BY season ASC, weekNumber ASC, gameID ASC"
        query = "SELECT " + info + ", " + stats + " FROM fantasyfootball.game WHERE playerID = " + str(playerID) \
                + " and season >= " + str(season) + " and weekNumber >= "+str(week) + orderBy + " LIMIT " + str(X) + ""
        P_df = self.query_to_df(query)
        P_df.sort_values(["season", "weekNumber", "gameID"], ascending=[True, True, True], inplace=True)
        return P_df.reset_index(drop=True)


if __name__ == "__main__":
    u = sys.argv[1] ; p = sys.argv[2] ; db = sys.argv[3] ; h = sys.argv[4]
    print(CH+" u: " + u)
    print(CH+" p: " + p)
    print(CH+"db: " + db)
    print(CH+" h: " + h)

    dB = DataBuilder(u, p, db, h)
    print(dB.get_Xweeks_from(666, 11, 2016, 4))




