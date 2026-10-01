from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Poset:
    """Finite partially ordered set represented by an explicit <= relation."""

    elements: FrozenSet[str]
    relation: FrozenSet[Tuple[str, str]]

    def __post_init__(self) -> None:
        expected = {(x, x) for x in self.elements}
        if not expected.issubset(self.relation):
            missing = sorted(expected - set(self.relation))
            raise ValueError(f"Relation is not reflexive; missing pairs: {missing}")

        for left, right in self.relation:
            if left not in self.elements or right not in self.elements:
                raise ValueError(
                    f"Relation contains an element outside the poset: {(left, right)}"
                )

        if any(
            (b, a) not in self.relation
            for a, b in self.relation
            if a != b
        ):
            if not self.is_antisymmetric():
                raise ValueError("Relation is not antisymmetric.")

        if not self.is_transitive():
            raise ValueError("Relation is not transitive.")

    def leq(self, a: str, b: str) -> bool:
        return (a, b) in self.relation

    def is_reflexive(self) -> bool:
        return all((x, x) in self.relation for x in self.elements)

    def is_antisymmetric(self) -> bool:
        return all(
            a == b or (b, a) not in self.relation
            for a, b in self.relation
        )

    def is_transitive(self) -> bool:
        for a, b in self.relation:
            for c in self.elements:
                if (b, c) in self.relation and (a, c) not in self.relation:
                    return False
        return True

    def comparable(self, a: str, b: str) -> bool:
        return self.leq(a, b) or self.leq(b, a)

    def comparable_pairs(self) -> List[Tuple[str, str]]:
        pairs = []
        for a, b in combinations(sorted(self.elements), 2):
            if self.comparable(a, b):
                pairs.append((a, b))
        return pairs

    def incomparable_pairs(self) -> List[Tuple[str, str]]:
        pairs = []
        for a, b in combinations(sorted(self.elements), 2):
            if not self.comparable(a, b):
                pairs.append((a, b))
        return pairs

    def strict_less(self, a: str, b: str) -> bool:
        return a != b and self.leq(a, b)

    def predecessors(self, x: str) -> Set[str]:
        return {y for y in self.elements if self.strict_less(y, x)}

    def successors(self, x: str) -> Set[str]:
        return {y for y in self.elements if self.strict_less(x, y)}

    def minimal_elements(self) -> Set[str]:
        return {
            x for x in self.elements
            if not any(self.strict_less(y, x) for y in self.elements)
        }

    def maximal_elements(self) -> Set[str]:
        return {
            x for x in self.elements
            if not any(self.strict_less(x, y) for y in self.elements)
        }

    def least_element(self) -> Optional[str]:
        candidates = [
            x for x in self.elements
            if all(self.leq(x, y) for y in self.elements)
        ]
        return next(iter(candidates), None)

    def greatest_element(self) -> Optional[str]:
        candidates = [
            x for x in self.elements
            if all(self.leq(y, x) for y in self.elements)
        ]
        return next(iter(candidates), None)

    def is_chain(self, subset: Iterable[str]) -> bool:
        values = set(subset)
        if not values.issubset(self.elements):
            return False
        return all(self.comparable(a, b) for a, b in combinations(values, 2))

    def is_antichain(self, subset: Iterable[str]) -> bool:
        values = set(subset)
        if not values.issubset(self.elements):
            return False
        return all(not self.comparable(a, b) for a, b in combinations(values, 2))

    def cover_relations(self) -> Set[Tuple[str, str]]:
        """
        Return x ⋖ y exactly when x < y and there is no z with x < z < y.

        Hasse diagrams contain cover relations rather than every transitive
        relation, which removes edges implied by longer paths.
        """
        covers: Set[Tuple[str, str]] = set()

        for x, y in self.relation:
            if not self.strict_less(x, y):
                continue

            has_intermediate = any(
                z != x
                and z != y
                and self.strict_less(x, z)
                and self.strict_less(z, y)
                for z in self.elements
            )

            if not has_intermediate:
                covers.add((x, y))

        return covers

    def topological_layers(self) -> List[List[str]]:
        """
        Layer the Hasse diagram from minimal elements upward.

        Removing each current set of minimal remaining elements produces
        levels useful for textual Hasse-diagram layouts.
        """
        remaining = set(self.elements)
        layers: List[List[str]] = []

        while remaining:
            layer = sorted(
                x for x in remaining
                if not any(
                    y in remaining and self.strict_less(y, x)
                    for y in remaining
                )
            )
            if not layer:
                raise ValueError("The relation does not define a finite DAG.")
            layers.append(layer)
            remaining -= set(layer)

        return layers

    def all_chains(self) -> List[Tuple[str, ...]]:
        """Enumerate every non-empty chain without duplicate subsets."""
        chains: Set[FrozenSet[str]] = set()

        for size in range(1, len(self.elements) + 1):
            for candidate in combinations(sorted(self.elements), size):
                if self.is_chain(candidate):
                    chains.add(frozenset(candidate))

        result = []
        for chain in chains:
            ordered = tuple(
                sorted(chain, key=lambda x: self.rank_key(x))
            )
            result.append(ordered)

        return sorted(result, key=lambda c: (len(c), c))

    def all_antichains(self) -> List[Tuple[str, ...]]:
        """Enumerate every non-empty antichain."""
        result: List[Tuple[str, ...]] = []

        for size in range(1, len(self.elements) + 1):
            for candidate in combinations(sorted(self.elements), size):
                if self.is_antichain(candidate):
                    result.append(candidate)

        return result

    def maximum_chain(self) -> Tuple[str, ...]:
        chains = self.all_chains()
        return max(chains, key=lambda c: (len(c), c))

    def maximum_antichain(self) -> Tuple[str, ...]:
        antichains = self.all_antichains()
        return max(antichains, key=lambda a: (len(a), a))

    def rank_key(self, x: str) -> Tuple[int, str]:
        """
        Rank an element by the length of a longest chain ending at x.

        This is useful for examples where the poset is graded or nearly
        graded. The computation works for any finite poset.
        """
        memo: Dict[str, int] = {}

        def depth(node: str) -> int:
            if node in memo:
                return memo[node]

            lower = [
                y for y in self.elements
                if self.strict_less(y, node)
            ]

            memo[node] = 0 if not lower else 1 + max(depth(y) for y in lower)
            return memo[node]

        return depth(x), x

    def textual_hasse_diagram(self) -> str:
        """
        Produce a compact textual representation.

        Every displayed edge is a cover relation. The output is not intended
        to replace a graphical drawing, but it makes the defining relation
        explicit and reproducible in a terminal.
        """
        lines = ["Hasse diagram edges (lower element -> upper element):"]
        for lower, upper in sorted(
            self.cover_relations(),
            key=lambda pair: (self.rank_key(pair[0]), pair)
        ):
            lines.append(f"  {lower} -> {upper}")

        lines.append("")
        lines.append("Layers:")
        for rank, layer in enumerate(self.topological_layers()):
            lines.append(f"  level {rank}: {'   '.join(layer)}")

        return "\n".join(lines)


def relation_from_divisibility(values: Iterable[int]) -> Poset:
    numbers = sorted(set(values))
    elements = frozenset(str(x) for x in numbers)

    relation = {
        (str(a), str(b))
        for a in numbers
        for b in numbers
        if b % a == 0
    }

    return Poset(elements, frozenset(relation))


def relation_from_subset_inclusion(
    universe: str,
    subsets: Iterable[Iterable[str]],
) -> Poset:
    normalized = {
        frozenset(subset)
        for subset in subsets
    }

    if any(not subset.issubset(set(universe)) for subset in normalized):
        raise ValueError("A subset contains an element outside the universe.")

    elements = frozenset(
        "{" + "".join(sorted(subset)) + "}" if subset else "∅"
        for subset in normalized
    )

    label_to_set = {
        ("{" + "".join(sorted(subset)) + "}" if subset else "∅"): subset
        for subset in normalized
    }

    relation = {
        (a, b)
        for a, set_a in label_to_set.items()
        for b, set_b in label_to_set.items()
        if set_a.issubset(set_b)
    }

    return Poset(elements, frozenset(relation))


def demonstrate_axioms() -> None:
    print("PARTIAL ORDER AXIOMS")

    numbers = {1, 2, 3, 4, 6, 12}
    poset = relation_from_divisibility(numbers)

    print(f"Elements: {sorted(poset.elements, key=int)}")
    print(f"Reflexive: {poset.is_reflexive()}")
    print(f"Antisymmetric: {poset.is_antisymmetric()}")
    print(f"Transitive: {poset.is_transitive()}")
    print(
        "Therefore the divisibility relation on this finite set "
        "forms a partial order."
    )

    print("\nComparability:")
    for a, b in [("2", "4"), ("2", "3"), ("3", "12")]:
        print(
            f"  {a} and {b}: "
            f"{'comparable' if poset.comparable(a, b) else 'incomparable'}"
        )


def demonstrate_poset_structure() -> None:
    print("\nDIVISIBILITY POSET")

    poset = relation_from_divisibility({1, 2, 3, 4, 6, 12})

    print(f"Minimal elements: {sorted(poset.minimal_elements(), key=int)}")
    print(f"Maximal elements: {sorted(poset.maximal_elements(), key=int)}")
    print(f"Least element: {poset.least_element()}")
    print(f"Greatest element: {poset.greatest_element()}")

    print("\nComparable pairs:")
    print(poset.comparable_pairs())

    print("\nIncomparable pairs:")
    print(poset.incomparable_pairs())

    print("\nCover relations:")
    for lower, upper in sorted(
        poset.cover_relations(),
        key=lambda pair: (int(pair[0]), int(pair[1]))
    ):
        print(f"  {lower} ⋖ {upper}")

    print("\nTextual Hasse diagram:")
    print(poset.textual_hasse_diagram())


def demonstrate_chains_and_antichains() -> None:
    print("\nCHAINS AND ANTICHAINS")

    poset = relation_from_divisibility({1, 2, 3, 4, 6, 12})

    chain = ("1", "2", "4", "12")
    antichain = ("3", "4")

    print(f"Candidate chain {chain}: {poset.is_chain(chain)}")
    print(f"Candidate antichain {antichain}: {poset.is_antichain(antichain)}")

    print(f"Maximum chain: {poset.maximum_chain()}")
    print(f"Maximum antichain: {poset.maximum_antichain()}")

    print("\nAll chains:")
    for chain_value in poset.all_chains():
        print(f"  {chain_value}")

    print("\nAll antichains:")
    for antichain_value in poset.all_antichains():
        print(f"  {antichain_value}")


def demonstrate_subset_poset() -> None:
    print("\nSUBSET-INCLUSION POSET")

    poset = relation_from_subset_inclusion(
        "abc",
        [
            set(),
            {"a"},
            {"b"},
            {"c"},
            {"a", "b"},
            {"a", "c"},
            {"b", "c"},
            {"a", "b", "c"},
        ],
    )

    print(poset.textual_hasse_diagram())

    print("\nRepresentative comparisons:")
    print(f"  {{a}} <= {{a,b}}: {poset.leq('{a}', '{a,b}')}")
    print(f"  {{a}} <= {{b}}: {poset.leq('{a}', '{b}')}")
    print(
        "  The singleton sets {a}, {b}, and {c} form an antichain because "
        "none contains another."
    )

    singleton_labels = ("{a}", "{b}", "{c}")
    print(
        f"  Singleton antichain valid: "
        f"{poset.is_antichain(singleton_labels)}"
    )


class DependencyPoset:
    """
    A practical use of a poset: representing dependency readiness.

    If A < B, B depends on A. The transitive relation means that a task can
    have indirect dependencies as well. The cover graph stores only immediate
    dependency relationships.
    """

    def __init__(self, dependencies: Dict[str, Set[str]]) -> None:
        self.dependencies = {
            task: set(prerequisites)
            for task, prerequisites in dependencies.items()
        }

        all_tasks = set(self.dependencies)
        for prerequisites in self.dependencies.values():
            all_tasks.update(prerequisites)

        self.tasks = all_tasks
        self._validate_acyclic()

    def _validate_acyclic(self) -> None:
        state = {task: 0 for task in self.tasks}

        def visit(task: str) -> None:
            if state[task] == 1:
                raise ValueError(f"Dependency cycle detected at {task}")
            if state[task] == 2:
                return

            state[task] = 1
            for prerequisite in self.dependencies.get(task, set()):
                visit(prerequisite)
            state[task] = 2

        for task in self.tasks:
            visit(task)

    def ready_tasks(self, completed: Set[str]) -> Set[str]:
        return {
            task
            for task in self.tasks - completed
            if self.dependencies.get(task, set()).issubset(completed)
        }

    def build_poset(self) -> Poset:
        """
        Convert dependency reachability into a partial order.

        x <= y means x is a prerequisite of y, directly or indirectly.
        """
        relation: Set[Tuple[str, str]] = {
            (task, task) for task in self.tasks
        }

        for start in self.tasks:
            stack = list(self.dependencies.get(start, set()))
            visited: Set[str] = set()

            while stack:
                prerequisite = stack.pop()
                if prerequisite in visited:
                    continue

                visited.add(prerequisite)
                relation.add((prerequisite, start))
                stack.extend(self.dependencies.get(prerequisite, set()))

        return Poset(
            elements=frozenset(self.tasks),
            relation=frozenset(relation),
        )


def demonstrate_realistic_dependency_case() -> None:
    print("\nREALISTIC DEPENDENCY POSET")

    dependencies = {
        "lint": set(),
        "unit-tests": {"lint"},
        "integration-tests": {"unit-tests"},
        "security-scan": {"lint"},
        "package": {"unit-tests", "security-scan"},
        "deploy-staging": {"package", "integration-tests"},
    }

    workflow = DependencyPoset(dependencies)
    poset = workflow.build_poset()

    completed: Set[str] = set()
    print(f"Initial ready tasks: {sorted(workflow.ready_tasks(completed))}")

    completed.update({"lint"})
    print(f"After lint: {sorted(workflow.ready_tasks(completed))}")

    completed.update({"unit-tests", "security-scan"})
    print(
        "After unit tests and security scan: "
        f"{sorted(workflow.ready_tasks(completed))}"
    )

    print("\nDependency-poset cover relations:")
    for lower, upper in sorted(poset.cover_relations()):
        print(f"  {lower} ⋖ {upper}")

    print("\nIndependent work:")
    for layer in poset.topological_layers():
        if len(layer) > 1:
            print(
                f"  {layer} can be considered concurrently because "
                "the listed elements are incomparable at that layer."
            )


def demonstrate_edge_cases() -> None:
    print("\nEDGE CASES AND VALIDATION")

    singleton = Poset(
        elements=frozenset({"A"}),
        relation=frozenset({("A", "A")}),
    )

    print(f"Singleton maximum chain: {singleton.maximum_chain()}")
    print(f"Singleton maximum antichain: {singleton.maximum_antichain()}")
    print(f"Singleton least element: {singleton.least_element()}")
    print(f"Singleton greatest element: {singleton.greatest_element()}")

    try:
        Poset(
            elements=frozenset({"A", "B"}),
            relation=frozenset(
                {
                    ("A", "A"),
                    ("B", "B"),
                    ("A", "B"),
                    ("B", "A"),
                }
            ),
        )
    except ValueError as error:
        print(f"Rejected non-antisymmetric relation: {error}")

    try:
        Poset(
            elements=frozenset({"A", "B", "C"}),
            relation=frozenset(
                {
                    ("A", "A"),
                    ("B", "B"),
                    ("C", "C"),
                    ("A", "B"),
                    ("B", "C"),
                }
            ),
        )
    except ValueError as error:
        print(f"Rejected non-transitive relation: {error}")

    try:
        DependencyPoset(
            {
                "compile": {"test"},
                "test": {"compile"},
            }
        )
    except ValueError as error:
        print(f"Rejected dependency cycle: {error}")


def explain_complexity() -> None:
    print("\nCOMPUTATIONAL CHARACTERISTICS")
    print(
        "The Poset class stores the relation explicitly, so a comparability "
        "lookup is O(1) on average with the underlying hash set."
    )
    print(
        "Computing cover relations by checking every possible intermediate "
        "element takes O(n^3) in this direct implementation."
    )
    print(
        "Enumerating all chains or antichains is exponential in the number "
        "of elements in the worst case because a poset can have exponentially "
        "many subsets."
    )
    print(
        "The dependency example uses graph reachability to construct the "
        "transitive partial order. A production implementation can use DAG "
        "algorithms, bitsets, or transitive-closure techniques when n is large."
    )


def main() -> None:
    demonstrate_axioms()
    demonstrate_poset_structure()
    demonstrate_chains_and_antichains()
    demonstrate_subset_poset()
    demonstrate_realistic_dependency_case()
    demonstrate_edge_cases()
    explain_complexity()


if __name__ == "__main__":
    main()
