import pandas as pd

def flipColNames(c):
    d = dict()
    for s in c:
        parts = s.split("_")
        d[s] = "_".join(parts[::-1])
    return d

### ALL STATS LONG JSON PRODUCTION

# load predictions
df = pd.read_pickle(f"./logs/current_and_future_predictions.pkl")

#first get some season/playoff start and end dates
cutoffs = df.groupby(["SEASON_ID", "PLAYOFFS"]).agg({"GAME_DATE":["min","max"]})
cutoffs.columns = ['start', 'stop']
cutoffs.reset_index(inplace=True)
cutoffs.replace([0,1], ['Regular Season','Playoffs'], inplace=True)
cutoffs.to_pickle(f"./logs/season_cutoffs")

# aggregate players with predictions for multiple positions by simply averaging the predictions together
# (e.g. Luka Doncic is listed as both a Guard and a Forward. Average the G and F predictions together)
df = df.groupby(['PLAYER_NAME', 'GAME_DATE', 'OPPONENT']).agg('mean').reset_index()

# stats of interest.
stats = ["PTS", "REB", "AST", "FG3M", "BLK", "STL"]
to_melt = stats + [s + "_PREDICT" for s in stats]
to_keep = ["PLAYER_NAME", "PLAYER_ID", "GAME_DATE", "OPPONENT", "PLAYOFFS", "FUTURE_GAME"]

# melt df into "long" format for ease of Altair plotting
df_long = pd.melt(df, id_vars=to_keep, value_vars=to_melt, var_name="MODEL", value_name="VALUE")
df_long.sort_values(['PLAYER_NAME', 'GAME_DATE', 'MODEL'], inplace=True)
df_long.reset_index(drop=True, inplace=True)

# save the long .json
url = f"./logs/predicted_stats.json"
df_long.to_json(url, orient="records")

### BEST BET LONG DF PRODUCTION

#load predictions and lines
df_p = pd.read_pickle(f"./logs/current_and_future_predictions.pkl")
df_p = df_p.loc[df_p['FUTURE_GAME']==1] #get only upcoming predictions

lines = pd.read_pickle(f"./logs/latest_line_all.pkl")

#get labels for the stats and stats+"_PREDICT"
stats = ["PTS", "REB", "AST", "FG3M", "BLK", "STL"]
stats_pred = [s+"_PREDICT" for s in stats]

#join the lines and the predictions
non_stat_cols = ["PLAYER_NAME",
         "OPPONENT",
         "GAME_DATE"]

df_p = (df_p[non_stat_cols+['POSITION']+stats_pred]
        .groupby(non_stat_cols).agg("mean").reset_index()
        .merge(lines, left_on='PLAYER_NAME', right_on='PLAYER')
        .drop("PLAYER", axis=1)
       )

#make a normalized deltaF/F "score" for comparing deviations among stats
#e.g. +3 BLK predicted is much stronger signal than +3 PTS

for stat in stats:
    df_p[stat+"_dff"] = (df_p[stat+"_PREDICT"] - df_p[stat+"_LINE"]) / df_p[stat+"_LINE"]

#flip the column names for proper conversion to long
c = df_p.columns.to_list()[3:]
c_flip = flipColNames(c)
df_p.rename(columns=c_flip, inplace=True)

labels = ["PREDICT", "LINE", "OVER", "UNDER", "dff"]
df_p_long = pd.wide_to_long(df_p, stubnames=labels, i = ["PLAYER_NAME","GAME_DATE"], j="STAT", sep="_", suffix=r'\w+')[labels]
df_p_long.reset_index(inplace=True)

df_p_long.to_pickle(f"./logs/best_bet.pkl")