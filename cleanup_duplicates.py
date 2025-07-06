from app import create_app
from models import db, Race

app = create_app()
with app.app_context():
    # Group races by (race_number, name)
    from collections import defaultdict
    race_groups = defaultdict(list)
    for race in Race.query.all():
        key = (race.race_number, race.name.lower())
        race_groups[key].append(race)

    deleted = 0
    for group, races in race_groups.items():
        if len(races) > 1:
            # Prefer races with a date, and if multiple, the earliest date
            with_date = [r for r in races if r.date]
            if with_date:
                # Sort by date, keep the earliest
                to_keep = sorted(with_date, key=lambda r: r.date)[0]
            else:
                # If none have a date, just keep the first
                to_keep = races[0]
            for r in races:
                if r != to_keep:
                    print(f"Deleting duplicate: {r} (id={r.id}, date={r.date}, circuit={r.circuit_name})")
                    db.session.delete(r)
                    deleted += 1
    db.session.commit()
    print(f"Cleanup complete. Deleted {deleted} duplicate races.") 