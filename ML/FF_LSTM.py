import sys
import keras
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import importlib
from DataBuilder import DataBuilder

CH = "[FF_LSTM] "

if __name__ == "__main__":
    print(CH + "Connecting to database. . .")
    u = sys.argv[1]; p = sys.argv[2]; db = sys.argv[3]; h = sys.argv[4]
    print(CH + " u: " + u)
    print(CH + " p: " + p)
    print(CH + "db: " + db)
    print(CH + " h: " + h)

    dB = DataBuilder(u, p, db, h)
    df = dB.get_player_stats(666)
    df = dB.df_add_0Weeks(df)
    df = dB.wiggle_norm(df)
    Xtrain, Ytrain, Xtest, Ytest = dB.build_series_set(df, 10, .5, slide=True)





