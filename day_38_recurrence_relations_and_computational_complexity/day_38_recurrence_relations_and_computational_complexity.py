"""
Recurrence Relations and Computational Complexity:
P, NP, NP-Completeness, and Polynomial-Time Reductions

A self-contained executable study program.

The program demonstrates:
- recurrence relations and recursive algorithms
- substitution-style recurrence evaluation
- recurrence trees
- Master Theorem classifications for common divide-and-conquer recurrences
- iterative versus recursive Fibonacci
- asymptotic growth
- polynomial-time complexity measurement
- exponential search
- decision problems
- P-style polynomial algorithms
- NP-style certificate verification
- NP-complete examples: SAT, 3-SAT, CLIQUE, and SUBSET SUM
- polynomial-time reductions between decision problems
- a concrete 3-SAT -> CLIQUE reduction
- verification versus search
- brute-force behavior and practical limitations

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import log2
from time import perf_counter
from typing import Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# Recurrence relations
# ---------------------------------------------------------------------------

def recurrence_values(
    base_value: int,
    recurrence: Callable[[int, int], int],
    n: int,
) -> list[int]:
    """Evaluate T(k) for k=0..n when T(k) depends on earlier values."""
    if n < 0:
        raise ValueError("n must be non-negative")

    values = [0] * (n + 1)
    values[0] = base_value

    for k in range(1, n + 1):
        values[k] = recurrence(k, values[k - 1])

    return values


def factorial_recursive(n: int) -> int:
    """T(n) = T(n-1) + O(1), therefore T(n) = O(n)."""
    if n < 0:
        raise ValueError("factorial requires n >= 0")
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)


def fibonacci_recursive(n: int) -> int:
    """
    Naive Fibonacci:
        T(n) = T(n-1) + T(n-2) + O(1)

    The number of calls grows exponentially.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_memoized(n: int, memo: dict[int, int] | None = None) -> int:
    """
    Memoization changes the repeated recursion into:
        T(n) = T(n-1) + O(1)
    after each state is computed once.

    Time: O(n)
    Space: O(n)
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if memo is None:
        memo = {0: 0, 1: 1}

    if n not in memo:
        memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)

    return memo[n]


def fibonacci_iterative(n: int) -> int:
    """Bottom-up Fibonacci with O(n) time and O(1) auxiliary space."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n

    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


# ---------------------------------------------------------------------------
# Recurrence tree demonstration
# ---------------------------------------------------------------------------

def recurrence_tree_cost(
    n: int,
    branching_factor: int,
    shrink_factor: int,
    local_cost: Callable[[int], int],
) -> int:
    """
    Directly expands a recurrence of the form

        T(n) = b T(n / a) + f(n)

    for integral subproblem sizes.

    This function is intentionally small enough for educational experiments.
    """
    if n <= 1:
        return local_cost(n)

    smaller = max(1, n // shrink_factor)

    return local_cost(n) + sum(
        recurrence_tree_cost(smaller, branching_factor, shrink_factor, local_cost)
        for _ in range(branching_factor)
    )


def recurrence_level_costs(
    n: int,
    branching_factor: int,
    shrink_factor: int,
    local_cost: Callable[[int], int],
) -> list[int]:
    """Return the total non-recursive work performed at each recurrence-tree level."""
    if n <= 1:
        return [local_cost(n)]

    levels: list[int] = []
    problem_sizes = [n]

    while problem_sizes:
        levels.append(sum(local_cost(size) for size in problem_sizes))

        next_sizes: list[int] = []
        for size in problem_sizes:
            if size > 1:
                next_sizes.extend(
                    [max(1, size // shrink_factor)] * branching_factor
                )
        problem_sizes = next_sizes

    return levels


# ---------------------------------------------------------------------------
# Master Theorem classification
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MasterTheoremResult:
    recurrence: str
    classification: str
    asymptotic_bound: str
    reason: str


def master_theorem(
    a: int,
    b: int,
    f_exponent: float,
) -> MasterTheoremResult:
    """
    Classify T(n) = aT(n/b) + Theta(n^c) for polynomial f(n).

    This intentionally handles the common polynomial comparison cases:
      c < log_b(a)
      c = log_b(a)
      c > log_b(a)
    """
    if a <= 0 or b <= 1:
        raise ValueError("Require a > 0 and b > 1")

    critical_exponent = log2(a) / log2(b)

    if f_exponent < critical_exponent:
        classification = "recursive-subproblem dominated"
        bound = f"Θ(n^{critical_exponent:.3g})"
        reason = f"f(n) grows slower than n^log_b(a), where log_b(a)={critical_exponent:.3g}."
    elif abs(f_exponent - critical_exponent) < 1e-12:
        classification = "balanced"
        bound = f"Θ(n^{critical_exponent:.3g} log n)"
        reason = "The work per recurrence level is asymptotically comparable."
    else:
        classification = "root-work dominated"
        bound = f"Θ(n^{f_exponent:.3g})"
        reason = "The non-recursive work grows polynomially faster than the recursive contribution."

    recurrence = f"T(n) = {a}T(n/{b}) + Θ(n^{f_exponent:g})"

    return MasterTheoremResult(
        recurrence=recurrence,
        classification=classification,
        asymptotic_bound=bound,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# Asymptotic algorithms
# ---------------------------------------------------------------------------

def constant_lookup(values: Sequence[int], index: int) -> int:
    """O(1) indexed access when the underlying sequence supports it."""
    if not 0 <= index < len(values):
        raise IndexError("index outside sequence")
    return values[index]


def linear_search(values: Sequence[int], target: int) -> int | None:
    """Worst-case O(n)."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return None


def binary_search(values: Sequence[int], target: int) -> int | None:
    """O(log n) search on an already sorted sequence."""
    low, high = 0, len(values) - 1

    while low <= high:
        middle = (low + high) // 2

        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1

    return None


def merge_sort(values: Sequence[int]) -> list[int]:
    """
    Merge sort recurrence:
        T(n) = 2T(n/2) + O(n)
        T(n) = O(n log n)
    """
    if len(values) <= 1:
        return list(values)

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    result: list[int] = []
    left_index = right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])
    return result


# ---------------------------------------------------------------------------
# Decision problems
# ---------------------------------------------------------------------------

def is_valid_boolean_assignment(
    variables: Sequence[str],
    assignment: dict[str, bool],
) -> bool:
    """Ensure an assignment supplies exactly the variables being considered."""
    return set(variables) == set(assignment)


@dataclass(frozen=True)
class Literal:
    variable: str
    positive: bool = True

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        value = assignment[self.variable]
        return value if self.positive else not value


@dataclass(frozen=True)
class Clause:
    literals: tuple[Literal, ...]

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        return any(literal.evaluate(assignment) for literal in self.literals)


@dataclass(frozen=True)
class CNFFormula:
    variables: tuple[str, ...]
    clauses: tuple[Clause, ...]

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        if not is_valid_boolean_assignment(self.variables, assignment):
            raise ValueError("Assignment does not match formula variables")
        return all(clause.evaluate(assignment) for clause in self.clauses)


def brute_force_sat(formula: CNFFormula) -> dict[str, bool] | None:
    """
    Search all 2^n assignments.

    SAT belongs to NP because a proposed assignment can be verified in
    polynomial time, while this brute-force search need not be polynomial.
    """
    for bits in product([False, True], repeat=len(formula.variables)):
        assignment = dict(zip(formula.variables, bits))
        if formula.evaluate(assignment):
            return assignment
    return None


def verify_sat_certificate(
    formula: CNFFormula,
    assignment: dict[str, bool],
) -> bool:
    """Polynomial-time verification of a SAT certificate."""
    return formula.evaluate(assignment)


# ---------------------------------------------------------------------------
# CLIQUE
# ---------------------------------------------------------------------------

@dataclass
class UndirectedGraph:
    vertices: set[int]
    edges: set[tuple[int, int]]

    def __post_init__(self) -> None:
        normalized: set[tuple[int, int]] = set()

        for u, v in self.edges:
            if u == v:
                raise ValueError("Self-loops are not allowed in this simple graph")
            if u not in self.vertices or v not in self.vertices:
                raise ValueError("Edge endpoint is not a graph vertex")
            normalized.add((min(u, v), max(u, v)))

        self.edges = normalized

    def adjacent(self, u: int, v: int) -> bool:
        return (min(u, v), max(u, v)) in self.edges


def verify_clique(graph: UndirectedGraph, candidate: Iterable[int]) -> bool:
    """Certificate verification takes O(k^2) edge checks for a k-vertex clique."""
    vertices = list(candidate)

    if len(vertices) != len(set(vertices)):
        return False

    if not set(vertices).issubset(graph.vertices):
        return False

    return all(
        graph.adjacent(u, v)
        for u, v in combinations(vertices, 2)
    )


# ---------------------------------------------------------------------------
# SUBSET SUM
# ---------------------------------------------------------------------------

def verify_subset_sum(
    numbers: Sequence[int],
    target: int,
    selected_indices: Sequence[int],
) -> bool:
    """
    Verify a subset-sum certificate.

    Verification checks:
    - indices are unique
    - indices are valid
    - selected values sum to the target

    This is polynomial in the explicit input representation and certificate size.
    """
    if len(selected_indices) != len(set(selected_indices)):
        return False

    if any(index < 0 or index >= len(numbers) for index in selected_indices):
        return False

    return sum(numbers[index] for index in selected_indices) == target


def brute_force_subset_sum(
    numbers: Sequence[int],
    target: int,
) -> list[int] | None:
    """Exhaustive subset search requiring up to 2^n candidate subsets."""
    for bits in product([False, True], repeat=len(numbers)):
        selected = [i for i, chosen in enumerate(bits) if chosen]
        if sum(numbers[i] for i in selected) == target:
            return selected
    return None


# ---------------------------------------------------------------------------
# Polynomial-time reduction: 3-SAT -> CLIQUE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CliqueReduction:
    graph: UndirectedGraph
    k: int
    literal_by_vertex: dict[int, Literal]
    clause_by_vertex: dict[int, int]


def reduce_3sat_to_clique(formula: CNFFormula) -> CliqueReduction:
    """
    Construct the classic reduction from 3-SAT to CLIQUE.

    For each literal occurrence in each clause:
      - create one graph vertex
      - connect vertices from different clauses when their literals
        are not contradictory

    A satisfying assignment selecting one true literal per clause
    corresponds to a clique containing one vertex from each clause.

    The reduction is polynomial because a 3-SAT instance with m clauses
    creates exactly 3m vertices and examines polynomially many pairs.
    """
    if any(len(clause.literals) != 3 for clause in formula.clauses):
        raise ValueError("This reduction expects exactly three literals per clause")

    vertices = set()
    edges: set[tuple[int, int]] = set()
    literal_by_vertex: dict[int, Literal] = {}
    clause_by_vertex: dict[int, int] = {}

    vertex_id = 0

    for clause_index, clause in enumerate(formula.clauses):
        for literal in clause.literals:
            literal_by_vertex[vertex_id] = literal
            clause_by_vertex[vertex_id] = clause_index
            vertices.add(vertex_id)
            vertex_id += 1

    for u, v in combinations(sorted(vertices), 2):
        clause_u = clause_by_vertex[u]
        clause_v = clause_by_vertex[v]

        if clause_u == clause_v:
            continue

        literal_u = literal_by_vertex[u]
        literal_v = literal_by_vertex[v]

        contradictory = (
            literal_u.variable == literal_v.variable
            and literal_u.positive != literal_v.positive
        )

        if not contradictory:
            edges.add((u, v))

    return CliqueReduction(
        graph=UndirectedGraph(vertices, edges),
        k=len(formula.clauses),
        literal_by_vertex=literal_by_vertex,
        clause_by_vertex=clause_by_vertex,
    )


def find_clique_for_reduced_formula(
    reduction: CliqueReduction,
) -> list[int] | None:
    """Brute-force the target CLIQUE instance."""
    vertices = sorted(reduction.graph.vertices)

    for candidate in combinations(vertices, reduction.k):
        if verify_clique(reduction.graph, candidate):
            return list(candidate)

    return None


# ---------------------------------------------------------------------------
# Complexity benchmarking
# ---------------------------------------------------------------------------

def benchmark(
    label: str,
    function: Callable[[], object],
    repetitions: int = 1,
) -> tuple[str, float, object]:
    start = perf_counter()
    result: object = None

    for _ in range(repetitions):
        result = function()

    elapsed = perf_counter() - start
    return label, elapsed, result


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demonstrate_recurrences() -> None:
    print("\n=== Recurrence Relations ===")

    factorial_values = recurrence_values(
        1,
        lambda k, previous: k * previous,
        8,
    )
    print("Factorial values:", factorial_values)

    print("Fibonacci recursive F(10):", fibonacci_recursive(10))
    print("Fibonacci memoized F(30):", fibonacci_memoized(30))
    print("Fibonacci iterative F(30):", fibonacci_iterative(30))

    print("\nMaster Theorem examples:")
    for result in (
        master_theorem(2, 2, 0),
        master_theorem(2, 2, 1),
        master_theorem(4, 2, 1),
    ):
        print(result.recurrence)
        print("Classification:", result.classification)
        print("Bound:", result.asymptotic_bound)
        print("Reason:", result.reason)

    levels = recurrence_level_costs(
        n=16,
        branching_factor=2,
        shrink_factor=2,
        local_cost=lambda size: size,
    )
    print("\nMerge-sort-style recurrence-tree level costs:", levels)


def demonstrate_complexity() -> None:
    print("\n=== Asymptotic Complexity ===")

    values = list(range(0, 100_000, 2))
    target = 84_246

    print("Linear search result:", linear_search(values, target))
    print("Binary search result:", binary_search(values, target))

    unsorted = [19, 4, 71, 2, 18, 7, 45, 12]
    print("Merge sort:", merge_sort(unsorted))

    print(
        "Conceptual growth order: "
        "1 < log n < n < n log n < n^2 < 2^n"
    )


def demonstrate_sat_and_verification() -> None:
    print("\n=== SAT and NP-Style Verification ===")

    formula = CNFFormula(
        variables=("x1", "x2", "x3"),
        clauses=(
            Clause((Literal("x1"), Literal("x2"), Literal("x3", False))),
            Clause((Literal("x1", False), Literal("x2"), Literal("x3"))),
            Clause((Literal("x1"), Literal("x2", False), Literal("x3"))),
        ),
    )

    solution = brute_force_sat(formula)
    print("SAT certificate found:", solution)

    if solution is not None:
        print("Certificate verifies:", verify_sat_certificate(formula, solution))


def demonstrate_clique() -> None:
    print("\n=== CLIQUE Certificate Verification ===")

    graph = UndirectedGraph(
        vertices={1, 2, 3, 4, 5},
        edges={
            (1, 2), (1, 3), (2, 3),
            (1, 4), (2, 4),
            (3, 5),
        },
    )

    print("Candidate {1, 2, 3} is a clique:", verify_clique(graph, {1, 2, 3}))
    print("Candidate {1, 3, 5} is a clique:", verify_clique(graph, {1, 3, 5}))


def demonstrate_subset_sum() -> None:
    print("\n=== SUBSET SUM ===")

    numbers = [3, 7, 11, 14, 19]
    target = 25

    selected = brute_force_subset_sum(numbers, target)
    print("Selected indices:", selected)

    if selected is not None:
        print(
            "Certificate verifies:",
            verify_subset_sum(numbers, target, selected),
        )


def demonstrate_reduction() -> None:
    print("\n=== Polynomial-Time Reduction: 3-SAT -> CLIQUE ===")

    formula = CNFFormula(
        variables=("a", "b", "c"),
        clauses=(
            Clause((
                Literal("a"),
                Literal("b"),
                Literal("c"),
            )),
            Clause((
                Literal("a", False),
                Literal("b"),
                Literal("c", False),
            )),
            Clause((
                Literal("a"),
                Literal("b", False),
                Literal("c"),
            )),
        ),
    )

    reduction = reduce_3sat_to_clique(formula)

    print("Source clauses:", len(formula.clauses))
    print("Constructed vertices:", len(reduction.graph.vertices))
    print("Constructed edges:", len(reduction.graph.edges))
    print("Target clique size:", reduction.k)

    clique = find_clique_for_reduced_formula(reduction)
    print("Target clique:", clique)

    if clique:
        literals = [reduction.literal_by_vertex[v] for v in clique]
        print(
            "Clique literals:",
            [
                f"{literal.variable}={'TRUE' if literal.positive else 'FALSE'}"
                for literal in literals
            ],
        )


def demonstrate_exponential_boundary() -> None:
    print("\n=== Polynomial versus Exponential Search ===")

    for n in range(8, 21, 4):
        start = perf_counter()
        count = 2**n
        elapsed = perf_counter() - start
        print(
            f"Number of assignments for n={n}: {count:,}; "
            f"enumeration-count calculation time: {elapsed:.8f}s"
        )

    print(
        "The key issue is not that every exponential calculation is slow "
        "for every small input. The issue is that the number of candidates "
        "can multiply rapidly as the input size increases."
    )


def main() -> None:
    demonstrate_recurrences()
    demonstrate_complexity()
    demonstrate_sat_and_verification()
    demonstrate_clique()
    demonstrate_subset_sum()
    demonstrate_reduction()
    demonstrate_exponential_boundary()


if __name__ == "__main__":
    main()
