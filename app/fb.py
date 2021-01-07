"""Firebase configuration"""
import pyrebase
from firebase_admin import credentials
import firebase_admin
import json
import os

file_dir = os.path.dirname(__file__)
fb_admin_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
}

path_config = os.path.join(file_dir, "fbAdminConfig.json")

if os.path.isfile(path_config):
    print("fbAdminConfig.json: Using path config for firebase config")
    cred = credentials.Certificate(path_config)
else:
    print("fbAdminConfig.json: Using environment variables for config")
    cred = credentials.Certificate(fb_admin_config)


path_pyrebase_config = os.path.join(file_dir, "fbconfig.json")

firebase = firebase_admin.initialize_app(cred)
if os.path.isfile(path_pyrebase_config):
    print("fbconfig.json: Using path config for pyrebase config")
    pyrebase_config = json.load(open(path_pyrebase_config))  # Data source
else:
    print("fbconfig.json: Using environment variables for pyrebase config")
    pyrebase_config = {
        "apiKey": os.getenv("PYREBASE_API_KEY"),
        "authDomain": os.getenv("PYREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv("PYREBASE_DATABASE_URL"),
        "projectId": os.getenv("PYREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("PYREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("PYREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("PYREBASE_APP_ID"),
        "measurementId": os.getenv("PYREBASE_MEASUREMENT_ID"),
    }

pb = pyrebase.initialize_app(pyrebase_config)
