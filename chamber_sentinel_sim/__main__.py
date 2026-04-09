"""CLI entry point for the Chamber Sentinel simulation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .config import ScenarioConfig
from .scenarios.assertions import AssertionEngine
from .scenarios.runner import SimulationRunner


def cmd_run(args: argparse.Namespace) -> int:
    """Run a simulation scenario."""
    scenario_path = args.scenario

    # Check if it's a built-in scenario name
    if not os.path.exists(scenario_path):
        builtin = Path(__file__).parent / "scenarios" / scenario_path
        if builtin.exists():
            scenario_path = str(builtin)
        elif not scenario_path.endswith(".yaml"):
            builtin_yaml = Path(__file__).parent / "scenarios" / f"{scenario_path}.yaml"
            if builtin_yaml.exists():
                scenario_path = str(builtin_yaml)

    if not os.path.exists(scenario_path):
        print(f"Error: scenario file not found: {scenario_path}")
        return 1

    config = ScenarioConfig.load(scenario_path)

    if args.seed is not None:
        config.seed = args.seed
    if args.acceleration is not None:
        config.acceleration = args.acceleration

    output_dir = args.output_dir or os.path.join("sim_output", config.name)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Chamber Sentinel Simulation")
    print(f"  Scenario:  {config.name}")
    print(f"  Duration:  {config.duration_days} days")
    print(f"  Patients:  {len(config.patients)}")
    print(f"  Seed:      {config.seed}")
    print(f"  Output:    {output_dir}")
    print()

    runner = SimulationRunner(config, output_dir)
    stats = runner.run(verbose=args.verbose)

    print()
    print(f"Simulation complete in {stats['wall_time_seconds']:.1f}s")
    print(f"  Ticks:        {stats['ticks']}")
    print(f"  Items gen:    {stats['items_generated']}")
    print(f"  Classified:   {stats['items_classified']}")
    print(f"  Delivered:    {stats['items_delivered_to_vault']}")
    print(f"  Burned:       {stats['items_burned']}")
    print(f"  Reports:      {stats['reports_generated']}")

    # Run assertions
    print()
    print("Running assertions...")
    engine = AssertionEngine(output_dir)
    results = engine.run_all(config.assertions)
    for r in results:
        icon = "+" if r.passed else "X"
        print(f"  [{icon}] {r.name}: {r.details}")

    print()
    if engine.all_passed:
        print("All assertions PASSED")
        return 0
    else:
        failed = [r for r in results if not r.passed]
        print(f"{len(failed)} assertion(s) FAILED")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List built-in scenarios."""
    scenarios_dir = Path(__file__).parent / "scenarios"
    yamls = sorted(scenarios_dir.glob("*.yaml"))
    if not yamls:
        print("No built-in scenarios found.")
        return 0
    print("Built-in scenarios:")
    for y in yamls:
        try:
            config = ScenarioConfig.load(str(y))
            print(f"  {y.stem:20s}  {config.duration_days:>5.0f}d  {len(config.patients)}p  {config.description[:60]}")
        except Exception as e:
            print(f"  {y.stem:20s}  (error: {e})")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a scenario file."""
    try:
        config = ScenarioConfig.load(args.scenario)
        print(f"Valid scenario: {config.name}")
        print(f"  Duration: {config.duration_days} days")
        print(f"  Patients: {len(config.patients)}")
        print(f"  Events:   {len(config.events)}")
        print(f"  Assertions: {', '.join(config.assertions)}")
        return 0
    except Exception as e:
        print(f"Invalid scenario: {e}")
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Generate report from simulation output."""
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        print(f"Output directory not found: {output_dir}")
        return 1

    # Stats
    stats_path = os.path.join(output_dir, "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path) as f:
            stats = json.load(f)
        print("Simulation Stats:")
        for k, v in stats.items():
            print(f"  {k}: {v}")

    # Assertions
    results_path = os.path.join(output_dir, "assertions", "results.json")
    if os.path.exists(results_path):
        with open(results_path) as f:
            results = json.load(f)
        print("\nAssertion Results:")
        for r in results:
            icon = "+" if r["passed"] else "X"
            print(f"  [{icon}] {r['name']}: {r['details']}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chamber-sentinel-sim",
        description="Chamber Sentinel — Local Simulation Environment",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    run_p = sub.add_parser("run", help="Run a simulation scenario")
    run_p.add_argument("scenario", help="Path to scenario YAML or built-in name")
    run_p.add_argument("--seed", type=int, help="Override random seed")
    run_p.add_argument("--acceleration", type=float, help="Override time acceleration")
    run_p.add_argument("--output-dir", help="Output directory")
    run_p.add_argument("--verbose", "-v", action="store_true", help="Verbose progress output")

    # list
    sub.add_parser("list-scenarios", help="List built-in scenarios")

    # validate
    val_p = sub.add_parser("validate", help="Validate a scenario file")
    val_p.add_argument("scenario", help="Path to scenario YAML")

    # report
    rep_p = sub.add_parser("report", help="View results from a completed simulation")
    rep_p.add_argument("output_dir", help="Simulation output directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "run": cmd_run,
        "list-scenarios": cmd_list,
        "validate": cmd_validate,
        "report": cmd_report,
    }
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
