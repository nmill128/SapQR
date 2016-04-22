import qrcode
from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from user import User, LoginForm, CreateLoginForm, login_required
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

@app.route("/stationOverview")
def stationOverview():
    return render_template('stationOverview.html')
	
@app.route("/stationQuestions/<id>")
@login_required
def stationQuestion(id=None):
	stationEntry = mongo.db.stations.find_one({"station_id":id})
	if stationEntry:
		userEntry = mongo.db.users.find_one({"username":session["user_id"]})
		if userEntry["session_id"] == stationEntry["session_id"]:
			return render_template('stationQuestion.html', questionsList=stationEntry["questionsList"])
		return "you do not have access"
	return "404"
	
@app.route("/stationVideo")
def stationVideo():
    return render_template('stationVideo.html')

@app.route("/vid")
def vid():
	return render_template('vid.html')
	
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


def makeQRCode(stationID):
    picture=mongo.db.stations.find_one({'id':stationID})['picture']
    if(picture not NONE):
        return picture
    link = mongo.db.stations.find_one({'id':stationID})['link']
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image()
    mongo.db.stations.update({'id':stationID},{$set:{"picture":img}})


@app.route("/wrongStation")
def wrongStation():
    return render_template('wrongStation.html')

@app.route("/404")
def error404():
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)#,use_debugger=True)
