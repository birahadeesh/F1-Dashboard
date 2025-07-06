import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Race, FavoriteRace
from auth import login_manager, register_user, login_user_with_supabase, logout_from_supabase
from utils import load_races_data, load_race_results, load_fastest_laps, load_pit_stops, load_grid_positions
from utils import import_all_yaml_data


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
    login_manager.init_app(app)

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

        Displays the marketing home page to non-authenticated users.
        Redirects authenticated users to the dashboard.

        Returns:
            Rendered home page template or redirect to dashboard
        """
        # If user is already logged in, redirect to the dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    @app.route('/dashboard')
    @login_required
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

        # Get user's favorites for highlighting
        favorites = []
        if current_user.is_authenticated:
            favorites = [fav.race_id for fav in FavoriteRace.query.filter_by(
                user_id=current_user.id).all()]

        return render_template('index.html', races=races, sort_by=sort_by, favorites=favorites)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login route."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user, error = login_user_with_supabase(email, password)

            if user:
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash(error or 'Invalid email or password', 'danger')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration route."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Validate form input
            if not all([email, username, password, confirm_password]):
                flash('All fields are required', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')

            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered', 'danger')
                return render_template('register.html')

            # Register new user
            user, error = register_user(email, password, username)

            if user:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash(error or 'Registration failed', 'danger')

        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        """User logout route."""
        success, error = logout_from_supabase()
        logout_user()
        if not success:
            flash(error, 'warning')
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password():
        """Password reset request route."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email')
            if not email:
                flash('Email is required', 'danger')
                return render_template('reset_password.html')

            # Check if user exists
            user = User.query.filter_by(email=email).first()
            if not user:
                flash('No account found with that email', 'danger')
                return render_template('reset_password.html')

            # Send password reset email
            from auth import reset_password as auth_reset_password
            success, message = auth_reset_password(email)

            if success:
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')

        return render_template('reset_password.html')

    @app.route('/race/<int:race_id>')
    @login_required
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

    @app.route('/favorite/<int:race_id>', methods=['POST'])
    @login_required
    def toggle_favorite(race_id):
        """Toggle favorite status for a race."""
        race = Race.query.get_or_404(race_id)

        # Check if already favorited
        favorite = FavoriteRace.query.filter_by(
            user_id=current_user.id,
            race_id=race.id
        ).first()

        if favorite:
            # Remove from favorites
            db.session.delete(favorite)
            message = 'Race removed from favorites'
            status = 'removed'
        else:
            # Add to favorites
            favorite = FavoriteRace(user_id=current_user.id, race_id=race.id)
            db.session.add(favorite)
            message = 'Race added to favorites'
            status = 'added'

        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": status, "message": message})
        else:
            flash(message, 'success')
            return redirect(url_for('race_details', race_id=race.id))

    @app.route('/my-favorites')
    @login_required
    def my_favorites():
        """Display user's favorite races."""
        favorites = FavoriteRace.query.filter_by(user_id=current_user.id).all()
        favorite_races = [fav.race for fav in favorites]

        return render_template('favorites.html', races=favorite_races)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.before_first_request
    def load_data_if_needed():
        from models import Race
        if Race.query.count() == 0:
            print("⚙️ No race data found. Importing YAMLs...")
            import_all_yaml_data()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
