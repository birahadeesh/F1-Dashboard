from app import create_app, db
from models import Race

app = create_app()
with app.app_context():
    races = Race.query.all()
    for race in races:
        print(f"ID: {race.id}, Name: '{race.name}', Folder: '{race.folder_name}', Number: {race.race_number}, Circuit: '{race.circuit_name}', Date: {race.date}")
