# Backend

This is the repo that contains the backend of the application written in Python and Flask

## Install

In order to install you must

- Clone the repository using `git clone git@github.com:PlayTopDog/application_backend.git`
- Create a new project in firebase if you don't already have one
- In the config of firebase go to __Project Overview -> General__ and scroll to the bottom
- You will find a firebase config like the following:
```js
const firebaseConfig = {
  apiKey: "xxx",
  authDomain: "xxx",
  databaseURL: "xxx",
  projectId: "xxx",
  storageBucket: "xxx",
  messagingSenderId: "xxx",
  appId: "xxx",
  measurementId: "xxx"
};
```

- Transform this to JSON and save it to `fbconfig.json` like the following
```json
{
  "apiKey": "xxx",
  "authDomain": "xxx",
  "databaseURL": "xxx",
  "projectId": "xxx",
  "storageBucket": "xxx",
  "messagingSenderId": "xxx",
  "appId": "xxx",
  "measurementId": "xxx"
}
```
- Enable email and password sign in — Go to Authentication -> Sign-In-Method and enable sign in with email and password
- Export Admin SDK private key — Go to Project Overview -> Service Accounts -> Firebase Admin SDK, then select Python as the language and click generate new private key and your file will download. Do NOT share this file or upload it anywhere it allows total read and write access of your Firebase project. Save it somewhere in your computer with the name `fbAdminConfig.json`
- Create a `.env` file with this.
```
MAILGUN_DOMAIN = ""
MAILGUN_API_KEY = ""
MAILGUN_FROM_EMAIL = ""
MAILGUN_FROM_TITLE = ""
DATABASE_URI = ""
APP_SECRET_KEY = ""
JWT_SECRET_KEY = ""
APPLICATION_SETTINGS=default_config.py
AWS_ACCESS_KEY_ID=""
AWS_ACCESS_KEY_SECRET=""
AWS_BUCKET=""
EMAIL_USER=""
EMAIL_PASSWORD=""
EMAIL_SMTP_SERVER=""
EMAIL_SMTP_PORT=""
```
- Also create a `.env.test` file that's gonna be used for testing. It's recommended that the `DATABASE_URI` is different for testing
- Set up a mailgun account and with the Domain and API key
- Input your AWS app credentials in the env files

## Running the app

For the first run:
``` sh
make up-build
```

For regular executions
``` sh
make up
```

To test
``` sh
make test
```

For more commands, check the `Makefile`

