"""
Discrete Mathematical Structures in Computer Science
=====================================================

A self-contained executable study file covering:
- Sets and set operations
- Relations and their properties
- Equivalence relations and partitions
- Partial orders and Hasse-style reasoning
- Functions and mappings
- Injective, surjective, and bijective functions
- Composition and inverse functions
- Propositional logic
- Predicate logic and quantifiers
- Logical equivalence and inference
- Mathematical structures used in computer science
- Graphs, trees, and algebraic structures
- Cardinality and finite counting ideas
- Boolean algebra
- Recursion and induction
- Algorithms and complexity connections
- Validation, edge cases, testing, and practical applications

The examples are intentionally executable. Running this file prints demonstrations
and assertions that verify important mathematical properties.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from collections import defaultdict, deque
from functools import reduce
from typing import Any, Callable, Iterable, TypeVar
import math


T = TypeVar("T")
U = TypeVar("U")


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print(f"\n--- {title} ---")


# ============================================================================
# 1. SETS
# ============================================================================

section("1. SETS: FUNDAMENTAL CONCEPTS")

# A set is an unordered collection of distinct objects.
# Python's built-in set directly models the mathematical idea.
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

print("A =", A)
print("B =", B)
print("Union:", A | B)
print("Intersection:", A & B)
print("A - B:", A - B)
print("B - A:", B - A)
print("Symmetric difference:", A ^ B)

# Membership asks whether an element belongs to a set.
print("3 in A:", 3 in A)
print("9 in A:", 9 in A)

# Subset and proper-subset relationships.
C = {1, 2}
print("C subset of A:", C <= A)
print("C proper subset of A:", C < A)

# Superset relationships.
print("A superset of C:", A >= C)

# Cardinality is the number of elements in a finite set.
print("|A| =", len(A))

# Duplicate values disappear because sets contain distinct elements.
duplicate_example = {1, 1, 2, 2, 3}
print("Duplicates removed:", duplicate_example)

# Empty set must be created with set(), because {} means an empty dictionary.
empty_set = set()
print("Empty set:", empty_set)

# Frozen sets are immutable and therefore hashable.
immutable_set = frozenset({1, 2, 3})
print("Frozen set:", immutable_set)


def powerset(values: Iterable[T]) -> list[frozenset[T]]:
    """Return the power set P(S), containing every subset of S."""
    items = list(values)
    result: list[frozenset[T]] = []

    for mask in range(1 << len(items)):
        subset = frozenset(
            items[index]
            for index in range(len(items))
            if mask & (1 << index)
        )
        result.append(subset)

    return result


subsection("Power Sets")

small_set = {1, 2, 3}
P = powerset(small_set)
print("S =", small_set)
print("P(S) =", P)
print("|P(S)| =", len(P))
print("2^|S| =", 2 ** len(small_set))

assert len(P) == 2 ** len(small_set)


def cartesian_product(
    left: Iterable[T],
    right: Iterable[U],
) -> list[tuple[T, U]]:
    """Return A x B, the Cartesian product of two finite collections."""
    return list(product(left, right))


subsection("Cartesian Products")

X = {"A", "B"}
Y = {1, 2, 3}
XY = cartesian_product(X, Y)

print("X =", X)
print("Y =", Y)
print("X × Y =", XY)
print("|X × Y| =", len(XY))

assert len(XY) == len(X) * len(Y)


# ============================================================================
# 2. RELATIONS
# ============================================================================

section("2. RELATIONS")

# A binary relation from A to B is any subset of A × B.
# A relation on A is a subset of A × A.

Relation = set[tuple[Any, Any]]


def relation_domain(relation: Relation) -> set[Any]:
    return {x for x, _ in relation}


def relation_range(relation: Relation) -> set[Any]:
    return {y for _, y in relation}


def is_reflexive(domain: set[T], relation: Relation) -> bool:
    return all((x, x) in relation for x in domain)


def is_irreflexive(domain: set[T], relation: Relation) -> bool:
    return all((x, x) not in relation for x in domain)


def is_symmetric(relation: Relation) -> bool:
    return all((y, x) in relation for x, y in relation)


def is_antisymmetric(relation: Relation) -> bool:
    return all(
        x == y or (y, x) not in relation
        for x, y in relation
    )


def is_asymmetric(relation: Relation) -> bool:
    return all((y, x) not in relation for x, y in relation)


def is_transitive(relation: Relation) -> bool:
    for x, y in relation:
        for y2, z in relation:
            if y == y2 and (x, z) not in relation:
                return False
    return True


def is_equivalence_relation(
    domain: set[T],
    relation: Relation,
) -> bool:
    return (
        is_reflexive(domain, relation)
        and is_symmetric(relation)
        and is_transitive(relation)
    )


def is_partial_order(
    domain: set[T],
    relation: Relation,
) -> bool:
    return (
        is_reflexive(domain, relation)
        and is_antisymmetric(relation)
        and is_transitive(relation)
    )


subsection("Relation Properties")

numbers = {1, 2, 3}
less_equal: Relation = {
    (1, 1), (1, 2), (1, 3),
    (2, 2), (2, 3),
    (3, 3),
}

print("≤ relation:", less_equal)
print("Reflexive:", is_reflexive(numbers, less_equal))
print("Symmetric:", is_symmetric(less_equal))
print("Antisymmetric:", is_antisymmetric(less_equal))
print("Transitive:", is_transitive(less_equal))
print("Partial order:", is_partial_order(numbers, less_equal))

assert is_partial_order(numbers, less_equal)
assert not is_symmetric(less_equal)


# ============================================================================
# 3. EQUIVALENCE RELATIONS
# ============================================================================

section("3. EQUIVALENCE RELATIONS AND PARTITIONS")

# Congruence modulo n is a standard equivalence relation:
# a ~ b iff a % n == b % n.
def modulo_relation(values: set[int], modulus: int) -> Relation:
    if modulus <= 0:
        raise ValueError("Modulus must be positive.")

    return {
        (a, b)
        for a in values
        for b in values
        if a % modulus == b % modulus
    }


values = set(range(8))
mod_relation = modulo_relation(values, 3)

print("Relation modulo 3:")
for pair in sorted(mod_relation):
    print(pair)

print("Reflexive:", is_reflexive(values, mod_relation))
print("Symmetric:", is_symmetric(mod_relation))
print("Transitive:", is_transitive(mod_relation))
print("Equivalence relation:", is_equivalence_relation(values, mod_relation))

assert is_equivalence_relation(values, mod_relation)


def equivalence_classes(
    domain: set[T],
    relation: Relation,
) -> list[set[T]]:
    """Construct equivalence classes for a finite equivalence relation."""
    unseen = set(domain)
    classes: list[set[T]] = []

    while unseen:
        representative = next(iter(unseen))
        current_class = {
            y
            for x, y in relation
            if x == representative
        }
        classes.append(current_class)
        unseen -= current_class

    return classes


classes = equivalence_classes(values, mod_relation)
print("Equivalence classes:", classes)

# Equivalence classes form a partition:
# every element occurs in exactly one class.
assert set().union(*classes) == values
assert sum(len(c) for c in classes) == len(values)


# ============================================================================
# 4. PARTIAL ORDERS
# ============================================================================

section("4. PARTIAL ORDERS")

# A partial order is reflexive, antisymmetric, and transitive.
# Subset inclusion is a canonical partial order.
sets = {
    frozenset(),
    frozenset({1}),
    frozenset({2}),
    frozenset({1, 2}),
}

subset_relation: Relation = {
    (a, b)
    for a in sets
    for b in sets
    if a <= b
}

print("Subset relation is a partial order:",
      is_partial_order(sets, subset_relation))


def minimal_elements(
    domain: set[T],
    relation: Relation,
) -> set[T]:
    """
    x is minimal if no distinct y satisfies y R x.
    """
    return {
        x
        for x in domain
        if not any(y != x and (y, x) in relation for y in domain)
    }


def maximal_elements(
    domain: set[T],
    relation: Relation,
) -> set[T]:
    """
    x is maximal if no distinct y satisfies x R y.
    """
    return {
        x
        for x in domain
        if not any(y != x and (x, y) in relation for y in domain)
    }


print("Minimal elements:", minimal_elements(sets, subset_relation))
print("Maximal elements:", maximal_elements(sets, subset_relation))


def topological_sort(
    nodes: set[T],
    edges: Relation,
) -> list[T]:
    """
    Topological sorting is applicable to directed acyclic graphs.
    A partial order can be represented by a directed acyclic relation
    after removing self-loops.
    """
    adjacency: dict[T, set[T]] = {node: set() for node in nodes}
    indegree: dict[T, int] = {node: 0 for node in nodes}

    for source, target in edges:
        if source == target:
            continue
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1

    queue = deque(node for node in nodes if indegree[node] == 0)
    ordering: list[T] = []

    while queue:
        node = queue.popleft()
        ordering.append(node)

        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(ordering) != len(nodes):
        raise ValueError("Graph contains a cycle.")

    return ordering


subsection("Topological Ordering")

course_dependencies = {
    ("Logic", "Algorithms"),
    ("Sets", "Relations"),
    ("Relations", "Databases"),
    ("Algorithms", "Databases"),
}

courses = {"Logic", "Sets", "Relations", "Algorithms", "Databases"}

order = topological_sort(courses, course_dependencies)
print("Valid dependency order:", order)


# ============================================================================
# 5. FUNCTIONS
# ============================================================================

section("5. FUNCTIONS AND MAPPINGS")

# A function f: A -> B assigns exactly one output in B to every input in A.
# In Python, functions are first-class objects.
def square(x: float) -> float:
    return x * x


print("square(7) =", square(7))

# Lambda expressions are useful for short functions.
cube = lambda x: x ** 3
print("cube(4) =", cube(4))

# A dictionary can explicitly represent a finite function.
finite_function = {
    "a": 1,
    "b": 4,
    "c": 9,
}

print("Finite function:", finite_function)


def is_function(
    domain: set[T],
    graph: Relation,
) -> bool:
    """
    A relation is a function from domain if every input has
    exactly one output.
    """
    outputs: dict[T, set[Any]] = defaultdict(set)

    for x, y in graph:
        outputs[x].add(y)

    return all(len(outputs[x]) == 1 for x in domain)


function_graph = {("a", 1), ("b", 4), ("c", 9)}
not_function_graph = {("a", 1), ("a", 2), ("b", 4), ("c", 9)}

print("Graph is a function:", is_function({"a", "b", "c"}, function_graph))
print("Conflicting graph is a function:",
      is_function({"a", "b", "c"}, not_function_graph))

assert is_function({"a", "b", "c"}, function_graph)
assert not is_function({"a", "b", "c"}, not_function_graph)


def function_image(
    function: dict[T, U],
) -> set[U]:
    return set(function.values())


def is_injective(
    function: dict[T, U],
) -> bool:
    values = list(function.values())
    return len(values) == len(set(values))


def is_surjective(
    function: dict[T, U],
    codomain: set[U],
) -> bool:
    return set(function.values()) == codomain


def is_bijective(
    function: dict[T, U],
    codomain: set[U],
) -> bool:
    return is_injective(function) and is_surjective(function, codomain)


subsection("Injective, Surjective, and Bijective Functions")

f_injective = {"a": 1, "b": 2, "c": 3}
f_surjective = {"a": 1, "b": 1, "c": 2}
codomain = {1, 2}

print("f_injective image:", function_image(f_injective))
print("Injective:", is_injective(f_injective))
print("Surjective onto {1,2}:",
      is_surjective(f_injective, codomain))
print("Bijective:", is_bijective(f_injective, {1, 2, 3}))

print("f_surjective injective:", is_injective(f_surjective))
print("f_surjective surjective:", is_surjective(f_surjective, codomain))

assert is_bijective(f_injective, {1, 2, 3})
assert is_surjective(f_surjective, codomain)
assert not is_injective(f_surjective)


def compose(
    f: Callable[[U], Any],
    g: Callable[[T], U],
) -> Callable[[T], Any]:
    """Return f ∘ g, meaning apply g first and then f."""
    return lambda x: f(g(x))


f = lambda x: x + 10
g = lambda x: x * 2

composition = compose(f, g)
print("(f ∘ g)(5) =", composition(5))
assert composition(5) == 20


def inverse_of_bijection(
    function: dict[T, U],
) -> dict[U, T]:
    """An inverse function exists only when the finite function is bijective."""
    if not is_injective(function):
        raise ValueError("A non-injective function has no inverse function.")

    return {output: input_value for input_value, output in function.items()}


bijection = {"A": 10, "B": 20, "C": 30}
inverse = inverse_of_bijection(bijection)

print("Function:", bijection)
print("Inverse:", inverse)

assert inverse[20] == "B"


# ============================================================================
# 6. PROPOSITIONAL LOGIC
# ============================================================================

section("6. PROPOSITIONAL LOGIC")

# A proposition is a statement that is either true or false.
# Truth values can be represented by Python booleans.
p = True
q = False

print("p =", p)
print("q =", q)
print("NOT p =", not p)
print("p AND q =", p and q)
print("p OR q =", p or q)
print("p XOR q =", p != q)
print("p -> q =", (not p) or q)
print("p <-> q =", p == q)


def implies(p: bool, q: bool) -> bool:
    return (not p) or q


def iff(p: bool, q: bool) -> bool:
    return p == q


def truth_table_two_variables(
    expression: Callable[[bool, bool], bool],
) -> list[tuple[bool, bool, bool]]:
    return [
        (p, q, expression(p, q))
        for p, q in product([False, True], repeat=2)
    ]


subsection("Truth Table")

table = truth_table_two_variables(lambda p, q: implies(p, q))

for row in table:
    print(f"p={row[0]!s:5} q={row[1]!s:5} expression={row[2]!s:5}")


def is_tautology(
    expression: Callable[..., bool],
    variable_count: int,
) -> bool:
    return all(
        expression(*assignment)
        for assignment in product([False, True], repeat=variable_count)
    )


def is_contradiction(
    expression: Callable[..., bool],
    variable_count: int,
) -> bool:
    return all(
        not expression(*assignment)
        for assignment in product([False, True], repeat=variable_count)
    )


def is_contingency(
    expression: Callable[..., bool],
    variable_count: int,
) -> bool:
    return not is_tautology(expression, variable_count) and not is_contradiction(
        expression,
        variable_count,
    )


# Law of excluded middle: p OR NOT p.
excluded_middle = lambda p: p or not p

# Contradiction: p AND NOT p.
contradiction = lambda p: p and not p

print("Excluded middle is tautology:",
      is_tautology(excluded_middle, 1))
print("Contradiction is contradiction:",
      is_contradiction(contradiction, 1))

assert is_tautology(excluded_middle, 1)
assert is_contradiction(contradiction, 1)


def logically_equivalent(
    first: Callable[..., bool],
    second: Callable[..., bool],
    variable_count: int,
) -> bool:
    return all(
        first(*assignment) == second(*assignment)
        for assignment in product([False, True], repeat=variable_count)
    )


# De Morgan's law:
# NOT(p AND q) <-> (NOT p OR NOT q)
demorgan_left = lambda p, q: not (p and q)
demorgan_right = lambda p, q: (not p) or (not q)

print("De Morgan equivalence:",
      logically_equivalent(demorgan_left, demorgan_right, 2))

assert logically_equivalent(demorgan_left, demorgan_right, 2)


# ============================================================================
# 7. PREDICATE LOGIC
# ============================================================================

section("7. PREDICATE LOGIC AND QUANTIFIERS")

numbers = list(range(1, 11))

is_even = lambda x: x % 2 == 0
is_positive = lambda x: x > 0

# Universal quantification: ∀x P(x)
print("All numbers are positive:",
      all(is_positive(x) for x in numbers))

# Existential quantification: ∃x P(x)
print("At least one number is even:",
      any(is_even(x) for x in numbers))

# "Exactly one" can be implemented by counting witnesses.
exactly_one_even_in = [1, 3, 5, 7]
print(
    "Exactly one even number:",
    sum(is_even(x) for x in exactly_one_even_in) == 1,
)

# Counterexamples are useful for disproving universal statements.
candidate_statement = lambda x: x * x >= x
counterexamples = [
    x for x in range(-5, 6)
    if not candidate_statement(x)
]

print("Counterexamples to x² >= x over [-5,5]:", counterexamples)


# ============================================================================
# 8. LOGICAL INFERENCE
# ============================================================================

section("8. LOGICAL INFERENCE")

# Modus ponens:
# p
# p -> q
# therefore q
def modus_ponens(p: bool, implication: bool) -> bool:
    if not p:
        raise ValueError("Modus ponens requires p to be true.")
    if not implication:
        raise ValueError("The implication p -> q must be true.")
    return True


print(
    "Modus ponens confirms q:",
    modus_ponens(True, implies(True, True)),
)

# A practical authorization rule:
# authenticated AND active -> permitted.
def access_allowed(authenticated: bool, active: bool) -> bool:
    return authenticated and active


cases = [
    (False, False),
    (False, True),
    (True, False),
    (True, True),
]

for authenticated, active in cases:
    print(
        f"authenticated={authenticated}, active={active} -> "
        f"access={access_allowed(authenticated, active)}"
    )


# ============================================================================
# 9. BOOLEAN ALGEBRA
# ============================================================================

section("9. BOOLEAN ALGEBRA")

# Boolean algebra provides algebraic rules for logical values.
# These identities are central to digital circuits and software conditions.

def boolean_expression_a(p: bool, q: bool, r: bool) -> bool:
    return (p and q) or (p and r)


def boolean_expression_b(p: bool, q: bool, r: bool) -> bool:
    return p and (q or r)


assert logically_equivalent(boolean_expression_a, boolean_expression_b, 3)
print("Distributive law verified for all 8 assignments.")

# Absorption:
# p OR (p AND q) == p
for p_value, q_value in product([False, True], repeat=2):
    assert (p_value or (p_value and q_value)) == p_value

print("Absorption law verified.")


# ============================================================================
# 10. RECURSION AND INDUCTION
# ============================================================================

section("10. RECURSION AND MATHEMATICAL INDUCTION")

def factorial_recursive(n: int) -> int:
    """
    Recursive definition:
    0! = 1
    n! = n * (n-1)! for n > 0
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)


for n in range(6):
    print(f"{n}! =", factorial_recursive(n))


def fibonacci_recursive(n: int) -> int:
    """Simple recursive Fibonacci implementation for teaching recurrence."""
    if n < 0:
        raise ValueError("Fibonacci index must not be negative.")
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


print("Fibonacci sequence:",
      [fibonacci_recursive(i) for i in range(10)])


def fibonacci_iterative(n: int) -> int:
    """Linear-time and constant-space Fibonacci implementation."""
    if n < 0:
        raise ValueError("Fibonacci index must not be negative.")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    return a


print("Fibonacci(30), iterative:", fibonacci_iterative(30))


# Mathematical induction can be mirrored by checking a finite range,
# although finite testing alone is not a proof for an infinite domain.
def induction_identity_holds(n: int) -> bool:
    left = sum(range(1, n + 1))
    right = n * (n + 1) // 2
    return left == right


for n in range(1, 101):
    assert induction_identity_holds(n)

print("Sum 1..n = n(n+1)/2 verified computationally for n=1..100.")


# ============================================================================
# 11. GRAPHS
# ============================================================================

section("11. GRAPHS AS MATHEMATICAL STRUCTURES")

# A graph G = (V, E) contains vertices and edges.
# An adjacency list is efficient for sparse graphs.
Graph = dict[str, set[str]]


def add_undirected_edge(
    graph: Graph,
    first: str,
    second: str,
) -> None:
    graph.setdefault(first, set()).add(second)
    graph.setdefault(second, set()).add(first)


graph: Graph = {}

edges = [
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("C", "D"),
    ("D", "E"),
]

for first, second in edges:
    add_undirected_edge(graph, first, second)

print("Adjacency list:")
for vertex in sorted(graph):
    print(vertex, "->", sorted(graph[vertex]))


def bfs(graph: Graph, start: str) -> list[str]:
    if start not in graph:
        raise KeyError(f"Unknown start vertex: {start}")

    queue = deque([start])
    visited = {start}
    order: list[str] = []

    while queue:
        current = queue.popleft()
        order.append(current)

        for neighbor in sorted(graph[current]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def dfs(graph: Graph, start: str) -> list[str]:
    if start not in graph:
        raise KeyError(f"Unknown start vertex: {start}")

    stack = [start]
    visited: set[str] = set()
    order: list[str] = []

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        order.append(current)

        for neighbor in sorted(graph[current], reverse=True):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


print("BFS:", bfs(graph, "A"))
print("DFS:", dfs(graph, "A"))


# ============================================================================
# 12. TREES
# ============================================================================

section("12. TREES")

@dataclass
class TreeNode:
    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def insert_bst(root: TreeNode | None, value: int) -> TreeNode:
    """
    Binary Search Tree invariant:
    values in left subtree < node value
    values in right subtree > node value
    """
    if root is None:
        return TreeNode(value)

    if value < root.value:
        root.left = insert_bst(root.left, value)
    elif value > root.value:
        root.right = insert_bst(root.right, value)

    return root


def inorder(root: TreeNode | None) -> list[int]:
    if root is None:
        return []

    return inorder(root.left) + [root.value] + inorder(root.right)


root = None
for value in [50, 30, 70, 20, 40, 60, 80]:
    root = insert_bst(root, value)

print("BST inorder traversal:", inorder(root))
assert inorder(root) == [20, 30, 40, 50, 60, 70, 80]


# ============================================================================
# 13. ALGEBRAIC STRUCTURES
# ============================================================================

section("13. ALGEBRAIC STRUCTURES")

# A binary operation combines two elements and produces another element.
# Closure is checked by verifying that every operation result remains
# inside the set.

def is_closed_under_addition(values: set[int]) -> bool:
    return all((a + b) in values for a in values for b in values)


def is_closed_under_multiplication(values: set[int]) -> bool:
    return all((a * b) in values for a in values for b in values)


modulus = 5
residue_set = set(range(modulus))


def modular_add(a: int, b: int, modulus: int) -> int:
    return (a + b) % modulus


def modular_multiply(a: int, b: int, modulus: int) -> int:
    return (a * b) % modulus


print(
    "Residues modulo 5 closed under addition:",
    all(
        modular_add(a, b, modulus) in residue_set
        for a, b in product(residue_set, repeat=2)
    ),
)

print(
    "Residues modulo 5 closed under multiplication:",
    all(
        modular_multiply(a, b, modulus) in residue_set
        for a, b in product(residue_set, repeat=2)
    ),
)

# Modular addition forms a finite group:
# closure, associativity, identity 0, and inverses all exist.
identity = 0

for a in residue_set:
    inverse = (-a) % modulus
    assert modular_add(a, inverse, modulus) == identity

print("Every residue modulo 5 has an additive inverse.")


# ============================================================================
# 14. MATRICES AS STRUCTURES
# ============================================================================

section("14. MATRICES AND DISCRETE STRUCTURES")

Matrix = list[list[int]]


def validate_matrix(matrix: Matrix) -> tuple[int, int]:
    if not matrix:
        return (0, 0)

    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("Matrix rows must have equal lengths.")

    return len(matrix), width


def matrix_add(first: Matrix, second: Matrix) -> Matrix:
    rows_a, cols_a = validate_matrix(first)
    rows_b, cols_b = validate_matrix(second)

    if (rows_a, cols_a) != (rows_b, cols_b):
        raise ValueError("Matrices must have equal dimensions.")

    return [
        [first[i][j] + second[i][j] for j in range(cols_a)]
        for i in range(rows_a)
    ]


def matrix_multiply(first: Matrix, second: Matrix) -> Matrix:
    rows_a, cols_a = validate_matrix(first)
    rows_b, cols_b = validate_matrix(second)

    if cols_a != rows_b:
        raise ValueError(
            "For A(m×n) × B(n×p), A columns must equal B rows."
        )

    return [
        [
            sum(first[i][k] * second[k][j] for k in range(cols_a))
            for j in range(cols_b)
        ]
        for i in range(rows_a)
    ]


M = [[1, 2], [3, 4]]
N = [[5, 6], [7, 8]]

print("M + N =", matrix_add(M, N))
print("M × N =", matrix_multiply(M, N))


# ============================================================================
# 15. COUNTING AND COMBINATORICS
# ============================================================================

section("15. COUNTING AND COMBINATORICS")

def permutation_count(n: int, r: int) -> int:
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= 0 and 0 <= r <= n.")

    return math.factorial(n) // math.factorial(n - r)


def combination_count(n: int, r: int) -> int:
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= 0 and 0 <= r <= n.")

    return math.comb(n, r)


print("P(5,2) =", permutation_count(5, 2))
print("C(5,2) =", combination_count(5, 2))

assert permutation_count(5, 2) == 20
assert combination_count(5, 2) == 10

# Pigeonhole principle:
# placing n+1 objects into n boxes forces at least one box to contain
# at least two objects.
def pigeonhole_collision_count(
    objects: list[Any],
    boxes: Callable[[Any], Any],
) -> dict[Any, list[Any]]:
    distribution: dict[Any, list[Any]] = defaultdict(list)

    for obj in objects:
        distribution[boxes(obj)].append(obj)

    return dict(distribution)


items = list(range(10))
distribution = pigeonhole_collision_count(items, lambda x: x % 3)

print("Pigeonhole distribution:", distribution)
print(
    "At least one box has two objects:",
    any(len(values) >= 2 for values in distribution.values()),
)


# ============================================================================
# 16. RELATIONS AS DATABASE CONSTRAINTS
# ============================================================================

section("16. RELATIONS IN DATABASES")

# A database table can be modeled as a set of tuples.
students = {
    ("S01", "Atul", "CS"),
    ("S02", "Mira", "Math"),
    ("S03", "Ravi", "CS"),
}

courses = {
    ("C01", "Algorithms"),
    ("C02", "Logic"),
    ("C03", "Databases"),
}

enrollments = {
    ("S01", "C01"),
    ("S01", "C03"),
    ("S02", "C02"),
    ("S03", "C01"),
}


def validate_foreign_keys(
    left_rows: set[tuple[str, str, str]],
    right_rows: set[tuple[str, str]],
    links: set[tuple[str, str]],
) -> bool:
    left_ids = {row[0] for row in left_rows}
    right_ids = {row[0] for row in right_rows}

    return all(
        student_id in left_ids and course_id in right_ids
        for student_id, course_id in links
    )


print(
    "Enrollment foreign keys valid:",
    validate_foreign_keys(students, courses, enrollments),
)

# This is a practical connection between relations and relational databases:
# tuples form relations, and integrity constraints restrict valid tuples.


# ============================================================================
# 17. FORMAL SPECIFICATION WITH ASSERTIONS
# ============================================================================

section("17. FORMAL PROPERTIES AS EXECUTABLE CHECKS")

# Set identities can be checked over finite sets.
universal_domain = set(range(5))

for subset_a in powerset(universal_domain):
    for subset_b in powerset(universal_domain):
        left = set(universal_domain - subset_a)
        right = set(universal_domain) - set(subset_a)
        assert left == right

print("Finite complement identity verified.")


# ============================================================================
# 18. EDGE CASES AND ERROR HANDLING
# ============================================================================

section("18. EDGE CASES")

edge_cases = [
    ("empty set", set()),
    ("singleton set", {42}),
    ("duplicate input", {1, 1, 1, 2}),
]

for name, value in edge_cases:
    print(name, "->", value, "cardinality =", len(value))

try:
    inverse_of_bijection({"a": 1, "b": 1})
except ValueError as error:
    print("Expected inverse error:", error)

try:
    matrix_multiply([[1, 2]], [[1, 2]])
except ValueError as error:
    print("Expected matrix dimension error:", error)

try:
    topological_sort({"A", "B"}, {("A", "B"), ("B", "A")})
except ValueError as error:
    print("Expected cycle error:", error)


# ============================================================================
# 19. PERFORMANCE CONSIDERATIONS
# ============================================================================

section("19. PERFORMANCE CONSIDERATIONS")

print(
    "Set membership is typically O(1) average case because Python sets "
    "are hash tables."
)
print(
    "Generating a power set is O(2^n) because there are 2^n subsets."
)
print(
    "BFS and DFS are O(V + E) with adjacency lists."
)
print(
    "Naive recursive Fibonacci has exponential time growth, while the "
    "iterative version is O(n)."
)
print(
    "Truth-table evaluation for n propositional variables examines 2^n "
    "assignments."
)


# ============================================================================
# 20. ADVANCED COMBINED EXAMPLE: PERMISSION SYSTEM
# ============================================================================

section("20. INTEGRATED COMPUTER SCIENCE EXAMPLE: PERMISSIONS")

# Users, roles, permissions, and role inheritance can be modeled using sets
# and relations.

users = {
    "alice",
    "bob",
    "carol",
}

roles = {
    "viewer",
    "editor",
    "admin",
}

permissions = {
    "read",
    "write",
    "delete",
}

role_permissions = {
    "viewer": {"read"},
    "editor": {"read", "write"},
    "admin": {"read", "write", "delete"},
}

user_roles = {
    "alice": {"admin"},
    "bob": {"editor"},
    "carol": {"viewer"},
}


def effective_permissions(
    username: str,
    user_roles: dict[str, set[str]],
    role_permissions: dict[str, set[str]],
) -> set[str]:
    if username not in user_roles:
        raise KeyError(f"Unknown user: {username}")

    result: set[str] = set()

    for role in user_roles[username]:
        if role not in role_permissions:
            raise KeyError(f"Unknown role: {role}")
        result |= role_permissions[role]

    return result


def can_perform(
    username: str,
    permission: str,
) -> bool:
    return permission in effective_permissions(
        username,
        user_roles,
        role_permissions,
    )


for username in sorted(users):
    print(
        username,
        "->",
        sorted(effective_permissions(username, user_roles, role_permissions)),
    )

assert can_perform("alice", "delete")
assert can_perform("bob", "write")
assert not can_perform("carol", "write")


# ============================================================================
# 21. RELATION CLOSURES
# ============================================================================

section("21. RELATION CLOSURES")

def reflexive_closure(
    domain: set[T],
    relation: Relation,
) -> Relation:
    return set(relation) | {(x, x) for x in domain}


def symmetric_closure(
    relation: Relation,
) -> Relation:
    return set(relation) | {(y, x) for x, y in relation}


def transitive_closure(
    relation: Relation,
) -> Relation:
    closure = set(relation)

    changed = True
    while changed:
        changed = False

        for x, y in list(closure):
            for y2, z in list(closure):
                if y == y2 and (x, z) not in closure:
                    closure.add((x, z))
                    changed = True

    return closure


base_relation: Relation = {
    ("A", "B"),
    ("B", "C"),
}

print("Base relation:", base_relation)
print("Reflexive closure:",
      reflexive_closure({"A", "B", "C"}, base_relation))
print("Symmetric closure:", symmetric_closure(base_relation))
print("Transitive closure:", transitive_closure(base_relation))

assert ("A", "C") in transitive_closure(base_relation)


# ============================================================================
# 22. NORMAL FORMS OF LOGIC
# ============================================================================

section("22. LOGICAL NORMAL FORMS")

# Conjunctive Normal Form (CNF) is an AND of OR clauses.
# Disjunctive Normal Form (DNF) is an OR of AND terms.
#
# The following expression:
# (p OR q) AND (NOT p OR r)
# is already in CNF.

def cnf_example(p: bool, q: bool, r: bool) -> bool:
    return (p or q) and ((not p) or r)


for assignment in product([False, True], repeat=3):
    p_value, q_value, r_value = assignment
    print(
        assignment,
        "->",
        cnf_example(p_value, q_value, r_value),
    )


# ============================================================================
# 23. INVARIANTS
# ============================================================================

section("23. INVARIANTS")

# An invariant is a condition that remains true throughout an algorithm.
# In a BST, inorder traversal must remain sorted.

values = [50, 30, 70, 20, 40, 60, 80]
root = None

for value in values:
    root = insert_bst(root, value)

ordered_values = inorder(root)

print("BST invariant: inorder traversal sorted:",
      ordered_values == sorted(set(values)))

assert ordered_values == sorted(set(values))


# ============================================================================
# 24. MINI TEST SUITE
# ============================================================================

section("24. MINI TEST SUITE")

def run_tests() -> None:
    assert {1, 2} | {2, 3} == {1, 2, 3}
    assert {1, 2} & {2, 3} == {2}
    assert {1, 2} <= {1, 2, 3}

    domain = {1, 2, 3}
    relation = {(1, 1), (2, 2), (3, 3), (1, 2), (2, 1)}
    assert is_reflexive(domain, relation)
    assert is_symmetric(relation)

    bijection = {"a": 1, "b": 2}
    assert is_bijective(bijection, {1, 2})

    assert logically_equivalent(
        lambda p, q: not (p and q),
        lambda p, q: (not p) or (not q),
        2,
    )

    assert factorial_recursive(5) == 120
    assert fibonacci_iterative(10) == 55
    assert combination_count(6, 2) == 15

    assert matrix_add([[1]], [[2]]) == [[3]]
    assert matrix_multiply([[2]], [[3]]) == [[6]]

    print("All tests passed.")


run_tests()


# ============================================================================
# 25. FINAL CONCEPT MAP
# ============================================================================

section("25. CONCEPT MAP")

concept_map = {
    "Sets": [
        "membership",
        "subset",
        "union",
        "intersection",
        "difference",
        "power set",
        "Cartesian product",
    ],
    "Relations": [
        "reflexive",
        "symmetric",
        "antisymmetric",
        "transitive",
        "equivalence relation",
        "partial order",
        "closure",
    ],
    "Functions": [
        "domain",
        "codomain",
        "range",
        "injective",
        "surjective",
        "bijective",
        "composition",
        "inverse",
    ],
    "Logic": [
        "proposition",
        "connectives",
        "truth tables",
        "tautology",
        "contradiction",
        "predicate",
        "quantifiers",
        "inference",
    ],
    "Structures": [
        "graphs",
        "trees",
        "matrices",
        "Boolean algebra",
        "groups",
        "database relations",
    ],
}

for concept, terms in concept_map.items():
    print(f"{concept}: {', '.join(terms)}")


print("\nDiscrete mathematical structures demonstrated successfully.")
