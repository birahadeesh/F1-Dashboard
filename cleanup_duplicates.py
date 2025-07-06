from app import create_app
from models import db, Race

app = create_app()
with app.app_context():
    # Find all Bahrain races
    bahrain_races = Race.query.filter(Race.name.ilike('bahrain')).all()
    for race in bahrain_races:
        # If the date is None or the circuit is just 'Bahrain', delete it
        if not race.date or race.circuit_name.lower() == 'bahrain':
            print(f"Deleting: {race}")
            db.session.delete(race)
    db.session.commit()
    print("Cleanup complete.") 