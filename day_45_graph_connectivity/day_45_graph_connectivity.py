#!/usr/bin/env python3
"""
Graph Connectivity: bridges, articulation points, connectivity, and SCCs.

A self-contained graph-analysis laboratory using only the Python standard
library. The undirected algorithms use Tarjan's low-link technique, while
strongly connected components are computed with Tarjan's directed algorithm.

Run:
    python graph_connectivity.py

The implementations are iterative where graph depth could otherwise exceed
Python's recursion limit. Their adjacency representations support parallel
edges and isolated vertices.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Hashable, Iterable, Optional

Vertex = Hashable
Edge = tuple[Vertex, Vertex]


class GraphError(ValueError):
    """Raised when a graph operation receives invalid input."""


class UndirectedGraph:
    """Undirected multigraph with explicit vertices and edge identities."""

    def __init__(self) -> None:
        self.adjacency: DefaultDict[Vertex, list[tuple[Vertex, int]]] = (
            defaultdict(list)
        )
        self.edges: list[Edge] = []

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable.") from exc
        self.adjacency[vertex]

    def add_edge(self, left: Vertex, right: Vertex) -> int:
        self.add_vertex(left)
        self.add_vertex(right)
        edge_id = len(self.edges)
        self.edges.append((left, right))
        self.adjacency[left].append((right, edge_id))
        self.adjacency[right].append((left, edge_id))
        return edge_id

    @property
    def vertex_count(self) -> int:
        return len(self.adjacency)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def connected_components(
        self, excluded_vertex: Optional[Vertex] = None
    ) -> list[set[Vertex]]:
        """Return connected components, optionally removing one vertex."""
        if excluded_vertex is not None and excluded_vertex not in self.adjacency:
            raise GraphError(f"Unknown vertex: {excluded_vertex!r}")

        visited: set[Vertex] = set()
        components: list[set[Vertex]] = []

        for start in self.adjacency:
            if start == excluded_vertex or start in visited:
                continue

            component: set[Vertex] = set()
            queue = deque([start])
            visited.add(start)

            while queue:
                current = queue.popleft()
                component.add(current)

                for neighbor, _ in self.adjacency[current]:
                    if neighbor == excluded_vertex or neighbor in visited:
                        continue
                    visited.add(neighbor)
                    queue.append(neighbor)

            components.append(component)

        return components

    def bridges_and_articulation_points(
        self,
    ) -> tuple[list[tuple[Vertex, Vertex]], set[Vertex]]:
        """
        Find bridges and articulation points in O(V + E) time.

        discovery[v] is the DFS discovery time of v.
        low[v] is the earliest discovery time reachable from v's DFS subtree
        using tree edges and at most one back edge.

        An edge (parent, child) is a bridge if low[child] > discovery[parent].
        A non-root parent is an articulation point if
        low[child] >= discovery[parent] for any DFS child.
        A DFS root is an articulation point only if it has at least two
        DFS-tree children.

        Edge IDs are essential: skipping the parent vertex alone would
        incorrectly handle parallel edges.
        """
        discovery: dict[Vertex, int] = {}
        low: dict[Vertex, int] = {}
        parent: dict[Vertex, Optional[Vertex]] = {}
        parent_edge: dict[Vertex, Optional[int]] = {}
        child_count: DefaultDict[Vertex, int] = defaultdict(int)

        bridges: list[tuple[Vertex, Vertex]] = []
        articulation: set[Vertex] = set()
        clock = 0

        for root in self.adjacency:
            if root in discovery:
                continue

            parent[root] = None
            parent_edge[root] = None
            discovery[root] = low[root] = clock
            clock += 1

            # Each frame stores a vertex and the next adjacency index.
            stack: list[tuple[Vertex, int]] = [(root, 0)]

            while stack:
                vertex, index = stack[-1]
                neighbors = self.adjacency[vertex]

                if index < len(neighbors):
                    neighbor, edge_id = neighbors[index]
                    stack[-1] = (vertex, index + 1)

                    if edge_id == parent_edge[vertex]:
                        continue

                    if neighbor not in discovery:
                        parent[neighbor] = vertex
                        parent_edge[neighbor] = edge_id
                        child_count[vertex] += 1
                        discovery[neighbor] = low[neighbor] = clock
                        clock += 1
                        stack.append((neighbor, 0))
                    else:
                        # An already discovered ancestor can lower low[v].
                        # The min operation is harmless for a descendant.
                        low[vertex] = min(low[vertex], discovery[neighbor])

                else:
                    stack.pop()
                    ancestor = parent[vertex]

                    if ancestor is None:
                        if child_count[vertex] > 1:
                            articulation.add(vertex)
                        continue

                    low[ancestor] = min(low[ancestor], low[vertex])

                    if low[vertex] > discovery[ancestor]:
                        bridges.append((ancestor, vertex))

                    if parent[ancestor] is not None and (
                        low[vertex] >= discovery[ancestor]
                    ):
                        articulation.add(ancestor)

        return bridges, articulation

    def is_connected(self) -> bool:
        """Connectivity convention: the empty graph is not connected."""
        if not self.adjacency:
            return False
        return len(self.connected_components()) == 1

    def edge_connectivity_failures(self) -> list[Edge]:
        """Return edge identities whose individual removal disconnects
        an originally connected graph."""
        if not self.is_connected():
            raise GraphError(
                "Single-edge failure analysis requires a connected graph."
            )

        bridges, _ = self.bridges_and_articulation_points()
        result: list[Edge] = []

        for bridge_left, bridge_right in bridges:
            # Match by endpoints, then preserve parallel-edge identities.
            for left, right in self.edges:
                if (
                    (left == bridge_left and right == bridge_right)
                    or (left == bridge_right and right == bridge_left)
                ):
                    result.append((left, right))
                    break

        return result


class DirectedGraph:
    """Directed graph for strongly connected component analysis."""

    def __init__(self) -> None:
        self.adjacency: DefaultDict[Vertex, list[Vertex]] = defaultdict(list)

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable.") from exc
        self.adjacency[vertex]

    def add_edge(self, source: Vertex, target: Vertex) -> None:
        self.add_vertex(source)
        self.add_vertex(target)
        self.adjacency[source].append(target)

    def strongly_connected_components(self) -> list[set[Vertex]]:
        """
        Tarjan's SCC algorithm in O(V + E).

        index[v] is the discovery index; low[v] tracks the earliest active
        ancestor reachable through tree edges and edges into the active stack.
        Unlike the undirected low-link algorithm, an edge to an already
        completed SCC must not influence low[v].
        """
        index: dict[Vertex, int] = {}
        low: dict[Vertex, int] = {}
        active_stack: list[Vertex] = []
        on_stack: set[Vertex] = set()
        components: list[set[Vertex]] = []
        clock = 0

        # Iterative frames retain the next outgoing-edge index and emulate
        # recursive postorder without depending on Python's recursion limit.
        for root in self.adjacency:
            if root in index:
                continue

            index[root] = low[root] = clock
            clock += 1
            active_stack.append(root)
            on_stack.add(root)
            frames: list[tuple[Vertex, int]] = [(root, 0)]

            while frames:
                vertex, edge_index = frames[-1]
                outgoing = self.adjacency[vertex]

                if edge_index < len(outgoing):
                    neighbor = outgoing[edge_index]
                    frames[-1] = (vertex, edge_index + 1)

                    if neighbor not in index:
                        index[neighbor] = low[neighbor] = clock
                        clock += 1
                        active_stack.append(neighbor)
                        on_stack.add(neighbor)
                        frames.append((neighbor, 0))
                    elif neighbor in on_stack:
                        low[vertex] = min(low[vertex], index[neighbor])

                else:
                    frames.pop()

                    if frames:
                        parent_vertex = frames[-1][0]
                        low[parent_vertex] = min(
                            low[parent_vertex], low[vertex]
                        )

                    if low[vertex] == index[vertex]:
                        component: set[Vertex] = set()
                        while True:
                            member = active_stack.pop()
                            on_stack.remove(member)
                            component.add(member)
                            if member == vertex:
                                break
                        components.append(component)

        return components

    def condensation_graph(self) -> tuple[list[set[Vertex]], set[tuple[int, int]]]:
        """Collapse each SCC into a DAG node and discard internal edges."""
        components = self.strongly_connected_components()
        owner: dict[Vertex, int] = {}

        for component_id, component in enumerate(components):
            for vertex in component:
                owner[vertex] = component_id

        condensation_edges: set[tuple[int, int]] = set()
        for source, outgoing in self.adjacency.items():
            for target in outgoing:
                left, right = owner[source], owner[target]
                if left != right:
                    condensation_edges.add((left, right))

        return components, condensation_edges


@dataclass(frozen=True)
class NetworkReport:
    """Compact analysis result for an undirected infrastructure network."""

    connected: bool
    component_count: int
    bridges: tuple[Edge, ...]
    articulation_points: frozenset[Vertex]


def analyze_network(graph: UndirectedGraph) -> NetworkReport:
    bridges, articulation = graph.bridges_and_articulation_points()
    return NetworkReport(
        connected=graph.is_connected(),
        component_count=len(graph.connected_components()),
        bridges=tuple(bridges),
        articulation_points=frozenset(articulation),
    )


def demonstrate_undirected_network() -> None:
    print("\n=== Undirected infrastructure network ===")
    graph = UndirectedGraph()

    # A-B-C forms a vulnerable backbone. C-D-E-F-C is a redundant ring.
    # G is an isolated site and must count as its own component.
    for site in "ABCDEFG":
        graph.add_vertex(site)

    for left, right in [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "F"),
        ("F", "C"),
    ]:
        graph.add_edge(left, right)

    report = analyze_network(graph)
    print(f"Sites: {graph.vertex_count}; links: {graph.edge_count}")
    print(f"Connected: {report.connected}")
    print(f"Connected components: {report.component_count}")
    print(f"Bridges: {list(report.bridges)}")
    print(f"Articulation points: {sorted(report.articulation_points)}")

    print("Components after removing C:")
    for component in graph.connected_components(excluded_vertex="C"):
        print(f"  {sorted(component)}")


def demonstrate_parallel_edges() -> None:
    print("\n=== Parallel-link edge case ===")
    graph = UndirectedGraph()
    graph.add_edge("gateway", "switch")
    graph.add_edge("gateway", "switch")
    graph.add_edge("switch", "server")

    bridges, articulation = graph.bridges_and_articulation_points()
    print(f"Bridges: {bridges}")
    print(f"Articulation points: {sorted(articulation)}")
    assert bridges == [("switch", "server")]


def demonstrate_directed_services() -> None:
    print("\n=== Directed service dependency graph ===")
    graph = DirectedGraph()

    for service in [
        "api",
        "auth",
        "billing",
        "ledger",
        "queue",
        "worker",
        "reporting",
    ]:
        graph.add_vertex(service)

    for source, target in [
        ("api", "auth"),
        ("auth", "billing"),
        ("billing", "ledger"),
        ("ledger", "billing"),
        ("api", "queue"),
        ("queue", "worker"),
        ("worker", "queue"),
        ("worker", "reporting"),
    ]:
        graph.add_edge(source, target)

    components, condensation_edges = graph.condensation_graph()

    for component_id, component in enumerate(components):
        print(f"SCC {component_id}: {sorted(component)}")

    print("Condensation DAG edges:")
    for source, target in sorted(condensation_edges):
        print(f"  SCC {source} -> SCC {target}")


def verify_against_brute_force() -> None:
    """
    Cross-check low-link results against deletion-based definitions.

    This test uses a small graph. Recomputing components after every deletion
    is slower than the production algorithm but gives an independent oracle.
    """
    graph = UndirectedGraph()

    for vertex in range(6):
        graph.add_vertex(vertex)

    for left, right in [
        (0, 1),
        (1, 2),
        (2, 0),
        (2, 3),
        (3, 4),
        (4, 5),
        (3, 5),
    ]:
        graph.add_edge(left, right)

    original_count = len(graph.connected_components())
    _, articulation = graph.bridges_and_articulation_points()

    expected_articulation = {
        vertex
        for vertex in graph.adjacency
        if len(graph.connected_components(vertex)) > original_count
    }
    assert articulation == expected_articulation

    expected_bridges: set[int] = set()
    for edge_id in range(graph.edge_count):
        reduced = UndirectedGraph()
        for vertex in graph.adjacency:
            reduced.add_vertex(vertex)

        for candidate_id, (left, right) in enumerate(graph.edges):
            if candidate_id != edge_id:
                reduced.add_edge(left, right)

        if len(reduced.connected_components()) > original_count:
            expected_bridges.add(edge_id)

    discovered_bridges, _ = graph.bridges_and_articulation_points()
    discovered_endpoint_pairs = {
        frozenset(edge) for edge in discovered_bridges
    }
    expected_endpoint_pairs = {
        frozenset(graph.edges[edge_id]) for edge_id in expected_bridges
    }

    assert discovered_endpoint_pairs == expected_endpoint_pairs
    print("\nIndependent deletion-based checks passed.")


def demonstrate_deep_graph() -> None:
    """Exercise iterative DFS on a long path without recursive stack growth."""
    vertex_count = 10_000
    graph = UndirectedGraph()

    for vertex in range(vertex_count):
        graph.add_vertex(vertex)

    for vertex in range(vertex_count - 1):
        graph.add_edge(vertex, vertex + 1)

    bridges, articulation = graph.bridges_and_articulation_points()
    assert len(bridges) == vertex_count - 1
    assert len(articulation) == vertex_count - 2
    print(
        f"\nDeep path with {vertex_count} vertices: "
        f"{len(bridges)} bridges, {len(articulation)} articulation points."
    )


def main() -> None:
    demonstrate_undirected_network()
    demonstrate_parallel_edges()
    demonstrate_directed_services()
    verify_against_brute_force()
    demonstrate_deep_graph()


if __name__ == "__main__":
    main()
