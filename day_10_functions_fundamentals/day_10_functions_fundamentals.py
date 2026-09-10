"""
Functions Fundamentals
=======================

Topic:
    Domain, codomain, range, mappings, function notation,
    injective, surjective, and bijective functions.

This standalone study script progresses from the basic idea of a function
through formal definitions, representations, classification, proofs,
finite-set enumeration, inverse functions, composition, cardinality,
piecewise functions, restrictions, and practical computational checks.

The examples use only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import factorial, gcd, isqrt
from typing import Any, Callable, Dict, Generic, Hashable, Iterable, List, Optional, Sequence, Set, Tuple, TypeVar


# =============================================================================
# 1. FOUNDATIONS: RELATIONS, INPUTS, OUTPUTS, AND FUNCTIONS
# =============================================================================

print("=" * 80)
print("FUNCTIONS FUNDAMENTALS")
print("=" * 80)


def print_section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


print_section("1. What is a function?")

print(
    """
A function is a rule that assigns exactly one output to every allowed input.

For a function f from a set A to a set B:

    f : A -> B

A is the domain.
B is the codomain.
The range is the set of outputs actually produced by elements of A.

The defining condition is:

    every element of the domain has exactly one image.

Different domain elements may have the same output. That is allowed.
An output in the codomain may receive no input. That is also allowed.

For example:

    f(x) = x^2

If the domain is {-2, -1, 0, 1, 2}, then:

    -2 -> 4
    -1 -> 1
     0 -> 0
     1 -> 1
     2 -> 4

The range is {0, 1, 4}.

Notice that the codomain could be larger than the range. For example,
the same function can be declared as:

    f : {-2,-1,0,1,2} -> {0,1,2,3,4,5}

The range is still {0,1,4}.
"""
)


# =============================================================================
# 2. FORMAL SET-THEORETIC DEFINITION
# =============================================================================

print_section("2. Formal definition of a function")

print(
    """
A relation from A to B is a subset of the Cartesian product A x B.

A function f : A -> B is a relation satisfying:

    for every x in A, there exists exactly one y in B
    such that (x, y) belongs to f.

The phrase "exactly one" contains two requirements:

1. Existence:
   Every domain element must be paired with an output.

2. Uniqueness:
   A domain element cannot be paired with two different outputs.

Thus:

    {(1, "a"), (2, "b"), (3, "b")}

is a function from {1,2,3} to {"a","b"}.

But:

    {(1, "a"), (1, "b"), (2, "c")}

is not a function because input 1 has two different outputs.

And:

    {(1, "a"), (2, "b")}

is not a function from {1,2,3} because input 3 has no output.
"""
)


Pair = Tuple[Hashable, Hashable]


def is_function_relation(
    relation: Iterable[Pair],
    domain: Set[Hashable],
) -> Tuple[bool, str]:
    """
    Check whether a finite relation defines a function on the given domain.

    A relation is represented as pairs (input, output).

    The function must:
    - assign at least one output to every domain element;
    - assign no more than one distinct output to any domain element.
    """
    relation_list = list(relation)
    outputs_by_input: Dict[Hashable, Set[Hashable]] = {}

    for x, y in relation_list:
        outputs_by_input.setdefault(x, set()).add(y)

    for x in domain:
        if x not in outputs_by_input:
            return False, f"Input {x!r} has no assigned output."

        if len(outputs_by_input[x]) != 1:
            return False, (
                f"Input {x!r} has multiple distinct outputs: "
                f"{outputs_by_input[x]!r}."
            )

    outside_inputs = set(outputs_by_input) - domain
    if outside_inputs:
        return False, (
            f"The relation contains inputs outside the declared domain: "
            f"{outside_inputs!r}."
        )

    return True, "The relation defines a function on the declared domain."


valid_relation = {(1, "a"), (2, "b"), (3, "b")}
invalid_relation_multiple_outputs = {(1, "a"), (1, "b"), (2, "c")}
invalid_relation_missing_input = {(1, "a"), (2, "b")}

print(is_function_relation(valid_relation, {1, 2, 3}))
print(is_function_relation(invalid_relation_multiple_outputs, {1, 2}))
print(is_function_relation(invalid_relation_missing_input, {1, 2, 3}))


# =============================================================================
# 3. DOMAIN, CODOMAIN, AND RANGE
# =============================================================================

print_section("3. Domain, codomain, and range")

print(
    """
Domain
------
The domain is the set of permitted inputs.

Codomain
--------
The codomain is the target set specified when the function is defined.

Range
-----
The range, also called the image of the function, is the subset of the
codomain consisting of values actually produced.

For f : A -> B:

    range(f) = {f(x) : x in A}

Therefore:

    range(f) is always a subset of codomain(f).

The codomain is part of the function's declared structure. It is not
automatically the same thing as the range.

Example:

    f : {1,2,3} -> {a,b,c,d}

    f(1) = a
    f(2) = b
    f(3) = b

Then:

    domain  = {1,2,3}
    codomain = {a,b,c,d}
    range   = {a,b}

The elements c and d belong to the codomain but not to the range.
"""
)


T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)


@dataclass(frozen=True)
class FiniteFunction(Generic[T, U]):
    """
    A mathematical function between finite sets.

    mapping:
        Dictionary representing x -> f(x).

    domain:
        Explicit domain.

    codomain:
        Explicit codomain.

    The constructor validates the defining condition of a finite function.
    """

    mapping: Dict[T, U]
    domain: Set[T]
    codomain: Set[U]

    def __post_init__(self) -> None:
        mapping_domain = set(self.mapping)

        if mapping_domain != self.domain:
            missing = self.domain - mapping_domain
            extra = mapping_domain - self.domain

            problems = []
            if missing:
                problems.append(f"missing inputs={missing!r}")
            if extra:
                problems.append(f"extra inputs={extra!r}")

            raise ValueError(
                "The mapping keys must equal the declared domain: "
                + ", ".join(problems)
            )

        outside_codomain = set(self.mapping.values()) - self.codomain
        if outside_codomain:
            raise ValueError(
                f"Some outputs are outside the codomain: {outside_codomain!r}"
            )

    def __call__(self, x: T) -> U:
        """Evaluate the function at x."""
        if x not in self.domain:
            raise ValueError(f"{x!r} is outside the domain.")
        return self.mapping[x]

    @property
    def range(self) -> Set[U]:
        """Return the set of actual outputs."""
        return set(self.mapping.values())

    def graph(self) -> Set[Tuple[T, U]]:
        """Return the graph as a set of ordered pairs."""
        return set(self.mapping.items())

    def is_injective(self) -> bool:
        """A function is injective when distinct inputs have distinct outputs."""
        return len(self.mapping.values()) == len(set(self.mapping.values()))

    def is_surjective(self) -> bool:
        """A function is surjective when its range equals its codomain."""
        return self.range == self.codomain

    def is_bijective(self) -> bool:
        """A function is bijective when it is both injective and surjective."""
        return self.is_injective() and self.is_surjective()

    def preimage(self, y: U) -> Set[T]:
        """Return all x such that f(x) = y."""
        return {x for x in self.domain if self.mapping[x] == y}

    def inverse(self) -> "FiniteFunction[U, T]":
        """
        Construct the inverse function.

        An inverse exists as a function exactly when the original finite
        function is bijective.
        """
        if not self.is_bijective():
            raise ValueError(
                "A function has an inverse function only when it is bijective."
            )

        inverse_mapping = {
            output: input_value for input_value, output in self.mapping.items()
        }

        return FiniteFunction(
            mapping=inverse_mapping,
            domain=set(self.codomain),
            codomain=set(self.domain),
        )


f_example = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "b"},
    domain={1, 2, 3},
    codomain={"a", "b", "c", "d"},
)

print("Domain :", f_example.domain)
print("Codomain:", f_example.codomain)
print("Range  :", f_example.range)
print("f(2)   :", f_example(2))


# =============================================================================
# 4. FUNCTION NOTATION
# =============================================================================

print_section("4. Function notation")

print(
    """
Common notation:

    f : A -> B

means that f maps elements of A into elements of B.

The notation:

    f(x) = 2x + 3

means that the output associated with input x is 2x + 3.

For example:

    f(0) = 3
    f(2) = 7
    f(-1) = 1

Important distinction:

    f

names the function.

    x

is an input variable.

    f(x)

is the output associated with x.

If:

    f(x) = x^2

then f is not the same thing as f(x). The former is the function itself;
the latter denotes its value at x.
"""
)


def linear_function(x: float) -> float:
    """f(x) = 2x + 3."""
    return 2 * x + 3


for input_value in [-2, 0, 2, 5]:
    print(f"f({input_value}) = {linear_function(input_value)}")


# =============================================================================
# 5. MAPPINGS AND DIAGRAMS IN TEXT FORM
# =============================================================================

print_section("5. Mapping representation")

print(
    """
A finite function can be represented as:

    domain             codomain

      1  ------------>  a
      2  ------------>  b
      3  ------------>  b

Several domain elements may point to the same codomain element.
That does not violate the definition of a function.

But one domain element cannot point to two different outputs.

For finite sets, a mapping can be stored naturally in Python using a
dictionary because a dictionary associates each key with one value.
"""
)


def print_mapping(function: FiniteFunction[Any, Any]) -> None:
    """Print a finite function as an arrow-style mapping."""
    print("Domain -> Codomain")
    for x in sorted(function.domain, key=repr):
        print(f"  {x!r} -> {function(x)!r}")


print_mapping(f_example)


# =============================================================================
# 6. IMAGE AND PREIMAGE
# =============================================================================

print_section("6. Image and preimage")

print(
    """
For a function f : A -> B and a subset S of A:

    f(S) = {f(x) : x in S}

This is the image of S.

For a subset T of B:

    f^(-1)(T) = {x in A : f(x) belongs to T}

This is the preimage of T.

The notation f^(-1)(T) here describes a preimage of a set. It does not
automatically mean that an inverse function exists.

For an individual value y:

    f^(-1)({y})

is the set of all inputs mapping to y.

If f is not injective, this preimage can contain multiple inputs.
If y is outside the range, the preimage is empty.
"""
)


def image_of_subset(
    function: FiniteFunction[T, U],
    subset: Set[T],
) -> Set[U]:
    """Compute f(S) for a subset S of the domain."""
    if not subset <= function.domain:
        raise ValueError("The subset must be contained in the domain.")
    return {function(x) for x in subset}


subset = {1, 3}
print("Image of {1, 3}:", image_of_subset(f_example, subset))
print("Preimage of 'b':", f_example.preimage("b"))
print("Preimage of 'd':", f_example.preimage("d"))


# =============================================================================
# 7. INJECTIVE FUNCTIONS
# =============================================================================

print_section("7. Injective functions")

print(
    """
Definition
----------
A function f : A -> B is injective, or one-to-one, if:

    f(x1) = f(x2)  =>  x1 = x2

Equivalently:

    x1 != x2  =>  f(x1) != f(x2)

Interpretation:
No two distinct domain elements share the same output.

For a finite function, injectivity means:

    number of distinct outputs = number of domain elements.

Example:

    f(x) = 2x + 1

on the real numbers is injective because:

    2x1 + 1 = 2x2 + 1
    2x1 = 2x2
    x1 = x2

Counterexample:

    f(x) = x^2

on the real numbers is not injective because:

    f(2) = 4
    f(-2) = 4

yet:

    2 != -2.

A function can be injective without being surjective.
"""
)


injective_example = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "c"},
    domain={1, 2, 3},
    codomain={"a", "b", "c", "d"},
)

non_injective_example = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "b"},
    domain={1, 2, 3},
    codomain={"a", "b", "c"},
)

print("Injective example:", injective_example.is_injective())
print("Non-injective example:", non_injective_example.is_injective())


def is_injective_by_definition(
    function: Callable[[Any], Any],
    domain: Iterable[Any],
) -> bool:
    """
    Check injectivity by directly comparing every pair of inputs.

    This implementation mirrors the mathematical definition and has
    O(n^2) time complexity for n finite inputs.
    """
    domain_list = list(domain)

    for index, x1 in enumerate(domain_list):
        for x2 in domain_list[index + 1:]:
            if function(x1) == function(x2):
                return False

    return True


print(
    "x^2 on {-2,-1,0,1,2}:",
    is_injective_by_definition(lambda x: x * x, range(-2, 3)),
)

print(
    "2x+1 on {-2,-1,0,1,2}:",
    is_injective_by_definition(lambda x: 2 * x + 1, range(-2, 3)),
)


# =============================================================================
# 8. SURJECTIVE FUNCTIONS
# =============================================================================

print_section("8. Surjective functions")

print(
    """
Definition
----------
A function f : A -> B is surjective, or onto, if every element of B is
the image of at least one element of A.

Formally:

    for every y in B, there exists x in A such that f(x) = y.

Equivalently:

    range(f) = codomain(f)

A function can be surjective without being injective.

Example:

    f : {1,2,3} -> {a,b}

    1 -> a
    2 -> b
    3 -> a

Every codomain element is reached, so f is surjective.

But it is not injective because 1 and 3 both map to a.

Surjectivity depends on the codomain.

For example:

    f(x) = x^2

is not surjective from R to R because negative real numbers are not
outputs.

But:

    f : R -> [0,infinity)

    f(x) = x^2

is surjective because every nonnegative real number y has an input
x = sqrt(y).
"""
)


surjective_example = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "a"},
    domain={1, 2, 3},
    codomain={"a", "b"},
)

print("Surjective example:", surjective_example.is_surjective())
print("Injective too?     :", surjective_example.is_injective())


# =============================================================================
# 9. BIJECTIVE FUNCTIONS
# =============================================================================

print_section("9. Bijective functions")

print(
    """
Definition
----------
A function is bijective if it is both:

    injective
    and
    surjective.

Thus:

    every codomain element has exactly one preimage.

A bijection establishes a one-to-one correspondence between the domain
and codomain.

For finite sets:

    f : A -> B is bijective
    exactly when |A| = |B| and f is injective.

Equivalently:

    f is bijective
    exactly when |A| = |B| and f is surjective.

A bijective function has an inverse function.

If:

    f(a) = b

then:

    f^(-1)(b) = a
"""
)


bijective_example = FiniteFunction(
    mapping={"A": 1, "B": 2, "C": 3},
    domain={"A", "B", "C"},
    codomain={1, 2, 3},
)

print("Injective:", bijective_example.is_injective())
print("Surjective:", bijective_example.is_surjective())
print("Bijective:", bijective_example.is_bijective())

inverse_example = bijective_example.inverse()
print("Inverse mapping:", inverse_example.mapping)


# =============================================================================
# 10. INVERSE FUNCTIONS
# =============================================================================

print_section("10. Inverse functions")

print(
    """
For a function f : A -> B, an inverse function exists when f is bijective.

The inverse is:

    f^(-1) : B -> A

and satisfies:

    f^(-1)(f(x)) = x       for every x in A

and:

    f(f^(-1)(y)) = y       for every y in B.

Do not confuse an inverse function with a reciprocal.

If:

    f(x) = 2x + 3

then:

    f^(-1)(x) = (x - 3) / 2

The reciprocal is:

    1 / f(x)

These are different concepts.

For non-bijective functions, an inverse relation may exist, but it may
not be a function.

For example:

    f(x) = x^2

has:

    f(2) = 4
    f(-2) = 4

Trying to reverse this gives:

    4 -> 2
    4 -> -2

which assigns two outputs to the input 4. Therefore the inverse relation
is not an inverse function on the full real domain.
"""
)


print("f mapping :", bijective_example.mapping)
print("f inverse :", inverse_example.mapping)

for x in bijective_example.domain:
    y = bijective_example(x)
    recovered_x = inverse_example(y)
    print(f"x={x!r}, f(x)={y!r}, inverse(f(x))={recovered_x!r}")


# =============================================================================
# 11. CARDINALITY AND FINITE SETS
# =============================================================================

print_section("11. Cardinality and finite-set rules")

print(
    """
The cardinality |A| of a finite set is the number of elements in A.

For a function f : A -> B where A and B are finite:

If |A| > |B|:
    f cannot be injective.
    This is the pigeonhole principle.

If |A| < |B|:
    f cannot be surjective.

If |A| = |B|:
    injective implies surjective.
    surjective implies injective.

Therefore, for finite sets of equal size:

    injective <=> surjective <=> bijective.

This equivalence does not apply blindly to infinite sets.

For example, the natural-number function:

    f(n) = n + 1

from N = {0,1,2,...} to N is injective but not surjective because 0
has no preimage.

Thus infinite sets can have the same cardinality while a function between
them is injective without being surjective.
"""
)


def finite_function_cardinality_test(
    function: FiniteFunction[Any, Any],
) -> Dict[str, Any]:
    """Return useful cardinality facts for a finite function."""
    domain_size = len(function.domain)
    codomain_size = len(function.codomain)
    range_size = len(function.range)

    return {
        "domain_size": domain_size,
        "codomain_size": codomain_size,
        "range_size": range_size,
        "injective": function.is_injective(),
        "surjective": function.is_surjective(),
        "bijective": function.is_bijective(),
    }


print(finite_function_cardinality_test(bijective_example))


# =============================================================================
# 12. PIGEONHOLE PRINCIPLE IN CODE
# =============================================================================

print_section("12. Pigeonhole principle")

print(
    """
If more than n objects are placed into n boxes, at least one box contains
two or more objects.

For functions:

    |A| > |B|

means more inputs than available outputs. Therefore two distinct inputs
must share an output.

This makes injectivity impossible.
"""
)


def must_have_collision(
    domain_size: int,
    codomain_size: int,
) -> bool:
    """Return whether every function A -> B must have a collision."""
    return domain_size > codomain_size


for domain_size, codomain_size in [(3, 2), (3, 3), (2, 3), (10, 5)]:
    print(
        f"|A|={domain_size}, |B|={codomain_size}: "
        f"every function must collide? "
        f"{must_have_collision(domain_size, codomain_size)}"
    )


# =============================================================================
# 13. ENUMERATING ALL FINITE FUNCTIONS
# =============================================================================

print_section("13. Enumerating finite functions")

print(
    """
If:

    |A| = m
    |B| = n

then the total number of functions from A to B is:

    n^m

because each of the m inputs independently chooses one of n outputs.

The number of injective functions from an m-element domain to an n-element
codomain, when m <= n, is:

    n * (n-1) * ... * (n-m+1)
    = n! / (n-m)!

The number of bijections from an n-element set to another n-element set is:

    n!

The number of surjective functions from an m-element set onto an
n-element set can be calculated using inclusion-exclusion:

    sum(k=0..n) (-1)^k C(n,k) (n-k)^m

for m >= n.

The code below verifies these counts for small sets.
"""
)


def count_all_functions(domain_size: int, codomain_size: int) -> int:
    """Count functions A -> B for finite sets of the specified sizes."""
    return codomain_size ** domain_size


def count_injective_functions(domain_size: int, codomain_size: int) -> int:
    """Count injective functions A -> B."""
    if domain_size > codomain_size:
        return 0

    result = 1
    for offset in range(domain_size):
        result *= codomain_size - offset
    return result


def count_bijective_functions(set_size: int) -> int:
    """Count bijections between two sets of equal finite cardinality."""
    return factorial(set_size)


def binomial_coefficient(n: int, r: int) -> int:
    """Compute C(n,r) without requiring external packages."""
    if r < 0 or r > n:
        return 0
    r = min(r, n - r)
    result = 1
    for i in range(1, r + 1):
        result = result * (n - r + i) // i
    return result


def count_surjective_functions(domain_size: int, codomain_size: int) -> int:
    """Count surjections using inclusion-exclusion."""
    if domain_size < codomain_size:
        return 0

    total = 0
    for k in range(codomain_size + 1):
        total += (
            (-1) ** k
            * binomial_coefficient(codomain_size, k)
            * (codomain_size - k) ** domain_size
        )
    return total


for m, n in [(2, 2), (3, 2), (3, 3), (4, 2), (2, 3)]:
    print(
        f"m={m}, n={n}: "
        f"all={count_all_functions(m, n)}, "
        f"injective={count_injective_functions(m, n)}, "
        f"surjective={count_surjective_functions(m, n)}"
    )


# =============================================================================
# 14. EXHAUSTIVE CLASSIFICATION OF SMALL FUNCTIONS
# =============================================================================

print_section("14. Exhaustively classify every function between small sets")

print(
    """
For finite sets, a function can be generated by choosing one codomain
element for each domain element.

For:

    A = {1,2}
    B = {"a","b"}

there are:

    2^2 = 4

functions.

Exactly two are bijections.
"""
)


def generate_all_finite_functions(
    domain: Sequence[T],
    codomain: Sequence[U],
) -> List[FiniteFunction[T, U]]:
    """Generate every function from a finite domain to a finite codomain."""
    if not codomain:
        if domain:
            return []
        return [
            FiniteFunction(
                mapping={},
                domain=set(),
                codomain=set(),
            )
        ]

    functions: List[FiniteFunction[T, U]] = []

    for chosen_outputs in product(codomain, repeat=len(domain)):
        mapping = dict(zip(domain, chosen_outputs))
        functions.append(
            FiniteFunction(
                mapping=mapping,
                domain=set(domain),
                codomain=set(codomain),
            )
        )

    return functions


small_functions = generate_all_finite_functions(
    [1, 2],
    ["a", "b"],
)

for function in small_functions:
    print(
        function.mapping,
        "injective=", function.is_injective(),
        "surjective=", function.is_surjective(),
        "bijective=", function.is_bijective(),
    )


# =============================================================================
# 15. SURJECTION, INJECTION, AND BIJECTION COUNTS
# =============================================================================

print_section("15. Counting classification types")

print(
    """
For a finite function A -> B:

- There can be no injection if |A| > |B|.
- There can be no surjection if |A| < |B|.
- There can be bijections only when |A| = |B|.

When both sets have two elements:

    total functions = 2^2 = 4
    injective       = 2
    surjective      = 2
    bijective       = 2

For equal finite cardinalities, the injective and surjective functions
are exactly the same set of functions.
"""
)


def classify_functions(
    domain: Sequence[T],
    codomain: Sequence[U],
) -> Dict[str, int]:
    """Count functions by classification."""
    functions = generate_all_finite_functions(domain, codomain)

    return {
        "total": len(functions),
        "injective": sum(f.is_injective() for f in functions),
        "surjective": sum(f.is_surjective() for f in functions),
        "bijective": sum(f.is_bijective() for f in functions),
    }


for sizes in [(1, 1), (2, 2), (3, 2), (2, 3), (3, 3)]:
    m, n = sizes
    print(f"{m} -> {n}: {classify_functions(list(range(m)), list(range(n)))}")


# =============================================================================
# 16. COMMON FUNCTION EXAMPLES
# =============================================================================

print_section("16. Standard mathematical examples")

print(
    """
Identity function
-----------------
    id_A(x) = x

It is always bijective from a set A to itself.

Constant function
-----------------
    f(x) = c

For a nonempty domain and codomain containing c, it is usually not
injective. It is surjective only when the codomain is the singleton {c}.

Linear function
---------------
    f(x) = ax + b

If a != 0 and the domain and codomain are both R, the function is
bijective.

Quadratic function
------------------
    f(x) = x^2

From R to R:
    not injective
    not surjective

From [0,infinity) to [0,infinity):
    bijective.

Absolute value
--------------
    f(x) = |x|

From R to [0,infinity):
    surjective
    not injective.

Cubic function
--------------
    f(x) = x^3

From R to R:
    bijective.
"""
)


def identity(x: Any) -> Any:
    return x


def constant(_: Any) -> str:
    return "constant"


def square(x: float) -> float:
    return x * x


def absolute_value(x: float) -> float:
    return abs(x)


def cube(x: float) -> float:
    return x ** 3


finite_domain = {-2, -1, 0, 1, 2}

for name, function in [
    ("identity", identity),
    ("constant", constant),
    ("square", square),
    ("absolute value", absolute_value),
    ("cube", cube),
]:
    outputs = [function(x) for x in finite_domain]
    print(f"{name:15} outputs={outputs}")


# =============================================================================
# 17. RESTRICTION OF A FUNCTION
# =============================================================================

print_section("17. Restricting a function")

print(
    """
A restriction changes the domain while keeping the same rule.

Consider:

    f(x) = x^2

on R.

This function is not injective because:

    f(-2) = f(2).

If we restrict the domain to:

    [0,infinity)

then the restricted function becomes injective.

This illustrates an important principle:

    Injectivity depends on the domain.

The algebraic formula alone does not completely determine whether a
function is injective or surjective.
"""
)


def square_on_reals(x: float) -> float:
    return x * x


def square_on_nonnegative_reals(x: float) -> float:
    if x < 0:
        raise ValueError("The restricted domain is [0, infinity).")
    return x * x


print("x^2(-2) =", square_on_reals(-2))
print("x^2(2)  =", square_on_reals(2))
print("Restricted x^2(3) =", square_on_nonnegative_reals(3))


# =============================================================================
# 18. PIECEWISE FUNCTIONS
# =============================================================================

print_section("18. Piecewise-defined functions")

print(
    """
A piecewise function uses different formulas on different parts of the
domain.

Example:

    f(x) = x^2       if x < 0
           x + 1     if x >= 0

The complete definition includes both the formulas and their conditions.

Piecewise functions must still satisfy the function rule: every allowed
input must receive exactly one output.

Overlapping conditions can cause ambiguity if different branches produce
different values.

A gap in the conditions can cause an input to receive no output.
"""
)


def piecewise_function(x: float) -> float:
    """A valid piecewise function defined for every real x."""
    if x < 0:
        return x * x
    return x + 1


for value in [-3, -1, 0, 2]:
    print(f"f({value}) = {piecewise_function(value)}")


# =============================================================================
# 19. DOMAIN RESTRICTIONS FROM FORMULAS
# =============================================================================

print_section("19. Determining domain from formulas")

print(
    """
A formula does not necessarily define a function for every real number.

Examples:

1. Rational expression

       f(x) = 1 / (x - 2)

   requires:

       x != 2

2. Square root

       f(x) = sqrt(x - 3)

   over the real numbers requires:

       x >= 3

3. Logarithm

       f(x) = ln(x)

   over the real numbers requires:

       x > 0

4. A declared domain can be narrower than the natural domain.

For example:

       f : {1,2,3} -> R
       f(x) = x^2

The formula itself could accept many more inputs, but the declared
function only permits 1, 2, and 3.
"""
)


def reciprocal_shifted(x: float) -> float:
    """1/(x-2), defined only when x != 2."""
    if x == 2:
        raise ValueError("Division by zero: x cannot equal 2.")
    return 1 / (x - 2)


def square_root_shifted(x: float) -> float:
    """sqrt(x-3), defined over the reals for x >= 3."""
    if x < 3:
        raise ValueError("Real square root requires x >= 3.")
    return (x - 3) ** 0.5


print("1/(5-2) =", reciprocal_shifted(5))
print("sqrt(7-3) =", square_root_shifted(7))

for invalid_input in [2]:
    try:
        reciprocal_shifted(invalid_input)
    except ValueError as error:
        print("Expected error:", error)


# =============================================================================
# 20. DOMAIN VS CODOMAIN: SAME FORMULA, DIFFERENT FUNCTION
# =============================================================================

print_section("20. Same formula, different functions")

print(
    """
The following declarations use the same formula but are different
functions because their domains and codomains differ:

    f : R -> R
        f(x) = x^2

    g : R -> [0,infinity)
        g(x) = x^2

    h : [0,infinity) -> [0,infinity)
        h(x) = x^2

Their classifications differ:

    f:
        neither injective nor surjective

    g:
        surjective but not injective

    h:
        bijective

This is one of the most important reasons domain and codomain must be
specified when discussing injectivity and surjectivity.
"""
)


# =============================================================================
# 21. VERTICAL LINE TEST AND GRAPHICAL INTERPRETATION
# =============================================================================

print_section("21. Graphical interpretation")

print(
    """
For a graph in the Cartesian plane, the vertical line test determines
whether the graph represents y as a function of x.

If any vertical line intersects the graph at more than one point, then
the relation is not a function of x.

Examples:

    y = x^2
        passes the vertical line test.

    x = y^2
        does not pass the vertical line test when viewed as y as a
        function of x because x = 4 gives y = 2 and y = -2.

The vertical line test concerns whether something is a function.

It does not by itself determine injectivity.

For injectivity, the horizontal line test is useful:

    If every horizontal line intersects the graph at most once,
    the function is injective on its domain.
"""
)


def vertical_line_test_example(x: float) -> List[float]:
    """
    Return y-values satisfying y = x^2.

    For this example there is exactly one y for every x.
    """
    return [x * x]


def inverse_relation_example(x: float) -> List[float]:
    """
    Return y-values satisfying x = y^2 for x >= 0.

    At x > 0 there are two y-values, showing why the relation is not
    a function y = f(x) on all nonnegative x.
    """
    if x < 0:
        return []

    root = x ** 0.5
    if root == 0:
        return [0]

    return [root, -root]


print("For y=x^2, x=3 gives y-values:", vertical_line_test_example(3))
print("For x=y^2, x=4 gives y-values:", inverse_relation_example(4))


# =============================================================================
# 22. FUNCTION COMPOSITION
# =============================================================================

print_section("22. Composition of functions")

print(
    """
If:

    f : A -> B
    g : B -> C

then the composition:

    g o f : A -> C

is defined by:

    (g o f)(x) = g(f(x))

The order matters.

In general:

    g o f != f o g

even when both compositions are meaningful.

Example:

    f(x) = x + 1
    g(x) = 2x

Then:

    (g o f)(x) = 2(x + 1) = 2x + 2

while:

    (f o g)(x) = 2x + 1

Composition connects function definitions to pipelines: one output becomes
the next input.
"""
)


def f_add_one(x: int) -> int:
    return x + 1


def g_double(x: int) -> int:
    return 2 * x


def compose(
    outer: Callable[[Any], Any],
    inner: Callable[[Any], Any],
) -> Callable[[Any], Any]:
    """Return outer(inner(x))."""
    return lambda x: outer(inner(x))


g_after_f = compose(g_double, f_add_one)
f_after_g = compose(f_add_one, g_double)

for value in [0, 1, 5]:
    print(
        f"x={value}: "
        f"(g o f)(x)={g_after_f(value)}, "
        f"(f o g)(x)={f_after_g(value)}"
    )


# =============================================================================
# 23. COMPOSITION OF FINITE FUNCTIONS
# =============================================================================

print_section("23. Composition of finite functions")

print(
    """
Suppose:

    f : A -> B
    g : B -> C

For each x in A:

    (g o f)(x) = g(f(x))

The following implementation checks that the intermediate codomain of f
matches the domain of g.
"""
)


V = TypeVar("V", bound=Hashable)


def compose_finite_functions(
    g: FiniteFunction[U, V],
    f: FiniteFunction[T, U],
) -> FiniteFunction[T, V]:
    """Compose g after f."""
    if f.codomain != g.domain:
        raise ValueError(
            "For g o f, the codomain of f must equal the domain of g "
            "in this finite-set implementation."
        )

    mapping = {x: g(f(x)) for x in f.domain}

    return FiniteFunction(
        mapping=mapping,
        domain=set(f.domain),
        codomain=set(g.codomain),
    )


finite_f = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "c"},
    domain={1, 2, 3},
    codomain={"a", "b", "c"},
)

finite_g = FiniteFunction(
    mapping={"a": 10, "b": 20, "c": 30},
    domain={"a", "b", "c"},
    codomain={10, 20, 30},
)

finite_composition = compose_finite_functions(finite_g, finite_f)
print("g o f:", finite_composition.mapping)


# =============================================================================
# 24. COMPOSITION AND INJECTIVITY
# =============================================================================

print_section("24. Injectivity and composition")

print(
    """
Important theorem:

If f and g are injective, then g o f is injective.

Proof idea:

Suppose:

    (g o f)(x1) = (g o f)(x2)

Then:

    g(f(x1)) = g(f(x2))

Since g is injective:

    f(x1) = f(x2)

Since f is injective:

    x1 = x2.

Therefore g o f is injective.

A converse is also useful:

If g o f is injective, then f must be injective.

But g itself does not necessarily have to be injective on its entire
domain unless every relevant part is considered carefully.

For example, f can map into a subset of g's domain on which g happens
to be injective.
"""
)


def composition_is_injective(
    outer: FiniteFunction[U, V],
    inner: FiniteFunction[T, U],
) -> bool:
    """Check injectivity of a finite composition."""
    return compose_finite_functions(outer, inner).is_injective()


injective_outer = FiniteFunction(
    mapping={"a": 1, "b": 2, "c": 3},
    domain={"a", "b", "c"},
    codomain={1, 2, 3},
)

injective_inner = finite_f

print(
    "Composition of injective functions is injective:",
    composition_is_injective(injective_outer, injective_inner),
)


# =============================================================================
# 25. COMPOSITION AND SURJECTIVITY
# =============================================================================

print_section("25. Surjectivity and composition")

print(
    """
If f : A -> B and g : B -> C are both surjective, then:

    g o f : A -> C

is surjective.

Proof idea:

Take any c in C.

Because g is surjective, there exists b in B such that:

    g(b) = c.

Because f is surjective, there exists a in A such that:

    f(a) = b.

Therefore:

    (g o f)(a) = g(f(a)) = g(b) = c.

So every c is reached.

The reverse implications require care and are not generally valid without
additional assumptions.
"""
)


surjective_inner = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "a", 4: "b"},
    domain={1, 2, 3, 4},
    codomain={"a", "b"},
)

surjective_outer = FiniteFunction(
    mapping={"a": "X", "b": "Y"},
    domain={"a", "b"},
    codomain={"X", "Y"},
)

surjective_composition = compose_finite_functions(
    surjective_outer,
    surjective_inner,
)

print("Surjective inner:", surjective_inner.is_surjective())
print("Surjective outer:", surjective_outer.is_surjective())
print("Surjective composition:", surjective_composition.is_surjective())


# =============================================================================
# 26. BIJECTIONS AND COMPOSITION
# =============================================================================

print_section("26. Composition of bijections")

print(
    """
The composition of two bijections is a bijection.

If:

    f : A -> B
    g : B -> C

are bijective, then:

    g o f : A -> C

is bijective.

Its inverse is:

    (g o f)^(-1) = f^(-1) o g^(-1)

The order reverses.

This is analogous to reversing a sequence of operations:
to undo g(f(x)), first undo g and then undo f.
"""
)


bijection_f = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "c"},
    domain={1, 2, 3},
    codomain={"a", "b", "c"},
)

bijection_g = FiniteFunction(
    mapping={"a": "X", "b": "Y", "c": "Z"},
    domain={"a", "b", "c"},
    codomain={"X", "Y", "Z"},
)

bijection_composition = compose_finite_functions(
    bijection_g,
    bijection_f,
)

print("Composition:", bijection_composition.mapping)
print("Is bijective:", bijection_composition.is_bijective())


# =============================================================================
# 27. FUNCTION EQUALITY
# =============================================================================

print_section("27. Equality of functions")

print(
    """
Two functions are equal only when all relevant structure and values agree.

For ordinary mathematical functions, equality requires:

1. The same domain.
2. The same codomain.
3. The same output for every input in the domain.

Thus the following declarations are different functions:

    f : R -> R
        f(x) = x^2

    g : R -> [0,infinity)
        g(x) = x^2

Even though their formulas and outputs are the same, their codomains differ.

In many elementary contexts, people informally focus only on the rule,
but formal function equality includes the specified domain and codomain.
"""
)


def functions_equal(
    first: FiniteFunction[Any, Any],
    second: FiniteFunction[Any, Any],
) -> bool:
    """Check equality of finite functions including domain and codomain."""
    return (
        first.domain == second.domain
        and first.codomain == second.codomain
        and first.mapping == second.mapping
    )


function_a = FiniteFunction(
    mapping={1: 1, 2: 4},
    domain={1, 2},
    codomain={1, 4, 9},
)

function_b = FiniteFunction(
    mapping={1: 1, 2: 4},
    domain={1, 2},
    codomain={1, 4, 9},
)

function_c = FiniteFunction(
    mapping={1: 1, 2: 4},
    domain={1, 2},
    codomain={1, 4},
)

print("A equals B:", functions_equal(function_a, function_b))
print("A equals C:", functions_equal(function_a, function_c))


# =============================================================================
# 28. DIFFERENT REPRESENTATIONS OF FUNCTIONS
# =============================================================================

print_section("28. Representations of functions")

print(
    """
A function may be represented in several equivalent ways.

1. Verbal rule
   "Map each person to their employee identification number."

2. Formula
   f(x) = 2x + 1

3. Table

       x     f(x)
       0      1
       1      3
       2      5

4. Ordered pairs

       {(0,1), (1,3), (2,5)}

5. Mapping diagram

       0 -> 1
       1 -> 3
       2 -> 5

6. Graph

       Points or a curve in the Cartesian plane.

The representation changes, but the underlying function is the same when
the domain, codomain, and assignments agree.
"""
)


def table_representation(
    function: FiniteFunction[Any, Any],
) -> List[Tuple[Any, Any]]:
    """Return sorted table rows for a finite function."""
    return sorted(function.mapping.items(), key=lambda pair: repr(pair[0]))


for row in table_representation(bijective_example):
    print(row)


# =============================================================================
# 29. FUNCTION VS RELATION
# =============================================================================

print_section("29. Function versus relation")

print(
    """
Every function is a relation, but not every relation is a function.

Relation:

    {(1,a), (1,b), (2,c)}

This is a relation because it is a set of ordered pairs.

It is not a function from {1,2} to {a,b,c} because input 1 has two
different outputs.

Another relation:

    {(1,a), (2,b)}

is not a function from {1,2,3} because input 3 is missing.

A useful test is:

    For each domain element, trace its outgoing assignments.

Exactly one output -> valid function.
Zero outputs      -> not a function on that domain.
Two or more       -> not a function.
"""
)


relations_to_test = [
    ({(1, "a"), (2, "b")}, {1, 2}),
    ({(1, "a"), (1, "b")}, {1}),
    ({(1, "a")}, {1, 2}),
]

for relation, domain in relations_to_test:
    print(is_function_relation(relation, domain))


# =============================================================================
# 30. MANY-TO-ONE, ONE-TO-ONE, AND ONE-TO-MANY
# =============================================================================

print_section("30. One-to-one and many-to-one terminology")

print(
    """
One-to-one
----------
Usually means injective.

Distinct inputs have distinct outputs.

Many-to-one
-----------
A function can map multiple inputs to the same output.

Example:

    1 -> a
    2 -> a
    3 -> b

This is a valid function but not injective.

One-to-many
-----------
A genuine function cannot be one-to-many in the sense that one input
produces multiple different outputs.

A relation can be one-to-many, but such a relation is not a function
from the first set to the second.

This distinction is important in database and data-modeling contexts.
"""
)


# =============================================================================
# 31. PREIMAGE STRUCTURE AND INJECTIVITY
# =============================================================================

print_section("31. Preimages characterize injectivity")

print(
    """
A function is injective exactly when every element of its codomain has
at most one preimage.

For each y in B:

    |f^(-1)({y})| <= 1

If some y has two distinct preimages, injectivity fails.

If the function is surjective, every y in B has at least one preimage.

Therefore for a bijection:

    every codomain element has exactly one preimage.

This gives a useful unified view:

    injective:
        at most one preimage per output

    surjective:
        at least one preimage per codomain element

    bijective:
        exactly one preimage per codomain element
"""
)


def preimage_sizes(
    function: FiniteFunction[Any, Any],
) -> Dict[Any, int]:
    """Return the number of preimages of every codomain element."""
    return {
        y: len(function.preimage(y))
        for y in function.codomain
    }


print("Preimage sizes:", preimage_sizes(surjective_example))
print("Preimage sizes:", preimage_sizes(bijective_example))


# =============================================================================
# 32. RANGE AS AN IMAGE
# =============================================================================

print_section("32. Range calculations")

print(
    """
For finite domains, the range is straightforward:

    range(f) = {f(x) for x in domain}

For symbolic functions, finding the range can require mathematical
analysis.

Examples:

    f(x) = x^2, domain R
        range = [0,infinity)

    f(x) = x^2, domain [-2,3]
        range = [0,9]

    f(x) = 1/(x-2), domain R \\ {2}
        range = R \\ {0}

    f(x) = sin(x), domain R
        range = [-1,1]

The range is therefore determined jointly by the formula and the domain.
"""
)


def finite_range(function: FiniteFunction[Any, Any]) -> Set[Any]:
    """Return the range of a finite function."""
    return function.range


range_example = FiniteFunction(
    mapping={-2: 4, -1: 1, 0: 0, 1: 1, 2: 4},
    domain={-2, -1, 0, 1, 2},
    codomain={0, 1, 4, 9},
)

print("Range of x^2 on {-2,-1,0,1,2}:", finite_range(range_example))


# =============================================================================
# 33. ALGEBRAIC TESTS FOR INJECTIVITY
# =============================================================================

print_section("33. Algebraic methods for proving injectivity")

print(
    """
A common proof method starts with:

    f(x1) = f(x2)

and attempts to derive:

    x1 = x2.

For linear functions:

    f(x) = ax + b

with a != 0:

    ax1 + b = ax2 + b
    ax1 = ax2
    x1 = x2.

Therefore the function is injective.

For x^2:

    x1^2 = x2^2

gives:

    (x1-x2)(x1+x2) = 0

so:

    x1 = x2
    OR
    x1 = -x2.

The second possibility prevents injectivity on a symmetric domain such
as R.

Monotonicity provides another useful theorem:

    A strictly increasing function on an interval is injective.
    A strictly decreasing function on an interval is injective.
"""
)


def prove_linear_injective_symbolically(
    a: float,
    b: float,
    x1: float,
    x2: float,
) -> bool:
    """
    Numerically illustrate the algebraic proof for f(x)=ax+b.

    The proof itself is symbolic; this function simply checks a finite
    numerical instance.
    """
    if a == 0:
        return False

    left_equal = a * x1 + b == a * x2 + b
    return not left_equal or x1 == x2


print(
    "Linear example:",
    prove_linear_injective_symbolically(3, 5, 2, 2),
)


# =============================================================================
# 34. MONOTONICITY AND INJECTIVITY
# =============================================================================

print_section("34. Strict monotonicity")

print(
    """
If a function is strictly increasing on an interval:

    x1 < x2  =>  f(x1) < f(x2)

then it must be injective.

Similarly, if it is strictly decreasing:

    x1 < x2  =>  f(x1) > f(x2)

then it must be injective.

Non-strict monotonicity does not guarantee injectivity because a function
may remain constant over an interval.

For example:

    f(x) = 0

is both nondecreasing and nonincreasing, but is not injective on any
domain containing more than one element.
"""
)


def is_strictly_increasing_on_samples(
    function: Callable[[float], float],
    samples: Sequence[float],
) -> bool:
    """Check strict increase on an ordered finite sample."""
    ordered = sorted(samples)
    return all(
        function(left) < function(right)
        for left, right in zip(ordered, ordered[1:])
    )


print(
    "x^3 is strictly increasing on samples:",
    is_strictly_increasing_on_samples(
        lambda x: x ** 3,
        [-2, -1, 0, 1, 2],
    ),
)

print(
    "x^2 on [-2,-1,0,1,2] is strictly increasing:",
    is_strictly_increasing_on_samples(
        lambda x: x ** 2,
        [-2, -1, 0, 1, 2],
    ),
)


# =============================================================================
# 35. HORIZONTAL LINE TEST
# =============================================================================

print_section("35. Horizontal line test")

print(
    """
The horizontal line test is a graphical version of injectivity.

A function is injective if every horizontal line intersects its graph
at most once.

Examples:

    y = x^3
        passes the horizontal line test.

    y = x^2
        fails because y=4 intersects at x=-2 and x=2.

The test is a graphical tool, while the definition remains:

    f(x1) = f(x2) => x1 = x2.
"""
)


def sampled_horizontal_collision(
    function: Callable[[float], float],
    samples: Sequence[float],
) -> Dict[float, List[float]]:
    """
    Find output values having multiple sampled preimages.

    This is a finite approximation, not a proof for continuous domains.
    """
    preimages: Dict[float, List[float]] = {}

    for x in samples:
        y = function(x)
        preimages.setdefault(y, []).append(x)

    return {
        y: xs for y, xs in preimages.items()
        if len(xs) > 1
    }


print(
    "Sampled collisions for x^2:",
    sampled_horizontal_collision(
        lambda x: x * x,
        [-2, -1, 0, 1, 2],
    ),
)


# =============================================================================
# 36. SURJECTIVITY TESTS
# =============================================================================

print_section("36. Algebraic methods for proving surjectivity")

print(
    """
To prove f : A -> B is surjective, take an arbitrary y in B and solve:

    y = f(x)

for an x in A.

You must show that the resulting x is actually allowed by the domain.

Example:

    f : R -> R
        f(x) = 2x + 3

Given y in R:

    y = 2x + 3
    x = (y - 3)/2

This x is real for every real y.

Therefore f is surjective.

For:

    f : R -> R
        f(x) = x^2

given y=-1:

    -1 = x^2

has no real solution.

Therefore f is not surjective.

Changing the codomain to [0,infinity) makes the same rule surjective.
"""
)


def solve_linear_for_input(y: float) -> float:
    """Solve y = 2x+3 for x."""
    return (y - 3) / 2


for target in [-5, 0, 10]:
    x_value = solve_linear_for_input(target)
    print(
        f"Target y={target}: x={x_value}, "
        f"verification={2 * x_value + 3}"
    )


# =============================================================================
# 37. SURJECTIVITY OF FINITE FUNCTIONS
# =============================================================================

print_section("37. Computational surjectivity")

print(
    """
For finite functions, surjectivity is especially simple:

    range == codomain

This is an exact test, not a numerical approximation.

The implementation compares the two sets directly.
"""
)


def explain_surjectivity(function: FiniteFunction[Any, Any]) -> str:
    """Explain why a finite function is or is not surjective."""
    missing = function.codomain - function.range

    if not missing:
        return "Surjective: every codomain element is reached."

    return f"Not surjective: these codomain elements are not reached: {missing}"


print(explain_surjectivity(f_example))
print(explain_surjectivity(surjective_example))


# =============================================================================
# 38. DOMAIN AND CODOMAIN IN PROGRAMMING
# =============================================================================

print_section("38. Domain and codomain in programming")

print(
    """
Programming functions often resemble mathematical functions but need not
have mathematically clean domains and codomains.

For example:

    def reciprocal(x):
        return 1/x

The intended real-number domain is:

    R \\ {0}

If Python receives x=0, the program raises an exception.

A mathematical specification should therefore make the valid input
conditions explicit.

Programming also allows partial operations, exceptions, side effects,
mutable state, I/O, and nondeterminism. These features are outside the
classical definition of a pure mathematical function.

A pure computational function is closer to the mathematical concept:

    same input -> same output

with no externally visible side effects.
"""
)


def pure_double(x: int) -> int:
    """Pure function: same input always produces the same output."""
    return 2 * x


def safe_integer_division(
    numerator: int,
    denominator: int,
) -> Optional[Fraction]:
    """Return an exact quotient or None when division is undefined."""
    if denominator == 0:
        return None
    return Fraction(numerator, denominator)


print("pure_double(5):", pure_double(5))
print("10/2:", safe_integer_division(10, 2))
print("10/0:", safe_integer_division(10, 0))


# =============================================================================
# 39. PARTIAL FUNCTIONS VS TOTAL FUNCTIONS
# =============================================================================

print_section("39. Total and partial functions")

print(
    """
In elementary set theory, a function f : A -> B assigns exactly one
output to every x in A. Such a function is total on A.

A rule such as:

    f(x) = 1/x

is not total on R because x=0 has no real output.

It is total on:

    R \\ {0}.

In programming, people sometimes call operations partial when they can
fail for certain inputs.

The clean mathematical solution is often to define the domain correctly.

Instead of:

    f : R -> R
        f(x) = 1/x

write:

    f : R \\ {0} -> R
        f(x) = 1/x.
"""
)


# =============================================================================
# 40. EDGE CASE: EMPTY DOMAIN
# =============================================================================

print_section("40. Edge case: empty domain")

print(
    """
The empty function:

    f : empty_set -> B

is a valid function for every codomain B.

There are no domain elements that need an output, so the condition is
satisfied vacuously.

For finite sets:

    empty_set -> B

is injective.

It is surjective only when B is also empty.

Therefore:

    empty_set -> empty_set

is bijective.

This is an example where logical definitions handle edge cases more
reliably than informal intuition.
"""
)


empty_to_nonempty = FiniteFunction(
    mapping={},
    domain=set(),
    codomain={"a"},
)

empty_to_empty = FiniteFunction(
    mapping={},
    domain=set(),
    codomain=set(),
)

print(
    "empty -> {a}:",
    empty_to_nonempty.is_injective(),
    empty_to_nonempty.is_surjective(),
)

print(
    "empty -> empty:",
    empty_to_empty.is_injective(),
    empty_to_empty.is_surjective(),
    empty_to_empty.is_bijective(),
)


# =============================================================================
# 41. EDGE CASE: SINGLETON SETS
# =============================================================================

print_section("41. Edge case: singleton sets")

print(
    """
A singleton set has exactly one element.

For:

    A = {a}
    B = {b}

the only possible function is:

    a -> b

It is automatically injective and surjective, hence bijective.

A function from a singleton domain to a larger codomain is injective but
not surjective.

A function from a larger domain to a singleton codomain is surjective
but not injective, provided the domain is nonempty.
"""
)


singleton_bijection = FiniteFunction(
    mapping={"a": "b"},
    domain={"a"},
    codomain={"b"},
)

print("Singleton bijection:", singleton_bijection.is_bijective())


# =============================================================================
# 42. EMPTY CODOMAIN EDGE CASE
# =============================================================================

print_section("42. Empty codomain")

print(
    """
A function from a nonempty domain to the empty set cannot exist because
each input needs an output and there are no available outputs.

The only function into the empty set is:

    empty_set -> empty_set.
"""
)


try:
    impossible_function = FiniteFunction(
        mapping={1: None},
        domain={1},
        codomain=set(),
    )
except ValueError as error:
    print("Expected impossibility:", error)


# =============================================================================
# 43. FUNCTION RESTRICTION AND SURJECTIVITY
# =============================================================================

print_section("43. Restrictions can change surjectivity")

print(
    """
Restricting a domain can change both injectivity and surjectivity.

For:

    f(x) = x^2

from R to [0,infinity), f is surjective but not injective.

Restrict the domain to [0,infinity):

    f : [0,infinity) -> [0,infinity)

Now it is bijective.

Restricting the domain removed the negative inputs that caused the
two-to-one behavior.
"""
)


# =============================================================================
# 44. CODOMAIN CHANGES CAN CHANGE SURJECTIVITY
# =============================================================================

print_section("44. Changing the codomain can change surjectivity")

print(
    """
The same rule:

    f(x) = x^2

can be:

    R -> R
        not surjective

or:

    R -> [0,infinity)
        surjective

The actual outputs have not changed.

Only the declared codomain changed.

Therefore surjectivity is not a property of the formula alone.
"""
)


# =============================================================================
# 45. INVERSE IMAGE VS INVERSE FUNCTION
# =============================================================================

print_section("45. Inverse image versus inverse function")

print(
    """
These two ideas are frequently confused.

Inverse image / preimage:
-------------------------
For any function f and subset S of its codomain, the preimage f^(-1)(S)
is defined even if f has no inverse function.

Inverse function:
-----------------
A function f^(-1) exists only when f is bijective between the relevant
domain and codomain.

Example:

    f(x) = x^2
    domain = R

The preimage of {4} is:

    {-2, 2}

This is perfectly well-defined.

But there is no inverse function from R to R because 4 would need to map
back to both -2 and 2.
"""
)


print("Preimage of 4 under x^2:", {-2, 2})


# =============================================================================
# 46. INVERSE OF A RESTRICTED FUNCTION
# =============================================================================

print_section("46. Restricting a function to obtain an inverse")

print(
    """
For:

    f(x) = x^2
    x >= 0

the inverse is:

    f^(-1)(y) = sqrt(y)
    y >= 0.

The restriction makes the function injective while the codomain
[0,infinity) ensures surjectivity.
"""
)


def restricted_square_inverse(y: float) -> float:
    """Inverse of x^2 from [0,infinity) to [0,infinity)."""
    if y < 0:
        raise ValueError("The inverse domain requires y >= 0.")
    return y ** 0.5


for target in [0, 1, 4, 25]:
    recovered = restricted_square_inverse(target)
    print(f"sqrt({target}) = {recovered}")


# =============================================================================
# 47. DIFFERENT TYPES OF MAPPINGS
# =============================================================================

print_section("47. Mapping classifications")

print(
    """
Common mapping terminology:

One-to-one:
    injective.

Many-to-one:
    a valid function where multiple inputs may share outputs.

Onto:
    surjective.

Into:
    often used informally for a function whose range is a proper subset
    of the codomain, meaning it is not surjective.

One-to-one correspondence:
    bijective.

A diagram can be classified by examining incoming arrows at codomain
elements and outgoing arrows from domain elements.
"""
)


mapping_types = {
    "injective_not_surjective": injective_example,
    "surjective_not_injective": surjective_example,
    "bijective": bijective_example,
    "neither": f_example,
}

for label, function in mapping_types.items():
    print(
        f"{label:25} -> "
        f"injective={function.is_injective()}, "
        f"surjective={function.is_surjective()}"
    )


# =============================================================================
# 48. COMMON MISTAKES
# =============================================================================

print_section("48. Common mistakes")

print(
    """
Mistake 1:
    Treating every relation as a function.

Correction:
    Check that every domain element has exactly one output.

Mistake 2:
    Assuming codomain equals range.

Correction:
    Range is the set actually reached. Codomain is the declared target.

Mistake 3:
    Saying x^2 is always non-injective.

Correction:
    Injectivity depends on the domain. x^2 is injective on [0,infinity).

Mistake 4:
    Saying x^2 is never surjective.

Correction:
    Surjectivity depends on the codomain. x^2 is surjective from R
    onto [0,infinity).

Mistake 5:
    Thinking an inverse function always exists.

Correction:
    A function must be bijective between the relevant sets.

Mistake 6:
    Confusing f^(-1)(x) with 1/f(x).

Correction:
    Inverse function and reciprocal are different concepts.

Mistake 7:
    Checking only a few numerical points to prove injectivity or
    surjectivity over an infinite domain.

Correction:
    Numerical sampling can find counterexamples but generally cannot
    establish universal properties over continuous or infinite domains.

Mistake 8:
    Ignoring domain restrictions such as division by zero or square roots
    of negative numbers.

Correction:
    Determine the valid domain before classifying the function.
"""
)


# =============================================================================
# 49. COUNTEREXAMPLE-BASED REASONING
# =============================================================================

print_section("49. Counterexamples")

print(
    """
To disprove injectivity, one counterexample is sufficient:

    find x1 != x2 such that f(x1) = f(x2).

To disprove surjectivity, one counterexample is sufficient:

    find y in the codomain that is not produced by any domain input.

To disprove that a relation is a function, find one input with either:
    - no output, or
    - more than one distinct output.

Counterexamples are often computationally useful for discovering the
structure of a problem, but a mathematical proof may still be required
for a complete result.
"""
)


def find_injective_counterexample(
    function: Callable[[Any], Any],
    domain: Sequence[Any],
) -> Optional[Tuple[Any, Any]]:
    """Return two distinct sampled inputs with equal outputs, if found."""
    for index, x1 in enumerate(domain):
        for x2 in domain[index + 1:]:
            if function(x1) == function(x2):
                return x1, x2
    return None


print(
    "Collision for x^2:",
    find_injective_counterexample(
        lambda x: x * x,
        [-3, -2, -1, 0, 1, 2, 3],
    ),
)


# =============================================================================
# 50. COMPUTATIONAL COMPLEXITY OF FINITE CHECKS
# =============================================================================

print_section("50. Performance considerations")

print(
    """
For a finite function with n domain elements:

Naive injectivity check:
    Compare every pair.
    Time: O(n^2)

Hash-based injectivity check:
    Store outputs in a set.
    Expected time: O(n)

Surjectivity:
    Build or inspect the range and compare it with the codomain.
    Expected time: O(n), assuming hash operations are O(1) on average.

The finite-function class uses:

    len(values) == len(set(values))

for injectivity, which is expected O(n).

The direct definition-based function above intentionally uses O(n^2)
because it demonstrates the mathematical definition literally.

The choice between an educational implementation and an optimized
implementation depends on the purpose of the code.
"""
)


def is_injective_fast(
    function: Callable[[T], U],
    domain: Iterable[T],
) -> bool:
    """
    Expected O(n) injectivity test for hashable outputs.

    The set detects whether two different inputs produce the same output.
    """
    seen: Set[U] = set()

    for x in domain:
        y = function(x)
        if y in seen:
            return False
        seen.add(y)

    return True


print(
    "Fast injectivity check:",
    is_injective_fast(
        lambda x: x * x,
        range(-100, 101),
    ),
)


# =============================================================================
# 51. DOMAIN VALIDATION
# =============================================================================

print_section("51. Input validation")

print(
    """
A robust implementation should distinguish:

    input outside domain

from:

    input that produces a valid output.

For a finite function, checking membership in the declared domain before
evaluation makes the mathematical specification explicit.
"""
)


for value in [1, 3, 99]:
    try:
        print(f"f_example({value}) = {f_example(value)}")
    except ValueError as error:
        print(f"f_example({value}) failed:", error)


# =============================================================================
# 52. CODOMAIN VALIDATION
# =============================================================================

print_section("52. Codomain validation")

print(
    """
When constructing a finite function, every produced value must belong
to the declared codomain.

For example, this is invalid:

    f : {1,2} -> {"a","b"}
    f(1) = "c"

because "c" is outside the codomain.

This distinction is useful in software because it catches specification
errors at construction time instead of allowing an inconsistent mapping.
"""
)


try:
    FiniteFunction(
        mapping={1: "c", 2: "a"},
        domain={1, 2},
        codomain={"a", "b"},
    )
except ValueError as error:
    print("Expected codomain error:", error)


# =============================================================================
# 53. PROVING A FUNCTION IS BIJECTIVE BY FINDING AN INVERSE
# =============================================================================

print_section("53. Proving bijectivity by constructing an inverse")

print(
    """
A useful theorem is:

    If a function has a two-sided inverse, it is bijective.

Suppose:

    g(f(x)) = x

for all x in A, and:

    f(g(y)) = y

for all y in B.

Then f cannot map two different inputs to the same output, so it is
injective. Every y in B equals f(g(y)), so it is surjective.

Therefore f is bijective.
"""
)


def verify_two_sided_inverse(
    f: FiniteFunction[T, U],
    inverse: FiniteFunction[U, T],
) -> bool:
    """Verify both inverse identities for a finite function."""
    first_identity = all(
        inverse(f(x)) == x
        for x in f.domain
    )

    second_identity = all(
        f(inverse(y)) == y
        for y in f.codomain
    )

    return first_identity and second_identity


print(
    "Two-sided inverse verified:",
    verify_two_sided_inverse(
        bijective_example,
        inverse_example,
    ),
)


# =============================================================================
# 54. FUNCTIONAL PROGRAMMING CONNECTION
# =============================================================================

print_section("54. Mathematical functions and pure programming functions")

print(
    """
A pure programming function has a useful correspondence with a
mathematical function:

    input -> output

For example:

    square(5) -> 25

If the function is deterministic and has no relevant side effects,
repeated evaluation with the same input gives the same result.

But Python functions can also:

    modify global state,
    read files,
    access the network,
    print output,
    mutate objects,
    depend on time or randomness.

Such functions do not behave like pure mathematical functions in the
strict sense because their result or observable behavior may depend on
more than their explicit argument.
"""
)


state = {"calls": 0}


def impure_square(x: int) -> int:
    """Same mathematical calculation, but with an observable side effect."""
    state["calls"] += 1
    return x * x


print("First call:", impure_square(4))
print("Second call:", impure_square(4))
print("Number of calls:", state["calls"])


# =============================================================================
# 55. HASHABILITY AND FINITE FUNCTION REPRESENTATION
# =============================================================================

print_section("55. Implementation detail: finite-set representation")

print(
    """
The FiniteFunction class uses Python sets and dictionaries.

This means elements need to be hashable.

Typical hashable values include:

    integers
    strings
    tuples containing hashable values
    frozensets

Mutable lists and dictionaries are not hashable and therefore cannot be
used directly as set elements or dictionary keys.

This is an implementation constraint, not a mathematical restriction.
Mathematically, sets may contain objects that do not correspond neatly
to Python hashable objects.
"""
)


tuple_based_function = FiniteFunction(
    mapping={(1, 2): "point A", (3, 4): "point B"},
    domain={(1, 2), (3, 4)},
    codomain={"point A", "point B"},
)

print(tuple_based_function.mapping)


# =============================================================================
# 56. REAL-WORLD APPLICATIONS
# =============================================================================

print_section("56. Real-world applications")

print(
    """
Functions appear throughout mathematics, computing, science, and data
systems.

Examples:

1. Employee ID lookup

       employee -> employee_id

   If each employee has exactly one ID, this is a function.

2. Product price lookup

       product_code -> price

   A current pricing table behaves like a function when each code has
   exactly one selected price.

3. Student grading

       student_id -> grade

   This can be a function when one grade is associated with each student
   for a particular assessment.

4. Coordinate transformation

       (x,y) -> (u,v)

   Bijective transformations are especially useful because every valid
   output corresponds to exactly one input.

5. Encryption

   A well-designed encryption transformation is often modeled using
   bijections over a defined message or state space so that decryption
   can uniquely recover the original value.

6. Database keys

   A unique identifier behaves like an injective mapping from records
   to identifiers when each record has a distinct key.

7. Hashing

   A hash function need not be injective because many possible inputs
   can map to the same fixed-size hash output.

8. Machine-learning models

   A deterministic model can be viewed abstractly as a function from
   an input space to an output space, although practical systems may
   include randomness, state, or numerical approximations.

9. Unit conversion

       meters -> centimeters

   is a function on its defined numerical domain.

10. Coordinate systems

       geographic coordinates -> projected coordinates

   can be functions with domain restrictions and may or may not be
   one-to-one depending on the projection and region.
"""
)


def employee_to_id(employee_name: str) -> str:
    """Example of a deterministic lookup-style function."""
    employee_ids = {
        "Alice": "E001",
        "Bob": "E002",
        "Charlie": "E003",
    }

    if employee_name not in employee_ids:
        raise KeyError(f"Unknown employee: {employee_name}")

    return employee_ids[employee_name]


print("Employee ID:", employee_to_id("Alice"))


# =============================================================================
# 57. INJECTIVITY AND DATABASE UNIQUENESS
# =============================================================================

print_section("57. Injectivity as uniqueness")

print(
    """
Suppose a system maps records to identifiers:

    record -> ID

If two distinct records receive the same ID, the mapping is not injective.

For a primary-key-like identifier, uniqueness is therefore closely related
to injectivity.

This does not mean every database relationship must be injective.
Many legitimate relationships are many-to-one or many-to-many.
The correct classification depends on the entities and direction of the
mapping being modeled.
"""
)


def ids_are_unique(record_ids: Sequence[str]) -> bool:
    """Check whether identifiers define an injective mapping over records."""
    return len(record_ids) == len(set(record_ids))


print("Unique IDs:", ids_are_unique(["E001", "E002", "E003"]))
print("Duplicate IDs:", ids_are_unique(["E001", "E002", "E001"]))


# =============================================================================
# 58. HASH FUNCTIONS AS NON-INJECTIVE EXAMPLES
# =============================================================================

print_section("58. Hashing and collisions")

print(
    """
A fixed-size hash function typically maps a much larger input space into
a smaller output space.

For example, if there are more possible inputs than possible hash values,
the pigeonhole principle guarantees collisions.

Therefore a general hash function cannot be injective over its entire
unbounded input space when the output space is finite.

A collision means:

    x1 != x2
    but
    hash(x1) = hash(x2)

This does not make hashing invalid. Hash functions are designed for
different purposes such as indexing and integrity checks, and cryptographic
hash functions are designed so that finding useful collisions is
computationally difficult, not mathematically impossible.
"""
)


def tiny_hash(text: str, number_of_buckets: int = 5) -> int:
    """Intentionally tiny hash for demonstrating inevitable collisions."""
    if number_of_buckets <= 0:
        raise ValueError("Number of buckets must be positive.")

    return sum(ord(character) for character in text) % number_of_buckets


words = ["cat", "dog", "apple", "banana", "orange", "grape"]
tiny_hash_results = {word: tiny_hash(word) for word in words}

print("Tiny hash values:", tiny_hash_results)

collisions: Dict[int, List[str]] = {}
for word, hash_value in tiny_hash_results.items():
    collisions.setdefault(hash_value, []).append(word)

print(
    "Hash buckets containing multiple words:",
    {bucket: values for bucket, values in collisions.items() if len(values) > 1},
)


# =============================================================================
# 59. SECURITY CONSIDERATIONS
# =============================================================================

print_section("59. Security considerations")

print(
    """
Function classification has practical security implications.

Injectivity:
    A transformation that must preserve unique identities may need
    injectivity so that distinct inputs do not become indistinguishable.

Surjectivity:
    If every valid output must be reachable, the transformation may need
    surjectivity.

Bijectivity:
    Reversible transformations require a unique inverse, so bijectivity
    is the natural mathematical model for many reversible operations.

Hashing:
    Cryptographic hashes intentionally compress large input spaces into
    fixed-size outputs, so they cannot be injective over all possible
    inputs. Security relies on computational hardness properties, not
    mathematical injectivity.

Input validation:
    Domain restrictions should be enforced before performing operations
    that are undefined or unsafe for certain values.

A mathematical proof of bijectivity does not by itself establish the
security of a real software system. Implementation details, numerical
precision, serialization, key management, side channels, and error
handling can introduce separate security concerns.
"""
)


# =============================================================================
# 60. NUMERICAL PRECISION AND FUNCTION EVALUATION
# =============================================================================

print_section("60. Numerical considerations")

print(
    """
Mathematical equality and floating-point equality are not always identical
in computer programs.

For example, decimal fractions may not have exact binary floating-point
representations.

This matters when testing properties such as:

    f(x1) == f(x2)

for numerical functions.

For exact finite symbolic examples, integers, strings, and Fraction objects
are preferable.

For floating-point applications, an approximate comparison may be needed,
but an approximation can change the behavior of computational tests.

Therefore:

    exact mathematical classification
and
    numerical experimental evidence

should not be treated as the same thing.
"""
)


def exact_fraction_function(x: Fraction) -> Fraction:
    """An exact function using rational arithmetic."""
    return x * x + Fraction(1, 2)


for fraction_value in [Fraction(1, 3), Fraction(2, 3)]:
    print(
        f"f({fraction_value}) = "
        f"{exact_fraction_function(fraction_value)}"
    )


# =============================================================================
# 61. TESTING FINITE FUNCTIONS
# =============================================================================

print_section("61. Automated tests")

print(
    """
For a finite function, important properties can be tested directly.

Useful invariants include:

1. Every mapping key belongs to the domain.
2. Every output belongs to the codomain.
3. range is a subset of codomain.
4. Injectivity means no repeated outputs.
5. Surjectivity means range equals codomain.
6. Bijectivity means both properties hold.
7. A computed inverse satisfies both inverse identities.
"""
)


def run_finite_function_tests() -> None:
    """Run basic assertions for the finite-function implementation."""
    assert f_example.domain == {1, 2, 3}
    assert f_example.range == {"a", "b"}
    assert f_example.range <= f_example.codomain

    assert not f_example.is_injective()
    assert not f_example.is_surjective()
    assert not f_example.is_bijective()

    assert bijective_example.is_injective()
    assert bijective_example.is_surjective()
    assert bijective_example.is_bijective()

    inverse = bijective_example.inverse()

    for x in bijective_example.domain:
        assert inverse(bijective_example(x)) == x

    for y in bijective_example.codomain:
        assert bijective_example(inverse(y)) == y

    assert singleton_bijection.is_bijective()
    assert empty_to_empty.is_bijective()
    assert empty_to_nonempty.is_injective()
    assert not empty_to_nonempty.is_surjective()


run_finite_function_tests()
print("All finite-function assertions passed.")


# =============================================================================
# 62. PROPERTY TABLE
# =============================================================================

print_section("62. Classification property table")

print(
    """
+-------------------------------+-------------------------------+
| Property                      | Meaning                       |
+-------------------------------+-------------------------------+
| Function                      | One output per input         |
| Injective                     | At most one input per output |
| Surjective                    | At least one input per       |
|                               | codomain element             |
| Bijective                     | Exactly one input per output |
| Non-injective                 | At least one collision       |
| Non-surjective                | At least one missed output   |
+-------------------------------+-------------------------------+

For a bijection:

    every domain element -> exactly one codomain element
    every codomain element <- exactly one domain element
"""
)


# =============================================================================
# 63. FINITE SET DECISION PROCEDURE
# =============================================================================

print_section("63. Practical decision procedure")

print(
    """
For a finite mapping, the following procedure is reliable:

Step 1:
    Verify that every domain element has exactly one output.

Step 2:
    Verify every output belongs to the codomain.

Step 3:
    Compute the range.

Step 4:
    Check injectivity:
        Are all outputs distinct?

Step 5:
    Check surjectivity:
        Does range equal codomain?

Step 6:
    If both are true:
        the function is bijective.

Step 7:
    If bijective:
        an inverse function exists.
"""
)


def classify_finite_function(
    function: FiniteFunction[Any, Any],
) -> str:
    """Return a human-readable classification."""
    if function.is_bijective():
        return "bijective"

    if function.is_injective():
        return "injective but not surjective"

    if function.is_surjective():
        return "surjective but not injective"

    return "neither injective nor surjective"


for name, function in mapping_types.items():
    print(f"{name:25}: {classify_finite_function(function)}")


# =============================================================================
# 64. EXAMPLE: FUNCTION FROM LETTERS TO NUMBERS
# =============================================================================

print_section("64. Complete finite example")

print(
    """
Consider:

    A = {"a","b","c","d"}
    B = {1,2,3,4}

and:

    a -> 2
    b -> 4
    c -> 1
    d -> 3

Every input has one output.
Every output is used exactly once.

Therefore the mapping is bijective.
Its inverse is:

    1 -> c
    2 -> a
    3 -> d
    4 -> b
"""
)


letter_number_function = FiniteFunction(
    mapping={
        "a": 2,
        "b": 4,
        "c": 1,
        "d": 3,
    },
    domain={"a", "b", "c", "d"},
    codomain={1, 2, 3, 4},
)

print_mapping(letter_number_function)
print("Range:", letter_number_function.range)
print("Classification:", classify_finite_function(letter_number_function))
print("Inverse:", letter_number_function.inverse().mapping)


# =============================================================================
# 65. EXAMPLE: FUNCTION THAT IS INJECTIVE BUT NOT SURJECTIVE
# =============================================================================

print_section("65. Injective but not surjective")

print(
    """
Example:

    A = {1,2,3}
    B = {"a","b","c","d"}

    1 -> a
    2 -> b
    3 -> c

No output is repeated, so the function is injective.

But d is never reached, so it is not surjective.

Because the function is not bijective, it has no inverse function
from B to A.
"""
)


injective_only = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "c"},
    domain={1, 2, 3},
    codomain={"a", "b", "c", "d"},
)

print("Classification:", classify_finite_function(injective_only))

try:
    injective_only.inverse()
except ValueError as error:
    print("Expected inverse error:", error)


# =============================================================================
# 66. EXAMPLE: SURJECTIVE BUT NOT INJECTIVE
# =============================================================================

print_section("66. Surjective but not injective")

print(
    """
Example:

    A = {1,2,3}
    B = {"a","b"}

    1 -> a
    2 -> b
    3 -> a

Both a and b are reached, so the function is surjective.

But 1 and 3 have the same output, so it is not injective.

There is no inverse function from B to A because a would need to map
back to both 1 and 3.
"""
)


surjective_only = FiniteFunction(
    mapping={1: "a", 2: "b", 3: "a"},
    domain={1, 2, 3},
    codomain={"a", "b"},
)

print("Classification:", classify_finite_function(surjective_only))

try:
    surjective_only.inverse()
except ValueError as error:
    print("Expected inverse error:", error)


# =============================================================================
# 67. EXAMPLE: NEITHER
# =============================================================================

print_section("67. Neither injective nor surjective")

print(
    """
Example:

    A = {1,2,3}
    B = {"a","b","c","d"}

    1 -> a
    2 -> a
    3 -> b

The function is not injective because 1 and 2 collide.

It is not surjective because c and d are never reached.
"""
)


neither_function = FiniteFunction(
    mapping={1: "a", 2: "a", 3: "b"},
    domain={1, 2, 3},
    codomain={"a", "b", "c", "d"},
)

print("Classification:", classify_finite_function(neither_function))


# =============================================================================
# 68. FUNCTION COMPOSITION WITH INVERSE
# =============================================================================

print_section("68. Composition with an inverse")

print(
    """
For a bijection f:

    f^(-1) o f = id_A

and:

    f o f^(-1) = id_B.

The identity function leaves every element unchanged.

This is the formal meaning of "undoing" a bijection.
"""
)


inverse_letter_number = letter_number_function.inverse()

identity_from_composition = compose_finite_functions(
    inverse_letter_number,
    letter_number_function,
)

identity_on_codomain = compose_finite_functions(
    letter_number_function,
    inverse_letter_number,
)

print("f^-1 o f:", identity_from_composition.mapping)
print("f o f^-1:", identity_on_codomain.mapping)


# =============================================================================
# 69. INFINITE SET EXAMPLE
# =============================================================================

print_section("69. Infinite-set example")

print(
    """
Consider:

    f : N -> N
    f(n) = n + 1

where:

    N = {0,1,2,3,...}

Injectivity:

    n1 + 1 = n2 + 1
    => n1 = n2

so f is injective.

Surjectivity:

    0 has no preimage because n + 1 = 0 has no solution in N.

Therefore f is not surjective.

This demonstrates why the finite-set rule:

    same cardinality + injective => surjective

cannot simply be replaced by intuition about infinite sets.
"""
)


def successor(n: int) -> int:
    """Successor function on nonnegative integers."""
    if n < 0:
        raise ValueError("This example uses N={0,1,2,...}.")
    return n + 1


print("Successor values:", [successor(n) for n in range(6)])


# =============================================================================
# 70. INFINITE BIJECTION EXAMPLE
# =============================================================================

print_section("70. A bijection between integers and even integers")

print(
    """
The function:

    f : Z -> 2Z
    f(n) = 2n

is bijective.

Injective:

    2n1 = 2n2
    => n1 = n2

Surjective onto the even integers:

    for every even integer y,
    y = 2n for n = y/2.

The codomain is important. The same formula:

    f(n) = 2n

viewed as:

    Z -> Z

is not surjective because odd integers are not reached.
"""
)


def double_integer(n: int) -> int:
    return 2 * n


integer_samples = list(range(-4, 5))
print(
    "Doubling:",
    {n: double_integer(n) for n in integer_samples},
)


# =============================================================================
# 71. FUNCTION NOTATION WITH PARAMETERS
# =============================================================================

print_section("71. Functions with parameters")

print(
    """
A family of functions can contain parameters.

For example:

    f_a(x) = ax

For each fixed value of a, this produces a different function.

If:

    a != 0

then:

    f_a : R -> R

is bijective.

If:

    a = 0

then:

    f_0(x) = 0

is constant, so it is neither injective nor surjective from R to R.
"""
)


def parameterized_linear(a: float, x: float) -> float:
    """Compute f_a(x)=a*x."""
    return a * x


for coefficient in [-2, 0, 3]:
    print(
        f"a={coefficient}:",
        [parameterized_linear(coefficient, x) for x in [-2, -1, 0, 1, 2]],
    )


# =============================================================================
# 72. FUNCTION COMPOSITION AS A PIPELINE
# =============================================================================

print_section("72. Composition as a computational pipeline")

print(
    """
Suppose:

    clean(x)
    normalize(x)
    encode(x)

are functions whose output domains match the next input domains.

Then:

    encode(normalize(clean(x)))

is a composition.

The same mathematical structure appears in software pipelines.

Composition is safest when each stage has clearly specified input and
output domains.
"""
)


def clean_text(text: str) -> str:
    return text.strip()


def normalize_text(text: str) -> str:
    return text.lower()


def encode_length(text: str) -> int:
    return len(text)


text_pipeline = compose(
    encode_length,
    compose(normalize_text, clean_text),
)

print("Pipeline result:", text_pipeline("  Function Theory  "))


# =============================================================================
# 73. CODOMAIN DESIGN
# =============================================================================

print_section("73. Designing an appropriate codomain")

print(
    """
Choosing a codomain is part of specifying a mathematical function.

Suppose a function computes an absolute value.

The natural real-valued rule is:

    |x|

If the codomain is R:
    the function is not surjective.

If the codomain is [0,infinity):
    it is surjective.

A narrow, accurate codomain can express useful guarantees.

In software APIs, an output type similarly communicates what results
are allowed, although a programming type system is not identical to a
mathematical codomain.
"""
)


# =============================================================================
# 74. RANGE COMPUTATION FOR FINITE FUNCTIONS
# =============================================================================

print_section("74. Range and codomain comparison")

print(
    """
A compact diagnostic for finite functions is:

    range = codomain
        => surjective

    range proper subset of codomain
        => not surjective
"""
)


def range_codomain_comparison(
    function: FiniteFunction[Any, Any],
) -> None:
    print("Range   :", function.range)
    print("Codomain:", function.codomain)
    print("Equal   :", function.range == function.codomain)


range_codomain_comparison(injective_only)
range_codomain_comparison(surjective_only)


# =============================================================================
# 75. PREIMAGE PARTITIONS
# =============================================================================

print_section("75. Preimages and partitions")

print(
    """
For any function f : A -> B, the sets

    f^(-1)({y})

for y in the range divide the domain into disjoint fibers.

Each domain element belongs to exactly one fiber because every input has
exactly one output.

For an injective function, every nonempty fiber contains exactly one
element.

For a many-to-one function, some fibers contain multiple elements.

For a surjective function, every codomain fiber is nonempty.

For a bijection, every codomain fiber contains exactly one element.
"""
)


def fibers(
    function: FiniteFunction[T, U],
) -> Dict[U, Set[T]]:
    """Return all nonempty preimage fibers."""
    return {
        y: function.preimage(y)
        for y in function.codomain
        if function.preimage(y)
    }


print("Fibers of surjective-only function:", fibers(surjective_only))
print("Fibers of bijection:", fibers(bijective_example))


# =============================================================================
# 76. ADVANCED SET-THEORETIC VIEW
# =============================================================================

print_section("76. Set-theoretic view of functions")

print(
    """
A function f : A -> B can be represented as a subset of A x B satisfying:

    for every x in A,
    there exists exactly one y in B
    such that (x,y) belongs to f.

The graph of f is therefore:

    Graph(f) = {(x, f(x)) : x in A}.

The graph contains exactly |A| ordered pairs when A is finite.

Injectivity means that the second coordinates in these pairs are all
distinct.

Surjectivity means every element of B occurs as a second coordinate.

Bijectivity means the graph pairs the two sets perfectly.
"""
)


print("Graph of bijection:", bijective_example.graph())


# =============================================================================
# 77. FUNCTION VALUES AND DOMAIN MEMBERSHIP
# =============================================================================

print_section("77. Evaluating functions correctly")

print(
    """
The expression:

    f(a)

has meaning only when a belongs to the domain of f.

For a declared function:

    f : A -> B

it is not correct to evaluate f(a) for an a outside A without changing
the mathematical function or extending its definition.

In programming, domain checking is an explicit way to preserve this
contract.
"""
)


try:
    print(f_example(100))
except ValueError as error:
    print("Domain violation handled:", error)


# =============================================================================
# 78. FUNCTION RESTRICTION IMPLEMENTATION
# =============================================================================

print_section("78. Implementing a finite restriction")

print(
    """
For a finite function f and a subset S of its domain, the restriction
f|S has:

    domain = S

while preserving:

    f|S(x) = f(x).
"""
)


def restrict_function(
    function: FiniteFunction[T, U],
    restricted_domain: Set[T],
) -> FiniteFunction[T, U]:
    """Return the restriction of a finite function."""
    if not restricted_domain <= function.domain:
        raise ValueError("Restriction domain must be a subset of the original domain.")

    return FiniteFunction(
        mapping={
            x: function(x)
            for x in restricted_domain
        },
        domain=set(restricted_domain),
        codomain=set(function.codomain),
    )


restricted_bijective_example = restrict_function(
    range_example,
    {0, 1, 2},
)

print("Restricted mapping:", restricted_bijective_example.mapping)
print("Restricted range:", restricted_bijective_example.range)


# =============================================================================
# 79. FUNCTION EXTENSION
# =============================================================================

print_section("79. Function extension")

print(
    """
An extension enlarges the domain while preserving the existing assignments.

Suppose f is defined on S. A larger function g defined on T, where:

    S subset T

is an extension if:

    g(x) = f(x)

for every x in S.

An extension can change injectivity because new domain elements may
produce outputs already used by old inputs.

It can also change surjectivity if the codomain remains fixed.
"""
)


# =============================================================================
# 80. FUNCTIONAL EQUATIONS AND FUNCTION IDENTITY
# =============================================================================

print_section("80. Function identities")

print(
    """
An identity such as:

    f(x) = g(x)

for all x in the common domain is a statement about equality of
functions when their domains and codomains also agree.

Testing a few values can suggest an identity, but for infinite domains
a proof must establish equality for every permitted input.

Example:

    (x+1)^2 = x^2 + 2x + 1

for every real x.

This is an algebraic identity and therefore defines the same rule wherever
the domain and codomain specifications match.
"""
)


def expanded_square(x: float) -> float:
    return (x + 1) ** 2


def polynomial_square(x: float) -> float:
    return x * x + 2 * x + 1


for value in [-10, -1, 0, 2, 100]:
    assert expanded_square(value) == polynomial_square(value)

print("Sampled identity checks passed.")


# =============================================================================
# 81. FUNCTIONAL DEPENDENCE
# =============================================================================

print_section("81. Functional dependence")

print(
    """
When y is a function of x, writing:

    y = f(x)

means x determines exactly one y.

This does not mean that x is necessarily determined by y.

For example:

    y = x^2

makes y a function of x.

But x is not a function of y over the full real domain because:

    y = 4

corresponds to:

    x = 2
    x = -2.

Thus:

    "y is a function of x"

does not automatically imply:

    "x is a function of y."

Injectivity is exactly the additional property that allows the reverse
mapping to be a function on the appropriate codomain.
"""
)


# =============================================================================
# 82. DOMAIN-CODOMAIN-RANGE DIAGNOSTIC
# =============================================================================

print_section("82. Complete diagnostic")

print(
    """
For any finite function, a useful diagnostic report contains:

    domain
    codomain
    range
    missing codomain values
    repeated outputs
    injectivity
    surjectivity
    bijectivity
    inverse, if available.
"""
)


def function_diagnostic(
    function: FiniteFunction[Any, Any],
) -> Dict[str, Any]:
    """Create a complete finite-function diagnostic report."""
    repeated_outputs: Dict[Any, List[Any]] = {}

    for x in function.domain:
        y = function(x)
        repeated_outputs.setdefault(y, []).append(x)

    repeated_outputs = {
        y: inputs
        for y, inputs in repeated_outputs.items()
        if len(inputs) > 1
    }

    return {
        "domain": function.domain,
        "codomain": function.codomain,
        "range": function.range,
        "missing_codomain_values": function.codomain - function.range,
        "repeated_outputs": repeated_outputs,
        "injective": function.is_injective(),
        "surjective": function.is_surjective(),
        "bijective": function.is_bijective(),
    }


print(function_diagnostic(surjective_only))
print(function_diagnostic(bijective_example))


# =============================================================================
# 83. MATHEMATICAL PROOF TEMPLATES
# =============================================================================

print_section("83. Proof templates")

print(
    """
Injectivity proof template
--------------------------
Let x1 and x2 belong to the domain and suppose:

    f(x1) = f(x2).

Use algebra or another property of f to show:

    x1 = x2.

Therefore f is injective.

Surjectivity proof template
---------------------------
Let y be an arbitrary element of the codomain.

Solve:

    y = f(x)

for x.

Show that the resulting x belongs to the domain.

Therefore every y in the codomain has a preimage, so f is surjective.

Bijectivity proof template
--------------------------
Prove both injectivity and surjectivity.

Alternatively, construct an explicit two-sided inverse and verify:

    f^(-1)(f(x)) = x

and:

    f(f^(-1)(y)) = y.

Counterexample template for non-injectivity
-------------------------------------------
Find:

    x1 != x2
    but
    f(x1) = f(x2).

Counterexample template for non-surjectivity
---------------------------------------------
Find y in the codomain such that:

    f(x) != y

for every x in the domain.
"""
)


# =============================================================================
# 84. FINAL INTEGRATED EXAMPLE
# =============================================================================

print_section("84. Integrated example: a complete analysis")

print(
    """
Consider:

    f : {-3,-2,-1,0,1,2,3} -> {0,1,4,9,16}

defined by:

    f(x) = x^2.

We can determine:

    domain  = {-3,-2,-1,0,1,2,3}
    codomain = {0,1,4,9,16}
    range = {0,1,4,9}

It is not injective because:

    f(-1) = f(1) = 1

It is not surjective because:

    16 belongs to the codomain but is not reached.

Therefore it is neither injective nor surjective.

If the domain is restricted to:

    {0,1,2,3}

then:

    range = {0,1,4,9}

and with codomain {0,1,4,9}, the function becomes bijective.

Its inverse is:

    0 -> 0
    1 -> 1
    4 -> 2
    9 -> 3.
"""
)


integrated_function = FiniteFunction(
    mapping={
        -3: 9,
        -2: 4,
        -1: 1,
        0: 0,
        1: 1,
        2: 4,
        3: 9,
    },
    domain={-3, -2, -1, 0, 1, 2, 3},
    codomain={0, 1, 4, 9, 16},
)

print("Integrated diagnostic:")
for key, value in function_diagnostic(integrated_function).items():
    print(f"  {key}: {value}")


restricted_integrated = restrict_function(
    integrated_function,
    {0, 1, 2, 3},
)

restricted_integrated = FiniteFunction(
    mapping=restricted_integrated.mapping,
    domain=restricted_integrated.domain,
    codomain={0, 1, 4, 9},
)

print("\nRestricted diagnostic:")
for key, value in function_diagnostic(restricted_integrated).items():
    print(f"  {key}: {value}")

print("Restricted inverse:", restricted_integrated.inverse().mapping)


# =============================================================================
# 85. SELF-CHECKING KNOWLEDGE TEST
# =============================================================================

print_section("85. Self-checking exercises")

print(
    """
The following assertions encode important facts from the topic.
They act as executable checks of the theory.
"""
)


# A function can be many-to-one.
many_to_one = FiniteFunction(
    mapping={1: "x", 2: "x", 3: "y"},
    domain={1, 2, 3},
    codomain={"x", "y"},
)

assert not many_to_one.is_injective()
assert many_to_one.is_surjective()

# A function can be injective but not onto.
one_to_one_into = FiniteFunction(
    mapping={1: "a", 2: "b"},
    domain={1, 2},
    codomain={"a", "b", "c"},
)

assert one_to_one_into.is_injective()
assert not one_to_one_into.is_surjective()

# Equal finite cardinalities make injection and surjection equivalent.
all_three_to_three = generate_all_finite_functions(
    [1, 2, 3],
    ["a", "b", "c"],
)

for function in all_three_to_three:
    assert function.is_injective() == function.is_surjective()

# Every bijection has an inverse.
for function in all_three_to_three:
    if function.is_bijective():
        inverse = function.inverse()

        for x in function.domain:
            assert inverse(function(x)) == x

        for y in function.codomain:
            assert function(inverse(y)) == y

print("All theory-based self-checks passed.")


# =============================================================================
# 86. CONCEPTUAL DISTINCTIONS
# =============================================================================

print_section("86. Key distinctions encoded in examples")

print(
    """
Function:
    exactly one output for each input.

Relation:
    arbitrary set of ordered pairs.

Domain:
    allowed inputs.

Codomain:
    declared target set.

Range:
    actual outputs.

Injective:
    no two distinct inputs share an output.

Surjective:
    every codomain element is reached.

Bijective:
    injective and surjective.

Inverse function:
    reverses a bijection.

Preimage:
    set of inputs producing a specified output or subset of outputs.

Restriction:
    same rule on a smaller domain.

Composition:
    applying one function after another.

Cardinality:
    number of elements in a finite set.

Pigeonhole principle:
    more inputs than outputs forces a collision.

The most important structural fact is that classification always depends
on the function as a mapping between specified sets, not merely on the
symbolic formula.
"""
)


# =============================================================================
# 87. SCRIPT COMPLETION
# =============================================================================

print_section("87. End of executable study script")

print(
    """
The script has demonstrated:

- formal function definitions;
- relations and ordered pairs;
- domain, codomain, and range;
- function notation;
- mapping representations;
- images and preimages;
- injective functions;
- surjective functions;
- bijective functions;
- inverse functions;
- finite cardinality;
- the pigeonhole principle;
- enumeration and counting formulas;
- algebraic and graphical reasoning;
- restrictions and extensions;
- piecewise functions;
- domain restrictions;
- composition;
- composition theorems;
- infinite-set behavior;
- edge cases;
- computational implementation;
- testing and validation;
- performance considerations;
- numerical considerations;
- programming connections;
- database and hashing examples;
- security implications;
- proof templates;
- integrated examples.
"""
)

print("=" * 80)
print("FUNCTIONS FUNDAMENTALS STUDY SCRIPT COMPLETED")
print("=" * 80)
