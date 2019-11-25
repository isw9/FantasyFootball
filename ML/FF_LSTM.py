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
from keras.models import model_from_json
from keras.activations import softmax
from keras.optimizers import SGD
from DataBuilder import DataBuilder

CH = "[FF_LSTM] "
path = os.path.abspath(__file__)

def save_model(model, name):
    model_json = model.to_json()
    with open(name + ".json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights(name+".h5")
    print(CH + "Model Saved!")

def load_model(model_name):
    json_file = open(model_name+".json", 'r')
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    model.load_weights(model_name+".h5")
    print(CH + "Loaded model ~" + model_name + "~")
    return model

if __name__ == "__main__":
    model = load_model("testModel")

    print(CH + "Connecting to database. . .")
    u = sys.argv[1]; p = sys.argv[2]; db = sys.argv[3]; h = sys.argv[4]
    print(CH + " u: " + u)
    print(CH + " p: " + p)
    print(CH + "db: " + db)
    print(CH + " h: " + h)

    # DB Setup
    dB = DataBuilder(u, p, db, h)
    dB.db_get_minmax()

    Test = dB.get_player_stats_Latest(666, 11).drop([0])
    Test = dB.df_wiggle_norm(Test, 0.05)
    Test = Test.drop(columns=["gameID"]).values.reshape(1, 10, 17)
    predict = model.predict(Test)
    print(predict)
    predict = dB.denormalize_prediction(predict, 0.05)
    print(predict)

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








