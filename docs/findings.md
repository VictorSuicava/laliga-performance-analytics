# Initial analytical findings

Source: Football-Data.co.uk CSV snapshots downloaded on 7 October 2026. These are descriptive observations from the validated 2024/25 and 2025/26 data. Club points and shooting measures were reconciled between raw data, SQLite and the Power BI engine.

## 1. Getafe gained points while shooting less

Getafe's points increased from **42 to 51**, the largest gain among the **17 clubs present in both seasons**. Shots per game fell from **11.42 to 9.24**, while goals scored fell from **34 to 32**. Goal conversion increased from **7.83% to 9.12%**.

This illustrates why a season review needs both outcome and process indicators. More points do not necessarily accompany greater shooting volume or more goals. The observed gain in conversion does not establish a persistent finishing skill, and the results do not establish why points improved.

**Dashboard:** Season comparison and Attack and defence; select Getafe and compare both seasons.

**Follow-up:** Examine scoreline distribution, close wins and opponent strength. xG would help assess chance quality if an appropriate source is integrated.

## 2. Athletic Club's decline accompanied both weaker conversion and more goals conceded

Athletic Club fell from **70 to 45 points**, the largest decline among returning clubs. Goals conceded rose from **29 to 58**, while goals scored fell from **54 to 43**. Shots per game increased from **12.37 to 13.74**, but goal conversion fell from **11.49% to 8.24%**.

Shooting more did not accompany better outcomes in this comparison. Both scoring and conceding indicators deteriorated. These totals support further investigation, but cannot distinguish changes in chance quality, goalkeeper performance, game state or tactical approach.

**Dashboard:** Season comparison, Club diagnosis and Attack and defence; select Athletic Club.

**Follow-up:** Inspect match chronology and home/away splits, then examine chance-quality data before attributing the decline to a specific cause.

## 3. Barcelona's point gain was concentrated at home

Barcelona's points rose from **88 to 94**. Home points increased from **43 to 57**, while away points decreased from **45 to 37**. Each venue had **19 fixtures in each season**.

The net gain of six points combines a **14-point home increase** with an **eight-point away decrease**. Home points per game rose from **2.26 to 3.00**; away points per game fell from **2.37 to 1.95**. The overall improvement therefore masks different venue trends.

**Dashboard:** Club diagnosis; select FC Barcelona and switch the season filter. The Home vs away chart shows both venue rates when the Venue slicer is cleared.

**Follow-up:** Investigate match-level scoring and opponent differences. This comparison alone does not isolate a causal home advantage.

## Reproduce the figures

```sql
SELECT * FROM mart_team_season
WHERE team_name IN ('Getafe CF', 'Athletic Club', 'FC Barcelona')
ORDER BY team_name, season_key;

SELECT team_name, season_key, venue,
       COUNT(*) AS played, SUM(points) AS points,
       1.0 * SUM(points) / COUNT(*) AS points_per_game
FROM fact_team_match
JOIN dim_team USING (team_key)
WHERE team_name = 'FC Barcelona'
GROUP BY team_name, season_key, venue;
```

These findings are provisional descriptive case studies for the portfolio, not recruitment or tactical recommendations. The dashboard does not model opponent strength, xG, injury status or player availability.

