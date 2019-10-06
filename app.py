from flask import Flask
from flask_login import LoginManager


app = Flask(__name__)


app.config['SECRET_KEY'] = "do not steal my secret key"



login = LoginManager(app)
login.login_view = 'login'

from models import start_db

start_db()

import views
