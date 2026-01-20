from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    folder_name = db.Column(db.String(120), unique=True, nullable=False)
    race_number = db.Column(db.Integer, nullable=False)
    circuit_name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<Race {self.name}>'