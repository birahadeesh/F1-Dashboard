from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    folder_name = db.Column(db.String(120), unique=True, nullable=False)
    race_number = db.Column(db.Integer, nullable=False)
    circuit_name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<Race {self.name}>'

class FavoriteRace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('favorite_races', lazy=True))
    race = db.relationship('Race', backref=db.backref('favorited_by', lazy=True)) 