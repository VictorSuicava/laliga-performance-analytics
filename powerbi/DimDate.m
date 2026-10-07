let
    Source = fnLoadCsv("dim_date.csv", {
        {"date_key", Int64.Type}, {"date_iso", type date}, {"year", Int64.Type},
        {"month", Int64.Type}, {"month_name", type text}, {"day", Int64.Type},
        {"weekday_name", type text}
    })
in
    Source

