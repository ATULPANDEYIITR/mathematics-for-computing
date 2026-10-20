# Advanced Graph Theory: Planarity, Isomorphism, Graph Minors, and Extremal Concepts

## Scope

This project examines four complementary areas of advanced graph theory through mathematical analysis, executable implementations, and relational modeling.

- **Planarity** determines whether a graph can be embedded in the plane without edge crossings, except at shared endpoints.
- **Graph isomorphism** determines whether two graphs have identical structures under a bijective relabeling of vertices.
- **Graph minors** describe graphs obtainable through vertex deletion, edge deletion, and edge contraction.
- **Extremal graph theory** investigates the maximum number of edges a graph can contain while avoiding specified structures or satisfying structural restrictions.

Each concept answers a different mathematical question. Isomorphism compares structures, planarity evaluates embedding possibilities, minor theory describes structural reductions, and extremal theory establishes quantitative limits.

## Mathematical Foundations

For a simple undirected graph \(G=(V,E)\), define

\[
n=|V|,\qquad m=|E|.
\]

A simple graph contains no self-loops or parallel edges. Its maximum possible number of edges is

\[
m\leq \binom{n}{2}=\frac{n(n-1)}{2}.
\]

This follows because every pair of distinct vertices can contribute at most one edge.

For a simple planar graph with \(n\geq 3\),

\[
m\leq 3n-6.
\]

For a simple bipartite planar graph with \(n\geq 3\),

\[
m\leq 2n-4.
\]

The bipartite bound follows from Euler's formula and the fact that a simple bipartite graph has no odd cycles, so every face in a suitable planar embedding has boundary length at least four.

These bounds provide necessary conditions for planarity, not sufficient conditions.

For example, \(K_{3,3}\) contains six vertices and nine edges. The general planar bound gives

\[
9\leq 3(6)-6=12,
\]

which does not reject the graph. The bipartite planar bound gives

\[
9\leq 2(6)-4=8,
\]

which is false. Therefore, \(K_{3,3}\) is non-planar.

The complete graph \(K_5\) is another fundamental non-planar graph because it has ten edges, exceeding the planar maximum of nine edges for five vertices.

## Planarity

Planarity concerns the existence of a crossing-free embedding, not merely the number of vertices and edges.

### Euler's Formula

For a connected planar graph,

\[
n-m+f=2,
\]

where \(f\) is the number of faces in a planar embedding.

For simple connected planar graphs with at least three vertices, combining Euler's formula with face-degree counting yields the bound \(m\leq 3n-6\). For bipartite planar graphs, the stronger bound \(m\leq 2n-4\) applies.

A graph that exceeds either applicable bound is certified as non-planar. A graph that satisfies the bound is not necessarily planar.

### Forbidden Structures

The graphs \(K_5\) and \(K_{3,3}\) are fundamental examples of non-planar structures.

Kuratowski's theorem states that a finite graph is planar if and only if it contains no subdivision of \(K_5\) or \(K_{3,3}\) as a subgraph. A subdivision replaces edges with paths by introducing intermediate vertices.

Wagner's theorem provides an equivalent characterization using graph minors: a finite graph is planar if and only if it contains neither \(K_5\) nor \(K_{3,3}\) as a minor.

These theorems explain why planarity, subdivisions, and graph minors are closely related without making the underlying concepts interchangeable.

### Implementation Strategy

The implementations use adjacency structures, graph counts, bipartiteness checks, and mathematical bounds to identify certifiable non-planar cases.

They distinguish three outcomes:

- `PLANAR`: planarity has been established by a complete decision procedure.
- `NON_PLANAR_CERTIFIED`: a valid certificate proves non-planarity.
- `UNDETERMINED`: the available tests cannot establish either conclusion.

An implementation that checks only Euler-derived inequalities must never report every graph satisfying those inequalities as planar.

For arbitrary large graphs, a production planarity service should use a proven complete algorithm, such as a linear-time planarity-testing algorithm.

## Graph Isomorphism

Two graphs \(G\) and \(H\) are isomorphic if there exists a bijection

\[
f:V(G)\rightarrow V(H)
\]

such that

\[
uv\in E(G)
\iff
f(u)f(v)\in E(H).
\]

The mapping must preserve both adjacency and non-adjacency. Matching vertex counts and edge counts alone is insufficient.

### Structural Invariants

Useful preliminary tests include:

- Equal numbers of vertices.
- Equal numbers of edges.
- Equal degree sequences.
- Equal numbers of connected components.
- Compatible cycle and neighborhood structures.

A degree sequence lists vertex degrees in sorted order. If two graphs have different degree sequences, they cannot be isomorphic.

Matching degree sequences does not establish isomorphism. Non-isomorphic graphs can share the same degree sequence.

### Constrained Backtracking

For small graphs, exact isomorphism testing can use recursive backtracking:

1. Compare basic graph invariants.
2. Build candidate vertex mappings using degree compatibility.
3. Assign an unmapped vertex to a compatible target vertex.
4. Reject a candidate when adjacency relationships contradict the mapping.
5. Continue until a complete bijection is found or every candidate fails.

A mapping can be represented as a function \(f\). For every newly assigned vertex, the implementation checks adjacency against previously mapped vertices.

The workflow is:

    Vertex and edge counts
            |
            v
      Degree sequence
            |
            v
    Candidate partitions
            |
            v
    Adjacency consistency
            |
            v
      Complete mapping
            |
            v
     Isomorphic / not isomorphic

This transparent approach is useful for small educational graphs. Its worst-case search can be exponential, so larger applications should consider partition refinement, canonical labeling, and specialized graph-isomorphism algorithms.

## Graph Minors

A graph \(H\) is a minor of graph \(G\) if \(H\) can be obtained by a sequence of the following operations:

- **Vertex deletion:** remove a vertex and all incident edges.
- **Edge deletion:** remove a selected edge.
- **Edge contraction:** merge the endpoints of an edge into one vertex.

### Edge Contraction

Suppose an edge \(uv\) is contracted. The vertices \(u\) and \(v\) are replaced by a merged vertex \(w\).

Edges incident to either endpoint are redirected to \(w\). Self-loops created by the operation are removed, and duplicate edges are collapsed when the model represents simple graphs.

For example, subdividing an edge of \(K_{3,3}\) introduces an intermediate vertex. The original \(K_{3,3}\) may no longer appear as a literal subgraph, but contracting the subdivided path restores the original structure as a minor.

This distinction matters:

| Relationship | Permitted operations |
|---|---|
| Subgraph | Delete vertices and edges |
| Minor | Delete vertices and edges, and contract edges |
| Isomorphism | Relabel vertices while preserving adjacency |

Minor theory is central to structural graph theory because it captures structural containment beyond literal subgraph matching.

### Minor Enumeration

A bounded minor-analysis implementation can enumerate selected reductions and compare the resulting graph against a target graph.

However, exhaustive minor enumeration can become combinatorially expensive. Practical implementations should restrict graph size, limit search depth, and use structural invariants to reject impossible candidates before expensive searches.

## Extremal Graph Theory

Extremal graph theory asks how many edges a graph can contain while avoiding a specified subgraph or satisfying a structural restriction.

The extremal number is commonly written as

\[
\operatorname{ex}(n,H),
\]

where \(H\) is a forbidden graph and \(\operatorname{ex}(n,H)\) denotes the maximum number of edges in an \(n\)-vertex graph containing no subgraph isomorphic to \(H\).

### Complete Graphs

Forbidding \(K_{n+1}\) on \(n\) vertices imposes no restriction because such a subgraph cannot exist. Consequently,

\[
\operatorname{ex}(n,K_{n+1})=\binom{n}{2}.
\]

Forbidding \(K_r\), where \(r\leq n\), is a different problem. Turán's theorem states that the maximum number of edges in an \(n\)-vertex graph containing no \(K_r\) is attained by the balanced complete \((r-1)\)-partite graph.

For \(r\geq 2\), if the vertex set is partitioned into \(r-1\) parts of sizes \(n_1,\ldots,n_{r-1}\), the corresponding complete multipartite graph has

\[
m=\sum_{i<j}n_i n_j
\]

edges. The maximum is achieved when the part sizes differ by at most one.

### Planar and Bipartite Planar Bounds

For simple planar graphs with \(n\geq 3\),

\[
m\leq 3n-6.
\]

For simple bipartite planar graphs with \(n\geq 3\),

\[
m\leq 2n-4.
\]

These are upper bounds. A graph exceeding an applicable bound is definitely non-planar, while a graph below the bound requires additional analysis.

A useful classification is:

    Graph metrics
         |
         v
    Select applicable bound
         |
         v
    Compare edge count
         |
         +--> Bound exceeded
         |       |
         |       v
         |   Non-planarity certified
         |
         +--> Bound satisfied
                 |
                 v
          Further testing required

Extremal bounds provide fast filters for structural analysis, but they do not replace complete recognition algorithms.

## Python Implementation

The Python program models a simple undirected graph using a dictionary of adjacency sets.

Its `Graph` class supports vertex insertion, edge insertion and deletion, vertex deletion, degree calculation, edge enumeration, induced subgraphs, connectivity testing, bipartiteness detection, and edge contraction.

The implementation uses sets to avoid duplicate neighbors and dictionaries to provide direct vertex-to-neighborhood lookup.

### Isomorphism

The isomorphism routine first compares vertex counts, edge counts, and sorted degree sequences. It then uses degree-compatible candidates and recursive backtracking to construct an exact mapping.

Adjacency checks prune invalid candidates before the entire mapping is constructed.

The implementation is appropriate for small graphs because exhaustive search can grow exponentially.

### Planarity Assessment

The planarity assessor calculates applicable Euler-derived bounds and checks for selected forbidden structures. It does not mistake a satisfied bound for a proof of planarity.

The result distinguishes certified non-planarity from unresolved cases. A complete planarity decision requires a complete algorithm or a valid planar embedding.

### Graph Minors

The contraction operation merges adjacent vertices, redirects their incident edges, and removes self-loops and duplicate edges.

The resulting graph preserves the simple-undirected-graph representation.

### Extremal Analysis

The script computes unrestricted simple-graph, planar, and bipartite-planar edge bounds where applicable. It compares graph measurements against these limits without claiming that satisfying a bound proves planarity.

For small graphs, direct coloring enumeration can provide another structural measurement through the chromatic polynomial. The number of valid colorings can be calculated by enumerating assignments and rejecting assignments that give adjacent vertices the same color. This technique is computationally expensive and should be limited to small inputs.

### Python-Specific Design Decisions

- Dictionaries and sets provide a natural adjacency representation.
- Immutable tuples can represent canonical undirected edges.
- Recursive functions make backtracking and graph reduction explicit.
- Exceptions reject invalid vertices, edges, and contraction requests.
- Standard-library combinations support bounded structural searches.
- Explicit size limits prevent untrusted inputs from triggering uncontrolled combinatorial work.

## JavaScript Implementation

The JavaScript implementation emphasizes event-driven graph analysis and asynchronous orchestration.

Its `Graph` class uses `Map` and `Set` for adjacency management, vertex lookup, and edge membership.

The graph constructors support common structures such as complete graphs, complete bipartite graphs, and cycles. These constructions provide controlled examples for testing structural properties.

### Structural Analysis

The isomorphism routine applies invariant filtering before constrained backtracking. Bipartiteness detection uses graph traversal and two-color assignment. Planarity-bound evaluation reports numerical certificates rather than claiming complete planarity recognition.

The edge-contraction method creates a merged vertex and updates the affected neighborhoods while preserving the simple-graph invariant.

### Event-Driven Policy Engine

The `GraphPolicyEngine` accepts graph-analysis requests, processes them asynchronously, and emits completion or failure events.

A typical processing sequence is:

    Graph update event
           |
           v
     Reconstruct graph
           |
           v
      Queue analysis
           |
           v
     Evaluate property
           |
           +--> Completion event
           |
           +--> Failure event

This architecture separates graph operations from application-level orchestration. It can support dependency-graph monitoring or topology analysis in systems where structural changes trigger recomputation.

Errors must remain explicit. A rejected analysis should not be represented as a valid negative mathematical result.

Input validation should also impose limits on graph size and search complexity, particularly when graphs are supplied by external clients.

## C++17 Implementation

The C++ program presents graph analysis as a dependency-network case study.

Vertices represent services, and edges represent undirected relationships between services. Graph contraction supports abstraction of selected relationships, while structural analysis evaluates properties of the resulting network.

### Data Structures

`RepositoryGraph` uses ordered associative containers:

- `std::set` stores vertices deterministically.
- `std::map` stores each vertex's adjacency set.
- `std::function` supports recursive isomorphism-search callbacks.
- Dedicated functions separate graph construction, structural comparison, and extremal calculations.

Ordered containers provide predictable logarithmic lookup. Graph traversal requires \(O(n+m)\) graph operations, with additional container lookup costs.

### Governance and Structural Decisions

The program evaluates:

- Graph validity and adjacency consistency.
- Vertex and edge counts.
- Degree-sequence compatibility.
- Exact isomorphism for bounded small graphs.
- Bipartiteness.
- Planarity-related numerical certificates.
- Edge contraction and selected minor relationships.
- Extremal edge bounds.

The planarity component reports an unresolved result when its available checks cannot establish planarity or certify non-planarity.

This explicit result state prevents numerical heuristics from being confused with a mathematical proof.

### C++ Implementation Considerations

Value-oriented graph construction helps isolate transformations from the original graph. Explicit exceptions make invalid operations visible, while bounded search protects against excessive computational work.

For larger dependency networks, exhaustive isomorphism or minor enumeration should be replaced with more scalable algorithms and strict resource limits.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented domain model that separates graph storage, mathematical results, and policy evaluation.

### Domain Types

| Type | Responsibility |
|---|---|
| `Graph` | Stores vertices and edges and performs graph operations |
| `Edge` | Represents a canonical undirected edge |
| `GraphRelation` | Represents the outcome of graph comparison |
| `PlanarityStatus` | Distinguishes established planarity, certified non-planarity, and unresolved cases |
| `PlanarityAssessment` | Stores a planarity status and its mathematical justification |
| `MergeRule` | Defines an application policy based on graph properties |
| `DenseGraphRule` | Evaluates a density-related restriction |
| `GovernanceService` | Coordinates graph validation and policy evaluation |

Java records provide immutable value objects for edges and analytical results. Enums make result states explicit, while interfaces separate policy contracts from individual policy implementations.

### Policy Evaluation

The governance service evaluates graph properties independently of graph storage. A density policy can reject a graph that exceeds a specified bound, but it must not treat a satisfied upper bound as proof of planarity.

This separation prevents a domain policy from overstating what its underlying mathematical test establishes.

### Failure States and Validation

The model rejects invalid graph operations, including edges with missing endpoints and contractions of nonexistent edges.

The isomorphism search uses preliminary invariants and exact adjacency checks. The planarity service distinguishes established results from inconclusive analysis.

For production deployments, validation should include maximum graph sizes, execution budgets for combinatorial algorithms, and clear error reporting. Concurrent access also requires an explicit mutability and synchronization policy if graphs are shared between threads.

## PostgreSQL Implementation

The PostgreSQL script represents graph structures and their analysis through relational tables, constraints, functions, views, and transactions.

### Relational Model

| Table | Responsibility |
|---|---|
| `graph` | Stores graph definitions and metadata |
| `vertex` | Stores vertices belonging to each graph |
| `graph_edge` | Stores undirected edges using canonical endpoint ordering |
| `graph_analysis` | Records analytical properties and decision states |
| `isomorphism_mapping` | Stores vertex mappings between compared graphs |
| `minor_operation` | Records vertex deletion, edge deletion, and contraction operations |
| `extremal_bound` | Stores upper bounds used in structural analysis |

### Canonical Edge Representation

An undirected edge is stored using two ordered endpoints:

\[
u<v.
\]

This prevents the same edge from being represented as both \((u,v)\) and \((v,u)\).

A unique constraint prevents duplicate edges, and a check constraint rejects self-loops.

A validation trigger checks that both edge endpoints belong to the graph identified by the edge record. This protects relational integrity even when multiple application clients write to the database.

### Graph Metrics

The `graph_metrics` view calculates vertex counts, edge counts, and the simple planar edge bound where applicable.

Reusable PostgreSQL functions calculate:

- `graph_vertex_count`
- `graph_edge_count`
- `planar_simple_edge_bound`
- `planar_bipartite_edge_bound`

The functions distinguish small graphs from cases where the standard Euler-derived bounds apply.

### Analytical Reporting

A common table expression combines graph metrics with the relevant extremal bounds and classifies each graph according to whether it exceeds the applicable limit.

The report distinguishes a graph that violates a necessary planarity condition from one that merely satisfies the condition. Satisfying the bound does not establish planarity.

The relational model also records isomorphism mappings and graph-reduction operations so that structural comparisons and minor transformations can be inspected independently of the original graph definition.

### Transactions and Integrity

Analytical records are inserted transactionally so that a decision and its associated metadata remain consistent.

Database constraints reject malformed states, including duplicate edges, self-loops, invalid analysis categories, invalid status values, and negative numerical bounds.

Indexes are applied where they support common access patterns, such as retrieving vertices and edges by graph or finding the endpoint pair for an undirected edge.

These mechanisms make PostgreSQL responsible for enforcing relational integrity rather than relying exclusively on application-level validation.

## Relational Workflow

The database analysis process follows this structure:

    Graph definition
          |
          +--> Vertices
          |
          +--> Edges
          |
          v
      Graph metrics
          |
          +--> Planar edge bounds
          |
          +--> Bipartite edge bounds
          |
          +--> Isomorphism mappings
          |
          +--> Minor operations
          |
          v
     Recorded analysis
          |
          v
     Structural reporting

The workflow keeps graph data separate from computed conclusions. If the graph changes, earlier analysis records should be treated as historical unless they are recomputed and explicitly associated with the updated graph state.

## Complexity and Limitations

Graph operations have different computational costs.

| Operation | Typical complexity or limitation |
|---|---|
| Vertex lookup | Expected \(O(1)\) with hash-based structures; \(O(\log n)\) with ordered maps |
| Edge membership | Expected \(O(1)\) with adjacency sets; \(O(\log n)\) with ordered sets |
| BFS or DFS | \(O(n+m)\) with adjacency-list representations |
| Degree-sequence comparison | \(O(n\log n)\) when sorting is required |
| Exact isomorphism search | Exponential worst case for naive backtracking |
| \(K_5\) subgraph search | Combinatorial enumeration |
| Minor enumeration | Potentially combinatorial |
| Euler-derived bound evaluation | \(O(1)\) after graph counts are available |
| Direct coloring enumeration | Exponential in the number of vertices |

The precise cost depends on the representation and implementation details.

The main limitation of the bounded planarity routines is that mathematical inequalities and selected obstruction checks do not constitute a complete planarity algorithm for arbitrary graphs.

Likewise, exact backtracking is appropriate for small graphs but may become impractical as graph size increases. Exhaustive minor enumeration can require substantial time and memory.

Production implementations should apply explicit resource limits, use complete specialized algorithms where required, and distinguish mathematical conclusions from inconclusive results.

## Security and Data Integrity

Graph-processing applications may receive dependency networks, topology definitions, or externally supplied graph structures. Invalid or deliberately oversized inputs can cause integrity problems or excessive computation.

Relevant safeguards include:

- Rejecting self-loops when simple graphs are required.
- Ensuring every edge endpoint belongs to the correct graph.
- Preventing duplicate undirected edges.
- Validating vertex and edge limits before expensive operations.
- Bounding recursive search and enumeration.
- Preserving canonical edge representation.
- Separating source graph data from derived analytical results.
- Recording the graph version associated with each analysis.
- Enforcing relational constraints at the database level.
- Returning explicit failure states instead of interpreting resource exhaustion as a mathematical conclusion.

The PostgreSQL implementation enforces data integrity through constraints, foreign keys, and trigger validation. The application implementations use explicit validation and exception handling to reject invalid operations.

## Relationship Between the Four Concepts

| Concept | Central question | Principal mechanism |
|---|---|---|
| Planarity | Can the graph be embedded without crossings? | Planarity testing, embeddings, forbidden subdivisions, and minor obstructions |
| Graph isomorphism | Are two graphs structurally identical up to relabeling? | Bijections that preserve adjacency |
| Graph minors | Can one graph be obtained from another through allowed reductions? | Vertex deletion, edge deletion, and edge contraction |
| Extremal graph theory | How many edges can a graph contain under a structural restriction? | Upper bounds and extremal constructions |

The concepts interact without becoming interchangeable.

A graph may be compared for isomorphism regardless of whether it is planar. A graph may contain another graph as a minor without containing it as a literal subgraph. Extremal inequalities may certify non-planarity when violated, but satisfying those inequalities does not prove planarity.

Kuratowski's theorem connects planarity to forbidden subdivisions, while Wagner's theorem connects planarity to forbidden minors. Extremal bounds provide complementary numerical restrictions, and isomorphism identifies when differently labeled graph constructions represent the same structure.

Together, these four perspectives provide a framework for analyzing graph structure, containment, embedding constraints, and density limits through mathematically distinct but mutually informative methods.
