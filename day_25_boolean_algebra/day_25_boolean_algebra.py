"""
Boolean Algebra: Boolean Variables, Boolean Expressions, and Boolean Identities

A self-contained study and executable demonstration of Boolean algebra, progressing
from fundamentals to advanced simplification, truth tables, canonical forms,
logic-equivalent transformations, Karnaugh-map-style minimization, and a practical
digital-circuit decision system.

Run with:
    python boolean_algebra.py
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================
#
# Boolean algebra works with values from a two-element set:
#
#     False = 0
#     True  = 1
#
# The three fundamental operations are:
#
#     NOT:  ¬A       or !A
#     AND:  A ∧ B    or A * B
#     OR:   A ∨ B    or A + B
#
# In Python:
#
#     not A
#     A and B
#     A or B
#
# Python's and/or operators short-circuit and return operands rather than
# necessarily returning bool objects. For Boolean algebra demonstrations,
# we explicitly normalize values with bool() where useful.


def show_fundamental_operations() -> None:
    print("\n" + "=" * 80)
    print("1. FUNDAMENTAL BOOLEAN OPERATIONS")
    print("=" * 80)

    values = [False, True]

    print("\nNOT operation:")
    for a in values:
        print(f"NOT {int(a)} = {int(not a)}")

    print("\nAND operation:")
    for a in values:
        for b in values:
            print(f"{int(a)} AND {int(b)} = {int(a and b)}")

    print("\nOR operation:")
    for a in values:
        for b in values:
            print(f"{int(a)} OR {int(b)} = {int(a or b)}")


# ============================================================================
# 2. BOOLEAN VARIABLES AND EXPRESSIONS
# ============================================================================

def boolean_expression(a: bool, b: bool, c: bool) -> bool:
    """
    Evaluate:

        F = (A AND B) OR (NOT A AND C)

    This is a Boolean expression composed of:
    - variables: A, B, C
    - complements: NOT A
    - products: A AND B
    - sums: OR between terms
    """
    return (a and b) or ((not a) and c)


def show_expression_truth_table() -> None:
    print("\n" + "=" * 80)
    print("2. BOOLEAN EXPRESSION TRUTH TABLE")
    print("=" * 80)

    print("\nExpression: F = (A AND B) OR (NOT A AND C)")
    print("\n A B C | F")
    print("-------+---")

    for a, b, c in product([False, True], repeat=3):
        result = boolean_expression(a, b, c)
        print(f" {int(a)} {int(b)} {int(c)} | {int(result)}")


# ============================================================================
# 3. OPERATOR PRECEDENCE
# ============================================================================
#
# A useful conventional precedence is:
#
#     1. NOT
#     2. AND
#     3. OR
#
# Therefore:
#
#     A OR B AND C
#
# means:
#
#     A OR (B AND C)
#
# Parentheses should be used when they improve clarity.


def precedence_examples() -> None:
    print("\n" + "=" * 80)
    print("3. OPERATOR PRECEDENCE")
    print("=" * 80)

    a = True
    b = False
    c = True

    expression_without_parentheses = a or b and c
    expression_with_parentheses = a or (b and c)
    different_grouping = (a or b) and c

    print(f"A = {int(a)}, B = {int(b)}, C = {int(c)}")
    print(f"A OR B AND C       = {int(expression_without_parentheses)}")
    print(f"A OR (B AND C)     = {int(expression_with_parentheses)}")
    print(f"(A OR B) AND C     = {int(different_grouping)}")


# ============================================================================
# 4. CORE BOOLEAN IDENTITIES
# ============================================================================
#
# Identity law:
#     A + 0 = A
#     A * 1 = A
#
# Null/dominance law:
#     A + 1 = 1
#     A * 0 = 0
#
# Idempotent law:
#     A + A = A
#     A * A = A
#
# Complement law:
#     A + A' = 1
#     A * A' = 0
#
# Involution:
#     (A')' = A
#
# Commutative:
#     A + B = B + A
#     A * B = B * A
#
# Associative:
#     A + (B + C) = (A + B) + C
#     A * (B * C) = (A * B) * C
#
# Distributive:
#     A * (B + C) = AB + AC
#     A + BC = (A + B)(A + C)
#
# Absorption:
#     A + AB = A
#     A(A + B) = A
#
# De Morgan:
#     (AB)' = A' + B'
#     (A + B)' = A'B'
#
# These identities permit algebraic simplification without changing the
# logical function.


def verify_identity(
    name: str,
    left: Callable[..., bool],
    right: Callable[..., bool],
    variables: int,
) -> bool:
    """Exhaustively verify an identity for every Boolean input combination."""
    for values in product([False, True], repeat=variables):
        if left(*values) != right(*values):
            print(f"FAILED: {name}, inputs={values}")
            return False

    print(f"PASSED: {name}")
    return True


def verify_core_identities() -> None:
    print("\n" + "=" * 80)
    print("4. CORE BOOLEAN IDENTITIES")
    print("=" * 80)

    identities = [
        (
            "Identity: A OR 0 = A",
            lambda a: a or False,
            lambda a: a,
            1,
        ),
        (
            "Identity: A AND 1 = A",
            lambda a: a and True,
            lambda a: a,
            1,
        ),
        (
            "Null: A OR 1 = 1",
            lambda a: a or True,
            lambda a: True,
            1,
        ),
        (
            "Null: A AND 0 = 0",
            lambda a: a and False,
            lambda a: False,
            1,
        ),
        (
            "Idempotent: A OR A = A",
            lambda a: a or a,
            lambda a: a,
            1,
        ),
        (
            "Idempotent: A AND A = A",
            lambda a: a and a,
            lambda a: a,
            1,
        ),
        (
            "Complement: A OR NOT A = 1",
            lambda a: a or not a,
            lambda a: True,
            1,
        ),
        (
            "Complement: A AND NOT A = 0",
            lambda a: a and not a,
            lambda a: False,
            1,
        ),
        (
            "Involution: NOT NOT A = A",
            lambda a: not not a,
            lambda a: a,
            1,
        ),
        (
            "Commutative OR",
            lambda a, b: a or b,
            lambda a, b: b or a,
            2,
        ),
        (
            "Commutative AND",
            lambda a, b: a and b,
            lambda a, b: b and a,
            2,
        ),
        (
            "Associative OR",
            lambda a, b, c: a or (b or c),
            lambda a, b, c: (a or b) or c,
            3,
        ),
        (
            "Associative AND",
            lambda a, b, c: a and (b and c),
            lambda a, b, c: (a and b) and c,
            3,
        ),
        (
            "Distributive AND over OR",
            lambda a, b, c: a and (b or c),
            lambda a, b, c: (a and b) or (a and c),
            3,
        ),
        (
            "Distributive OR over AND",
            lambda a, b, c: a or (b and c),
            lambda a, b, c: (a or b) and (a or c),
            3,
        ),
        (
            "Absorption: A OR (A AND B) = A",
            lambda a, b: a or (a and b),
            lambda a, b: a,
            2,
        ),
        (
            "Absorption: A AND (A OR B) = A",
            lambda a, b: a and (a or b),
            lambda a, b: a,
            2,
        ),
        (
            "De Morgan: NOT(A AND B) = NOT A OR NOT B",
            lambda a, b: not (a and b),
            lambda a, b: (not a) or (not b),
            2,
        ),
        (
            "De Morgan: NOT(A OR B) = NOT A AND NOT B",
            lambda a, b: not (a or b),
            lambda a, b: (not a) and (not b),
            2,
        ),
    ]

    for identity in identities:
        verify_identity(*identity)


# ============================================================================
# 5. DERIVED BOOLEAN LAWS
# ============================================================================

def verify_derived_laws() -> None:
    print("\n" + "=" * 80)
    print("5. DERIVED BOOLEAN LAWS")
    print("=" * 80)

    verify_identity(
        "Consensus theorem: AB + A'C + BC = AB + A'C",
        lambda a, b, c: (a and b) or ((not a) and c) or (b and c),
        lambda a, b, c: (a and b) or ((not a) and c),
        3,
    )

    verify_identity(
        "XOR: A XOR B = A'B + AB'",
        lambda a, b: bool(a) ^ bool(b),
        lambda a, b: ((not a) and b) or (a and (not b)),
        2,
    )

    verify_identity(
        "XNOR: A XNOR B = AB + A'B'",
        lambda a, b: not (bool(a) ^ bool(b)),
        lambda a, b: (a and b) or ((not a) and (not b)),
        2,
    )

    verify_identity(
        "Redundancy: A + A'B = A + B",
        lambda a, b: a or ((not a) and b),
        lambda a, b: a or b,
        2,
    )


# ============================================================================
# 6. EXPRESSION REPRESENTATIONS
# ============================================================================
#
# Sum of Products (SOP):
#
#     AB + A'C + BC
#
# Product of Sums (POS):
#
#     (A + B)(A' + C)(B + C)
#
# A minterm is an AND term containing every variable exactly once.
# A maxterm is an OR term containing every variable exactly once.
#
# For variables A, B, C:
#
#     minterm m5 corresponds to binary 101:
#     A B C = 1 0 1
#     m5 = A B' C
#
# A Boolean function can be represented as:
#
#     F = Σm(indices)
#
# or:
#
#     F = ΠM(indices)
#
# depending on the selected canonical form.


def minterm(index: int, variable_count: int) -> str:
    bits = f"{index:0{variable_count}b}"
    variables = [chr(ord("A") + i) for i in range(variable_count)]

    terms = []
    for variable, bit in zip(variables, bits):
        terms.append(variable if bit == "1" else variable + "'")

    return "".join(terms)


def maxterm(index: int, variable_count: int) -> str:
    bits = f"{index:0{variable_count}b}"
    variables = [chr(ord("A") + i) for i in range(variable_count)]

    terms = []
    for variable, bit in zip(variables, bits):
        terms.append(variable + "'" if bit == "1" else variable)

    return "(" + " + ".join(terms) + ")"


def canonical_forms_demo() -> None:
    print("\n" + "=" * 80)
    print("6. CANONICAL SOP AND POS FORMS")
    print("=" * 80)

    variable_count = 3
    true_indices = [1, 3, 5, 7]
    false_indices = [0, 2, 4, 6]

    print("\nFunction F(A,B,C) = 1 at minterms:", true_indices)
    print("Canonical SOP:")
    print(" + ".join(minterm(i, variable_count) for i in true_indices))

    print("\nCanonical POS:")
    print(" ".join(maxterm(i, variable_count) for i in false_indices))

    print("\nSigma notation:")
    print(f"F = Σm({', '.join(map(str, true_indices))})")

    print("\nPi notation:")
    print(f"F = ΠM({', '.join(map(str, false_indices))})")


# ============================================================================
# 7. TRUTH TABLE ENGINE
# ============================================================================

def truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> list[tuple[tuple[bool, ...], bool]]:
    """Generate every input combination and its Boolean result."""
    rows = []

    for values in product([False, True], repeat=len(variables)):
        rows.append((values, bool(expression(*values))))

    return rows


def print_truth_table(
    variables: Sequence[str],
    expression: Callable[..., bool],
) -> None:
    header = " ".join(f"{name:>3}" for name in variables)
    print(f"\n{header} | F")
    print("-" * (len(header) + 4))

    for values, result in truth_table(variables, expression):
        inputs = " ".join(f"{int(value):>3}" for value in values)
        print(f"{inputs} | {int(result)}")


# ============================================================================
# 8. FUNCTIONAL COMPLETENESS
# ============================================================================
#
# AND, OR, and NOT form a functionally complete set.
#
# NAND alone is also functionally complete:
#
#     NOT A = A NAND A
#
#     A AND B = (A NAND B) NAND (A NAND B)
#
#     A OR B = (A NAND A) NAND (B NAND B)
#
# NOR alone is likewise functionally complete.


def nand(a: bool, b: bool) -> bool:
    return not (a and b)


def nor(a: bool, b: bool) -> bool:
    return not (a or b)


def not_using_nand(a: bool) -> bool:
    return nand(a, a)


def and_using_nand(a: bool, b: bool) -> bool:
    intermediate = nand(a, b)
    return nand(intermediate, intermediate)


def or_using_nand(a: bool, b: bool) -> bool:
    return nand(nand(a, a), nand(b, b))


def demonstrate_functional_completeness() -> None:
    print("\n" + "=" * 80)
    print("7. FUNCTIONALLY COMPLETE NAND/NOR SYSTEMS")
    print("=" * 80)

    for a, b in product([False, True], repeat=2):
        print(
            f"A={int(a)} B={int(b)} | "
            f"NAND={int(nand(a,b))} | "
            f"AND-from-NAND={int(and_using_nand(a,b))} | "
            f"OR-from-NAND={int(or_using_nand(a,b))}"
        )

    print("\nNOT from NAND:")
    for a in [False, True]:
        print(f"A={int(a)} -> NOT A={int(not_using_nand(a))}")


# ============================================================================
# 9. XOR, XNOR, HALF ADDER, FULL ADDER
# ============================================================================
#
# XOR:
#
#     A XOR B = A'B + AB'
#
# XNOR:
#
#     A XNOR B = AB + A'B'
#
# A half adder adds two bits:
#
#     Sum   = A XOR B
#     Carry = A AND B
#
# A full adder adds A, B, and carry-in:
#
#     Sum = A XOR B XOR Cin
#     Cout = AB + Cin(A XOR B)


def xor_gate(a: bool, b: bool) -> bool:
    return bool(a) ^ bool(b)


def xnor_gate(a: bool, b: bool) -> bool:
    return not xor_gate(a, b)


def half_adder(a: bool, b: bool) -> tuple[bool, bool]:
    return xor_gate(a, b), a and b


def full_adder(a: bool, b: bool, carry_in: bool) -> tuple[bool, bool]:
    sum_bit = xor_gate(xor_gate(a, b), carry_in)
    carry_out = (a and b) or (carry_in and xor_gate(a, b))
    return sum_bit, carry_out


def demonstrate_adders() -> None:
    print("\n" + "=" * 80)
    print("8. XOR, XNOR, HALF ADDER, AND FULL ADDER")
    print("=" * 80)

    print("\nHalf adder:")
    print("A B | Sum Carry")
    for a, b in product([False, True], repeat=2):
        total, carry = half_adder(a, b)
        print(f"{int(a)} {int(b)} |  {int(total)}    {int(carry)}")

    print("\nFull adder:")
    print("A B Cin | Sum Cout")
    for a, b, carry_in in product([False, True], repeat=3):
        total, carry_out = full_adder(a, b, carry_in)
        print(
            f"{int(a)} {int(b)}  {int(carry_in)}  |  "
            f"{int(total)}    {int(carry_out)}"
        )


# ============================================================================
# 10. BOOLEAN EXPRESSION TREE
# ============================================================================
#
# Representing expressions as a tree is useful for:
# - parsing
# - symbolic simplification
# - compiler optimization
# - logic synthesis
# - circuit generation
#
# Nodes represent constants, variables, AND, OR, and NOT.


class BooleanNode:
    def evaluate(self, environment: dict[str, bool]) -> bool:
        raise NotImplementedError

    def expression(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Variable(BooleanNode):
    name: str

    def evaluate(self, environment: dict[str, bool]) -> bool:
        if self.name not in environment:
            raise KeyError(f"Missing Boolean variable: {self.name}")
        return bool(environment[self.name])

    def expression(self) -> str:
        return self.name


@dataclass(frozen=True)
class Constant(BooleanNode):
    value: bool

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return self.value

    def expression(self) -> str:
        return "1" if self.value else "0"


@dataclass(frozen=True)
class Not(BooleanNode):
    operand: BooleanNode

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return not self.operand.evaluate(environment)

    def expression(self) -> str:
        return f"(NOT {self.operand.expression()})"


@dataclass(frozen=True)
class And(BooleanNode):
    left: BooleanNode
    right: BooleanNode

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return self.left.evaluate(environment) and self.right.evaluate(environment)

    def expression(self) -> str:
        return f"({self.left.expression()} AND {self.right.expression()})"


@dataclass(frozen=True)
class Or(BooleanNode):
    left: BooleanNode
    right: BooleanNode

    def evaluate(self, environment: dict[str, bool]) -> bool:
        return self.left.evaluate(environment) or self.right.evaluate(environment)

    def expression(self) -> str:
        return f"({self.left.expression()} OR {self.right.expression()})"


def expression_tree_demo() -> None:
    print("\n" + "=" * 80)
    print("9. BOOLEAN EXPRESSION TREE")
    print("=" * 80)

    a = Variable("A")
    b = Variable("B")
    c = Variable("C")

    # F = (A AND B) OR (NOT A AND C)
    expression = Or(
        And(a, b),
        And(Not(a), c),
    )

    print("Expression:", expression.expression())

    environment = {"A": True, "B": False, "C": True}
    print("Environment:", environment)
    print("Result:", expression.evaluate(environment))


# ============================================================================
# 11. PROGRAMMATIC SIMPLIFICATION
# ============================================================================
#
# A full symbolic algebra system can use rewrite rules. The implementation
# below applies several safe identities recursively.
#
# This is deliberately an educational simplifier rather than a complete
# industrial Boolean minimizer.


def simplify(node: BooleanNode) -> BooleanNode:
    if isinstance(node, Variable) or isinstance(node, Constant):
        return node

    if isinstance(node, Not):
        operand = simplify(node.operand)

        if isinstance(operand, Constant):
            return Constant(not operand.value)

        if isinstance(operand, Not):
            return simplify(operand.operand)

        return Not(operand)

    if isinstance(node, And):
        left = simplify(node.left)
        right = simplify(node.right)

        if isinstance(left, Constant):
            return right if left.value else Constant(False)

        if isinstance(right, Constant):
            return left if right.value else Constant(False)

        if left == right:
            return left

        if isinstance(right, Not) and right.operand == left:
            return Constant(False)

        if isinstance(left, Not) and left.operand == right:
            return Constant(False)

        # A * (A + B) = A
        if isinstance(right, Or):
            if right.left == left or right.right == left:
                return left

        if isinstance(left, Or):
            if left.left == right or left.right == right:
                return right

        return And(left, right)

    if isinstance(node, Or):
        left = simplify(node.left)
        right = simplify(node.right)

        if isinstance(left, Constant):
            return Constant(True) if left.value else right

        if isinstance(right, Constant):
            return Constant(True) if right.value else left

        if left == right:
            return left

        if isinstance(right, Not) and right.operand == left:
            return Constant(True)

        if isinstance(left, Not) and left.operand == right:
            return Constant(True)

        # A + AB = A
        if isinstance(right, And):
            if right.left == left or right.right == left:
                return left

        if isinstance(left, And):
            if left.left == right or left.right == right:
                return right

        return Or(left, right)

    raise TypeError(f"Unsupported Boolean node: {type(node).__name__}")


def symbolic_simplification_demo() -> None:
    print("\n" + "=" * 80)
    print("10. SYMBOLIC SIMPLIFICATION")
    print("=" * 80)

    a = Variable("A")
    b = Variable("B")

    examples = {
        "A AND 1": And(a, Constant(True)),
        "A OR 0": Or(a, Constant(False)),
        "A AND A": And(a, a),
        "A OR A": Or(a, a),
        "A AND NOT A": And(a, Not(a)),
        "A OR NOT A": Or(a, Not(a)),
        "A AND (A OR B)": And(a, Or(a, b)),
        "A OR (A AND B)": Or(a, And(a, b)),
        "NOT NOT A": Not(Not(a)),
    }

    for name, expression in examples.items():
        simplified = simplify(expression)
        print(f"{name:24} -> {simplified.expression()}")


# ============================================================================
# 12. K-MAP-STYLE GROUPING
# ============================================================================
#
# Karnaugh maps exploit adjacency between minterms to simplify expressions.
# This implementation demonstrates grouping at a conceptual level by finding
# implicants that cover sets of minterms.
#
# A pattern contains:
#
#     0 -> variable must be 0
#     1 -> variable must be 1
#     - -> variable does not matter
#
# Example:
#
#     1-0
#
# represents A=1, B=don't-care, C=0.


def pattern_covers(pattern: str, index: int, variable_count: int) -> bool:
    bits = f"{index:0{variable_count}b}"
    return all(p == "-" or p == b for p, b in zip(pattern, bits))


def pattern_minterms(pattern: str) -> set[int]:
    positions = [i for i, char in enumerate(pattern) if char == "-"]
    base = list(pattern)
    results = set()

    for choices in product("01", repeat=len(positions)):
        candidate = base[:]
        for position, value in zip(positions, choices):
            candidate[position] = value
        results.add(int("".join(candidate), 2))

    return results


def simplify_minterms_with_patterns(
    variable_count: int,
    on_set: set[int],
) -> list[str]:
    """
    Find prime-like implicant candidates by repeatedly combining patterns.

    This is an educational Quine-McCluskey-style combination process.
    It does not attempt every optimization used by industrial logic synthesis.
    """

    patterns = {format(index, f"0{variable_count}b") for index in on_set}
    prime_candidates: set[str] = set()

    while patterns:
        used: set[str] = set()
        combined: set[str] = set()

        pattern_list = sorted(patterns)

        for i, first in enumerate(pattern_list):
            for second in pattern_list[i + 1:]:
                differences = [
                    position
                    for position, (a, b) in enumerate(zip(first, second))
                    if a != b
                ]

                if len(differences) != 1:
                    continue

                position = differences[0]

                # Only combine when neither differing character is '-'.
                if first[position] == "-" or second[position] == "-":
                    continue

                merged = (
                    first[:position]
                    + "-"
                    + first[position + 1:]
                )

                covered = pattern_minterms(merged)

                if covered <= on_set:
                    combined.add(merged)
                    used.add(first)
                    used.add(second)

        prime_candidates.update(patterns - used)
        patterns = combined

    return sorted(prime_candidates)


def pattern_to_expression(pattern: str) -> str:
    variables = [chr(ord("A") + i) for i in range(len(pattern))]
    terms = []

    for variable, value in zip(variables, pattern):
        if value == "1":
            terms.append(variable)
        elif value == "0":
            terms.append(variable + "'")

    return "".join(terms) if terms else "1"


def kmap_style_demo() -> None:
    print("\n" + "=" * 80)
    print("11. QUINE-MCCLUSKEY-STYLE MINTERM COMBINATION")
    print("=" * 80)

    # F(A,B,C,D) = Σm(0,1,2,3,8,9,10,11)
    on_set = {0, 1, 2, 3, 8, 9, 10, 11}

    patterns = simplify_minterms_with_patterns(4, on_set)

    print("Function: F(A,B,C,D) = Σm(0,1,2,3,8,9,10,11)")
    print("\nPrime-like implicants found:")

    for pattern in patterns:
        print(f"  {pattern} -> {pattern_to_expression(pattern)}")

    print(
        "\nThese patterns reveal that the function simplifies to a "
        "two-variable condition involving B and C."
    )


# ============================================================================
# 13. EQUIVALENCE TESTING
# ============================================================================
#
# Two Boolean expressions are logically equivalent if they produce identical
# outputs for every possible input combination.
#
# Exhaustive truth-table comparison is practical for a small number of
# variables. It grows exponentially:
#
#     n variables -> 2^n input combinations.
#
# Symbolic methods or SAT-based methods become more appropriate for larger
# expressions.


def expressions_are_equivalent(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
) -> bool:
    for values in product([False, True], repeat=len(variables)):
        if bool(first(*values)) != bool(second(*values)):
            return False

    return True


def equivalence_demo() -> None:
    print("\n" + "=" * 80)
    print("12. LOGICAL EQUIVALENCE")
    print("=" * 80)

    variables = ["A", "B"]

    expression_one = lambda a, b: not (a and b)
    expression_two = lambda a, b: (not a) or (not b)

    print(
        "NOT(A AND B) and (NOT A OR NOT B):",
        expressions_are_equivalent(variables, expression_one, expression_two),
    )

    expression_three = lambda a, b: a or (a and b)
    expression_four = lambda a, b: a

    print(
        "A OR (A AND B) and A:",
        expressions_are_equivalent(variables, expression_three, expression_four),
    )


# ============================================================================
# 14. PRACTICAL SECURITY EXAMPLE: ACCESS CONTROL LOGIC
# ============================================================================
#
# Boolean expressions naturally model policy conditions.
#
# Example:
#
# Access is granted when:
#
#     authenticated AND (admin OR owner)
#
# OR:
#
#     emergency_override
#
# This is a simplified example. Production authorization should not rely on
# ad-hoc Boolean logic alone; identity, policy evaluation, auditing, failure
# modes, and explicit deny rules must be considered.


def access_granted(
    authenticated: bool,
    admin: bool,
    owner: bool,
    emergency_override: bool,
) -> bool:
    return authenticated and (admin or owner) or emergency_override


def access_control_demo() -> None:
    print("\n" + "=" * 80)
    print("13. PRACTICAL APPLICATION: ACCESS CONTROL")
    print("=" * 80)

    scenarios = [
        (False, False, False, False),
        (True, False, True, False),
        (True, True, False, False),
        (True, False, False, False),
        (False, False, False, True),
    ]

    print("Authenticated Admin Owner Emergency | Access")

    for authenticated, admin, owner, emergency in scenarios:
        access = access_granted(authenticated, admin, owner, emergency)

        print(
            f"     {int(authenticated)}          {int(admin)}"
            f"      {int(owner)}          {int(emergency)}"
            f"     |   {int(access)}"
        )

    print(
        "\nSecurity note: Boolean expressions should not be treated as a "
        "complete authorization architecture. Explicit policy semantics, "
        "default-deny behavior, logging, and privilege boundaries matter."
    )


# ============================================================================
# 15. PRACTICAL APPLICATION: ALARM SYSTEM
# ============================================================================
#
# Suppose:
#
# D = door open
# W = window open
# M = motion detected
# S = system armed
#
# Alarm:
#
#     Alarm = S AND (D OR W OR M)
#
# This demonstrates how Boolean algebra maps directly to digital systems.


def alarm_system(armed: bool, door_open: bool, window_open: bool, motion: bool) -> bool:
    return armed and (door_open or window_open or motion)


def alarm_demo() -> None:
    print("\n" + "=" * 80)
    print("14. PRACTICAL APPLICATION: ALARM SYSTEM")
    print("=" * 80)

    print("Armed Door Window Motion | Alarm")

    for inputs in product([False, True], repeat=4):
        alarm = alarm_system(*inputs)

        if alarm:
            print(
                f"  {int(inputs[0])}    {int(inputs[1])}    "
                f" {int(inputs[2])}    {int(inputs[3])}   |   {int(alarm)}"
            )


# ============================================================================
# 16. EDGE CASES AND COMMON MISTAKES
# ============================================================================
#
# Common mistakes:
#
# 1. Confusing Boolean OR with arithmetic addition.
# 2. Treating XOR as ordinary OR.
# 3. Applying De Morgan's law incorrectly.
# 4. Forgetting operator precedence.
# 5. Removing parentheses without preserving grouping.
# 6. Assuming two expressions are equivalent after checking only some inputs.
# 7. Confusing Boolean equality with assignment in programming languages.
# 8. Forgetting that programming-language truthiness may contain more than
#    two conceptual states.
#
# Python-specific subtlety:
#
#     bool(0)      -> False
#     bool(1)      -> True
#     bool([])     -> False
#     bool([1])    -> True
#
# Those are Python truthiness rules, not additional values in Boolean algebra.


def edge_case_demo() -> None:
    print("\n" + "=" * 80)
    print("15. EDGE CASES AND PYTHON TRUTHINESS")
    print("=" * 80)

    examples = [
        0,
        1,
        "",
        "Boolean",
        [],
        [1],
        None,
    ]

    for value in examples:
        print(f"{value!r:12} -> bool(value) = {bool(value)}")

    print("\nXOR differs from OR:")
    print("True OR True   =", True or True)
    print("True XOR True  =", True ^ True)


# ============================================================================
# 17. PERFORMANCE CONSIDERATIONS
# ============================================================================
#
# For n Boolean variables:
#
#     truth-table enumeration = O(2^n)
#
# This exponential behavior is fundamental to exhaustive evaluation.
#
# Individual Boolean operations are O(1), but expression size and evaluation
# frequency affect total runtime.
#
# In real systems:
# - simplify expressions before repeated evaluation;
# - avoid redundant computations;
# - use bit-parallel representations for large batches;
# - use decision diagrams, SAT solvers, or specialized logic synthesis for
#   large symbolic problems.


def performance_demo() -> None:
    print("\n" + "=" * 80)
    print("16. PERFORMANCE CONSIDERATIONS")
    print("=" * 80)

    for variable_count in range(1, 11):
        combinations = 2 ** variable_count
        print(
            f"{variable_count:2} Boolean variables -> "
            f"{combinations:5} truth-table rows"
        )


# ============================================================================
# 18. TESTING
# ============================================================================

def run_self_tests() -> None:
    print("\n" + "=" * 80)
    print("17. SELF-TESTS")
    print("=" * 80)

    # Fundamental Boolean operations.
    assert nand(False, False) is True
    assert nand(True, True) is False
    assert nor(False, False) is True
    assert nor(True, False) is False

    # Adders.
    assert half_adder(False, False) == (False, False)
    assert half_adder(True, False) == (True, False)
    assert half_adder(True, True) == (False, True)

    assert full_adder(False, False, False) == (False, False)
    assert full_adder(True, False, False) == (True, False)
    assert full_adder(True, True, False) == (False, True)
    assert full_adder(True, True, True) == (True, True)

    # De Morgan equivalence.
    assert expressions_are_equivalent(
        ["A", "B"],
        lambda a, b: not (a and b),
        lambda a, b: (not a) or (not b),
    )

    # Access control.
    assert access_granted(True, True, False, False)
    assert access_granted(True, False, True, False)
    assert not access_granted(True, False, False, False)
    assert access_granted(False, False, False, True)

    # Expression tree.
    a = Variable("A")
    b = Variable("B")
    expression = And(a, Not(b))

    assert expression.evaluate({"A": True, "B": False}) is True
    assert expression.evaluate({"A": True, "B": True}) is False

    print("All self-tests passed.")


# ============================================================================
# 19. STUDY EXERCISES WITH EXECUTABLE ANSWERS
# ============================================================================

def exercises() -> None:
    print("\n" + "=" * 80)
    print("18. EXERCISES WITH VERIFIED ANSWERS")
    print("=" * 80)

    # Exercise 1:
    # Simplify A + AB.
    #
    # Answer: A by absorption.
    a = Variable("A")
    b = Variable("B")

    exercise_1 = Or(a, And(a, b))
    print("\nExercise 1: Simplify A + AB")
    print("Answer:", simplify(exercise_1).expression())

    # Exercise 2:
    # Simplify A(A + B).
    #
    # Answer: A.
    exercise_2 = And(a, Or(a, b))
    print("Exercise 2: Simplify A(A + B)")
    print("Answer:", simplify(exercise_2).expression())

    # Exercise 3:
    # Test whether A XOR B equals A'B + AB'.
    print("Exercise 3: Verify XOR expansion")
    xor_equivalent = expressions_are_equivalent(
        ["A", "B"],
        xor_gate,
        lambda a, b: ((not a) and b) or (a and (not b)),
    )
    print("Answer:", xor_equivalent)

    # Exercise 4:
    # F = (A+B)(A+C) should equal A+BC.
    print("Exercise 4: Verify distributive identity")
    distributive_equivalent = expressions_are_equivalent(
        ["A", "B", "C"],
        lambda a, b, c: (a or b) and (a or c),
        lambda a, b, c: a or (b and c),
    )
    print("Answer:", distributive_equivalent)


# ============================================================================
# 20. MAIN PROGRAM
# ============================================================================

def main() -> None:
    print("=" * 80)
    print("BOOLEAN ALGEBRA: COMPLETE EXECUTABLE STUDY")
    print("=" * 80)
    print(
        "\nTopic coverage: Boolean variables, expressions, truth tables, "
        "identities, canonical forms, functional completeness, symbolic "
        "expressions, simplification, logic circuits, testing, and practical "
        "applications."
    )

    show_fundamental_operations()
    show_expression_truth_table()
    precedence_examples()
    verify_core_identities()
    verify_derived_laws()
    canonical_forms_demo()

    print("\nTruth table for F = (A AND B) OR (NOT A AND C):")
    print_truth_table(
        ["A", "B", "C"],
        boolean_expression,
    )

    demonstrate_functional_completeness()
    demonstrate_adders()
    expression_tree_demo()
    symbolic_simplification_demo()
    kmap_style_demo()
    equivalence_demo()
    access_control_demo()
    alarm_demo()
    edge_case_demo()
    performance_demo()
    run_self_tests()
    exercises()

    print("\n" + "=" * 80)
    print("END OF BOOLEAN ALGEBRA STUDY")
    print("=" * 80)


if __name__ == "__main__":
    main()
