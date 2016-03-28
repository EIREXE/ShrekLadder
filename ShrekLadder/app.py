from flask import Flask, render_template, request, g, Response, redirect, session, abort, send_file, url_for, Markup 
from flask.ext.login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown

from flaskext.markdown import Markdown
from juggernaut import Juggernaut

from ShrekLadder.config_file import config, configi
from ShrekLadder.database import db, init_db
from ShrekLadder.objects import User
from ShrekLadder.kerbdown import KerbDown

from ShrekLadder.blueprints.public import public_pages
from ShrekLadder.blueprints.accounts import accounts
from ShrekLadder.blueprints.admin import admin
from ShrekLadder.blueprints.profile import profile
from ShrekLadder.blueprints.match import match
from ShrekLadder.blueprints.ladder import ladder
from ShrekLadder.blueprints.notifications import *
init_db()

app = Flask(__name__)
pagedown = PageDown(app)
Bootstrap(app)
markdown = Markdown(app, safe_mode='remove', extensions=[KerbDown()])

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    return User.query.filter(User.username == username).first()

login_manager.anonymous_user = lambda: None

app.register_blueprint(public_pages)
app.register_blueprint(accounts)
app.register_blueprint(admin)
app.register_blueprint(profile)
app.register_blueprint(notifications)
app.register_blueprint(match)
app.register_blueprint(ladder)
app.secret_key = config('secret_key')
app.jinja_env.cache = None
    
@app.context_processor
def inject_prep():
    return {
        'user': current_user,
        'site_name': config('site_name')
    }
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()

