from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from user import User, LoginForm, CreateLoginForm
from werkzeug.debug import DebuggedApplication
from flask.ext.pymongo import PyMongo
app = Flask(__name__)
import qrviews


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
			return redirect(url_for('loggedIn', next=request.url))
		return "validate fail"
	return render_template('login.html', form=form)
			
	
@app.route("/loggedIn")
def loggedIn():
	if session['user_id']:
		uname = mongo.db.users.find_one({'username': session['user_id']})["username"]
		
		return u'<h1>logged in as %s</h1><a href="/logout">logout</a>' % uname
	else:
		return redirect(url_for('login', next=request.url))
	
@app.route("/logout")
def logout():
	session['user_id'] = None
	return redirect(url_for('login', next=request.url))
	
@app.route("/sessionLogin", methods=["GET", "POST"])
def sessionLogin():
	form = CreateLoginForm(request.form)
	if request.method == "GET":
		counter = mongo.db.counters.find_and_modify(query={'_id': 'username'}, update={ "$inc": { "seq": 1 } }, upsert=False, fullresponse=True)
		return render_template('sessionLogin.html', username=counter["seq"], form=form, session_id=1)
	if form.validate():
		session['user_id'] = form.user.get_id()
		return u'<h2>Annonyamous user created:</h2><h1>%s</h1><h2>Please screen shot your userid in case you are logged out</h2>' % session['user_id']
	return "validate fail"


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

@app.route("/adminLogin")
def adminLogin():
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

@app.route("/loginThankYou")
def loginThankYou():
    return render_template('loginThankYou.html')

@app.route("/wrongStation")
def wrongStation():
    return render_template('wrongStation.html')

@app.route("/404")
def error404():
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)#,use_debugger=True)