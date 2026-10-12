# Graph Properties: Degree, Walks, Paths, Cycles, and Connectedness

## Scope

Graph theory represents relationships using vertices and edges. It provides a mathematical framework for studying transportation networks, service dependencies, communication systems, social networks, and infrastructure connectivity.

This project examines five related but distinct properties:

- **Degree** measures the number of edge incidences associated with a vertex.
- **Walks and paths** describe sequences of vertices connected by edges, with different rules about repetition.
- **Cycles** identify closed routes and circular dependencies.
- **Connectedness** determines whether vertices can reach one another under a specified interpretation of connectivity.
- **Connected components** partition a graph into maximal connected groups.

The implementations use both undirected and directed graphs. An undirected edge represents a symmetric relationship. A directed edge represents a one-way relationship, such as a service depending on another service or a deployment stage depending on a preceding stage.

## Mathematical model

A graph is represented as \(G=(V,E)\), where \(V\) is the vertex set and \(E\) is the edge set.

For an undirected graph, an edge joins two vertices without assigning a direction. For a directed graph, an edge is an ordered pair \((u,v)\), indicating a relationship from \(u\) to \(v\).

The programs use simple graphs by default. A simple graph does not contain parallel edges between the same pair of vertices. The Python, JavaScript, C++, and Java implementations store adjacency relationships in sets, which naturally prevent duplicate neighbors. The SQL implementation uses a unique index to prevent duplicate ordered endpoint pairs.

The SQL schema prohibits self-loops, while the in-memory implementations can represent them. This distinction is deliberate: it demonstrates how a data model's integrity constraints can impose narrower rules than a general graph abstraction.

## Degree and local structure

For an undirected vertex \(v\), the degree \(\deg(v)\) is the number of incident edges. An isolated vertex has degree zero. A vertex connected to five distinct neighbors has degree five.

For a directed graph, two measurements are necessary:

- **In-degree** counts incoming edges.
- **Out-degree** counts outgoing edges.

A directed vertex can have a high in-degree and a low out-degree, or the reverse. For example, many application services might call one identity service, giving that service a high in-degree in a dependency graph.

For an undirected graph without self-loops, the handshaking lemma states:

\[
\sum_{v\in V}\deg(v)=2|E|
\]

Each edge contributes one degree to each endpoint, so the total degree is twice the number of edges. A self-loop contributes two incidences at its single endpoint.

The implementations distinguish the number of neighbors from the mathematical degree of a self-looped vertex. This matters because an adjacency set stores a self-neighbor only once.

### Degree implementation choices

Python uses an adjacency dictionary whose values are sets. It calculates degrees on demand and generates a degree sequence sorted by decreasing degree.

JavaScript uses a private `Map` of adjacency sets. Its degree distribution groups vertices by degree, making it possible to inspect how concentrated connectivity is across a network.

C++ uses ordered maps and sets to produce reproducible output. Its degree methods reject the use of undirected degree semantics on directed graphs.

Java uses explicit connectivity modes and separate in-degree and out-degree methods. Its report captures per-vertex degree measurements in an immutable result structure.

The SQL view `graph_degree_report` includes isolated vertices by starting from the vertex table rather than from the edge table. An edge-only query would omit vertices with no incident edges, producing incomplete degree reports.

## Walks, trails, and simple paths

A walk is a sequence of vertices in which each consecutive pair is connected by an edge. A walk can repeat vertices and edges.

A trail is a walk that does not repeat an edge. A vertex can still appear more than once in a trail.

A simple path does not repeat vertices. Under this project's convention, a path of length zero consists of one vertex and is valid. The length of a path is its number of edges, not its number of vertices.

For example, the sequence `A → B → A` is a walk when the edge between A and B exists. It is not a simple path because A is repeated.

### Shortest paths

Breadth-first search (BFS) finds a minimum-edge path in an unweighted graph. It explores all vertices at distance \(d\) before exploring vertices at distance \(d+1\).

The implementations store predecessor information when a vertex is first discovered. Once the target is found, the path is reconstructed by following predecessor links backward.

For a graph represented with adjacency lists, BFS runs in \(O(|V|+|E|)\) time. Its traversal state requires \(O(|V|)\) auxiliary space, excluding graph storage and the returned path.

A missing route is represented by `None` in Python, `null` in JavaScript, an empty vector in C++, an empty list in Java, or the absence of a matching reachable pair in a SQL reachability query. These representations distinguish an unreachable target from a valid route.

### Enumerating simple paths

Python includes a generator that enumerates simple paths between two vertices. The generator tracks the current path and a set of vertices already on that path. A vertex is removed from the set during backtracking, allowing it to appear in a different candidate path.

Simple-path enumeration can take exponential time because a graph can contain exponentially many simple paths. A generator reduces the need to retain all results in memory, but it does not eliminate the combinatorial cost. The optional maximum depth limits the number of vertices in each candidate path.

## Cycles

A cycle is a closed route that returns to its starting vertex. In a simple undirected graph, a cycle normally contains at least three distinct vertices. A directed cycle follows edge directions and returns to its starting vertex.

A cycle in a road network can indicate an alternative route. A cycle in a dependency graph can indicate a configuration that prevents a strict topological ordering.

### Undirected cycle detection

The Python, C++, and Java implementations use depth-first traversal with parent tracking. When traversal reaches an already visited neighbor that is not the current vertex's parent, a cycle has been detected.

Self-loops require explicit treatment in implementations that permit them. A self-loop is a cycle under the program's general graph convention.

### Directed cycle detection

Directed cycle detection requires different logic. A visited vertex alone does not prove a cycle, because an edge can point to a vertex that has already been completely processed.

The Python, JavaScript, C++, and Java implementations use three logical states:

- Unvisited vertices have not entered DFS.
- Active vertices are on the current DFS path.
- Completed vertices have had their outgoing edges fully examined.

An edge to an active vertex establishes a directed cycle. An edge to a completed vertex does not by itself establish one.

The recursive DFS implementation takes \(O(|V|+|E|)\) time. For extremely deep graphs, recursive implementations may encounter call-stack limits; an iterative DFS or a strongly connected component algorithm is more appropriate for such environments.

## Connectedness and connected components

An undirected graph is connected if every pair of vertices has a path between them. An isolated vertex is a component by itself.

A connected component is a maximal set of vertices in which every pair is mutually reachable through undirected paths. Components are disjoint and collectively cover all vertices.

The implementations use BFS to discover components. Each traversal starts at an undiscovered vertex, marks every reachable vertex, and records that group as one component. Once all vertices have been visited, the component list is complete.

The programs adopt a consistent convention that an empty graph is not connected. In mathematical literature, conventions about the empty graph can differ, so applications should state their chosen definition.

### Directed connectivity

Directed graphs require more precise terminology.

**Weak connectivity** ignores edge direction when determining whether vertices belong to the same component. **Strong connectivity** requires every vertex in a group to reach every other vertex by following edge directions.

The current component methods deliberately calculate weak components for directed graphs. They construct an undirected view of the edge relationships before traversal. Their results must not be interpreted as strongly connected components.

Strongly connected components require an algorithm such as Tarjan's or Kosaraju's algorithm. The directed cycle detectors answer a different question: whether at least one directed cycle exists.

## Python implementation

The Python program uses the standard library and is executable without external packages.

Its `Graph` class supports vertex and edge insertion, edge removal, neighbor inspection, degree measurements, BFS, DFS, shortest paths, connected components, and cycle detection.

The campus network provides a practical undirected example. Buildings are vertices and walkable connections are edges. The isolated museum or annex illustrates how a graph can contain several components even when one part of the network is internally connected.

The deployment example uses a directed graph to model stage dependencies. Introducing a reverse dependency demonstrates how an otherwise acyclic workflow can become cyclic.

The `GraphStatistics` dataclass groups graph-level measurements. Assertions verify key invariants, including the handshaking lemma, triangle cycle detection, directed in-degree and out-degree, and shortest-path reconstruction.

The script also demonstrates validation failures. Unknown vertices, invalid names, and operations that are inappropriate for the selected graph type are rejected explicitly rather than producing misleading results.

## JavaScript implementation

The JavaScript program emphasizes event-driven graph changes and controlled access to internal state.

The adjacency map is private. Consumers cannot directly mutate the internal neighbor sets, which reduces the risk of bypassing validation or leaving graph state inconsistent.

Graph mutations emit immutable events with revision numbers. Subscribers can observe additions to the graph, making the design suitable for network monitoring or a live visualization layer. Observer exceptions are caught so that one faulty listener does not prevent other listeners from receiving a mutation event that has already occurred.

The `unsubscribe` function removes a listener when it is no longer needed. This helps avoid retaining obsolete callbacks in long-running applications.

The BFS implementation uses an array with a moving head index rather than repeatedly calling `shift()`. This avoids repeated element movement that can make queue processing unnecessarily expensive.

The graph supports directed degree measurements, weak components, shortest paths, walk validation, simple-path validation, and cycle detection. The test section verifies the distinctions between walks and simple paths and checks that a reverse directed edge creates a cycle.

## C++ case study: campus connectivity and service dependencies

The C++ program uses a coherent infrastructure scenario with two graph interpretations.

The campus model represents buildings and roads. It reports degrees, connected components, and shortest routes. The remote annex demonstrates that a valid vertex may still be unreachable from the main network. Adding a perimeter road introduces an alternative route and creates a cycle.

The service model represents directional dependencies among infrastructure services. Its adjacency map records outgoing dependencies. In-degree and out-degree are calculated separately because the direction of a service relationship affects reachability.

The implementation uses ordered maps and sets to produce deterministic reports. BFS maintains a queue and predecessor map. Component detection builds a symmetric view of the adjacency relationships so that weak connectivity is calculated correctly even when the original graph is directed.

The implementation rejects unknown vertices and inappropriate degree or cycle operations through exceptions. Its main function catches failures and reports an error rather than silently continuing with an invalid analysis.

For a graph with \(V\) vertices and \(E\) edges, BFS has \(O(V+E)\) time complexity. Ordered-map and ordered-set operations add logarithmic factors to some graph construction and lookup operations compared with hash-based structures. That trade-off provides predictable ordering in diagnostic output.

## Java implementation: typed graph policies

The Java program models graph behavior through explicit domain types.

`ConnectivityMode` prevents callers from confusing directed and undirected operations. The `Edge` record validates its endpoints, while `GraphReport` groups the results of graph analysis.

The `Graph` class exposes unmodifiable vertex and neighbor collections. Callers can inspect graph state without obtaining a mutable reference that could bypass graph invariants.

`GraphPolicy` defines a policy interface. `RequireConnected` evaluates whether the network forms one nonempty connected component. `RequireAcyclic` evaluates whether a dependency graph has a cycle. These policies demonstrate how graph properties can become explicit application rules rather than merely printed statistics.

The enterprise scenario includes an isolated disaster-recovery site. The connectedness policy correctly fails because the site has no path to the primary infrastructure. Adding a redundant connection creates a cycle, which is useful for demonstrating the difference between redundancy and acyclicity: a cycle may be desirable in a physical network but unacceptable in a dependency workflow.

The Java implementation uses `ArrayDeque` for BFS, maps for predecessor and color state, and immutable collections for results. Validation errors and invalid graph operations use distinct exception types to make incorrect API use easier to diagnose.

## SQL implementation: relational graph analysis

The PostgreSQL schema represents graph data through normalized relational tables.

| Table | Purpose |
|---|---|
| `graph_definitions` | Identifies each graph and its directed or undirected interpretation. |
| `graph_vertices` | Stores vertices, including isolated vertices. |
| `graph_edges` | Stores weighted edges and enforces endpoint integrity. |
| `graph_walk_steps` | Records an ordered sequence of vertices for a candidate walk. |
| `graph_component_members` | Provides a place to persist derived component membership. |

Composite foreign keys ensure that both endpoints of every edge belong to the same graph. The unique edge index prevents duplicate directed endpoint pairs. The schema prohibits self-loops and negative weights, making these constraints explicit at the database layer.

The `graph_degree_report` view calculates degree information for every vertex. For undirected graphs, each edge contributes to the degree of both endpoints. For directed graphs, the view reports outgoing and incoming degrees separately.

### Recursive reachability

Recursive common table expressions calculate reachability. The recursive relation starts with known vertex pairs and repeatedly extends routes through adjacent edges.

Using `UNION` rather than `UNION ALL` eliminates duplicate source-destination pairs. This is important when cycles exist, because unrestricted recursive expansion can repeatedly revisit the same vertices.

For component analysis, the SQL implementation constructs a weakly connected interpretation by treating each edge as traversable in both directions. The minimum reachable vertex identifier is used as a deterministic component label. This approach is suitable for the supplied examples, although more specialized algorithms are preferable for large graphs.

### Walk validation

The `graph_walk_steps` table stores each vertex in a walk with a step number. A window function obtains the next vertex with `lead()`. The validation query then checks whether every consecutive pair is represented by a valid edge under the graph's direction rules.

The table's unique constraint prevents duplicate step numbers within a named walk. Foreign keys ensure that every recorded vertex exists in its graph. Edge existence remains a separate semantic validation because a foreign key on vertices alone cannot prove that two consecutive vertices are adjacent.

### Transactions and integrity

The SQL script uses a transaction to keep its schema and demonstration data together. Foreign keys, checks, and unique indexes enforce structural rules that should not depend solely on application code.

The recursive queries demonstrate reachability and cycle detection, but the script is not a production-scale graph database. Recursive reachability can produce up to \(O(V^2)\) source-destination pairs, and materializing all such pairs can consume substantial memory and execution time. Larger graphs may require specialized graph-processing infrastructure or carefully indexed application-level traversal.

## Edge cases and interpretation

Several distinctions are essential when interpreting graph results.

- **An isolated vertex is not an invalid vertex.** It has degree zero and forms its own component.
- **A walk is not necessarily a path.** Walks can repeat vertices, whereas simple paths cannot.
- **A cycle is not equivalent to connectedness.** A connected tree has no cycle, while a graph containing a cycle can still have disconnected components.
- **Directed degree is directional.** In-degree and out-degree measure different relationships.
- **Weak connectivity is not strong connectivity.** Ignoring direction can combine vertices that cannot reach one another through directed edges.
- **A missing path is not a malformed graph.** Both vertices can exist while no route connects them.
- **An empty graph needs an explicit convention.** These programs define it as disconnected.
- **Graph representation affects performance.** Adjacency lists are efficient for sparse graphs, while adjacency matrices can be useful when constant-time edge-existence checks are more important than storage efficiency.

## Practical interpretation

Degree measurements reveal local connectivity and potential concentration points. Shortest paths identify minimum-hop routes. Connected components expose isolated infrastructure or disconnected network regions. Cycle detection identifies circular relationships, which may be acceptable for transport networks but problematic for strict dependency workflows.

These properties are complementary. A useful graph analysis evaluates the structure relevant to the domain instead of interpreting one property in isolation. A network with cycles may offer redundancy, while a dependency graph with the same structural feature may violate an execution policy. The appropriate interpretation depends on whether edges represent physical connections, permissible movement, or directional prerequisites.
