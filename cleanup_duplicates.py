from app import create_app, db
from models import Race

def cleanup_duplicates():
    app = create_app()
    with app.app_context():
        races_to_delete = Race.query.filter(
            Race.name.in_(['United States', 'Brazil']),
            Race.date.is_(None)
        ).all()

        if not races_to_delete:
            print("No duplicate TBA races found for United States or Brazil.")
            return

        print(f"Found {len(races_to_delete)} duplicate races to delete:")
        for race in races_to_delete:
            print(f" - {race.name} (ID: {race.id}, Folder: {race.folder_name})")
            db.session.delete(race)
        
        db.session.commit()
        print("Cleanup complete.")

if __name__ == '__main__':
    cleanup_duplicates()