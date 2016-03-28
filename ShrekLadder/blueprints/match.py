from flask import Blueprint, render_template, abort, request, redirect
from flask.ext.login import current_user
from jinja2 import TemplateNotFound
from sqlalchemy import desc
from ShrekLadder.objects import User, Main, Game, Match
from ShrekLadder.database  import db, Base
from ShrekLadder.decorators import *
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
match = Blueprint('match', __name__, template_folder='../../templates/matches')

@loginrequired
@with_session
@match.route("/match/add", methods = ['POST', 'GET'])
def add_match():
    if request.method == 'GET':
        game = Game.query.order_by(desc(Game.id)).all()
        return render_template("add_match.html", games = game)
    else:

        other_user = User.query.filter(User.username.ilike(request.form.get('other-user'))).first()
        tournament = request.form.get('tournament')
        if current_user == other_user:
            return redirect("/match/add")
        if other_user == None:
            return redirect("/match/add")
        other_character = Main.query.filter(Main.name == request.form.get('other-character')).first()
        print(request.form.get('current-character'))
        current_character = Main.query.filter(Main.name == request.form.get('current-character')).first()
        won = request.form.get('won')
        if won == None or False:
            won = False
            match_db = Match(other_user, current_user, other_character, current_character, current_user, tournament)
        else:
            won = True
            match_db = Match(current_user, other_user, current_character, other_character, current_user, tournament)
        db.add(match_db)
        db.commit()
        match_id = match_db.id
        other_user.add_notification('print-link', current_user.username + " has added a new match against you, click here to check it out", "/match/review/" + str(match_id))
        return redirect("/match/add")

@loginrequired
@with_session
@match.route("/match/review/<match_id>", methods = ['POST', 'GET'])
def review_match(match_id):
    if request.method == 'GET':
        if any(Match.query.filter(Match.id == match_id)):
            print("test")
            match_db = Match.query.filter(Match.id == match_id).first()
            if match_db.confirmed == True or match_db.waiting_for_admin_confirmation:
                return redirect('/')
            if match_db.get_other_player() == current_user:
                print("aaa")
                return render_template("review_match.html", match_to_review = match_db)
@loginrequired
@with_session
@match.route("/match/review_ok/<match_id>", methods = ['POST'])
def review_ok(match_id):
    if any(Match.query.filter(Match.id == match_id)):
        match_db = Match.query.filter(Match.id == match_id).first()
        if match_db.get_other_player() == current_user:
            if match_db.waiting_for_admin_confirmation == False or current_user.admin:
                match_db.confirm(True)
                return redirect("/")
        else:
            return redirect('/')
    else:
        return redirect('/')
@loginrequired
@with_session
@match.route("/match/review_not_ok/<match_id>", methods = ['POST'])
def review_not_ok(match_id):
    if any(Match.query.filter(Match.id == match_id)):
        match_db = Match.query.filter(Match.id == match_id).first()
        if match_db.get_other_player() == current_user:
            if match_db.waiting_for_admin_confirmation == False and match_db.confirmed == False:
                match_db.waiting_for_admin_confirmation = True
                match_db.creator.add_notification('print-link', current_user.username + " has said that your match information is incorrect, click here to provide proof", "/match/provide_proof/" + str(match_db.id))
                current_user.add_notification('print-link', 'Waiting for the other user to review the data')
                db.commit()
                return redirect("/")
            else:
                return redirect('/')
@loginrequired
@with_session
@match.route("/match/provide_proof/<match_id>", methods = ['POST', 'GET'])
def provide_proof(match_id):
    if request.method == 'GET':
        if any(Match.query.filter(Match.id == match_id and Match.waiting_for_admin_confirmation == True and Match.confirmed == False)):
            print("test")
            match_db = Match.query.filter(Match.id == match_id and Match.waiting_for_admin_confirmation == True and Match.confirmed == False).first()
            if match_db.creator == current_user:
                print("aaa")
                return render_template("provide_proof.html", match_to_review = match_db)
        else:
            return redirect('/')
    else:
        if any(Match.query.filter(Match.id == match_id and Match.waiting_for_admin_confirmation == True and Match.confirmed == False)):
            print("test")
            match_db = Match.query.filter(Match.id == match_id and Match.waiting_for_admin_confirmation == True and Match.confirmed == False).first()
            if match_db.creator == current_user:
                proof = request.form.get('proof')
                match_db.proof = proof
                db.commit()
                return redirect('/')