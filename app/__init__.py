from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from user import User
from flask.ext.pymongo import PyMongo
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'sapQR'
mongo = PyMongo(app, config_prefix="MONGO")

@app.route("/")
def index():
    return render_template('index.html')
	
@app.route("/login")
def login():
	with app.app_context():
		return  mongo.db.users.find_one({'username': "1337"})['username']
	
@app.route("/sessionLogin")
def sessionLogin():
	
    return render_template('sessionLogin.html')
	
@app.route("/stationOverview")
def stationOverview():
    return render_template('stationOverview.html')
	
@app.route("/stationQuestion")
def stationQuestion():
    return render_template('stationQuestion.html') 
	
@app.route("/stationVideo")
def stationVideo():
    return render_template('stationVideo.html')
	
@app.route("/template")
def template():
    return render_template('template.html')

@app.route("/userLogin")
def userLogin():
    return render_template('login.html')

@app.route("/sessionList")
def sessionList():
    return render_template('sessionList.html')

@app.route("/sessionInfo")
def sessionInfo():
    return render_template('sessionInfo.html')

@app.route("/userInfo")
def userInfo():
    return render_template('userInfo.html')

@app.route("/stationInfo")
def stationInfo():
    return render_template('stationInfo.html')

if __name__ == "__main__":
    app.run(debug=True)