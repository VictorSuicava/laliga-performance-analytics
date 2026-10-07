# Metric definitions

| Measure | Definition | Interpretation |
|---|---|---|
| Matches | Distinct match IDs in filter context | League: 380 per complete season; club: 38 |
| Club Games | Number of club-match rows | League: 760 per season; club: 38 |
| Points | Sum of club points | Meaningful primarily for club selections |
| Points per Game | Points / Club Games | Comparable between home/away subsets |
| Goals For / Against | Sum of club goals scored/conceded | League-wide totals are equal |
| Goal Difference | Goals For - Goals Against | Descriptive club goal balance |
| Goals per Game | Goals For / Club Games | League selection means goals per club appearance |
| Shots per Game | Average non-missing shots_for | Display coverage when missing values exist |
| Shots Against per Game | Average non-missing shots_against | Volume conceded, not chance quality |
| Shot Accuracy | Sum shots on target / sum shots, restricted to paired non-missing rows | Format as percentage |
| Goal Conversion | Sum goals / sum shots, restricted to rows with shots recorded | Includes own goals; not a pure finishing statistic |
| Clean Sheet Rate | Club games with zero conceded / Club Games | Format as percentage |
| Points Change | Current points - previous-season points, for one club and season | Blank if either season is missing |

Use **ratio of sums**, not average of match percentages. `DIVIDE` returns a blank for a zero denominator by default. Missing comparison values must remain blank, not become zero.

The DAX definitions are supplied in `powerbi/measures.dax`; create each measure separately in the dedicated Metrics table. The project definitions have been executed in Power BI Desktop, and core aggregates and ratios were reconciled with SQL. See `docs/powerbi_validation.json` for the checked scope. Revalidate after changing measures or data.

