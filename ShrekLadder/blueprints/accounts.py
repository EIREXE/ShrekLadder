from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text
from sqlalchemy.orm import relationship, backref
from passlib.hash import pbkdf2_sha256
import urllib
from flask import Blueprint, render_template, abort, request, redirect, session
from flask.ext.login import current_user, login_user, logout_user
from jinja2 import TemplateNotFound
from ShrekLadder.database import db
from ShrekLadder.objects import User


import re
import random
import base64
import binascii
import os

accounts = Blueprint('accounts', __name__, template_folder='../../templates/accounts')

@accounts.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # Validate
        kwargs = dict()
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('repeatPassword')
        if not email:
            kwargs['emailError'] = 'Email is required.'
        else:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                kwargs['emailError'] = 'Please specify a valid email address.'
            elif db.query(User).filter(User.email == email).first():
                kwargs['emailError'] = 'A user with this email already exists.'
        if not username:
            kwargs['usernameError'] = 'Username is required.'
        else:
            if not re.match(r"^[A-Za-z0-9_]+$", username):
                kwargs['usernameError'] = 'Please only use letters, numbers, and underscores.'
            if len(username) < 3 or len(username) > 24:
                kwargs['usernameError'] = 'Usernames must be between 3 and 24 characters.'
            if db.query(User).filter(User.username.ilike(username)).first():
                kwargs['usernameError'] = 'A user by this name already exists.'
        if not password:
            kwargs['passwordError'] = 'Password is required.'
        else:
            if password != confirmPassword:
                kwargs['repeatPasswordError'] = 'Passwords do not match.'
            if len(password) < 5:
                kwargs['passwordError'] = 'Your password must be greater than 5 characters.'
            if len(password) > 256:
                kwargs['passwordError'] = 'We admire your dedication to security, but please use a shorter password.'
        if not kwargs == dict():
            if email is not None:
                kwargs['email'] = email
            if username is not None:
                kwargs['username'] = username
            return render_template("register.html", **kwargs)
        # All valid, let's make them an account
        user = User(username, password, email)
        user.confirmed = True
        db.add(user)
        db.commit() # We do this manually so that we're sure everything's hunky dory before the email leaves
        login_user(user, remember=True)
        return redirect("/")
    else:
        if current_user:
            return redirect("/")
        return render_template("register.html")

@accounts.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user:
            return redirect("/")
        reset = request.args.get('reset') == '1'
        return render_template("login.html", **{ 'return_to': request.args.get('return_to'), 'reset': reset })
    else:
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember-me')
        if remember == "on":
            remember = True
        else:
            remember = False
        user = User.query.filter(User.username.ilike(username)).first()
        if not user:
            return render_template("login.html", **{ "username": username, "errors": 'Your username or password is incorrect.' })
        if not pbkdf2_sha256.verify(password, user.password):
            return render_template("login.html", **{ "asusername": username, "errors": 'Your username or password is incorrect.' })
        login_user(user, remember=remember)
        if 'return_to' in request.form and request.form['return_to']:
            return redirect(urllib.parse.unquote(request.form.get('return_to')))
        return redirect("/")

@accounts.route("/logout")
def logout():
    logout_user()
    return redirect("/")