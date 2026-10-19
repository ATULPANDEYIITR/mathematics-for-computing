# Graph Optimization

Graph optimization studies how a network can be represented mathematically and how different objectives can be optimized over that network. The same graph can support very different optimization problems: finding the cheapest route between two locations, connecting every location with minimum total infrastructure cost, or maximizing the amount of traffic that can pass through capacity-constrained links.

This project treats three related areas as distinct problems:

- **Shortest paths** optimize movement between specified vertices.
- **Minimum spanning trees** optimize total connectivity across an undirected network.
- **Network optimization** covers capacity-oriented decisions such as maximum flow, where the objective is aggregate throughput rather than route length.

The implementations use realistic transportation, infrastructure, logistics, and service-network scenarios so that the difference between the objectives is visible in executable behavior.

## Problem Model

A weighted graph contains vertices and edges. A vertex can represent a warehouse, router, data center, regional hub, service location, or other network endpoint. An edge represents a relationship between two vertices and carries a numerical quantity such as travel time, latency, construction cost, distance, or capacity.

A weighted directed graph distinguishes `A -> B` from `B -> A`. This is appropriate when a route has a directional constraint. An undirected graph treats the relationship as bidirectional and is appropriate for many physical infrastructure planning problems.

The weight must be interpreted according to the optimization objective. A lower weight may represent less travel time, lower construction cost, or lower latency. It is not automatically a measure of capacity.

The central design principle is therefore:

`graph structure + edge attributes + optimization objective = optimization problem`

Changing the objective without changing the graph can produce a completely different optimal solution.

## Shortest Paths

A shortest-path problem asks for the minimum accumulated cost between vertices. The Python, JavaScript, C++, and Java implementations use Dijkstra's algorithm for non-negative edge weights.

Dijkstra maintains a tentative distance for every reachable vertex. The source begins with distance zero. When a vertex with the smallest tentative distance is selected, each outgoing edge is examined. If reaching the neighbor through that vertex produces a lower cost, the neighbor's distance and predecessor are updated.

The predecessor structure is important because the numerical distance alone does not describe the actual route. The implementations therefore retain predecessor information and reconstruct the path after optimization.

The Python example models a warehouse-to-store logistics route. The JavaScript example uses a data-center routing scenario. The C++ case study uses regional logistics facilities. The Java program uses enterprise network sites.

Dijkstra is not valid for arbitrary weighted graphs containing negative edges. The Python implementation explicitly rejects negative weights in its main graph class. This is preferable to silently returning an invalid result.

With an adjacency-list representation and a binary heap, the typical complexity is `O((V + E) log V)`, where `V` is the number of vertices and `E` is the number of edges.

## Alternative Shortest-Path Models

The Python implementation also contains Bellman-Ford and Floyd-Warshall because their roles are materially different from Dijkstra.

Bellman-Ford repeatedly relaxes every edge and can handle negative edge weights. It can also detect a reachable negative-weight cycle. A negative cycle makes a conventional shortest-path answer undefined because the path cost can continue decreasing by traversing the cycle.

Floyd-Warshall solves all-pairs shortest paths. It maintains a distance matrix and considers each vertex as a possible intermediate point. Its `O(V^3)` running time makes it unsuitable for many large sparse graphs, but it is useful when a relatively small network requires shortest-path information for many source-target combinations.

These algorithms demonstrate an important optimization-engineering decision: the correct algorithm depends on graph properties and query requirements, not simply on which algorithm is easiest to implement.

## Minimum Spanning Trees

A minimum spanning tree solves a different problem from shortest paths.

Given a connected, undirected, weighted graph, an MST connects every vertex while minimizing the sum of selected edge weights. It contains exactly `V - 1` edges and contains no cycle.

An MST does not attempt to minimize the route from one particular source to one particular destination. A locally longer route can be part of the globally cheapest infrastructure because the same edge may connect an important group of sites.

The Python implementation provides both Kruskal's and Prim's algorithms.

Kruskal sorts candidate edges by weight and accepts an edge when it connects two previously separate components. The implementation uses a disjoint-set union structure with path compression and union by rank. These operations make component membership efficient.

Prim starts with one vertex and repeatedly chooses the cheapest edge crossing from the already-connected region to an unconnected vertex. Its priority queue represents the frontier of the growing tree.

The C++ case study models physical infrastructure deployment. The edge weight represents deployment cost rather than travel latency. This distinction is essential: a network that is cheap to build is not necessarily a network that provides the shortest route for every user.

## Network Capacity Optimization

Shortest paths and MSTs do not fully describe capacity-constrained networks.

Suppose a service provider has links with fixed capacities. Sending more traffic through one link than that link can carry is infeasible, regardless of how short the route is.

The Python and C++ implementations therefore include maximum-flow models. The source represents an origin of traffic and the sink represents the destination. Each directed capacity edge specifies the maximum flow that can cross it.

The Edmonds-Karp implementation uses breadth-first search to find augmenting paths in the residual network. Residual edges allow previously allocated flow to be reduced and rerouted when a later augmenting path makes that necessary.

This is fundamentally different from shortest-path optimization:

| Problem | Objective | Typical constraint |
|---|---|---|
| Shortest path | Minimize cost between selected vertices | Edge weights |
| Minimum spanning tree | Minimize total cost of network connectivity | Connectivity |
| Maximum flow | Maximize transferable quantity | Edge capacities |

A real network-planning system may need all three analyses at different stages.

## Python Implementation

The Python program provides the broadest algorithmic laboratory.

`WeightedGraph` uses an adjacency-list representation and stores explicit edge records. The representation is efficient for sparse networks and allows the same graph abstraction to support multiple algorithms.

The Dijkstra implementation uses `heapq` as its priority queue. Because Python's heap does not provide a decrease-key operation, a new candidate is inserted whenever a distance improves. Older entries remain in the heap and are ignored when their distance no longer equals the authoritative distance table.

`reconstruct_path` separates optimization from presentation. The shortest-path algorithm calculates distances and predecessors, while the reconstruction function turns those predecessors into an ordered route.

The MST implementation uses `DisjointSetUnion` for Kruskal's algorithm and a heap-based frontier for Prim's algorithm. Both reject disconnected graphs because a spanning tree cannot contain every vertex unless the graph is connected.

The maximum-flow implementation explicitly maintains residual capacities. This exposes a mechanism that does not appear in ordinary shortest-path algorithms: flow can be reversed on residual edges when rerouting is necessary.

The Python program also contains validation for unknown vertices, negative weights, disconnected MST inputs, and other invalid states.

## JavaScript Implementation

The JavaScript program emphasizes event-driven graph optimization rather than translating the Python structure.

Graph adjacency is represented with `Map`, which is useful when vertex identifiers are meaningful strings rather than dense integer indexes. The custom `MinPriorityQueue` demonstrates how a priority queue can be implemented without requiring an npm dependency.

The JavaScript Dijkstra implementation uses a `Map` for distances and predecessors. The algorithm keeps stale priority-queue entries and discards them when they no longer match the current best distance.

A separate asynchronous generator, `shortestPathEvents`, exposes optimization progress as events. It yields vertex-settlement and distance-relaxation events instead of forcing the algorithm to print directly. `OptimizationMonitor` converts those events into an event-driven interface.

This separation is useful for applications where graph optimization feeds a dashboard, browser visualization, monitoring system, or interactive network planner. The optimization engine can produce structured events while another component decides whether to display, record, or aggregate them.

The file remains executable under Node.js and does not require an external package.

## C++ Case Study

The C++ program models a network service provider with three distinct operational concerns.

The logistics topology uses Dijkstra to determine a low-cost route through regional facilities. Edge weights represent travel time. The route reconstruction logic walks backward through the predecessor array and reverses the resulting sequence.

The infrastructure topology uses Kruskal's algorithm. `UnionFind` maintains connected components and prevents the selected infrastructure links from creating cycles. This models the practical decision of selecting a set of physical links that connects every site at minimum deployment cost.

The capacity topology uses an explicit residual network. Each residual edge stores a reverse-edge index, allowing an augmenting path to update both forward and reverse residual capacities efficiently.

The C++ implementation therefore demonstrates three different data-structure requirements:

- Dijkstra needs a priority queue and predecessor information.
- Kruskal needs sorted edges and disjoint-set components.
- Maximum flow needs residual adjacency and breadth-first search.

The program also uses exceptions for invalid graph definitions and impossible spanning-tree requests. It targets C++17 and uses only the standard library.

## Java Enterprise Model

The Java implementation models a more strongly typed enterprise network.

`Site` represents a registered network location and associates it with a `NodeRole`. The role distinguishes data centers, regional hubs, service sites, and backup sites.

`Link` is a Java record containing immutable link attributes: source, destination, cost, and capacity. Constructor validation prevents invalid negative costs or capacities from entering the domain model.

`NetworkTopology` acts as the domain repository for sites and links. It validates that both endpoints exist before accepting a connection. This prevents an invalid topology from being created through an accidental reference to a nonexistent site.

`RouteService` owns shortest-path behavior. Its result contains both the calculated distance and the reconstructed immutable path.

`ConnectivityPolicy` represents a domain rule separately from the routing algorithm. Critical site roles can require redundancy, while route validity remains a separate concern. This separation prevents business policy from becoming hidden inside the graph algorithm.

The MST planner uses a component structure based on maps rather than relying on integer node indexes. This matches the enterprise domain model where site identifiers are meaningful values such as `DC-DEL` and `HUB-LKO`.

## PostgreSQL Data Model

The SQL implementation represents graph optimization as persistent relational data.

`network_node` stores graph vertices and their operational roles. A unique node code provides a stable domain identifier while the numeric primary key provides a compact relational reference.

`network_edge` stores source and target nodes, optimization cost, capacity, direction, and active status. Foreign keys ensure that an edge cannot reference a nonexistent node. Check constraints reject negative costs and capacities.

The partial indexes on active source and target edges support operational queries without indexing inactive links in the same way.

`routing_demand` represents actual optimization requests. A demand has source and destination nodes, a requested quantity, priority, and lifecycle status.

`optimization_run` provides an audit record for optimization activity. It distinguishes shortest-path, MST, and maximum-flow objectives instead of treating every graph calculation as the same kind of operation.

`optimization_path`, `mst_selection`, and `flow_allocation` persist the outputs appropriate to their respective optimization problems.

## Recursive Route Evaluation in SQL

The PostgreSQL recursive CTE enumerates simple routes for the small demonstration topology.

The recursive state contains the current vertex, the complete path array, and accumulated cost. The expression `NOT edge.target_node_id = ANY(route.path)` prevents a recursive branch from revisiting a vertex already present in that route.

The query then applies `ROW_NUMBER()` within each source-target pair to select the cheapest enumerated route.

This is intentionally different from implementing Dijkstra inside SQL. Recursive path enumeration is appropriate only for relatively small demonstration networks because the number of possible paths can grow rapidly. For large production graphs, a dedicated graph algorithm or specialized graph-processing architecture is normally preferable.

## Transactional Result Recording

The SQL script records a shortest-path optimization inside a transaction.

The optimization run and its selected path are persistent records that should represent one coherent result. A transaction prevents a partially recorded optimization result from being committed if a later statement fails.

This illustrates the relationship between graph algorithms and database integrity. The database does not need to perform every graph optimization itself to play an important role. It can persist topology, demands, optimization runs, selected paths, capacity allocations, and audit information while enforcing structural invariants.

## Constraints and Invalid States

The relational schema prevents several classes of invalid data:

- A network edge cannot reference a nonexistent node because both endpoints use foreign keys.
- Negative route costs are rejected by a check constraint.
- Negative capacity is rejected independently of route cost.
- Demand quantities must be positive.
- Optimization objectives are restricted to known values.
- Optimization status values are constrained to the supported lifecycle.
- A completed optimization cannot have a completion timestamp earlier than its start.
- An MST selection cannot contain the same edge twice for the same run because of its composite primary key.

These rules belong at the database layer because they protect data regardless of which application writes it.

## Choosing the Right Optimization

The most important distinction is the question being optimized.

A shortest-path calculation asks, in effect, "What is the cheapest route from this source to this destination?" It can ignore much of the rest of the graph when solving a single-source problem.

An MST asks, "What is the cheapest set of links that connects all required vertices?" It is concerned with total infrastructure cost and global connectivity.

A maximum-flow model asks, "What is the greatest quantity that can pass through this network under the link capacities?" The shortest route may carry less total traffic than several longer routes used together.

These objectives can conflict. A network can have a very cheap MST while containing a poor route between two important locations. A shortest route can use a high-capacity bottleneck that becomes unsuitable when many demands compete for the same link. A high-throughput network can require more infrastructure than the minimum-cost spanning structure.

## Edge Cases and Failure Modes

Disconnected graphs require special handling for MST algorithms because no spanning tree can connect separate components.

Unreachable vertices require explicit handling in shortest-path results. The Python, C++, and Java implementations preserve an infinite or equivalent distance instead of fabricating a route.

Negative edge weights invalidate the assumptions of Dijkstra. The Python graph abstraction rejects them for its Dijkstra workflow rather than producing misleading results.

Zero-capacity links may exist in operational data, but they cannot carry flow. Capacity validation therefore treats zero as valid while rejecting negative capacity.

Duplicate or contradictory edge records can cause ambiguous optimization behavior. The SQL schema uses a source-target uniqueness rule for its demonstration topology, while a production system may need an explicit versioning or parallel-edge model if multiple physical links between the same endpoints are legitimate.

Cycles are valid graph structures but must be treated differently by different algorithms. Shortest-path traversal must avoid endlessly following cycles, MST selection must avoid adding cycle-forming edges, and maximum-flow residual graphs intentionally contain reverse relationships that represent the ability to reroute existing flow.

## Performance Considerations

Adjacency lists require `O(V + E)` storage and are generally appropriate for sparse networks.

Dijkstra with a binary heap typically requires `O((V + E) log V)` time. Its effectiveness depends on the non-negative-weight assumption.

Kruskal requires sorting the edges, giving a dominant `O(E log E)` component. Union-Find operations are effectively near-constant amortized time for practical purposes when path compression and union by rank are used.

Prim with a binary heap is commonly `O(E log V)` with an adjacency-list representation.

Floyd-Warshall requires `O(V^3)` time and `O(V^2)` memory, making it appropriate for smaller graphs where all-pairs answers justify the matrix.

Edmonds-Karp has a worst-case complexity of `O(VE^2)`. It is straightforward and useful for demonstration and moderate networks, but large production flow problems may require more specialized algorithms.

The SQL recursive route enumeration has a different scalability profile from Dijkstra. Enumerating many possible paths can become expensive very quickly, which is why the SQL demonstration is intentionally constrained to a small network.

## Security and Reliability

Graph optimization systems can make operational decisions, so input validation is important. Negative or malformed weights, invalid capacities, nonexistent endpoints, and disconnected infrastructure should not be silently accepted.

Database foreign keys and check constraints provide protection against structurally invalid graph data. Application-level validation provides earlier and more descriptive feedback, so both layers have a role.

Capacity data can affect resource allocation. A stale or manipulated capacity value can cause an optimization engine to recommend an infeasible plan. Production systems should therefore treat capacity as controlled operational data and preserve the provenance and timestamp of measurements where required.

Optimization results should also be auditable. The SQL model separates the current network topology from historical optimization runs so that a later topology change does not silently rewrite the meaning of an earlier decision.

## Practical Architecture

A production graph-optimization service can be viewed as several cooperating layers:

`network data -> validation -> graph construction -> optimization engine -> feasibility checks -> persisted result -> operational decision`

The graph layer should not be responsible for business policy that belongs elsewhere. Likewise, a database should not be forced to reproduce an algorithm whose computational characteristics are better handled by an application service.

The implementations deliberately preserve this separation. Graph algorithms calculate mathematical results, domain models represent operational meaning, and the relational schema enforces persistent data integrity.

This separation also makes it possible to compare algorithms against the same topology without confusing algorithmic behavior with presentation or storage concerns.

## Distinctions That Matter

A shortest path is not a minimum spanning tree.

An MST contains every required vertex and minimizes the sum of selected edge costs. A shortest path normally concerns one source and one destination and minimizes the cost accumulated along that route.

A shortest path is not maximum flow.

A shortest-path result identifies a preferred route according to a scalar cost. Maximum flow determines how much aggregate quantity can be transmitted when links have capacity constraints.

An MST is not a maximum-flow solution.

An MST intentionally minimizes total connectivity cost and contains exactly `V - 1` edges for a connected graph. Maximum-flow solutions can use multiple paths and are governed by source, sink, and capacity constraints.

Understanding these distinctions prevents a common design error: selecting an algorithm because the data happens to be a graph rather than because the optimization objective matches the algorithm.
