let
    Source = fnLoadCsv("dim_season.csv", {
        {"season_key", Int64.Type}, {"season_label", type text}, {"source_code", type text}
    })
in
    Source

