PRAGMA foreign_keys = ON;

CREATE TABLE dim_season (
    season_key INTEGER PRIMARY KEY,
    season_label TEXT NOT NULL UNIQUE,
    source_code TEXT NOT NULL UNIQUE
);
CREATE TABLE dim_team (
    team_key TEXT PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL UNIQUE
);
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_iso TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    weekday_name TEXT NOT NULL
);
CREATE TABLE fact_match (
    match_id TEXT PRIMARY KEY,
    season_key INTEGER NOT NULL REFERENCES dim_season,
    date_key INTEGER NOT NULL REFERENCES dim_date,
    kickoff_time TEXT,
    home_team_key TEXT NOT NULL REFERENCES dim_team,
    away_team_key TEXT NOT NULL REFERENCES dim_team,
    home_goals INTEGER NOT NULL CHECK (home_goals >= 0),
    away_goals INTEGER NOT NULL CHECK (away_goals >= 0),
    result TEXT NOT NULL CHECK (result IN ('H', 'D', 'A')),
    CHECK (home_team_key <> away_team_key),
    UNIQUE (season_key, home_team_key, away_team_key)
);
CREATE TABLE fact_team_match (
    match_id TEXT NOT NULL REFERENCES fact_match,
    team_key TEXT NOT NULL REFERENCES dim_team,
    opponent_key TEXT NOT NULL REFERENCES dim_team,
    opponent_name TEXT NOT NULL,
    season_key INTEGER NOT NULL REFERENCES dim_season,
    date_key INTEGER NOT NULL REFERENCES dim_date,
    venue TEXT NOT NULL CHECK (venue IN ('Home', 'Away')),
    team_game_number INTEGER NOT NULL CHECK (team_game_number BETWEEN 1 AND 38),
    result TEXT NOT NULL CHECK (result IN ('W', 'D', 'L')),
    points INTEGER NOT NULL CHECK (points IN (0, 1, 3)),
    goals_for INTEGER NOT NULL CHECK (goals_for >= 0),
    goals_against INTEGER NOT NULL CHECK (goals_against >= 0),
    shots_for INTEGER CHECK (shots_for >= 0),
    shots_against INTEGER CHECK (shots_against >= 0),
    shots_on_target_for INTEGER CHECK (shots_on_target_for >= 0),
    shots_on_target_against INTEGER CHECK (shots_on_target_against >= 0),
    corners_for INTEGER CHECK (corners_for >= 0),
    corners_against INTEGER CHECK (corners_against >= 0),
    fouls_committed INTEGER CHECK (fouls_committed >= 0),
    fouls_received INTEGER CHECK (fouls_received >= 0),
    yellow_cards INTEGER CHECK (yellow_cards >= 0),
    red_cards INTEGER CHECK (red_cards >= 0),
    PRIMARY KEY (match_id, team_key)
);
CREATE INDEX ix_team_season_date ON fact_team_match(team_key, season_key, date_key);

