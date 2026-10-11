#!/usr/bin/env python3
"""
Graph Theory Fundamentals
=========================

A self-contained practical implementation of graph theory fundamentals.

Topics:
- Vertices and edges
- Directed and undirected graphs
- Weighted and unweighted edges
- Adjacency lists, adjacency matrices, and edge lists
- Vertex and edge validation
- Neighbors, degrees, isolated vertices, and self-loops
- Breadth-first and depth-first traversal
- Reachability, connected components, and cycle detection
- Representation conversion and storage complexity
- Practical network analysis and executable assertions

Run with:
    python graph_fundamentals.py
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import inf
from typing import Hashable, Iterable, Iterator, Optional

Vertex = Hashable


@dataclass(frozen=True)
class Edge:
    """An edge records its endpoints and optional numerical weight."""

    source: Vertex
    target: Vertex
    weight: float = 1.0


class Graph:
    """
    Graph supporting directed or undirected edges.

    The adjacency dictionary preserves vertices with no neighbors.
    The adjacency list stores outgoing edges for directed graphs and
    incident edges for undirected graphs.
    """

    def __init__(
        self,
        directed: bool = False,
        weighted: bool = False,
    ) -> None:
        self.directed = directed
        self.weighted = weighted
        self._adjacency: dict[Vertex, dict[Vertex, float]] = {}
        self._edge_count = 0

    @property
    def vertex_count(self) -> int:
        return len(self._adjacency)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    @property
    def vertices(self) -> tuple[Vertex, ...]:
        return tuple(self._adjacency)

    def add_vertex(self, vertex: Vertex) -> None:
        """Add an isolated vertex without removing existing information."""
        try:
            hash(vertex)
        except TypeError as exc:
            raise TypeError("Vertices must be hashable.") from exc

        self._adjacency.setdefault(vertex, {})

    def _require_vertex(self, vertex: Vertex) -> None:
        if vertex not in self._adjacency:
            raise KeyError(f"Unknown vertex: {vertex!r}")

    def add_edge(
        self,
        source: Vertex,
        target: Vertex,
        weight: float = 1.0,
    ) -> None:
        """
        Insert an edge, replacing its weight if the same edge exists.

        An undirected edge is stored in both adjacency directions, but
        counted once. A self-loop is also counted once.
        """
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise TypeError("Edge weight must be a real number.")

        from math import isfinite

        if not isfinite(weight):
            raise ValueError("Edge weight must be finite.")

        self.add_vertex(source)
        self.add_vertex(target)

        existed = target in self._adjacency[source]

        if existed:
            self._adjacency[source][target] = float(weight)
            if not self.directed and source != target:
                self._adjacency[target][source] = float(weight)
            return

        self._adjacency[source][target] = float(weight)

        if not self.directed and source != target:
            self._adjacency[target][source] = float(weight)

        self._edge_count += 1

    def remove_edge(self, source: Vertex, target: Vertex) -> bool:
        """Remove an existing edge and return whether it was present."""
        self._require_vertex(source)
        self._require_vertex(target)

        if target not in self._adjacency[source]:
            return False

        del self._adjacency[source][target]

        if not self.directed and source != target:
            del self._adjacency[target][source]

        self._edge_count -= 1
        return True

    def neighbors(self, vertex: Vertex) -> tuple[Vertex, ...]:
        self._require_vertex(vertex)
        return tuple(self._adjacency[vertex])

    def has_edge(self, source: Vertex, target: Vertex) -> bool:
        self._require_vertex(source)
        self._require_vertex(target)
        return target in self._adjacency[source]

    def edge_weight(self, source: Vertex, target: Vertex) -> float:
        self._require_vertex(source)
        self._require_vertex(target)
        return self._adjacency[source][target]

    def edges(self) -> list[Edge]:
        """Return each logical edge exactly once."""
        result: list[Edge] = []

        for source, neighbors in self._adjacency.items():
            for target, weight in neighbors.items():
                if self.directed:
                    result.append(Edge(source, target, weight))
                elif list(self._adjacency).index(source) <= list(
                    self._adjacency
                ).index(target):
                    result.append(Edge(source, target, weight))

        return result

    def degree(self, vertex: Vertex) -> int:
        """Return total degree for undirected graphs."""
        self._require_vertex(vertex)

        if self.directed:
            raise ValueError(
                "Use in_degree() or out_degree() for directed graphs."
            )

        # A self-loop contributes two to the degree of an undirected vertex.
        neighbors = self._adjacency[vertex]
        return sum(2 if neighbor == vertex else 1 for neighbor in neighbors)

    def out_degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)
        return len(self._adjacency[vertex])

    def in_degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)

        if not self.directed:
            raise ValueError("In-degree is defined here for directed graphs.")

        return sum(
            1
            for neighbors in self._adjacency.values()
            if vertex in neighbors
        )

    def adjacency_list(self) -> dict[Vertex, dict[Vertex, float]]:
        """Return a copy so callers cannot mutate the graph accidentally."""
        return {
            vertex: dict(neighbors)
            for vertex, neighbors in self._adjacency.items()
        }

    def edge_list(self) -> list[tuple[Vertex, Vertex, float]]:
        return [
            (edge.source, edge.target, edge.weight)
            for edge in self.edges()
        ]

    def adjacency_matrix(
        self,
    ) -> tuple[list[Vertex], list[list[Optional[float]]]]:
        """
        Build a matrix using None for absent edges.

        Zero is a valid edge weight, so zero cannot safely mean
        'no edge' in a weighted graph.
        """
        vertices = list(self._adjacency)
        index = {vertex: i for i, vertex in enumerate(vertices)}
        size = len(vertices)

        matrix: list[list[Optional[float]]] = [
            [None] * size for _ in range(size)
        ]

        for source, neighbors in self._adjacency.items():
            for target, weight in neighbors.items():
                matrix[index[source]][index[target]] = weight

        return vertices, matrix

    @classmethod
    def from_edge_list(
        cls,
        edges: Iterable[tuple[Vertex, Vertex, float]],
        vertices: Iterable[Vertex] = (),
        directed: bool = False,
        weighted: bool = False,
    ) -> Graph:
        graph = cls(directed=directed, weighted=weighted)

        for vertex in vertices:
            graph.add_vertex(vertex)

        for source, target, weight in edges:
            graph.add_edge(source, target, weight)

        return graph

    def breadth_first_search(self, start: Vertex) -> list[Vertex]:
        """
        Visit reachable vertices in layers.

        With an adjacency list, the traversal costs O(V + E) over the
        explored component.
        """
        self._require_vertex(start)
        visited = {start}
        queue = deque([start])
        order: list[Vertex] = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in self._adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def depth_first_search(self, start: Vertex) -> list[Vertex]:
        """Iterative DFS avoids recursion-depth limits on large graphs."""
        self._require_vertex(start)
        visited: set[Vertex] = set()
        stack = [start]
        order: list[Vertex] = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            # Reverse insertion order to make output predictable.
            stack.extend(
                neighbor
                for neighbor in reversed(tuple(self._adjacency[current]))
                if neighbor not in visited
            )

        return order

    def reachable(self, source: Vertex, target: Vertex) -> bool:
        self._require_vertex(source)
        self._require_vertex(target)

        if source == target:
            return True

        return target in self.breadth_first_search(source)

    def connected_components(self) -> list[set[Vertex]]:
        """
        Return connected components of an undirected graph.

        For directed graphs, callers should choose a directed connectivity
        definition such as weak or strong connectivity explicitly.
        """
        if self.directed:
            raise ValueError(
                "Connected components require an undirected graph."
            )

        unseen = set(self._adjacency)
        components: list[set[Vertex]] = []

        while unseen:
            start = next(iter(unseen))
            component = set(self.breadth_first_search(start))
            components.append(component)
            unseen.difference_update(component)

        return components

    def has_undirected_cycle(self) -> bool:
        """Detect cycles in an undirected graph using DFS parent tracking."""
        if self.directed:
            raise ValueError("This cycle detector requires an undirected graph.")

        visited: set[Vertex] = set()

        for start in self._adjacency:
            if start in visited:
                continue

            stack: list[tuple[Vertex, Optional[Vertex]]] = [(start, None)]

            while stack:
                vertex, parent = stack.pop()

                if vertex in visited:
                    continue

                visited.add(vertex)

                for neighbor in self._adjacency[vertex]:
                    if neighbor == vertex:
                        return True

                    if neighbor not in visited:
                        stack.append((neighbor, vertex))
                    elif neighbor != parent:
                        return True

        return False

    def shortest_unweighted_path(
        self,
        source: Vertex,
        target: Vertex,
    ) -> Optional[list[Vertex]]:
        """
        Return a minimum-edge path using BFS.

        Edge weights are deliberately ignored. For weighted shortest paths,
        use Dijkstra's algorithm with nonnegative weights or another
        algorithm suitable for the weight domain.
        """
        self._require_vertex(source)
        self._require_vertex(target)

        parent: dict[Vertex, Optional[Vertex]] = {source: None}
        queue = deque([source])

        while queue:
            current = queue.popleft()

            if current == target:
                break

            for neighbor in self._adjacency[current]:
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

        if target not in parent:
            return None

        path: list[Vertex] = []
        current: Optional[Vertex] = target

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        return path

    def describe(self) -> None:
        graph_type = "directed" if self.directed else "undirected"
        weight_type = "weighted" if self.weighted else "unweighted"

        print(
            f"{graph_type.title()} {weight_type} graph: "
            f"{self.vertex_count} vertices, {self.edge_count} edges"
        )

        for vertex, neighbors in self._adjacency.items():
            if self.weighted:
                details = ", ".join(
                    f"{neighbor!r} (weight={weight:g})"
                    for neighbor, weight in neighbors.items()
                )
            else:
                details = ", ".join(repr(n) for n in neighbors)

            print(f"  {vertex!r}: [{details}]")


def demonstrate_representations() -> None:
    print("\n=== Graph representations ===")

    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "D", 3),
        ("C", "D", 1),
    ]

    graph = Graph.from_edge_list(
        edges,
        vertices=["A", "B", "C", "D", "E"],
        directed=False,
        weighted=True,
    )

    graph.describe()
    print("Edge list:", graph.edge_list())

    vertices, matrix = graph.adjacency_matrix()
    print("Matrix vertex order:", vertices)

    for row in matrix:
        print(row)

    print("Isolated vertex E:", graph.neighbors("E"))


def demonstrate_traversal() -> None:
    print("\n=== Traversal and connectivity ===")

    graph = Graph()
    graph.add_edge("Router", "Switch")
    graph.add_edge("Switch", "Server")
    graph.add_edge("Switch", "Printer")
    graph.add_vertex("Disconnected workstation")

    print("BFS from Router:", graph.breadth_first_search("Router"))
    print("DFS from Router:", graph.depth_first_search("Router"))
    print(
        "Router can reach Server:",
        graph.reachable("Router", "Server"),
    )
    print("Shortest path:", graph.shortest_unweighted_path("Router", "Server"))
    print("Connected components:", graph.connected_components())
    print("Contains cycle:", graph.has_undirected_cycle())


def demonstrate_directed_graph() -> None:
    print("\n=== Directed dependency graph ===")

    graph = Graph(directed=True)
    graph.add_edge("Design", "Implementation")
    graph.add_edge("Implementation", "Testing")
    graph.add_edge("Testing", "Deployment")
    graph.add_edge("Design", "Documentation")

    graph.describe()

    for vertex in graph.vertices:
        print(
            f"{vertex}: in-degree={graph.in_degree(vertex)}, "
            f"out-degree={graph.out_degree(vertex)}"
        )

    print(
        "Design can reach Deployment:",
        graph.reachable("Design", "Deployment"),
    )
    print(
        "Deployment can reach Design:",
        graph.reachable("Deployment", "Design"),
    )


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases and validation ===")

    graph = Graph()
    graph.add_vertex("Standalone")
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")

    # Re-inserting an edge does not increase the logical edge count.
    assert graph.edge_count == 1

    # Removing an absent edge is safe and leaves the graph unchanged.
    assert graph.remove_edge("A", "Standalone") is False
    assert graph.remove_edge("A", "B") is True
    assert graph.edge_count == 0

    loop_graph = Graph()
    loop_graph.add_edge("A", "A")
    assert loop_graph.has_undirected_cycle()
    assert loop_graph.degree("A") == 2

    zero_weight_graph = Graph(weighted=True)
    zero_weight_graph.add_edge("A", "B", 0)
    _, matrix = zero_weight_graph.adjacency_matrix()
    assert matrix[0][1] == 0

    try:
        graph.add_edge("A", "B", inf)
    except ValueError as exc:
        print("Rejected infinite weight:", exc)

    try:
        graph.breadth_first_search("Missing")
    except KeyError as exc:
        print("Rejected unknown start vertex:", exc)

    print("Edge cases passed.")


def demonstrate_storage_tradeoffs() -> None:
    print("\n=== Representation trade-offs ===")

    graph = Graph(directed=True)
    for vertex in range(6):
        graph.add_vertex(vertex)

    graph.add_edge(0, 1)
    graph.add_edge(0, 2)
    graph.add_edge(3, 4)

    vertices, matrix = graph.adjacency_matrix()
    vertex_count = len(vertices)
    edge_count = graph.edge_count

    print(f"Vertices: {vertex_count}")
    print(f"Directed edges: {edge_count}")
    print(f"Adjacency matrix cells: {vertex_count * vertex_count}")
    print(f"Adjacency-list neighbor entries: {edge_count}")

    # A directed adjacency list uses O(V + E) space; a matrix uses O(V^2).
    # A matrix is useful for dense graphs and constant-time edge lookup.


def run_assertions() -> None:
    undirected = Graph()
    undirected.add_edge("A", "B")
    undirected.add_edge("B", "C")

    assert undirected.vertex_count == 3
    assert undirected.edge_count == 2
    assert undirected.degree("B") == 2
    assert undirected.reachable("A", "C")
    assert undirected.shortest_unweighted_path("A", "C") == ["A", "B", "C"]

    directed = Graph(directed=True)
    directed.add_edge("A", "B")
    directed.add_edge("B", "C")

    assert directed.out_degree("A") == 1
    assert directed.in_degree("C") == 1
    assert directed.reachable("A", "C")
    assert not directed.reachable("C", "A")

    components = Graph()
    components.add_edge(1, 2)
    components.add_vertex(3)
    assert len(components.connected_components()) == 2

    print("\nAll graph fundamentals assertions passed.")


def main() -> None:
    demonstrate_representations()
    demonstrate_traversal()
    demonstrate_directed_graph()
    demonstrate_edge_cases()
    demonstrate_storage_tradeoffs()
    run_assertions()


if __name__ == "__main__":
    main()
