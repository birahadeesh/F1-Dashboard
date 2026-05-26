from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Race(db.Model):
    """Local YAML-backed race (2024 season data from files)."""
    __tablename__ = 'race'
    id            = db.Column(db.Integer, primary_key=True)
    season        = db.Column(db.Integer, nullable=False, default=2024)
    name          = db.Column(db.String(120), nullable=False)
    folder_name   = db.Column(db.String(120), unique=True, nullable=False)
    race_number   = db.Column(db.Integer, nullable=False)
    circuit_name  = db.Column(db.String(120), nullable=False)
    country       = db.Column(db.String(80), nullable=True)
    locality      = db.Column(db.String(80), nullable=True)
    date          = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Race {self.season} R{self.race_number} {self.name}>'


class SeasonCache(db.Model):
    """
    Generic JSON cache for one API payload per (season, data_type).
    data_type examples: 'schedule', 'driver_standings', 'constructor_standings',
                        'race_results_1', 'race_results_2', ...
    """
    __tablename__ = 'season_cache'
    id            = db.Column(db.Integer, primary_key=True)
    season        = db.Column(db.Integer, nullable=False)
    data_type     = db.Column(db.String(60), nullable=False)
    payload       = db.Column(db.Text, nullable=False)   # JSON string
    fetched_at    = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('season', 'data_type', name='uq_season_datatype'),
    )

    def __repr__(self):
        return f'<SeasonCache {self.season}/{self.data_type}>'