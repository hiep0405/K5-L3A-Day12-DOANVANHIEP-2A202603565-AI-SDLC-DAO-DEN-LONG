"""
Comprehensive unit tests for Phase 2 new features (Ticket-02):
Dash, Wind Charms, Drifters (steal/drop), Jump Pads, Falling off island,
Safe Zone push-out, Pause mechanism, and Multi-night simulation.
"""

import json
import os
import sys
import time
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from src.core.engine import DaoDenLongSim


class TestPhase2Features(unittest.TestCase):
    def test_dash_mechanic(self):
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3, "dash_cd_ticks": 0},
            "random_motes": False,
            "random_shades": False,
        }
        inputs = {
            "frames": [
                {"tick": 0, "move": [0, 1], "dash": True},
                {"tick": 1, "dash": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, night=1, scenario_data=scenario, inputs_data=inputs, snapshot_every=10)
        output = sim.run(20)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        dash_events = [line for line in lines if line.get("name") == "dash"]
        self.assertEqual(len(dash_events), 1)

        # In 12 ticks of dash at 14 m/s + 8 ticks at 6 m/s: total distance > 3.0m
        final_snap = [l for l in lines if l.get("type") == "snapshot"][-1]
        self.assertGreater(final_snap["player"]["pos"][2], 3.0)

    def test_wind_charm_pickup_and_speedup(self):
        scenario = {
            "player": {"pos": [35, 0, 0.5], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "charms": [{"id": "C1", "pos": [35, 0, 0]}],
        }
        sim = DaoDenLongSim(seed=42, night=2, scenario_data=scenario)
        output = sim.run(5)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        charm_events = [line for line in lines if line.get("name") == "charm_picked"]
        self.assertEqual(len(charm_events), 1)
        self.assertEqual(charm_events[0]["data"]["charm_id"], "C1")
        self.assertEqual(charm_events[0]["data"]["charm_ticks"], 600)

    def test_drifter_steal_and_pulse_drop(self):
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 6, "flames": 3},
            "random_motes": False,
            "random_shades": False,
            "drifters": [{"id": "D1", "pos": [0, 0, 1.0]}],
        }
        # Tick 0: drifter steals min(3, carried) = 3 -> player carried becomes 3
        # Tick 1: pulse triggered -> drifter drops stolen motes as dropped motes
        inputs = {
            "frames": [
                {"tick": 1, "pulse": True},
                {"tick": 2, "pulse": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, night=2, scenario_data=scenario, inputs_data=inputs)
        output = sim.run(5)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        steal_events = [l for l in lines if l.get("name") == "drifter_steal"]
        drop_events = [l for l in lines if l.get("name") == "drifter_drop"]
        pulse_events = [l for l in lines if l.get("name") == "pulse"]

        self.assertEqual(len(steal_events), 1)
        self.assertEqual(steal_events[0]["data"]["amount"], 3)
        self.assertEqual(len(pulse_events), 1)
        self.assertEqual(len(drop_events), 1)
        self.assertEqual(drop_events[0]["data"]["amount"], 3)

    def test_jump_pad_launch(self):
        scenario = {
            "player": {"pos": [20.0, 0.0, 18.0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
        }
        sim = DaoDenLongSim(seed=42, night=2, scenario_data=scenario)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        snaps = [l for l in lines if l.get("type") == "snapshot"]
        # Player should be in air (pos Y > 0) moving towards island B (70,0,0)
        final_p = snaps[-1]["player"]
        self.assertGreater(final_p["pos"][1], 0.5)
        self.assertGreater(final_p["pos"][0], 21.0)

    def test_falling_off_island_penalty(self):
        scenario = {
            "player": {"pos": [50.0, -11.0, 0.0], "carried": 5, "flames": 3},
            "random_motes": False,
            "random_shades": False,
        }
        sim = DaoDenLongSim(seed=42, night=1, scenario_data=scenario)
        output = sim.run(5)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        hit_events = [l for l in lines if l.get("name") == "player_hit" and l["data"].get("by") == "fall"]
        self.assertEqual(len(hit_events), 1)
        self.assertEqual(hit_events[0]["data"]["flames"], 2)
        self.assertEqual(hit_events[0]["data"]["dropped"], 5)
        self.assertTrue(hit_events[0]["data"]["lost"])

    def test_pause_mechanism(self):
        scenario = {
            "player": {"pos": [0, 0, 0], "carried": 0, "flames": 3},
            "random_motes": False,
            "random_shades": False,
        }
        inputs = {
            "frames": [
                {"tick": 0, "pause": True},
                {"tick": 1, "pause": False},
            ]
        }
        sim = DaoDenLongSim(seed=42, night=1, scenario_data=scenario, inputs_data=inputs)
        output = sim.run(15)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        pause_events = [l for l in lines if l.get("name") == "paused"]
        self.assertEqual(len(pause_events), 1)

        paused_snaps = [l for l in lines if l.get("type") == "snapshot" and l.get("state") == "paused"]
        self.assertGreater(len(paused_snaps), 0)

    def test_night3_map_and_wind(self):
        scenario = {
            "wind_enabled": True,
            "random_motes": False,
            "random_shades": False,
        }
        sim = DaoDenLongSim(seed=42, night=3, scenario_data=scenario)
        output = sim.run(10)
        lines = [json.loads(line) for line in output.strip().split("\n")]

        snap0 = [l for l in lines if l.get("type") == "snapshot"][0]
        self.assertEqual(snap0["night"], 3)
        self.assertEqual(len(snap0["lanterns"]), 7)
        self.assertEqual(len(snap0["charms"]), 2)

    def test_full_night_performance(self):
        # DoD requirement: Run full night (up to 21,600 ticks) in <= 30 seconds
        sim = DaoDenLongSim(seed=999, night=1)
        t_start = time.time()
        sim.run(6000)  # benchmark 6000 ticks
        elapsed = time.time() - t_start

        # Extrapolate to 21600 ticks: 6000 ticks should take under 5 seconds
        self.assertLess(elapsed, 5.0)


if __name__ == "__main__":
    unittest.main()
