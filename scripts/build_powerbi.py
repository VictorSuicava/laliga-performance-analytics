"""Build a local Power BI project (PBIP + PBIR + TMSL) from validated CSV exports.

The generated semantic model contains a machine-specific DataFolder parameter and
is excluded from Git. Re-run on a new machine, then refresh in Power BI Desktop.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERBI = ROOT / "powerbi"
REPORT = POWERBI / "LL.Report"
MODEL = POWERBI / "LL.SemanticModel"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/"
TABLE_FILES = {"DimTeam": "dim_team", "DimSeason": "dim_season",
               "DimDate": "dim_date", "FactTeamMatch": "fact_team_match"}


def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def identifier(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def literal(value) -> dict:
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, (int, float)):
        text = f"{value}D"
    else:
        text = "'" + str(value).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": text}}}


def colour(value: str) -> dict:
    return {"solid": {"color": literal(value)}}


def column(table: str, name: str, label: str | None = None) -> dict:
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
            "queryRef": f"{table}.{name}", "nativeQueryRef": label or name,
            "displayName": label or name}


def measure(name: str, label: str | None = None) -> dict:
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "Metrics"}}, "Property": name}},
            "queryRef": f"Metrics.{name}", "nativeQueryRef": name,
            "displayName": label or name}


def selection_filter(table: str, field: str, value: str) -> dict:
    return {"filter": {"Version": 2, "From": [{"Name": "s", "Entity": table, "Type": 0}],
        "Where": [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": field}}],
            "Values": [[{"Literal": {"Value": "'" + value.replace("'", "''") + "'"}}]]
        }}}]}}


def formatting(title: str, background: str = "#FFFFFF", border: bool = True) -> dict:
    return {
        "title": [{"properties": {"show": literal(bool(title)), "text": literal(title),
                    "fontSize": literal(12), "fontColor": colour("#182230"), "bold": literal(True)}}],
        "background": [{"properties": {"show": literal(True), "color": colour(background), "transparency": literal(0)}}],
        "border": [{"properties": {"show": literal(border), "color": colour("#E4E9F0"), "radius": literal(8)}}],
    }


class Page:
    def __init__(self, name: str, display_name: str):
        self.name = identifier(name)
        self.path = REPORT / "definition/pages" / self.name
        self.number = 0
        write_json(self.path / "page.json", {
            "$schema": SCHEMA + "definition/page/2.1.0/schema.json",
            "name": self.name, "displayName": display_name, "displayOption": "FitToPage",
            "height": 720, "width": 1280,
            "objects": {"background": [{"properties": {"color": colour("#F7F9FC"), "transparency": literal(0)}}]},
        })

    def visual(self, kind: str, title: str, bounds: tuple, roles: dict | None = None,
               objects: dict | None = None, sort: dict | None = None) -> None:
        self.number += 1
        visual_name = identifier(f"{self.name}:{self.number}")
        x, y, width, height = bounds
        config = {"visualType": kind, "drillFilterOtherVisuals": True,
                  "visualContainerObjects": formatting(title)}
        if kind == "textbox":
            config["visualContainerObjects"] = {
                "title": [{"properties": {"show": literal(False)}}],
                "background": [{"properties": {"show": literal(False)}}],
                "border": [{"properties": {"show": literal(False)}}],
                "padding": [{"properties": {side: literal(0) for side in ("top", "bottom", "left", "right")}}],
            }
        if roles:
            query = {"queryState": {role: {"projections": projections} for role, projections in roles.items()}}
            if sort:
                query["sortDefinition"] = {"sort": [sort], "isDefaultSort": False}
            config["query"] = query
        if objects:
            config["objects"] = objects
        if kind == "barChart":
            config.setdefault("objects", {}).setdefault("categoryAxis", [{"properties": {
                "preferredCategoryWidth": literal(14), "fontSize": literal(9),
                "innerPadding": literal(20)}}])
        if kind == "tableEx":
            config.setdefault("objects", {}).update({
                "grid": [{"properties": {"rowPadding": literal(0)}}],
                "values": [{"properties": {"fontSize": literal(9)}}],
                "columnHeaders": [{"properties": {"fontSize": literal(9), "wordWrap": literal(False)}}],
                "total": [{"properties": {"fontSize": literal(9)}}],
            })
        write_json(self.path / "visuals" / visual_name / "visual.json", {
            "$schema": SCHEMA + "definition/visualContainer/2.7.0/schema.json",
            "name": visual_name,
            "position": {"x": x, "y": y, "z": self.number, "height": height, "width": width,
                         "tabOrder": self.number},
            "visual": config,
        })

    def text(self, text: str, bounds: tuple, size: int = 12, bold: bool = False) -> None:
        self.visual("textbox", "", bounds, objects={"general": [{"properties": {
            "paragraphs": [{"textRuns": [{"value": text, "textStyle": {
                "fontFamily": "Segoe UI", "fontSize": f"{size}pt", "fontWeight": "bold" if bold else "normal",
                "color": "#182230"}}]}]}}]})

    def header(self, title: str, subtitle: str) -> None:
        self.text(title, (24, 14, 920, 50), 24, True)
        self.text(subtitle, (24, 66, 930, 42), 11)
        self.slicer("DimSeason", "season_label", "Season", (992, 16, 264, 90), "2025/26")
        self.text("Source: Football-Data.co.uk  |  Snapshot: 07 Oct 2026  |  Full-time results", (24, 680, 1232, 28), 9)

    def slicer(self, table: str, field: str, title: str, bounds: tuple, selected: str | None = None) -> None:
        props = {"mode": literal("Dropdown")}
        if field == "venue":
            props["mode"] = literal("Basic")
        objects = {"data": [{"properties": props}], "header": [{"properties": {"show": literal(False)}}], "selection": [{"properties": {
            "singleSelect": literal(True), "selectAllCheckboxEnabled": literal(False)}}]}
        if selected:
            objects["general"] = [{"properties": {"filter": selection_filter(table, field, selected)}}]
        self.visual("slicer", title, bounds, {"Values": [column(table, field, title)]}, objects)

    def card(self, metric: str, bounds: tuple, title: str | None = None) -> None:
        self.visual("card", title or metric, bounds, {"Values": [measure(metric)]}, {
            "labels": [{"properties": {"fontSize": literal(30), "color": colour("#136F63"), "labelDisplayUnits": literal(1)}}],
            "categoryLabels": [{"properties": {"show": literal(False)}}],
        })


def read_measures() -> list[dict]:
    text = (POWERBI / "measures.dax").read_text(encoding="utf-8")
    text = re.sub(r"(?m)^//.*$", "", text)
    definitions = re.split(r"\n\s*\n", text.strip())
    measures = []
    for definition in definitions:
        name, expression = definition.split("=", 1)
        name = name.strip()
        fmt = "0.0%" if name in ("Shot Accuracy", "Goal Conversion", "Clean Sheet Rate", "Shot Data Coverage") else \
              "0.00" if "per Game" in name or "PPG" in name else "#,0"
        entry = {"name": name, "expression": expression.strip(), "displayFolder": "Performance",
                 "lineageTag": identifier("measure:" + name)}
        if name != "Club Label":
            entry["formatString"] = fmt
        measures.append(entry)
    return measures


def build_model(data_folder: Path) -> None:
    tables = []
    for table, csv_name in TABLE_FILES.items():
        m_query = (POWERBI / f"{table}.m").read_text(encoding="utf-8")
        with (data_folder / f"{csv_name}.csv").open(encoding="utf-8", newline="") as handle:
            columns = next(csv.reader(handle))
        types = dict(re.findall(r'\{"([^\"]+)",\s*(type\s+\w+|Int64.Type)\}', m_query))
        model_columns = []
        for name in columns:
            datatype = {"type text": "string", "type date": "dateTime", "Int64.Type": "int64"}[types[name]]
            field = {"name": name, "dataType": datatype, "sourceColumn": name,
                     "summarizeBy": "none", "lineageTag": identifier(table + ":" + name)}
            if name.endswith("_key") or name == "match_id" or name == "source_name":
                field["isHidden"] = True
            if table == "DimDate" and name == "date_iso":
                field.update({"isKey": True, "formatString": "dd MMM yyyy"})
            if table == "DimDate" and name == "month_name":
                field["sortByColumn"] = "month"
            model_columns.append(field)
        model_table = {"name": table, "lineageTag": identifier(table), "columns": model_columns,
                       "partitions": [{"name": table, "mode": "import", "source": {"type": "m", "expression": m_query}}]}
        if table == "DimDate":
            model_table["dataCategory"] = "Time"
        tables.append(model_table)
    tables.append({"name": "Metrics", "lineageTag": identifier("Metrics"),
        "columns": [{"name": "_placeholder", "dataType": "int64", "sourceColumn": "_placeholder", "isHidden": True}],
        "partitions": [{"name": "Metrics", "mode": "import", "source": {"type": "m",
                         "expression": "#table(type table [_placeholder = Int64.Type], {{0}})"}}],
        "measures": read_measures()})
    function = (POWERBI / "fnLoadCsv.m").read_text(encoding="utf-8")
    model = {"name": "LaLigaPerformance", "compatibilityLevel": 1600,
        "model": {"culture": "en-US", "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US", "tables": tables,
            "expressions": [
                {"name": "DataFolder", "kind": "m", "expression": '"' + str(data_folder).replace('"', '""') +
                    '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'},
                {"name": "fnLoadCsv", "kind": "m", "expression": function}],
            "relationships": [{"name": identifier("relationship:" + table), "fromTable": "FactTeamMatch",
                "fromColumn": field, "toTable": table, "toColumn": field,
                "crossFilteringBehavior": "oneDirection"}
                for table, field in (("DimTeam", "team_key"), ("DimSeason", "season_key"), ("DimDate", "date_key"))],
            "annotations": [{"name": "PBI_QueryOrder", "value": json.dumps(["DataFolder", "fnLoadCsv", *TABLE_FILES])},
                            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"}],
        }}
    write_json(MODEL / "model.bim", model)
    write_json(MODEL / "definition.pbism", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json", "version": "4.0", "settings": {"qnaEnabled": False}})


def build_report() -> None:
    club = column("DimTeam", "team_name", "Club")
    def descending(metric):
        return {"field": measure(metric)["field"], "direction": "Descending"}
    overview = Page("overview", "01 | League overview")
    overview.header("LaLiga | Performance Analytics", "Results, shooting and club trends across two complete seasons.")
    for index, metric in enumerate(("Matches", "Goals For", "Goals per Game", "Shot Accuracy")):
        overview.card(metric, (24 + index * 312, 124, 296, 104), "Goals per club game" if metric == "Goals per Game" else None)
    overview.visual("barChart", "Points by club", (24, 248, 452, 412), {
        "Category": [club], "Y": [measure("Points")]}, sort=descending("Points"))
    overview.visual("tableEx", "Club performance | sorted by points", (496, 248, 760, 412), {
        "Values": [club, *[measure(name) for name in ("Club Games", "Points", "Goals For", "Goals Against", "Goal Difference", "Points per Game")]]},
        sort=descending("Points"))

    diagnosis = Page("diagnosis", "02 | Club diagnosis")
    diagnosis.header("Club diagnosis", "Select a club to inspect results, chronology and home/away performance.")
    diagnosis.slicer("DimTeam", "team_name", "Club", (24, 124, 296, 92), "FC Barcelona")
    diagnosis.slicer("FactTeamMatch", "venue", "Venue", (340, 124, 200, 92))
    for index, metric in enumerate(("Points per Game", "Goal Difference", "Clean Sheet Rate")):
        diagnosis.card(metric, (560 + index * 232, 124, 216, 92))
    diagnosis.visual("lineChart", "Cumulative points by match date", (24, 236, 746, 264), {
        "Category": [column("DimDate", "date_iso", "Match date")], "Y": [measure("Cumulative Points")]},
        sort={"field": column("DimDate", "date_iso")["field"], "direction": "Ascending"})
    diagnosis.visual("clusteredColumnChart", "Home vs away | points per game", (790, 236, 466, 264), {
        "Category": [column("FactTeamMatch", "venue", "Venue")], "Y": [measure("Points per Game")]})
    diagnosis.visual("tableEx", "Match history", (24, 520, 1232, 140), {
        "Values": [column("DimDate", "date_iso", "Date"), column("FactTeamMatch", "opponent_name", "Opponent"),
            column("FactTeamMatch", "venue", "Venue"), column("FactTeamMatch", "result", "Result"),
            measure("Goals For"), measure("Goals Against"), measure("Points")]},
        sort={"field": column("DimDate", "date_iso")["field"], "direction": "Descending"})

    shooting = Page("shooting", "03 | Attack and defence")
    shooting.header("Attack and defence", "Shooting volume and conversion describe performance; they do not establish chance quality or causality.")
    shooting.visual("scatterChart", "Shooting volume vs points per game", (24, 124, 568, 258), {
        "Category": [club], "X": [measure("Shots per Game")], "Y": [measure("Points per Game")],
        "Size": [measure("Goals For")], "Tooltips": [measure("Club Games")]}, objects={
            "valueAxis": [{"properties": {"start": literal(0), "end": literal(3)}}],
            "categoryAxis": [{"properties": {"start": literal(0), "end": literal(20)}}]})
    shooting.visual("scatterChart", "Shot accuracy vs goal conversion", (24, 402, 568, 258), {
        "Category": [club], "X": [measure("Shot Accuracy")], "Y": [measure("Goal Conversion")],
        "Tooltips": [measure("Club Games"), measure("Shot Data Coverage")]}, objects={
            "categoryAxis": [{"properties": {"start": literal(0.24), "end": literal(0.44)}}],
            "valueAxis": [{"properties": {"start": literal(0), "end": literal(0.20)}}]})
    shooting.visual("tableEx", "Shooting metrics | all clubs", (612, 124, 644, 480), {
        "Values": [club, measure("Shots per Game", "Shots/game"),
                   measure("Shots Against per Game", "Shots allowed"),
                   measure("Shot Accuracy", "Accuracy"), measure("Goal Conversion", "Conversion"),
                   measure("Shot Data Coverage", "Coverage")]})
    shooting.text("Shots allowed is opponent shooting volume per club game.\nCoverage indicates the share of club games with paired shooting data.",
                  (612, 624, 644, 40), 10)

    comparison = Page("comparison", "04 | Season comparison")
    comparison.header("Season comparison", "Changes are shown only for clubs present in both seasons. Select 2025/26 to compare with 2024/25.")
    comparison.visual("barChart", "Points change vs previous season", (24, 124, 604, 446), {
        "Category": [club], "Y": [measure("Points Change")]}, sort=descending("Points Change"))
    comparison.visual("tableEx", "Club results and prior-season coverage", (648, 124, 608, 476), {
        "Values": [club, measure("Points"), measure("Previous Season Points", "Prior points"),
                   measure("Points Change"), measure("Points per Game", "PPG"), measure("PPG Change")]},
        sort=descending("Points Change"))
    comparison.text("Blank prior-season values indicate clubs absent from that season.\nChanges compare complete seasons for returning clubs. Official tie-breaks and deductions are outside scope.",
                    (24, 620, 1232, 40), 10)

    names = [page.name for page in (overview, diagnosis, shooting, comparison)]
    write_json(REPORT / "definition/pages/pages.json", {
        "$schema": SCHEMA + "definition/pagesMetadata/1.0.0/schema.json", "pageOrder": names, "activePageName": names[0]})
    write_json(REPORT / "definition/version.json", {
        "$schema": SCHEMA + "definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    theme_name = "LaLigaTheme"
    write_json(REPORT / "StaticResources/RegisteredResources" / theme_name,
               json.loads((POWERBI / "theme.json").read_text(encoding="utf-8")))
    theme_version = {"visual": "2.7.0", "page": "2.1.0", "report": "3.2.0"}
    write_json(REPORT / "definition/report.json", {
        "$schema": SCHEMA + "definition/report/3.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU06", "reportVersionAtImport": theme_version, "type": "SharedResources"},
            "customTheme": {"name": theme_name, "reportVersionAtImport": theme_version, "type": "RegisteredResources"}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items": [
            {"name": theme_name, "path": theme_name, "type": "CustomTheme"}]}],
    })
    write_json(REPORT / "definition.pbir", {"$schema": SCHEMA + "definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../LL.SemanticModel"}}})
    write_json(POWERBI / "LaLiga.pbip", {"version": "1.0", "artifacts": [{"report": {"path": "LL.Report"}}],
                                       "settings": {"enableAutoRecovery": True}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-folder", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly regenerate existing project definitions; replaces report edits")
    args = parser.parse_args()
    if (MODEL / "definition").exists():
        parser.error("A Desktop-authored TMDL model exists. Keep it or use a separate project folder; this builder emits TMSL.")
    if (MODEL / "model.bim").exists() and not args.overwrite:
        parser.error("The project already exists. Open LaLiga.pbip, or use --overwrite only to deliberately regenerate its definitions.")
    build_model(args.data_folder.resolve())
    if not REPORT.exists() or args.overwrite:
        build_report()
    else:
        print("Existing report definitions preserved; local semantic model created.")
    print(f"Power BI project created: {POWERBI / 'LaLiga.pbip'}")
    print("Open in Power BI Desktop and refresh to load local CSV data.")

