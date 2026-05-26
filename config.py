import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY                  = os.environ.get('SECRET_KEY', 'f1-dash-secret-2025')
    SQLALCHEMY_DATABASE_URI     = os.environ.get('DATABASE_URI', 'sqlite:///f1_dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Local race YAML data (2024 season)
    RACES_FOLDER = os.environ.get('RACES_FOLDER', 'races')

    # Jolpica API (free, no key required)
    JOLPICA_BASE = 'https://api.jolpi.ca/ergast/f1'

    # Cache TTL in seconds (6 hours)
    CACHE_TTL_SECONDS = 6 * 60 * 60

    # Seasons supported
    SUPPORTED_SEASONS = [2024, 2025, 2026]
    DEFAULT_SEASON    = 2025