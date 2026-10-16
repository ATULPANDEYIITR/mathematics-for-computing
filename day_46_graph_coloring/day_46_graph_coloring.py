#!/usr/bin/env python3
"""Graph coloring, chromatic numbers, bipartite graphs, and practical applications.

This self-contained program uses only the Python standard library. It includes
graph validation, greedy coloring, exact backtracking, bipartite testing,
conflict detection, exam scheduling, register allocation, and verification.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Mapping

Vertex = Hashable


class GraphError(ValueError):
    """Raised when a graph or coloring violates structural requirements."""


class UndirectedGraph:
    """Simple undirected graph represented by adjacency sets."""

    def __init__(
        self,
        vertices: Iterable[Vertex] = (),
        edges: Iterable[tuple[Vertex, Vertex]] = (),
    ) -> None:
        self.adjacency: dict[Vertex, set[Vertex]] = {}
        for vertex in vertices:
            self.add_vertex(vertex)
        for left, right in edges:
            self.add_edge(left, right)

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise GraphError("Vertices must be hashable.") from exc
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, left: Vertex, right: Vertex) -> None:
        if left == right:
            raise GraphError("Self-loops are not supported by this simple graph.")
        self.add_vertex(left)
        self.add_vertex(right)
        self.adjacency[left].add(right)
        self.adjacency[right].add(left)

    @property
    def vertices(self) -> tuple[Vertex, ...]:
        return tuple(self.adjacency)

    @property
    def edges(self) -> tuple[tuple[Vertex, Vertex], ...]:
        return tuple(
            (left, right)
            for left in self.adjacency
            for right in self.adjacency[left]
            if self._position(left) < self._position(right)
        )

    def _position(self, vertex: Vertex) -> int:
        return list(self.adjacency).index(vertex)

    def degree(self, vertex: Vertex) -> int:
        self._require_vertex(vertex)
        return len(self.adjacency[vertex])

    def _require_vertex(self, vertex: Vertex) -> None:
        if vertex not in self.adjacency:
            raise GraphError(f"Unknown vertex: {vertex!r}")

    def validate_coloring(self, coloring: Mapping[Vertex, int]) -> bool:
        """Require every vertex to have a nonnegative integer color."""
        if set(coloring) != set(self.adjacency):
            return False
        if any(
            isinstance(color, bool)
            or not isinstance(color, int)
            or color < 0
            for color in coloring.values()
        ):
            return False
        return all(
            coloring[left] != coloring[right]
            for left, right in self.edges
        )

    def conflicts(self, coloring: Mapping[Vertex, int]) -> list[tuple[Vertex, Vertex]]:
        """Return monochromatic edges without assuming the coloring is valid."""
        return [
            (left, right)
            for left, right in self.edges
            if left in coloring
            and right in coloring
            and coloring[left] == coloring[right]
        ]

    def greedy_coloring(
        self,
        order: Iterable[Vertex] | None = None,
    ) -> dict[Vertex, int]:
        """Color each vertex with the smallest color absent from its neighbors."""
        vertices = list(self.adjacency)
        if order is not None:
            vertices = list(order)
            if len(vertices) != len(self.adjacency) or set(vertices) != set(self.adjacency):
                raise GraphError("The coloring order must contain every vertex exactly once.")

        coloring: dict[Vertex, int] = {}
        for vertex in vertices:
            unavailable = {
                coloring[neighbor]
                for neighbor in self.adjacency[vertex]
                if neighbor in coloring
            }
            color = 0
            while color in unavailable:
                color += 1
            coloring[vertex] = color

        if not self.validate_coloring(coloring):
            raise RuntimeError("Internal error: greedy coloring is invalid.")
        return coloring

    def dsatur_coloring(self) -> dict[Vertex, int]:
        """Use saturation degree to select the next vertex dynamically."""
        coloring: dict[Vertex, int] = {}

        while len(coloring) < len(self.adjacency):
            remaining = set(self.adjacency) - set(coloring)

            def priority(vertex: Vertex) -> tuple[int, int, int]:
                saturation = len({
                    coloring[n]
                    for n in self.adjacency[vertex]
                    if n in coloring
                })
                # Stable insertion order breaks otherwise equal priorities.
                return (
                    saturation,
                    len(self.adjacency[vertex]),
                    -self._position(vertex),
                )

            vertex = max(remaining, key=priority)
            unavailable = {
                coloring[n]
                for n in self.adjacency[vertex]
                if n in coloring
            }
            color = 0
            while color in unavailable:
                color += 1
            coloring[vertex] = color

        return coloring

    def bipartition(self) -> tuple[set[Vertex], set[Vertex]] | None:
        """Return the two partitions, or None when an odd cycle exists."""
        side: dict[Vertex, int] = {}

        for start in self.adjacency:
            if start in side:
                continue

            side[start] = 0
            queue = deque([start])

            while queue:
                vertex = queue.popleft()
                for neighbor in self.adjacency[vertex]:
                    if neighbor not in side:
                        side[neighbor] = 1 - side[vertex]
                        queue.append(neighbor)
                    elif side[neighbor] == side[vertex]:
                        return None

        return (
            {v for v, partition in side.items() if partition == 0},
            {v for v, partition in side.items() if partition == 1},
        )

    def is_bipartite(self) -> bool:
        return self.bipartition() is not None

    def exact_coloring(self) -> tuple[int, dict[Vertex, int]]:
        """Find the chromatic number using symmetry-reduced backtracking.

        Exponential worst-case time is unavoidable for this general problem.
        The vertex-selection heuristic chooses the most constrained vertex.
        """
        vertices = list(self.adjacency)
        if not vertices:
            return 0, {}

        # Bipartite graphs have chromatic number at most two.
        partition = self.bipartition()
        if partition is not None:
            left, right = partition
            if not self.edges:
                return 1, {v: 0 for v in vertices}
            return 2, {
                **{v: 0 for v in left},
                **{v: 1 for v in right},
            }

        # A greedy solution supplies a finite upper bound.
        initial = self.dsatur_coloring()
        upper_bound = max(initial.values()) + 1
        best = dict(initial)

        def can_color_with(limit: int) -> dict[Vertex, int] | None:
            coloring: dict[Vertex, int] = {}

            def search() -> bool:
                if len(coloring) == len(vertices):
                    return True

                remaining = set(vertices) - set(coloring)

                def priority(vertex: Vertex) -> tuple[int, int, int]:
                    used = {
                        coloring[n]
                        for n in self.adjacency[vertex]
                        if n in coloring
                    }
                    return (
                        len(used),
                        len(self.adjacency[vertex]),
                        -self._position(vertex),
                    )

                vertex = max(remaining, key=priority)
                unavailable = {
                    coloring[n]
                    for n in self.adjacency[vertex]
                    if n in coloring
                }

                # Introducing colors in order removes equivalent color-label
                # permutations while preserving the existence of a solution.
                largest_used = max(coloring.values(), default=-1)
                for color in range(min(limit - 1, largest_used + 1) + 1):
                    if color in unavailable:
                        continue
                    coloring[vertex] = color
                    if search():
                        return True
                    del coloring[vertex]
                return False

            return dict(coloring) if search() else None

        for limit in range(1, upper_bound):
            solution = can_color_with(limit)
            if solution is not None:
                best = solution
                upper_bound = limit
                break

        # The greedy solution remains a valid upper bound if no smaller
        # coloring exists.
        return max(best.values()) + 1, best


@dataclass(frozen=True)
class Exam:
    code: str
    students: frozenset[str]


def build_exam_conflict_graph(exams: Iterable[Exam]) -> UndirectedGraph:
    """Connect exams that share at least one enrolled student."""
    exam_list = list(exams)
    graph = UndirectedGraph(exam.code for exam in exam_list)
    for left, right in combinations(exam_list, 2):
        if left.students & right.students:
            graph.add_edge(left.code, right.code)
    return graph


def print_coloring(
    title: str,
    graph: UndirectedGraph,
    coloring: Mapping[Vertex, int],
) -> None:
    print(f"\n{title}")
    for vertex in graph.vertices:
        print(f"  {vertex!s:20} -> color {coloring[vertex]}")
    print(f"  Valid: {graph.validate_coloring(coloring)}")
    print(f"  Colors used: {len(set(coloring.values()))}")


def demonstrate_fundamentals() -> None:
    print("GRAPH COLORING FUNDAMENTALS")

    triangle = UndirectedGraph(
        ["A", "B", "C"],
        [("A", "B"), ("B", "C"), ("C", "A")],
    )
    number, coloring = triangle.exact_coloring()
    print_coloring("Triangle: an odd cycle needs three colors", triangle, coloring)
    print(f"  Chromatic number: {number}")

    square = UndirectedGraph(
        ["A", "B", "C", "D"],
        [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    )
    number, coloring = square.exact_coloring()
    print_coloring("Four-cycle: a bipartite graph", square, coloring)
    print(f"  Chromatic number: {number}")
    print(f"  Bipartition: {square.bipartition()}")

    empty = UndirectedGraph()
    number, coloring = empty.exact_coloring()
    print(f"\nEmpty graph: chromatic number = {number}, coloring = {coloring}")

    isolated = UndirectedGraph(["unassigned-room", "unused-resource"])
    number, coloring = isolated.exact_coloring()
    print(f"Edgeless nonempty graph: chromatic number = {number}, coloring = {coloring}")


def demonstrate_exam_scheduling() -> None:
    exams = [
        Exam("CS101", frozenset({"Asha", "Ravi", "Meera"})),
        Exam("CS202", frozenset({"Ravi", "Kabir"})),
        Exam("MA110", frozenset({"Meera", "Kabir", "Tara"})),
        Exam("PH120", frozenset({"Asha", "Tara"})),
        Exam("EC205", frozenset({"Kabir", "Dev"})),
        Exam("HS130", frozenset({"Dev", "Asha"})),
    ]
    graph = build_exam_conflict_graph(exams)
    print("\nUNIVERSITY EXAM SCHEDULING")
    print(f"Conflicting exam pairs: {graph.edges}")

    # DSATUR prioritizes exams with the most distinct neighbor colors.
    coloring = graph.dsatur_coloring()
    print_coloring("Greedy DSATUR timetable", graph, coloring)

    slot_names = {
        0: "Monday 09:00",
        1: "Monday 13:00",
        2: "Tuesday 09:00",
        3: "Tuesday 13:00",
        4: "Wednesday 09:00",
        5: "Wednesday 13:00",
    }
    for exam in graph.vertices:
        print(f"  {exam}: {slot_names[coloring[exam]]}")

    chromatic_number, optimal = graph.exact_coloring()
    print(f"Minimum possible slots for this conflict graph: {chromatic_number}")
    print(f"Exact coloring: {optimal}")


def demonstrate_register_allocation() -> None:
    # Values whose live ranges overlap cannot occupy the same register.
    live_ranges = {
        "temperature": (0, 4),
        "pressure": (2, 6),
        "flow_rate": (4, 8),
        "threshold": (1, 3),
        "alarm_flag": (6, 9),
    }

    graph = UndirectedGraph(live_ranges)
    for (left, left_range), (right, right_range) in combinations(
        live_ranges.items(), 2
    ):
        start_left, end_left = left_range
        start_right, end_right = right_range
        # Closed intervals overlap when each begins before the other ends.
        if max(start_left, start_right) <= min(end_left, end_right):
            graph.add_edge(left, right)

    print("\nREGISTER ALLOCATION")
    coloring = graph.dsatur_coloring()
    print_coloring("Registers assigned to simultaneously live values", graph, coloring)
    for variable, register in coloring.items():
        print(f"  {variable:15} -> R{register}")


def demonstrate_validation() -> None:
    print("\nVALIDATION AND FAILURE CASES")
    graph = UndirectedGraph(["build", "test", "deploy"], [
        ("build", "test"),
        ("test", "deploy"),
    ])

    invalid = {"build": 0, "test": 0, "deploy": 1}
    print(f"Invalid coloring accepted: {graph.validate_coloring(invalid)}")
    print(f"Detected conflicts: {graph.conflicts(invalid)}")

    try:
        graph.add_edge("build", "build")
    except GraphError as exc:
        print(f"Self-loop rejected: {exc}")

    try:
        graph.greedy_coloring(["build", "test"])
    except GraphError as exc:
        print(f"Incomplete ordering rejected: {exc}")

    try:
        graph.degree("missing")
    except GraphError as exc:
        print(f"Unknown vertex rejected: {exc}")

    odd_cycle = UndirectedGraph(
        ["P", "Q", "R"],
        [("P", "Q"), ("Q", "R"), ("R", "P")],
    )
    print(f"Odd cycle is bipartite: {odd_cycle.is_bipartite()}")

    # A coloring can use more colors than necessary and still be valid.
    overcolored = {"build": 0, "test": 2, "deploy": 4}
    print(f"Overcolored assignment is valid: {graph.validate_coloring(overcolored)}")


def demonstrate_complexity() -> None:
    print("\nALGORITHM CHARACTERISTICS")
    print("Bipartite test: O(V + E) time and O(V) auxiliary space.")
    print("Greedy coloring: O(V + E) with adjacency-set membership and bounded")
    print("  color bookkeeping in typical sparse graphs; color-set construction")
    print("  can cost more as the number of distinct neighbor colors grows.")
    print("DSATUR heuristic: generally much faster than exhaustive search, but")
    print("  its result is not guaranteed to be optimal.")
    print("Exact chromatic number: exponential worst-case search.")
    print("Applications: exam timetables, register allocation, frequency planning,")
    print("  map coloring, and conflict-free resource assignment.")


def main() -> None:
    demonstrate_fundamentals()
    demonstrate_exam_scheduling()
    demonstrate_register_allocation()
    demonstrate_validation()
    demonstrate_complexity()


if __name__ == "__main__":
    main()
