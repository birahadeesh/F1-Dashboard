"""
api_client.py
=============
Fetches Formula 1 data from the Jolpica (Ergast-compatible) API and caches
results in the SQLite SeasonCache table.

Strategy:
  - On each request, check SeasonCache for a fresh entry (< CACHE_TTL_SECONDS).
  - If stale or missing, call the Jolpica API, store in DB, return data.
  - All callers get dicts/lists — never raw JSON strings.
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from flask import current_app
from models import db, SeasonCache

log = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────

def _base():
    return current_app.config['JOLPICA_BASE']

def _ttl():
    return current_app.config['CACHE_TTL_SECONDS']


def _get_cache(season: int, data_type: str):
    """Return parsed payload if cache is fresh, else None."""
    row = SeasonCache.query.filter_by(season=season, data_type=data_type).first()
    if row is None:
        return None
    age = (datetime.utcnow() - row.fetched_at).total_seconds()
    if age > _ttl():
        return None
    try:
        return json.loads(row.payload)
    except Exception:
        return None


def _set_cache(season: int, data_type: str, data):
    """Upsert the cache row."""
    row = SeasonCache.query.filter_by(season=season, data_type=data_type).first()
    payload = json.dumps(data, ensure_ascii=False)
    if row:
        row.payload    = payload
        row.fetched_at = datetime.utcnow()
    else:
        row = SeasonCache(season=season, data_type=data_type,
                          payload=payload, fetched_at=datetime.utcnow())
        db.session.add(row)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        log.warning("Cache write failed: %s", exc)


def _fetch(url: str, params: dict = None) -> dict:
    """HTTP GET with a 10-second timeout; returns parsed JSON or {}."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.warning("Jolpica fetch failed for %s: %s", url, exc)
        return {}


# ── public API ────────────────────────────────────────────────────────────────

def get_schedule(season: int) -> list:
    """
    Returns list of race dicts for the given season.
    Each dict: {round, raceName, Circuit, date, time, Results (if any)}
    """
    cached = _get_cache(season, 'schedule')
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/races/"
    data = _fetch(url, {'limit': 30})
    races = (data.get('MRData') or {}).get('RaceTable', {}).get('Races', [])
    _set_cache(season, 'schedule', races)
    return races


def get_driver_standings(season: int) -> list:
    """
    Returns list of driver standing dicts.
    Each dict: {position, points, wins, Driver, Constructors}
    """
    cached = _get_cache(season, 'driver_standings')
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/driverStandings/"
    data = _fetch(url)
    try:
        standings = (data['MRData']['StandingsTable']
                     ['StandingsLists'][0]['DriverStandings'])
    except (KeyError, IndexError):
        standings = []
    _set_cache(season, 'driver_standings', standings)
    return standings


def get_constructor_standings(season: int) -> list:
    """
    Returns list of constructor standing dicts.
    """
    cached = _get_cache(season, 'constructor_standings')
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/constructorStandings/"
    data = _fetch(url)
    try:
        standings = (data['MRData']['StandingsTable']
                     ['StandingsLists'][0]['ConstructorStandings'])
    except (KeyError, IndexError):
        standings = []
    _set_cache(season, 'constructor_standings', standings)
    return standings


def get_race_results(season: int, round_num: int) -> list:
    """
    Returns list of result dicts for a specific race round.
    """
    key   = f'results_{round_num}'
    cached = _get_cache(season, key)
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/{round_num}/results/"
    data = _fetch(url)
    try:
        results = (data['MRData']['RaceTable']['Races'][0]['Results'])
    except (KeyError, IndexError):
        results = []
    _set_cache(season, key, results)
    return results


def get_qualifying(season: int, round_num: int) -> list:
    """Returns qualifying results for a race round."""
    key   = f'qualifying_{round_num}'
    cached = _get_cache(season, key)
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/{round_num}/qualifying/"
    data = _fetch(url)
    try:
        results = (data['MRData']['RaceTable']['Races'][0]['QualifyingResults'])
    except (KeyError, IndexError):
        results = []
    _set_cache(season, key, results)
    return results


def get_pit_stops(season: int, round_num: int) -> list:
    """Returns pit stop data for a race round."""
    key   = f'pitstops_{round_num}'
    cached = _get_cache(season, key)
    if cached is not None:
        return cached

    url  = f"{_base()}/{season}/{round_num}/pitstops/"
    data = _fetch(url, {'limit': 100})
    try:
        results = (data['MRData']['RaceTable']['Races'][0]['PitStops'])
    except (KeyError, IndexError):
        results = []
    _set_cache(season, key, results)
    return results


def get_fastest_laps(season: int, round_num: int) -> list:
    """
    Returns fastest lap entries from race results
    (Ergast embeds FastestLap inside Results).
    """
    results = get_race_results(season, round_num)
    laps = []
    for r in results:
        fl = r.get('FastestLap')
        if fl:
            laps.append({
                'position':      fl.get('rank'),
                'driverName':    r['Driver']['familyName'],
                'driverCode':    r['Driver'].get('code', ''),
                'constructor':   r['Constructor']['name'],
                'lap':           fl.get('lap'),
                'time':          fl.get('Time', {}).get('time', '-'),
                'avgSpeed':      fl.get('AverageSpeed', {}).get('speed', '-'),
            })
    laps.sort(key=lambda x: int(x['position'] or 99))
    return laps


# ── team colour helper ────────────────────────────────────────────────────────

TEAM_COLORS = {
    'mclaren':        '#FF8000',
    'ferrari':        '#E8002D',
    'mercedes':       '#27F4D2',
    'red bull':       '#3671C6',
    'red_bull':       '#3671C6',
    'aston martin':   '#229971',
    'alpine':         '#FF87BC',
    'williams':       '#64C4FF',
    'haas':           '#B6BABD',
    'rb':             '#6692FF',
    'visa cash app rb': '#6692FF',
    'kick sauber':    '#52E252',
    'sauber':         '#52E252',
    'alphatauri':     '#5E8FAA',
    'alfa romeo':     '#B12335',
}

def team_color(name: str) -> str:
    if not name:
        return '#888'
    key = name.lower().strip()
    for k, v in TEAM_COLORS.items():
        if k in key:
            return v
    return '#888'


# ── country flag emoji ────────────────────────────────────────────────────────

# ── Country flag emojis ───────────────────────────────────────────────────────

COUNTRY_FLAGS = {
    'bahrain':        '🇧🇭',
    'saudi':          '🇸🇦',
    'australia':      '🇦🇺',
    'japan':          '🇯🇵',
    'china':          '🇨🇳',
    'miami':          '🇺🇸',
    'emilia':         '🇮🇹',
    'romagna':        '🇮🇹',
    'monaco':         '🇲🇨',
    'spain':          '🇪🇸',
    'canada':         '🇨🇦',
    'austria':        '🇦🇹',
    'great britain':  '🇬🇧',
    'british':        '🇬🇧',
    'belgium':        '🇧🇪',
    'hungary':        '🇭🇺',
    'netherlands':    '🇳🇱',
    'dutch':          '🇳🇱',
    'italian':        '🇮🇹',
    'italy':          '🇮🇹',
    'azerbaijan':     '🇦🇿',
    'singapore':      '🇸🇬',
    'united states':  '🇺🇸',
    'mexico':         '🇲🇽',
    'brazil':         '🇧🇷',
    'las vegas':      '🇺🇸',
    'qatar':          '🇶🇦',
    'abu dhabi':      '🇦🇪',
}

def _get_flag(name_lower: str) -> str:
    for k, v in COUNTRY_FLAGS.items():
        if k in name_lower:
            return v
    return '🏁'

def race_flag(race_dict: dict) -> str:
    country = (race_dict.get('Circuit') or {}).get('Location', {}).get('country', '')
    name    = race_dict.get('raceName', '')
    return _get_flag((name + ' ' + country).lower())


# ── Centralized Race Image Map ────────────────────────────────────────────────
# PRIMARY: keyed by exact Grand Prix name (lowercase) → filename in /static/img/races/
# This is season-agnostic — the GP name is stable across 2024/2025/2026.

RACE_IMAGE_MAP = {
    # Bahrain
    'bahrain grand prix':           'bahrain.jpg',
    # Saudi Arabia
    'saudi arabian grand prix':     'saudi.jpg',
    # Australia
    'australian grand prix':        'australia.jpg',
    # Japan
    'japanese grand prix':          'japan.jpg',
    # China
    'chinese grand prix':           'china.jpg',
    # Miami
    'miami grand prix':             'miami.jpg',
    # Emilia Romagna / Imola
    'emilia romagna grand prix':    'emilia.jpg',
    # Monaco
    'monaco grand prix':            'monaco.jpg',
    # Spain (covers both Spanish Grand Prix and Barcelona Grand Prix)
    'spanish grand prix':           'spain.jpg',
    'barcelona grand prix':         'spain.jpg',
    'madrid grand prix':            'spain.jpg',
    # Canada
    'canadian grand prix':          'canada.jpg',
    # Austria
    'austrian grand prix':          'austria.jpg',
    # Great Britain / Silverstone
    'british grand prix':           'silverstone.jpg',
    # Belgium
    'belgian grand prix':           'belgium.jpg',
    # Hungary
    'hungarian grand prix':         'hungary.jpg',
    # Netherlands / Zandvoort
    'dutch grand prix':             'netherlands.jpg',
    # Italy / Monza
    'italian grand prix':           'monza.jpg',
    # Azerbaijan / Baku
    'azerbaijan grand prix':        'azerbaijan.jpg',
    # Singapore
    'singapore grand prix':         'singapore.jpg',
    # United States / COTA
    'united states grand prix':     'united_states.jpg',
    # Mexico
    'mexico city grand prix':       'mexico.jpg',
    'mexican grand prix':           'mexico.jpg',
    # Brazil / Interlagos / São Paulo
    'são paulo grand prix':         'brazil.jpg',
    'sao paulo grand prix':         'brazil.jpg',
    'brazilian grand prix':         'brazil.jpg',
    # Las Vegas
    'las vegas grand prix':         'las_vegas.jpg',
    # Qatar
    'qatar grand prix':             'qatar.jpg',
    # Abu Dhabi
    'abu dhabi grand prix':         'abu_dhabi.jpg',

    # ── 2024 LOCAL DB SHORT NAMES ──────────────────────────────────────────
    # Race.name values stored by utils.py (folder name without number prefix).
    # These are exact lowercase keys — no "Grand Prix" suffix.
    'bahrain':          'bahrain.jpg',
    'saudi arabia':     'saudi.jpg',
    'australia':        'australia.jpg',
    'japan':            'japan.jpg',
    'china':            'china.jpg',
    'miami':            'miami.jpg',
    'emilia romagna':   'emilia.jpg',
    'monaco':           'monaco.jpg',
    'spain':            'spain.jpg',
    'canada':           'canada.jpg',
    'austria':          'austria.jpg',
    'great britain':    'silverstone.jpg',
    'hungary':          'hungary.jpg',
    'belgium':          'belgium.jpg',
    'netherlands':      'netherlands.jpg',
    'italy':            'monza.jpg',
    'azerbaijan':       'azerbaijan.jpg',
    'singapore':        'singapore.jpg',
    'united states':    'united_states.jpg',
    'mexico':           'mexico.jpg',
    'brazil':           'brazil.jpg',
    'las vegas':        'las_vegas.jpg',
    'qatar':            'qatar.jpg',
    'abu dhabi':        'abu_dhabi.jpg',
}

# SECONDARY: keyword-based fallback (covers abbreviated/local 2024 folder names)
RACE_IMAGE_KEYWORDS = [
    # Order matters — more specific first
    ('las vegas',    'las_vegas.jpg'),
    ('abu dhabi',    'abu_dhabi.jpg'),
    ('great britain','silverstone.jpg'),
    ('emilia',       'emilia.jpg'),
    ('romagna',      'emilia.jpg'),
    ('saudi',        'saudi.jpg'),
    ('jeddah',       'saudi.jpg'),
    ('australia',    'australia.jpg'),
    ('melbourne',    'australia.jpg'),
    ('bahrain',      'bahrain.jpg'),
    ('japan',        'japan.jpg'),
    ('suzuka',       'japan.jpg'),
    ('china',        'china.jpg'),
    ('shanghai',     'china.jpg'),
    ('miami',        'miami.jpg'),
    ('monaco',       'monaco.jpg'),
    ('spain',        'spain.jpg'),
    ('barcelona',    'spain.jpg'),
    ('madrid',       'spain.jpg'),
    ('canada',       'canada.jpg'),
    ('montreal',     'canada.jpg'),
    ('austria',      'austria.jpg'),
    ('british',      'silverstone.jpg'),
    ('silverstone',  'silverstone.jpg'),
    ('belgium',      'belgium.jpg'),
    ('spa',          'belgium.jpg'),
    ('hungary',      'hungary.jpg'),
    ('netherlands',  'netherlands.jpg'),
    ('zandvoort',    'netherlands.jpg'),
    ('dutch',        'netherlands.jpg'),
    ('italy',        'monza.jpg'),
    ('italian',      'monza.jpg'),
    ('monza',        'monza.jpg'),
    ('azerbaijan',   'azerbaijan.jpg'),
    ('baku',         'azerbaijan.jpg'),
    ('singapore',    'singapore.jpg'),
    ('united states','united_states.jpg'),
    ('austin',       'united_states.jpg'),
    ('mexico',       'mexico.jpg'),
    ('brazil',       'brazil.jpg'),
    ('interlagos',   'brazil.jpg'),
    ('paulo',        'brazil.jpg'),
    ('qatar',        'qatar.jpg'),
    ('lusail',       'qatar.jpg'),
]

# Default fallback image (guaranteed to exist)
F1_DEFAULT_IMAGE = 'f1_default.jpg'


def get_card_image(race_name: str, country: str = '') -> dict:
    """
    Returns dict:
      img_path       — URL path to /static/img/races/<file>  (always set)
      css_gradient   — None (kept for backward compat, but img_path always wins)
      flag           — emoji flag string

    Priority:
      1. Exact GP name match  (RACE_IMAGE_MAP)
      2. Keyword scan         (RACE_IMAGE_KEYWORDS)
      3. Default F1 image     (f1_default.jpg)
    """
    import os
    # Resolve races_dir absolutely.
    # current_app.root_path is the app's root folder set by Flask — always absolute.
    try:
        from flask import current_app as _ca
        _root = _ca.root_path
    except RuntimeError:
        # Outside Flask app context (e.g. unit tests) — fall back to __file__
        _root = os.path.dirname(os.path.abspath(__file__))
    races_dir = os.path.join(_root, 'static', 'img', 'races')
    name_lower = race_name.lower().strip()

    def _resolve(filename: str) -> str | None:
        # Guard: empty filename means no mapping — must not resolve to the directory itself
        if not filename:
            return None
        path = os.path.join(races_dir, filename)
        return f'/static/img/races/{filename}' if os.path.exists(path) else None

    # 1 — Exact GP name lookup
    img = _resolve(RACE_IMAGE_MAP.get(name_lower, ''))
    if img:
        return {'img_path': img, 'css_gradient': None, 'flag': _get_flag(name_lower + ' ' + country.lower())}

    # 2 — Keyword scan over race name + country
    search = name_lower + ' ' + country.lower()
    for keyword, filename in RACE_IMAGE_KEYWORDS:
        if keyword in search:
            img = _resolve(filename)
            if img:
                return {'img_path': img, 'css_gradient': None, 'flag': _get_flag(search)}

    # 3 — Default F1 fallback (always exists)
    return {
        'img_path': f'/static/img/races/{F1_DEFAULT_IMAGE}',
        'css_gradient': None,
        'flag': _get_flag(search),
    }

