#!/usr/bin/env python3
"""Graph matching algorithms: matchings, maximal matching, maximum matching,
and maximum bipartite matching.

Run with Python 3.10 or later. No external dependencies are required.
"""

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable

Vertex = Hashable
Edge = tuple[Vertex, Vertex]


def normalize_edge(u: Vertex, v: Vertex) -> frozenset[Vertex]:
    if u == v:
        raise ValueError("Self-loops cannot belong to a matching.")
    return frozenset((u, v))


class Graph:
    """Undirected simple graph represented by adjacency sets."""

    def __init__(self, vertices: Iterable[Vertex] = ()) -> None:
        self.adjacency: dict[Vertex, set[Vertex]] = {}
        for vertex in vertices:
            self.add_vertex(vertex)

    def add_vertex(self, vertex: Vertex) -> None:
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, u: Vertex, v: Vertex) -> None:
        if u == v:
            raise ValueError("Self-loops are not supported.")
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        return v in self.adjacency.get(u, set())

    def edges(self) -> list[Edge]:
        result = []
        for u in self.adjacency:
            for v in self.adjacency[u]:
                if repr(u) < repr(v):
                    result.append((u, v))
        return result

    def validate_matching(self, matching: Iterable[Edge]) -> bool:
        used: set[Vertex] = set()
        for u, v in matching:
            if not self.has_edge(u, v):
                return False
            if u in used or v in used:
                return False
            used.update((u, v))
        return True


def greedy_maximal_matching(graph: Graph) -> list[Edge]:
    """Build a maximal matching by greedily accepting disjoint edges.

    Maximal means no additional edge can be added directly.
    It does not necessarily mean the matching has maximum cardinality.
    """
    matching = []
    matched: set[Vertex] = set()

    for u, v in graph.edges():
        if u not in matched and v not in matched:
            matching.append((u, v))
            matched.update((u, v))

    assert graph.validate_matching(matching)
    return matching


def is_maximal_matching(graph: Graph, matching: Iterable[Edge]) -> bool:
    matching = list(matching)
    if not graph.validate_matching(matching):
        return False

    matched = {vertex for edge in matching for vertex in edge}
    return not any(
        u not in matched and v not in matched
        for u, v in graph.edges()
    )


def maximum_matching_small_graph(graph: Graph) -> list[Edge]:
    """Find an exact maximum matching using recursive backtracking.

    This exponential algorithm is suitable for small general graphs and
    serves as a transparent reference implementation.
    """
    vertices = list(graph.adjacency)
    best: list[Edge] = []

    def search(
        remaining: frozenset[Vertex],
        current: list[Edge],
    ) -> None:
        nonlocal best

        if len(current) + len(remaining) // 2 <= len(best):
            return

        if not remaining:
            if len(current) > len(best):
                best = current.copy()
            return

        # Select a vertex with the fewest available partners.
        u = min(
            remaining,
            key=lambda vertex: sum(
                neighbor in remaining
                for neighbor in graph.adjacency[vertex]
            ),
        )
        without_u = remaining - {u}

        # A vertex may remain unmatched in a maximum matching.
        search(without_u, current)

        for v in graph.adjacency[u] & remaining:
            if v == u:
                continue
            current.append((u, v))
            search(without_u - {v}, current)
            current.pop()

    search(frozenset(vertices), [])
    return best


@dataclass
class BipartiteMatchingResult:
    pairs: list[tuple[Vertex, Vertex]]
    unmatched_left: set[Vertex]
    unmatched_right: set[Vertex]

    @property
    def cardinality(self) -> int:
        return len(self.pairs)


class BipartiteGraph:
    """Bipartite graph with explicitly declared left and right partitions."""

    def __init__(
        self,
        left: Iterable[Vertex],
        right: Iterable[Vertex],
    ) -> None:
        self.left = list(left)
        self.right = list(right)

        if len(set(self.left)) != len(self.left):
            raise ValueError("Duplicate vertices in the left partition.")
        if len(set(self.right)) != len(self.right):
            raise ValueError("Duplicate vertices in the right partition.")
        if set(self.left) & set(self.right):
            raise ValueError("Partitions must be disjoint.")

        self.left_set = set(self.left)
        self.right_set = set(self.right)
        self.adjacency: dict[Vertex, set[Vertex]] = {
            vertex: set() for vertex in self.left
        }

    def add_edge(self, left: Vertex, right: Vertex) -> None:
        if left not in self.left_set or right not in self.right_set:
            raise ValueError("An edge must connect the two partitions.")
        self.adjacency[left].add(right)

    def maximum_matching(self) -> BipartiteMatchingResult:
        """Compute maximum cardinality using augmenting paths.

        Each successful augmentation increases the matching size by one.
        This DFS implementation runs in O(VE) time.
        """
        right_owner: dict[Vertex, Vertex] = {}

        def augment(left_vertex: Vertex, seen: set[Vertex]) -> bool:
            for right_vertex in self.adjacency[left_vertex]:
                if right_vertex in seen:
                    continue
                seen.add(right_vertex)

                owner = right_owner.get(right_vertex)
                if owner is None or augment(owner, seen):
                    right_owner[right_vertex] = left_vertex
                    return True

            return False

        for left_vertex in self.left:
            augment(left_vertex, set())

        pairs = [
            (left_vertex, right_vertex)
            for right_vertex, left_vertex in right_owner.items()
        ]
        matched_left = {left for left, _ in pairs}

        return BipartiteMatchingResult(
            pairs=sorted(pairs, key=lambda pair: repr(pair[0])),
            unmatched_left=self.left_set - matched_left,
            unmatched_right=self.right_set - set(right_owner),
        )

    def verify_matching(self, pairs: Iterable[tuple[Vertex, Vertex]]) -> bool:
        pairs = list(pairs)
        used_left: set[Vertex] = set()
        used_right: set[Vertex] = set()

        for left, right in pairs:
            if left not in self.left_set or right not in self.right_set:
                return False
            if right not in self.adjacency[left]:
                return False
            if left in used_left or right in used_right:
                return False
            used_left.add(left)
            used_right.add(right)

        return True


def demo_basic_matching() -> None:
    print("\n--- Matching fundamentals ---")
    graph = Graph(range(1, 7))

    for edge in [
        (1, 2), (1, 3), (2, 3),
        (2, 4), (3, 5), (4, 5), (4, 6), (5, 6),
    ]:
        graph.add_edge(*edge)

    greedy = greedy_maximal_matching(graph)
    exact = maximum_matching_small_graph(graph)

    print("Graph edges:", sorted(graph.edges(), key=repr))
    print("Greedy maximal matching:", greedy)
    print("Is greedy matching maximal?", is_maximal_matching(graph, greedy))
    print("Maximum matching:", exact)
    print("Maximum cardinality:", len(exact))
    print("Valid maximum matching:", graph.validate_matching(exact))


def demo_difference_between_maximal_and_maximum() -> None:
    print("\n--- Maximal is not necessarily maximum ---")
    graph = Graph("ABCD")

    # Choosing A-B prevents the greedy algorithm from selecting C-D
    # only when that edge is absent. This graph instead demonstrates
    # a maximal matching with smaller cardinality.
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")

    greedy = [("B", "C")]
    maximum = maximum_matching_small_graph(graph)

    print("Edges:", graph.edges())
    print("Example maximal matching:", greedy)
    print("Is maximal?", is_maximal_matching(graph, greedy))
    print("Maximum matching:", maximum)
    print("Maximum cardinality:", len(maximum))


def demo_bipartite_assignment() -> None:
    print("\n--- Bipartite assignment ---")
    engineers = ["E1", "E2", "E3", "E4"]
    projects = ["P1", "P2", "P3", "P4"]

    graph = BipartiteGraph(engineers, projects)

    # Edges represent valid skill or eligibility assignments.
    eligibility = [
        ("E1", "P1"), ("E1", "P2"),
        ("E2", "P1"),
        ("E3", "P2"), ("E3", "P3"),
        ("E4", "P3"),
    ]
    for edge in eligibility:
        graph.add_edge(*edge)

    result = graph.maximum_matching()

    print("Assignments:", result.pairs)
    print("Number of assignments:", result.cardinality)
    print("Unassigned engineers:", sorted(result.unmatched_left))
    print("Unfilled projects:", sorted(result.unmatched_right))
    print("Matching valid:", graph.verify_matching(result.pairs))


def demo_hall_condition_example() -> None:
    print("\n--- Limited eligibility ---")
    graph = BipartiteGraph(
        left=["A", "B", "C"],
        right=["X", "Y"],
    )

    graph.add_edge("A", "X")
    graph.add_edge("B", "X")
    graph.add_edge("C", "Y")

    result = graph.maximum_matching()
    print("Maximum matching:", result.pairs)
    print("Cardinality:", result.cardinality)
    print("Unmatched left vertices:", result.unmatched_left)

    # Three left vertices cannot all be matched to two right vertices.
    assert result.cardinality <= 2


def demo_edge_cases() -> None:
    print("\n--- Edge cases ---")
    empty = Graph()
    print("Empty graph matching:", maximum_matching_small_graph(empty))

    isolated = Graph(["isolated"])
    print(
        "Isolated vertex matching:",
        maximum_matching_small_graph(isolated),
    )

    try:
        empty.add_edge("x", "x")
    except ValueError as error:
        print("Self-loop rejected:", error)

    bipartite = BipartiteGraph(["L"], ["R"])
    try:
        bipartite.add_edge("R", "L")
    except ValueError as error:
        print("Invalid partition edge rejected:", error)


def main() -> None:
    demo_basic_matching()
    demo_difference_between_maximal_and_maximum()
    demo_bipartite_assignment()
    demo_hall_condition_example()
    demo_edge_cases()


if __name__ == "__main__":
    main()
