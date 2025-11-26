#!/usr/bin/env python
# coding: utf-8


import tensorflow as tf
import numpy as np
import matplotlib.pyplot
import requests
from ai_service.Crypto_Coin_Train import get_data,extract_data
import pickle
TIME_STEP=60
CURRT=0 #THE CURRENT INDEX
HIGH=1 #THE HIGHEST PRICE INDEX
LOW=2 #THE LOWEST PRICE INDEX
import os
COIN_PATH= os.path.join(os.path.dirname(__file__),"coin_config")



#  Data Fetch Function
#  Prediction data creation
robust_scaler=None
def create_predict(x_pred):
    print(x_pred.shape)#(200, 3)
    x_pred = x_pred[::-1]# Sort by Timestamp
    return x_pred[-TIME_STEP:,:]# Extract and Return Last 8 Records
    
#  Load Model
def load_rnnmodel(tpath):
    return tf.keras.models.load_model(tpath, compile=True)

#  Date-based Prediction Output Function
def y_predict(model,x_pred,timegap,coinname="BTC"):
    global robust_scaler
    data_array=[]
    if not robust_scaler:
        with open(f"{COIN_PATH}/{coinname.lower()}_robust_scaler","rb") as fp:
            robust_scaler=pickle.load(fp)
    for i in range(timegap):
        y_pred= model.predict(x_pred)
        y_true= robust_scaler.inverse_transform(y_pred)
        data_array.append(y_true[0].tolist())
        x_pred= x_pred[:,:1:,:]
        x_pred=x_pred[:,1:,:]
        print(x_pred.shape)#(1, 59, 3)
        print(y_pred.shape)#(1,3)
        y_pred = y_pred.reshape(1,1,3)
        print(y_pred.shape)
        x_pred = np.concatenate((x_pred,y_pred),axis=1)
        print("data verification:",y_pred[0][0][0]==x_pred[0][-1][0])
    return data_array    
 
def convert_price(price_data,coinname):
    global robust_scaler
    if not robust_scaler:
        with open(f"{COIN_PATH}/{coinname}_robust_scaler","rb") as fp:
                robust_scaler = pickle.load(fp)
    return robust_scaler.inverse_transform(price_data)
#  Prediction Price Restoration Function



if __name__=="__main__":
   print("Execution Time Testing")
   coin_name="BTC"
   raw_data = get_data(f"https://api.bithumb.com/v1/candles/days?market=KRW-{coin_name}&count=200")
   # print("currt price ",raw_data[0]["trade_price"])
   # print("highest price ",raw_data[0]["high_price"])
   # print("lowest price ",raw_data[0]["low_price"])
  
   preproc_data = extract_data(raw_data,False)
   # print(convert_price(preproc_data)[0])
   # print("currt price ",currt_1[0])
   # print("highest price ",currt_1[1])
   # print("lowest price ",currt_1[2])
    
   x_pred = create_predict(preproc_data)
   # currt_2=convert_price(x_pred)[-1] 
   # print("currt price ",currt_2[0])
   # print("highest price ",currt_2[1])
   # print("lowest price ",currt_2[2])
    
   print(len(x_pred))
   print(x_pred.shape)
   print(x_pred[0]) 
   lstm_model = load_rnnmodel(f"{COIN_PATH}/lstm_model.keras")
   print(lstm_model) 
   y_predarr= y_predict(lstm_model,np.array([x_pred]),7)
   currt_price=convert_price(x_pred)
   print("today currnt price:",currt_price[-1][0])
   print("today high price:",currt_price[-1][1])
   print("today low price:",currt_price[-1][2])
   day_cnt=1
   for curp,highp,lowp in y_predarr:
       print(f" day {day_cnt} : standard price:{curp}, high price{highp}, low price{lowp}")
       day_cnt+=1





