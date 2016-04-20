from app import app
from flask import render_template, request, redirect, url_for, flash, session
import app as module
import user

@app.route("/qr/station/<id>")
@user.login_required
def loadStation(id=None):
	stationEntry = module.mongo.db.stations.find_one({"station_id":id})
	if stationEntry:
		userEntry = module.mongo.db.users.find_one({"username":session["user_id"]})
		if userEntry["session_id"] == stationEntry["session_id"]:
			return render_template('stationVideo.html')
		return "sorry you are not allowed to view this page"
	return "404 station not found"