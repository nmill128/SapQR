from app import app
from flask import render_template, request, redirect, url_for, flash, session
import app as module

@app.route("/qr/station/<id>")
def loadStation(id=None):
	if id:
		stationEntry = module.mongo.db.stations.find_one({"station_id":id})
		print stationEntry
		return render_template('stationVideo.html')