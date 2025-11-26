import base64

from flask import Flask,render_template,request,json,jsonify

from flask import Flask,render_template,request,json,jsonify
from ai_service.Crypto_Coin_Service import input_request
import numpy as np
app = Flask(__name__)
#** ADDITION COIN LIST
COIN_NAMES=["BTC","ETC","XRP"]
COIN_HAN= ["Bitcoin","Ethereum","Ripple"]
import os
COIN_PATH= os.path.join(os.path.dirname(__file__),"coin_config")
AI_PATH="ai_service/"

#utils
def crypto_coin_anal(coinname,timegap):
    #calling the model and return the result
   return input_request(coinname, timegap)
#route

@app.route("/") #main intro page
def root():
    return render_template("intro_index.html")
@app.route("/page/<pagename>")
def page_href(pagename):
    return render_template(f"{pagename}.html")
@app.route("/coin_name")
def out_coinname():
    coin_name_dict={"eng_name":COIN_NAMES,"han_name":COIN_HAN}
    return jsonify(coin_name_dict)
@app.route("/user_data",methods=["post"]) # expecting coin price page
def user_data():
    print("---------")
    user_datas= request.get_json()
    print(user_datas)
    coinname=user_datas["coinname"]
    timegap=int(user_datas["timegaps"])
    report= crypto_coin_anal(coinname,timegap)
    print(report)
    return jsonify(report)


#link coin verification model and response


app.run("127.0.0.1",4321,True)