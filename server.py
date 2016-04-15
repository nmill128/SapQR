#New python server
import os
import json
import bson.json_util
import flask
from flask import Flask, request, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
import sendgrid
import urllib, urllib2

app = Flask(__name__, static_url_path='/static')


#Ned the mongodb connection string
#connection = MongoClient('mongodb://admin:admin@ds055110.mongolab.com:55110/IbmCloud_uaackvrv_430gkc3k')
#collection = connection.IbmCloud_uaackvrv_430gkc3k.testHouse
#names = connection.IbmCloud_uaackvrv_430gkc3k.testNames
#timers = connection.IbmCloud_uaackvrv_430gkc3k.timers


@app.route('/')
def root():
	return "Welcome to Sap QR"
