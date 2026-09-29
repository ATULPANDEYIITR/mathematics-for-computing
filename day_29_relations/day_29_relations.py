"""
Relations: Binary Relations and Relation Properties
====================================================

A self-contained study and demonstration program covering:

1. Relations and ordered pairs
2. Cartesian products
3. Binary relations
4. Domain and range
5. Relation representations
6. Reflexive relations
7. Irreflexive relations
8. Symmetric relations
9. Antisymmetric relations
10. Asymmetric relations
11. Transitive relations
12. Equivalence relations
13. Partial orders
14. Relation composition
15. Inverse relations
16. Closures
17. Matrix and graph representations
18. Property testing
19. Edge cases and counterexamples
20. Algorithmic complexity
21. Practical applications

The program uses finite sets so that the mathematical concepts can be
observed directly through executable Python code.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Optional, Sequence


Element = Any
Pair = tuple[Element, Element]
Relation = set[Pair]


# ---------------------------------------------------------------------------
# 1. Basic set and Cartesian-product operations
# ---------------------------------------------------------------------------

def cartesian_product(left: Iterable[Element],
                       right: Iterable[Element]) -> set[Pair]:
    """Return A x B, the set of all ordered pairs (a, b)."""
    return {(a, b) for a in left for b in right}


def relation_from_pairs(pairs: Iterable[Pair]) -> Relation:
    """
    Normalize an iterable of pairs into a set.

    A binary relation is mathematically a subset of A x B.
    """
    relation: Relation = set()

    for pair in pairs:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError(f"Every relation element must be a 2-tuple: {pair!r}")
        relation.add(pair)

    return relation


def validate_relation(
    relation: Relation,
    domain: set[Element],
    codomain: set[Element],
) -> None:
    """Verify R is a subset of domain x codomain."""
    universe = cartesian_product(domain, codomain)
    invalid_pairs = relation - universe

    if invalid_pairs:
        raise ValueError(
            f"Relation contains pairs outside domain x codomain: {invalid_pairs}"
        )


def relation_domain(relation: Relation) -> set[Element]:
    """Return elements appearing in first position."""
    return {a for a, _ in relation}


def relation_range(relation: Relation) -> set[Element]:
    """Return elements appearing in second position."""
    return {b for _, b in relation}


# ---------------------------------------------------------------------------
# 2. Relation representations
# ---------------------------------------------------------------------------

def relation_as_table(
    relation: Relation,
    domain: Sequence[Element],
    codomain: Sequence[Element],
) -> list[list[int]]:
    """
    Create a Boolean matrix.

    Entry [i][j] is 1 exactly when (domain[i], codomain[j]) belongs to R.
    """
    return [
        [1 if (a, b) in relation else 0 for b in codomain]
        for a in domain
    ]


def print_relation_matrix(
    relation: Relation,
    elements: Sequence[Element],
) -> None:
    """Print the matrix representation of a relation on one finite set."""
    matrix = relation_as_table(relation, elements, elements)

    print("    " + " ".join(f"{str(x):>4}" for x in elements))
    print("    " + "-" * (5 * len(elements)))

    for element, row in zip(elements, matrix):
        print(f"{str(element):>3} | " + " ".join(f"{value:>4}" for value in row))


def relation_as_adjacency_list(
    relation: Relation,
    elements: Iterable[Element],
) -> dict[Element, set[Element]]:
    """Represent a relation as directed adjacency lists."""
    adjacency = {element: set() for element in elements}

    for source, target in relation:
        adjacency.setdefault(source, set()).add(target)

    return adjacency


# ---------------------------------------------------------------------------
# 3. Fundamental relation properties
# ---------------------------------------------------------------------------

def is_reflexive(
    relation: Relation,
    universe: set[Element],
) -> bool:
    """
    R is reflexive on A iff (a, a) belongs to R for every a in A.
    """
    return all((element, element) in relation for element in universe)


def is_irreflexive(
    relation: Relation,
    universe: set[Element],
) -> bool:
    """
    R is irreflexive on A iff (a, a) does not belong to R for every a in A.
    """
    return all((element, element) not in relation for element in universe)


def is_symmetric(relation: Relation) -> bool:
    """
    R is symmetric iff (a, b) in R implies (b, a) in R.
    """
    return all((b, a) in relation for a, b in relation)


def is_antisymmetric(relation: Relation) -> bool:
    """
    R is antisymmetric iff:
        (a, b) in R and (b, a) in R implies a == b.

    Note that antisymmetric does NOT mean "not symmetric".
    """
    return all(
        a == b or (b, a) not in relation
        for a, b in relation
    )


def is_asymmetric(relation: Relation) -> bool:
    """
    R is asymmetric iff (a, b) in R implies (b, a) not in R.

    An asymmetric relation is necessarily irreflexive.
    """
    return all((b, a) not in relation for a, b in relation)


def is_transitive(relation: Relation) -> bool:
    """
    R is transitive iff:
        (a, b) in R and (b, c) in R implies (a, c) in R.
    """
    for a, b in relation:
        for x, c in relation:
            if b == x and (a, c) not in relation:
                return False
    return True


def is_connected(relation: Relation, universe: set[Element]) -> bool:
    """
    A relation is connected/total when for distinct a and b,
    at least one of (a,b) or (b,a) belongs to R.
    """
    for a in universe:
        for b in universe:
            if a != b and (a, b) not in relation and (b, a) not in relation:
                return False
    return True


def property_report(
    relation: Relation,
    universe: set[Element],
) -> dict[str, bool]:
    """Return all major properties in one dictionary."""
    return {
        "reflexive": is_reflexive(relation, universe),
        "irreflexive": is_irreflexive(relation, universe),
        "symmetric": is_symmetric(relation),
        "antisymmetric": is_antisymmetric(relation),
        "asymmetric": is_asymmetric(relation),
        "transitive": is_transitive(relation),
        "connected": is_connected(relation, universe),
    }


# ---------------------------------------------------------------------------
# 4. Relation transformations
# ---------------------------------------------------------------------------

def inverse_relation(relation: Relation) -> Relation:
    """Return R^-1 = {(b, a) : (a, b) in R}."""
    return {(b, a) for a, b in relation}


def compose_relations(
    first: Relation,
    second: Relation,
) -> Relation:
    """
    Return second o first.

    If (a,b) belongs to first and (b,c) belongs to second,
    then (a,c) belongs to the composition.
    """
    result: Relation = set()

    for a, b in first:
        for x, c in second:
            if b == x:
                result.add((a, c))

    return result


def relation_power(relation: Relation, exponent: int) -> Relation:
    """
    Compute R^n using relation composition.

    R^1 = R
    R^2 = R o R
    R^3 = R o R o R
    """
    if exponent < 1:
        raise ValueError("Relation powers require a positive exponent.")

    result = set(relation)

    for _ in range(exponent - 1):
        result = compose_relations(result, relation)

    return result


# ---------------------------------------------------------------------------
# 5. Closures
# ---------------------------------------------------------------------------

def reflexive_closure(
    relation: Relation,
    universe: set[Element],
) -> Relation:
    """Add every missing (a,a) pair."""
    return relation | {(a, a) for a in universe}


def symmetric_closure(relation: Relation) -> Relation:
    """Add every reverse pair required for symmetry."""
    return relation | inverse_relation(relation)


def transitive_closure(
    relation: Relation,
    universe: set[Element],
) -> Relation:
    """
    Compute the transitive closure using repeated composition.

    For a finite relation, repeatedly adding R^2-derived edges reaches
    the smallest transitive relation containing the original relation.
    """
    closure = set(relation)

    changed = True
    while changed:
        changed = False

        new_pairs = {
            (a, c)
            for a, b in closure
            for x, c in closure
            if b == x
        }

        missing = new_pairs - closure

        if missing:
            closure.update(missing)
            changed = True

    return closure


def warshall_transitive_closure(
    relation: Relation,
    elements: Sequence[Element],
) -> Relation:
    """
    Compute transitive closure using Warshall's algorithm.

    Time complexity: O(n^3)
    Space complexity: O(n^2)
    """
    n = len(elements)
    index = {element: i for i, element in enumerate(elements)}
    matrix = [[False] * n for _ in range(n)]

    for a, b in relation:
        matrix[index[a]][index[b]] = True

    for k in range(n):
        for i in range(n):
            if not matrix[i][k]:
                continue

            for j in range(n):
                matrix[i][j] = matrix[i][j] or matrix[k][j]

    return {
        (elements[i], elements[j])
        for i in range(n)
        for j in range(n)
        if matrix[i][j]
    }


# ---------------------------------------------------------------------------
# 6. Equivalence relations and partial orders
# ---------------------------------------------------------------------------

def is_equivalence_relation(
    relation: Relation,
    universe: set[Element],
) -> bool:
    """An equivalence relation is reflexive, symmetric, and transitive."""
    return (
        is_reflexive(relation, universe)
        and is_symmetric(relation)
        and is_transitive(relation)
    )


def is_partial_order(
    relation: Relation,
    universe: set[Element],
) -> bool:
    """
    A partial order is reflexive, antisymmetric, and transitive.
    """
    return (
        is_reflexive(relation, universe)
        and is_antisymmetric(relation)
        and is_transitive(relation)
    )


def equivalence_class(
    relation: Relation,
    element: Element,
    universe: set[Element],
) -> set[Element]:
    """Return the equivalence class [element] if R is an equivalence relation."""
    if not is_equivalence_relation(relation, universe):
        raise ValueError("The relation is not an equivalence relation.")

    return {
        other
        for other in universe
        if (element, other) in relation
    }


def equivalence_classes(
    relation: Relation,
    universe: set[Element],
) -> list[set[Element]]:
    """Partition the universe into equivalence classes."""
    if not is_equivalence_relation(relation, universe):
        raise ValueError("The relation is not an equivalence relation.")

    unclassified = set(universe)
    classes: list[set[Element]] = []

    while unclassified:
        representative = next(iter(unclassified))
        current_class = equivalence_class(relation, representative, universe)
        classes.append(current_class)
        unclassified -= current_class

    return classes


# ---------------------------------------------------------------------------
# 7. Relation construction examples
# ---------------------------------------------------------------------------

def relation_by_rule(
    universe: set[int],
    predicate,
) -> Relation:
    """Construct a relation from a Boolean predicate over ordered pairs."""
    return {
        (a, b)
        for a in universe
        for b in universe
        if predicate(a, b)
    }


def divides_relation(universe: set[int]) -> Relation:
    """Return the relation 'a divides b' on a finite positive integer set."""
    return relation_by_rule(
        universe,
        lambda a, b: b % a == 0,
    )


def less_than_relation(universe: set[int]) -> Relation:
    """Return the strict relation a < b."""
    return relation_by_rule(universe, lambda a, b: a < b)


def less_equal_relation(universe: set[int]) -> Relation:
    """Return the non-strict relation a <= b."""
    return relation_by_rule(universe, lambda a, b: a <= b)


def congruent_modulo_relation(
    universe: set[int],
    modulus: int,
) -> Relation:
    """Return a relation where a R b iff a == b modulo modulus."""
    if modulus <= 0:
        raise ValueError("The modulus must be positive.")

    return relation_by_rule(
        universe,
        lambda a, b: (a - b) % modulus == 0,
    )


# ---------------------------------------------------------------------------
# 8. Counterexample generation
# ---------------------------------------------------------------------------

def reflexivity_counterexample(
    relation: Relation,
    universe: set[Element],
) -> Optional[Pair]:
    """Return a missing diagonal pair when reflexivity fails."""
    for element in universe:
        if (element, element) not in relation:
            return element, element
    return None


def symmetry_counterexample(
    relation: Relation,
) -> Optional[Pair]:
    """Return (a,b) whose reverse pair is missing."""
    for a, b in relation:
        if (b, a) not in relation:
            return a, b
    return None


def antisymmetry_counterexample(
    relation: Relation,
) -> Optional[Pair]:
    """Return distinct mutually related elements."""
    for a, b in relation:
        if a != b and (b, a) in relation:
            return a, b
    return None


def transitivity_counterexample(
    relation: Relation,
) -> Optional[tuple[Element, Element, Element]]:
    """Return a,b,c demonstrating a transitivity failure."""
    for a, b in relation:
        for x, c in relation:
            if b == x and (a, c) not in relation:
                return a, b, c
    return None


# ---------------------------------------------------------------------------
# 9. A reusable Relation class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FiniteRelation:
    """
    Immutable-style wrapper around a finite binary relation.

    The internal relation is copied at construction so callers cannot
    accidentally mutate the original set through the constructor input.
    """

    universe: frozenset[Element]
    pairs: frozenset[Pair]

    def __post_init__(self) -> None:
        invalid = {
            pair for pair in self.pairs
            if pair[0] not in self.universe or pair[1] not in self.universe
        }

        if invalid:
            raise ValueError(f"Invalid pairs for this universe: {invalid}")

    @classmethod
    def create(
        cls,
        universe: Iterable[Element],
        pairs: Iterable[Pair],
    ) -> "FiniteRelation":
        return cls(
            frozenset(universe),
            frozenset(relation_from_pairs(pairs)),
        )

    def reflexive(self) -> bool:
        return is_reflexive(set(self.pairs), set(self.universe))

    def irreflexive(self) -> bool:
        return is_irreflexive(set(self.pairs), set(self.universe))

    def symmetric(self) -> bool:
        return is_symmetric(set(self.pairs))

    def antisymmetric(self) -> bool:
        return is_antisymmetric(set(self.pairs))

    def asymmetric(self) -> bool:
        return is_asymmetric(set(self.pairs))

    def transitive(self) -> bool:
        return is_transitive(set(self.pairs))

    def equivalence(self) -> bool:
        return is_equivalence_relation(
            set(self.pairs),
            set(self.universe),
        )

    def partial_order(self) -> bool:
        return is_partial_order(
            set(self.pairs),
            set(self.universe),
        )

    def inverse(self) -> "FiniteRelation":
        return FiniteRelation.create(
            self.universe,
            inverse_relation(set(self.pairs)),
        )

    def compose(self, other: "FiniteRelation") -> "FiniteRelation":
        if self.universe != other.universe:
            raise ValueError("Composition requires matching universes in this class.")

        return FiniteRelation.create(
            self.universe,
            compose_relations(
                set(self.pairs),
                set(other.pairs),
            ),
        )

    def reflexive_closure(self) -> "FiniteRelation":
        return FiniteRelation.create(
            self.universe,
            reflexive_closure(
                set(self.pairs),
                set(self.universe),
            ),
        )

    def symmetric_closure(self) -> "FiniteRelation":
        return FiniteRelation.create(
            self.universe,
            symmetric_closure(set(self.pairs)),
        )

    def transitive_closure(self) -> "FiniteRelation":
        return FiniteRelation.create(
            self.universe,
            transitive_closure(
                set(self.pairs),
                set(self.universe),
            ),
        )


# ---------------------------------------------------------------------------
# 10. Demonstration helpers
# ---------------------------------------------------------------------------

def print_properties(
    name: str,
    relation: Relation,
    universe: set[Element],
) -> None:
    print(f"\n{name}")
    print("-" * len(name))
    print(f"Relation: {sorted(relation, key=str)}")

    for property_name, value in property_report(relation, universe).items():
        print(f"{property_name:>14}: {value}")


def print_counterexamples(
    relation: Relation,
    universe: set[Element],
) -> None:
    checks = [
        ("reflexivity", reflexivity_counterexample(relation, universe)),
        ("symmetry", symmetry_counterexample(relation)),
        ("antisymmetry", antisymmetry_counterexample(relation)),
        ("transitivity", transitivity_counterexample(relation)),
    ]

    print("\nCounterexamples")
    print("---------------")

    for property_name, counterexample in checks:
        if counterexample is None:
            print(f"{property_name:>14}: none")
        else:
            print(f"{property_name:>14}: {counterexample}")


# ---------------------------------------------------------------------------
# 11. Main educational demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 78)
    print("BINARY RELATIONS AND RELATION PROPERTIES")
    print("=" * 78)

    # -----------------------------------------------------------------------
    # Ordered pairs
    # -----------------------------------------------------------------------
    print("\n1. ORDERED PAIRS AND CARTESIAN PRODUCTS")
    print("---------------------------------------")

    A = {1, 2, 3}
    B = {"x", "y"}

    AxB = cartesian_product(A, B)

    print(f"A = {A}")
    print(f"B = {B}")
    print(f"A x B = {sorted(AxB, key=str)}")
    print("(1, 'x') in A x B:", (1, "x") in AxB)
    print("(1, 2) in A x B:", (1, 2) in AxB)

    # An ordered pair is different from an unordered pair:
    print("\nOrder matters:")
    print("(1, 2) == (2, 1):", (1, 2) == (2, 1))

    # -----------------------------------------------------------------------
    # A binary relation
    # -----------------------------------------------------------------------
    print("\n2. BINARY RELATION")
    print("------------------")

    universe = {1, 2, 3}

    # R = {(1,1), (1,2), (2,2), (2,3), (3,3)}
    R = {
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 3),
        (3, 3),
    }

    validate_relation(R, universe, universe)

    print(f"Universe A = {universe}")
    print(f"R = {sorted(R)}")
    print(f"R is a subset of A x A: {R <= cartesian_product(universe, universe)}")
    print(f"Domain(R): {relation_domain(R)}")
    print(f"Range(R): {relation_range(R)}")

    # -----------------------------------------------------------------------
    # Matrix representation
    # -----------------------------------------------------------------------
    print("\n3. MATRIX REPRESENTATION")
    print("-------------------------")
    print_relation_matrix(R, sorted(universe))

    print("\nInterpretation:")
    print("A 1 at row a and column b means (a,b) belongs to R.")
    print("A 0 means the ordered pair is absent.")

    # -----------------------------------------------------------------------
    # Directed graph representation
    # -----------------------------------------------------------------------
    print("\n4. DIRECTED-GRAPH REPRESENTATION")
    print("---------------------------------")

    adjacency = relation_as_adjacency_list(R, universe)

    for source in sorted(adjacency):
        print(f"{source} -> {sorted(adjacency[source])}")

    # -----------------------------------------------------------------------
    # Core properties
    # -----------------------------------------------------------------------
    print("\n5. CORE RELATION PROPERTIES")
    print("---------------------------")

    print_properties("Example relation R", R, universe)
    print_counterexamples(R, universe)

    print(
        "\nImportant distinction:"
        "\n- Symmetric means reverse pairs must also exist."
        "\n- Antisymmetric permits both directions only when the elements are equal."
        "\n- Therefore a relation can be both symmetric and antisymmetric."
    )

    identity = {(x, x) for x in universe}
    print_properties("Identity relation I", identity, universe)

    # -----------------------------------------------------------------------
    # Standard mathematical examples
    # -----------------------------------------------------------------------
    print("\n6. STANDARD EXAMPLES")
    print("--------------------")

    less_than = less_than_relation(universe)
    less_equal = less_equal_relation(universe)
    divides = divides_relation({1, 2, 3, 4, 6})

    print_properties("< relation", less_than, universe)
    print_properties("<= relation", less_equal, universe)
    print_properties("Divides relation", divides, {1, 2, 3, 4, 6})

    # -----------------------------------------------------------------------
    # Logical relationships among properties
    # -----------------------------------------------------------------------
    print("\n7. LOGICAL RELATIONSHIPS")
    print("------------------------")

    print("If a relation is asymmetric, it is always irreflexive.")
    print(
        "Verified for <:",
        is_asymmetric(less_than),
        "and",
        is_irreflexive(less_than, universe),
    )

    print("\nSymmetric does not imply reflexive:")
    symmetric_non_reflexive = {(1, 2), (2, 1)}
    print_properties(
        "Symmetric but non-reflexive relation",
        symmetric_non_reflexive,
        universe,
    )

    print("\nAntisymmetric does not mean non-symmetric:")
    print_properties("Identity relation", identity, universe)

    # -----------------------------------------------------------------------
    # Equivalence relation
    # -----------------------------------------------------------------------
    print("\n8. EQUIVALENCE RELATIONS")
    print("------------------------")

    modulo_universe = set(range(8))
    modulo_relation = congruent_modulo_relation(modulo_universe, 3)

    print_properties(
        "Congruence modulo 3",
        modulo_relation,
        modulo_universe,
    )

    print(
        "\nIs equivalence relation:",
        is_equivalence_relation(modulo_relation, modulo_universe),
    )

    classes = equivalence_classes(modulo_relation, modulo_universe)

    print("Equivalence classes:")
    for current_class in sorted(classes, key=lambda values: min(values)):
        print(" ", sorted(current_class))

    # -----------------------------------------------------------------------
    # Partial order
    # -----------------------------------------------------------------------
    print("\n9. PARTIAL ORDERS")
    print("-----------------")

    divisibility_universe = {1, 2, 3, 4, 6, 12}
    divisibility = divides_relation(divisibility_universe)

    print_properties(
        "Divisibility relation",
        divisibility,
        divisibility_universe,
    )

    print(
        "\nIs partial order:",
        is_partial_order(divisibility, divisibility_universe),
    )

    print(
        "Is connected:",
        is_connected(divisibility, divisibility_universe),
        "(false means some elements are incomparable)",
    )

    # -----------------------------------------------------------------------
    # Inverse
    # -----------------------------------------------------------------------
    print("\n10. INVERSE RELATIONS")
    print("---------------------")

    directed = {(1, 2), (2, 3), (3, 1)}

    print("R:", sorted(directed))
    print("R^-1:", sorted(inverse_relation(directed)))

    # -----------------------------------------------------------------------
    # Composition
    # -----------------------------------------------------------------------
    print("\n11. RELATION COMPOSITION")
    print("------------------------")

    R1 = {
        ("Alice", "Python"),
        ("Bob", "C++"),
        ("Carol", "Python"),
    }

    R2 = {
        ("Python", "Programming"),
        ("C++", "Programming"),
    }

    composition = compose_relations(R1, R2)

    print("R1:", sorted(R1))
    print("R2:", sorted(R2))
    print("R2 o R1:", sorted(composition))

    # -----------------------------------------------------------------------
    # Powers
    # -----------------------------------------------------------------------
    print("\n12. RELATION POWERS")
    print("-------------------")

    graph_relation = {
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
    }

    print("R:", sorted(graph_relation))
    print("R^2:", sorted(relation_power(graph_relation, 2)))
    print("R^3:", sorted(relation_power(graph_relation, 3)))

    # -----------------------------------------------------------------------
    # Closures
    # -----------------------------------------------------------------------
    print("\n13. CLOSURES")
    print("------------")

    incomplete = {(1, 2), (2, 3)}

    print("Original:", sorted(incomplete))
    print(
        "Reflexive closure:",
        sorted(reflexive_closure(incomplete, universe)),
    )
    print(
        "Symmetric closure:",
        sorted(symmetric_closure(incomplete)),
    )
    print(
        "Transitive closure:",
        sorted(transitive_closure(incomplete, universe)),
    )

    # -----------------------------------------------------------------------
    # Warshall algorithm
    # -----------------------------------------------------------------------
    print("\n14. WARSHALL'S ALGORITHM")
    print("-----------------------")

    warshall_result = warshall_transitive_closure(
        incomplete,
        sorted(universe),
    )

    repeated_result = transitive_closure(incomplete, universe)

    print("Repeated-composition closure:", sorted(repeated_result))
    print("Warshall closure:", sorted(warshall_result))
    print("Both methods agree:", warshall_result == repeated_result)

    # -----------------------------------------------------------------------
    # Class-based API
    # -----------------------------------------------------------------------
    print("\n15. OBJECT-ORIENTED RELATION MODEL")
    print("----------------------------------")

    finite_relation = FiniteRelation.create(
        universe,
        R,
    )

    print("Reflexive:", finite_relation.reflexive())
    print("Symmetric:", finite_relation.symmetric())
    print("Antisymmetric:", finite_relation.antisymmetric())
    print("Transitive:", finite_relation.transitive())
    print("Equivalence:", finite_relation.equivalence())
    print("Partial order:", finite_relation.partial_order())

    # -----------------------------------------------------------------------
    # Practical application: access control
    # -----------------------------------------------------------------------
    print("\n16. PRACTICAL APPLICATION: ACCESS CONTROL")
    print("------------------------------------------")

    users = {"Alice", "Bob", "Carol"}
    resources = {"Database", "Reports", "Dashboard"}

    access_relation = {
        ("Alice", "Database"),
        ("Alice", "Reports"),
        ("Bob", "Reports"),
        ("Carol", "Dashboard"),
    }

    print("Users:", users)
    print("Resources:", resources)
    print("Access relation:", sorted(access_relation))

    print("\nAlice can access Database:",
          ("Alice", "Database") in access_relation)
    print("Bob can access Dashboard:",
          ("Bob", "Dashboard") in access_relation)

    # This is a relation from Users to Resources, not a relation on one set.
    validate_relation(access_relation, users, resources)

    # -----------------------------------------------------------------------
    # Practical application: prerequisite graph
    # -----------------------------------------------------------------------
    print("\n17. PRACTICAL APPLICATION: PREREQUISITES")
    print("-----------------------------------------")

    prerequisites = {
        ("Programming", "Data Structures"),
        ("Data Structures", "Algorithms"),
        ("Algorithms", "Machine Learning"),
    }

    print("Direct prerequisites:", sorted(prerequisites))

    all_dependencies = transitive_closure(
        prerequisites,
        {
            "Programming",
            "Data Structures",
            "Algorithms",
            "Machine Learning",
        },
    )

    print("Reachable dependency relationships:")
    for pair in sorted(all_dependencies):
        print(" ", pair)

    print(
        "\nThe transitive closure exposes indirect dependencies, "
        "such as Programming -> Machine Learning."
    )

    # -----------------------------------------------------------------------
    # Edge cases
    # -----------------------------------------------------------------------
    print("\n18. EDGE CASES")
    print("--------------")

    empty_relation: Relation = set()
    empty_universe: set[int] = set()

    print("Empty relation on non-empty universe:")
    print(
        "  Reflexive:",
        is_reflexive(empty_relation, universe),
        "(false because diagonal pairs are missing)",
    )
    print(
        "  Symmetric:",
        is_symmetric(empty_relation),
        "(true vacuously)",
    )
    print(
        "  Antisymmetric:",
        is_antisymmetric(empty_relation),
        "(true vacuously)",
    )
    print(
        "  Transitive:",
        is_transitive(empty_relation),
        "(true vacuously)",
    )

    print("\nEmpty relation on empty universe:")
    print(
        "  Reflexive:",
        is_reflexive(empty_relation, empty_universe),
    )
    print(
        "  Symmetric:",
        is_symmetric(empty_relation),
    )
    print(
        "  Transitive:",
        is_transitive(empty_relation),
    )

    print("\nA singleton identity relation:")
    singleton = {(42, 42)}
    print_properties("Singleton", singleton, {42})

    # -----------------------------------------------------------------------
    # Assertions as executable mathematical checks
    # -----------------------------------------------------------------------
    print("\n19. EXECUTABLE ASSERTIONS")
    print("-------------------------")

    assert is_reflexive(identity, universe)
    assert is_symmetric(identity)
    assert is_antisymmetric(identity)
    assert is_transitive(identity)

    assert is_irreflexive(less_than, universe)
    assert is_asymmetric(less_than)
    assert is_transitive(less_than)

    assert is_reflexive(less_equal, universe)
    assert is_antisymmetric(less_equal)
    assert is_transitive(less_equal)

    assert is_equivalence_relation(modulo_relation, modulo_universe)
    assert is_partial_order(divisibility, divisibility_universe)

    assert warshall_result == repeated_result

    print("All mathematical assertions passed.")

    # -----------------------------------------------------------------------
    # Complexity discussion through actual measurements of operation sizes
    # -----------------------------------------------------------------------
    print("\n20. PERFORMANCE CONSIDERATIONS")
    print("------------------------------")

    print(
        "For a relation on n elements, the universe A x A contains n^2 "
        "possible ordered pairs."
    )

    print(
        "Reflexivity check: O(n), assuming set membership is O(1) average."
    )
    print(
        "Symmetry check: O(|R|), assuming set membership is O(1) average."
    )
    print(
        "Antisymmetry check: O(|R|), assuming set membership is O(1) average."
    )
    print(
        "The straightforward transitivity check can take O(|R|^2)."
    )
    print(
        "Warshall's transitive-closure algorithm takes O(n^3) time and "
        "O(n^2) space."
    )

    # -----------------------------------------------------------------------
    # Security/design considerations
    # -----------------------------------------------------------------------
    print("\n21. SECURITY AND DESIGN CONSIDERATIONS")
    print("---------------------------------------")

    print(
        "Relations used for authorization should be validated against "
        "known users/resources."
    )
    print(
        "Do not treat an arbitrary pair supplied by a client as valid "
        "without checking the allowed domain and codomain."
    )
    print(
        "For dependency or reachability systems, transitive closure can "
        "reveal indirect relationships that are not obvious from direct edges."
    )
    print(
        "For large systems, storing every pair in a dense matrix may be "
        "impractical; sparse adjacency structures are often preferable."
    )

    print("\n" + "=" * 78)
    print("END OF RELATION STUDY")
    print("=" * 78)


if __name__ == "__main__":
    main()
