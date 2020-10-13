"""Firebase configuration"""
import pyrebase
from firebase_admin import credentials
import firebase_admin
import json

cred = credentials.Certificate("fbAdminConfig.json")

# This is needed so tests run correctly
# TODO check if this can be done without using this comparison
if len(firebase_admin._apps) == 0:
    firebase = firebase_admin.initialize_app(cred)
    pb = pyrebase.initialize_app(json.load(open("fbconfig.json")))  # Data source
