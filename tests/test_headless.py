"""
Unit tests and scenario verification for Dao Den Long Headless Mode.
Updated for Phase 2 standardized parameters (Ticket-02).
"""

import json
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from src.core.engine import DaoDenLongSim


class TestDaoDenLongHeadless(unittest.TestCase):
    def test_basic_mote_pickup(self):
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [[0, 0, 1.0]],
            "lanterns": [],
            "time_left_s": 300,
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario, snapshot_every=10)
        output = sim.run(20)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        mote_events = [line for line in lines if line.get("name") == "mote_picked"]
        self.assertEqual(len(mote_events), 1)
        self.assertEqual(mote_events[0]["data"]["carried"], 1)

    def test_lantern_deposit_and_win(self):
        # Note: In Phase 2, lantern_cost changed from 5 to 10.
        # Adjusted carried to 10 to test full deposit and victory.
        scenario = {
            "player": {"pos": [0, 0, 24.0], "carried": 10, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 25.0], "deposited": 0, "lit": False},
                {"id": "L2", "lit": True},
                {"id": "L3", "lit": True},
                {"id": "L4", "lit": True},
                {"id": "L5", "lit": True},
            ],
            "time_left_s": 100,
        }
        inputs = {
            "frames": [
                {"tick": 0, "interact": True},
                {"tick": 1, "interact": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario, inputs_data=inputs, snapshot_every=10)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        dep_events = [line for line in lines if line.get("name") == "deposit"]
        lit_events = [line for line in lines if line.get("name") == "lantern_lit"]
        over_events = [line for line in lines if line.get("name") == "game_over"]

        self.assertEqual(len(dep_events), 1)
        self.assertEqual(dep_events[0]["data"]["amount"], 10)
        self.assertEqual(len(lit_events), 1)
        self.assertEqual(len(over_events), 1)
        self.assertEqual(over_events[0]["data"]["result"], "won")

    def test_pulse_stun_shade(self):
        # Note: In Phase 2, pulse_cost changed from 1 to 3.
        # Adjusted carried to 3 to satisfy activation cost.
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 3, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [0, 0, 3.0]}],
            "time_left_s": 200,
        }
        inputs = {
            "frames": [
                {"tick": 0, "pulse": True},
                {"tick": 1, "pulse": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario, inputs_data=inputs)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        pulse_events = [line for line in lines if line.get("name") == "pulse"]
        self.assertEqual(len(pulse_events), 1)
        self.assertIn("S1", pulse_events[0]["data"]["stunned_ids"])

    def test_shade_hit_and_lose(self):
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 4, "flames": 1},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "shades": [{"id": "S1", "pos": [0, 0, 0.5]}],
            "time_left_s": 200,
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        hit_events = [line for line in lines if line.get("name") == "player_hit"]
        over_events = [line for line in lines if line.get("name") == "game_over"]

        self.assertEqual(len(hit_events), 1)
        self.assertEqual(hit_events[0]["data"]["flames"], 0)
        self.assertEqual(len(over_events), 1)
        self.assertEqual(over_events[0]["data"]["result"], "lost")
        self.assertEqual(over_events[0]["data"]["reason"], "no_flames")

    def test_determinism(self):
        sim1 = DaoDenLongSim(seed=123)
        out1 = sim1.run(60)

        sim2 = DaoDenLongSim(seed=123)
        out2 = sim2.run(60)

        self.assertEqual(out1, out2)

    def test_cli_exit_code_on_bad_input(self):
        cmd = [
            sys.executable,
            os.path.join(ROOT_DIR, "run_headless.py"),
            "--seed", "42",
            "--night", "1",
            "--ticks", "10",
            "--scenario", "non_existent_file.json",
            "--out", "tmp.jsonl",
        ]
        res = subprocess.run(cmd, capture_output=True)
        self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()
