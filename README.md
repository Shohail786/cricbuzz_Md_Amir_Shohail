# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A multi-page Streamlit app that combines **live data from the Cricbuzz API** with a
**SQL database** for player statistics, 25 analytical queries and full CRUD management.

## Features
| Page | What it does |
|---|---|
| Home | Project overview, tools, instructions, navigation |
| Live Matches | Ongoing matches and detailed scorecards from the API (cached) |
| Top Player Stats | Batting/bowling leaderboards from the database and from the API, with charts |
| SQL Analytics | 25 practice queries (beginner to advanced) plus a read-only custom SQL box |
| CRUD Operations | Create, read, update, delete players and their career stats via forms |

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env and add your RAPIDAPI_KEY
python -m database.init_db  # optional: the app also does this on first start
streamlit run app.py
```

## API setup
1. Subscribe to a Cricbuzz Cricket API (e.g. on RapidAPI) and copy your key.
2. Put `RAPIDAPI_KEY` and `RAPIDAPI_HOST` in `.env` (never commit this file).
3. Endpoint paths live in `ENDPOINTS` at the top of `api/cricbuzz_client.py`. **Confirm them in
   your provider's dashboard**; if they differ, change only that dictionary. If the JSON shape differs,
   adjust only `services/match_service.py`.

## Database setup
SQLite is the default (zero setup). For MySQL or PostgreSQL set `DATABASE_URL` in `.env`
(examples in `.env.example`) and install the driver listed in `requirements.txt`.
`python -m database.init_db --reset` drops and rebuilds everything.

**About the data.** The API provides current-state data, not a bulk history of every innings, so the
per-innings tables behind the SQL questions are filled with **generated sample data**
(`database/seed_data.py`): 8 teams, 16 venues, 112 fictional players, ~640 matches, ~17k batting rows.
Dates are relative to today, so "last 30 days" queries always return rows. Replace or extend it with
API-loaded data whenever you like; the schema is the same.

## SQL dialect note
Queries are written for SQLite. Date functions (`date('now', ...)`, `strftime`) and two-argument
`MIN/MAX` differ in MySQL/PostgreSQL; the notes at the top of `sql/analytics_queries.py` list the
equivalents (e.g. `STDDEV_POP`, `LEAST/GREATEST`, `INTERVAL`).

## Project structure
```
app.py                      entry point + navigation
config.py                   settings from environment
pages/                      home, live_matches, top_stats, sql_queries, crud_operations
api/cricbuzz_client.py      the only module that calls the API (headers, retries, timeouts)
services/                   match_service (JSON parsing), player_service (CRUD logic), analytics_service
database/                   init_db, seed_data, player_repository
sql/                        schema.sql, analytics_queries.py (Q1-Q25 + Q22b)
utils/                      db_connection, validators, exceptions, logger
tests/                      pytest suite
notebooks/                  optional API experiments
```

## Testing
```bash
pip install pytest
pytest -q
```
Covers validators, JSON parsing, custom-SQL safety, all 26 queries, and a CRUD cycle on a temp database.

## Security
Secrets come from environment variables / `.env` / Streamlit secrets; all SQL uses bound parameters;
the custom SQL box only accepts a single read-only `SELECT`.

## Deployment (Streamlit Community Cloud)
Push to GitHub, create the app from `app.py`, and paste `RAPIDAPI_KEY` / `RAPIDAPI_HOST` into the app's
Secrets. The SQLite file is recreated automatically on first start (it resets when the app restarts).
For persistence use a hosted MySQL/PostgreSQL and set `DATABASE_URL`.

## Screenshots
_Add screenshots of each page here before submitting._

## Future improvements
Auto-refreshing live scores, scheduled API-to-database sync, authentication for the CRUD page,
match-outcome prediction, fantasy team builder.
