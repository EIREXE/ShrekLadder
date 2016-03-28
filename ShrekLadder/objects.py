from datetime import datetime, timezone
from trueskill import Rating, rate_1vs1
from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text, FLOAT, desc
from sqlalchemy.orm import relationship, backref, relation
from sqlalchemy.dialects.postgresql import ARRAY
from passlib.hash import pbkdf2_sha256
from trueskill import Rating
import calendar
from .database import Base, db
from arrow import Arrow

main_users = Table('main_users', Base.metadata,
    Column('main_id', Integer, ForeignKey('main.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
match_users = Table('match_users', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
main_game = Table('main_game', Base.metadata,
    Column('game_id', Integer, ForeignKey('game.id')),
    Column('main_id', Integer, ForeignKey('main.id')),
)
match_loser = Table('match_loser', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
match_winner = Table('match_winner', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
match_creator = Table('match_creator', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
match_winnerchar = Table('match_winnerchar', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('main_id', Integer, ForeignKey('main.id')),
)
match_loserchar = Table('match_loserchar', Base.metadata,
    Column('match_id', Integer, ForeignKey('match.id')),
    Column('main_id', Integer, ForeignKey('main.id')),
)
notification_user = Table('notification_user', Base.metadata,
    Column('notification_id', Integer, ForeignKey('notification.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username =  Column(String(128), nullable=False, index = True)
    email =  Column(String(256), nullable=False, index = True)
    password = Column(String)
    confirmed = Column(Boolean())
    confirm_code = Column(String(128))
    created = Column(DateTime)
    mains = relationship("Main", secondary=main_users)
    admin = Column(Boolean())
    rating_mu = Column(FLOAT())
    rating_sigma = Column(FLOAT())
    description = Column(String())
    matches = relationship("Match", secondary=match_users)
    def __init__(self, user, passwd, email):
        self.username = user
        self.email = email
        self.password = pbkdf2_sha256.encrypt(passwd, rounds=200000, salt_size=16)
        self.created = datetime.now()
        self.admin = False
        self.rating_mu = 25.000
        self.rating_sigma = 8.333
    def has_main(self, main):
        if main in self.mains:
            return True
        else:
            return False
    def get_matches(self,game):
        matches = []
        if len(self.matches) == 0:
            return None
        for match in self.matches:
            if match.loser_character.game == game:
                if match.winner == self or match.loser == self:
                    matches.append(match)
        if len(matches) == 0:
            return None
        else:
            return matches
    def get_most_used_character(self, game):
        matches = self.get_matches(game)
        characters = []
        most_used_character = None
        most_used_character_number = 0
        for match in matches:
            if match.user_won(self):
                characters.append(match.winner_character)
            else:
                characters.append(match.loser_character)
        for main in game.get_mains():
            main_count = characters.count(main)
            if main_count > most_used_character_number:
                most_used_character_number = main_count
                most_used_character = main
        return most_used_character, most_used_character_number
    def get_notifications(self, unread = False):
        all_notifications = Notification.query.all()
        notifications = []
        if len(all_notifications) == 0:
            return None
        for notification in all_notifications:
            if len(all_notifications) != 0:
                if notification.owner == self:
                    if unread and not notification.seen:
                        notifications.append(notification)
                    if not unread:
                        notifications.append(notification)
        if len(notifications) > 0:
            return notifications
    def get_number_of_notifications(self, unread = False):
        all_notifications = Notification.query.all()
        notifications = []
        if len(all_notifications) == 0:
            return 0
        for notification in all_notifications:
            if len(all_notifications) != 0:
                if notification.owner == self:
                    if unread and not notification.seen:
                        notifications.append(notification)
                    if not unread:
                        notifications.append(notification)
        if len(notifications) == 0:
            return len(notifications)
        if len(notifications) > 0:
            return len(notifications)
    def add_notification(self, type, message, link):
        notification = Notification(self, False, type, message, link)
        db.add(notification)
        db.commit()
    def get_lost_matches(self,game):
        matches = []
        if len(self.matches) == 0:
            return 0
        for match in self.matches:
            if match.loser_character.game == game:
                if match.loser == self:
                    matches.append(match)
        if len(matches) == 0:
            return 0
        else:
            return len(matches)
    def get_won_matches(self,game):
        matches = []
        if len(self.matches) == 0:
            return 0
        for match in self.matches:
            if match.loser_character.game == game:
                if match.winner == self:
                    matches.append(match)
        if len(matches) == 0:
            return 0
        else:
            return len(matches)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key = True)
    name =  Column(String(128), nullable=False, index = True)

    def __init__(self, name):
        self.name = name
    def get_mains(self):
        mains = []
        for main in Main.query.order_by(Main.id):
            if main.game == self:
                mains.append(main)
        return mains
    def get_matches(self):
        matches = Match.query
        game_matches = []
        for match in matches:
            if match.game == self:
                game_matches.append(match)
        return game_matches
class Main(Base):
    __tablename__ = 'main'
    id = Column(Integer, primary_key = True)
    name = Column(String(128), nullable=False, index = True)

    game_id = Column(None, ForeignKey('game.id'))
    game = relation(Game, primaryjoin=(game_id==Game.id), backref=backref('game_mains', order_by=id))

    portrait_url = Column(String())

    def __init__(self, name, game, portrait_url):
        self.name = name
        self.game = game
        self.portrait_url = portrait_url

class Match(Base):
    __tablename__ = 'match'
    id = Column(Integer, primary_key = True)

    creator_id = Column(None, ForeignKey('user.id'))
    creator = relation(User, primaryjoin=(creator_id==User.id), backref=backref('match_created', order_by=id))

    winner_id = Column(None, ForeignKey('user.id'))
    winner = relation(User, primaryjoin=(winner_id==User.id), backref=backref('match_won', order_by=id))

    loser_id = Column(None, ForeignKey('user.id'))
    loser = relation(User, primaryjoin=(loser_id==User.id), backref=backref('match_lost', order_by=id))

    winner_character_id = Column(None, ForeignKey('main.id'))
    winner_character = relation(Main, primaryjoin=(winner_character_id==Main.id), backref=backref('match_won_character', order_by=id))

    loser_character_id = Column(None, ForeignKey('main.id'))
    loser_character = relation(Main, primaryjoin=(loser_character_id==Main.id), backref=backref('match_loser_character', order_by=id))

    confirmed = Column(Boolean())
    reviewed = Column(Boolean)
    created = Column(DateTime)
    waiting_for_admin_confirmation = Column(Boolean)
    proof = Column(String)
    tournament = Column(String)
    def __init__(self, winner, loser, winner_character, loser_character, creator, tournament):
        self.winner = winner
        self.loser = loser
        self.winner_character = winner_character
        self.loser_character = loser_character
        self.creator = creator
        self.created = datetime.now()
        self.waiting_for_admin_confirmation = False
        self.confirmed = False
        self.reviewed = False
        self.tournament = tournament
    def confirm(self, confirmed):
        self.confirmed = confirmed
        self.reviewed = True
        if self.confirmed:
            winner_rating = Rating(self.winner.rating_mu, self.winner.rating_sigma)
            loser_rating = Rating(self.loser.rating_mu, self.loser.rating_sigma)
            winner_rating, loser_rating = rate_1vs1(winner_rating, loser_rating)
            self.winner.rating_mu = winner_rating.mu
            self.winner.rating_sigma = winner_rating.sigma
            self.loser.rating_mu = loser_rating.mu
            self.loser.rating_sigma = loser_rating.sigma
            self.winner.matches.append(self)
            self.loser.matches.append(self)
            db.commit()
            self.creator.add_notification('print', self.get_other_player().username + " has confirmed your match", "")

    def get_creator(self):
        return self.creator;
    def get_other_player(self):
        if self.winner != self.creator:
            return self.winner
        else:
            return self.loser
    def get_different_player(self, user):
        if self.winner != user:
            return self.winner
        else:
            return self.loser
    def get_other_character(self):
        if self.winner != self.creator:
            return self.winner_character
        else:
            return self.loser_character
    def user_won(self, user):
        if self.winner == user:
            return True
        else:
            return False
    def get_creator_character(self):
        if self.winner != self.creator:
            return self.loser_character
        else:
            return self.winner_character
    def get_character(self, user):
        if self.winner == user:
            return self.winner_character
        else:
            return self.loser_character

class Notification(Base):
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)

    owner_id = Column(None, ForeignKey('user.id'))
    owner = relation(User, primaryjoin=(owner_id==User.id), backref=backref('notification_owner', order_by=id))
    seen = Column(Boolean())
    type = Column(String())
    message = Column(String())
    link = Column(String())
    created = Column(DateTime)
    def __init__(self,owner, seen, type, message, link):
        self.owner = owner
        self.seen = seen
        self.type = type
        self.link = link
        self.message = message
        self.created = datetime.now()
    def get_time_humanized(self):
        now = self.created
        otherdate = datetime.now()
        if otherdate:
            dt = otherdate - now
            offset = dt.seconds + (dt.days * 60*60*24)
        if offset:
            delta_s = offset % 60
            offset /= 60
            delta_m = offset % 60
            offset /= 60
            delta_h = offset % 24
            offset /= 24
            delta_d = offset
        else:
            raise ValueError("Must supply otherdate or offset (from now)")
        if delta_h > 1:
            return Arrow.now().replace(hours=delta_h * -1, minutes=delta_m * -1).humanize()
        if delta_m > 1:
            return Arrow.now().replace(seconds=delta_s * -1, minutes=delta_m * -1).humanize()
        else:
            return Arrow.now().replace(days=delta_d * -1).humanize()