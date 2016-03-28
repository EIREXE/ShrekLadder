from flask import Blueprint, render_template, abort, redirect
from flask.ext.login import current_user
from sqlalchemy import desc
from ShrekLadder.objects import User, Game, Main, Match
from ShrekLadder.database import db
from ShrekLadder.decorators import *
from flask.ext.login import current_user, login_user, logout_user

admin = Blueprint('admin', __name__, template_folder='../../templates/admin')

@admin.route("/admin")
@adminrequired
def backend():
    users = User.query.count()
    new_users = User.query.order_by(desc(User.created)).limit(24)
    games = Game.query.order_by(desc(Game.id)).all()
    mains = Main.query.order_by(desc(Main.id)).all()
    return render_template("admin.html", users=users, games=games, mains=mains)

@admin.route("/games/create", methods=['POST'])
@adminrequired
def create_game():
    game = request.form.get("game_name")
    if not game:
        return redirect("/admin_is_dumb")
    if any(Game.query.filter(Game.name == game)):
        return redirect("/FUCK")
    game_db = Game(game)
    db.add(game_db)
    db.commit()
    return redirect("/admin")
@admin.route("/main/create", methods=['POST'])
@adminrequired
def create_main():
    main_name = request.form.get("main-name")
    game_name = request.form.get("main-game-name")
    main_portrait_url = request.form.get("main-url")
    main_game = Game.query.filter(Game.name == game_name).first()
    print(game_name)
    main = Main(main_name, main_game, main_portrait_url)
    if not main_name:
        return redirect("/admin_is_dumb")
    if any(Main.query.filter(Main.name == main_name)):
        return redirect("/FUCK")
    db.add(main)
    db.commit()
    return redirect("/admin")

@admin.route("/admin/moderate_proofs")
@adminrequired
def moderate_proofs():
    matches = Match.query.filter(Match.waiting_for_admin_confirmation == True and Match.confirmed == False)
    games = Game.query
    return render_template("moderate_proofs.html", matches = matches, games = games)