import prediction_pipeline as pp
import pandas as pd
import dill as pickle

stat = 'PTS'

def makeModel(df, stat='PTS'):
    model = pp.GroupbyEstimator('POSITION', pp.stat_pipeline).fit(df, df[stat])

    with open(f".\\logs\\models\\model_{stat}.pkl", 'wb') as file:
        pickle.dump(model, file)
    return model

df = pd.read_pickle("./logs/current_and_future_logs.pkl")

#get only past data for training model
df_past = df[df["FUTURE_GAME"]==0]

#list of stats to model
stats = ["PTS", "REB", "AST", "FG3M", "BLK", "STL"]

#iterate over stats to model
for stat in stats:
    print(f"Modeling {stat}...")
    #make trained model using only past games
    model = makeModel(df_past, stat)

    #use model to predict all games, including past and future
    prediction = model.predict(df)

    #pickle prediction
    prediction.to_pickle(f"./logs/predictions/predictions_{stat}.pkl")