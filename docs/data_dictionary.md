# Data dictionary

## Tables

| CSV | Grain | Key | Report usage |
|---|---|---|---|
| `dim_team.csv` | One club across both seasons | `team_key` | Import as `DimTeam` |
| `dim_season.csv` | One season | `season_key` | Import as `DimSeason` |
| `dim_date.csv` | One calendar day across the observed date range | `date_key` | Import as `DimDate` |
| `fact_team_match.csv` | One club in one fixture | `match_id` + `team_key` | Import as `FactTeamMatch` |
| `fact_match.csv` | One fixture | `match_id` | Audit/export only; do not load into the initial report model |
| `mart_team_season.csv` | One club in one season | `season_key` + `team_key` | SQL reference for validation |
| `mart_season_comparison.csv` | One returning club in two consecutive seasons | `team_key` + `current_season` | SQL reference for validation |

## FactTeamMatch fields

| Field | Meaning |
|---|---|
| `match_id` | Deterministic key from competition, season and ordered home/away source club names |
| `team_key` | Club in this perspective; joins to `DimTeam` |
| `opponent_key`, `opponent_name` | Opponent identifier and display label; no active opponent relationship in v1 |
| `season_key` | Season starting year: 2024 or 2025 |
| `date_key` | Integer YYYYMMDD; joins to `DimDate` |
| `venue` | `Home` or `Away` from this club's perspective |
| `team_game_number` | Chronological club game sequence within season; not official matchday |
| `result` | `W`, `D` or `L` from this club's perspective |
| `points` | 3 for a win, 1 for a draw, 0 for a loss; no disciplinary deductions |
| `goals_for`, `goals_against` | Full-time goals scored/conceded |
| `shots_for`, `shots_against` | Club/opponent shots |
| `shots_on_target_for`, `shots_on_target_against` | Club/opponent shots on target |
| `corners_for`, `corners_against` | Club/opponent corners |
| `fouls_committed`, `fouls_received` | Fouls recorded for the club/opponent respectively |
| `yellow_cards`, `red_cards` | Club cards, using the source's definitions |

Missing optional statistics remain SQL NULL and export as empty CSV cells. The Power Query scripts convert these cells to null before assigning types. No missing statistics are replaced by zero.

Club labels are a documented display mapping from source abbreviations, using plain Latin spelling. Keys derive from the source name and are stable when source naming stays unchanged. If a future source changes an abbreviation, introduce an explicit alias mapping before merging.

Dates are exported in ISO format. Kickoff time is preserved for source ordering only; no timezone conversion is assumed. Numeric CSV values use a decimal point. Club comparison exports do not contain promoted/relegated clubs that lack one season.

