#!/usr/bin/env python3
"""
CLI entry point for running Dao Den Long in headless mode according to Test Contract v1.0.
"""

import argparse
import json
import os
import sys

# Ensure src is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.core.engine import DaoDenLongSim


def load_tuning_config() -> dict:
    contract_path = os.path.join(os.path.dirname(__file__), "game.contract.json")
    if os.path.exists(contract_path):
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tuning", {})
        except Exception:
            pass
    return {}


def main():
    parser = argparse.ArgumentParser(description="Dao Den Long Headless Runner (Contract v1.0)")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for determinism")
    parser.add_argument("--night", type=int, default=1, help="Night / Level (default 1)")
    parser.add_argument("--scenario", type=str, default=None, help="Path to scenario JSON file")
    parser.add_argument("--inputs", type=str, default=None, help="Path to inputs JSON file")
    parser.add_argument("--ticks", type=int, required=True, help="Total simulation ticks to run")
    parser.add_argument("--out", type=str, required=True, help="Path to output JSONL file")
    parser.add_argument(
        "--snapshot-every", type=int, default=10, help="Snapshot interval (default 10 ticks)"
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    scenario_data = None
    if args.scenario:
        if not os.path.exists(args.scenario):
            sys.stderr.write(f"Error: Scenario file not found: {args.scenario}\n")
            sys.exit(2)
        try:
            with open(args.scenario, "r", encoding="utf-8") as f:
                scenario_data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error parsing scenario JSON: {e}\n")
            sys.exit(2)

    inputs_data = None
    if args.inputs:
        if not os.path.exists(args.inputs):
            sys.stderr.write(f"Error: Inputs file not found: {args.inputs}\n")
            sys.exit(2)
        try:
            with open(args.inputs, "r", encoding="utf-8") as f:
                inputs_data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error parsing inputs JSON: {e}\n")
            sys.exit(2)

    tuning = load_tuning_config()

    try:
        sim = DaoDenLongSim(
            seed=args.seed,
            night=args.night,
            tuning=tuning,
            scenario_data=scenario_data,
            inputs_data=inputs_data,
            snapshot_every=args.snapshot_every,
        )
        output_content = sim.run(args.ticks)
    except ValueError as e:
        sys.stderr.write(f"Validation Error (Input/Scenario): {e}\n")
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"Simulation runtime error: {e}\n")
        sys.exit(1)

    try:
        out_dir = os.path.dirname(args.out)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output_content)
    except Exception as e:
        sys.stderr.write(f"Error writing output file: {e}\n")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
