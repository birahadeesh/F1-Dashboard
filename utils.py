import os
from unittest import result
import yaml
import re
from models import Race, db
from utils import import_all_yaml_data


def load_races_data(races_folder):
    """Load races data from the races folder and populate the database, avoiding duplicates by (race_number, name, date)."""
    import datetime
    races = []

    # List all race directories
    for item in os.listdir(races_folder):
        # Skip non-directory items and 'uploads' directory
        if not os.path.isdir(os.path.join(races_folder, item)) or item == 'uploads':
            continue

        # Parse race number and name
        match = re.match(r'(\d+)\s+(.*)', item)
        if match:
            race_number = int(match.group(1))
            race_name = match.group(2).strip()
            # Try to infer the date from the folder name (optional, fallback to None)
            race_date = None
            # Check for a YAML file with a date, or use a mapping if available (not implemented here)
            # Check if race already exists in the database by (race_number, name, date)
            existing_race = Race.query.filter_by(
                race_number=race_number, name=race_name).first()
            if not existing_race:
                # Create new race entry
                race = Race(
                    name=race_name,
                    folder_name=item,
                    race_number=race_number,
                    circuit_name=race_name,  # Default to race name, could be updated later
                    date=race_date
                )
                db.session.add(race)
                races.append(race)

    if races:
        db.session.commit()

    return races


def load_race_results(race_folder):
    """Load race results from a specific race folder."""
    results_file = os.path.join(race_folder, 'race-results.yml')
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_fastest_laps(race_folder):
    """Load fastest laps data from a specific race folder."""
    laps_file = os.path.join(race_folder, 'fastest-laps.yml')
    if os.path.exists(laps_file):
        with open(laps_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_pit_stops(race_folder):
    """Load pit stops data from a specific race folder."""
    pit_stops_file = os.path.join(race_folder, 'pit-stops.yml')
    if os.path.exists(pit_stops_file):
        with open(pit_stops_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_grid_positions(race_folder):
    """Load starting grid positions from a specific race folder."""
    grid_file = os.path.join(race_folder, 'starting-grid-positions.yml')
    if os.path.exists(grid_file):
        with open(grid_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def import_all_yaml_data():
    races_dir = os.path.join(os.path.dirname(__file__), 'races')
    load_races_data(races_dir)

    for race in Race.query.all():
        folder_path = os.path.join(races_dir, race.folder_name)

        # Race Results
        results = load_race_results(folder_path)
        for entry in results:
            driver = driver.query.filter_by(name=entry['driver']).first()
            if not driver:
                driver = driver(name=entry['driver'])
                db.session.add(driver)

            team = team.query.filter_by(name=entry['team']).first()
            if not team:
                team = team(name=entry['team'])
                db.session.add(team)

            db.session.add(load_race_results(
                race_id=race.id,
                driver=driver,
                team=team,
                position=entry.get('position'),
                laps=entry.get('laps'),
                time_retired=entry.get('time_retired'),
                points=entry.get('points')
            ))

        # Fastest Laps
        laps = load_fastest_laps(folder_path)
        for lap in laps:
            driver = driver.query.filter_by(name=lap['driver']).first()
            team = team.query.filter_by(name=lap['team']).first()
            db.session.add(load_fastest_laps(
                race_id=race.id,
                driver=driver,
                team=team,
                lap_time=lap.get('lap_time'),
                lap_number=lap.get('lap_number')
            ))

        # Pit Stops
        stops = load_pit_stops(folder_path)
        for stop in stops:
            driver = driver.query.filter_by(name=stop['driver']).first()
            db.session.add(load_pit_stops(
                race_id=race.id,
                driver=driver,
                stop_number=stop.get('stop_number'),
                lap=stop.get('lap'),
                time=stop.get('time')
            ))

        # Grid Positions
        grid = load_grid_positions(folder_path)
        for pos in grid:
            driver = driver.query.filter_by(name=pos['driver']).first()
            db.session.add(load_grid_positions(
                race_id=race.id,
                driver=driver,
                position=pos.get('position')
            ))

    db.session.commit()
