# Euler and Hamiltonian Graphs

## Mathematical model

A graph is written as \(G = (V, E)\), where \(V\) is the set of vertices and \(E\) is the set of edges connecting them. In an undirected graph, an edge \(\{u,v\}\) can be traversed in either direction.

Eulerian and Hamiltonian problems describe different kinds of coverage. Eulerian problems focus on edges, while Hamiltonian problems focus on vertices. A graph may satisfy one property without satisfying the other.

The implementations use undirected simple graphs without self-loops or duplicate edges. This restriction keeps the examples and route validation consistent across the four programming languages and the relational schema.

## Euler paths and circuits

An **Euler trail** traverses every edge exactly once. A trail may start and finish at different vertices.

An **Euler circuit** traverses every edge exactly once and returns to its starting vertex. Every Euler circuit is an Euler trail, but an Euler trail is not necessarily a circuit.

For an undirected graph, ignoring isolated vertices, the graph must be connected to admit an Euler trail. The degree of a vertex is the number of incident edges.

| Graph condition | Result |
|---|---|
| Connected active portion and zero odd-degree vertices | Euler circuit exists |
| Connected active portion and exactly two odd-degree vertices | Euler trail exists, but no Euler circuit |
| More than two odd-degree vertices | No Euler trail |
| Multiple disconnected components containing edges | No Euler trail covering every edge |

An isolated vertex does not prevent an Euler trail through the remaining graph because the connectivity condition concerns vertices incident to edges. If the graph contains no edges, the empty-edge case must be handled separately by the implementation.

### Hierholzer's algorithm

Hierholzer's algorithm constructs an Euler trail by repeatedly following unused edges and merging closed traversals into the current route. Each undirected edge receives an identifier so that its two adjacency-list entries represent one logical edge.

The algorithm runs in \(O(V+E)\) time when adjacency lists and edge identifiers are used. It is suitable for large edge-covering tasks compared with brute-force route enumeration.

A route validator should verify that every edge is used exactly once. Merely checking that consecutive vertices are adjacent is insufficient because the route might repeat an edge or omit another one.

## Hamiltonian paths and cycles

A **Hamiltonian path** visits every vertex exactly once. It does not need to return to the starting vertex.

A **Hamiltonian cycle** visits every vertex exactly once and then returns to its starting vertex. In the implementations, the stored cycle lists each vertex once; the closing edge is checked separately instead of repeating the starting vertex in the list.

Hamiltonian problems are not governed by a simple degree-parity criterion comparable to Eulerian problems. Finding a Hamiltonian path or cycle is computationally difficult in general, and the decision problem is NP-complete.

The implementations use depth-first backtracking. Each candidate vertex is marked visited before recursion and unmarked when that branch fails. Fixing the starting vertex for cycle search eliminates equivalent rotations of the same cycle, although it does not remove every symmetric candidate.

The worst-case running time is factorial in the number of vertices. These implementations are intended for learning and modest graphs, not as a general-purpose solver for very large networks.

## Why the distinctions matter

Consider a square with vertices A, B, C, and D and edges AB, BC, CD, and DA.

Every vertex has degree two. The graph admits an Euler circuit, and the route A-B-C-D also forms a Hamiltonian cycle.

Now consider a triangle A-B-C-A with a pendant edge C-D. Vertices A and B have degree two, C has degree three, and D has degree one. Exactly two vertices have odd degree, so an Euler trail exists, but an Euler circuit does not. The graph also has a Hamiltonian path, such as D-C-A-B, but no Hamiltonian cycle because D has only one incident edge.

The complete graph \(K_4\) contains every possible edge between four distinct vertices. Every vertex has degree three, so all four vertices have odd degree. No Euler trail exists. Nevertheless, a Hamiltonian cycle exists because the vertices can be visited once in a cycle.

These examples show why edge coverage and vertex coverage must be tested independently.

## Python implementation

The Python program defines a `Graph` class backed by adjacency lists and an explicit edge list. The edge list preserves edge identity, while the adjacency dictionary supports degree queries and neighbor traversal.

The connectivity check begins at a non-isolated vertex and confirms that every other non-isolated vertex is reachable. Euler eligibility then combines this condition with the count of odd-degree vertices.

The `euler_trail()` method implements Hierholzer's algorithm with edge indices and a stack. Its final edge-count check prevents an incomplete traversal from being reported as a valid result.

The Hamiltonian search methods use recursive backtracking. `find_hamiltonian_path()` tries different starting vertices; `find_hamiltonian_cycle()` anchors the cycle at the first vertex. The script also contains assertions for a square, a triangle with a tail, a disconnected graph, and invalid duplicate or unknown edges. A brute-force reference function is included for cross-checking Hamiltonian paths on small graphs.

## JavaScript implementation

The JavaScript implementation uses a `Map` from vertex identifiers to neighbor arrays. This representation makes the graph structure explicit and allows vertex validation before graph analysis.

Undirected edge keys are canonicalized so that A-B and B-A are recognized as the same edge. The Euler traversal uses indexed edges rather than relying only on neighbor names.

The `verifyEulerTrail()` function checks the returned route against a multiset of edges. It confirms that the route contains exactly one traversal of every stored edge, rather than assuming that an algorithm's output is correct simply because it was produced by the traversal routine.

The Hamiltonian methods return a path or `null` when no route is found. This distinction makes failure handling explicit and avoids confusing a missing route with a valid empty route.

## C++ case study: road maintenance

The C++ program models a district road network in which vertices are inspection locations and edges are road segments. The maintenance team needs to know whether every segment can be inspected in one continuous traversal. That is an Eulerian question.

The same district can also be analyzed as a station-visiting problem, in which every inspection location must be visited once. That is a Hamiltonian question.

`DistrictGraph` owns vertex names, adjacency lists, and an edge list. `addEdge()` checks vertex indices, rejects self-loops, and detects duplicate undirected edges. The graph analysis methods separate connectivity, degree parity, Euler traversal, and Hamiltonian backtracking.

Hierholzer's algorithm is used for edge coverage, while recursive search is used for vertex coverage. The program reports both properties for a ring, a complete network, and a disconnected network.

The two algorithms serve different operational goals. An Euler route can reduce repeated road-segment inspections, whereas a Hamiltonian route can represent a visit plan that reaches every station exactly once. Real road routing may require weighted edges, travel-time constraints, directed streets, and route optimization, which are outside this unweighted undirected model.

## Java implementation: facilities route planning

The Java program uses a domain-oriented `Graph` class and an immutable `Road` record. The `RouteType` enum gives route classifications explicit names instead of relying on unvalidated strings.

Graph construction validates unique station names. `addRoad()` validates both endpoint indices and rejects duplicate undirected roads before updating adjacency lists.

The Euler and Hamiltonian algorithms use separate methods because their completion conditions differ. Euler traversal tracks edge identifiers; Hamiltonian search tracks visited vertices and checks the closing edge for a cycle.

The `report()` method converts vertex indices back into station names so that route output is meaningful to an operations team. The example also demonstrates validation failure when a duplicate road is added.

The implementation favors standard Java collections and explicit validation over external graph libraries. Its recursive Hamiltonian methods remain exponential and can exhaust the call stack on sufficiently large graphs.

## PostgreSQL data model

The SQL script stores graph definitions in `graph`, vertices in `vertex`, and undirected edges in `edge`.

The composite primary and foreign keys keep edges associated with valid vertices in the same graph. The `CHECK (endpoint_a < endpoint_b)` rule establishes a canonical endpoint order. The unique constraint on `(graph_id, endpoint_a, endpoint_b)` prevents duplicate edges.

The `vertex_degree` view calculates each vertex's degree by counting both endpoint positions. `UNION ALL` is necessary because every undirected edge contributes one incidence to each endpoint.

A recursive common table expression computes reachability. The parity query combines connectivity with the count of odd-degree vertices to determine whether an Euler trail or circuit can exist.

Hamiltonian analysis requires a different kind of evaluation. The `route_analysis` table stores candidate routes, and subsequent queries validate vertex coverage, uniqueness, consecutive adjacency, and the closing edge for cycles. The database schema records findings; it does not claim to solve the general Hamiltonian search problem efficiently in SQL.

Transactions group related analysis inserts so that the set of stored findings is committed together. Indexes support edge endpoint lookups and retrieval of route analyses by graph and route type.

The schema's constraints enforce structural integrity, but application-level algorithms are still needed to find routes. A row stating that a route exists is a stored finding, not a mathematical proof. Production systems should validate results before persisting them and record enough information to reproduce each analysis.

## Complexity and limitations

| Operation | Typical complexity |
|---|---|
| Degree lookup with adjacency lists | \(O(1)\) |
| Connectivity traversal | \(O(V+E)\) |
| Euler existence test | \(O(V+E)\) |
| Hierholzer's Euler trail construction | \(O(V+E)\) |
| Hamiltonian path or cycle search | Exponential in the worst case |
| Validation of a supplied Hamiltonian path | \(O(V+E)\) with the adjacency-list implementations shown |

The exact cost of Hamiltonian search depends on the graph's structure and how quickly failed branches can be pruned. Dense graphs can generate many candidate permutations, while sparse graphs may allow failures to be detected early.

The examples use undirected, unweighted graphs. Directed Eulerian graphs require in-degree and out-degree conditions, and directed Hamiltonian problems require respecting edge direction. Weighted route optimization introduces a separate objective, such as minimizing total distance or travel time, rather than merely determining whether a route exists.
