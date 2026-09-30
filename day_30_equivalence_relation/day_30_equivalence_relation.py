from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, Generic, Hashable, Iterable, TypeVar


T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)


class EquivalenceRelation(Generic[T]):
    """
    A finite-set model of an equivalence relation.

    A relation R on a set S is an equivalence relation when it is:
    reflexive:  x R x
    symmetric: x R y implies y R x
    transitive: x R y and y R z imply x R z

    This class can either receive an explicit relation predicate or construct
    one from a key function. A key function is especially useful because
    equality of keys immediately gives a canonical equivalence relation.
    """

    def __init__(
        self,
        elements: Iterable[T],
        relation: Callable[[T, T], bool],
        name: str = "R",
    ) -> None:
        self.elements = list(dict.fromkeys(elements))
        self.relation = relation
        self.name = name

    def pairs(self) -> set[tuple[T, T]]:
        """Return every related ordered pair in the finite domain."""
        return {
            (x, y)
            for x in self.elements
            for y in self.elements
            if self.relation(x, y)
        }

    def is_reflexive(self) -> bool:
        return all(self.relation(x, x) for x in self.elements)

    def is_symmetric(self) -> bool:
        return all(
            not self.relation(x, y) or self.relation(y, x)
            for x in self.elements
            for y in self.elements
        )

    def is_transitive(self) -> bool:
        for x in self.elements:
            for y in self.elements:
                if self.relation(x, y):
                    for z in self.elements:
                        if self.relation(y, z) and not self.relation(x, z):
                            return False
        return True

    def is_equivalence(self) -> bool:
        return (
            self.is_reflexive()
            and self.is_symmetric()
            and self.is_transitive()
        )

    def equivalence_class(self, element: T) -> frozenset[T]:
        if element not in self.elements:
            raise ValueError(f"{element!r} is not in the relation's domain.")
        return frozenset(
            other for other in self.elements if self.relation(element, other)
        )

    def classes(self) -> set[frozenset[T]]:
        if not self.is_equivalence():
            raise ValueError(
                f"{self.name} is not an equivalence relation, so its "
                "equivalence classes do not form a valid partition."
            )
        return {
            self.equivalence_class(element)
            for element in self.elements
        }


def relation_from_key(
    elements: Iterable[T],
    key: Callable[[T], U],
    name: str = "R",
) -> EquivalenceRelation[T]:
    """
    Build R where x R y exactly when key(x) == key(y).

    This is a practical construction of an equivalence relation:
    equality of keys is reflexive, symmetric, and transitive.
    """
    items = list(dict.fromkeys(elements))
    return EquivalenceRelation(
        items,
        lambda x, y: key(x) == key(y),
        name,
    )


def print_relation_report(relation: EquivalenceRelation[T]) -> None:
    print(f"\n=== {relation.name}: relation analysis ===")
    print(f"Domain: {relation.elements}")
    print(f"Reflexive: {relation.is_reflexive()}")
    print(f"Symmetric: {relation.is_symmetric()}")
    print(f"Transitive: {relation.is_transitive()}")
    print(f"Equivalence relation: {relation.is_equivalence()}")

    if relation.is_equivalence():
        print("Equivalence classes:")
        for class_set in sorted(
            relation.classes(),
            key=lambda c: (len(c), repr(sorted(c, key=repr))),
        ):
            print(f"  {set(class_set)}")


def demonstrate_basic_relation() -> None:
    """
    Demonstrate congruence modulo n.

    On integers, x ≡ y (mod n) exactly when n divides x-y.
    The finite domain lets us inspect all relevant pairs and classes.
    """
    domain = list(range(-8, 9))
    modulus = 4

    relation = EquivalenceRelation(
        domain,
        lambda x, y: (x - y) % modulus == 0,
        name=f"congruence modulo {modulus}",
    )

    print_relation_report(relation)

    print("\nSpecific class calculations:")
    for representative in [-7, -2, 0, 1, 6]:
        print(
            f"[{representative}]_{modulus} = "
            f"{sorted(relation.equivalence_class(representative))}"
        )


def demonstrate_key_based_relation() -> None:
    """
    Partition employee records by department.

    Employees are equivalent exactly when they have the same department.
    The equivalence class therefore represents a department group.
    """
    employees = [
        {"id": 101, "name": "Asha", "department": "Engineering"},
        {"id": 102, "name": "Ravi", "department": "Finance"},
        {"id": 103, "name": "Mina", "department": "Engineering"},
        {"id": 104, "name": "Omar", "department": "Research"},
        {"id": 105, "name": "Isha", "department": "Finance"},
        {"id": 106, "name": "Noah", "department": "Research"},
    ]

    # Dictionaries are not hashable, so use employee IDs as the domain and
    # keep the records separately.
    records = {employee["id"]: employee for employee in employees}

    relation = relation_from_key(
        records.keys(),
        key=lambda employee_id: records[employee_id]["department"],
        name="same-department",
    )

    print("\n=== Same-department equivalence relation ===")
    for class_set in sorted(relation.classes(), key=lambda c: min(c)):
        department = records[min(class_set)]["department"]
        members = [records[employee_id]["name"] for employee_id in sorted(class_set)]
        print(f"{department}: {members}")


def demonstrate_partition_to_relation() -> None:
    """
    A partition determines an equivalence relation.

    If P is a partition of S, define x R y exactly when x and y belong to
    the same block of P. The partition blocks then become the equivalence
    classes of R.
    """
    domain = set(range(1, 13))
    partition = [
        frozenset({1, 4, 7, 10}),
        frozenset({2, 5, 8, 11}),
        frozenset({3, 6, 9, 12}),
    ]

    # Validate the partition before turning it into a relation.
    flattened = set().union(*partition)
    pairwise_disjoint = all(
        partition[i].isdisjoint(partition[j])
        for i in range(len(partition))
        for j in range(i + 1, len(partition))
    )

    if flattened != domain or not pairwise_disjoint:
        raise ValueError("The supplied family is not a partition.")

    def same_block(x: int, y: int) -> bool:
        return any(x in block and y in block for block in partition)

    relation = EquivalenceRelation(
        sorted(domain),
        same_block,
        name="relation induced by partition",
    )

    print("\n=== Partition -> equivalence relation ===")
    print(f"Partition: {[sorted(block) for block in partition]}")
    print(f"Is equivalence relation: {relation.is_equivalence()}")

    for x, y in [(1, 7), (1, 2), (5, 11), (9, 12)]:
        print(f"{x} R {y}: {relation.relation(x, y)}")


def validate_partition(
    universe: set[T],
    blocks: Iterable[Iterable[T]],
) -> tuple[bool, str]:
    """
    Validate the defining properties of a partition.

    A partition must consist of nonempty blocks whose union is the universe
    and whose distinct blocks are pairwise disjoint.
    """
    normalized = [frozenset(block) for block in blocks]

    if any(not block for block in normalized):
        return False, "A partition cannot contain an empty block."

    if any(not block <= universe for block in normalized):
        return False, "A block contains an element outside the universe."

    for index, left in enumerate(normalized):
        for right in normalized[index + 1:]:
            if left & right:
                return False, "Distinct blocks must be disjoint."

    if set().union(*normalized) != universe:
        return False, "The blocks must cover the entire universe."

    return True, "Valid partition."


def demonstrate_invalid_relations() -> None:
    """
    Show why all three equivalence properties are necessary.

    The relation x R y iff x < y is neither reflexive nor symmetric.
    The relation x R y iff x and y have different parity is symmetric but
    not reflexive, and therefore cannot define equivalence classes.
    """
    domain = [1, 2, 3]

    less_than = EquivalenceRelation(
        domain,
        lambda x, y: x < y,
        name="strict less-than",
    )

    different_parity = EquivalenceRelation(
        domain,
        lambda x, y: (x % 2) != (y % 2),
        name="different parity",
    )

    print_relation_report(less_than)
    print_relation_report(different_parity)


@dataclass(frozen=True)
class Product:
    product_id: int
    name: str
    category: str
    price: float


def demonstrate_quotient_structure() -> None:
    """
    Construct a quotient set from products identified by category.

    The quotient S/R is the set of equivalence classes rather than the
    original individual products. A canonical representative can be chosen
    for display, but the quotient element itself is the entire class.
    """
    products = [
        Product(1, "Laptop", "electronics", 1200.0),
        Product(2, "Monitor", "electronics", 350.0),
        Product(3, "Desk", "furniture", 500.0),
        Product(4, "Chair", "furniture", 180.0),
        Product(5, "Python Book", "books", 45.0),
        Product(6, "Database Book", "books", 60.0),
    ]

    by_id = {product.product_id: product for product in products}

    relation = relation_from_key(
        by_id.keys(),
        key=lambda product_id: by_id[product_id].category,
        name="same-product-category",
    )

    quotient_set = relation.classes()

    print("\n=== Quotient structure S/R ===")
    print(f"Original set size: {len(products)}")
    print(f"Quotient set size: {len(quotient_set)}")

    for quotient_element in sorted(
        quotient_set,
        key=lambda class_set: by_id[min(class_set)].category,
    ):
        representative_id = min(quotient_element)
        representative = by_id[representative_id]
        names = [by_id[item].name for item in sorted(quotient_element)]

        print(
            f"Class [{representative.name}] = {names}; "
            f"category={representative.category!r}"
        )


def demonstrate_well_defined_quotient_operation() -> None:
    """
    Demonstrate a well-defined operation on Z/nZ.

    Addition of residue classes is defined by:
        [a] + [b] = [a+b]

    The definition is independent of representatives because if a ≡ a'
    and b ≡ b' modulo n, then a+b ≡ a'+b' modulo n.
    """
    modulus = 5

    def class_of(value: int) -> int:
        return value % modulus

    def quotient_add(a: int, b: int) -> int:
        return class_of(a + b)

    def quotient_multiply(a: int, b: int) -> int:
        return class_of(a * b)

    print("\n=== Well-defined operations on Z/5Z ===")

    pairs = [
        (2, 8),
        (-3, 12),
        (7, 17),
    ]

    for a, a_prime in pairs:
        same_class = class_of(a) == class_of(a_prime)
        print(f"{a} and {a_prime}: same class = {same_class}")

    first_representatives = (2, 7)
    second_representatives = (12, 17)

    addition_one = quotient_add(*first_representatives)
    addition_two = quotient_add(*second_representatives)
    multiplication_one = quotient_multiply(*first_representatives)
    multiplication_two = quotient_multiply(*second_representatives)

    print(
        f"[2] + [12] = [{addition_one}], "
        f"[7] + [17] = [{addition_two}]"
    )
    print(
        f"[2] * [12] = [{multiplication_one}], "
        f"[7] * [17] = [{multiplication_two}]"
    )

    if addition_one != addition_two or multiplication_one != multiplication_two:
        raise AssertionError("Quotient operation was not well-defined.")


def demonstrate_partition_validation() -> None:
    universe = set(range(1, 9))

    valid = [
        {1, 2},
        {3, 4, 5},
        {6, 7, 8},
    ]

    invalid_overlap = [
        {1, 2, 3},
        {3, 4},
        {5, 6, 7, 8},
    ]

    invalid_missing = [
        {1, 2},
        {3, 4},
        {5, 6},
    ]

    print("\n=== Partition validation ===")
    for label, candidate in [
        ("valid", valid),
        ("overlapping", invalid_overlap),
        ("missing element", invalid_missing),
    ]:
        result, message = validate_partition(universe, candidate)
        print(f"{label}: {result} - {message}")


def demonstrate_union_find_equivalence_classes() -> None:
    """
    Use a disjoint-set union structure to build equivalence classes efficiently.

    Union-find is useful when equivalence classes are created incrementally.
    Path compression and union by rank make repeated connectivity queries
    highly efficient in practical workloads.
    """

    class DisjointSet:
        def __init__(self, elements: Iterable[int]) -> None:
            self.parent = {element: element for element in elements}
            self.rank = {element: 0 for element in self.parent}

        def find(self, element: int) -> int:
            if element not in self.parent:
                raise KeyError(f"Unknown element: {element}")

            # Path compression makes future find operations faster.
            if self.parent[element] != element:
                self.parent[element] = self.find(self.parent[element])
            return self.parent[element]

        def union(self, left: int, right: int) -> bool:
            left_root = self.find(left)
            right_root = self.find(right)

            if left_root == right_root:
                return False

            # Union by rank keeps the representative tree shallow.
            if self.rank[left_root] < self.rank[right_root]:
                self.parent[left_root] = right_root
            elif self.rank[left_root] > self.rank[right_root]:
                self.parent[right_root] = left_root
            else:
                self.parent[right_root] = left_root
                self.rank[left_root] += 1

            return True

        def classes(self) -> dict[int, set[int]]:
            groups: dict[int, set[int]] = defaultdict(set)
            for element in self.parent:
                groups[self.find(element)].add(element)
            return dict(groups)

    dsu = DisjointSet(range(1, 11))

    equivalences = [
        (1, 4),
        (4, 7),
        (2, 5),
        (5, 8),
        (3, 6),
        (6, 9),
        (9, 10),
    ]

    for left, right in equivalences:
        dsu.union(left, right)

    print("\n=== Incrementally constructed equivalence classes ===")
    for representative, members in sorted(dsu.classes().items()):
        print(f"Representative {representative}: {sorted(members)}")

    print(f"1 and 7 equivalent: {dsu.find(1) == dsu.find(7)}")
    print(f"2 and 6 equivalent: {dsu.find(2) == dsu.find(6)}")


def demonstrate_homomorphism_and_quotient_mapping() -> None:
    """
    Illustrate the quotient map q: Z -> Z/nZ.

    q sends an integer to its residue class. The output uses residue
    representatives 0,...,n-1, which are labels for quotient elements,
    not the quotient elements themselves.
    """
    modulus = 3
    integers = list(range(-5, 7))

    quotient_map = lambda value: value % modulus

    print("\n=== Quotient map q: Z -> Z/3Z ===")
    for value in integers:
        print(f"q({value}) = [{quotient_map(value)}]")

    print("\nCompatibility with addition:")
    for a, b in [(-4, 7), (2, 5), (8, -2)]:
        left = quotient_map(a + b)
        right = (quotient_map(a) + quotient_map(b)) % modulus
        print(f"q({a}+{b}) = {left}; q({a})+q({b}) = {right}")
        assert left == right


def demonstrate_quotient_vs_representative() -> None:
    """
    Clarify the distinction between an equivalence class and a representative.

    The class [2] modulo 5 contains infinitely many integers in Z, while 2
    is merely one representative of that class. In a finite display we show
    several representatives rather than pretending that the class is finite.
    """
    modulus = 5
    representative = 2

    visible_members = [
        value
        for value in range(-20, 21)
        if (value - representative) % modulus == 0
    ]

    print("\n=== Class versus representative ===")
    print(f"Representative: {representative}")
    print(f"Visible members of [{representative}] modulo {modulus}: {visible_members}")
    print(
        "The quotient element is the entire equivalence class; "
        "the integer 2 is only one representative."
    )


def main() -> None:
    print("EQUIVALENCE RELATIONS, CLASSES, PARTITIONS, AND QUOTIENT STRUCTURES")
    print("=" * 76)

    demonstrate_basic_relation()
    demonstrate_key_based_relation()
    demonstrate_partition_to_relation()
    demonstrate_partition_validation()
    demonstrate_invalid_relations()
    demonstrate_quotient_structure()
    demonstrate_well_defined_quotient_operation()
    demonstrate_union_find_equivalence_classes()
    demonstrate_homomorphism_and_quotient_mapping()
    demonstrate_quotient_vs_representative()

    print("\n=== Verification checks ===")
    relation = EquivalenceRelation(
        range(10),
        lambda x, y: (x - y) % 3 == 0,
        name="modulo-3 congruence",
    )

    assert relation.is_reflexive()
    assert relation.is_symmetric()
    assert relation.is_transitive()
    assert len(relation.classes()) == 3

    valid, _ = validate_partition(
        set(range(1, 7)),
        [{1, 2}, {3}, {4, 5, 6}],
    )
    assert valid

    print("All core equivalence-relation checks passed.")


if __name__ == "__main__":
    main()
