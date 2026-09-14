"""Physical access methods wrapping the taxi index implementations.

Both access methods expose the same interface, so the executor can treat them
interchangeably::

    am.build()
    am.snapshot_query(q)      -> int
    am.interval_query(qs, qe) -> int
"""

from IntervalTree import IntervalTree
from GridIndex import GridIndex


class IntervalTreeAccessMethod:
    """Interval tree access method (Index/interval/IntervalTree.py)."""

    name = "it"

    def __init__(self, relation, **kwargs):
        self.relation = relation
        self.index = IntervalTree()

    def build(self):
        # Feed the column arrays straight in: no 3.7M Trip objects are built.
        self.index.build((self.relation.starts, self.relation.ends))

    def snapshot_query(self, q):
        return self.index.snapshot_query(q)

    def interval_query(self, qs, qe):
        return self.index.interval_query(qs, qe)


class GridAccessMethod:
    """Uniform 2-D grid access method (Index/grid/GridIndex.py)."""

    name = "grid"

    def __init__(self, relation, nx=100, ny=100):
        self.relation = relation
        self.index = GridIndex(nx=nx, ny=ny)

    def build(self):
        self.index.build_arrays(self.relation.starts, self.relation.ends)

    def snapshot_query(self, q):
        return self.index.snapshot_query(q)

    def interval_query(self, qs, qe):
        return self.index.interval_query(qs, qe)
