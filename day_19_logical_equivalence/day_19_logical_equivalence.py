"""
Logical Equivalence: De Morgan's Laws, Implication Equivalence,
Distributive Laws, and Absorption Laws

A standalone study program that progresses from propositional-logic
fundamentals to symbolic equivalence checking and automated
truth-table verification.

Run:
    python logical_equivalence.py
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


# ============================================================
# 1. FUNDAMENTAL PROPOSITIONAL LOGIC
# ============================================================

def logical_not(value: bool) -> bool:
    """Logical negation."""
    return not value


def logical_and(left: bool, right: bool) -> bool:
    """Logical conjunction: true only when both operands are true."""
    return left and right


def logical_or(left: bool, right: bool) -> bool:
    """Logical disjunction: true when at least one operand is true."""
    return left or right


def logical_xor(left: bool, right: bool) -> bool:
    """Exclusive OR: true when exactly one operand is true."""
    return left != right


def logical_implies(left: bool, right: bool) -> bool:
    """
    Material implication.

    P -> Q is false only when P is true and Q is false.
    Equivalent form:
        P -> Q == ~P OR Q
    """
    return (not left) or right


def logical_iff(left: bool, right: bool) -> bool:
    """Logical biconditional: true when both operands have the same value."""
    return left == right


def logical_nand(left: bool, right: bool) -> bool:
    """NAND: negation of conjunction."""
    return not (left and right)


def logical_nor(left: bool, right: bool) -> bool:
    """NOR: negation of disjunction."""
    return not (left or right)


def truth(value: bool) -> str:
    """Display Boolean values in a truth-table-friendly form."""
    return "T" if value else "F"


# ============================================================
# 2. BASIC TRUTH TABLES
# ============================================================

def print_header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def demonstrate_basic_operators() -> None:
    print_header("Basic logical operators")

    print(" P Q | NOT P | P AND Q | P OR Q | P XOR Q | P -> Q | P <-> Q")
    print("-" * 65)

    for p, q in product([False, True], repeat=2):
        print(
            f" {truth(p)} {truth(q)} |"
            f"   {truth(not p)}   |"
            f"    {truth(p and q)}    |"
            f"   {truth(p or q)}   |"
            f"    {truth(p != q)}    |"
            f"   {truth(logical_implies(p, q))}   |"
            f"    {truth(p == q)}"
        )

    print("\nImportant implication fact:")
    print("P -> Q is false only for P=True and Q=False.")


# ============================================================
# 3. WHAT LOGICAL EQUIVALENCE MEANS
# ============================================================

def demonstrate_equivalence_definition() -> None:
    print_header("Logical equivalence")

    print("Two propositions P and Q are logically equivalent when:")
    print("    P <-> Q is a tautology.")
    print("Equivalently, P and Q have identical truth values for every")
    print("possible assignment of their variables.")

    print("\nExample: P -> Q and ~P OR Q")
    for p, q in product([False, True], repeat=2):
        first = logical_implies(p, q)
        second = (not p) or q
        print(
            f"P={truth(p)}, Q={truth(q)}:"
            f"  P->Q={truth(first)},  ~P OR Q={truth(second)}"
        )


# ============================================================
# 4. DATA MODEL FOR SYMBOLIC PROPOSITIONS
# ============================================================

class Proposition:
    """Base class for symbolic Boolean expressions."""

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def variables(self) -> set[str]:
        raise NotImplementedError

    def precedence(self) -> int:
        raise NotImplementedError

    def to_string(self, parent_precedence: int = 0) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.to_string()

    def __and__(self, other: "Proposition") -> "Proposition":
        return And(self, other)

    def __or__(self, other: "Proposition") -> "Proposition":
        return Or(self, other)

    def __invert__(self) -> "Proposition":
        return Not(self)

    def implies(self, other: "Proposition") -> "Proposition":
        return Implies(self, other)

    def iff(self, other: "Proposition") -> "Proposition":
        return Iff(self, other)


@dataclass(frozen=True)
class Variable(Proposition):
    name: str

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        if self.name not in assignment:
            raise KeyError(f"Missing value for variable {self.name!r}")
        return assignment[self.name]

    def variables(self) -> set[str]:
        return {self.name}

    def precedence(self) -> int:
        return 100

    def to_string(self, parent_precedence: int = 0) -> str:
        return self.name


@dataclass(frozen=True)
class Constant(Proposition):
    value: bool

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return self.value

    def variables(self) -> set[str]:
        return set()

    def precedence(self) -> int:
        return 100

    def to_string(self, parent_precedence: int = 0) -> str:
        return "T" if self.value else "F"


@dataclass(frozen=True)
class Not(Proposition):
    operand: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return not self.operand.evaluate(assignment)

    def variables(self) -> set[str]:
        return self.operand.variables()

    def precedence(self) -> int:
        return 80

    def to_string(self, parent_precedence: int = 0) -> str:
        text = self.operand.to_string(self.precedence())
        result = f"~{text}"
        return f"({result})" if self.precedence() < parent_precedence else result


@dataclass(frozen=True)
class And(Proposition):
    left: Proposition
    right: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return (
            self.left.evaluate(assignment)
            and self.right.evaluate(assignment)
        )

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def precedence(self) -> int:
        return 60

    def to_string(self, parent_precedence: int = 0) -> str:
        result = (
            f"{self.left.to_string(self.precedence())} AND "
            f"{self.right.to_string(self.precedence())}"
        )
        return f"({result})" if self.precedence() < parent_precedence else result


@dataclass(frozen=True)
class Or(Proposition):
    left: Proposition
    right: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return (
            self.left.evaluate(assignment)
            or self.right.evaluate(assignment)
        )

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def precedence(self) -> int:
        return 50

    def to_string(self, parent_precedence: int = 0) -> str:
        result = (
            f"{self.left.to_string(self.precedence())} OR "
            f"{self.right.to_string(self.precedence())}"
        )
        return f"({result})" if self.precedence() < parent_precedence else result


@dataclass(frozen=True)
class Implies(Proposition):
    left: Proposition
    right: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return logical_implies(
            self.left.evaluate(assignment),
            self.right.evaluate(assignment),
        )

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def precedence(self) -> int:
        return 30

    def to_string(self, parent_precedence: int = 0) -> str:
        result = (
            f"{self.left.to_string(self.precedence())} -> "
            f"{self.right.to_string(self.precedence())}"
        )
        return f"({result})" if self.precedence() < parent_precedence else result


@dataclass(frozen=True)
class Iff(Proposition):
    left: Proposition
    right: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return (
            self.left.evaluate(assignment)
            == self.right.evaluate(assignment)
        )

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def precedence(self) -> int:
        return 20

    def to_string(self, parent_precedence: int = 0) -> str:
        result = (
            f"{self.left.to_string(self.precedence())} <-> "
            f"{self.right.to_string(self.precedence())}"
        )
        return f"({result})" if self.precedence() < parent_precedence else result


# ============================================================
# 5. TRUTH-TABLE GENERATION
# ============================================================

def all_assignments(variables: Iterable[str]) -> List[Dict[str, bool]]:
    names = sorted(set(variables))
    return [
        dict(zip(names, values))
        for values in product([False, True], repeat=len(names))
    ]


def truth_table(expression: Proposition) -> List[Tuple[Dict[str, bool], bool]]:
    return [
        (assignment, expression.evaluate(assignment))
        for assignment in all_assignments(expression.variables())
    ]


def print_truth_table(expression: Proposition) -> None:
    variables = sorted(expression.variables())

    print(f"\nExpression: {expression}")
    print(" | ".join(variables + [str(expression)]))
    print("-" * (4 * len(variables) + len(str(expression)) + 8))

    for assignment, result in truth_table(expression):
        values = [truth(assignment[name]) for name in variables]
        print(" | ".join(values + [truth(result)]))


# ============================================================
# 6. AUTOMATIC EQUIVALENCE CHECKING
# ============================================================

def are_equivalent(
    first: Proposition,
    second: Proposition,
) -> bool:
    """
    Compare two expressions for every possible variable assignment.

    This is an exhaustive semantic test. For n variables, it evaluates
    2^n assignments, so it is ideal for learning and verification but
    not necessarily efficient for very large expressions.
    """
    variables = first.variables() | second.variables()

    for assignment in all_assignments(variables):
        if first.evaluate(assignment) != second.evaluate(assignment):
            return False

    return True


def explain_equivalence(
    first: Proposition,
    second: Proposition,
) -> None:
    print(f"\nFirst : {first}")
    print(f"Second: {second}")

    variables = first.variables() | second.variables()
    mismatch_found = False

    print("\n" + " | ".join(sorted(variables) + [str(first), str(second), "Same"]))
    print("-" * 70)

    for assignment in all_assignments(variables):
        first_value = first.evaluate(assignment)
        second_value = second.evaluate(assignment)
        same = first_value == second_value

        values = [truth(assignment[name]) for name in sorted(variables)]
        print(
            " | ".join(
                values
                + [truth(first_value), truth(second_value), truth(same)]
            )
        )

        if not same:
            mismatch_found = True

    if mismatch_found:
        print("\nResult: NOT logically equivalent.")
    else:
        print("\nResult: Logically equivalent.")


# ============================================================
# 7. CLASSIC LOGICAL LAWS
# ============================================================

def demonstrate_basic_laws() -> None:
    print_header("Core laws of propositional logic")

    p = Variable("P")
    q = Variable("Q")

    laws = [
        ("Double negation", ~~p, p),
        ("Identity for AND", p & Constant(True), p),
        ("Identity for OR", p | Constant(False), p),
        ("Domination for AND", p & Constant(False), Constant(False)),
        ("Domination for OR", p | Constant(True), Constant(True)),
        ("Idempotent AND", p & p, p),
        ("Idempotent OR", p | p, p),
        ("Complement AND", p & ~p, Constant(False)),
        ("Complement OR", p | ~p, Constant(True)),
        ("Commutative AND", p & q, q & p),
        ("Commutative OR", p | q, q | p),
        (
            "Associative AND",
            (p & q) & Variable("R"),
            p & (q & Variable("R")),
        ),
        (
            "Associative OR",
            (p | q) | Variable("R"),
            p | (q | Variable("R")),
        ),
    ]

    for name, first, second in laws:
        result = are_equivalent(first, second)
        print(f"{name:25} {'PASS' if result else 'FAIL'}")
        print(f"  {first}  ==  {second}")


# ============================================================
# 8. DE MORGAN'S LAWS
# ============================================================

def demonstrate_de_morgan() -> None:
    print_header("De Morgan's laws")

    p = Variable("P")
    q = Variable("Q")

    first_law_left = ~(p & q)
    first_law_right = (~p) | (~q)

    second_law_left = ~(p | q)
    second_law_right = (~p) & (~q)

    print("First De Morgan law:")
    print("  ~(P AND Q) <-> (~P OR ~Q)")
    explain_equivalence(first_law_left, first_law_right)

    print("\nSecond De Morgan law:")
    print("  ~(P OR Q) <-> (~P AND ~Q)")
    explain_equivalence(second_law_left, second_law_right)

    print("\nInterpretation:")
    print("Negating a conjunction changes AND to OR and negates each operand.")
    print("Negating a disjunction changes OR to AND and negates each operand.")


# ============================================================
# 9. IMPLICATION EQUIVALENCES
# ============================================================

def demonstrate_implication_equivalences() -> None:
    print_header("Implication equivalences")

    p = Variable("P")
    q = Variable("Q")

    equivalences = [
        (
            "Implication elimination",
            p.implies(q),
            (~p) | q,
        ),
        (
            "Contrapositive",
            p.implies(q),
            (~q).implies(~p),
        ),
        (
            "Implication as disjunction",
            p.implies(q),
            (~p) | q,
        ),
        (
            "Negated implication",
            ~(p.implies(q)),
            p & ~q,
        ),
    ]

    for name, first, second in equivalences:
        print(f"\n{name}:")
        print(f"  {first}")
        print(f"  {second}")
        print(f"  Equivalent: {are_equivalent(first, second)}")

    print("\nImportant distinction:")
    print("P -> Q is not equivalent to Q -> P.")
    print("P -> Q is equivalent to its contrapositive ~Q -> ~P.")
    print("The converse Q -> P is generally a different proposition.")


# ============================================================
# 10. DISTRIBUTIVE LAWS
# ============================================================

def demonstrate_distributive_laws() -> None:
    print_header("Distributive laws")

    p = Variable("P")
    q = Variable("Q")
    r = Variable("R")

    and_over_or_left = p & (q | r)
    and_over_or_right = (p & q) | (p & r)

    or_over_and_left = p | (q & r)
    or_over_and_right = (p | q) & (p | r)

    print("AND distributes over OR:")
    explain_equivalence(and_over_or_left, and_over_or_right)

    print("\nOR distributes over AND:")
    explain_equivalence(or_over_and_left, or_over_and_right)

    print("\nBoth directions are valid in Boolean algebra.")
    print("This differs from ordinary arithmetic intuition, where")
    print("multiplication distributing over addition is familiar but")
    print("addition distributing over multiplication requires attention.")


# ============================================================
# 11. ABSORPTION LAWS
# ============================================================

def demonstrate_absorption_laws() -> None:
    print_header("Absorption laws")

    p = Variable("P")
    q = Variable("Q")

    first_left = p | (p & q)
    first_right = p

    second_left = p & (p | q)
    second_right = p

    print("First absorption law:")
    print("  P OR (P AND Q) <-> P")
    explain_equivalence(first_left, first_right)

    print("\nSecond absorption law:")
    print("  P AND (P OR Q) <-> P")
    explain_equivalence(second_left, second_right)

    print("\nAbsorption removes a redundant condition.")
    print("For example, if P is already required, adding P AND Q inside")
    print("P OR (P AND Q) cannot change the final result.")


# ============================================================
# 12. OTHER IMPORTANT EQUIVALENCES
# ============================================================

def demonstrate_additional_equivalences() -> None:
    print_header("Additional important equivalences")

    p = Variable("P")
    q = Variable("Q")
    r = Variable("R")

    examples = [
        (
            "Biconditional expansion",
            p.iff(q),
            (p & q) | ((~p) & (~q)),
        ),
        (
            "Biconditional as two implications",
            p.iff(q),
            p.implies(q) & q.implies(p),
        ),
        (
            "Exclusive OR",
            p.__xor__(q) if hasattr(p, "__xor__") else Xor(p, q),
            (p | q) & ~(p & q),
        ),
        (
            "Negated implication",
            ~(p.implies(q)),
            p & ~q,
        ),
        (
            "Consensus-style equivalence",
            (p & q) | (~p & r) | (q & r),
            (p & q) | (~p & r) | (q & r),
        ),
    ]

    for name, first, second in examples:
        print(f"\n{name}:")
        print(f"  {first}")
        print(f"  {second}")
        print(f"  Equivalent: {are_equivalent(first, second)}")


# Xor is defined separately because the core expression hierarchy
# uses only NOT, AND, OR, implication, and biconditional.
@dataclass(frozen=True)
class Xor(Proposition):
    left: Proposition
    right: Proposition

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return (
            self.left.evaluate(assignment)
            != self.right.evaluate(assignment)
        )

    def variables(self) -> set[str]:
        return self.left.variables() | self.right.variables()

    def precedence(self) -> int:
        return 40

    def to_string(self, parent_precedence: int = 0) -> str:
        result = (
            f"{self.left.to_string(self.precedence())} XOR "
            f"{self.right.to_string(self.precedence())}"
        )
        return f"({result})" if self.precedence() < parent_precedence else result


# ============================================================
# 13. CORRECTING A COMMON MISCONCEPTION ABOUT IMPLICATION
# ============================================================

def demonstrate_implication_edge_cases() -> None:
    print_header("Implication edge cases")

    cases = [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]

    print(" P Q | P -> Q | ~P OR Q")
    print("-" * 25)

    for p, q in cases:
        implication = logical_implies(p, q)
        equivalent_form = (not p) or q
        print(
            f" {truth(p)} {truth(q)} |"
            f"   {truth(implication)}   |"
            f"    {truth(equivalent_form)}"
        )

    print("\nA false antecedent makes a material implication true.")
    print("This is a semantic rule of classical propositional logic.")
    print("It does not mean that P caused Q or that P and Q are unrelated.")


# ============================================================
# 14. EQUIVALENCE VS IMPLICATION
# ============================================================

def demonstrate_equivalence_vs_implication() -> None:
    print_header("Equivalence versus implication")

    p = Variable("P")
    q = Variable("Q")

    implication = p.implies(q)
    reverse = q.implies(p)
    biconditional = p.iff(q)

    print(f"P -> Q:   {implication}")
    print(f"Q -> P:   {reverse}")
    print(f"P <-> Q:  {biconditional}")

    print("\nP <-> Q can be understood as:")
    print("  (P -> Q) AND (Q -> P)")

    print(
        "Verified:",
        are_equivalent(
            biconditional,
            implication & reverse,
        ),
    )


# ============================================================
# 15. TAUTOLOGY, CONTRADICTION, AND CONTINGENCY
# ============================================================

def classify_expression(expression: Proposition) -> str:
    values = [result for _, result in truth_table(expression)]

    if all(values):
        return "tautology"
    if not any(values):
        return "contradiction"
    return "contingency"


def demonstrate_classification() -> None:
    print_header("Tautology, contradiction, and contingency")

    p = Variable("P")
    q = Variable("Q")

    expressions = {
        "Law of excluded middle": p | ~p,
        "Law of contradiction": p & ~p,
        "Simple implication": p.implies(q),
        "Biconditional": p.iff(q),
    }

    for name, expression in expressions.items():
        print(f"{name:30} {classify_expression(expression):15} {expression}")


# ============================================================
# 16. REWRITING EXPRESSIONS USING EQUIVALENCE LAWS
# ============================================================

def rewrite_implication(expression: Proposition) -> Proposition:
    """Recursively eliminate material implication."""
    if isinstance(expression, Variable) or isinstance(expression, Constant):
        return expression

    if isinstance(expression, Not):
        return Not(rewrite_implication(expression.operand))

    if isinstance(expression, And):
        return And(
            rewrite_implication(expression.left),
            rewrite_implication(expression.right),
        )

    if isinstance(expression, Or):
        return Or(
            rewrite_implication(expression.left),
            rewrite_implication(expression.right),
        )

    if isinstance(expression, Implies):
        left = rewrite_implication(expression.left)
        right = rewrite_implication(expression.right)
        return Or(Not(left), right)

    if isinstance(expression, Iff):
        left = rewrite_implication(expression.left)
        right = rewrite_implication(expression.right)
        return And(
            Or(Not(left), right),
            Or(Not(right), left),
        )

    if isinstance(expression, Xor):
        return Xor(
            rewrite_implication(expression.left),
            rewrite_implication(expression.right),
        )

    raise TypeError(f"Unsupported expression type: {type(expression)}")


def demonstrate_symbolic_rewriting() -> None:
    print_header("Symbolic implication elimination")

    p = Variable("P")
    q = Variable("Q")
    r = Variable("R")

    expression = (p.implies(q)) & (q.implies(r))
    rewritten = rewrite_implication(expression)

    print("Original:")
    print(f"  {expression}")
    print("After eliminating implications:")
    print(f"  {rewritten}")
    print("Semantically equivalent:", are_equivalent(expression, rewritten))


# ============================================================
# 17. NORMAL FORMS
# ============================================================

def demonstrate_normal_form_concepts() -> None:
    print_header("Normal-form concepts")

    print("Conjunctive Normal Form (CNF): AND of OR clauses.")
    print("Example:")
    print("  (P OR Q) AND (~P OR R)")

    print("\nDisjunctive Normal Form (DNF): OR of AND terms.")
    print("Example:")
    print("  (P AND ~Q) OR (~P AND R)")

    print("\nDe Morgan's laws help move negations inward.")
    print("Distributive laws help restructure expressions.")
    print("Together these laws are central to Boolean simplification and")
    print("conversion into CNF or DNF.")

    p = Variable("P")
    q = Variable("Q")
    r = Variable("R")

    cnf = (p | q) & (~p | r)
    dnf = (p & ~q) | (~p & r)

    print(f"\nCNF example: {cnf}")
    print(f"DNF example: {dnf}")
    print(f"CNF classification: {classify_expression(cnf)}")
    print(f"DNF classification: {classify_expression(dnf)}")


# ============================================================
# 18. BOOLEAN SIMPLIFICATION PATTERNS
# ============================================================

def simplify_absorption_example() -> None:
    print_header("Step-by-step absorption simplification")

    p = Variable("P")
    q = Variable("Q")

    original = p | (p & q)

    print("Original expression:")
    print(f"  {original}")

    print("\nApply absorption law:")
    print("  P OR (P AND Q) <-> P")

    simplified = p

    print(f"\nSimplified expression:")
    print(f"  {simplified}")

    print(
        "\nSemantic verification:",
        are_equivalent(original, simplified),
    )


def simplify_demorgan_example() -> None:
    print_header("Step-by-step De Morgan simplification")

    p = Variable("P")
    q = Variable("Q")

    original = ~(p & q)

    print(f"Original: {original}")
    print("Apply De Morgan's first law:")
    print("  ~(P AND Q) <-> (~P OR ~Q)")

    simplified = (~p) | (~q)

    print(f"Simplified: {simplified}")
    print("Equivalent:", are_equivalent(original, simplified))


# ============================================================
# 19. COUNTEREXAMPLE GENERATION
# ============================================================

def find_counterexample(
    first: Proposition,
    second: Proposition,
) -> Dict[str, bool] | None:
    variables = first.variables() | second.variables()

    for assignment in all_assignments(variables):
        if first.evaluate(assignment) != second.evaluate(assignment):
            return assignment

    return None


def demonstrate_false_equivalence() -> None:
    print_header("Finding a counterexample to a false equivalence")

    p = Variable("P")
    q = Variable("Q")

    first = p.implies(q)
    converse = q.implies(p)

    print(f"First proposition: {first}")
    print(f"Second proposition: {converse}")

    counterexample = find_counterexample(first, converse)

    print("\nCounterexample:")
    print(counterexample)

    if counterexample:
        print(
            f"First evaluates to {first.evaluate(counterexample)}; "
            f"second evaluates to {converse.evaluate(counterexample)}."
        )

    print("\nA single counterexample is sufficient to disprove equivalence.")


# ============================================================
# 20. PERFORMANCE OF EXHAUSTIVE EQUIVALENCE TESTING
# ============================================================

def equivalence_search_space(variable_count: int) -> int:
    return 2 ** variable_count


def demonstrate_complexity() -> None:
    print_header("Complexity of truth-table equivalence checking")

    print("For n independent Boolean variables, a full truth table has 2^n rows.")

    for n in range(1, 11):
        print(f"Variables: {n:2} -> assignments: {equivalence_search_space(n):4}")

    print("\nExhaustive semantic checking is exponential in the number of variables.")
    print("It is excellent for small educational examples and test cases.")
    print("Larger symbolic systems often use canonical forms, SAT solving,")
    print("Binary Decision Diagrams, algebraic simplification, or other methods.")


# ============================================================
# 21. PROPERTY-BASED CHECKS FOR LOGICAL LAWS
# ============================================================

def verify_law(
    name: str,
    left_builder: Callable[..., Proposition],
    right_builder: Callable[..., Proposition],
    variables: Sequence[Variable],
) -> bool:
    left = left_builder(*variables)
    right = right_builder(*variables)
    result = are_equivalent(left, right)
    print(f"{name:40} {'PASS' if result else 'FAIL'}")
    return result


def demonstrate_automated_law_suite() -> None:
    print_header("Automated verification suite")

    p, q, r = Variable("P"), Variable("Q"), Variable("R")

    verify_law(
        "De Morgan 1",
        lambda p, q: ~(p & q),
        lambda p, q: (~p) | (~q),
        [p, q],
    )

    verify_law(
        "De Morgan 2",
        lambda p, q: ~(p | q),
        lambda p, q: (~p) & (~q),
        [p, q],
    )

    verify_law(
        "Implication elimination",
        lambda p, q: p.implies(q),
        lambda p, q: (~p) | q,
        [p, q],
    )

    verify_law(
        "Contrapositive",
        lambda p, q: p.implies(q),
        lambda p, q: (~q).implies(~p),
        [p, q],
    )

    verify_law(
        "AND over OR distribution",
        lambda p, q, r: p & (q | r),
        lambda p, q, r: (p & q) | (p & r),
        [p, q, r],
    )

    verify_law(
        "OR over AND distribution",
        lambda p, q, r: p | (q & r),
        lambda p, q, r: (p | q) & (p | r),
        [p, q, r],
    )

    verify_law(
        "Absorption 1",
        lambda p, q: p | (p & q),
        lambda p, q: p,
        [p, q],
    )

    verify_law(
        "Absorption 2",
        lambda p, q: p & (p | q),
        lambda p, q: p,
        [p, q],
    )


# ============================================================
# 22. BOOLEAN CIRCUIT INTERPRETATION
# ============================================================

def demonstrate_boolean_circuit() -> None:
    print_header("Logical equivalence and Boolean circuits")

    print("A Boolean expression can be implemented as a logic circuit.")
    print("Equivalent expressions therefore describe circuits with the")
    print("same output for every input combination.")

    p = Variable("P")
    q = Variable("Q")

    circuit_a = ~(p & q)
    circuit_b = (~p) | (~q)

    print(f"\nCircuit A: {circuit_a}")
    print(f"Circuit B: {circuit_b}")
    print("Same input/output behavior:", are_equivalent(circuit_a, circuit_b))

    print("\nDe Morgan transformation can replace:")
    print("  NAND = NOT(AND)")
    print("with:")
    print("  OR of individually inverted inputs")

    print("\nThis relationship is important in digital logic design.")


# ============================================================
# 23. DATABASE AND QUERY LOGIC INTERPRETATION
# ============================================================

def demonstrate_query_logic() -> None:
    print_header("Logical equivalence in query-style conditions")

    age_eligible = Variable("AgeEligible")
    verified = Variable("Verified")
    blocked = Variable("Blocked")

    original = ~(age_eligible & verified)
    transformed = (~age_eligible) | (~verified)

    print("Condition:")
    print("  NOT (AgeEligible AND Verified)")

    print("Equivalent condition:")
    print("  NOT AgeEligible OR NOT Verified")

    print("Verified:", are_equivalent(original, transformed))

    access_condition = verified & ~blocked
    print("\nAccess condition:")
    print(f"  {access_condition}")

    print(
        "This illustrates why logical equivalence matters when conditions"
        " are rewritten by applications, compilers, or query planners."
    )


# ============================================================
# 24. SECURITY-RELEVANT BOOLEAN REWRITING
# ============================================================

def demonstrate_security_condition() -> None:
    print_header("Security-condition reasoning")

    authenticated = Variable("Authenticated")
    authorized = Variable("Authorized")
    suspended = Variable("Suspended")

    access = authenticated & authorized & ~suspended

    denied = ~access

    equivalent_denial = (
        (~authenticated)
        | (~authorized)
        | suspended
    )

    print(f"Access condition: {access}")
    print(f"Negated access:   {denied}")
    print(f"De Morgan form:   {equivalent_denial}")
    print("Equivalent:", are_equivalent(denied, equivalent_denial))

    print(
        "\nLogical equivalence is useful when auditing security conditions,"
        " but semantic equivalence does not by itself guarantee that the"
        " surrounding application implements authorization correctly."
    )


# ============================================================
# 25. EDGE CASES
# ============================================================

def demonstrate_edge_cases() -> None:
    print_header("Edge cases")

    true_value = Constant(True)
    false_value = Constant(False)
    p = Variable("P")

    cases = [
        ("~T", ~true_value),
        ("~F", ~false_value),
        ("P AND T", p & true_value),
        ("P OR F", p | false_value),
        ("P AND F", p & false_value),
        ("P OR T", p | true_value),
        ("P AND ~P", p & ~p),
        ("P OR ~P", p | ~p),
    ]

    for description, expression in cases:
        print(
            f"{description:12} -> {expression:25} "
            f"({classify_expression(expression)})"
        )

    print("\nNo variable assignment is required for constant-only expressions.")


# ============================================================
# 26. COMMON MISTAKES
# ============================================================

def demonstrate_common_mistakes() -> None:
    print_header("Common logical-equivalence mistakes")

    p = Variable("P")
    q = Variable("Q")

    mistaken_converse = q.implies(p)
    correct_contrapositive = (~q).implies(~p)

    print("Mistake: treating the converse as equivalent to the implication.")
    print(f"Original:     {p.implies(q)}")
    print(f"Converse:     {mistaken_converse}")
    print(
        "Equivalent:",
        are_equivalent(p.implies(q), mistaken_converse),
    )

    print("\nCorrect transformation: use the contrapositive.")
    print(f"Original:       {p.implies(q)}")
    print(f"Contrapositive: {correct_contrapositive}")
    print(
        "Equivalent:",
        are_equivalent(p.implies(q), correct_contrapositive),
    )

    print("\nAnother common mistake:")
    print("~(P AND Q) is NOT (~P AND ~Q).")
    print("Correct De Morgan transformation is (~P OR ~Q).")

    wrong = ~(p & q)
    incorrect = (~p) & (~q)
    correct = (~p) | (~q)

    print("Wrong equivalence:", are_equivalent(wrong, incorrect))
    print("Correct equivalence:", are_equivalent(wrong, correct))


# ============================================================
# 27. A SMALL LOGICAL RULE ENGINE
# ============================================================

@dataclass
class Rule:
    name: str
    condition: Proposition
    result: Proposition

    def fires(self, assignment: Dict[str, bool]) -> bool:
        return self.condition.evaluate(assignment)


class RuleEngine:
    """Minimal rule engine showing Boolean expressions as decision logic."""

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)

    def evaluate(self, assignment: Dict[str, bool]) -> List[str]:
        return [
            rule.name
            for rule in self.rules
            if rule.fires(assignment)
        ]


def demonstrate_rule_engine() -> None:
    print_header("Logical equivalence inside a rule engine")

    verified = Variable("Verified")
    premium = Variable("Premium")
    suspended = Variable("Suspended")

    rules = [
        Rule(
            "Permit verified premium user",
            verified & premium & ~suspended,
            Constant(True),
        ),
        Rule(
            "Permit verified non-premium user",
            verified & ~premium & ~suspended,
            Constant(True),
        ),
        Rule(
            "Deny suspended user",
            suspended,
            Constant(False),
        ),
    ]

    engine = RuleEngine(rules)

    assignments = [
        {"Verified": True, "Premium": True, "Suspended": False},
        {"Verified": True, "Premium": False, "Suspended": False},
        {"Verified": False, "Premium": True, "Suspended": False},
        {"Verified": True, "Premium": True, "Suspended": True},
    ]

    for assignment in assignments:
        print(f"{assignment} -> {engine.evaluate(assignment)}")


# ============================================================
# 28. MAIN STUDY PROGRAM
# ============================================================

def main() -> None:
    print_header("LOGICAL EQUIVALENCE STUDY PROGRAM")
    print("Topic:")
    print("De Morgan's laws, implication equivalence, distributive laws,")
    print("absorption laws, and related Boolean identities.")

    demonstrate_basic_operators()
    demonstrate_equivalence_definition()
    demonstrate_basic_laws()
    demonstrate_de_morgan()
    demonstrate_implication_equivalences()
    demonstrate_distributive_laws()
    demonstrate_absorption_laws()

    print_header("Extended symbolic demonstrations")
    demonstrate_additional_equivalences()
    demonstrate_implication_edge_cases()
    demonstrate_equivalence_vs_implication()
    demonstrate_classification()
    demonstrate_symbolic_rewriting()
    demonstrate_normal_form_concepts()

    simplify_absorption_example()
    simplify_demorgan_example()
    demonstrate_false_equivalence()
    demonstrate_complexity()
    demonstrate_automated_law_suite()
    demonstrate_boolean_circuit()
    demonstrate_query_logic()
    demonstrate_security_condition()
    demonstrate_edge_cases()
    demonstrate_common_mistakes()
    demonstrate_rule_engine()

    print_header("End of logical equivalence study")
    print("All major examples above are executable and semantically verified.")
    print("The central verification principle is equality of truth values")
    print("for every possible assignment of the relevant variables.")


if __name__ == "__main__":
    main()
