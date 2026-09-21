"""
Quantifier Logic
================

A self-contained study program for:

- Universal and existential quantifiers
- Nested quantifiers
- Scope and variable binding
- Translating natural language into predicate logic
- Negating quantified statements
- Quantifier order and non-commutativity
- Vacuous truth
- Restricted domains
- Counterexamples and witnesses
- Logical equivalence
- Prenex-style transformations
- Truth evaluation over finite domains
- Satisfiability and counterexample search
- Common translation mistakes
- Practical applications

The program is intentionally educational. It implements a small finite-domain
predicate-logic evaluator rather than attempting to become a complete theorem
prover for unrestricted first-order logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence, Any


# ============================================================================
# SECTION 1: BASIC TERMINOLOGY
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def explain(text: str) -> None:
    print(text)


def demo_basic_terms() -> None:
    section("1. Basic terminology")

    explain(
        """
Predicate logic extends ordinary propositional logic by talking about
individual objects and properties or relationships involving those objects.

A predicate is an expression whose truth depends on one or more arguments.

Examples:

    Student(x)
    x > 0
    Knows(x, y)
    Likes(student, subject)

A variable such as x represents an object from a domain.

A domain is the collection of objects over which variables range.

A quantifier tells us how many objects satisfy a predicate.

Universal quantifier:
    ∀x P(x)
means:
    "For every object x in the domain, P(x) is true."

Existential quantifier:
    ∃x P(x)
means:
    "There exists at least one object x in the domain for which P(x) is true."

The expression following a quantifier is its scope.
"""
    )

    print("Examples:")
    print("  ∀x Student(x)        Every object is a student.")
    print("  ∃x Student(x)        At least one object is a student.")
    print("  ∀x (Student(x) → Learns(x))")
    print("                         Every student learns.")
    print("  ∃x (Student(x) ∧ Learns(x))")
    print("                         Some student learns.")


# ============================================================================
# SECTION 2: FINITE DOMAINS AND PREDICATES
# ============================================================================

@dataclass(frozen=True)
class Person:
    name: str
    age: int
    student: bool
    employed: bool


def demo_finite_domain() -> None:
    section("2. Finite domains and predicates")

    people = [
        Person("Alice", 20, True, False),
        Person("Bob", 30, False, True),
        Person("Carol", 22, True, True),
        Person("David", 17, True, False),
    ]

    student = lambda p: p.student
    adult = lambda p: p.age >= 18
    employed = lambda p: p.employed

    print("Domain:")
    for person in people:
        print(f"  {person}")

    # Universal quantification over a finite domain is implemented by all().
    every_student_is_adult = all(
        (not student(person)) or adult(person)
        for person in people
    )

    # Existential quantification is implemented by any().
    some_student_is_employed = any(
        student(person) and employed(person)
        for person in people
    )

    print("\n∀x (Student(x) → Adult(x)) =", every_student_is_adult)
    print("∃x (Student(x) ∧ Employed(x)) =", some_student_is_employed)

    explain(
        """
For a finite domain:

    ∀x P(x)  corresponds naturally to all(P(x) for x in domain)
    ∃x P(x)  corresponds naturally to any(P(x) for x in domain)

The universal implementation stops as soon as it finds a counterexample.
The existential implementation stops as soon as it finds a witness.
"""
    )


# ============================================================================
# SECTION 3: UNIVERSAL QUANTIFIER
# ============================================================================

def forall(domain: Iterable[Any], predicate: Callable[[Any], bool]) -> bool:
    """Evaluate a universal quantifier over a finite iterable."""
    return all(predicate(item) for item in domain)


def exists(domain: Iterable[Any], predicate: Callable[[Any], bool]) -> bool:
    """Evaluate an existential quantifier over a finite iterable."""
    return any(predicate(item) for item in domain)


def demo_universal_quantifier() -> None:
    section("3. Universal quantification")

    numbers = [-3, -2, -1, 0, 1, 2, 3]

    print("Domain:", numbers)
    print("∀x (x < 10):", forall(numbers, lambda x: x < 10))
    print("∀x (x >= -3):", forall(numbers, lambda x: x >= -3))
    print("∀x (x > 0):", forall(numbers, lambda x: x > 0))

    explain(
        """
A universal statement is false if even one counterexample exists.

For example:

    ∀x (x > 0)

is false over {-3, -2, -1, 0, 1, 2, 3}.

The values -3, -2, -1, and 0 are counterexamples.

A useful proof pattern is therefore:

    To prove ∀x P(x):
        choose an arbitrary x
        prove P(x)

A useful disproof pattern is:

    To disprove ∀x P(x):
        find one x for which P(x) is false.
"""
    )


# ============================================================================
# SECTION 4: EXISTENTIAL QUANTIFIER
# ============================================================================

def demo_existential_quantifier() -> None:
    section("4. Existential quantification")

    numbers = [1, 4, 7, 10, 13]

    print("Domain:", numbers)
    print("∃x (x is even):", exists(numbers, lambda x: x % 2 == 0))
    print("∃x (x > 20):", exists(numbers, lambda x: x > 20))
    print("∃x (x is divisible by 7):", exists(numbers, lambda x: x % 7 == 0))

    explain(
        """
An existential statement is true when at least one witness exists.

For:

    ∃x P(x)

a witness is a particular domain object a for which P(a) is true.

To prove an existential statement, it is enough to exhibit one witness.

To disprove an existential statement, every possible domain object must fail
the predicate.
"""
    )


# ============================================================================
# SECTION 5: RESTRICTED DOMAINS AND IMPLICATION
# ============================================================================

def demo_restricted_domains() -> None:
    section("5. Restricted domains and implication")

    people = [
        Person("Alice", 20, True, False),
        Person("Bob", 30, False, True),
        Person("Carol", 22, True, True),
        Person("David", 17, True, False),
    ]

    # "Every student is an adult" is represented as an implication.
    statement = forall(
        people,
        lambda p: (not p.student) or p.age >= 18
    )

    print("Every student is an adult:", statement)

    # "Some student is an adult" uses conjunction.
    statement = exists(
        people,
        lambda p: p.student and p.age >= 18
    )

    print("Some student is an adult:", statement)

    explain(
        """
Natural language often contains an implicit restriction.

"Every student is an adult" does NOT mean:

    ∀x (Student(x) ∧ Adult(x))

It means:

    ∀x (Student(x) → Adult(x))

The implication is important because non-students do not need to satisfy
Adult(x).

Similarly:

"Some student is an adult"

means:

    ∃x (Student(x) ∧ Adult(x))

For an existential statement, conjunction is normally used because the same
object must satisfy both properties.
"""
    )


# ============================================================================
# SECTION 6: TRANSLATING NATURAL LANGUAGE
# ============================================================================

def demo_translation() -> None:
    section("6. Translating natural language into predicate logic")

    examples = [
        (
            "Every programmer knows Python.",
            "∀x (Programmer(x) → Knows(x, Python))"
        ),
        (
            "Some programmer knows Python.",
            "∃x (Programmer(x) ∧ Knows(x, Python))"
        ),
        (
            "No programmer knows Python.",
            "∀x (Programmer(x) → ¬Knows(x, Python))"
        ),
        (
            "Some programmer does not know Python.",
            "∃x (Programmer(x) ∧ ¬Knows(x, Python))"
        ),
        (
            "Every student knows some programming language.",
            "∀x (Student(x) → ∃y (Language(y) ∧ Knows(x, y)))"
        ),
        (
            "There is a programming language known by every student.",
            "∃y (Language(y) ∧ ∀x (Student(x) → Knows(x, y)))"
        ),
    ]

    for natural_language, formula in examples:
        print(f"\nNatural language: {natural_language}")
        print(f"Logic:             {formula}")

    explain(
        """
The most important translation skill is identifying:

1. The domain.
2. The predicate or relation.
3. Which object is quantified.
4. Whether the statement says "every", "some", "none", "not every",
   "everyone", "someone", "something", or a similar expression.
5. Whether quantifiers are nested.
6. Whether the same object must satisfy multiple properties.
7. Whether quantifier order changes the meaning.
"""
    )


# ============================================================================
# SECTION 7: NESTED QUANTIFIERS
# ============================================================================

def demo_nested_quantifiers() -> None:
    section("7. Nested quantifiers")

    students = ["Alice", "Bob", "Carol"]
    subjects = ["Math", "Physics", "Programming"]

    passed = {
        ("Alice", "Math"),
        ("Alice", "Programming"),
        ("Bob", "Physics"),
        ("Carol", "Math"),
        ("Carol", "Physics"),
        ("Carol", "Programming"),
    }

    relation = lambda student, subject: (student, subject) in passed

    every_student_passed_some_subject = forall(
        students,
        lambda student: exists(
            subjects,
            lambda subject: relation(student, subject)
        )
    )

    some_subject_was_passed_by_every_student = exists(
        subjects,
        lambda subject: forall(
            students,
            lambda student: relation(student, subject)
        )
    )

    print(
        "∀student ∃subject Passed(student, subject):",
        every_student_passed_some_subject,
    )

    print(
        "∃subject ∀student Passed(student, subject):",
        some_subject_was_passed_by_every_student,
    )

    explain(
        """
Compare:

    ∀x ∃y R(x, y)

with:

    ∃y ∀x R(x, y)

The first says:

    "For every x, there is at least one y that works for that x."

The second says:

    "There is one y that works for every x."

These are generally NOT equivalent.

Example:

    ∀student ∃subject Passed(student, subject)

allows Alice, Bob, and Carol to have different successful subjects.

    ∃subject ∀student Passed(student, subject)

requires one common subject passed by everyone.
"""
    )


# ============================================================================
# SECTION 8: QUANTIFIER ORDER
# ============================================================================

def demo_quantifier_order() -> None:
    section("8. Quantifier order matters")

    employees = ["Alice", "Bob", "Carol"]
    projects = ["P1", "P2"]

    assigned = {
        ("Alice", "P1"),
        ("Bob", "P2"),
        ("Carol", "P1"),
    }

    first = forall(
        employees,
        lambda employee: exists(
            projects,
            lambda project: (employee, project) in assigned
        ),
    )

    second = exists(
        projects,
        lambda project: forall(
            employees,
            lambda employee: (employee, project) in assigned
        ),
    )

    print("Every employee has some assigned project:", first)
    print("Some single project is assigned to every employee:", second)

    explain(
        """
Quantifier order expresses dependency.

In:

    ∀x ∃y R(x, y)

the y may depend on x.

In:

    ∃y ∀x R(x, y)

the y is selected before x varies, so the same y must work for all x.

This distinction is fundamental in mathematics, databases, formal verification,
program specifications, automated reasoning, and computer science.
"""
    )


# ============================================================================
# SECTION 9: NEGATING QUANTIFIED STATEMENTS
# ============================================================================

def negate_forall(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> bool:
    """
    Evaluate ¬∀x P(x).

    By quantifier negation:

        ¬∀x P(x) ≡ ∃x ¬P(x)
    """
    return exists(domain, lambda item: not predicate(item))


def negate_exists(
    domain: Iterable[Any],
    predicate: Callable[[Any], bool],
) -> bool:
    """
    Evaluate ¬∃x P(x).

    By quantifier negation:

        ¬∃x P(x) ≡ ∀x ¬P(x)
    """
    return forall(domain, lambda item: not predicate(item))


def demo_negation() -> None:
    section("9. Negating quantified statements")

    numbers = [1, 2, 3, 4, 5]

    universal = forall(numbers, lambda x: x < 10)
    negated_universal = negate_forall(numbers, lambda x: x < 10)

    existential = exists(numbers, lambda x: x > 3)
    negated_existential = negate_exists(numbers, lambda x: x > 3)

    print("∀x (x < 10):", universal)
    print("¬∀x (x < 10):", negated_universal)

    print("∃x (x > 3):", existential)
    print("¬∃x (x > 3):", negated_existential)

    explain(
        """
The two fundamental quantifier-negation rules are:

    ¬∀x P(x)  ≡  ∃x ¬P(x)

    ¬∃x P(x)  ≡  ∀x ¬P(x)

The quantifier changes and the predicate is negated.

For nested quantifiers, the process continues through every quantifier.

Example:

    ¬∀x ∃y P(x, y)

becomes:

    ∃x ¬∃y P(x, y)

then:

    ∃x ∀y ¬P(x, y)

This is an application of logical equivalence, not merely a change of
punctuation.
"""
    )


# ============================================================================
# SECTION 10: NEGATION OF NATURAL LANGUAGE
# ============================================================================

def demo_natural_language_negation() -> None:
    section("10. Negating natural-language quantified statements")

    examples = [
        (
            "Every student passed.",
            "∀x (Student(x) → Passed(x))",
            "∃x (Student(x) ∧ ¬Passed(x))",
            "At least one student did not pass.",
        ),
        (
            "Some student passed.",
            "∃x (Student(x) ∧ Passed(x))",
            "∀x (Student(x) → ¬Passed(x))",
            "No student passed.",
        ),
        (
            "Every student knows some language.",
            "∀x (Student(x) → ∃y (Language(y) ∧ Knows(x, y)))",
            "∃x (Student(x) ∧ ∀y (Language(y) → ¬Knows(x, y)))",
            "There is a student who knows no language.",
        ),
    ]

    for original, formula, negation, meaning in examples:
        print("\nOriginal:", original)
        print("Formula:", formula)
        print("Negation:", negation)
        print("Natural-language negation:", meaning)


# ============================================================================
# SECTION 11: COMMON INCORRECT TRANSLATIONS
# ============================================================================

def demo_common_mistakes() -> None:
    section("11. Common translation mistakes")

    mistakes = [
        (
            "Every student is intelligent.",
            "∀x (Student(x) ∧ Intelligent(x))",
            "∀x (Student(x) → Intelligent(x))",
            "Conjunction incorrectly requires every domain object to be a student.",
        ),
        (
            "Some student is intelligent.",
            "∃x (Student(x) → Intelligent(x))",
            "∃x (Student(x) ∧ Intelligent(x))",
            "Implication can be true for a non-student and therefore fails to express existence of an intelligent student.",
        ),
        (
            "Every student has a mentor.",
            "∃y ∀x (Student(x) → Mentors(y, x))",
            "∀x (Student(x) → ∃y Mentors(y, x))",
            "The incorrect formula requires one common mentor.",
        ),
    ]

    for sentence, incorrect, correct, reason in mistakes:
        print(f"\nSentence: {sentence}")
        print(f"Incorrect: {incorrect}")
        print(f"Correct:   {correct}")
        print(f"Why:       {reason}")


# ============================================================================
# SECTION 12: VACUOUS TRUTH
# ============================================================================

def demo_vacuous_truth() -> None:
    section("12. Vacuous truth")

    empty_domain: list[int] = []

    universal_result = forall(empty_domain, lambda x: x > 100)
    existential_result = exists(empty_domain, lambda x: x > 100)

    print("Empty domain:", empty_domain)
    print("∀x (x > 100):", universal_result)
    print("∃x (x > 100):", existential_result)

    explain(
        """
In standard classical logic, a universal statement over an empty domain is
true:

    ∀x P(x) = True

because there is no counterexample.

An existential statement over an empty domain is false:

    ∃x P(x) = False

because there is no witness.

This can feel unintuitive in natural language, but it is a mathematically
important property.

For restricted statements such as:

    ∀x (Student(x) → Passed(x))

if there are no students, the statement is true. This is sometimes called
vacuous truth.
"""
    )


# ============================================================================
# SECTION 13: COUNTEREXAMPLES AND WITNESSES
# ============================================================================

def find_counterexample(
    domain: Sequence[Any],
    predicate: Callable[[Any], bool],
) -> Any | None:
    """Return the first counterexample to a universal statement."""
    for item in domain:
        if not predicate(item):
            return item
    return None


def find_witness(
    domain: Sequence[Any],
    predicate: Callable[[Any], bool],
) -> Any | None:
    """Return the first witness for an existential statement."""
    for item in domain:
        if predicate(item):
            return item
    return None


def demo_witnesses_and_counterexamples() -> None:
    section("13. Witnesses and counterexamples")

    numbers = [2, 4, 6, 7, 8]

    counterexample = find_counterexample(
        numbers,
        lambda x: x % 2 == 0
    )

    witness = find_witness(
        numbers,
        lambda x: x % 2 == 0
    )

    print("Counterexample to 'every number is even':", counterexample)
    print("Witness for 'some number is even':", witness)

    explain(
        """
For an existential statement, search for a witness.

For a universal statement, search for a counterexample.

This duality is useful in testing software specifications:

    Universal requirement:
        every input must satisfy a safety property.

    Counterexample:
        one input violates that property.

Model checking and property-based testing frequently rely on this style of
reasoning.
"""
    )


# ============================================================================
# SECTION 14: MULTIPLE QUANTIFIERS WITH RELATIONS
# ============================================================================

def demo_relationships() -> None:
    section("14. Relationships between objects")

    people = ["Alice", "Bob", "Carol", "David"]

    knows = {
        ("Alice", "Bob"),
        ("Alice", "Carol"),
        ("Bob", "Carol"),
        ("Carol", "Alice"),
        ("David", "Alice"),
    }

    relation = lambda a, b: (a, b) in knows

    everyone_knows_someone = forall(
        people,
        lambda person: exists(
            people,
            lambda other: person != other and relation(person, other)
        )
    )

    someone_is_known_by_everyone = exists(
        people,
        lambda target: forall(
            people,
            lambda person: person == target or relation(person, target)
        )
    )

    print("Everyone knows someone else:", everyone_knows_someone)
    print("Someone is known by everyone:", someone_is_known_by_everyone)

    explain(
        """
Binary predicates allow quantified statements about relationships.

Examples:

    ∀x ∃y Knows(x, y)

    "Everyone knows someone."

    ∃y ∀x Knows(x, y)

    "There is someone known by everyone."

The two formulas have different meanings because the quantifier order is
different.
"""
    )


# ============================================================================
# SECTION 15: FORMAL EXPRESSION CLASSES
# ============================================================================

class Formula:
    """Base class for a small educational first-order logic AST."""

    def evaluate(self, environment: dict[str, Any]) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Predicate(Formula):
    name: str
    function: Callable[..., bool]
    variables: tuple[str, ...]

    def evaluate(self, environment: dict[str, Any]) -> bool:
        values = [environment[name] for name in self.variables]
        return bool(self.function(*values))


@dataclass(frozen=True)
class Not(Formula):
    operand: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        return not self.operand.evaluate(environment)


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        return (
            self.left.evaluate(environment)
            and self.right.evaluate(environment)
        )


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        return (
            self.left.evaluate(environment)
            or self.right.evaluate(environment)
        )


@dataclass(frozen=True)
class Implies(Formula):
    antecedent: Formula
    consequent: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        return (
            not self.antecedent.evaluate(environment)
            or self.consequent.evaluate(environment)
        )


@dataclass(frozen=True)
class ForAll(Formula):
    variable: str
    domain: Sequence[Any]
    body: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        for value in self.domain:
            extended = dict(environment)
            extended[self.variable] = value
            if not self.body.evaluate(extended):
                return False
        return True


@dataclass(frozen=True)
class Exists(Formula):
    variable: str
    domain: Sequence[Any]
    body: Formula

    def evaluate(self, environment: dict[str, Any]) -> bool:
        for value in self.domain:
            extended = dict(environment)
            extended[self.variable] = value
            if self.body.evaluate(extended):
                return True
        return False


def demo_formula_ast() -> None:
    section("15. A small executable quantified-logic evaluator")

    domain = [1, 2, 3, 4, 5]

    positive = Predicate(
        name="Positive",
        function=lambda x: x > 0,
        variables=("x",),
    )

    less_than_ten = Predicate(
        name="LessThanTen",
        function=lambda x: x < 10,
        variables=("x",),
    )

    formula = ForAll(
        variable="x",
        domain=domain,
        body=And(positive, less_than_ten),
    )

    print("Formula: ∀x (Positive(x) ∧ LessThanTen(x))")
    print("Result:", formula.evaluate({}))

    explain(
        """
Representing formulas as objects creates an abstract syntax tree.

This makes it possible to separate:

    syntax representation
        from
    semantic evaluation.

A real theorem prover or logic engine can build on this architecture with
parsers, symbolic substitution, normalization, unification, inference rules,
and proof procedures.
"""
    )


# ============================================================================
# SECTION 16: FREE AND BOUND VARIABLES
# ============================================================================

def demo_scope_and_binding() -> None:
    section("16. Scope, bound variables, and free variables")

    explain(
        """
In:

    ∀x (Student(x) → Smart(x))

the occurrence of x is bound by ∀x.

In:

    Student(x) → ∃y Knows(x, y)

the x outside the existential quantifier is free, while y is bound.

A variable occurrence is bound when it lies inside the scope of a matching
quantifier.

A sentence with no free variables is a closed formula.

A formula with one or more free variables is an open formula.

Examples:

    P(x)
        x is free.

    ∀x P(x)
        x is bound.

    ∀x ∃y R(x, y)
        x and y are bound.

    R(x, y) ∧ ∀z P(z)
        x and y are free; z is bound.

Renaming a bound variable without changing its scope does not change meaning:

    ∀x P(x)

and

    ∀z P(z)

have the same logical structure.
"""
    )


# ============================================================================
# SECTION 17: LOGICAL EQUIVALENCES
# ============================================================================

def demo_equivalences() -> None:
    section("17. Quantifier equivalences")

    explain(
        """
Important equivalences include:

    ¬∀x P(x) ≡ ∃x ¬P(x)

    ¬∃x P(x) ≡ ∀x ¬P(x)

For a fixed domain, quantifiers also interact with connectives under specific
conditions.

For example:

    ∀x (P(x) ∧ Q(x))
    ≡
    (∀x P(x)) ∧ (∀x Q(x))

and:

    ∃x (P(x) ∨ Q(x))
    ≡
    (∃x P(x)) ∨ (∃x Q(x))

But generally:

    ∀x (P(x) ∨ Q(x))

is NOT equivalent to:

    (∀x P(x)) ∨ (∀x Q(x))

Likewise:

    ∃x (P(x) ∧ Q(x))

is NOT equivalent to:

    (∃x P(x)) ∧ (∃x Q(x))

because the two existential statements could have different witnesses.
"""
    )

    domain = [1, 2]

    p = lambda x: x == 1
    q = lambda x: x == 2

    left = forall(domain, lambda x: p(x) or q(x))
    right = forall(domain, p) or forall(domain, q)

    print("∀x(P(x) ∨ Q(x)) =", left)
    print("(∀xP(x)) ∨ (∀xQ(x)) =", right)


# ============================================================================
# SECTION 18: AUTOMATIC COUNTEREXAMPLE SEARCH
# ============================================================================

def compare_formulas_on_domain(
    domain: Sequence[Any],
    first: Callable[[Any], bool],
    second: Callable[[Any], bool],
) -> bool:
    """Compare two unary predicates point-by-point."""
    return all(first(x) == second(x) for x in domain)


def demo_equivalence_testing() -> None:
    section("18. Testing candidate equivalences")

    domain = list(range(-3, 4))

    # ¬∀x P(x) and ∃x ¬P(x) should always agree.
    p = lambda x: x < 2

    left = not forall(domain, p)
    right = exists(domain, lambda x: not p(x))

    print("¬∀x P(x):", left)
    print("∃x ¬P(x):", right)
    print("Equivalent on this domain:", left == right)

    explain(
        """
For finite domains, logical equivalence can be experimentally checked by
evaluating formulas over all relevant assignments.

This is not, by itself, a proof of unrestricted logical equivalence, but it is
a useful debugging and educational technique.

A finite counterexample is sufficient to disprove an alleged equivalence.
"""
    )


# ============================================================================
# SECTION 19: DATABASE INTERPRETATION
# ============================================================================

def demo_database_style_queries() -> None:
    section("19. Quantifiers and database-style reasoning")

    customers = ["Alice", "Bob", "Carol"]
    products = ["Laptop", "Phone", "Tablet"]

    purchases = {
        ("Alice", "Laptop"),
        ("Alice", "Phone"),
        ("Bob", "Phone"),
        ("Carol", "Tablet"),
        ("Carol", "Phone"),
    }

    bought = lambda customer, product: (customer, product) in purchases

    customers_with_a_purchase = [
        customer
        for customer in customers
        if exists(products, lambda product: bought(customer, product))
    ]

    customers_who_bought_every_product = [
        customer
        for customer in customers
        if forall(products, lambda product: bought(customer, product))
    ]

    products_bought_by_every_customer = [
        product
        for product in products
        if forall(customers, lambda customer: bought(customer, product))
    ]

    print("Customers with at least one purchase:")
    print(customers_with_a_purchase)

    print("Customers who bought every product:")
    print(customers_who_bought_every_product)

    print("Products bought by every customer:")
    print(products_bought_by_every_customer)

    explain(
        """
Database queries often have the same logical structure as quantified
statements.

Examples:

    "Customers who bought at least one product"
        ∃product Purchase(customer, product)

    "Customers who bought every product"
        ∀product Purchase(customer, product)

    "Products purchased by every customer"
        ∀customer Purchase(customer, product)

SQL constructs such as EXISTS and NOT EXISTS are closely related to
existential and negated existential reasoning.
"""
    )


# ============================================================================
# SECTION 20: ADVANCED NESTED QUANTIFIER EXAMPLES
# ============================================================================

def demo_advanced_nested_formulas() -> None:
    section("20. Advanced nested quantified formulas")

    people = ["A", "B", "C"]
    resources = ["R1", "R2", "R3"]

    access = {
        ("A", "R1"),
        ("A", "R2"),
        ("B", "R2"),
        ("B", "R3"),
        ("C", "R1"),
        ("C", "R2"),
        ("C", "R3"),
    }

    # Every person has access to at least one resource.
    formula_1 = forall(
        people,
        lambda person: exists(
            resources,
            lambda resource: (person, resource) in access
        ),
    )

    # There exists a resource accessible to every person.
    formula_2 = exists(
        resources,
        lambda resource: forall(
            people,
            lambda person: (person, resource) in access
        ),
    )

    # Every resource has at least one person with access.
    formula_3 = forall(
        resources,
        lambda resource: exists(
            people,
            lambda person: (person, resource) in access
        ),
    )

    print("Every person has some resource:", formula_1)
    print("Some resource is available to everyone:", formula_2)
    print("Every resource has some authorized person:", formula_3)

    explain(
        """
These patterns occur in access-control systems.

    ∀user ∃resource Authorized(user, resource)

does not imply:

    ∃resource ∀user Authorized(user, resource)

The first permits each user to have a different resource.

The second requires a shared resource.

The difference can affect authorization requirements, scheduling, resource
allocation, dependency management, and system specifications.
"""
    )


# ============================================================================
# SECTION 21: NEGATING A NESTED FORMULA PROGRAMMATICALLY
# ============================================================================

def nested_formula(
    people: Sequence[str],
    resources: Sequence[str],
    authorized: set[tuple[str, str]],
) -> bool:
    return forall(
        people,
        lambda person: exists(
            resources,
            lambda resource: (person, resource) in authorized
        ),
    )


def negated_nested_formula_direct(
    people: Sequence[str],
    resources: Sequence[str],
    authorized: set[tuple[str, str]],
) -> bool:
    """
    Direct implementation of:

        ∃person ∀resource ¬Authorized(person, resource)
    """
    return exists(
        people,
        lambda person: forall(
            resources,
            lambda resource: (person, resource) not in authorized
        ),
    )


def demo_nested_negation() -> None:
    section("21. Negating a nested formula")

    people = ["Alice", "Bob", "Carol"]
    resources = ["Database", "Server"]

    authorized = {
        ("Alice", "Database"),
        ("Bob", "Server"),
    }

    original = nested_formula(people, resources, authorized)
    negated = not original

    transformed = negated_nested_formula_direct(
        people,
        resources,
        authorized,
    )

    print("Original formula:", original)
    print("Its direct negation:", negated)
    print("Transformed negation:", transformed)

    explain(
        """
Start with:

    ∀x ∃y R(x, y)

Negate:

    ¬∀x ∃y R(x, y)

Apply the first rule:

    ∃x ¬∃y R(x, y)

Apply the second rule:

    ∃x ∀y ¬R(x, y)

Thus:

    ¬(∀x ∃y R(x,y))
        ≡
    ∃x ∀y ¬R(x,y)

The order of quantifiers is retained while each quantifier changes type.
"""
    )


# ============================================================================
# SECTION 22: PERFORMANCE CONSIDERATIONS
# ============================================================================

def quantified_pair_search(
    outer_domain: Sequence[Any],
    inner_domain: Sequence[Any],
    relation: Callable[[Any, Any], bool],
) -> bool:
    """
    Evaluate ∀x ∃y R(x,y).

    Worst-case work is O(|X| * |Y|).
    Short-circuiting can make typical execution substantially faster.
    """
    for x in outer_domain:
        found = False

        for y in inner_domain:
            if relation(x, y):
                found = True
                break

        if not found:
            return False

    return True


def demo_performance() -> None:
    section("22. Performance considerations")

    users = list(range(1, 101))
    resources = list(range(1, 101))

    relation = lambda user, resource: resource == user

    result = quantified_pair_search(users, resources, relation)

    print("∀user ∃resource resource == user:", result)

    explain(
        """
A naive implementation of:

    ∀x ∃y R(x,y)

may inspect up to:

    |X| × |Y|

pairs.

For finite sets this is O(nm).

Performance can often be improved by using an appropriate index.

For example, if R represents membership in a set of pairs, a hash set can
reduce individual relation checks to approximately O(1) average time.

Logical structure therefore influences data-structure design.
"""
    )


# ============================================================================
# SECTION 23: PROPERTY-BASED TESTING
# ============================================================================

def test_quantifier_negation_rules() -> None:
    domains = [
        [],
        [0],
        [1, 2, 3],
        [-2, -1, 0, 1, 2],
    ]

    predicates = [
        lambda x: x > 0,
        lambda x: x % 2 == 0,
        lambda x: x == 42,
    ]

    for domain in domains:
        for predicate in predicates:
            assert (
                not forall(domain, predicate)
            ) == (
                exists(domain, lambda x: not predicate(x))
            )

            assert (
                not exists(domain, predicate)
            ) == (
                forall(domain, lambda x: not predicate(x))
            )


def test_implication_definition() -> None:
    values = [False, True]

    for p, q in product(values, repeat=2):
        implication = (not p) or q

        # Material implication is false only when p is true and q is false.
        expected = not (p and not q)

        assert implication == expected


def run_tests() -> None:
    section("23. Executable tests")

    test_quantifier_negation_rules()
    test_implication_definition()

    print("All quantified-logic tests passed.")


# ============================================================================
# SECTION 24: EDGE CASES
# ============================================================================

def demo_edge_cases() -> None:
    section("24. Important edge cases")

    empty: list[int] = []
    singleton = [5]

    print("Empty ∀:", forall(empty, lambda x: x == 5))
    print("Empty ∃:", exists(empty, lambda x: x == 5))

    print("Singleton ∀:", forall(singleton, lambda x: x == 5))
    print("Singleton ∃:", exists(singleton, lambda x: x == 5))

    duplicate_domain = [1, 1, 1, 2]

    print(
        "Duplicate-domain universal:",
        forall(duplicate_domain, lambda x: x >= 1),
    )

    print(
        "Duplicate-domain existential:",
        exists(duplicate_domain, lambda x: x == 2),
    )

    explain(
        """
Edge cases worth checking include:

- Empty domains.
- Singleton domains.
- Duplicate values in implementation-level collections.
- Predicates that are always true.
- Predicates that are always false.
- Nested quantifiers over empty inner domains.
- Relations with no matching pairs.
- Relations where every pair matches.
- Variables accidentally reused with the wrong scope.
"""
    )


# ============================================================================
# SECTION 25: SYNTACTIC VERSUS SEMANTIC ISSUES
# ============================================================================

def demo_syntax_vs_semantics() -> None:
    section("25. Syntax versus semantics")

    explain(
        """
Syntax concerns whether an expression is constructed correctly.

Example:

    ∀x (Student(x) → Passed(x))

is syntactically structured as a quantified implication.

Semantics concerns what the expression means under a particular interpretation.

The same formula can be true under one interpretation and false under another.

For example:

    ∀x (Student(x) → Adult(x))

is true if every student in the domain is an adult.

It is false if at least one student is not an adult.

A formula therefore does not have a truth value in isolation unless the
relevant interpretation, domain, and predicate meanings are specified.

A sentence with no free variables is closed, but being closed does not
guarantee that it is true.
"""
    )


# ============================================================================
# SECTION 26: PRACTICAL FORMAL SPECIFICATIONS
# ============================================================================

def demo_specification_patterns() -> None:
    section("26. Practical specification patterns")

    users = ["Alice", "Bob", "Carol"]
    resources = ["read", "write", "admin"]

    permissions = {
        ("Alice", "read"),
        ("Alice", "write"),
        ("Bob", "read"),
        ("Carol", "read"),
        ("Carol", "write"),
        ("Carol", "admin"),
    }

    # Every user has at least one permission.
    every_user_has_permission = forall(
        users,
        lambda user: exists(
            resources,
            lambda permission: (user, permission) in permissions
        ),
    )

    # At least one user has administrative permission.
    some_admin = exists(
        users,
        lambda user: ("admin" in {
            permission
            for owner, permission in permissions
            if owner == user
        }),
    )

    # No user has a permission outside the approved set.
    approved = set(resources)
    no_invalid_permissions = forall(
        permissions,
        lambda pair: pair[1] in approved,
    )

    print("Every user has a permission:", every_user_has_permission)
    print("Some user has admin permission:", some_admin)
    print("No invalid permissions exist:", no_invalid_permissions)

    explain(
        """
Formal specifications can express requirements such as:

    Every user has at least one permission.

    ∀u (User(u) → ∃p (Permission(p) ∧ Has(u,p)))

or:

    Some user has administrator access.

    ∃u (User(u) ∧ Admin(u))

Formalizing requirements exposes ambiguity before implementation.
"""
    )


# ============================================================================
# SECTION 27: SECURITY CONSIDERATIONS
# ============================================================================

def demo_security_considerations() -> None:
    section("27. Security considerations")

    explain(
        """
Quantifier logic is useful in security specifications, but a formal-looking
statement is not automatically a secure implementation.

Consider:

    ∀u (User(u) → ∃r (Resource(r) ∧ Authorized(u,r)))

This says every user has at least one authorized resource.

It does NOT say:

    - users have only authorized resources;
    - resources are isolated;
    - authorization is checked at every operation;
    - credentials cannot be forged;
    - policy changes are synchronized;
    - the implementation correctly enforces the specification.

A security specification may therefore require several formulas.

For example:

    ∀u∀r ((User(u) ∧ Resource(r) ∧ Access(u,r)) → Authorized(u,r))

states that every recorded access must be authorized.

Formal specifications should be matched to actual enforcement mechanisms and
tested against adversarial inputs.
"""
    )


# ============================================================================
# SECTION 28: DESIGN GUIDELINES
# ============================================================================

def demo_best_practices() -> None:
    section("28. Best practices")

    guidelines = [
        "Define the domain before writing the formula.",
        "Identify the predicate vocabulary explicitly.",
        "Determine whether a phrase means every, some, none, or not every.",
        "Use implication for restricted universal statements.",
        "Use conjunction for restricted existential statements.",
        "Track quantifier scope carefully.",
        "Do not assume quantifiers can be reordered.",
        "Negate both the quantifier and the predicate when appropriate.",
        "Test formulas against witnesses and counterexamples.",
        "Check empty-domain behavior when implementing finite evaluators.",
        "Distinguish a common witness from a witness that depends on another variable.",
        "Use explicit parentheses for nested expressions.",
        "Keep logical meaning separate from implementation details.",
    ]

    for index, guideline in enumerate(guidelines, start=1):
        print(f"{index:02d}. {guideline}")


# ============================================================================
# SECTION 29: COMPREHENSIVE MINI CASE STUDY
# ============================================================================

def demo_case_study() -> None:
    section("29. Comprehensive mini case study: course management")

    students = ["Alice", "Bob", "Carol", "David"]
    courses = ["Math", "Physics", "Programming"]
    enrollments = {
        ("Alice", "Math"),
        ("Alice", "Programming"),
        ("Bob", "Physics"),
        ("Carol", "Math"),
        ("Carol", "Physics"),
        ("Carol", "Programming"),
        ("David", "Programming"),
    }

    passed = {
        ("Alice", "Math"),
        ("Alice", "Programming"),
        ("Bob", "Physics"),
        ("Carol", "Math"),
        ("Carol", "Physics"),
    }

    enrolled = lambda student, course: (student, course) in enrollments
    passed_course = lambda student, course: (student, course) in passed

    all_students_enrolled_somewhere = forall(
        students,
        lambda student: exists(
            courses,
            lambda course: enrolled(student, course),
        ),
    )

    every_student_passed_at_least_one = forall(
        students,
        lambda student: exists(
            courses,
            lambda course: passed_course(student, course),
        ),
    )

    some_course_passed_by_every_student = exists(
        courses,
        lambda course: forall(
            students,
            lambda student: passed_course(student, course),
        ),
    )

    student_without_a_pass = find_witness(
        students,
        lambda student: not exists(
            courses,
            lambda course: passed_course(student, course),
        ),
    )

    print("Every student enrolled somewhere:", all_students_enrolled_somewhere)
    print(
        "Every student passed at least one course:",
        every_student_passed_at_least_one,
    )
    print(
        "One course passed by every student:",
        some_course_passed_by_every_student,
    )
    print("Student with no passed course:", student_without_a_pass)

    explain(
        """
The case study demonstrates how the same logical vocabulary can express
business rules.

The statement:

    Every student passed at least one course.

is:

    ∀s (Student(s) → ∃c (Course(c) ∧ Passed(s,c)))

Its negation is:

    ∃s (Student(s) ∧ ∀c (Course(c) → ¬Passed(s,c)))

The negation identifies a concrete student who failed to pass every available
course.

This is a useful pattern for converting abstract logic into executable
validation rules.
"""
    )


# ============================================================================
# SECTION 30: MAIN
# ============================================================================

def main() -> None:
    section("Quantifier Logic: Complete Study Program")

    demo_basic_terms()
    demo_finite_domain()
    demo_universal_quantifier()
    demo_existential_quantifier()
    demo_restricted_domains()
    demo_translation()
    demo_nested_quantifiers()
    demo_quantifier_order()
    demo_negation()
    demo_natural_language_negation()
    demo_common_mistakes()
    demo_vacuous_truth()
    demo_witnesses_and_counterexamples()
    demo_relationships()
    demo_formula_ast()
    demo_scope_and_binding()
    demo_equivalences()
    demo_equivalence_testing()
    demo_database_style_queries()
    demo_advanced_nested_formulas()
    demo_nested_negation()
    demo_performance()
    run_tests()
    demo_edge_cases()
    demo_syntax_vs_semantics()
    demo_specification_patterns()
    demo_security_considerations()
    demo_best_practices()
    demo_case_study()

    section("End of study program")
    print(
        "The program has demonstrated quantified statements, nested "
        "quantifiers, negation, natural-language translation, executable "
        "evaluation, edge cases, testing, performance, and applications."
    )


if __name__ == "__main__":
    main()
