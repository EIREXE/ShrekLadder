from flask import Blueprint, render_template, abort, request, redirect
from flask.ext.login import current_user
from jinja2 import TemplateNotFound
from ShrekLadder.objects import User, Main, Game
from ShrekLadder.database  import db, Base
from ShrekLadder.decorators import *
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
profile = Blueprint('profile', __name__, template_folder='../../templates/public')

class PageDownProfileDescription(Form):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Submit')

@profile.route("/profile/<user_name>")
def see_profile(user_name):
    user = User.query.filter(User.username.ilike(user_name)).first()
    return render_template('profile.html', profile_user = user,games = Game.query, mains = Main.query)

@profile.route("/profile/edit", methods = ['GET', 'POST'])
def profile_edit():
    if request.method == 'POST':
        description = request.form.get('description')
        current_user.description = description
        db.commit()
    return render_template('edit_profile.html', games = Game.query)

@profile.route("/main/add" , methods=['POST'])
def add_main():
    main_name = request.form.get("main-name")
    if(not any( Main.query.filter(Main.name == main_name))):
        return redirect("/profile/edit")
    main = Main.query.filter(Main.name == main_name).first()
    current_user.mains.append(main)
    db.commit()
    return redirect("/profile/edit")
@loginrequired
@with_session
@profile.route("/mains/edit")
def edit_mains():
    return render_template('profile_add_mains.html', mains = Main.query, games = Game.query)

@loginrequired
@with_session
@profile.route("/test", methods = ['GET','POST'])
def test():
    message = request.form.get('message')
    return render_template('test.html', mains = Main.query, games = Game.query)

@loginrequired
@with_session
@profile.route("/main/remove", methods = ['POST'])
def remove_main():
    main_name = request.form.get("main-name")
    print(main_name)
    if(not any( Main.query.filter(Main.name == main_name))):
        return redirect("/profile/edit")
    main = Main.query.filter(Main.name == main_name).first()
    if main in current_user.mains:
        print('userhasmain')
        current_user.mains.remove(main)
        db.commit()
        return redirect("/profile/edit")