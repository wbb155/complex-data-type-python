from base_index import BaseIndex
from trip import Trip
import bisect

class ITnode:
    def __init__(self, center):
        self.center = center
        self.by_start = []   # sort by start
        self.by_end = []     # sort by end
        self.left = None
        self.right = None

class IntervalTree(BaseIndex):
    def build(self, trips):
        self.root = self._build(trips)

    def _build(self, trips):
        if not trips:
            return None
        endpoints = []

        for t in trips:
            endpoints.append(t.start)
            endpoints.append(t.end)
        endpoints.sort()
        m = len(endpoints) // 2
        center = endpoints[m-1]

        # Now we assign the intervals
        node = ITnode(center)
        left_trips, right_trips = [],[]
        for t in trips:
            if(t.end < center):
                left_trips.append(t)
            elif(t.start > center):
                right_trips.append(t)
            else:
                node.by_start.append(t)
                node.by_end.append(t)

        node.by_start.sort(key=lambda t: t.start)
        node.by_end.sort(key=lambda t: t.end)
        node.left = self._build(left_trips)
        node.right = self._build(right_trips)
        return node

    def snapshot_query(self, q):
        return self._query(self.root, q, q)

    def interval_query(self, qs, qe):
        return self._query(self.root, qs, qe)

    ## have some problems which haven't been solved
    def _query(self, node, qs, qe):
        if node is None:
            return 0
        count = 0

        if qs < node.center:
            count += self._query(node.left, qs,qe)
        elif qs > node.center:
            count += self._query(node.right, qs,qe)
        else:
            count += self._query(node.left, qs, qe)
            count += self._query(node.right, qs, qe)
        return count