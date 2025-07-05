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
    user_id = db.Column(db.String(36), db.ForeignKey(
        'user.id'), nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)

    user = db.relationship(
        'User', backref=db.backref('favorite_races', lazy=True))
    race = db.relationship(
        'Race', backref=db.backref('favorited_by', lazy=True))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'driver.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    position = db.Column(db.Integer)
    laps = db.Column(db.Integer)
    time_retired = db.Column(db.String(50))
    points = db.Column(db.Float)

    race = db.relationship('Race', backref=db.backref('results', lazy=True))
    driver = db.relationship(
        'Driver', backref=db.backref('results', lazy=True))
    team = db.relationship('Team', backref=db.backref('results', lazy=True))


class FastestLap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'driver.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    lap_time = db.Column(db.String(20))
    lap_number = db.Column(db.Integer)

    race = db.relationship(
        'Race', backref=db.backref('fastest_laps', lazy=True))
    driver = db.relationship(
        'Driver', backref=db.backref('fastest_laps', lazy=True))
    team = db.relationship(
        'Team', backref=db.backref('fastest_laps', lazy=True))


class PitStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'driver.id'), nullable=False)
    stop_number = db.Column(db.Integer)
    lap = db.Column(db.Integer)
    time = db.Column(db.String(20))

    race = db.relationship('Race', backref=db.backref('pit_stops', lazy=True))
    driver = db.relationship(
        'Driver', backref=db.backref('pit_stops', lazy=True))


class GridPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'driver.id'), nullable=False)
    position = db.Column(db.Integer)

    race = db.relationship(
        'Race', backref=db.backref('grid_positions', lazy=True))
    driver = db.relationship(
        'Driver', backref=db.backref('grid_positions', lazy=True))
