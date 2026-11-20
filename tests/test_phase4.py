"""
Unit and integration tests for Phase 4 (Ticket-04 "Bình minh: phát hành v1.0.0", Contract v1.3).
Tests:
- Test Contract v1.3 schema & command definitions
- Leaderboard ranking, sorting, top 10 limit, and CLI export
- Benchmark runner execution and metric validity
- Soak runner execution and memory leak stability
"""

import json
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from run_game import load_leaderboard, save_leaderboard, add_leaderboard_entry, export_leaderboard


class TestPhase4ContractAndTools(unittest.TestCase):
    def test_contract_v1_3_schema(self):
        contract_path = os.path.join(ROOT_DIR, "game.contract.json")
        self.assertTrue(os.path.exists(contract_path))
        with open(contract_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("contract_version"), "1.3")
        self.assertIn("bench_cmd", data)
        self.assertIn("soak_cmd", data)
        self.assertIn("run_cmd", data)
        self.assertIn("headless_cmd", data)

    def test_leaderboard_sorting_and_top10_cap(self):
        # Create test entries with different scores and dates
        test_entries = [
            {"name": "PlayerA", "score": 500, "nights_won": 1, "achieved_at": "2026-11-20T10:00:00+07:00", "seed": 1},
            {"name": "PlayerB", "score": 900, "nights_won": 2, "achieved_at": "2026-11-20T11:00:00+07:00", "seed": 2},
            {"name": "PlayerC", "score": 900, "nights_won": 2, "achieved_at": "2026-11-20T09:00:00+07:00", "seed": 3},  # Earlier time -> rank higher
            {"name": "PlayerD", "score": 1200, "nights_won": 3, "achieved_at": "2026-11-20T12:00:00+07:00", "seed": 4},
        ]
        for i in range(10):
            test_entries.append({
                "name": f"P{i}", "score": 100 + i * 10, "nights_won": 0, "achieved_at": "2026-11-20T12:00:00+07:00", "seed": i
            })

        save_leaderboard(test_entries)
        loaded = load_leaderboard()

        self.assertLessEqual(len(loaded), 10)
        # Highest score should be PlayerD (1200)
        self.assertEqual(loaded[0]["name"], "PlayerD")
        self.assertEqual(loaded[0]["score"], 1200)

        # Between PlayerB and PlayerC (both 900), PlayerC achieved earlier (09:00 vs 11:00), so PlayerC should be first
        self.assertEqual(loaded[1]["name"], "PlayerC")
        self.assertEqual(loaded[2]["name"], "PlayerB")

    def test_leaderboard_cli_export(self):
        out_path = os.path.join(ROOT_DIR, "data", "test_export.json")
        if os.path.exists(out_path):
            os.remove(out_path)

        cmd = [sys.executable, os.path.join(ROOT_DIR, "run_game.py"), "--export-leaderboard", out_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(out_path))

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("entries", data)
        self.assertIsInstance(data["entries"], list)
        self.assertLessEqual(len(data["entries"]), 10)

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_soak_test_runner(self):
        out_path = os.path.join(ROOT_DIR, "data", "test_soak_run.json")
        if os.path.exists(out_path):
            os.remove(out_path)

        cmd = [
            sys.executable,
            os.path.join(ROOT_DIR, "run_soak.py"),
            "--seed", "7",
            "--nights", "3",
            "--out", out_path,
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(out_path))

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["nights"], 3)
        self.assertEqual(data["crashes"], 0)
        self.assertEqual(len(data["results"]), 3)
        self.assertIn("mem_start_mb", data)
        self.assertIn("mem_end_mb", data)
        self.assertLessEqual(data["mem_end_mb"], 1.25 * data["mem_start_mb"])

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_benchmark_runner_metrics(self):
        out_path = os.path.join(ROOT_DIR, "data", "test_bench_run.json")
        if os.path.exists(out_path):
            os.remove(out_path)

        cmd = [
            sys.executable,
            os.path.join(ROOT_DIR, "run_bench.py"),
            "--seed", "42",
            "--duration", "1.5",
            "--out", out_path,
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(out_path))

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["contract_version"], "1.3")
        self.assertGreaterEqual(data["avg_fps"], 60.0)
        self.assertGreaterEqual(data["p1_low_fps"], 30.0)
        self.assertLessEqual(data["load_ms"], 10000.0)
        self.assertTrue(data["vsync_off"])
        self.assertIn("frames", data)
        self.assertIn("peak_mem_mb", data)

        if os.path.exists(out_path):
            os.remove(out_path)


if __name__ == "__main__":
    unittest.main()
