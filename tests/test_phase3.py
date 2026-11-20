"""
Unit and integration tests for Phase 3 (Ticket-03 "Đèn cạn dầu", Contract v1.2).
Tests fuel decay, lantern burnout, refueling, relighting (5 motes), shade draining,
weak lantern targeting, dawn survival win condition, darkness deadlock, and dynamic capacity.
"""

import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from src.core.engine import DaoDenLongSim


class TestPhase3FuelAndDawn(unittest.TestCase):
    def test_fuel_decay_and_lantern_out(self):
        # Lantern with 1.0 fuel (60 ticks) burns out
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 25.0], "lit": True, "fuel": 1.0},
            ],
            "time_left_s": 100,
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario)
        output = sim.run(65)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        out_events = [line for line in lines if line.get("name") == "lantern_out"]
        self.assertEqual(len(out_events), 1)
        self.assertEqual(out_events[0]["data"]["lantern_id"], "L1")
        self.assertEqual(out_events[0]["data"]["reason"], "fuel_empty")

        # Verify lantern state: unlit, deposited=0, ever_lit=True
        target_lan = next(l for l in sim.lanterns if l.id == "L1")
        self.assertFalse(target_lan.lit)
        self.assertEqual(target_lan.fuel, 0.0)
        self.assertTrue(target_lan.ever_lit)

    def test_refuel_lit_lantern(self):
        # Player refuels a lantern with 85 fuel using 2 motes
        scenario = {
            "player": {"pos": [0, 0, 24.5], "carried": 3, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 25.0], "lit": True, "fuel": 85.0},
            ],
            "time_left_s": 100,
        }
        inputs = {
            "frames": [
                {"tick": 0, "interact": True},
                {"tick": 1, "interact": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario, inputs_data=inputs)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        refuel_events = [line for line in lines if line.get("name") == "refuel"]
        self.assertEqual(len(refuel_events), 1)
        evt_data = refuel_events[0]["data"]
        self.assertEqual(evt_data["lantern_id"], "L1")
        # ceil((100 - 85)/10) = 2 motes needed
        self.assertEqual(evt_data["motes_used"], 2)
        self.assertEqual(evt_data["player_carried"], 1)
        self.assertEqual(evt_data["fuel_after"], 100.0)
        # Score: +5 per mote = +10
        self.assertEqual(sim.score, 10)

    def test_relight_cost_5_and_dynamic_capacity(self):
        # Lantern that was previously lit (ever_lit=True) only needs 5 motes to relight
        scenario = {
            "player": {"pos": [0, 0, 24.5], "carried": 6, "flames": 3, "successful_lights": 1},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 25.0], "lit": False, "ever_lit": True, "deposited": 0},
            ],
            "time_left_s": 100,
        }
        inputs = {
            "frames": [
                {"tick": 0, "interact": True},
                {"tick": 1, "interact": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario, inputs_data=inputs)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        lit_events = [line for line in lines if line.get("name") == "lantern_lit"]
        self.assertEqual(len(lit_events), 1)
        self.assertTrue(lit_events[0]["data"]["relight"])
        # Initial capacity was 10 + 2*1 = 12. After relight, successful_lights = 2, so capacity = 14
        self.assertEqual(lit_events[0]["data"]["new_capacity"], 14)
        # Player carried 6 - 5 = 1 mote left
        self.assertEqual(sim.player.carried, 1)
        # Score: 5*5 (deposit) + 40 (relight) = 65
        self.assertEqual(sim.score, 65)

    def test_shade_drain_weak_lantern(self):
        # Shade in wander targets a lantern with fuel < 30 and enters drain state within 2m
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 20.0], "lit": True, "fuel": 25.0},
            ],
            "shades": [
                {"id": "S1", "pos": [0, 0, 21.0], "state": "wander"},
            ],
            "time_left_s": 100,
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario)
        # S1 is 1m away from L1 (<= 2m), so at step 0 it switches to drain
        output = sim.run(65)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        drain_events = [line for line in lines if line.get("name") == "fuel_drain"]
        self.assertGreaterEqual(len(drain_events), 1)
        self.assertEqual(drain_events[0]["data"]["lantern_id"], "L1")
        self.assertEqual(drain_events[0]["data"]["shades_count"], 1)

    def test_pulse_on_draining_shade_gives_15_score(self):
        # Pulse stuns a draining shade and awards +15 points instead of +5
        scenario = {
            "player": {"pos": [0, 0, 19.0], "carried": 3, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "pos": [0, 0, 20.0], "lit": True, "fuel": 25.0},
            ],
            "shades": [
                {"id": "S1", "pos": [0, 0, 20.5], "state": "drain", "target_lantern_id": "L1"},
            ],
            "time_left_s": 100,
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
        # Score is +15 for stun on drain
        self.assertEqual(sim.score, 15)

    def test_dawn_insufficient_light_lose(self):
        # Night ends with only 2 out of 5 lanterns lit (< 60%), resulting in loss
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "lit": True, "fuel": 80.0},
                {"id": "L2", "lit": True, "fuel": 80.0},
                {"id": "L3", "lit": False},
                {"id": "L4", "lit": False},
                {"id": "L5", "lit": False},
            ],
            "time_left_s": 0.1,  # 6 ticks
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]
        over_events = [line for line in lines if line.get("name") == "game_over"]
        self.assertEqual(len(over_events), 1)
        self.assertEqual(over_events[0]["data"]["result"], "lost")
        self.assertEqual(over_events[0]["data"]["reason"], "dawn_insufficient_light")

    def test_darkness_deadlock_lose(self):
        # Absolute deadlock: all lanterns unlit, 0 motes carried, 0 motes in world
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "motes": [],
            "lanterns": [
                {"id": "L1", "lit": False},
                {"id": "L2", "lit": False},
                {"id": "L3", "lit": False},
                {"id": "L4", "lit": False},
                {"id": "L5", "lit": False},
            ],
            "time_left_s": 200,
        }
        sim = DaoDenLongSim(seed=42, scenario_data=scenario)
        output = sim.run(5)
        lines = [json.loads(line) for line in output.strip().split("\n")]
        over_events = [line for line in lines if line.get("name") == "game_over"]
        self.assertEqual(len(over_events), 1)
        self.assertEqual(over_events[0]["data"]["result"], "lost")
        self.assertEqual(over_events[0]["data"]["reason"], "darkness")


if __name__ == "__main__":
    unittest.main()
