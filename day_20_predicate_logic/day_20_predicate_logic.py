"""
Predicate Logic: Predicates, Quantifiers, Universal Quantification,
and Existential Quantification

A self-contained study and executable demonstration from beginner to advanced level.

The program uses finite domains so that logical statements can be evaluated
directly. It demonstrates:

- Propositions versus predicates
- Predicate construction
- Free and bound variables
- Domains and interpretations
- Truth values
- Universal quantification
- Existential quantification
- Negation of quantified statements
- Quantifier laws
- Nested quantifiers
- Order of quantifiers
- Multiple variables
- Relations
- Implication and logical equivalence
- Vacuous truth
- Counterexamples
- Satisfiability and validity over finite domains
- Translating English statements into predicate logic
- Basic theorem-style reasoning
- Practical rule evaluation
- A small first-order-logic-inspired inference engine
- Complexity considerations
- Common logical mistakes
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# 1. Basic logical building blocks
# ---------------------------------------------------------------------------

def proposition(value: bool) -> bool:
    """A proposition is a statement that is either True or False."""
    return bool(value)


def logical_not(value: bool) -> bool:
    return not value


def logical_and(left: bool, right: bool) -> bool:
    return left and right


def logical_or(left: bool, right: bool) -> bool:
    return left or right


def logical_implies(antecedent: bool, consequent: bool) -> bool:
    """
    P -> Q is false only when P is True and Q is False.

    Truth-table equivalent:
        P -> Q == (not P) or Q
    """
    return (not antecedent) or consequent


def logical_iff(left: bool, right: bool) -> bool:
    """P <-> Q is true when P and Q have the same truth value."""
    return left == right


# ---------------------------------------------------------------------------
# 2. Predicates
# ---------------------------------------------------------------------------

def is_even(number: int) -> bool:
    """Unary predicate: Even(x)."""
    return number % 2 == 0


def is_positive(number: int) -> bool:
    """Unary predicate: Positive(x)."""
    return number > 0


def is_prime(number: int) -> bool:
    """Unary predicate: Prime(x)."""
    if number < 2:
        return False

    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1

    return True


def less_than(left: int, right: int) -> bool:
    """Binary predicate: LessThan(x, y)."""
    return left < right


def knows(person_a: str, person_b: str) -> bool:
    """
    A small binary relation.

    In formal notation this can be written:
        Knows(x, y)
    """
    relationships = {
        ("Alice", "Bob"),
        ("Bob", "Carol"),
        ("Carol", "Alice"),
    }
    return (person_a, person_b) in relationships


# ---------------------------------------------------------------------------
# 3. Predicate application
# ---------------------------------------------------------------------------

def demonstrate_predicates() -> None:
    print("\n=== Predicates ===")

    print("Even(4):", is_even(4))
    print("Even(5):", is_even(5))
    print("Positive(-2):", is_positive(-2))
    print("Prime(7):", is_prime(7))
    print("Prime(8):", is_prime(8))

    print("LessThan(3, 8):", less_than(3, 8))
    print("Knows(Alice, Bob):", knows("Alice", "Bob"))
    print("Knows(Alice, Carol):", knows("Alice", "Carol"))


# ---------------------------------------------------------------------------
# 4. Free and bound variables
# ---------------------------------------------------------------------------

def evaluate_free_variable_predicate(
    value: int,
    predicate: Callable[[int], bool],
) -> bool:
    """
    Here 'value' is supplied from outside.

    In a symbolic expression such as:
        P(x)

    x is free until a quantifier binds it.
    """
    return predicate(value)


def demonstrate_free_and_bound_variables() -> None:
    print("\n=== Free and Bound Variables ===")

    value = 10

    # Conceptually:
    #   Even(x)
    #
    # x is free because no quantifier introduces it.

    print("Predicate with supplied free variable x=10:", is_even(value))

    # Conceptually:
    #   forall x in {1,2,3,4}: Even(x)
    #
    # x is bound by the universal quantifier.
    print("A quantified variable is bound inside its quantifier's scope.")


# ---------------------------------------------------------------------------
# 5. Universal quantification
# ---------------------------------------------------------------------------

def forall(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> bool:
    """
    Universal quantification.

    Mathematical form:
        forall x in D, P(x)

    Meaning:
        P(x) must be true for every x in the domain D.

    Python's all() implements the same finite-domain idea.
    """
    return all(predicate(item) for item in domain)


def exists(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> bool:
    """
    Existential quantification.

    Mathematical form:
        exists x in D, P(x)

    Meaning:
        At least one element of D must make P(x) true.

    Python's any() implements the same finite-domain idea.
    """
    return any(predicate(item) for item in domain)


def demonstrate_basic_quantifiers() -> None:
    print("\n=== Universal and Existential Quantification ===")

    numbers = [2, 4, 6, 8]

    print("Domain:", numbers)

    statement_1 = forall(numbers, is_even)
    statement_2 = exists(numbers, is_prime)

    print("∀x Even(x):", statement_1)
    print("∃x Prime(x):", statement_2)

    mixed_numbers = [1, 2, 3, 4, 5]

    print("Domain:", mixed_numbers)
    print("∀x Even(x):", forall(mixed_numbers, is_even))
    print("∃x Even(x):", exists(mixed_numbers, is_even))


# ---------------------------------------------------------------------------
# 6. Why the domain matters
# ---------------------------------------------------------------------------

def demonstrate_domain_dependence() -> None:
    print("\n=== Domain Dependence ===")

    positive_numbers = [2, 4, 6, 8]
    all_integers_sample = [-3, -2, -1, 0, 1, 2, 3]

    statement_a = forall(positive_numbers, is_positive)
    statement_b = forall(all_integers_sample, is_positive)

    print(
        "∀x Positive(x) over positive domain:",
        statement_a,
    )

    print(
        "∀x Positive(x) over mixed domain:",
        statement_b,
    )

    print(
        "The same predicate can produce different truth values "
        "when the domain changes."
    )


# ---------------------------------------------------------------------------
# 7. Counterexamples
# ---------------------------------------------------------------------------

def find_counterexample(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> Any | None:
    """
    A counterexample to ∀x P(x) is an element for which P(x) is false.
    """
    for item in domain:
        if not predicate(item):
            return item
    return None


def demonstrate_counterexamples() -> None:
    print("\n=== Counterexamples ===")

    domain = [2, 4, 6, 7, 8]

    statement = forall(domain, is_even)
    counterexample = find_counterexample(domain, is_even)

    print("Statement:", statement)
    print("Counterexample:", counterexample)

    if counterexample is not None:
        print(
            f"{counterexample} disproves the universal statement "
            "because it is not even."
        )


# ---------------------------------------------------------------------------
# 8. Vacuous truth
# ---------------------------------------------------------------------------

def demonstrate_vacuous_truth() -> None:
    print("\n=== Vacuous Truth ===")

    empty_domain: list[int] = []

    universal_statement = forall(empty_domain, is_prime)
    existential_statement = exists(empty_domain, is_prime)

    print("∀x Prime(x) over empty domain:", universal_statement)
    print("∃x Prime(x) over empty domain:", existential_statement)

    print(
        "A universal statement over an empty domain is true because "
        "there is no counterexample."
    )

    print(
        "An existential statement over an empty domain is false because "
        "there is no witness."
    )


# ---------------------------------------------------------------------------
# 9. Negating quantified statements
# ---------------------------------------------------------------------------

def demonstrate_quantifier_negation() -> None:
    print("\n=== Negation of Quantifiers ===")

    domain = [1, 2, 3, 4]

    # ¬∀x P(x) is logically equivalent to ∃x ¬P(x).
    left = not forall(domain, is_even)
    right = exists(domain, lambda x: not is_even(x))

    print("¬∀x Even(x):", left)
    print("∃x ¬Even(x):", right)
    print("Equivalent:", left == right)

    # ¬∃x P(x) is logically equivalent to ∀x ¬P(x).
    left = not exists(domain, is_even)
    right = forall(domain, lambda x: not is_even(x))

    print("¬∃x Even(x):", left)
    print("∀x ¬Even(x):", right)
    print("Equivalent:", left == right)


# ---------------------------------------------------------------------------
# 10. De Morgan-style quantifier laws
# ---------------------------------------------------------------------------

def verify_quantifier_laws(domain: Sequence[int]) -> None:
    predicates = [
        ("Even", is_even),
        ("Positive", is_positive),
        ("Prime", is_prime),
    ]

    print("\n=== Quantifier Laws ===")

    for name, predicate in predicates:
        law_1_left = not forall(domain, predicate)
        law_1_right = exists(domain, lambda x: not predicate(x))

        law_2_left = not exists(domain, predicate)
        law_2_right = forall(domain, lambda x: not predicate(x))

        print(f"\nPredicate: {name}")
        print(
            "¬∀x P(x) == ∃x ¬P(x):",
            law_1_left == law_1_right,
        )
        print(
            "¬∃x P(x) == ∀x ¬P(x):",
            law_2_left == law_2_right,
        )


# ---------------------------------------------------------------------------
# 11. Binary predicates and relations
# ---------------------------------------------------------------------------

def forall_pairs(
    domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    """Evaluate ∀x∀y R(x,y) over a finite domain."""
    return all(
        relation(first, second)
        for first in domain
        for second in domain
    )


def exists_pair(
    domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    """Evaluate ∃x∃y R(x,y) over a finite domain."""
    return any(
        relation(first, second)
        for first in domain
        for second in domain
    )


def demonstrate_binary_predicates() -> None:
    print("\n=== Binary Predicates ===")

    numbers = [1, 2, 3, 4]

    print(
        "∀x∀y (x < y):",
        forall_pairs(numbers, less_than),
    )

    print(
        "∃x∃y (x < y):",
        exists_pair(numbers, less_than),
    )

    print(
        "∃x∃y (x = y):",
        exists_pair(numbers, lambda x, y: x == y),
    )


# ---------------------------------------------------------------------------
# 12. Nested quantifiers
# ---------------------------------------------------------------------------

def forall_exists(
    outer_domain: Sequence[Any],
    inner_domain: Sequence[Any],
    predicate: Callable[[Any, Any], bool],
) -> bool:
    """
    Evaluate:

        ∀x ∃y P(x,y)

    For every x, there must be at least one y that satisfies P(x,y).
    """
    return all(
        any(predicate(x, y) for y in inner_domain)
        for x in outer_domain
    )


def exists_forall(
    outer_domain: Sequence[Any],
    inner_domain: Sequence[Any],
    predicate: Callable[[Any, Any], bool],
) -> bool:
    """
    Evaluate:

        ∃x ∀y P(x,y)

    There must be one x that satisfies P(x,y) for every y.
    """
    return any(
        all(predicate(x, y) for y in inner_domain)
        for x in outer_domain
    )


def demonstrate_nested_quantifiers() -> None:
    print("\n=== Nested Quantifiers ===")

    domain = [1, 2, 3, 4]

    # ∀x ∃y (x <= y)
    statement_a = forall_exists(
        domain,
        domain,
        lambda x, y: x <= y,
    )

    # ∃x ∀y (x <= y)
    statement_b = exists_forall(
        domain,
        domain,
        lambda x, y: x <= y,
    )

    print("∀x∃y (x <= y):", statement_a)
    print("∃x∀y (x <= y):", statement_b)

    print(
        "The two formulas have different meanings even though "
        "they use the same predicate."
    )


# ---------------------------------------------------------------------------
# 13. Quantifier order matters
# ---------------------------------------------------------------------------

def compare_quantifier_order() -> None:
    print("\n=== Quantifier Order ===")

    people = ["Alice", "Bob", "Carol"]

    knows_relation = knows

    first = forall_exists(
        people,
        people,
        knows_relation,
    )

    second = exists_forall(
        people,
        people,
        knows_relation,
    )

    print("∀x∃y Knows(x,y):", first)
    print("∃x∀y Knows(x,y):", second)

    print(
        "Changing the order of quantifiers can change the meaning "
        "and the truth value."
    )


# ---------------------------------------------------------------------------
# 14. Multiple variables
# ---------------------------------------------------------------------------

def demonstrate_multiple_variables() -> None:
    print("\n=== Multiple Variables ===")

    domain = [1, 2, 3, 4, 5]

    # ∃x∃y (x != y)
    different_pair_exists = any(
        x != y
        for x in domain
        for y in domain
    )

    # ∀x∃y (y > x)
    greater_element_exists_for_each = forall_exists(
        domain,
        domain,
        lambda x, y: y > x,
    )

    print("∃x∃y (x != y):", different_pair_exists)
    print("∀x∃y (y > x):", greater_element_exists_for_each)


# ---------------------------------------------------------------------------
# 15. Implication inside quantified statements
# ---------------------------------------------------------------------------

def demonstrate_implication() -> None:
    print("\n=== Implication and Quantifiers ===")

    domain = [1, 2, 3, 4, 5, 6]

    # ∀x (Even(x) -> x > 0)
    statement = forall(
        domain,
        lambda x: logical_implies(is_even(x), x > 0),
    )

    print("∀x (Even(x) -> x > 0):", statement)

    # Notice that implication does not assert that every x is even.
    # It only constrains x when Even(x) is true.


# ---------------------------------------------------------------------------
# 16. Equivalence of predicate expressions
# ---------------------------------------------------------------------------

def demonstrate_logical_equivalence() -> None:
    print("\n=== Logical Equivalence ===")

    domain = [1, 2, 3, 4, 5]

    # P -> Q is equivalent to ¬P OR Q.
    implication_form = forall(
        domain,
        lambda x: logical_implies(
            is_even(x),
            is_positive(x),
        ),
    )

    equivalent_form = forall(
        domain,
        lambda x: (
            logical_not(is_even(x))
            or is_positive(x)
        ),
    )

    print("∀x (Even(x) -> Positive(x)):", implication_form)
    print("∀x (¬Even(x) ∨ Positive(x)):", equivalent_form)
    print("Equivalent:", implication_form == equivalent_form)


# ---------------------------------------------------------------------------
# 17. Translating English into predicate logic
# ---------------------------------------------------------------------------

def translate_english_examples() -> None:
    print("\n=== English-to-Predicate-Logic Translation ===")

    people = ["Alice", "Bob", "Carol", "David"]

    employed = {
        "Alice": True,
        "Bob": True,
        "Carol": False,
        "David": True,
    }

    qualified = {
        "Alice": True,
        "Bob": False,
        "Carol": True,
        "David": True,
    }

    employed_predicate = lambda person: employed[person]
    qualified_predicate = lambda person: qualified[person]

    # "Everyone is employed."
    everyone_employed = forall(people, employed_predicate)

    # "Someone is qualified."
    someone_qualified = exists(people, qualified_predicate)

    # "Everyone who is qualified is employed."
    every_qualified_is_employed = forall(
        people,
        lambda person: logical_implies(
            qualified_predicate(person),
            employed_predicate(person),
        ),
    )

    print("Everyone is employed:", everyone_employed)
    print("Someone is qualified:", someone_qualified)
    print(
        "Everyone qualified is employed:",
        every_qualified_is_employed,
    )


# ---------------------------------------------------------------------------
# 18. Witness extraction
# ---------------------------------------------------------------------------

def find_witness(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> Any | None:
    """
    An existential statement is established by a witness.

    If ∃x P(x) is true, this function returns one x for which P(x) is true.
    """
    for item in domain:
        if predicate(item):
            return item
    return None


def demonstrate_witnesses() -> None:
    print("\n=== Existential Witnesses ===")

    domain = [1, 3, 5, 8, 10]

    witness = find_witness(domain, is_even)

    print("∃x Even(x):", witness is not None)
    print("Witness:", witness)


# ---------------------------------------------------------------------------
# 19. A small finite-model evaluator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FiniteModel:
    """
    A finite first-order-style model.

    domain:
        Objects over which variables range.

    predicates:
        Mapping from predicate names to Python callables.
    """

    domain: tuple[Any, ...]
    predicates: dict[str, Callable[..., bool]]

    def evaluate_unary(
        self,
        predicate_name: str,
        value: Any,
    ) -> bool:
        return self.predicates[predicate_name](value)

    def evaluate_binary(
        self,
        predicate_name: str,
        first: Any,
        second: Any,
    ) -> bool:
        return self.predicates[predicate_name](first, second)


def demonstrate_finite_model() -> None:
    print("\n=== Finite Model ===")

    model = FiniteModel(
        domain=(1, 2, 3, 4, 5),
        predicates={
            "Even": is_even,
            "Prime": is_prime,
            "LessThan": less_than,
        },
    )

    print(
        "Even(4):",
        model.evaluate_unary("Even", 4),
    )

    print(
        "Prime(5):",
        model.evaluate_unary("Prime", 5),
    )

    print(
        "LessThan(2, 4):",
        model.evaluate_binary("LessThan", 2, 4),
    )


# ---------------------------------------------------------------------------
# 20. Formula-like abstractions
# ---------------------------------------------------------------------------

class Formula:
    """Base class for finite-domain logical formulas."""

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class PredicateFormula(Formula):
    name: str
    function: Callable[..., bool]
    variables: tuple[str, ...]

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        arguments = [
            assignment[variable]
            for variable in self.variables
        ]
        return bool(self.function(*arguments))


@dataclass(frozen=True)
class NotFormula(Formula):
    formula: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        return not self.formula.evaluate(assignment)


@dataclass(frozen=True)
class AndFormula(Formula):
    left: Formula
    right: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        return (
            self.left.evaluate(assignment)
            and self.right.evaluate(assignment)
        )


@dataclass(frozen=True)
class OrFormula(Formula):
    left: Formula
    right: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        return (
            self.left.evaluate(assignment)
            or self.right.evaluate(assignment)
        )


@dataclass(frozen=True)
class ImpliesFormula(Formula):
    left: Formula
    right: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        return logical_implies(
            self.left.evaluate(assignment),
            self.right.evaluate(assignment),
        )


@dataclass(frozen=True)
class UniversalFormula(Formula):
    variable: str
    domain: tuple[Any, ...]
    body: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        for value in self.domain:
            extended_assignment = dict(assignment)
            extended_assignment[self.variable] = value

            if not self.body.evaluate(extended_assignment):
                return False

        return True


@dataclass(frozen=True)
class ExistentialFormula(Formula):
    variable: str
    domain: tuple[Any, ...]
    body: Formula

    def evaluate(self, assignment: dict[str, Any]) -> bool:
        for value in self.domain:
            extended_assignment = dict(assignment)
            extended_assignment[self.variable] = value

            if self.body.evaluate(extended_assignment):
                return True

        return False


def demonstrate_formula_objects() -> None:
    print("\n=== Formula Objects ===")

    domain = (1, 2, 3, 4, 5)

    even_x = PredicateFormula(
        name="Even",
        function=is_even,
        variables=("x",),
    )

    positive_x = PredicateFormula(
        name="Positive",
        function=is_positive,
        variables=("x",),
    )

    formula = UniversalFormula(
        variable="x",
        domain=domain,
        body=ImpliesFormula(
            left=even_x,
            right=positive_x,
        ),
    )

    result = formula.evaluate({})

    print("∀x (Even(x) -> Positive(x)):", result)


# ---------------------------------------------------------------------------
# 21. Variable shadowing and scope
# ---------------------------------------------------------------------------

def demonstrate_scope() -> None:
    print("\n=== Scope and Variable Binding ===")

    domain = [1, 2, 3]

    # The inner x is conceptually local to its quantifier.
    # Reusing a variable name can make formulas difficult to read.
    #
    # Prefer:
    #   ∀x ∃y P(x,y)
    #
    # over:
    #   ∀x ∃x P(x,x)
    #
    # when the variables represent different logical objects.

    statement = forall_exists(
        domain,
        domain,
        lambda x, y: x <= y,
    )

    print("∀x∃y (x <= y):", statement)
    print(
        "Clear variable names reduce mistakes when formulas "
        "contain multiple quantifier scopes."
    )


# ---------------------------------------------------------------------------
# 22. Satisfiability and validity over finite domains
# ---------------------------------------------------------------------------

def is_satisfiable(
    domain: Sequence[Any],
    formula: Callable[[Any], bool],
) -> bool:
    """A formula is satisfiable if it is true for at least one object."""
    return exists(domain, formula)


def is_universally_valid(
    domain: Sequence[Any],
    formula: Callable[[Any], bool],
) -> bool:
    """A formula is valid within this finite model if it is true everywhere."""
    return forall(domain, formula)


def demonstrate_satisfiability_and_validity() -> None:
    print("\n=== Satisfiability and Validity in a Finite Domain ===")

    domain = [1, 2, 3, 4, 5]

    print(
        "Even(x) is satisfiable:",
        is_satisfiable(domain, is_even),
    )

    print(
        "Positive(x) is universally valid:",
        is_universally_valid(domain, is_positive),
    )

    print(
        "Prime(x) is universally valid:",
        is_universally_valid(domain, is_prime),
    )


# ---------------------------------------------------------------------------
# 23. Testing logical equivalences
# ---------------------------------------------------------------------------

def verify_double_negation(domain: Sequence[Any]) -> bool:
    for item in domain:
        if logical_not(logical_not(is_even(item))) != is_even(item):
            return False
    return True


def verify_implication_equivalence(domain: Sequence[Any]) -> bool:
    for item in domain:
        left = logical_implies(
            is_even(item),
            is_positive(item),
        )

        right = (
            logical_not(is_even(item))
            or is_positive(item)
        )

        if left != right:
            return False

    return True


def demonstrate_logical_tests() -> None:
    print("\n=== Automated Logical Tests ===")

    domain = list(range(-5, 6))

    print(
        "Double negation:",
        verify_double_negation(domain),
    )

    print(
        "Implication equivalence:",
        verify_implication_equivalence(domain),
    )


# ---------------------------------------------------------------------------
# 24. Practical rule system
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Person:
    name: str
    age: int
    employee: bool
    manager: bool
    certified: bool


def is_adult(person: Person) -> bool:
    return person.age >= 18


def is_eligible_for_system_access(person: Person) -> bool:
    """
    Example rule:

        Employee(x) AND Adult(x) AND Certified(x)
        -> Eligible(x)
    """
    return (
        person.employee
        and is_adult(person)
        and person.certified
    )


def demonstrate_rule_system() -> None:
    print("\n=== Practical Rule System ===")

    people = [
        Person("Alice", 30, True, True, True),
        Person("Bob", 17, True, False, True),
        Person("Carol", 25, False, False, True),
        Person("David", 40, True, False, False),
    ]

    all_adults = forall(people, is_adult)
    someone_is_eligible = exists(
        people,
        is_eligible_for_system_access,
    )

    print("All people are adults:", all_adults)
    print("Someone is eligible:", someone_is_eligible)

    eligible_people = [
        person.name
        for person in people
        if is_eligible_for_system_access(person)
    ]

    print("Eligible people:", eligible_people)


# ---------------------------------------------------------------------------
# 25. Checking a universal claim and reporting evidence
# ---------------------------------------------------------------------------

def explain_universal_claim(
    domain: Sequence[Any],
    predicate: Callable[[Any], bool],
) -> dict[str, Any]:
    counterexample = find_counterexample(domain, predicate)

    return {
        "true": counterexample is None,
        "counterexample": counterexample,
        "domain_size": len(domain),
    }


def explain_existential_claim(
    domain: Sequence[Any],
    predicate: Callable[[Any], bool],
) -> dict[str, Any]:
    witness = find_witness(domain, predicate)

    return {
        "true": witness is not None,
        "witness": witness,
        "domain_size": len(domain),
    }


def demonstrate_evidence_reporting() -> None:
    print("\n=== Evidence for Quantified Claims ===")

    domain = list(range(1, 11))

    universal_report = explain_universal_claim(
        domain,
        is_even,
    )

    existential_report = explain_existential_claim(
        domain,
        is_prime,
    )

    print("Universal report:", universal_report)
    print("Existential report:", existential_report)


# ---------------------------------------------------------------------------
# 26. Complexity considerations
# ---------------------------------------------------------------------------

def count_unary_quantifier_checks(
    domain_size: int,
) -> int:
    """
    A direct ∀x or ∃x evaluation can require O(n) predicate checks.
    """
    return domain_size


def count_binary_nested_checks(
    domain_size: int,
) -> int:
    """
    Direct ∀x∀y or ∃x∃y evaluation can require O(n²) checks.
    """
    return domain_size * domain_size


def count_ternary_nested_checks(
    domain_size: int,
) -> int:
    """
    Three nested finite quantifiers can require O(n³) checks.
    """
    return domain_size ** 3


def demonstrate_complexity() -> None:
    print("\n=== Finite Quantifier Evaluation Complexity ===")

    n = 100

    print("Unary quantifier checks:", count_unary_quantifier_checks(n))
    print("Binary nested checks:", count_binary_nested_checks(n))
    print("Ternary nested checks:", count_ternary_nested_checks(n))

    print(
        "Nested quantifiers can cause combinatorial growth, "
        "which is important in automated reasoning."
    )


# ---------------------------------------------------------------------------
# 27. Short-circuit behavior
# ---------------------------------------------------------------------------

def demonstrate_short_circuiting() -> None:
    print("\n=== Short-Circuit Evaluation ===")

    domain = [2, 4, 6, 7, 8, 10]

    # forall() stops at the first counterexample.
    result = forall(domain, is_even)

    print("∀x Even(x):", result)

    # exists() stops at the first witness.
    result = exists(domain, is_even)

    print("∃x Even(x):", result)

    print(
        "Short-circuiting avoids unnecessary predicate evaluations "
        "when a decisive result is found."
    )


# ---------------------------------------------------------------------------
# 28. Relations and relational properties
# ---------------------------------------------------------------------------

def is_reflexive(
    domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    return all(relation(item, item) for item in domain)


def is_symmetric(
    domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    return all(
        not relation(x, y) or relation(y, x)
        for x in domain
        for y in domain
    )


def is_transitive(
    domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    return all(
        not (relation(x, y) and relation(y, z))
        or relation(x, z)
        for x in domain
        for y in domain
        for z in domain
    )


def demonstrate_relation_properties() -> None:
    print("\n=== Properties of Relations ===")

    domain = [1, 2, 3]

    equality = lambda x, y: x == y

    print("Equality reflexive:", is_reflexive(domain, equality))
    print("Equality symmetric:", is_symmetric(domain, equality))
    print("Equality transitive:", is_transitive(domain, equality))


# ---------------------------------------------------------------------------
# 29. A practical authorization predicate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccessRequest:
    user: str
    role: str
    resource: str
    authenticated: bool
    active: bool


def can_access(request: AccessRequest) -> bool:
    """
    Simplified policy:

        Authenticated(x)
        AND Active(x)
        AND Role(x) == "admin"
        -> AccessGranted(x)

    The example illustrates how predicates can represent policy rules.
    """
    return (
        request.authenticated
        and request.active
        and request.role == "admin"
    )


def demonstrate_authorization_logic() -> None:
    print("\n=== Predicate Logic in Authorization ===")

    requests = [
        AccessRequest(
            "alice",
            "admin",
            "database",
            True,
            True,
        ),
        AccessRequest(
            "bob",
            "user",
            "database",
            True,
            True,
        ),
        AccessRequest(
            "carol",
            "admin",
            "database",
            True,
            False,
        ),
    ]

    for request in requests:
        print(
            request.user,
            "access granted:",
            can_access(request),
        )

    print(
        "A production authorization system would require "
        "stronger controls than this educational model."
    )


# ---------------------------------------------------------------------------
# 30. Common mistakes
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print("\n=== Common Logical Mistakes ===")

    domain = [1, 2, 3, 4]

    # Mistake:
    # Treating ∀x P(x) as if it meant ∃x P(x).
    universal_even = forall(domain, is_even)
    existential_even = exists(domain, is_even)

    print("∀x Even(x):", universal_even)
    print("∃x Even(x):", existential_even)

    # Mistake:
    # Negating ∀x P(x) as ∀x ¬P(x).
    #
    # Correct:
    #   ¬∀x P(x) == ∃x ¬P(x)
    incorrect = forall(domain, lambda x: not is_even(x))
    correct = exists(domain, lambda x: not is_even(x))

    print("Incorrect negation of ∀x Even(x):", incorrect)
    print("Correct negation of ∀x Even(x):", correct)

    # Mistake:
    # Assuming ∀x∃y P(x,y) means ∃y∀x P(x,y).
    first = forall_exists(
        domain,
        domain,
        lambda x, y: x <= y,
    )

    second = exists_forall(
        domain,
        domain,
        lambda x, y: x <= y,
    )

    print("∀x∃y (x <= y):", first)
    print("∃y∀x (x <= y):", second)


# ---------------------------------------------------------------------------
# 31. Integrated case study
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Employee:
    employee_id: int
    name: str
    department: str
    age: int
    active: bool
    trained: bool
    security_clearance: int


def employee_is_adult(employee: Employee) -> bool:
    return employee.age >= 18


def employee_can_enter_secure_area(
    employee: Employee,
) -> bool:
    return (
        employee.active
        and employee.trained
        and employee.security_clearance >= 2
        and employee_is_adult(employee)
    )


def every_employee_is_adult(
    employees: Sequence[Employee],
) -> bool:
    return forall(employees, employee_is_adult)


def at_least_one_employee_can_enter(
    employees: Sequence[Employee],
) -> bool:
    return exists(
        employees,
        employee_can_enter_secure_area,
    )


def every_trained_employee_is_active(
    employees: Sequence[Employee],
) -> bool:
    return forall(
        employees,
        lambda employee: logical_implies(
            employee.trained,
            employee.active,
        ),
    )


def demonstrate_integrated_case_study() -> None:
    print("\n=== Integrated Case Study ===")

    employees = [
        Employee(
            101,
            "Alice",
            "Security",
            31,
            True,
            True,
            3,
        ),
        Employee(
            102,
            "Bob",
            "Finance",
            29,
            True,
            False,
            1,
        ),
        Employee(
            103,
            "Carol",
            "Engineering",
            17,
            False,
            True,
            2,
        ),
        Employee(
            104,
            "David",
            "Security",
            44,
            True,
            True,
            2,
        ),
    ]

    print(
        "∀x Adult(x):",
        every_employee_is_adult(employees),
    )

    print(
        "∃x CanEnterSecureArea(x):",
        at_least_one_employee_can_enter(employees),
    )

    print(
        "∀x (Trained(x) -> Active(x)):",
        every_trained_employee_is_active(employees),
    )

    counterexample = find_counterexample(
        employees,
        every_trained_employee_is_active,
    )

    # The helper above expects a direct predicate, so use a direct search
    # for an employee violating the implication.
    violating_employee = next(
        (
            employee
            for employee in employees
            if employee.trained and not employee.active
        ),
        None,
    )

    print(
        "Counterexample to trained -> active:",
        violating_employee,
    )


# ---------------------------------------------------------------------------
# 32. Assertions as executable logical expectations
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    domain = [1, 2, 3, 4, 5]

    assert exists(domain, is_even)
    assert exists(domain, is_prime)
    assert not forall(domain, is_even)

    assert (
        not forall(domain, is_even)
        == exists(domain, lambda x: not is_even(x))
    )

    assert (
        not exists(domain, is_even)
        == forall(domain, lambda x: not is_even(x))
    )

    assert logical_implies(True, True)
    assert logical_implies(False, False)
    assert not logical_implies(True, False)

    assert verify_double_negation(domain)
    assert verify_implication_equivalence(domain)


# ---------------------------------------------------------------------------
# 33. Educational reference table
# ---------------------------------------------------------------------------

def print_reference_table() -> None:
    print("\n=== Predicate Logic Reference ===")

    reference = [
        ("P(x)", "Unary predicate"),
        ("P(x, y)", "Binary predicate"),
        ("∀x P(x)", "P is true for every x"),
        ("∃x P(x)", "P is true for at least one x"),
        ("¬P(x)", "P(x) is false"),
        ("P(x) ∧ Q(x)", "Both predicates are true"),
        ("P(x) ∨ Q(x)", "At least one predicate is true"),
        ("P(x) → Q(x)", "If P then Q"),
        ("P(x) ↔ Q(x)", "P and Q have the same truth value"),
        ("¬∀x P(x)", "Equivalent to ∃x ¬P(x)"),
        ("¬∃x P(x)", "Equivalent to ∀x ¬P(x)"),
    ]

    for notation, meaning in reference:
        print(f"{notation:25} {meaning}")


# ---------------------------------------------------------------------------
# 34. Main program
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("PREDICATE LOGIC STUDY PROGRAM")
    print("=" * 72)

    demonstrate_predicates()
    demonstrate_free_and_bound_variables()
    demonstrate_basic_quantifiers()
    demonstrate_domain_dependence()
    demonstrate_counterexamples()
    demonstrate_vacuous_truth()
    demonstrate_quantifier_negation()
    verify_quantifier_laws([1, 2, 3, 4, 5])
    demonstrate_binary_predicates()
    demonstrate_nested_quantifiers()
    compare_quantifier_order()
    demonstrate_multiple_variables()
    demonstrate_implication()
    demonstrate_logical_equivalence()
    translate_english_examples()
    demonstrate_witnesses()
    demonstrate_finite_model()
    demonstrate_formula_objects()
    demonstrate_scope()
    demonstrate_satisfiability_and_validity()
    demonstrate_logical_tests()
    demonstrate_rule_system()
    demonstrate_evidence_reporting()
    demonstrate_complexity()
    demonstrate_short_circuiting()
    demonstrate_relation_properties()
    demonstrate_authorization_logic()
    demonstrate_common_mistakes()
    demonstrate_integrated_case_study()
    run_assertions()
    print_reference_table()

    print("\n" + "=" * 72)
    print("All executable predicate-logic demonstrations completed.")
    print("=" * 72)


if __name__ == "__main__":
    main()
