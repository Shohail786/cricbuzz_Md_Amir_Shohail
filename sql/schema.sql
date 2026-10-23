-- Cricbuzz LiveStats schema (SQLite-first, portable SQL).
-- For MySQL/PostgreSQL, ids are always supplied by the application,
-- so no AUTO_INCREMENT/SERIAL is required.

CREATE TABLE IF NOT EXISTS teams (
    team_id      INTEGER PRIMARY KEY,
    team_name    VARCHAR(100) NOT NULL UNIQUE,
    country      VARCHAR(60)  NOT NULL,
    team_type    VARCHAR(20)  NOT NULL DEFAULT 'international'
                 CHECK (team_type IN ('international', 'franchise', 'domestic'))
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id     INTEGER PRIMARY KEY,
    venue_name   VARCHAR(150) NOT NULL,
    city         VARCHAR(80)  NOT NULL,
    country      VARCHAR(60)  NOT NULL,
    capacity     INTEGER      CHECK (capacity IS NULL OR capacity > 0)
);

CREATE TABLE IF NOT EXISTS players (
    player_id     INTEGER PRIMARY KEY,
    full_name     VARCHAR(120) NOT NULL,
    team_id       INTEGER,
    playing_role  VARCHAR(30)  NOT NULL
                  CHECK (playing_role IN ('Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper')),
    batting_style VARCHAR(40),
    bowling_style VARCHAR(60),
    date_of_birth DATE,
    FOREIGN KEY (team_id) REFERENCES teams (team_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS series (
    series_id             INTEGER PRIMARY KEY,
    series_name           VARCHAR(150) NOT NULL,
    host_country          VARCHAR(60),
    match_type            VARCHAR(10)  CHECK (match_type IN ('Test', 'ODI', 'T20I', 'Mixed')),
    start_date            DATE,
    end_date              DATE,
    total_matches_planned INTEGER CHECK (total_matches_planned IS NULL OR total_matches_planned >= 0),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id        INTEGER PRIMARY KEY,
    series_id       INTEGER,
    match_desc      VARCHAR(150) NOT NULL,
    match_format    VARCHAR(10)  NOT NULL CHECK (match_format IN ('Test', 'ODI', 'T20I')),
    team1_id        INTEGER NOT NULL,
    team2_id        INTEGER NOT NULL,
    venue_id        INTEGER,
    match_date      DATE NOT NULL,
    toss_winner_id  INTEGER,
    toss_decision   VARCHAR(5) CHECK (toss_decision IN ('bat', 'bowl')),
    winner_id       INTEGER,
    victory_margin  INTEGER CHECK (victory_margin IS NULL OR victory_margin >= 0),
    victory_type    VARCHAR(10) CHECK (victory_type IN ('runs', 'wickets')),
    status          VARCHAR(20) NOT NULL DEFAULT 'Completed'
                    CHECK (status IN ('Upcoming', 'Live', 'Completed', 'Abandoned')),
    CHECK (team1_id <> team2_id),
    FOREIGN KEY (series_id)      REFERENCES series (series_id) ON DELETE SET NULL,
    FOREIGN KEY (team1_id)       REFERENCES teams (team_id),
    FOREIGN KEY (team2_id)       REFERENCES teams (team_id),
    FOREIGN KEY (venue_id)       REFERENCES venues (venue_id),
    FOREIGN KEY (toss_winner_id) REFERENCES teams (team_id),
    FOREIGN KEY (winner_id)      REFERENCES teams (team_id)
);

CREATE TABLE IF NOT EXISTS innings (
    innings_id      INTEGER PRIMARY KEY,
    match_id        INTEGER NOT NULL,
    innings_no      INTEGER NOT NULL CHECK (innings_no BETWEEN 1 AND 4),
    batting_team_id INTEGER NOT NULL,
    bowling_team_id INTEGER NOT NULL,
    total_runs      INTEGER CHECK (total_runs >= 0),
    wickets_lost    INTEGER CHECK (wickets_lost BETWEEN 0 AND 10),
    overs           DECIMAL(5,1),
    UNIQUE (match_id, innings_no),
    CHECK (batting_team_id <> bowling_team_id),
    FOREIGN KEY (match_id)        REFERENCES matches (match_id) ON DELETE CASCADE,
    FOREIGN KEY (batting_team_id) REFERENCES teams (team_id),
    FOREIGN KEY (bowling_team_id) REFERENCES teams (team_id)
);

CREATE TABLE IF NOT EXISTS match_players (
    match_id   INTEGER NOT NULL,
    player_id  INTEGER NOT NULL,
    team_id    INTEGER NOT NULL,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id)  REFERENCES matches (match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id)   REFERENCES teams (team_id)
);

CREATE TABLE IF NOT EXISTS batting_performances (
    batting_id       INTEGER PRIMARY KEY,
    innings_id       INTEGER NOT NULL,
    player_id        INTEGER NOT NULL,
    batting_position INTEGER NOT NULL CHECK (batting_position BETWEEN 1 AND 11),
    runs             INTEGER NOT NULL CHECK (runs >= 0),
    balls_faced      INTEGER NOT NULL CHECK (balls_faced >= 0),
    fours            INTEGER NOT NULL DEFAULT 0 CHECK (fours >= 0),
    sixes            INTEGER NOT NULL DEFAULT 0 CHECK (sixes >= 0),
    strike_rate      DECIMAL(6,2),
    is_out           BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE (innings_id, player_id),
    UNIQUE (innings_id, batting_position),
    FOREIGN KEY (innings_id) REFERENCES innings (innings_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id)  REFERENCES players (player_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bowling_performances (
    bowling_id     INTEGER PRIMARY KEY,
    innings_id     INTEGER NOT NULL,
    player_id      INTEGER NOT NULL,
    overs          DECIMAL(4,1) NOT NULL CHECK (overs >= 0),
    maidens        INTEGER NOT NULL DEFAULT 0 CHECK (maidens >= 0),
    runs_conceded  INTEGER NOT NULL CHECK (runs_conceded >= 0),
    wickets        INTEGER NOT NULL DEFAULT 0 CHECK (wickets BETWEEN 0 AND 10),
    economy_rate   DECIMAL(5,2),
    UNIQUE (innings_id, player_id),
    FOREIGN KEY (innings_id) REFERENCES innings (innings_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id)  REFERENCES players (player_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fielding_performances (
    fielding_id INTEGER PRIMARY KEY,
    match_id    INTEGER NOT NULL,
    player_id   INTEGER NOT NULL,
    catches     INTEGER NOT NULL DEFAULT 0 CHECK (catches >= 0),
    stumpings   INTEGER NOT NULL DEFAULT 0 CHECK (stumpings >= 0),
    UNIQUE (match_id, player_id),
    FOREIGN KEY (match_id)  REFERENCES matches (match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_career_stats (
    player_id      INTEGER NOT NULL,
    match_format   VARCHAR(10) NOT NULL CHECK (match_format IN ('Test', 'ODI', 'T20I')),
    matches_played INTEGER NOT NULL DEFAULT 0 CHECK (matches_played >= 0),
    innings_batted INTEGER NOT NULL DEFAULT 0,
    total_runs     INTEGER NOT NULL DEFAULT 0 CHECK (total_runs >= 0),
    highest_score  INTEGER NOT NULL DEFAULT 0,
    batting_avg    DECIMAL(6,2),
    strike_rate    DECIMAL(6,2),
    centuries      INTEGER NOT NULL DEFAULT 0,
    fifties        INTEGER NOT NULL DEFAULT 0,
    total_wickets  INTEGER NOT NULL DEFAULT 0 CHECK (total_wickets >= 0),
    bowling_avg    DECIMAL(6,2),
    economy_rate   DECIMAL(5,2),
    PRIMARY KEY (player_id, match_format),
    FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_players_team        ON players (team_id);
CREATE INDEX IF NOT EXISTS idx_players_role        ON players (playing_role);
CREATE INDEX IF NOT EXISTS idx_venues_capacity     ON venues (capacity);
CREATE INDEX IF NOT EXISTS idx_venues_country      ON venues (country);
CREATE INDEX IF NOT EXISTS idx_series_start        ON series (start_date);
CREATE INDEX IF NOT EXISTS idx_matches_date        ON matches (match_date);
CREATE INDEX IF NOT EXISTS idx_matches_venue       ON matches (venue_id);
CREATE INDEX IF NOT EXISTS idx_matches_winner      ON matches (winner_id);
CREATE INDEX IF NOT EXISTS idx_matches_series      ON matches (series_id);
CREATE INDEX IF NOT EXISTS idx_innings_match       ON innings (match_id);
CREATE INDEX IF NOT EXISTS idx_batting_player      ON batting_performances (player_id);
CREATE INDEX IF NOT EXISTS idx_bowling_player      ON bowling_performances (player_id);
CREATE INDEX IF NOT EXISTS idx_mplayers_player     ON match_players (player_id);
CREATE INDEX IF NOT EXISTS idx_career_format_runs  ON player_career_stats (match_format, total_runs);
