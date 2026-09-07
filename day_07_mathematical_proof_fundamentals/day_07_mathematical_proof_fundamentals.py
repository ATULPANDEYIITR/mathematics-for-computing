"""
Mathematical Proof Fundamentals
================================

A comprehensive executable study script covering:

1. Statements and truth values
2. Propositions
3. Assumptions and hypotheses
4. Conclusions
5. Logical implication
6. Direct proofs
7. Proof structure
8. Counterexamples
9. Universal and existential statements
10. Common proof mistakes
11. Edge cases and vacuous truth
12. Contrapositive reasoning
13. Proof by contradiction
14. Mathematical examples implemented and verified with Python

Important distinction:
Python experimentation can support mathematical reasoning, discover
patterns, test examples, and find counterexamples. Finite computational
testing is not, by itself, a proof of a statement about infinitely many
objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, TypeVar


T = TypeVar("T")


# =============================================================================
# 1. STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("1. STATEMENTS")
print("=" * 80)

# A mathematical statement is a declarative sentence that has a definite truth
# value: true or false.

statement_examples = {
    "2 + 3 = 5": True,
    "10 is less than 4": False,
    "7 is a prime number": True,
    "0 is greater than 1": False,
}

for statement, truth_value in statement_examples.items():
    print(f"{statement!r} -> {truth_value}")

# Questions, commands, and expressions with unspecified variables are usually
# not propositions by themselves.

print("\nExamples that are NOT propositions until more information is supplied:")
non_propositions = [
    "What is your name?",
    "Close the door.",
    "x + 2 = 7",
]
for item in non_propositions:
    print(f"- {item}")

# The expression x + 2 = 7 becomes a proposition if a value for x is supplied.
x = 5
print(f"\nFor x = {x}, x + 2 = 7 is {x + 2 == 7}")


# =============================================================================
# 2. PROPOSITIONS
# =============================================================================

print("\n" + "=" * 80)
print("2. PROPOSITIONS")
print("=" * 80)

# A proposition is a statement that is either True or False.

@dataclass(frozen=True)
class Proposition:
    """Represents a mathematical proposition with a known truth value."""

    description: str
    truth_value: bool

    def __str__(self) -> str:
        return f"{self.description}: {self.truth_value}"


prime_proposition = Proposition("13 is prime", True)
composite_proposition = Proposition("21 is prime", False)

print(prime_proposition)
print(composite_proposition)


# =============================================================================
# 3. COMPOUND PROPOSITIONS
# =============================================================================

print("\n" + "=" * 80)
print("3. COMPOUND PROPOSITIONS")
print("=" * 80)

# Mathematical arguments often combine propositions using logical operators.

P = True
Q = False

logical_results = {
    "P AND Q": P and Q,
    "P OR Q": P or Q,
    "NOT P": not P,
    "P -> Q (implication)": (not P) or Q,
    "P <-> Q (biconditional)": P == Q,
}

for expression, result in logical_results.items():
    print(f"{expression} = {result}")


def implication(p: bool, q: bool) -> bool:
    """
    Logical implication P -> Q.

    It is false only when P is true and Q is false.

    Equivalent logical form:
        P -> Q  is equivalent to  NOT P OR Q
    """
    return (not p) or q


print("\nTruth table for implication P -> Q:")
for p in (True, False):
    for q in (True, False):
        print(f"P={p:<5} Q={q:<5} P->Q={implication(p, q)}")


# =============================================================================
# 4. CONDITIONAL STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("4. CONDITIONAL STATEMENTS")
print("=" * 80)

# A conditional statement has the form:
#
#     If P, then Q.
#
# P is the hypothesis, assumption, premise, or antecedent.
# Q is the conclusion or consequent.
#
# Example:
#
#     If n is an even integer, then n^2 is even.


def is_even(n: int) -> bool:
    return n % 2 == 0


def conditional_even_square(n: int) -> bool:
    """Tests: If n is even, then n^2 is even."""
    hypothesis = is_even(n)
    conclusion = is_even(n * n)
    return implication(hypothesis, conclusion)


for n in range(-5, 6):
    print(
        f"n={n:2d}, "
        f"hypothesis(n even)={is_even(n)}, "
        f"conclusion(n² even)={is_even(n * n)}, "
        f"conditional={conditional_even_square(n)}"
    )


# =============================================================================
# 5. ASSUMPTIONS AND CONCLUSIONS
# =============================================================================

print("\n" + "=" * 80)
print("5. ASSUMPTIONS AND CONCLUSIONS")
print("=" * 80)

# Consider:
#
#     If a and b are odd integers, then a + b is even.
#
# Assumptions:
#     1. a is an integer.
#     2. b is an integer.
#     3. a is odd.
#     4. b is odd.
#
# Conclusion:
#     a + b is even.


def is_odd(n: int) -> bool:
    return n % 2 != 0


def odd_sum_statement(a: int, b: int) -> bool:
    assumptions = is_odd(a) and is_odd(b)
    conclusion = is_even(a + b)
    return implication(assumptions, conclusion)


test_pairs = [(1, 3), (5, 7), (-3, 9), (2, 5)]

for a, b in test_pairs:
    print(
        f"a={a:2d}, b={b:2d}, "
        f"both assumptions true={is_odd(a) and is_odd(b)}, "
        f"conclusion(a+b even)={is_even(a+b)}, "
        f"statement={odd_sum_statement(a, b)}"
    )


# =============================================================================
# 6. DIRECT PROOF
# =============================================================================

print("\n" + "=" * 80)
print("6. DIRECT PROOF")
print("=" * 80)

# A direct proof begins with the assumptions and uses definitions, known facts,
# algebra, and logical deductions to establish the conclusion.
#
# Example theorem:
#
#     If n is an even integer, then n^2 is even.
#
# Proof:
#
# Assume n is even.
#
# By definition of even, there exists an integer k such that:
#
#     n = 2k
#
# Then:
#
#     n^2 = (2k)^2
#         = 4k^2
#         = 2(2k^2)
#
# Since 2k^2 is an integer, n^2 is divisible by 2.
# Therefore, n^2 is even.


def demonstrate_even_square_direct_proof(n: int) -> Optional[str]:
    """
    Demonstrates the algebraic structure of a direct proof for one even integer.

    This is an illustration, not a proof for all integers by enumeration.
    The general proof depends on representing every even integer as 2k.
    """
    if not is_even(n):
        return None

    k = n // 2
    n_squared = n * n
    new_integer = 2 * k * k

    return (
        f"Assume n = {n} is even. Then n = 2({k}). "
        f"Therefore n² = ({n})² = {n_squared} = 2({new_integer}), "
        f"and {new_integer} is an integer. Hence n² is even."
    )


for n in (-6, 0, 4, 10):
    print(demonstrate_even_square_direct_proof(n))


# =============================================================================
# 7. DEFINITIONS AS PROOF TOOLS
# =============================================================================

print("\n" + "=" * 80)
print("7. DEFINITIONS AS PROOF TOOLS")
print("=" * 80)

# Many proofs start by expanding definitions.
#
# Even integer:
#     n is even if n = 2k for some integer k.
#
# Odd integer:
#     n is odd if n = 2k + 1 for some integer k.
#
# Divisibility:
#     a divides b if b = ak for some integer k.


def divides(a: int, b: int) -> bool:
    """
    Returns whether a divides b.

    Division by zero is not permitted in the usual definition.
    """
    if a == 0:
        return b == 0
    return b % a == 0


def demonstrate_divisibility_transitivity(a: int, b: int, c: int) -> bool:
    """
    Tests the theorem:

        If a divides b and b divides c, then a divides c.

    General direct proof:

        b = am for some integer m
        c = bn for some integer n

    Substituting:

        c = (am)n = a(mn)

    Since mn is an integer, a divides c.
    """
    assumptions = divides(a, b) and divides(b, c)
    conclusion = divides(a, c)
    return implication(assumptions, conclusion)


examples = [(2, 6, 24), (3, 12, 36), (5, 20, 100)]
for a, b, c in examples:
    print(
        f"If {a}|{b} and {b}|{c}, then {a}|{c}: "
        f"{demonstrate_divisibility_transitivity(a, b, c)}"
    )


# =============================================================================
# 8. UNIVERSAL STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("8. UNIVERSAL STATEMENTS")
print("=" * 80)

# A universal statement claims that a property holds for every object in a domain.
#
# Symbolically:
#
#     For every x in D, P(x)
#
# A single counterexample is enough to disprove a universal statement.


def all_satisfy(domain: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    """Finite-domain computational analogue of a universal statement."""
    return all(predicate(value) for value in domain)


finite_domain = range(-10, 11)
result = all_satisfy(finite_domain, lambda n: n * n >= 0)

print("For every tested integer n, n² >= 0:", result)

# Important limitation:
# Checking a finite range does not prove the statement for all integers.


# =============================================================================
# 9. EXISTENTIAL STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("9. EXISTENTIAL STATEMENTS")
print("=" * 80)

# An existential statement claims that at least one object satisfies a property.
#
# Symbolically:
#
#     There exists x in D such that P(x)
#
# To prove an existential statement, one valid witness may be sufficient.


def find_witness(
    domain: Iterable[T],
    predicate: Callable[[T], bool],
) -> Optional[T]:
    """Returns one witness satisfying the predicate, if one exists."""
    for value in domain:
        if predicate(value):
            return value
    return None


witness = find_witness(range(-20, 21), lambda n: n * n == 49)
print("Witness for 'there exists n such that n² = 49':", witness)

# A witness proves an existential claim only when the relevant domain and
# property are correctly specified.


# =============================================================================
# 10. COUNTEREXAMPLES
# =============================================================================

print("\n" + "=" * 80)
print("10. COUNTEREXAMPLES")
print("=" * 80)

# A counterexample disproves a universal claim.
#
# Suppose someone claims:
#
#     Every prime number is odd.
#
# The number 2 is prime but not odd.
# Therefore 2 is a counterexample.


def is_prime(n: int) -> bool:
    """Returns True when n is a prime integer."""
    if n < 2:
        return False

    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1

    return True


claim_domain = range(-10, 50)
counterexample = find_witness(
    claim_domain,
    lambda n: is_prime(n) and not is_odd(n),
)

print(
    "Counterexample to 'Every prime number is odd':",
    counterexample,
)


# =============================================================================
# 11. HOW TO FIND COUNTEREXAMPLES
# =============================================================================

print("\n" + "=" * 80)
print("11. HOW TO FIND COUNTEREXAMPLES")
print("=" * 80)

# To disprove:
#
#     For every x, P(x)
#
# search for:
#
#     An x for which P(x) is false.
#
# Example false claim:
#
#     For every integer n, n² > n.


def false_claim(n: int) -> bool:
    return n * n > n


counterexample = find_witness(range(-10, 11), lambda n: not false_claim(n))
print("Counterexample to n² > n for every integer n:", counterexample)

if counterexample is not None:
    print(
        f"For n={counterexample}: "
        f"n²={counterexample * counterexample}, "
        f"and {counterexample * counterexample} > {counterexample} is False."
    )

# Note that both 0 and 1 are counterexamples because:
#
#     0² = 0, not greater than 0
#     1² = 1, not greater than 1


# =============================================================================
# 12. ONE EXAMPLE DOES NOT PROVE A UNIVERSAL CLAIM
# =============================================================================

print("\n" + "=" * 80)
print("12. EXAMPLES VERSUS PROOFS")
print("=" * 80)

# Testing several cases may suggest a pattern but cannot establish an infinite
# universal statement.

tested_values = list(range(1, 11))
print("Testing n² >= n for n from 1 through 10:")

for n in tested_values:
    print(f"n={n:2d}: {n*n >= n}")

print(
    "\nAll tested values satisfy the statement, but the mathematical proof "
    "requires reasoning that applies to every positive integer."
)


# =============================================================================
# 13. DIRECT PROOF EXAMPLE: SUM OF TWO EVEN INTEGERS
# =============================================================================

print("\n" + "=" * 80)
print("13. DIRECT PROOF EXAMPLE: EVEN + EVEN = EVEN")
print("=" * 80)

# Theorem:
#
#     The sum of two even integers is even.
#
# Assume:
#
#     a = 2m
#     b = 2n
#
# where m and n are integers.
#
# Then:
#
#     a + b = 2m + 2n
#           = 2(m + n)
#
# Since m + n is an integer, a + b is even.


def even_plus_even(a: int, b: int) -> bool:
    assumptions = is_even(a) and is_even(b)
    conclusion = is_even(a + b)
    return implication(assumptions, conclusion)


for a, b in [(2, 4), (-6, 10), (0, 8), (12, -14)]:
    print(f"{a} + {b} = {a+b}; theorem holds: {even_plus_even(a, b)}")


# =============================================================================
# 14. DIRECT PROOF EXAMPLE: ODD + ODD = EVEN
# =============================================================================

print("\n" + "=" * 80)
print("14. DIRECT PROOF EXAMPLE: ODD + ODD = EVEN")
print("=" * 80)

# Assume:
#
#     a = 2m + 1
#     b = 2n + 1
#
# Then:
#
#     a + b = (2m + 1) + (2n + 1)
#           = 2m + 2n + 2
#           = 2(m + n + 1)
#
# Therefore a + b is even.


def odd_plus_odd(a: int, b: int) -> bool:
    assumptions = is_odd(a) and is_odd(b)
    conclusion = is_even(a + b)
    return implication(assumptions, conclusion)


for a, b in [(1, 3), (-5, 7), (9, 11)]:
    print(f"{a} + {b} = {a+b}; theorem holds: {odd_plus_odd(a, b)}")


# =============================================================================
# 15. DIRECT PROOF EXAMPLE: ODD TIMES ODD = ODD
# =============================================================================

print("\n" + "=" * 80)
print("15. DIRECT PROOF EXAMPLE: ODD × ODD = ODD")
print("=" * 80)

# Assume:
#
#     a = 2m + 1
#     b = 2n + 1
#
# Then:
#
#     ab = (2m + 1)(2n + 1)
#        = 4mn + 2m + 2n + 1
#        = 2(2mn + m + n) + 1
#
# Since 2mn + m + n is an integer, ab is odd.


def odd_times_odd(a: int, b: int) -> bool:
    assumptions = is_odd(a) and is_odd(b)
    conclusion = is_odd(a * b)
    return implication(assumptions, conclusion)


for a, b in [(3, 5), (-3, 7), (-5, -9)]:
    print(f"{a} × {b} = {a*b}; theorem holds: {odd_times_odd(a, b)}")


# =============================================================================
# 16. PROOF STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("16. PROOF STRUCTURE")
print("=" * 80)

# A clear proof generally has this structure:
#
# 1. State the assumptions.
# 2. Expand relevant definitions.
# 3. Apply valid mathematical rules.
# 4. Establish intermediate results.
# 5. Connect the intermediate results to the required conclusion.
#
# A proof should not assume the conclusion as part of its reasoning.


def structured_proof_example(n: int) -> None:
    """
    Illustrates proof organization for:
        If n is divisible by 6, then n is divisible by 3.
    """
    if n % 6 != 0:
        print(f"{n} does not satisfy the assumption 'divisible by 6'.")
        return

    k = n // 6
    quotient = 2 * k

    print(f"Assumption: {n} is divisible by 6.")
    print(f"Therefore {n} = 6 × {k}.")
    print(f"Since 6 = 3 × 2, {n} = 3 × ({quotient}).")
    print(f"{quotient} is an integer.")
    print(f"Conclusion: {n} is divisible by 3.")


structured_proof_example(42)


# =============================================================================
# 17. COMMON MISTAKE: ASSUMING THE CONCLUSION
# =============================================================================

print("\n" + "=" * 80)
print("17. COMMON MISTAKE: CIRCULAR REASONING")
print("=" * 80)

# Circular reasoning occurs when the conclusion is used to justify itself.
#
# Invalid pattern:
#
#     Claim: A implies B.
#     Proof attempt: Assume B. Therefore B.
#
# This does not show that A leads to B.
#
# Correct reasoning must begin with permitted assumptions, known theorems,
# definitions, or previously established facts.


# =============================================================================
# 18. COMMON MISTAKE: REVERSING AN IMPLICATION
# =============================================================================

print("\n" + "=" * 80)
print("18. COMMON MISTAKE: REVERSING AN IMPLICATION")
print("=" * 80)

# If:
#
#     P -> Q
#
# is true, it does not automatically follow that:
#
#     Q -> P
#
# Example:
#
#     If n is divisible by 4, then n is even.
#
# The reverse claim:
#
#     If n is even, then n is divisible by 4.
#
# is false because n = 2 is a counterexample.


def divisible_by_4(n: int) -> bool:
    return n % 4 == 0


reverse_counterexample = find_witness(
    range(-20, 21),
    lambda n: is_even(n) and not divisible_by_4(n),
)

print(
    "Counterexample to 'If n is even, then n is divisible by 4':",
    reverse_counterexample,
)


# =============================================================================
# 19. CONTRAPOSITIVE
# =============================================================================

print("\n" + "=" * 80)
print("19. CONTRAPOSITIVE")
print("=" * 80)

# The contrapositive of:
#
#     If P, then Q
#
# is:
#
#     If not Q, then not P
#
# A statement and its contrapositive are logically equivalent.
#
# Example:
#
#     If n is even, then n² is even.
#
# Contrapositive:
#
#     If n² is odd, then n is odd.


def contrapositive_example(n: int) -> bool:
    original = implication(is_even(n), is_even(n * n))
    contrapositive = implication(
        is_odd(n * n),
        is_odd(n),
    )
    return original == contrapositive


for n in range(-10, 11):
    assert contrapositive_example(n)

print("The original statement and contrapositive agree for tested integers.")


# =============================================================================
# 20. CONVERSE AND INVERSE
# =============================================================================

print("\n" + "=" * 80)
print("20. CONVERSE AND INVERSE")
print("=" * 80)

# Original:
#     P -> Q
#
# Converse:
#     Q -> P
#
# Inverse:
#     not P -> not Q
#
# Contrapositive:
#     not Q -> not P
#
# The original statement is equivalent to its contrapositive.
# The converse is equivalent to the inverse.
# Original and converse are not generally equivalent.


def show_logical_forms(p: bool, q: bool) -> None:
    original = implication(p, q)
    converse = implication(q, p)
    inverse = implication(not p, not q)
    contrapositive = implication(not q, not p)

    print(f"P={p}, Q={q}")
    print(f"Original:       {original}")
    print(f"Converse:       {converse}")
    print(f"Inverse:        {inverse}")
    print(f"Contrapositive: {contrapositive}")


show_logical_forms(True, False)


# =============================================================================
# 21. PROOF BY CONTRADICTION
# =============================================================================

print("\n" + "=" * 80)
print("21. PROOF BY CONTRADICTION")
print("=" * 80)

# Proof by contradiction works by:
#
# 1. Assuming the desired statement is false.
# 2. Following the consequences of that assumption.
# 3. Deriving a contradiction.
# 4. Concluding that the original assumption was impossible.
#
# Classical example:
#
#     sqrt(2) is irrational.
#
# The full mathematical proof assumes:
#
#     sqrt(2) = a / b
#
# where a and b are integers with no common factor.
#
# Squaring:
#
#     2 = a² / b²
#     a² = 2b²
#
# Therefore a² is even, so a is even.
# Write a = 2k.
#
# Substitution eventually shows b is also even.
# This contradicts the assumption that a and b have no common factor.
#
# Therefore sqrt(2) is irrational.
#
# The code below does not prove irrationality by floating-point approximation.
# It demonstrates why finite decimal output is not sufficient proof.


import math

sqrt_two = math.sqrt(2)
print("Approximation of sqrt(2):", sqrt_two)
print(
    "A decimal approximation cannot establish whether sqrt(2) is rational or irrational."
)


# =============================================================================
# 22. COUNTEREXAMPLES AND QUANTIFIERS
# =============================================================================

print("\n" + "=" * 80)
print("22. COUNTEREXAMPLES AND QUANTIFIERS")
print("=" * 80)

# Universal statement:
#
#     For every x, P(x)
#
# To disprove it, find one x such that P(x) is false.
#
# Existential statement:
#
#     There exists x such that P(x)
#
# To prove it, find one x such that P(x) is true.
#
# To disprove an existential statement, every possible element of the domain
# must fail the property. For infinite domains, this usually requires proof.


def classify_quantified_claim(
    domain: Iterable[int],
    predicate: Callable[[int], bool],
) -> tuple[bool, Optional[int]]:
    """
    Returns:
        (all_elements_satisfy_predicate, first_counterexample_or_none)

    This applies only to the supplied finite domain.
    """
    for value in domain:
        if not predicate(value):
            return False, value
    return True, None


finite_result, finite_counterexample = classify_quantified_claim(
    range(1, 11),
    lambda n: n >= 1,
)

print(
    "All values in range(1, 11) satisfy n >= 1:",
    finite_result,
)
print("Counterexample:", finite_counterexample)


# =============================================================================
# 23. EDGE CASES
# =============================================================================

print("\n" + "=" * 80)
print("23. EDGE CASES")
print("=" * 80)

# Mathematical statements can fail at boundary values.
#
# Example:
#
#     n / n = 1
#
# This is true for nonzero n but undefined for n = 0.


def divide_number_by_itself(n: float) -> float:
    if n == 0:
        raise ZeroDivisionError("n / n is undefined when n = 0.")
    return n / n


for value in (5, -2, 0):
    try:
        print(f"{value} / {value} = {divide_number_by_itself(value)}")
    except ZeroDivisionError as error:
        print(f"For n={value}: {error}")

# A proof must respect domain restrictions. A transformation that involves
# division is invalid when the divisor might be zero.


# =============================================================================
# 24. VACUOUS TRUTH
# =============================================================================

print("\n" + "=" * 80)
print("24. VACUOUS TRUTH")
print("=" * 80)

# An implication P -> Q is logically true whenever P is false.
#
# For example:
#
#     If n is both even and odd, then n is divisible by 100.
#
# Under ordinary integer parity definitions, the hypothesis cannot occur.
# Therefore the conditional is true for every integer in the logical sense.


def impossible_hypothesis_statement(n: int) -> bool:
    hypothesis = is_even(n) and is_odd(n)
    conclusion = n % 100 == 0
    return implication(hypothesis, conclusion)


for n in range(-3, 4):
    print(
        f"n={n}, "
        f"hypothesis={is_even(n) and is_odd(n)}, "
        f"statement={impossible_hypothesis_statement(n)}"
    )


# =============================================================================
# 25. TESTING A THEOREM VERSUS PROVING A THEOREM
# =============================================================================

print("\n" + "=" * 80)
print("25. TESTING VERSUS PROVING")
print("=" * 80)

# Testing is useful for:
#
# - finding patterns
# - discovering possible counterexamples
# - checking implementations
# - detecting arithmetic mistakes
#
# Testing alone cannot prove an infinite statement.


def test_even_square_many_values(lower: int, upper: int) -> bool:
    for n in range(lower, upper + 1):
        if is_even(n) and not is_even(n * n):
            return False
    return True


print(
    "Computational test over [-1000, 1000]:",
    test_even_square_many_values(-1000, 1000),
)

print(
    "The general proof still requires the representation n = 2k for an "
    "arbitrary even integer n."
)


# =============================================================================
# 26. PROOF BY CASES
# =============================================================================

print("\n" + "=" * 80)
print("26. PROOF BY CASES")
print("=" * 80)

# Some statements naturally divide the domain into exhaustive cases.
#
# Example:
#
#     For every integer n, n² is either even or odd.
#
# Every integer is either even or odd. In each case, the square retains the
# corresponding parity.


def parity_case_result(n: int) -> str:
    if is_even(n):
        assert is_even(n * n)
        return f"{n} is even, so {n*n} is even."
    assert is_odd(n)
    assert is_odd(n * n)
    return f"{n} is odd, so {n*n} is odd."


for n in range(-3, 4):
    print(parity_case_result(n))


# =============================================================================
# 27. PROOF BY EXHAUSTION FOR FINITE DOMAINS
# =============================================================================

print("\n" + "=" * 80)
print("27. PROOF BY EXHAUSTION FOR FINITE DOMAINS")
print("=" * 80)

# For a genuinely finite domain, checking every possible case can be a valid
# proof technique.
#
# Example:
#
# Every integer from 0 through 9 has a square ending in one of:
#
#     0, 1, 4, 5, 6, 9


allowed_last_digits = {0, 1, 4, 5, 6, 9}

for digit in range(10):
    square_last_digit = (digit * digit) % 10
    assert square_last_digit in allowed_last_digits
    print(f"{digit}² ends in {square_last_digit}")

print("All ten possible final digits have been checked.")


# =============================================================================
# 28. A COMPLETE DIRECT PROOF IMPLEMENTATION MODEL
# =============================================================================

print("\n" + "=" * 80)
print("28. COMPLETE DIRECT PROOF MODEL")
print("=" * 80)

# Theorem:
#
#     If a divides b and a divides c, then a divides b + c.
#
# Direct proof:
#
# Assume:
#
#     a divides b
#     a divides c
#
# Then there exist integers m and n such that:
#
#     b = am
#     c = an
#
# Therefore:
#
#     b + c = am + an
#           = a(m + n)
#
# Since m + n is an integer:
#
#     a divides b + c.


def divisibility_sum_theorem(a: int, b: int, c: int) -> bool:
    if a == 0:
        # The standard relation "a divides b" is normally defined for nonzero a.
        # We avoid treating the zero divisor as a normal divisor here.
        raise ValueError("This theorem demonstration requires a nonzero divisor.")

    assumptions = divides(a, b) and divides(a, c)
    conclusion = divides(a, b + c)

    return implication(assumptions, conclusion)


for values in [(3, 12, 21), (5, 10, 35), (-2, 8, 14)]:
    a, b, c = values
    print(
        f"a={a}, b={b}, c={c}, theorem holds: "
        f"{divisibility_sum_theorem(a, b, c)}"
    )


# =============================================================================
# 29. ASSUMPTION VALIDATION IN COMPUTATIONAL MODELS
# =============================================================================

print("\n" + "=" * 80)
print("29. ASSUMPTION VALIDATION")
print("=" * 80)

# Mathematical proofs depend on assumptions.
# Software implementations should explicitly validate assumptions when invalid
# inputs would otherwise produce misleading results.


def positive_square_root_property(x: float) -> float:
    """
    Demonstrates a domain-restricted mathematical operation.

    Assumption:
        x >= 0

    Result:
        sqrt(x)

    For real numbers, sqrt(x) is not defined when x < 0.
    """
    if x < 0:
        raise ValueError("Real square root requires x >= 0.")
    return math.sqrt(x)


for value in (0, 4, 25, -1):
    try:
        print(f"sqrt({value}) = {positive_square_root_property(value)}")
    except ValueError as error:
        print(f"Input {value}: {error}")


# =============================================================================
# 30. COMMON PROOF MISTAKES
# =============================================================================

print("\n" + "=" * 80)
print("30. COMMON PROOF MISTAKES")
print("=" * 80)

common_mistakes = [
    "Checking examples and claiming that infinitely many cases are proved.",
    "Using the conclusion as an assumption.",
    "Reversing an implication without justification.",
    "Ignoring the domain of variables.",
    "Dividing by an expression that might equal zero.",
    "Using an example that does not satisfy the original assumptions.",
    "Confusing an existential statement with a universal statement.",
    "Presenting a counterexample that is outside the stated domain.",
    "Skipping the reason why an introduced quantity is an integer.",
    "Treating numerical approximation as exact mathematical proof.",
]

for index, mistake in enumerate(common_mistakes, start=1):
    print(f"{index}. {mistake}")


# =============================================================================
# 31. A COUNTEREXAMPLE SEARCH ENGINE
# =============================================================================

print("\n" + "=" * 80)
print("31. COUNTEREXAMPLE SEARCH ENGINE")
print("=" * 80)

# This generic function searches a finite domain for an element satisfying the
# assumptions while violating the conclusion.


def find_conditional_counterexample(
    domain: Iterable[T],
    assumption: Callable[[T], bool],
    conclusion: Callable[[T], bool],
) -> Optional[T]:
    """
    Searches for x such that:

        assumption(x) is True
        conclusion(x) is False

    Such an x disproves the conditional:

        If assumption(x), then conclusion(x)

    for a universal statement over the searched domain.
    """
    for value in domain:
        if assumption(value) and not conclusion(value):
            return value
    return None


# False claim:
#
#     If an integer n is positive, then n is even.

counterexample = find_conditional_counterexample(
    range(-10, 11),
    assumption=lambda n: n > 0,
    conclusion=is_even,
)

print(
    "Counterexample to 'If n > 0, then n is even':",
    counterexample,
)


# =============================================================================
# 32. COMPARING PROOF METHODS
# =============================================================================

print("\n" + "=" * 80)
print("32. COMPARING PROOF METHODS")
print("=" * 80)

proof_methods = {
    "Direct proof": (
        "Start from assumptions and derive the conclusion."
    ),
    "Contrapositive": (
        "Prove not-Q implies not-P instead of directly proving P implies Q."
    ),
    "Contradiction": (
        "Assume the claim is false and derive an impossibility."
    ),
    "Proof by cases": (
        "Divide the domain into exhaustive cases and prove the result in each."
    ),
    "Counterexample": (
        "Disprove a universal statement using one valid failing instance."
    ),
    "Exhaustion": (
        "Check every case when the domain is genuinely finite."
    ),
}

for method, description in proof_methods.items():
    print(f"{method}: {description}")


# =============================================================================
# 33. DEBUGGING MATHEMATICAL REASONING WITH SMALL CASES
# =============================================================================

print("\n" + "=" * 80)
print("33. DEBUGGING MATHEMATICAL REASONING")
print("=" * 80)

# Small examples are valuable for detecting mistakes before writing a formal
# proof. They can reveal:
#
# - false statements
# - missing assumptions
# - incorrect algebra
# - overlooked boundary cases


def inspect_candidate_claim(
    values: Iterable[int],
    claim: Callable[[int], bool],
) -> None:
    for value in values:
        result = claim(value)
        print(f"x={value:3d}: {result}")


print("Candidate claim: n² >= n for every integer n")
inspect_candidate_claim(range(-3, 4), lambda n: n * n >= n)

print(
    "The negative values and zero satisfy this claim, while the exact proof "
    "requires an argument covering all integers."
)


# =============================================================================
# 34. PRODUCTION-LIKE IMPLEMENTATION: FORMAL CLAIM REPRESENTATION
# =============================================================================

print("\n" + "=" * 80)
print("34. CLAIM REPRESENTATION")
print("=" * 80)

# In software, it can be useful to represent a conditional mathematical claim
# explicitly.


@dataclass
class ConditionalClaim:
    """
    Represents a statement of the form:

        If assumption(x), then conclusion(x)
    """

    name: str
    assumption: Callable[[int], bool]
    conclusion: Callable[[int], bool]

    def holds_for(self, value: int) -> bool:
        return implication(
            self.assumption(value),
            self.conclusion(value),
        )

    def counterexample_in(self, domain: Iterable[int]) -> Optional[int]:
        return find_conditional_counterexample(
            domain,
            self.assumption,
            self.conclusion,
        )


even_square_claim = ConditionalClaim(
    name="If n is even, then n² is even",
    assumption=is_even,
    conclusion=lambda n: is_even(n * n),
)

false_positive_even_claim = ConditionalClaim(
    name="If n is positive, then n is even",
    assumption=lambda n: n > 0,
    conclusion=is_even,
)

claims = [even_square_claim, false_positive_even_claim]

for claim in claims:
    counterexample = claim.counterexample_in(range(-100, 101))
    print(f"\nClaim: {claim.name}")
    print(f"Counterexample in tested domain: {counterexample}")


# =============================================================================
# 35. SIMPLE ASSERTION-BASED TESTS
# =============================================================================

print("\n" + "=" * 80)
print("35. ASSERTION-BASED TESTS")
print("=" * 80)

# Assertions are useful for checking expected mathematical properties over
# selected finite domains.

for n in range(-100, 101):
    if is_even(n):
        assert is_even(n * n)

for n in range(-100, 101):
    if is_odd(n):
        assert is_odd(n * n)

for a in range(-20, 21):
    for b in range(-20, 21):
        if is_even(a) and is_even(b):
            assert is_even(a + b)

print("Selected finite-domain property tests passed.")

# These assertions test the implementation and support confidence in examples.
# They are not replacements for the corresponding general mathematical proofs.


# =============================================================================
# 36. FINAL INTEGRATED EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("36. FINAL INTEGRATED EXAMPLE")
print("=" * 80)

# Theorem:
#
#     If n is divisible by 12, then n is divisible by 3.
#
# Direct reasoning:
#
# Assume n is divisible by 12.
#
# Then:
#
#     n = 12k
#
# for some integer k.
#
# Since:
#
#     12 = 3 × 4
#
# we have:
#
#     n = 3(4k)
#
# Because 4k is an integer, n is divisible by 3.


def divisible_by_12_implies_divisible_by_3(n: int) -> bool:
    assumption = n % 12 == 0
    conclusion = n % 3 == 0
    return implication(assumption, conclusion)


for n in range(-36, 37):
    assert divisible_by_12_implies_divisible_by_3(n)

print(
    "The conditional 'If n is divisible by 12, then n is divisible by 3' "
    "passes the selected computational tests."
)


# =============================================================================
# END OF STUDY SCRIPT
# =============================================================================

print("\n" + "=" * 80)
print("END OF MATHEMATICAL PROOF FUNDAMENTALS")
print("=" * 80)
