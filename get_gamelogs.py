import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamelog


#to start with, here are the last 5 seasons
season_list = [
    '2022-21',
    '2021-20',
    '2020-19',
    '2019-18',
    '2018-17'
]
def getplayoffandregular(year):
    # get playoff stats
    df_reg = leaguegamelog.LeagueGameLog(
        season=year,
        season_type_all_star='Regular Season',
        player_or_team_abbreviation='P'
    ).get_data_frames()[0]
    # add a feature indicating that these rows are regular season
    df_reg['PLAYOFFS'] = 0

    # get regular season stats
    df_playoffs = leaguegamelog.LeagueGameLog(
        season=year,
        season_type_all_star='Playoffs',
        player_or_team_abbreviation='P'
    ).get_data_frames()[0]
    # add a feature indicating that these rows are playoffs
    df_playoffs['PLAYOFFS'] = 1

    # join them together
    df_all = pd.concat([df_reg, df_playoffs])
    return df_all


gamelogs = pd.DataFrame()
for year in season_list:
    df = getplayoffandregular(year)

    if gamelogs.empty:
        gamelogs = df
    else:
        gamelogs = pd.concat([gamelogs, df])

gamelogs.sort_values(['PLAYER_NAME', 'GAME_DATE'], ascending=[True, False], inplace=True)
gamelogs.drop(['FANTASY_PTS', 'VIDEO_AVAILABLE'], axis=1, inplace=True)

#get opponent name from the matchup string
gamelogs['OPPONENT'] = gamelogs['MATCHUP'].str.split(' vs. | @ ',expand=True)[1]

#get the opponent ID from the opponent abbreviation
def GetTeamID(s):
    return teams.find_team_by_abbreviation(s)['id']
gamelogs['OPPONENT_ID'] = gamelogs['OPPONENT'].apply(GetTeamID)

#pickle the gamelogs
title = ".\logs\All_%s-%s_Gamelogs.pkl" % (season_list[-1][0:4],season_list[0][-2:])
gamelogs.to_pickle(title)