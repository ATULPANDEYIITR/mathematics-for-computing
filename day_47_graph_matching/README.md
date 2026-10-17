# Graph Matching: From Disjoint Edges to Optimal Bipartite Assignment

## Technical scope

Graph matching identifies a set of edges that do not share vertices. It is useful when entities must be paired without assigning any entity to more than one partner.

This project examines four connected concepts:

- **Matching:** a set of pairwise vertex-disjoint edges.
- **Maximal matching:** a matching to which no additional edge can be added.
- **Maximum matching:** a matching containing the greatest possible number of edges.
- **Bipartite matching:** a matching in a graph whose vertices are divided into two disjoint partitions, with edges connecting vertices from opposite partitions.

The implementations use graph matching to model assignment problems, particularly reviewer allocation across repository pull requests. Eligibility determines which edges exist. The matching algorithm selects compatible edges without violating one-to-one assignment constraints.

## Mathematical model

An undirected graph is \(G=(V,E)\), where \(V\) is the vertex set and \(E\) is the edge set. A matching \(M\subseteq E\) satisfies the condition that no two edges in \(M\) share a vertex.

The cardinality of a matching is \(|M|\).

A maximal matching cannot be extended by adding a single edge while retaining the matching property. A maximum matching has the largest cardinality among all matchings in the graph.

Every maximum matching is maximal, but a maximal matching need not be maximum.

For a bipartite graph \(G=(L\cup R,E)\), the sets \(L\) and \(R\) are disjoint, and every edge joins a vertex in \(L\) to one in \(R\). A matching therefore assigns each selected left-side entity to at most one right-side entity and vice versa.

In the repository-review scenario, reviewers form \(L\), pull requests form \(R\), and an edge represents eligibility to review a request. A matching represents a conflict-free allocation. It does not itself represent a review approval or establish that a reviewer has completed a review.

## Maximal versus maximum matching

Consider a path with vertices \(A,B,C,D\) and edges \(AB,BC,CD\).

The matching \(\{BC\}\) is maximal because both remaining vertices, \(A\) and \(D\), cannot be paired with each other: the edge \(AD\) does not exist. It is not maximum because \(\{AB,CD\}\) is a valid matching of cardinality two.

This distinction matters when a greedy algorithm is used for allocation. A greedy algorithm can produce a valid maximal matching quickly, but its result depends on edge selection order and may contain fewer edges than an optimal solution.

## Augmenting paths

An augmenting path is a path whose edges alternate between edges outside the current matching and edges inside it, with both endpoints unmatched.

Flipping the membership of every edge on an augmenting path increases the matching cardinality by one. An unmatched edge becomes matched, a matched edge becomes unmatched, and all internal vertices remain matched.

The bipartite implementations use depth-first search to find augmenting paths. When a candidate right-side vertex is already assigned, the algorithm attempts to relocate its current owner to another eligible vertex before assigning the contested vertex to the new left-side vertex.

Repeated successful augmentations produce a maximum-cardinality bipartite matching.

## Python implementation

The Python script separates general graph matching from bipartite matching.

`Graph` stores an undirected graph using adjacency sets. It rejects self-loops and provides a matching validator that checks whether every selected edge exists and whether any vertex appears more than once.

`greedy_maximal_matching` accepts edges when both endpoints remain unmatched. Its output is a valid maximal matching, not a guaranteed maximum matching.

`maximum_matching_small_graph` uses recursive backtracking to explore alternatives, including the possibility of leaving a vertex unmatched. It is an exact reference algorithm for small general graphs. Its exponential worst-case running time makes it unsuitable for large arbitrary graphs.

`BipartiteGraph.maximum_matching` uses augmenting paths and returns selected pairs along with unmatched vertices on both sides. The implementation demonstrates why bipartite structure enables a more efficient algorithm than exhaustive search over all general-graph matchings.

The examples cover ordinary matching, the distinction between maximal and maximum, assignment under restricted eligibility, isolated vertices, invalid edges, and self-loop rejection.

## JavaScript implementation

The JavaScript implementation combines bipartite matching with an event-driven allocation service.

`BipartiteMatcher` maintains the two partitions and an adjacency map. Its `maximumMatching` method uses augmenting paths to reassign occupied tasks when an alternative allocation exists. The returned result includes assignments, cardinality, unmatched workers, and unmatched tasks.

`AllocationService` models the lifecycle of an allocation request. It permits allocation only from the `OPEN` state, validates the computed matching, emits an `allocated` event after validation, and permits closure only after successful allocation.

This separation distinguishes the graph algorithm from the service lifecycle. The graph determines a feasible assignment; the service controls when the result is accepted and when the allocation workflow may close.

The implementation also validates partition membership and rejects repeated allocation attempts after closure. It uses Node.js-compatible JavaScript and requires no external packages.

## C++ case study

The C++ program models reviewer assignment for a repository with several open pull requests.

`GovernanceMatchingEngine` stores reviewer identities, pull-request identifiers, and eligibility edges. A reviewer may be eligible for multiple requests, but a valid matching assigns at most one request to each reviewer and at most one reviewer to each request.

The `augment` method searches for a path that can improve the current allocation. `maximumMatching` clears the previous allocation and recomputes the matching from the eligibility graph. The `validate` method independently verifies that every selected pair is an eligible edge and that neither partition contains duplicate assignments.

The case study rejects duplicate vertices, unknown reviewers, and unknown pull requests. It also demonstrates a constrained allocation in which the number of eligible assignments may be smaller than the number of reviewers or requests.

For \(V\) vertices and \(E\) edges, the implemented augmenting-path method has an \(O(VE)\) upper bound for a bipartite graph when each left-side vertex initiates one depth-first search. A more specialized algorithm, such as Hopcroft-Karp, can improve performance for large bipartite graphs.

The engine handles allocation only. A real repository governance service must separately evaluate code ownership, reviewer independence, approval policies, and branch protection requirements.

## Java implementation

The Java program uses domain records to represent `Reviewer`, `PullRequest`, and `Assignment`. `ReviewRole` distinguishes code owners, security reviewers, and general reviewers.

A reviewer record contains repository access information. The `canReview` method checks whether the reviewer has access to the repository associated with a pull request. This makes repository eligibility an explicit constraint rather than an assumption made by the matching algorithm.

`BipartiteMatchingService` stores eligible reviewer-request pairs and maintains a mapping from each assigned request to its current reviewer. Its recursive `augment` method can relocate an existing reviewer when another reviewer needs the same request.

The service checks for duplicate domain objects, unknown requests, unknown reviewers, and missing repository access. It validates the final assignment before returning an immutable list.

Java records and immutable collection copies make the domain objects easier to reason about. The matching service still uses mutable internal state while computing assignments, but it exposes the result as an immutable list.

Review roles provide context for eligibility; they do not automatically implement approval rules. A security reviewer, for example, may be eligible for a request without having completed a security review or issued an approval.

## SQL data model

The PostgreSQL script represents the bipartite graph using relational tables.

| Table | Purpose |
|---|---|
| `repositories` | Stores repository identities. |
| `reviewers` | Stores reviewer identities, roles, and active status. |
| `pull_requests` | Stores requests, repository relationships, target branches, and lifecycle states. |
| `reviewer_eligibility` | Stores graph edges connecting eligible reviewers and requests. |
| `review_assignments` | Stores a selected allocation. |

The composite primary key on `reviewer_eligibility` prevents duplicate eligibility edges. Foreign keys enforce valid references to reviewers and pull requests. The primary key on `review_assignments.pull_request_id` ensures that a pull request has at most one assigned reviewer in the selected allocation. Its uniqueness and foreign-key constraints support relational integrity.

The candidate view joins the eligibility edges with active reviewers and open requests. It exposes possible reviewer-request pairs without claiming that every pair can be selected simultaneously.

The allocation query deliberately illustrates the limitations of a simple greedy strategy. It selects the lowest reviewer identifier for each request and then removes repeated reviewer assignments. The resulting set is a feasible partial matching, but it is not guaranteed to have maximum cardinality.

This is an important algorithmic boundary: relational constraints can enforce uniqueness and valid references, but they do not independently prove that no larger matching exists. An exact matching service must run an appropriate graph algorithm and persist the resulting pairs within a transaction when concurrent allocation requests are possible.

The SQL script uses indexes for eligibility lookups by request and for filtering open requests. Its transaction ends with `ROLLBACK`, making the script suitable for a repeatable demonstration without leaving sample records in the database.

## Algorithm comparison

| Approach | Graph type | Main purpose | Complexity |
|---|---|---|---|
| Greedy edge selection | General graph | Quickly construct a maximal matching | \(O(E)\) after edge enumeration |
| Recursive backtracking | General graph | Find an exact maximum matching for small graphs | Exponential in the worst case |
| Augmenting-path DFS | Bipartite graph | Find a maximum-cardinality matching | \(O(VE)\) |
| Hopcroft-Karp | Bipartite graph | Scale maximum matching to larger graphs | \(O(E\sqrt{V})\) |

The complexities assume standard adjacency-list representations, with implementation-specific costs for edge enumeration and validation. The recursive general-graph implementation is educational rather than production-scale. General graphs with odd cycles require algorithms that account for blossoms to achieve efficient maximum matching; the bipartite augmenting-path implementation does not solve that general problem.

## Practical applications

Graph matching is useful when assignments must satisfy one-to-one constraints while respecting eligibility.

- **Code review allocation:** Match reviewers to pull requests based on repository access, expertise, and workload constraints.
- **Incident response:** Match qualified responders to incidents when each responder can own at most one active incident in a given allocation round.
- **Job assignment:** Match workers to tasks when eligibility is represented by edges.
- **Resource allocation:** Match equipment operators to compatible machines when both sides have limited assignment capacity.
- **Academic examination scheduling:** Match qualified examiners to projects when each examiner and project can participate in at most one assignment in a particular matching.

These examples share the same mathematical structure, but the domain-specific eligibility rules must be modeled separately. If assignments have different costs or priorities, maximum cardinality alone may not be the right objective. Weighted matching or min-cost flow may be more appropriate.

## Limitations and production considerations

The implementations assume unweighted edges and one-to-one assignments. They do not optimize reviewer workload across multiple time periods, account for review duration, or enforce independence between reviewers and authors.

A maximum-cardinality matching maximizes the number of assignments, not necessarily their quality or total utility. In production systems, eligibility edges should be generated from authoritative access and policy data, and assignments should be revalidated when that data changes.

Concurrent allocation requests require transaction boundaries or equivalent coordination to prevent multiple services from independently assigning the same resource. The database constraints in the SQL example protect important uniqueness properties, but a production workflow must also address transaction isolation, stale eligibility data, audit history, retries, and assignment revocation.

The matching result should be treated as a proposed allocation. Repository merge eligibility, review completion, required approvals, and protected-branch rules remain independent governance decisions.
