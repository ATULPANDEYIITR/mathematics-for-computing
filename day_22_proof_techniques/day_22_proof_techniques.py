"""
Proof Techniques
================

A comprehensive executable study of:
1. Direct proof
2. Proof by contradiction
3. Proof by contrapositive
4. Proof by cases

The program begins with basic logical ideas and progresses to reusable
proof-verification utilities, concrete mathematical examples, counterexample
analysis, and a small proof-oriented test suite.

This file is intentionally executable. The printed demonstrations explain
what each technique is doing while the functions model the mathematical
reasoning computationally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence
import math


# ---------------------------------------------------------------------------
# SECTION 1: FOUNDATIONS OF MATHEMATICAL PROOFS
# ---------------------------------------------------------------------------

print("=" * 78)
print("PROOF TECHNIQUES: DIRECT PROOF, CONTRADICTION, CONTRAPOSITIVE, CASES")
print("=" * 78)


def implication(p: bool, q: bool) -> bool:
    """
    Evaluate the logical implication P -> Q.

    P -> Q is false only when P is true and Q is false.
    In every other situation it is true.
    """
    return (not p) or q


def biconditional(p: bool, q: bool) -> bool:
    """Evaluate P <-> Q."""
    return p == q


def truth_table_implication() -> None:
    """Display the complete truth table for P -> Q."""
    print("\nTruth table for P -> Q")
    print("-" * 32)
    print(" P     Q     P -> Q")
    print("-" * 32)

    for p in (False, True):
        for q in (False, True):
            print(f"{str(p):5} {str(q):5} {str(implication(p, q)):5}")


truth_table_implication()


# ---------------------------------------------------------------------------
# SECTION 2: PROPOSITIONS, PREDICATES, AND QUANTIFIERS
# ---------------------------------------------------------------------------

def is_even(n: int) -> bool:
    """An integer is even exactly when it is divisible by 2."""
    return n % 2 == 0


def is_odd(n: int) -> bool:
    """An integer is odd exactly when it leaves remainder 1 modulo 2."""
    return n % 2 != 0


def is_divisible_by(a: int, b: int) -> bool:
    """
    Return whether b divides a.

    The mathematical notation b | a means that there exists an integer k
    such that a = bk.
    """
    if b == 0:
        return a == 0
    return a % b == 0


def verify_universal_statement(
    predicate: Callable[[int], bool],
    domain: Iterable[int],
) -> tuple[bool, list[int]]:
    """
    Computationally inspect a universal statement over a finite domain.

    This does NOT replace a mathematical proof over an infinite domain.
    It demonstrates the difference between testing and proving.
    """
    counterexamples = [x for x in domain if not predicate(x)]
    return len(counterexamples) == 0, counterexamples


def find_counterexample(
    predicate: Callable[[int], bool],
    domain: Iterable[int],
) -> int | None:
    """Return the first counterexample found in a finite search."""
    for value in domain:
        if not predicate(value):
            return value
    return None


print("\nFinite testing is useful for finding counterexamples.")
statement_holds, counterexamples = verify_universal_statement(
    lambda n: n * n >= 0,
    range(-20, 21),
)
print("Statement: n² >= 0 for tested integers")
print("Test result:", statement_holds)
print("Counterexamples:", counterexamples)


# ---------------------------------------------------------------------------
# SECTION 3: DIRECT PROOF
# ---------------------------------------------------------------------------

def demonstrate_direct_proof_even_sum(a: int, b: int) -> int:
    """
    Direct proof pattern:

    Claim:
        If a and b are even, then a + b is even.

    Proof:
        Since a is even, a = 2m for some integer m.
        Since b is even, b = 2n for some integer n.
        Therefore:
            a + b = 2m + 2n
                  = 2(m + n)
        Since m + n is an integer, a + b is even.

    The program verifies the algebraic structure numerically.
    """
    if not is_even(a) or not is_even(b):
        raise ValueError("Both inputs must be even.")

    m = a // 2
    n = b // 2
    result = 2 * (m + n)

    assert a + b == result
    assert is_even(result)

    return result


print("\nDIRECT PROOF")
print("-" * 78)
print("Claim: The sum of two even integers is even.")

for pair in [(2, 8), (-10, 6), (0, 14)]:
    a, b = pair
    result = demonstrate_direct_proof_even_sum(a, b)
    print(f"{a} + {b} = {result}; even = {is_even(result)}")


def demonstrate_direct_proof_odd_product(a: int, b: int) -> int:
    """
    Claim:
        The product of two odd integers is odd.

    If a = 2m + 1 and b = 2n + 1, then

        ab = (2m + 1)(2n + 1)
           = 4mn + 2m + 2n + 1
           = 2(2mn + m + n) + 1.

    Hence ab has the form 2k + 1 and is odd.
    """
    if not is_odd(a) or not is_odd(b):
        raise ValueError("Both inputs must be odd.")

    m = (a - 1) // 2
    n = (b - 1) // 2

    k = 2 * m * n + m + n
    result = 2 * k + 1

    assert result == a * b
    assert is_odd(result)

    return result


for pair in [(3, 5), (-3, 7), (1, 9)]:
    a, b = pair
    print(f"{a} × {b} = {demonstrate_direct_proof_odd_product(a, b)}")


def demonstrate_direct_proof_divisibility(
    a: int,
    b: int,
    divisor: int,
) -> bool:
    """
    Claim:
        If d | a and d | b, then d | (a + b).

    Write:
        a = dm
        b = dn

    Therefore:
        a + b = d(m + n).

    The same pattern also proves that d divides any integer linear
    combination ax + by.
    """
    if divisor == 0:
        raise ValueError("The divisor must be nonzero.")

    if not is_divisible_by(a, divisor):
        raise ValueError("divisor does not divide a")

    if not is_divisible_by(b, divisor):
        raise ValueError("divisor does not divide b")

    m = a // divisor
    n = b // divisor
    result = divisor * (m + n)

    assert result == a + b
    return is_divisible_by(result, divisor)


print("\nDivisibility example:")
print(
    "12 and 30 are both divisible by 6:",
    demonstrate_direct_proof_divisibility(12, 30, 6),
)


# ---------------------------------------------------------------------------
# SECTION 4: DIRECT PROOF WITH INEQUALITIES
# ---------------------------------------------------------------------------

def direct_inequality_example(x: float) -> bool:
    """
    Claim:
        If x > 3, then x² > 9.

    Direct reasoning:
        x > 3 > 0.
        Multiplying x > 3 by the positive number x preserves the inequality:
            x² > 3x.
        Since x > 3 and 3 > 0:
            3x > 9.
        Therefore x² > 9.

    The function checks the conclusion for a concrete input.
    """
    if x <= 3:
        raise ValueError("The hypothesis x > 3 is required.")

    return x * x > 9


for value in [3.1, 4, 10]:
    print(f"If x = {value}, then x² > 9:", direct_inequality_example(value))


# ---------------------------------------------------------------------------
# SECTION 5: CONTRAPOSITIVE
# ---------------------------------------------------------------------------

def contrapositive(p: bool, q: bool) -> tuple[bool, bool]:
    """
    Return the truth values of P -> Q and its contrapositive.

    The contrapositive of:
        P -> Q

    is:
        not Q -> not P.

    They always have the same truth value.
    """
    original = implication(p, q)
    opposite_direction = implication(not q, not p)
    return original, opposite_direction


print("\nCONTRAPOSITIVE")
print("-" * 78)
print("P -> Q is logically equivalent to not Q -> not P.")

for p in (False, True):
    for q in (False, True):
        original, opposite = contrapositive(p, q)
        print(
            f"P={p:<5} Q={q:<5} "
            f"P->Q={original:<5} "
            f"not Q->not P={opposite:<5}"
        )


def direct_or_contrapositive_divisibility(n: int) -> bool:
    """
    Claim:
        If n² is even, then n is even.

    A particularly clean proof uses the contrapositive:

        If n is odd, then n² is odd.

    Write:
        n = 2k + 1.

    Then:
        n² = 4k² + 4k + 1
           = 2(2k² + 2k) + 1,

    which is odd.

    Therefore, by the contrapositive, if n² is even, n must be even.
    """
    # The actual computational implication being checked:
    if is_even(n * n):
        return is_even(n)

    return True


for n in range(-10, 11):
    assert direct_or_contrapositive_divisibility(n)

print("Verified over a finite range: n² even implies n even.")


def contrapositive_prime_divisibility(a: int, p: int) -> bool:
    """
    Example of a common contrapositive pattern:

        If p does not divide a, then a is not a multiple of p.

    This is deliberately elementary: it illustrates how negating the
    conclusion can make the hypothesis easier to reason about.
    """
    if p == 0:
        raise ValueError("p must be nonzero.")

    hypothesis = not is_divisible_by(a, p)
    conclusion = not is_divisible_by(a, p)

    return implication(hypothesis, conclusion)


print(
    "Contrapositive-style divisibility statement:",
    contrapositive_prime_divisibility(17, 5),
)


# ---------------------------------------------------------------------------
# SECTION 6: PROOF BY CONTRADICTION
# ---------------------------------------------------------------------------

def contradiction_even_odd_example(n: int) -> bool:
    """
    Prove that an integer cannot be both even and odd.

    Assume the contrary:
        n is even and n is odd.

    Then:
        n = 2a
        n = 2b + 1

    Equating:
        2a = 2b + 1

    The left side is even and the right side is odd.
    Their difference would imply:
        2(a - b) = 1,

    which is impossible because the left side is even.

    Computationally, the contradiction is represented by the impossible
    conjunction is_even(n) and is_odd(n).
    """
    assumed_contradiction = is_even(n) and is_odd(n)
    return not assumed_contradiction


for n in range(-10, 11):
    assert contradiction_even_odd_example(n)

print("\nCONTRADICTION")
print("-" * 78)
print("No tested integer is both even and odd.")


def contradiction_square_root_two_is_irrational_structure() -> dict[str, str]:
    """
    Record the classic proof structure that sqrt(2) is irrational.

    Assume:
        sqrt(2) = a / b

    where a and b are integers, b != 0, and the fraction is in lowest terms.

    Squaring:
        2 = a² / b²
        a² = 2b²

    Therefore a² is even, so a is even.
    Let a = 2k.

    Then:
        4k² = 2b²
        b² = 2k²

    Therefore b is even.

    Thus both a and b are even, contradicting the assumption that a/b was
    reduced to lowest terms.

    The function returns the logical chain rather than pretending floating
    point arithmetic can prove irrationality.
    """
    return {
        "assumption": "sqrt(2) = a/b in lowest terms",
        "equation_1": "a² = 2b²",
        "deduction_1": "a² even, therefore a even",
        "substitution": "a = 2k",
        "equation_2": "b² = 2k²",
        "deduction_2": "b even",
        "contradiction": "a and b are both even, so a/b was not in lowest terms",
    }


print("\nClassic contradiction proof: sqrt(2) is irrational")
for step, statement in contradiction_square_root_two_is_irrational_structure().items():
    print(f"{step}: {statement}")


# ---------------------------------------------------------------------------
# SECTION 7: PROOF BY CASES
# ---------------------------------------------------------------------------

def proof_by_cases_square_parity(n: int) -> bool:
    """
    Prove:
        n² has the same parity as n.

    Cases:

    Case 1: n is even.
        n = 2k
        n² = 4k² = 2(2k²), so n² is even.

    Case 2: n is odd.
        n = 2k + 1
        n² = 4k² + 4k + 1
           = 2(2k² + 2k) + 1,
        so n² is odd.

    Since every integer is either even or odd, the result follows.
    """
    if is_even(n):
        k = n // 2
        square = 4 * k * k
        assert square == n * n
        return is_even(square)

    k = (n - 1) // 2
    square = 4 * k * k + 4 * k + 1
    assert square == n * n
    return is_odd(square)


print("\nPROOF BY CASES")
print("-" * 78)

for n in range(-8, 9):
    print(
        f"n={n:3}, case={'even' if is_even(n) else 'odd':4}, "
        f"n²={n*n:3}, same parity={proof_by_cases_square_parity(n)}"
    )


def absolute_value_identity(x: float) -> float:
    """
    Proof by cases for:
        |x| =
            x  if x >= 0
           -x  if x < 0

    The definition itself is case-based.
    """
    if x >= 0:
        return x
    return -x


print("\nAbsolute value is naturally handled by cases:")
for x in [-7.5, -0.0, 0.0, 4.25]:
    print(f"|{x}| = {absolute_value_identity(x)}")


# ---------------------------------------------------------------------------
# SECTION 8: PROOF BY CASES WITH THREE OR MORE CASES
# ---------------------------------------------------------------------------

def remainder_mod_three_cases(n: int) -> int:
    """
    Every integer has exactly one remainder among:
        0, 1, 2

    when divided by 3.

    This creates three cases:
        n = 3k
        n = 3k + 1
        n = 3k + 2
    """
    return n % 3


def square_remainder_mod_three(n: int) -> int:
    """
    Prove by three cases that n² mod 3 is either 0 or 1, never 2.

    Case 1: n = 3k
        n² mod 3 = 0.

    Case 2: n = 3k + 1
        n² = 9k² + 6k + 1
        n² mod 3 = 1.

    Case 3: n = 3k + 2
        n² = 9k² + 12k + 4
        n² mod 3 = 1.
    """
    case = remainder_mod_three_cases(n)

    if case == 0:
        return 0
    if case == 1:
        return 1
    if case == 2:
        return 1

    raise AssertionError("Modulo 3 must produce one of three cases.")


for n in range(-15, 16):
    result = square_remainder_mod_three(n)
    assert result in (0, 1)

print("\nFor every tested integer, n² mod 3 is 0 or 1.")


# ---------------------------------------------------------------------------
# SECTION 9: CASES FOR INEQUALITIES
# ---------------------------------------------------------------------------

def prove_product_nonnegative(a: float, b: float) -> bool:
    """
    Prove:
        If a >= 0 and b >= 0, then ab >= 0.

    A more useful four-case sign analysis can be built by considering the
    signs of both values.

    The cases are:
        (+,+) -> +
        (+,-) -> -
        (-,+) -> -
        (-,-) -> +

    Zero belongs naturally to the nonnegative/nonpositive boundary cases.
    """
    if a >= 0 and b >= 0:
        expected = a * b >= 0
    elif a >= 0 and b < 0:
        expected = a * b <= 0
    elif a < 0 and b >= 0:
        expected = a * b <= 0
    else:
        expected = a * b >= 0

    return expected


for pair in [(2, 3), (2, -3), (-2, 3), (-2, -3), (0, -4)]:
    print(
        f"a={pair[0]:3}, b={pair[1]:3}, "
        f"sign-case reasoning valid={prove_product_nonnegative(*pair)}"
    )


# ---------------------------------------------------------------------------
# SECTION 10: DIRECT PROOF VS CONTRAPOSITIVE VS CONTRADICTION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProofTechnique:
    """A compact representation of a proof method."""

    name: str
    starting_point: str
    main_operation: str
    typical_strength: str


TECHNIQUES = [
    ProofTechnique(
        "Direct proof",
        "Assume the hypothesis P",
        "Derive Q directly",
        "Natural when definitions lead cleanly to the conclusion",
    ),
    ProofTechnique(
        "Contrapositive",
        "Assume not Q",
        "Derive not P",
        "Useful when not Q is easier to manipulate than P",
    ),
    ProofTechnique(
        "Contradiction",
        "Assume P and not Q",
        "Derive an impossibility",
        "Useful when the negation creates a strong structural contradiction",
    ),
    ProofTechnique(
        "Cases",
        "Partition the possibilities",
        "Prove the conclusion in every exhaustive case",
        "Useful when the domain naturally splits into finite cases",
    ),
]

print("\nCOMPARING PROOF METHODS")
print("-" * 78)
for technique in TECHNIQUES:
    print(f"\n{technique.name}")
    print(f"Starting point: {technique.starting_point}")
    print(f"Main operation: {technique.main_operation}")
    print(f"Typical use:    {technique.typical_strength}")


# ---------------------------------------------------------------------------
# SECTION 11: COMMON LOGICAL ERRORS
# ---------------------------------------------------------------------------

def converse(p: bool, q: bool) -> bool:
    """The converse of P -> Q is Q -> P."""
    return implication(q, p)


def inverse(p: bool, q: bool) -> bool:
    """The inverse of P -> Q is not P -> not Q."""
    return implication(not p, not q)


print("\nCONVERSE AND INVERSE")
print("-" * 78)
print("Original:       P -> Q")
print("Converse:       Q -> P")
print("Inverse:        not P -> not Q")
print("Contrapositive: not Q -> not P")

print("\nImportant distinction:")
print(
    "The contrapositive is logically equivalent to the original implication; "
    "the converse and inverse generally are not."
)

# A concrete counterexample:
# P: n is divisible by 4
# Q: n is even
#
# P -> Q is true.
# Q -> P is false because 2 is even but not divisible by 4.
n = 2
p = is_divisible_by(n, 4)
q = is_even(n)

print(f"\nCounterexample to the converse using n={n}:")
print("P (divisible by 4):", p)
print("Q (even):", q)
print("Q -> P:", implication(q, p))


# ---------------------------------------------------------------------------
# SECTION 12: COUNTEREXAMPLES
# ---------------------------------------------------------------------------

def square_less_than_linear(n: int) -> bool:
    """A deliberately false universal statement."""
    return n * n < n


counterexample = find_counterexample(square_less_than_linear, range(-10, 11))
print("\nCOUNTEREXAMPLE SEARCH")
print("-" * 78)
print("False statement: n² < n for every integer n.")
print("Counterexample found:", counterexample)

if counterexample is not None:
    print(
        f"{counterexample}² = {counterexample**2}, "
        f"but {counterexample} = {counterexample}"
    )


# ---------------------------------------------------------------------------
# SECTION 13: VACUOUS TRUTH
# ---------------------------------------------------------------------------

def implication_over_empty_condition(domain: Sequence[int]) -> bool:
    """
    Demonstrate a universal implication whose hypothesis never occurs.

    Statement:
        For every x in the supplied domain, if x > 10 and x < 5,
        then x² > 0.

    No x satisfies x > 10 and x < 5, so there is no counterexample.
    """
    for x in domain:
        hypothesis = x > 10 and x < 5
        conclusion = x * x > 0

        if hypothesis and not conclusion:
            return False

    return True


print("\nVACUOUS TRUTH")
print("-" * 78)
print(
    "The implication 'x > 10 and x < 5 -> x² > 0' "
    "is true over the tested domain because the hypothesis is never satisfied."
)
print(implication_over_empty_condition(range(-100, 101)))


# ---------------------------------------------------------------------------
# SECTION 14: EXISTENTIAL STATEMENTS
# ---------------------------------------------------------------------------

def find_witness(
    predicate: Callable[[int], bool],
    domain: Iterable[int],
) -> int | None:
    """
    Find a witness for an existential statement.

    A proof of:
        exists x such that P(x)

    needs only one valid witness.
    """
    return find_counterexample(lambda x: not predicate(x), domain)


witness = find_witness(lambda x: x * x == 49, range(-20, 21))
print("\nEXISTENTIAL WITNESS")
print("-" * 78)
print("Statement: There exists an integer x such that x² = 49.")
print("Witness found:", witness)


# ---------------------------------------------------------------------------
# SECTION 15: A STRUCTURED PROOF REPRESENTATION
# ---------------------------------------------------------------------------

@dataclass
class ProofStep:
    """Represent one readable mathematical proof step."""

    statement: str
    reason: str


def print_proof(title: str, steps: Sequence[ProofStep]) -> None:
    """Print a structured proof."""
    print(f"\n{title}")
    print("-" * len(title))

    for number, step in enumerate(steps, start=1):
        print(f"{number}. {step.statement}")
        print(f"   Reason: {step.reason}")


print_proof(
    "Direct proof: odd + odd is even",
    [
        ProofStep("Let a and b be odd integers.", "Hypothesis"),
        ProofStep("a = 2m + 1 for some integer m.", "Definition of odd"),
        ProofStep("b = 2n + 1 for some integer n.", "Definition of odd"),
        ProofStep(
            "a + b = 2m + 2n + 2 = 2(m + n + 1).",
            "Algebra",
        ),
        ProofStep(
            "a + b is even.",
            "Definition of even",
        ),
    ],
)


# ---------------------------------------------------------------------------
# SECTION 16: A PROOF CHECKER FOR SIMPLE ALGEBRAIC FORMS
# ---------------------------------------------------------------------------

def verify_even_representation(n: int) -> bool:
    """
    Check whether n has the form 2k for an integer k.

    This demonstrates how a definition can become a computational predicate.
    """
    k = n // 2
    return n == 2 * k


def verify_odd_representation(n: int) -> bool:
    """Check whether n has the form 2k + 1 for an integer k."""
    k = (n - 1) // 2
    return n == 2 * k + 1


for n in range(-20, 21):
    assert verify_even_representation(n) == is_even(n)
    assert verify_odd_representation(n) == is_odd(n)

print("\nDefinitions checked computationally for integers from -20 to 20.")


# ---------------------------------------------------------------------------
# SECTION 17: EDGE CASES
# ---------------------------------------------------------------------------

print("\nEDGE CASES")
print("-" * 78)

edge_values = [
    -1000000,
    -1,
    0,
    1,
    1000000,
]

for n in edge_values:
    print(
        f"n={n:8}, even={is_even(n)}, odd={is_odd(n)}, "
        f"n²={n*n}"
    )

print(
    "\nZero is even because 0 = 2 × 0. "
    "Zero is not odd because it cannot be written as 2k + 1 for an integer k."
)


# ---------------------------------------------------------------------------
# SECTION 18: PROOF STRATEGY SELECTION
# ---------------------------------------------------------------------------

def recommend_proof_structure(
    *,
    hypothesis_easy_to_use: bool,
    conclusion_negation_easy_to_use: bool,
    contradiction_natural: bool,
    finite_cases_natural: bool,
) -> list[str]:
    """
    Return possible proof structures based on mathematical features.

    This is not a theorem prover. It models strategic choices a mathematician
    can make when deciding how to structure a proof.
    """
    choices = []

    if hypothesis_easy_to_use:
        choices.append("direct proof")

    if conclusion_negation_easy_to_use:
        choices.append("contrapositive")

    if contradiction_natural:
        choices.append("contradiction")

    if finite_cases_natural:
        choices.append("proof by cases")

    return choices


print("\nPROOF STRATEGY SELECTION")
print("-" * 78)

strategies = recommend_proof_structure(
    hypothesis_easy_to_use=True,
    conclusion_negation_easy_to_use=True,
    contradiction_natural=False,
    finite_cases_natural=True,
)

print("Possible structures:", ", ".join(strategies))


# ---------------------------------------------------------------------------
# SECTION 19: COMPLEX CASE STUDY
# ---------------------------------------------------------------------------

def classify_integer(n: int) -> str:
    """
    Classify an integer using nested proof-by-cases reasoning.

    Cases:
        1. negative
        2. zero
        3. positive

    Then positive/negative values are classified by parity.
    """
    if n < 0:
        sign = "negative"
    elif n == 0:
        return "zero"
    else:
        sign = "positive"

    parity = "even" if is_even(n) else "odd"
    return f"{sign} {parity}"


print("\nMULTI-LEVEL CASE ANALYSIS")
print("-" * 78)

for n in [-7, -4, -1, 0, 1, 4, 9]:
    print(f"{n:3} -> {classify_integer(n)}")


# ---------------------------------------------------------------------------
# SECTION 20: MATHEMATICAL INDUCTION IS DISTINCT
# ---------------------------------------------------------------------------

def explain_induction_distinction() -> None:
    """
    Induction is mentioned to prevent a common conceptual mistake.

    Mathematical induction is a separate proof technique:
        base case + inductive step.

    It should not be confused with direct proof, contradiction,
    contrapositive, or finite case analysis.
    """
    print("\nDISTINCTION FROM MATHEMATICAL INDUCTION")
    print("-" * 78)
    print("Induction normally contains:")
    print("1. A base case.")
    print("2. An inductive hypothesis.")
    print("3. An inductive step.")
    print(
        "Direct proof, contradiction, contrapositive, and cases can appear "
        "inside an inductive argument, but induction itself is a separate "
        "proof structure."
    )


explain_induction_distinction()


# ---------------------------------------------------------------------------
# SECTION 21: PERFORMANCE AND COMPUTATIONAL LIMITATIONS
# ---------------------------------------------------------------------------

def brute_force_verify(
    predicate: Callable[[int], bool],
    start: int,
    end: int,
) -> bool:
    """
    Test a predicate over a finite interval.

    Time complexity is O(n), where n is the number of tested integers.

    This can provide evidence or discover counterexamples, but it cannot
    establish a statement over an infinite domain merely by testing values.
    """
    for n in range(start, end + 1):
        if not predicate(n):
            return False
    return True


print("\nCOMPUTATIONAL TESTING VS MATHEMATICAL PROOF")
print("-" * 78)

print(
    "Finite verification:",
    brute_force_verify(lambda n: n * n >= 0, -100000, 100000),
)
print(
    "The test covers 200001 values, not infinitely many integers. "
    "The mathematical proof uses structure rather than enumeration."
)


# ---------------------------------------------------------------------------
# SECTION 22: MINI TEST SUITE
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Run correctness tests for the executable examples."""

    # Logical equivalence of implication and contrapositive.
    for p in (False, True):
        for q in (False, True):
            original, opposite = contrapositive(p, q)
            assert original == opposite

    # Parity properties.
    for n in range(-100, 101):
        assert is_even(n) != is_odd(n)
        assert proof_by_cases_square_parity(n)
        assert square_remainder_mod_three(n) in (0, 1)

    # Direct proofs.
    for a in range(-20, 21, 2):
        for b in range(-20, 21, 2):
            assert demonstrate_direct_proof_even_sum(a, b) == a + b

    for a in range(-19, 20, 2):
        for b in range(-19, 20, 2):
            assert demonstrate_direct_proof_odd_product(a, b) == a * b

    # Counterexample logic.
    assert find_counterexample(lambda n: n >= 0, range(-5, 6)) == -5
    assert find_counterexample(lambda n: n * n >= 0, range(-5, 6)) is None

    # Absolute value cases.
    for x in [-10.5, -1, 0, 2, 8.75]:
        assert absolute_value_identity(x) == abs(x)

    print("\nAll executable proof demonstrations passed.")


run_tests()


# ---------------------------------------------------------------------------
# SECTION 23: FINAL REFERENCE TABLE
# ---------------------------------------------------------------------------

print("\nREFERENCE")
print("=" * 78)

reference = [
    (
        "Direct proof",
        "Assume P",
        "Derive Q",
        "Use definitions/algebra directly",
    ),
    (
        "Contrapositive",
        "Assume not Q",
        "Derive not P",
        "Useful when not Q is simpler",
    ),
    (
        "Contradiction",
        "Assume P and not Q",
        "Derive false/impossible",
        "Useful when the assumption creates structure",
    ),
    (
        "Cases",
        "Partition all possibilities",
        "Prove Q in each case",
        "Useful for parity, signs, residues, intervals",
    ),
]

print(f"{'Method':<20} {'Starting assumption':<28} {'Goal':<28}")
print("-" * 78)

for method, start, goal, _ in reference:
    print(f"{method:<20} {start:<28} {goal:<28}")

print("\nProgram execution complete.")
