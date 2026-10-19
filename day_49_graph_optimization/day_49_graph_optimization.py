from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from heapq import heappop, heappush
from math import inf
from collections import defaultdict, deque
from typing import Dict, Iterable, List, Optional, Tuple


class GraphError(ValueError):
    """Raised when a graph operation receives invalid input."""


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    weight: float


class WeightedGraph:
    """Adjacency-list representation of a weighted directed or undirected graph."""

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self._adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self._edges: List[Edge] = []

    def add_vertex(self, vertex: str) -> None:
        if not vertex:
            raise GraphError("Vertex names cannot be empty.")
        self._adj.setdefault(vertex, [])

    def add_edge(self, source: str, target: str, weight: float) -> None:
        if not source or not target:
            raise GraphError("Both endpoints are required.")
        if weight < 0:
            raise GraphError(
                "This graph implementation uses non-negative weights so "
                "Dijkstra's algorithm remains valid."
            )

        self.add_vertex(source)
        self.add_vertex(target)
        self._adj[source].append((target, weight))
        self._edges.append(Edge(source, target, weight))

        if not self.directed:
            self._adj[target].append((source, weight))

    @property
    def vertices(self) -> List[str]:
        return list(self._adj)

    @property
    def edges(self) -> List[Edge]:
        return list(self._edges)

    def neighbors(self, vertex: str) -> List[Tuple[str, float]]:
        if vertex not in self._adj:
            raise GraphError(f"Unknown vertex: {vertex}")
        return list(self._adj[vertex])


def reconstruct_path(
    previous: Dict[str, Optional[str]],
    source: str,
    target: str,
) -> List[str]:
    if target not in previous:
        return []

    path: List[str] = []
    current: Optional[str] = target

    while current is not None:
        path.append(current)
        if current == source:
            path.reverse()
            return path
        current = previous.get(current)

    return []


def dijkstra(
    graph: WeightedGraph,
    source: str,
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Single-source shortest paths for graphs with non-negative edge weights.

    The heap stores candidate (distance, vertex) pairs. A stale heap entry
    is ignored when its distance is larger than the currently known distance.
    """

    if source not in graph.vertices:
        raise GraphError(f"Unknown source vertex: {source}")

    distances = {vertex: inf for vertex in graph.vertices}
    previous: Dict[str, Optional[str]] = {
        vertex: None for vertex in graph.vertices
    }
    distances[source] = 0.0

    heap: List[Tuple[float, str]] = [(0.0, source)]

    while heap:
        current_distance, current = heappop(heap)

        if current_distance != distances[current]:
            continue

        for neighbor, weight in graph.neighbors(current):
            candidate = current_distance + weight

            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = current
                heappush(heap, (candidate, neighbor))

    return distances, previous


def bellman_ford(
    graph: WeightedGraph,
    source: str,
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Bellman-Ford supports negative edge weights and detects negative cycles.

    The graph class normally rejects negative weights because its primary
    shortest-path demonstration targets Dijkstra. This function therefore
    accepts a separate edge collection so the algorithm itself remains
    available for educational comparison.
    """

    vertices = graph.vertices
    if source not in vertices:
        raise GraphError(f"Unknown source vertex: {source}")

    distances = {vertex: inf for vertex in vertices}
    previous: Dict[str, Optional[str]] = {vertex: None for vertex in vertices}
    distances[source] = 0.0

    for _ in range(len(vertices) - 1):
        changed = False

        for edge in graph.edges:
            if distances[edge.source] == inf:
                continue

            candidate = distances[edge.source] + edge.weight
            if candidate < distances[edge.target]:
                distances[edge.target] = candidate
                previous[edge.target] = edge.source
                changed = True

        if not changed:
            break

    for edge in graph.edges:
        if (
            distances[edge.source] != inf
            and distances[edge.source] + edge.weight < distances[edge.target]
        ):
            raise GraphError("Negative-weight cycle detected.")

    return distances, previous


class DisjointSetUnion:
    """Union-Find structure used by Kruskal's minimum spanning tree algorithm."""

    def __init__(self, vertices: Iterable[str]) -> None:
        self.parent = {vertex: vertex for vertex in vertices}
        self.rank = {vertex: 0 for vertex in vertices}

    def find(self, vertex: str) -> str:
        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])
        return self.parent[vertex]

    def union(self, first: str, second: str) -> bool:
        root_first = self.find(first)
        root_second = self.find(second)

        if root_first == root_second:
            return False

        if self.rank[root_first] < self.rank[root_second]:
            root_first, root_second = root_second, root_first

        self.parent[root_second] = root_first

        if self.rank[root_first] == self.rank[root_second]:
            self.rank[root_first] += 1

        return True


def kruskal_mst(
    graph: WeightedGraph,
) -> Tuple[List[Edge], float]:
    if graph.directed:
        raise GraphError("Minimum spanning trees require an undirected graph.")

    dsu = DisjointSetUnion(graph.vertices)
    chosen: List[Edge] = []
    total_weight = 0.0

    for edge in sorted(graph.edges, key=lambda item: item.weight):
        if dsu.union(edge.source, edge.target):
            chosen.append(edge)
            total_weight += edge.weight

            if len(chosen) == len(graph.vertices) - 1:
                break

    if len(chosen) != max(0, len(graph.vertices) - 1):
        raise GraphError("The graph is disconnected; no spanning tree exists.")

    return chosen, total_weight


def prim_mst(graph: WeightedGraph) -> Tuple[List[Edge], float]:
    if graph.directed:
        raise GraphError("Minimum spanning trees require an undirected graph.")
    if not graph.vertices:
        return [], 0.0

    start = graph.vertices[0]
    visited = {start}
    heap: List[Tuple[float, str, str]] = []

    for neighbor, weight in graph.neighbors(start):
        heappush(heap, (weight, start, neighbor))

    chosen: List[Edge] = []
    total_weight = 0.0

    while heap and len(visited) < len(graph.vertices):
        weight, source, target = heappop(heap)

        if target in visited:
            continue

        visited.add(target)
        chosen.append(Edge(source, target, weight))
        total_weight += weight

        for neighbor, neighbor_weight in graph.neighbors(target):
            if neighbor not in visited:
                heappush(heap, (neighbor_weight, target, neighbor))

    if len(visited) != len(graph.vertices):
        raise GraphError("The graph is disconnected; no spanning tree exists.")

    return chosen, total_weight


def floyd_warshall(
    graph: WeightedGraph,
) -> Dict[str, Dict[str, float]]:
    """
    All-pairs shortest paths.

    The implementation materializes a distance matrix and repeatedly allows
    each vertex to become an intermediate point. Its O(V^3) cost makes it
    useful for dense graphs and smaller networks where many source-target
    queries are expected.
    """

    vertices = graph.vertices
    distances = {
        source: {target: inf for target in vertices}
        for source in vertices
    }

    for vertex in vertices:
        distances[vertex][vertex] = 0.0

    for edge in graph.edges:
        distances[edge.source][edge.target] = min(
            distances[edge.source][edge.target],
            edge.weight,
        )
        if not graph.directed:
            distances[edge.target][edge.source] = min(
                distances[edge.target][edge.source],
                edge.weight,
            )

    for intermediate in vertices:
        for source in vertices:
            if distances[source][intermediate] == inf:
                continue

            for target in vertices:
                candidate = (
                    distances[source][intermediate]
                    + distances[intermediate][target]
                )
                if candidate < distances[source][target]:
                    distances[source][target] = candidate

    for vertex in vertices:
        if distances[vertex][vertex] < 0:
            raise GraphError("Negative cycle detected.")

    return distances


@dataclass
class NetworkDemand:
    source: str
    target: str
    units: int


@dataclass
class CapacityEdge:
    source: str
    target: str
    capacity: int
    cost: float


def max_flow(
    vertices: Iterable[str],
    edges: Iterable[CapacityEdge],
    source: str,
    sink: str,
) -> Tuple[int, Dict[Tuple[str, str], int]]:
    """
    Edmonds-Karp maximum-flow implementation.

    Residual capacities are represented explicitly. Reverse residual edges
    allow previously selected flow to be rerouted when a later augmenting
    path provides a better allocation.
    """

    vertex_list = list(vertices)
    if source not in vertex_list or sink not in vertex_list:
        raise GraphError("Source and sink must exist.")
    if source == sink:
        raise GraphError("Source and sink must be different.")

    residual: Dict[str, Dict[str, int]] = {
        vertex: defaultdict(int) for vertex in vertex_list
    }
    original: Dict[Tuple[str, str], int] = {}

    for edge in edges:
        if edge.capacity < 0:
            raise GraphError("Capacity cannot be negative.")
        residual[edge.source][edge.target] += edge.capacity
        residual[edge.target].setdefault(edge.source, 0)
        original[(edge.source, edge.target)] = (
            original.get((edge.source, edge.target), 0) + edge.capacity
        )

    total = 0

    while True:
        parent: Dict[str, Optional[str]] = {source: None}
        queue = deque([source])

        while queue and sink not in parent:
            current = queue.popleft()

            for neighbor, capacity in residual[current].items():
                if capacity > 0 and neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

                    if neighbor == sink:
                        break

        if sink not in parent:
            break

        bottleneck = inf
        current = sink

        while current != source:
            previous = parent[current]
            assert previous is not None
            bottleneck = min(bottleneck, residual[previous][current])
            current = previous

        current = sink
        while current != source:
            previous = parent[current]
            assert previous is not None
            residual[previous][current] -= int(bottleneck)
            residual[current][previous] += int(bottleneck)
            current = previous

        total += int(bottleneck)

    flow: Dict[Tuple[str, str], int] = {}

    for (u, v), capacity in original.items():
        remaining = residual[u][v]
        flow[(u, v)] = capacity - remaining

    return total, flow


def print_shortest_path_demo() -> None:
    graph = WeightedGraph(directed=True)

    roads = [
        ("Warehouse", "Hub-A", 4),
        ("Warehouse", "Hub-B", 2),
        ("Hub-A", "Hub-C", 3),
        ("Hub-B", "Hub-A", 1),
        ("Hub-B", "Hub-C", 5),
        ("Hub-C", "Store", 2),
        ("Hub-A", "Store", 9),
    ]

    for source, target, weight in roads:
        graph.add_edge(source, target, weight)

    distances, previous = dijkstra(graph, "Warehouse")

    print("Shortest-path analysis")
    for destination in graph.vertices:
        path = reconstruct_path(previous, "Warehouse", destination)
        distance = distances[destination]
        readable_distance = "unreachable" if distance == inf else f"{distance:.1f}"
        print(f"  Warehouse -> {destination}: {readable_distance} via {path}")


def print_mst_demo() -> None:
    network = WeightedGraph(directed=False)

    links = [
        ("Delhi", "Agra", 3),
        ("Delhi", "Jaipur", 5),
        ("Agra", "Jaipur", 2),
        ("Agra", "Lucknow", 6),
        ("Jaipur", "Lucknow", 4),
        ("Jaipur", "Bhopal", 7),
        ("Lucknow", "Bhopal", 3),
        ("Lucknow", "Patna", 5),
        ("Bhopal", "Patna", 2),
    ]

    for source, target, weight in links:
        network.add_edge(source, target, weight)

    kruskal_edges, kruskal_cost = kruskal_mst(network)
    prim_edges, prim_cost = prim_mst(network)

    print("\nMinimum spanning tree")
    print("  Kruskal:")
    for edge in kruskal_edges:
        print(f"    {edge.source} -- {edge.target}: {edge.weight}")
    print(f"    total construction cost = {kruskal_cost}")

    print("  Prim:")
    for edge in prim_edges:
        print(f"    {edge.source} -- {edge.target}: {edge.weight}")
    print(f"    total construction cost = {prim_cost}")


def print_all_pairs_demo() -> None:
    graph = WeightedGraph(directed=True)

    for source, target, weight in [
        ("A", "B", 7),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 2),
        ("C", "B", 3),
        ("C", "D", 8),
        ("D", "A", 4),
    ]:
        graph.add_edge(source, target, weight)

    distances = floyd_warshall(graph)

    print("\nAll-pairs shortest-path matrix")
    print("       " + " ".join(f"{v:>7}" for v in graph.vertices))
    for source in graph.vertices:
        values = []
        for target in graph.vertices:
            value = distances[source][target]
            values.append("INF" if value == inf else f"{value:7.1f}")
        print(f"{source:>5} " + " ".join(values))


def print_flow_demo() -> None:
    vertices = ["Source", "North", "South", "Central", "East", "Sink"]

    capacities = [
        CapacityEdge("Source", "North", 12, 0),
        CapacityEdge("Source", "South", 8, 0),
        CapacityEdge("North", "Central", 7, 0),
        CapacityEdge("North", "East", 5, 0),
        CapacityEdge("South", "Central", 4, 0),
        CapacityEdge("South", "East", 6, 0),
        CapacityEdge("Central", "Sink", 8, 0),
        CapacityEdge("East", "Sink", 10, 0),
    ]

    total, flow = max_flow(vertices, capacities, "Source", "Sink")

    print("\nNetwork capacity optimization")
    print(f"  maximum simultaneous flow = {total}")
    for edge, amount in flow.items():
        if amount:
            print(f"  {edge[0]} -> {edge[1]}: {amount}")


def demonstrate_failure_conditions() -> None:
    print("\nFailure conditions and validation")

    try:
        graph = WeightedGraph(directed=False)
        graph.add_edge("A", "B", -3)
    except GraphError as exc:
        print(f"  rejected negative Dijkstra edge: {exc}")

    try:
        disconnected = WeightedGraph(directed=False)
        disconnected.add_edge("A", "B", 1)
        disconnected.add_vertex("C")
        kruskal_mst(disconnected)
    except GraphError as exc:
        print(f"  rejected disconnected MST request: {exc}")

    try:
        empty = WeightedGraph(directed=True)
        dijkstra(empty, "missing")
    except GraphError as exc:
        print(f"  rejected unknown source: {exc}")


def main() -> None:
    print_shortest_path_demo()
    print_mst_demo()
    print_all_pairs_demo()
    print_flow_demo()
    demonstrate_failure_conditions()

    print("\nAlgorithm selection")
    print("  Dijkstra: non-negative weighted single-source shortest paths.")
    print("  Bellman-Ford: negative edges and negative-cycle detection.")
    print("  Floyd-Warshall: many all-pairs queries on smaller graphs.")
    print("  Kruskal: MST using globally sorted edges and Union-Find.")
    print("  Prim: MST by expanding the cheapest frontier edge.")
    print("  Edmonds-Karp: maximum flow under explicit capacity constraints.")


if __name__ == "__main__":
    main()
