from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from user import User, LoginForm, CreateLoginForm, login_required, facilitator_required
from werkzeug.debug import DebuggedApplication
from werkzeug.security import check_password_hash, generate_password_hash
from flask.ext.pymongo import PyMongo
import datetime
app = Flask(__name__)
import qrviews
import json
import os

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
		momments = [{'time':request.args['time'], 'comfort':request.args['comfort'], 'username':session['user_id']}]
		mongo.db.stationResponses.insert({'username':session['user_id'], 'station_id':request.args['station_id'], 'momments':momments})
		return "first"
	momments = stationResponse['momments']
	momments.append({'time':request.args['time'], 'comfort':request.args['comfort'], 'username':session['user_id']})
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
		return render_template('sessionInfo.html', users=usersList, stations=stationsList, id=id)
	return redirect(url_for('error404', next=request.url))

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
	questions = []
	qIndex = 0
	questionsList = stationEntry['questionsList']
	while qIndex < len(questionsList):
		question = {'question':questionsList[qIndex]['question'], 'answers': []}
		for answer in questionsList[qIndex]['answers']:
			question['answers'].append([answer, 0])
		questions.append(question)
		qIndex+= 1
	momments_list = []
	average_momments = [[0,0]]
	usersComfort = {}
	for stationResponse in stationResponses:
		usersComfort[stationResponse['username']] = 0
		momments_list += stationResponse['momments']
		userEntry = mongo.db.users.find_one({'username':stationResponse['username']})
		gender[userEntry['gender']] += 1
		qIndex = 0
		if 'question_responses' in stationResponse:
			while qIndex < len(questionsList):
				answer_response = stationResponse['question_responses']['q' + str(qIndex + 1)]
				for possible_answer in questions[qIndex]['answers']:
					if possible_answer[0] == answer_response:
						possible_answer[1] += 1
						break;
				qIndex += 1
	momments_list = sorted(momments_list, key=mommentKey)
	for momment in momments_list:
		usersComfort[momment['username']] = float(momment['comfort'])
		comfort_total = 0
		for key in usersComfort:
			comfort_total += usersComfort[key]
		average_momments.append([float(momment['time']), comfort_total/len(usersComfort)])
	return render_template('stationInfo.html', gender=gender, station=stationEntry, questions=questions, average_momments=average_momments)

def mommentKey(momment):
		return float(momment['time'])
		
@app.route("/userStationInfo/<username>/<id>")
@facilitator_required
def userStationInfo(username=None, id=None):
	stationEntry = mongo.db.stations.find_one({'station_id':id})
	userEntry = mongo.db.users.find_one({'username':username})
	stationResponse = mongo.db.stationResponses.find_one({'username':username, 'station_id':id})
	momments = []
	for momment in stationResponse['momments']:
		momments.append([float(momment['time']), float(momment['comfort'])])
	momments = sorted(momments, key=mommentArrayKey) 
	return render_template('userStationInfo.html', momments=momments, station = stationEntry, user=userEntry, questions=stationEntry['questionsList'], answers=stationResponse['question_responses'])
	
def mommentArrayKey(momment):
	return momment[0]
@app.route("/wrongStation")
def wrongStation():
    return render_template('wrongStation.html')

@app.route("/createStation/<session_id>")
@facilitator_required
def createStation(session_id=None, message=""):
	vidNames = os.listdir("/home/ec2-user/SapQR/static/vid") 
	choosenSession = mongo.db.sessions.find({'session_id':session_id})
	sessions = list(mongo.db.sessions.find({'owner':session['user_id']}))
	return render_template('createStation.html', message=message, vidNames=vidNames, sessions = sessions, choosenSession=choosenSession)
	
@app.route("/createStation", methods=["POST"])
@facilitator_required
def createStationPost():
	message = ""
	if request.form['session_id'] and (not request.form['name'] == "") and request.form['video'] and request.form['questionsList']:
		station_id = mongo.db.counters.find_one({'_id':'station_id'})['seq']
		mongo.db.counters.update({'_id':'station_id'}, {'$inc':{'seq':1}})
		doc = { 'station_id':str(station_id),
				'session_id':request.form['session_id'],
				'name':request.form['name'],
				'video':request.form['video'],
				'questionsList':json.loads(request.form['questionsList']),
				'number_completed':0,
				'Link':'sapqr.tk/qr/station/' + str(station_id)}
		mongo.db.stations.insert(doc)
		return ""
	message = "missing some fields"
	return message, 400
	
@app.route("/createSession", methods=['GET', 'POST'])
@facilitator_required
def createSession():
	message = ""
	if request.method == 'POST':
		if request.form['name'] and request.form['session_date']:
			session_id = mongo.db.counters.find_one({'_id':'session_id'})['seq']
			mongo.db.counters.update({'_id':'session_id'}, {'$inc': {'seq':1}})
			date = datetime.datetime.strptime(request.form['session_date'], '%m/%d/%Y')
			doc = {'session_id':str(session_id),
					'name': request.form['name'],
					'session_date': date,
					'owner': session['user_id']}
			mongo.db.sessions.insert(doc)
			return redirect(url_for('sessionList', next=request.url))
		else:
			message = "missing some fields"
	return render_template('createSession.html', message = message)
	
@app.route("/404")
def error404():
    return render_template('404.html')
	
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
	
@app.route("/registerFacilitator", methods=['GET', 'POST'])
def registerFacilitator():
	message = ""
	if request.method == 'POST':
		if request.form['code'] and  request.form['username'] and  request.form['password1'] and  request.form['password2'] and  request.form['first'] and  request.form['last']:
			if request.form['code'] == 'NEW':
				oldUser = mongo.db.users.find_one({'username':request.form['username']})
				if oldUser:		
					message = "username already taken, please choose another username"
				else:
					if not request.form['password1'] == request.form['password2']:
						message = "password mismatch"
					else:
						doc = { 'username':request.form['username'],
								'password':generate_password_hash(request.form['password1']),
								'facilitator': True,
								'first_name':request.form['first'],
								'last_name':request.form['last']}
						mongo.db.users.insert(doc)
						newUser = mongo.db.users.find_one({'username':request.form['username']})
						if newUser:
							session['user_id'] = request.form['username']
							return redirect(url_for('sessionList',  next=request.url))
						else:
							message = "persistence error"
			else:
				message = "Incorrect create new code"
		else:
			message = "missing some fields"
	return render_template('registerFacilitator.html', message=message)

if __name__ == "__main__":
    app.run(debug=True)