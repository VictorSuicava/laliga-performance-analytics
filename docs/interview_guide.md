# Presenting the project in an interview

Use this as a practice script. Adapt it to your own voice, reproduce the calculations and explain the code before describing the project as your work. No production deployment or measurable business impact is claimed.

## Two-minute walkthrough

"This project compares club performance in LaLiga across the complete 2024/25 and 2025/26 seasons. Its main question is which clubs improved or declined, and how results relate to shooting and home/away performance.

The source is Football-Data.co.uk. A Python pipeline downloads the CSVs, keeps source hashes and validates fixtures, scorelines and statistics. It then creates a SQLite warehouse and typed CSV exports for Power BI.

The key modelling decision is the fact-table grain: one club in one match. Every fixture has two perspectives, so there are 760 fixtures and 1,520 club appearances. This makes home/away and club comparisons straightforward, but distinct match counts must be separated from appearance counts.

The report has four pages: league overview, club diagnosis, attack and defence, and season comparison. Ratios use sums of numerators and denominators. Missing statistics remain missing, and season changes are shown only for clubs observed in both seasons.

One useful finding is that Barcelona gained six points overall, but gained 14 points at home and lost eight away. That difference is hidden by the overall total. Athletic Club also lost 25 points while conceding twice as many goals.

These are descriptive findings. The dataset has no xG or player availability, so it cannot explain tactical causes. The project reconciles SQL aggregates against raw data and the Power BI engine, and has seven tests covering business rules. A next step would be to evaluate a suitable xG source before adding a predictive model."

## Questions to rehearse

| Question | What a strong answer covers |
|---|---|
| Why two fact rows per fixture? | A consistent club perspective, explicit opponent statistics and venue. The cost is potential double-counting. |
| Why not average club conversion percentages? | A ratio of sums weights by shot volume; an unweighted average answers a different question. |
| Why preserve missing values? | A missing measurement is not a recorded zero. Paired coverage is required for shooting ratios. |
| Why are promoted clubs' deltas blank? | Absence from LaLiga is not zero points. There is no comparable prior-season observation. |
| Why single-direction relationships? | Dimension filters reach the fact table without ambiguous paths. There is no active opponent relationship. |
| How did you verify DAX? | Live engine results matched SQL for 40 club-season rows, 80 club-venue rows and 17 common-club comparisons. |
| Is this the official league table? | Points come from results. Official tie-breaking rules and deductions are outside scope. |
| Does more shooting cause more points? | The report shows associations. Chance quality, opponents and game state are not controlled for. |
| What would change for ML? | Define a prediction time, prevent future-data leakage, split chronologically and compare with simple baselines. |

## Demonstrate understanding in Power BI

1. Show that one season contains 380 Matches and 760 Club Games.
2. Filter Barcelona to Home and confirm 19 Club Games and 57 points in 2025/26.
3. Explain the two rows of one fixture in FactTeamMatch.
4. Open Points per Game and explain its denominator.
5. Select Real Oviedo in 2025/26 and explain its blank prior-season comparison.
6. Show Athletic Club's -25 change and state one limitation before suggesting further analysis.

## Portfolio or CV wording

After completing the walkthrough and understanding the implementation:

> LaLiga performance analytics: a Python and SQL pipeline for 760 fixtures, a club-match star schema and a four-page Power BI report, with business-rule tests and DAX-to-SQL reconciliation.

Avoid claims about revenue, hiring decisions, operational use or improved prediction accuracy: none of these outcomes was measured.
