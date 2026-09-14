"""
Uniform 2-D grid access method for the [Trip.start, Trip.end] interval table.

The grid answers the *same* stabbing / interval queries as the interval tree.
Each trip is embedded as a point in the (start, end) plane::

        trip [s, e]  <->  point (s, e)

and an interval query [qs, qe] becomes the axis-aligned rectangle::

        start in [dmin, qe]   and   end in [qs, dmax]

where dmin = min(start) and dmax = max(end) over the domain.

The grid is a GX * GY array of cells.  A query visits only the cells its
rectangle overlaps, using the optimisations described in the notes:

  * a cell wholly inside the rectangle contributes its stored count directly
    (the whole interior is accumulated in O(1) with a 2-D prefix sum);
  * a cell the query spans on one axis needs only the *other* coordinate
    tested (a binary search on that cell's sorted start/end list);
  * the one corner cell is resolved with two binary searches;
  * cells the rectangle does not touch are never visited (no full 10 000-cell
    sweep).
"""

import bisect


class GridIndex:
    def __init__(self, nx: int = 100, ny: int = 100):
        self.nx = nx
        self.ny = ny
        self.dmin = 0
        self.dmax = 0
        self._span = 1
        # per-cell sorted key lists
        self._starts = None   # nx x ny, each a sorted list of starts
        self._ends = None     # nx x ny, each a sorted list of ends
        self._prefix = None   # (nx+1) x (ny+1) prefix sums of cell counts

    # ------------------------------------------------------------------ build
    def build(self, trips):
        """Build from any iterable of objects exposing ``.start`` / ``.end``."""
        starts, ends = [], []
        for t in trips:
            starts.append(t.start)
            ends.append(t.end)
        self.build_arrays(starts, ends)

    def build_arrays(self, starts, ends):
        """Build from two parallel sequences of start / end values."""
        if not isinstance(starts, list):
            starts = list(starts)
            ends = list(ends)

        nx, ny = self.nx, self.ny
        self._starts = [[[] for _ in range(ny)] for _ in range(nx)]
        self._ends = [[[] for _ in range(ny)] for _ in range(nx)]

        if starts:
            self.dmin = min(starts)
            self.dmax = max(ends)
            self._span = self.dmax - self.dmin + 1
            for s, e in zip(starts, ends):
                self._starts[self._index_of(s, nx)][self._index_of(e, ny)].append(s)
                self._ends[self._index_of(s, nx)][self._index_of(e, ny)].append(e)
        else:
            self.dmin = self.dmax = 0
            self._span = 1

        # sort each cell's key lists and build the 2-D prefix sum of counts
        prefix = [[0] * (ny + 1) for _ in range(nx + 1)]
        cells_s = self._starts
        cells_e = self._ends
        for i in range(nx):
            row_s = cells_s[i]
            row_e = cells_e[i]
            above = prefix[i]
            cur = prefix[i + 1]
            run = 0
            for j in range(ny):
                lst = row_s[j]
                if lst:
                    lst.sort()
                    row_e[j].sort()
                run += len(lst)
                cur[j + 1] = above[j + 1] + run
        self._prefix = prefix

    def _index_of(self, v, n):
        if v <= self.dmin:
            return 0
        if v >= self.dmax:
            return n - 1
        return (v - self.dmin) * n // self._span

    # ---------------------------------------------------------------- queries
    def snapshot_query(self, q):
        return self.interval_query(q, q)

    def interval_query(self, qs, qe):
        cx = self._index_of(qe, self.nx)   # boundary column (straddles qe)
        cy = self._index_of(qs, self.ny)   # boundary row    (straddles qs)

        count = 0

        # interior: columns [0, cx-1] x rows [cy+1, ny-1] are wholly inside
        if cx >= 1 and cy + 1 <= self.ny - 1:
            count += self._rect(0, cx - 1, cy + 1, self.ny - 1)

        starts = self._starts
        ends = self._ends

        # boundary column cx, rows fully inside on y -> test x only
        col_s = starts[cx]
        for r in range(cy + 1, self.ny):
            lst = col_s[r]
            if lst:
                count += bisect.bisect_right(lst, qe)

        # boundary row cy, columns fully inside on x -> test y only
        for c in range(cx):
            lst = ends[c][cy]
            if lst:
                count += len(lst) - bisect.bisect_left(lst, qs)

        # single corner cell -> test both coordinates
        corner_s = starts[cx][cy]
        if corner_s:
            count += bisect.bisect_right(corner_s, qe) - bisect.bisect_left(ends[cx][cy], qs)

        return count

    def _rect(self, x0, x1, y0, y1):
        p = self._prefix
        return p[x1 + 1][y1 + 1] - p[x0][y1 + 1] - p[x1 + 1][y0] + p[x0][y0]
