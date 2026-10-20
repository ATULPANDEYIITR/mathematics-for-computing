#!/usr/bin/env python3
"""
Advanced Graph Theory:
Planarity, graph isomorphism, graph minors, and extremal concepts.

Self-contained educational implementation using only the Python standard library.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple


Vertex = str
Edge = Tuple[Vertex, Vertex]


def canonical_edge(u: Vertex, v: Vertex) -> Edge:
    """Represent an undirected edge in a deterministic form."""
    if u == v:
        raise ValueError("Self-loops are not supported in simple graphs.")
    return (u, v) if u < v else (v, u)


class Graph:
    """Simple undirected graph with adjacency-set representation."""

    def __init__(self, vertices: Iterable[Vertex] = ()) -> None:
        self.vertices: Set[Vertex] = set(vertices)
        self.adjacency: Dict[Vertex, Set[Vertex]] = {
            vertex: set() for vertex in self.vertices
        }

    def add_vertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            self.vertices.add(vertex)
            self.adjacency[vertex] = set()

    def add_edge(self, u: Vertex, v: Vertex) -> None:
        if u == v:
            raise ValueError("Simple graphs cannot contain self-loops.")
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    def remove_edge(self, u: Vertex, v: Vertex) -> None:
        self.adjacency.get(u, set()).discard(v)
        self.adjacency.get(v, set()).discard(u)

    def remove_vertex(self, vertex: Vertex) -> None:
        if vertex not in self.vertices:
            return
        for neighbor in list(self.adjacency[vertex]):
            self.adjacency[neighbor].discard(vertex)
        del self.adjacency[vertex]
        self.vertices.remove(vertex)

    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        return v in self.adjacency.get(u, set())

    def edges(self) -> Set[Edge]:
        return {
            canonical_edge(u, v)
            for u in self.vertices
            for v in self.adjacency[u]
            if u < v
        }

    def degree(self, vertex: Vertex) -> int:
        return len(self.adjacency[vertex])

    def copy(self) -> "Graph":
        result = Graph(self.vertices)
        for u, v in self.edges():
            result.add_edge(u, v)
        return result

    def induced_subgraph(self, selected: Set[Vertex]) -> "Graph":
        result = Graph(selected)
        for u, v in self.edges():
            if u in selected and v in selected:
                result.add_edge(u, v)
        return result

    def contract_edge(self, u: Vertex, v: Vertex) -> "Graph":
        """Contract uv into a fresh vertex, removing parallel edges."""
        if not self.has_edge(u, v):
            raise ValueError(f"Cannot contract absent edge {u}-{v}.")

        merged = f"({u}+{v})"
        result = self.copy()
        neighbors = (result.adjacency[u] | result.adjacency[v]) - {u, v}
        result.remove_vertex(u)
        result.remove_vertex(v)
        result.add_vertex(merged)

        for neighbor in neighbors:
            result.add_edge(merged, neighbor)

        return result

    def connected(self) -> bool:
        if not self.vertices:
            return True

        start = next(iter(self.vertices))
        visited = {start}
        queue = deque([start])

        while queue:
            current = queue.popleft()
            for neighbor in self.adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited == self.vertices

    def __repr__(self) -> str:
        return f"Graph(V={sorted(self.vertices)}, E={sorted(self.edges())})"


def cycle_graph(n: int) -> Graph:
    if n < 3:
        raise ValueError("A simple cycle requires at least three vertices.")
    graph = Graph(str(i) for i in range(n))
    for i in range(n):
        graph.add_edge(str(i), str((i + 1) % n))
    return graph


def complete_graph(n: int) -> Graph:
    graph = Graph(str(i) for i in range(n))
    for u, v in combinations(graph.vertices, 2):
        graph.add_edge(u, v)
    return graph


def complete_bipartite_graph(left: int, right: int) -> Graph:
    if left < 1 or right < 1:
        raise ValueError("Both bipartition sizes must be positive.")

    graph = Graph()
    left_vertices = [f"L{i}" for i in range(left)]
    right_vertices = [f"R{i}" for i in range(right)]

    for vertex in left_vertices + right_vertices:
        graph.add_vertex(vertex)

    for u in left_vertices:
        for v in right_vertices:
            graph.add_edge(u, v)

    return graph


def degree_sequence(graph: Graph) -> Tuple[int, ...]:
    return tuple(sorted((graph.degree(v) for v in graph.vertices), reverse=True))


def has_triangle(graph: Graph) -> bool:
    """Detect K3, useful for small non-planarity experiments."""
    for u, v, w in combinations(graph.vertices, 3):
        if graph.has_edge(u, v) and graph.has_edge(v, w) and graph.has_edge(u, w):
            return True
    return False


def is_bipartite(graph: Graph) -> bool:
    color: Dict[Vertex, int] = {}

    for source in graph.vertices:
        if source in color:
            continue

        color[source] = 0
        queue = deque([source])

        while queue:
            current = queue.popleft()
            for neighbor in graph.adjacency[current]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[current]
                    queue.append(neighbor)
                elif color[neighbor] == color[current]:
                    return False

    return True


def euler_bound(graph: Graph) -> bool:
    """
    Necessary condition for a simple planar graph:
        |E| <= 3|V| - 6, for |V| >= 3.

    This is not sufficient for planarity.
    """
    n = len(graph.vertices)
    m = len(graph.edges())

    if n < 3:
        return True

    return m <= 3 * n - 6


def bipartite_euler_bound(graph: Graph) -> bool:
    """
    For a simple planar bipartite graph with n >= 3:
        |E| <= 2|V| - 4.
    """
    n = len(graph.vertices)
    m = len(graph.edges())

    if n < 3:
        return True

    if not is_bipartite(graph):
        return True

    return m <= 2 * n - 4


def chromatic_polynomial_values(graph: Graph, max_colors: int = 5) -> List[int]:
    """
    Evaluate the chromatic polynomial by direct backtracking for small graphs.

    This is deliberately exponential and intended for small educational cases.
    """
    vertices = sorted(graph.vertices, key=lambda v: graph.degree(v), reverse=True)
    results: List[int] = []

    for colors in range(0, max_colors + 1):
        if colors == 0:
            results.append(1 if not graph.vertices else 0)
            continue

        assignment: Dict[Vertex, int] = {}
        count = 0

        def assign(index: int) -> None:
            nonlocal count

            if index == len(vertices):
                count += 1
                return

            vertex = vertices[index]
            forbidden = {
                assignment[neighbor]
                for neighbor in graph.adjacency[vertex]
                if neighbor in assignment
            }

            for color in range(colors):
                if color not in forbidden:
                    assignment[vertex] = color
                    assign(index + 1)
                    del assignment[vertex]

        assign(0)
        results.append(count)

    return results


def is_isomorphic(
    first: Graph,
    second: Graph,
    return_mapping: bool = False,
) -> Tuple[bool, Optional[Dict[Vertex, Vertex]]]:
    """
    Exact graph-isomorphism test for small graphs.

    It uses invariant filtering followed by degree-compatible backtracking.
    This is exponential in the worst case, but practical for the small
    educational examples used here.
    """
    if len(first.vertices) != len(second.vertices):
        return False, None

    if len(first.edges()) != len(second.edges()):
        return False, None

    if degree_sequence(first) != degree_sequence(second):
        return False, None

    first_counts = Counter(first.degree(v) for v in first.vertices)
    second_counts = Counter(second.degree(v) for v in second.vertices)

    if first_counts != second_counts:
        return False, None

    second_by_degree: Dict[int, List[Vertex]] = {}
    for vertex in second.vertices:
        second_by_degree.setdefault(second.degree(vertex), []).append(vertex)

    ordered_first = sorted(
        first.vertices,
        key=lambda v: (
            -first.degree(v),
            -sum(first.degree(n) for n in first.adjacency[v]),
        ),
    )

    mapping: Dict[Vertex, Vertex] = {}
    used: Set[Vertex] = set()

    def compatible(u: Vertex, candidate: Vertex) -> bool:
        for mapped_u, mapped_v in mapping.items():
            if first.has_edge(u, mapped_u) != second.has_edge(candidate, mapped_v):
                return False
        return True

    def search(index: int) -> bool:
        if index == len(ordered_first):
            return True

        u = ordered_first[index]

        for candidate in second_by_degree[first.degree(u)]:
            if candidate in used:
                continue

            if not compatible(u, candidate):
                continue

            mapping[u] = candidate
            used.add(candidate)

            if search(index + 1):
                return True

            used.remove(candidate)
            del mapping[u]

        return False

    found = search(0)

    if found:
        return True, dict(mapping) if return_mapping else None

    return False, None


def contains_k5_subgraph(graph: Graph) -> bool:
    for subset in combinations(graph.vertices, 5):
        selected = set(subset)
        if all(
            graph.has_edge(u, v)
            for u, v in combinations(selected, 2)
        ):
            return True
    return False


def contains_k33_subgraph(graph: Graph) -> bool:
    if len(graph.vertices) < 6:
        return False

    vertices = list(graph.vertices)

    for subset in combinations(vertices, 6):
        selected = set(subset)

        for left_tuple in combinations(subset, 3):
            left = set(left_tuple)
            right = selected - left

            if all(
                graph.has_edge(u, v)
                for u in left
                for v in right
            ):
                return True

    return False


def small_planarity_certificate(graph: Graph) -> Tuple[bool, str]:
    """
    A deliberately bounded planarity classifier for small teaching examples.

    It first uses Euler-type necessary conditions and detects K5/K3,3
    subgraphs. For the supplied examples this provides useful exact answers.

    General planarity testing requires algorithms such as Hopcroft-Tarjan or
    Boyer-Myrvold; this routine intentionally does not claim to implement them.
    """
    n = len(graph.vertices)

    if n <= 4:
        return True, "Every simple graph with at most four vertices is planar."

    if not euler_bound(graph):
        return False, "Fails the planar Euler edge bound."

    if not bipartite_euler_bound(graph):
        return False, "Fails the bipartite planar edge bound."

    if contains_k5_subgraph(graph):
        return False, "Contains K5 as a subgraph."

    if contains_k33_subgraph(graph):
        return False, "Contains K3,3 as a subgraph."

    return True, (
        "No bounded certificate of non-planarity was found; "
        "the necessary edge bounds hold. A general planarity algorithm "
        "is required for arbitrary graphs."
    )


def all_k5_minor_obstructions(graph: Graph) -> List[Graph]:
    """
    Search for a K5 minor by repeatedly contracting edges and checking
    whether the resulting graph is K5. This is intentionally bounded.
    """
    target = complete_graph(5)
    found: List[Graph] = []

    def canonical_state(g: Graph) -> Tuple[Tuple[str, ...], Tuple[Edge, ...]]:
        return tuple(sorted(g.vertices)), tuple(sorted(g.edges()))

    seen: Set[Tuple[Tuple[str, ...], Tuple[Edge, ...]]] = set()

    def search(g: Graph) -> bool:
        state = canonical_state(g)
        if state in seen:
            return False
        seen.add(state)

        if len(g.vertices) == 5:
            iso, _ = is_isomorphic(g, target)
            if iso:
                found.append(g)
                return True

        if len(g.vertices) <= 5:
            return False

        for u, v in sorted(g.edges()):
            contracted = g.contract_edge(u, v)
            if search(contracted):
                return True

        return False

    search(graph)
    return found


def subdivisions_of_k33_example() -> Graph:
    """
    Construct a graph obtained from K3,3 by subdividing one edge.
    Subdivision preserves the K3,3 minor.
    """
    graph = complete_bipartite_graph(3, 3)
    graph.remove_edge("L0", "R0")
    graph.add_vertex("X")
    graph.add_edge("L0", "X")
    graph.add_edge("X", "R0")
    return graph


def extremal_bipartite_bound(n: int, left_size: int, right_size: int) -> int:
    """
    Maximum edges in a bipartite graph with prescribed partition sizes.
    """
    if n != left_size + right_size:
        raise ValueError("Partition sizes must sum to n.")
    if left_size < 0 or right_size < 0:
        raise ValueError("Partition sizes cannot be negative.")
    return left_size * right_size


def demonstrate_isomorphism() -> None:
    first = Graph(["A", "B", "C", "D", "E"])
    for u, v in [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")]:
        first.add_edge(u, v)

    second = Graph(["1", "2", "3", "4", "5"])
    for u, v in [("1", "3"), ("3", "5"), ("5", "2"), ("2", "4"), ("4", "1")]:
        second.add_edge(u, v)

    equivalent, mapping = is_isomorphic(first, second, return_mapping=True)

    print("Graph isomorphism")
    print("-----------------")
    print("First degree sequence :", degree_sequence(first))
    print("Second degree sequence:", degree_sequence(second))
    print("Isomorphic            :", equivalent)
    print("Mapping               :", mapping)
    print()


def demonstrate_planarity() -> None:
    examples = {
        "cycle C5": cycle_graph(5),
        "complete K5": complete_graph(5),
        "complete bipartite K3,3": complete_bipartite_graph(3, 3),
        "subdivided K3,3": subdivisions_of_k33_example(),
    }

    print("Planarity-related tests")
    print("-----------------------")

    for name, graph in examples.items():
        planar, reason = small_planarity_certificate(graph)
        print(f"{name:25} | V={len(graph.vertices):2} E={len(graph.edges()):2} "
              f"| planar={planar} | {reason}")

    print()


def demonstrate_minors() -> None:
    k5 = complete_graph(5)
    larger = Graph(str(i) for i in range(6))

    for u, v in combinations(larger.vertices, 2):
        if {u, v} != {"0", "1"}:
            larger.add_edge(u, v)

    # The edge 0-1 is intentionally missing, so contracting another edge
    # demonstrates how a dense graph can approach a K5 minor.
    print("Graph minor operations")
    print("----------------------")
    print("Original graph:", larger)
    print("Connected:", larger.connected())

    if larger.edges():
        u, v = sorted(larger.edges())[0]
        contracted = larger.contract_edge(u, v)
        print(f"Contracted edge {u}-{v}:")
        print(contracted)

    k5_minor = all_k5_minor_obstructions(k5)
    print("K5 contains a K5 minor:", bool(k5_minor))
    print()


def demonstrate_extremal_concepts() -> None:
    print("Extremal graph concepts")
    print("-----------------------")

    for n in range(3, 9):
        complete_edges = n * (n - 1) // 2
        planar_upper_bound = 3 * n - 6
        print(
            f"n={n}: complete-graph edges={complete_edges}, "
            f"planar upper bound={planar_upper_bound}"
        )

    print("\nBipartite extremal examples:")
    for left, right in [(2, 3), (3, 3), (3, 4), (4, 4)]:
        n = left + right
        maximum = extremal_bipartite_bound(n, left, right)
        planar_limit = 2 * n - 4
        print(
            f"K_{left},{right}: n={n}, edges={maximum}, "
            f"bipartite-planar bound={planar_limit}"
        )

    print()


def demonstrate_coloring() -> None:
    triangle = complete_graph(3)
    square = cycle_graph(4)

    print("Chromatic-polynomial evaluations")
    print("---------------------------------")
    print("K3:", chromatic_polynomial_values(triangle, 4))
    print("C4:", chromatic_polynomial_values(square, 4))
    print()


def main() -> None:
    print("Advanced Graph Theory Laboratory")
    print("=================================")
    demonstrate_isomorphism()
    demonstrate_planarity()
    demonstrate_minors()
    demonstrate_extremal_concepts()
    demonstrate_coloring()

    print("Key implementation boundaries")
    print("-----------------------------")
    print("* Isomorphism uses exact backtracking and is intended for small graphs.")
    print("* Planarity checks use mathematical necessary conditions plus small"
          " forbidden-subgraph certificates.")
    print("* Minor search uses bounded edge contraction and is exponential.")
    print("* Extremal bounds are mathematical upper bounds, not automatic"
          " construction algorithms.")
    print("* Adjacency sets provide expected O(1) membership and O(n + m)"
          " traversal for standard graph operations.")


if __name__ == "__main__":
    main()
