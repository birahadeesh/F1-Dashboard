# F1 Race Data Dashboard

An immersive Formula 1 data dashboard that visualizes 2024 race season stats using Flask, with local file import and a modern UI. The app pulls race data directly from a local races/ folder, presenting each event with detailed insights and engaging visuals.

## Features

- **User Authentication**: Secure login and registration via Supabase
- **Race Data Import**: Automatically loads race data from a local races/ folder
- **Race Details**: Each race includes:
  - Fastest laps
  - Race results
  - Pit stops
  - Starting grid positions
- **Race Cards**: Overview cards with circuit information
- **Favorites**: Save your favorite races for quick access
- **Modern UI**: Dark mode with red highlights, responsive design, FontAwesome icons

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Authentication**: Supabase

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up Supabase:
   - Create a Supabase account at [supabase.io](https://supabase.io)
   - Create a new project
   - Enable Email Auth in Authentication -> Providers
   - Get your Supabase URL and Anon Key from Project Settings -> API
   - Update the `.env` file with your Supabase credentials

4. Configure the environment variables:
   - Update the `.env` file with your settings:
     ```
     SECRET_KEY=your_secret_key
     DATABASE_URI=sqlite:///f1_dashboard.db
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_anon_key
     RACES_FOLDER=../races
     ```

5. Run the application:
   ```
   python app.py
   ```

## Supabase Setup Guide

1. Go to [supabase.io](https://supabase.io) and create an account
2. Create a new project with a name of your choice
3. Navigate to Authentication -> Providers and ensure Email Auth is enabled
4. Go to Project Settings -> API to find your:
   - Project URL (e.g., https://xxxxxxxxxxxx.supabase.co)
   - Project API Keys (use the `anon` `public` key)
5. Update the `.env` file with these values:
   ```
   SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=your_anon_public_key
   ```

## Data Structure

The app expects race data in YAML format organized in folders named by race number and location:
```
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