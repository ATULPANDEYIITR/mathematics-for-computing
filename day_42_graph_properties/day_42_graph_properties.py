#!/usr/bin/env python3
"""Executable study of graph properties using only the Python standard library.

The implementation covers vertex degree, walks, paths, cycles, connectedness,
connected components, graph validation, traversal algorithms, and structural
properties of undirected and directed graphs.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class GraphStatistics:
    vertices: int
    edges: int
    components: int
    connected: bool
    minimum_degree: int
    maximum_degree: int
    average_degree: float
    cycle_exists: bool


class Graph:
    """Simple graph supporting directed and undirected edges."""

    def __init__(
        self,
        vertices: Iterable[str] = (),
        directed: bool = False,
    ) -> None:
        self.directed = directed
        self.adjacency: dict[str, set[str]] = {}
        for vertex in vertices:
            self.add_vertex(vertex)

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex names must be nonempty strings.")
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, source: str, target: str) -> None:
        self.add_vertex(source)
        self.add_vertex(target)
        self.adjacency[source].add(target)
        if not self.directed:
            self.adjacency[target].add(source)

    def remove_edge(self, source: str, target: str) -> None:
        if source not in self.adjacency or target not in self.adjacency:
            raise KeyError("Both endpoints must exist.")
        self.adjacency[source].remove(target)
        if not self.directed:
            self.adjacency[target].remove(source)

    def vertices(self) -> list[str]:
        return sorted(self.adjacency)

    def neighbors(self, vertex: str) -> tuple[str, ...]:
        self._require_vertex(vertex)
        return tuple(sorted(self.adjacency[vertex]))

    def _require_vertex(self, vertex: str) -> None:
        if vertex not in self.adjacency:
            raise KeyError(f"Unknown vertex: {vertex}")

    def edges(self) -> list[tuple[str, str]]:
        result = []
        for source in sorted(self.adjacency):
            for target in sorted(self.adjacency[source]):
                if self.directed or source <= target:
                    result.append((source, target))
        return result

    def degree(self, vertex: str) -> int:
        """Degree counts incident edges; a self-loop contributes two."""
        self._require_vertex(vertex)
        if self.directed:
            raise ValueError("Use in_degree() or out_degree() for directed graphs.")
        total = len(self.adjacency[vertex])
        if vertex in self.adjacency[vertex]:
            total += 1
        return total

    def out_degree(self, vertex: str) -> int:
        self._require_vertex(vertex)
        if not self.directed:
            raise ValueError("out_degree() is intended for directed graphs.")
        return len(self.adjacency[vertex])

    def in_degree(self, vertex: str) -> int:
        self._require_vertex(vertex)
        if not self.directed:
            raise ValueError("in_degree() is intended for directed graphs.")
        return sum(vertex in targets for targets in self.adjacency.values())

    def degree_sequence(self) -> list[tuple[str, int]]:
        if self.directed:
            raise ValueError("Degree sequence here is defined for undirected graphs.")
        return sorted(
            ((vertex, self.degree(vertex)) for vertex in self.adjacency),
            key=lambda item: (-item[1], item[0]),
        )

    def breadth_first_search(self, start: str) -> list[str]:
        self._require_vertex(start)
        visited = {start}
        queue = deque([start])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def depth_first_search(self, start: str) -> list[str]:
        self._require_vertex(start)
        visited = set()
        order = []
        stack = [start]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            order.append(current)
            # Reverse insertion makes the resulting traversal deterministic.
            stack.extend(
                neighbor
                for neighbor in reversed(self.neighbors(current))
                if neighbor not in visited
            )
        return order

    def connected_components(self) -> list[set[str]]:
        """Connected components use ordinary connectivity for undirected graphs.

        For directed graphs, this method computes weakly connected components
        by treating each directed edge as an undirected relationship.
        """
        undirected_neighbors = {v: set() for v in self.adjacency}
        for source, targets in self.adjacency.items():
            for target in targets:
                undirected_neighbors[source].add(target)
                undirected_neighbors[target].add(source)

        unseen = set(self.adjacency)
        components = []

        while unseen:
            start = min(unseen)
            component = set()
            queue = deque([start])
            unseen.remove(start)

            while queue:
                current = queue.popleft()
                component.add(current)
                for neighbor in sorted(undirected_neighbors[current]):
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        queue.append(neighbor)
            components.append(component)

        return sorted(components, key=lambda component: min(component))

    def is_connected(self) -> bool:
        if not self.adjacency:
            # The empty graph is treated as not connected in this program.
            return False
        return len(self.connected_components()) == 1

    def has_cycle(self) -> bool:
        """Detect cycles in an undirected graph using DFS and parent tracking.

        A self-loop is a cycle. In directed graphs, use has_directed_cycle().
        """
        if self.directed:
            raise ValueError("Use has_directed_cycle() for directed graphs.")

        visited = set()

        for start in self.adjacency:
            if start in visited:
                continue

            stack = [(start, None)]
            while stack:
                current, parent = stack.pop()
                if current in visited:
                    continue
                visited.add(current)

                for neighbor in self.adjacency[current]:
                    if neighbor == current:
                        return True
                    if neighbor not in visited:
                        stack.append((neighbor, current))
                    elif neighbor != parent:
                        return True
        return False

    def has_directed_cycle(self) -> bool:
        """Detect directed cycles using three-color DFS state."""
        if not self.directed:
            raise ValueError("This method requires a directed graph.")

        # WHITE: unvisited; GRAY: active DFS path; BLACK: fully processed.
        state = {vertex: 0 for vertex in self.adjacency}

        def visit(vertex: str) -> bool:
            state[vertex] = 1
            for neighbor in self.adjacency[vertex]:
                if state[neighbor] == 1:
                    return True
                if state[neighbor] == 0 and visit(neighbor):
                    return True
            state[vertex] = 2
            return False

        return any(
            state[vertex] == 0 and visit(vertex)
            for vertex in self.adjacency
        )

    def is_walk(self, sequence: Iterable[str]) -> bool:
        """A walk permits repeated vertices and repeated edges."""
        vertices = list(sequence)
        if not vertices:
            return False
        if any(vertex not in self.adjacency for vertex in vertices):
            return False
        return all(
            target in self.adjacency[source]
            for source, target in zip(vertices, vertices[1:])
        )

    def is_trail(self, sequence: Iterable[str]) -> bool:
        """A trail is a walk that does not repeat an edge."""
        vertices = list(sequence)
        if not self.is_walk(vertices):
            return False

        used_edges = set()
        for source, target in zip(vertices, vertices[1:]):
            edge = (source, target) if self.directed else tuple(
                sorted((source, target))
            )
            if edge in used_edges:
                return False
            used_edges.add(edge)
        return True

    def is_simple_path(self, sequence: Iterable[str]) -> bool:
        """A simple path does not repeat any vertex."""
        vertices = list(sequence)
        return self.is_walk(vertices) and len(vertices) == len(set(vertices))

    def all_simple_paths(
        self,
        source: str,
        target: str,
        max_depth: int | None = None,
    ) -> Iterator[list[str]]:
        """Enumerate simple paths with optional vertex-count limit.

        The number of simple paths can grow exponentially. This generator
        avoids storing all paths at once but does not remove worst-case cost.
        """
        self._require_vertex(source)
        self._require_vertex(target)

        if max_depth is not None and max_depth < 1:
            raise ValueError("max_depth must be at least one.")

        path = [source]
        visited = {source}

        def search(current: str) -> Iterator[list[str]]:
            if current == target:
                yield path.copy()
                return
            if max_depth is not None and len(path) >= max_depth:
                return

            for neighbor in self.neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                path.append(neighbor)
                yield from search(neighbor)
                path.pop()
                visited.remove(neighbor)

        yield from search(source)

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        """Return a minimum-edge path using BFS, or None if unreachable."""
        self._require_vertex(source)
        self._require_vertex(target)

        queue = deque([source])
        predecessor: dict[str, str | None] = {source: None}

        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                cursor: str | None = target
                while cursor is not None:
                    path.append(cursor)
                    cursor = predecessor[cursor]
                return list(reversed(path))

            for neighbor in self.neighbors(current):
                if neighbor not in predecessor:
                    predecessor[neighbor] = current
                    queue.append(neighbor)
        return None

    def statistics(self) -> GraphStatistics:
        count = len(self.adjacency)
        component_count = len(self.connected_components())
        if self.directed:
            degrees = [
                self.in_degree(vertex) + self.out_degree(vertex)
                for vertex in self.adjacency
            ]
            cycle_exists = self.has_directed_cycle()
            edge_count = len(self.edges())
        else:
            degrees = [self.degree(vertex) for vertex in self.adjacency]
            cycle_exists = self.has_cycle()
            edge_count = len(self.edges())

        return GraphStatistics(
            vertices=count,
            edges=edge_count,
            components=component_count,
            connected=count > 0 and component_count == 1,
            minimum_degree=min(degrees, default=0),
            maximum_degree=max(degrees, default=0),
            average_degree=sum(degrees) / count if count else 0.0,
            cycle_exists=cycle_exists,
        )


def demonstrate_undirected_graph() -> None:
    print("\n=== Undirected graph: campus network ===")
    graph = Graph(
        ["Library", "Laboratory", "Cafeteria", "Hostel", "Gym", "Museum"]
    )
    graph.add_edge("Library", "Laboratory")
    graph.add_edge("Library", "Cafeteria")
    graph.add_edge("Laboratory", "Cafeteria")
    graph.add_edge("Cafeteria", "Hostel")
    graph.add_edge("Hostel", "Gym")

    print("Vertices:", graph.vertices())
    print("Edges:", graph.edges())
    print("Degrees:", graph.degree_sequence())
    print("Library degree:", graph.degree("Library"))
    print("BFS from Library:", graph.breadth_first_search("Library"))
    print("DFS from Library:", graph.depth_first_search("Library"))
    print("Shortest route:", graph.shortest_path("Library", "Gym"))
    print("Connected components:", graph.connected_components())
    print("Connected:", graph.is_connected())
    print("Contains cycle:", graph.has_cycle())

    print("Valid walk:", graph.is_walk(
        ["Library", "Cafeteria", "Library", "Laboratory"]
    ))
    print("Valid trail:", graph.is_trail(
        ["Library", "Cafeteria", "Hostel", "Gym"]
    ))
    print("Simple path:", graph.is_simple_path(
        ["Library", "Cafeteria", "Hostel", "Gym"]
    ))
    print("All simple Library-to-Gym paths:")
    for path in graph.all_simple_paths("Library", "Gym", max_depth=6):
        print(" ", " -> ".join(path))

    print("Statistics:", graph.statistics())


def demonstrate_cycle_and_components() -> None:
    print("\n=== Components and cycle detection ===")
    graph = Graph(["A", "B", "C", "D", "E", "F", "G"])
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    graph.add_edge("D", "E")
    graph.add_edge("F", "F")

    print("Components:", graph.connected_components())
    print("Connected:", graph.is_connected())
    print("Cycle exists:", graph.has_cycle())
    print("Self-loop degree:", graph.degree("F"))
    print("Statistics:", graph.statistics())

    tree = Graph(["Root", "Left", "Right", "Leaf"])
    tree.add_edge("Root", "Left")
    tree.add_edge("Root", "Right")
    tree.add_edge("Left", "Leaf")
    print("Tree has cycle:", tree.has_cycle())
    print("Tree degree sum:", sum(tree.degree(v) for v in tree.vertices()))


def demonstrate_directed_graph() -> None:
    print("\n=== Directed graph: deployment dependencies ===")
    graph = Graph(["build", "test", "package", "deploy", "notify"], directed=True)
    graph.add_edge("build", "test")
    graph.add_edge("test", "package")
    graph.add_edge("package", "deploy")
    graph.add_edge("deploy", "notify")

    for vertex in graph.vertices():
        print(
            f"{vertex}: in={graph.in_degree(vertex)}, "
            f"out={graph.out_degree(vertex)}"
        )

    print("Directed cycle:", graph.has_directed_cycle())
    print("Deployment path:", graph.shortest_path("build", "notify"))

    graph.add_edge("notify", "test")
    print("Cycle after adding notify -> test:", graph.has_directed_cycle())


def demonstrate_validation() -> None:
    print("\n=== Validation and edge cases ===")
    graph = Graph(["A", "B"])
    graph.add_edge("A", "B")

    for description, operation in [
        ("unknown vertex", lambda: graph.degree("Z")),
        ("invalid vertex name", lambda: graph.add_vertex("   ")),
        ("directed-only operation", lambda: graph.in_degree("A")),
        ("empty walk", lambda: graph.is_walk([])),
        ("zero path depth", lambda: list(graph.all_simple_paths("A", "B", 0))),
    ]:
        try:
            operation()
        except (KeyError, ValueError) as error:
            print(f"{description}: rejected ({error})")

    empty = Graph()
    print("Empty graph connected:", empty.is_connected())
    print("Empty graph components:", empty.connected_components())

    isolated = Graph(["A", "B", "C"])
    print("Isolated vertices:", isolated.connected_components())
    print("Unreachable target:", isolated.shortest_path("A", "C"))


def verify_properties() -> None:
    """Small executable checks catch mistakes in the demonstration."""
    graph = Graph(["A", "B", "C"])
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    assert graph.degree("A") == 1
    assert graph.degree("B") == 2
    assert graph.is_connected()
    assert not graph.has_cycle()
    assert graph.shortest_path("A", "C") == ["A", "B", "C"]
    assert graph.is_simple_path(["A", "B", "C"])
    assert not graph.is_simple_path(["A", "B", "A"])

    graph.add_edge("C", "A")
    assert graph.has_cycle()
    assert sum(graph.degree(v) for v in graph.vertices()) == 2 * len(graph.edges())

    directed = Graph(["A", "B"], directed=True)
    directed.add_edge("A", "B")
    assert directed.out_degree("A") == 1
    assert directed.in_degree("B") == 1
    assert not directed.has_directed_cycle()
    directed.add_edge("B", "A")
    assert directed.has_directed_cycle()

    print("\nAll graph property checks passed.")


def main() -> None:
    demonstrate_undirected_graph()
    demonstrate_cycle_and_components()
    demonstrate_directed_graph()
    demonstrate_validation()
    verify_properties()


if __name__ == "__main__":
    main()
