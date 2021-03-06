"""Firebase configuration"""
import pyrebase
from firebase_admin import credentials
import firebase_admin
import json
import os

file_dir = os.path.dirname(__file__)
cred = credentials.Certificate(os.path.join(file_dir, "fbAdminConfig.json"))

firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(
    json.load(open(os.path.join(file_dir, "fbconfig.json")))
)  # Data source
