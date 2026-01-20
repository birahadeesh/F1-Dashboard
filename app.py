import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from config import Config
from models import db, Race
from utils import load_races_data, load_race_results, load_fastest_laps, load_pit_stops, load_grid_positions



def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    This function sets up the Flask application with all necessary
    configurations, database connections, and route registrations.

    Args:
        config_class: Configuration class for the application (default: Config)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)


    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Load race data
        races_folder = app.config['RACES_FOLDER']
        if os.path.exists(races_folder):
            load_races_data(races_folder)

    @app.route('/')
    def home():
        """
        Landing page route.

        Displays the marketing home page.
        """
        return render_template('home.html')


    @app.route('/dashboard')
    def dashboard():
        """
        Dashboard page route.

        Displays the main dashboard with a list of races.
        Races can be sorted by different criteria.

        Returns:
            Rendered dashboard template with race data
        """
        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'race_number')

        # Validate sort parameter
        if sort_by not in ['race_number', 'name']:
            sort_by = 'race_number'

        # Get races sorted by the selected field
        if sort_by == 'race_number':
            races = Race.query.order_by(Race.race_number).all()
        else:
            races = Race.query.order_by(Race.name).all()

        return render_template('index.html', races=races, sort_by=sort_by)




    @app.route('/race/<int:race_id>')
    def race_details(race_id):
        """Display race details."""
        race = Race.query.get_or_404(race_id)

        # Get the full path to the race folder
        race_folder = os.path.join(
            app.config['RACES_FOLDER'], race.folder_name)

        # Load race data
        results = load_race_results(race_folder)
        fastest_laps = load_fastest_laps(race_folder)
        pit_stops = load_pit_stops(race_folder)
        grid_positions = load_grid_positions(race_folder)

        return render_template('race_details.html',
                               race=race,
                               results=results,
                               fastest_laps=fastest_laps,
                               pit_stops=pit_stops,
                               grid_positions=grid_positions)



    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
