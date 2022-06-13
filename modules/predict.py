import dill as pickle
import pandas as pd
import os
import prediction_pipeline as pp


def makeModel(df, stat='PTS'):
    model = pp.GroupbyEstimator('POSITION', pp.stat_pipeline).fit(df, df[stat])

    model_path = os.path.join(os.path.pardir,"logs","models",f"model_{stat}.pkl")
    with open(model_path, 'wb') as file:
        pickle.dump(model, file)
    return model

df_upcoming_path = os.path.join(os.path.pardir,"logs","current_and_future_logs.pkl")
df = pd.read_pickle(df_upcoming_path)

# get only past data for training model
df_past = df[df["FUTURE_GAME"] == 0]

# list of stats to model
stats = ["PTS", "REB", "AST", "FG3M", "BLK", "STL"]

all_p = pd.DataFrame()

# iterate over stats to model
for stat in stats:
    print(f"Modeling {stat}...")
    # make trained model using only past games
    model = makeModel(df_past, stat)

    # use model to predict all games, including past and future
    prediction = model.predict(df)

    all_p[stat + "_PREDICT"] = prediction

df_predict = pd.DataFrame()
for pos in ["C", "F", "G"]:
    temp = df[df['POSITION'] == pos].copy()
    temp.reset_index(inplace=True, drop=True)
    df_predict = pd.concat([df_predict, temp.join(all_p.loc[pos])])

df_prediction_path = os.path.join(os.path.pardir,"logs","current_and_future_predictions.pkl")
df_predict.to_pickle(df_prediction_path)
