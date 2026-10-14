"""
Graph Traversal Mathematics: BFS, DFS, Reachability, and Traversal Trees

A self-contained implementation covering graph representations, traversal
invariants, shortest paths in unweighted graphs, reachability, connected
components, cycle detection, traversal trees, and mathematical validation.

Run with:
    python graph_traversal.py
"""

from collections import deque
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Optional, Set, Tuple, TypeVar

Node = TypeVar("Node", bound=Hashable)


class GraphError(ValueError):
    """Raised when graph input violates the graph model."""


class Graph(Generic[Node]):
    """Adjacency-list graph supporting directed and undirected edges."""

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self._adjacency: Dict[Node, List[Node]] = {}

    @property
    def vertices(self) -> Tuple[Node, ...]:
        return tuple(self._adjacency)

    def add_vertex(self, vertex: Node) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable.") from exc
        self._adjacency.setdefault(vertex, [])

    def add_edge(self, source: Node, target: Node) -> None:
        self.add_vertex(source)
        self.add_vertex(target)

        if target not in self._adjacency[source]:
            self._adjacency[source].append(target)

        if not self.directed and source not in self._adjacency[target]:
            self._adjacency[target].append(source)

    def neighbors(self, vertex: Node) -> Tuple[Node, ...]:
        if vertex not in self._adjacency:
            raise GraphError(f"Unknown vertex: {vertex!r}")
        return tuple(self._adjacency[vertex])

    def has_vertex(self, vertex: Node) -> bool:
        return vertex in self._adjacency

    def edge_count(self) -> int:
        directed_edges = sum(len(items) for items in self._adjacency.values())
        return directed_edges if self.directed else directed_edges // 2

    def bfs(self, start: Node) -> List[Node]:
        """Visit vertices in nondecreasing shortest-path distance."""
        self._require_vertex(start)
        visited = {start}
        queue = deque([start])
        order: List[Node] = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in self._adjacency[current]:
                if neighbor not in visited:
                    # Mark on enqueue, not dequeue, to avoid duplicate queue entries.
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def bfs_distances(self, start: Node) -> Dict[Node, int]:
        """Return distances from start; unreachable vertices are omitted."""
        self._require_vertex(start)
        distance = {start: 0}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            for neighbor in self._adjacency[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)

        return distance

    def bfs_tree(
        self, start: Node
    ) -> Tuple[List[Node], Dict[Node, Optional[Node]], Dict[Node, int]]:
        """Return discovery order, parent pointers, and shortest distances."""
        self._require_vertex(start)
        order = [start]
        parent: Dict[Node, Optional[Node]] = {start: None}
        distance = {start: 0}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            for neighbor in self._adjacency[current]:
                if neighbor not in parent:
                    parent[neighbor] = current
                    distance[neighbor] = distance[current] + 1
                    order.append(neighbor)
                    queue.append(neighbor)

        return order, parent, distance

    def dfs(self, start: Node) -> List[Node]:
        """Iterative depth-first traversal with recursive-style exploration."""
        self._require_vertex(start)
        visited: Set[Node] = set()
        order: List[Node] = []
        stack = [start]

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            # Reverse insertion preserves the adjacency-list order in traversal.
            for neighbor in reversed(self._adjacency[current]):
                if neighbor not in visited:
                    stack.append(neighbor)

        return order

    def dfs_recursive(self, start: Node) -> List[Node]:
        """Recursive DFS, useful for understanding recursion and its limits."""
        self._require_vertex(start)
        visited: Set[Node] = set()
        order: List[Node] = []

        def visit(vertex: Node) -> None:
            visited.add(vertex)
            order.append(vertex)

            for neighbor in self._adjacency[vertex]:
                if neighbor not in visited:
                    visit(neighbor)

        visit(start)
        return order

    def reachable(self, source: Node, target: Node) -> bool:
        """Test directed reachability or undirected connectivity."""
        self._require_vertex(source)
        self._require_vertex(target)

        if source == target:
            return True

        visited = {source}
        queue = deque([source])

        while queue:
            current = queue.popleft()

            for neighbor in self._adjacency[current]:
                if neighbor == target:
                    return True

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def shortest_path(self, source: Node, target: Node) -> Optional[List[Node]]:
        """Find a path with the fewest edges in an unweighted graph."""
        self._require_vertex(source)
        self._require_vertex(target)

        parent: Dict[Node, Optional[Node]] = {source: None}
        queue = deque([source])

        while queue:
            current = queue.popleft()

            if current == target:
                path: List[Node] = []
                cursor: Optional[Node] = target

                while cursor is not None:
                    path.append(cursor)
                    cursor = parent[cursor]

                path.reverse()
                return path

            for neighbor in self._adjacency[current]:
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

        return None

    def connected_components(self) -> List[Set[Node]]:
        """Compute connected components; only valid for undirected graphs."""
        if self.directed:
            raise GraphError(
                "Connected components require an undirected graph. "
                "Use strongly connected components for directed graphs."
            )

        unseen = set(self._adjacency)
        components: List[Set[Node]] = []

        while unseen:
            start = next(iter(unseen))
            component = set(self.bfs(start))
            components.append(component)
            unseen.difference_update(component)

        return components

    def has_undirected_cycle(self) -> bool:
        """Detect a cycle in a simple undirected graph."""
        if self.directed:
            raise GraphError("This cycle detector requires an undirected graph.")

        visited: Set[Node] = set()

        for start in self._adjacency:
            if start in visited:
                continue

            stack: List[Tuple[Node, Optional[Node]]] = [(start, None)]

            while stack:
                current, parent = stack.pop()

                if current in visited:
                    continue

                visited.add(current)

                for neighbor in self._adjacency[current]:
                    if neighbor == parent:
                        continue

                    if neighbor in visited:
                        return True

                    stack.append((neighbor, current))

        return False

    def has_directed_cycle(self) -> bool:
        """Detect a directed cycle using three-color DFS states."""
        if not self.directed:
            raise GraphError("This cycle detector requires a directed graph.")

        # WHITE: unseen, GRAY: active DFS path, BLACK: fully processed.
        color: Dict[Node, int] = {vertex: 0 for vertex in self._adjacency}

        def visit(vertex: Node) -> bool:
            color[vertex] = 1

            for neighbor in self._adjacency[vertex]:
                if color[neighbor] == 1:
                    return True

                if color[neighbor] == 0 and visit(neighbor):
                    return True

            color[vertex] = 2
            return False

        return any(
            color[vertex] == 0 and visit(vertex)
            for vertex in self._adjacency
        )

    def validate_bfs_tree(
        self,
        start: Node,
        parent: Dict[Node, Optional[Node]],
        distance: Dict[Node, int],
    ) -> bool:
        """Check parent edges and distance consistency for a BFS tree."""
        self._require_vertex(start)

        if parent.get(start, object()) is not None:
            return False

        if distance.get(start) != 0:
            return False

        if set(parent) != set(distance):
            return False

        for vertex, predecessor in parent.items():
            if vertex == start:
                continue

            if predecessor is None or predecessor not in parent:
                return False

            if vertex not in self._adjacency[predecessor]:
                return False

            if distance[vertex] != distance[predecessor] + 1:
                return False

        return True

    def _require_vertex(self, vertex: Node) -> None:
        if vertex not in self._adjacency:
            raise GraphError(f"Unknown vertex: {vertex!r}")


@dataclass(frozen=True)
class TraversalMetrics:
    vertices_reached: int
    edges_examined: int
    maximum_distance: int


def traversal_metrics(
    graph: Graph[Node], start: Node
) -> TraversalMetrics:
    """Measure the reached subgraph without modifying the graph."""
    distances = graph.bfs_distances(start)
    reached = set(distances)
    edges_examined = sum(
        1
        for vertex in reached
        for neighbor in graph.neighbors(vertex)
    )

    return TraversalMetrics(
        vertices_reached=len(reached),
        edges_examined=edges_examined,
        maximum_distance=max(distances.values(), default=0),
    )


def verify_shortest_path(
    graph: Graph[Node], path: Optional[List[Node]], source: Node, target: Node
) -> bool:
    """Validate endpoints and every consecutive edge in a returned path."""
    if path is None:
        return not graph.reachable(source, target)

    if not path or path[0] != source or path[-1] != target:
        return False

    return all(
        right in graph.neighbors(left)
        for left, right in zip(path, path[1:])
    )


def build_sample_graph() -> Graph[str]:
    graph = Graph[str](directed=False)

    for vertex in "ABCDEFGH":
        graph.add_vertex(vertex)

    for source, target in [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("B", "E"),
        ("C", "F"),
        ("E", "F"),
        ("G", "H"),
    ]:
        graph.add_edge(source, target)

    return graph


def demonstrate_undirected_graph() -> None:
    graph = build_sample_graph()

    print("\nUndirected graph")
    print("Vertices:", graph.vertices)
    print("Edges:", graph.edge_count())
    print("BFS from A:", graph.bfs("A"))
    print("DFS from A:", graph.dfs("A"))
    print("Recursive DFS from A:", graph.dfs_recursive("A"))
    print("Distances from A:", graph.bfs_distances("A"))

    order, parent, distance = graph.bfs_tree("A")
    print("BFS discovery order:", order)
    print("BFS parents:", parent)
    print("BFS tree distances:", distance)
    print("BFS tree valid:", graph.validate_bfs_tree("A", parent, distance))

    path = graph.shortest_path("A", "F")
    print("Shortest path A to F:", path)
    print("Path valid:", verify_shortest_path(graph, path, "A", "F"))
    print("A reaches H:", graph.reachable("A", "H"))
    print("Connected components:", graph.connected_components())
    print("Contains undirected cycle:", graph.has_undirected_cycle())
    print("Traversal metrics:", traversal_metrics(graph, "A"))


def demonstrate_directed_graph() -> None:
    graph = Graph[str](directed=True)

    for source, target in [
        ("compile", "test"),
        ("test", "package"),
        ("package", "deploy"),
        ("compile", "lint"),
    ]:
        graph.add_edge(source, target)

    graph.add_vertex("archive")

    print("\nDirected dependency graph")
    print("BFS from compile:", graph.bfs("compile"))
    print("Reachable compile -> deploy:", graph.reachable("compile", "deploy"))
    print("Reachable deploy -> compile:", graph.reachable("deploy", "compile"))
    print("Shortest dependency path:", graph.shortest_path("compile", "deploy"))
    print("Contains directed cycle:", graph.has_directed_cycle())

    cyclic = Graph[str](directed=True)
    cyclic.add_edge("build", "test")
    cyclic.add_edge("test", "release")
    cyclic.add_edge("release", "build")
    print("Cycle in build pipeline:", cyclic.has_directed_cycle())


def demonstrate_edge_cases() -> None:
    print("\nEdge cases")

    graph = Graph[int]()
    graph.add_vertex(10)
    graph.add_vertex(20)

    print("Isolated vertex traversal:", graph.bfs(10))
    print("Path from isolated 10 to 20:", graph.shortest_path(10, 20))
    print("Same-vertex path:", graph.shortest_path(10, 10))
    print("Self reachability:", graph.reachable(10, 10))

    graph.add_edge(10, 20)
    graph.add_edge(10, 20)
    print("Duplicate edge is ignored:", graph.edge_count())

    try:
        graph.bfs(999)
    except GraphError as exc:
        print("Invalid start handled:", exc)

    directed = Graph[int](directed=True)
    directed.add_edge(1, 2)

    try:
        directed.connected_components()
    except GraphError as exc:
        print("Invalid component operation handled:", exc)


def demonstrate_mathematical_invariants() -> None:
    graph = build_sample_graph()
    distances = graph.bfs_distances("A")

    # Every reached vertex other than the source must have a predecessor
    # at distance exactly one less along a real edge.
    for vertex, distance in distances.items():
        if distance == 0:
            continue

        assert any(
            distances.get(neighbor) == distance - 1
            for neighbor in graph.neighbors(vertex)
        )

    # BFS distances satisfy d(v) <= d(u) + 1 for every reachable edge u -> v.
    for source in distances:
        for target in graph.neighbors(source):
            if target in distances:
                assert distances[target] <= distances[source] + 1

    # Each BFS tree edge increases the distance by exactly one.
    order, parent, tree_distance = graph.bfs_tree("A")
    tree_edges = sum(value is not None for value in parent.values())

    assert len(order) == len(parent)
    assert tree_edges == len(parent) - 1
    assert graph.validate_bfs_tree("A", parent, tree_distance)

    print("\nMathematical invariants")
    print("Shortest-distance inequalities: passed")
    print("Parent-edge and distance invariants: passed")
    print("Tree edge count:", tree_edges)
    print("Reached vertices:", len(parent))


if __name__ == "__main__":
    demonstrate_undirected_graph()
    demonstrate_directed_graph()
    demonstrate_edge_cases()
    demonstrate_mathematical_invariants()
