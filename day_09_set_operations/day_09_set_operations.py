"""
SET OPERATIONS: FROM BEGINNER TO ADVANCED

A self-contained study script covering:
- Sets and set notation
- Membership and subset relations
- Union
- Intersection
- Difference
- Complement
- Symmetric difference
- Cartesian product
- Power sets
- Cardinality and inclusion-exclusion
- Venn-diagram data and ASCII visualization
- Set identities and verification
- Relations between set operations
- Nested and immutable sets
- Practical applications
- Edge cases and common mistakes
- Complexity and implementation considerations
- Advanced finite-set algorithms
- Testing and validation

The script uses only Python's standard library.
"""

from __future__ import annotations

from itertools import product
from math import comb
from typing import FrozenSet, Iterable, TypeVar


T = TypeVar("T")


# =============================================================================
# 1. FOUNDATIONS: WHAT IS A SET?
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a readable subsection heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


section("1. FOUNDATIONS: SETS")

# A set is an unordered collection of distinct objects.
# Curly braces create a set when they contain elements:
numbers = {1, 2, 3, 4, 5}

# Duplicate values are automatically removed.
duplicate_values = {1, 2, 2, 3, 3, 3}
print("Set with duplicates removed:", duplicate_values)

# An empty set must be created with set(), not {}.
empty_set = set()
empty_dictionary = {}
print("Empty set:", empty_set)
print("Empty dictionary:", empty_dictionary)

# Strings, integers, tuples, and many other hashable objects can be elements.
mixed_set = {1, "Python", 3.14, (10, 20)}
print("Mixed set:", mixed_set)

# A set does not preserve meaningful positional order.
# Therefore indexing is invalid:
try:
    print(numbers[0])
except TypeError as error:
    print("Sets do not support indexing:", error)

# Membership testing is one of the principal uses of a set.
print("3 in numbers:", 3 in numbers)
print("99 in numbers:", 99 in numbers)

# len() gives the cardinality, meaning the number of distinct elements.
print("Cardinality of numbers:", len(numbers))


# =============================================================================
# 2. SET NOTATION AND TERMINOLOGY
# =============================================================================

section("2. SET NOTATION AND TERMINOLOGY")

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}
U = set(range(1, 9))  # Universal set for this example.

print("A =", A)
print("B =", B)
print("U =", U)

# Common mathematical notation:
#
# x ∈ A       x belongs to A
# x ∉ A       x does not belong to A
# A ⊆ B       A is a subset of B
# A ⊂ B       A is a proper subset of B
# A = B       A and B contain exactly the same elements
# A ∪ B       union
# A ∩ B       intersection
# A - B       difference
# Aᶜ          complement of A relative to U
# A Δ B       symmetric difference
# A × B       Cartesian product
#
# In Python:
#
# x in A
# x not in A
# A <= B
# A < B
# A == B
# A | B
# A & B
# A - B
# U - A
# A ^ B
# set(product(A, B))

print("3 belongs to A:", 3 in A)
print("10 does not belong to A:", 10 not in A)


# =============================================================================
# 3. UNION
# =============================================================================

section("3. UNION")

# The union contains every element that belongs to A, B, or both.
#
# Mathematical definition:
# A ∪ B = {x | x ∈ A OR x ∈ B}

union_operator = A | B
union_method = A.union(B)

print("A ∪ B using |:", union_operator)
print("A ∪ B using union():", union_method)

# Repeated elements occur only once.
C = {1, 2, 3}
D = {3, 4, 5}
print("C ∪ D:", C | D)

# Union can involve more than two sets.
E = {5, 6, 7}
print("A ∪ B ∪ E:", A | B | E)

# The update form modifies the left-hand set in place.
mutable_union = {1, 2}
mutable_union.update({2, 3, 4})
print("After update:", mutable_union)

# Important distinction:
# | returns a new set; |= modifies the existing set.
original = {1, 2}
result = original | {3}
print("Original after |:", original)
print("Result:", result)

original |= {3}
print("Original after |=:", original)


# =============================================================================
# 4. INTERSECTION
# =============================================================================

section("4. INTERSECTION")

# The intersection contains elements common to every participating set.
#
# A ∩ B = {x | x ∈ A AND x ∈ B}

print("A ∩ B:", A & B)
print("Using intersection():", A.intersection(B))

# Multiple-set intersection.
F = {3, 4, 7}
print("A ∩ B ∩ F:", A & B & F)

# An empty intersection means no common elements.
disjoint_1 = {1, 2}
disjoint_2 = {3, 4}
print("Disjoint intersection:", disjoint_1 & disjoint_2)

# The in-place operation &= modifies the set.
common = {1, 2, 3, 4}
common &= {2, 3, 5}
print("After &=:", common)


# =============================================================================
# 5. DIFFERENCE
# =============================================================================

section("5. DIFFERENCE")

# A - B contains elements that are in A but not in B.
#
# A - B = {x | x ∈ A AND x ∉ B}

print("A - B:", A - B)
print("B - A:", B - A)

# Difference is generally not commutative:
# A - B != B - A
print("A - B equals B - A:", A - B == B - A)

# Removing elements that are absent is harmless with difference().
print("{1, 2} - {99}:", {1, 2} - {99})

# remove() raises KeyError if the element is absent.
values = {1, 2, 3}
try:
    values.remove(99)
except KeyError as error:
    print("remove() on an absent element:", error)

# discard() silently ignores an absent element.
values.discard(99)
print("After discard(99):", values)

# pop() removes and returns an arbitrary element.
# Do not rely on a specific element being selected.
sample = {10, 20, 30}
removed = sample.pop()
print("Element returned by pop():", removed)
print("Remaining set:", sample)


# =============================================================================
# 6. COMPLEMENT
# =============================================================================

section("6. COMPLEMENT")

# A complement is meaningful only relative to a universal set U.
#
# Aᶜ = U - A
#
# Without specifying U, the complement is ambiguous.

U = set(range(1, 11))
A = {1, 2, 3, 4}

complement_A = U - A
print("Universal set U:", U)
print("A:", A)
print("Aᶜ relative to U:", complement_A)

# The same set A can have different complements under different universes.
U2 = {1, 2, 3, 4, 5}
print("Aᶜ relative to U2:", U2 - A)

# Complement properties:
# A ∪ Aᶜ = U
# A ∩ Aᶜ = ∅
print("A ∪ Aᶜ:", A | complement_A)
print("A ∩ Aᶜ:", A & complement_A)

# The double complement returns the original set,
# provided both complements use the same universal set.
double_complement = U - (U - A)
print("(Aᶜ)ᶜ:", double_complement)


# =============================================================================
# 7. SYMMETRIC DIFFERENCE
# =============================================================================

section("7. SYMMETRIC DIFFERENCE")

# Symmetric difference contains elements belonging to exactly one set.
#
# A Δ B = (A - B) ∪ (B - A)
#
# It can also be written as:
# A Δ B = (A ∪ B) - (A ∩ B)

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

symmetric_1 = A ^ B
symmetric_2 = A.symmetric_difference(B)
symmetric_3 = (A - B) | (B - A)
symmetric_4 = (A | B) - (A & B)

print("A Δ B:", symmetric_1)
print("Equivalent construction:", symmetric_2)
print("Difference-based construction:", symmetric_3)
print("Union-minus-intersection:", symmetric_4)

# Symmetric difference is commutative.
print("A Δ B == B Δ A:", A ^ B == B ^ A)

# It is also associative.
G = {2, 4, 6, 8}
print("(A Δ B) Δ G:", (A ^ B) ^ G)
print("A Δ (B Δ G):", A ^ (B ^ G))


# =============================================================================
# 8. SET OPERATIONS AS LOGICAL OPERATIONS
# =============================================================================

section("8. SET OPERATIONS AND LOGIC")

# Set operations correspond closely to Boolean logic:
#
# Union        -> OR
# Intersection -> AND
# Difference   -> AND NOT
# Complement   -> NOT
#
# Membership can therefore be viewed as a Boolean proposition.

def membership_truth_table(
    universe: set[int],
    first: set[int],
    second: set[int],
) -> None:
    """Display logical membership values for two sets."""
    print("x | x∈A | x∈B | x∈A∪B | x∈A∩B | x∈A-B")
    print("-" * 42)
    for x in sorted(universe):
        in_a = x in first
        in_b = x in second
        print(
            f"{x:1d} | {str(in_a):4s} | {str(in_b):4s} | "
            f"{str(in_a or in_b):6s} | {str(in_a and in_b):6s} | "
            f"{str(in_a and not in_b):5s}"
        )


membership_truth_table(set(range(1, 7)), {1, 2, 3}, {3, 4, 5})


# =============================================================================
# 9. SUBSETS, PROPER SUBSETS, AND EQUALITY
# =============================================================================

section("9. SUBSETS AND SET RELATIONSHIPS")

A = {1, 2}
B = {1, 2, 3}
C = {1, 2}

print("A ⊆ B:", A <= B)
print("A ⊂ B:", A < B)
print("B ⊆ A:", B <= A)
print("A == C:", A == C)

# A set is always a subset of itself.
print("A ⊆ A:", A <= A)

# The empty set is a subset of every set.
print("∅ ⊆ A:", set() <= A)
print("∅ ⊆ B:", set() <= B)

# Proper subset means subset but not equal.
print("A < C:", A < C)
print("A < B:", A < B)

# Disjoint sets have no common elements.
D = {10, 11}
E = {12, 13}
print("D and E are disjoint:", D.isdisjoint(E))

# Equality can be established through mutual inclusion.
print("A == C through mutual subsets:", A <= C and C <= A)


# =============================================================================
# 10. DISJOINT SETS
# =============================================================================

section("10. DISJOINT SETS")

# Two sets are disjoint if their intersection is empty.
def are_disjoint(first: set[T], second: set[T]) -> bool:
    """Return True when two sets have no common elements."""
    return len(first & second) == 0


students_python = {"A", "B", "C"}
students_java = {"D", "E"}
students_both = {"F"}

print("Python and Java sets are disjoint:", are_disjoint(students_python, students_java))
print("Using isdisjoint():", students_python.isdisjoint(students_java))

# A common mistake is to confuse disjointness with inequality.
# Different sets can overlap.
print("{1, 2} and {2, 3} are disjoint:", {1, 2}.isdisjoint({2, 3}))


# =============================================================================
# 11. CARTESIAN PRODUCT
# =============================================================================

section("11. CARTESIAN PRODUCT")

# The Cartesian product A × B is the set of ordered pairs (a, b)
# such that a ∈ A and b ∈ B.
#
# |A × B| = |A| × |B|
#
# Unlike ordinary sets, order inside each ordered pair matters:
# (1, "x") != ("x", 1)

A = {1, 2, 3}
B = {"x", "y"}

cartesian_product = set(product(A, B))
print("A × B:", cartesian_product)
print("|A × B|:", len(cartesian_product))
print("|A| × |B|:", len(A) * len(B))

# A × B is usually not equal to B × A.
reverse_product = set(product(B, A))
print("A × B == B × A:", cartesian_product == reverse_product)

# A × B and B × A have the same cardinality when both sets are finite,
# even though their ordered pairs are generally different.

# Cartesian product with an empty set is empty.
print("A × ∅:", set(product(A, set())))
print("∅ × A:", set(product(set(), A)))

# Repeated Cartesian products create tuples with more components.
C = {True, False}
A_times_B_times_C = set(product(A, B, C))
print("|A × B × C|:", len(A_times_B_times_C))
print("|A| × |B| × |C|:", len(A) * len(B) * len(C))


# =============================================================================
# 12. IMPLEMENTING CARTESIAN PRODUCT WITHOUT itertools.product
# =============================================================================

section("12. MANUAL CARTESIAN PRODUCT")

def cartesian_product_manual(first: Iterable[T], second: Iterable[T]) -> set[tuple[T, T]]:
    """Construct A × B using explicit nested iteration."""
    result: set[tuple[T, T]] = set()

    for first_value in first:
        for second_value in second:
            result.add((first_value, second_value))

    return result


manual_result = cartesian_product_manual({1, 2}, {"a", "b", "c"})
builtin_result = set(product({1, 2}, {"a", "b", "c"}))

print("Manual result:", manual_result)
print("Matches itertools.product:", manual_result == builtin_result)


# =============================================================================
# 13. POWER SET
# =============================================================================

section("13. POWER SET")

# The power set P(A), or 𝒫(A), is the set of all subsets of A.
#
# If |A| = n, then:
#
# |𝒫(A)| = 2^n
#
# Because Python sets must contain hashable elements, each subset is
# represented as a frozenset.

def power_set(values: Iterable[T]) -> set[frozenset[T]]:
    """Return the complete power set of a finite iterable."""
    elements = list(values)
    result: set[frozenset[T]] = {frozenset()}

    for element in elements:
        expanded = {subset | frozenset({element}) for subset in result}
        result |= expanded

    return result


small_set = {1, 2, 3}
powers = power_set(small_set)

print("A:", small_set)
print("Power set:", powers)
print("Number of subsets:", len(powers))
print("Expected number:", 2 ** len(small_set))

# Every power set contains:
# - the empty set
# - the original set
print("Empty subset present:", frozenset() in powers)
print("Original set present:", frozenset(small_set) in powers)

# A set with n elements has C(n, k) subsets containing exactly k elements.
for k in range(len(small_set) + 1):
    count = sum(len(subset) == k for subset in powers)
    expected = comb(len(small_set), k)
    print(f"Subsets of size {k}: actual={count}, expected={expected}")


# =============================================================================
# 14. FROZENSET AND SETS OF SETS
# =============================================================================

section("14. FROZENSET: IMMUTABLE SETS")

# A normal set is mutable and therefore unhashable.
# It cannot be an element of another set.
try:
    invalid_nested_set = {{1, 2}, {3, 4}}
    print(invalid_nested_set)
except TypeError as error:
    print("A normal set cannot contain another set:", error)

# frozenset is immutable and hashable.
nested_set = {frozenset({1, 2}), frozenset({3, 4})}
print("Set containing frozensets:", nested_set)

# frozenset supports normal set operations that produce frozensets.
first = frozenset({1, 2, 3})
second = frozenset({3, 4, 5})
print("frozenset union:", first | second)
print("frozenset intersection:", first & second)


# =============================================================================
# 15. VENN-DIAGRAM REGIONS
# =============================================================================

section("15. VENN-DIAGRAM REGIONS")

# A Venn diagram represents relationships between sets visually.
# For two sets A and B, the universal region can be divided into:
#
# A only       = A - B
# B only       = B - A
# Both         = A ∩ B
# Neither      = U - (A ∪ B)

U = set(range(1, 13))
A = {1, 2, 3, 4, 5, 6}
B = {4, 5, 6, 7, 8}

regions_2 = {
    "A only": A - B,
    "B only": B - A,
    "Both": A & B,
    "Neither": U - (A | B),
}

for name, region in regions_2.items():
    print(f"{name:10s}: {sorted(region)}")

# The four regions form a partition of U:
# they are pairwise disjoint and their union is U.
all_regions = list(regions_2.values())

pairwise_disjoint = all(
    all_regions[i].isdisjoint(all_regions[j])
    for i in range(len(all_regions))
    for j in range(i + 1, len(all_regions))
)

combined_regions = set().union(*all_regions)

print("Regions pairwise disjoint:", pairwise_disjoint)
print("Regions cover U:", combined_regions == U)


# =============================================================================
# 16. SIMPLE ASCII VENN DIAGRAM
# =============================================================================

section("16. ASCII VENN-DIAGRAM VISUALIZATION")

def ascii_venn_two_sets(
    universe: set[T],
    first: set[T],
    second: set[T],
) -> None:
    """
    Print the four logical regions of a two-set Venn diagram.

    This is not a geometric drawing. It is a textual representation
    of the four mathematically meaningful regions.
    """
    print()
    print("                 ┌───────────────┐")
    print("                 │     A only    │")
    print(f"                 │ {sorted(first - second)!s:13s} │")
    print("          ┌──────┴───────┬───────┴──────┐")
    print("          │              │              │")
    print("          │    A ∩ B     │    B only    │")
    print(f"          │ {sorted(first & second)!s:12s} │ {sorted(second - first)!s:12s} │")
    print("          └──────────────┴──────────────┘")
    print()
    print("Neither:", sorted(universe - (first | second)))


ascii_venn_two_sets(
    set(range(1, 10)),
    {1, 2, 3, 4},
    {3, 4, 5, 6},
)


# =============================================================================
# 17. THREE-SET VENN REGIONS
# =============================================================================

section("17. THREE-SET VENN REGIONS")

# For three sets A, B, C, there are 2^3 = 8 possible membership regions:
#
# A only
# B only
# C only
# A∩B only
# A∩C only
# B∩C only
# A∩B∩C
# outside all three

def venn_three_regions(
    universe: set[T],
    first: set[T],
    second: set[T],
    third: set[T],
) -> dict[str, set[T]]:
    """Compute all eight membership regions for three sets."""
    return {
        "A only": first - second - third,
        "B only": second - first - third,
        "C only": third - first - second,
        "A and B only": (first & second) - third,
        "A and C only": (first & third) - second,
        "B and C only": (second & third) - first,
        "A and B and C": first & second & third,
        "Outside all": universe - (first | second | third),
    }


U = set(range(1, 16))
A = {1, 2, 3, 4, 5, 6}
B = {4, 5, 6, 7, 8, 9}
C = {2, 4, 6, 8, 10, 12}

regions_3 = venn_three_regions(U, A, B, C)

for name, region in regions_3.items():
    print(f"{name:17s}: {sorted(region)}")

print(
    "All three-set regions cover U:",
    set().union(*regions_3.values()) == U,
)


# =============================================================================
# 18. CARDINALITY OF UNION
# =============================================================================

section("18. CARDINALITY AND INCLUSION-EXCLUSION")

# Cardinality means the number of elements in a finite set.
#
# For two sets:
#
# |A ∪ B| = |A| + |B| - |A ∩ B|
#
# The intersection is subtracted because shared elements are counted twice.

A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7}

actual_union_size = len(A | B)
formula_union_size = len(A) + len(B) - len(A & B)

print("Actual |A ∪ B|:", actual_union_size)
print("Formula:", formula_union_size)

# If two sets are disjoint, the intersection is empty:
# |A ∪ B| = |A| + |B|
disjoint_A = {1, 2}
disjoint_B = {3, 4, 5}
print("Disjoint union size:", len(disjoint_A | disjoint_B))
print("Sum of sizes:", len(disjoint_A) + len(disjoint_B))


# =============================================================================
# 19. THREE-SET INCLUSION-EXCLUSION
# =============================================================================

section("19. THREE-SET INCLUSION-EXCLUSION")

# For three finite sets:
#
# |A ∪ B ∪ C|
# = |A| + |B| + |C|
#   - |A∩B| - |A∩C| - |B∩C|
#   + |A∩B∩C|

A = {1, 2, 3, 4, 5, 6}
B = {4, 5, 6, 7, 8}
C = {2, 4, 6, 8, 10}

actual = len(A | B | C)

inclusion_exclusion = (
    len(A)
    + len(B)
    + len(C)
    - len(A & B)
    - len(A & C)
    - len(B & C)
    + len(A & B & C)
)

print("Actual union cardinality:", actual)
print("Inclusion-exclusion result:", inclusion_exclusion)
print("Formula is correct:", actual == inclusion_exclusion)


# =============================================================================
# 20. SET IDENTITIES
# =============================================================================

section("20. IMPORTANT SET IDENTITIES")

# Set algebra has identities analogous to Boolean algebra.

universe = set(range(1, 11))
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

identities = {
    "Commutative union": (A | B) == (B | A),
    "Commutative intersection": (A & B) == (B & A),
    "Associative union": ((A | B) | universe) == (A | (B | universe)),
    "Associative intersection": ((A & B) & universe) == (A & (B & universe)),
    "Idempotent union": (A | A) == A,
    "Idempotent intersection": (A & A) == A,
    "Identity union": (A | set()) == A,
    "Identity intersection": (A & universe) == A,
    "Domination union": (A | universe) == universe,
    "Domination intersection": (A & set()) == set(),
    "Complement union": (A | (universe - A)) == universe,
    "Complement intersection": (A & (universe - A)) == set(),
    "Double complement": (universe - (universe - A)) == A,
    "Absorption 1": (A | (A & B)) == A,
    "Absorption 2": (A & (A | B)) == A,
}

for identity_name, result in identities.items():
    print(f"{identity_name:28s}: {result}")


# =============================================================================
# 21. DE MORGAN'S LAWS
# =============================================================================

section("21. DE MORGAN'S LAWS")

# De Morgan's laws:
#
# (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
# (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
#
# Complements are relative to the same universal set.

complement_union = universe - (A | B)
intersection_of_complements = (universe - A) & (universe - B)

complement_intersection = universe - (A & B)
union_of_complements = (universe - A) | (universe - B)

print(
    "(A ∪ B)ᶜ == Aᶜ ∩ Bᶜ:",
    complement_union == intersection_of_complements,
)
print(
    "(A ∩ B)ᶜ == Aᶜ ∪ Bᶜ:",
    complement_intersection == union_of_complements,
)


# =============================================================================
# 22. DISTRIBUTIVE LAWS
# =============================================================================

section("22. DISTRIBUTIVE LAWS")

# Set operations satisfy:
#
# A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)
# A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)

C = {2, 4, 6, 8}

left_1 = A & (B | C)
right_1 = (A & B) | (A & C)

left_2 = A | (B & C)
right_2 = (A | B) & (A | C)

print("Intersection distributes over union:", left_1 == right_1)
print("Union distributes over intersection:", left_2 == right_2)


# =============================================================================
# 23. SET DIFFERENCE IDENTITIES
# =============================================================================

section("23. DIFFERENCE IDENTITIES")

# Difference can be expressed using intersection and complement:
#
# A - B = A ∩ Bᶜ

print(
    "A - B == A ∩ Bᶜ:",
    A - B == A & (universe - B),
)

# Another useful identity:
#
# A - (B ∪ C) = (A - B) ∩ (A - C)

print(
    "A - (B ∪ C) identity:",
    A - (B | C) == (A - B) & (A - C),
)

# And:
#
# A - (B ∩ C) = (A - B) ∪ (A - C)

print(
    "A - (B ∩ C) identity:",
    A - (B & C) == (A - B) | (A - C),
)


# =============================================================================
# 24. SET PARTITIONS
# =============================================================================

section("24. PARTITIONS")

# A partition of a set U is a collection of nonempty subsets that:
# 1. are pairwise disjoint
# 2. have union equal to U

U = set(range(1, 11))

partition = [
    {1, 2, 3},
    {4, 5},
    {6, 7, 8, 9, 10},
]

def is_partition(universe: set[T], blocks: list[set[T]]) -> bool:
    """Check whether blocks form a partition of the universe."""
    if any(not block for block in blocks):
        return False

    for index, first in enumerate(blocks):
        for second in blocks[index + 1:]:
            if not first.isdisjoint(second):
                return False

    return set().union(*blocks) == universe


print("Is valid partition:", is_partition(U, partition))

invalid_partition = [
    {1, 2, 3},
    {3, 4, 5},  # overlaps at 3
    {6, 7, 8, 9, 10},
]
print("Is invalid partition:", is_partition(U, invalid_partition))


# =============================================================================
# 25. SET OPERATIONS ON REAL-WORLD DATA
# =============================================================================

section("25. PRACTICAL APPLICATION: USER GROUPS")

# Sets are especially useful for membership and overlap analysis.

website_visitors = {
    "Asha",
    "Bharat",
    "Chen",
    "Deepa",
    "Evan",
}

newsletter_subscribers = {
    "Bharat",
    "Deepa",
    "Fatima",
    "Gopal",
}

premium_customers = {
    "Asha",
    "Deepa",
    "Gopal",
}

print("Visitors who subscribed:", website_visitors & newsletter_subscribers)
print("Visitors who did not subscribe:", website_visitors - newsletter_subscribers)
print("Subscribers who did not visit:", newsletter_subscribers - website_visitors)
print("People in either group:", website_visitors | newsletter_subscribers)
print("Exactly one of the two groups:", website_visitors ^ newsletter_subscribers)

# Users who are visitors, subscribers, and premium customers:
print(
    "Visitors who are also subscribers and premium:",
    website_visitors & newsletter_subscribers & premium_customers,
)


# =============================================================================
# 26. PRACTICAL APPLICATION: COURSE ENROLLMENT
# =============================================================================

section("26. PRACTICAL APPLICATION: COURSE ENROLLMENT")

python_students = {"Anil", "Beena", "Chetan", "Divya", "Esha"}
sql_students = {"Beena", "Divya", "Farhan", "Gita"}
statistics_students = {"Chetan", "Divya", "Gita", "Hari"}

print("Students taking Python:", len(python_students))
print("Students taking SQL:", len(sql_students))
print("Students taking both:", python_students & sql_students)
print("Students taking all three:", python_students & sql_students & statistics_students)

all_students = python_students | sql_students | statistics_students
print("Students taking at least one course:", len(all_students))

python_only = python_students - sql_students - statistics_students
print("Python only:", python_only)

exactly_one_course = (
    (python_students - sql_students - statistics_students)
    | (sql_students - python_students - statistics_students)
    | (statistics_students - python_students - sql_students)
)

print("Exactly one course:", exactly_one_course)


# =============================================================================
# 27. PRACTICAL APPLICATION: PERMISSIONS
# =============================================================================

section("27. PRACTICAL APPLICATION: PERMISSIONS")

required_permissions = {"read", "write"}
user_permissions = {"read", "write", "export"}

# issubset tells us whether the user has every required permission.
authorized = required_permissions <= user_permissions
print("Authorized:", authorized)

missing_permissions = required_permissions - user_permissions
extra_permissions = user_permissions - required_permissions

print("Missing permissions:", missing_permissions)
print("Extra permissions:", extra_permissions)

# For an administrator:
administrator_permissions = {"read", "write", "delete", "export", "audit"}
print(
    "Administrator has all user permissions:",
    user_permissions <= administrator_permissions,
)


# =============================================================================
# 28. PRACTICAL APPLICATION: DATA DEDUPLICATION
# =============================================================================

section("28. PRACTICAL APPLICATION: DEDUPLICATION")

# A set removes duplicates automatically.
emails = [
    "a@example.com",
    "b@example.com",
    "a@example.com",
    "c@example.com",
    "b@example.com",
]

unique_emails = set(emails)

print("Original records:", emails)
print("Unique emails:", unique_emails)

# Important limitation:
# converting to a set does not preserve the original ordering semantics.
# If ordered deduplication is needed, dict.fromkeys() is often appropriate.
ordered_unique_emails = list(dict.fromkeys(emails))
print("Order-preserving unique emails:", ordered_unique_emails)


# =============================================================================
# 29. PRACTICAL APPLICATION: TAG MATCHING
# =============================================================================

section("29. PRACTICAL APPLICATION: TAG MATCHING")

article_tags = {"python", "sets", "algorithms", "data"}
required_tags = {"python", "data"}

print("Contains all required tags:", required_tags <= article_tags)
print("Shared tags:", article_tags & required_tags)
print("Missing required tags:", required_tags - article_tags)


# =============================================================================
# 30. SET COMPREHENSIONS
# =============================================================================

section("30. SET COMPREHENSIONS")

# A set comprehension creates a set using an expression and optional condition.

squares = {number ** 2 for number in range(1, 11)}
print("Squares:", squares)

even_squares = {
    number ** 2
    for number in range(1, 11)
    if number % 2 == 0
}
print("Squares of even numbers:", even_squares)

# Duplicates collapse automatically.
remainders = {number % 3 for number in range(20)}
print("Possible remainders modulo 3:", remainders)

# A set comprehension can implement filtering.
positive_values = {-3, -2, -1, 0, 1, 2, 3}
positive_values = {value for value in positive_values if value > 0}
print("Positive values:", positive_values)


# =============================================================================
# 31. SET METHODS
# =============================================================================

section("31. IMPORTANT SET METHODS")

sample = {1, 2, 3}

print("copy():", sample.copy())
print("union():", sample.union({3, 4}))
print("intersection():", sample.intersection({2, 3, 4}))
print("difference():", sample.difference({2}))
print("symmetric_difference():", sample.symmetric_difference({3, 4}))

print("issubset():", {1, 2}.issubset(sample))
print("issuperset():", sample.issuperset({1, 2}))
print("isdisjoint():", sample.isdisjoint({10, 11}))

# update methods mutate the set:
mutating = {1, 2, 3}
mutating.update({3, 4})
print("update():", mutating)

mutating = {1, 2, 3}
mutating.intersection_update({2, 3, 4})
print("intersection_update():", mutating)

mutating = {1, 2, 3}
mutating.difference_update({2})
print("difference_update():", mutating)

mutating = {1, 2, 3}
mutating.symmetric_difference_update({3, 4})
print("symmetric_difference_update():", mutating)


# =============================================================================
# 32. OPERATOR VERSUS METHOD
# =============================================================================

section("32. OPERATORS VERSUS METHODS")

# Operators provide concise notation:
print("{1,2} | {2,3}:", {1, 2} | {2, 3})
print("{1,2} & {2,3}:", {1, 2} & {2, 3})
print("{1,2} - {2,3}:", {1, 2} - {2, 3})
print("{1,2} ^ {2,3}:", {1, 2} ^ {2, 3})

# Methods express the same operations:
print("{1,2}.union({2,3}):", {1, 2}.union({2, 3}))
print("{1,2}.intersection({2,3}):", {1, 2}.intersection({2, 3}))
print("{1,2}.difference({2,3}):", {1, 2}.difference({2, 3}))
print(
    "{1,2}.symmetric_difference({2,3}):",
    {1, 2}.symmetric_difference({2, 3}),
)

# Operator operands generally need to be set-like types.
# Methods can accept broader iterable arguments in many cases.
print("{1,2}.intersection([2,3]):", {1, 2}.intersection([2, 3]))

try:
    print({1, 2} & [2, 3])
except TypeError as error:
    print("Operator with list:", error)


# =============================================================================
# 33. MUTABILITY AND ALIASING
# =============================================================================

section("33. MUTABILITY, COPY, AND ALIASING")

original = {1, 2, 3}
alias = original

# Both variables refer to the same set.
alias.add(4)
print("Original after alias mutation:", original)

# copy() creates an independent shallow copy.
original = {1, 2, 3}
independent_copy = original.copy()
independent_copy.add(4)

print("Original after copy mutation:", original)
print("Copy:", independent_copy)


# =============================================================================
# 34. SETS WITH DIFFERENT DATA TYPES
# =============================================================================

section("34. HASHABLE ELEMENTS")

# Set elements must be hashable.
valid = {
    1,
    "text",
    (1, 2),
    frozenset({3, 4}),
}
print("Valid heterogeneous set:", valid)

try:
    invalid = {[1, 2], [3, 4]}
    print(invalid)
except TypeError as error:
    print("Lists cannot be set elements:", error)

# Tuples are hashable only when all of their elements are hashable.
valid_tuple = {(1, 2), (3, 4)}
print("Set of tuples:", valid_tuple)

try:
    invalid_tuple = {(1, [2, 3])}
    print(invalid_tuple)
except TypeError as error:
    print("Tuple containing a list is not hashable:", error)


# =============================================================================
# 35. BOOLEAN VALUES AND NUMERIC EQUALITY
# =============================================================================

section("35. BOOLEAN AND NUMERIC EDGE CASE")

# In Python, True == 1 and False == 0.
# Sets use hashing and equality, so these values can collide as set elements.

special = {True, 1, False, 0}
print("{True, 1, False, 0}:", special)
print("Length:", len(special))

# This is mathematically surprising if you are thinking of True and 1
# as completely unrelated objects. Python deliberately treats them as equal
# for numeric equality and hashing purposes.


# =============================================================================
# 36. NAN EDGE CASE
# =============================================================================

section("36. FLOATING-POINT NaN EDGE CASE")

# NaN is unusual because NaN != NaN.
# Set behavior involving NaN therefore deserves care.

nan_value = float("nan")
nan_set = {nan_value}

print("nan_value in nan_set:", nan_value in nan_set)
print("nan_value == nan_value:", nan_value == nan_value)

# Creating a second NaN object can produce different membership behavior.
another_nan = float("nan")
print("another_nan == nan_value:", another_nan == nan_value)
print("another_nan in nan_set:", another_nan in nan_set)


# =============================================================================
# 37. EMPTY SET EDGE CASES
# =============================================================================

section("37. EMPTY SET")

empty = set()
nonempty = {1, 2, 3}

print("∅ ∪ A:", empty | nonempty)
print("∅ ∩ A:", empty & nonempty)
print("A - ∅:", nonempty - empty)
print("∅ - A:", empty - nonempty)
print("∅ ⊆ A:", empty <= nonempty)
print("A × ∅:", set(product(nonempty, empty)))

# Cardinality:
print("|∅|:", len(empty))

# The power set of the empty set contains exactly one subset:
print("P(∅):", power_set(empty))


# =============================================================================
# 38. MULTI-SET WARNING
# =============================================================================

section("38. SETS DO NOT REPRESENT MULTISETS")

# A mathematical set records whether an element is present, not how many
# times it occurs.
data = ["A", "A", "B", "B", "B"]

print("Data:", data)
print("Set representation:", set(data))

# If frequency matters, use collections.Counter instead of set.
from collections import Counter

frequencies = Counter(data)
print("Frequency representation:", frequencies)


# =============================================================================
# 39. ORDERED DATA VERSUS SET DATA
# =============================================================================

section("39. WHEN NOT TO USE A SET")

ordered_values = [5, 2, 9, 1, 5]
value_set = set(ordered_values)

print("List preserves sequence:", ordered_values)
print("Set emphasizes membership:", value_set)

# Use a list when:
# - duplicates matter
# - position matters
# - stable sequence is fundamental
#
# Use a set when:
# - uniqueness matters
# - membership matters
# - intersection/union/difference matter

# If deterministic display is needed, sort the set:
print("Sorted set:", sorted(value_set))


# =============================================================================
# 40. FROZENSET AS A DICTIONARY KEY
# =============================================================================

section("40. FROZENSET AS A DICTIONARY KEY")

# A frozenset can be used as a dictionary key because it is hashable.
course_pair_scores = {
    frozenset({"Python", "SQL"}): 92,
    frozenset({"Python", "Statistics"}): 88,
}

lookup_key = frozenset({"SQL", "Python"})
print("Order-independent lookup:", course_pair_scores[lookup_key])


# =============================================================================
# 41. BITMASK REPRESENTATION OF FINITE SETS
# =============================================================================

section("41. ADVANCED: BITMASK SET REPRESENTATION")

# A finite set whose universe is {0, 1, ..., n-1} can be represented
# by an integer. Bit i is 1 exactly when element i belongs to the set.
#
# Example:
# {0, 2, 3} -> binary 1101 -> decimal 13

def set_to_bitmask(values: Iterable[int], universe_size: int) -> int:
    """Encode elements from 0..universe_size-1 as bits."""
    mask = 0

    for value in values:
        if not 0 <= value < universe_size:
            raise ValueError(
                f"Element {value} is outside universe 0..{universe_size - 1}"
            )
        mask |= 1 << value

    return mask


def bitmask_to_set(mask: int, universe_size: int) -> set[int]:
    """Decode a bitmask into its represented finite set."""
    if mask < 0:
        raise ValueError("Mask must be non-negative")

    return {
        index
        for index in range(universe_size)
        if mask & (1 << index)
    }


universe_size = 8
bitmask_A = set_to_bitmask({0, 2, 3}, universe_size)
bitmask_B = set_to_bitmask({2, 4, 5}, universe_size)

print("A bitmask:", bin(bitmask_A))
print("B bitmask:", bin(bitmask_B))

# Bitwise OR corresponds to union.
union_mask = bitmask_A | bitmask_B

# Bitwise AND corresponds to intersection.
intersection_mask = bitmask_A & bitmask_B

# AND with the complement mask corresponds to difference.
universe_mask = (1 << universe_size) - 1
difference_mask = bitmask_A & ~bitmask_B & universe_mask

# XOR corresponds to symmetric difference.
symmetric_mask = bitmask_A ^ bitmask_B

print("Union:", bitmask_to_set(union_mask, universe_size))
print("Intersection:", bitmask_to_set(intersection_mask, universe_size))
print("Difference A-B:", bitmask_to_set(difference_mask, universe_size))
print("Symmetric difference:", bitmask_to_set(symmetric_mask, universe_size))


# =============================================================================
# 42. BITMASK COMPLEMENT
# =============================================================================

section("42. BITMASK COMPLEMENT")

# Python's ~ operator flips all integer bits, conceptually including
# infinitely many leading bits. Therefore a finite universe mask must be
# applied to restrict the result to the intended universe.

A_mask = set_to_bitmask({1, 3, 5}, 8)
universe_mask = (1 << 8) - 1

complement_mask = (~A_mask) & universe_mask

print("A:", bitmask_to_set(A_mask, 8))
print("Complement:", bitmask_to_set(complement_mask, 8))


# =============================================================================
# 43. BITMASK CARDINALITY
# =============================================================================

section("43. BITMASK CARDINALITY")

# Python's int.bit_count() counts the number of set bits.
mask = set_to_bitmask({0, 2, 4, 7}, 8)

print("Set:", bitmask_to_set(mask, 8))
print("Cardinality from bit count:", mask.bit_count())


# =============================================================================
# 44. ENUMERATING ALL SUBSETS WITH BITMASKS
# =============================================================================

section("44. ENUMERATING SUBSETS USING BITMASKS")

def subsets_using_bitmasks(values: list[T]) -> list[set[T]]:
    """Generate every subset of a list using binary masks."""
    n = len(values)
    subsets: list[set[T]] = []

    for mask in range(1 << n):
        subset = {
            values[index]
            for index in range(n)
            if mask & (1 << index)
        }
        subsets.append(subset)

    return subsets


bitmask_subsets = subsets_using_bitmasks(["A", "B", "C"])

for subset in bitmask_subsets:
    print(subset)

print("Number of subsets:", len(bitmask_subsets))


# =============================================================================
# 45. VENN REGION CLASSIFICATION BY MEMBERSHIP SIGNATURE
# =============================================================================

section("45. ADVANCED: GENERAL MEMBERSHIP SIGNATURES")

# For n sets, each element belongs to one of 2^n membership patterns.
# A Boolean signature such as (True, False, True) means:
# element is in A, not in B, and in C.

def membership_signature(
    value: T,
    named_sets: list[set[T]],
) -> tuple[bool, ...]:
    """Return membership bits for a value across several sets."""
    return tuple(value in current_set for current_set in named_sets)


A = {1, 2, 3, 4}
B = {3, 4, 5}
C = {2, 4, 6}
U = set(range(1, 8))

for value in sorted(U):
    print(value, membership_signature(value, [A, B, C]))

# Group elements into their Venn regions.
def classify_by_signature(
    universe: set[T],
    named_sets: list[set[T]],
) -> dict[tuple[bool, ...], set[T]]:
    """Group universe elements by their membership signature."""
    regions: dict[tuple[bool, ...], set[T]] = {}

    for value in universe:
        signature = membership_signature(value, named_sets)
        regions.setdefault(signature, set()).add(value)

    return regions


classified = classify_by_signature(U, [A, B, C])

for signature, values in sorted(classified.items()):
    print(f"{signature}: {sorted(values)}")


# =============================================================================
# 46. GENERAL SET EXPRESSION EVALUATION
# =============================================================================

section("46. GENERAL SET EXPRESSIONS")

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}
C = {4, 6, 7, 8}
U = set(range(1, 10))

# Parentheses are important because set expressions combine operations.
expression_1 = (A | B) & C
expression_2 = A | (B & C)
expression_3 = (A - B) | (C - A)
expression_4 = U - ((A | B) & C)

print("(A ∪ B) ∩ C:", expression_1)
print("A ∪ (B ∩ C):", expression_2)
print("(A - B) ∪ (C - A):", expression_3)
print("U - ((A ∪ B) ∩ C):", expression_4)


# =============================================================================
# 47. SET EXPRESSIONS AND OPERATOR PRECEDENCE
# =============================================================================

section("47. OPERATOR PRECEDENCE AND READABILITY")

# Complex set expressions can become difficult to read.
# Parentheses are recommended even when Python's precedence would produce
# the intended result.

A = {1, 2, 3}
B = {3, 4}
C = {3, 5}

readable = (A | B) & C
print("Readable expression:", readable)

# Prefer explicit parentheses in production code when the logical grouping
# is important to the reader.


# =============================================================================
# 48. VALIDATING SET IDENTITIES PROGRAMMATICALLY
# =============================================================================

section("48. PROGRAMMATICALLY TESTING SET IDENTITIES")

def verify_de_morgan(
    universe: set[T],
    first: set[T],
    second: set[T],
) -> tuple[bool, bool]:
    """Verify both De Morgan laws."""
    first_law = (
        universe - (first | second)
        == (universe - first) & (universe - second)
    )

    second_law = (
        universe - (first & second)
        == (universe - first) | (universe - second)
    )

    return first_law, second_law


test_universe = set(range(20))
test_A = {0, 2, 4, 6, 8, 10}
test_B = {5, 6, 7, 8, 9, 10}

law_1, law_2 = verify_de_morgan(test_universe, test_A, test_B)

print("First De Morgan law:", law_1)
print("Second De Morgan law:", law_2)


# =============================================================================
# 49. RANDOMIZED IDENTITY TESTING
# =============================================================================

section("49. RANDOMIZED SET-IDENTITY TESTING")

import random

random.seed(42)

for trial in range(10):
    random_A = {
        number
        for number in range(20)
        if random.random() < 0.4
    }

    random_B = {
        number
        for number in range(20)
        if random.random() < 0.4
    }

    random_C = {
        number
        for number in range(20)
        if random.random() < 0.4
    }

    assert (random_A | random_B) == (random_B | random_A)
    assert (random_A & random_B) == (random_B & random_A)
    assert random_A | (random_B & random_C) == (
        (random_A | random_B) & (random_A | random_C)
    )
    assert random_A - random_B == random_A & (set(range(20)) - random_B)

print("10 randomized identity trials passed.")


# =============================================================================
# 50. COMMON MISTAKES
# =============================================================================

section("50. COMMON MISTAKES")

# Mistake 1: using {} for an empty set.
print("{} creates a:", type({}).__name__)
print("set() creates a:", type(set()).__name__)

# Mistake 2: expecting duplicates to survive.
print("Duplicates disappear:", {1, 1, 1, 2, 2})

# Mistake 3: assuming order is meaningful.
unordered = {"a", "b", "c"}
print("Use sorted() for deterministic presentation:", sorted(unordered))

# Mistake 4: confusing difference with symmetric difference.
A = {1, 2, 3}
B = {3, 4}
print("A - B:", A - B)
print("A ^ B:", A ^ B)

# Mistake 5: forgetting the universal set for complements.
U = {1, 2, 3, 4, 5}
A = {1, 2}
print("Complement relative to U:", U - A)


# =============================================================================
# 51. COMMON ERROR: UNHASHABLE ELEMENTS
# =============================================================================

section("51. ERROR HANDLING: UNHASHABLE ELEMENTS")

try:
    bad_set = {[1, 2], [3, 4]}
except TypeError as error:
    print("Expected error:", error)

try:
    bad_set = {{"name": "Alice"}}
except TypeError as error:
    print("Expected error:", error)


# =============================================================================
# 52. COMMON ERROR: MUTATING WHILE ITERATING
# =============================================================================

section("52. MUTATION DURING ITERATION")

# Modifying a set while iterating over it is unsafe and raises RuntimeError.
values = {1, 2, 3, 4, 5}

try:
    for value in values:
        if value % 2 == 0:
            values.remove(value)
except RuntimeError as error:
    print("Expected mutation error:", error)

# Safe approach: iterate over a copy or construct a new set.
values = {1, 2, 3, 4, 5}
values = {value for value in values if value % 2 != 0}
print("Safely filtered:", values)


# =============================================================================
# 53. SET ALGEBRA FUNCTION LIBRARY
# =============================================================================

section("53. REUSABLE SET-OPERATION FUNCTIONS")

def set_union(*sets: set[T]) -> set[T]:
    """Return the union of zero or more sets."""
    result: set[T] = set()

    for current_set in sets:
        result |= current_set

    return result


def set_intersection(*sets: set[T]) -> set[T]:
    """Return the intersection of zero or more sets.

    For zero arguments, the mathematical result depends on the chosen
    universe and therefore is not defined by this function.
    """
    if not sets:
        raise ValueError("At least one set is required")

    result = sets[0].copy()

    for current_set in sets[1:]:
        result &= current_set

    return result


def set_difference(first: set[T], *others: set[T]) -> set[T]:
    """Return elements of first that occur in none of the other sets."""
    result = first.copy()

    for current_set in others:
        result -= current_set

    return result


print("Function union:", set_union({1, 2}, {2, 3}, {3, 4}))
print("Function intersection:", set_intersection({1, 2, 3}, {2, 3}, {3, 4}))
print("Function difference:", set_difference({1, 2, 3}, {2}, {3}))


# =============================================================================
# 54. SET-BASED RELATIONAL ANALYSIS
# =============================================================================

section("54. RELATION ANALYSIS WITH SETS")

# A binary relation from A to B can be represented as a subset of A × B.
A = {"Alice", "Bob"}
B = {"Math", "Physics"}

relation = {
    ("Alice", "Math"),
    ("Bob", "Physics"),
}

full_product = set(product(A, B))

print("A × B:", full_product)
print("Relation R:", relation)
print("R ⊆ A × B:", relation <= full_product)

# Domain and range can be extracted with set comprehensions.
domain = {left for left, right in relation}
range_values = {right for left, right in relation}

print("Domain:", domain)
print("Range:", range_values)


# =============================================================================
# 55. RELATIONAL COMPOSITION
# =============================================================================

section("55. ADVANCED: RELATION COMPOSITION")

# Given:
# R ⊆ A × B
# S ⊆ B × C
#
# Composition S ∘ R consists of (a, c) whenever there exists b such that
# (a, b) ∈ R and (b, c) ∈ S.

R = {
    ("Alice", "Math"),
    ("Bob", "Physics"),
}

S = {
    ("Math", "Professor"),
    ("Physics", "Laboratory"),
}

composition = {
    (person, destination)
    for person, intermediate_1 in R
    for intermediate_2, destination in S
    if intermediate_1 == intermediate_2
}

print("R:", R)
print("S:", S)
print("S ∘ R:", composition)


# =============================================================================
# 56. SET COVERING CONCEPT
# =============================================================================

section("56. ADVANCED APPLICATION: SET COVERING")

# Set cover asks for a collection of subsets whose union covers a target universe.
# Finding a minimum set cover is computationally difficult in general.
# A greedy heuristic repeatedly selects the set covering the largest number
# of currently uncovered elements.

def greedy_set_cover(
    universe: set[T],
    candidates: list[set[T]],
) -> list[set[T]]:
    """
    Greedy approximation for the set-cover problem.

    At every step, choose the candidate that covers the most currently
    uncovered elements.
    """
    uncovered = universe.copy()
    selected: list[set[T]] = []

    while uncovered:
        best_candidate = max(
            candidates,
            key=lambda candidate: len(candidate & uncovered),
            default=set(),
        )

        newly_covered = best_candidate & uncovered

        if not newly_covered:
            raise ValueError("The candidates do not cover the entire universe")

        selected.append(best_candidate)
        uncovered -= best_candidate

    return selected


cover_universe = set(range(1, 11))
cover_candidates = [
    {1, 2, 3, 4},
    {3, 4, 5, 6},
    {6, 7, 8},
    {8, 9},
    {9, 10},
]

selected_cover = greedy_set_cover(cover_universe, cover_candidates)

print("Selected sets:", selected_cover)
print("Covered universe:", set().union(*selected_cover))
print("Complete cover:", set().union(*selected_cover) == cover_universe)


# =============================================================================
# 57. PERFORMANCE CONSIDERATIONS
# =============================================================================

section("57. PERFORMANCE CONSIDERATIONS")

# Python sets are implemented using hash tables.
#
# Average-case complexity:
#
# Membership: x in S       -> O(1)
# Add:        S.add(x)     -> O(1)
# Remove:     S.remove(x)  -> O(1)
# Union:                    -> O(len(A) + len(B)) approximately
# Intersection:            -> proportional to the smaller/iterated side
# Difference:              -> proportional to the first/iterated side
#
# These are average-case expectations, not absolute guarantees.

# Membership demonstration:
large_set = set(range(1_000_000))
print("Fast membership test:", 999_999 in large_set)

# A list performs linear membership search in the average case:
large_list = list(range(1_000_000))
print("List membership also works:", 999_999 in large_list)

# The important conceptual distinction is:
# set membership is designed for fast lookup;
# list membership is designed around sequential storage and order.


# =============================================================================
# 58. INTERSECTION PERFORMANCE STRATEGY
# =============================================================================

section("58. INTERSECTION PERFORMANCE STRATEGY")

# When manually intersecting sets, starting from the smallest set can reduce
# the amount of work needed in some algorithms.

sets_to_intersect = [
    set(range(0, 1000)),
    set(range(0, 100)),
    set(range(0, 10)),
]

smallest_first = min(sets_to_intersect, key=len)

result = smallest_first.copy()
for current_set in sets_to_intersect:
    result &= current_set

print("Smallest input size:", len(smallest_first))
print("Intersection size:", len(result))


# =============================================================================
# 59. SECURITY AND ROBUSTNESS CONSIDERATIONS
# =============================================================================

section("59. SECURITY AND ROBUSTNESS")

# Set operations themselves are safe data-structure operations, but inputs
# can still create operational risks.
#
# 1. Extremely large sets consume memory.
# 2. Untrusted input should be validated before expensive set construction.
# 3. Hash-based structures depend on hashing behavior.
# 4. Do not treat set ordering as a security or protocol guarantee.
# 5. Never use set order to determine authentication, authorization,
#    cryptographic material, or reproducible protocol output.

# Example of validation:
def validate_integer_universe(values: Iterable[object], maximum: int) -> set[int]:
    """Validate that all values are integers in a bounded range."""
    result: set[int] = set()

    for value in values:
        if not isinstance(value, int):
            raise TypeError("Every element must be an integer")

        if not 0 <= value <= maximum:
            raise ValueError(f"Element must be between 0 and {maximum}")

        result.add(value)

    return result


print(
    "Validated set:",
    validate_integer_universe([1, 2, 2, 3], 10),
)

try:
    validate_integer_universe([1, 20], 10)
except ValueError as error:
    print("Validation rejected input:", error)


# =============================================================================
# 60. DETERMINISTIC OUTPUT
# =============================================================================

section("60. DETERMINISTIC OUTPUT")

# Set iteration order should not be treated as a mathematical ordering.
# When output must be deterministic, sort elements when they are mutually
# comparable.

result = {"delta", "alpha", "charlie", "bravo"}
print("Deterministic representation:", sorted(result))

# For heterogeneous values that cannot be directly sorted, use a key:
mixed = {1, "2", 3}
try:
    print(sorted(mixed))
except TypeError as error:
    print("Mixed values cannot always be directly sorted:", error)

print(
    "Sort heterogeneous values using a key:",
    sorted(mixed, key=str),
)


# =============================================================================
# 61. TESTING SET FUNCTIONS
# =============================================================================

section("61. UNIT-STYLE TESTING")

def test_set_operations() -> None:
    """Verify fundamental set-operation behavior."""
    A = {1, 2, 3}
    B = {3, 4}

    assert A | B == {1, 2, 3, 4}
    assert A & B == {3}
    assert A - B == {1, 2}
    assert B - A == {4}
    assert A ^ B == {1, 2, 4}
    assert A <= A
    assert {1, 2} < A
    assert set().isdisjoint(A)

    universe = {1, 2, 3, 4, 5}
    assert universe - A == {4, 5}

    assert (A | B) == (B | A)
    assert (A & B) == (B & A)

    assert universe - (A | B) == (
        (universe - A) & (universe - B)
    )

    assert universe - (A & B) == (
        (universe - A) | (universe - B)
    )


test_set_operations()
print("Fundamental set-operation tests passed.")


# =============================================================================
# 62. PROPERTY-BASED STYLE TESTING
# =============================================================================

section("62. PROPERTY-BASED STYLE TESTING")

def test_set_properties(number_of_trials: int = 100) -> None:
    """Check general algebraic properties across random finite sets."""
    random.seed(12345)
    universe = set(range(30))

    for _ in range(number_of_trials):
        A = {x for x in universe if random.random() < 0.3}
        B = {x for x in universe if random.random() < 0.3}
        C = {x for x in universe if random.random() < 0.3}

        assert A | B == B | A
        assert A & B == B & A

        assert (A | B) | C == A | (B | C)
        assert (A & B) & C == A & (B & C)

        assert A | A == A
        assert A & A == A

        assert A | set() == A
        assert A & universe == A

        assert A - B == A & (universe - B)
        assert A ^ B == (A - B) | (B - A)

        assert universe - (A | B) == (
            (universe - A) & (universe - B)
        )

        assert universe - (A & B) == (
            (universe - A) | (universe - B)
        )

        assert A & (B | C) == (A & B) | (A & C)
        assert A | (B & C) == (A | B) & (A | C)

        assert len(A | B) == len(A) + len(B) - len(A & B)

    print(f"{number_of_trials} randomized property tests passed.")


test_set_properties()


# =============================================================================
# 63. EDGE CASE TEST SUITE
# =============================================================================

section("63. EDGE CASE TEST SUITE")

def test_edge_cases() -> None:
    """Test empty, singleton, equal, and disjoint sets."""
    empty = set()
    singleton = {1}
    equal_a = {1, 2, 3}
    equal_b = {3, 2, 1}
    disjoint_a = {1, 2}
    disjoint_b = {3, 4}

    assert empty | singleton == singleton
    assert empty & singleton == empty
    assert singleton - singleton == empty

    assert equal_a == equal_b
    assert equal_a <= equal_b
    assert not equal_a < equal_b

    assert disjoint_a.isdisjoint(disjoint_b)
    assert disjoint_a & disjoint_b == empty

    assert len(power_set(empty)) == 1
    assert len(power_set(singleton)) == 2

    assert set(product(empty, singleton)) == empty
    assert set(product(singleton, empty)) == empty


test_edge_cases()
print("Edge-case tests passed.")


# =============================================================================
# 64. COMPARISON: LIST, TUPLE, SET, FROZENSET, DICTIONARY
# =============================================================================

section("64. DATA-STRUCTURE COMPARISON")

comparison = {
    "list": {
        "ordered": True,
        "duplicates": True,
        "mutable": True,
        "hashable": False,
        "primary_use": "sequence",
    },
    "tuple": {
        "ordered": True,
        "duplicates": True,
        "mutable": False,
        "hashable": "depends on elements",
        "primary_use": "immutable sequence",
    },
    "set": {
        "ordered": False,
        "duplicates": False,
        "mutable": True,
        "hashable": False,
        "primary_use": "unique membership",
    },
    "frozenset": {
        "ordered": False,
        "duplicates": False,
        "mutable": False,
        "hashable": True,
        "primary_use": "immutable set",
    },
    "dict": {
        "ordered": True,
        "duplicates": "keys are unique",
        "mutable": True,
        "hashable": False,
        "primary_use": "key-value mapping",
    },
}

for data_structure, properties in comparison.items():
    print(f"\n{data_structure}:")
    for property_name, value in properties.items():
        print(f"  {property_name}: {value}")


# =============================================================================
# 65. MATHEMATICAL CARDINALITY CHECKS
# =============================================================================

section("65. CARDINALITY CHECKS")

def verify_two_set_cardinality(
    first: set[T],
    second: set[T],
) -> bool:
    """Verify the two-set inclusion-exclusion formula."""
    return len(first | second) == (
        len(first) + len(second) - len(first & second)
    )


def verify_cartesian_cardinality(
    first: set[T],
    second: set[T],
) -> bool:
    """Verify |A × B| = |A||B|."""
    return len(set(product(first, second))) == len(first) * len(second)


def verify_power_set_cardinality(values: set[T]) -> bool:
    """Verify |P(A)| = 2^|A|."""
    return len(power_set(values)) == 2 ** len(values)


A = {1, 2, 3}
B = {2, 3, 4, 5}

print("Two-set cardinality formula:", verify_two_set_cardinality(A, B))
print("Cartesian cardinality:", verify_cartesian_cardinality(A, B))
print("Power-set cardinality:", verify_power_set_cardinality(A))


# =============================================================================
# 66. GENERALIZED CARTESIAN PRODUCT
# =============================================================================

section("66. GENERALIZED CARTESIAN PRODUCT")

def generalized_cartesian_product(
    collections: list[Iterable[T]],
) -> set[tuple[T, ...]]:
    """
    Return the Cartesian product of an arbitrary number of finite collections.
    """
    return set(product(*collections))


general_product = generalized_cartesian_product([
    {1, 2},
    {"A", "B"},
    {True, False},
])

print("Number of tuples:", len(general_product))
print("Expected:", 2 * 2 * 2)
print("Tuples:", general_product)


# =============================================================================
# 67. SET RELATIONSHIPS IN DATABASE-STYLE ANALYSIS
# =============================================================================

section("67. DATABASE-STYLE SET OPERATIONS")

# Many relational-data concepts correspond naturally to set operations.
customers_2025 = {"C1", "C2", "C3", "C4"}
customers_2026 = {"C3", "C4", "C5", "C6"}

returning_customers = customers_2025 & customers_2026
new_customers = customers_2026 - customers_2025
lost_customers = customers_2025 - customers_2026
all_customers = customers_2025 | customers_2026

print("Returning customers:", returning_customers)
print("New customers:", new_customers)
print("Lost customers:", lost_customers)
print("All known customers:", all_customers)


# =============================================================================
# 68. SET-BASED FILTERING
# =============================================================================

section("68. SET-BASED FILTERING")

allowed_statuses = {"active", "pending"}
records = [
    {"id": 1, "status": "active"},
    {"id": 2, "status": "disabled"},
    {"id": 3, "status": "pending"},
    {"id": 4, "status": "active"},
]

valid_records = [
    record
    for record in records
    if record["status"] in allowed_statuses
]

print("Records with allowed statuses:", valid_records)


# =============================================================================
# 69. ADVANCED: MINIMUM HITTING SET CONCEPT
# =============================================================================

section("69. ADVANCED: HITTING-SET VERIFICATION")

# A hitting set H intersects every set in a family.
# This is a useful concept in optimization, testing, coverage, and diagnosis.

family = [
    {"A", "B"},
    {"B", "C"},
    {"C", "D"},
]

candidate = {"B", "D"}

hits_every_set = all(bool(candidate & current) for current in family)

print("Candidate:", candidate)
print("Hits every family member:", hits_every_set)

# This is only verification. Finding a minimum hitting set is an optimization
# problem and is generally computationally difficult.


# =============================================================================
# 70. ADVANCED: SET PARTITION BY FUNCTION
# =============================================================================

section("70. PARTITIONING A DATASET WITH SET COMPREHENSIONS")

numbers = set(range(1, 21))

evens = {x for x in numbers if x % 2 == 0}
odds = {x for x in numbers if x % 2 != 0}

print("Evens:", evens)
print("Odds:", odds)
print("Disjoint:", evens.isdisjoint(odds))
print("Cover all:", evens | odds == numbers)


# =============================================================================
# 71. ADVANCED: EQUIVALENCE-CLASS STYLE GROUPING
# =============================================================================

section("71. EQUIVALENCE-CLASS STYLE GROUPING")

# Partition integers by their remainder modulo 3.
classes = {
    remainder: {
        value
        for value in range(15)
        if value % 3 == remainder
    }
    for remainder in range(3)
}

for remainder, values in classes.items():
    print(f"Remainder {remainder}:", values)

class_sets = list(classes.values())

print(
    "Classes are pairwise disjoint:",
    all(
        class_sets[i].isdisjoint(class_sets[j])
        for i in range(len(class_sets))
        for j in range(i + 1, len(class_sets))
    ),
)

print(
    "Classes cover universe:",
    set().union(*class_sets) == set(range(15)),
)


# =============================================================================
# 72. SET OPERATION REFERENCE DEMONSTRATION
# =============================================================================

section("72. QUICK REFERENCE")

reference_A = {1, 2, 3}
reference_B = {3, 4, 5}
reference_U = {1, 2, 3, 4, 5, 6}

reference_table = [
    ("Union", "A | B", reference_A | reference_B),
    ("Intersection", "A & B", reference_A & reference_B),
    ("Difference", "A - B", reference_A - reference_B),
    ("Reverse difference", "B - A", reference_B - reference_A),
    ("Complement", "U - A", reference_U - reference_A),
    ("Symmetric difference", "A ^ B", reference_A ^ reference_B),
    ("Subset", "A <= B", reference_A <= reference_B),
    ("Proper subset", "A < B", reference_A < reference_B),
    ("Superset", "A >= B", reference_A >= reference_B),
    ("Proper superset", "A > B", reference_A > reference_B),
    ("Disjoint", "A.isdisjoint(B)", reference_A.isdisjoint(reference_B)),
]

for operation, syntax, result in reference_table:
    print(f"{operation:22s} | {syntax:22s} | {result}")


# =============================================================================
# 73. FINAL INTEGRATED EXAMPLE
# =============================================================================

section("73. INTEGRATED EXAMPLE: THREE-COURSE ANALYTICS")

students = set(
    [
        "Asha",
        "Bharat",
        "Chen",
        "Deepa",
        "Eshan",
        "Fatima",
        "Gopal",
        "Hari",
    ]
)

python_students = {"Asha", "Bharat", "Deepa", "Fatima"}
sql_students = {"Bharat", "Chen", "Deepa", "Gopal"}
ml_students = {"Asha", "Deepa", "Eshan", "Gopal"}

print("All registered students:", students)
print("Python:", python_students)
print("SQL:", sql_students)
print("ML:", ml_students)

print("\nStudents in at least one course:")
print(python_students | sql_students | ml_students)

print("\nStudents in all three:")
print(python_students & sql_students & ml_students)

print("\nPython but not SQL:")
print(python_students - sql_students)

print("\nSQL but not Python:")
print(sql_students - python_students)

print("\nExactly one of Python and SQL:")
print(python_students ^ sql_students)

print("\nStudents in no listed course:")
print(students - (python_students | sql_students | ml_students))

print("\nPython and ML but not SQL:")
print((python_students & ml_students) - sql_students)

print("\nNumber taking at least one:")
print(len(python_students | sql_students | ml_students))

print("\nNumber taking all three:")
print(len(python_students & sql_students & ml_students))


# =============================================================================
# 74. FINAL VALIDATION OF IMPORTANT THEOREMS
# =============================================================================

section("74. FINAL THEOREM VALIDATION")

def validate_set_theorems() -> None:
    """Validate major identities over a finite universal set."""
    U = set(range(12))

    test_sets = [
        set(),
        {0},
        {1, 3, 5, 7},
        {2, 4, 6, 8},
        {1, 2, 3, 4, 5},
        U,
    ]

    for A in test_sets:
        for B in test_sets:
            for C in test_sets:
                # Commutative laws
                assert A | B == B | A
                assert A & B == B & A

                # Associative laws
                assert (A | B) | C == A | (B | C)
                assert (A & B) & C == A & (B & C)

                # Distributive laws
                assert A & (B | C) == (A & B) | (A & C)
                assert A | (B & C) == (A | B) & (A | C)

                # De Morgan's laws
                assert U - (A | B) == (U - A) & (U - B)
                assert U - (A & B) == (U - A) | (U - B)

                # Difference identities
                assert A - B == A & (U - B)
                assert A - (B | C) == (A - B) & (A - C)
                assert A - (B & C) == (A - B) | (A - C)

                # Symmetric difference
                assert A ^ B == (A - B) | (B - A)
                assert A ^ B == (A | B) - (A & B)
                assert A ^ B == B ^ A

                # Absorption
                assert A | (A & B) == A
                assert A & (A | B) == A

                # Complements
                assert A | (U - A) == U
                assert A & (U - A) == set()
                assert U - (U - A) == A

    print(
        "All major set identities passed for",
        len(test_sets),
        "representative sets.",
    )


validate_set_theorems()


# =============================================================================
# 75. COMPLETION
# =============================================================================

section("75. STUDY SCRIPT COMPLETED")

print(
    "The script has demonstrated fundamental, intermediate, and advanced "
    "set operations, Venn-region analysis, Cartesian products, cardinality, "
    "set identities, implementation patterns, edge cases, testing, "
    "performance considerations, and practical applications."
)
