"""
Core simulation engine for Dao Den Long (Island of Lanterns).
Implements Test Contract v1.1 specifications: 3 Nights, standardized tuning,
strict 12-step tick execution, jump pads, Drifters, Wind Charms, cliff collisions,
and falling physics.
"""

import json
import math
import random
from typing import Dict, Any, List, Optional, Tuple


class Player:
    def __init__(self, pos: List[float], flames: int = 3, carried: int = 0):
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.vel = [0.0, 0.0, 0.0]
        self.grounded = True
        self.flames = int(flames)
        self.carried = int(carried)
        self.facing_yaw = 0.0  # Facing angle in degrees

        # Timers in ticks
        self.invuln_ticks = 0
        self.dash_cd_ticks = 0
        self.dash_ticks_left = 0
        self.pulse_cd_ticks = 0
        self.charm_ticks = 0

        # Jump pad flight mode
        self.in_jump_pad_flight = False
        self.launch_vel = [0.0, 0.0, 0.0]

        # Falling state
        self.is_falling = False
        self.fall_respawn_delay = 0


class Lantern:
    def __init__(self, id: str, pos: List[float], lit: bool = False, deposited: int = 0):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.lit = bool(lit)
        self.deposited = int(deposited)
        self.just_lit_ticks = 0  # To push out shades when recently lit


class Shade:
    def __init__(
        self,
        id: str,
        pos: List[float],
        state: str = "spawning",
        state_ticks_left: int = 0,
    ):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.state = state  # "spawning", "wander", "chase", "recoil", "stunned"
        self.state_ticks_left = state_ticks_left
        self.stun_push_dir = [0.0, 0.0]
        self.recoil_dir = [0.0, 0.0]
        self.recoil_ticks = 0


class Drifter:
    def __init__(self, id: str, pos: List[float]):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.state = "idle"  # "idle", "chase", "flee", "removed"
        self.stolen = 0
        self.flee_ticks = 0
        self.has_stolen = False


class Charm:
    def __init__(self, id: str, pos: List[float]):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.available = True
        self.respawn_ticks = 0


class Mote:
    def __init__(self, id: str, pos: List[float], kind: str = "random", ttl_ticks: int = 0):
        self.id = id
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.kind = kind  # "random" or "dropped"
        self.ttl_ticks = ttl_ticks
        self.can_pickup = True if kind == "random" else False


def dist_xz(p1: List[float], p2: List[float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[2] - p2[2])


def dist_3d(p1: List[float], p2: List[float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)


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
        self.night = int(night)
        self.snapshot_every = max(1, int(snapshot_every))

        # Standardized tuning matching Ticket-02 / Contract v1.1
        self.tuning = {
            "player_speed": 6.0,
            "dash_speed": 14.0,
            "dash_duration_s": 0.2,
            "dash_cooldown_s": 1.5,
            "carry_capacity": 10,
            "lantern_cost": 10,
            "lantern_count_night1": 5,
            "lantern_count_night2": 6,
            "lantern_count_night3": 7,
            "pickup_radius": 1.0,
            "interact_radius": 2.0,
            "pulse_cost": 3,
            "pulse_radius": 5.0,
            "pulse_stun_s": 2.0,  # 120 ticks
            "pulse_push_m": 4.0,
            "pulse_cooldown_s": 3.0,
            "safe_radius": 6.0,
            "shade_speed": 4.0 if self.night < 3 else 4.5,
            "shade_speed_night3": 4.5,
            "shade_hit_radius": 1.0,
            "night1_duration_s": 300,
            "night2_duration_s": 330,
            "night3_duration_s": 360,
            "flames": 3,
            "invuln_s": 1.5,
            "hit_drop_ratio": 0.5,
            "fall_enabled": True,
            "score": {
                "per_mote": 10,
                "per_lantern": 100,
                "per_stun": 5,
                "per_second_left": 2,
                "per_flame_left": 50,
            },
        }
        if tuning:
            self.tuning.update(tuning)

        duration_key = f"night{self.night}_duration_s"
        self.time_left_s = float(self.tuning.get(duration_key, 300))
        self.score = 0
        self.state = "playing"  # "playing", "paused", "won", "lost"
        self.is_paused = False
        self.sim_tick = 0
        self.next_mote_id = 1
        self.next_shade_id = 1
        self.next_drifter_id = 1

        # Wind state for Night 3
        self.wind_active = False
        self.wind_dir_deg = 0.0
        self.wind_ticks_left = 0
        self.wind_enabled = True if self.night == 3 else False

        # Entity lists
        self.player = Player(pos=[0.0, 0.0, 0.0], flames=self.tuning["flames"], carried=0)
        self.lanterns: List[Lantern] = []
        self.motes: List[Mote] = []
        self.shades: List[Shade] = []
        self.drifters: List[Drifter] = []
        self.charms: List[Charm] = []

        # Map setup
        self._init_map()

        # Apply Scenario override if given
        if scenario_data:
            self._apply_scenario(scenario_data)

        # Parse & index input frames
        self.input_frames: Dict[int, Dict[str, Any]] = {}
        if inputs_data:
            self._parse_inputs(inputs_data)

        # Input state
        self.cur_move = [0.0, 0.0]
        self.cur_cam_yaw_deg = 0.0
        self.cur_jump = False
        self.cur_interact = False
        self.cur_pulse = False
        self.cur_dash = False
        self.cur_pause = False

        self.output_lines: List[str] = []

    def _init_map(self):
        if self.night == 1:
            l_coords = [
                (0.0, 0.0, 25.0),
                (23.8, 0.0, 7.7),
                (14.7, 0.0, -20.2),
                (-14.7, 0.0, -20.2),
                (-23.8, 0.0, 7.7),
            ]
            self.lanterns = [Lantern(f"L{i+1}", list(pos)) for i, pos in enumerate(l_coords)]
            self._spawn_initial_motes_night1()

        elif self.night == 2:
            l_coords = [
                (0.0, 0.0, 20.0),
                (17.0, 0.0, -10.0),
                (-17.0, 0.0, -10.0),
                (70.0, 0.0, 20.0),
                (87.0, 0.0, -10.0),
                (53.0, 0.0, -10.0),
            ]
            self.lanterns = [Lantern(f"L{i+1}", list(pos)) for i, pos in enumerate(l_coords)]
            self.charms = [Charm("C1", [35.0, 0.0, 0.0])]
            self._spawn_initial_motes_night2()

        elif self.night == 3:
            l_coords = [
                (0.0, 6.0, 6.0),
                (18.0, 3.0, 10.0),
                (-18.0, 3.0, 10.0),
                (35.0, 0.0, -10.0),
                (-35.0, 0.0, -10.0),
                (20.0, 0.0, -35.0),
                (-20.0, 0.0, -35.0),
            ]
            self.lanterns = [Lantern(f"L{i+1}", list(pos)) for i, pos in enumerate(l_coords)]
            self.charms = [
                Charm("C1", [30.0, 0.0, 25.0]),
                Charm("C2", [-30.0, 0.0, 25.0]),
            ]
            self._spawn_initial_motes_night3()

    def _spawn_initial_motes_night1(self):
        points = []
        for i in range(8):
            a = math.radians(i * 45)
            points.append((round(12.0 * math.cos(a), 3), 0.0, round(12.0 * math.sin(a), 3)))
        for i in range(16):
            a = math.radians(i * 22.5)
            points.append((round(33.0 * math.cos(a), 3), 0.0, round(33.0 * math.sin(a), 3)))
        for i in range(min(20, len(points))):
            p = points[i]
            self.motes.append(Mote(f"M{self.next_mote_id}", [p[0], p[1], p[2]], "random"))
            self.next_mote_id += 1

    def _spawn_initial_motes_night2(self):
        points = []
        for cx in [0.0, 70.0]:
            for i in range(4):
                a = math.radians(i * 90)
                points.append((round(cx + 10.0 * math.cos(a), 3), 0.0, round(10.0 * math.sin(a), 3)))
            for i in range(8):
                a = math.radians(i * 45)
                points.append((round(cx + 22.0 * math.cos(a), 3), 0.0, round(22.0 * math.sin(a), 3)))
        for i in range(min(20, len(points))):
            p = points[i]
            self.motes.append(Mote(f"M{self.next_mote_id}", [p[0], p[1], p[2]], "random"))
            self.next_mote_id += 1

    def _spawn_initial_motes_night3(self):
        points = []
        for i in range(18):
            a = math.radians(i * 20)
            points.append((round(34.0 * math.cos(a), 3), 0.0, round(34.0 * math.sin(a), 3)))
        for i in range(8):
            a = math.radians(20 + i * 20)
            points.append((round(18.0 * math.cos(a), 3), 3.0, round(18.0 * math.sin(a), 3)))
        for i in range(4):
            a = math.radians(45 + i * 90)
            points.append((round(5.0 * math.cos(a), 3), 6.0, round(5.0 * math.sin(a), 3)))
        for i in range(min(20, len(points))):
            p = points[i]
            self.motes.append(Mote(f"M{self.next_mote_id}", [p[0], p[1], p[2]], "random"))
            self.next_mote_id += 1

    def _apply_scenario(self, sc: Dict[str, Any]):
        if "time_left_s" in sc:
            self.time_left_s = float(sc["time_left_s"])
        if "wind_enabled" in sc:
            self.wind_enabled = bool(sc["wind_enabled"])

        if "player" in sc:
            p_data = sc["player"]
            if "pos" in p_data:
                self.player.pos = [float(x) for x in p_data["pos"]]
            if "flames" in p_data:
                self.player.flames = int(p_data["flames"])
            if "carried" in p_data:
                self.player.carried = int(p_data["carried"])
            if "invuln_ticks" in p_data:
                self.player.invuln_ticks = int(p_data["invuln_ticks"])
            if "dash_cd_ticks" in p_data:
                self.player.dash_cd_ticks = int(p_data["dash_cd_ticks"])
            if "pulse_cd_ticks" in p_data:
                self.player.pulse_cd_ticks = int(p_data["pulse_cd_ticks"])
            if "charm_ticks" in p_data:
                self.player.charm_ticks = int(p_data["charm_ticks"])

        if sc.get("random_motes") is False:
            self.motes = []
        if "motes" in sc:
            self.motes = [
                Mote(f"M{i+1}", [float(p[0]), float(p[1]), float(p[2])], "random")
                for i, p in enumerate(sc["motes"])
            ]
            self.next_mote_id = len(self.motes) + 1

        if sc.get("random_shades") is False:
            self.shades = []
        if "shades" in sc:
            self.shades = [
                Shade(
                    item.get("id", f"S{i+1}"),
                    [float(item["pos"][0]), float(item["pos"][1]), float(item["pos"][2])],
                    state=item.get("state", "chase"),
                    state_ticks_left=item.get("state_ticks_left", 0),
                )
                for i, item in enumerate(sc["shades"])
            ]
            self.next_shade_id = len(self.shades) + 1

        if sc.get("random_drifters") is False:
            self.drifters = []
        if "drifters" in sc:
            self.drifters = [
                Drifter(item.get("id", f"D{i+1}"), [float(p) for p in item["pos"]])
                for i, item in enumerate(sc["drifters"])
            ]

        if "charms" in sc:
            self.charms = [
                Charm(item.get("id", f"C{i+1}"), [float(p) for p in item["pos"]])
                for i, item in enumerate(sc["charms"])
            ]

        if "lanterns" in sc:
            for item in sc["lanterns"]:
                lid = item.get("id")
                target = next((lan for lan in self.lanterns if lan.id == lid), None)
                if not target:
                    target = Lantern(lid, [0.0, 0.0, 0.0], lit=False, deposited=0)
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

    def _get_ground_height(self, x: float, z: float) -> Optional[float]:
        if self.night == 1:
            if math.hypot(x, z) <= 40.0:
                return 0.0
            return None

        elif self.night == 2:
            if math.hypot(x, z) <= 28.0:
                return 0.0
            if math.hypot(x - 70.0, z) <= 28.0:
                return 0.0
            if 26.0 <= x <= 44.0 and -2.0 <= z <= 2.0:
                return 0.0
            return None

        elif self.night == 3:
            dist = math.hypot(x, z)
            if dist > 45.0:
                return None
            if dist <= 2.0:
                return 6.0  # Bell tower base / top
            if dist <= 8.0:
                return 6.0  # Tier 2
            if 12.0 <= dist <= 24.0 and z > 0:
                return 3.0  # Tier 1
            # Ramps at 30° and 150° from r=30 (Y=0) to r=24 (Y=3)
            angle_deg = math.degrees(math.atan2(z, x)) % 360
            for ramp_angle in [30.0, 150.0]:
                if abs(angle_deg - ramp_angle) <= 3.5:
                    if 24.0 <= dist <= 30.0:
                        progress = (30.0 - dist) / 6.0
                        return progress * 3.0
            return 0.0

        return 0.0

    def _record_snapshot(self):
        state_str = "paused" if self.is_paused else self.state
        snap = {
            "type": "snapshot",
            "tick": self.sim_tick,
            "sim_tick": self.sim_tick,
            "state": state_str,
            "night": self.night,
            "time_left_s": round(self.time_left_s, 1),
            "score": self.score,
            "wind": {"active": self.wind_active, "dir_deg": round(self.wind_dir_deg, 1)},
            "player": {
                "pos": [round(x, 3) for x in self.player.pos],
                "vel": [round(v, 3) for v in self.player.vel],
                "grounded": self.player.grounded,
                "invuln": self.player.invuln_ticks > 0,
                "flames": self.player.flames,
                "carried": self.player.carried,
                "dash_cd_s": round(self.player.dash_cd_ticks / 60.0, 1),
                "pulse_cd_s": round(self.player.pulse_cd_ticks / 60.0, 1),
                "charm_s": round(self.player.charm_ticks / 60.0, 1),
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
            "drifters": [
                {
                    "id": d.id,
                    "pos": [round(x, 3) for x in d.pos],
                    "state": d.state,
                    "stolen": d.stolen,
                }
                for d in self.drifters
            ],
            "charms": [
                {
                    "id": c.id,
                    "available": c.available,
                    "respawn_s": round(c.respawn_ticks / 60.0, 1),
                }
                for c in self.charms
            ],
            "motes": [
                {
                    "id": m.id,
                    "pos": [round(x, 3) for x in m.pos],
                    "kind": m.kind,
                    "ttl_s": round(m.ttl_ticks / 60.0, 1),
                }
                for m in self.motes
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
        self._record_event(0, "night_start", {"night": self.night})
        self._record_snapshot()

        dt = 1.0 / 60.0

        for step in range(total_ticks):
            if self.state in ["won", "lost"]:
                break

            next_tick = step + 1
            prev_interact = self.cur_interact
            prev_pulse = self.cur_pulse
            prev_jump = self.cur_jump
            prev_dash = self.cur_dash
            prev_pause = self.cur_pause

            # 1. Read input & Pause processing
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
                if "dash" in frame:
                    self.cur_dash = bool(frame["dash"])
                if "pause" in frame:
                    self.cur_pause = bool(frame["pause"])

            pause_triggered = self.cur_pause and not prev_pause
            if pause_triggered:
                self.is_paused = not self.is_paused
                if self.is_paused:
                    self._record_event(next_tick, "paused", {})
                else:
                    self._record_event(next_tick, "resumed", {})

            if self.is_paused:
                if (step + 1) % self.snapshot_every == 0:
                    self._record_snapshot()
                continue

            interact_triggered = self.cur_interact and not prev_interact
            pulse_triggered = self.cur_pulse and not prev_pulse
            jump_triggered = self.cur_jump and not prev_jump
            dash_triggered = self.cur_dash and not prev_dash

            # 2. Decrease counters
            self.time_left_s = max(0.0, self.time_left_s - dt)
            if self.player.invuln_ticks > 0:
                self.player.invuln_ticks -= 1
            if self.player.dash_cd_ticks > 0:
                self.player.dash_cd_ticks -= 1
            if self.player.pulse_cd_ticks > 0:
                self.player.pulse_cd_ticks -= 1
            if self.player.charm_ticks > 0:
                self.player.charm_ticks -= 1
            if self.player.dash_ticks_left > 0:
                self.player.dash_ticks_left -= 1

            for c in self.charms:
                if not c.available and c.respawn_ticks > 0:
                    c.respawn_ticks -= 1
                    if c.respawn_ticks == 0:
                        c.available = True

            expired_motes = []
            for m in self.motes:
                m.can_pickup = True
                if m.kind == "dropped":
                    m.ttl_ticks -= 1
                    if m.ttl_ticks <= 0:
                        expired_motes.append(m)
            for m in expired_motes:
                self.motes.remove(m)

            if self.wind_enabled:
                cycle_tick = step % 1800
                if cycle_tick == 0 and step > 0:
                    self.wind_active = True
                    self.wind_ticks_left = 300
                    self.wind_dir_deg = self.rng.uniform(0, 360)
                if self.wind_active:
                    self.wind_ticks_left -= 1
                    if self.wind_ticks_left <= 0:
                        self.wind_active = False

            # 3. Move Mây (Jumping, Dashing, Jump Pad, Wind, Falling)
            if self.player.fall_respawn_delay > 0:
                self.player.fall_respawn_delay -= 1
                if self.player.fall_respawn_delay == 0:
                    self.player.pos = [0.0, 0.0, 0.0]
                    self.player.vel = [0.0, 0.0, 0.0]
                    self.player.grounded = True
                    self.player.invuln_ticks = 90
                    self.player.is_falling = False
            else:
                can_dash = (self.player.dash_cd_ticks == 0 or self.player.charm_ticks > 0)
                if dash_triggered and can_dash and self.player.dash_ticks_left == 0:
                    self.player.dash_ticks_left = 12
                    self.player.dash_cd_ticks = 90 if self.player.charm_ticks == 0 else 0
                    self._record_event(next_tick, "dash", {})

                theta = math.radians(self.cur_cam_yaw_deg)
                mx, mz = self.cur_move[0], self.cur_move[1]
                x_prime = mx * math.cos(theta) + mz * math.sin(theta)
                z_prime = -mx * math.sin(theta) + mz * math.cos(theta)
                m_len = math.hypot(x_prime, z_prime)
                if m_len > 0.01:
                    x_prime /= m_len
                    z_prime /= m_len
                    self.player.facing_yaw = math.degrees(math.atan2(x_prime, z_prime))

                prev_pos = [self.player.pos[0], self.player.pos[1], self.player.pos[2]]

                if self.player.dash_ticks_left > 0:
                    dash_dir_x = x_prime if m_len > 0.01 else math.sin(math.radians(self.player.facing_yaw))
                    dash_dir_z = z_prime if m_len > 0.01 else math.cos(math.radians(self.player.facing_yaw))
                    self.player.pos[0] += dash_dir_x * self.tuning["dash_speed"] * dt
                    self.player.pos[2] += dash_dir_z * self.tuning["dash_speed"] * dt
                    self.player.vel[1] = 0.0
                elif self.player.in_jump_pad_flight:
                    self.player.pos[0] += self.player.launch_vel[0] * dt
                    self.player.pos[2] += self.player.launch_vel[2] * dt
                    self.player.vel[1] += -20.0 * dt
                    self.player.pos[1] += self.player.vel[1] * dt
                else:
                    speed = 7.2 if self.player.charm_ticks > 0 else self.tuning["player_speed"]
                    self.player.pos[0] += x_prime * speed * dt
                    self.player.pos[2] += z_prime * speed * dt

                    if jump_triggered and self.player.grounded:
                        self.player.vel[1] = 7.0
                        self.player.grounded = False

                    if not self.player.grounded:
                        self.player.vel[1] += -20.0 * dt
                        self.player.pos[1] += self.player.vel[1] * dt

                    if self.wind_active:
                        w_rad = math.radians(self.wind_dir_deg)
                        self.player.pos[0] += 2.0 * math.cos(w_rad) * dt
                        self.player.pos[2] += 2.0 * math.sin(w_rad) * dt

                # Cliff & ground collision check
                ground_y = self._get_ground_height(self.player.pos[0], self.player.pos[2])
                if ground_y is not None:
                    # If target ground is significantly higher than player and player is not in air above it, block horizontal movement (cliff)
                    if ground_y > prev_pos[1] + 0.6 and not self.player.in_jump_pad_flight:
                        self.player.pos[0] = prev_pos[0]
                        self.player.pos[2] = prev_pos[2]
                        ground_y = self._get_ground_height(self.player.pos[0], self.player.pos[2])

                    if ground_y is not None and self.player.pos[1] <= ground_y:
                        self.player.pos[1] = ground_y
                        self.player.vel[1] = 0.0
                        self.player.grounded = True
                        self.player.in_jump_pad_flight = False
                    else:
                        self.player.grounded = False
                else:
                    self.player.grounded = False

                # Jump Pad triggers
                if self.player.grounded:
                    if self.night == 2:
                        if math.hypot(self.player.pos[0] - 20.0, self.player.pos[2] - 18.0) <= 1.0:
                            dx, dz = 70.0 - 20.0, 0.0 - 18.0
                            dist = math.hypot(dx, dz)
                            self.player.in_jump_pad_flight = True
                            self.player.launch_vel = [24.0 * (dx / dist), 0.0, 24.0 * (dz / dist)]
                            self.player.vel[1] = 14.0
                            self.player.grounded = False
                        elif math.hypot(self.player.pos[0] - 50.0, self.player.pos[2] - (-18.0)) <= 1.0:
                            dx, dz = 0.0 - 50.0, 0.0 - (-18.0)
                            dist = math.hypot(dx, dz)
                            self.player.in_jump_pad_flight = True
                            self.player.launch_vel = [24.0 * (dx / dist), 0.0, 24.0 * (dz / dist)]
                            self.player.vel[1] = 14.0
                            self.player.grounded = False

                    elif self.night == 3:
                        if math.hypot(self.player.pos[0] - 0.0, self.player.pos[2] - 13.0) <= 1.0:
                            self.player.in_jump_pad_flight = True
                            self.player.launch_vel = [0.0, 0.0, -8.0]
                            self.player.vel[1] = 12.0
                            self.player.grounded = False

                # Check falling off island (Y < -10)
                if self.player.pos[1] < -10.0 and not self.player.is_falling:
                    self.player.is_falling = True
                    self.player.flames -= 1
                    dropped_motes = self.player.carried
                    self.player.carried = 0
                    self._record_event(
                        next_tick,
                        "player_hit",
                        {
                            "by": "fall",
                            "flames": self.player.flames,
                            "dropped": dropped_motes,
                            "lost": True,
                        },
                    )
                    if self.player.flames <= 0:
                        self.state = "lost"
                        self._record_event(next_tick, "game_over", {"result": "lost", "reason": "no_flames"})
                        self.sim_tick = next_tick
                        break
                    else:
                        self.player.fall_respawn_delay = 60

            # 4. Pickup Motes & Charms
            if not self.player.is_falling and self.player.fall_respawn_delay == 0:
                pickup_r = self.tuning["pickup_radius"]
                cap = self.tuning["carry_capacity"]
                motes_to_remove = []
                for m in self.motes:
                    if m.can_pickup:
                        d_xz = dist_xz(self.player.pos, m.pos)
                        d_y = abs(self.player.pos[1] - m.pos[1])
                        if d_xz <= pickup_r and d_y <= 1.5:
                            if self.player.carried < cap:
                                self.player.carried += 1
                                motes_to_remove.append(m)
                                self._record_event(next_tick, "mote_picked", {"carried": self.player.carried})
                for m in motes_to_remove:
                    self.motes.remove(m)

                for c in self.charms:
                    if c.available:
                        if dist_xz(self.player.pos, c.pos) <= pickup_r and abs(self.player.pos[1] - c.pos[1]) <= 1.5:
                            c.available = False
                            c.respawn_ticks = 2700
                            self.player.charm_ticks = 600
                            self._record_event(next_tick, "charm_picked", {"charm_id": c.id, "charm_ticks": 600})

            # 5. Interact with Lanterns
            if interact_triggered and not self.player.is_falling:
                interact_r = self.tuning["interact_radius"]
                candidates = [
                    lan for lan in self.lanterns
                    if not lan.lit and dist_xz(self.player.pos, lan.pos) <= interact_r
                ]
                if candidates:
                    candidates.sort(key=lambda lan: (dist_xz(self.player.pos, lan.pos), lan.id))
                    target_lan = candidates[0]
                    if self.player.carried > 0:
                        needed = self.tuning["lantern_cost"] - target_lan.deposited
                        amount = min(self.player.carried, needed)
                        if amount > 0:
                            self.player.carried -= amount
                            target_lan.deposited += amount
                            self.score += amount * self.tuning["score"]["per_mote"]
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
                                target_lan.just_lit_ticks = 30
                                self.score += self.tuning["score"]["per_lantern"]
                                self._record_event(next_tick, "lantern_lit", {"lantern_id": target_lan.id})

                                if all(lan.lit for lan in self.lanterns):
                                    self.state = "won"
                                    sec_bonus = int(math.floor(self.time_left_s)) * self.tuning["score"]["per_second_left"]
                                    flame_bonus = self.player.flames * self.tuning["score"]["per_flame_left"]
                                    self.score += sec_bonus + flame_bonus
                                    self._record_event(next_tick, "game_over", {"result": "won", "reason": "all_lit"})
                                    self.sim_tick = next_tick
                                    break

            # 6. Update Safe Zones
            safe_r = self.tuning["safe_radius"]
            for lan in self.lanterns:
                if lan.lit and lan.just_lit_ticks > 0:
                    lan.just_lit_ticks -= 1
                    for s in self.shades:
                        d = dist_xz(s.pos, lan.pos)
                        if d < safe_r:
                            dir_x = (s.pos[0] - lan.pos[0]) / d if d > 0.001 else 1.0
                            dir_z = (s.pos[2] - lan.pos[2]) / d if d > 0.001 else 0.0
                            step_out = (safe_r - d) / max(1, lan.just_lit_ticks + 1)
                            s.pos[0] += dir_x * step_out
                            s.pos[2] += dir_z * step_out

            # 7. Tỏa Sáng (Pulse)
            if pulse_triggered and self.state == "playing" and not self.player.is_falling:
                if self.player.carried >= self.tuning["pulse_cost"] and self.player.pulse_cd_ticks == 0:
                    self.player.carried -= self.tuning["pulse_cost"]
                    self.player.pulse_cd_ticks = 180
                    pulse_center = [self.player.pos[0], self.player.pos[1] + 0.8, self.player.pos[2]]
                    pulse_r = self.tuning["pulse_radius"]
                    stunned_ids = []

                    for s in self.shades:
                        d3 = dist_3d(pulse_center, s.pos)
                        if d3 <= pulse_r:
                            s.state = "stunned"
                            s.state_ticks_left = 120
                            d_xz = dist_xz(pulse_center, s.pos)
                            if d_xz > 0.001:
                                s.stun_push_dir = [(s.pos[0] - pulse_center[0]) / d_xz, (s.pos[2] - pulse_center[2]) / d_xz]
                            else:
                                s.stun_push_dir = [1.0, 0.0]
                            self.score += self.tuning["score"]["per_stun"]
                            stunned_ids.append(s.id)

                    for d in self.drifters:
                        if dist_3d(pulse_center, d.pos) <= pulse_r:
                            if d.state == "chase":
                                d.state = "flee"
                                d.flee_ticks = 240
                            elif d.state == "flee" and d.stolen > 0:
                                dropped_cnt = d.stolen
                                for _ in range(dropped_cnt):
                                    self.motes.append(Mote(f"M{self.next_mote_id}", [d.pos[0], d.pos[1], d.pos[2]], "dropped", 480))
                                    self.next_mote_id += 1
                                self._record_event(next_tick, "drifter_drop", {"drifter_id": d.id, "amount": dropped_cnt})
                                d.stolen = 0
                                d.flee_ticks = 120

                    self._record_event(next_tick, "pulse", {"stunned_ids": stunned_ids})

            # 8. Move Shades & Drifters
            shade_speed = self.tuning["shade_speed"]
            for s in self.shades:
                if s.state == "stunned":
                    s.state_ticks_left -= 1
                    if s.state_ticks_left >= 105:
                        s.pos[0] += s.stun_push_dir[0] * (4.0 / 15.0)
                        s.pos[2] += s.stun_push_dir[1] * (4.0 / 15.0)
                    if s.state_ticks_left <= 0:
                        s.state = "wander"

                elif s.state == "recoil":
                    s.recoil_ticks -= 1
                    s.pos[0] += s.recoil_dir[0] * (2.0 / 60.0)
                    s.pos[2] += s.recoil_dir[1] * (2.0 / 60.0)
                    if s.recoil_ticks <= 0:
                        s.state = "wander"

                elif s.state == "spawning":
                    s.state = "wander"

                elif s.state in ["wander", "chase"]:
                    d_player = dist_xz(s.pos, self.player.pos)
                    if s.state == "wander" and d_player <= 12.0:
                        s.state = "chase"
                    elif s.state == "chase" and d_player > 18.0:
                        s.state = "wander"

                    if s.state == "chase" and d_player > 0.001:
                        step_s = min(d_player, shade_speed * dt)
                        nx = s.pos[0] + (self.player.pos[0] - s.pos[0]) / d_player * step_s
                        nz = s.pos[2] + (self.player.pos[2] - s.pos[2]) / d_player * step_s

                        for lan in self.lanterns:
                            if lan.lit:
                                dl = math.hypot(nx - lan.pos[0], nz - lan.pos[2])
                                if dl < safe_r:
                                    if dl > 0.001:
                                        nx = lan.pos[0] + (nx - lan.pos[0]) / dl * safe_r
                                        nz = lan.pos[2] + (nz - lan.pos[2]) / dl * safe_r
                        s.pos[0] = nx
                        s.pos[2] = nz

            # Move Drifters
            drifters_to_remove = []
            for d in self.drifters:
                d_player = dist_xz(d.pos, self.player.pos)
                if d.state == "idle":
                    if self.player.carried >= 5 and d_player <= 15.0 and not d.has_stolen:
                        d.state = "chase"
                elif d.state == "chase":
                    if self.player.carried < 5 or d_player > 18.0:
                        d.state = "idle"
                    elif d_player > 0.001:
                        step_d = 7.0 * dt
                        d.pos[0] += (self.player.pos[0] - d.pos[0]) / d_player * step_d
                        d.pos[2] += (self.player.pos[2] - d.pos[2]) / d_player * step_d
                elif d.state == "flee":
                    d.flee_ticks -= 1
                    if d_player > 0.001:
                        d.pos[0] += (d.pos[0] - self.player.pos[0]) / d_player * (7.0 * dt)
                        d.pos[2] += (d.pos[2] - self.player.pos[2]) / d_player * (7.0 * dt)
                    if d.flee_ticks <= 0:
                        drifters_to_remove.append(d)
            for d in drifters_to_remove:
                self.drifters.remove(d)

            # 9. Contact / Damage: Drifters steal first, then Shades hit (sorted by id)
            if not self.player.is_falling and self.player.fall_respawn_delay == 0:
                for d in self.drifters:
                    if d.state == "chase" and not d.has_stolen:
                        if dist_xz(d.pos, self.player.pos) <= 1.2:
                            steal_amt = min(3, self.player.carried)
                            if steal_amt > 0:
                                self.player.carried -= steal_amt
                                d.stolen = steal_amt
                                d.has_stolen = True
                                d.state = "flee"
                                d.flee_ticks = 240
                                self._record_event(
                                    next_tick,
                                    "drifter_steal",
                                    {
                                        "drifter_id": d.id,
                                        "amount": steal_amt,
                                        "carried": self.player.carried,
                                    },
                                )

                sorted_shades = sorted(self.shades, key=lambda s: s.id)
                hit_occurred = False
                for s in sorted_shades:
                    if s.state not in ["stunned", "recoil"] and self.state == "playing":
                        # If shade is inside a just-lit lantern safe zone being pushed out, it deals NO damage
                        in_pushout = any(
                            lan.lit and lan.just_lit_ticks > 0 and dist_xz(s.pos, lan.pos) <= safe_r
                            for lan in self.lanterns
                        )
                        if in_pushout:
                            continue

                        d_xz = dist_xz(s.pos, self.player.pos)
                        d_y = abs(s.pos[1] - self.player.pos[1])
                        if d_xz <= self.tuning["shade_hit_radius"] and d_y <= 1.5:
                            if self.player.invuln_ticks <= 0 and not hit_occurred:
                                hit_occurred = True
                                self.player.flames -= 1
                                drop_amt = self.player.carried // 2
                                self.player.carried -= drop_amt

                                for i in range(drop_amt):
                                    angle = (i * 2.0 * math.pi / max(1, drop_amt))
                                    dist_m = 1.5 + (i % 3) * 0.4
                                    mx = self.player.pos[0] + dist_m * math.cos(angle)
                                    mz = self.player.pos[2] + dist_m * math.sin(angle)
                                    self.motes.append(Mote(f"M{self.next_mote_id}", [mx, self.player.pos[1], mz], "dropped", 480))
                                    self.next_mote_id += 1

                                self.player.invuln_ticks = 90
                                s.state = "recoil"
                                s.recoil_ticks = 60
                                if d_xz > 0.001:
                                    s.recoil_dir = [(s.pos[0] - self.player.pos[0]) / d_xz, (s.pos[2] - self.player.pos[2]) / d_xz]
                                else:
                                    s.recoil_dir = [1.0, 0.0]

                                self._record_event(
                                    next_tick,
                                    "player_hit",
                                    {
                                        "by": "shade",
                                        "flames": self.player.flames,
                                        "dropped": drop_amt,
                                        "lost": False,
                                    },
                                )
                                if self.player.flames <= 0:
                                    self.state = "lost"
                                    self._record_event(next_tick, "game_over", {"result": "lost", "reason": "no_flames"})
                                    self.sim_tick = next_tick
                                    break

            # 10. Spawn motes, shades, drifters according to schedule
            if step > 0 and step % 240 == 0 and len(self.motes) < 30:
                angle = self.rng.uniform(0, 2 * math.pi)
                r_mote = self.rng.uniform(8.0, 35.0)
                mx, mz = r_mote * math.cos(angle), r_mote * math.sin(angle)
                gy = self._get_ground_height(mx, mz)
                if gy is not None:
                    self.motes.append(Mote(f"M{self.next_mote_id}", [mx, gy, mz], "random"))
                    self.next_mote_id += 1

            max_shades = 6 if self.night == 1 else (8 if self.night == 2 else 10)
            spawn_interval = 480 if self.night == 1 else (420 if self.night == 2 else 360)

            should_spawn_shade = False
            spawn_count = 1
            if step == 300:
                should_spawn_shade = True
                spawn_count = 2
            elif step > 300 and (step - 300) % spawn_interval == 0:
                should_spawn_shade = True
                spawn_count = 1

            if should_spawn_shade and len(self.shades) < max_shades:
                for _ in range(min(spawn_count, max_shades - len(self.shades))):
                    a = self.rng.uniform(0, 2 * math.pi)
                    sr = 37.0 if self.night == 1 else (26.0 if self.night == 2 else 43.0)
                    sx, sz = sr * math.cos(a), sr * math.sin(a)
                    if math.hypot(sx - self.player.pos[0], sz - self.player.pos[2]) >= 15.0:
                        s_id = f"S{self.next_shade_id}"
                        self.next_shade_id += 1
                        self.shades.append(Shade(s_id, [sx, 0.0, sz], "spawning"))
                        self._record_event(next_tick, "shade_spawned", {"id": s_id})

            if self.night >= 2 and step > 0 and step % 1200 == 0:
                if len(self.drifters) < 2:
                    d_id = f"D{self.next_drifter_id}"
                    self.next_drifter_id += 1
                    da = self.rng.uniform(0, 2 * math.pi)
                    self.drifters.append(Drifter(d_id, [30.0 * math.cos(da), 1.0, 30.0 * math.sin(da)]))

            # 11. Win / Loss evaluation
            if self.time_left_s <= 0.0 and self.state == "playing":
                self.state = "lost"
                self._record_event(next_tick, "game_over", {"result": "lost", "reason": "dawn"})
                self.sim_tick = next_tick
                break

            self.sim_tick = next_tick

            # 12. Snapshot recording
            if self.sim_tick % self.snapshot_every == 0:
                self._record_snapshot()

        # End record
        end_rec = {
            "type": "end",
            "ticks": self.sim_tick,
            "state": self.state,
            "score": self.score,
        }
        self.output_lines.append(json.dumps(end_rec))

        return "\n".join(self.output_lines) + "\n"
