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

if __name__ == "__main__":
    app.run(debug=True)