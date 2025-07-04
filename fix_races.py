import os
import sys
from datetime import datetime, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re
import sqlite3
try:
    from f1_dashboard.config import DATABASE_PATH
except ImportError:
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'f1_dashboard.db')

def fix_race_database():
    """Fix the race data in the database, fixing any duplicates or naming issues."""
    # Import inside the function to avoid circular imports
    from app import create_app
    from models import db, Race
    from sqlalchemy import func
    
    # Create the Flask application context
    app = create_app()
    
    with app.app_context():
        # Check if there's a duplicate Japan race with name "jap"
        jap_race = Race.query.filter_by(name="jap").first()
        if jap_race:
            print("Found 'jap' race entry - renaming to 'Japan'")
            jap_race.name = "Japan"
            db.session.commit()
            
        # Check all race entries to ensure they have their proper circuit names
        races = Race.query.all()
        print(f"Found {len(races)} races in database")
        
        race_data = {
            "Bahrain": ("Bahrain International Circuit", date(2024, 3, 2)),
            "Saudi Arabia": ("Jeddah Corniche Circuit", date(2024, 3, 9)),
            "Australia": ("Albert Park Circuit", date(2024, 3, 24)),
            "Japan": ("Suzuka International Racing Course", date(2024, 4, 7)),
            "China": ("Shanghai International Circuit", date(2024, 4, 21)),
            "Miami": ("Miami International Autodrome", date(2024, 5, 5)),
            "Emilia Romagna": ("Autodromo Enzo e Dino Ferrari", date(2024, 5, 19)),
            "Monaco": ("Circuit de Monaco", date(2024, 5, 26)),
            "Canada": ("Circuit Gilles Villeneuve", date(2024, 6, 9)),
            "Spain": ("Circuit de Barcelona-Catalunya", date(2024, 6, 23)),
            "Austria": ("Red Bull Ring", date(2024, 6, 30)),
            "Great Britain": ("Silverstone Circuit", date(2024, 7, 7)),
            "Hungary": ("Hungaroring", date(2024, 7, 21)),
            "Belgium": ("Circuit de Spa-Francorchamps", date(2024, 7, 28)),
            "Netherlands": ("Circuit Zandvoort", date(2024, 8, 25)),
            "Italy": ("Autodromo Nazionale Monza", date(2024, 9, 1)),
            "Azerbaijan": ("Baku City Circuit", date(2024, 9, 15)),
            "Singapore": ("Marina Bay Street Circuit", date(2024, 9, 22)),
            "United States": ("Circuit of the Americas", date(2024, 10, 20)),
            "Mexico": ("Autódromo Hermanos Rodríguez", date(2024, 10, 27)),
            "Brazil": ("Autódromo José Carlos Pace", date(2024, 11, 3)),
            "Las Vegas": ("Las Vegas Strip Circuit", date(2024, 11, 23)),
            "Qatar": ("Losail International Circuit", date(2024, 12, 1)),
            "Abu Dhabi": ("Yas Marina Circuit", date(2024, 12, 8)),
        }
        
        # Update each race with correct information
        for race in races:
            if race.name in race_data:
                circuit_name, race_date = race_data[race.name]
                
                # Only update if different
                if race.circuit_name != circuit_name or race.date != race_date:
                    print(f"Updating {race.name} with correct circuit and date info")
                    race.circuit_name = circuit_name
                    race.date = race_date
                    db.session.commit()
        
        print("Race data fixes completed!")

def normalize_name(name):
    # Lowercase, remove non-alphanumeric, replace spaces with underscores
    return re.sub(r'[^a-z0-9]', '', name.lower().replace(' ', ''))

def remove_duplicate_races():
    seen = set()
    duplicates = []
    races = Race.query.order_by(Race.date, Race.name).all()
    for race in races:
        norm_name = normalize_name(race.name)
        key = (norm_name, race.date)
        if key in seen:
            duplicates.append(race)
        else:
            seen.add(key)
    for dup in duplicates:
        print(f"Deleting duplicate: {dup.name} ({dup.date}) id={dup.id}")
        db.session.delete(dup)
    db.session.commit()
    print(f"Removed {len(duplicates)} duplicate races.")

def remove_unwanted_race_names():
    # List of unwanted names (case-insensitive)
    unwanted = {"aus", "emilia", "britian", "us", "abu dhabi"}
    deleted = 0
    for race in Race.query.all():
        if race.name.strip().lower() in unwanted:
            print(f"Deleting unwanted race: {race.name} (id={race.id})")
            db.session.delete(race)
            deleted += 1
    db.session.commit()
    print(f"Removed {deleted} unwanted race entries.")

def restore_abu_dhabi():
    # Check if Abu Dhabi exists
    abudhabi = Race.query.filter(func.lower(Race.name) == "abu dhabi").first()
    if not abudhabi:
        print("Restoring Abu Dhabi race entry...")
        abudhabi = Race(
            name="Abu Dhabi",
            folder_name="24 abu dhabi",
            race_number=24,
            circuit_name="Yas Marina Circuit",
            date=date(2024, 12, 8)
        )
        db.session.add(abudhabi)
        db.session.commit()
        print("Abu Dhabi race restored.")
    else:
        print("Abu Dhabi already exists.")

def remove_duplicate_las_vegas():
    # Find all Las Vegas races
    las_vegas_races = Race.query.filter(func.lower(Race.name) == "las vegas").order_by(Race.date).all()
    if len(las_vegas_races) > 1:
        # Keep the one with the correct date (2024-11-23), or the first if not found
        to_keep = None
        for race in las_vegas_races:
            if race.date == date(2024, 11, 23):
                to_keep = race
                break
        if not to_keep:
            to_keep = las_vegas_races[0]
        for race in las_vegas_races:
            if race != to_keep:
                print(f"Deleting duplicate Las Vegas: {race.name} ({race.date}) id={race.id}")
                db.session.delete(race)
        db.session.commit()
        print("Removed duplicate Las Vegas entries.")
    else:
        print("No duplicate Las Vegas entries found.")

def remove_sao_paulo():
    removed = 0
    for race in Race.query.all():
        if race.name.strip().lower() == "sao paulo":
            print(f"Deleting Sao Paulo race: {race.name} (id={race.id})")
            db.session.delete(race)
            removed += 1
    db.session.commit()
    print(f"Removed {removed} Sao Paulo race entries.")

def print_race_names():
    from models import Race
    from flask import current_app
    from sqlalchemy import inspect
    from models import db
    inspector = inspect(db.engine)
    if not inspector.has_table('race'):
        print("No 'race' table found.")
        return
    races = Race.query.order_by(Race.date).all()
    print("Current races in database:")
    for race in races:
        print(f"ID: {race.id}, Name: {race.name}, Date: {race.date}")

def clean_races():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # Remove Sao Paulo
    c.execute("DELETE FROM races WHERE LOWER(name) LIKE '%sao paulo%'")
    # Remove duplicate/incorrect Australia (keep 'Australia')
    c.execute("DELETE FROM races WHERE LOWER(name) IN ('aus', 'australia') AND id NOT IN (SELECT id FROM races WHERE name = 'Australia')")
    # Remove duplicate/incorrect Japan (keep 'Japan')
    c.execute("DELETE FROM races WHERE LOWER(name) IN ('jap', 'japan') AND id NOT IN (SELECT id FROM races WHERE name = 'Japan')")
    # Remove duplicate/incorrect US (keep 'United States')
    c.execute("DELETE FROM races WHERE LOWER(name) IN ('us', 'united states', 'austin') AND id NOT IN (SELECT id FROM races WHERE name = 'United States')")
    # Remove duplicate/incorrect Brazil (keep 'Brazil')
    c.execute("DELETE FROM races WHERE LOWER(name) IN ('brazil', 'sao paulo') AND id NOT IN (SELECT id FROM races WHERE name = 'Brazil')")
    conn.commit()
    conn.close()

def remove_non_2024_races():
    """Remove all races not matching the official 2024 F1 calendar (name and date)."""
    from models import db, Race
    from datetime import date
    official_2024 = {
        ("Bahrain", date(2024, 3, 2)),
        ("Saudi Arabia", date(2024, 3, 9)),
        ("Australia", date(2024, 3, 24)),
        ("Japan", date(2024, 4, 7)),
        ("China", date(2024, 4, 21)),
        ("Miami", date(2024, 5, 5)),
        ("Emilia Romagna", date(2024, 5, 19)),
        ("Monaco", date(2024, 5, 26)),
        ("Canada", date(2024, 6, 9)),
        ("Spain", date(2024, 6, 23)),
        ("Austria", date(2024, 6, 30)),
        ("Great Britain", date(2024, 7, 7)),
        ("Hungary", date(2024, 7, 21)),
        ("Belgium", date(2024, 7, 28)),
        ("Netherlands", date(2024, 8, 25)),
        ("Italy", date(2024, 9, 1)),
        ("Azerbaijan", date(2024, 9, 15)),
        ("Singapore", date(2024, 9, 22)),
        ("United States", date(2024, 10, 20)),
        ("Mexico", date(2024, 10, 27)),
        ("Brazil", date(2024, 11, 3)),
        ("Las Vegas", date(2024, 11, 23)),
        ("Qatar", date(2024, 12, 1)),
        ("Abu Dhabi", date(2024, 12, 8)),
    }
    races = Race.query.all()
    to_delete = []
    seen = set()
    for race in races:
        key = (race.name, race.date)
        if key not in official_2024 or key in seen:
            to_delete.append(race)
        else:
            seen.add(key)
    for race in to_delete:
        print(f"Deleting non-2024 or duplicate race: {race.name} ({race.date}) id={race.id}")
        db.session.delete(race)
    db.session.commit()
    print(f"Removed {len(to_delete)} non-2024 or duplicate races.")

def delete_all_races():
    from models import db, Race
    num = Race.query.delete()
    db.session.commit()
    print(f"Deleted {num} races from the database.")

def insert_official_2024_races():
    from models import db, Race
    from datetime import date
    official_2024 = [
        (1, "Bahrain", "Bahrain International Circuit", date(2024, 3, 2), "1 bahrain"),
        (2, "Saudi Arabia", "Jeddah Corniche Circuit", date(2024, 3, 9), "2 Saudi Arabia"),
        (3, "Australia", "Albert Park Circuit", date(2024, 3, 24), "3 Australia"),
        (4, "Japan", "Suzuka International Racing Course", date(2024, 4, 7), "4 Japan"),
        (5, "China", "Shanghai International Circuit", date(2024, 4, 21), "5 china"),
        (6, "Miami", "Miami International Autodrome", date(2024, 5, 5), "6 miami"),
        (7, "Emilia Romagna", "Autodromo Enzo e Dino Ferrari", date(2024, 5, 19), "7 Emilia Romagna"),
        (8, "Monaco", "Circuit de Monaco", date(2024, 5, 26), "8 monaco"),
        (9, "Canada", "Circuit Gilles Villeneuve", date(2024, 6, 9), "9 canada"),
        (10, "Spain", "Circuit de Barcelona-Catalunya", date(2024, 6, 23), "10 spain"),
        (11, "Austria", "Red Bull Ring", date(2024, 6, 30), "11 austria"),
        (12, "Great Britain", "Silverstone Circuit", date(2024, 7, 7), "12 Great Britain"),
        (13, "Hungary", "Hungaroring", date(2024, 7, 21), "13 hungary"),
        (14, "Belgium", "Circuit de Spa-Francorchamps", date(2024, 7, 28), "14 belgium"),
        (15, "Netherlands", "Circuit Zandvoort", date(2024, 8, 25), "15 netherlands"),
        (16, "Italy", "Autodromo Nazionale Monza", date(2024, 9, 1), "16 italy"),
        (17, "Azerbaijan", "Baku City Circuit", date(2024, 9, 15), "17 azerbaijan"),
        (18, "Singapore", "Marina Bay Street Circuit", date(2024, 9, 22), "18 singapore"),
        (19, "United States", "Circuit of the Americas", date(2024, 10, 20), "19 us"),
        (20, "Mexico", "Autódromo Hermanos Rodríguez", date(2024, 10, 27), "20 mexico"),
        (21, "Brazil", "Autódromo José Carlos Pace", date(2024, 11, 3), "21 sao paulo"),
        (22, "Las Vegas", "Las Vegas Strip Circuit", date(2024, 11, 23), "22 las vegas"),
        (23, "Qatar", "Losail International Circuit", date(2024, 12, 1), "23 qatar"),
        (24, "Abu Dhabi", "Yas Marina Circuit", date(2024, 12, 8), "24 abu dhabi"),
    ]
    for race_number, name, circuit_name, race_date, folder_name in official_2024:
        race = Race(
            name=name,
            folder_name=folder_name,
            race_number=race_number,
            circuit_name=circuit_name,
            date=race_date
        )
        db.session.add(race)
    db.session.commit()
    print("Inserted official 24 races for 2024.")

def remove_saudi_and_great_britian_typos():
    from models import db, Race
    removed = 0
    for race in Race.query.all():
        if race.name.strip().lower() in ["saudi", "great britian"]:
            print(f"Deleting typo race: {race.name} (id={race.id})")
            db.session.delete(race)
            removed += 1
    db.session.commit()
    print(f"Removed {removed} typo race entries for 'Saudi' and 'Great Britian'.")

if __name__ == "__main__":
    from app import create_app
    from models import db, Race
    from sqlalchemy import func
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Before cleanup:")
        print_race_names()
        delete_all_races()
        insert_official_2024_races()
        fix_race_database()
        remove_non_2024_races()
        remove_saudi_and_great_britian_typos()
        print("\nAfter cleanup:")
        print_race_names()
        count = db.session.query(func.count(Race.id)).scalar()
        print(f"\nTotal races in database: {count}") 