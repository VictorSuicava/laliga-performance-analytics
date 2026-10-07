let
    Source = fnLoadCsv("fact_team_match.csv", {
        {"match_id", type text}, {"team_key", type text}, {"opponent_key", type text},
        {"opponent_name", type text}, {"season_key", Int64.Type}, {"date_key", Int64.Type},
        {"venue", type text}, {"team_game_number", Int64.Type}, {"result", type text},
        {"points", Int64.Type}, {"goals_for", Int64.Type}, {"goals_against", Int64.Type},
        {"shots_for", Int64.Type}, {"shots_against", Int64.Type},
        {"shots_on_target_for", Int64.Type}, {"shots_on_target_against", Int64.Type},
        {"corners_for", Int64.Type}, {"corners_against", Int64.Type},
        {"fouls_committed", Int64.Type}, {"fouls_received", Int64.Type},
        {"yellow_cards", Int64.Type}, {"red_cards", Int64.Type}
    })
in
    Source

