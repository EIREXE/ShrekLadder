from flask import Blueprint, render_template, abort
from flask.ext.login import current_user
from jinja2 import TemplateNotFound

public_pages = Blueprint('public_pages', __name__, template_folder='../../templates/public')

@public_pages.route("/")
def index():
    return render_template('index.html')

@public_pages.route("/main_box_debug")
def mbd():
    return render_template('main_box.html')