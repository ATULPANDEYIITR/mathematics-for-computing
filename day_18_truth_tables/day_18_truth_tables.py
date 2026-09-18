"""
Truth Tables: Construction, Tautologies, Contradictions, and Contingencies

A self-contained study program covering propositional logic from beginner
through advanced level. The program constructs truth tables, evaluates
propositional formulas, classifies formulas as tautologies, contradictions,
or contingencies, compares logical equivalence, computes logical consequence,
and demonstrates useful logical transformations.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# 1. Fundamental logical operations
# ---------------------------------------------------------------------------
#
# A proposition is a statement that is either True or False.
#
# Common operators:
#
#   NOT p       -> ¬p
#   p AND q     -> p ∧ q
#   p OR q      -> p ∨ q
#   p XOR q     -> p ⊕ q
#   p IMPLIES q -> p → q
#   p IFF q     -> p ↔ q
#
# Material implication p → q is False only when p is True and q is False.
# This is equivalent to ¬p ∨ q.
# ---------------------------------------------------------------------------


def logical_not(value: bool) -> bool:
    return not value


def logical_and(left: bool, right: bool) -> bool:
    return left and right


def logical_or(left: bool, right: bool) -> bool:
    return left or right


def logical_xor(left: bool, right: bool) -> bool:
    return left != right


def logical_implies(antecedent: bool, consequent: bool) -> bool:
    # p → q is equivalent to ¬p ∨ q.
    return (not antecedent) or consequent


def logical_iff(left: bool, right: bool) -> bool:
    return left == right


def demonstrate_basic_operators() -> None:
    print("\n" + "=" * 78)
    print("1. BASIC LOGICAL OPERATORS")
    print("=" * 78)

    rows = list(product([False, True], repeat=2))

    print(f"{'p':^5}{'q':^5}{'¬p':^7}{'p∧q':^7}{'p∨q':^7}"
          f"{'p⊕q':^7}{'p→q':^7}{'p↔q':^7}")

    for p, q in rows:
        print(
            f"{str(p):^5}{str(q):^5}"
            f"{str(not p):^7}"
            f"{str(p and q):^7}"
            f"{str(p or q):^7}"
            f"{str(p != q):^7}"
            f"{str(logical_implies(p, q)):^7}"
            f"{str(p == q):^7}"
        )

    print("\nImportant implication rule:")
    print("p → q is false only for p=True and q=False.")


# ---------------------------------------------------------------------------
# 2. Truth-table generation
# ---------------------------------------------------------------------------


def generate_assignments(variables: list[str]) -> Iterable[dict[str, bool]]:
    """
    Generate every possible truth assignment.

    With n variables there are exactly 2^n rows.
    """
    for values in product([False, True], repeat=len(variables)):
        yield dict(zip(variables, values))


def print_truth_table(
    variables: list[str],
    expression_name: str,
    evaluator: Callable[[dict[str, bool]], bool],
) -> list[dict[str, bool]]:
    """
    Construct and display a complete truth table.

    The returned list is useful for further programmatic analysis.
    """
    rows = []

    header = " | ".join(variables + [expression_name])
    print("\n" + header)
    print("-" * len(header))

    for assignment in generate_assignments(variables):
        result = evaluator(assignment)
        row = {**assignment, expression_name: result}
        rows.append(row)

        values = [assignment[name] for name in variables] + [result]
        print(" | ".join("T" if value else "F" for value in values))

    return rows


def demonstrate_truth_table_construction() -> None:
    print("\n" + "=" * 78)
    print("2. TRUTH-TABLE CONSTRUCTION")
    print("=" * 78)

    # Example: p ∧ (p → q)
    # The expression is true only when both p and p → q are true.
    variables = ["p", "q"]

    print("\nExpression: p ∧ (p → q)")
    print_truth_table(
        variables,
        "p ∧ (p → q)",
        lambda a: a["p"] and logical_implies(a["p"], a["q"]),
    )

    print("\nRow-count principle:")
    for variable_count in range(1, 6):
        print(
            f"{variable_count} variable(s) -> "
            f"{2 ** variable_count} possible assignment(s)"
        )


# ---------------------------------------------------------------------------
# 3. Intermediate truth-table analysis
# ---------------------------------------------------------------------------


def classify_truth_values(values: list[bool]) -> str:
    """
    Classify an expression according to all rows of its truth table.

    Tautology:
        True on every possible assignment.

    Contradiction:
        False on every possible assignment.

    Contingency:
        True on at least one assignment and false on at least one assignment.
    """
    if all(values):
        return "tautology"
    if not any(values):
        return "contradiction"
    return "contingency"


def classify_expression(
    variables: list[str],
    evaluator: Callable[[dict[str, bool]], bool],
) -> tuple[str, list[bool]]:
    values = [evaluator(a) for a in generate_assignments(variables)]
    return classify_truth_values(values), values


def demonstrate_classification() -> None:
    print("\n" + "=" * 78)
    print("3. TAUTOLOGIES, CONTRADICTIONS, AND CONTINGENCIES")
    print("=" * 78)

    examples = [
        (
            "p ∨ ¬p",
            ["p"],
            lambda a: a["p"] or not a["p"],
        ),
        (
            "p ∧ ¬p",
            ["p"],
            lambda a: a["p"] and not a["p"],
        ),
        (
            "p ∧ q",
            ["p", "q"],
            lambda a: a["p"] and a["q"],
        ),
        (
            "(p → q) ↔ (¬p ∨ q)",
            ["p", "q"],
            lambda a: logical_implies(a["p"], a["q"])
            == ((not a["p"]) or a["q"]),
        ),
    ]

    for expression, variables, evaluator in examples:
        classification, values = classify_expression(variables, evaluator)
        print(
            f"{expression:<35} "
            f"{classification:<14} "
            f"values={''.join('T' if value else 'F' for value in values)}"
        )


# ---------------------------------------------------------------------------
# 4. Formula tree
# ---------------------------------------------------------------------------
#
# Truth-table construction becomes more useful when formulas are represented
# structurally rather than as handwritten Python lambdas.
#
# Example:
#
#       p ∧ (q ∨ ¬r)
#
# can be represented as a tree:
#
#             AND
#            /   \
#           p     OR
#                /  \
#               q   NOT
#                    |
#                    r
#
# Each node can evaluate itself for a given assignment.
# ---------------------------------------------------------------------------


class Formula:
    """Abstract base class for propositional formulas."""

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        raise NotImplementedError

    def variables(self) -> set[str]:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Variable(Formula):
    name: str

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        if self.name not in assignment:
            raise KeyError(f"Missing truth value for variable {self.name}")
        return assignment[self.name]

    def variables(self) -> set[str]:
        return {self.name}

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Not(Formula):
    operand: Formula

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        return not self.operand.evaluate(assignment)

    def variables(self) -> set[str]:
        return self.operand.variables()

    def __str__(self) -> str:
        return f"¬({self.operand})"


@dataclass(frozen=True)
class BinaryFormula(Formula):
    left: Formula
    right: Formula
    operator: str

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        left_value = self.left.evaluate(assignment)
        right_value = self.right.evaluate(assignment)

        if self.operator == "∧":
            return left_value and right_value
        if self.operator == "∨":
            return left_value or right_value
        if self.operator == "⊕":
            return left_value != right_value
        if self.operator == "→":
            return logical_implies(left_value, right_value)
        if self.operator == "↔":
            return left_value == right_value

        raise ValueError(f"Unsupported operator: {self.operator}")

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


def Var(name: str) -> Variable:
    return Variable(name)


def And(left: Formula, right: Formula) -> BinaryFormula:
    return BinaryFormula(left, right, "∧")


def Or(left: Formula, right: Formula) -> BinaryFormula:
    return BinaryFormula(left, right, "∨")


def Xor(left: Formula, right: Formula) -> BinaryFormula:
    return BinaryFormula(left, right, "⊕")


def Implies(left: Formula, right: Formula) -> BinaryFormula:
    return BinaryFormula(left, right, "→")


def Iff(left: Formula, right: Formula) -> BinaryFormula:
    return BinaryFormula(left, right, "↔")


def show_formula_truth_table(formula: Formula) -> None:
    variables = sorted(formula.variables())
    print(f"\nFormula: {formula}")
    print_truth_table(
        variables,
        str(formula),
        formula.evaluate,
    )


def demonstrate_formula_tree() -> None:
    print("\n" + "=" * 78)
    print("4. STRUCTURAL REPRESENTATION OF FORMULAS")
    print("=" * 78)

    p = Var("p")
    q = Var("q")
    r = Var("r")

    formula = And(p, Or(q, Not(r)))

    show_formula_truth_table(formula)


# ---------------------------------------------------------------------------
# 5. Parser for propositional formulas
# ---------------------------------------------------------------------------
#
# Supported textual operators:
#
#   !p       or ~p   -> NOT
#   p & q    -> AND
#   p | q    -> OR
#   p ^ q    -> XOR
#   p -> q   -> implication
#   p <-> q  -> biconditional
#
# Parentheses may be used to control grouping.
#
# Precedence, from strongest to weakest:
#
#   NOT
#   AND
#   XOR
#   OR
#   IMPLIES
#   IFF
#
# Implication is right-associative:
#   p -> q -> r
# means
#   p -> (q -> r)
# ---------------------------------------------------------------------------


TOKEN_PATTERN = re.compile(
    r"\s*(<->|->|[()!~&|^]|[A-Za-z_][A-Za-z0-9_]*)"
)


class FormulaParser:
    def __init__(self, text: str):
        self.tokens = self.tokenize(text)
        self.position = 0

    @staticmethod
    def tokenize(text: str) -> list[str]:
        tokens = []
        position = 0

        while position < len(text):
            match = TOKEN_PATTERN.match(text, position)
            if not match:
                raise ValueError(
                    f"Invalid token near position {position}: "
                    f"{text[position:position + 20]!r}"
                )
            tokens.append(match.group(1))
            position = match.end()

        return tokens

    def current(self) -> str | None:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self, expected: str | None = None) -> str:
        token = self.current()

        if token is None:
            raise ValueError("Unexpected end of expression")

        if expected is not None and token != expected:
            raise ValueError(
                f"Expected {expected!r}, found {token!r}"
            )

        self.position += 1
        return token

    def parse(self) -> Formula:
        if not self.tokens:
            raise ValueError("Expression cannot be empty")

        result = self.parse_iff()

        if self.current() is not None:
            raise ValueError(
                f"Unexpected token {self.current()!r}"
            )

        return result

    def parse_iff(self) -> Formula:
        left = self.parse_implies()

        while self.current() == "<->":
            self.consume("<->")
            right = self.parse_implies()
            left = Iff(left, right)

        return left

    def parse_implies(self) -> Formula:
        left = self.parse_or()

        # Right associativity:
        # p -> q -> r = p -> (q -> r)
        if self.current() == "->":
            self.consume("->")
            right = self.parse_implies()
            return Implies(left, right)

        return left

    def parse_or(self) -> Formula:
        left = self.parse_xor()

        while self.current() == "|":
            self.consume("|")
            right = self.parse_xor()
            left = Or(left, right)

        return left

    def parse_xor(self) -> Formula:
        left = self.parse_and()

        while self.current() == "^":
            self.consume("^")
            right = self.parse_and()
            left = Xor(left, right)

        return left

    def parse_and(self) -> Formula:
        left = self.parse_unary()

        while self.current() == "&":
            self.consume("&")
            right = self.parse_unary()
            left = And(left, right)

        return left

    def parse_unary(self) -> Formula:
        token = self.current()

        if token in ("!", "~"):
            self.consume()
            return Not(self.parse_unary())

        if token == "(":
            self.consume("(")
            expression = self.parse_iff()
            self.consume(")")
            return expression

        if token is None:
            raise ValueError("Expected a proposition")

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            self.consume()
            return Var(token)

        raise ValueError(f"Unexpected token {token!r}")


def parse_formula(text: str) -> Formula:
    return FormulaParser(text).parse()


def demonstrate_parser() -> None:
    print("\n" + "=" * 78)
    print("5. TEXT FORMULA PARSING")
    print("=" * 78)

    expressions = [
        "p | ~p",
        "p & (q | ~r)",
        "(p -> q) <-> (~p | q)",
        "p -> q -> r",
        "(p ^ q) & ~(p & q)",
    ]

    for expression in expressions:
        formula = parse_formula(expression)
        print(f"\nInput:      {expression}")
        print(f"Parsed as:  {formula}")
        print(f"Variables:  {', '.join(sorted(formula.variables()))}")

        classification, _ = classify_expression(
            sorted(formula.variables()),
            formula.evaluate,
        )
        print(f"Classified: {classification}")


# ---------------------------------------------------------------------------
# 6. Logical equivalence
# ---------------------------------------------------------------------------


def equivalent(first: Formula, second: Formula) -> bool:
    """
    Two formulas are logically equivalent when they have the same truth value
    for every possible assignment of their shared variables.
    """
    variables = sorted(first.variables() | second.variables())

    return all(
        first.evaluate(assignment) == second.evaluate(assignment)
        for assignment in generate_assignments(variables)
    )


def demonstrate_equivalence() -> None:
    print("\n" + "=" * 78)
    print("6. LOGICAL EQUIVALENCE")
    print("=" * 78)

    p = Var("p")
    q = Var("q")

    left = Implies(p, q)
    right = Or(Not(p), q)

    print(f"{left}  ≡  {right}")
    print(f"Equivalent: {equivalent(left, right)}")

    de_morgan_left = Not(And(p, q))
    de_morgan_right = Or(Not(p), Not(q))

    print(f"{de_morgan_left}  ≡  {de_morgan_right}")
    print(f"Equivalent: {equivalent(de_morgan_left, de_morgan_right)}")


# ---------------------------------------------------------------------------
# 7. Important logical laws
# ---------------------------------------------------------------------------


def demonstrate_logical_laws() -> None:
    print("\n" + "=" * 78)
    print("7. IMPORTANT LOGICAL LAWS VERIFIED BY TRUTH TABLES")
    print("=" * 78)

    p = Var("p")
    q = Var("q")
    r = Var("r")

    laws = [
        (
            "Law of excluded middle",
            Or(p, Not(p)),
        ),
        (
            "Law of contradiction",
            Not(And(p, Not(p))),
        ),
        (
            "Double negation",
            Iff(Not(Not(p)), p),
        ),
        (
            "De Morgan's law",
            Iff(Not(And(p, q)), Or(Not(p), Not(q))),
        ),
        (
            "Second De Morgan's law",
            Iff(Not(Or(p, q)), And(Not(p), Not(q))),
        ),
        (
            "Implication replacement",
            Iff(Implies(p, q), Or(Not(p), q)),
        ),
        (
            "Contrapositive",
            Iff(Implies(p, q), Implies(Not(q), Not(p))),
        ),
        (
            "Commutativity of AND",
            Iff(And(p, q), And(q, p)),
        ),
        (
            "Commutativity of OR",
            Iff(Or(p, q), Or(q, p)),
        ),
        (
            "Associativity of AND",
            Iff(And(And(p, q), r), And(p, And(q, r))),
        ),
        (
            "Distributive law",
            Iff(And(p, Or(q, r)), Or(And(p, q), And(p, r))),
        ),
    ]

    for name, formula in laws:
        variables = sorted(formula.variables())
        classification, _ = classify_expression(variables, formula.evaluate)
        print(f"{name:<32}: {classification}")


# ---------------------------------------------------------------------------
# 8. Normal forms
# ---------------------------------------------------------------------------
#
# A truth table can be converted into canonical:
#
# DNF / Sum of Products:
#   OR together one conjunction for every TRUE row.
#
# CNF / Product of Sums:
#   AND together one disjunction for every FALSE row.
#
# For example, a row p=True, q=False contributes:
#
#   DNF minterm: p ∧ ¬q
#
# The corresponding CNF maxterm is:
#
#   ¬p ∨ q
# ---------------------------------------------------------------------------


def canonical_dnf(formula: Formula) -> str:
    variables = sorted(formula.variables())
    terms = []

    for assignment in generate_assignments(variables):
        if formula.evaluate(assignment):
            literals = []
            for variable in variables:
                literals.append(
                    variable if assignment[variable]
                    else f"¬{variable}"
                )
            terms.append("(" + " ∧ ".join(literals) + ")")

    if not terms:
        return "⊥"

    return " ∨ ".join(terms)


def canonical_cnf(formula: Formula) -> str:
    variables = sorted(formula.variables())
    clauses = []

    for assignment in generate_assignments(variables):
        if not formula.evaluate(assignment):
            literals = []
            for variable in variables:
                literals.append(
                    f"¬{variable}" if assignment[variable]
                    else variable
                )
            clauses.append("(" + " ∨ ".join(literals) + ")")

    if not clauses:
        return "⊤"

    return " ∧ ".join(clauses)


def demonstrate_normal_forms() -> None:
    print("\n" + "=" * 78)
    print("8. CANONICAL DISJUNCTIVE AND CONJUNCTIVE NORMAL FORMS")
    print("=" * 78)

    p = Var("p")
    q = Var("q")

    formula = And(p, Or(Not(p), q))

    print(f"Formula: {formula}")
    print(f"Canonical DNF: {canonical_dnf(formula)}")
    print(f"Canonical CNF: {canonical_cnf(formula)}")


# ---------------------------------------------------------------------------
# 9. Satisfiability, validity, and counterexamples
# ---------------------------------------------------------------------------


def satisfying_assignments(formula: Formula) -> list[dict[str, bool]]:
    variables = sorted(formula.variables())
    return [
        assignment
        for assignment in generate_assignments(variables)
        if formula.evaluate(assignment)
    ]


def falsifying_assignments(formula: Formula) -> list[dict[str, bool]]:
    variables = sorted(formula.variables())
    return [
        assignment
        for assignment in generate_assignments(variables)
        if not formula.evaluate(assignment)
    ]


def find_counterexample(first: Formula, second: Formula) -> dict[str, bool] | None:
    """
    Find an assignment where two formulas disagree.

    None means no counterexample exists, so the formulas are equivalent.
    """
    variables = sorted(first.variables() | second.variables())

    for assignment in generate_assignments(variables):
        if first.evaluate(assignment) != second.evaluate(assignment):
            return assignment

    return None


def demonstrate_satisfiability() -> None:
    print("\n" + "=" * 78)
    print("9. SATISFIABILITY AND COUNTEREXAMPLES")
    print("=" * 78)

    p = Var("p")
    q = Var("q")

    formulas = [
        ("p ∧ q", And(p, q)),
        ("p ∨ ¬p", Or(p, Not(p))),
        ("p ∧ ¬p", And(p, Not(p))),
    ]

    for name, formula in formulas:
        satisfying = satisfying_assignments(formula)
        print(f"\n{name}")
        print(f"  Satisfiable: {bool(satisfying)}")
        print(f"  Satisfying assignments: {satisfying}")

    first = Implies(p, q)
    second = Or(Not(p), q)
    print("\nEquivalence counterexample search:")
    print(f"  {first} vs {second}")
    print(f"  Counterexample: {find_counterexample(first, second)}")

    third = And(p, q)
    print(f"  {first} vs {third}")
    print(f"  Counterexample: {find_counterexample(first, third)}")


# ---------------------------------------------------------------------------
# 10. Logical consequence and argument validity
# ---------------------------------------------------------------------------
#
# An argument:
#
#   Premise 1
#   Premise 2
#   ...
#   Therefore conclusion
#
# is valid when there is no assignment in which every premise is True and the
# conclusion is False.
#
# This can be tested by checking:
#
#   premises AND ¬conclusion
#
# for satisfiability.
# ---------------------------------------------------------------------------


def argument_is_valid(
    premises: list[Formula],
    conclusion: Formula,
) -> bool:
    variables = set(conclusion.variables())

    for premise in premises:
        variables |= premise.variables()

    variables = sorted(variables)

    for assignment in generate_assignments(variables):
        all_premises_true = all(
            premise.evaluate(assignment)
            for premise in premises
        )

        if all_premises_true and not conclusion.evaluate(assignment):
            return False

    return True


def find_invalid_argument_counterexample(
    premises: list[Formula],
    conclusion: Formula,
) -> dict[str, bool] | None:
    variables = set(conclusion.variables())

    for premise in premises:
        variables |= premise.variables()

    for assignment in generate_assignments(sorted(variables)):
        if (
            all(p.evaluate(assignment) for p in premises)
            and not conclusion.evaluate(assignment)
        ):
            return assignment

    return None


def demonstrate_argument_validity() -> None:
    print("\n" + "=" * 78)
    print("10. ARGUMENT VALIDITY")
    print("=" * 78)

    p = Var("p")
    q = Var("q")

    valid_premises = [
        Implies(p, q),
        p,
    ]
    valid_conclusion = q

    print("Argument:")
    print("  p → q")
    print("  p")
    print("  Therefore q")
    print(
        "Valid:",
        argument_is_valid(valid_premises, valid_conclusion),
    )

    invalid_premises = [
        Implies(p, q),
        q,
    ]
    invalid_conclusion = p

    print("\nArgument:")
    print("  p → q")
    print("  q")
    print("  Therefore p")
    print(
        "Valid:",
        argument_is_valid(invalid_premises, invalid_conclusion),
    )
    print(
        "Counterexample:",
        find_invalid_argument_counterexample(
            invalid_premises,
            invalid_conclusion,
        ),
    )


# ---------------------------------------------------------------------------
# 11. Truth-table optimization using bit patterns
# ---------------------------------------------------------------------------
#
# For n variables, a complete truth table contains 2^n rows. Each formula
# therefore has a truth vector of length 2^n.
#
# The vector can be represented as an integer bit mask. This allows logical
# operations to be performed on many truth-table rows simultaneously.
#
# For example:
#   AND -> bitwise &
#   OR  -> bitwise |
#   NOT -> bitwise complement restricted to n rows
# ---------------------------------------------------------------------------


class TruthVector:
    def __init__(self, variable_count: int, bits: int):
        if variable_count < 0:
            raise ValueError("Variable count cannot be negative")

        self.variable_count = variable_count
        self.row_count = 2 ** variable_count
        self.mask = (1 << self.row_count) - 1
        self.bits = bits & self.mask

    @classmethod
    def from_values(cls, values: list[bool]) -> "TruthVector":
        if not values:
            raise ValueError("A truth vector needs at least one row")

        bits = 0
        for index, value in enumerate(values):
            if value:
                bits |= 1 << index

        variable_count = (len(values)).bit_length() - 1

        if 2 ** variable_count != len(values):
            raise ValueError(
                "Truth-vector length must be a power of two"
            )

        return cls(variable_count, bits)

    def __and__(self, other: "TruthVector") -> "TruthVector":
        self._check_compatible(other)
        return TruthVector(self.variable_count, self.bits & other.bits)

    def __or__(self, other: "TruthVector") -> "TruthVector":
        self._check_compatible(other)
        return TruthVector(self.variable_count, self.bits | other.bits)

    def xor(self, other: "TruthVector") -> "TruthVector":
        self._check_compatible(other)
        return TruthVector(self.variable_count, self.bits ^ other.bits)

    def negate(self) -> "TruthVector":
        return TruthVector(
            self.variable_count,
            (~self.bits) & self.mask,
        )

    def implies(self, other: "TruthVector") -> "TruthVector":
        self._check_compatible(other)
        return self.negate() | other

    def equivalent(self, other: "TruthVector") -> bool:
        self._check_compatible(other)
        return self.bits == other.bits

    def values(self) -> list[bool]:
        return [
            bool(self.bits & (1 << index))
            for index in range(self.row_count)
        ]

    def _check_compatible(self, other: "TruthVector") -> None:
        if self.variable_count != other.variable_count:
            raise ValueError(
                "Truth vectors must contain the same number of rows"
            )

    def __str__(self) -> str:
        return "".join("T" if value else "F" for value in self.values())


def variable_truth_vector(
    variable_name: str,
    variables: list[str],
) -> TruthVector:
    if variable_name not in variables:
        raise ValueError(f"Unknown variable {variable_name}")

    values = [
        assignment[variable_name]
        for assignment in generate_assignments(variables)
    ]

    return TruthVector.from_values(values)


def demonstrate_truth_vectors() -> None:
    print("\n" + "=" * 78)
    print("11. TRUTH-TABLE BIT VECTORS")
    print("=" * 78)

    variables = ["p", "q"]
    p = variable_truth_vector("p", variables)
    q = variable_truth_vector("q", variables)

    print(f"p = {p}")
    print(f"q = {q}")
    print(f"p ∧ q = {p & q}")
    print(f"p ∨ q = {p | q}")
    print(f"¬p = {p.negate()}")
    print(f"p → q = {p.implies(q)}")
    print(f"p ↔ q = {p.implies(q) & q.implies(p)}")


# ---------------------------------------------------------------------------
# 12. Edge cases and parser validation
# ---------------------------------------------------------------------------


def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("12. EDGE CASES AND ERROR HANDLING")
    print("=" * 78)

    invalid_expressions = [
        "",
        "p &",
        "p ->",
        "(p & q",
        "p && q",
        "p @ q",
    ]

    for expression in invalid_expressions:
        try:
            parse_formula(expression)
        except ValueError as error:
            print(f"Rejected {expression!r}: {error}")

    print("\nSingle-variable tautology:")
    formula = parse_formula("p | ~p")
    print(f"{formula} -> {classify_expression(['p'], formula.evaluate)[0]}")

    print("\nConstant-like behavior:")
    tautology = parse_formula("p | ~p")
    contradiction = parse_formula("p & ~p")
    print(f"DNF of tautology:     {canonical_dnf(tautology)}")
    print(f"CNF of contradiction: {canonical_cnf(contradiction)}")


# ---------------------------------------------------------------------------
# 13. Performance analysis
# ---------------------------------------------------------------------------
#
# Exhaustive truth-table evaluation has exponential growth:
#
#   n variables -> 2^n rows
#
# This is practical for small n and becomes expensive as n increases.
# Formula evaluation also depends on the number of operations in the formula.
#
# Memory can become a concern when every row and every intermediate column
# is stored. Streaming rows reduces memory usage, while bit-vector evaluation
# can process many rows in parallel.
# ---------------------------------------------------------------------------


def truth_table_complexity_demo() -> None:
    print("\n" + "=" * 78)
    print("13. PERFORMANCE AND COMPLEXITY")
    print("=" * 78)

    print(
        "For n variables, an exhaustive truth table contains 2^n rows.\n"
    )

    for n in range(0, 21):
        print(f"n={n:2d}: {2 ** n:>8,d} rows")

    print(
        "\nThis exponential growth is a central limitation of naive exhaustive "
        "truth-table methods."
    )


# ---------------------------------------------------------------------------
# 14. A complete interactive evaluator
# ---------------------------------------------------------------------------


def evaluate_user_expression(expression: str) -> None:
    formula = parse_formula(expression)
    variables = sorted(formula.variables())

    classification, values = classify_expression(
        variables,
        formula.evaluate,
    )

    print(f"\nParsed formula: {formula}")
    print(f"Variables: {', '.join(variables) or '(none)'}")
    print(f"Classification: {classification}")
    print(f"Truth values: {''.join('T' if v else 'F' for v in values)}")

    print_truth_table(
        variables,
        str(formula),
        formula.evaluate,
    )

    print(f"\nCanonical DNF: {canonical_dnf(formula)}")
    print(f"Canonical CNF: {canonical_cnf(formula)}")


def interactive_mode() -> None:
    print("\n" + "=" * 78)
    print("14. INTERACTIVE PROPOSITIONAL LOGIC EVALUATOR")
    print("=" * 78)

    print(
        "\nEnter formulas using:"
        "\n  ! or ~   NOT"
        "\n  &        AND"
        "\n  |        OR"
        "\n  ^        XOR"
        "\n  ->       IMPLIES"
        "\n  <->      IFF"
        "\n  ( )      grouping"
        "\nType 'quit' to exit."
    )

    while True:
        try:
            expression = input("\nFormula> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if expression.lower() in {"quit", "exit"}:
            break

        if not expression:
            print("Please enter a formula.")
            continue

        try:
            evaluate_user_expression(expression)
        except (ValueError, KeyError) as error:
            print(f"Error: {error}")


# ---------------------------------------------------------------------------
# 15. Integrated study demonstrations
# ---------------------------------------------------------------------------


def run_all_demonstrations() -> None:
    demonstrate_basic_operators()
    demonstrate_truth_table_construction()
    demonstrate_classification()
    demonstrate_formula_tree()
    demonstrate_parser()
    demonstrate_equivalence()
    demonstrate_logical_laws()
    demonstrate_normal_forms()
    demonstrate_satisfiability()
    demonstrate_argument_validity()
    demonstrate_truth_vectors()
    demonstrate_edge_cases()
    truth_table_complexity_demo()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 78)
    print("TRUTH TABLES: A COMPLETE PROPOSITIONAL LOGIC STUDY PROGRAM")
    print("=" * 78)

    run_all_demonstrations()

    print("\n" + "=" * 78)
    print("INTERACTIVE MODE")
    print("=" * 78)
    print(
        "The interactive evaluator is disabled by default so the script can "
        "run unattended in automated environments."
    )
    print(
        "Set RUN_INTERACTIVE = True in main() if interactive input is desired."
    )

    RUN_INTERACTIVE = False

    if RUN_INTERACTIVE:
        interactive_mode()


if __name__ == "__main__":
    main()
