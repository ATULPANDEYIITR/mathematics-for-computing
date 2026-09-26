"""
Boolean Functions: Truth Tables, Boolean Function Representation,
Minterms, and Maxterms

This standalone study script progresses from Boolean algebra fundamentals
to canonical minterm/maxterm representations, truth-table generation,
simplification, equivalence checking, and a practical digital-logic example.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


# ============================================================
# 1. BOOLEAN FUNDAMENTALS
# ============================================================

print("=" * 78)
print("BOOLEAN FUNCTIONS: TRUTH TABLES, MINTERMS, AND MAXTERMS")
print("=" * 78)


def boolean_not(value: bool) -> bool:
    """Logical NOT."""
    return not value


def boolean_and(left: bool, right: bool) -> bool:
    """Logical AND."""
    return left and right


def boolean_or(left: bool, right: bool) -> bool:
    """Logical OR."""
    return left or right


def boolean_xor(left: bool, right: bool) -> bool:
    """Logical exclusive OR."""
    return left != right


def boolean_xnor(left: bool, right: bool) -> bool:
    """Logical equivalence: true when both inputs are equal."""
    return left == right


print("\n1. BASIC BOOLEAN OPERATIONS")
for a, b in product([False, True], repeat=2):
    print(
        f"A={int(a)} B={int(b)} | "
        f"NOT A={int(boolean_not(a))} | "
        f"A AND B={int(boolean_and(a, b))} | "
        f"A OR B={int(boolean_or(a, b))} | "
        f"A XOR B={int(boolean_xor(a, b))} | "
        f"A XNOR B={int(boolean_xnor(a, b))}"
    )


# ============================================================
# 2. BOOLEAN FUNCTION CONCEPT
# ============================================================

BooleanFunction = Callable[..., bool]


def majority_function(a: bool, b: bool, c: bool) -> bool:
    """
    Three-input majority function.

    The output is true when at least two inputs are true.
    Algebraically:
        F = AB + AC + BC
    """
    return (a and b) or (a and c) or (b and c)


def parity_function(a: bool, b: bool, c: bool) -> bool:
    """
    Odd-parity function.

    The output is true when an odd number of inputs are true.
    """
    return a ^ b ^ c


print("\n2. EXAMPLE BOOLEAN FUNCTIONS")
for inputs in product([False, True], repeat=3):
    a, b, c = inputs
    print(
        f"A={int(a)} B={int(b)} C={int(c)} | "
        f"MAJORITY={int(majority_function(a, b, c))} | "
        f"PARITY={int(parity_function(a, b, c))}"
    )


# ============================================================
# 3. TRUTH TABLE GENERATION
# ============================================================

@dataclass(frozen=True)
class TruthTable:
    variables: tuple[str, ...]
    rows: tuple[tuple[int, ...], ...]
    outputs: tuple[int, ...]

    @property
    def variable_count(self) -> int:
        return len(self.variables)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def print_table(self, title: str = "Truth Table") -> None:
        """Display the truth table in a readable form."""
        print(f"\n{title}")
        print("-" * 78)

        header = " | ".join(self.variables) + " | F"
        print(header)
        print("-" * len(header))

        for inputs, output in zip(self.rows, self.outputs):
            input_text = " | ".join(str(value) for value in inputs)
            print(f"{input_text} | {output}")


def generate_truth_table(
    variables: Sequence[str],
    function: Callable[..., bool],
) -> TruthTable:
    """
    Generate every possible input combination.

    For n Boolean variables there are exactly 2^n combinations.
    The ordering used here is binary counting, with the first variable
    treated as the most significant bit.
    """
    variable_tuple = tuple(variables)
    rows = []
    outputs = []

    for combination in product([0, 1], repeat=len(variable_tuple)):
        rows.append(tuple(combination))
        result = function(*[bool(value) for value in combination])
        outputs.append(int(bool(result)))

    return TruthTable(
        variables=variable_tuple,
        rows=tuple(rows),
        outputs=tuple(outputs),
    )


majority_table = generate_truth_table(
    ["A", "B", "C"],
    majority_function,
)
majority_table.print_table("Majority Function: F = AB + AC + BC")


# ============================================================
# 4. BOOLEAN FUNCTION REPRESENTATIONS
# ============================================================

"""
A Boolean function can be represented in several equivalent ways:

1. Logical expression
2. Truth table
3. Boolean circuit
4. Canonical sum of products
5. Canonical product of sums
6. Set of minterm indices
7. Set of maxterm indices
8. Binary output vector

For n variables:
    Number of possible input combinations = 2^n
    Number of distinct Boolean functions = 2^(2^n)

For example, with 3 variables:
    8 input combinations
    256 possible Boolean functions
"""

print("\n3. NUMBER OF POSSIBLE INPUTS AND BOOLEAN FUNCTIONS")
for variable_count in range(1, 5):
    rows = 2 ** variable_count
    functions = 2 ** rows
    print(
        f"{variable_count} variable(s): "
        f"{rows} truth-table rows, "
        f"{functions} possible Boolean functions"
    )


# ============================================================
# 5. INDEXING TRUTH-TABLE ROWS
# ============================================================

def binary_index(inputs: Sequence[int]) -> int:
    """
    Convert a Boolean input vector to its decimal row index.

    Example:
        A B C = 1 0 1
        binary 101 = decimal 5
    """
    index = 0
    for bit in inputs:
        if bit not in (0, 1):
            raise ValueError("Boolean inputs must contain only 0 or 1.")
        index = (index << 1) | bit
    return index


print("\n4. BINARY INPUT TO DECIMAL MINTERM INDEX")
examples = [
    (0, 0, 0),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 1),
]

for example in examples:
    print(f"{example} -> index {binary_index(example)}")


# ============================================================
# 6. MINTERMS
# ============================================================

"""
A minterm is a product/AND term containing every variable exactly once,
either complemented or uncomplemented.

For variables A, B, C:

m0 = A'B'C'
m1 = A'B'C
m2 = A'BC'
m3 = A'BC
m4 = AB'C'
m5 = AB'C
m6 = ABC'
m7 = ABC

A minterm is 1 for exactly one row of the truth table.

Canonical Sum of Products (SOP):
    F = Σm(indices)

If F=1 at rows 1, 3, 5, and 7:
    F = Σm(1,3,5,7)
"""


def minterm_expression(
    variables: Sequence[str],
    index: int,
) -> str:
    """Build the symbolic minterm corresponding to a row index."""
    variable_count = len(variables)

    if index < 0 or index >= 2 ** variable_count:
        raise ValueError("Minterm index is outside the valid range.")

    binary = format(index, f"0{variable_count}b")
    parts = []

    for variable, bit in zip(variables, binary):
        # A 1 means the variable appears normally.
        # A 0 means the variable is complemented.
        parts.append(variable if bit == "1" else f"{variable}'")

    return "".join(parts)


def maxterm_expression(
    variables: Sequence[str],
    index: int,
) -> str:
    """Build the symbolic maxterm corresponding to a row index."""
    variable_count = len(variables)

    if index < 0 or index >= 2 ** variable_count:
        raise ValueError("Maxterm index is outside the valid range.")

    binary = format(index, f"0{variable_count}b")
    parts = []

    for variable, bit in zip(variables, binary):
        # A 0 means the variable appears normally in the OR term.
        # A 1 means the variable is complemented.
        parts.append(variable if bit == "0" else f"{variable}'")

    return "(" + " + ".join(parts) + ")"


print("\n5. ALL THREE-VARIABLE MINTERMS")
for index in range(8):
    print(f"m{index} = {minterm_expression(['A', 'B', 'C'], index)}")


# ============================================================
# 7. MAXTERMS
# ============================================================

"""
A maxterm is a sum/OR term containing every variable exactly once.

For A, B, C:

M0 = (A + B + C)
M1 = (A + B + C')
M2 = (A + B' + C)
M3 = (A + B' + C')
M4 = (A' + B + C)
M5 = (A' + B + C')
M6 = (A' + B' + C)
M7 = (A' + B' + C')

A maxterm is 0 for exactly one row.

Canonical Product of Sums (POS):
    F = ΠM(indices)

The maxterm indices normally identify the rows where F = 0.
"""


print("\n6. ALL THREE-VARIABLE MAXTERMS")
for index in range(8):
    print(f"M{index} = {maxterm_expression(['A', 'B', 'C'], index)}")


# ============================================================
# 8. EXTRACT MINTERMS AND MAXTERMS FROM A TRUTH TABLE
# ============================================================

def truth_table_indices(
    table: TruthTable,
) -> tuple[list[int], list[int]]:
    """
    Return:
        minterm indices = rows where F=1
        maxterm indices = rows where F=0
    """
    minterms = []
    maxterms = []

    for inputs, output in zip(table.rows, table.outputs):
        index = binary_index(inputs)

        if output == 1:
            minterms.append(index)
        else:
            maxterms.append(index)

    return minterms, maxterms


def canonical_sop(
    variables: Sequence[str],
    minterms: Iterable[int],
) -> str:
    """Create a canonical sum-of-products expression."""
    indices = list(minterms)

    if not indices:
        return "0"

    if len(indices) == 2 ** len(variables):
        return "1"

    terms = [
        minterm_expression(variables, index)
        for index in indices
    ]
    return " + ".join(terms)


def canonical_pos(
    variables: Sequence[str],
    maxterms: Iterable[int],
) -> str:
    """Create a canonical product-of-sums expression."""
    indices = list(maxterms)

    if not indices:
        return "1"

    if len(indices) == 2 ** len(variables):
        return "0"

    terms = [
        maxterm_expression(variables, index)
        for index in indices
    ]
    return "".join(terms)


minterms, maxterms = truth_table_indices(majority_table)

print("\n7. CANONICAL REPRESENTATIONS OF THE MAJORITY FUNCTION")
print(f"Minterm indices: {minterms}")
print(f"Maxterm indices: {maxterms}")
print(f"SOP: {canonical_sop(majority_table.variables, minterms)}")
print(f"POS: {canonical_pos(majority_table.variables, maxterms)}")


# ============================================================
# 9. VERIFY MINTERM UNIQUENESS
# ============================================================

def evaluate_minterm(
    inputs: Sequence[int],
    target_index: int,
) -> int:
    """
    Evaluate one minterm.

    Exactly one input combination can make a given minterm equal 1.
    """
    return int(binary_index(inputs) == target_index)


def evaluate_maxterm(
    inputs: Sequence[int],
    target_index: int,
) -> int:
    """
    Evaluate one maxterm.

    Exactly one input combination can make a given maxterm equal 0.
    """
    return int(binary_index(inputs) != target_index)


print("\n8. MINTERM AND MAXTERM BEHAVIOR")
for index in range(8):
    minterm_values = [
        evaluate_minterm(inputs, index)
        for inputs in product([0, 1], repeat=3)
    ]
    maxterm_values = [
        evaluate_maxterm(inputs, index)
        for inputs in product([0, 1], repeat=3)
    ]

    print(
        f"Index {index}: "
        f"minterm ones={sum(minterm_values)}, "
        f"maxterm zeros={maxterm_values.count(0)}"
    )


# ============================================================
# 10. CANONICAL SOP/POS EVALUATORS
# ============================================================

def evaluate_sop_from_minterms(
    inputs: Sequence[int],
    minterms: Iterable[int],
) -> int:
    """Evaluate a canonical SOP represented by minterm indices."""
    target_indices = set(minterms)
    return int(binary_index(inputs) in target_indices)


def evaluate_pos_from_maxterms(
    inputs: Sequence[int],
    maxterms: Iterable[int],
) -> int:
    """Evaluate a canonical POS represented by maxterm indices."""
    target_indices = set(maxterms)

    # A POS is zero exactly at its maxterm indices.
    return int(binary_index(inputs) not in target_indices)


print("\n9. VERIFYING SOP AND POS REPRESENTATIONS")

for inputs in product([0, 1], repeat=3):
    sop_value = evaluate_sop_from_minterms(inputs, minterms)
    pos_value = evaluate_pos_from_maxterms(inputs, maxterms)
    direct_value = majority_function(*[bool(x) for x in inputs])

    assert sop_value == int(direct_value)
    assert pos_value == int(direct_value)

print("Canonical SOP and canonical POS both match the original function.")


# ============================================================
# 11. STANDARD BOOLEAN IDENTITIES
# ============================================================

print("\n10. IMPORTANT BOOLEAN IDENTITIES")

identity_examples = [
    ("Identity: A + 0 = A", lambda a: (a or False) == a),
    ("Null: A + 1 = 1", lambda a: (a or True) is True),
    ("Identity: A·1 = A", lambda a: (a and True) == a),
    ("Null: A·0 = 0", lambda a: (a and False) is False),
    ("Idempotent: A + A = A", lambda a: (a or a) == a),
    ("Idempotent: A·A = A", lambda a: (a and a) == a),
    ("Complement: A + A' = 1", lambda a: (a or not a) is True),
    ("Complement: A·A' = 0", lambda a: (a and not a) is False),
]

for description, identity in identity_examples:
    assert all(identity(value) for value in [False, True])
    print(f"PASS: {description}")


# ============================================================
# 12. DE MORGAN'S LAWS
# ============================================================

print("\n11. DE MORGAN'S LAWS")

for a, b in product([False, True], repeat=2):
    first_law_left = not (a and b)
    first_law_right = (not a) or (not b)

    second_law_left = not (a or b)
    second_law_right = (not a) and (not b)

    assert first_law_left == first_law_right
    assert second_law_left == second_law_right

print("NOT(A AND B) = (NOT A) OR (NOT B)")
print("NOT(A OR B) = (NOT A) AND (NOT B)")
print("Both laws verified for all four two-input combinations.")


# ============================================================
# 13. FUNCTION EQUIVALENCE
# ============================================================

def are_equivalent(
    variables: Sequence[str],
    first: Callable[..., bool],
    second: Callable[..., bool],
) -> bool:
    """Check functional equivalence by exhaustive truth-table testing."""
    for inputs in product([0, 1], repeat=len(variables)):
        first_value = bool(first(*[bool(x) for x in inputs]))
        second_value = bool(second(*[bool(x) for x in inputs]))

        if first_value != second_value:
            return False

    return True


print("\n12. FUNCTION EQUIVALENCE")

expression_one = lambda a, b, c: (a and b) or (a and c) or (b and c)
expression_two = lambda a, b, c: a and (b or c) or (b and c)

print(
    "AB + AC + BC equivalent to A(B+C)+BC:",
    are_equivalent(["A", "B", "C"], expression_one, expression_two),
)


# ============================================================
# 14. BOOLEAN FUNCTION FROM A SPECIFIC MINTERM SET
# ============================================================

def function_from_minterms(
    minterm_indices: Iterable[int],
    variable_count: int,
) -> Callable[..., bool]:
    """
    Construct a Boolean function from its minterm set.

    This is a direct truth-table implementation rather than a symbolic
    algebra simplifier.
    """
    indices = frozenset(minterm_indices)
    maximum_index = 2 ** variable_count - 1

    if any(index < 0 or index > maximum_index for index in indices):
        raise ValueError("A minterm index is outside the valid range.")

    def generated_function(*values: bool) -> bool:
        if len(values) != variable_count:
            raise ValueError(
                f"Expected {variable_count} variables, got {len(values)}."
            )

        bits = tuple(int(bool(value)) for value in values)
        return binary_index(bits) in indices

    return generated_function


custom_function = function_from_minterms([1, 2, 5, 7], 3)
custom_table = generate_truth_table(["A", "B", "C"], custom_function)
custom_table.print_table("Function F = Σm(1,2,5,7)")

custom_minterms, custom_maxterms = truth_table_indices(custom_table)

print(f"Canonical SOP: {canonical_sop(custom_table.variables, custom_minterms)}")
print(f"Canonical POS: {canonical_pos(custom_table.variables, custom_maxterms)}")


# ============================================================
# 15. DON'T-CARE CONDITIONS
# ============================================================

"""
A don't-care condition represents an input combination whose output is
not constrained by the specification.

Don't-care values are commonly represented by X.

During simplification, a don't-care may be treated as either 0 or 1 if
that produces a simpler implementation. It is not automatically a 1.

This script represents:
    ON-set      = rows where F must be 1
    OFF-set     = rows where F must be 0
    DC-set      = rows where either value is acceptable.
"""

@dataclass(frozen=True)
class BooleanSpecification:
    variable_count: int
    on_set: frozenset[int]
    off_set: frozenset[int]
    dont_care_set: frozenset[int]

    def validate(self) -> None:
        valid_indices = set(range(2 ** self.variable_count))

        if not self.on_set <= valid_indices:
            raise ValueError("ON-set contains an invalid row.")

        if not self.off_set <= valid_indices:
            raise ValueError("OFF-set contains an invalid row.")

        if not self.dont_care_set <= valid_indices:
            raise ValueError("Don't-care set contains an invalid row.")

        if self.on_set & self.off_set:
            raise ValueError("ON-set and OFF-set overlap.")

        if self.on_set & self.dont_care_set:
            raise ValueError("ON-set and don't-care set overlap.")

        if self.off_set & self.dont_care_set:
            raise ValueError("OFF-set and don't-care set overlap.")


specification = BooleanSpecification(
    variable_count=3,
    on_set=frozenset({1, 3, 5}),
    off_set=frozenset({0, 2, 7}),
    dont_care_set=frozenset({4, 6}),
)

specification.validate()

print("\n13. DON'T-CARE SPECIFICATION")
print(f"ON-set: {sorted(specification.on_set)}")
print(f"OFF-set: {sorted(specification.off_set)}")
print(f"Don't-care set: {sorted(specification.dont_care_set)}")


# ============================================================
# 16. K-MAP-STYLE ADJACENCY
# ============================================================

def hamming_distance(left: int, right: int, variable_count: int) -> int:
    """
    Count differing Boolean bits.

    Two minterms with Hamming distance 1 differ in exactly one variable.
    This is a key property used by Karnaugh maps and Quine-McCluskey.
    """
    left_binary = format(left, f"0{variable_count}b")
    right_binary = format(right, f"0{variable_count}b")

    return sum(a != b for a, b in zip(left_binary, right_binary))


def adjacent_minterms(
    index: int,
    variable_count: int,
) -> list[int]:
    """Return minterm indices one bit away from index."""
    return [
        candidate
        for candidate in range(2 ** variable_count)
        if candidate != index
        and hamming_distance(index, candidate, variable_count) == 1
    ]


print("\n14. MINTERM ADJACENCY")
for index in range(8):
    print(f"m{index}: {adjacent_minterms(index, 3)}")


# ============================================================
# 17. QUINE-MCCLUSKEY-STYLE GROUPING
# ============================================================

"""
The following implementation demonstrates the core grouping mechanism
behind the Quine-McCluskey minimization approach.

A pattern such as:
    1-0-
means:
    first variable = 1
    second variable = don't care
    third variable = 0
    fourth variable = don't care

Only compatible implicants can be combined.
"""


@dataclass(frozen=True)
class Implicant:
    pattern: str
    covered_minterms: frozenset[int]

    @property
    def ones_count(self) -> int:
        return self.pattern.count("1")

    def combine(self, other: "Implicant") -> "Implicant | None":
        """
        Combine two implicants when they differ in exactly one fixed bit.
        """
        if len(self.pattern) != len(other.pattern):
            return None

        difference_positions = []

        for position, (left, right) in enumerate(
            zip(self.pattern, other.pattern)
        ):
            if left != right:
                # A '-' cannot be directly combined with a fixed symbol
                # by this simple one-step rule.
                if left == "-" or right == "-":
                    return None
                difference_positions.append(position)

        if len(difference_positions) != 1:
            return None

        position = difference_positions[0]
        combined_pattern = (
            self.pattern[:position]
            + "-"
            + self.pattern[position + 1:]
        )

        return Implicant(
            pattern=combined_pattern,
            covered_minterms=(
                self.covered_minterms | other.covered_minterms
            ),
        )


def initial_implicants(
    minterms: Iterable[int],
    variable_count: int,
) -> list[Implicant]:
    return [
        Implicant(
            pattern=format(index, f"0{variable_count}b"),
            covered_minterms=frozenset({index}),
        )
        for index in sorted(set(minterms))
    ]


def one_step_combine(
    implicants: Sequence[Implicant],
) -> tuple[list[Implicant], list[Implicant]]:
    """
    Perform one round of implicant combination.

    Returns:
        combined implicants
        implicants that could not be combined in this round
    """
    combined_patterns: dict[str, Implicant] = {}
    combined_indices: set[int] = set()

    for i, first in enumerate(implicants):
        for j in range(i + 1, len(implicants)):
            second = implicants[j]
            combined = first.combine(second)

            if combined is not None:
                combined_patterns[combined.pattern] = combined
                combined_indices.update([i, j])

    leftovers = [
        implicant
        for index, implicant in enumerate(implicants)
        if index not in combined_indices
    ]

    return list(combined_patterns.values()), leftovers


initial = initial_implicants([1, 3, 5, 7], 3)
combined, leftovers = one_step_combine(initial)

print("\n15. ONE QUINE-MCCLUSKEY COMBINATION ROUND")
for implicant in combined:
    print(
        f"{implicant.pattern} covers "
        f"{sorted(implicant.covered_minterms)}"
    )

print("Uncombined:")
for implicant in leftovers:
    print(
        f"{implicant.pattern} covers "
        f"{sorted(implicant.covered_minterms)}"
    )


# ============================================================
# 18. PRACTICAL DIGITAL LOGIC EXAMPLE
# ============================================================

"""
Example: a three-input safety controller.

Inputs:
    D = door closed
    A = authorization valid
    E = emergency override

Output:
    S = system may activate

Policy:
    - Normal activation requires D AND A.
    - Emergency override permits activation when E is true.

Therefore:
    S = DA + E

This is a Boolean function used to model a simple control decision.
"""

def safety_controller(door_closed: bool, authorized: bool, emergency: bool) -> bool:
    return (door_closed and authorized) or emergency


safety_table = generate_truth_table(
    ["D", "A", "E"],
    safety_controller,
)

safety_table.print_table("Safety Controller: S = DA + E")

safety_minterms, safety_maxterms = truth_table_indices(safety_table)

print("\n16. SAFETY CONTROLLER REPRESENTATION")
print(f"S = Σm({','.join(map(str, safety_minterms))})")
print(f"S = ΠM({','.join(map(str, safety_maxterms))})")
print(
    "Canonical SOP:",
    canonical_sop(["D", "A", "E"], safety_minterms),
)
print(
    "Canonical POS:",
    canonical_pos(["D", "A", "E"], safety_maxterms),
)


# ============================================================
# 19. EDGE CASES
# ============================================================

print("\n17. EDGE CASES")

constant_zero = generate_truth_table(["A", "B"], lambda a, b: False)
constant_one = generate_truth_table(["A", "B"], lambda a, b: True)

zero_minterms, zero_maxterms = truth_table_indices(constant_zero)
one_minterms, one_maxterms = truth_table_indices(constant_one)

print(
    "Constant 0:",
    f"minterms={zero_minterms}, maxterms={zero_maxterms}",
)
print(
    "Constant 1:",
    f"minterms={one_minterms}, maxterms={one_maxterms}",
)

assert canonical_sop(["A", "B"], zero_minterms) == "0"
assert canonical_pos(["A", "B"], zero_maxterms) == "0"

assert canonical_sop(["A", "B"], one_minterms) == "1"
assert canonical_pos(["A", "B"], one_maxterms) == "1"


# ============================================================
# 20. VALIDATION AND COMMON ERRORS
# ============================================================

print("\n18. VALIDATION EXAMPLES")

try:
    binary_index([1, 0, 2])
except ValueError as error:
    print("Caught invalid Boolean input:", error)

try:
    minterm_expression(["A", "B"], 4)
except ValueError as error:
    print("Caught invalid minterm index:", error)

try:
    invalid_specification = BooleanSpecification(
        variable_count=2,
        on_set=frozenset({1}),
        off_set=frozenset({1}),
        dont_care_set=frozenset(),
    )
    invalid_specification.validate()
except ValueError as error:
    print("Caught overlapping specification:", error)


# ============================================================
# 21. PERFORMANCE CONSIDERATIONS
# ============================================================

def exhaustive_truth_table_cost(variable_count: int) -> tuple[int, int]:
    """
    Return:
        number of rows
        number of possible Boolean functions

    The second value grows doubly exponentially:
        2^(2^n)
    """
    rows = 2 ** variable_count
    function_count = 2 ** rows
    return rows, function_count


print("\n19. GROWTH OF BOOLEAN FUNCTION SPACE")
for variable_count in range(1, 6):
    rows, function_count = exhaustive_truth_table_cost(variable_count)
    print(
        f"n={variable_count}: "
        f"rows={rows:,}, "
        f"possible functions={function_count:,}"
    )


# ============================================================
# 22. EXHAUSTIVE TESTING OF AN IMPLEMENTATION
# ============================================================

def test_majority_function() -> None:
    """Exhaustively test the majority function."""
    expected_outputs = {
        (0, 0, 0): 0,
        (0, 0, 1): 0,
        (0, 1, 0): 0,
        (0, 1, 1): 1,
        (1, 0, 0): 0,
        (1, 0, 1): 1,
        (1, 1, 0): 1,
        (1, 1, 1): 1,
    }

    for inputs, expected in expected_outputs.items():
        actual = int(majority_function(*[bool(x) for x in inputs]))
        assert actual == expected, (
            f"Expected {expected} for {inputs}, got {actual}"
        )


test_majority_function()
print("\n20. TESTING")
print("Majority-function exhaustive tests: PASS")


# ============================================================
# 23. BOOLEAN FUNCTION COMPARISON
# ============================================================

def compare_functions(
    variables: Sequence[str],
    named_functions: dict[str, Callable[..., bool]],
) -> None:
    """Compare several Boolean functions row by row."""
    print("\n21. FUNCTION COMPARISON")

    names = list(named_functions)
    print(" | ".join(list(variables) + names))
    print("-" * (len(" | ".join(list(variables) + names))))

    for inputs in product([0, 1], repeat=len(variables)):
        values = [
            int(function(*[bool(x) for x in inputs]))
            for function in named_functions.values()
        ]

        print(
            " | ".join(
                map(str, inputs + tuple(values))
            )
        )


compare_functions(
    ["A", "B", "C"],
    {
        "MAJ": majority_function,
        "PARITY": parity_function,
        "XOR_AB": lambda a, b, c: a ^ b,
    },
)


# ============================================================
# 24. IMPORTANT DISTINCTION: MINTERM VS MAXTERM
# ============================================================

print("\n22. MINTERM VS MAXTERM")

comparison = [
    ("Minterm", "AND/product term", "1 for exactly one row", "SOP", "Σm"),
    ("Maxterm", "OR/sum term", "0 for exactly one row", "POS", "ΠM"),
]

for row in comparison:
    print(
        f"{row[0]:10} | {row[1]:20} | "
        f"{row[2]:26} | {row[3]:3} | {row[4]}"
    )


# ============================================================
# 25. FINAL SELF-CHECK
# ============================================================

def self_check() -> None:
    """Run consistency checks across the complete implementation."""

    variables = ["A", "B", "C"]

    table = generate_truth_table(
        variables,
        lambda a, b, c: (a and b) or (not c),
    )

    minterm_indices, maxterm_indices = truth_table_indices(table)

    for inputs, expected in zip(table.rows, table.outputs):
        sop_result = evaluate_sop_from_minterms(
            inputs,
            minterm_indices,
        )
        pos_result = evaluate_pos_from_maxterms(
            inputs,
            maxterm_indices,
        )

        assert sop_result == expected
        assert pos_result == expected

    # Every row belongs to exactly one of the ON-set or OFF-set
    # when there are no don't-care values.
    assert set(minterm_indices).isdisjoint(maxterm_indices)
    assert len(minterm_indices) + len(maxterm_indices) == 8


self_check()

print("\n23. FINAL SELF-CHECK")
print("All truth-table, minterm, maxterm, SOP, and POS consistency checks passed.")
print("\nStudy script execution completed successfully.")
