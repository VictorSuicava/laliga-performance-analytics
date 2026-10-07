-- Grain: one club in one season. NULL statistics remain missing, never zero-filled.
CREATE VIEW mart_team_season AS
SELECT
    f.season_key,
    s.season_label,
    f.team_key,
    t.team_name,
    COUNT(*) AS played,
    SUM(f.points) AS points,
    SUM(f.result = 'W') AS wins,
    SUM(f.result = 'D') AS draws,
    SUM(f.result = 'L') AS losses,
    SUM(f.goals_for) AS goals_for,
    SUM(f.goals_against) AS goals_against,
    SUM(f.goals_for - f.goals_against) AS goal_difference,
    SUM(f.shots_for) AS shots_for,
    SUM(f.shots_against) AS shots_against,
    SUM(f.shots_on_target_for) AS shots_on_target_for,
    COUNT(f.shots_for) AS games_with_shots,
    ROUND(1.0 * SUM(f.points) / COUNT(*), 4) AS points_per_game,
    ROUND(AVG(f.goals_for), 4) AS goals_per_game,
    ROUND(AVG(f.goals_against), 4) AS goals_against_per_game,
    ROUND(AVG(f.shots_for), 4) AS shots_per_game,
    ROUND(AVG(f.shots_against), 4) AS shots_against_per_game,
    -- Restrict both numerator and denominator to observations with both inputs.
    ROUND(1.0 * SUM(CASE WHEN f.shots_for IS NOT NULL THEN f.goals_for END)
        / NULLIF(SUM(f.shots_for), 0), 6) AS goal_conversion,
    ROUND(1.0 * SUM(CASE WHEN f.shots_for IS NOT NULL AND f.shots_on_target_for IS NOT NULL
                            THEN f.shots_on_target_for END)
        / NULLIF(SUM(CASE WHEN f.shots_for IS NOT NULL AND f.shots_on_target_for IS NOT NULL
                            THEN f.shots_for END), 0), 6) AS shot_accuracy
FROM fact_team_match f
JOIN dim_team t USING (team_key)
JOIN dim_season s USING (season_key)
GROUP BY f.season_key, s.season_label, f.team_key, t.team_name;

-- Compare only clubs present in both consecutive seasons. Promoted/relegated
-- clubs have no comparable row; absence is not zero performance.
CREATE VIEW mart_season_comparison AS
SELECT
    current.team_key,
    current.team_name,
    previous.season_label AS previous_season,
    current.season_label AS current_season,
    previous.points AS previous_points,
    current.points AS current_points,
    current.points - previous.points AS points_change,
    current.goals_for - previous.goals_for AS goals_for_change,
    current.goals_against - previous.goals_against AS goals_against_change,
    ROUND(current.points_per_game - previous.points_per_game, 4) AS ppg_change,
    ROUND(current.shots_per_game - previous.shots_per_game, 4) AS shots_per_game_change
FROM mart_team_season current
JOIN mart_team_season previous
    ON current.team_key = previous.team_key
    AND current.season_key = previous.season_key + 1;

