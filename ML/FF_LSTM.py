import sys
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import importlib
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import TimeDistributed
from keras.models import model_from_json
from keras.activations import softmax
from keras.optimizers import SGD
from keras.optimizers import rmsprop
from keras.optimizers import adam
from DataBuilder import DataBuilder

CH = "[FF_LSTM] "
path = os.path.abspath(__file__)


def save_model(model, name):
    model_json = model.to_json()
    with open(name + ".json", "w") as json_file:
        json_file.write("Models/"+model_json)
    model.save_weights("Models/"+name+".h5")
    print(CH + "Model Saved!")


def load_model(model_name):
    json_file = open("Models/"+model_name+".json", 'r')
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    model.load_weights("Models/"+model_name+".h5")
    print(CH + "Loaded model ~" + model_name + "~")
    return model


def train_model(dB, name):
    ban = []
    model = Sequential()
    model.add(LSTM(50, input_shape=(10, 15), return_sequences=True))
    model.add(Dropout(0.1))
    model.add(LSTM(50, input_shape=(10, 15), return_sequences=True))
    model.add(Dropout(0.1))
    model.add(LSTM(50, input_shape=(10, 15), return_sequences=True))
    model.add(Dropout(0.1))
    model.add(LSTM(50, input_shape=(10, 15), return_sequences=False))
    model.add(Dropout(0.1))
    model.add(Dense(units=13, activation="softmax"))
    model.compile(loss='mse', optimizer="rmsprop", metrics=['accuracy'])

    pIDrange = range(517, 1999)

    for player in pIDrange:
        try:
            if not player in ban:
                print("! " + str(player) + " !")
                df = dB.get_player_stats(int(player))
                # df = dB.df_add_0Weeks(df)
                df = dB.df_wiggle_norm(df, 0.05)
                trainX, trainY, testX, testY = dB.build_series_set(df, 10, .7, slide=True)
                history = model.fit(trainX, trainY, epochs=50, validation_data=(testX, testY), verbose=2, shuffle=False)
        except:
            ban.append(player)
            print("FAIL")
            #print(player)
            #print(ban)

    plt.plot(history.history['accuracy'], label='acc')
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_accuracy'], label='val_acc')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.legend()
    plt.savefig("Plots/"+name+"_log.png")
    plt.close()
    return model


def influence_model(model, playerID, wiggle_norm):

    model.compile(loss='mse', optimizer="rmsprop", metrics=['accuracy'])
    for i in range(0, 20):
        train_df = dB.get_player_stats(playerID)
        train_df = dB.df_wiggle_norm(train_df, wiggle_norm)
        test_df = dB.get_player_stats_Latest(666, 11)
        trainX, trainY, testX, testY = dB.build_series_set(train_df, 10, .7, slide=True)
        model.fit(trainX, trainY, epochs=50, validation_data=(testX, testY), verbose=0, shuffle=False)
        predict_and_compare(model, test_df, wiggle_norm)


def predict_and_compare(model, input_df, wiggle_norm):
    truth = input_df.iloc[10:].drop(columns=["gameID", "season", "weekNumber", "opponentTeamID", "ageDuringGame"])
    data = dB.df_wiggle_norm(input_df.iloc[0:10], 0.05).drop(columns=["gameID", "season", "weekNumber"]).iloc[0:10].values.reshape(1, 10, 15)

    predict = model.predict(data)
    predict = dB.denormalize_prediction(predict, wiggle_norm)

    print("~ Prediction: ")
    print(predict)
    print("")
    print("~ Truth")
    print(truth)


def predict_next(model, input_df, wiggle_norm):
    data = dB.df_wiggle_norm(input_df, 0.05).drop(columns=["gameID", "season", "weekNumber"]).values.reshape(1, 10, 15)

    predict = model.predict(data)
    predict = dB.denormalize_prediction(predict, wiggle_norm)

    return predict

def predict_next_week(playerID, c_week, season, model, dB, wiggle_norm):
    df = dB.get_Xweeks_before(playerID, 10, season, c_week)
    return predict_next(model, df, wiggle_norm)



if __name__ == "__main__":
    # DB setup:
    print(CH + "Connecting to database. . .")
    u = sys.argv[1]; p = sys.argv[2]; db = sys.argv[3]; h = sys.argv[4]
    print(CH + " u: " + u)
    print(CH + " p: " + p)
    print(CH + "db: " + db)
    print(CH + " h: " + h)

    """
    How to predict a player's next score from week X season Y to week X+1
    need to import DataBuilder.py and FF_LSTM.py
    """
    # Create DataBuilder:
    dB = DataBuilder(u, p, db, h)
    # Get MinMax (necessary for normalization, do it once for a DB object)
    dB.db_get_minmax()
    # Load model by name
    model = load_model("3by50")
    # set wiggle %
    w_norm = 0.05
    # Predict the week after week 4, 2018 for playerID = 666
    prediction = predict_next_week(666, 4, 2018, model, dB, w_norm)
    print(prediction)


    #name = "4by50_full"
    #model = train_model(dB, name)

    #model = load_model("testModel")
    #influence_model(model, 666, 0.05)

    #model = train_model(dB)
    #test_df = dB.get_player_stats_Latest(666, 11)
    #predict_and_compare(model, test_df, 0.05)


    #save_model(model, name)


    #save_model(model, "testModel2")



    """
    top_players = ["600", "547", "537", "521", "559", "595", "561", "574", "568", "585"]
    ban = []
    model = Sequential()
    model.add(LSTM(50, input_shape=(10, 17), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=13, activation="softmax"))
    model.compile(loss='mean_squared_error', optimizer=SGD(lr=0.001), metrics=['accuracy'])

    pIDrange = range(517, 1999)
    #pIDrange = range(517, 550)

    for player in pIDrange:
        try:
            if not player in ban:
                print("! " + str(player) + " !")
                df = dB.get_player_stats(int(player))
                #df = dB.df_add_0Weeks(df)
                df = dB.df_wiggle_norm(df, 0.05)
                trainX, trainY, testX, testY = dB.build_series_set(df, 10, .7, slide=True)
                history = model.fit(trainX, trainY, epochs=50, validation_data=(testX, testY), verbose=2, shuffle=False)
        except:
            ban.append(player)
            print("FAIL")
            print(player)
            print(ban)

    plt.plot(history.history['accuracy'], label='acc')
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_accuracy'], label='val_acc')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.legend()
    plt.savefig("Plots/model_log.png")
    plt.close()

    Test = dB.get_player_stats_Latest(666, 11).drop([0])
    Test = dB.df_wiggle_norm(Test, 0.05)
    Test = Test.drop(columns=["gameID"]).values.reshape(1, 10, 17)
    predict = model.predict(Test)
    print(predict)
    predict = dB.denormalize_prediction(predict, 0.05)
    print(predict)

    save_model(model, "testModel")
    """








