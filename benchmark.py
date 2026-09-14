#!/usr/bin/env python3
"""
Task 4 driver: experimentally compare the interval tree (IT) and the grid.

Usage
-----
    python benchmark.py --use-logs DIR --trips PATH --answers DIR

    --use-logs DIR   directory holding querylogs.csv
    --trips PATH     the preprocessed Trip table (.parquet or .csv)
    --answers DIR    output directory

For every graded log it writes DIR/<log>/it.csv and DIR/<log>/grid.csv (one row
per query: log,qstart,qend,answer) and prints, per log, a line

    <log> IT <seconds> GRID <seconds>

followed by the index construction times, reported separately:

    BUILD IT <seconds> GRID <seconds>
"""

import argparse
import sys

from dbe.catalog import AccessMethodRegistry
from dbe.relation import TripRelation
from dbe.access_methods import IntervalTreeAccessMethod, GridAccessMethod
from dbe.engine import QueryEngine, write_answers
from dbe.querylog import read_querylogs

GRADED_LOGS = ("snapshot", "interval_0.01pct", "interval_0.1pct", "interval_1pct")


def build_registry() -> AccessMethodRegistry:
    registry = AccessMethodRegistry()
    registry.register("it", IntervalTreeAccessMethod)
    registry.register("grid", GridAccessMethod)
    return registry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="IT vs grid query benchmark (Task 4)")
    parser.add_argument("--use-logs", required=True, metavar="DIR",
                        help="directory holding querylogs.csv")
    parser.add_argument("--trips", required=True, metavar="PATH",
                        help="the preprocessed Trip table (.parquet or .csv)")
    parser.add_argument("--answers", required=True, metavar="DIR",
                        help="output directory for the answer files")
    args = parser.parse_args(argv)

    relation = TripRelation.load(args.trips)
    print(f"# loaded {len(relation)} trips, "
          f"domain={relation.stats.domain_length()}s", file=sys.stderr)

    engine = QueryEngine(relation, build_registry())
    engine.create_index("it")
    engine.create_index("grid")
    print(f"BUILD IT {engine.build_times['it']:.6f} "
          f"GRID {engine.build_times['grid']:.6f}")

    groups = read_querylogs(args.use_logs)

    # graded logs first, in the canonical order; then any extras found
    order = [g for g in GRADED_LOGS if g in groups]
    order += [g for g in groups if g not in order]

    for log in order:
        queries = groups[log]
        it_res = engine.run("it", queries)
        grid_res = engine.run("grid", queries)

        write_answers(f"{args.answers}/{log}/it.csv", queries, it_res.answers)
        write_answers(f"{args.answers}/{log}/grid.csv", queries, grid_res.answers)

        print(f"{log} IT {it_res.elapsed:.6f} GRID {grid_res.elapsed:.6f}")
        for name, res in (("it", it_res), ("grid", grid_res)):
            if res.mismatches:
                print(f"# WARNING {log}/{name}: {len(res.mismatches)} mismatches",
                      file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
