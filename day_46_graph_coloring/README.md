# Graph Coloring: Algorithms, Bipartite Graphs, and Applications

## Scope

Graph coloring assigns labels to vertices so that adjacent vertices receive different labels. It models resource conflicts in which two incompatible activities cannot use the same resource at the same time.

This project implements graph coloring in Python, JavaScript, C++, Java, and PostgreSQL. The programs use different perspectives: algorithm experimentation, event-driven planning, radio-frequency allocation, enterprise maintenance scheduling, and relational timetable validation.

The central mathematical model is an undirected graph \(G=(V,E)\), where \(V\) is the set of vertices and \(E\) is the set of edges.

A vertex represents an entity being assigned a resource. An edge represents a conflict that prevents the two endpoint vertices from sharing a resource.

A coloring is a function

\[
c:V\rightarrow\{0,1,\ldots,k-1\}
\]

that satisfies

\[
\forall (u,v)\in E,\quad c(u)\ne c(v).
\]

The smallest possible number of colors is the **chromatic number**, written \(\chi(G)\).

The examples use zero-based color identifiers. A color identifier has no inherent meaning until the application maps it to a concrete resource, such as a time slot, register, or radio-frequency channel.

## Vertex coloring and graph representation

An adjacency-list representation stores the neighbors of each vertex. It is well suited to sparse graphs because it stores relationships that actually exist rather than allocating a full \(V \times V\) matrix.

For an undirected graph, adding an edge \((u,v)\) must update both adjacency lists. A correct representation must also account for isolated vertices, which have no edges but remain members of the graph.

The implementations reject self-loops. A self-loop would require a vertex to have a different color from itself, making a proper coloring impossible. Parallel edges do not change the mathematical coloring constraint for a simple graph, so the implementations use sets or normalized edge representations to avoid redundant adjacency relationships.

The principal graph operations are:

- **Vertex insertion:** create an adjacency entry even when no edges exist.
- **Edge insertion:** establish a symmetric conflict relationship.
- **Color validation:** verify complete vertex coverage, legal color values, and different colors across every edge.
- **Conflict detection:** identify edges whose endpoints have received the same color.

Validation is separate from color generation. A coloring algorithm proposes an assignment; validation determines whether the assignment satisfies the graph's constraints.

## Greedy coloring and DSATUR

### Greedy coloring

Greedy coloring processes vertices in an order and assigns each vertex the smallest nonnegative color that none of its already-colored neighbors uses.

For a vertex \(v\), define its unavailable colors as

\[
F(v)=\{c(u)\mid u\in N(v),\ u\text{ already colored}\}.
\]

The selected color is the smallest nonnegative integer not in \(F(v)\).

Greedy coloring is efficient and easy to implement, but its result depends on vertex ordering. A poor ordering can use substantially more colors than an optimal solution requires. The result is a valid upper bound on the chromatic number, not necessarily the chromatic number itself.

### DSATUR

DSATUR selects an uncolored vertex with the greatest saturation degree. Saturation degree is the number of distinct colors currently assigned to its colored neighbors.

When saturation degrees tie, the implementations use vertex degree as a secondary selection criterion. A vertex connected to many neighbors is often more constrained and benefits from being colored earlier.

DSATUR repeatedly:

- Selects the most constrained uncolored vertex.
- Determines the colors unavailable through its colored neighbors.
- Assigns the smallest available color.
- Continues until every vertex is colored.

DSATUR generally improves heuristic solutions for difficult conflict graphs. It does not guarantee an optimal coloring unless combined with an appropriate exact search.

### Exact chromatic number

The Python and C++ implementations include backtracking-based exact search for non-bipartite graphs. They start with a valid heuristic coloring as an upper bound and test whether fewer colors suffice.

Backtracking assigns a color, checks the constraints against already-colored neighbors, and reverses the assignment when the partial solution cannot be extended.

Symmetry reduction avoids exploring equivalent solutions that differ only in color labels. For example, renaming every occurrence of color 0 to color 2 does not produce a mathematically different coloring.

Exact chromatic-number computation has exponential worst-case complexity. The method is useful for small and moderate graphs, teaching algorithmic search, and validating heuristic results. It is not a general guarantee of practical performance on large graphs.

## Bipartite graphs

A graph is bipartite when its vertices can be divided into two disjoint sets \(A\) and \(B\) such that every edge connects a vertex in \(A\) to a vertex in \(B\). No edge may connect two vertices within the same partition.

A breadth-first search assigns alternating partition labels while traversing each connected component. If an edge joins two vertices already assigned to the same partition, the graph is not bipartite.

The time complexity is

\[
O(|V|+|E|).
\]

A nonempty bipartite graph containing at least one edge has chromatic number 2. An edgeless graph with at least one vertex has chromatic number 1 because all vertices can share one color. The empty graph is conventionally assigned chromatic number 0 in these implementations.

An odd cycle, such as a triangle, is not bipartite. Alternating two colors around the cycle eventually forces the final edge to connect vertices with the same color.

Bipartiteness does not mean every application has only two practical resource types. It is a mathematical property of the conflict graph. A scheduling system may have other constraints, such as time availability or resource capacities, that require a richer model.

## Python implementation

The Python script provides an executable graph-analysis library using only the standard library.

`UndirectedGraph` stores adjacency sets and exposes vertex, edge, degree, validation, conflict-detection, and coloring operations. `GraphError` distinguishes invalid graph operations from internal algorithm failures.

`greedy_coloring()` accepts an optional complete vertex ordering. This makes it possible to examine how the same graph can produce different greedy results under different orderings.

`dsatur_coloring()` dynamically chooses a vertex according to saturation degree and vertex degree. `bipartition()` processes disconnected components as well as connected graphs, which is necessary because testing only one component could miss an odd cycle elsewhere.

`exact_coloring()` uses the bipartite result when possible and otherwise combines a heuristic upper bound with a constrained backtracking search.

The exam-scheduling case study builds edges whenever two exams share an enrolled student. A shared student cannot attend two exams in the same time slot, so the graph-coloring constraint directly represents a scheduling restriction.

The register-allocation example uses overlapping live ranges. Two values with overlapping closed intervals interfere and therefore cannot occupy the same register under the simplified model. Real compiler register allocation also handles register classes, calling conventions, spilling, and machine-specific constraints.

The validation demonstrations cover invalid assignments, self-loops, incomplete vertex orders, unknown vertices, odd cycles, and valid but unnecessarily expensive colorings.

## JavaScript implementation

The JavaScript file combines graph coloring with an event-driven resource-planning service.

The `Graph` class keeps its adjacency map private. Its `validateColoring()` method verifies that the assignment covers exactly the graph's vertices and uses legal integer color identifiers.

The bipartite test uses an array and a moving queue index. This avoids repeated array shifting during breadth-first traversal.

`ColoringService` extends Node.js's `EventEmitter`. It separates calculating a candidate plan from publishing an accepted plan. Consumers can react to `plan:proposed`, `plan:published`, and `plan:evaluated` events without coupling their logic directly to the coloring algorithm.

The service assigns revisions to published plans. When a candidate graph is evaluated, the caller supplies the expected revision. A stale revision is rejected, illustrating how a resource-planning application can avoid evaluating changes against an outdated accepted state.

This revision check is an in-memory demonstration rather than a distributed concurrency guarantee. A production service would need persistent revisions, atomic updates, and appropriate locking or optimistic concurrency controls.

The implementation deliberately uses greedy coloring instead of duplicating the Python exact-search implementation. Its focus is event-driven processing, private state, plan publication, and validation at service boundaries.

## C++ case study: radio-frequency assignment

The C++ program models transmitters that interfere with neighboring transmitters. An edge represents an interference relationship, and a color represents a frequency channel.

`InterferenceGraph` maps transmitter names to integer vertex identifiers. Integer identifiers make adjacency storage compact, while `vector<set<int>>` maintains neighbor relationships and prevents duplicate edges.

The DSATUR implementation selects the uncolored transmitter with the greatest saturation degree, breaking ties by degree. It then chooses the lowest channel not used by an adjacent transmitter.

The bipartite test performs breadth-first traversal over all connected components. The exact chromatic-number routine uses recursive search to test smaller channel limits, with DSATUR selection to reduce branching.

The program validates assignments before reporting them. It also demonstrates rejection of a self-interference edge and verifies that assigning the same channel to every transmitter is invalid when interference edges exist.

The mathematical model is intentionally limited to pairwise conflicts. Real radio planning also considers signal strength, geographic distance, antenna characteristics, regulatory spectrum restrictions, and interference between channels that are not identical. Graph coloring is a useful abstraction, but it is not a complete radio-propagation model.

## Java implementation: enterprise maintenance scheduling

The Java program models maintenance jobs competing for technicians, equipment, and exclusive work areas.

The `Job` record stores a job identifier, description, and immutable resource set. Its constructor validates the identifier and description before the job enters the scheduling model.

`Conflict` records the shared resources responsible for an edge. This gives operators an explanation for a scheduling restriction rather than only reporting that two jobs conflict.

`MaintenanceGraph` builds an undirected conflict graph by intersecting resource sets for each pair of jobs. Its validation method requires a complete assignment and verifies every edge.

`Schedule` represents the generated slot assignments, the number of slots used, and their validation status. `SchedulingService` separates job validation from schedule creation and maintains explicit job states.

The Java model uses records and immutable collection copies to reduce accidental mutation of domain data. Linked collections provide stable output ordering, which makes test results and operational logs easier to compare.

The example uses DSATUR because it is practical for heuristic scheduling and avoids requiring exact optimization for every operational change. A production scheduler would also need maintenance windows, job duration, dependencies, resource capacities, priority rules, and authorization for schedule changes.

## PostgreSQL data model

The SQL script represents exam scheduling relationally rather than performing graph search inside SQL.

| Relation | Purpose |
|---|---|
| `students` | Stores students with unique email addresses. |
| `exams` | Stores courses requiring examination slots and their workflow states. |
| `time_slots` | Defines valid scheduling windows. |
| `enrollments` | Connects students to exams through a composite primary key. |
| `exam_conflicts` | Stores normalized undirected conflict edges and shared-student counts. |
| `exam_assignments` | Associates each exam with a time slot. |

The enrollment table is the source of truth for conflict generation. A self-join matches enrollments belonging to the same student but different exams. The query normalizes each edge using `LEAST` and `GREATEST`, then counts shared students.

The constraint `exam_id_low < exam_id_high` prevents self-edges and ensures that the reverse representation of an existing edge cannot be inserted as a separate row.

Primary keys and foreign keys enforce identity and referential integrity. Check constraints restrict exam states, positive conflict counts, and valid time intervals. Indexes support enrollment lookups and slot-based assignment reports.

`exam_coloring_report` provides an operational view of assignments. `exam_slot_conflicts` joins the conflict graph to the current assignment table and returns every edge whose endpoints share a slot. An empty result means the currently assigned exams satisfy the pairwise conflict rule.

The transaction near the end deliberately introduces an invalid assignment, queries the resulting conflicts, and rolls the change back. This demonstrates the difference between detecting a violation and enforcing the rule before a change is committed.

The database cannot enforce the cross-row coloring constraint through an ordinary row-level `CHECK` constraint. A production system must route assignment changes through a controlled transaction, trigger, or service that validates all affected edges. Concurrent schedule changes must also be serialized or protected with a suitable locking strategy.

The triangle query identifies triangle witnesses. A triangle proves that a graph is not bipartite, but failure to find a triangle does not prove bipartiteness because odd cycles can be longer than three edges.

## Applications and model boundaries

### Examination timetables

Exams become vertices, and shared students create edges. A color represents an examination period. Proper coloring prevents direct student conflicts, but it does not automatically minimize student gaps, balance room capacity, or respect instructor availability.

### Compiler register allocation

Program values become vertices, and overlapping live ranges create edges. Colors correspond to physical registers. If the graph requires more colors than available registers, a compiler may spill selected values to memory. Real allocation must account for register types and machine-specific constraints.

### Radio-frequency planning

Transmitters become vertices, and interference relationships create edges. Colors identify channels. A proper coloring prevents modeled adjacent transmitters from sharing a channel, but the graph must accurately represent the physical interference constraints.

### Map coloring

Regions become vertices, with edges between regions sharing a boundary under the chosen adjacency definition. The four-color theorem guarantees that every planar map can be colored with at most four colors. That result does not imply that every arbitrary graph requires at most four colors.

### Operational resource scheduling

Maintenance jobs, deployments, or incompatible tasks can be modeled as vertices. Shared exclusive resources create edges, and colors represent time slots. Duration, precedence, and capacity constraints may require additional optimization models beyond ordinary vertex coloring.

## Correctness, complexity, and limitations

A coloring is correct only if every vertex is assigned a legal color and no edge has equally colored endpoints. A low color count is desirable, but it is not sufficient if any conflict remains.

| Operation | Typical complexity | Guarantee |
|---|---|---|
| Adjacency-list storage | \(O(V+E)\) space | Stores graph structure. |
| Bipartite testing | \(O(V+E)\) time | Correctly determines bipartiteness. |
| Greedy coloring | Depends on ordering and representation | Produces a proper coloring. |
| DSATUR heuristic | Polynomial per selection, with repeated vertex and neighbor scans | Produces a proper coloring, not necessarily an optimal one. |
| Exact chromatic number | Exponential worst-case search | Finds the minimum number of colors when it completes. |
| Coloring verification | \(O(V+E)\) for a valid complete assignment | Detects violated graph constraints. |

Graph coloring is NP-hard in the general case when minimizing the number of colors. Practical systems therefore often use heuristics and verify their output independently.

A coloring model can also be incomplete. If a real conflict is omitted from the graph, the algorithm may return a mathematically valid coloring that is operationally unsafe. If unnecessary edges are added, the system may consume more resources than needed.

Reliable applications must maintain accurate graph construction, validate assignments after changes, define the meaning of each color, and keep application-specific constraints separate from the graph-coloring rule.
