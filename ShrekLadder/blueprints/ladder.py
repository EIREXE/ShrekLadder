from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text, desc
from sqlalchemy.orm import relationship, backref
from passlib.hash import pbkdf2_sha256
import urllib
from flask import Blueprint, render_template, abort, request, redirect, session
from flask.ext.login import current_user, login_user, logout_user
from jinja2 import TemplateNotFound
from ShrekLadder.database import db
from ShrekLadder.objects import User, Game

import re
import random
import base64
import binascii
import os

ladder = Blueprint('ladder', __name__, template_folder='../../templates/accounts')

@ladder.route("/ladder")
def check_ladder():
    users = User.query.filter(User.matches != None).order_by(desc(User.rating_mu))
    games = Game.query
    return render_template("ladder.html", users = users[:100], games = games)