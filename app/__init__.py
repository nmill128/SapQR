from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from user import User, LoginForm, CreateLoginForm, login_required, facilitator_required
from werkzeug.debug import DebuggedApplication
from flask.ext.pymongo import PyMongo
app = Flask(__name__)
import qrviews
import json


app.wsgi_app = DebuggedApplication(app.wsgi_app, True)


app.secret_key = "claiisbestlai"
app.config['MONGO_DBNAME'] = 'sapQR'
app.config['DEBUG'] = True
mongo = PyMongo(app, config_prefix="MONGO")


@app.route("/")
def index():
    return render_template('index.html')
	
@app.route("/login", methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if request.method == "POST":
		if form.validate():
			session['user_id'] = form.user.get_id()
			userEntry = mongo.db.users.find_one({'username':session['user_id']})
			if userEntry['facilitator']:
				return redirect(url_for('sessionList', next=request.url))
			return redirect(url_for('loginThankYou', next=request.url))
		return "validate fail"
	return render_template('login.html', form=form)

#Get for this route in qr views	
@app.route("/sessionLogin", methods=["POST"])
def sessionLogin(id=None):
	form = CreateLoginForm(request.form)
	if form.validate():
		session['user_id'] = form.user.get_id()
		return redirect(url_for('loginThankYou', next=request.url))
	return "validate fail"
	
@app.route("/loggedIn")
@login_required
def loggedIn():
	uEntry = mongo.db.users.find_one({'username': session['user_id']})
	if uEntry:
		return u'<h1>logged in as %s</h1><a href="/logout">logout</a>' % uEntry["username"]
	return redirect(url_for('login', next=request.url))
	
@app.route("/logout") 
def logout():
	session['user_id'] = None
	return redirect(url_for('login', next=request.url))
	

@app.route("/loginThankYou")
@login_required
def loginThankYou():
    return render_template('loginThankYou.html', userid=session["user_id"])

@app.route("/stationOverview/<id>")
def stationOverview(id=None):
	stationEntry = mongo.db.stations.find_one({"station_id":id})
	stations = list(mongo.db.stations.find({"session_id":stationEntry['session_id']}))
	completedStations = list(mongo.db.stationResponses.find({"username":session['user_id']}))
	listCompleted = []
	count = 0
	while(count < len(stations)):
		listCompleted.append(False)
		for completed in completedStations:
			if completed['station_id'] == stations[count]['station_id']:
				listCompleted[count] = True
		count+=1
	return render_template('stationOverview.html', stations=stations, listCompleted=listCompleted)
	
@app.route("/stationQuestion/<id>", methods=["GET", "POST"])
@login_required
def stationQuestion(id=None):
	stationEntry = mongo.db.stations.find_one({"station_id":id})
	if stationEntry:
		userEntry = mongo.db.users.find_one({"username":session["user_id"]})
		if userEntry["session_id"] == stationEntry["session_id"]:
			if request.method == "POST":
				mongo.db.stationResponses.update({'username':session['user_id'], 'station_id':id}, {'$set': {'question_responses':request.form}})
				mongo.db.stations.update({'station_id':id}, {'$inc':{'number_completed': 1}})
				return redirect(url_for('stationOverview', next=request.url, id=id))
			return render_template('stationQuestion.html', questionsList=stationEntry["questionsList"], id=id, name=stationEntry['name'])
		return redirect(url_for('/wrongStation', next=request.url))
	return redirect(url_for('/404', next=request.url))
	
@app.route("/sliderData",  methods=["GET"])
def sliderData():
	stationResponse = mongo.db.stationResponses.find_one({'username':session['user_id'], 'station_id':request.args['station_id'] })
	if(stationResponse is None):
		momments = [{'time':request.args['time'], 'comfort':request.args['comfort']}]
		mongo.db.stationResponses.insert({'username':session['user_id'], 'station_id':request.args['station_id'], 'momments':momments})
		return "first"
	momments = stationResponse['momments']
	momments.append({'time':request.args['time'], 'comfort':request.args['comfort']})
	mongo.db.stationResponses.update({'username':session['user_id'], 'station_id':request.args['station_id'] },{'$set': {'momments': momments}})
	return json.dumps(momments)
	
	
@app.route("/template")
def template():
    return render_template('template.html')

@app.route("/adminLogin")
def adminLogin():
    return render_template('login.html')

@app.route("/sessionList")
@facilitator_required
def sessionList():
	userEntry = mongo.db.users.find_one({'username':session['user_id']})
	sessions = list(mongo.db.sessions.find({'owner':session['user_id']}))
	return render_template('sessionList.html', sessions=sessions)

@app.route("/sessionInfo/<id>")
@facilitator_required
def sessionInfo(id=None):
	sessionEntry = mongo.db.sessions.find_one({'session_id':id})
	if sessionEntry:
		usersList = list(mongo.db.users.find({'session_id':id}))
		stationsList = list(mongo.db.stations.find({'session_id':id}))
		return render_template('sessionInfo.html', users=usersList, stations=stationsList)
	return redirect(url_for('404', next=request.url))

@app.route("/userInfo/<username>")
@facilitator_required
def userInfo(username=None):
	userEntry = mongo.db.users.find_one({'username':username})
	stations = list(mongo.db.stations.find({"session_id":userEntry['session_id']}))
	completedStations = list(mongo.db.stationResponses.find({"username":username}))
	listCompleted = []
	count = 0
	while(count < len(stations)):
		listCompleted.append(False)
		for completed in completedStations:
			if completed['station_id'] == stations[count]['station_id']:
				listCompleted[count] = True
		count+=1
	return render_template('userInfo.html', user=userEntry, stations=stations, listCompleted=listCompleted)

@app.route("/stationInfo/<id>") 
def stationInfo(id=None):
	stationEntry = mongo.db.stations.find_one({'station_id':id})
	stationResponses = list(mongo.db.stationResponses.find({'station_id':id}))
	gender = {'Male':0, 'Female':0, 'Other':0, 'Choose not to Identify':0}
	for stationResponse in stationResponses:
		userEntry = mongo.db.users.find_one({'username':stationResponse['username']})
		gender[userEntry['gender']] += 1
	return render_template('stationInfo.html', gender=gender, station=stationEntry)

@app.route("/wrongStation")
def wrongStation():
    return render_template('wrongStation.html')

@app.route("/404")
def error404():
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)