# Graph Traversal Using an Adjacency Matrix

## Technical scope

Graph traversal is the process of visiting vertices according to the relationships represented by a graph. An adjacency matrix stores these relationships in a two-dimensional array, where the entry at row `u` and column `v` describes the edge from vertex `u` to vertex `v`.

This implementation studies graph traversal through five complementary representations: a Python graph-processing library, an event-driven JavaScript implementation, a C++ transport-network case study, a Java service-dependency model, and a PostgreSQL relational representation.

The central distinction is between the **graph representation** and the **traversal algorithm**. The adjacency matrix defines the available edges. Breadth-first search and depth-first search determine the order in which reachable vertices are explored.

## Adjacency matrix fundamentals

For a graph with \(V\) vertices, the adjacency matrix is a \(V \times V\) matrix.

For an unweighted graph, its entries are commonly defined as

\[
A[u][v] =
\begin{cases}
1 & \text{if an edge exists from }u\text{ to }v,\\
0 & \text{otherwise.}
\end{cases}
\]

For an undirected graph, the matrix is symmetric:

\[
A[u][v] = A[v][u].
\]

For a directed graph, symmetry is not required. An edge from a service to a dependency does not automatically create a reverse edge.

A weighted adjacency matrix stores edge costs instead of binary values. This representation requires a clear convention for absent edges. The programs use zero for no edge between distinct vertices and positive values for existing weighted edges. Consequently, zero-cost edges are not supported by these weighted examples.

A self-loop is represented by a diagonal entry. The implementations reject self-loops in their basic graph models or exclude diagonal entries from neighbor discovery.

### Example matrix

Consider a graph with four vertices and undirected edges between vertices `0` and `1`, `0` and `2`, and `1` and `3`.

The matrix is

\[
A =
\begin{bmatrix}
0 & 1 & 1 & 0\\
1 & 0 & 0 & 1\\
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0
\end{bmatrix}.
\]

The entry `A[0][2]` is `1`, so vertex `2` is adjacent to vertex `0`. The entry `A[0][3]` is `0`, so no direct edge connects those vertices.

## Breadth-first search

Breadth-first search (BFS) explores the graph in layers of increasing distance from a starting vertex. It uses a first-in, first-out queue.

For an unweighted graph, BFS computes the minimum number of edges needed to reach each reachable vertex from the starting vertex.

The algorithm maintains three important structures:

- The queue holds vertices awaiting processing.
- The visited or discovered structure prevents the same vertex from being enqueued repeatedly.
- The parent array records the predecessor through which each vertex was first discovered.

A distance of zero is assigned to the starting vertex. When a previously undiscovered neighbor is found, its distance becomes the current vertex's distance plus one.

The parent relationships form a BFS tree. Following parent pointers backward from a target reconstructs a shortest path in terms of edge count.

BFS does not guarantee the minimum total weight in a weighted graph. Its distance calculation counts edges, not travel cost. Weighted shortest paths require an appropriate algorithm such as Dijkstra's algorithm when all edge weights are nonnegative.

### Python implementation

The `GraphMatrix.bfs` method uses `collections.deque` for queue operations. It returns a `TraversalResult` containing the visit order, parent relationships, and distances.

The `path_to` method reconstructs a route and returns `None` when the target is unreachable. It validates the target index before accessing the result arrays.

The script also demonstrates disconnected graphs. A traversal starting in one connected component does not visit vertices in another component.

### JavaScript implementation

The JavaScript implementation uses an array and a moving queue-head index. This avoids the repeated element shifting associated with calling `Array.shift()` for every dequeue.

The optional `onVisit` callback exposes traversal events. Consumers can record visits, update a user interface, or forward events to a monitoring component without embedding those responsibilities in the traversal algorithm.

The callback is synchronous, while a separate asynchronous demonstration illustrates how traversal results can be consumed within a Node.js application.

### Java implementation

The Java implementation uses `ArrayDeque<Integer>` for efficient queue operations and returns an immutable `TraversalResult`.

The result's constructor copies the supplied collections. This prevents callers from accidentally changing recorded traversal order or distance values after the computation finishes.

The `GraphType` enum distinguishes directed from undirected graphs. This makes the graph's structural behavior explicit and allows the connected-component operation to reject unsupported directed-graph input.

### C++ implementation

The transport-network case study models intersections as vertices and roads as edges. The BFS distance represents the fewest roads needed to reach each intersection, while the reconstructed path gives the corresponding route.

The implementation uses `std::queue<int>` and dynamically sized vectors. A `GraphError` exception reports invalid vertices, malformed matrices, and unsupported algorithm configurations.

## Depth-first search

Depth-first search (DFS) follows one branch as far as possible before backtracking. It can be implemented recursively or iteratively with an explicit stack.

The implementations use iterative DFS to avoid depending on the language runtime's call-stack depth. This matters when graphs contain long chains of vertices.

DFS produces an exploration order, but it does not generally produce shortest paths. The depth of a DFS-tree vertex depends on the order in which branches are explored, not simply on the minimum number of edges from the start.

Neighbor ordering also affects traversal order. The examples enumerate matrix columns in ascending order and use reverse stack insertion where necessary to produce predictable visits.

A deterministic order is useful for debugging and automated tests. It should not be interpreted as a guarantee that every implementation or every neighbor-ordering policy will produce the same DFS sequence.

## Directed graphs and connected components

A directed graph distinguishes outgoing edges from incoming edges. A traversal from vertex `u` follows entries in row `u`, so it reaches vertices accessible through outgoing edges.

For an undirected graph, connected components are maximal sets of vertices in which every pair of vertices is connected by a path.

The Python, JavaScript, C++, and Java implementations identify connected components by starting a traversal at each unvisited vertex. Every vertex discovered during that traversal belongs to the same component.

This method is not a complete treatment of directed connectivity. Directed graphs require a defined connectivity model:

- Weakly connected components ignore edge direction when determining connectivity.
- Strongly connected components require every vertex in a component to be reachable from every other vertex through directed paths.

The Java service-dependency model is directed because dependency relationships have direction. Its reachability results should not be interpreted as undirected connected components.

## Weighted graphs and Dijkstra's algorithm

Weighted edges represent costs such as travel time, latency, or monetary distance.

Dijkstra's algorithm repeatedly selects the unsettled vertex with the smallest known distance and relaxes its outgoing edges. Relaxation replaces a tentative distance when a cheaper route is found.

The Python and JavaScript examples use a matrix-based implementation with \(O(V^2)\) time complexity. The C++ case study also uses this approach. For an adjacency matrix, scanning all possible neighbors takes \(O(V)\) time per processed vertex, making the overall time complexity \(O(V^2)\).

All three implementations reject negative edge weights. Dijkstra's algorithm relies on nonnegative weights to justify permanently settling the currently closest vertex.

An unreachable vertex retains an infinite distance. Applications must distinguish this value from a valid numeric route cost.

For sparse graphs, an adjacency list combined with a priority queue is generally more efficient than scanning every matrix cell. The matrix remains useful when the graph is dense or when direct edge lookup is important.

## C++ case study: transport-network routing

The C++ program represents a road network using a symmetric adjacency matrix. Each intersection receives an integer index, and a matrix entry of `1` indicates a direct road connection.

Its BFS output provides the minimum number of roads from the starting intersection. The parent array supports route reconstruction without storing a complete path for every discovered vertex.

The weighted example models road costs and uses Dijkstra's algorithm to find minimum accumulated costs. The cost is not necessarily the same as the fewest number of roads.

The implementation separates graph validation, neighbor discovery, traversal, path reconstruction, and output. This structure makes the algorithm's responsibilities explicit and keeps malformed input from silently entering the traversal logic.

The matrix requires \(O(V^2)\) memory. It is a reasonable representation for a small, dense network, but a network containing millions of intersections and relatively few roads would usually benefit from an adjacency list.

## Java case study: service dependencies

The Java program models service dependencies as directed edges. A service is represented by a vertex, and an edge from one vertex to another indicates an outgoing dependency relationship.

BFS identifies which services are reachable from a starting service and measures the shortest dependency-chain length in edges. The parent array reconstructs the chain leading to a reachable service.

The implementation validates that the adjacency matrix is square and that an undirected matrix is symmetric. Its graph type is immutable after construction, and traversal results are returned as immutable collections.

These decisions are useful in enterprise systems because graph data and analysis results often pass between multiple application components. Defensive copying reduces accidental mutation, while explicit graph types prevent callers from confusing directed reachability with undirected connectivity.

A dependency graph can contain cycles. Traversal must mark vertices as discovered so that a cycle does not lead to infinite exploration. A traversal order alone does not prove that a dependency graph is acyclic; cycle detection or topological analysis is needed for that separate question.

## PostgreSQL data model

The SQL implementation stores graph data relationally rather than placing the entire matrix in one database column.

The `graph_definitions` table identifies individual graphs. The `graph_vertices` table stores vertex indices and labels. The `graph_edges` table stores directed edge records and their weights.

Composite foreign keys ensure that each edge references valid vertices in the same graph. The edge primary key prevents duplicate directed edges for a given source and target. Positive-weight constraints reject invalid weighted edges.

The transport graph stores each undirected edge in both directions. This convention allows traversal queries to use the same outgoing-edge join used for directed graphs. It requires consistent insertion and update behavior so that reverse edges remain synchronized.

### Matrix reconstruction

A relational matrix can be reconstructed by joining each source vertex to each target vertex and left-joining the corresponding edge. `COALESCE` converts missing edges into zero-valued matrix cells.

This operation returns \(V^2\) rows per graph. Its output can become expensive for large sparse graphs because the result includes absent edges as well as existing edges.

The normalized edge table is therefore the persistent source of truth, while the matrix-shaped query is a useful analytical or display representation.

### Recursive traversal

PostgreSQL recursive common table expressions support graph reachability by repeatedly joining the current set of reachable vertices to outgoing edges.

The SQL example tracks a path array and rejects a candidate extension when the target already appears in that path. This prevents an individual candidate path from revisiting a vertex.

The recursive query enumerates simple paths rather than implementing a queue-based BFS directly. It uses path length and deterministic ordering to select a shortest path for each target in the sample graph.

This distinction matters for performance. The number of simple paths can grow exponentially in dense graphs, so recursive path enumeration is not a general replacement for an efficient BFS implementation. For large graphs, an application-side BFS, a dedicated graph-processing system, or a carefully designed iterative database procedure may be more appropriate.

The `traversal_results` table persists selected paths, their distances, and the algorithm name. Its foreign keys ensure that the stored starting and target vertices exist in the specified graph.

## Complexity and representation trade-offs

Let \(V\) be the number of vertices and \(E\) the number of edges.

| Operation | Adjacency matrix |
|---|---|
| Matrix storage | \(O(V^2)\) |
| Check whether a specific edge exists | \(O(1)\) |
| Enumerate a vertex's neighbors | \(O(V)\) |
| BFS traversal | \(O(V^2)\) |
| DFS traversal | \(O(V^2)\) |
| Matrix-based Dijkstra | \(O(V^2)\) |
| Reconstruct a path from parent pointers | \(O(L)\), where \(L\) is the path length |

For an adjacency-list representation, BFS and DFS take \(O(V+E)\) time when the graph is traversed from a starting vertex and neighbor enumeration is efficient.

An adjacency matrix is most attractive when direct edge lookup and dense connectivity justify its storage cost. An adjacency list is generally preferable when the number of edges is much smaller than \(V^2\).

## Validation and failure handling

Malformed matrices can cause incorrect traversals or invalid memory access. Each implementation validates the matrix shape before using it.

Undirected unweighted matrices must be symmetric. Unweighted entries must follow the binary convention. Traversal starting points and path targets must fall within the valid vertex range.

The weighted examples reject negative weights and use zero to indicate the absence of an edge. Applications that require zero-cost edges need a different representation, such as a separate edge-presence matrix or an explicit sentinel for missing edges.

Disconnected graphs require special handling because not every target has a path from every starting vertex. A path-reconstruction method should report unreachable targets instead of fabricating a route.

## Practical applications

- **Network analysis:** BFS can determine minimum-hop reachability between nodes, while DFS can explore dependency structures.
- **Service dependency analysis:** A directed graph can identify services accessible through chains of dependencies.
- **Transport planning:** BFS minimizes the number of roads in an unweighted network; Dijkstra minimizes accumulated nonnegative road costs.
- **Connectivity assessment:** Connected-component analysis can identify isolated segments in an undirected network.
- **Database analysis:** Recursive queries can inspect reachability and reconstruct paths when graph size and path complexity remain manageable.

The correct traversal algorithm depends on the question being asked. BFS answers minimum-edge-distance questions in unweighted graphs, DFS provides a depth-first exploration, connected-component analysis identifies undirected connectivity groups, and Dijkstra handles minimum accumulated costs under nonnegative weights.
