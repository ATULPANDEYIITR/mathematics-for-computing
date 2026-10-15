# Graph Connectivity: Algorithms, Network Analysis, and Failure Modeling

## Introduction

Graph connectivity describes whether vertices in a graph can reach one another through edges. It provides a mathematical foundation for evaluating communication networks, infrastructure dependencies, transportation systems, distributed services, and relationships between entities.

A graph is represented by \(G=(V,E)\), where \(V\) is the set of vertices and \(E\) is the set of edges. The interpretation of connectivity depends on whether edges are directed, whether the graph changes over time, and whether the objective is ordinary reachability or resilience to failures.

These implementations examine connectivity from complementary perspectives: traversal algorithms, incremental connectivity, network fault analysis, enterprise service availability, and relational data integrity.

## Core Concepts

### Reachability and connected components

A vertex \(v\) is reachable from vertex \(u\) when a path exists from \(u\) to \(v\). In an undirected graph, connected components are maximal groups of vertices in which every pair is connected by a path.

An isolated vertex forms a component of its own. A graph with several components is disconnected, even if every component contains many vertices. The examples treat an empty undirected graph as connected by convention, although applications can adopt a different convention.

Adjacency lists store each vertex's neighbors. For sparse graphs, they generally require \(O(V+E)\) space, compared with \(O(V^2)\) space for an adjacency matrix.

### Directed connectivity

Directed edges encode permitted movement or communication in one direction.

- **Weak connectivity** ignores edge directions when determining components.
- **Strong connectivity** requires every vertex to reach every other vertex by following directed edges.
- **Strongly connected components** partition a directed graph into maximal strongly connected groups.

A directed graph can be weakly connected but not strongly connected. A path from a control service to a sensor does not establish that the sensor can send information back to the control service.

### Connectivity and resilience

Connectivity describes whether a path exists under the current topology. Resilience examines whether that path survives changes or failures.

A **bridge** is an undirected edge whose removal increases the number of connected components. An **articulation point** is a vertex whose removal increases the number of components.

A connected graph need not be resilient. A chain is connected, but every edge is a bridge. A cycle of at least three vertices remains connected after any single edge removal.

Degree is a useful diagnostic, but it is not a substitute for bridge analysis. A vertex with several neighbors may still depend on a bridge elsewhere in the network.

## Algorithms and Complexity

| Algorithm | Purpose | Time complexity | Main limitation |
|---|---|---|---|
| Breadth-first search | Reachability and traversal | \(O(V+E)\) | Examines the reachable subgraph |
| Depth-first search | Traversal and structural analysis | \(O(V+E)\) | Recursive implementations may exhaust the call stack |
| Connected components | Partition an undirected graph | \(O(V+E)\) | Requires traversal of the graph |
| Disjoint Set Union | Maintain connectivity during insertions | Amortized \(O(\alpha(V))\) per operation | Does not directly handle arbitrary edge deletions |
| Kosaraju's algorithm | Strongly connected components | \(O(V+E)\) | Requires graph reversal and two traversal passes |
| Low-link DFS | Bridges and articulation points | \(O(V+E)\) | Standard formulation applies to undirected graphs |

Here, \(\alpha(V)\) is the inverse Ackermann function, which grows so slowly that it is effectively constant for practical input sizes.

Breadth-first search discovers vertices in increasing order of distance from the starting vertex in an unweighted graph. Depth-first search explores one path before backtracking. Both are suitable for ordinary reachability, but their traversal orders differ.

Disjoint Set Union, also called Union-Find, answers a different question efficiently: whether two vertices belong to the same component after a sequence of edge insertions. Path compression shortens parent chains, while union by size attaches smaller trees beneath larger trees.

## Python Implementation

The Python program uses an adjacency-list `Graph` class that supports directed and undirected topologies. It validates vertex references, rejects invalid graph operations, provides copying for isolated failure simulations, and offers deterministic traversal output where practical.

`connected_components()` partitions an undirected graph. `weak_components()` converts directed edges into undirected relationships before computing components. `strongly_connected_components()` implements Kosaraju's algorithm by recording DFS finishing order, reversing all directed edges, and traversing the reversed graph in the appropriate order.

`bridges_and_articulation_points()` implements low-link analysis. Discovery times record when vertices enter DFS. Low-link values record the earliest discovery time reachable from a vertex's DFS subtree through tree edges and back edges. For a DFS tree edge from \(u\) to \(v\), the condition

\[
low[v] > discovery[u]
\]

identifies a bridge. For a non-root vertex \(u\), the condition

\[
low[v] \ge discovery[u]
\]

identifies an articulation point when it holds for a child subtree. A DFS root is an articulation point only when it has more than one DFS-tree child.

`DisjointSetUnion` handles insertion-oriented connectivity queries. `connectivity_after_edge_failures()` copies the graph before removing links, so the original topology remains unchanged.

The executable demonstration includes a network with an isolated backup site, a failure simulation, directed strong-component analysis, and a seeded random graph. The `unittest` cases exercise isolated vertices, bridges, cycles, duplicate union operations, directed components, invalid probability values, and preservation of the original graph during failure analysis.

The recursive low-link and directed cycle routines are clear algorithmic implementations, but extremely deep graphs may exceed Python's recursion limit. Large-scale production systems should use iterative DFS or a tested graph-processing library when such input sizes are expected.

## JavaScript Implementation

The JavaScript implementation focuses on event-driven network monitoring rather than reproducing every algorithm in the Python module.

`UndirectedGraph` stores neighbors in `Map` and `Set` structures. These collections prevent duplicate adjacency entries and support efficient membership checks. Its breadth-first search uses an array with a moving head index rather than repeatedly calling `shift()`, avoiding the repeated array movement associated with queue removal from the front.

`UnionFind` provides a separate incremental connectivity index with path compression and union by size. The index is useful while links are being inserted. If links are removed, the existing Union-Find structure cannot determine the resulting components by itself; it must be rebuilt or replaced with a deletion-capable approach.

`NetworkMonitor` demonstrates an event-driven design. Subscribers register listeners for link changes, and the registration method returns an unsubscribe function. The monitor records successful link insertions and provides snapshots for operational reporting.

`processEvents()` processes a sequence of link additions and removals asynchronously. Its `setImmediate()` yield allows other event-loop work to run between events. It does not make graph mutation thread-safe or guarantee atomic processing of the entire event sequence.

Failure simulation operates on a graph copy. Invalid endpoints are rejected instead of being implicitly registered, which prevents malformed events from silently changing network inventory.

The event log in this example is an in-memory demonstration rather than a durable audit system. A production monitor would need persistent event storage, ordering guarantees, concurrency controls, and recovery behavior for partially processed event batches.

## C++ Case Study: Regional Utility Network

The C++ program models a regional utility network containing control facilities, substations, relay hubs, and a water-treatment monitoring site. Each site is a vertex, and each communication link is an undirected edge.

The `Network` class uses `std::map` for site adjacency and `std::set` for neighboring vertices. This representation gives deterministic output and prevents duplicate neighbors. Its `connectedComponents()` method uses an explicit stack, avoiding recursion for ordinary reachability analysis.

The case study calculates component counts, identifies bridges and articulation points, simulates a failed communication link, and evaluates incremental connectivity with `DisjointSetUnion`.

The bridge algorithm uses low-link values to identify links without an alternate route around the DFS subtree they connect. The articulation-point calculation distinguishes DFS roots from other vertices because a root's removal behavior depends on the number of DFS-tree children.

The failure simulation creates a copy of the network and removes the specified link. This separation avoids accidentally modifying the live topology while investigating a hypothetical outage.

`DisjointSetUnion` uses path compression and union by size. The program inserts each undirected link once into the connectivity index by considering only one canonical endpoint ordering.

Input validation rejects unregistered sites, and duplicate link insertion is idempotent because adjacency uses sets. The model uses an empty string to represent the absence of a DFS parent, so an actual site with an empty identifier is prohibited.

The complexity of component discovery and low-link analysis is \(O(V+E)\) with conventional adjacency-list traversal. The use of ordered maps and sets adds logarithmic lookup and insertion overhead compared with hash-based adjacency structures, trading some performance for deterministic behavior.

## Java Implementation: Enterprise Availability Modeling

The Java program separates the network inventory from connectivity analysis and business-level availability evaluation.

The `Site` record represents a registered facility with a validated identifier, type, and region. The `Link` record canonicalizes endpoint order, ensuring that an undirected link has one representation. `NetworkInventory` owns the site registry, adjacency map, and set of established links.

`ConnectivityAnalyzer` provides component discovery and reachability from a specified site. Its BFS implementation uses `ArrayDeque`, which is appropriate for queue operations. Snapshot methods expose unmodifiable maps and sets so consumers cannot directly modify the inventory's internal collections through returned references.

`AvailabilityService` applies a domain policy to the connectivity results. It receives a service name, a set of required sites, and the primary control site. The service is:

- `AVAILABLE` when every required site is reachable from primary control.
- `DEGRADED` when some, but not all, required sites are reachable.
- `ISOLATED` when no required site is reachable.

These statuses are application-level interpretations of reachability. They are not graph-theoretic definitions, and a real availability policy may also require latency, redundancy, health checks, or minimum bandwidth.

The failure scenario uses `NetworkInventory.copy()` to test an outage without mutating the baseline inventory. Explicit exceptions reject unknown sites, duplicate links, invalid service requirements, and invalid control-site references.

The model is single-threaded and in-memory. Unmodifiable snapshots protect against direct external mutation but do not provide transaction isolation or concurrency safety. A production service would need coordinated updates and consistent snapshots when topology changes occur concurrently.

## SQL Implementation: Relational Connectivity Analysis

The PostgreSQL script represents graph connectivity through relational tables rather than storing the entire graph in a single serialized field.

### Relational schema

| Relation | Purpose |
|---|---|
| `site` | Stores registered infrastructure vertices and their attributes |
| `network_link` | Stores canonical undirected edges, bandwidth, and operational state |
| `directed_route` | Stores directional control, telemetry, and backup relationships |
| `service_requirement` | Defines the sites required by each operational service |
| `link_failure` | Records outage intervals without deleting the underlying link |

Primary keys provide stable identifiers. Foreign keys prevent links, routes, failures, or requirements from referring to nonexistent entities. Check constraints validate endpoint ordering, positive bandwidth, supported site types, and failure timestamps.

The unique constraint on `(endpoint_a, endpoint_b)` prevents duplicate links, while `CHECK (endpoint_a < endpoint_b)` establishes a canonical representation for undirected edges. The application must sort endpoint identifiers before insertion.

The indexes support endpoint lookups, active-link filtering, directed-route traversal, and active-failure queries. The partial indexes contain only rows relevant to operational queries, reducing index size when inactive records are common.

### Recursive reachability

`reachable_sites(start_site)` uses a recursive common table expression. The anchor query selects the starting site. The recursive term follows an operational edge from every already-reached site to its opposite endpoint.

The recursive query uses `UNION`, which deduplicates reached sites. This is important for cyclic graphs: a traversal must not repeatedly revisit the same vertices. The operational-link view excludes administratively disabled links and links with active failure records.

`service_reachability` joins service requirements with the current reachable-site set. Aggregation then calculates the number of required sites that remain reachable and whether all requirements are satisfied.

The script records a simulated link failure, queries the degraded topology, marks the failure as recovered, and checks the restored operational link. Historical failure records remain available for audit purposes.

### Database integrity and limitations

The final integrity checks deliberately attempt invalid inserts inside exception-handling blocks. Each invalid statement runs within an inner PL/pgSQL block, allowing the demonstration to continue after the expected constraint violation.

The recursive query evaluates connectivity from a chosen start vertex against the current database state. It is not a materialized connected-component index. Repeated queries on a large, frequently changing graph can be expensive, especially when the recursive join repeatedly searches the edge relation.

The script uses PostgreSQL-specific features, including identity columns, partial indexes, filtered aggregates, recursive CTEs, and PL/pgSQL exception handling. It is not directly portable to every SQL database.

## Distinguishing the Implementation Strategies

The implementations address different operational needs rather than treating all connectivity questions as equivalent.

| Requirement | Suitable mechanism | Reason |
|---|---|---|
| Determine whether a site can reach a control center | BFS or DFS | Computes reachability in the current topology |
| Identify every isolated group | Connected-component traversal | Produces a complete partition of vertices |
| Track repeated edge insertions | Disjoint Set Union | Avoids recomputing all components after each insertion |
| Find single-link failure risks | Bridge analysis | Detects edges whose removal increases component count |
| Find critical relay sites | Articulation-point analysis | Detects vertices whose removal disconnects a graph |
| Analyze one-way communication relationships | Directed reachability or SCC analysis | Preserves edge direction |
| Evaluate service-specific required-site reachability | Domain policy over graph results | Converts topology into operational status |
| Query stored topology and outage history | Relational queries and recursive CTEs | Integrates graph analysis with persistent business data |

A Union-Find structure is not a replacement for BFS in every situation. It answers connectivity-equivalence queries efficiently for an incrementally constructed undirected graph, but it does not return paths, distances, or bridge information. It also cannot directly handle arbitrary edge deletion because deleting one edge may split a component in ways not represented by the existing parent forest.

Similarly, a connected-component count does not reveal which link is responsible for a disconnection. Bridge analysis identifies that structural dependency, while articulation-point analysis identifies vulnerable vertices.

## Edge Cases and Common Failure Modes

- **Isolated vertices:** They must be included in the graph representation even when they have no edges. Otherwise, component counts will be understated.
- **Duplicate edges:** Set-based adjacency and canonical relational endpoint ordering prevent duplicate undirected links from inflating edge counts.
- **Unknown endpoints:** Graph operations should reject references to vertices absent from the registry rather than silently creating unintended infrastructure.
- **Self-loops:** Self-loops require explicit handling. The SQL and Java models reject them, while the Python model permits them and detects them as cycles.
- **Disconnected input:** Traversal from one vertex explores only its reachable component. Complete component analysis must start new traversals for all unvisited vertices.
- **Directed edges:** Treating directed edges as undirected can establish weak connectivity, but it cannot establish strong connectivity.
- **Cycles:** Traversal algorithms must track visited vertices. Without deduplication, cyclic graphs can produce repeated work or nonterminating recursion.
- **Edge removal:** Ordinary Union-Find does not support arbitrary deletions. Recompute components or use a dynamic-connectivity algorithm when the workload requires frequent removals.
- **Concurrent changes:** A traversal over a topology that changes during analysis may combine inconsistent states. Operational systems should use snapshots, locks, or transactional isolation.
- **Fault tolerance:** A connected topology can still contain bridges. Connectivity alone does not establish redundancy, service quality, or acceptable failure risk.

## Performance and Production Considerations

For a static sparse graph, adjacency lists and linear-time traversal algorithms are effective general-purpose choices. Disjoint Set Union is especially effective when the workload is dominated by edge insertions and connectivity queries. Bridge and articulation-point analysis should be used when the operational question concerns resilience rather than simple reachability.

For large production graphs, memory usage, graph mutation frequency, snapshot consistency, and failure-event volume often matter as much as asymptotic time complexity. Recursive implementations can also impose stack-depth limits even when their theoretical running time is linear.

A practical monitoring system should distinguish topology inventory from observed link health. A configured link may exist but be unavailable because of a physical failure, maintenance window, or policy restriction. Modeling these states separately allows historical failure records to remain intact while operational queries use only currently available edges.

Database-backed systems must also account for transaction boundaries. A query may be correct for one consistent snapshot while becoming stale immediately after a concurrent outage. Connectivity results used for critical operational decisions should carry timestamps or version identifiers, and updates to link state should be recorded consistently with the events that caused them.
