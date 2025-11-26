import tensorflow as tf
import numpy as np
import sklearn
import matplotlib.pyplot as plt
import requests
import random
import pickle
import os
from tensorflow.keras import Input, Sequential
from tensorflow.keras.layers import Dense,LSTM, Dropout,BatchNormalization
random.seed(111) # to fix learning
np.random.seed(111)
tf.random.set_seed(111)
#0. Environment Variable
TIME_STEP=60
CURRT=0 #THE CURRENT INDEX
HIGH=1 #THE HIGHEST PRICE INDEX
LOW=2 #THE LOWEST PRICE INDEX
import os
COIN_PATH= os.path.join(os.path.dirname(__file__),"coin_config")





#Data Collection
def get_data(url):
    raw_data = requests.get(url).json()
    return raw_data





def extract_data(raw_data,new_data=True,coin_name="btc"):
   #indeed data extraction(time_stamp, trade_price, high_price, low_price),Run the quartile method function
    data_sets=[]
    for i in range(len(raw_data)):
        unit_arr = []
        unit_arr.append(raw_data[i]["trade_price"])
        unit_arr.append(raw_data[i]["high_price"])
        unit_arr.append(raw_data[i]["low_price"])
        data_sets.append(unit_arr)
    data_sets= np.array(data_sets,dtype=np.float64) #(200,3)
    print(data_sets.shape)
    print(data_sets.max())
    print(data_sets.min())
    #A preprocessing technique suitable for data without outliers.
    robust_scaler=None
    if new_data:
        robust_scaler= sklearn.preprocessing.RobustScaler() #tFirst-stage quartile preprocessing,RobustScaler normalization
        data_sets= robust_scaler.fit_transform(data_sets)
        if not os.path.exists(COIN_PATH):
         os.makedirs(COIN_PATH)   
        with open(f"{COIN_PATH}/{coin_name.lower()}_robust_scaler","wb") as fp:
            pickle.dump(robust_scaler,fp)
    else : 
       with open(f"{COIN_PATH}/{coin_name.lower()}_robust_scaler","rb") as fp:
           robust_scaler=pickle.load(fp)
       data_sets= robust_scaler.transform(data_sets)
    # print(data_sets.max())
    # print(data_sets.min())
    # print(data_sets.shape)
    return data_sets
def rnn_data_create(preproc_data):
    preproc_data = preproc_data[::-1]
    #(200, 4)
    x_data=[]
    y_data=[]
    for i in range(len(preproc_data)-TIME_STEP):
        x_data.append(preproc_data[i:i+TIME_STEP])
        y_data.append(preproc_data[i+TIME_STEP])
    # Put the recent data in the end
    x_data=np.array(x_data)
    x_data= x_data[:-1]
    y_data=np.array(y_data)[:-1]
    print("check",x_data.shape)
    print("check",y_data.shape)
    return x_data,y_data
def struct_model():
    model= Sequential()
    model.add(Input((TIME_STEP,3)))
    cb= tf.keras.callbacks.EarlyStopping( #early stopping
        monitor='val_loss',
        patience=50, 
        verbose=1,     
        restore_best_weights=True,
        #start_from_epoch=400
)
    lstm_1 = tf.keras.layers.LSTM(
            64,
            activation='tanh',
            recurrent_activation='sigmoid',
            return_sequences=True)
    lstm_2 = tf.keras.layers.LSTM(
            32,
            activation='tanh',
            recurrent_activation='sigmoid',
            return_sequences=True)
    lstm_3 = tf.keras.layers.LSTM(
            16,
            activation='tanh',
            recurrent_activation='sigmoid',
            return_sequences=False)
    model.add(lstm_1)
    model.add(lstm_2)
    model.add(lstm_3)
    model.add(BatchNormalization())
    model.add(Dense(256,activation="relu"))
    model.add(Dropout(0.4))
    model.add(Dense(64,activation="relu"))
    model.add(Dense(16,activation="relu"))
    model.add(Dense(3,activation="linear"))
    model.compile(loss="mse",optimizer="adam",metrics=["mae"])
    return model
def sample_weight(length): #weight in order to time
    return np.linspace(0.0001,1,length)
def train_fit(tmodel,x_train,y_train,epoch,time_weight):
        cb= tf.keras.callbacks.EarlyStopping( #early stopping
        monitor='val_loss',
        patience=50, 
        verbose=1,     
        restore_best_weights=True,
        #start_from_epoch=400
    )
        return tmodel.fit(x_train,y_train,validation_data=(x_train,y_train),epochs=epoch,
               batch_size=len(x_train)//10,sample_weight=time_weight,callbacks=[cb],verbose=0)
def result_graph(fit_history,coin_name):
    history= fit_history.history
    plt.subplot(1,2,1)
    plt.plot(history["val_loss"],label="valid_loss")
    plt.title("MSE")
    plt.subplot(1,2,2)
    plt.plot(history["mae"],label="train_mae")
    plt.plot(history["val_mae"],label="valid_mae")
    plt.title("MAE")
    if not os.path.exists(f"{COIN_PATH}/static"):
        os.makedirs(f"{COIN_PATH}/static/chart")
    plt.savefig(r"{}/static/chart/{}_mse_mae.png".format(COIN_PATH,coin_name.lower()))
    plt.close()
def confirm_pred(y_true,y_pred,coin_name):
    if y_true.shape==y_pred.shape:
        plt.plot(y_true,y_true,label="Y_TRUE")
        plt.scatter(y_true,y_pred,s=2,color="red",label="Y_PRED")
        if not os.path.exists(f"{COIN_PATH}/static"):
           os.makedirs(f"{COIN_PATH}/static/chart")
        plt.savefig(r"{}/static/chart/{}_scatter.png".format(COIN_PATH,coin_name.lower()))
        plt.close()





if  __name__=="__main__":
    coin_names=["BTC","ETH","XRP"]
    for coin_name in coin_names:        
        raw_data = get_data(f"https://api.bithumb.com/v1/candles/days?market=KRW-{coin_name}&count=200")
        # print("Data Quantity:",len(raw_data))
        # print("Data Sample:", raw_data[0])
        # print("Data Key:", raw_data[0].keys())
        preproc_data= extract_data(raw_data,coin_name=coin_name)
        x_train,y_train=rnn_data_create(preproc_data)
        #Data validation
        # print(y_train[0]==x_train[1][-1])
        # print(y_train[1]==x_train[2][-1])
        #Data shape validation
        # print(type(x_train[0][0][0]))
        # print(type(x_train[0][0][1]))
        # print(type(x_train[0][0][2]))
        # print(type(y_train[0][0]))
        #Data Verification
        # print((x_train[0][0][0]))
        # print((x_train[0][0][1]))
        # print((x_train[0][0][2]))
        # print((y_train[0][0]))
        model = struct_model()
        #Model running verification
        # res= model(x_train)
        # print(res.shape)
        time_weight= sample_weight(len(x_train))
        # print(x_train.shape)
        # print(y_train.shape)
        # print(len(time_weight))
        print(coin_name+" On Training........")
        fit_history = train_fit(model,x_train,y_train,500,time_weight)
        result_graph(fit_history,coin_name)
        y_pred = model.predict(x_train)
        # print(y_train.shape)
        # print(y_pred.shape)
        confirm_pred(y_train,y_pred,coin_name)
      
        #Error rate calculation
        # y_pred,y_train
        print(y_pred.shape)
        print(y_train.shape)
        #current price error rate
        y_gap= y_train-y_pred
        print(y_gap.shape)
        #Absolute value transformation
        y_abs_gap=np.absolute(y_gap)
        print((y_abs_gap<0).sum())
        y_mean= np.mean(y_abs_gap,axis=0)
        print(y_mean.shape)
        print(f"current price error rate:{y_mean[0]:.2%}%")
        print(f"high price error rate:{y_mean[1]:.2%}%")
        print(f"low price error rate:{y_mean[2]:.2%}%")
        err_dict= {"currt":y_mean[0],"high":y_mean[1],"low":y_mean[2]}
        #Model saving
        print(model)
        with open(r"./coin_config/{}err_rate".format(coin_name.lower()),"wb") as fp:
             pickle.dump(err_dict,fp)
        model.save(r"./coin_config/{}_lstm_model.keras".format(coin_name.lower()))









