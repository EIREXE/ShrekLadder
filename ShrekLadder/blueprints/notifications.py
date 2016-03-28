from flask import Blueprint, render_template, abort, request, redirect, session, url_for, current_app
from flask.ext.login import current_user, login_user
from sqlalchemy import desc, asc
from ShrekLadder.config_file import config
from ShrekLadder.database import db
from datetime import datetime
import datetime
import flask
import redis

#red = redis.StrictRedis()

notifications = Blueprint('notifications', __name__, template_folder='../../templates/notifications')

@notifications.route('/notifications/dismiss/<notification_id>', methods=['POST'])
def dismiss_notification(notification_id):
    from ShrekLadder.objects import Notification
    notification = Notification.query.filter(Notification.id == notification_id).first()
    if(notification.owner == current_user):
        notification.seen = True
        db.commit()
        return redirect(request.args.get('return_to'))
@notifications.route('/notifications')
def view_notifications():
    from ShrekLadder.objects import Notification, User
    return render_template("notifications.html", notification=current_user.get_notifications())