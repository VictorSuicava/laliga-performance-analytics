# Power BI learning path

The project includes a working report and the source scripts used to construct it. Use the report to learn by making small changes and checking their effects.

## Session 1: explore the report

1. Open `powerbi/LaLigaPortfolio.pbix` in Power BI Desktop.
2. On League overview, switch between 2024/25 and 2025/26. Each season must show 380 Matches.
3. Open Club diagnosis, choose FC Barcelona, and compare home/away performance across seasons.
4. Open Attack and defence and hover over the scatter points to identify clubs.
5. Open Season comparison, select 2025/26, and inspect returning and promoted clubs.

## Session 2: understand the model

- In Model view, identify the three dimension-to-fact relationships.
- Explain why FactTeamMatch has two rows per fixture.
- Compare Matches with Club Games at league and club level.
- Open Transform data and inspect DataFolder, fnLoadCsv and the typed CSV queries.
- Review the dedicated Metrics table and open Points per Game and Goal Conversion.

## Session 3: make one improvement

Add a Goals Against per Game card to Club diagnosis. Its definition is Goals Against / Club Games. Compare its home and away values and verify them against the underlying match rows.

Then replace the default FC Barcelona selection with Athletic Club, inspect the findings in `docs/findings.md`, and explain which conclusions the data can and cannot support.

## Session 4: prepare the portfolio story

Be ready to explain the business question, source coverage, table grain, missing-data policy, ratio-of-sums definitions, cross-season coverage, validation approach and one finding with a limitation.

Changes made in the PBIX do not automatically update the separate PBIP source project. Choose one editing copy, then use Desktop Save As to synchronise formats when necessary. The generator can recreate the initial project, but `--overwrite` deliberately replaces report edits.

