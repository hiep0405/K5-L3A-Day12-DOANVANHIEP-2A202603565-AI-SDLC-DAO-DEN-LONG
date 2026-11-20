"""
Core simulation engine for Dao Den Long (Island of Lanterns).
Implements Test Contract v1.0 specifications with exact determinism and 60 tick/s model.
"""

import json
import math
import random
import sys
from typing import Dict, Any, List, Optional, Tuple


class Player:
    def __init__(self, pos: List[float], flames: int = 3, carried: int = 0):
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.flames = int(flames)
        self.carried = int(carried)
        self.invuln_timer = 0.0
        self.pulse_cooldown = 0.0


class Lantern:
    def __init__(self, id: str, pos: List[float], lit: bool = False, deposited: int = 0):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.lit = bool(lit)
        self.deposited = int(deposited)


class Shade:
    def __init__(self, id: str, pos: List[float], state: str = "chase"):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.state = state  # "chase" or "stunned"
        self.stun_timer = 0.0


class Mote:
    def __init__(self, id: str, pos: List[float]):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]


def dist_xz(p1: List[float], p2: List[float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2)


class DaoDenLongSim:
    def __init__(
        self,
        seed: int = 42,
        night: int = 1,
        tuning: Optional[Dict[str, Any]] = None,
        scenario_data: Optional[Dict[str, Any]] = None,
        inputs_data: Optional[Dict[str, Any]] = None,
        snapshot_every: int = 10,
    ):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.night = night
        self.snapshot_every = max(1, int(snapshot_every))

        # Default tuning from Test Contract v1.0
        self.tuning = {
            "player_speed": 6.0,
            "carry_capacity": 10,
            "lantern_cost": 5,
            "lantern_count_night1": 5,
            "pickup_radius": 1.5,
            "interact_radius": 2.5,
            "pulse_cost": 1,
            "pulse_radius": 5.0,
            "night1_duration_s": 300.0,
            "flames": 3,
            "invuln_s": 1.5,
            "hit_drop_ratio": 0.5,
            "pulse_stun_s": 3.0,
            "pulse_push_m": 2.0,
            "pulse_cooldown_s": 2.0,
            "safe_radius": 4.0,
            "shade_speed": 3.5,
            "shade_hit_radius": 1.0,
            "fall_enabled": False,
            "score": {
                "per_mote": 10,
                "per_lantern": 100,
                "per_stun": 20,
                "per_second_left": 1,
                "per_flame_left": 50,
            },
        }
        if tuning:
            self.tuning.update(tuning)

        self.time_left_s = float(self.tuning["night1_duration_s"])
        self.score = 0
        self.state = "playing"  # "playing", "won", "lost"
        self.sim_tick = 0

        # Player setup
        self.player = Player(pos=[0.0, 0.0, 0.0], flames=self.tuning["flames"], carried=0)

        # Default 5 Lanterns arranged in circle of radius 25m
        self.lanterns: List[Lantern] = []
        for i in range(5):
            angle = i * (2.0 * math.pi / 5.0)
            lx = round(25.0 * math.sin(angle), 3)
            lz = round(25.0 * math.cos(angle), 3)
            self.lanterns.append(Lantern(id=f"L{i+1}", pos=[lx, 0.0, lz], lit=False, deposited=0))

        # Default Motes
        self.motes: List[Mote] = []
        for i in range(25):
            r = self.rng.uniform(6.0, 42.0)
            a = self.rng.uniform(0.0, 2.0 * math.pi)
            mx = round(r * math.sin(a), 3)
            mz = round(r * math.cos(a), 3)
            self.motes.append(Mote(id=f"M{i+1}", pos=[mx, 0.0, mz]))

        # Default Shades
        self.shades: List[Shade] = []
        base_angles = [0.5, 2.6, 4.7]
        for i, ba in enumerate(base_angles):
            sx = round(30.0 * math.sin(ba), 3)
            sz = round(30.0 * math.cos(ba), 3)
            self.shades.append(Shade(id=f"S{i+1}", pos=[sx, 0.0, sz], state="chase"))

        # Apply Scenario override if given
        if scenario_data:
            self._apply_scenario(scenario_data)

        # Parse & index input frames
        self.input_frames: Dict[int, Dict[str, Any]] = {}
        if inputs_data:
            self._parse_inputs(inputs_data)

        # Current input state
        self.cur_move = [0.0, 0.0]
        self.cur_cam_yaw_deg = 0.0
        self.cur_jump = False
        self.cur_interact = False
        self.cur_pulse = False

        # Output collector
        self.output_lines: List[str] = []

    def _apply_scenario(self, sc: Dict[str, Any]):
        if "time_left_s" in sc:
            self.time_left_s = float(sc["time_left_s"])

        if "player" in sc:
            p_data = sc["player"]
            if "pos" in p_data:
                self.player.pos = [float(x) for x in p_data["pos"]]
            if "flames" in p_data:
                self.player.flames = int(p_data["flames"])
            if "carried" in p_data:
                self.player.carried = int(p_data["carried"])

        if sc.get("random_motes") is False:
            self.motes = []
        if "motes" in sc:
            self.motes = [
                Mote(id=f"M{i+1}", pos=[float(p[0]), float(p[1]), float(p[2])])
                for i, p in enumerate(sc["motes"])
            ]

        if sc.get("random_shades") is False:
            self.shades = []
        if "shades" in sc:
            self.shades = [
                Shade(
                    id=item.get("id", f"S{i+1}"),
                    pos=[float(item["pos"][0]), float(item["pos"][1]), float(item["pos"][2])],
                    state="chase",
                )
                for i, item in enumerate(sc["shades"])
            ]

        if "lanterns" in sc:
            for item in sc["lanterns"]:
                lid = item.get("id")
                target = next((lan for lan in self.lanterns if lan.id == lid), None)
                if not target:
                    target = Lantern(id=lid, pos=[0.0, 0.0, 0.0], lit=False, deposited=0)
                    self.lanterns.append(target)
                if "pos" in item:
                    target.pos = [float(x) for x in item["pos"]]
                if "deposited" in item:
                    target.deposited = int(item["deposited"])
                if "lit" in item:
                    target.lit = bool(item["lit"])

    def _parse_inputs(self, inp: Dict[str, Any]):
        if not isinstance(inp, dict) or "frames" not in inp:
            raise ValueError("Input JSON must contain 'frames' array")
        frames = inp["frames"]
        if not isinstance(frames, list):
            raise ValueError("'frames' must be a list")

        last_tick = -1
        for f in frames:
            if not isinstance(f, dict):
                raise ValueError("Frame item must be a JSON object")
            if "tick" not in f or not isinstance(f["tick"], int):
                raise ValueError("Frame must have an integer 'tick'")
            t = f["tick"]
            if t <= last_tick:
                raise ValueError("Frame ticks must be strictly increasing")
            last_tick = t

            if "move" in f:
                m = f["move"]
                if not isinstance(m, list) or len(m) != 2:
                    raise ValueError("'move' must be [x, z]")
                if not all(isinstance(v, (int, float)) and -1.0 <= v <= 1.0 for v in m):
                    raise ValueError("'move' values must be between -1.0 and 1.0")

            self.input_frames[t] = f

    def _record_snapshot(self):
        snap = {
            "type": "snapshot",
            "tick": self.sim_tick,
            "sim_tick": self.sim_tick,
            "state": self.state,
            "time_left_s": round(self.time_left_s, 1),
            "score": self.score,
            "player": {
                "pos": [round(x, 3) for x in self.player.pos],
                "flames": self.player.flames,
                "carried": self.player.carried,
            },
            "lanterns": [
                {
                    "id": lan.id,
                    "pos": [round(x, 3) for x in lan.pos],
                    "lit": lan.lit,
                    "deposited": lan.deposited,
                }
                for lan in self.lanterns
            ],
            "shades": [
                {
                    "id": s.id,
                    "pos": [round(x, 3) for x in s.pos],
                    "state": s.state,
                }
                for s in self.shades
            ],
            "motes_active": len(self.motes),
        }
        self.output_lines.append(json.dumps(snap))

    def _record_event(self, next_tick: int, name: str, data: Dict[str, Any]):
        evt = {
            "type": "event",
            "tick": next_tick,
            "name": name,
            "data": data,
        }
        self.output_lines.append(json.dumps(evt))

    def run(self, total_ticks: int) -> str:
        # Snapshot tick 0
        self._record_snapshot()

        dt = 1.0 / 60.0

        for step in range(total_ticks):
            if self.state != "playing":
                break

            # 1. Update current input from frames
            next_tick = step + 1
            prev_interact = self.cur_interact
            prev_pulse = self.cur_pulse
            prev_jump = self.cur_jump

            if step in self.input_frames:
                frame = self.input_frames[step]
                if "move" in frame:
                    self.cur_move = [float(frame["move"][0]), float(frame["move"][1])]
                if "cam_yaw_deg" in frame:
                    self.cur_cam_yaw_deg = float(frame["cam_yaw_deg"])
                if "jump" in frame:
                    self.cur_jump = bool(frame["jump"])
                if "interact" in frame:
                    self.cur_interact = bool(frame["interact"])
                if "pulse" in frame:
                    self.cur_pulse = bool(frame["pulse"])

            interact_triggered = self.cur_interact and not prev_interact
            pulse_triggered = self.cur_pulse and not prev_pulse

            # 2. Player movement
            theta = math.radians(self.cur_cam_yaw_deg)
            mx, mz = self.cur_move[0], self.cur_move[1]
            x_prime = mx * math.cos(theta) + mz * math.sin(theta)
            z_prime = -mx * math.sin(theta) + mz * math.cos(theta)
            length = math.sqrt(x_prime**2 + z_prime**2)
            if length > 1.0:
                x_prime /= length
                z_prime /= length

            speed = self.tuning["player_speed"]
            self.player.pos[0] += x_prime * speed * dt
            self.player.pos[2] += z_prime * speed * dt

            # 3. Timers
            self.time_left_s = max(0.0, self.time_left_s - dt)
            if self.player.invuln_timer > 0:
                self.player.invuln_timer = max(0.0, self.player.invuln_timer - dt)
            if self.player.pulse_cooldown > 0:
                self.player.pulse_cooldown = max(0.0, self.player.pulse_cooldown - dt)

            # 4. Mote pickup
            pickup_r = self.tuning["pickup_radius"]
            cap = self.tuning["carry_capacity"]
            motes_to_remove = []
            for m in self.motes:
                if dist_xz(self.player.pos, m.pos) <= pickup_r:
                    if self.player.carried < cap:
                        self.player.carried += 1
                        self.score += self.tuning["score"]["per_mote"]
                        motes_to_remove.append(m)
                        self._record_event(next_tick, "mote_picked", {"carried": self.player.carried})
            for m in motes_to_remove:
                self.motes.remove(m)

            # 5. Interact with Lanterns (Deposit)
            if interact_triggered:
                interact_r = self.tuning["interact_radius"]
                nearby_lanterns = [
                    lan for lan in self.lanterns if dist_xz(self.player.pos, lan.pos) <= interact_r
                ]
                if nearby_lanterns:
                    # Choose closest
                    nearby_lanterns.sort(key=lambda lan: dist_xz(self.player.pos, lan.pos))
                    target_lan = nearby_lanterns[0]
                    if not target_lan.lit and self.player.carried > 0:
                        needed = self.tuning["lantern_cost"] - target_lan.deposited
                        amount = min(self.player.carried, needed)
                        if amount > 0:
                            self.player.carried -= amount
                            target_lan.deposited += amount
                            self._record_event(
                                next_tick,
                                "deposit",
                                {
                                    "lantern_id": target_lan.id,
                                    "amount": amount,
                                    "deposited": target_lan.deposited,
                                },
                            )
                            if target_lan.deposited >= self.tuning["lantern_cost"]:
                                target_lan.lit = True
                                self.score += self.tuning["score"]["per_lantern"]
                                self._record_event(
                                    next_tick, "lantern_lit", {"lantern_id": target_lan.id}
                                )

                                # Check win condition
                                if all(lan.lit for lan in self.lanterns):
                                    self.state = "won"
                                    # Add bonus score
                                    sec_bonus = int(math.floor(self.time_left_s)) * self.tuning["score"]["per_second_left"]
                                    flame_bonus = self.player.flames * self.tuning["score"]["per_flame_left"]
                                    self.score += sec_bonus + flame_bonus
                                    self._record_event(
                                        next_tick,
                                        "game_over",
                                        {"result": "won", "reason": "all_lit"},
                                    )
                                    self.sim_tick = next_tick
                                    break

            # 6. Pulse
            if pulse_triggered and self.state == "playing":
                pulse_cost = self.tuning["pulse_cost"]
                if self.player.carried >= pulse_cost and self.player.pulse_cooldown <= 0.0:
                    self.player.carried -= pulse_cost
                    self.player.pulse_cooldown = self.tuning["pulse_cooldown_s"]
                    pulse_r = self.tuning["pulse_radius"]
                    push_m = self.tuning["pulse_push_m"]
                    stun_s = self.tuning["pulse_stun_s"]
                    stunned_ids = []

                    for s in self.shades:
                        d = dist_xz(self.player.pos, s.pos)
                        if d <= pulse_r:
                            s.state = "stunned"
                            s.stun_timer = stun_s
                            if d > 0.0001:
                                dir_x = (s.pos[0] - self.player.pos[0]) / d
                                dir_z = (s.pos[2] - self.player.pos[2]) / d
                            else:
                                dir_x, dir_z = 1.0, 0.0
                            s.pos[0] += dir_x * push_m
                            s.pos[2] += dir_z * push_m
                            self.score += self.tuning["score"]["per_stun"]
                            stunned_ids.append(s.id)

                    self._record_event(next_tick, "pulse", {"stunned_ids": stunned_ids})

            # 7. Shades AI movement
            shade_speed = self.tuning["shade_speed"]
            safe_r = self.tuning["safe_radius"]
            for s in self.shades:
                if s.state == "stunned":
                    s.stun_timer -= dt
                    if s.stun_timer <= 0.0:
                        s.state = "chase"
                        s.stun_timer = 0.0
                elif s.state == "chase":
                    d = dist_xz(s.pos, self.player.pos)
                    if d > 0.0001:
                        step_dist = min(d, shade_speed * dt)
                        nx = s.pos[0] + (self.player.pos[0] - s.pos[0]) / d * step_dist
                        nz = s.pos[2] + (self.player.pos[2] - s.pos[2]) / d * step_dist

                        # Lantern safe radius collision
                        for lan in self.lanterns:
                            dl = math.sqrt((nx - lan.pos[0]) ** 2 + (nz - lan.pos[2]) ** 2)
                            if dl < safe_r:
                                if dl > 0.0001:
                                    nx = lan.pos[0] + (nx - lan.pos[0]) / dl * safe_r
                                    nz = lan.pos[2] + (nz - lan.pos[2]) / dl * safe_r
                                else:
                                    nx = lan.pos[0] + safe_r
                        s.pos[0] = nx
                        s.pos[2] = nz

            # 8. Shades attack Player
            hit_r = self.tuning["shade_hit_radius"]
            for s in self.shades:
                if s.state != "stunned" and self.state == "playing":
                    d = dist_xz(s.pos, self.player.pos)
                    if d <= hit_r:
                        if self.player.invuln_timer <= 0.0:
                            self.player.flames -= 1
                            ratio = self.tuning["hit_drop_ratio"]
                            dropped = int(math.floor(self.player.carried * ratio))
                            self.player.carried -= dropped
                            self.player.invuln_timer = self.tuning["invuln_s"]
                            self._record_event(
                                next_tick,
                                "player_hit",
                                {
                                    "by": "shade",
                                    "flames": self.player.flames,
                                    "dropped": dropped,
                                },
                            )
                            if self.player.flames <= 0:
                                self.state = "lost"
                                self._record_event(
                                    next_tick,
                                    "game_over",
                                    {"result": "lost", "reason": "no_flames"},
                                )
                                self.sim_tick = next_tick
                                break

            # 9. Time check
            if self.time_left_s <= 0.0 and self.state == "playing":
                self.state = "lost"
                self._record_event(
                    next_tick,
                    "game_over",
                    {"result": "lost", "reason": "dawn"},
                )
                self.sim_tick = next_tick
                break

            self.sim_tick = next_tick

            # Snapshot recording
            if self.sim_tick % self.snapshot_every == 0:
                self._record_snapshot()

        # Final end record
        end_rec = {
            "type": "end",
            "ticks": self.sim_tick,
            "state": self.state,
            "score": self.score,
        }
        self.output_lines.append(json.dumps(end_rec))

        return "\n".join(self.output_lines) + "\n"
