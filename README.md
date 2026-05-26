# F1 Race Data Dashboard

An immersive, multi-season Formula 1 data dashboard that visualizes race stats using Flask. The app seamlessly blends historical local data (2024) with live, auto-updating API data (2025 and 2026) to present each event with detailed insights, driver/constructor standings, and premium motorsport visuals.

## Features

- **Multi-Season Support**: Instantly switch between 2024, 2025, and 2026 championships.
- **Live F1 Data**: Automatically fetches up-to-date schedules, standings, and race results via the Jolpica/Ergast F1 API.
- **Comprehensive Race Details**: Each completed race includes:
  - Race results
  - Fastest laps
  - Pit stops
  - Starting grid/qualifying positions
- **Premium F1 Theme**: A stunning dark-mode aesthetic featuring high-contrast tables, interactive hover glows, and accurate dynamic team colors (e.g., Ferrari red, McLaren orange).
- **Offline Data Fallback**: The 2024 season runs completely locally using YAML-backed datasets, demonstrating local data ingestion architecture.

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **External Data API**: Jolpica F1 API (formerly Ergast)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript

## Setup Instructions

1. Clone the repository
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your environment variables by creating a `.env` file in the root directory:
   ```ini
   SECRET_KEY=your_secure_secret_key
   DATABASE_URI=sqlite:///f1_dashboard.db
   RACES_FOLDER=races
   ```
4. Run the application locally:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000`

## Local Data Structure (2024 Season)

While the 2025 and 2026 seasons pull live data from the web, the app expects 2024 race data in YAML format organized in folders named by race number and location:
```text
races/
├── 1 bahrain/
│   ├── race-results.yml
│   ├── fastest-laps.yml
│   ├── pit-stops.yml
│   └── starting-grid-positions.yml
├── 2 saudi/
    ...
```

## License

MIT