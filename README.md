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

