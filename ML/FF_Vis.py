import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
#import matplotlib.pyplot as plt
from DataBuilder import DataBuilder

CH = "[FF_Vis] "

"""
TODO
kde_ridgeplot for comparing single stats/FF scores between several players, multiplot
https://seaborn.pydata.org/examples/kde_ridgeplot.html

regression_marginals for comparing 2 stat totals for set of players
https://seaborn.pydata.org/examples/regression_marginals.html

categorical point plot for yearly average progression of player's stats
https://seaborn.pydata.org/examples/pointplot_anova.html

annotated heatmap with marginal distributions to show total/average stats of a team
https://seaborn.pydata.org/examples/heatmap_annotation.html
"""


## Top 10's by Year
# Horizontal bar chart w/breakdown by fantasy points

def make_top_10_QB_graph(position, season, dB):
    top_10 = dB.get_top10_players(position, season, FS=True)

    top_10.plot.barh(x="playerID")
    #plt.savefig("test.png")

    return True

if __name__ == "__main__":
    print(CH + "Connecting to database. . .")
    u = sys.argv[1] ; p = sys.argv[2] ; db = sys.argv[3] ; h = sys.argv[4]
    print(CH+" u: " + u)
    print(CH+" p: " + p)
    print(CH+"db: " + db)
    print(CH+" h: " + h)

    dB = DataBuilder(u, p, db, h)

    make_top_10_QB_graph("QB", 2018, dB)
