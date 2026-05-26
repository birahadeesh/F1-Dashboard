"""
app.py — F1 Multi-Season Dashboard
====================================
Routes:
  GET /                         → home page
  GET /dashboard                → redirect to /season/2025
  GET /season/<year>            → season dashboard (calendar + standings)
  GET /race/<race_id>           → local YAML race details (2024)
  GET /api-race/<year>/<round>  → API-backed race details (2025 / 2026)
  GET /api/standings/<year>     → JSON standings (AJAX)
  GET /api/schedule/<year>      → JSON schedule (AJAX)
"""

import os
import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, jsonify, abort, session
from config import Config
from models import db, Race
from utils import (load_races_data, load_race_results,
                   load_fastest_laps, load_pit_stops, load_grid_positions)
import api_client as apic

log = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        db.create_all()
        races_folder = app.config['RACES_FOLDER']
        if os.path.exists(races_folder):
            load_races_data(races_folder, season=2024)

    # ── Jinja2 helpers ────────────────────────────────────────────────────────
    app.jinja_env.globals['team_color']     = apic.team_color
    app.jinja_env.globals['race_flag']      = apic.race_flag
    app.jinja_env.globals['get_card_image'] = apic.get_card_image
    app.jinja_env.globals['now']            = datetime.utcnow

    # ── Routes ────────────────────────────────────────────────────────────────

    @app.route('/')
    def home():
        """Marketing landing page with dynamic season highlights."""
        season = session.get('season', 2026)
        try:
            driver_st = apic.get_driver_standings(season)[:5]
            constr_st = apic.get_constructor_standings(season)[:5]
            schedule  = apic.get_schedule(season)
        except Exception:
            driver_st, constr_st, schedule = [], [], []
        return render_template('home.html',
                               driver_standings=driver_st,
                               constructor_standings=constr_st,
                               schedule=schedule,
                               current_year=season)

    @app.route('/dashboard')
    def dashboard():
        season = session.get('season', 2026)
        return redirect(url_for('season_dashboard', year=season))

    @app.route('/season/<int:year>')
    def season_dashboard(year):
        """Main season dashboard — calendar + live standings."""
        if year not in app.config['SUPPORTED_SEASONS']:
            abort(404)
            
        session['season'] = year
        sort_by = request.args.get('sort', 'round')

        if year == 2024:
            # Use local YAML-backed data
            raw_races = Race.query.filter_by(season=2024).all()
            
            unique_races = {}
            for r in raw_races:
                key = r.race_number
                if key not in unique_races:
                    unique_races[key] = r
                else:
                    existing = unique_races[key]
                    
                    def has_data(race_obj):
                        folder = os.path.join(app.config['RACES_FOLDER'], race_obj.folder_name)
                        return os.path.exists(os.path.join(folder, 'race-results.yml'))
                        
                    r_has_data = has_data(r)
                    e_has_data = has_data(existing)
                    
                    if r_has_data and not e_has_data:
                        if not r.date and existing.date:
                            r.date = existing.date
                        if (existing.circuit_name and existing.circuit_name != existing.name) and (not r.circuit_name or r.circuit_name == r.name):
                            r.circuit_name = existing.circuit_name
                        unique_races[key] = r
                    elif e_has_data and not r_has_data:
                        if not existing.date and r.date:
                            existing.date = r.date
                        if (r.circuit_name and r.circuit_name != r.name) and (not existing.circuit_name or existing.circuit_name == existing.name):
                            existing.circuit_name = r.circuit_name
                    else:
                        score_new = 1 if r.date else 0
                        score_exist = 1 if existing.date else 0
                        if r.circuit_name and r.circuit_name != r.name:
                            score_new += 1
                        if existing.circuit_name and existing.circuit_name != existing.name:
                            score_exist += 1
                        
                        if score_new > score_exist:
                            unique_races[key] = r
                        
            races_db = list(unique_races.values())
            if sort_by == 'name':
                races_db.sort(key=lambda r: r.name)
            else:
                races_db.sort(key=lambda r: r.race_number)
                
            schedule   = []   # not used in template for 2024
            use_local  = True
        else:
            races_db   = []
            schedule   = apic.get_schedule(year)
            if sort_by == 'name':
                schedule = sorted(schedule, key=lambda r: r.get('raceName', ''))
            use_local  = False

        try:
            driver_st  = apic.get_driver_standings(year)
            constr_st  = apic.get_constructor_standings(year)
        except Exception:
            driver_st, constr_st = [], []

        return render_template('season.html',
                               year=year,
                               supported_seasons=app.config['SUPPORTED_SEASONS'],
                               races=races_db,
                               schedule=schedule,
                               use_local=use_local,
                               sort_by=sort_by,
                               driver_standings=driver_st,
                               constructor_standings=constr_st,
                               team_color=apic.team_color,
                               race_flag=apic.race_flag)

    # ── Local (2024 YAML) race details ────────────────────────────────────────
    @app.route('/race/<int:race_id>')
    def race_details(race_id):
        race = Race.query.get_or_404(race_id)
        session['season'] = race.season
        folder = os.path.join(app.config['RACES_FOLDER'], race.folder_name)
        return render_template('race_details.html',
                               race=race,
                               results=load_race_results(folder),
                               fastest_laps=load_fastest_laps(folder),
                               pit_stops=load_pit_stops(folder),
                               grid_positions=load_grid_positions(folder),
                               year=race.season,
                               supported_seasons=app.config['SUPPORTED_SEASONS'])

    # ── API-backed (2025/2026) race details ───────────────────────────────────
    @app.route('/api-race/<int:year>/<int:round_num>')
    def api_race_details(year, round_num):
        if year not in app.config['SUPPORTED_SEASONS']:
            abort(404)
        session['season'] = year
        schedule = apic.get_schedule(year)
        race_info = next((r for r in schedule
                          if int(r.get('round', 0)) == round_num), None)
        if not race_info:
            abort(404)

        results       = apic.get_race_results(year, round_num)
        fastest_laps  = apic.get_fastest_laps(year, round_num)
        pit_stops     = apic.get_pit_stops(year, round_num)
        qualifying    = apic.get_qualifying(year, round_num)

        return render_template('api_race_details.html',
                               race_info=race_info,
                               year=year,
                               round_num=round_num,
                               results=results,
                               fastest_laps=fastest_laps,
                               pit_stops=pit_stops,
                               qualifying=qualifying,
                               supported_seasons=app.config['SUPPORTED_SEASONS'],
                               team_color=apic.team_color)

    # ── JSON API endpoints (AJAX / future use) ────────────────────────────────
    @app.route('/api/standings/<int:year>')
    def api_standings(year):
        return jsonify({
            'drivers':      apic.get_driver_standings(year),
            'constructors': apic.get_constructor_standings(year),
        })

    @app.route('/api/schedule/<int:year>')
    def api_schedule(year):
        return jsonify(apic.get_schedule(year))

    # ── Error handlers ────────────────────────────────────────────────────────
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
