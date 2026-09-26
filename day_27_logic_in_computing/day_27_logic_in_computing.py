"""
Logic in Computing
==================

Digital logic, predicates in programs, assertions, and verification concepts.

This file is a self-contained study and executable demonstration of computational
logic. It progresses from Boolean algebra and digital gates to predicates,
assertions, invariants, contracts, truth tables, rule evaluation, exhaustive
verification, counterexamples, and property-based-style testing.

No external packages are required.

Run:
    python logic_in_computing.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import Callable, Iterable, Sequence


# ============================================================================
# 1. FUNDAMENTAL BOOLEAN LOGIC
# ============================================================================

def logical_not(value: bool) -> bool:
    """NOT reverses a Boolean value."""
    return not value


def logical_and(left: bool, right: bool) -> bool:
    """AND is true only when both inputs are true."""
    return left and right


def logical_or(left: bool, right: bool) -> bool:
    """OR is true when at least one input is true."""
    return left or right


def logical_xor(left: bool, right: bool) -> bool:
    """XOR is true when exactly one input is true."""
    return left != right


def logical_nand(left: bool, right: bool) -> bool:
    """NAND is NOT(AND)."""
    return not (left and right)


def logical_nor(left: bool, right: bool) -> bool:
    """NOR is NOT(OR)."""
    return not (left or right)


def logical_xnor(left: bool, right: bool) -> bool:
    """XNOR is true when both inputs are equal."""
    return left == right


def implication(antecedent: bool, consequent: bool) -> bool:
    """
    Logical implication:

        P -> Q

    is equivalent to:

        NOT P OR Q

    It is false only when P is true and Q is false.
    """
    return (not antecedent) or consequent


def biconditional(left: bool, right: bool) -> bool:
    """P <-> Q is true when P and Q have the same truth value."""
    return left == right


# ============================================================================
# 2. TRUTH TABLES
# ============================================================================

def print_two_input_truth_table(
    name: str,
    operation: Callable[[bool, bool], bool],
) -> None:
    """Print a truth table for a two-input Boolean operation."""
    print(f"\n{name}")
    print("-" * len(name))
    print(" A | B | Result")
    print("---+---+-------")

    for a, b in product([False, True], repeat=2):
        result = operation(a, b)
        print(f" {int(a)} | {int(b)} |   {int(result)}")


def demonstrate_truth_tables() -> None:
    print("\n=== DIGITAL LOGIC GATES ===")

    operations = {
        "AND": logical_and,
        "OR": logical_or,
        "XOR": logical_xor,
        "NAND": logical_nand,
        "NOR": logical_nor,
        "XNOR": logical_xnor,
    }

    for name, operation in operations.items():
        print_two_input_truth_table(name, operation)

    print("\nNOT")
    print("---")
    print(" A | NOT A")
    print("---+------")
    for value in [False, True]:
        print(f" {int(value)} |   {int(not value)}")


# ============================================================================
# 3. BOOLEAN ALGEBRA AND EQUIVALENCES
# ============================================================================

def demonstrate_boolean_laws() -> None:
    print("\n=== BOOLEAN ALGEBRA ===")

    values = [False, True]

    # Identity laws:
    # P AND True = P
    # P OR False = P
    for p in values:
        assert logical_and(p, True) == p
        assert logical_or(p, False) == p

    # Domination laws:
    # P AND False = False
    # P OR True = True
    for p in values:
        assert logical_and(p, False) is False
        assert logical_or(p, True) is True

    # Idempotent laws:
    # P AND P = P
    # P OR P = P
    for p in values:
        assert logical_and(p, p) == p
        assert logical_or(p, p) == p

    # Complement laws:
    # P AND NOT P = False
    # P OR NOT P = True
    for p in values:
        assert logical_and(p, not p) is False
        assert logical_or(p, not p) is True

    # Double negation:
    # NOT(NOT P) = P
    for p in values:
        assert not (not p) == p

    # De Morgan's laws:
    # NOT(P AND Q) = NOT P OR NOT Q
    # NOT(P OR Q) = NOT P AND NOT Q
    for p, q in product(values, repeat=2):
        assert not (p and q) == ((not p) or (not q))
        assert not (p or q) == ((not p) and (not q))

    print("Identity, domination, idempotent, complement, double-negation,")
    print("and De Morgan laws verified for all Boolean input combinations.")


# ============================================================================
# 4. COMBINATIONAL CIRCUITS
# ============================================================================

def half_adder(a: bool, b: bool) -> tuple[bool, bool]:
    """
    A half adder adds two one-bit values.

    sum   = A XOR B
    carry = A AND B
    """
    return logical_xor(a, b), logical_and(a, b)


def full_adder(a: bool, b: bool, carry_in: bool) -> tuple[bool, bool]:
    """
    A full adder adds A, B, and an incoming carry.

    The implementation composes two half adders.
    """
    first_sum, first_carry = half_adder(a, b)
    second_sum, second_carry = half_adder(first_sum, carry_in)
    carry_out = logical_or(first_carry, second_carry)
    return second_sum, carry_out


def add_binary_bits(
    left: Sequence[bool],
    right: Sequence[bool],
) -> list[bool]:
    """
    Add two equal-length binary sequences.

    Bits are stored least-significant first internally.
    """
    if len(left) != len(right):
        raise ValueError("Binary operands must have equal length.")

    result: list[bool] = []
    carry = False

    for a, b in zip(left, right):
        sum_bit, carry = full_adder(a, b, carry)
        result.append(sum_bit)

    if carry:
        result.append(carry)

    return result


def bits_from_integer(number: int, width: int) -> list[bool]:
    """Convert an unsigned integer into least-significant-first bits."""
    if number < 0:
        raise ValueError("Only unsigned integers are supported.")
    if width <= 0:
        raise ValueError("Width must be positive.")
    if number >= 2**width:
        raise ValueError("Number does not fit in requested width.")

    return [bool((number >> index) & 1) for index in range(width)]


def integer_from_bits(bits: Sequence[bool]) -> int:
    """Convert least-significant-first bits to an integer."""
    return sum((1 << index) for index, bit in enumerate(bits) if bit)


def demonstrate_adders() -> None:
    print("\n=== COMBINATIONAL CIRCUITS ===")

    print("Half-adder:")
    for a, b in product([False, True], repeat=2):
        total, carry = half_adder(a, b)
        print(
            f"A={int(a)} B={int(b)} "
            f"=> sum={int(total)} carry={int(carry)}"
        )

    print("\nFull-adder:")
    for a, b, carry_in in product([False, True], repeat=3):
        total, carry_out = full_adder(a, b, carry_in)
        print(
            f"A={int(a)} B={int(b)} Cin={int(carry_in)} "
            f"=> sum={int(total)} Cout={int(carry_out)}"
        )

    left = bits_from_integer(13, 5)
    right = bits_from_integer(9, 5)
    result = add_binary_bits(left, right)
    print(
        f"\nBinary addition: 13 + 9 = "
        f"{integer_from_bits(result)}"
    )


# ============================================================================
# 5. PREDICATES
# ============================================================================

def is_even(number: int) -> bool:
    """A predicate maps an input to True or False."""
    return number % 2 == 0


def is_valid_age(age: int) -> bool:
    """Example predicate used by application logic."""
    return 0 <= age <= 130


def can_enter_lab(age: int, has_id: bool, authorized: bool) -> bool:
    """
    A compound predicate.

    Access requires:
        valid age AND identification AND authorization
    """
    return is_valid_age(age) and has_id and authorized


def demonstrate_predicates() -> None:
    print("\n=== PREDICATES ===")

    samples = [-2, 0, 3, 8, 11]
    for number in samples:
        print(f"is_even({number}) = {is_even(number)}")

    print("\nCompound predicate:")
    cases = [
        (25, True, True),
        (25, True, False),
        (25, False, True),
        (-1, True, True),
    ]

    for age, has_id, authorized in cases:
        print(
            f"age={age}, has_id={has_id}, authorized={authorized} "
            f"=> access={can_enter_lab(age, has_id, authorized)}"
        )


# ============================================================================
# 6. PREDICATE LOGIC: QUANTIFIERS
# ============================================================================

def all_satisfy(
    values: Iterable[int],
    predicate: Callable[[int], bool],
) -> bool:
    """Universal quantification: forall x in values, P(x)."""
    return all(predicate(value) for value in values)


def any_satisfy(
    values: Iterable[int],
    predicate: Callable[[int], bool],
) -> bool:
    """Existential quantification: exists x in values such that P(x)."""
    return any(predicate(value) for value in values)


def demonstrate_quantifiers() -> None:
    print("\n=== QUANTIFIERS ===")

    numbers = [2, 4, 6, 8]

    print(
        "All numbers are even:",
        all_satisfy(numbers, is_even),
    )

    print(
        "At least one number is even:",
        any_satisfy([1, 3, 8, 11], is_even),
    )

    empty: list[int] = []

    # Python's all([]) is True because there is no counterexample.
    # This is called vacuous truth.
    print("all(is_even(x) for x in []):", all_satisfy(empty, is_even))
    print("any(is_even(x) for x in []):", any_satisfy(empty, is_even))


# ============================================================================
# 7. ASSERTIONS
# ============================================================================

def calculate_percentage(part: float, whole: float) -> float:
    """
    Assertions document assumptions that should hold during development.

    A user-controlled invalid value should normally be handled with explicit
    validation. Assertions are more appropriate for programmer assumptions
    and internal invariants.
    """
    if whole == 0:
        raise ValueError("whole cannot be zero.")

    percentage = part / whole * 100

    # Internal invariant: a finite normal percentage is expected here.
    assert percentage == percentage, "Percentage became NaN."
    return percentage


def demonstrate_assertions() -> None:
    print("\n=== ASSERTIONS ===")

    print("25 out of 200 =", calculate_percentage(25, 200), "%")

    try:
        calculate_percentage(10, 0)
    except ValueError as error:
        print("Expected validation error:", error)

    # Demonstration of an assertion:
    def square_root_domain_check(number: float) -> float:
        assert number >= 0, "Square-root input must be non-negative."
        return number ** 0.5

    print("sqrt(16) =", square_root_domain_check(16))

    try:
        square_root_domain_check(-1)
    except AssertionError as error:
        print("Expected assertion:", error)


# ============================================================================
# 8. PRECONDITIONS, POSTCONDITIONS, AND INVARIANTS
# ============================================================================

def transfer_money(
    balance: float,
    amount: float,
) -> tuple[float, float]:
    """
    A small contract-style example.

    Precondition:
        amount must be positive.

    Postconditions:
        resulting balance must not be negative,
        transferred amount must be positive.

    In a larger system, contracts should be designed explicitly and enforced
    at trustworthy boundaries.
    """
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")

    if amount > balance:
        raise ValueError("Insufficient balance.")

    new_balance = balance - amount

    assert new_balance >= 0
    assert amount > 0

    return new_balance, amount


@dataclass
class Inventory:
    """A simple object with an invariant."""

    quantity: int = 0

    def __post_init__(self) -> None:
        self._check_invariant()

    def add(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot add a negative quantity.")

        self.quantity += amount
        self._check_invariant()

    def remove(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot remove a negative quantity.")

        if amount > self.quantity:
            raise ValueError("Cannot remove more than available quantity.")

        self.quantity -= amount
        self._check_invariant()

    def _check_invariant(self) -> None:
        # Class invariant: inventory quantity can never be negative.
        assert self.quantity >= 0


def demonstrate_contracts() -> None:
    print("\n=== CONTRACTS AND INVARIANTS ===")

    balance, transferred = transfer_money(500, 125)
    print(f"Balance after transfer: {balance}")
    print(f"Transferred: {transferred}")

    inventory = Inventory()
    inventory.add(10)
    inventory.remove(4)
    print("Inventory quantity:", inventory.quantity)

    try:
        inventory.remove(20)
    except ValueError as error:
        print("Expected invariant-preserving validation:", error)


# ============================================================================
# 9. LOGIC EXPRESSIONS
# ============================================================================

@dataclass(frozen=True)
class User:
    age: int
    email_verified: bool
    account_active: bool
    is_admin: bool
    has_two_factor_authentication: bool


def secure_login_allowed(user: User) -> bool:
    """
    Example security predicate:

        active AND verified AND (admin OR MFA)

    This demonstrates grouping and operator precedence explicitly.
    """
    return (
        user.account_active
        and user.email_verified
        and (user.is_admin or user.has_two_factor_authentication)
    )


def demonstrate_security_predicate() -> None:
    print("\n=== COMPOUND LOGIC AND SECURITY RULES ===")

    users = [
        User(30, True, True, False, True),
        User(30, True, True, True, False),
        User(30, False, True, True, True),
        User(30, True, False, True, True),
    ]

    for index, user in enumerate(users, start=1):
        print(f"User {index}: login_allowed={secure_login_allowed(user)}")


# ============================================================================
# 10. EQUIVALENCE CHECKING
# ============================================================================

def expressions_are_equivalent(
    first: Callable[[bool, bool], bool],
    second: Callable[[bool, bool], bool],
) -> bool:
    """
    Two Boolean expressions are logically equivalent when they produce the
    same output for every possible input combination.
    """
    return all(
        first(a, b) == second(a, b)
        for a, b in product([False, True], repeat=2)
    )


def demonstrate_equivalence() -> None:
    print("\n=== LOGICAL EQUIVALENCE ===")

    original = lambda p, q: not (p and q)
    equivalent = lambda p, q: (not p) or (not q)

    print(
        "NOT(P AND Q) == NOT P OR NOT Q:",
        expressions_are_equivalent(original, equivalent),
    )

    non_equivalent = lambda p, q: not (p or q)

    print(
        "NOT(P AND Q) == NOT(P OR Q):",
        expressions_are_equivalent(original, non_equivalent),
    )


# ============================================================================
# 11. DECISION TABLES
# ============================================================================

def shipping_cost(
    order_total: float,
    is_member: bool,
    expedited: bool,
) -> float:
    """
    A decision-table-style rule system.

    Rules:
        1. Invalid total -> error.
        2. Expedited -> fixed premium.
        3. Member with qualifying order -> free.
        4. Otherwise -> standard shipping.
    """
    if order_total < 0:
        raise ValueError("Order total cannot be negative.")

    if expedited:
        return 15.0

    if is_member and order_total >= 100:
        return 0.0

    return 7.5


def demonstrate_decision_table() -> None:
    print("\n=== DECISION TABLE ===")

    for total, member, expedited in [
        (120, True, False),
        (80, True, False),
        (120, False, False),
        (120, True, True),
    ]:
        cost = shipping_cost(total, member, expedited)
        print(
            f"total={total}, member={member}, expedited={expedited} "
            f"=> shipping={cost}"
        )


# ============================================================================
# 12. VERIFICATION
# ============================================================================

class VerificationResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class VerificationFailure:
    inputs: tuple[bool, ...]
    expected: bool
    actual: bool


def verify_boolean_property(
    function: Callable[..., bool],
    expected_function: Callable[..., bool],
    input_count: int,
) -> tuple[VerificationResult, list[VerificationFailure]]:
    """
    Exhaustively verify a Boolean function.

    For n Boolean inputs there are 2^n possible combinations.
    Exhaustive verification is practical for small finite input spaces.
    """
    failures: list[VerificationFailure] = []

    for inputs in product([False, True], repeat=input_count):
        actual = function(*inputs)
        expected = expected_function(*inputs)

        if actual != expected:
            failures.append(
                VerificationFailure(
                    inputs=inputs,
                    expected=expected,
                    actual=actual,
                )
            )

    return (
        VerificationResult.PASS if not failures else VerificationResult.FAIL,
        failures,
    )


def demonstrate_exhaustive_verification() -> None:
    print("\n=== EXHAUSTIVE VERIFICATION ===")

    status, failures = verify_boolean_property(
        logical_nand,
        lambda a, b: not (a and b),
        2,
    )

    print("NAND verification:", status.value)

    # Intentionally incorrect specification to demonstrate a counterexample.
    status, failures = verify_boolean_property(
        logical_xor,
        logical_or,
        2,
    )

    print("XOR == OR verification:", status.value)

    if failures:
        first = failures[0]
        print(
            "Counterexample:",
            first.inputs,
            "expected=",
            first.expected,
            "actual=",
            first.actual,
        )


# ============================================================================
# 13. PROPERTY-STYLE TESTING
# ============================================================================

def verify_addition_for_range(limit: int) -> bool:
    """
    Check a mathematical property over a finite range:

        a + b == b + a

    This is a lightweight property-based testing technique without an
    external testing package.
    """
    for a in range(limit):
        for b in range(limit):
            if a + b != b + a:
                return False
    return True


def verify_boolean_algebra_properties() -> dict[str, bool]:
    """Check several algebraic properties exhaustively."""
    results: dict[str, bool] = {}

    values = [False, True]

    results["commutative AND"] = all(
        (a and b) == (b and a)
        for a, b in product(values, repeat=2)
    )

    results["commutative OR"] = all(
        (a or b) == (b or a)
        for a, b in product(values, repeat=2)
    )

    results["associative AND"] = all(
        ((a and b) and c) == (a and (b and c))
        for a, b, c in product(values, repeat=3)
    )

    results["associative OR"] = all(
        ((a or b) or c) == (a or (b or c))
        for a, b, c in product(values, repeat=3)
    )

    results["distributive AND over OR"] = all(
        (a and (b or c)) == ((a and b) or (a and c))
        for a, b, c in product(values, repeat=3)
    )

    return results


def demonstrate_property_testing() -> None:
    print("\n=== PROPERTY-STYLE TESTING ===")

    print(
        "Integer addition commutativity:",
        verify_addition_for_range(20),
    )

    for property_name, passed in verify_boolean_algebra_properties().items():
        print(f"{property_name}: {passed}")


# ============================================================================
# 14. THREE-VALUED LOGIC
# ============================================================================

class TruthValue(Enum):
    FALSE = 0
    UNKNOWN = 1
    TRUE = 2


def three_valued_not(value: TruthValue) -> TruthValue:
    if value is TruthValue.TRUE:
        return TruthValue.FALSE
    if value is TruthValue.FALSE:
        return TruthValue.TRUE
    return TruthValue.UNKNOWN


def three_valued_and(left: TruthValue, right: TruthValue) -> TruthValue:
    if left is TruthValue.FALSE or right is TruthValue.FALSE:
        return TruthValue.FALSE
    if left is TruthValue.UNKNOWN or right is TruthValue.UNKNOWN:
        return TruthValue.UNKNOWN
    return TruthValue.TRUE


def three_valued_or(left: TruthValue, right: TruthValue) -> TruthValue:
    if left is TruthValue.TRUE or right is TruthValue.TRUE:
        return TruthValue.TRUE
    if left is TruthValue.UNKNOWN or right is TruthValue.UNKNOWN:
        return TruthValue.UNKNOWN
    return TruthValue.FALSE


def demonstrate_three_valued_logic() -> None:
    print("\n=== THREE-VALUED LOGIC ===")

    values = list(TruthValue)

    for left, right in product(values, repeat=2):
        result_and = three_valued_and(left, right)
        result_or = three_valued_or(left, right)
        print(
            f"{left.name:7} AND {right.name:7} = {result_and.name:7}; "
            f"OR = {result_or.name:7}"
        )

    print(
        "NOT UNKNOWN =",
        three_valued_not(TruthValue.UNKNOWN).name,
    )


# ============================================================================
# 15. LOGIC CIRCUIT MODEL
# ============================================================================

class Gate:
    """Base abstraction for a Boolean gate."""

    def evaluate(self, *inputs: bool) -> bool:
        raise NotImplementedError


class AndGate(Gate):
    def evaluate(self, *inputs: bool) -> bool:
        if len(inputs) != 2:
            raise ValueError("AND gate requires two inputs.")
        return inputs[0] and inputs[1]


class OrGate(Gate):
    def evaluate(self, *inputs: bool) -> bool:
        if len(inputs) != 2:
            raise ValueError("OR gate requires two inputs.")
        return inputs[0] or inputs[1]


class NotGate(Gate):
    def evaluate(self, *inputs: bool) -> bool:
        if len(inputs) != 1:
            raise ValueError("NOT gate requires one input.")
        return not inputs[0]


def demonstrate_circuit_composition() -> None:
    print("\n=== CIRCUIT COMPOSITION ===")

    # Circuit:
    #
    # A ----\
    #        AND ----\
    # B ----/         OR ---- output
    # C --------------/
    #
    # output = (A AND B) OR C

    and_gate = AndGate()
    or_gate = OrGate()

    for a, b, c in product([False, True], repeat=3):
        output = or_gate.evaluate(and_gate.evaluate(a, b), c)
        print(
            f"A={int(a)} B={int(b)} C={int(c)} "
            f"=> output={int(output)}"
        )


# ============================================================================
# 16. MINI RULE ENGINE
# ============================================================================

@dataclass(frozen=True)
class Transaction:
    amount: float
    account_age_days: int
    identity_verified: bool
    suspicious_location: bool
    trusted_device: bool


def transaction_is_allowed(transaction: Transaction) -> bool:
    """
    Example authorization predicate.

    Conditions:
        amount must be positive,
        identity must be verified,
        account must be at least 30 days old,
        suspicious location must be absent,
        trusted device OR low-value transaction must hold.

    This is illustrative and does not represent a production fraud model.
    """
    amount_valid = transaction.amount > 0
    mature_account = transaction.account_age_days >= 30
    identity_ok = transaction.identity_verified
    location_ok = not transaction.suspicious_location
    device_or_low_value = (
        transaction.trusted_device or transaction.amount <= 1000
    )

    return (
        amount_valid
        and mature_account
        and identity_ok
        and location_ok
        and device_or_low_value
    )


def explain_transaction_decision(transaction: Transaction) -> dict[str, bool]:
    """Return individual predicates to make the decision auditable."""
    return {
        "amount_valid": transaction.amount > 0,
        "mature_account": transaction.account_age_days >= 30,
        "identity_ok": transaction.identity_verified,
        "location_ok": not transaction.suspicious_location,
        "device_or_low_value": (
            transaction.trusted_device or transaction.amount <= 1000
        ),
    }


def demonstrate_rule_engine() -> None:
    print("\n=== RULE ENGINE ===")

    transaction = Transaction(
        amount=750,
        account_age_days=180,
        identity_verified=True,
        suspicious_location=False,
        trusted_device=False,
    )

    decision = transaction_is_allowed(transaction)
    print("Transaction allowed:", decision)

    for name, result in explain_transaction_decision(transaction).items():
        print(f"  {name}: {result}")


# ============================================================================
# 17. DEBUGGING LOGIC
# ============================================================================

def debug_predicate(
    name: str,
    predicates: dict[str, bool],
    final_result: bool,
) -> None:
    """Print intermediate predicate values to locate logical errors."""
    print(f"\n{name}")
    for predicate_name, value in predicates.items():
        print(f"  {predicate_name:25} = {value}")
    print(f"  {'FINAL RESULT':25} = {final_result}")


def demonstrate_debugging() -> None:
    print("\n=== DEBUGGING LOGICAL CONDITIONS ===")

    user = User(
        age=22,
        email_verified=True,
        account_active=True,
        is_admin=False,
        has_two_factor_authentication=True,
    )

    predicates = {
        "account_active": user.account_active,
        "email_verified": user.email_verified,
        "is_admin": user.is_admin,
        "mfa": user.has_two_factor_authentication,
        "admin_or_mfa": user.is_admin or user.has_two_factor_authentication,
    }

    result = secure_login_allowed(user)

    debug_predicate("Login decision", predicates, result)


# ============================================================================
# 18. EDGE CASES AND COMMON LOGICAL MISTAKES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\n=== EDGE CASES AND COMMON MISTAKES ===")

    # Mistake: confusing equality with assignment.
    # Python uses == for equality and = for assignment.
    value = 10
    print("10 == 10:", value == 10)

    # Mistake: confusing "not A and B" with "not (A and B)".
    a = True
    b = False

    expression_one = not a and b
    expression_two = not (a and b)

    print("not A and B:", expression_one)
    print("not (A and B):", expression_two)

    # Empty collections have Boolean semantics in Python.
    print("bool([]):", bool([]))
    print("bool([1]):", bool([1]))

    # Short-circuit evaluation:
    # the second operand is not evaluated when the first operand is enough.
    def unsafe_operation() -> bool:
        raise RuntimeError("This function should not execute.")

    result = False and unsafe_operation()
    print("Short-circuit result:", result)


# ============================================================================
# 19. PERFORMANCE CONSIDERATIONS
# ============================================================================

def benchmark_like_operation(iterations: int = 1_000_000) -> int:
    """
    A simple deterministic workload.

    Boolean operations are normally O(1), but evaluating a large collection
    with all()/any() is O(n) in the worst case and may terminate early.
    """
    count = 0

    for index in range(iterations):
        if (index % 2 == 0) and (index % 3 == 0):
            count += 1

    return count


def demonstrate_performance_concepts() -> None:
    print("\n=== PERFORMANCE CONCEPTS ===")

    result = benchmark_like_operation(100_000)
    print("Matches in 100,000 iterations:", result)

    print("Single Boolean gate: O(1)")
    print("Truth table for n variables: O(2^n)")
    print("Linear predicate scan: O(n) worst case")
    print("Nested exhaustive verification: potentially exponential")


# ============================================================================
# 20. CAPSTONE VERIFICATION SUITE
# ============================================================================

def run_verification_suite() -> None:
    print("\n=== CAPSTONE VERIFICATION SUITE ===")

    checks: list[tuple[str, Callable[[], bool]]] = [
        (
            "AND truth definition",
            lambda: all(
                logical_and(a, b) == (a and b)
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "OR truth definition",
            lambda: all(
                logical_or(a, b) == (a or b)
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "XOR truth definition",
            lambda: all(
                logical_xor(a, b) == (a != b)
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "NAND definition",
            lambda: all(
                logical_nand(a, b) == (not (a and b))
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "NOR definition",
            lambda: all(
                logical_nor(a, b) == (not (a or b))
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "XNOR definition",
            lambda: all(
                logical_xnor(a, b) == (a == b)
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "De Morgan law 1",
            lambda: all(
                not (a and b) == ((not a) or (not b))
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "De Morgan law 2",
            lambda: all(
                not (a or b) == ((not a) and (not b))
                for a, b in product([False, True], repeat=2)
            ),
        ),
        (
            "Binary adder",
            lambda: all(
                integer_from_bits(
                    add_binary_bits(
                        bits_from_integer(a, 5),
                        bits_from_integer(b, 5),
                    )
                ) == a + b
                for a, b in product(range(16), repeat=2)
            ),
        ),
    ]

    failures = 0

    for name, check in checks:
        try:
            passed = check()
        except Exception as error:
            passed = False
            print(f"{name}: ERROR ({error})")

        if passed:
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")
            failures += 1

    print(f"\nVerification checks: {len(checks)}")
    print(f"Failures: {failures}")

    if failures:
        raise AssertionError("Verification suite failed.")

    print("All verification checks passed.")


# ============================================================================
# 21. MAIN STUDY PROGRAM
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("LOGIC IN COMPUTING")
    print("Digital Logic | Predicates | Assertions | Verification")
    print("=" * 78)

    demonstrate_truth_tables()
    demonstrate_boolean_laws()
    demonstrate_adders()
    demonstrate_predicates()
    demonstrate_quantifiers()
    demonstrate_assertions()
    demonstrate_contracts()
    demonstrate_security_predicate()
    demonstrate_equivalence()
    demonstrate_decision_table()
    demonstrate_exhaustive_verification()
    demonstrate_property_testing()
    demonstrate_three_valued_logic()
    demonstrate_circuit_composition()
    demonstrate_rule_engine()
    demonstrate_debugging()
    demonstrate_edge_cases()
    demonstrate_performance_concepts()
    run_verification_suite()

    print("\nStudy program completed successfully.")


if __name__ == "__main__":
    main()
