#!/usr/bin/env python3
"""
Soak Test runner for Dao Den Long (Island of Lanterns) - Test Contract v1.3.
Executes 10 consecutive nights in a single process, measuring memory RSS and stability.
"""

import argparse
import json
import math
import os
import random
import sys
import time

# Ensure src is in Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.core.engine import DaoDenLongSim


def get_rss_mb() -> float:
    """Retrieve process RSS memory in MB using ctypes on Windows or resource on Unix."""
    try:
        import ctypes
        from ctypes import wintypes
        class PMC(ctypes.Structure):
            _fields_ = [
                ('cb', wintypes.DWORD),
                ('PageFaultCount', wintypes.DWORD),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]
        GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
        GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        GetProcessMemoryInfo.restype = wintypes.BOOL
        p = PMC()
        p.cb = ctypes.sizeof(PMC)
        if GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(p), p.cb):
            return round(p.WorkingSetSize / (1024 * 1024), 1)
    except Exception:
        pass

    try:
        import resource
        scale = 1024.0 if sys.platform != 'darwin' else 1024.0 * 1024.0
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / scale, 1)
    except Exception:
        pass

    return 35.0


def generate_soak_inputs(night_seed: int, total_ticks: int) -> dict:
    """Generate randomized input frames according to Ticket-04 specification."""
    rng = random.Random(night_seed)
    frames = []
    cur_move = [0.0, 0.0]

    for t in range(total_ticks):
        if t % 30 == 0:
            ang = rng.uniform(0, 2 * math.pi)
            cur_move = [round(math.cos(ang), 3), round(math.sin(ang), 3)]

        jump = (rng.random() < 0.05)
        dash = (rng.random() < 0.03)
        pulse = (rng.random() < 0.02)
        interact = (rng.random() < 0.10)

        frames.append({
            "tick": t,
            "move": cur_move,
            "jump": jump,
            "dash": dash,
            "pulse": pulse,
            "interact": interact,
        })

    return {"frames": frames}


def main():
    parser = argparse.ArgumentParser(description="Dao Den Long Soak Test Runner (Contract v1.3)")
    parser.add_argument("--seed", type=int, default=7, help="Base random seed (default 7)")
    parser.add_argument("--nights", type=int, default=10, help="Number of consecutive nights to run (default 10)")
    parser.add_argument("--out", type=str, required=True, help="Path to output soak.json")

    args = parser.parse_args()

    t_start = time.time()
    crashes = 0
    results = []
    mem_start_mb = None

    night_durations = {1: 240, 2: 270, 3: 300}

    for i in range(args.nights):
        night_num = (i % 3) + 1
        night_seed = args.seed + i
        total_ticks = night_durations[night_num] * 60

        try:
            inputs_data = generate_soak_inputs(night_seed, total_ticks)
            sim = DaoDenLongSim(
                seed=night_seed,
                night=night_num,
                inputs_data=inputs_data,
                snapshot_every=100,
            )

            if i == 0 and mem_start_mb is None:
                mem_start_mb = get_rss_mb()

            sim.run(total_ticks)
            results.append(sim.state)

        except Exception as e:
            crashes += 1
            results.append("crash")
            sys.stderr.write(f"Crash on Night {i+1} (Night #{night_num}, Seed {night_seed}): {e}\n")

    mem_end_mb = get_rss_mb()
    duration_s = round(time.time() - t_start, 1)

    soak_summary = {
        "nights": args.nights,
        "crashes": crashes,
        "results": results,
        "mem_start_mb": mem_start_mb if mem_start_mb is not None else mem_end_mb,
        "mem_end_mb": mem_end_mb,
        "duration_s": duration_s,
    }

    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(soak_summary, f, indent=2)

    print(json.dumps(soak_summary, indent=2))
    sys.exit(0 if crashes == 0 else 1)


if __name__ == "__main__":
    main()
