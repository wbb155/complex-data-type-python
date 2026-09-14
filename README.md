# complex-data-type
a repository for complex-data-type in hku
assignment for COMP7107 Management of complex data types [Section 1A, 2026]

## Assignment 1
create interval tree for taxi data
Use dataset in website https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page which records information about taxi trips in NYC. Goto 2026 and click on January Yellow Taxi Trip Records.

### Interval Tree
Proposed for managing intervals in memory
Output sensitive search time: O(logn+k)
Space complexity: O(n)
Construction cost: O(nlogn)

We use a binary tree to manage intervals. 

1. Find the median point of all intervals endpoints
2. Collect Intervals that include c, saving them to current node in the tree
3. Maintain two arrays, one for intervals sorted by start point, another one for intervals sorted by end point
4. Intervals before c will be put into the left node, while intervals after c will be put into the right node. Both nodes will be processed in the same way as their father node. 

### Implementation status (scope)

The Python / NumPy implementation under `Index/` is the **reference prototype**.

| Scale | Build | Query | Runnable end-to-end |
| --- | --- | --- | --- |
| `data/sample.csv` (1,000) | yes | yes | **yes** (`benchmark.py` produces `it.csv` / `grid.csv`) |
| ~500k intervals | yes | yes | yes |
| full `data/trips.parquet` (3,724,889) | yes (NumPy `stack` builder) | no | no - query phase too slow |

Notes:

* The interval tree exposes two equivalent builders: `_build` (recursive) and
  `_build_stack` (explicit stack, not bound by the recursion limit). The tree
  itself is balanced (depth ~ log2 n) and builds on the full table in seconds.
* The bottleneck at full scale is the **query** phase: each query walks the tree
  in Python, paying one Python<->C round-trip per node. This is inherent to the
  pure-Python implementation, not a bug in the algorithm.
* The driver and catalog framework (`dbe/`) are language-agnostic. To handle the
  full dataset, replace only the implementation behind
  `dbe/access_methods.py` with a native backend (C extension or Numba); the
  relation, query-log and engine layers stay unchanged.

