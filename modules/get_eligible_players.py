'''
Get eligible players by position!
Iterate over three position types (G, F, C) and sort by players who have played 500+ minutes and 30+ games in the last season

n.b. consider changing these criteria to be more robust to account for hurt players
'''

# filter by games and minutes played
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats


def gp_min_filter(df, min_limit=500, gp_limit=30):
    return df[(df['MIN'] >= min_limit) & (df['GP'] >= gp_limit)]


eligible_players = pd.DataFrame()

for position in ['G', 'F', 'C']:

    df = leaguedashplayerstats.LeagueDashPlayerStats(
        player_position_abbreviation_nullable=position).get_data_frames()[0]

    # drop all of the ranking columns
    df.drop([i for i in df.columns if 'RANK' in i], axis=1, inplace=True)
    # drop all of the PCT columns, because they are linear combinations
    df.drop([i for i in df.columns if 'PCT' in i], axis=1, inplace=True)

    df = gp_min_filter(df)
    df['POSITION'] = position

    df = df[['PLAYER_NAME', 'PLAYER_ID', 'AGE', 'POSITION', 'TEAM_ABBREVIATION']]

    if eligible_players.empty:
        eligible_players = df
    else:
        eligible_players = pd.concat([eligible_players, df])

# pickle the players list for later if necessary
eligible_players.to_pickle("..\logs\eligible_players.pkl")