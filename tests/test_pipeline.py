"""Business regression checks for ingestion and the two-perspective fact grain."""
import csv
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pipeline import REQUIRED, parse_season, team_rows


def fixture(**changes):
    row = {column: "0" for column in REQUIRED}
    row.update({"Div": "SP1", "Date": "15/08/2024", "Time": "18:00",
                "HomeTeam": "Barcelona", "AwayTeam": "Real Madrid",
                "FTHG": "2", "FTAG": "1", "FTR": "H", "HS": "10", "AS": "8",
                "HST": "5", "AST": "3", "HF": "9", "AF": "11"})
    row.update(changes)
    return row


def encode(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=sorted(REQUIRED))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


class PipelineBusinessTests(unittest.TestCase):
    def test_fixture_generates_correct_home_and_away_perspectives(self):
        rows = team_rows(parse_season(encode([fixture()]), 2024))
        home, away = rows
        self.assertEqual((home["points"], away["points"]), (3, 0))
        self.assertEqual((home["goals_for"], away["goals_for"]), (2, 1))
        self.assertEqual((home["shots_against"], away["shots_for"]), (8, 8))
        self.assertEqual((home["fouls_received"], away["fouls_committed"]), (11, 11))
        self.assertEqual(home["match_id"], away["match_id"])
        self.assertEqual(sum(row["goals_for"] for row in rows), 3)

    def test_draw_awards_one_point_to_each_club(self):
        rows = team_rows(parse_season(encode([fixture(FTHG="1", FTAG="1", FTR="D")]), 2024))
        self.assertEqual([row["points"] for row in rows], [1, 1])

    def test_missing_shots_remain_missing(self):
        rows = team_rows(parse_season(encode([fixture(HS="", HST="")]), 2024))
        self.assertIsNone(rows[0]["shots_for"])
        self.assertIsNone(rows[1]["shots_against"])

    def test_duplicate_fixture_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate fixture"):
            parse_season(encode([fixture(), fixture()]), 2024)

    def test_result_inconsistent_with_goals_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Result disagrees"):
            parse_season(encode([fixture(FTR="A")]), 2024)

    def test_impossible_shooting_statistics_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Shots on target exceed"):
            parse_season(encode([fixture(HST="11")]), 2024)

    def test_chronology_is_sorted_before_numbering_club_games(self):
        rows = team_rows(parse_season(encode([
            fixture(Date="20/08/2024", AwayTeam="Betis"), fixture()
        ]), 2024))
        home_rows = [row for row in rows if row["venue"] == "Home"]
        self.assertEqual([row["team_game_number"] for row in home_rows], [1, 2])
        self.assertEqual([row["date_key"] for row in home_rows], [20240815, 20240820])


if __name__ == "__main__":
    unittest.main()

