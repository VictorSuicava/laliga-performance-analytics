# Build the Power BI report

The first working report is available as `powerbi/LaLigaPortfolio.pbix`; its core measures have been checked in Power BI Desktop. This guide explains how to rebuild the model manually as a learning exercise. The pipeline's SQL checks alone do not validate Desktop rendering or DAX execution.

## 1. Generate the data

Run `python scripts/pipeline.py` from the project folder. Open `docs/quality_report.json` and confirm 760 fixtures and 1,520 club-match rows.

## 2. Create the parameter and queries

1. Open Power BI Desktop and create a blank report.
2. Open **Transform data**, then **Manage parameters > New parameter**.
3. Name the parameter `DataFolder`, set its type to Text and set its current value to the absolute path of this project's `data\processed` folder. Do not include a trailing slash.
4. Create a blank query, open **Advanced Editor**, paste `powerbi/fnLoadCsv.m` and name it `fnLoadCsv`.
5. Create four blank queries, pasting the matching `.m` files and naming them exactly `DimTeam`, `DimSeason`, `DimDate` and `FactTeamMatch`.
6. **Close & Apply**. Check that the dimension keys are unique and statistics are Whole Number. ISO date text must become Date.

Do not import the analytical marts into this first model: they are reference exports for validation. Do not activate an opponent relationship.

## 3. Create relationships

In **Model view**, use three active relationships with **single-direction filtering from dimension to fact**, cardinality **one to many**:

| Dimension | Dimension column | Fact column |
|---|---|---|
| DimTeam | team_key | FactTeamMatch.team_key |
| DimSeason | season_key | FactTeamMatch.season_key |
| DimDate | date_key | FactTeamMatch.date_key |

Remove incorrect automatically detected relationships. Mark `DimDate` as the date table using `date_iso`. Sort `month_name` by `month`. Hide technical keys from report view, retaining them in the model.

## 4. Create measures

Create a dedicated table called `Metrics` using **Enter data** (one placeholder value is sufficient), and hide its placeholder column. Create each measure from `powerbi/measures.dax` individually in `Metrics` using **New measure**. A dedicated table avoids case-insensitive name collisions between the `points` column and the `Points` measure. Names in the formulas depend on the exact query names above. Use comma argument separators unless Desktop is configured for localised DAX separators.

- Whole numbers: Matches, Club Games, Points, Wins, Draws, Losses, Goals For/Against and Goal Difference.
- Two decimal places: per-game measures.
- Percentage, one decimal place: Shot Accuracy, Goal Conversion, Shot Data Coverage and Clean Sheet Rate.

Cumulative Points accumulates within the selected date range. Use a single club and season and an unfiltered full-season date range for a full-season curve.

Previous Season Points removes only the season filter: venue and other selections remain in effect. A date filter confined to the current season will exclude prior-season rows. **Do not place a date or game-number filter on the Season comparison page**; use one season selector and a table with one row per club instead.

## 5. Build the first page

1. Import `powerbi/theme.json` through **View > Themes > Browse for themes**.
2. Add a single-select slicer using `DimSeason[season_label]`, defaulting to 2025/26.
3. Add cards for Matches and Goals For.
4. Add a table with `DimTeam[team_name]`, Club Games, Points, Goals For, Goals Against, Goal Difference and Points per Game.
5. Sort the table by Points descending. Label it **Club performance**, not Official standings: official ties are not reconstructed.
6. Add a horizontal bar chart of Points by club.
7. Add a source caption: **Source: Football-Data.co.uk | Complete seasons 2024/25 and 2025/26** and the download date from the quality report.

Build the remaining pages from `docs/project_brief.md` after the first page reconciles with SQL.

## 6. Validate before publishing

- Full league, one season: Matches = 380; Club Games = 760.
- Single club, one season: Matches = Club Games = 38.
- Single club and Home: Club Games = 19; Away: 19.
- Compare club totals and ratios with `data/processed/mart_team_season.csv`.
- Select a promoted club in 2025/26: Previous Season Points and Points Change are blank.
- In the season comparison table, returning club changes match `mart_season_comparison.csv`.
- At league level, Goals For = Goals Against. Per-game measures refer to club appearances.
- Test slicers, chart interactions, missing data and refresh.

Save a learning copy under a separate filename in `powerbi/` so the validated `LaLigaPortfolio.pbix` remains available. PBIX binaries are ignored by default; screenshots, the PBIR project and a short walkthrough can be shared independently of Power BI Service access.

## Official references

- [CSV import in Power Query](https://learn.microsoft.com/en-us/powerquery-m/csv-document)
- [DIVIDE in DAX](https://learn.microsoft.com/en-us/dax/divide-function-dax)

