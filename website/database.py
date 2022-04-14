from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# Database: Gallery Entries
class Paintings(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), unique=True, nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    alt = db.Column(db.String(250), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    price = db.Column(db.Integer)
    sold = db.Column(db.Boolean)
    note = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    # foreign key: Users -> Paintings
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# database: Artists
class Artists(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(150), unique=True, nullable=False)
    filename = db.Column(db.String(250), unique=True)
    note = db.Column(db.String(1000))
    twitter = db.Column(db.String(500))
    facebook = db.Column(db.String(500))
    youtube = db.Column(db.String(500))
    instagram = db.Column(db.String(500))
    email = db.Column(db.String(500))

    # foreign key: Users -> Artists
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# database: User credentials
class Users(db.Model, UserMixin):   # remove UserMixin if no connection between users and paintings

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)   
    #email = db.Column(db.String(150), unique=True, nullable=False)

    # foreign keys
    paintings = db.relationship("Paintings", backref="user", lazy=True)
    artists = db.relationship("Artists", backref="user", lazy=True)