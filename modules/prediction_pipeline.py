import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import OneHotEncoder


# ShiftStats transformer selects the appropriate personal stats and shifts them for the last game, 2 games ago, etc.
class ShiftStats(BaseEstimator, TransformerMixin):
    def __init__(self, stats, shiftwidth=1):
        self.stats = stats
        self.shiftwidth = shiftwidth

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        stats_shifted = X[['PLAYER_ID'] + self.stats].groupby(['PLAYER_ID']).shift(self.shiftwidth)
        return stats_shifted


# Cumulative stats generates rolling cumulative average, and a rolling average of last 4 games with smoothing weight
class MakeCumulativeStats(BaseEstimator, TransformerMixin):

    def __init__(self, stats, window=4):
        self.stats = stats
        self.window = window

    def fit(self, X, y=None):
        self.game_number = X[['PLAYER_ID']].groupby(['PLAYER_ID']).cumcount() + 1
        return self

    def transform(self, X):
        df = pd.DataFrame()
        for stat in self.stats:
            # make cumulative sum of counting stats and divide by game number
            df[stat + '_AVG'] = X[['PLAYER_ID', stat]].groupby(['PLAYER_ID']).cumsum()
            df[stat + '_AVG'] = df[stat + '_AVG'] / self.game_number

            # make rolling average of counting stats. Uses a window of 4 games, and a Gaussian window with std 3 weight
            temp = (X[['PLAYER_ID', stat]]
                    .groupby(['PLAYER_ID'])
                    .rolling(self.window, min_periods=1, win_type='gaussian', closed='left')
                    .mean(std=3)
                    )

            df[stat + '_RECENT'] = temp.reset_index(level=0)[stat]
        return df.sort_index(ascending=False, inplace=True)


# Opponent stats gets the players stats during last and last-3 previous matchups
class MakeOpponentStats(BaseEstimator, TransformerMixin):
    def __init__(self, stats, window=3):
        self.stats = stats
        self.window = window

    def fit(self, X, y=None):
        self.game_number = X[['PLAYER_ID']].groupby(['PLAYER_ID']).cumcount() + 1
        return self

    def transform(self, X):
        df = pd.DataFrame()
        for stat in self.stats:
            # last matchup against opponent
            temp = (X[['PLAYER_ID', 'OPPONENT', stat]]
                    .groupby(['PLAYER_ID', 'OPPONENT'])
                    .rolling(1, min_periods=1, closed='left')
                    .mean()
                    )

            df[stat + '_PREV_VS_OPP'] = temp.reset_index(level=[0, 1])[stat]  # reset multilevel indices

            # avg 3 past matchups against opponent
            temp = (X[['PLAYER_ID', 'OPPONENT', stat]]
                    .groupby(['PLAYER_ID', 'OPPONENT'])
                    .rolling(self.window, min_periods=1, closed='left')
                    .mean()
                    )

            df[stat + '_PREV3_VS_OPP'] = temp.reset_index(level=[0, 1])[stat]

        return df.sort_index(ascending=False)


# "group-by" estimator that applies the pipeline defined below to each player position (G, F, C)
# based on the TDI ts miniproject
class GroupbyEstimator(BaseEstimator, RegressorMixin):

    def __init__(self, column, estimator_factory):
        # column is the value to group by; estimator_factory can be
        # called to produce estimators
        self.column = column
        self.estimator_factory = estimator_factory
        self.predictors = {}
        self.predictions = {}
        self.player_names = {}

    def helper_fit(self, X, y):
        # get position name
        position_name = X[self.column].iloc[0]

        # index y by city index to get "grouped" y
        y_position = y.loc[X.index]

        # apply estimator to grouped X and y
        self.predictors[position_name] = self.estimator_factory().fit(X, y_position)

    def fit(self, X, y):
        X_group = X.groupby(self.column)
        X_group.apply(self.helper_fit, y)

        return self

    def helper_predict(self, X):
        # get position name
        position_name = X[self.column].iloc[0]
        # predict make a predictor for a given city
        self.predictions[position_name] = pd.Series(self.predictors[position_name].predict(X))
        self.player_names[position_name] = X['PLAYER_NAME']

        return self.predictors[position_name]

    def predict(self, X):
        X_group = X.groupby(self.column)
        X_group.apply(self.helper_predict)

        return pd.concat(self.predictions)


# make pipeline that does the following:
# 1) One-hot encodes TEAM, OPPONENT, and PLAYOFFS
# 2) does game-shifts with windows of 1, 2, and 3-games past
# 3) get cumulative self
# 4) get rolling stats of past matchups vs opponent
def stat_pipeline():
    # List of stats that should be accumulated. Might change later
    stats_to_accumulate = ['MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
                           'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                           'PF', 'PTS', 'PLUS_MINUS']

    # one-hot encode the player's team, the opponent team, and whether it's a playoff or regular game
    ct_features = ColumnTransformer([
        ('OHE', OneHotEncoder(), ['TEAM_ABBREVIATION', 'OPPONENT', 'PLAYOFFS'])
    ])

    # join together the OHE features, and the 3 transformers for current, cumulative, and opponent stats
    all_features = FeatureUnion([
        ('ct_features', ct_features),
        ('one_game_ago', ShiftStats(stats_to_accumulate, shiftwidth=1)),
        ('two_games_ago', ShiftStats(stats_to_accumulate, shiftwidth=2)),
        ('three_games_ago', ShiftStats(stats_to_accumulate, shiftwidth=3)),
        ('cum_stats', MakeCumulativeStats(stats_to_accumulate)),
        ('opp_stats', MakeOpponentStats(stats_to_accumulate))
    ])

    pipe = Pipeline([
        ('features', all_features),
        ('imputer', SimpleImputer()),
        ('regressor', RidgeCV(alphas=np.logspace(-4, 4, 10)))
    ])
    return pipe
