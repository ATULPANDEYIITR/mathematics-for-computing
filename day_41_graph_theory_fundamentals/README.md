# Graph Theory Fundamentals

## Scope

A graph is a mathematical model for relationships among entities. It consists of a vertex set \(V\) and an edge set \(E\). Vertices represent entities, while edges represent relationships, connections, dependencies, or permitted transitions.

A graph can represent a campus network, a software service dependency map, a transport network, or communication links between devices. The meaning of an edge depends on the domain model. A physical connection may be bidirectional, while a service dependency or data-flow relationship may have a specific direction.

This repository implements graph structures and operations in Python, JavaScript, C++, Java, and PostgreSQL. Each implementation emphasizes a different engineering perspective: reusable graph operations, event-driven updates, network analysis, enterprise service modeling, and relational graph storage.

## Vertices and edges

A **vertex**, also called a node, is an individual element of a graph. Examples include a router, a server, a service, or a laboratory.

An **edge** connects two vertices. In an unweighted graph, an edge records the existence of a relationship. In a weighted graph, it also stores a numerical value such as latency, distance, cost, or capacity.

A graph may contain isolated vertices that have no incident edges. These vertices must remain part of the graph because their existence is independent of their current connections.

Self-loops connect a vertex to itself. They can represent a recursive dependency or a local transition. Whether self-loops are meaningful depends on the application.

For a simple graph, duplicate edges between the same pair of vertices are not represented as separate relationships. The implementations update an existing edge when it is inserted again. Multigraphs, which permit multiple distinct edges between the same vertices, require a different data model.

## Directed and undirected graphs

### Undirected graphs

An undirected edge between \(u\) and \(v\) represents a symmetric relationship. The connection can be traversed in either direction.

The mathematical edge is written as \(\{u,v\}\). A campus network can use an undirected graph when physical links are treated as bidirectional.

The degree of a vertex is the number of incident edge endpoints. A self-loop contributes two to the degree of an undirected vertex. In a simple undirected graph without loops, the sum of all vertex degrees equals twice the number of edges:

\[
\sum_{v \in V} \deg(v) = 2|E|
\]

### Directed graphs

A directed edge is an ordered pair \((u,v)\). It represents a relationship from source \(u\) to target \(v\). The existence of this edge does not imply that an edge from \(v\) to \(u\) exists.

Directed graphs are appropriate for dependency relationships, data-flow systems, and one-way transitions.

The **out-degree** counts edges leaving a vertex. The **in-degree** counts edges entering it. For a directed graph, the total in-degree and total out-degree both equal the number of edges:

\[
\sum_{v \in V} \deg^{-}(v)
=
\sum_{v \in V} \deg^{+}(v)
=
|E|
\]

The direction of an edge must be preserved by every representation and traversal algorithm.

## Graph representations

The same graph can be represented in different ways. Choosing a representation affects memory use, edge lookup, neighbor enumeration, and implementation complexity.

### Adjacency list

An adjacency list associates each vertex with its neighbors. A weighted implementation associates each neighbor with an edge weight.

For a directed graph, only outgoing edges are stored. For an undirected graph, each non-loop edge is stored in both endpoint adjacency collections, although it remains one logical edge.

With a hash-based adjacency list, expected edge lookup is \(O(1)\). Traversing all vertices and edges takes \(O(V+E)\). The space requirement is \(O(V+E)\).

The Python and JavaScript implementations use dictionary- and map-based adjacency lists. The Java implementation uses insertion-ordered maps to make traversal output predictable. The C++ implementation uses ordered maps, trading some lookup speed for deterministic ordering.

Adjacency lists are effective for sparse graphs, where the number of edges is much smaller than \(V^2\).

### Adjacency matrix

An adjacency matrix is a two-dimensional structure in which cell \((i,j)\) represents the relationship from vertex \(i\) to vertex \(j\).

For an unweighted graph, cells can store Boolean values. For a weighted graph, cells can store weights. The matrix must distinguish a missing edge from a valid edge whose weight is zero.

The implementations use `None`, `null`, or a suitable infinity marker to represent absent edges.

An adjacency matrix uses \(O(V^2)\) space. Edge lookup is \(O(1)\) when vertex indices are already known. Enumerating the neighbors of a vertex requires scanning its row, which takes \(O(V)\) time.

For undirected graphs, the matrix is symmetric. Directed graphs do not generally have this property.

### Edge list

An edge list stores each logical edge as a source, target, and optional weight.

This representation is compact and convenient for importing datasets, exporting graph structures, or processing a sequence of relationships. Its space requirement is \(O(E)\), excluding the separate vertex registry.

Checking whether an arbitrary edge exists usually requires scanning the list unless an additional index is maintained.

The Python and Java implementations expose edge-list conversion methods. The SQL schema stores edges in a relational table with explicit endpoint references.

### Representation comparison

| Property | Adjacency list | Adjacency matrix | Edge list |
|---|---|---|---|
| Storage | \(O(V+E)\) | \(O(V^2)\) | \(O(E)\) |
| Edge lookup | Expected \(O(1)\) with hash maps | \(O(1)\) after indexing vertices | \(O(E)\) without an index |
| Neighbor enumeration | \(O(\deg(v))\) | \(O(V)\) | \(O(E)\) |
| Isolated vertices | Stored explicitly | Represented by an all-empty row and column | Require a separate vertex registry |
| Typical use | Sparse graph traversal | Dense graphs and frequent edge queries | Import, export, and edge-oriented processing |

## Python implementation

The Python program defines a reusable `Graph` class with explicit vertex and edge operations. Its adjacency dictionary maps each vertex to a dictionary of neighbors and weights.

The class distinguishes the logical edge count from the number of adjacency entries. An undirected edge normally produces two adjacency entries, so counting entries directly would incorrectly double the number of edges. Self-loops are stored once and counted once.

The implementation supports:

- Vertex creation, edge insertion, edge removal, and edge-existence checks.
- Directed in-degree and out-degree calculations.
- Undirected degree calculations with correct self-loop treatment.
- Conversion to an adjacency matrix and edge list.
- Breadth-first search, depth-first search, reachability, and minimum-hop paths.
- Connected components for undirected graphs and undirected cycle detection.
- Validation of unknown vertices and non-finite edge weights.

The `shortest_unweighted_path` method uses breadth-first search to find a path containing the minimum number of edges. It does not minimize the sum of weights. A weighted shortest-path problem requires an algorithm appropriate to the weight domain, such as Dijkstra's algorithm for nonnegative weights.

The cycle detector uses depth-first search with parent tracking. In an undirected graph, encountering an already visited neighbor other than the current vertex's parent indicates a cycle. A self-loop is detected immediately.

## JavaScript implementation

The JavaScript file uses `Map` objects for adjacency storage and `Set` objects for visited vertices. These structures preserve vertex identity and support values that are not limited to string keys.

Breadth-first search uses an array with a moving head index rather than repeatedly calling `shift()`. This avoids repeatedly moving the remaining queue elements during traversal.

The `GraphChangeEmitter` class separates graph mutation from event notification. Subscribers can react to edge additions, updates, and removals. Its subscription method returns an unsubscribe function, which allows callers to release listeners and avoid unnecessary retention.

The example models a physical network and a directed dependency graph. The physical topology supports weighted edges, while the dependency graph preserves direction. Both use the same underlying graph abstraction without conflating the meanings of their edges.

The matrix conversion uses `null` for absent edges. This is important because a zero-weight connection remains a valid edge. The tests also check disconnected paths, unknown vertices, directionality, and edge-count stability when an existing connection is updated.

## C++ network case study

The C++ program models two operational systems.

The campus network represents physical connectivity among an Internet gateway, a core switch, a library, a server room, and a research laboratory. It is modeled as an undirected weighted graph.

The service dependency model represents relationships among application services. It is a directed unweighted graph because a dependency from one service to another does not imply the reverse dependency.

The `Graph` class stores adjacency maps and maintains a separate logical edge count. Standard library containers provide deterministic iteration and straightforward validation. The program rejects empty vertex identifiers and non-finite edge weights.

Breadth-first search computes a traversal order. The shortest-path routine uses a parent map to reconstruct a minimum-hop path. The matrix exporter uses an infinity marker for absent edges, avoiding confusion between a missing connection and a valid edge weight.

The example also checks edge replacement, edge removal, self-loop degree, and unknown-vertex handling. Its main operational distinction is that weighted connections do not automatically make breadth-first search a weighted shortest-path algorithm.

The ordered maps make output stable and simplify debugging. Their logarithmic lookup costs differ from expected constant-time hash-table operations. For larger production graphs, the appropriate container should be selected based on graph density, identifier type, update patterns, and traversal workload.

## Java enterprise model

The Java implementation models service dependencies through a `ServiceRegistry`. Service names are validated before they become vertices, and dependency declarations create directed edges.

The generic `Graph<V>` class separates graph operations from the domain-specific service registry. This allows the same graph abstraction to work with different vertex types while keeping dependency naming and registration rules in the domain layer.

The `Edge<V>` record validates endpoints and weights at construction. The graph uses `LinkedHashMap` to preserve insertion order, making diagnostic output and traversal results repeatable for a given insertion sequence.

Public neighbor access returns an unmodifiable copy. This prevents callers from bypassing the graph's edge-count bookkeeping by directly modifying its internal adjacency maps.

The connected-components operation is restricted to undirected graphs. Directed graphs require a more specific definition, such as weakly connected or strongly connected components. Enforcing this distinction prevents a plausible-looking result from having the wrong mathematical meaning.

The example includes domain-specific service registration, dependency reporting, degree calculations, path reconstruction, and assertions for invalid state handling.

## PostgreSQL relational model

The SQL script creates a `graph_lab` schema containing graph metadata, vertices, and edges.

The `graph` table records whether a graph is directed and whether its edges are weighted. The `vertex` table stores vertices independently of their connections, allowing isolated vertices to be represented accurately.

The `edge` table references both endpoints through composite foreign keys. The graph identifier in each foreign key prevents an edge from connecting vertices belonging to different graphs.

For undirected graphs, a trigger normalizes endpoint order so that the same logical edge cannot be inserted once as \(u,v\) and again as \(v,u\). Directed edges retain their original orientation.

The uniqueness constraint prevents duplicate ordered endpoint pairs. The schema also rejects non-finite weights and creates indexes for source- and target-oriented edge lookups.

The `adjacency_list` view aggregates neighboring vertices into JSON arrays while retaining isolated vertices. Additional queries calculate undirected degrees, directed in-degrees and out-degrees, reachable vertices, and isolated vertices.

The recursive reachability query uses `UNION` rather than `UNION ALL`. Duplicate elimination ensures that a vertex is not repeatedly added to the recursive result when a cycle is present. This is an important database-level safeguard when traversing cyclic graphs.

The script uses a transaction and savepoint to demonstrate a temporary edge insertion followed by rollback. The foreign-key constraints prevent edges from referencing nonexistent vertices. The SQL model is suitable for learning relational graph storage, although very large graph traversals may require specialized indexing, query planning, or a graph-oriented execution engine.

## Traversal and path semantics

Breadth-first search explores vertices in layers according to their distance in number of edges from the start vertex. It can therefore find minimum-hop paths in unweighted graphs.

Depth-first search follows a path as far as possible before backtracking. It is useful for reachability analysis and provides the foundation for many cycle-detection algorithms.

Both algorithms maintain a visited set to prevent revisiting vertices indefinitely. This is essential for cyclic graphs and also avoids redundant work when multiple edges lead to the same vertex.

For adjacency-list representations, breadth-first and depth-first traversal run in \(O(V+E)\) time over the explored graph, assuming expected constant-time neighbor access. The auxiliary memory used by the traversal can grow to \(O(V)\).

Reachability is directional in a directed graph. If a path exists from \(u\) to \(v\), the reverse path need not exist. In an undirected graph, every edge is traversable in both directions, so reachability is symmetric.

## Correctness and practical limitations

A graph implementation should preserve several invariants:

- Every edge endpoint must belong to the same graph as the edge.
- An undirected edge must be available from both endpoints in adjacency-list storage.
- A logical edge must be counted once even when it is stored in both adjacency directions.
- Updating an existing edge must not increase the logical edge count.
- Removing an edge must remove both adjacency entries in an undirected graph.
- Isolated vertices must survive representation conversion and reporting.
- Directed edge orientation must be preserved during insertion, conversion, and traversal.

The examples use simple graphs rather than multigraphs. They do not implement weighted shortest-path algorithms, strongly connected components, graph isomorphism, or large-scale distributed graph processing.

In a production network model, the meaning of each edge weight must be documented. Latency, distance, cost, and capacity are different quantities and cannot be combined or optimized interchangeably without a defined objective function. The graph representation and traversal algorithm must reflect the actual operational question rather than merely the available data.
