import pandas as pd


def FutureStats(lines, eligible_players, matchup_dict):
    cols = ["PLAYER_NAME", "PLAYER_ID", "POSITION", "GAME_DATE", "TEAM_ABBREVIATION", "OPPONENT", "PLAYOFFS"]
    X = pd.merge(eligible_players, lines, left_on="PLAYER_NAME", right_on="PLAYER", sort=True)
    X['OPPONENT'] = X.apply(lambda x: matchup_dict[x.TEAM_ABBREVIATION][0], axis=1)
    X['GAME_DATE'] = X.apply(lambda x: matchup_dict[x.TEAM_ABBREVIATION][1], axis=1).astype(str)
    X['PLAYOFFS'] = 1
    return X[cols]


eligible_players = pd.read_pickle("./logs/eligible_players.pkl")
gamelogs = pd.read_pickle("./logs/gamelogs.pkl")

#
df = pd.merge(eligible_players, gamelogs, on=('PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION'))
df.sort_values(['PLAYER_NAME', 'GAME_DATE'], inplace=True)

# load scraped lines
lines = pd.read_pickle("./logs/latest_line_all.pkl")

matchup_dict = pd.read_pickle("./logs/upcoming_info.pkl")

futures = FutureStats(lines, eligible_players, matchup_dict)

futures["FUTURE_GAME"] = 1
df["FUTURE_GAME"] = 0

df_upcoming = pd.concat([df, futures], ignore_index=True)
df_upcoming.sort_values(['PLAYER_NAME', 'GAME_DATE', 'FUTURE_GAME'], inplace=True, ignore_index=True)

df_upcoming.to_pickle("./logs/current_and_future_logs.pkl")
