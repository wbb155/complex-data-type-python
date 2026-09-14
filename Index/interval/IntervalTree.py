"""
Interval tree over [Trip.start, Trip.end] intervals (numpy-backed).

SCOPE: reference prototype.  Validated and fully runnable on the sample and on
moderate tables (<= ~500k intervals).  It also *builds* the full 3.7M-trip table
(the "stack" builder), but the query phase is too slow at that scale: each query
walks the tree in Python and pays one Python<->C round-trip per node.  For the
full dataset, plug a native backend (C/Numba) into dbe/access_methods.py.

Each node answers with a binary search on one of its two sorted key arrays,
so a node never scans its intervals:

    node.center   domain center = lower median of the endpoints in the subtree
    node.cnt      number of intervals that span the center
    node.starts   sorted starts of those spanning intervals   (for binary search)
    node.ends     sorted ends   of those spanning intervals   (for binary search)
    node.left     subtree of intervals entirely left  of the center
    node.right    subtree of intervals entirely right of the center

Only counts are ever needed, so a node does not have to keep the Trip objects
themselves - two sorted key arrays plus a count are enough, and they are kept
as numpy arrays so that construction (which runs on millions of intervals)
stays at C speed.

Two construction routines are provided and produce identical trees:

    method="recursive"   textbook recursion (_build)
    method="stack"       explicit stack (_build_stack); not bounded by Python's
                         recursion limit, so it also builds the full dataset
"""

import numpy as np

from base_index import BaseIndex


class ITnode:
    __slots__ = ("center", "cnt", "starts", "ends", "left", "right")

    def __init__(self, center, cnt, starts, ends):
        self.center = center
        self.cnt = cnt            # number of spanning intervals
        self.starts = starts      # sorted numpy array of their starts
        self.ends = ends          # sorted numpy array of their ends
        self.left = None
        self.right = None


class IntervalTree(BaseIndex):
    def build(self, trips, method="stack"):
        """Build the tree.

        trips is either a pair (starts, ends) or an iterable of Trip objects.
        method="recursive" uses the textbook recursion (_build); method="stack"
        uses an explicit stack (_build_stack) and is not bounded by Python's
        recursion limit, so it also builds the full dataset.
        """
        starts, ends = self._to_arrays(trips)
        if method == "recursive":
            self.root = self._build(starts, ends)
        elif method == "stack":
            self.root = self._build_stack(starts, ends)
        else:
            raise ValueError(f"unknown build method: {method!r}")

    @staticmethod
    def _to_arrays(trips):
        if isinstance(trips, tuple) and len(trips) == 2:
            starts, ends = trips
            return (np.ascontiguousarray(starts, dtype=np.int64),
                    np.ascontiguousarray(ends, dtype=np.int64))
        trips = list(trips)
        starts = np.fromiter((t.start for t in trips), dtype=np.int64, count=len(trips))
        ends = np.fromiter((t.end for t in trips), dtype=np.int64, count=len(trips))
        return starts, ends

    def _split(self, S, E):
        """Pick this node's center (lower median of the endpoints) and split
        the intervals into (spanning, left, right).  Shared by both builds."""
        endpoints = np.concatenate((S, E))
        m = endpoints.size // 2
        center = int(np.partition(endpoints, m - 1)[m - 1])

        left = E < center
        right = S > center
        span = ~(left | right)

        starts = np.sort(S[span])
        ends = np.sort(E[span])
        node = ITnode(center, starts.size, starts, ends)
        return node, S[left], E[left], S[right], E[right]

    # ---- build the tree from the intervals (recursive reference version) ----
    def _build(self, S, E):
        if S.size == 0:
            return None
        node, ls, le, rs, re = self._split(S, E)
        node.left = self._build(ls, le)
        node.right = self._build(rs, re)
        return node

    # ---- build the tree from the intervals (iterative: explicit stack) ----
    def _build_stack(self, S, E):
        if S.size == 0:
            return None
        root = None
        # work items: (starts, ends, parent node, side); side -1 = left, +1 = right
        stack = [(S, E, None, 0)]
        while stack:
            s, e, parent, side = stack.pop()
            node, ls, le, rs, re = self._split(s, e)
            if parent is None:
                root = node
            elif side < 0:
                parent.left = node
            else:
                parent.right = node
            if ls.size:
                stack.append((ls, le, node, -1))
            if rs.size:
                stack.append((rs, re, node, 1))
        return root

    def snapshot_query(self, q):
        return self._query(self.root, q, q)

    def interval_query(self, qs, qe):
        return self._query(self.root, qs, qe)

    # interval query: one binary search per node, descending only into subtrees
    # that can still intersect the query
    def _query(self, node, qs, qe):
        if node is None:
            return 0
        c = node.center
        if qe < c:                       # query lies entirely left of center
            count = int(np.searchsorted(node.starts, qe, side="right"))
            return count + self._query(node.left, qs, qe)
        elif qs > c:                     # query lies entirely right of center
            count = node.ends.size - int(np.searchsorted(node.ends, qs, side="left"))
            return count + self._query(node.right, qs, qe)
        else:                            # qs <= c <= qe: center inside the query
            return (node.cnt
                    + self._query(node.left, qs, qe)
                    + self._query(node.right, qs, qe))