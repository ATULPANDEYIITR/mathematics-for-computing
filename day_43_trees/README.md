# Trees: Rooted Hierarchies, Binary Trees, and Spanning Trees

## Technical scope

A tree is a connected, acyclic graph. This definition connects several structures that serve different purposes in computer science:

- A **rooted tree** represents a hierarchy in which one node is designated as the root and every other node has exactly one parent.
- A **binary tree** is a rooted structure in which each node has at most two children, conventionally called the left and right child.
- A **spanning tree** is a selection of edges from a connected graph that preserves connectivity while eliminating cycles and retaining every vertex.

These structures share fundamental properties, but their constraints and uses differ. Rooted trees represent parent-child relationships, binary trees impose a limit on child positions, and spanning trees optimize or simplify connections in a general graph.

The six implementations examine these distinctions through executable programs, structural measurements, graph algorithms, and a relational data model.

## Core mathematical properties

For a finite, nonempty, undirected tree containing \(V\) vertices and \(E\) edges,

\[
E = V - 1
\]

The following properties are equivalent for a finite, simple, undirected graph:

- The graph is connected and acyclic.
- Every pair of vertices has exactly one simple path between them.
- The graph is connected and has \(V-1\) edges.
- The graph is acyclic and has \(V-1\) edges.

The edge-count condition alone is insufficient to establish that a graph is a tree. A disconnected graph can contain a cycle in one component and an isolated vertex elsewhere. Connectivity and acyclicity must be considered together, or the appropriate equivalent conditions must be established.

A forest is an acyclic graph that may have multiple connected components. If a forest has \(V\) vertices and \(C\) connected components, then

\[
E = V-C
\]

This relationship is useful when validating graph structures and understanding why a disconnected graph cannot have a spanning tree.

### Rooted-tree terminology

The root has no parent. Every other node has one parent, and descendants are reached by repeatedly following child links. A leaf has no children. The depth of a node is the number of edges between that node and the root. The height of a rooted tree is the maximum node depth.

In this collection, tree height is measured in edges. A tree containing only a root therefore has height zero. An empty binary tree has height minus one, which makes the height convention consistent with the child-height recurrence:

\[
h(v)=1+\max(h(v_L),h(v_R))
\]

where a missing child has height \(-1\).

The number of edges in a rooted tree with \(V\) nodes is \(V-1\). This follows because every non-root node has exactly one parent edge.

### Binary-tree distinctions

A binary tree is not necessarily a binary search tree. A binary search tree adds an ordering invariant: keys in the left subtree are smaller than the node's key, and keys in the right subtree are larger. The implementations reject duplicate keys to make this invariant unambiguous.

Several structural properties are related but distinct:

| Property | Definition |
|---|---|
| Full | Every node has either zero or two children. |
| Complete | Every level except possibly the last is full, and the last level is filled from left to right. |
| Perfect | Every internal node has two children, and every leaf has the same depth. |
| Height-balanced | At every node, the heights of the left and right subtrees differ by at most one. |

A full tree need not be complete, and a complete tree need not be perfect. A balanced tree is not necessarily a binary search tree. These properties describe different aspects of structure or ordering.

## Traversal algorithms

Traversal determines the order in which nodes are processed.

**Preorder** visits a node before its children. It is useful for serializing a hierarchy or emitting a parent before its descendants.

**Postorder** visits children before their parent. It is useful when processing dependencies from the leaves upward, such as calculating aggregate values or removing hierarchical resources safely.

**Inorder** visits the left subtree, node, and right subtree. For a valid binary search tree with distinct keys, this produces keys in ascending order.

**Level-order traversal** processes nodes by depth using a queue. It is useful for displaying a hierarchy level by level and checking the completeness of a binary tree.

An iterative traversal uses an explicit stack or queue instead of relying on recursive calls. This is particularly important for highly skewed trees, where recursive traversal can exceed a language runtime's call-stack limit.

## Python implementation

The Python program provides three complementary models.

### Rooted hierarchies

`RootedTreeNode` stores a value, a parent reference, and an ordered list of children. Its `add_child` method rejects self-links, multiple parents, and attachments that would create a cycle.

`rooted_tree_metrics` measures node count, edge count, height, and leaf count. It also verifies that each child points back to its parent. The implementation uses an explicit stack so a deeply nested hierarchy does not depend on Python's recursion limit.

### Binary trees and search trees

`BinaryNode` represents a binary-tree node. Separate functions implement preorder, inorder, postorder, and level-order traversal. `binary_metrics` computes structural properties, while `tree_diameter` calculates the maximum number of edges on a path between any two nodes.

`BinarySearchTree` implements insertion, membership testing, minimum and maximum lookup, and deletion. Deletion distinguishes three cases:

- A leaf can be removed directly.
- A node with one child can be replaced by that child.
- A node with two children can be replaced by its inorder successor, after which the successor node is removed from its original position.

The successor method preserves the search-tree ordering invariant. The implementation is deliberately unbalanced, so sorted insertion can create a chain and degrade operations to linear time.

### Weighted graphs and spanning trees

`UndirectedGraph` stores an adjacency set for each vertex and a separate edge list containing weights. It supports breadth-first search, depth-first search, path reconstruction, cycle detection, and connectivity checks.

`DisjointSet` implements path compression and union by rank. These operations make Kruskal's minimum spanning tree algorithm efficient in practice. Kruskal processes edges in ascending weight order and accepts an edge only if its endpoints belong to different components.

The program also provides Prim's algorithm using a priority queue. Both algorithms reject disconnected graphs when a complete spanning tree is requested.

The self-tests exercise duplicate insertion, deletion of a node with two children, empty-tree behavior, cycle rejection, and consistency between the total weights returned by the two minimum spanning tree algorithms.

## JavaScript implementation

The JavaScript program emphasizes runtime validation, object references, and iterative algorithms.

`RootedNode` uses parent and child references to model hierarchy. Because JavaScript does not enforce domain invariants on ordinary objects, the attachment method explicitly rejects invalid relationships.

`BinarySearchTree` uses an iterative insertion and deletion strategy. Its `size` field changes only when a key is actually inserted or deleted. Duplicate insertion and deletion of a missing key return `false`, making these outcomes distinguishable from successful state changes.

The `levelOrder` function uses an array with a moving head index instead of repeatedly calling `Array.shift()`. Removing the first array element may require shifting the remaining elements, so a moving index avoids that repeated work.

`WeightedGraph` stores each vertex's neighbors in a `Map`. Kruskal's algorithm uses maps for the disjoint-set parent and rank structures. Its returned object contains both the selected edges and the total weight.

The executable checks cover sorted traversal, deletion, the empty-tree height convention, and minimum spanning tree weight. These checks are intentionally small enough to run without a testing framework.

## C++ case study: service-network design

The C++ program models a deployment network connecting a gateway, API service, cache, database, and worker.

Each weighted edge represents an installation or connection cost. The original network contains cycles because several alternative connections are available. The objective is to select a subset of edges that keeps every service reachable at minimum total cost.

### Architecture and data structures

`Network` stores vertex names, an adjacency list, and a weighted edge list. The adjacency list supports traversal, while the edge list is the primary input to Kruskal's algorithm.

`DisjointSet` represents connected components during edge selection. When an edge connects two different components, the algorithm accepts it and joins those components. An edge whose endpoints already share a representative would introduce a cycle, so it is rejected.

The algorithm sorts \(E\) edges and then performs disjoint-set operations. Its usual time complexity is

\[
O(E\log E)
\]

The sorting stage dominates for typical implementations using path compression and union by rank.

### Connectivity and failure handling

`connected` performs breadth-first search. `hasCycle` examines the graph component by component, which also handles disconnected input. `isTree` requires a nonempty graph, connectivity, and exactly \(V-1\) edges.

`shortestUnweightedPath` minimizes the number of connections, not their weights. This distinction matters: a minimum-hop route can differ from a minimum-cost route. The method reconstructs the path by recording each vertex's predecessor during breadth-first search.

The program rejects unknown endpoints, duplicate edges, self-loops, non-finite weights, and disconnected minimum spanning tree requests. The explicit `destroyTree` function releases the dynamically allocated binary-tree nodes used in the demonstration.

The network example is a model of topology and cost. In a production system, edge weights would need to be defined consistently, and a calculated spanning tree would need to be checked against operational requirements such as redundancy and failure tolerance. A minimum spanning tree minimizes connection cost, but by definition it does not preserve redundant paths.

## Java implementation: typed tree modeling

The Java implementation uses explicit domain types to make structural constraints visible.

`NodeKind` classifies nodes in an enterprise deployment hierarchy. `RootedNode` stores an identifier, a node kind, a parent, and a collection of children. The `children` accessor returns an unmodifiable view, preventing callers from bypassing the attachment method by directly modifying the list.

`TreeMetrics` is a Java record that groups the measured properties into an immutable result. The `Edge` record validates endpoints and weights at construction time, so invalid edge values cannot enter the network through that constructor.

`Network` uses a set for vertex membership, a map of adjacency maps for weighted connectivity, and a list of edges for Kruskal's algorithm. The `find` method compresses paths in the disjoint-set structure. The algorithm returns an immutable list of selected edges, and a stream calculates their total weight.

The implementation uses Java 17 language features and standard-library collections only. It demonstrates how type-oriented domain modeling, constructor validation, immutable results, and explicit exception handling can make graph-processing code easier to maintain.

The Java case study also separates structural measurement from graph optimization. The rooted hierarchy is measured through `measure`, while the weighted network is analyzed through `Network`. This prevents the meaning of a parent-child relationship from being confused with an arbitrary graph connection.

## PostgreSQL data model

The SQL implementation defines a dedicated `tree_lab` schema.

### Graph and node relationships

`graph` identifies each structure and classifies it as `ROOTED`, `BINARY`, or `UNDIRECTED`.

`tree_node` stores node identity, a graph-local key, an optional parent, a node kind, and optional binary-tree information. The composite foreign key `(graph_id, parent_node_id)` ensures that a parent belongs to the same graph as its child. This is stronger than a foreign key on `parent_node_id` alone.

The unique constraint on `(graph_id, node_key)` prevents duplicate logical node keys within one graph while allowing the same label to appear in another graph.

For binary nodes, `binary_side` records whether a node is its parent's left or right child. A partial unique index prevents two left children or two right children for the same parent. The database cannot infer the full binary search tree ordering rule from these constraints alone; that rule requires additional validation or a trigger that considers the parent and relevant descendants.

### Undirected weighted edges

`graph_edge` references two vertices belonging to the same graph and stores a numeric weight. Its check constraint rejects self-loops. The endpoint-normalization trigger puts the lower node identifier first, so inserting an edge in the opposite direction cannot create a second representation of the same undirected edge.

The edge table's uniqueness constraint prevents duplicate normalized endpoint pairs. The numeric weight is stored with a fixed precision suitable for costs. Production systems should select precision and scale according to their domain and explicitly define whether negative weights are permitted.

### Recursive traversal and structural checks

The recursive hierarchy query begins with the root and follows parent-child references to obtain each descendant's depth. A path array records visited node identifiers to guard against revisiting a node in malformed cyclic data.

The graph inspection function calculates the number of vertices and edges and checks reachability. The graph summary view provides vertex and edge counts for structural analysis.

Database constraints enforce local rules such as valid references, unique keys, and child-position limits. They do not automatically enforce every graph-wide invariant. For example, a self-referencing foreign key does not prove that every node is reachable from one root or that the parent relation is acyclic. Those properties require validation logic, controlled write procedures, or other enforcement mechanisms.

The `tree_property_snapshot` table can store measured results, but snapshots can become stale after graph mutations. A production implementation should refresh them transactionally or attach a version identifier to the graph state from which each snapshot was calculated.

## Spanning trees and minimum spanning trees

A spanning tree contains every vertex of a connected undirected graph and exactly \(V-1\) edges. If the original graph has cycles, different spanning trees may be possible.

A minimum spanning tree minimizes the sum of the selected edge weights:

\[
T_{\min} =
\underset{T\text{ spanning tree}}{\operatorname{arg\,min}}
\sum_{e\in T} w(e)
\]

The minimum spanning tree does not necessarily minimize the longest path, the number of hops between every pair, or the number of failures that can be tolerated.

Kruskal's algorithm considers edges in nondecreasing weight order and uses a disjoint-set structure to avoid cycles. Prim's algorithm grows a tree from a starting vertex, repeatedly selecting the least-weight edge connecting the current tree to an unvisited vertex.

For a connected graph with \(V\) vertices and \(E\) edges:

| Operation | Typical time complexity |
|---|---|
| Breadth-first or depth-first traversal | \(O(V+E)\) |
| Tree traversal | \(O(V)\) |
| Kruskal's minimum spanning tree | \(O(E\log E)\) |
| Search in an unbalanced binary search tree | \(O(h)\) |
| Search in a balanced binary search tree | \(O(\log V)\) |

The height \(h\) of an unbalanced binary search tree can reach \(V-1\). Balanced search trees maintain stronger structural invariants to avoid this worst case.

## Practical distinctions and limitations

A rooted hierarchy encodes a single-parent relationship. A general graph does not: a service may connect to several other services, and a vertex may be reachable by multiple paths.

A binary tree limits the number of child positions but does not require keys to be ordered. A binary search tree adds a key-ordering invariant. A balanced search tree adds yet another constraint concerning subtree heights or other balancing metadata.

A spanning tree is not simply a rooted tree with different labels. It is an edge subset of an existing graph. Selecting a root for a spanning tree can impose parent-child orientation afterward, but the original spanning-tree optimization concerns connectivity and edge selection.

The implementations also make different trade-offs. Iterative algorithms reduce recursion-depth risks. Hash-based adjacency structures provide efficient membership and neighbor lookup, at the cost of deterministic ordering unless ordering is imposed explicitly. Adjacency lists are well suited to sparse graphs, while adjacency matrices may be more convenient for dense graphs and constant-time edge-presence checks.

Graph validation must account for empty graphs, disconnected components, duplicate edges, self-loops, and invalid weights. Tree validation must also distinguish a missing child from a malformed parent reference. For persistent relational data, local integrity constraints and graph-wide validation solve different problems and should not be treated as interchangeable.
