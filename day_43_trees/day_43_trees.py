#!/usr/bin/env python3
"""
Trees: rooted trees, binary trees, spanning trees, and tree properties.

A self-contained implementation covering tree construction, traversal,
validation, structural properties, binary search trees, and spanning-tree
algorithms. Uses only the Python standard library.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import ceil, log2
from typing import Iterable


class TreeError(ValueError):
    """Raised when an operation violates a tree-specific constraint."""


class DisjointSet:
    """Union-find with path compression and union by rank."""

    def __init__(self, vertices: Iterable[str]) -> None:
        self.parent = {vertex: vertex for vertex in vertices}
        self.rank = {vertex: 0 for vertex in self.parent}
        self.components = len(self.parent)

    def find(self, vertex: str) -> str:
        if vertex not in self.parent:
            raise KeyError(f"Unknown vertex: {vertex}")

        while self.parent[vertex] != vertex:
            self.parent[vertex] = self.parent[self.parent[vertex]]
            vertex = self.parent[vertex]
        return vertex

    def union(self, first: str, second: str) -> bool:
        root_a = self.find(first)
        root_b = self.find(second)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a

        self.parent[root_b] = root_a

        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1

        self.components -= 1
        return True


class UndirectedGraph:
    """Undirected graph supporting tree checks and spanning-tree algorithms."""

    def __init__(self, vertices: Iterable[str]) -> None:
        self.vertices = list(dict.fromkeys(vertices))

        if any(not isinstance(v, str) or not v for v in self.vertices):
            raise TreeError("Vertex labels must be nonempty strings.")

        self.adjacency: dict[str, set[str]] = {
            vertex: set() for vertex in self.vertices
        }
        self.edges: list[tuple[str, str, float]] = []

    def add_edge(self, first: str, second: str, weight: float = 1) -> None:
        if first not in self.adjacency or second not in self.adjacency:
            raise TreeError("Both endpoints must belong to the graph.")
        if first == second:
            raise TreeError("Self-loops are not allowed in this graph model.")
        if any(not isinstance(weight, (int, float)) for _ in [0]):
            raise TreeError("Edge weight must be numeric.")
        if not float(weight) == float(weight) or weight in (float("inf"), float("-inf")):
            raise TreeError("Edge weight must be finite.")

        if second in self.adjacency[first]:
            raise TreeError(f"Duplicate edge: {first}-{second}")

        self.adjacency[first].add(second)
        self.adjacency[second].add(first)
        self.edges.append((first, second, float(weight)))

    def connected_components(self) -> list[set[str]]:
        unseen = set(self.vertices)
        components = []

        while unseen:
            start = next(iter(unseen))
            component = set()
            queue = deque([start])
            unseen.remove(start)

            while queue:
                vertex = queue.popleft()
                component.add(vertex)

                for neighbor in self.adjacency[vertex]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        queue.append(neighbor)

            components.append(component)

        return components

    def is_connected(self) -> bool:
        return len(self.connected_components()) <= 1

    def has_cycle(self) -> bool:
        visited = set()

        for start in self.vertices:
            if start in visited:
                continue

            stack = [(start, None)]
            while stack:
                vertex, parent = stack.pop()

                if vertex in visited:
                    continue

                visited.add(vertex)

                for neighbor in self.adjacency[vertex]:
                    if neighbor == parent:
                        continue
                    if neighbor in visited:
                        return True
                    stack.append((neighbor, vertex))

        return False

    def is_tree(self) -> bool:
        if not self.vertices:
            return False
        return len(self.edges) == len(self.vertices) - 1 and self.is_connected()

    def bfs(self, start: str) -> list[str]:
        if start not in self.adjacency:
            raise TreeError(f"Unknown start vertex: {start}")

        visited = {start}
        queue = deque([start])
        order = []

        while queue:
            vertex = queue.popleft()
            order.append(vertex)

            for neighbor in sorted(self.adjacency[vertex]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def dfs(self, start: str) -> list[str]:
        if start not in self.adjacency:
            raise TreeError(f"Unknown start vertex: {start}")

        visited = set()
        order = []
        stack = [start]

        while stack:
            vertex = stack.pop()

            if vertex in visited:
                continue

            visited.add(vertex)
            order.append(vertex)
            stack.extend(sorted(self.adjacency[vertex] - visited, reverse=True))

        return order

    def path_between(self, start: str, target: str) -> list[str] | None:
        if start not in self.adjacency or target not in self.adjacency:
            raise TreeError("Both path endpoints must exist.")

        parent: dict[str, str | None] = {start: None}
        queue = deque([start])

        while queue:
            vertex = queue.popleft()
            if vertex == target:
                path = []
                current: str | None = target
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return list(reversed(path))

            for neighbor in self.adjacency[vertex]:
                if neighbor not in parent:
                    parent[neighbor] = vertex
                    queue.append(neighbor)

        return None

    def kruskal_mst(self) -> tuple[list[tuple[str, str, float]], float]:
        if not self.vertices:
            return [], 0.0

        dsu = DisjointSet(self.vertices)
        chosen = []
        total_weight = 0.0

        for first, second, weight in sorted(
            self.edges, key=lambda edge: (edge[2], edge[0], edge[1])
        ):
            if dsu.union(first, second):
                chosen.append((first, second, weight))
                total_weight += weight

        if len(chosen) != len(self.vertices) - 1:
            raise TreeError("A spanning tree does not exist for a disconnected graph.")

        return chosen, total_weight

    def prim_mst(self) -> tuple[list[tuple[str, str, float]], float]:
        """Prim's algorithm using an adjacency scan; O(V^2 + E)."""
        if not self.vertices:
            return [], 0.0

        import heapq

        start = self.vertices[0]
        visited = {start}
        candidates = []
        chosen = []
        total_weight = 0.0

        for neighbor in self.adjacency[start]:
            weight = next(
                edge[2] for edge in self.edges
                if {edge[0], edge[1]} == {start, neighbor}
            )
            heapq.heappush(candidates, (weight, start, neighbor))

        while candidates and len(visited) < len(self.vertices):
            weight, first, second = heapq.heappop(candidates)

            if second in visited:
                continue

            visited.add(second)
            chosen.append((first, second, weight))
            total_weight += weight

            for neighbor in self.adjacency[second]:
                if neighbor in visited:
                    continue
                edge_weight = next(
                    edge[2] for edge in self.edges
                    if {edge[0], edge[1]} == {second, neighbor}
                )
                heapq.heappush(candidates, (edge_weight, second, neighbor))

        if len(visited) != len(self.vertices):
            raise TreeError("A spanning tree does not exist for a disconnected graph.")

        return chosen, total_weight


@dataclass
class RootedTreeNode:
    """A node in a rooted, ordered tree."""

    value: str
    children: list[RootedTreeNode] = field(default_factory=list)
    parent: RootedTreeNode | None = field(default=None, repr=False)

    def add_child(self, child: RootedTreeNode) -> None:
        if child is self:
            raise TreeError("A node cannot be its own child.")
        if child.parent is not None:
            raise TreeError("A child cannot be attached to multiple parents.")

        ancestor: RootedTreeNode | None = self
        while ancestor is not None:
            if ancestor is child:
                raise TreeError("Attaching this child would create a cycle.")
            ancestor = ancestor.parent

        child.parent = self
        self.children.append(child)


def rooted_tree_metrics(root: RootedTreeNode) -> dict[str, int]:
    """Return node count, edge count, height, and leaf count."""
    node_count = 0
    leaf_count = 0
    maximum_depth = 0
    seen = set()
    stack = [(root, 0)]

    while stack:
        node, depth = stack.pop()

        if id(node) in seen:
            raise TreeError("The rooted structure contains a cycle or shared node.")
        seen.add(id(node))

        node_count += 1
        maximum_depth = max(maximum_depth, depth)

        if not node.children:
            leaf_count += 1

        for child in node.children:
            if child.parent is not node:
                raise TreeError("Parent-child references are inconsistent.")
            stack.append((child, depth + 1))

    return {
        "nodes": node_count,
        "edges": node_count - 1,
        "height": maximum_depth,
        "leaves": leaf_count,
    }


def rooted_preorder(root: RootedTreeNode) -> list[str]:
    order = []
    stack = [root]

    while stack:
        node = stack.pop()
        order.append(node.value)
        stack.extend(reversed(node.children))

    return order


def rooted_postorder(root: RootedTreeNode) -> list[str]:
    order = []
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if expanded:
            order.append(node.value)
        else:
            stack.append((node, True))
            for child in reversed(node.children):
                stack.append((child, False))

    return order


@dataclass
class BinaryNode:
    """A binary-tree node with at most one child per side."""

    key: int
    left: BinaryNode | None = None
    right: BinaryNode | None = None


def binary_inorder(root: BinaryNode | None) -> list[int]:
    result = []
    stack = []
    current = root

    while current is not None or stack:
        while current is not None:
            stack.append(current)
            current = current.left

        current = stack.pop()
        result.append(current.key)
        current = current.right

    return result


def binary_preorder(root: BinaryNode | None) -> list[int]:
    if root is None:
        return []

    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.key)

        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)

    return result


def binary_postorder(root: BinaryNode | None) -> list[int]:
    if root is None:
        return []

    result = []
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if expanded:
            result.append(node.key)
        else:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))

    return result


def binary_level_order(root: BinaryNode | None) -> list[int]:
    if root is None:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.key)

        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)

    return result


def binary_metrics(root: BinaryNode | None) -> dict[str, int | bool]:
    """Measure height in edges, node count, and structural properties."""
    if root is None:
        return {
            "nodes": 0,
            "height": -1,
            "leaves": 0,
            "full": True,
            "complete": True,
            "perfect": True,
            "balanced": True,
        }

    nodes = []
    queue = deque([(root, 0)])
    leaf_count = 0
    full = True
    complete = True
    balanced = True
    gap_seen = False
    first_unbalanced = False
    heights: dict[int, int] = {}

    while queue:
        node, depth = queue.popleft()
        nodes.append((node, depth))

        has_left = node.left is not None
        has_right = node.right is not None

        if not has_left and not has_right:
            leaf_count += 1
        if has_left != has_right:
            full = False

        for child in (node.left, node.right):
            if child is None:
                gap_seen = True
            else:
                if gap_seen:
                    complete = False
                queue.append((child, depth + 1))

    # Compute subtree heights in postorder without recursion.
    stack = [(root, False)]
    while stack:
        node, expanded = stack.pop()
        if expanded:
            left_height = heights.get(id(node.left), -1)
            right_height = heights.get(id(node.right), -1)
            if abs(left_height - right_height) > 1:
                balanced = False
            heights[id(node)] = 1 + max(left_height, right_height)
        else:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))

    height = heights[id(root)]
    perfect = len(nodes) == 2 ** (height + 1) - 1

    return {
        "nodes": len(nodes),
        "height": height,
        "leaves": leaf_count,
        "full": full,
        "complete": complete,
        "perfect": perfect,
        "balanced": balanced,
    }


class BinarySearchTree:
    """Unbalanced binary search tree with duplicate-key rejection."""

    def __init__(self) -> None:
        self.root: BinaryNode | None = None
        self.size = 0

    def insert(self, key: int) -> bool:
        if self.root is None:
            self.root = BinaryNode(key)
            self.size = 1
            return True

        current = self.root

        while True:
            if key == current.key:
                return False
            if key < current.key:
                if current.left is None:
                    current.left = BinaryNode(key)
                    self.size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = BinaryNode(key)
                    self.size += 1
                    return True
                current = current.right

    def contains(self, key: int) -> bool:
        current = self.root

        while current is not None:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right

        return False

    def minimum(self) -> int:
        if self.root is None:
            raise TreeError("An empty search tree has no minimum.")

        current = self.root
        while current.left is not None:
            current = current.left
        return current.key

    def maximum(self) -> int:
        if self.root is None:
            raise TreeError("An empty search tree has no maximum.")

        current = self.root
        while current.right is not None:
            current = current.right
        return current.key

    def delete(self, key: int) -> bool:
        parent: BinaryNode | None = None
        current = self.root

        while current is not None and current.key != key:
            parent = current
            current = current.left if key < current.key else current.right

        if current is None:
            return False

        # For two children, copy the inorder successor and remove its node.
        if current.left is not None and current.right is not None:
            successor_parent = current
            successor = current.right

            while successor.left is not None:
                successor_parent = successor
                successor = successor.left

            current.key = successor.key
            parent = successor_parent
            current = successor

        replacement = current.left if current.left is not None else current.right

        if parent is None:
            self.root = replacement
        elif parent.left is current:
            parent.left = replacement
        else:
            parent.right = replacement

        self.size -= 1
        return True


def tree_diameter(root: BinaryNode | None) -> int:
    """Return the longest path between two nodes, measured in edges."""
    if root is None:
        return 0

    heights: dict[int, int] = {}
    diameter = 0
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if expanded:
            left_height = heights.get(id(node.left), -1) + 1
            right_height = heights.get(id(node.right), -1) + 1
            diameter = max(diameter, left_height + right_height)
            heights[id(node)] = 1 + max(left_height, right_height)
        else:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))

    return diameter


def demonstrate_rooted_tree() -> None:
    print("\nROOTED TREE")

    company = RootedTreeNode("Engineering")
    backend = RootedTreeNode("Backend")
    frontend = RootedTreeNode("Frontend")
    infrastructure = RootedTreeNode("Infrastructure")

    company.add_child(backend)
    company.add_child(frontend)
    company.add_child(infrastructure)

    backend.add_child(RootedTreeNode("API"))
    backend.add_child(RootedTreeNode("Database"))
    infrastructure.add_child(RootedTreeNode("Deployment"))

    print("Preorder:", rooted_preorder(company))
    print("Postorder:", rooted_postorder(company))
    print("Metrics:", rooted_tree_metrics(company))


def demonstrate_binary_tree() -> None:
    print("\nBINARY TREE")

    root = BinaryNode(
        20,
        BinaryNode(10, BinaryNode(5), BinaryNode(15)),
        BinaryNode(30, BinaryNode(25), BinaryNode(35)),
    )

    print("Preorder:", binary_preorder(root))
    print("Inorder:", binary_inorder(root))
    print("Postorder:", binary_postorder(root))
    print("Level order:", binary_level_order(root))
    print("Properties:", binary_metrics(root))
    print("Diameter in edges:", tree_diameter(root))

    # A binary search tree is a binary tree with an ordering invariant.
    search_tree = BinarySearchTree()
    for key in [40, 20, 60, 10, 30, 50, 70, 25]:
        search_tree.insert(key)

    print("BST inorder:", binary_inorder(search_tree.root))
    print("BST contains 25:", search_tree.contains(25))
    print("Duplicate insertion accepted:", search_tree.insert(30))
    print("Delete node with two children:", search_tree.delete(20))
    print("BST after deletion:", binary_inorder(search_tree.root))


def demonstrate_spanning_trees() -> None:
    print("\nSPANNING TREES")

    network = UndirectedGraph(["A", "B", "C", "D", "E"])
    network.add_edge("A", "B", 4)
    network.add_edge("A", "C", 2)
    network.add_edge("B", "C", 1)
    network.add_edge("B", "D", 5)
    network.add_edge("C", "D", 8)
    network.add_edge("C", "E", 10)
    network.add_edge("D", "E", 2)
    network.add_edge("B", "E", 7)

    print("Connected:", network.is_connected())
    print("Has cycle:", network.has_cycle())
    print("Is a tree:", network.is_tree())
    print("BFS from A:", network.bfs("A"))
    print("DFS from A:", network.dfs("A"))
    print("Path A to E:", network.path_between("A", "E"))

    kruskal_edges, kruskal_cost = network.kruskal_mst()
    prim_edges, prim_cost = network.prim_mst()

    print("Kruskal MST:", kruskal_edges, "total weight:", kruskal_cost)
    print("Prim MST:", prim_edges, "total weight:", prim_cost)

    assert kruskal_cost == prim_cost

    # A spanning tree for a graph with V vertices has exactly V - 1 edges.
    assert len(kruskal_edges) == len(network.vertices) - 1


def demonstrate_tree_properties() -> None:
    print("\nTREE PROPERTIES")

    graph = UndirectedGraph(["server-a", "server-b", "server-c", "server-d"])
    graph.add_edge("server-a", "server-b")
    graph.add_edge("server-b", "server-c")
    graph.add_edge("server-c", "server-d")

    print("A connected acyclic graph:", graph.is_tree())
    print("Edges equal vertices minus one:",
          len(graph.edges) == len(graph.vertices) - 1)
    print("Path across the tree:", graph.path_between("server-a", "server-d"))

    cyclic = UndirectedGraph(["a", "b", "c"])
    cyclic.add_edge("a", "b")
    cyclic.add_edge("b", "c")
    cyclic.add_edge("c", "a")
    print("Triangle has cycle:", cyclic.has_cycle())
    print("Triangle is tree:", cyclic.is_tree())

    disconnected = UndirectedGraph(["a", "b", "c"])
    disconnected.add_edge("a", "b")
    try:
        disconnected.kruskal_mst()
    except TreeError as exc:
        print("Disconnected graph rejected:", exc)

    print("Minimum height of a binary tree with 15 nodes:",
          ceil(log2(15 + 1)) - 1)


def run_self_tests() -> None:
    empty = BinarySearchTree()
    assert not empty.contains(1)

    try:
        empty.minimum()
    except TreeError:
        pass
    else:
        raise AssertionError("An empty tree must not have a minimum.")

    tree = BinarySearchTree()
    for value in [8, 4, 12, 2, 6, 10, 14, 5]:
        assert tree.insert(value)

    assert not tree.insert(6)
    assert tree.contains(5)
    assert tree.delete(4)
    assert not tree.contains(4)
    assert binary_inorder(tree.root) == [2, 5, 6, 8, 10, 12, 14]

    graph = UndirectedGraph(["x", "y"])
    graph.add_edge("x", "y", 3)
    assert graph.is_tree()

    try:
        graph.add_edge("x", "x")
    except TreeError:
        pass
    else:
        raise AssertionError("Self-loops must be rejected.")

    assert tree_diameter(BinaryNode(1, BinaryNode(2), BinaryNode(3))) == 2
    print("\nAll self-tests passed.")


def main() -> None:
    demonstrate_rooted_tree()
    demonstrate_binary_tree()
    demonstrate_spanning_trees()
    demonstrate_tree_properties()
    run_self_tests()


if __name__ == "__main__":
    main()
