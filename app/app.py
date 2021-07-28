from datetime import timedelta

from flask import Flask, session

app = Flask(__name__)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=180)



if __name__ == '__main__':

    app.run()
