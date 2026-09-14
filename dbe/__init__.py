"""
dbe - a tiny, DB-flavoured query engine for the COMP7107 taxi assignment.

It is intentionally laid out like the pieces of a real relational engine:

    catalog         system catalogs (schema, statistics, access-method registry)
    relation        a stored relation (the Trip table) with its columns/stats
    access_methods  physical access methods (interval tree, grid) registered
                    as pluggable "AM"s, in the spirit of PostgreSQL's pg_am
    querylog        the workload (query logs) read from querylogs.csv
    engine          the executor: builds indexes, runs workloads, times them

Keeping the taxi index implementations (Index/interval, Index/grid) on the
path lets the access methods reuse the code that already exists.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "Index", "interval"),
           os.path.join(_ROOT, "Index", "grid")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
