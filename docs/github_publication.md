# GitHub publication guide

Project repository: [VictorSuicava/laliga-performance-analytics](https://github.com/VictorSuicava/laliga-performance-analytics).

For a new machine, clone this repository and follow the README:

```powershell
git clone https://github.com/VictorSuicava/laliga-performance-analytics.git
cd laliga-performance-analytics
python scripts/pipeline.py
python scripts/build_powerbi.py
```

Open `powerbi/LaLiga.pbip` and refresh in Power BI Desktop. The loaded `LaLigaPortfolio.pbix` is a local artifact.

## Repository presentation

- Suggested name: `laliga-performance-analytics`
- Suggested description: `LaLiga club performance across 2024/25 and 2025/26 with Python, SQL and a four-page Power BI dashboard.`
- Suggested topics: `power-bi`, `data-analysis`, `python`, `sql`, `football`, `sports-analytics`, `portfolio`.
- Pin the repository on your profile after publication.
- The README includes report previews, findings, source attribution and reproduction instructions.

## Publish as a standalone project

This project has its own Git repository. If keeping it inside a folder containing other projects, run Git commands from this project's root. Do not push unrelated projects into this repository.

The publication archive in `output/release/` contains the shareable project files at its root. It excludes cached downloads, generated datasets, the loaded PBIX, machine-specific paths and application caches.

1. Create an empty GitHub repository using the suggested name. Do not add a README when creating it.
2. Extract the publication archive to a new folder outside the parent Git repository.
3. In that extracted folder, run the commands below. Replace the remote URL with your actual repository URL.

```powershell
git init -b main
git add .
git commit -m "Add LaLiga analytics portfolio project"
git remote add origin https://github.com/YOUR_USERNAME/laliga-performance-analytics.git
git push -u origin main
```

Use your own GitHub authentication when requested. No token needs to be pasted into project files.

## What readers can access

The four screenshots and the PDF can be viewed without Power BI. The PBIP report definitions are included. To generate the local semantic model and load the report, readers run the Python pipeline and report builder from the README, then refresh in Power BI Desktop.

The loaded PBIX embeds source observations and a local refresh path. It is kept local by default. Review the data provider's redistribution terms before adding it or source CSVs as public release assets. The static previews contain derived aggregates and selected match rows with source attribution; no unrestricted source-data redistribution license is asserted.

## Keep the portfolio coherent

Use the same business question in the repository description, README and interview walkthrough. Start with one finding, explain the model decision behind it and close with a limitation. Add a short recorded walkthrough after you can explain the filters and measures independently.
