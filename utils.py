import os
import yaml
import re
from models import Race, db


def load_races_data(races_folder, season=2024):
    """Load 2024 YAML race folders into the DB, tagged with the given season."""
    import datetime
    races = []
    for item in os.listdir(races_folder):
        if not os.path.isdir(os.path.join(races_folder, item)) or item == 'uploads':
            continue
        match = re.match(r'(\d+)\s+(.*)', item)
        if not match:
            continue
        race_number = int(match.group(1))
        race_name   = match.group(2).strip()

        existing = Race.query.filter_by(folder_name=item).first()
        if existing:
            # Ensure season tag is correct
            if existing.season != season:
                existing.season = season
                db.session.commit()
            print(f"Skipping duplicate: {item} ({race_name}, {race_number})")
            continue

        race = Race(
            season=season,
            name=race_name,
            folder_name=item,
            race_number=race_number,
            circuit_name=race_name,
            date=None,
        )
        db.session.add(race)
        races.append(race)

    if races:
        db.session.commit()
    return races


# ── YAML loaders (unchanged) ──────────────────────────────────────────────────

def load_race_results(race_folder):
    path = os.path.join(race_folder, 'race-results.yml')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return yaml.safe_load(f) or []
    return []


def load_fastest_laps(race_folder):
    path = os.path.join(race_folder, 'fastest-laps.yml')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return yaml.safe_load(f) or []
    return []


def load_pit_stops(race_folder):
    path = os.path.join(race_folder, 'pit-stops.yml')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return yaml.safe_load(f) or []
    return []


def load_grid_positions(race_folder):
    path = os.path.join(race_folder, 'starting-grid-positions.yml')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return yaml.safe_load(f) or []
    return []
