import base64

from flask import Flask,render_template,request,json,jsonify
app = Flask(__name__)
#adderess routing
@app.route("/")
def root_connect():
    return render_template("index.html")
@app.route("/myinfo",methods=["post"])
def myinformation():
    myname=(request.form["myname"])
    age=(request.form["age"])
    return render_template("join.html",myname=myname,age=age)
# sending the original file using base 64 encoding
@app.route("/getimg/<imgname>")
def getimage(imgname="snow_fox.jpg"):
    with open(f"static/img/{imgname}","rb") as fp:
       img_byte= fp.read()
       # the process of read the image as byte then askey encoding and sending
       encoded= base64.b64encode(img_byte).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

@app.route("/aaa")
def aaa():
    return "You have been connected to aaa query string"
#how the receive data with address
@app.route("/bbb/<name>",methods=["get"])
@app.route("/ccc/<name>",methods=["get"])
def get_param(name):
    print("sent data to bbb",name)
    return f"{name}, Welcome"

#how to receive data with query string
@app.route("/fff")
def get_querystring():
    name= (request.args.get("name"))
    age= (request.args.get("age"))
    return f"You are {name} and {age} yrs old."

#how to receive post data
@app.route("/jtest")
def jsondata_test():
    return render_template("jtest.html")
@app.route("/jtest/jdata", methods=["post"])
def get_jdata():
    print("json approved")
    jdict= (request.get_json())

    return jsonify(jdict)



app.run("127.0.0.1",4321,True)