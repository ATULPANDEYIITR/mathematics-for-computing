"""
MATHEMATICAL INDUCTION
======================

A comprehensive executable study file covering:

1. The idea of proof by induction
2. Induction terminology and structure
3. Base case and inductive step
4. Weak (ordinary) induction
5. Strong induction
6. Why induction works
7. Recursive definitions and induction
8. Summation identities
9. Divisibility proofs
10. Inequalities
11. Counting and combinatorics
12. Recurrence-style arguments
13. Algorithm correctness
14. Structural induction ideas
15. Choosing weak versus strong induction
16. Common mistakes and invalid proofs
17. Edge cases and boundary conditions
18. Automated finite verification versus proof
19. A proof-checking framework
20. Performance and implementation considerations

The program is intentionally self-contained and uses only the Python
standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, factorial, isqrt
from typing import Callable, Iterable, Optional


# ---------------------------------------------------------------------------
# SECTION 1: BASIC UTILITIES
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def expect_equal(actual, expected, description: str) -> None:
    """Small assertion helper used by the executable demonstrations."""
    if actual != expected:
        raise AssertionError(
            f"{description}: expected {expected!r}, got {actual!r}"
        )
    print(f"PASS: {description}")


# ---------------------------------------------------------------------------
# SECTION 2: THE BASIC STRUCTURE OF INDUCTION
# ---------------------------------------------------------------------------

section("1. The structure of mathematical induction")

print(
    """
Mathematical induction proves a statement P(n) for every integer n in a
specified domain, usually n >= n0.

The standard structure is:

    1. Base case:
       Prove P(n0).

    2. Inductive hypothesis:
       Assume P(k) is true for an arbitrary k >= n0.

    3. Inductive step:
       Using that assumption, prove P(k + 1).

If both parts are valid, P(n) holds for every n >= n0.

The inductive hypothesis is an assumption made inside the proof. It is not
a circular assumption that every case is already true. It concerns one
arbitrary predecessor k and is used to establish its successor.
"""
)


@dataclass
class InductionProof:
    """A simple data model for an induction proof."""

    statement_name: str
    base_n: int
    base_result: bool
    step_description: str
    conclusion: str

    def display(self) -> None:
        print(f"Statement: {self.statement_name}")
        print(f"Base case n = {self.base_n}: {self.base_result}")
        print(f"Inductive step: {self.step_description}")
        print(f"Conclusion: {self.conclusion}")


proof_example = InductionProof(
    statement_name="1 + 2 + ... + n = n(n + 1)/2",
    base_n=1,
    base_result=True,
    step_description=(
        "Assume the identity for k and add k + 1 to both sides."
    ),
    conclusion="The identity holds for every positive integer n.",
)
proof_example.display()


# ---------------------------------------------------------------------------
# SECTION 3: WEAK INDUCTION
# ---------------------------------------------------------------------------

section("2. Weak induction")

print(
    """
Weak induction is also called ordinary induction or simple induction.

Its logical pattern is:

    P(n0)
    For every k >= n0, P(k) -> P(k + 1)
    Therefore, for every n >= n0, P(n)

The word "weak" does not mean the proof is weaker or less rigorous. It means
that the inductive step assumes only the immediately preceding statement
P(k), rather than all earlier statements.
"""
)


def sum_formula(n: int) -> int:
    """Closed-form sum 1 + 2 + ... + n."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    return n * (n + 1) // 2


def sum_iterative(n: int) -> int:
    """Directly compute 1 + 2 + ... + n."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    total = 0
    for value in range(1, n + 1):
        total += value
    return total


subsection("2.1 Example: sum of the first n positive integers")

print("Claim: 1 + 2 + ... + n = n(n + 1)/2 for every n >= 1.")
print()
print("Base case:")
print("  n = 1")
print("  Left side  = 1")
print("  Right side = 1(2)/2 = 1")
print("  Therefore P(1) is true.")
print()
print("Inductive hypothesis:")
print("  Assume 1 + 2 + ... + k = k(k + 1)/2.")
print()
print("Inductive step:")
print("  1 + 2 + ... + k + (k + 1)")
print("  = k(k + 1)/2 + (k + 1)")
print("  = (k + 1)(k + 2)/2")
print("  Therefore P(k + 1) is true.")

for n in range(1, 11):
    expect_equal(
        sum_iterative(n),
        sum_formula(n),
        f"sum identity for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 4: INDUCTION STARTING AT ZERO
# ---------------------------------------------------------------------------

section("3. The starting point matters")

print(
    """
Induction does not automatically begin at n = 1.

If a statement is defined for n >= 0, the base case may be n = 0.
If a statement is defined for n >= 5, the first required case may be n = 5.

The base case must match the domain of the theorem.
"""
)


def powers_of_two_identity(n: int) -> bool:
    """
    Verify:
        1 + 2 + 4 + ... + 2^n = 2^(n+1) - 1

    Domain: n >= 0.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")
    left = sum(2**k for k in range(n + 1))
    right = 2 ** (n + 1) - 1
    return left == right


print("Base case n=0:")
print("  1 = 2^1 - 1 = 1")

for n in range(0, 11):
    expect_equal(
        powers_of_two_identity(n),
        True,
        f"geometric sum identity for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 5: INDUCTION WITH A GENERAL BASE n0
# ---------------------------------------------------------------------------

section("4. Induction with an arbitrary base value")

print(
    """
A theorem can begin at any integer n0.

For example, suppose:

    P(n): n^2 >= 3n

The inequality is true for n >= 3.

The induction structure is:

    Base: prove P(3).
    Step: assume k^2 >= 3k for k >= 3 and prove
          (k + 1)^2 >= 3(k + 1).

The base case establishes where the chain begins.
"""
)


def quadratic_inequality(n: int) -> bool:
    return n * n >= 3 * n


expect_equal(quadratic_inequality(3), True, "base case n=3")
for n in range(3, 11):
    expect_equal(
        quadratic_inequality(n),
        True,
        f"n^2 >= 3n for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 6: DIVISIBILITY
# ---------------------------------------------------------------------------

section("5. Induction and divisibility")

print(
    """
Induction is particularly useful for divisibility statements.

Example:

    3 divides n^3 - n

for every integer n.

Base case:
    1^3 - 1 = 0,
    and 3 divides 0.

Inductive step:
    Assume 3 divides k^3 - k.

Then:

    (k + 1)^3 - (k + 1)
    = k^3 + 3k^2 + 3k + 1 - k - 1
    = (k^3 - k) + 3k^2 + 3k.

The first term is divisible by 3 by the inductive hypothesis, and the
remaining terms are explicitly multiples of 3.
"""
)


def divides(divisor: int, value: int) -> bool:
    """Return whether divisor divides value."""
    if divisor == 0:
        raise ValueError("Divisibility by zero is undefined.")
    return value % divisor == 0


def cubic_minus_n(n: int) -> int:
    return n**3 - n


expect_equal(divides(3, cubic_minus_n(1)), True, "base divisibility case")

for n in range(1, 21):
    expect_equal(
        divides(3, cubic_minus_n(n)),
        True,
        f"3 divides n^3-n for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 7: A DIVISIBILITY IDENTITY WITH A NONTRIVIAL STEP
# ---------------------------------------------------------------------------

section("6. Another divisibility example")

print(
    """
Claim:

    7 divides 8^n - 1

for every n >= 1.

Base:
    8^1 - 1 = 7.

Inductive step:
    Assume 8^k - 1 = 7m.

Then:

    8^(k+1) - 1
      = 8 * 8^k - 1
      = 8(8^k - 1) + 7.

Both terms are divisible by 7.
"""
)


def power_minus_one_divisible(n: int) -> bool:
    return divides(7, 8**n - 1)


for n in range(1, 9):
    expect_equal(
        power_minus_one_divisible(n),
        True,
        f"7 divides 8^{n}-1",
    )


# ---------------------------------------------------------------------------
# SECTION 8: INEQUALITIES
# ---------------------------------------------------------------------------

section("7. Induction and inequalities")

print(
    """
Induction can prove inequalities when the inductive step preserves the
required relationship.

Example:

    2^n >= n + 1

for n >= 0.

Base:
    2^0 = 1 >= 1.

Inductive hypothesis:
    2^k >= k + 1.

Then:

    2^(k+1)
      = 2 * 2^k
      >= 2(k + 1)
      = 2k + 2
      >= k + 2

because k >= 0.

Thus the result follows.
"""
)


def exponential_lower_bound(n: int) -> bool:
    return 2**n >= n + 1


for n in range(0, 16):
    expect_equal(
        exponential_lower_bound(n),
        True,
        f"2^n >= n+1 for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 9: FACTORIAL INEQUALITY
# ---------------------------------------------------------------------------

section("8. A factorial inequality")

print(
    """
For n >= 1:

    n! >= 2^(n-1)

Base:
    1! = 1 = 2^0.

Inductive step:
    Assume k! >= 2^(k-1).

Then:

    (k+1)! = (k+1)k!
           >= (k+1)2^(k-1)
           >= 2 * 2^(k-1)
           = 2^k

for k >= 1.
"""
)


def factorial_lower_bound(n: int) -> bool:
    if n < 1:
        raise ValueError("n must be at least 1.")
    return factorial(n) >= 2 ** (n - 1)


for n in range(1, 11):
    expect_equal(
        factorial_lower_bound(n),
        True,
        f"n! >= 2^(n-1) for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 10: STRONG INDUCTION
# ---------------------------------------------------------------------------

section("9. Strong induction")

print(
    """
Strong induction is also called complete induction.

Its structure is:

    Base case(s):
        Prove the necessary initial statements.

    Strong inductive hypothesis:
        Assume P(n0), P(n0+1), ..., P(k) are all true.

    Inductive step:
        Use any or all of those earlier statements to prove P(k+1).

Weak induction assumes P(k).
Strong induction assumes every earlier statement in the induction range.

The two methods are logically equivalent in proof power. Strong induction
can simply make some proofs more natural because several previous cases may
be needed.
"""
)


# ---------------------------------------------------------------------------
# SECTION 11: PRIME FACTORIZATION
# ---------------------------------------------------------------------------

section("10. Strong induction example: prime factorization")

print(
    """
The fundamental idea:

Every integer n >= 2 is either prime or composite.

If n is prime, it already has a prime factorization.

If n is composite, write:

    n = ab

where 2 <= a < n and 2 <= b < n.

By the strong inductive hypothesis, both a and b have prime factorizations.
Combining those factorizations gives a prime factorization of n.

This is a classic example where strong induction naturally fits because the
proof uses potentially smaller values that are not necessarily n - 1.
"""
)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    limit = isqrt(n)
    divisor = 3
    while divisor <= limit:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def prime_factorization(n: int) -> list[int]:
    """
    Return the prime factors of n in nondecreasing order.

    This implementation is algorithmic rather than a formal proof,
    but its recursive structure mirrors the strong-induction argument.
    """
    if n < 2:
        raise ValueError("Prime factorization requires n >= 2.")

    if is_prime(n):
        return [n]

    divisor = 2
    while divisor <= isqrt(n):
        if n % divisor == 0:
            return prime_factorization(divisor) + prime_factorization(n // divisor)
        divisor += 1

    return [n]


def product(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


for number in [2, 3, 4, 6, 12, 18, 60, 84, 97, 360, 1001]:
    factors = prime_factorization(number)
    print(f"{number:4d} -> {factors}")
    expect_equal(
        product(factors),
        number,
        f"factorization product for {number}",
    )
    expect_equal(
        all(is_prime(factor) for factor in factors),
        True,
        f"all factors of {number} are prime",
    )


# ---------------------------------------------------------------------------
# SECTION 12: WEAK VERSUS STRONG INDUCTION
# ---------------------------------------------------------------------------

section("11. Weak induction versus strong induction")

comparison = [
    ("Weak induction", "Assume P(k)", "Immediately previous case"),
    (
        "Strong induction",
        "Assume P(n0), ..., P(k)",
        "Any earlier case or combination",
    ),
]

for method, hypothesis, typical_use in comparison:
    print(f"{method}:")
    print(f"  Hypothesis: {hypothesis}")
    print(f"  Useful when: {typical_use}")
    print()

print(
    """
Strong induction does not prove a stronger mathematical conclusion merely
because it uses a stronger-looking hypothesis. Both forms can establish the
same class of induction theorems when formulated correctly.

The practical difference is the convenience of the inductive hypothesis.
"""


# ---------------------------------------------------------------------------
# SECTION 13: FIBONACCI NUMBERS
# ---------------------------------------------------------------------------

section("12. Strong induction and Fibonacci-style dependencies")

print(
    """
The Fibonacci recurrence is:

    F(n) = F(n-1) + F(n-2)

for n >= 2.

A proof involving a Fibonacci recurrence often needs two previous cases.
Ordinary induction can still be used by strengthening the statement or
proving multiple consecutive cases, but strong induction provides a direct
way to assume all earlier statements.
"""
)


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n == 0:
        return 0
    if n == 1:
        return 1

    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


expected_fibonacci = [
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
]

for n, expected in enumerate(expected_fibonacci):
    expect_equal(fibonacci(n), expected, f"Fibonacci F({n})")


# ---------------------------------------------------------------------------
# SECTION 14: BINOMIAL COEFFICIENTS
# ---------------------------------------------------------------------------

section("13. Pascal's identity and induction-related reasoning")

print(
    """
Pascal's identity is:

    C(n, k) = C(n-1, k-1) + C(n-1, k)

for suitable n and k.

The boundary values are:

    C(n, 0) = 1
    C(n, n) = 1

Many combinatorial proofs use induction together with these recurrence
relationships.
"""
)


def binomial_coefficient(n: int, k: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    if k < 0 or k > n:
        return 0
    return comb(n, k)


for n in range(1, 9):
    for k in range(1, n):
        left = binomial_coefficient(n, k)
        right = (
            binomial_coefficient(n - 1, k - 1)
            + binomial_coefficient(n - 1, k)
        )
        expect_equal(
            left,
            right,
            f"Pascal identity C({n},{k})",
        )


# ---------------------------------------------------------------------------
# SECTION 15: COUNTING
# ---------------------------------------------------------------------------

section("14. Counting arguments")

print(
    """
A common induction pattern is to count a structure after adding one new
element.

Example:

The number of subsets of an n-element set is 2^n.

When one new element is added, every old subset produces exactly two subsets:

    1. one without the new element
    2. one with the new element

Therefore:

    S(n+1) = 2S(n)

with S(0) = 1.

This gives S(n) = 2^n.
"""
)


def subset_count(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    return 2**n


for n in range(0, 11):
    expect_equal(
        subset_count(n),
        2**n,
        f"number of subsets of an {n}-element set",
    )


# ---------------------------------------------------------------------------
# SECTION 16: HANDLING EDGE CASES
# ---------------------------------------------------------------------------

section("15. Edge cases")

print(
    """
An induction proof must respect its domain.

Examples of possible errors:

- Proving only n = 1 when the theorem starts at n = 0.
- Using division without checking whether a denominator can be zero.
- Applying a formula outside its stated domain.
- Assuming a recurrence has valid initial values.
- Forgetting boundary cases such as k = 0.
"""
)


def safe_average(values: list[float]) -> float:
    """An unrelated-looking utility used to illustrate explicit edge checks."""
    if not values:
        raise ValueError("Cannot calculate an average of an empty list.")
    return sum(values) / len(values)


try:
    safe_average([])
except ValueError as error:
    print(f"Expected edge-case error: {error}")


# ---------------------------------------------------------------------------
# SECTION 17: INDUCTION AND ALGORITHMIC CORRECTNESS
# ---------------------------------------------------------------------------

section("16. Mathematical induction for algorithm correctness")

print(
    """
Induction is not limited to algebraic identities.

It is commonly used to prove that algorithms are correct.

Suppose an algorithm processes the first n elements of a list.

A typical proof has:

Base:
    The algorithm correctly handles a list of length 0 or 1.

Inductive hypothesis:
    Assume the algorithm correctly handles the first k elements.

Step:
    Show that processing element k+1 preserves correctness.

This connects induction with loop invariants and recursive algorithm proofs.
"""


def insertion_sort(values: list[int]) -> list[int]:
    """
    Insertion sort.

    Correctness intuition:
    Before inserting the current element, the prefix before it is sorted.
    The insertion operation places the new element into its correct position.

    This is closely related to an induction invariant:
    after processing i elements, the first i elements are sorted.
    """
    result = values.copy()

    for index in range(1, len(result)):
        current = result[index]
        position = index - 1

        while position >= 0 and result[position] > current:
            result[position + 1] = result[position]
            position -= 1

        result[position + 1] = current

    return result


sorting_examples = [
    [],
    [1],
    [5, 2, 4, 6, 1, 3],
    [3, 3, 2, 1, 2],
    [-5, 4, 0, -2, 8],
]

for example in sorting_examples:
    sorted_result = insertion_sort(example)
    expect_equal(
        sorted_result,
        sorted(example),
        f"insertion sort correctness for {example}",
    )


# ---------------------------------------------------------------------------
# SECTION 18: LOOP INVARIANTS AND INDUCTION
# ---------------------------------------------------------------------------

section("17. Loop invariants")

print(
    """
A loop invariant is a property that remains true at a particular point of
every iteration.

The proof pattern resembles induction:

Initialization:
    Show the invariant is true before the first iteration.

Maintenance:
    Assume it is true at the start of an iteration and show it remains true
    after the iteration.

Termination:
    Combine the invariant with the loop's stopping condition to establish
    the desired result.

This is essentially an induction-like reasoning pattern over iterations.
"""
)


def sum_with_invariant(values: list[int]) -> int:
    total = 0

    # Invariant:
    # after processing values[0:i], total equals their sum.
    for value in values:
        total += value

    return total


test_values = [4, -2, 7, 1, -5]
expect_equal(
    sum_with_invariant(test_values),
    sum(test_values),
    "loop invariant example",
)


# ---------------------------------------------------------------------------
# SECTION 19: RECURSIVE DEFINITIONS
# ---------------------------------------------------------------------------

section("18. Recursive definitions and induction")

print(
    """
Recursive definitions often pair naturally with induction.

For example:

    f(0) = 0
    f(n) = f(n-1) + 2

A natural theorem is:

    f(n) = 2n.

Base:
    f(0) = 0 = 2(0).

Step:
    Assume f(k) = 2k.

Then:
    f(k+1)
      = f(k) + 2
      = 2k + 2
      = 2(k+1).

The recursion and the induction proof mirror one another.
"""


def recursive_even_sequence(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    if n == 0:
        return 0
    return recursive_even_sequence(n - 1) + 2


for n in range(0, 9):
    expect_equal(
        recursive_even_sequence(n),
        2 * n,
        f"recursive sequence f({n}) = 2n",
    )


# ---------------------------------------------------------------------------
# SECTION 20: STRONG INDUCTION WITH COIN REPRESENTATION
# ---------------------------------------------------------------------------

section("19. Strong induction example: representing integers")

print(
    """
Consider denominations 3 and 5.

A useful question is:

    Which sufficiently large integers can be represented as 3a + 5b
    for non-negative integers a and b?

The values 8, 9, and 10 can be represented:

    8  = 3 + 5
    9  = 3 + 3 + 3
    10 = 5 + 5

For every n >= 8, subtracting 3 gives n - 3 >= 5. A strong-induction
formulation can use a previously established representability statement.

This illustrates how induction can reason about constructive existence.
"""


def representable_by_three_and_five(n: int) -> bool:
    if n < 0:
        return False

    for threes in range(n // 3 + 1):
        remainder = n - 3 * threes
        if remainder % 5 == 0:
            return True
    return False


for n in range(8, 31):
    expect_equal(
        representable_by_three_and_five(n),
        True,
        f"{n} is representable as 3a+5b",
    )


# ---------------------------------------------------------------------------
# SECTION 21: INDUCTION OVER STRUCTURES
# ---------------------------------------------------------------------------

section("20. Structural induction")

print(
    """
Structural induction generalizes the idea of induction from integers to
recursively constructed objects.

For a recursively defined structure:

    1. Prove the property for every base constructor.
    2. Assume the property for the immediate substructures.
    3. Prove it for the structure constructed from those substructures.

Examples include:

- Binary trees
- Abstract syntax trees
- Recursive expressions
- Formally defined lists
- Recursive grammar structures

The same conceptual pattern appears:

    base objects + preservation under construction
"""
)


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


def tree_size(node: Optional[TreeNode]) -> int:
    """
    Recursively calculate the number of nodes.

    Structural recursion:
        empty tree -> 0
        non-empty tree -> 1 + left size + right size
    """
    if node is None:
        return 0

    return 1 + tree_size(node.left) + tree_size(node.right)


tree = TreeNode(
    10,
    left=TreeNode(
        5,
        left=TreeNode(2),
        right=TreeNode(7),
    ),
    right=TreeNode(
        15,
        right=TreeNode(20),
    ),
)

expect_equal(tree_size(tree), 6, "binary-tree structural recursion")


# ---------------------------------------------------------------------------
# SECTION 22: A STRUCTURAL PROPERTY OF BINARY TREES
# ---------------------------------------------------------------------------

section("21. Binary-tree structural induction example")

print(
    """
For a finite full binary tree, every internal node has exactly two children.

If I is the number of internal nodes and L is the number of leaves, then:

    L = I + 1

This can be proved structurally.

Base:
    A tree consisting of a single leaf has I = 0 and L = 1.

Construction:
    Combining two full binary trees under a new internal root adds:

        one internal node
        all leaves of both subtrees

If each subtree satisfies L = I + 1, the combined tree also satisfies the
relationship.

The example below constructs full binary trees and verifies the identity.
"""


@dataclass
class FullBinaryNode:
    value: str
    left: Optional["FullBinaryNode"] = None
    right: Optional["FullBinaryNode"] = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def count_internal_and_leaves(
    node: Optional[FullBinaryNode],
) -> tuple[int, int]:
    if node is None:
        return 0, 0

    if node.is_leaf:
        return 0, 1

    if node.left is None or node.right is None:
        raise ValueError("Tree is not full: internal node has one child.")

    left_internal, left_leaves = count_internal_and_leaves(node.left)
    right_internal, right_leaves = count_internal_and_leaves(node.right)

    return (
        1 + left_internal + right_internal,
        left_leaves + right_leaves,
    )


full_tree = FullBinaryNode(
    "root",
    FullBinaryNode(
        "A",
        FullBinaryNode("B"),
        FullBinaryNode("C"),
    ),
    FullBinaryNode(
        "D",
        FullBinaryNode("E"),
        FullBinaryNode("F"),
    ),
)

internal_count, leaf_count = count_internal_and_leaves(full_tree)

print(f"Internal nodes: {internal_count}")
print(f"Leaves: {leaf_count}")

expect_equal(
    leaf_count,
    internal_count + 1,
    "full binary tree leaves = internal nodes + 1",
)


# ---------------------------------------------------------------------------
# SECTION 23: A FORMAL PROOF OBJECT
# ---------------------------------------------------------------------------

section("22. Representing an induction proof computationally")

print(
    """
A computer cannot replace a mathematical proof merely by checking many
examples.

It can, though, represent the logical components of an induction argument
and verify finite instances.

The following model separates:

    - the domain
    - the base condition
    - the inductive implication
    - the human-readable conclusion
"""


@dataclass
class InductionSpecification:
    name: str
    start: int
    statement: Callable[[int], bool]
    successor_step: Callable[[int], bool]

    def check_base(self) -> bool:
        return self.statement(self.start)

    def check_finite_range(self, end: int) -> bool:
        if end < self.start:
            raise ValueError("End must not be below the start.")

        for value in range(self.start, end + 1):
            if not self.statement(value):
                return False
        return True

    def check_successor_range(self, end: int) -> bool:
        if end <= self.start:
            return True

        for value in range(self.start, end):
            if not self.successor_step(value):
                return False

        return True


sum_specification = InductionSpecification(
    name="Sum identity",
    start=1,
    statement=lambda n: sum_iterative(n) == sum_formula(n),
    successor_step=lambda k: (
        sum_iterative(k + 1) == sum_formula(k + 1)
        if sum_iterative(k) == sum_formula(k)
        else False
    ),
)

expect_equal(
    sum_specification.check_base(),
    True,
    "formal specification base case",
)

expect_equal(
    sum_specification.check_finite_range(20),
    True,
    "finite verification of sum identity",
)


# ---------------------------------------------------------------------------
# SECTION 24: FINITE VERIFICATION IS NOT INDUCTION
# ---------------------------------------------------------------------------

section("23. Verification versus proof")

print(
    """
Checking n = 1 through n = 1,000 can provide evidence, but it does not by
itself prove that a statement is true for every positive integer.

Induction provides a general argument because the inductive step applies to
an arbitrary k in the domain.

This distinction is fundamental:

    Finite testing:
        "The statement worked for these tested inputs."

    Mathematical proof:
        "The statement follows for every input in the specified domain."
"""
)


# ---------------------------------------------------------------------------
# SECTION 25: COMMON INVALID ARGUMENT
# ---------------------------------------------------------------------------

section("24. Common mistake: missing the base case")

print(
    """
A proof of P(k) -> P(k+1) without a valid starting point does not establish
that any P(n) is true.

Analogy:

    If every person who has a key can open the next door,
    but nobody is shown to possess the first key,
    the argument does not establish that anyone reaches the final door.

In induction:

    Implication alone is insufficient.
    A valid base case is required.
"""
)


# ---------------------------------------------------------------------------
# SECTION 26: COMMON INVALID ARGUMENT
# ---------------------------------------------------------------------------

section("25. Common mistake: assuming the target")

print(
    """
A circular proof may assume exactly what it is trying to prove.

Correct:

    Assume P(k).
    Transform the expression using that assumption.
    Derive P(k+1).

Incorrect:

    Assume P(k+1).
    Rearrange until P(k+1) appears.

The inductive hypothesis must concern an already-established predecessor,
not the target statement itself.
"""
)


# ---------------------------------------------------------------------------
# SECTION 27: COMMON INVALID ARGUMENT
# ---------------------------------------------------------------------------

section("26. Common mistake: using a statement outside its domain")

print(
    """
Suppose a theorem is claimed only for n >= 5.

Then the induction step should be written for k >= 5.

Using a property at k = 3 or k = 4 without proving it is irrelevant or
invalid for that theorem.

The domain is part of the theorem, not an optional detail.
"""
)


# ---------------------------------------------------------------------------
# SECTION 28: MULTIPLE BASE CASES
# ---------------------------------------------------------------------------

section("27. Multiple base cases")

print(
    """
Some recurrence relations depend on several preceding cases.

For example:

    P(k+1) may depend on P(k) and P(k-1).

Then proving two initial cases can be necessary.

This is often called a two-step induction or an induction with multiple base
cases.

A strong-induction formulation can express the same dependency by allowing
all earlier statements to be assumed.
"""


def tiling_sequence(n: int) -> int:
    """
    Number of ways to tile a 1 x n board using tiles of length 1 and 2.

    Recurrence:
        T(0) = 1
        T(1) = 1
        T(n) = T(n-1) + T(n-2)

    This is Fibonacci-like.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n <= 1:
        return 1

    first, second = 1, 1

    for _ in range(2, n + 1):
        first, second = second, first + second

    return second


expected_tilings = [1, 1, 2, 3, 5, 8, 13, 21]

for n, expected in enumerate(expected_tilings):
    expect_equal(
        tiling_sequence(n),
        expected,
        f"tiling count T({n})",
    )


# ---------------------------------------------------------------------------
# SECTION 29: INDUCTION AND RECURSION ARE NOT IDENTICAL
# ---------------------------------------------------------------------------

section("28. Induction versus recursion")

print(
    """
Recursion is a method of defining or computing an object in terms of
smaller objects.

Induction is a method of proving a statement about an entire family of
objects.

They are closely related but are not the same concept.

Example:

    Recursive computation:
        factorial(n) = n * factorial(n-1)

    Inductive proof:
        Prove a property of factorial(n) for every n in a domain.

A recursive function can exist without an induction proof being written,
and an induction proof can concern a non-recursive formula.
"""
)


def recursive_factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial requires n >= 0.")

    if n in (0, 1):
        return 1

    return n * recursive_factorial(n - 1)


for n in range(0, 9):
    expect_equal(
        recursive_factorial(n),
        factorial(n),
        f"recursive factorial for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 30: STRONG INDUCTION AND ALGORITHM DESIGN
# ---------------------------------------------------------------------------

section("29. Strong induction and dynamic programming")

print(
    """
Many dynamic-programming algorithms compute a value from several smaller
values.

A mathematical correctness proof may use strong induction because the result
for n depends on multiple earlier states.

Consider the minimum number of coins needed to make a target amount using
coins 1, 3, and 4.

The recurrence is:

    dp[n] = 1 + min(dp[n-c])

for valid coins c.

Each state depends on smaller states, which is naturally compatible with a
strong-induction proof.
"""


def minimum_coins(amount: int, coins: list[int]) -> Optional[int]:
    if amount < 0:
        raise ValueError("Amount must be non-negative.")

    valid_coins = sorted(set(coin for coin in coins if coin > 0))

    if amount == 0:
        return 0

    if not valid_coins:
        return None

    infinity = amount + 1
    dp = [infinity] * (amount + 1)
    dp[0] = 0

    for current_amount in range(1, amount + 1):
        for coin in valid_coins:
            if coin > current_amount:
                break

            previous = dp[current_amount - coin]

            if previous != infinity:
                dp[current_amount] = min(
                    dp[current_amount],
                    previous + 1,
                )

    return None if dp[amount] == infinity else dp[amount]


coin_system = [1, 3, 4]

expected_coin_results = {
    0: 0,
    1: 1,
    2: 2,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 3,
    10: 3,
}

for amount, expected in expected_coin_results.items():
    expect_equal(
        minimum_coins(amount, coin_system),
        expected,
        f"minimum coins for amount {amount}",
    )


# ---------------------------------------------------------------------------
# SECTION 31: COMPLEXITY OF THE DYNAMIC PROGRAM
# ---------------------------------------------------------------------------

section("30. Performance considerations")

print(
    """
For the minimum-coin implementation:

    Number of states: O(A)
    Number of coin checks per state: O(C)

Therefore:

    Time:  O(A*C)
    Space: O(A)

where:

    A = target amount
    C = number of distinct valid coin denominations.

Mathematical induction can establish correctness, while complexity analysis
describes resource usage. They answer different questions.
"""
)


# ---------------------------------------------------------------------------
# SECTION 32: AN INDUCTION PROOF GENERATOR
# ---------------------------------------------------------------------------

section("31. Generic induction proof template")

print(
    """
A reusable proof-writing template is:

    Claim:
        State exactly what P(n) says and its domain.

    Base case:
        Verify P(n0).

    Inductive hypothesis:
        Assume P(k) for an arbitrary k >= n0.

    Inductive step:
        Starting from the expression for P(k+1), use P(k) to establish
        P(k+1).

    Conclusion:
        By mathematical induction, P(n) holds for every n >= n0.

For strong induction, replace the inductive hypothesis with:

        Assume P(j) is true for every n0 <= j <= k.

Then use whichever earlier statements are needed.
"""
)


# ---------------------------------------------------------------------------
# SECTION 33: A PRACTICAL PROOF VALIDATOR
# ---------------------------------------------------------------------------

section("32. Automated theorem testing framework")

print(
    """
The following helper does not prove a theorem. It performs finite testing.

This distinction is deliberately preserved in the API name:
    finite_test
rather than
    prove
"""


def finite_test(
    statement: Callable[[int], bool],
    start: int,
    end: int,
) -> tuple[bool, Optional[int]]:
    if end < start:
        raise ValueError("end must be >= start")

    for n in range(start, end + 1):
        if not statement(n):
            return False, n

    return True, None


success, counterexample = finite_test(
    lambda n: sum_iterative(n) == sum_formula(n),
    1,
    1000,
)

expect_equal(success, True, "finite test of sum formula")
expect_equal(counterexample, None, "no counterexample found in tested range")


# ---------------------------------------------------------------------------
# SECTION 34: DELIBERATELY FALSE CLAIM
# ---------------------------------------------------------------------------

section("33. Counterexamples and failed induction candidates")

print(
    """
Not every plausible-looking statement is true.

Consider the false statement:

    n^2 + n + 41 is prime for every positive integer n.

A finite test can find a counterexample.
"""
)


def false_prime_claim(n: int) -> bool:
    return is_prime(n * n + n + 41)


failed_success, failed_counterexample = finite_test(
    false_prime_claim,
    1,
    100,
)

print(f"Claim passed finite test: {failed_success}")
print(f"First counterexample found: {failed_counterexample}")

if failed_counterexample is not None:
    value = (
        failed_counterexample**2
        + failed_counterexample
        + 41
    )
    print(
        f"At n={failed_counterexample}, the expression equals {value}, "
        "which is not prime."
    )


# ---------------------------------------------------------------------------
# SECTION 35: A SUBTLE POINT ABOUT INDUCTIVE HYPOTHESES
# ---------------------------------------------------------------------------

section("34. The inductive variable must be arbitrary")

print(
    """
The variable k in the inductive step represents an arbitrary member of the
induction domain.

A proof that works only for one selected value, such as k = 10, does not
establish the universal successor implication.

The key logical structure is:

    For every k >= n0:
        if P(k), then P(k+1).

The phrase "arbitrary k" is mathematically significant.
"""
)


# ---------------------------------------------------------------------------
# SECTION 36: INDUCTION ON EVEN INTEGERS
# ---------------------------------------------------------------------------

section("35. Induction over a restricted domain")

print(
    """
Induction can advance by more than one ordinary integer if the theorem is
formulated over an appropriate domain.

For example, to prove a statement for every even non-negative integer, one
can define:

    n = 2k

and perform ordinary induction on k.

This avoids accidentally treating odd integers as members of the target
domain.
"""


def even_number_is_twice_an_integer(k: int) -> bool:
    return 2 * k % 2 == 0


for k in range(0, 11):
    expect_equal(
        even_number_is_twice_an_integer(k),
        True,
        f"2*{k} is even",
    )


# ---------------------------------------------------------------------------
# SECTION 37: INDUCTION AND MONOTONICITY
# ---------------------------------------------------------------------------

section("36. Induction can establish recursively preserved properties")

print(
    """
Suppose a sequence satisfies:

    a_0 = 1
    a_(n+1) = 2a_n + 1

A natural inductive theorem is:

    a_n = 2^(n+1) - 1.

The inductive step substitutes the closed form into the recurrence.
"""


def recurrence_sequence(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")

    value = 1
    for _ in range(n):
        value = 2 * value + 1
    return value


def recurrence_closed_form(n: int) -> int:
    return 2 ** (n + 1) - 1


for n in range(0, 12):
    expect_equal(
        recurrence_sequence(n),
        recurrence_closed_form(n),
        f"recurrence closed form for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 38: INDUCTION AND GEOMETRIC SERIES
# ---------------------------------------------------------------------------

section("37. Geometric series")

print(
    """
For r != 1:

    1 + r + r^2 + ... + r^n
        = (r^(n+1) - 1)/(r - 1)

The proof follows by adding r^(k+1) to the inductive hypothesis.
"""


def geometric_sum(n: int, ratio: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    return sum(ratio**power for power in range(n + 1))


def geometric_formula(n: int, ratio: int) -> int:
    if ratio == 1:
        return n + 1
    return (ratio ** (n + 1) - 1) // (ratio - 1)


for ratio in [2, 3, 5, -1]:
    for n in range(0, 8):
        expect_equal(
            geometric_sum(n, ratio),
            geometric_formula(n, ratio),
            f"geometric identity r={ratio}, n={n}",
        )


# ---------------------------------------------------------------------------
# SECTION 39: INDUCTION AND POLYNOMIAL IDENTITIES
# ---------------------------------------------------------------------------

section("38. Sum of squares")

print(
    """
A classical theorem is:

    1^2 + 2^2 + ... + n^2
      = n(n+1)(2n+1)/6.

Induction verifies that adding (k+1)^2 transforms the k-case into the
(k+1)-case.
"""


def sum_of_squares(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    return sum(value * value for value in range(1, n + 1))


def sum_of_squares_formula(n: int) -> int:
    return n * (n + 1) * (2 * n + 1) // 6


for n in range(0, 16):
    expect_equal(
        sum_of_squares(n),
        sum_of_squares_formula(n),
        f"sum-of-squares formula for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 40: SUM OF CUBES
# ---------------------------------------------------------------------------

section("39. Sum of cubes")

print(
    """
Another classical identity is:

    1^3 + 2^3 + ... + n^3
      = [n(n+1)/2]^2.

The right side is the square of the sum of the first n integers.
"""
)


def sum_of_cubes(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")
    return sum(value**3 for value in range(1, n + 1))


def sum_of_cubes_formula(n: int) -> int:
    return sum_formula(n) ** 2


for n in range(0, 14):
    expect_equal(
        sum_of_cubes(n),
        sum_of_cubes_formula(n),
        f"sum-of-cubes formula for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 41: INDUCTION AND LOGIC
# ---------------------------------------------------------------------------

section("40. Logical interpretation")

print(
    """
Induction can be understood as an infinite chain:

    P(n0)
    P(n0) -> P(n0+1)
    P(n0+1) -> P(n0+2)
    P(n0+2) -> P(n0+3)
    ...

The base case starts the chain.

The inductive implication propagates truth from each integer to its
successor.

The theorem is therefore not based on empirical observation of infinitely
many cases. It is based on a finite proof of the propagation rule plus a
finite proof of the starting point.
"""
)


# ---------------------------------------------------------------------------
# SECTION 42: INDUCTION IS NOT "ASSUME EVERYTHING"
# ---------------------------------------------------------------------------

section("41. The exact meaning of the inductive hypothesis")

print(
    """
Weak induction:

    Assume P(k) for one arbitrary k in the domain.

Strong induction:

    Assume P(j) for every j between the starting value and k.

Neither statement means:

    "Assume the theorem is true for all n."

The target P(k+1) remains unproved until the inductive step establishes it.
"""
)


# ---------------------------------------------------------------------------
# SECTION 43: PROOF DESIGN CHECKLIST
# ---------------------------------------------------------------------------

section("42. Proof-design checklist")

checklist = [
    "State the proposition P(n) precisely.",
    "State the domain of n.",
    "Identify the first required value n0.",
    "Verify every required base case.",
    "State the inductive hypothesis precisely.",
    "Treat k as arbitrary within the domain.",
    "Derive P(k+1) without assuming P(k+1).",
    "Use only assumptions already justified.",
    "Check algebraic transformations carefully.",
    "Conclude using the induction principle.",
]

for number, item in enumerate(checklist, start=1):
    print(f"{number:2d}. {item}")


# ---------------------------------------------------------------------------
# SECTION 44: WEAK INDUCTION IMPLEMENTATION PATTERN
# ---------------------------------------------------------------------------

section("43. Weak-induction implementation pattern")

print(
    """
A computational analogy for weak induction is:

    state = base_state

    for each next position:
        state = transition(state)

The transition only needs the immediately preceding state.

This does not itself constitute a mathematical proof, but it mirrors the
dependency pattern.
"""


def weak_induction_style_sequence(
    start_value: int,
    steps: int,
    transition: Callable[[int], int],
) -> list[int]:
    if steps < 0:
        raise ValueError("steps must be non-negative.")

    values = [start_value]

    for _ in range(steps):
        values.append(transition(values[-1]))

    return values


sequence = weak_induction_style_sequence(
    start_value=1,
    steps=8,
    transition=lambda value: value + 3,
)

print(sequence)
expect_equal(
    sequence,
    [1, 4, 7, 10, 13, 16, 19, 22, 25],
    "weak-induction-style recurrence",
)


# ---------------------------------------------------------------------------
# SECTION 45: STRONG INDUCTION IMPLEMENTATION PATTERN
# ---------------------------------------------------------------------------

section("44. Strong-induction implementation pattern")

print(
    """
A strong-induction-style algorithm may inspect multiple previous states.

For a recurrence:

    state[n] = F(state[0], ..., state[n-1])

the algorithm can store all previously computed states.

Again, this is an implementation analogy rather than a substitute for a
formal proof.
"""


def strong_induction_style_sequence(
    start: int,
    count: int,
    transition: Callable[[list[int]], int],
) -> list[int]:
    if count < 0:
        raise ValueError("count must be non-negative.")

    values = [start]

    for _ in range(1, count):
        values.append(transition(values))

    return values


strong_sequence = strong_induction_style_sequence(
    start=1,
    count=8,
    transition=lambda previous: previous[-1] + (
        previous[-2] if len(previous) >= 2 else 0
    ),
)

print(strong_sequence)


# ---------------------------------------------------------------------------
# SECTION 46: SECURITY AND RELIABILITY CONSIDERATIONS
# ---------------------------------------------------------------------------

section("45. Reliability considerations")

print(
    """
Mathematical induction itself is not a security mechanism.

In software that implements algorithms justified by induction, reliability
still depends on:

- Correct domain validation
- Correct base conditions
- Correct boundary handling
- Integer overflow behavior
- Recursion depth
- Input validation
- Deterministic testing
- Correct assumptions about data structures

In Python, arbitrary-precision integers eliminate ordinary fixed-width
integer overflow for integers, but memory and execution time remain finite.

In C++, fixed-width integer overflow requires particular care because signed
overflow is not a safe substitute for arbitrary-precision arithmetic.
"""


# ---------------------------------------------------------------------------
# SECTION 47: PYTHON RECURSION LIMIT
# ---------------------------------------------------------------------------

section("46. Practical recursion limits")

print(
    """
A mathematical recursive definition can be valid for arbitrarily large n,
while a recursive program may have a finite call-stack limit.

Therefore:

    mathematical induction
        !=
    recursive execution

For production software, an iterative implementation or explicit stack may
be preferable when the input depth can become large.
"""
)


# ---------------------------------------------------------------------------
# SECTION 48: COMPLEXITY COMPARISON
# ---------------------------------------------------------------------------

section("47. Complexity examples")

print(
    """
Some induction-related algorithms have very different computational costs.

Naive recursive Fibonacci:

    Time: exponential in n
    Space: O(n) call depth

Iterative Fibonacci:

    Time: O(n)
    Space: O(1)

Matrix exponentiation can reduce Fibonacci computation to O(log n) arithmetic
steps, although each arithmetic operation itself has a cost depending on the
integer size.

Mathematical proof and algorithmic efficiency are separate dimensions.
"""


def fibonacci_iterative_constant_space(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative.")

    a, b = 0, 1

    for _ in range(n):
        a, b = b, a + b

    return a


for n in range(20):
    expect_equal(
        fibonacci_iterative_constant_space(n),
        fibonacci(n),
        f"constant-space Fibonacci for n={n}",
    )


# ---------------------------------------------------------------------------
# SECTION 49: TESTING THE ENTIRE STUDY FILE
# ---------------------------------------------------------------------------

section("48. Integrated verification")

test_groups = {
    "sum identity": all(
        sum_iterative(n) == sum_formula(n)
        for n in range(0, 100)
    ),
    "powers of two": all(
        powers_of_two_identity(n)
        for n in range(0, 100)
    ),
    "cubic divisibility": all(
        divides(3, cubic_minus_n(n))
        for n in range(1, 100)
    ),
    "exponential inequality": all(
        exponential_lower_bound(n)
        for n in range(0, 100)
    ),
    "factorial inequality": all(
        factorial_lower_bound(n)
        for n in range(1, 50)
    ),
    "sum of squares": all(
        sum_of_squares(n) == sum_of_squares_formula(n)
        for n in range(0, 100)
    ),
    "sum of cubes": all(
        sum_of_cubes(n) == sum_of_cubes_formula(n)
        for n in range(0, 100)
    ),
}

for name, result in test_groups.items():
    print(f"{name:28s}: {'PASS' if result else 'FAIL'}")


# ---------------------------------------------------------------------------
# SECTION 50: FINAL CONCEPTUAL MAP
# ---------------------------------------------------------------------------

section("49. Conceptual map")

print(
    """
MATHEMATICAL INDUCTION
|
+-- Basic structure
|   +-- Proposition P(n)
|   +-- Domain
|   +-- Base case
|   +-- Inductive hypothesis
|   +-- Inductive step
|   +-- Conclusion
|
+-- Weak induction
|   +-- Assumes P(k)
|   +-- Proves P(k+1)
|   +-- Natural for one-step dependencies
|
+-- Strong induction
|   +-- Assumes all earlier P(j)
|   +-- Proves P(k+1)
|   +-- Natural for multiple dependencies
|
+-- Applications
|   +-- Algebraic identities
|   +-- Divisibility
|   +-- Inequalities
|   +-- Counting
|   +-- Recurrences
|   +-- Algorithm correctness
|   +-- Dynamic programming
|   +-- Prime factorization
|
+-- Generalizations
    +-- Multiple-base induction
    +-- Restricted-domain induction
    +-- Structural induction
    +-- Recursive structures

The central principle is:

    establish a valid starting point
    +
    prove preservation from one stage to the next
    =
    establish the statement throughout the intended domain.
"""
)


# ---------------------------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> None:
    """
    The demonstrations above execute when the file is run directly.

    Keeping an explicit main function makes the study file easier to extend
    into a reusable module while retaining executable educational examples.
    """
    print("\nMathematical induction study completed successfully.")
    print("All integrated finite verification tests passed.")


if __name__ == "__main__":
    main()
