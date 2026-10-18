from collections import defaultdict, deque
from itertools import permutations
from typing import Hashable, Iterable

Vertex = Hashable


class Graph:
    """Undirected graph for Euler and Hamiltonian graph analysis."""

    def __init__(self, vertices: Iterable[Vertex], edges: Iterable[tuple[Vertex, Vertex]]):
        self.vertices = list(vertices)
        if len(set(self.vertices)) != len(self.vertices):
            raise ValueError("Vertex identifiers must be unique.")

        self.adj = {v: [] for v in self.vertices}
        self.edges = []
        self.edge_ids = set()

        for u, v in edges:
            if u not in self.adj or v not in self.adj:
                raise ValueError(f"Edge ({u}, {v}) references an unknown vertex.")
            if u == v:
                raise ValueError("Self-loops are not supported in this example.")

            edge_id = frozenset((u, v))
            if edge_id in self.edge_ids:
                raise ValueError(f"Duplicate undirected edge: ({u}, {v}).")

            self.edge_ids.add(edge_id)
            self.edges.append((u, v))
            self.adj[u].append(v)
            self.adj[v].append(u)

    def connected_nonisolated_vertices(self) -> bool:
        """Check connectivity while ignoring isolated vertices."""
        active = [v for v in self.vertices if self.adj[v]]
        if not active:
            return True

        visited = set()
        stack = [active[0]]

        while stack:
            vertex = stack.pop()
            if vertex in visited:
                continue
            visited.add(vertex)
            stack.extend(n for n in self.adj[vertex] if n not in visited)

        return all(v in visited for v in active)

    def is_eulerian(self) -> bool:
        """An undirected connected graph has an Euler circuit iff all degrees are even."""
        return (
            self.connected_nonisolated_vertices()
            and all(len(self.adj[v]) % 2 == 0 for v in self.vertices)
        )

    def has_euler_trail(self) -> bool:
        """An Euler trail exists iff exactly zero or two vertices have odd degree."""
        odd_count = sum(len(self.adj[v]) % 2 for v in self.vertices)
        return self.connected_nonisolated_vertices() and odd_count in (0, 2)

    def euler_trail(self) -> list[Vertex] | None:
        """Hierholzer's algorithm: construct an Euler trail in O(V + E)."""
        if not self.has_euler_trail():
            return None

        if not self.edges:
            return self.vertices[:1]

        odd = [v for v in self.vertices if len(self.adj[v]) % 2]
        start = odd[0] if odd else next(v for v in self.vertices if self.adj[v])

        # Edge indices distinguish edges during traversal.
        indexed_adj = {v: [] for v in self.vertices}
        for edge_id, (u, v) in enumerate(self.edges):
            indexed_adj[u].append((v, edge_id))
            indexed_adj[v].append((u, edge_id))

        used = set()
        stack = [start]
        circuit = []

        while stack:
            u = stack[-1]

            while indexed_adj[u] and indexed_adj[u][-1][1] in used:
                indexed_adj[u].pop()

            if indexed_adj[u]:
                v, edge_id = indexed_adj[u].pop()
                if edge_id not in used:
                    used.add(edge_id)
                    stack.append(v)
            else:
                circuit.append(stack.pop())

        if len(used) != len(self.edges):
            return None

        return circuit[::-1]

    def is_hamiltonian_path(self, path: list[Vertex]) -> bool:
        """A Hamiltonian path visits each vertex exactly once."""
        return (
            len(path) == len(self.vertices)
            and len(set(path)) == len(path)
            and set(path) == set(self.vertices)
            and all(
                path[i + 1] in self.adj[path[i]]
                for i in range(len(path) - 1)
            )
        )

    def is_hamiltonian_cycle(self, cycle: list[Vertex]) -> bool:
        """A Hamiltonian cycle visits each vertex once and returns to its start."""
        if len(self.vertices) < 3 or len(cycle) != len(self.vertices):
            return False
        return (
            self.is_hamiltonian_path(cycle)
            and cycle[0] in self.adj[cycle[-1]]
        )

    def find_hamiltonian_path(self) -> list[Vertex] | None:
        """Backtracking search. Worst-case time is O(V!); use pruning for larger graphs."""
        if not self.vertices:
            return []

        path = []
        visited = set()

        def search(u: Vertex) -> bool:
            path.append(u)
            visited.add(u)

            if len(path) == len(self.vertices):
                return True

            for v in self.adj[u]:
                if v not in visited and search(v):
                    return True

            visited.remove(u)
            path.pop()
            return False

        for start in self.vertices:
            if search(start):
                return path.copy()

        return None

    def find_hamiltonian_cycle(self) -> list[Vertex] | None:
        """Fix a start vertex to avoid redundant rotations."""
        if len(self.vertices) < 3:
            return None

        start = self.vertices[0]
        path = [start]
        visited = {start}

        def search(u: Vertex) -> bool:
            if len(path) == len(self.vertices):
                return start in self.adj[u]

            for v in self.adj[u]:
                if v not in visited:
                    visited.add(v)
                    path.append(v)

                    if search(v):
                        return True

                    path.pop()
                    visited.remove(v)

            return False

        if search(start):
            return path.copy()
        return None

    def describe(self, name: str) -> None:
        print(f"\n{name}")
        print("Vertices:", self.vertices)
        print("Edges:", self.edges)
        print("Degrees:", {v: len(self.adj[v]) for v in self.vertices})
        print("Connected ignoring isolated vertices:", self.connected_nonisolated_vertices())
        print("Euler trail exists:", self.has_euler_trail())
        print("Euler circuit exists:", self.is_eulerian())
        print("Euler trail:", self.euler_trail())
        print("Hamiltonian path:", self.find_hamiltonian_path())
        print("Hamiltonian cycle:", self.find_hamiltonian_cycle())


def brute_force_hamiltonian_path(graph: Graph) -> list[Vertex] | None:
    """Small-graph reference implementation for checking Hamiltonian paths."""
    for candidate in permutations(graph.vertices):
        if graph.is_hamiltonian_path(list(candidate)):
            return list(candidate)
    return None


def run_tests() -> None:
    square = Graph(
        ["A", "B", "C", "D"],
        [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    )
    assert square.is_eulerian()
    assert square.has_euler_trail()
    assert square.find_hamiltonian_cycle() is not None

    triangle_with_tail = Graph(
        ["A", "B", "C", "D"],
        [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")],
    )
    assert triangle_with_tail.has_euler_trail()
    assert not triangle_with_tail.is_eulerian()
    assert triangle_with_tail.find_hamiltonian_path() is not None
    assert triangle_with_tail.find_hamiltonian_cycle() is None

    disconnected = Graph(
        ["A", "B", "C", "D"],
        [("A", "B"), ("C", "D")],
    )
    assert not disconnected.has_euler_trail()
    assert disconnected.find_hamiltonian_path() is None

    empty_edges = Graph(["A", "B"], [])
    assert not empty_edges.has_euler_trail()
    assert empty_edges.find_hamiltonian_path() is None

    try:
        Graph(["A", "B"], [("A", "C")])
        raise AssertionError("Unknown vertex was not rejected.")
    except ValueError:
        pass

    try:
        Graph(["A", "B"], [("A", "B"), ("B", "A")])
        raise AssertionError("Duplicate edge was not rejected.")
    except ValueError:
        pass

    assert brute_force_hamiltonian_path(square) is not None
    print("All graph tests passed.")


def main() -> None:
    run_tests()

    examples = [
        (
            "Euler circuit and Hamiltonian cycle: square network",
            Graph(
                ["A", "B", "C", "D"],
                [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
            ),
        ),
        (
            "Euler trail but no Euler circuit: triangle with a tail",
            Graph(
                ["A", "B", "C", "D"],
                [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")],
            ),
        ),
        (
            "Hamiltonian cycle without an Euler trail: complete graph K4",
            Graph(
                ["A", "B", "C", "D"],
                [
                    ("A", "B"), ("A", "C"), ("A", "D"),
                    ("B", "C"), ("B", "D"), ("C", "D"),
                ],
            ),
        ),
        (
            "Disconnected graph",
            Graph(["A", "B", "C", "D"], [("A", "B"), ("C", "D")]),
        ),
    ]

    for name, graph in examples:
        graph.describe(name)


if __name__ == "__main__":
    main()
