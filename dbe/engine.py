"""The executor: build access methods, run workloads, measure time."""

import os
import time

from .querylog import Query


class ExecutionResult:
    def __init__(self, answers, elapsed, mismatches=None):
        self.answers = answers
        self.elapsed = elapsed
        self.mismatches = mismatches or []


class QueryEngine:
    """Builds indexes and executes query logs against them.

    Index construction time is measured and reported separately from query
    processing time, as required by the assignment.
    """

    def __init__(self, relation, registry):
        self.relation = relation
        self.registry = registry
        self.methods = {}          # am name -> access method instance
        self.build_times = {}      # am name -> seconds

    def create_index(self, name: str):
        am = self.registry.create(name, self.relation)
        t0 = time.perf_counter()
        am.build()
        self.build_times[name] = time.perf_counter() - t0
        self.methods[name] = am
        return am

    def run(self, am_name: str, queries) -> ExecutionResult:
        am = self.methods[am_name]
        answers = []
        mismatches = []
        snapshot = am.snapshot_query
        interval = am.interval_query

        t0 = time.perf_counter()
        for q in queries:
            ans = snapshot(q.qstart) if q.is_snapshot else interval(q.qstart, q.qend)
            answers.append(ans)
            if q.answer != "" and int(q.answer) != ans:
                mismatches.append((q, ans))
        elapsed = time.perf_counter() - t0
        return ExecutionResult(answers, elapsed, mismatches)


def write_answers(path: str, queries, answers) -> None:
    """Write the per-query answers to ``path`` (log,qstart,qend,answer)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        fh.write("log,qstart,qend,answer\n")
        for q, ans in zip(queries, answers):
            fh.write(f"{q.log},{q.qstart},{q.qend},{ans}\n")
