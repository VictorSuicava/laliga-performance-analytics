let
    Source = fnLoadCsv("dim_team.csv", {
        {"team_key", type text}, {"team_name", type text}, {"source_name", type text}
    })
in
    Source

