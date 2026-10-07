"""Download, validate and transform two complete LaLiga seasons; Python stdlib only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SEASONS = {2024: "2425", 2025: "2526"}
SOURCE = "https://www.football-data.co.uk/mmz4281/{code}/SP1.csv"
TEAM_NAMES = {
    "Alaves": "Deportivo Alaves", "Ath Bilbao": "Athletic Club",
    "Ath Madrid": "Atletico Madrid", "Barcelona": "FC Barcelona",
    "Betis": "Real Betis", "Celta": "Celta Vigo", "Elche": "Elche CF",
    "Espanol": "Espanyol", "Getafe": "Getafe CF", "Girona": "Girona FC",
    "Las Palmas": "UD Las Palmas", "Leganes": "CD Leganes",
    "Levante": "Levante UD", "Mallorca": "RCD Mallorca", "Osasuna": "CA Osasuna",
    "Oviedo": "Real Oviedo", "Real Madrid": "Real Madrid", "Sevilla": "Sevilla FC",
    "Sociedad": "Real Sociedad", "Valencia": "Valencia CF",
    "Valladolid": "Real Valladolid", "Vallecano": "Rayo Vallecano",
    "Villarreal": "Villarreal CF",
}
STAT_PAIRS = {
    "shots": ("HS", "AS"), "shots_on_target": ("HST", "AST"),
    "corners": ("HC", "AC"), "fouls": ("HF", "AF"),
    "yellow_cards": ("HY", "AY"), "red_cards": ("HR", "AR"),
}
REQUIRED = {"Div", "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"}
REQUIRED |= {column for pair in STAT_PAIRS.values() for column in pair}
MONTHS = ("", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def stable_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def integer(value: str | None, column: str, required: bool = False) -> int | None:
    if value is None or not value.strip():
        if required:
            raise ValueError(f"Missing required value: {column}")
        return None
    if not value.strip().isdigit():
        raise ValueError(f"Invalid non-negative integer in {column}: {value!r}")
    return int(value)


def parse_season(content: bytes, season: int) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    missing = REQUIRED - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing columns for {season}: {sorted(missing)}")
    matches, seen = [], set()
    for row_number, row in enumerate(reader, start=2):
        if not any(value for value in row.values()):
            continue
        if None in row:
            raise ValueError(f"Extra CSV fields at row {row_number}")
        home, away = (row[field].strip() for field in ("HomeTeam", "AwayTeam"))
        if row["Div"] != "SP1" or home == away or not home or not away:
            raise ValueError(f"Invalid fixture at row {row_number}")
        if home not in TEAM_NAMES or away not in TEAM_NAMES:
            raise ValueError(f"Unknown club name; update mapping: {home!r}, {away!r}")
        fixture = (home, away)
        if fixture in seen:
            raise ValueError(f"Duplicate fixture: {fixture}")
        seen.add(fixture)
        match_date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
        if not date(season, 7, 1) <= match_date <= date(season + 1, 6, 30):
            raise ValueError(f"Date outside season: {match_date}")
        kickoff = row["Time"].strip() or None
        if kickoff:
            datetime.strptime(kickoff, "%H:%M")
        hg, ag = (integer(row[field], field, required=True) for field in ("FTHG", "FTAG"))
        expected_result = "H" if hg > ag else "A" if ag > hg else "D"
        if row["FTR"] != expected_result:
            raise ValueError(f"Result disagrees with goals: {home} vs {away}")
        stats = {field: integer(row[field], field) for pair in STAT_PAIRS.values() for field in pair}
        for shots, on_target in (("HS", "HST"), ("AS", "AST")):
            if stats[shots] is not None and stats[on_target] is not None:
                if stats[on_target] > stats[shots]:
                    raise ValueError(f"Shots on target exceed shots: {home} vs {away}")
        matches.append({"match_id": stable_key(f"SP1:{season}:{home}:{away}"),
                        "season_key": season, "date": match_date,
                        "date_key": int(match_date.strftime("%Y%m%d")),
                        "kickoff_time": kickoff, "home": home, "away": away,
                        "home_goals": hg, "away_goals": ag, "result": expected_result,
                        "stats": stats})
    return sorted(matches, key=lambda m: (m["date"], m["kickoff_time"] or "", m["match_id"]))


def validate_complete_season(matches: list[dict]) -> None:
    appearances = Counter(m[side] for m in matches for side in ("home", "away"))
    home_games = Counter(m["home"] for m in matches)
    away_games = Counter(m["away"] for m in matches)
    if len(matches) != 380 or len(appearances) != 20:
        raise ValueError("Expected a complete season: 380 fixtures, 20 clubs")
    if any(appearances[t] != 38 or home_games[t] != 19 or away_games[t] != 19 for t in appearances):
        raise ValueError("Each club must have 38 games: 19 home and 19 away")


def team_rows(matches: list[dict]) -> list[dict]:
    rows, game_counts = [], Counter()
    for match in matches:
        for side in ("home", "away"):
            is_home = side == "home"
            own, other = ("home", "away") if is_home else ("away", "home")
            club, opponent = match[own], match[other]
            game_counts[(match["season_key"], club)] += 1
            gf, ga = match[f"{own}_goals"], match[f"{other}_goals"]
            result = "W" if gf > ga else "L" if gf < ga else "D"
            stats = {}
            for metric, (home_field, away_field) in STAT_PAIRS.items():
                own_value = match["stats"][home_field if is_home else away_field]
                other_value = match["stats"][away_field if is_home else home_field]
                if metric in ("yellow_cards", "red_cards"):
                    stats[metric] = own_value
                elif metric == "fouls":
                    stats["fouls_committed"], stats["fouls_received"] = own_value, other_value
                else:
                    stats[f"{metric}_for"], stats[f"{metric}_against"] = own_value, other_value
            rows.append({"match_id": match["match_id"], "team_key": stable_key(club),
                         "opponent_key": stable_key(opponent), "opponent_name": TEAM_NAMES[opponent],
                         "season_key": match["season_key"], "date_key": match["date_key"],
                         "venue": "Home" if is_home else "Away",
                         "team_game_number": game_counts[(match["season_key"], club)],
                         "result": result, "points": {"W": 3, "D": 1, "L": 0}[result],
                         "goals_for": gf, "goals_against": ga, **stats})
    return rows


def insert_rows(connection: sqlite3.Connection, table: str, rows: list[dict]) -> None:
    columns = list(rows[0])
    placeholders = ",".join("?" for _ in columns)
    connection.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                           [[row[c] for c in columns] for row in rows])


def export_query(connection: sqlite3.Connection, table: str, output: Path) -> None:
    cursor = connection.execute(f"SELECT * FROM {table}")
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(cursor)


def build_database(matches: list[dict], path: Path) -> dict:
    connection = sqlite3.connect(path)
    try:
        connection.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))
        clubs = sorted({m[side] for m in matches for side in ("home", "away")})
        insert_rows(connection, "dim_season", [
            {"season_key": season, "season_label": f"{season}/{str(season + 1)[-2:]}", "source_code": code}
            for season, code in SEASONS.items()])
        insert_rows(connection, "dim_team", [{"team_key": stable_key(club),
                    "team_name": TEAM_NAMES[club], "source_name": club} for club in clubs])
        dates, current = [], min(m["date"] for m in matches)
        end = max(m["date"] for m in matches)
        while current <= end:
            dates.append({"date_key": int(current.strftime("%Y%m%d")), "date_iso": current.isoformat(),
                          "year": current.year, "month": current.month, "month_name": MONTHS[current.month],
                          "day": current.day, "weekday_name": WEEKDAYS[current.weekday()]})
            current += timedelta(days=1)
        insert_rows(connection, "dim_date", dates)
        insert_rows(connection, "fact_match", [{"match_id": m["match_id"],
                    "season_key": m["season_key"], "date_key": m["date_key"],
                    "kickoff_time": m["kickoff_time"], "home_team_key": stable_key(m["home"]),
                    "away_team_key": stable_key(m["away"]), "home_goals": m["home_goals"],
                    "away_goals": m["away_goals"], "result": m["result"]} for m in matches])
        rows = team_rows(matches)
        insert_rows(connection, "fact_team_match", rows)
        connection.executescript((ROOT / "sql/analytics.sql").read_text(encoding="utf-8"))
        # Business invariants catch duplicated club rows and reversed perspectives.
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign key validation failed")
        invalid = connection.execute("""SELECT match_id FROM fact_team_match GROUP BY match_id
            HAVING COUNT(*) <> 2 OR SUM(goals_for) <> SUM(goals_against)
            OR SUM(points) NOT IN (2, 3) OR COUNT(DISTINCT venue) <> 2""").fetchall()
        if invalid:
            raise ValueError(f"Invalid team perspectives: {invalid}")
        connection.commit()
        for table in ("dim_season", "dim_team", "dim_date", "fact_match", "fact_team_match",
                      "mart_team_season", "mart_season_comparison"):
            export_query(connection, table, ROOT / "data/processed" / f"{table}.csv")
        missing = {field: sum(row[field] is None for row in rows)
                   for field in rows[0] if field in {"shots_for", "shots_against", "shots_on_target_for",
                       "shots_on_target_against", "corners_for", "corners_against", "fouls_committed",
                       "fouls_received", "yellow_cards", "red_cards"}}
        summary = {"matches": len(matches), "team_match_rows": len(rows), "distinct_clubs": len(clubs),
                   "missing_stat_values": missing,
                   "comparable_clubs": connection.execute("SELECT COUNT(*) FROM mart_season_comparison").fetchone()[0],
                   "checks": {"complete_seasons": "passed", "foreign_keys": "passed",
                              "team_perspectives": "passed", "sqlite_integrity": connection.execute(
                                  "PRAGMA integrity_check").fetchone()[0]}}
        return summary
    finally:
        connection.close()


def run(refresh: bool = False) -> dict:
    for folder in ("raw", "processed", "warehouse"):
        (ROOT / "data" / folder).mkdir(parents=True, exist_ok=True)
    matches, sources = [], []
    for season, code in SEASONS.items():
        raw_path = ROOT / "data/raw" / f"SP1_{code}.csv"
        metadata_path = raw_path.with_suffix(".metadata.json")
        url = SOURCE.format(code=code)
        if refresh or not raw_path.exists():
            request = Request(url, headers={"User-Agent": "LaLigaPerformanceAnalytics/0.1 (portfolio research)"})
            with urlopen(request, timeout=45) as response:
                content = response.read()
            # Validate before replacing a previously usable snapshot.
            parsed = parse_season(content, season)
            validate_complete_season(parsed)
            raw_path.write_bytes(content)
            metadata_path.write_text(json.dumps({"url": url, "downloaded_at_utc": datetime.now(
                timezone.utc).isoformat(), "sha256": hashlib.sha256(content).hexdigest()}, indent=2), encoding="utf-8")
        else:
            content = raw_path.read_bytes()
            parsed = parse_season(content, season)
            validate_complete_season(parsed)
        matches.extend(parsed)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {"url": url}
        sources.append({"season": season, "rows": len(parsed), "sha256": hashlib.sha256(content).hexdigest(),
                        "downloaded_at_utc": metadata.get("downloaded_at_utc"), "url": url})
    # Build a new database before replacing an existing one, preserving source snapshots.
    path = ROOT / "data/warehouse/laliga.sqlite"
    temporary = ROOT / "data/warehouse/laliga.build.sqlite"
    if temporary.exists():
        temporary.unlink()
    try:
        summary = build_database(matches, temporary)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "sources": sources, **summary}
    (ROOT / "docs/quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Download new source snapshots instead of using cached CSVs")
    run(parser.parse_args().refresh)

