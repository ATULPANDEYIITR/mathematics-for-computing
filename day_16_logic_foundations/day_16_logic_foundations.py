"""
Logic Foundations: Statements, Truth Values, Propositions, and Logical Connectives

A self-contained study program covering propositional logic from absolute
beginner concepts through formal notation, truth tables, equivalence,
normal forms, validation, satisfiability, inference, and practical use.

The program uses only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


# ============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


section("1. Statements and truth values")

# A proposition (or declarative statement) is a sentence that can be
# classified as either true or false, but not both under the same
# interpretation.
#
# Examples:
#   "2 + 2 = 4"          -> proposition, True
#   "7 is even"          -> proposition, False
#
# Questions, commands, and open sentences are generally not propositions:
#   "What time is it?"   -> question
#   "Close the door."    -> command
#   "x > 5"              -> open sentence until x is assigned a value

propositions = {
    "p": True,   # 2 + 2 = 4
    "q": False,  # 7 is even
    "r": True,   # Python is a programming language
}

for symbol, truth_value in propositions.items():
    print(f"{symbol} = {truth_value}")


# ============================================================================
# 2. BASIC TRUTH-VALUED OPERATIONS
# ============================================================================

section("2. Logical connectives")

# NOT / negation:
#   ¬p
#
# AND / conjunction:
#   p ∧ q
#
# OR / disjunction:
#   p ∨ q
#
# XOR / exclusive OR:
#   p ⊕ q
#
# IMPLICATION:
#   p → q
#
# BICONDITIONAL:
#   p ↔ q

def logical_not(value: bool) -> bool:
    return not value


def logical_and(left: bool, right: bool) -> bool:
    return left and right


def logical_or(left: bool, right: bool) -> bool:
    return left or right


def logical_xor(left: bool, right: bool) -> bool:
    # XOR is true exactly when the operands have different truth values.
    return left != right


def implication(antecedent: bool, consequent: bool) -> bool:
    # p -> q is logically equivalent to ¬p OR q.
    #
    # The only false case is:
    # p = True and q = False.
    return (not antecedent) or consequent


def biconditional(left: bool, right: bool) -> bool:
    # p <-> q is true when both operands have the same truth value.
    return left == right


p = True
q = False

print("p       =", p)
print("q       =", q)
print("NOT p   =", logical_not(p))
print("p AND q =", logical_and(p, q))
print("p OR q  =", logical_or(p, q))
print("p XOR q =", logical_xor(p, q))
print("p -> q  =", implication(p, q))
print("p <-> q =", biconditional(p, q))


# ============================================================================
# 3. TRUTH TABLE GENERATION
# ============================================================================

section("3. Truth tables")

def truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[tuple[tuple[bool, ...], bool]]:
    """Evaluate an expression for every possible assignment."""

    rows = []

    # n Boolean variables have 2^n possible assignments.
    for values in product([False, True], repeat=len(variables)):
        result = bool(expression(*values))
        rows.append((values, result))

    return rows


def print_truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
    title: str,
) -> None:
    print(f"\n{title}")
    print(" | ".join(variables) + " | Result")
    print("-" * (len(variables) * 6 + 10))

    for values, result in truth_table(variables, expression):
        value_text = " | ".join("T" if value else "F" for value in values)
        print(f"{value_text} | {'T' if result else 'F'}")


print_truth_table(
    ["p", "q"],
    logical_and,
    "Conjunction: p ∧ q",
)

print_truth_table(
    ["p", "q"],
    logical_or,
    "Disjunction: p ∨ q",
)

print_truth_table(
    ["p", "q"],
    implication,
    "Implication: p → q",
)

print_truth_table(
    ["p", "q"],
    biconditional,
    "Biconditional: p ↔ q",
)


# ============================================================================
# 4. COMPOUND PROPOSITIONS
# ============================================================================

section("4. Compound propositions")

# A compound proposition combines simpler propositions using logical
# connectives.
#
# Example:
#     (p AND q) OR NOT r
#
# Python's Boolean operators provide a direct executable representation:
#     (p and q) or (not r)

def compound_example(p: bool, q: bool, r: bool) -> bool:
    return (p and q) or (not r)


print_truth_table(
    ["p", "q", "r"],
    compound_example,
    "(p ∧ q) ∨ ¬r",
)


# ============================================================================
# 5. OPERATOR PRECEDENCE
# ============================================================================

section("5. Precedence and parentheses")

# A conventional precedence order is:
#
#   1. ¬  NOT
#   2. ∧  AND
#   3. ∨  OR
#   4. →  implication
#   5. ↔  biconditional
#
# Parentheses should be used when clarity matters.
#
# For example:
#   ¬p ∨ q
# means:
#   (¬p) ∨ q

def precedence_example(p: bool, q: bool, r: bool) -> bool:
    return (not p) or (q and r)


print_truth_table(
    ["p", "q", "r"],
    precedence_example,
    "¬p ∨ (q ∧ r)",
)


# ============================================================================
# 6. SPECIAL TYPES OF PROPOSITIONAL FORMULAS
# ============================================================================

section("6. Tautology, contradiction, and contingency")

def is_tautology(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> bool:
    return all(result for _, result in truth_table(variables, expression))


def is_contradiction(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> bool:
    return not any(result for _, result in truth_table(variables, expression))


def is_contingency(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> bool:
    results = [result for _, result in truth_table(variables, expression)]
    return any(results) and not all(results)


# Law of excluded middle:
#     p ∨ ¬p
excluded_middle = lambda p: p or (not p)

# Law of contradiction:
#     p ∧ ¬p
contradiction_law = lambda p: p and (not p)

# Contingent proposition:
#     p ∧ q
contingent = lambda p, q: p and q

print("p ∨ ¬p is tautology:", is_tautology(["p"], excluded_middle))
print("p ∧ ¬p is contradiction:", is_contradiction(["p"], contradiction_law))
print("p ∧ q is contingency:", is_contingency(["p", "q"], contingent))


# ============================================================================
# 7. LOGICAL EQUIVALENCE
# ============================================================================

section("7. Logical equivalence")

def logically_equivalent(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
) -> bool:
    """Two formulas are equivalent if they have identical truth tables."""

    for values in product([False, True], repeat=len(variables)):
        if bool(first(*values)) != bool(second(*values)):
            return False

    return True


# De Morgan's first law:
#     ¬(p ∧ q) ≡ ¬p ∨ ¬q

demorgan_and_left = lambda p, q: not (p and q)
demorgan_and_right = lambda p, q: (not p) or (not q)

print(
    "De Morgan AND law:",
    logically_equivalent(
        ["p", "q"],
        demorgan_and_left,
        demorgan_and_right,
    ),
)

# De Morgan's second law:
#     ¬(p ∨ q) ≡ ¬p ∧ ¬q

demorgan_or_left = lambda p, q: not (p or q)
demorgan_or_right = lambda p, q: (not p) and (not q)

print(
    "De Morgan OR law:",
    logically_equivalent(
        ["p", "q"],
        demorgan_or_left,
        demorgan_or_right,
    ),
)

# Implication equivalence:
#     p → q ≡ ¬p ∨ q

implication_form = lambda p, q: implication(p, q)
implication_rewrite = lambda p, q: (not p) or q

print(
    "Implication rewrite:",
    logically_equivalent(
        ["p", "q"],
        implication_form,
        implication_rewrite,
    ),
)


# ============================================================================
# 8. COMMON LOGICAL LAWS
# ============================================================================

section("8. Fundamental logical laws")

laws: dict[str, tuple[Sequence[str], Callable[..., bool], Callable[..., bool]]] = {
    "Double negation": (
        ["p"],
        lambda p: not (not p),
        lambda p: p,
    ),
    "Identity AND": (
        ["p"],
        lambda p: p and True,
        lambda p: p,
    ),
    "Identity OR": (
        ["p"],
        lambda p: p or False,
        lambda p: p,
    ),
    "Domination AND": (
        ["p"],
        lambda p: p and False,
        lambda p: False,
    ),
    "Domination OR": (
        ["p"],
        lambda p: p or True,
        lambda p: True,
    ),
    "Idempotent AND": (
        ["p"],
        lambda p: p and p,
        lambda p: p,
    ),
    "Idempotent OR": (
        ["p"],
        lambda p: p or p,
        lambda p: p,
    ),
    "Complement OR": (
        ["p"],
        lambda p: p or (not p),
        lambda p: True,
    ),
    "Complement AND": (
        ["p"],
        lambda p: p and (not p),
        lambda p: False,
    ),
    "Commutative AND": (
        ["p", "q"],
        lambda p, q: p and q,
        lambda p, q: q and p,
    ),
    "Commutative OR": (
        ["p", "q"],
        lambda p, q: p or q,
        lambda p, q: q or p,
    ),
    "Associative AND": (
        ["p", "q", "r"],
        lambda p, q, r: (p and q) and r,
        lambda p, q, r: p and (q and r),
    ),
    "Associative OR": (
        ["p", "q", "r"],
        lambda p, q, r: (p or q) or r,
        lambda p, q, r: p or (q or r),
    ),
    "Distributive AND over OR": (
        ["p", "q", "r"],
        lambda p, q, r: p and (q or r),
        lambda p, q, r: (p and q) or (p and r),
    ),
    "Distributive OR over AND": (
        ["p", "q", "r"],
        lambda p, q, r: p or (q and r),
        lambda p, q, r: (p or q) and (p or r),
    ),
}

for name, (variables, first, second) in laws.items():
    print(f"{name:30}:", logically_equivalent(variables, first, second))


# ============================================================================
# 9. IMPLICATIONS AND RELATED FORMS
# ============================================================================

section("9. Implication, converse, inverse, and contrapositive")

# Original implication:
#     p -> q
#
# Converse:
#     q -> p
#
# Inverse:
#     ¬p -> ¬q
#
# Contrapositive:
#     ¬q -> ¬p
#
# A proposition and its contrapositive are equivalent.
# The converse and inverse are also equivalent to each other, but generally
# neither is equivalent to the original implication.

original = lambda p, q: implication(p, q)
converse = lambda p, q: implication(q, p)
inverse = lambda p, q: implication(not p, not q)
contrapositive = lambda p, q: implication(not q, not p)

print("Original vs converse:",
      logically_equivalent(["p", "q"], original, converse))
print("Original vs inverse:",
      logically_equivalent(["p", "q"], original, inverse))
print("Original vs contrapositive:",
      logically_equivalent(["p", "q"], original, contrapositive))
print("Converse vs inverse:",
      logically_equivalent(["p", "q"], converse, inverse))


# ============================================================================
# 10. ARGUMENTS AND VALIDITY
# ============================================================================

section("10. Arguments and logical validity")

# An argument consists of premises followed by a conclusion.
#
# Modus ponens:
#     p -> q
#     p
#     ----
#     q
#
# The argument is valid because there is no assignment in which both
# premises are true while the conclusion is false.

def argument_is_valid(
    variables: Sequence[str],
    premises: Sequence[Callable[..., bool]],
    conclusion: Callable[..., bool],
) -> bool:
    for values in product([False, True], repeat=len(variables)):
        premise_values = [bool(p(*values)) for p in premises]
        conclusion_value = bool(conclusion(*values))

        if all(premise_values) and not conclusion_value:
            return False

    return True


print(
    "Modus ponens valid:",
    argument_is_valid(
        ["p", "q"],
        [
            lambda p, q: implication(p, q),
            lambda p, q: p,
        ],
        lambda p, q: q,
    ),
)

# Affirming the consequent is invalid:
#     p -> q
#     q
#     ----
#     p
#
# A counterexample is p=False, q=True.

print(
    "Affirming the consequent valid:",
    argument_is_valid(
        ["p", "q"],
        [
            lambda p, q: implication(p, q),
            lambda p, q: q,
        ],
        lambda p, q: p,
    ),
)


# ============================================================================
# 11. SATISFIABILITY
# ============================================================================

section("11. Satisfiability")

def satisfying_assignments(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[dict[str, bool]]:
    solutions = []

    for values in product([False, True], repeat=len(variables)):
        if expression(*values):
            solutions.append(dict(zip(variables, values)))

    return solutions


# Formula:
#     (p OR q) AND (NOT p OR r)
formula = lambda p, q, r: (p or q) and ((not p) or r)

solutions = satisfying_assignments(["p", "q", "r"], formula)

print("Number of satisfying assignments:", len(solutions))
for solution in solutions:
    print(solution)


# ============================================================================
# 12. CONJUNCTIVE NORMAL FORM AND DISJUNCTIVE NORMAL FORM
# ============================================================================

section("12. CNF and DNF concepts")

# CNF: conjunction (AND) of clauses, where each clause is a disjunction.
#
#     (p OR q) AND (NOT p OR r)
#
# DNF: disjunction (OR) of terms, where each term is a conjunction.
#
#     (p AND q) OR (NOT p AND r)
#
# The following helpers construct a DNF directly from a truth table and a
# CNF from falsifying assignments. This is a canonical construction and is
# intentionally simple for educational purposes.

Literal = tuple[str, bool]
Term = list[Literal]


def dnf_from_truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[Term]:
    terms: list[Term] = []

    for values in product([False, True], repeat=len(variables)):
        if expression(*values):
            terms.append(list(zip(variables, values)))

    return terms


def cnf_from_truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[Term]:
    clauses: list[Term] = []

    for values in product([False, True], repeat=len(variables)):
        if not expression(*values):
            # To make this assignment falsify the clause, use:
            #   x     when x is False
            #   ¬x    when x is True
            clause = [
                (variable, not value)
                for variable, value in zip(variables, values)
            ]
            clauses.append(clause)

    return clauses


def format_literal(literal: Literal) -> str:
    variable, positive = literal
    return variable if positive else f"¬{variable}"


def format_dnf(terms: list[Term]) -> str:
    if not terms:
        return "False"

    formatted_terms = []
    for term in terms:
        if not term:
            formatted_terms.append("True")
        else:
            formatted_terms.append(
                "(" + " ∧ ".join(format_literal(x) for x in term) + ")"
            )

    return " ∨ ".join(formatted_terms)


def format_cnf(clauses: list[Term]) -> str:
    if not clauses:
        return "True"

    formatted_clauses = []
    for clause in clauses:
        if not clause:
            formatted_clauses.append("False")
        else:
            formatted_clauses.append(
                "(" + " ∨ ".join(format_literal(x) for x in clause) + ")"
            )

    return " ∧ ".join(formatted_clauses)


simple_formula = lambda p, q: p and q

dnf = dnf_from_truth_table(["p", "q"], simple_formula)
cnf = cnf_from_truth_table(["p", "q"], simple_formula)

print("Canonical DNF:", format_dnf(dnf))
print("Canonical CNF:", format_cnf(cnf))


# ============================================================================
# 13. A SMALL PROPOSITIONAL FORMULA DATA MODEL
# ============================================================================

section("13. Structured logical formulas")

# Representing formulas as objects makes it possible to build reusable
# evaluators, validators, and symbolic transformations.

class Formula:
    def evaluate(self, environment: dict[str, bool]) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Variable(Formula):
    name: str

    def evaluate(self, environment: dict[str, bool]) -> bool:
        if self.name not in environment:
            raise KeyError(f"Missing truth value for {self.name}")
        return bool(environment[self.name])


@dataclass(frozen=True)
class Not(Formula):
    operand: Formula

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return not self.operand.evaluate(environment)


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return self.left.evaluate(environment) and self.right.evaluate(environment)


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return self.left.evaluate(environment) or self.right.evaluate(environment)


@dataclass(frozen=True)
class Implies(Formula):
    antecedent: Formula
    consequent: Formula

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return (
            not self.antecedent.evaluate(environment)
            or self.consequent.evaluate(environment)
        )


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return (
            self.left.evaluate(environment)
            == self.right.evaluate(environment)
        )


P = Variable("p")
Q = Variable("q")
R = Variable("r")

structured_formula = Or(And(P, Q), Not(R))

for environment in [
    {"p": False, "q": False, "r": False},
    {"p": True, "q": True, "r": True},
    {"p": True, "q": False, "r": True},
]:
    print(environment, "=>", structured_formula.evaluate(environment))


# ============================================================================
# 14. FORMULA IDENTIFICATION
# ============================================================================

section("14. Classifying a structured formula")

def formula_variables(formula: Formula) -> set[str]:
    if isinstance(formula, Variable):
        return {formula.name}

    if isinstance(formula, Not):
        return formula_variables(formula.operand)

    if isinstance(formula, (And, Or, Iff)):
        return formula_variables(formula.left) | formula_variables(formula.right)

    if isinstance(formula, Implies):
        return (
            formula_variables(formula.antecedent)
            | formula_variables(formula.consequent)
        )

    raise TypeError(f"Unsupported formula type: {type(formula).__name__}")


def classify_formula(formula: Formula) -> str:
    variables = sorted(formula_variables(formula))

    evaluator = lambda *values: formula.evaluate(
        dict(zip(variables, values))
    )

    if is_tautology(variables, evaluator):
        return "tautology"

    if is_contradiction(variables, evaluator):
        return "contradiction"

    return "contingency"


print("Formula classification:", classify_formula(structured_formula))


# ============================================================================
# 15. TRUTH TABLE FOR A STRUCTURED FORMULA
# ============================================================================

section("15. Truth table for structured formulas")

def print_formula_truth_table(formula: Formula) -> None:
    variables = sorted(formula_variables(formula))

    print(" | ".join(variables) + " | Result")
    print("-" * (len(variables) * 6 + 10))

    for values in product([False, True], repeat=len(variables)):
        environment = dict(zip(variables, values))
        result = formula.evaluate(environment)
        values_text = " | ".join("T" if x else "F" for x in values)
        print(f"{values_text} | {'T' if result else 'F'}")


print_formula_truth_table(structured_formula)


# ============================================================================
# 16. EDGE CASES AND EXCEPTIONS
# ============================================================================

section("16. Edge cases")

# Zero-variable truth tables have exactly one assignment: the empty
# assignment. This is useful when reasoning about constant formulas.
print("Constant True:", truth_table([], lambda: True))
print("Constant False:", truth_table([], lambda: False))

# Missing variables are explicit errors rather than silently assuming False.
try:
    print(P.evaluate({}))
except KeyError as error:
    print("Expected validation error:", error)

# Boolean conversion can be dangerous when arbitrary Python objects are used.
# A logic system should normally validate that values are actual booleans.
for value in [True, False]:
    assert isinstance(value, bool)

print("Boolean validation completed.")


# ============================================================================
# 17. STRICT PROPOSITIONAL VALIDATION
# ============================================================================

section("17. Strict truth-value validation")

def require_boolean(value: object, name: str = "value") -> bool:
    # bool is a subclass of int in Python, so checking `value in (0, 1)` is
    # not a sufficient semantic validation strategy for a strict logic API.
    if type(value) is not bool:
        raise TypeError(f"{name} must be exactly True or False")
    return value


def strict_and(left: object, right: object) -> bool:
    return require_boolean(left, "left") and require_boolean(right, "right")


for candidate in [True, False]:
    print("Accepted:", candidate)

for candidate in [0, 1, None, "True", [], 2]:
    try:
        strict_and(candidate, True)
    except TypeError as error:
        print("Rejected:", repr(candidate), "->", error)


# ============================================================================
# 18. PERFORMANCE
# ============================================================================

section("18. Complexity considerations")

# Exhaustive truth-table evaluation for n independent variables requires
# 2^n assignments. This exponential growth is one reason why large-scale
# propositional satisfiability requires specialized algorithms.
#
# Example sizes:
for number_of_variables in range(1, 11):
    rows = 2 ** number_of_variables
    print(f"{number_of_variables:2} variables -> {rows:4} assignments")


# ============================================================================
# 19. TESTING LOGICAL LAWS
# ============================================================================

section("19. Automated verification")

def assert_equivalent(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
    description: str,
) -> None:
    if not logically_equivalent(variables, first, second):
        raise AssertionError(f"Failed logical equivalence: {description}")

    print("PASS:", description)


assert_equivalent(
    ["p", "q"],
    lambda p, q: not (p and q),
    lambda p, q: (not p) or (not q),
    "De Morgan's AND law",
)

assert_equivalent(
    ["p", "q"],
    lambda p, q: not (p or q),
    lambda p, q: (not p) and (not q),
    "De Morgan's OR law",
)

assert_equivalent(
    ["p", "q"],
    lambda p, q: implication(p, q),
    lambda p, q: (not p) or q,
    "Implication equivalence",
)

assert_equivalent(
    ["p", "q"],
    lambda p, q: biconditional(p, q),
    lambda p, q: implication(p, q) and implication(q, p),
    "Biconditional equivalence",
)


# ============================================================================
# 20. PRACTICAL ACCESS CONTROL EXAMPLE
# ============================================================================

section("20. Practical application: access control")

# Suppose:
#   authenticated = user successfully authenticated
#   administrator = user has administrator role
#   account_active = account is active
#
# Access policy:
#   authenticated AND account_active AND administrator

def can_access_admin_panel(
    authenticated: bool,
    administrator: bool,
    account_active: bool,
) -> bool:
    return authenticated and administrator and account_active


cases = [
    (True, True, True),
    (True, True, False),
    (True, False, True),
    (False, True, True),
]

for authenticated, administrator, active in cases:
    access = can_access_admin_panel(
        authenticated,
        administrator,
        active,
    )
    print(
        {
            "authenticated": authenticated,
            "administrator": administrator,
            "account_active": active,
            "access": access,
        }
    )


# ============================================================================
# 21. PRACTICAL BUSINESS RULE
# ============================================================================

section("21. Practical application: transaction validation")

# Example policy:
# A transaction may proceed when:
#   account is active AND
#   either the amount is within the normal limit OR a manager approved it.

def transaction_allowed(
    account_active: bool,
    amount_within_limit: bool,
    manager_approved: bool,
) -> bool:
    return account_active and (amount_within_limit or manager_approved)


for case in [
    (True, True, False),
    (True, False, True),
    (True, False, False),
    (False, True, True),
]:
    print(case, "=>", transaction_allowed(*case))


# ============================================================================
# 22. LOGICAL REASONING BY COUNTEREXAMPLE
# ============================================================================

section("22. Counterexamples")

def find_counterexample(
    variables: Sequence[str],
    premises: Sequence[Callable[..., bool]],
    conclusion: Callable[..., bool],
) -> dict[str, bool] | None:
    for values in product([False, True], repeat=len(variables)):
        if all(p(*values) for p in premises) and not conclusion(*values):
            return dict(zip(variables, values))

    return None


counterexample = find_counterexample(
    ["p", "q"],
    [
        lambda p, q: implication(p, q),
        lambda p, q: q,
    ],
    lambda p, q: p,
)

print("Counterexample:", counterexample)


# ============================================================================
# 23. PROPOSITIONAL LOGIC VS BOOLEAN PROGRAMMING
# ============================================================================

section("23. Logic and programming")

# Python's `and` and `or` are short-circuit operators. They are often used
# to represent Boolean logic, but they also return operands rather than
# necessarily returning bool values.
#
# In a formal logic library, explicit Boolean normalization may be safer.

print("Python `and` with booleans:", True and False)
print("Python `or` with booleans:", False or True)

print("Python `and` with integers:", 5 and 10)
print("Python `or` with integers:", 0 or 10)

print("Normalized Boolean:", bool(5 and 10))


# ============================================================================
# 24. SHORT-CIRCUIT BEHAVIOR
# ============================================================================

section("24. Short-circuit evaluation")

def safe_division_denominator() -> bool:
    print("This function was evaluated.")
    return True


# The right side is not evaluated because False AND anything is False.
result = False and safe_division_denominator()
print("Result:", result)

# In formal truth-functional logic, p ∧ q is determined by truth values.
# In programming, short-circuit evaluation also controls whether q is
# evaluated at all. This operational distinction matters when expressions
# contain side effects or exceptions.


# ============================================================================
# 25. FINAL STUDY CHECKS
# ============================================================================

section("25. Final verification")

checks = {
    "Excluded middle": is_tautology(
        ["p"], lambda p: p or not p
    ),
    "Non-contradiction": is_contradiction(
        ["p"], lambda p: p and not p
    ),
    "De Morgan": logically_equivalent(
        ["p", "q"],
        lambda p, q: not (p and q),
        lambda p, q: not p or not q,
    ),
    "Contrapositive": logically_equivalent(
        ["p", "q"],
        lambda p, q: implication(p, q),
        lambda p, q: implication(not q, not p),
    ),
    "Biconditional expansion": logically_equivalent(
        ["p", "q"],
        lambda p, q: biconditional(p, q),
        lambda p, q: implication(p, q) and implication(q, p),
    ),
}

for name, passed in checks.items():
    print(f"{name:28} -> {'PASS' if passed else 'FAIL'}")

print("\nLogic foundations demonstration completed successfully.")
