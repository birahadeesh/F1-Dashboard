import os
import yaml
import re
from models import Race, db


def load_races_data(races_folder):
    """Load races data from the races folder and populate the database, avoiding duplicates by folder_name and (race_number, name)."""
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
            # Check for duplicates by folder_name and (race_number, name)
            existing_by_folder = Race.query.filter_by(folder_name=item).first()
            existing_by_number_name = Race.query.filter_by(race_number=race_number, name=race_name).first()
            if not existing_by_folder and not existing_by_number_name:
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
            else:
                print(f"Skipping duplicate: {item} ({race_name}, {race_number})")

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
