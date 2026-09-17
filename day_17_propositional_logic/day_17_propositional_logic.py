"""
Propositional Logic: AND, OR, NOT, Implication, Biconditional, and Precedence

A standalone study and executable demonstration covering propositional logic from
fundamentals through practical and advanced implementation techniques.

The examples use Boolean propositions represented by True and False.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


# =============================================================================
# 1. FUNDAMENTALS
# =============================================================================

print("=" * 80)
print("PROPOSITIONAL LOGIC")
print("=" * 80)


def explain_proposition():
    """
    A proposition is a declarative statement that has exactly one truth value:
    True or False.

    Examples:
        "5 is greater than 2"       -> True
        "10 is less than 3"         -> False

    Questions, commands, and ambiguous expressions are not propositions in the
    ordinary propositional-logic sense.
    """
    propositions = {
        "P: 5 > 2": 5 > 2,
        "Q: 10 < 3": 10 < 3,
        "R: Python is a programming language": True,
    }

    for statement, value in propositions.items():
        print(f"{statement:<42} = {value}")


explain_proposition()


# =============================================================================
# 2. BOOLEAN VALUES
# =============================================================================

print("\n" + "=" * 80)
print("BOOLEAN VALUES")
print("=" * 80)

P = True
Q = False

print("P =", P)
print("Q =", Q)

# Python's Boolean operators correspond closely to propositional connectives:
# and -> logical AND
# or  -> logical OR
# not -> logical NOT

print("P AND Q =", P and Q)
print("P OR Q  =", P or Q)
print("NOT P   =", not P)


# =============================================================================
# 3. LOGICAL AND
# =============================================================================

print("\n" + "=" * 80)
print("AND")
print("=" * 80)


def logical_and(p: bool, q: bool) -> bool:
    """
    Logical conjunction.

    Symbol:
        P ∧ Q

    Meaning:
        P and Q must both be true.

    Truth condition:
        P ∧ Q is true exactly when P=True and Q=True.
    """
    return p and q


for p, q in product([False, True], repeat=2):
    print(f"{p!s:5} AND {q!s:5} = {logical_and(p, q)}")


# =============================================================================
# 4. LOGICAL OR
# =============================================================================

print("\n" + "=" * 80)
print("OR")
print("=" * 80)


def logical_or(p: bool, q: bool) -> bool:
    """
    Logical disjunction.

    Symbol:
        P ∨ Q

    In propositional logic this is inclusive OR:
    the result is true when at least one proposition is true.

    Therefore:
        True OR True = True
        True OR False = True
        False OR True = True
        False OR False = False
    """
    return p or q


for p, q in product([False, True], repeat=2):
    print(f"{p!s:5} OR  {q!s:5} = {logical_or(p, q)}")


# =============================================================================
# 5. LOGICAL NOT
# =============================================================================

print("\n" + "=" * 80)
print("NOT")
print("=" * 80)


def logical_not(p: bool) -> bool:
    """
    Negation.

    Symbol:
        ¬P

    NOT reverses the truth value.
    """
    return not p


for p in [False, True]:
    print(f"NOT {p!s:5} = {logical_not(p)}")


# =============================================================================
# 6. IMPLICATION
# =============================================================================

print("\n" + "=" * 80)
print("IMPLICATION")
print("=" * 80)


def implies(p: bool, q: bool) -> bool:
    """
    Material implication.

    Symbol:
        P → Q

    Definition:
        P → Q is equivalent to ¬P ∨ Q.

    The only false case is:
        P=True and Q=False.

    Important:
        An implication does NOT say that P causes Q.
        It is a truth-functional logical connective.
    """
    return (not p) or q


for p, q in product([False, True], repeat=2):
    print(f"{p!s:5} -> {q!s:5} = {implies(p, q)}")

print("\nEquivalent implementation:")
for p, q in product([False, True], repeat=2):
    print(
        f"P={p!s:5}, Q={q!s:5}, "
        f"P->Q={implies(p, q)}, "
        f"NOT P OR Q={(not p) or q}"
    )


# =============================================================================
# 7. BICONDITIONAL
# =============================================================================

print("\n" + "=" * 80)
print("BICONDITIONAL")
print("=" * 80)


def iff(p: bool, q: bool) -> bool:
    """
    Biconditional.

    Symbol:
        P ↔ Q

    Meaning:
        P if and only if Q.

    It is true when P and Q have the same truth value.

    Equivalent forms:
        (P → Q) ∧ (Q → P)
        (P ∧ Q) ∨ (¬P ∧ ¬Q)
        P == Q
    """
    return p == q


for p, q in product([False, True], repeat=2):
    print(f"{p!s:5} <-> {q!s:5} = {iff(p, q)}")


# =============================================================================
# 8. STANDARD TRUTH TABLE
# =============================================================================

print("\n" + "=" * 80)
print("CORE TRUTH TABLE")
print("=" * 80)

print(" P     Q   | NOT P | P AND Q | P OR Q | P -> Q | P <-> Q")
print("-" * 62)

for p, q in product([False, True], repeat=2):
    print(
        f" {str(p):5} {str(q):5} | "
        f"{str(not p):5} | "
        f"{str(p and q):7} | "
        f"{str(p or q):6} | "
        f"{str(implies(p, q)):6} | "
        f"{str(iff(p, q)):7}"
    )


# =============================================================================
# 9. OPERATOR PRECEDENCE
# =============================================================================

print("\n" + "=" * 80)
print("PRECEDENCE")
print("=" * 80)

"""
For the logical language used in this project, a conventional precedence order
is:

    1. NOT          ¬P
    2. AND          P ∧ Q
    3. OR           P ∨ Q
    4. IMPLICATION  P → Q
    5. BICONDITIONAL P ↔ Q

Parentheses override precedence.

For example:

    ¬P ∨ Q ∧ R

is conventionally read as:

    (¬P) ∨ (Q ∧ R)

not:

    (¬P ∨ Q) ∧ R

Implication is normally right-associative:

    P → Q → R

is read as:

    P → (Q → R)

unless parentheses specify otherwise.
"""

P, Q, R = True, False, True

expression_without_parentheses = (not P) or (Q and R)
expression_with_parentheses = ((not P) or Q) and R

print("P =", P, "Q =", Q, "R =", R)
print("(NOT P) OR (Q AND R) =", expression_without_parentheses)
print("((NOT P) OR Q) AND R   =", expression_with_parentheses)

right_associative = implies(P, implies(Q, R))
left_grouped = implies(implies(P, Q), R)

print("P -> (Q -> R) =", right_associative)
print("(P -> Q) -> R =", left_grouped)


# =============================================================================
# 10. CUSTOM PROPOSITIONAL EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("COMPOSITE EXPRESSIONS")
print("=" * 80)

def expression_1(p: bool, q: bool, r: bool) -> bool:
    """
    ¬P ∨ (Q ∧ R)
    """
    return (not p) or (q and r)


def expression_2(p: bool, q: bool, r: bool) -> bool:
    """
    (P ∨ Q) → R
    """
    return implies(p or q, r)


def expression_3(p: bool, q: bool, r: bool) -> bool:
    """
    (P → Q) ∧ (Q → R)
    """
    return implies(p, q) and implies(q, r)


for values in product([False, True], repeat=3):
    p, q, r = values
    print(
        f"P={p}, Q={q}, R={r} | "
        f"E1={expression_1(p,q,r)} | "
        f"E2={expression_2(p,q,r)} | "
        f"E3={expression_3(p,q,r)}"
    )


# =============================================================================
# 11. TRUTH TABLE GENERATOR
# =============================================================================

print("\n" + "=" * 80)
print("GENERIC TRUTH TABLE GENERATOR")
print("=" * 80)


def truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[dict[str, bool]]:
    """
    Generate every possible Boolean assignment and evaluate an expression.

    With n variables there are exactly 2^n rows.
    """
    rows = []

    for values in product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        result = bool(expression(*values))
        assignment["result"] = result
        rows.append(assignment)

    return rows


rows = truth_table(
    ["P", "Q", "R"],
    lambda p, q, r: implies(p and q, r),
)

for row in rows:
    print(row)


# =============================================================================
# 12. TAUTOLOGY, CONTRADICTION, CONTINGENCY
# =============================================================================

print("\n" + "=" * 80)
print("TAUTOLOGY, CONTRADICTION, CONTINGENCY")
print("=" * 80)


def classify_expression(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> str:
    """
    Classify a propositional formula.

    Tautology:
        true under every possible assignment.

    Contradiction:
        false under every possible assignment.

    Contingency:
        true for some assignments and false for others.
    """
    results = [
        bool(expression(*values))
        for values in product([False, True], repeat=len(variables))
    ]

    if all(results):
        return "tautology"
    if not any(results):
        return "contradiction"
    return "contingency"


tautology = lambda p: p or not p
contradiction = lambda p: p and not p
contingency = lambda p: p

print("P OR NOT P:", classify_expression(["P"], tautology))
print("P AND NOT P:", classify_expression(["P"], contradiction))
print("P:", classify_expression(["P"], contingency))


# =============================================================================
# 13. LOGICAL EQUIVALENCE
# =============================================================================

print("\n" + "=" * 80)
print("LOGICAL EQUIVALENCE")
print("=" * 80)


def equivalent(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
) -> bool:
    """
    Two formulas are logically equivalent when they have identical truth values
    for every possible assignment.
    """
    for values in product([False, True], repeat=len(variables)):
        if bool(first(*values)) != bool(second(*values)):
            return False
    return True


print(
    "P -> Q equivalent to NOT P OR Q:",
    equivalent(
        ["P", "Q"],
        implies,
        lambda p, q: (not p) or q,
    ),
)

print(
    "P <-> Q equivalent to (P -> Q) AND (Q -> P):",
    equivalent(
        ["P", "Q"],
        iff,
        lambda p, q: implies(p, q) and implies(q, p),
    ),
)


# =============================================================================
# 14. IMPORTANT LOGICAL LAWS
# =============================================================================

print("\n" + "=" * 80)
print("LOGICAL LAWS")
print("=" * 80)


def demonstrate_laws():
    """
    Important equivalences for two Boolean variables.

    Identity:
        P ∧ True = P
        P ∨ False = P

    Domination:
        P ∨ True = True
        P ∧ False = False

    Idempotent:
        P ∨ P = P
        P ∧ P = P

    Complement:
        P ∨ ¬P = True
        P ∧ ¬P = False

    Double negation:
        ¬¬P = P

    De Morgan:
        ¬(P ∧ Q) = ¬P ∨ ¬Q
        ¬(P ∨ Q) = ¬P ∧ ¬Q

    Absorption:
        P ∨ (P ∧ Q) = P
        P ∧ (P ∨ Q) = P
    """
    for p, q in product([False, True], repeat=2):
        assert (not (p and q)) == ((not p) or (not q))
        assert (not (p or q)) == ((not p) and (not q))
        assert (p or (p and q)) == p
        assert (p and (p or q)) == p

    print("De Morgan's laws verified.")
    print("Absorption laws verified.")


demonstrate_laws()


# =============================================================================
# 15. CONVERSE, INVERSE, CONTRAPOSITIVE
# =============================================================================

print("\n" + "=" * 80)
print("IMPLICATION RELATIONSHIPS")
print("=" * 80)


def implication_forms(p: bool, q: bool) -> dict[str, bool]:
    """
    Given P -> Q:

        Original:       P -> Q
        Converse:       Q -> P
        Inverse:        ¬P -> ¬Q
        Contrapositive: ¬Q -> ¬P

    An implication is logically equivalent to its contrapositive.

    The converse and inverse are logically equivalent to each other, but they
    are not generally equivalent to the original implication.
    """
    return {
        "original": implies(p, q),
        "converse": implies(q, p),
        "inverse": implies(not p, not q),
        "contrapositive": implies(not q, not p),
    }


for p, q in product([False, True], repeat=2):
    print(f"P={p}, Q={q} -> {implication_forms(p, q)}")


# =============================================================================
# 16. NECESSARY AND SUFFICIENT CONDITIONS
# =============================================================================

print("\n" + "=" * 80)
print("NECESSARY AND SUFFICIENT CONDITIONS")
print("=" * 80)

"""
For P -> Q:

    P is sufficient for Q.
    Q is necessary for P.

For example:

    "Being divisible by 4" -> "Being even"

Divisibility by 4 is sufficient for being even.
Being even is necessary for divisibility by 4.

The reverse implication is not automatically valid.
"""


# =============================================================================
# 17. SHORT-CIRCUIT EVALUATION
# =============================================================================

print("\n" + "=" * 80)
print("SHORT-CIRCUIT EVALUATION")
print("=" * 80)


def dangerous_operation() -> bool:
    print("dangerous_operation() was evaluated")
    raise RuntimeError("This function should not have been evaluated")


# False AND anything is false, so Python does not evaluate the second operand.
safe_result = False and dangerous_operation()
print("False AND dangerous_operation() =", safe_result)

# True OR anything is true, so Python does not evaluate the second operand.
safe_result = True or dangerous_operation()
print("True OR dangerous_operation() =", safe_result)


# =============================================================================
# 18. LOGICAL VS BITWISE OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("LOGICAL VS BITWISE OPERATORS")
print("=" * 80)

"""
Python:
    and, or, not      -> logical Boolean operators
    &, |, ~           -> bitwise operators

They are not interchangeable.

For integers:
    5 & 3
performs bitwise AND.

For Boolean operands:
    True & False
also produces a Boolean result, but uses bitwise semantics.

Logical operators also short-circuit; bitwise operators evaluate operands.
"""

print("Logical: True and False =", True and False)
print("Bitwise: True & False   =", True & False)
print("Integer 5 & 3            =", 5 & 3)


# =============================================================================
# 19. AN EXPRESSION TREE
# =============================================================================

print("\n" + "=" * 80)
print("EXPRESSION TREE")
print("=" * 80)


@dataclass
class Literal:
    name: str
    value: bool

    def evaluate(self) -> bool:
        return self.value


@dataclass
class Not:
    operand: "Node"

    def evaluate(self) -> bool:
        return not self.operand.evaluate()


@dataclass
class And:
    left: "Node"
    right: "Node"

    def evaluate(self) -> bool:
        return self.left.evaluate() and self.right.evaluate()


@dataclass
class Or:
    left: "Node"
    right: "Node"

    def evaluate(self) -> bool:
        return self.left.evaluate() or self.right.evaluate()


@dataclass
class Implication:
    left: "Node"
    right: "Node"

    def evaluate(self) -> bool:
        return (not self.left.evaluate()) or self.right.evaluate()


@dataclass
class Biconditional:
    left: "Node"
    right: "Node"

    def evaluate(self) -> bool:
        return self.left.evaluate() == self.right.evaluate()


Node = Literal | Not | And | Or | Implication | Biconditional

tree: Node = Or(
    Not(Literal("P", True)),
    And(Literal("Q", False), Literal("R", True)),
)

print("Expression tree result:", tree.evaluate())


# =============================================================================
# 20. FORMULA REPRESENTATION
# =============================================================================

print("\n" + "=" * 80)
print("REUSABLE FORMULA REPRESENTATION")
print("=" * 80)


@dataclass(frozen=True)
class Formula:
    """
    A small callable wrapper for propositional formulas.

    This allows formulas to be composed without repeatedly writing anonymous
    functions.
    """

    name: str
    evaluator: Callable[..., bool]

    def evaluate(self, *values: bool) -> bool:
        return bool(self.evaluator(*values))


P_formula = Formula("P", lambda p: p)
not_p_formula = Formula("NOT P", lambda p: not p)

print(P_formula.evaluate(True))
print(not_p_formula.evaluate(True))


# =============================================================================
# 21. NORMAL FORMS
# =============================================================================

print("\n" + "=" * 80)
print("CNF AND DNF")
print("=" * 80)

"""
Conjunctive Normal Form (CNF):

    AND of OR clauses

Example:
    (P OR Q) AND (NOT P OR R)

Disjunctive Normal Form (DNF):

    OR of AND terms

Example:
    (P AND Q) OR (NOT P AND R)

CNF is central to SAT solving and many constraint-solving systems.
"""


def cnf_example(p: bool, q: bool, r: bool) -> bool:
    return (p or q) and ((not p) or r)


def dnf_example(p: bool, q: bool, r: bool) -> bool:
    return (p and q) or ((not p) and r)


print("CNF:", classify_expression(["P", "Q", "R"], cnf_example))
print("DNF:", classify_expression(["P", "Q", "R"], dnf_example))


# =============================================================================
# 22. SAT-STYLE SEARCH
# =============================================================================

print("\n" + "=" * 80)
print("SAT-STYLE SATISFIABILITY SEARCH")
print("=" * 80)


def satisfying_assignments(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[dict[str, bool]]:
    """
    Find assignments that make a formula true.

    Brute-force search requires O(2^n) evaluations for n independent variables.
    """
    solutions = []

    for values in product([False, True], repeat=len(variables)):
        if expression(*values):
            solutions.append(dict(zip(variables, values)))

    return solutions


solutions = satisfying_assignments(
    ["P", "Q", "R"],
    lambda p, q, r: implies(p and q, r),
)

print("Number of satisfying assignments:", len(solutions))
for solution in solutions:
    print(solution)


# =============================================================================
# 23. COUNTEREXAMPLE SEARCH
# =============================================================================

print("\n" + "=" * 80)
print("COUNTEREXAMPLE SEARCH")
print("=" * 80)


def find_counterexample(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
) -> dict[str, bool] | None:
    """
    If two expressions are not equivalent, return an assignment on which they
    differ. Such an assignment is a counterexample to equivalence.
    """
    for values in product([False, True], repeat=len(variables)):
        if bool(first(*values)) != bool(second(*values)):
            return dict(zip(variables, values))
    return None


counterexample = find_counterexample(
    ["P", "Q"],
    implies,
    lambda p, q: implies(q, p),
)

print("Counterexample to P->Q == Q->P:", counterexample)


# =============================================================================
# 24. PRACTICAL ACCESS-CONTROL EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("PRACTICAL ACCESS-CONTROL EXAMPLE")
print("=" * 80)

"""
Suppose an internal system grants access when:

    authenticated AND (admin OR owner)

Let:
    A = authenticated
    D = administrator
    O = resource owner

Access:
    A ∧ (D ∨ O)
"""


def can_access(authenticated: bool, admin: bool, owner: bool) -> bool:
    return authenticated and (admin or owner)


access_cases = [
    (False, False, False),
    (False, True, True),
    (True, False, False),
    (True, False, True),
    (True, True, False),
]

for authenticated, admin, owner in access_cases:
    print(
        f"authenticated={authenticated}, admin={admin}, owner={owner} "
        f"-> access={can_access(authenticated, admin, owner)}"
    )


# =============================================================================
# 25. PRACTICAL VALIDATION EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("PRACTICAL VALIDATION EXAMPLE")
print("=" * 80)

"""
A transaction can proceed when:

    authenticated AND verified AND (employee OR trusted_service)

This illustrates how propositions can model authorization policy conditions.
"""


def transaction_allowed(
    authenticated: bool,
    verified: bool,
    employee: bool,
    trusted_service: bool,
) -> bool:
    return authenticated and verified and (employee or trusted_service)


print(
    transaction_allowed(
        authenticated=True,
        verified=True,
        employee=False,
        trusted_service=True,
    )
)


# =============================================================================
# 26. EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("EDGE CASES")
print("=" * 80)

print("NOT False =", not False)
print("NOT True =", not True)
print("False AND False =", False and False)
print("True AND True =", True and True)
print("False OR False =", False or False)
print("True OR True =", True or True)

print("False -> False =", implies(False, False))
print("False -> True  =", implies(False, True))
print("True -> False  =", implies(True, False))
print("True -> True   =", implies(True, True))

print("False <-> False =", iff(False, False))
print("False <-> True  =", iff(False, True))
print("True <-> False  =", iff(True, False))
print("True <-> True   =", iff(True, True))


# =============================================================================
# 27. COMMON MISTAKES
# =============================================================================

print("\n" + "=" * 80)
print("COMMON MISTAKES")
print("=" * 80)

"""
1. Confusing implication with causation.

   P -> Q is false only when P is true and Q is false.

2. Assuming P -> Q means Q -> P.

   This is invalid unless an additional biconditional relationship is known.

3. Confusing OR with exclusive OR.

   P OR Q is true when both are true.
   XOR is true only when exactly one is true.

4. Ignoring precedence.

   Use parentheses when readability or correctness could be affected.

5. Confusing equality with logical equivalence in different contexts.

   In Python, == compares values.
   In propositional logic, equivalence means identical truth behavior for every
   assignment.

6. Forgetting short-circuit behavior in programming languages.

7. Treating implication as a causal statement.
"""


def xor(p: bool, q: bool) -> bool:
    """Exclusive OR: true exactly when the operands differ."""
    return p != q


print("True XOR True =", xor(True, True))
print("True XOR False =", xor(True, False))


# =============================================================================
# 28. PRECEDENCE TESTS
# =============================================================================

print("\n" + "=" * 80)
print("PRECEDENCE TESTS")
print("=" * 80)

P, Q, R = True, False, False

print("NOT P OR Q AND R:", (not P) or (Q and R))
print("(NOT P OR Q) AND R:", ((not P) or Q) and R)
print("NOT (P OR Q) AND R:", (not (P or Q)) and R)

"""
When formulas become difficult to read, explicit parentheses are preferable
even when formal precedence already determines the result.
"""


# =============================================================================
# 29. FORMULA SIZE AND BRUTE-FORCE COST
# =============================================================================

print("\n" + "=" * 80)
print("TRUTH-TABLE GROWTH")
print("=" * 80)

for variable_count in range(1, 11):
    rows = 2 ** variable_count
    print(
        f"{variable_count:2} variables -> "
        f"{rows:4} truth-table assignments"
    )

"""
A truth table with n independent variables contains 2^n assignments.

This exponential growth is a fundamental reason why naive brute-force Boolean
reasoning becomes expensive for large formulas.
"""


# =============================================================================
# 30. TESTING THE CORE OPERATORS
# =============================================================================

print("\n" + "=" * 80)
print("SELF-TESTS")
print("=" * 80)


def run_self_tests() -> None:
    assert logical_and(True, True) is True
    assert logical_and(True, False) is False
    assert logical_and(False, True) is False
    assert logical_and(False, False) is False

    assert logical_or(False, False) is False
    assert logical_or(True, False) is True
    assert logical_or(False, True) is True
    assert logical_or(True, True) is True

    assert logical_not(True) is False
    assert logical_not(False) is True

    assert implies(False, False) is True
    assert implies(False, True) is True
    assert implies(True, False) is False
    assert implies(True, True) is True

    assert iff(False, False) is True
    assert iff(False, True) is False
    assert iff(True, False) is False
    assert iff(True, True) is True

    for p, q in product([False, True], repeat=2):
        assert implies(p, q) == implies(not q, not p)
        assert iff(p, q) == (implies(p, q) and implies(q, p))

    for p, q in product([False, True], repeat=2):
        assert not (p and q) == ((not p) or (not q))
        assert not (p or q) == ((not p) and (not q))

    print("All propositional-logic tests passed.")


run_self_tests()


# =============================================================================
# 31. ADVANCED: SYMBOLIC FORMULA AST
# =============================================================================

print("\n" + "=" * 80)
print("ADVANCED SYMBOLIC FORMULA AST")
print("=" * 80)


class Symbolic:
    """
    A symbolic propositional expression.

    Unlike the earlier Literal class, this class stores variable names and can
    evaluate the same expression under many different assignments.
    """

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Variable(Symbolic):
    name: str

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        if self.name not in assignment:
            raise KeyError(f"Missing value for variable {self.name!r}")
        return bool(assignment[self.name])

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class UnaryNot(Symbolic):
    operand: Symbolic

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        return not self.operand.evaluate(assignment)

    def __str__(self) -> str:
        return f"¬({self.operand})"


@dataclass(frozen=True)
class Binary(Symbolic):
    left: Symbolic
    right: Symbolic
    operator: str

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        left_value = self.left.evaluate(assignment)
        right_value = self.right.evaluate(assignment)

        if self.operator == "AND":
            return left_value and right_value
        if self.operator == "OR":
            return left_value or right_value
        if self.operator == "IMPLIES":
            return (not left_value) or right_value
        if self.operator == "IFF":
            return left_value == right_value

        raise ValueError(f"Unknown operator: {self.operator}")

    def __str__(self) -> str:
        symbols = {
            "AND": "∧",
            "OR": "∨",
            "IMPLIES": "→",
            "IFF": "↔",
        }
        symbol = symbols[self.operator]
        return f"({self.left} {symbol} {self.right})"


p = Variable("P")
q = Variable("Q")
r = Variable("R")

advanced_formula = Binary(
    UnaryNot(p),
    Binary(q, r, "AND"),
    "OR",
)

print("Formula:", advanced_formula)

for assignment in truth_table(
    ["P", "Q", "R"],
    lambda p_value, q_value, r_value: advanced_formula.evaluate(
        {"P": p_value, "Q": q_value, "R": r_value}
    ),
):
    print(assignment)


# =============================================================================
# 32. ADVANCED: ERROR HANDLING
# =============================================================================

print("\n" + "=" * 80)
print("ERROR HANDLING")
print("=" * 80)

try:
    advanced_formula.evaluate({"P": True, "Q": False})
except KeyError as error:
    print("Handled missing variable:", error)


# =============================================================================
# 33. ADVANCED: PROPOSITIONAL ENTAILMENT
# =============================================================================

print("\n" + "=" * 80)
print("PROPOSITIONAL ENTAILMENT")
print("=" * 80)


def entails(
    variables: Sequence[str],
    premise: Callable[..., bool],
    conclusion: Callable[..., bool],
) -> bool:
    """
    Determine whether premise entails conclusion.

    P entails Q iff there is no assignment for which:
        P is true and Q is false.

    This is equivalent to checking whether:
        P -> Q
    is a tautology.
    """
    for values in product([False, True], repeat=len(variables)):
        if premise(*values) and not conclusion(*values):
            return False
    return True


print(
    "(P AND Q) entails P:",
    entails(
        ["P", "Q"],
        lambda p, q: p and q,
        lambda p, q: p,
    ),
)

print(
    "P entails (P OR Q):",
    entails(
        ["P", "Q"],
        lambda p, q: p,
        lambda p, q: p or q,
    ),
)

print(
    "P entails Q:",
    entails(
        ["P", "Q"],
        lambda p, q: p,
        lambda p, q: q,
    ),
)


# =============================================================================
# 34. ADVANCED: LOGICAL ARGUMENT VALIDITY
# =============================================================================

print("\n" + "=" * 80)
print("ARGUMENT VALIDITY")
print("=" * 80)


def argument_is_valid(
    variables: Sequence[str],
    premises: Sequence[Callable[..., bool]],
    conclusion: Callable[..., bool],
) -> bool:
    """
    An argument is valid when every assignment satisfying all premises also
    satisfies the conclusion.
    """
    for values in product([False, True], repeat=len(variables)):
        if all(premise(*values) for premise in premises):
            if not conclusion(*values):
                return False

    return True


valid_argument = argument_is_valid(
    ["P", "Q"],
    [
        lambda p, q: implies(p, q),
        lambda p, q: p,
    ],
    lambda p, q: q,
)

invalid_argument = argument_is_valid(
    ["P", "Q"],
    [
        lambda p, q: implies(p, q),
        lambda p, q: q,
    ],
    lambda p, q: p,
)

print("Modus ponens argument valid:", valid_argument)
print("Converse-style argument valid:", invalid_argument)


# =============================================================================
# 35. ADVANCED: COMMON INFERENCE PATTERNS
# =============================================================================

print("\n" + "=" * 80)
print("INFERENCE PATTERNS")
print("=" * 80)

"""
Modus Ponens:
    P → Q
    P
    therefore Q

Modus Tollens:
    P → Q
    ¬Q
    therefore ¬P

Hypothetical Syllogism:
    P → Q
    Q → R
    therefore P → R

Disjunctive Syllogism:
    P ∨ Q
    ¬P
    therefore Q
"""

modus_ponens = argument_is_valid(
    ["P", "Q"],
    [lambda p, q: implies(p, q), lambda p, q: p],
    lambda p, q: q,
)

modus_tollens = argument_is_valid(
    ["P", "Q"],
    [lambda p, q: implies(p, q), lambda p, q: not q],
    lambda p, q: not p,
)

hypothetical_syllogism = argument_is_valid(
    ["P", "Q", "R"],
    [
        lambda p, q, r: implies(p, q),
        lambda p, q, r: implies(q, r),
    ],
    lambda p, q, r: implies(p, r),
)

disjunctive_syllogism = argument_is_valid(
    ["P", "Q"],
    [lambda p, q: p or q, lambda p, q: not p],
    lambda p, q: q,
)

print("Modus Ponens:", modus_ponens)
print("Modus Tollens:", modus_tollens)
print("Hypothetical Syllogism:", hypothetical_syllogism)
print("Disjunctive Syllogism:", disjunctive_syllogism)


# =============================================================================
# 36. ADVANCED: BOOLEAN FUNCTION ENUMERATION
# =============================================================================

print("\n" + "=" * 80)
print("BOOLEAN FUNCTION ENUMERATION")
print("=" * 80)

"""
For n Boolean input variables there are:

    2^(2^n)

possible Boolean functions.

For n=2:
    2^(2^2) = 16 functions.

For n=3:
    2^(2^3) = 256 functions.

This demonstrates why the space of Boolean functions grows much faster than
the number of input assignments.
"""

for n in range(1, 4):
    functions = 2 ** (2 ** n)
    print(f"{n} variables -> {functions} possible Boolean functions")


# =============================================================================
# 37. ADVANCED: EXPLICIT PRECEDENCE MODEL
# =============================================================================

print("\n" + "=" * 80)
print("EXPLICIT PRECEDENCE MODEL")
print("=" * 80)

"""
A parser for propositional logic normally separates lexical analysis, parsing,
and evaluation.

A conventional grammar can be organized from highest precedence to lowest:

    expression
        := biconditional

    biconditional
        := implication ("<->" implication)*

    implication
        := disjunction ("->" implication)?

    disjunction
        := conjunction ("OR" conjunction)*

    conjunction
        := negation ("AND" negation)*

    negation
        := "NOT" negation | atom

    atom
        := variable | "(" expression ")"

This structure makes precedence explicit rather than relying on host-language
operator behavior.
"""


# =============================================================================
# 38. MINI TOKENIZER AND PARSER
# =============================================================================

print("\n" + "=" * 80)
print("MINI PROPOSITIONAL-LOGIC PARSER")
print("=" * 80)


class ParseError(ValueError):
    """Raised when a propositional expression cannot be parsed."""


def tokenize(text: str) -> list[str]:
    """
    Convert an expression into tokens.

    Supported syntax:
        NOT
        AND
        OR
        ->
        <->
        (
        )
        variable names such as P, Q, R, user_authenticated
    """
    tokens: list[str] = []
    index = 0

    while index < len(text):
        character = text[index]

        if character.isspace():
            index += 1
            continue

        if text.startswith("<->", index):
            tokens.append("<->")
            index += 3
            continue

        if text.startswith("->", index):
            tokens.append("->")
            index += 2
            continue

        if character in "()":
            tokens.append(character)
            index += 1
            continue

        if character.isalpha() or character == "_":
            start = index
            index += 1

            while index < len(text):
                current = text[index]
                if current.isalnum() or current == "_":
                    index += 1
                else:
                    break

            tokens.append(text[start:index])
            continue

        raise ParseError(f"Unexpected character {character!r}")

    return tokens


class Parser:
    """
    Recursive-descent parser implementing the precedence hierarchy described
    above.
    """

    def __init__(self, tokens: Sequence[str]):
        self.tokens = list(tokens)
        self.position = 0

    def current(self) -> str | None:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self, expected: str | None = None) -> str:
        token = self.current()

        if token is None:
            raise ParseError("Unexpected end of expression")

        if expected is not None and token.upper() != expected.upper():
            raise ParseError(
                f"Expected {expected!r}, found {token!r}"
            )

        self.position += 1
        return token

    def parse(self) -> Symbolic:
        result = self.parse_biconditional()

        if self.current() is not None:
            raise ParseError(
                f"Unexpected token {self.current()!r}"
            )

        return result

    def parse_biconditional(self) -> Symbolic:
        left = self.parse_implication()

        while self.current() == "<->":
            self.consume("<->")
            right = self.parse_implication()
            left = Binary(left, right, "IFF")

        return left

    def parse_implication(self) -> Symbolic:
        left = self.parse_or()

        if self.current() == "->":
            self.consume("->")
            right = self.parse_implication()
            return Binary(left, right, "IMPLIES")

        return left

    def parse_or(self) -> Symbolic:
        left = self.parse_and()

        while self.current() is not None and self.current().upper() == "OR":
            self.consume()
            right = self.parse_and()
            left = Binary(left, right, "OR")

        return left

    def parse_and(self) -> Symbolic:
        left = self.parse_not()

        while self.current() is not None and self.current().upper() == "AND":
            self.consume()
            right = self.parse_not()
            left = Binary(left, right, "AND")

        return left

    def parse_not(self) -> Symbolic:
        if self.current() is not None and self.current().upper() == "NOT":
            self.consume()
            return UnaryNot(self.parse_not())

        return self.parse_atom()

    def parse_atom(self) -> Symbolic:
        token = self.current()

        if token is None:
            raise ParseError("Expected variable or '('")

        if token == "(":
            self.consume("(")
            expression = self.parse_biconditional()

            if self.current() != ")":
                raise ParseError("Expected ')'")

            self.consume(")")
            return expression

        if token in {")", "AND", "OR", "NOT", "->", "<->"}:
            raise ParseError(f"Unexpected token {token!r}")

        self.consume()
        return Variable(token)


def parse_expression(text: str) -> Symbolic:
    return Parser(tokenize(text)).parse()


expression_text = "NOT P OR Q AND R"
parsed = parse_expression(expression_text)

print("Input:", expression_text)
print("Parsed:", parsed)
print(
    "Evaluation:",
    parsed.evaluate({"P": True, "Q": False, "R": True}),
)


# =============================================================================
# 39. PARSER EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("PARSER EDGE CASES")
print("=" * 80)

parser_examples = [
    "P",
    "NOT P",
    "P AND Q",
    "P OR Q AND R",
    "P -> Q",
    "P -> Q -> R",
    "P <-> Q",
    "(P OR Q) AND R",
    "NOT (P AND Q)",
]

for text in parser_examples:
    try:
        formula = parse_expression(text)
        print(f"{text:<25} -> {formula}")
    except ParseError as error:
        print(f"{text:<25} -> ERROR: {error}")


# =============================================================================
# 40. ADVANCED PARSER EVALUATION
# =============================================================================

print("\n" + "=" * 80)
print("PARSER-BASED TRUTH TABLE")
print("=" * 80)


def evaluate_parsed_formula(
    text: str,
    variables: Sequence[str],
) -> list[dict[str, bool]]:
    formula = parse_expression(text)
    rows = []

    for values in product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        assignment["result"] = formula.evaluate(assignment)
        rows.append(assignment)

    return rows


formula_text = "(P OR Q) AND (NOT P OR R)"

for row in evaluate_parsed_formula(formula_text, ["P", "Q", "R"]):
    print(row)


# =============================================================================
# 41. PRODUCTION-ORIENTED VALIDATION
# =============================================================================

print("\n" + "=" * 80)
print("PRODUCTION-ORIENTED VALIDATION")
print("=" * 80)


def validate_boolean(value: object, name: str = "value") -> bool:
    """
    Require an actual Boolean rather than silently accepting arbitrary truthy
    objects. This distinction can matter in security-sensitive policy code.
    """
    if not isinstance(value, bool):
        raise TypeError(
            f"{name} must be bool, received {type(value).__name__}"
        )
    return value


def secure_policy(
    authenticated: object,
    verified: object,
    administrator: object,
    owner: object,
) -> bool:
    authenticated = validate_boolean(authenticated, "authenticated")
    verified = validate_boolean(verified, "verified")
    administrator = validate_boolean(administrator, "administrator")
    owner = validate_boolean(owner, "owner")

    return authenticated and verified and (administrator or owner)


print(
    "Validated policy:",
    secure_policy(True, True, False, True),
)

try:
    secure_policy(True, "yes", False, True)
except TypeError as error:
    print("Validation error:", error)


# =============================================================================
# 42. PERFORMANCE CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("PERFORMANCE CONSIDERATIONS")
print("=" * 80)

"""
For n independent variables:

    Number of assignments = 2^n.

Thus brute-force truth-table evaluation has exponential growth in n.

For small educational examples, brute force is simple, transparent, and useful.

For large industrial formulas, practical systems can use:
    - SAT solvers
    - Binary Decision Diagrams
    - symbolic simplification
    - CNF transformations
    - Tseitin-style encodings
    - constraint propagation
    - memoization
    - incremental solving

The choice depends on the formula structure and problem requirements.
"""

for n in range(1, 21, 3):
    print(f"{n:2} variables -> {2 ** n:,} assignments")


# =============================================================================
# 43. SECURITY CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("SECURITY CONSIDERATIONS")
print("=" * 80)

"""
Logical authorization policies should be:

    - explicit
    - testable
    - deny-by-default where appropriate
    - validated
    - auditable
    - resistant to ambiguous parsing
    - covered by exhaustive tests for small policies

A policy such as:

    authenticated AND (admin OR owner)

is structurally different from:

    authenticated AND admin OR owner

because precedence can change the effective authorization condition.

For security-sensitive logic, parentheses and named intermediate conditions
can reduce ambiguity.
"""


# =============================================================================
# 44. FINAL INTEGRATION EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("FINAL INTEGRATION EXAMPLE")
print("=" * 80)


def enterprise_access_policy(
    authenticated: bool,
    account_active: bool,
    mfa_verified: bool,
    administrator: bool,
    resource_owner: bool,
    emergency_lock: bool,
) -> bool:
    """
    Example enterprise policy:

        authenticated
        AND active account
        AND MFA verified
        AND administrator OR owner
        AND NOT emergency lock

    Explicit parentheses are used to avoid precedence ambiguity.
    """
    return (
        authenticated
        and account_active
        and mfa_verified
        and (administrator or resource_owner)
        and not emergency_lock
    )


scenarios = [
    {
        "name": "Administrator",
        "authenticated": True,
        "account_active": True,
        "mfa_verified": True,
        "administrator": True,
        "resource_owner": False,
        "emergency_lock": False,
    },
    {
        "name": "Owner",
        "authenticated": True,
        "account_active": True,
        "mfa_verified": True,
        "administrator": False,
        "resource_owner": True,
        "emergency_lock": False,
    },
    {
        "name": "Locked account",
        "authenticated": True,
        "account_active": True,
        "mfa_verified": True,
        "administrator": True,
        "resource_owner": True,
        "emergency_lock": True,
    },
    {
        "name": "Unauthenticated",
        "authenticated": False,
        "account_active": True,
        "mfa_verified": True,
        "administrator": True,
        "resource_owner": False,
        "emergency_lock": False,
    },
]

for scenario in scenarios:
    data = scenario.copy()
    name = data.pop("name")
    decision = enterprise_access_policy(**data)
    print(f"{name:<20} -> access={decision}")


print("\n" + "=" * 80)
print("END OF PROPOSITIONAL LOGIC STUDY")
print("=" * 80)
