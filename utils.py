import os
import yaml
import re
from models import Race, Team, Driver, Result, FastestLap, PitStop, GridPosition, db


def load_races_data(races_folder):
    import datetime
    races = []
    for item in os.listdir(races_folder):
        if not os.path.isdir(os.path.join(races_folder, item)) or item == 'uploads':
            continue
        match = re.match(r'(\d+)\s+(.*)', item)
        if match:
            race_number = int(match.group(1))
            race_name = match.group(2).strip()
            race_date = None
            existing_race = Race.query.filter_by(
                race_number=race_number, name=race_name).first()
            if not existing_race:
                race = Race(
                    name=race_name,
                    folder_name=item,
                    race_number=race_number,
                    circuit_name=race_name,
                    date=race_date
                )
                db.session.add(race)
                races.append(race)
    if races:
        db.session.commit()
    return races


def load_race_results(race_folder):
    results_file = os.path.join(race_folder, 'race-results.yml')
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_fastest_laps(race_folder):
    laps_file = os.path.join(race_folder, 'fastest-laps.yml')
    if os.path.exists(laps_file):
        with open(laps_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_pit_stops(race_folder):
    pit_stops_file = os.path.join(race_folder, 'pit-stops.yml')
    if os.path.exists(pit_stops_file):
        with open(pit_stops_file, 'r') as f:
            return yaml.safe_load(f)
    return []


def load_grid_positions(race_folder):
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

        # Results
        results = load_race_results(folder_path)
        for entry in results:
            driver = Driver.query.filter_by(name=entry['driver']).first()
            team = Team.query.filter_by(name=entry['team']).first()
            if not driver:
                driver = Driver(name=entry['driver'])
                db.session.add(driver)
            if not team:
                team = Team(name=entry['team'])
                db.session.add(team)
            result = Result(
                race_id=race.id,
                driver=driver,
                team=team,
                position=entry.get('position'),
                laps=entry.get('laps'),
                time_retired=entry.get('time_retired'),
                points=entry.get('points')
            )
            db.session.add(result)

        # Fastest Laps
        laps = load_fastest_laps(folder_path)
        for lap in laps:
            driver = Driver.query.filter_by(name=lap['driver']).first()
            team = Team.query.filter_by(name=lap['team']).first()
            fastest = FastestLap(
                race_id=race.id,
                driver=driver,
                team=team,
                lap_time=lap.get('lap_time'),
                lap_number=lap.get('lap_number')
            )
            db.session.add(fastest)

        # Pit Stops
        stops = load_pit_stops(folder_path)
        for stop in stops:
            driver = Driver.query.filter_by(name=stop['driver']).first()
            pit = PitStop(
                race_id=race.id,
                driver=driver,
                stop_number=stop.get('stop_number'),
                lap=stop.get('lap'),
                time=stop.get('time')
            )
            db.session.add(pit)

        # Grid Positions
        grid = load_grid_positions(folder_path)
        for pos in grid:
            driver = Driver.query.filter_by(name=pos['driver']).first()
            grid_pos = GridPosition(
                race_id=race.id,
                driver=driver,
                position=pos.get('position')
            )
            db.session.add(grid_pos)

    db.session.commit()
