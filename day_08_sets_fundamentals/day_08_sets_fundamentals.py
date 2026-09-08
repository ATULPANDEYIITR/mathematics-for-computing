"""
Sets Fundamentals
=================

A comprehensive, self-contained study script covering:

- Sets and elements
- Set notation
- Empty sets
- Universal sets
- Finite and infinite sets
- Equality of sets
- Equivalent sets
- Subsets and proper subsets
- Power sets
- Membership
- Set-builder notation
- Union, intersection, difference, and symmetric difference
- Complements
- Disjoint sets
- Cardinality
- Venn-diagram reasoning through Python operations
- Important mathematical laws
- Python set implementation details
- Mutable vs immutable set concepts
- Edge cases
- Common mistakes
- Practical applications
- Algorithms and performance considerations
- Validation and testing
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, FrozenSet, Iterable, Set


# =============================================================================
# 1. INTRODUCTION TO SETS
# =============================================================================

print("\n" + "=" * 80)
print("1. INTRODUCTION TO SETS")
print("=" * 80)

# A mathematical set is a collection of distinct objects called elements.
#
# Python's built-in set type follows the same fundamental principle:
# duplicate values are automatically removed.

numbers = {1, 2, 3, 4, 5}
print("Set:", numbers)

# Duplicate elements are removed.
duplicates_removed = {1, 1, 2, 2, 3, 3}
print("Duplicates removed:", duplicates_removed)

# Sets are unordered.
# The printed order should not be treated as mathematically meaningful.
letters = {"a", "b", "c"}
print("Letters:", letters)


# =============================================================================
# 2. ELEMENTS AND MEMBERSHIP
# =============================================================================

print("\n" + "=" * 80)
print("2. ELEMENTS AND MEMBERSHIP")
print("=" * 80)

students = {"Asha", "Bharat", "Charu"}

# Mathematical notation:
#
# Asha ∈ students
#
# means "Asha is an element of students".

print("'Asha' in students:", "Asha" in students)
print("'David' in students:", "David" in students)

# Mathematical notation:
#
# David ∉ students
#
# means "David is not an element of students".

print("'David' not in students:", "David" not in students)


# =============================================================================
# 3. SET NOTATION
# =============================================================================

print("\n" + "=" * 80)
print("3. SET NOTATION")
print("=" * 80)

# Roster notation lists elements explicitly.

A = {1, 2, 3, 4}
print("A =", A)

# In mathematics, a set can also be described by a condition.
#
# Set-builder notation:
#
# B = {x | x is an even integer and 0 <= x <= 10}
#
# Python equivalent:

B = {x for x in range(11) if x % 2 == 0}
print("B =", B)


# =============================================================================
# 4. THE EMPTY SET
# =============================================================================

print("\n" + "=" * 80)
print("4. THE EMPTY SET")
print("=" * 80)

# The empty set contains no elements.
#
# Mathematical notation:
#
# ∅
#
# or
#
# {}

empty_set = set()

print("Empty set:", empty_set)
print("Number of elements:", len(empty_set))

# Important Python distinction:
#
# {} creates an empty dictionary, NOT an empty set.

empty_dictionary = {}

print("Type of set():", type(empty_set).__name__)
print("Type of {}:", type(empty_dictionary).__name__)


# =============================================================================
# 5. FINITE AND INFINITE SETS
# =============================================================================

print("\n" + "=" * 80)
print("5. FINITE AND INFINITE SETS")
print("=" * 80)

finite_set = {10, 20, 30}

print("Finite set:", finite_set)
print("Cardinality:", len(finite_set))

# Mathematical examples of infinite sets:
#
# Natural numbers:
# N = {1, 2, 3, ...}
#
# Integers:
# Z = {..., -2, -1, 0, 1, 2, ...}
#
# Real numbers:
# R = all real values
#
# A normal Python set cannot explicitly store an actually infinite collection.
# Instead, Python programs often represent infinite mathematical structures
# using generators, formulas, predicates, or bounded approximations.

first_ten_natural_numbers = set(range(1, 11))
print("Finite approximation of natural numbers:", first_ten_natural_numbers)


# =============================================================================
# 6. CARDINALITY
# =============================================================================

print("\n" + "=" * 80)
print("6. CARDINALITY")
print("=" * 80)

# Cardinality means the number of distinct elements in a set.
#
# Mathematical notation:
#
# |A|

C = {10, 20, 30, 40}

print("C =", C)
print("|C| =", len(C))

# Repeated elements do not increase cardinality.

D = {1, 1, 1, 2, 2, 3}
print("D =", D)
print("|D| =", len(D))


# =============================================================================
# 7. EQUAL SETS
# =============================================================================

print("\n" + "=" * 80)
print("7. EQUAL SETS")
print("=" * 80)

# Two sets are equal if they contain exactly the same elements.
# Order does not matter.

set_one = {1, 2, 3}
set_two = {3, 2, 1}

print("set_one:", set_one)
print("set_two:", set_two)
print("Are they equal?", set_one == set_two)

# Duplicates do not affect equality.

set_three = {1, 1, 2, 3}
print("set_one == set_three?", set_one == set_three)


# =============================================================================
# 8. EQUIVALENT SETS
# =============================================================================

print("\n" + "=" * 80)
print("8. EQUIVALENT SETS")
print("=" * 80)

# Two sets are equivalent when they have the same cardinality,
# even if their elements differ.

E = {1, 2, 3}
F = {"red", "green", "blue"}

print("E =", E)
print("F =", F)
print("|E| =", len(E))
print("|F| =", len(F))
print("Equivalent by cardinality?", len(E) == len(F))
print("Equal?", E == F)


# =============================================================================
# 9. SUBSETS
# =============================================================================

print("\n" + "=" * 80)
print("9. SUBSETS")
print("=" * 80)

# A is a subset of B if every element of A belongs to B.
#
# Mathematical notation:
#
# A ⊆ B

A = {1, 2}
B = {1, 2, 3, 4}

print("A =", A)
print("B =", B)
print("A is a subset of B:", A.issubset(B))
print("A <= B:", A <= B)

# Every set is a subset of itself.

print("A is a subset of A:", A <= A)

# The empty set is a subset of every set.

print("Empty set is subset of B:", set() <= B)


# =============================================================================
# 10. PROPER SUBSETS
# =============================================================================

print("\n" + "=" * 80)
print("10. PROPER SUBSETS")
print("=" * 80)

# A is a proper subset of B if:
#
# 1. Every element of A belongs to B.
# 2. A and B are not equal.
#
# Mathematical notation is commonly:
#
# A ⊂ B
#
# Python uses < for proper subset testing.

small = {1, 2}
large = {1, 2, 3}

print("small < large:", small < large)
print("small <= large:", small <= large)
print("large < large:", large < large)


# =============================================================================
# 11. SUPERSETS
# =============================================================================

print("\n" + "=" * 80)
print("11. SUPERSETS")
print("=" * 80)

# B is a superset of A if A is a subset of B.

A = {1, 2}
B = {1, 2, 3, 4}

print("B is a superset of A:", B.issuperset(A))
print("B >= A:", B >= A)

# Proper superset.

print("B > A:", B > A)


# =============================================================================
# 12. THE UNIVERSAL SET
# =============================================================================

print("\n" + "=" * 80)
print("12. THE UNIVERSAL SET")
print("=" * 80)

# The universal set contains all objects under consideration.
#
# Mathematical notation often uses:
#
# U

U = set(range(1, 11))
A = {2, 4, 6, 8}

print("Universal set U:", U)
print("Set A:", A)
print("A is subset of U:", A <= U)

# The universal set depends on context.
#
# Example:
#
# If the discussion concerns numbers from 1 through 10,
# U = {1, 2, ..., 10}.
#
# If the discussion concerns students in a class,
# U might contain every student in that class.


# =============================================================================
# 13. SET COMPLEMENT
# =============================================================================

print("\n" + "=" * 80)
print("13. SET COMPLEMENT")
print("=" * 80)

# The complement of A contains elements in the universal set
# that are not in A.
#
# Mathematical notation:
#
# Aᶜ
#
# or
#
# U - A

U = {1, 2, 3, 4, 5, 6, 7, 8}
A = {2, 4, 6, 8}

A_complement = U - A

print("U =", U)
print("A =", A)
print("Complement of A =", A_complement)


# =============================================================================
# 14. UNION
# =============================================================================

print("\n" + "=" * 80)
print("14. UNION")
print("=" * 80)

# The union of A and B contains every element that belongs
# to A, B, or both.
#
# Mathematical notation:
#
# A ∪ B
#
# Python:
#
# A | B
#
# or
#
# A.union(B)

A = {1, 2, 3}
B = {3, 4, 5}

union_result = A | B

print("A =", A)
print("B =", B)
print("A union B =", union_result)
print("A.union(B) =", A.union(B))


# =============================================================================
# 15. INTERSECTION
# =============================================================================

print("\n" + "=" * 80)
print("15. INTERSECTION")
print("=" * 80)

# The intersection contains elements common to both sets.
#
# Mathematical notation:
#
# A ∩ B
#
# Python:
#
# A & B
#
# or
#
# A.intersection(B)

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

intersection_result = A & B

print("A =", A)
print("B =", B)
print("A intersection B =", intersection_result)


# =============================================================================
# 16. SET DIFFERENCE
# =============================================================================

print("\n" + "=" * 80)
print("16. SET DIFFERENCE")
print("=" * 80)

# A - B contains elements that belong to A but not to B.

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

print("A - B =", A - B)
print("B - A =", B - A)

# Set difference is NOT generally commutative.

print("(A - B) == (B - A):", (A - B) == (B - A))


# =============================================================================
# 17. SYMMETRIC DIFFERENCE
# =============================================================================

print("\n" + "=" * 80)
print("17. SYMMETRIC DIFFERENCE")
print("=" * 80)

# The symmetric difference contains elements that belong to
# exactly one of the sets.
#
# Mathematical notation:
#
# A Δ B
#
# Python:
#
# A ^ B
#
# or
#
# A.symmetric_difference(B)

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

print("A symmetric difference B =", A ^ B)


# =============================================================================
# 18. DISJOINT SETS
# =============================================================================

print("\n" + "=" * 80)
print("18. DISJOINT SETS")
print("=" * 80)

# Two sets are disjoint if they have no elements in common.
#
# Mathematically:
#
# A ∩ B = ∅

A = {1, 2, 3}
B = {4, 5, 6}
C = {3, 4, 5}

print("A and B are disjoint:", A.isdisjoint(B))
print("A and C are disjoint:", A.isdisjoint(C))
print("A intersection B:", A & B)


# =============================================================================
# 19. POWER SET
# =============================================================================

print("\n" + "=" * 80)
print("19. POWER SET")
print("=" * 80)

# The power set of A is the set containing every possible subset of A.
#
# Mathematical notation:
#
# P(A)
#
# If a set has n elements, its power set has:
#
# 2^n
#
# subsets.

def power_set(values: Iterable[Any]) -> Set[FrozenSet[Any]]:
    """
    Return the mathematical power set as a set of frozensets.

    A normal mutable set cannot be stored inside another normal set because
    mutable sets are unhashable. frozenset is immutable and hashable, so it
    can represent a subset inside the outer power set.
    """
    values = list(values)
    result: Set[FrozenSet[Any]] = set()

    for subset_size in range(len(values) + 1):
        for subset in combinations(values, subset_size):
            result.add(frozenset(subset))

    return result


A = {1, 2, 3}
P_A = power_set(A)

print("A =", A)
print("Power set size:", len(P_A))
print("Expected size:", 2 ** len(A))

print("Power set:")
for subset in sorted(P_A, key=lambda item: (len(item), sorted(map(str, item)))):
    print(set(subset))


# =============================================================================
# 20. SET-BUILDER NOTATION AND COMPREHENSIONS
# =============================================================================

print("\n" + "=" * 80)
print("20. SET-BUILDER NOTATION AND COMPREHENSIONS")
print("=" * 80)

# Mathematical form:
#
# A = {x | condition involving x}
#
# Python set comprehension:
#
# {expression for item in iterable if condition}

even_numbers = {x for x in range(1, 21) if x % 2 == 0}
squares = {x * x for x in range(1, 11)}
unique_first_letters = {name[0] for name in ["Alice", "Andrew", "Bob", "Bella"]}

print("Even numbers:", even_numbers)
print("Squares:", squares)
print("Unique first letters:", unique_first_letters)


# =============================================================================
# 21. BASIC SET LAWS
# =============================================================================

print("\n" + "=" * 80)
print("21. BASIC SET LAWS")
print("=" * 80)

A = {1, 2, 3}
B = {3, 4, 5}
C = {5, 6, 7}

# Commutative laws:
#
# A ∪ B = B ∪ A
# A ∩ B = B ∩ A

print("Union commutative:", A | B == B | A)
print("Intersection commutative:", A & B == B & A)

# Associative laws:
#
# (A ∪ B) ∪ C = A ∪ (B ∪ C)
# (A ∩ B) ∩ C = A ∩ (B ∩ C)

print("Union associative:", (A | B) | C == A | (B | C))
print("Intersection associative:", (A & B) & C == A & (B & C))

# Idempotent laws:
#
# A ∪ A = A
# A ∩ A = A

print("Union idempotent:", A | A == A)
print("Intersection idempotent:", A & A == A)

# Identity laws:
#
# A ∪ ∅ = A
# A ∩ U = A, when A ⊆ U

U = set(range(1, 11))
print("Union with empty set:", A | set() == A)
print("Intersection with universal set:", A & U == A)


# =============================================================================
# 22. ABSORPTION LAWS
# =============================================================================

print("\n" + "=" * 80)
print("22. ABSORPTION LAWS")
print("=" * 80)

# A ∪ (A ∩ B) = A
# A ∩ (A ∪ B) = A

A = {1, 2, 3}
B = {3, 4, 5}

print("A union (A intersection B) == A:", A | (A & B) == A)
print("A intersection (A union B) == A:", A & (A | B) == A)


# =============================================================================
# 23. DISTRIBUTIVE LAWS
# =============================================================================

print("\n" + "=" * 80)
print("23. DISTRIBUTIVE LAWS")
print("=" * 80)

A = {1, 2, 3}
B = {3, 4, 5}
C = {2, 5, 6}

# A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)

left_union_distribution = A | (B & C)
right_union_distribution = (A | B) & (A | C)

print("Union distributes over intersection:",
      left_union_distribution == right_union_distribution)

# A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)

left_intersection_distribution = A & (B | C)
right_intersection_distribution = (A & B) | (A & C)

print("Intersection distributes over union:",
      left_intersection_distribution == right_intersection_distribution)


# =============================================================================
# 24. DE MORGAN'S LAWS
# =============================================================================

print("\n" + "=" * 80)
print("24. DE MORGAN'S LAWS")
print("=" * 80)

# Given universal set U:
#
# (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
#
# (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ

U = set(range(1, 11))
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

left_1 = U - (A | B)
right_1 = (U - A) & (U - B)

left_2 = U - (A & B)
right_2 = (U - A) | (U - B)

print("De Morgan law 1:", left_1 == right_1)
print("De Morgan law 2:", left_2 == right_2)


# =============================================================================
# 25. SET RELATIONSHIPS
# =============================================================================

print("\n" + "=" * 80)
print("25. SET RELATIONSHIPS")
print("=" * 80)

def describe_relationship(first: set[Any], second: set[Any]) -> None:
    """Print important relationships between two sets."""

    print("\nFirst set:", first)
    print("Second set:", second)
    print("Equal:", first == second)
    print("First subset of second:", first <= second)
    print("Second subset of first:", second <= first)
    print("First proper subset of second:", first < second)
    print("Second proper subset of first:", second < first)
    print("Disjoint:", first.isdisjoint(second))
    print("Intersection:", first & second)
    print("Union:", first | second)
    print("First minus second:", first - second)
    print("Second minus first:", second - first)


describe_relationship({1, 2}, {1, 2, 3})
describe_relationship({1, 2}, {3, 4})
describe_relationship({1, 2, 3}, {3, 2, 1})


# =============================================================================
# 26. PYTHON SET CREATION
# =============================================================================

print("\n" + "=" * 80)
print("26. PYTHON SET CREATION")
print("=" * 80)

literal_set = {1, 2, 3}
from_list = set([1, 2, 2, 3])
from_string = set("banana")

print("Literal:", literal_set)
print("From list:", from_list)
print("From string:", from_string)

# A string is iterable, so set("banana") creates a set of unique characters.


# =============================================================================
# 27. MUTABLE SETS AND FROZEN SETS
# =============================================================================

print("\n" + "=" * 80)
print("27. MUTABLE SETS AND FROZEN SETS")
print("=" * 80)

# Python set:
# - Mutable
# - Cannot be used as a dictionary key
# - Cannot normally be an element of another set

mutable_set = {1, 2, 3}
mutable_set.add(4)

print("Mutable set:", mutable_set)

# frozenset:
# - Immutable
# - Hashable when all contained elements are hashable
# - Can be used as a dictionary key
# - Can be placed inside another set

immutable_set = frozenset({1, 2, 3})

print("Frozen set:", immutable_set)

nested_sets = {
    frozenset({1, 2}),
    frozenset({3, 4}),
}

print("Set containing frozensets:", nested_sets)


# =============================================================================
# 28. ADDING AND REMOVING ELEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("28. ADDING AND REMOVING ELEMENTS")
print("=" * 80)

values = {1, 2, 3}

values.add(4)
print("After add(4):", values)

# Adding an existing value changes nothing.

values.add(4)
print("After adding 4 again:", values)

# update() adds multiple values from an iterable.

values.update([5, 6, 7])
print("After update([5, 6, 7]):", values)

# remove() raises KeyError if the value is absent.

values.remove(7)
print("After remove(7):", values)

# discard() does not raise an error if the value is absent.

values.discard(100)
print("After discard(100):", values)

# pop() removes an arbitrary element.

removed_value = values.pop()
print("Arbitrary removed value:", removed_value)
print("Remaining set:", values)


# =============================================================================
# 29. MUTATING SET OPERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("29. MUTATING SET OPERATIONS")
print("=" * 80)

A = {1, 2, 3}
B = {3, 4, 5}

A.update(B)
print("After A.update(B):", A)

A = {1, 2, 3}
A.intersection_update(B)
print("After A.intersection_update(B):", A)

A = {1, 2, 3}
A.difference_update(B)
print("After A.difference_update(B):", A)

A = {1, 2, 3}
A.symmetric_difference_update(B)
print("After A.symmetric_difference_update(B):", A)


# =============================================================================
# 30. IMPORTANT EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("30. IMPORTANT EDGE CASES")
print("=" * 80)

# Empty set behavior.

empty = set()
A = {1, 2, 3}

print("A union empty:", A | empty)
print("A intersection empty:", A & empty)
print("A minus empty:", A - empty)
print("Empty minus A:", empty - A)
print("A symmetric difference empty:", A ^ empty)

# Every set contains itself as a subset.

print("A <= A:", A <= A)

# The empty set is a subset of itself.

print("empty <= empty:", empty <= empty)

# The empty set has exactly one subset: itself.

empty_power_set = power_set(empty)
print("Power set of empty set:", empty_power_set)
print("Size:", len(empty_power_set))


# =============================================================================
# 31. UNHASHABLE ELEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("31. UNHASHABLE ELEMENTS")
print("=" * 80)

# Set elements must be hashable.
#
# Numbers, strings, tuples containing hashable values, and frozensets
# are commonly hashable.
#
# Lists, dictionaries, and ordinary sets are mutable and unhashable.

valid_set = {
    42,
    "hello",
    (1, 2),
    frozenset({3, 4}),
}

print("Valid hashable elements:", valid_set)

try:
    invalid_set = {[1, 2, 3]}
except TypeError as error:
    print("Cannot store a list in a set:", error)


# =============================================================================
# 32. SETS VERSUS LISTS
# =============================================================================

print("\n" + "=" * 80)
print("32. SETS VERSUS LISTS")
print("=" * 80)

sample_list = [1, 2, 2, 3, 3, 3]
sample_set = {1, 2, 2, 3, 3, 3}

print("List:", sample_list)
print("Set:", sample_set)

# Important distinctions:
#
# List:
# - Ordered
# - Allows duplicates
# - Supports indexing
#
# Set:
# - Stores unique elements
# - Designed for membership testing and set algebra
# - Does not provide positional indexing

try:
    print(sample_set[0])
except TypeError as error:
    print("Sets cannot be indexed:", error)


# =============================================================================
# 33. SETS VERSUS TUPLES
# =============================================================================

print("\n" + "=" * 80)
print("33. SETS VERSUS TUPLES")
print("=" * 80)

sample_tuple = (1, 2, 2, 3)
sample_set = {1, 2, 2, 3}

print("Tuple:", sample_tuple)
print("Set:", sample_set)

# Tuples preserve sequence structure and duplicates.
# Sets represent uniqueness and membership.


# =============================================================================
# 34. SETS VERSUS DICTIONARIES
# =============================================================================

print("\n" + "=" * 80)
print("34. SETS VERSUS DICTIONARIES")
print("=" * 80)

# A dictionary maps unique keys to values.
# A set stores only unique values.

dictionary = {"name": "Asha", "age": 25}
set_of_values = {"Asha", 25}

print("Dictionary:", dictionary)
print("Set:", set_of_values)

# Both dictionaries and sets rely heavily on hashing internally.


# =============================================================================
# 35. PRACTICAL APPLICATION: REMOVING DUPLICATES
# =============================================================================

print("\n" + "=" * 80)
print("35. PRACTICAL APPLICATION: REMOVING DUPLICATES")
print("=" * 80)

raw_ids = [101, 102, 103, 101, 104, 102, 105]

unique_ids = set(raw_ids)

print("Original IDs:", raw_ids)
print("Unique IDs:", unique_ids)

# Converting directly to a set removes duplicates, but the original ordering
# should not be relied upon.

# If both uniqueness and original order are needed:

ordered_unique_ids = list(dict.fromkeys(raw_ids))

print("Ordered unique IDs:", ordered_unique_ids)


# =============================================================================
# 36. PRACTICAL APPLICATION: COMMON INTERESTS
# =============================================================================

print("\n" + "=" * 80)
print("36. PRACTICAL APPLICATION: COMMON INTERESTS")
print("=" * 80)

user_a_interests = {"python", "data", "music", "travel"}
user_b_interests = {"music", "sports", "travel", "history"}

common_interests = user_a_interests & user_b_interests
all_interests = user_a_interests | user_b_interests
only_user_a = user_a_interests - user_b_interests
only_user_b = user_b_interests - user_a_interests

print("Common:", common_interests)
print("All:", all_interests)
print("Only user A:", only_user_a)
print("Only user B:", only_user_b)


# =============================================================================
# 37. PRACTICAL APPLICATION: ACCESS CONTROL
# =============================================================================

print("\n" + "=" * 80)
print("37. PRACTICAL APPLICATION: ACCESS CONTROL")
print("=" * 80)

required_permissions = {"read_reports", "view_dashboard"}
user_permissions = {"read_reports", "view_dashboard", "download_reports"}

# The user satisfies the requirement if required_permissions is a subset
# of user_permissions.

has_required_access = required_permissions <= user_permissions

print("Required permissions:", required_permissions)
print("User permissions:", user_permissions)
print("Access granted:", has_required_access)


# =============================================================================
# 38. PRACTICAL APPLICATION: MISSING REQUIREMENTS
# =============================================================================

print("\n" + "=" * 80)
print("38. PRACTICAL APPLICATION: MISSING REQUIREMENTS")
print("=" * 80)

required_skills = {"python", "sql", "statistics", "git"}
candidate_skills = {"python", "sql", "excel"}

missing_skills = required_skills - candidate_skills
matching_skills = required_skills & candidate_skills

print("Required:", required_skills)
print("Candidate:", candidate_skills)
print("Matching:", matching_skills)
print("Missing:", missing_skills)


# =============================================================================
# 39. PRACTICAL APPLICATION: DATA VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("39. PRACTICAL APPLICATION: DATA VALIDATION")
print("=" * 80)

allowed_statuses = {"pending", "approved", "rejected"}

submitted_statuses = {"pending", "approved", "invalid"}

invalid_statuses = submitted_statuses - allowed_statuses

if invalid_statuses:
    print("Invalid statuses found:", invalid_statuses)
else:
    print("All statuses are valid.")


# =============================================================================
# 40. PRACTICAL APPLICATION: DETECTING DUPLICATES
# =============================================================================

print("\n" + "=" * 80)
print("40. PRACTICAL APPLICATION: DETECTING DUPLICATES")
print("=" * 80)

def find_duplicates(values: Iterable[Any]) -> Set[Any]:
    """
    Return values that appear more than once.

    A set named seen stores elements encountered for the first time.
    A set named duplicates stores elements encountered again.
    """
    seen: Set[Any] = set()
    duplicates: Set[Any] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return duplicates


values = [1, 2, 3, 2, 4, 5, 3, 3]

print("Values:", values)
print("Duplicates:", find_duplicates(values))


# =============================================================================
# 41. PRACTICAL APPLICATION: UNIQUE WORDS
# =============================================================================

print("\n" + "=" * 80)
print("41. PRACTICAL APPLICATION: UNIQUE WORDS")
print("=" * 80)

sentence = "sets provide efficient membership testing and sets remove duplicates"

words = sentence.lower().split()
unique_words = set(words)

print("Words:", words)
print("Unique words:", unique_words)
print("Number of unique words:", len(unique_words))


# =============================================================================
# 42. PERFORMANCE CHARACTERISTICS
# =============================================================================

print("\n" + "=" * 80)
print("42. PERFORMANCE CHARACTERISTICS")
print("=" * 80)

# Python sets are implemented using a hash-table-based structure.
#
# Average-case complexities are typically:
#
# Membership:
#     value in set        -> O(1)
#
# Add:
#     set.add(value)      -> O(1)
#
# Remove:
#     set.remove(value)   -> O(1)
#
# Set intersection:
#     often proportional to the size of the smaller set
#
# Set union:
#     generally proportional to the total number of processed elements
#
# Exact performance depends on hashing, collisions, resizing,
# object types, and implementation details.

large_values = set(range(1_000))
target = 500

print("Membership result:", target in large_values)


# =============================================================================
# 43. WHY HASHABILITY MATTERS
# =============================================================================

print("\n" + "=" * 80)
print("43. WHY HASHABILITY MATTERS")
print("=" * 80)

# Sets use hashes to quickly locate elements.
#
# Hashable objects should have stable hash values during their lifetime
# while used as members of a set.

values = {"apple", "banana", "orange"}

for value in values:
    print(value, "-> hash:", hash(value))


# =============================================================================
# 44. CUSTOM OBJECTS AND SETS
# =============================================================================

print("\n" + "=" * 80)
print("44. CUSTOM OBJECTS AND SETS")
print("=" * 80)

# Custom objects need carefully defined equality and hashing behavior
# when they are intended for use in sets.


class Student:
    """
    Student identity is determined by student_id.

    __eq__ defines logical equality.
    __hash__ must remain consistent with __eq__.
    """

    def __init__(self, student_id: int, name: str) -> None:
        self.student_id = student_id
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented

        return self.student_id == other.student_id

    def __hash__(self) -> int:
        return hash(self.student_id)

    def __repr__(self) -> str:
        return (
            f"Student(student_id={self.student_id}, "
            f"name={self.name!r})"
        )


student_1 = Student(101, "Asha")
student_2 = Student(101, "Different Name")
student_3 = Student(102, "Bharat")

student_set = {student_1, student_2, student_3}

print("Student set:", student_set)
print("Number of students:", len(student_set))

# student_1 and student_2 have the same student_id,
# so they are treated as equal.


# =============================================================================
# 45. COMMON MISTAKE: CONFUSING {} WITH AN EMPTY SET
# =============================================================================

print("\n" + "=" * 80)
print("45. COMMON MISTAKE: {} IS A DICTIONARY")
print("=" * 80)

empty_braces = {}
actual_empty_set = set()

print("{} type:", type(empty_braces).__name__)
print("set() type:", type(actual_empty_set).__name__)


# =============================================================================
# 46. COMMON MISTAKE: EXPECTING ORDER
# =============================================================================

print("\n" + "=" * 80)
print("46. COMMON MISTAKE: EXPECTING ORDER")
print("=" * 80)

values = {10, 20, 30, 40}

print("Set:", values)

# Do not treat the displayed order as a mathematical ordering.
#
# If deterministic ordering is needed for display:

print("Sorted values:", sorted(values))


# =============================================================================
# 47. COMMON MISTAKE: MODIFYING A SET WHILE ITERATING
# =============================================================================

print("\n" + "=" * 80)
print("47. COMMON MISTAKE: MODIFYING WHILE ITERATING")
print("=" * 80)

values = {1, 2, 3, 4, 5}

# Modifying the size of a set during direct iteration can raise RuntimeError.
#
# Safe approach: iterate over a copy.

for value in values.copy():
    if value % 2 == 0:
        values.remove(value)

print("After removing even values safely:", values)


# =============================================================================
# 48. COMMON MISTAKE: MUTABLE OBJECTS AS ELEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("48. COMMON MISTAKE: MUTABLE OBJECTS AS ELEMENTS")
print("=" * 80)

try:
    values = {{"a": 1}}
except TypeError as error:
    print("Dictionary cannot be a set element:", error)

# Use immutable representations where appropriate.

valid_values = {
    frozenset({"a", "b"}),
    frozenset({"c", "d"}),
}

print("Using frozensets:", valid_values)


# =============================================================================
# 49. ADVANCED CONCEPT: SET PARTITION
# =============================================================================

print("\n" + "=" * 80)
print("49. ADVANCED CONCEPT: SET PARTITION")
print("=" * 80)

# A partition divides a set into non-empty subsets such that:
#
# 1. Every element belongs to exactly one partition.
# 2. The subsets are pairwise disjoint.
# 3. The union of all subsets equals the original set.

universal = {1, 2, 3, 4, 5, 6}
partition = [
    {1, 2},
    {3, 4},
    {5, 6},
]

combined = set().union(*partition)

pairwise_disjoint = all(
    first.isdisjoint(second)
    for first, second in combinations(partition, 2)
)

print("Universal:", universal)
print("Partition:", partition)
print("Union equals universal:", combined == universal)
print("All partition groups pairwise disjoint:", pairwise_disjoint)


# =============================================================================
# 50. ADVANCED CONCEPT: JACCARD SIMILARITY
# =============================================================================

print("\n" + "=" * 80)
print("50. ADVANCED CONCEPT: JACCARD SIMILARITY")
print("=" * 80)

# Jaccard similarity measures overlap between two sets:
#
# J(A, B) = |A ∩ B| / |A ∪ B|
#
# Important edge case:
#
# If both sets are empty, the union is empty and the ordinary
# mathematical expression divides by zero.
#
# This implementation defines similarity(empty, empty) as 1.0 because
# the two sets are identical.

def jaccard_similarity(
    first: Set[Any],
    second: Set[Any],
) -> float:
    """Calculate Jaccard similarity with explicit empty-set handling."""
    union = first | second

    if not union:
        return 1.0

    return len(first & second) / len(union)


A = {"python", "sql", "statistics"}
B = {"python", "sql", "excel"}

print("Jaccard similarity:", jaccard_similarity(A, B))
print(
    "Empty-set similarity:",
    jaccard_similarity(set(), set()),
)


# =============================================================================
# 51. ADVANCED CONCEPT: SET COVERAGE
# =============================================================================

print("\n" + "=" * 80)
print("51. ADVANCED CONCEPT: SET COVERAGE")
print("=" * 80)

# A coverage ratio can measure how much of a required set is present.

def coverage_ratio(
    required: Set[Any],
    available: Set[Any],
) -> float:
    """
    Return the fraction of required elements that are available.

    An empty required set is considered fully satisfied.
    """
    if not required:
        return 1.0

    return len(required & available) / len(required)


required_features = {
    "login",
    "dashboard",
    "reporting",
    "export",
}

implemented_features = {
    "login",
    "dashboard",
    "reporting",
}

print(
    "Coverage:",
    coverage_ratio(required_features, implemented_features),
)


# =============================================================================
# 52. ADVANCED CONCEPT: INCLUSION-EXCLUSION FOR TWO SETS
# =============================================================================

print("\n" + "=" * 80)
print("52. INCLUSION-EXCLUSION PRINCIPLE")
print("=" * 80)

# For two finite sets:
#
# |A ∪ B| = |A| + |B| - |A ∩ B|

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

calculated_union_size = len(A) + len(B) - len(A & B)
actual_union_size = len(A | B)

print("Calculated union size:", calculated_union_size)
print("Actual union size:", actual_union_size)
print("Formula correct:", calculated_union_size == actual_union_size)


# =============================================================================
# 53. ADVANCED CONCEPT: INCLUSION-EXCLUSION FOR THREE SETS
# =============================================================================

print("\n" + "=" * 80)
print("53. THREE-SET INCLUSION-EXCLUSION")
print("=" * 80)

# For finite sets A, B, and C:
#
# |A ∪ B ∪ C|
# =
# |A| + |B| + |C|
# - |A ∩ B| - |A ∩ C| - |B ∩ C|
# + |A ∩ B ∩ C|

A = {1, 2, 3, 4}
B = {3, 4, 5, 6}
C = {4, 6, 7, 8}

calculated_size = (
    len(A)
    + len(B)
    + len(C)
    - len(A & B)
    - len(A & C)
    - len(B & C)
    + len(A & B & C)
)

actual_size = len(A | B | C)

print("Calculated:", calculated_size)
print("Actual:", actual_size)
print("Formula correct:", calculated_size == actual_size)


# =============================================================================
# 54. ADVANCED CONCEPT: RELATION BETWEEN SUBSETS AND POWER SETS
# =============================================================================

print("\n" + "=" * 80)
print("54. SUBSETS AND POWER SETS")
print("=" * 80)

A = {"x", "y"}

all_subsets = power_set(A)

print("Original set:", A)
print("All subsets:")

for subset in all_subsets:
    print(set(subset))

print("Number of subsets:", len(all_subsets))
print("2^|A|:", 2 ** len(A))


# =============================================================================
# 55. PRODUCTION CONSIDERATION: INPUT NORMALIZATION
# =============================================================================

print("\n" + "=" * 80)
print("55. INPUT NORMALIZATION")
print("=" * 80)

# Real data often contains inconsistent capitalization or surrounding spaces.

raw_tags = [
    " Python",
    "python",
    "PYTHON",
    "Data",
    " data ",
]

normalized_tags = {
    tag.strip().lower()
    for tag in raw_tags
}

print("Raw tags:", raw_tags)
print("Normalized unique tags:", normalized_tags)


# =============================================================================
# 56. PRODUCTION CONSIDERATION: VALIDATING SET-LIKE INPUT
# =============================================================================

print("\n" + "=" * 80)
print("56. VALIDATING SET-LIKE INPUT")
print("=" * 80)

def ensure_set(values: Iterable[Any]) -> Set[Any]:
    """
    Convert an iterable to a set.

    Raises a clear TypeError if the object is not iterable.
    """
    try:
        return set(values)
    except TypeError as error:
        raise TypeError(
            "Expected an iterable containing hashable values."
        ) from error


print("Validated set:", ensure_set([1, 2, 2, 3]))

try:
    ensure_set(42)
except TypeError as error:
    print("Validation error:", error)


# =============================================================================
# 57. TESTING SET OPERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("57. TESTING SET OPERATIONS")
print("=" * 80)

def test_set_operations() -> None:
    """Use assertions to verify fundamental set behavior."""

    A = {1, 2, 3}
    B = {3, 4}

    assert A | B == {1, 2, 3, 4}
    assert A & B == {3}
    assert A - B == {1, 2}
    assert B - A == {4}
    assert A ^ B == {1, 2, 4}

    assert {1, 2} <= A
    assert {1, 2} < A
    assert set() <= A

    U = {1, 2, 3, 4, 5}
    assert U - A == {4, 5}

    assert len(power_set({1, 2, 3})) == 8
    assert len(power_set(set())) == 1

    assert jaccard_similarity({1, 2}, {2, 3}) == 1 / 3
    assert jaccard_similarity(set(), set()) == 1.0


test_set_operations()

print("All set operation tests passed.")


# =============================================================================
# 58. MINI APPLICATION: STUDENT COURSE ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("58. MINI APPLICATION: STUDENT COURSE ANALYSIS")
print("=" * 80)

python_students = {
    "Asha",
    "Bharat",
    "Charu",
    "Deepak",
}

sql_students = {
    "Bharat",
    "Charu",
    "Esha",
}

statistics_students = {
    "Asha",
    "Charu",
    "Esha",
}

# Students enrolled in at least one course.

at_least_one_course = (
    python_students
    | sql_students
    | statistics_students
)

# Students enrolled in every course.

all_courses = (
    python_students
    & sql_students
    & statistics_students
)

# Python students who are not studying SQL.

python_only = (
    python_students
    - sql_students
)

# Students studying exactly Python and SQL is not simply a union because
# the desired definition may exclude students taking statistics.
#
# A direct set expression makes the condition explicit.

python_and_sql_not_statistics = (
    (python_students & sql_students)
    - statistics_students
)

print("Students in at least one course:", at_least_one_course)
print("Students in every course:", all_courses)
print("Python but not SQL:", python_only)
print(
    "Python and SQL but not statistics:",
    python_and_sql_not_statistics,
)


# =============================================================================
# 59. MINI APPLICATION: CHANGE DETECTION
# =============================================================================

print("\n" + "=" * 80)
print("59. MINI APPLICATION: CHANGE DETECTION")
print("=" * 80)

previous_version = {
    "authentication",
    "dashboard",
    "reports",
    "settings",
}

current_version = {
    "authentication",
    "dashboard",
    "reports",
    "export",
}

added_features = current_version - previous_version
removed_features = previous_version - current_version
changed_features = previous_version ^ current_version

print("Added:", added_features)
print("Removed:", removed_features)
print("All changed feature names:", changed_features)


# =============================================================================
# 60. SECURITY CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("60. SECURITY CONSIDERATIONS")
print("=" * 80)

# Sets are useful for:
#
# - Permission membership checks
# - Allow lists
# - Deny lists
# - Detecting repeated identifiers
#
# Important security rule:
#
# Membership in a set is not itself a complete authorization system.
# Authorization decisions may require identity verification, contextual checks,
# auditing, expiration handling, and server-side enforcement.

allowed_actions = {
    "read",
    "write",
}

requested_action = "delete"

if requested_action in allowed_actions:
    print("Action permitted by this simple allow list.")
else:
    print("Action rejected by this simple allow list.")


# =============================================================================
# 61. MEMORY CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("61. MEMORY CONSIDERATIONS")
print("=" * 80)

# Sets trade memory for efficient membership operations.
#
# A hash-table-based structure may use more memory than a compact sequence
# containing the same elements.
#
# This trade-off is often worthwhile when:
#
# - Membership checks are frequent.
# - Duplicates must be eliminated.
# - Set algebra is required.
#
# For extremely large data collections, memory usage must be considered.

small_collection = list(range(10))
small_set = set(small_collection)

print("List length:", len(small_collection))
print("Set cardinality:", len(small_set))


# =============================================================================
# 62. COMPREHENSIVE FINAL EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("62. COMPREHENSIVE FINAL EXAMPLE")
print("=" * 80)

# Scenario:
#
# A system contains all registered users.
# Some users have completed training.
# Some users have administrative permissions.
# Some users are inactive.

all_users = {
    "user_1",
    "user_2",
    "user_3",
    "user_4",
    "user_5",
    "user_6",
}

trained_users = {
    "user_1",
    "user_2",
    "user_4",
    "user_5",
}

administrators = {
    "user_2",
    "user_3",
}

inactive_users = {
    "user_5",
    "user_6",
}

# Active users are the complement of inactive users
# relative to all_users.

active_users = all_users - inactive_users

# Active users who completed training.

active_and_trained = active_users & trained_users

# Users who are administrators or trained.

admins_or_trained = administrators | trained_users

# Active administrators who completed training.

qualified_administrators = (
    active_users
    & administrators
    & trained_users
)

# Users who have not completed training.

not_trained = all_users - trained_users

# Users represented in either administrator or training groups,
# but not both.

exclusive_roles = administrators ^ trained_users

print("All users:", all_users)
print("Active users:", active_users)
print("Trained users:", trained_users)
print("Administrators:", administrators)
print("Active and trained:", active_and_trained)
print("Administrators or trained:", admins_or_trained)
print("Qualified administrators:", qualified_administrators)
print("Not trained:", not_trained)
print("Exclusive role membership:", exclusive_roles)


# =============================================================================
# 63. FINAL REFERENCE TABLE
# =============================================================================

print("\n" + "=" * 80)
print("63. FINAL REFERENCE TABLE")
print("=" * 80)

reference_operations = [
    ("Membership", "x in A", "True if x belongs to A"),
    ("Non-membership", "x not in A", "True if x does not belong to A"),
    ("Subset", "A <= B", "Every element of A belongs to B"),
    ("Proper subset", "A < B", "A is a subset of B and A != B"),
    ("Superset", "A >= B", "B is a subset of A"),
    ("Union", "A | B", "Elements in A or B"),
    ("Intersection", "A & B", "Elements common to A and B"),
    ("Difference", "A - B", "Elements in A but not B"),
    ("Symmetric difference", "A ^ B", "Elements in exactly one set"),
    ("Cardinality", "len(A)", "Number of distinct elements"),
    ("Disjointness", "A.isdisjoint(B)", "True when A and B share no elements"),
]

for name, syntax, meaning in reference_operations:
    print(f"{name:22} | {syntax:22} | {meaning}")

print("\nEnd of Sets Fundamentals study script.")
