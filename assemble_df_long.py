import pandas as pd

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
