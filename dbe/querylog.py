"""Reading the query workload (querylogs.csv)."""

import csv
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Query:
    log: str
    qstart: int
    qend: int
    answer: str = ""      # expected answer when provided, empty for graded logs

    @property
    def is_snapshot(self) -> bool:
        return self.qstart == self.qend


def read_querylogs(directory: str, filename: str = "querylogs.csv"):
    """Return ``{log_name: [Query, ...]}`` preserving file order."""
    path = os.path.join(directory, filename)
    groups = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            q = Query(
                log=row["log"],
                qstart=int(row["qstart"]),
                qend=int(row["qend"]),
                answer=row.get("answer", "") or "",
            )
            groups.setdefault(q.log, []).append(q)
    return groups
