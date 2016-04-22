from app import app
from flask import render_template, request, redirect, url_for, flash, session
import app as module
import user
from user import CreateLoginForm

@app.route("/qr/station/<id>")
@user.login_required
def loadStation(id=None):
	stationEntry = module.mongo.db.stations.find_one({"station_id":id})
	if stationEntry:
		userEntry = module.mongo.db.users.find_one({"username":session["user_id"]})
		if userEntry["session_id"] == stationEntry["session_id"]:
			return render_template('stationVideo.html', id=id)
		return "sorry you are not allowed to view this page"
	return "404 station not found"
	
@app.route("/qr/sessionLogin/<id>", methods=["GET"])
def qrSessionLogin(id=None):
	form = CreateLoginForm(request.form)
	if not 'user_id' in session or session["user_id"] is None:
		counter = module.mongo.db.counters.find_and_modify(query={'_id': 'username'}, update={ "$inc": { "seq": 1 } }, upsert=False, fullresponse=True)
		return render_template('sessionLogin.html', username=counter["seq"], form=form, session_id=id)
	return redirect(url_for('loginThankYou', next=request.url))
	