# Analytical brief

## Scope and decisions

The first release is a club and match analysis for two complete seasons. The report and portfolio documentation are in English. Instructions during the learning sessions can be explained in Portuguese.

Use **2025/26 as the default season** and **2024/25 as the comparison**. The current incomplete season is outside this initial release. Use a single-season selection for tables and club diagnostics; use explicit comparison measures for year-over-year changes.

## Report pages

| Page | Question | Visuals and interactions |
|---|---|---|
| League overview | How did clubs perform in the selected season? | Season selector, match and goal cards, club table with points/goals/goal difference, horizontal points bar chart |
| Club diagnosis | How did one club's results evolve? | Single club selector, season selector, home/away filter, PPG cards, cumulative points by date, recent match table |
| Attack and defence | Do shooting volume and conversion accompany results? | Shots per club game vs PPG scatter, goal conversion vs shot accuracy scatter, shots conceded comparison, tooltips showing sample size |
| Season comparison | Which returning clubs changed most? | Points and PPG changes by club, goals for/against comparison, previous-season absence shown as blank |

Use actual match date or `team_game_number` for chronology. Label the latter **Club game number**. Postponements mean it cannot be called Matchday or Round.

## Design

- Canvas: 16:9, light background, consistent spacing and restrained colours.
- Use a season selector on each page and synchronise selections where appropriate.
- Club selector: single-select on the diagnosis page; do not synchronise this club filter onto the whole league overview.
- Home/away comparisons must use per-game metrics or display the number of club appearances.
- Percentage metrics remain numeric and receive percentage formatting.
- Titles describe what the chart shows, rather than implying untested causal explanations.
- Include a visible source note and snapshot date.

## Acceptance criteria

- Each full-season league filter returns 380 distinct matches.
- Each full-season club filter returns 38 club games, including 19 home and 19 away.
- Club points, goals and shooting metrics agree with `mart_team_season.csv`.
- Returning clubs' changes agree with `mart_season_comparison.csv`.
- Promoted clubs show a blank prior-season comparison, with an explanatory label.
- No KPI claims to measure xG, player performance or official league ranking.
- Source files, data types and relationships refresh without errors.

## Final analytical write-up

For each of three findings, provide the question, selected filters, numerical result, relevant chart, plausible interpretation, limitations and a follow-up question. Do not draft findings before inspecting validated outputs.

