"""
NUMBER SYSTEM
=============

A detailed, self-contained study program covering number systems from
basic to advanced concepts.

Topics covered
--------------
1. What a number system is
2. Positional and non-positional number systems
3. Base/radix
4. Decimal number system
5. Binary number system
6. Octal number system
7. Hexadecimal number system
8. Digits and positional weights
9. Converting integers between bases
10. Converting fractions between bases
11. Repeated division method
12. Repeated multiplication method
13. Binary <-> octal conversion
14. Binary <-> hexadecimal conversion
15. Decimal <-> binary conversion
16. Decimal <-> octal conversion
17. Decimal <-> hexadecimal conversion
18. Mixed integer/fractional representations
19. Arithmetic in different bases
20. Binary addition
21. Binary subtraction
22. Binary multiplication
23. Binary division
24. Carry and borrow
25. Complements
26. 1's complement
27. 2's complement
28. 8's and 9's complements
29. 15's and 16's complements
30. Signed magnitude
31. Sign-magnitude representation
32. One's complement representation
33. Two's complement representation
34. Range of signed and unsigned integers
35. Overflow and underflow
36. Bit width
37. Fixed-width binary arithmetic
38. Sign extension
39. Zero extension
40. Truncation
41. Bitwise interpretation
42. ASCII/Unicode and hexadecimal representation
43. Binary representation of real numbers
44. Fixed-point representation
45. Floating-point representation
46. IEEE-754 concepts
47. Normalized numbers
48. Subnormal numbers
49. Infinity
50. NaN
51. Precision and rounding
52. Exact versus approximate representation
53. Arbitrary bases
54. Balanced number systems
55. Modular arithmetic
56. Number systems in computing
57. Common mistakes and edge cases
58. Practice-oriented demonstrations
"""

from fractions import Fraction
import math
import struct


# ============================================================
# 1. INTRODUCTION
# ============================================================

print("=" * 72)
print("NUMBER SYSTEM")
print("=" * 72)

print("""
A number system is a method of representing numerical quantities using
a defined collection of symbols and rules.

The most important concept is the BASE, also called the RADIX.

For example:

    Decimal  -> base 10
    Binary   -> base 2
    Octal    -> base 8
    Hexadecimal -> base 16

In a positional number system, the value of a digit depends on:

    1. The digit itself
    2. Its position
    3. The base of the number system

For example:

    583

means:

    5 * 10^2 + 8 * 10^1 + 3 * 10^0

    = 500 + 80 + 3
    = 583

The same positional principle works in binary, octal, hexadecimal,
and other positional systems.
""")


# ============================================================
# 2. POSITIONAL NUMBER SYSTEM
# ============================================================

print("\n" + "=" * 72)
print("POSITIONAL NUMBER SYSTEM")
print("=" * 72)

print("""
A positional number system assigns a weight to every position.

For a number:

    d3 d2 d1 d0

in base b, its value is:

    d3*b^3 + d2*b^2 + d1*b^1 + d0*b^0

For positions to the right of the radix point:

    d[-1] * b^-1
    d[-2] * b^-2
    d[-3] * b^-3

For example:

    101.101₂

is:

    1*2^2 + 0*2^1 + 1*2^0
    + 1*2^-1 + 0*2^-2 + 1*2^-3

    = 4 + 0 + 1 + 0.5 + 0 + 0.125
    = 5.625
""")


# ============================================================
# 3. COMMON NUMBER SYSTEMS
# ============================================================

print("\n" + "=" * 72)
print("COMMON NUMBER SYSTEMS")
print("=" * 72)

systems = {
    "Decimal": 10,
    "Binary": 2,
    "Octal": 8,
    "Hexadecimal": 16
}

for name, base in systems.items():
    print(f"{name:15} Base = {base}")

print("""
Decimal uses:
    0 1 2 3 4 5 6 7 8 9

Binary uses:
    0 1

Octal uses:
    0 1 2 3 4 5 6 7

Hexadecimal uses:
    0 1 2 3 4 5 6 7 8 9 A B C D E F

Hexadecimal values:

    A = 10
    B = 11
    C = 12
    D = 13
    E = 14
    F = 15
""")


# ============================================================
# 4. GENERAL BASE CONVERSION TO DECIMAL
# ============================================================

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def validate_number(number, base):
    """
    Validate that every digit in a positional number is legal.
    Supports an optional fractional part.
    """
    number = number.upper()

    if number.count(".") > 1:
        raise ValueError("A number can contain at most one radix point.")

    integer_part, _, fractional_part = number.partition(".")

    if integer_part == "":
        integer_part = "0"

    for digit in integer_part + fractional_part:
        if digit not in DIGITS[:base]:
            raise ValueError(
                f"Digit '{digit}' is invalid for base {base}."
            )


def char_to_value(char):
    return DIGITS.index(char.upper())


def value_to_char(value):
    if value < 0 or value >= len(DIGITS):
        raise ValueError("Digit value outside supported range.")
    return DIGITS[value]


def base_to_decimal(number, base):
    """
    Convert a number from an arbitrary positional base to Decimal.

    Example:
        base_to_decimal("1011", 2) -> 11
        base_to_decimal("1A", 16)  -> 26
        base_to_decimal("101.101", 2) -> 5.625
    """
    number = number.upper()
    validate_number(number, base)

    integer_part, _, fractional_part = number.partition(".")

    value = 0

    for digit in integer_part:
        value = value * base + char_to_value(digit)

    fraction_value = Fraction(0, 1)

    for position, digit in enumerate(fractional_part, start=1):
        fraction_value += Fraction(
            char_to_value(digit),
            base ** position
        )

    return Fraction(value, 1) + fraction_value


print("\nGENERAL BASE -> DECIMAL EXAMPLES")

examples = [
    ("1011", 2),
    ("17", 8),
    ("1A", 16),
    ("123", 10),
    ("101.101", 2),
    ("7.4", 8),
    ("A.C", 16),
]

for number, base in examples:
    print(
        f"{number} (base {base}) = "
        f"{base_to_decimal(number, base)} (decimal)"
    )


# ============================================================
# 5. DECIMAL INTEGER TO ANY BASE
# ============================================================

def decimal_integer_to_base(number, base):
    """
    Convert a non-negative integer from decimal to any base up to 36.

    Repeated division is used.

    Example:

        45 / 2 = 22 remainder 1
        22 / 2 = 11 remainder 0
        11 / 2 = 5  remainder 1
        5  / 2 = 2  remainder 1
        2  / 2 = 1  remainder 0
        1  / 2 = 0  remainder 1

    Reading the remainders from bottom to top:

        101101₂
    """
    if base < 2 or base > 36:
        raise ValueError("Base must be between 2 and 36.")

    if number == 0:
        return "0"

    if number < 0:
        return "-" + decimal_integer_to_base(-number, base)

    digits = []

    while number > 0:
        remainder = number % base
        digits.append(value_to_char(remainder))
        number //= base

    return "".join(reversed(digits))


print("\nDECIMAL INTEGER CONVERSION")

for number in [10, 25, 42, 100, 255, 1024]:
    print(f"\nDecimal: {number}")
    print("Binary:      ", decimal_integer_to_base(number, 2))
    print("Octal:       ", decimal_integer_to_base(number, 8))
    print("Hexadecimal: ", decimal_integer_to_base(number, 16))


# ============================================================
# 6. SHOW REPEATED DIVISION PROCESS
# ============================================================

def show_repeated_division(number, base):
    """
    Display the complete repeated division process.
    """
    if number < 0:
        number = abs(number)

    print(f"\nConverting {number} from decimal to base {base}")

    if number == 0:
        print("0")
        return

    while number > 0:
        quotient, remainder = divmod(number, base)

        print(
            f"{number:>8} ÷ {base} = "
            f"{quotient:>8} remainder {remainder}"
        )

        number = quotient


show_repeated_division(156, 2)
show_repeated_division(156, 8)
show_repeated_division(156, 16)


# ============================================================
# 7. DECIMAL FRACTION TO ANY BASE
# ============================================================

def decimal_fraction_to_base(value, base, precision=12):
    """
    Convert a decimal Fraction or floating-point value to another base.

    Fractional conversion uses repeated multiplication.

    Example:

        0.625 * 2 = 1.25 -> digit 1
        0.25  * 2 = 0.5  -> digit 0
        0.5   * 2 = 1.0  -> digit 1

    Therefore:

        0.625₁₀ = 0.101₂
    """
    if not 0 <= value < 1:
        raise ValueError("Value must be in [0, 1).")

    if not isinstance(value, Fraction):
        value = Fraction(value)

    result = []

    for _ in range(precision):
        value *= base
        digit = value.numerator // value.denominator

        result.append(value_to_char(digit))

        value -= digit

        if value == 0:
            break

    return "".join(result)


def decimal_to_base(value, base, precision=12):
    """
    Convert a decimal number, including a fractional component,
    into another base.
    """
    if isinstance(value, int):
        return decimal_integer_to_base(value, base)

    value = Fraction(value)

    negative = value < 0

    if negative:
        value = -value

    integer_part = value.numerator // value.denominator
    fractional_part = value - integer_part

    integer_string = decimal_integer_to_base(integer_part, base)

    if fractional_part == 0:
        result = integer_string
    else:
        fraction_string = decimal_fraction_to_base(
            fractional_part,
            base,
            precision
        )
        result = integer_string + "." + fraction_string

    return "-" + result if negative else result


print("\nDECIMAL FRACTION CONVERSION")

fraction_examples = [
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(1, 8),
    Fraction(1, 10),
    Fraction(13, 16),
]

for value in fraction_examples:
    print(
        f"{value} decimal = "
        f"{decimal_to_base(value, 2, 16)} binary"
    )


# ============================================================
# 8. SHOW REPEATED MULTIPLICATION PROCESS
# ============================================================

def show_repeated_multiplication(fraction, base, steps=12):
    """
    Display the repeated multiplication process for a fraction.
    """
    if not 0 <= fraction < 1:
        raise ValueError("Fraction must be between 0 and 1.")

    fraction = Fraction(fraction)

    print(
        f"\nConverting {fraction} from decimal "
        f"fraction to base {base}"
    )

    for i in range(steps):
        fraction *= base

        digit = fraction.numerator // fraction.denominator

        print(
            f"Step {i + 1:>2}: "
            f"{fraction} -> digit {digit} "
            f"({value_to_char(digit)})"
        )

        fraction -= digit

        if fraction == 0:
            break


show_repeated_multiplication(Fraction(5, 8), 2)
show_repeated_multiplication(Fraction(1, 10), 2)


# ============================================================
# 9. WHY SOME DECIMAL FRACTIONS NEVER TERMINATE IN BINARY
# ============================================================

print("\n" + "=" * 72)
print("TERMINATING AND NON-TERMINATING FRACTIONS")
print("=" * 72)

print("""
A fraction terminates in base b when, after reduction, its denominator
contains no prime factors other than the prime factors of b.

For binary:

    base = 2

Therefore a reduced fraction terminates in binary only when its
denominator is of the form:

    2^n

Examples:

    1/2  -> 0.1₂
    1/4  -> 0.01₂
    3/8  -> 0.011₂

But:

    1/10

has denominator:

    10 = 2 * 5

The factor 5 is not a factor of base 2, so its binary representation
does not terminate.

This distinction is important when understanding floating-point
precision in computers.
""")


# ============================================================
# 10. BINARY, OCTAL AND HEXADECIMAL GROUPING
# ============================================================

print("\n" + "=" * 72)
print("BINARY GROUPING")
print("=" * 72)

print("""
Binary and octal are closely related because:

    8 = 2^3

Therefore every octal digit corresponds to exactly three binary bits.

Binary -> Octal:

    101 110 011
     5   6   3

    = 563₈

Similarly:

    16 = 2^4

Therefore every hexadecimal digit corresponds to exactly four binary
bits.

Binary -> Hexadecimal:

    1010 1111 0011
      A    F    3

    = AF3₁₆
""")


BINARY_TO_OCTAL = {
    "000": "0",
    "001": "1",
    "010": "2",
    "011": "3",
    "100": "4",
    "101": "5",
    "110": "6",
    "111": "7",
}

BINARY_TO_HEX = {
    format(i, "04b"): value_to_char(i)
    for i in range(16)
}


def binary_to_octal(binary):
    binary = binary.replace("_", "")

    if "." in binary:
        integer, fraction = binary.split(".")

        while len(integer) % 3 != 0:
            integer = "0" + integer

        while len(fraction) % 3 != 0:
            fraction += "0"

        integer_result = "".join(
            BINARY_TO_OCTAL[integer[i:i + 3]]
            for i in range(0, len(integer), 3)
        )

        fraction_result = "".join(
            BINARY_TO_OCTAL[fraction[i:i + 3]]
            for i in range(0, len(fraction), 3)
        )

        return integer_result + "." + fraction_result

    while len(binary) % 3 != 0:
        binary = "0" + binary

    return "".join(
        BINARY_TO_OCTAL[binary[i:i + 3]]
        for i in range(0, len(binary), 3)
    )


def binary_to_hex(binary):
    binary = binary.replace("_", "")

    if "." in binary:
        integer, fraction = binary.split(".")

        while len(integer) % 4 != 0:
            integer = "0" + integer

        while len(fraction) % 4 != 0:
            fraction += "0"

        integer_result = "".join(
            BINARY_TO_HEX[integer[i:i + 4]]
            for i in range(0, len(integer), 4)
        )

        fraction_result = "".join(
            BINARY_TO_HEX[fraction[i:i + 4]]
            for i in range(0, len(fraction), 4)
        )

        return integer_result + "." + fraction_result

    while len(binary) % 4 != 0:
        binary = "0" + binary

    return "".join(
        BINARY_TO_HEX[binary[i:i + 4]]
        for i in range(0, len(binary), 4)
    )


print("\nBinary 101110011 -> Octal:")
print(binary_to_octal("101110011"))

print("\nBinary 101011110011 -> Hexadecimal:")
print(binary_to_hex("101011110011"))


# ============================================================
# 11. OCTAL/HEXADECIMAL TO BINARY
# ============================================================

OCTAL_TO_BINARY = {
    value: key
    for key, value in BINARY_TO_OCTAL.items()
}

HEX_TO_BINARY = {
    value: key
    for key, value in BINARY_TO_HEX.items()
}


def octal_to_binary(octal):
    if "." in octal:
        integer, fraction = octal.split(".")

        result_integer = "".join(
            OCTAL_TO_BINARY[digit]
            for digit in integer
        )

        result_fraction = "".join(
            OCTAL_TO_BINARY[digit]
            for digit in fraction
        )

        return result_integer + "." + result_fraction

    return "".join(
        OCTAL_TO_BINARY[digit]
        for digit in octal
    )


def hex_to_binary(hexadecimal):
    hexadecimal = hexadecimal.upper()

    if "." in hexadecimal:
        integer, fraction = hexadecimal.split(".")

        result_integer = "".join(
            HEX_TO_BINARY[digit]
            for digit in integer
        )

        result_fraction = "".join(
            HEX_TO_BINARY[digit]
            for digit in fraction
        )

        return result_integer + "." + result_fraction

    return "".join(
        HEX_TO_BINARY[digit]
        for digit in hexadecimal
    )


print("\nOctal 563 -> Binary:")
print(octal_to_binary("563"))

print("\nHexadecimal AF3 -> Binary:")
print(hex_to_binary("AF3"))


# ============================================================
# 12. BASE CONVERSION THROUGH DECIMAL
# ============================================================

def convert_base(number, from_base, to_base, precision=16):
    """
    General base conversion.

    Example:
        convert_base("101101", 2, 16)
    """
    decimal_value = base_to_decimal(number, from_base)

    integer_part = decimal_value.numerator // decimal_value.denominator
    fraction_part = decimal_value - integer_part

    integer_result = decimal_integer_to_base(
        integer_part,
        to_base
    )

    if fraction_part == 0:
        return integer_result

    fraction_result = decimal_fraction_to_base(
        fraction_part,
        to_base,
        precision
    )

    return integer_result + "." + fraction_result


print("\nGENERAL BASE CONVERSIONS")

print("101101₂ -> Hexadecimal:",
      convert_base("101101", 2, 16))

print("2F₁₆ -> Binary:",
      convert_base("2F", 16, 2))

print("745₈ -> Binary:",
      convert_base("745", 8, 2))

print("745₈ -> Hexadecimal:",
      convert_base("745", 8, 16))


# ============================================================
# 13. RADIX POINT
# ============================================================

print("\n" + "=" * 72)
print("RADIX POINT")
print("=" * 72)

print("""
The decimal point is specifically a radix point.

In decimal:

    123.45

means:

    1*10^2 + 2*10^1 + 3*10^0
    + 4*10^-1 + 5*10^-2

In binary:

    101.11

means:

    1*2^2 + 0*2^1 + 1*2^0
    + 1*2^-1 + 1*2^-2

    = 4 + 0 + 1 + 0.5 + 0.25
    = 5.75
""")

print(
    "101.11 binary =",
    base_to_decimal("101.11", 2),
    "decimal"
)


# ============================================================
# 14. ARITHMETIC IN DIFFERENT BASES
# ============================================================

print("\n" + "=" * 72)
print("ARITHMETIC IN DIFFERENT BASES")
print("=" * 72)

print("""
Arithmetic rules are not fundamentally different between bases.

The important difference is the point at which a carry occurs.

Decimal:

    9 + 1 = 10

Binary:

    1 + 1 = 10

Octal:

    7 + 1 = 10

Hexadecimal:

    F + 1 = 10

The symbol '10' does not always mean decimal ten.

It means:

    1 * base + 0

Therefore:

    10₂ = 2
    10₈ = 8
    10₁₀ = 10
    10₁₆ = 16
""")


# ============================================================
# 15. BINARY ADDITION
# ============================================================

print("\n" + "=" * 72)
print("BINARY ADDITION")
print("=" * 72)

print("""
Binary addition follows four basic cases:

    0 + 0 = 0
    0 + 1 = 1
    1 + 0 = 1
    1 + 1 = 10

The last case produces:

    sum digit = 0
    carry = 1

For three bits:

    1 + 1 + 1 = 11₂

because decimal 3 is binary 11.
""")


def binary_add(a, b):
    """
    Binary addition using integer arithmetic for validation.
    """
    if any(bit not in "01" for bit in a + b):
        raise ValueError("Binary values may contain only 0 and 1.")

    return decimal_integer_to_base(
        int(a, 2) + int(b, 2),
        2
    )


print("1011 + 1101 =", binary_add("1011", "1101"))


# ============================================================
# 16. MANUAL BINARY ADDITION
# ============================================================

def manual_binary_add(a, b):
    """
    Perform binary addition bit by bit.
    """
    if any(bit not in "01" for bit in a + b):
        raise ValueError("Only binary digits are allowed.")

    a = a.zfill(max(len(a), len(b)))
    b = b.zfill(max(len(a), len(b)))

    carry = 0
    result = []

    for x, y in zip(reversed(a), reversed(b)):
        total = int(x) + int(y) + carry

        result.append(str(total % 2))
        carry = total // 2

    if carry:
        result.append("1")

    return "".join(reversed(result))


print("Manual binary addition:")
print("1111 + 0001 =", manual_binary_add("1111", "0001"))


# ============================================================
# 17. BINARY SUBTRACTION
# ============================================================

print("\n" + "=" * 72)
print("BINARY SUBTRACTION")
print("=" * 72)

print("""
Binary subtraction:

    0 - 0 = 0
    1 - 0 = 1
    1 - 1 = 0

For:

    0 - 1

we need to borrow.

In binary, borrowing one unit from the next position gives:

    10₂

which has decimal value 2.

Therefore:

    10₂ - 1₂ = 1₂
""")


def binary_subtract(a, b):
    if int(a, 2) < int(b, 2):
        raise ValueError(
            "This basic unsigned subtraction expects a >= b."
        )

    return decimal_integer_to_base(
        int(a, 2) - int(b, 2),
        2
    )


print("11010 - 00111 =", binary_subtract("11010", "00111"))


# ============================================================
# 18. BINARY MULTIPLICATION
# ============================================================

print("\n" + "=" * 72)
print("BINARY MULTIPLICATION")
print("=" * 72)

print("""
Binary multiplication is particularly simple:

    0 * 0 = 0
    0 * 1 = 0
    1 * 0 = 0
    1 * 1 = 1

Multiplication by a power of two is equivalent to a left shift.

For example:

    1011₂ * 2 = 10110₂

    1011₂ * 4 = 101100₂

provided we are considering an unrestricted integer representation.
""")


def binary_multiply(a, b):
    return decimal_integer_to_base(
        int(a, 2) * int(b, 2),
        2
    )


print("1011 * 110 =", binary_multiply("1011", "110"))


# ============================================================
# 19. BINARY DIVISION
# ============================================================

print("\n" + "=" * 72)
print("BINARY DIVISION")
print("=" * 72)

print("""
Binary division follows the same long-division principle used in
decimal arithmetic.

A useful property is:

    dividing by 2  -> right shift
    multiplying by 2 -> left shift

For unsigned integers:

    11000₂ / 2 = 1100₂
    11000₂ / 4 = 110₂

When division is not exact, the right-shift interpretation corresponds
to integer division where the fractional part is discarded.
""")


def binary_divide(a, b):
    dividend = int(a, 2)
    divisor = int(b, 2)

    if divisor == 0:
        raise ZeroDivisionError("Division by zero.")

    quotient, remainder = divmod(dividend, divisor)

    return (
        decimal_integer_to_base(quotient, 2),
        decimal_integer_to_base(remainder, 2)
    )


quotient, remainder = binary_divide("110101", "101")

print("110101 / 101")
print("Quotient :", quotient)
print("Remainder:", remainder)


# ============================================================
# 20. COMPLEMENTS
# ============================================================

print("\n" + "=" * 72)
print("COMPLEMENTS")
print("=" * 72)

print("""
Complements are extremely important in positional arithmetic and
computer representation.

For base r and an n-digit number:

    (r - 1)'s complement
    = subtract every digit from r - 1

    r's complement
    = (r - 1)'s complement + 1

Examples in decimal:

    9's complement of 123
    = 876

    10's complement of 123
    = 877

Examples in binary:

    1's complement
    = invert every bit

    2's complement
    = 1's complement + 1
""")


def ones_complement(binary):
    if any(bit not in "01" for bit in binary):
        raise ValueError("Invalid binary number.")

    return "".join(
        "1" if bit == "0" else "0"
        for bit in binary
    )


def twos_complement(binary):
    """
    Compute two's complement while retaining the same width.
    """
    inverted = ones_complement(binary)

    result = list(inverted)
    carry = 1

    for i in range(len(result) - 1, -1, -1):
        if carry == 0:
            break

        if result[i] == "0":
            result[i] = "1"
            carry = 0
        else:
            result[i] = "0"

    return "".join(result)


print("Original:       10110010")
print("1's complement:", ones_complement("10110010"))
print("2's complement:", twos_complement("10110010"))


# ============================================================
# 21. DECIMAL COMPLEMENTS
# ============================================================

def nines_complement(number):
    """
    Compute the 9's complement of a non-negative decimal integer.
    """
    if not number.isdigit():
        raise ValueError("Use a non-negative decimal integer.")

    return "".join(
        str(9 - int(digit))
        for digit in number
    )


def tens_complement(number):
    """
    Compute the 10's complement while preserving digit width.
    """
    complement = nines_complement(number)

    result = list(complement)
    carry = 1

    for i in range(len(result) - 1, -1, -1):
        value = int(result[i]) + carry

        if value == 10:
            result[i] = "0"
            carry = 1
        else:
            result[i] = str(value)
            carry = 0
            break

    return "".join(result)


print("\n9's complement of 247:", nines_complement("247"))
print("10's complement of 247:", tens_complement("247"))


# ============================================================
# 22. HEXADECIMAL COMPLEMENTS
# ============================================================

def radix_complement(number, base):
    """
    Compute the base complement for an integer with fixed width.

    For example, in hexadecimal:

        16's complement = 15's complement + 1
    """
    number = number.upper()
    validate_number(number, base)

    max_value = base ** len(number)

    value = int(base_to_decimal(number, base))

    complement = (max_value - value) % max_value

    return decimal_integer_to_base(complement, base).zfill(len(number))


print("\n16's complement of 2A7:")
print(radix_complement("2A7", 16))


# ============================================================
# 23. SUBTRACTION USING TWO'S COMPLEMENT
# ============================================================

print("\n" + "=" * 72)
print("SUBTRACTION USING TWO'S COMPLEMENT")
print("=" * 72)

print("""
Computers can perform subtraction using addition.

To calculate:

    A - B

we can calculate:

    A + two's_complement(B)

The result is interpreted within the selected bit width.

For example using 8 bits:

    A = 13
    B = 5

    A = 00001101
    B = 00000101

    2's complement(B)
      = 11111011

    00001101
  + 11111011
  ------------
    00001000

which represents:

    8
""")


def fixed_width_twos_complement(value, bits):
    """
    Return the two's-complement bit pattern for an integer.
    """
    if bits <= 0:
        raise ValueError("Bit width must be positive.")

    modulus = 2 ** bits
    encoded = value % modulus

    return format(encoded, f"0{bits}b")


def signed_from_twos(binary):
    """
    Interpret a binary bit pattern as a signed two's-complement integer.
    """
    bits = len(binary)
    value = int(binary, 2)

    if binary[0] == "1":
        value -= 2 ** bits

    return value


def twos_complement_subtraction(a, b, bits):
    """
    Compute a-b within a fixed-width two's-complement representation.
    """
    encoded_a = int(fixed_width_twos_complement(a, bits), 2)
    encoded_b = int(fixed_width_twos_complement(b, bits), 2)

    result = (encoded_a - encoded_b) % (2 ** bits)

    binary = format(result, f"0{bits}b")

    return binary, signed_from_twos(binary)


binary_result, signed_result = twos_complement_subtraction(
    13, 5, 8
)

print("13 - 5 using 8-bit two's complement:")
print("Binary :", binary_result)
print("Signed :", signed_result)


# ============================================================
# 24. SIGNED NUMBER REPRESENTATIONS
# ============================================================

print("\n" + "=" * 72)
print("SIGNED NUMBER REPRESENTATIONS")
print("=" * 72)

print("""
There are three historically important fixed-width signed
representations:

1. Sign-magnitude
2. One's complement
3. Two's complement

For an 8-bit value:

    Sign-magnitude:
        first bit = sign
        remaining 7 bits = magnitude

    0xxxxxxx -> positive
    1xxxxxxx -> negative

One's complement:
    negative value = complement of positive representation

Two's complement:
    negative value = complement + 1

Two's complement became the dominant representation for ordinary
signed integers because arithmetic is simpler and it has only one
representation of zero.
""")


def sign_magnitude(value, bits):
    if bits < 2:
        raise ValueError("Need at least two bits.")

    magnitude_bits = bits - 1
    minimum = -(2 ** magnitude_bits - 1)
    maximum = 2 ** magnitude_bits - 1

    if not minimum <= value <= maximum:
        raise OverflowError("Value cannot be represented.")

    sign = "1" if value < 0 else "0"

    magnitude = format(
        abs(value),
        f"0{magnitude_bits}b"
    )

    return sign + magnitude


def ones_complement_signed(value, bits):
    """
    Encode a signed value using one's complement.
    """
    if bits < 2:
        raise ValueError("Need at least two bits.")

    maximum = 2 ** (bits - 1) - 1
    minimum = -maximum

    if not minimum <= value <= maximum:
        raise OverflowError("Value cannot be represented.")

    if value >= 0:
        return format(value, f"0{bits}b")

    positive = format(abs(value), f"0{bits}b")

    return ones_complement(positive)


def twos_complement_signed(value, bits):
    minimum = -(2 ** (bits - 1))
    maximum = 2 ** (bits - 1) - 1

    if not minimum <= value <= maximum:
        raise OverflowError("Value cannot be represented.")

    return fixed_width_twos_complement(value, bits)


value = -13
bits = 8

print(f"\nRepresenting {value} using {bits} bits:")
print("Sign-magnitude :", sign_magnitude(value, bits))
print("1's complement:", ones_complement_signed(value, bits))
print("2's complement:", twos_complement_signed(value, bits))


# ============================================================
# 25. ZERO REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("REPRESENTATION OF ZERO")
print("=" * 72)

print("""
Sign-magnitude has two zeros:

    +0 = 00000000
    -0 = 10000000

One's complement also has two zeros:

    +0 = 00000000
    -0 = 11111111

Two's complement has one zero:

    00000000

This is one of the reasons two's complement is preferred for signed
integer representation.
""")


# ============================================================
# 26. RANGE OF UNSIGNED INTEGERS
# ============================================================

def unsigned_range(bits):
    return 0, 2 ** bits - 1


print("\nUNSIGNED INTEGER RANGES")

for bits in [4, 8, 16, 32, 64]:
    minimum, maximum = unsigned_range(bits)

    print(
        f"{bits:>2}-bit unsigned: "
        f"{minimum} to {maximum}"
    )


# ============================================================
# 27. RANGE OF SIGNED TWO'S COMPLEMENT
# ============================================================

def twos_complement_range(bits):
    return -(2 ** (bits - 1)), 2 ** (bits - 1) - 1


print("\nSIGNED TWO'S COMPLEMENT RANGES")

for bits in [4, 8, 16, 32, 64]:
    minimum, maximum = twos_complement_range(bits)

    print(
        f"{bits:>2}-bit signed: "
        f"{minimum} to {maximum}"
    )


# ============================================================
# 28. WHY 8-BIT SIGNED RANGE IS -128 TO 127
# ============================================================

print("\n" + "=" * 72)
print("WHY TWO'S COMPLEMENT IS ASYMMETRIC")
print("=" * 72)

print("""
For n bits, two's complement has:

    2^n

different bit patterns.

One pattern is zero.

The negative side contains:

    -2^(n-1) through -1

The non-negative side contains:

    0 through 2^(n-1)-1

Therefore:

    minimum = -2^(n-1)
    maximum =  2^(n-1)-1

For 8 bits:

    minimum = -128
    maximum = 127

The extra negative value occurs because zero occupies one of the
non-negative patterns.
""")


# ============================================================
# 29. OVERFLOW
# ============================================================

print("\n" + "=" * 72)
print("OVERFLOW")
print("=" * 72)

print("""
Overflow occurs when a mathematical result cannot be represented
within the available number of bits.

For 8-bit unsigned integers:

    maximum = 255

Therefore:

    255 + 1 = 256

but 256 requires 9 bits:

    100000000₂

If only 8 bits are retained:

    00000000

The mathematical value is 256, but the fixed-width representation
wraps around to zero.

For signed two's complement, overflow occurs when the mathematical
result is outside:

    -2^(n-1) to 2^(n-1)-1
""")


def unsigned_add_fixed(a, b, bits):
    modulus = 2 ** bits

    result = (a + b) % modulus

    overflow = (a + b) >= modulus

    return result, overflow


print("\n8-bit unsigned:")
result, overflow = unsigned_add_fixed(255, 1, 8)

print("255 + 1 =", result)
print("Overflow:", overflow)


# ============================================================
# 30. SIGNED TWO'S COMPLEMENT OVERFLOW
# ============================================================

def signed_add_fixed(a, b, bits):
    minimum, maximum = twos_complement_range(bits)

    mathematical_result = a + b

    encoded = mathematical_result % (2 ** bits)

    represented = signed_from_twos(
        format(encoded, f"0{bits}b")
    )

    overflow = not (
        minimum <= mathematical_result <= maximum
    )

    return represented, overflow


print("\n8-bit signed two's-complement examples:")

for a, b in [(100, 50), (100, 30), (-100, -50)]:
    result, overflow = signed_add_fixed(a, b, 8)

    print(
        f"{a} + {b} = represented {result}, "
        f"overflow = {overflow}"
    )


# ============================================================
# 31. SIGN EXTENSION
# ============================================================

print("\n" + "=" * 72)
print("SIGN EXTENSION")
print("=" * 72)

print("""
When a signed two's-complement number is expanded to a larger width,
the sign bit is replicated.

Example:

    8-bit:
        11111011

This represents -5.

Expanding to 16 bits:

    11111111 11111011

The value remains -5.

The leading 1s preserve the negative value.
""")


def sign_extend(binary, new_width):
    old_width = len(binary)

    if new_width < old_width:
        raise ValueError("New width must be larger.")

    sign = binary[0]

    return sign * (new_width - old_width) + binary


print(
    "11111011 ->",
    sign_extend("11111011", 16)
)


# ============================================================
# 32. ZERO EXTENSION
# ============================================================

print("\n" + "=" * 72)
print("ZERO EXTENSION")
print("=" * 72)

print("""
Unsigned numbers are expanded by adding zeros on the left.

Example:

    10110110

becomes:

    00000000 10110110

when expanded from 8 bits to 16 bits.

Unlike sign extension, zero extension always inserts zero bits.
""")


def zero_extend(binary, new_width):
    if new_width < len(binary):
        raise ValueError("New width must be larger.")

    return binary.zfill(new_width)


print(
    "10110110 ->",
    zero_extend("10110110", 16)
)


# ============================================================
# 33. TRUNCATION
# ============================================================

print("\n" + "=" * 72)
print("TRUNCATION")
print("=" * 72)

print("""
Truncation means discarding higher-order bits when reducing width.

For example:

    10110110

truncated to 4 bits:

    0110

This does not generally preserve the original value.

For unsigned numbers, truncating n bits effectively performs arithmetic
modulo 2^n.

Example:

    246 mod 16 = 6

and:

    246 = 11110110₂

lower four bits:

    0110₂ = 6
""")


# ============================================================
# 34. BIT WIDTH
# ============================================================

print("\n" + "=" * 72)
print("BIT WIDTH")
print("=" * 72)

print("""
A bit can have two possible states:

    0
    1

Therefore n bits provide:

    2^n

distinct bit patterns.

Examples:

    1 bit  -> 2 patterns
    2 bits -> 4 patterns
    3 bits -> 8 patterns
    4 bits -> 16 patterns
    8 bits -> 256 patterns

This is the foundation of binary representation in digital computers.
""")


# ============================================================
# 35. BINARY PLACE VALUES
# ============================================================

print("\nBINARY PLACE VALUES")

for power in range(10, -1, -1):
    print(f"2^{power:>2} = {2 ** power}")


# ============================================================
# 36. POWERS OF TWO
# ============================================================

print("\nPOWERS OF TWO")

for exponent in range(0, 21):
    print(
        f"2^{exponent:>2} = "
        f"{2 ** exponent:>8}"
    )


# ============================================================
# 37. HEXADECIMAL AS A COMPACT BINARY REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("HEXADECIMAL AND BINARY")
print("=" * 72)

print("""
Hexadecimal is frequently used in computing because one hexadecimal
digit represents exactly four bits.

Examples:

    Binary       Hex
    0000          0
    0001          1
    0010          2
    0011          3
    0100          4
    0101          5
    0110          6
    0111          7
    1000          8
    1001          9
    1010          A
    1011          B
    1100          C
    1101          D
    1110          E
    1111          F

Therefore:

    11111111₂ = FF₁₆

and:

    1111111111111111₂ = FFFF₁₆
""")


# ============================================================
# 38. OCTAL IN COMPUTING
# ============================================================

print("\n" + "=" * 72)
print("OCTAL")
print("=" * 72)

print("""
Octal was historically useful because one octal digit corresponds to
three binary bits.

For example:

    111 101 001

becomes:

    7   5   1

so:

    111101001₂ = 751₈

Octal is less common than hexadecimal in modern general-purpose
programming, but it remains important in areas such as Unix permission
notation and historical computer architectures.
""")


# ============================================================
# 39. ASCII AND HEXADECIMAL
# ============================================================

print("\n" + "=" * 72)
print("CHARACTERS, ASCII AND HEXADECIMAL")
print("=" * 72)

print("""
Characters are ultimately represented by numeric codes.

For example, in ASCII:

    'A' = 65 decimal = 41 hexadecimal
    'B' = 66 decimal = 42 hexadecimal
    'a' = 97 decimal = 61 hexadecimal
    '0' = 48 decimal = 30 hexadecimal

Hexadecimal therefore provides a convenient way to inspect byte-level
data.
""")


for character in "ABCabc012":
    code = ord(character)

    print(
        f"{character!r}: "
        f"decimal={code}, "
        f"binary={code:08b}, "
        f"hex={code:02X}"
    )


# ============================================================
# 40. GENERAL ARBITRARY BASES
# ============================================================

print("\n" + "=" * 72)
print("ARBITRARY BASES")
print("=" * 72)

print("""
Positional notation is not limited to bases 2, 8, 10 and 16.

A system can use:

    base 3
    base 5
    base 7
    base 12
    base 20
    base 36

and many others.

For base 3:

    digits = 0, 1, 2

For base 12, additional symbols are needed if ordinary decimal
characters are insufficient.

The general rule remains:

    value = sum(digit_i * base^position_i)
""")


for base in [3, 5, 7, 12, 20, 36]:
    number = 123
    representation = decimal_integer_to_base(number, base)

    print(
        f"123 decimal in base {base:>2}: "
        f"{representation}"
    )


# ============================================================
# 41. BASE 36
# ============================================================

print("\n" + "=" * 72)
print("BASE 36")
print("=" * 72)

print("""
Base 36 uses:

    0-9
    A-Z

for a total of 36 symbols.

It is useful for compact textual representations.

For example:

    35 decimal = Z₃₆
    36 decimal = 10₃₆
""")

for value in range(30, 45):
    print(
        value,
        "decimal =",
        decimal_integer_to_base(value, 36),
        "base 36"
    )


# ============================================================
# 42. BALANCED NUMBER SYSTEMS
# ============================================================

print("\n" + "=" * 72)
print("BALANCED NUMBER SYSTEMS")
print("=" * 72)

print("""
A balanced number system allows digits with negative as well as
positive values.

A classic example is balanced ternary.

Its digits can represent:

    -1
     0
    +1

These may be written conceptually as:

    -
    0
    +

Balanced systems have interesting arithmetic properties and have been
studied in computing and theoretical computer science.

The important distinction is that a positional system does not
necessarily require every digit to be a non-negative integer.
""")


# ============================================================
# 43. MODULAR ARITHMETIC
# ============================================================

print("\n" + "=" * 72)
print("MODULAR ARITHMETIC")
print("=" * 72)

print("""
Fixed-width unsigned binary arithmetic naturally behaves like modular
arithmetic.

For n bits:

    modulus = 2^n

For 8 bits:

    modulus = 256

Therefore:

    257 mod 256 = 1
    256 mod 256 = 0
    255 mod 256 = 255

This explains why fixed-width unsigned arithmetic wraps around.
""")


for value in [255, 256, 257, 511, 512]:
    print(
        f"{value} mod 256 = {value % 256}"
    )


# ============================================================
# 44. MODULAR ADDITION
# ============================================================

print("\nMODULAR ADDITION")

a = 250
b = 20
modulus = 256

print(
    f"({a} + {b}) mod {modulus} = "
    f"{(a + b) % modulus}"
)


# ============================================================
# 45. MODULAR MULTIPLICATION
# ============================================================

print("\nMODULAR MULTIPLICATION")

a = 200
b = 20
modulus = 256

print(
    f"({a} * {b}) mod {modulus} = "
    f"{(a * b) % modulus}"
)


# ============================================================
# 46. FIXED-POINT REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("FIXED-POINT REPRESENTATION")
print("=" * 72)

print("""
A fixed-point representation allocates a fixed number of bits to the
integer part and a fixed number of bits to the fractional part.

Suppose an 8-bit value uses:

    4 bits for integer part
    4 bits for fractional part

Then:

    1010.1100₂

has value:

    10 + 0.75
    = 10.75

The fractional weights are:

    2^-1 = 0.5
    2^-2 = 0.25
    2^-3 = 0.125
    2^-4 = 0.0625
""")


def fixed_point_to_decimal(binary, fractional_bits):
    if any(bit not in "01" for bit in binary):
        raise ValueError("Binary string required.")

    integer_value = int(binary, 2)

    return Fraction(
        integer_value,
        2 ** fractional_bits
    )


fixed_binary = "10101100"

print(
    f"{fixed_binary} with 4 fractional bits =",
    fixed_point_to_decimal(fixed_binary, 4)
)


# ============================================================
# 47. DECIMAL TO FIXED-POINT
# ============================================================

def decimal_to_fixed_point(value, total_bits, fractional_bits):
    """
    Encode a non-negative decimal value using unsigned fixed point.
    """
    scale = 2 ** fractional_bits
    scaled = Fraction(value) * scale

    if scaled.denominator != 1:
        raise ValueError(
            "Value cannot be represented exactly "
            "with this number of fractional bits."
        )

    integer_value = scaled.numerator

    if not 0 <= integer_value < 2 ** total_bits:
        raise OverflowError("Value does not fit.")

    return format(
        integer_value,
        f"0{total_bits}b"
    )


print(
    "10.75 -> fixed point:",
    decimal_to_fixed_point(10.75, 8, 4)
)


# ============================================================
# 48. BINARY FRACTIONS
# ============================================================

print("\n" + "=" * 72)
print("BINARY FRACTIONAL PLACE VALUES")
print("=" * 72)

for power in range(1, 11):
    print(
        f"2^-{power:>2} = "
        f"{2 ** (-power)}"
    )


# ============================================================
# 49. FLOATING-POINT REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("FLOATING-POINT REPRESENTATION")
print("=" * 72)

print("""
Floating-point representation is analogous to scientific notation.

Decimal scientific notation:

    6.25 × 10^3

Binary scientific notation:

    1.101 × 2^2

A floating-point value is represented using fields conceptually
corresponding to:

    sign
    exponent
    significand/fraction

IEEE 754 specifies common floating-point formats.

The commonly encountered binary32 format contains:

    1 sign bit
    8 exponent bits
    23 fraction bits

The commonly encountered binary64 format contains:

    1 sign bit
    11 exponent bits
    52 fraction bits
""")


# ============================================================
# 50. INSPECTING IEEE-754 BINARY32
# ============================================================

def float32_bits(value):
    """
    Return the IEEE-754 binary32 bit pattern for a Python float.
    """
    packed = struct.pack(">f", value)
    integer = int.from_bytes(packed, "big")

    return format(integer, "032b")


def float32_hex(value):
    packed = struct.pack(">f", value)
    return packed.hex().upper()


def explain_float32(value):
    bits = float32_bits(value)

    sign = bits[0]
    exponent = bits[1:9]
    fraction = bits[9:]

    exponent_value = int(exponent, 2)

    if exponent_value == 0:
        exponent_type = "zero/subnormal region"
    elif exponent_value == 255:
        exponent_type = "infinity/NaN region"
    else:
        exponent_type = "normal number"

    print(f"Value: {value}")
    print(f"Bits: {bits}")
    print(f"Sign: {sign}")
    print(f"Exponent: {exponent}")
    print(f"Fraction: {fraction}")
    print(f"Exponent field value: {exponent_value}")
    print(f"Classification: {exponent_type}")
    print(f"Hexadecimal: {float32_hex(value)}")


explain_float32(5.75)


# ============================================================
# 51. NORMALIZED BINARY SCIENTIFIC NOTATION
# ============================================================

print("\n" + "=" * 72)
print("NORMALIZATION")
print("=" * 72)

print("""
A non-zero normalized binary floating-point number can conceptually be
written as:

    1.xxxxx × 2^e

For example:

    1101.01₂

Move the radix point three places left:

    1.10101₂ × 2^3

The leading 1 is implicit in standard normalized binary IEEE
representation for normal numbers, which allows the available
fraction field to provide additional effective precision.
""")


# ============================================================
# 52. FLOATING-POINT SPECIAL VALUES
# ============================================================

print("\n" + "=" * 72)
print("FLOATING-POINT SPECIAL VALUES")
print("=" * 72)

print("""
IEEE-754 representations include special categories.

Positive infinity:

    +∞

Negative infinity:

    -∞

NaN:

    Not a Number

NaN can arise from operations such as:

    0 / 0

in floating-point arithmetic.

Floating-point arithmetic also distinguishes signed zero:

    +0.0
    -0.0

This is different from ordinary integer two's-complement arithmetic,
where zero has a single representation.
""")


special_values = [
    float("inf"),
    float("-inf"),
    float("nan"),
    0.0,
    -0.0,
]

for value in special_values:
    print(
        repr(value),
        "is_integer=",
        getattr(value, "is_integer", lambda: False)()
    )


# ============================================================
# 53. FLOATING-POINT PRECISION
# ============================================================

print("\n" + "=" * 72)
print("FLOATING-POINT PRECISION")
print("=" * 72)

print("""
A floating-point format has finite precision.

Consequently, many real numbers cannot be represented exactly.

For example:

    0.1

does not have a finite binary representation.

Therefore the stored floating-point value is an approximation.

This is why expressions such as:

    0.1 + 0.2

may not produce exactly the mathematical value 0.3.
""")


x = 0.1
y = 0.2
z = x + y

print("0.1 + 0.2 =", z)
print("Is exactly 0.3?", z == 0.3)
print("Difference:", z - 0.3)


# ============================================================
# 54. MACHINE EPSILON
# ============================================================

print("\n" + "=" * 72)
print("MACHINE PRECISION")
print("=" * 72)

print("""
For a floating-point format, machine epsilon is commonly used to
describe the spacing near 1.0 or the smallest increment such that
1 + epsilon differs from 1 under the format's rounding behavior.

For Python's standard float, which normally corresponds to binary64,
the relevant value can be inspected using sys.float_info.epsilon.
""")

import sys

print("Python float epsilon:", sys.float_info.epsilon)
print("Python float mantissa bits:", sys.float_info.mant_dig)
print("Python float exponent max:", sys.float_info.max_exp)
print("Python float exponent min:", sys.float_info.min_exp)


# ============================================================
# 55. ROUNDING
# ============================================================

print("\n" + "=" * 72)
print("ROUNDING IN FLOATING-POINT")
print("=" * 72)

print("""
When a mathematical result cannot fit exactly into the available
floating-point precision, the value must be rounded.

IEEE-754 supports several rounding-direction concepts. The default
rounding mode used in many environments is round-to-nearest, with
ties handled according to the specified rule.

Rounding means that arithmetic may introduce small errors even when
the mathematical operation itself is exact.
""")


# ============================================================
# 56. INTEGER VERSUS FLOATING-POINT
# ============================================================

print("\n" + "=" * 72)
print("INTEGER AND FLOATING-POINT REPRESENTATION")
print("=" * 72)

print("""
Integers and floating-point numbers solve different representation
problems.

Integer representation is exact for values within the supported range.

Floating-point representation provides a very large dynamic range,
but finite precision means that not every integer or real number can
be represented exactly at every magnitude.

For example, binary64 can exactly represent every integer up to
2^53, after which consecutive integers cannot all be represented.
""")


print("2^53 =", 2 ** 53)
print("2^53 + 1 =", 2 ** 53 + 1)

float_value = float(2 ** 53 + 1)

print(
    "As Python float:",
    float_value
)

print(
    "Is float(2^53 + 1) equal to 2^53?",
    float_value == float(2 ** 53)
)


# ============================================================
# 57. NEGATIVE BINARY NUMBERS
# ============================================================

print("\n" + "=" * 72)
print("NEGATIVE BINARY NUMBERS")
print("=" * 72)

print("""
A minus sign by itself does not define how a computer stores a
negative integer.

A computer must choose a representation.

For modern signed integer arithmetic, two's complement is the standard
representation used by most general-purpose processors.

For example, in 8 bits:

    +5 = 00000101

To represent -5:

    00000101
    invert:
    11111010
    add 1:
    11111011

Therefore:

    -5 = 11111011
""")


print("+5:", fixed_width_twos_complement(5, 8))
print("-5:", fixed_width_twos_complement(-5, 8))


# ============================================================
# 58. DECODING TWO'S COMPLEMENT MANUALLY
# ============================================================

print("\n" + "=" * 72)
print("DECODING TWO'S COMPLEMENT")
print("=" * 72)

print("""
To decode a two's-complement value:

1. Inspect the most significant bit.

2. If it is 0, the value is non-negative and ordinary binary
   interpretation applies.

3. If it is 1, subtract 2^n from the unsigned interpretation.

For example:

    11111011₂

Unsigned value:

    251

For 8 bits:

    251 - 256 = -5

Therefore:

    11111011₂ = -5
""")


binary = "11111011"

print(
    binary,
    "unsigned =",
    int(binary, 2),
    "signed =",
    signed_from_twos(binary)
)


# ============================================================
# 59. BITWISE OPERATIONS AND NUMBER REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("BITWISE OPERATIONS")
print("=" * 72)

print("""
Number representation is closely related to bitwise operations.

Common operations:

    AND  &
    OR   |
    XOR  ^
    NOT  ~
    left shift <<
    right shift >>

Example:

    1010
AND 1100
--------
    1000

XOR is especially important because:

    x XOR x = 0
    x XOR 0 = x

Bitwise operations work directly on the binary representation of
integers.
""")


a = 0b1010
b = 0b1100

print("a       =", format(a, "04b"))
print("b       =", format(b, "04b"))
print("a & b   =", format(a & b, "04b"))
print("a | b   =", format(a | b, "04b"))
print("a ^ b   =", format(a ^ b, "04b"))


# ============================================================
# 60. LEFT AND RIGHT SHIFT
# ============================================================

print("\n" + "=" * 72)
print("SHIFT OPERATIONS")
print("=" * 72)

print("""
For positive integers:

    x << n

corresponds to multiplication by:

    2^n

when no relevant bits are lost.

Similarly:

    x >> n

corresponds to integer division by:

    2^n

for non-negative integers.

Example:

    00101100 << 2

becomes:

    10110000

The exact behavior of signed right shifts depends on language and
integer representation rules, so signed shifts should be considered
separately from the simple unsigned case.
""")


x = 44

print("44 binary:", format(x, "08b"))
print("44 << 2:", x << 2, format(x << 2, "08b"))
print("44 >> 2:", x >> 2, format(x >> 2, "08b"))


# ============================================================
# 61. HEXADECIMAL BYTE REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("BYTES AND HEXADECIMAL")
print("=" * 72)

print("""
One byte contains:

    8 bits

and therefore:

    2^8 = 256

possible values.

For an unsigned byte:

    00000000 = 00₁₆ = 0
    11111111 = FF₁₆ = 255

Hexadecimal represents one byte using exactly two hexadecimal digits.
""")

for value in [0, 1, 15, 16, 127, 128, 254, 255]:
    print(
        f"{value:>3} -> "
        f"{value:08b} -> "
        f"{value:02X}"
    )


# ============================================================
# 62. ENDINESS
# ============================================================

print("\n" + "=" * 72)
print("ENDIANNESS")
print("=" * 72)

print("""
Endianness describes the order in which the bytes of a multi-byte
number are stored in memory.

Consider the 32-bit hexadecimal number:

    0x12345678

It consists of four bytes:

    12
    34
    56
    78

Big-endian stores the most significant byte first:

    12 34 56 78

Little-endian stores the least significant byte first:

    78 56 34 12

The numerical value itself does not change. Only the byte ordering in
memory changes.
""")


value = 0x12345678

print(
    "Value:",
    hex(value)
)

print(
    "Big endian:",
    value.to_bytes(4, "big").hex()
)

print(
    "Little endian:",
    value.to_bytes(4, "little").hex()
)


# ============================================================
# 63. RADIX VERSUS ENCODING
# ============================================================

print("\n" + "=" * 72)
print("RADIX VERSUS ENCODING")
print("=" * 72)

print("""
A number system and an encoding scheme are not identical concepts.

Binary positional notation represents numerical values using base 2.

ASCII maps characters to numerical codes.

Unicode defines a much larger character repertoire and multiple
encoding forms.

BCD, Binary-Coded Decimal, represents decimal digits individually
using binary patterns.

For example, decimal 59 in ordinary binary is:

    111011

But BCD represents each decimal digit separately:

    5 -> 0101
    9 -> 1001

Therefore:

    59 BCD = 0101 1001

This is not the same representation as ordinary binary 111011.
""")


# ============================================================
# 64. BCD
# ============================================================

def decimal_to_bcd(number):
    """
    Convert a non-negative decimal integer to Binary-Coded Decimal.
    """
    if number < 0:
        raise ValueError("BCD function expects a non-negative integer.")

    return " ".join(
        format(int(digit), "04b")
        for digit in str(number)
    )


print("59 ordinary binary:", format(59, "b"))
print("59 BCD:", decimal_to_bcd(59))

print("123 BCD:", decimal_to_bcd(123))


# ============================================================
# 65. SIGNED AND UNSIGNED INTERPRETATION OF SAME BITS
# ============================================================

print("\n" + "=" * 72)
print("SAME BITS, DIFFERENT INTERPRETATIONS")
print("=" * 72)

print("""
A bit pattern does not inherently carry a universal meaning.

For example:

    11111111

as an 8-bit unsigned integer:

    255

as an 8-bit two's-complement signed integer:

    -1

The physical bits are identical.

The interpretation rules are different.
""")


pattern = "11111111"

print("Bits:", pattern)
print("Unsigned:", int(pattern, 2))
print("Signed two's complement:", signed_from_twos(pattern))


# ============================================================
# 66. BASE CONVERSION USING POLYNOMIAL EVALUATION
# ============================================================

print("\n" + "=" * 72)
print("HORNER'S METHOD FOR BASE CONVERSION")
print("=" * 72)

print("""
A positional number can be evaluated efficiently using Horner's
method.

For:

    1234₅

instead of explicitly calculating every power, evaluate:

    (((1 * 5 + 2) * 5 + 3) * 5 + 4)

This is:

    194 decimal

Horner's method reduces the number of multiplications and additions
needed to evaluate the positional polynomial.
""")


def base_to_decimal_horner(number, base):
    number = number.upper()

    if "." in number:
        raise ValueError(
            "This demonstration handles integers only."
        )

    validate_number(number, base)

    result = 0

    for digit in number:
        result = result * base + char_to_value(digit)

    return result


print(
    "1234 base 5 =",
    base_to_decimal_horner("1234", 5)
)


# ============================================================
# 67. NUMBER SYSTEMS AND ALGORITHMIC COMPLEXITY
# ============================================================

print("\n" + "=" * 72)
print("NUMBER SYSTEMS AND COMPUTATIONAL REPRESENTATION")
print("=" * 72)

print("""
The number of digits required to represent a positive integer n in
base b is approximately:

    floor(log_b(n)) + 1

For example, decimal 1000 needs:

    floor(log_10(1000)) + 1
    = 4 digits

Binary 1000 requires:

    floor(log_2(1000)) + 1
    = 10 bits

This relationship matters in storage, algorithm design, data
structures, and computational complexity.
""")


def digit_count(number, base):
    if number == 0:
        return 1

    return len(decimal_integer_to_base(abs(number), base))


for number in [10, 100, 1000, 1000000]:
    print(
        f"{number}: "
        f"decimal digits={digit_count(number, 10)}, "
        f"binary bits={digit_count(number, 2)}, "
        f"hex digits={digit_count(number, 16)}"
    )


# ============================================================
# 68. LOGARITHMIC RELATION BETWEEN BASES
# ============================================================

print("\n" + "=" * 72)
print("BASE AND REPRESENTATION LENGTH")
print("=" * 72)

print("""
The relationship between the number of digits in two bases is
approximately:

    digits_base_a(n)
    ≈ digits_base_b(n) * log_b(a)

Binary needs more digits because base 2 carries only one bit of
information per digit.

Hexadecimal is compact because one hexadecimal digit represents four
binary bits.
""")

value = 10 ** 12

print("Value:", value)
print("Decimal digits:", digit_count(value, 10))
print("Binary bits:", digit_count(value, 2))
print("Hexadecimal digits:", digit_count(value, 16))


# ============================================================
# 69. INFORMATION CONTENT OF A DIGIT
# ============================================================

print("\n" + "=" * 72)
print("INFORMATION CONTENT OF A DIGIT")
print("=" * 72)

print("""
A digit in base b can take b different values.

Its information capacity is:

    log2(b) bits

Examples:

    binary digit:
        log2(2) = 1 bit

    octal digit:
        log2(8) = 3 bits

    hexadecimal digit:
        log2(16) = 4 bits

This explains why:

    3 binary digits = 1 octal digit

and:

    4 binary digits = 1 hexadecimal digit
""")


for base in [2, 4, 8, 10, 16, 32, 64]:
    print(
        f"Base {base:>2}: "
        f"{math.log2(base):.4f} bits per digit"
    )


# ============================================================
# 70. CHECKING CONVERSIONS
# ============================================================

print("\n" + "=" * 72)
print("VERIFYING BASE CONVERSIONS")
print("=" * 72)

print("""
A conversion should ideally be reversible.

For example:

    binary -> decimal -> binary

should produce the original value, provided no precision has been
discarded.

For fractional conversions with limited digits, exact reversibility
may not be possible because the target representation may be
non-terminating.
""")


def verify_conversion(number, base_a, base_b):
    converted = convert_base(number, base_a, base_b)

    try:
        restored = convert_base(converted, base_b, base_a)
    except Exception:
        restored = None

    print(
        f"{number} (base {base_a}) -> "
        f"{converted} (base {base_b}) -> "
        f"{restored} (base {base_a})"
    )


verify_conversion("101101", 2, 16)
verify_conversion("745", 8, 2)
verify_conversion("1A", 16, 2)


# ============================================================
# 71. COMMON EDGE CASES
# ============================================================

print("\n" + "=" * 72)
print("EDGE CASES")
print("=" * 72)

print("""
Important edge cases in number systems include:

1. Zero
2. Negative numbers
3. Leading zeros
4. Trailing fractional zeros
5. Invalid digits
6. Overflow
7. Underflow
8. Non-terminating fractions
9. Fixed-width truncation
10. Signed versus unsigned interpretation
11. Special floating-point values
12. Rounding
13. Different byte ordering
14. Different encoding schemes
15. Loss of precision
""")


# ============================================================
# 72. LEADING ZEROS
# ============================================================

print("\nLEADING ZEROS")

print("""
Leading zeros do not change the numerical value in ordinary positional
notation.

For example:

    00010110₂
    10110₂

both represent:

    22 decimal

But leading zeros can be important in fixed-width representation,
where the width itself carries information about how the value should
be interpreted.
""")

print(int("00010110", 2))
print(int("10110", 2))


# ============================================================
# 73. TRAILING FRACTIONAL ZEROS
# ============================================================

print("\nTRAILING FRACTIONAL ZEROS")

print("""
Trailing zeros after a radix point do not change the numerical value.

For example:

    10.100₂
    10.1₂

have the same mathematical value.

The extra zero simply expresses the same fraction at a greater
specified precision or fixed width.
""")


print(
    base_to_decimal("10.100", 2),
    base_to_decimal("10.1", 2)
)


# ============================================================
# 74. INVALID DIGITS
# ============================================================

print("\nINVALID DIGIT EXAMPLES")

invalid_examples = [
    ("102", 2),
    ("89", 8),
    ("1G", 16),
    ("29", 2),
]

for number, base in invalid_examples:
    try:
        print(number, "base", base, "=", base_to_decimal(number, base))
    except ValueError as error:
        print(number, "base", base, "->", error)


# ============================================================
# 75. UNDERFLOW
# ============================================================

print("\n" + "=" * 72)
print("UNDERFLOW")
print("=" * 72)

print("""
Underflow occurs when a numerical result becomes too small to be
represented normally within the chosen numerical format.

For integer representations, the term is often used informally when
a result falls outside a representable range.

For floating-point systems, underflow has a more specific meaning:
a result may become smaller in magnitude than the smallest normal
representable value.

IEEE-754 provides subnormal numbers so that values can gradually
approach zero instead of immediately jumping from the smallest normal
value to zero.
""")


# ============================================================
# 76. SUBNORMAL FLOATING-POINT VALUES
# ============================================================

print("\nSUBNORMAL VALUES")

small = 2 ** -149

print("A very small binary32-scale value:", small)
print(
    "As binary32:",
    float32_hex(small)
)


# ============================================================
# 77. INFINITY
# ============================================================

print("\n" + "=" * 72)
print("INFINITY")
print("=" * 72)

print("""
Floating-point systems can represent positive and negative infinity.

Infinity is not merely a very large ordinary finite number.

It is a special representation.

Examples of operations that can produce infinity in floating-point
arithmetic include overflow during certain operations.
""")

positive_infinity = float("inf")
negative_infinity = float("-inf")

print("Positive infinity:", positive_infinity)
print("Negative infinity:", negative_infinity)


# ============================================================
# 78. NAN
# ============================================================

print("\n" + "=" * 72)
print("NaN")
print("=" * 72)

print("""
NaN means "Not a Number".

NaN is used to represent certain undefined or invalid floating-point
results.

An important property is:

    NaN != NaN

Therefore checking:

    value == float("nan")

is not the correct general way to test for NaN.

Python provides math.isnan().
""")


nan_value = float("nan")

print("NaN == NaN:", nan_value == nan_value)
print("math.isnan(NaN):", math.isnan(nan_value))


# ============================================================
# 79. BASE REPRESENTATION OF DECIMAL NUMBERS
# ============================================================

print("\n" + "=" * 72)
print("REPRESENTATION IS CONTEXT-DEPENDENT")
print("=" * 72)

print("""
The symbol sequence:

    10

has different values depending on the base.

    10₂  = 2
    10₃  = 3
    10₈  = 8
    10₁₀ = 10
    10₁₆ = 16

Therefore a number should conceptually be understood together with
its radix when ambiguity is possible.
""")


for base in [2, 3, 8, 10, 16]:
    print(
        f"10 base {base} =",
        base_to_decimal("10", base)
    )


# ============================================================
# 80. POLYNOMIAL VIEW OF POSITIONAL NOTATION
# ============================================================

print("\n" + "=" * 72)
print("POSITIONAL NOTATION AS A POLYNOMIAL")
print("=" * 72)

print("""
A number such as:

    3142₅

can be interpreted as:

    3x^3 + 1x^2 + 4x + 2

evaluated at:

    x = 5

Thus:

    3(5^3) + 1(5^2) + 4(5) + 2

This polynomial interpretation explains why positional notation works
systematically for arbitrary bases.
""")


number = "3142"
base = 5

value = sum(
    char_to_value(digit) * base ** power
    for power, digit in enumerate(reversed(number))
)

print(
    f"{number} base {base} = {value} decimal"
)


# ============================================================
# 81. FRACTIONAL POLYNOMIAL VIEW
# ============================================================

print("\n" + "=" * 72)
print("FRACTIONAL POSITIONAL NOTATION")
print("=" * 72)

print("""
For:

    12.34₅

the polynomial interpretation is:

    1*5^1
    + 2*5^0
    + 3*5^-1
    + 4*5^-2

The same positional rule therefore applies on both sides of the
radix point.
""")

print(
    "12.34 base 5 =",
    base_to_decimal("12.34", 5)
)


# ============================================================
# 82. NEGATIVE EXPONENTS
# ============================================================

print("\n" + "=" * 72)
print("NEGATIVE POWERS IN FRACTIONS")
print("=" * 72)

for base in [2, 8, 10, 16]:
    print(f"\nBase {base}")
    for exponent in range(1, 5):
        print(
            f"{base}^-{exponent} = "
            f"{Fraction(1, base ** exponent)}"
        )


# ============================================================
# 83. INTEGER DIVISION AND REMAINDERS
# ============================================================

print("\n" + "=" * 72)
print("INTEGER DIVISION AND REMAINDERS")
print("=" * 72)

print("""
Repeated division works because every integer n can be expressed as:

    n = q*b + r

where:

    q = quotient
    b = base
    r = remainder

and:

    0 <= r < b

The remainder becomes the next digit in the target base.

This is the mathematical basis of repeated-division base conversion.
""")


for number in [37, 38, 39, 40]:
    q, r = divmod(number, 5)

    print(
        f"{number} = {q} * 5 + {r}"
    )


# ============================================================
# 84. FRACTIONAL MULTIPLICATION PRINCIPLE
# ============================================================

print("\n" + "=" * 72)
print("FRACTIONAL CONVERSION PRINCIPLE")
print("=" * 72)

print("""
For a fractional value f in the interval [0, 1):

    multiply f by the target base.

The integer part of the result becomes the next digit.

Then retain the fractional part and repeat.

This works because:

    f = d1/b + d2/b^2 + d3/b^3 + ...

Repeated multiplication extracts d1, d2, d3, and so on.
""")


# ============================================================
# 85. PRACTICAL CONVERSION TABLE
# ============================================================

print("\n" + "=" * 72)
print("CONVERSION TABLE")
print("=" * 72)

print(
    f"{'Decimal':>10} "
    f"{'Binary':>12} "
    f"{'Octal':>10} "
    f"{'Hex':>10}"
)

print("-" * 48)

for number in range(0, 33):
    print(
        f"{number:>10} "
        f"{decimal_integer_to_base(number, 2):>12} "
        f"{decimal_integer_to_base(number, 8):>10} "
        f"{decimal_integer_to_base(number, 16):>10}"
    )


# ============================================================
# 86. POWER-OF-TWO RELATIONSHIPS
# ============================================================

print("\n" + "=" * 72)
print("POWER-OF-TWO BASE RELATIONSHIPS")
print("=" * 72)

print("""
The most useful relationships are:

    2^1 = 2
    2^3 = 8
    2^4 = 16

Therefore:

    1 binary digit  = 1 bit
    1 octal digit   = 3 bits
    1 hex digit     = 4 bits

This is why binary-octal and binary-hexadecimal conversion can be
performed by grouping bits rather than repeatedly converting through
decimal.
""")


# ============================================================
# 87. NUMBER SYSTEMS IN MEMORY
# ============================================================

print("\n" + "=" * 72)
print("NUMBER SYSTEMS AND MEMORY")
print("=" * 72)

print("""
Memory is fundamentally addressed and manipulated using binary
hardware.

A memory byte consists of eight bits.

A sequence of bytes may be displayed using hexadecimal because it is
much more compact than binary.

For example:

    Binary:
        11010110 10101100 01110001

    Hex:
        D6 AC 71

Both represent the same bit sequence.
""")


data = bytes([0xD6, 0xAC, 0x71])

print("Bytes:", data)
print("Hex:", data.hex(" "))
print(
    "Binary:",
    " ".join(format(byte, "08b") for byte in data)
)


# ============================================================
# 88. NUMBER SYSTEMS AND NETWORKING
# ============================================================

print("\n" + "=" * 72)
print("NUMBER SYSTEMS IN NETWORKING")
print("=" * 72)

print("""
Networking uses number systems extensively.

IPv4 addresses are normally written in decimal dotted notation:

    192.168.1.10

Each component is an 8-bit unsigned value.

Therefore every octet ranges from:

    0 to 255

The underlying representation is binary.
""")


ip = [192, 168, 1, 10]

for octet in ip:
    print(
        f"{octet:>3} -> "
        f"{octet:08b} -> "
        f"{octet:02X}"
    )


# ============================================================
# 89. HEXADECIMAL IN MEMORY DEBUGGING
# ============================================================

print("\n" + "=" * 72)
print("HEX REPRESENTATION IN DEBUGGING")
print("=" * 72)

print("""
When inspecting binary data, hexadecimal is often easier to read.

For example:

    0x7F
    0x80
    0xFF

can immediately be recognized as single-byte values.

The 0x prefix is a conventional notation used in many programming
languages to indicate hexadecimal.
""")

values = [0x00, 0x01, 0x7F, 0x80, 0xFF]

for value in values:
    print(
        f"0x{value:02X} = "
        f"{value} decimal = "
        f"{value:08b} binary"
    )


# ============================================================
# 90. NUMERICAL PRECISION VERSUS RANGE
# ============================================================

print("\n" + "=" * 72)
print("RANGE VERSUS PRECISION")
print("=" * 72)

print("""
Floating-point representation involves a trade-off between range and
precision.

The exponent provides large dynamic range.

The significand provides precision.

Increasing exponent capacity generally expands the range.

Increasing significand precision improves the number of significant
digits that can be represented.

These are distinct properties.

A format can represent extremely large numbers while still having
limited precision between adjacent representable numbers at large
magnitudes.
""")


# ============================================================
# 91. ABSOLUTE ERROR AND RELATIVE ERROR
# ============================================================

print("\n" + "=" * 72)
print("NUMERICAL ERROR")
print("=" * 72)

print("""
Suppose the exact value is:

    x

and an approximation is:

    x_hat

Absolute error:

    |x - x_hat|

Relative error:

    |x - x_hat| / |x|

for x != 0.

These concepts are useful when studying floating-point representation
and numerical computation.
""")


exact = 1 / 3
approximation = float(exact)

absolute_error = abs(exact - approximation)
relative_error = absolute_error / abs(exact)

print("Exact:", exact)
print("Approximation:", approximation)
print("Absolute error:", absolute_error)
print("Relative error:", relative_error)


# ============================================================
# 92. EXACT BINARY FRACTIONS
# ============================================================

print("\n" + "=" * 72)
print("EXACT BINARY FRACTIONS")
print("=" * 72)

print("""
A finite binary fraction has the form:

    integer / 2^n

Examples:

    1/2
    3/4
    5/8
    7/16

These can be represented exactly with a finite number of binary
fractional digits.

For example:

    5/8 = 0.101₂
""")


exact_binary_fractions = [
    Fraction(1, 2),
    Fraction(3, 4),
    Fraction(5, 8),
    Fraction(7, 16),
]

for fraction in exact_binary_fractions:
    print(
        fraction,
        "->",
        decimal_fraction_to_base(fraction, 2, 20)
    )


# ============================================================
# 93. NON-EXACT BINARY FRACTIONS
# ============================================================

print("\n" + "=" * 72)
print("NON-EXACT BINARY FRACTIONS")
print("=" * 72)

non_exact = [
    Fraction(1, 3),
    Fraction(1, 5),
    Fraction(1, 10),
    Fraction(2, 7),
]

for fraction in non_exact:
    print(
        fraction,
        "->",
        decimal_fraction_to_base(fraction, 2, 20),
        "..."
    )


# ============================================================
# 94. BASE CONVERSION AND PRECISION LOSS
# ============================================================

print("\n" + "=" * 72)
print("PRECISION LOSS DURING FRACTION CONVERSION")
print("=" * 72)

print("""
When a fractional value has a non-terminating representation in the
target base, a finite conversion must stop after a chosen number of
digits.

For example, decimal 0.1 converted to binary produces an infinite
repeating expansion.

If only eight binary fractional digits are retained, the result is
an approximation rather than an exact representation.
""")


value = Fraction(1, 10)

for precision in [4, 8, 16, 32]:
    representation = decimal_fraction_to_base(
        value,
        2,
        precision
    )

    print(
        f"Precision {precision:>2}: "
        f"0.{representation}₂"
    )


# ============================================================
# 95. NUMBER SYSTEM CONVERSION SUMMARY TABLE
# ============================================================

print("\n" + "=" * 72)
print("CONVERSION METHODS")
print("=" * 72)

print("""
DECIMAL INTEGER -> OTHER BASE
    Repeated division by target base.

DECIMAL FRACTION -> OTHER BASE
    Repeated multiplication by target base.

OTHER BASE -> DECIMAL
    Multiply each digit by its positional weight and sum.

BINARY -> OCTAL
    Group bits in sets of 3.

OCTAL -> BINARY
    Replace each octal digit with 3 bits.

BINARY -> HEXADECIMAL
    Group bits in sets of 4.

HEXADECIMAL -> BINARY
    Replace each hex digit with 4 bits.

ARBITRARY BASE -> ARBITRARY BASE
    Convert through decimal or use another mathematically valid
    conversion process.
""")


# ============================================================
# 96. PRACTICE CALCULATIONS
# ============================================================

print("\n" + "=" * 72)
print("PRACTICE CALCULATIONS")
print("=" * 72)

practice = [
    ("101010", 2, 10),
    ("11111111", 2, 16),
    ("753", 8, 10),
    ("ABC", 16, 10),
    ("1001", 2, 8),
    ("345", 6, 10),
    ("Z", 36, 10),
]

for number, source_base, target_base in practice:
    try:
        result = convert_base(
            number,
            source_base,
            target_base
        )

        print(
            f"{number} base {source_base} -> "
            f"{result} base {target_base}"
        )

    except ValueError as error:
        print(
            f"{number} base {source_base}: {error}"
        )


# ============================================================
# 97. VERIFYING TWO'S COMPLEMENT RANGES
# ============================================================

print("\n" + "=" * 72)
print("TWO'S COMPLEMENT RANGE CHECK")
print("=" * 72)

for bits in [4, 8]:
    minimum, maximum = twos_complement_range(bits)

    print(
        f"\n{bits}-bit range: {minimum} to {maximum}"
    )

    for value in [minimum, -1, 0, 1, maximum]:
        binary = fixed_width_twos_complement(value, bits)

        print(
            f"{value:>5} -> "
            f"{binary} -> "
            f"{signed_from_twos(binary)}"
        )


# ============================================================
# 98. FIXED-WIDTH WRAPAROUND
# ============================================================

print("\n" + "=" * 72)
print("FIXED-WIDTH WRAPAROUND")
print("=" * 72)

print("""
For an unsigned n-bit integer, adding 1 to the maximum value produces
zero after truncation.

For 8 bits:

    11111111 + 1
    = 1 00000000

If only eight bits are retained:

    00000000
""")


bits = 8

for value in [254, 255, 256, 257]:
    encoded = format(
        value % (2 ** bits),
        f"0{bits}b"
    )

    print(
        f"{value:>3} -> {encoded}"
    )


# ============================================================
# 99. TWO'S COMPLEMENT NEGATION
# ============================================================

print("\n" + "=" * 72)
print("TWO'S COMPLEMENT NEGATION")
print("=" * 72)

print("""
To negate a two's-complement value:

    1. Invert every bit.
    2. Add one.

For example:

    +6:

        00000110

    invert:

        11111001

    add one:

        11111010

    therefore:

        11111010 = -6
""")


for value in [1, 2, 5, 6, 10]:
    positive = fixed_width_twos_complement(value, 8)
    negative = twos_complement(positive)

    print(
        f"+{value:>2}: {positive}    "
        f"-{value:>2}: {negative}"
    )


# ============================================================
# 100. THE SPECIAL TWO'S COMPLEMENT MINIMUM
# ============================================================

print("\n" + "=" * 72)
print("SPECIAL CASE: MINIMUM TWO'S-COMPLEMENT VALUE")
print("=" * 72)

print("""
The minimum two's-complement value is special.

For 8 bits:

    minimum = -128

Its bit pattern is:

    10000000

There is no positive +128 in signed 8-bit two's complement.

Therefore attempting to negate -128 within the same width produces
the same bit pattern:

    -(-128)

mathematically equals +128,

but +128 is not representable in signed 8-bit two's complement.

This is an important edge case in fixed-width arithmetic.
""")


minimum = -(2 ** 7)

pattern = fixed_width_twos_complement(minimum, 8)

print("Minimum:", minimum)
print("Pattern:", pattern)
print(
    "Negated mathematically:",
    -minimum
)

print(
    "Negated within 8 bits:",
    twos_complement(pattern)
)


# ============================================================
# 101. BASE COMPLEMENT GENERALIZATION
# ============================================================

print("\n" + "=" * 72)
print("GENERAL COMPLEMENT FORMULATION")
print("=" * 72)

print("""
For an n-digit number N in base r:

    (r^n - N)

is its r's complement.

The (r-1)'s complement is:

    (r^n - 1) - N

and therefore:

    r's complement
    = (r-1)'s complement + 1

Binary:

    r = 2

therefore:

    (r-1) = 1

which gives:

    1's complement
    2's complement

Decimal:

    r = 10

therefore:

    (r-1) = 9

which gives:

    9's complement
    10's complement
""")


# ============================================================
# 102. NUMBER SYSTEMS AND COMPUTER ARCHITECTURE
# ============================================================

print("\n" + "=" * 72)
print("NUMBER SYSTEMS IN COMPUTER ARCHITECTURE")
print("=" * 72)

print("""
Number systems appear throughout computer architecture.

Examples include:

    CPU registers
    memory addresses
    instruction encodings
    machine instructions
    bit masks
    status flags
    virtual addresses
    physical addresses
    cache tags
    binary data
    floating-point values
    network addresses

Hexadecimal is commonly used as a human-readable shorthand for binary
because each hexadecimal digit maps exactly to four bits.
""")


# ============================================================
# 103. MEMORY ADDRESS EXAMPLE
# ============================================================

address = 0x7FF0A2

print("\nExample memory address:")
print("Hexadecimal :", hex(address))
print("Decimal     :", address)
print("Binary      :", format(address, "024b"))


# ============================================================
# 104. BIT MASKS
# ============================================================

print("\n" + "=" * 72)
print("BIT MASKS")
print("=" * 72)

print("""
A bit mask is a binary pattern used to inspect or modify selected bits.

Example:

    value = 10110110
    mask  = 00001111

AND:

    10110110
  & 00001111
    --------
    00000110

The lower four bits are extracted.

Hexadecimal makes this concise:

    0xB6 & 0x0F = 0x06
""")


value = 0xB6
mask = 0x0F

print("Value:", hex(value))
print("Mask :", hex(mask))
print("AND  :", hex(value & mask))


# ============================================================
# 105. BINARY PARITY
# ============================================================

print("\n" + "=" * 72)
print("PARITY AND BINARY REPRESENTATION")
print("=" * 72)

print("""
Parity is a simple property of a binary word.

Even parity means the number of 1 bits is even.

Odd parity means the number of 1 bits is odd.

Parity has been used for basic error detection.
""")


def parity(number):
    ones = bin(number).count("1")

    return "even" if ones % 2 == 0 else "odd"


for number in [0, 1, 3, 7, 10, 255]:
    print(
        f"{number:>3} -> {number:08b} -> "
        f"{parity(number)} parity"
    )


# ============================================================
# 106. HAMMING WEIGHT
# ============================================================

print("\n" + "=" * 72)
print("HAMMING WEIGHT")
print("=" * 72)

print("""
The Hamming weight of a binary value is the number of 1 bits in its
representation.

For example:

    10110110

contains five 1s.

Hamming weight is useful in coding theory, digital systems,
cryptography, error detection, and bit manipulation.
""")


def hamming_weight(number):
    return number.bit_count()


for number in [0, 1, 7, 15, 16, 255]:
    print(
        f"{number:>3}: "
        f"{number:08b}, "
        f"weight={hamming_weight(number)}"
    )


# ============================================================
# 107. NUMBER SYSTEMS AND CRYPTOGRAPHY
# ============================================================

print("\n" + "=" * 72)
print("NUMBER SYSTEMS IN CRYPTOGRAPHY")
print("=" * 72)

print("""
Cryptographic algorithms operate heavily on integers and bit strings.

Binary representation is used for:

    bitwise operations
    rotations
    XOR
    modular arithmetic
    finite-field representations
    hash functions
    block ciphers

Hexadecimal is widely used when displaying:

    keys
    hashes
    byte sequences
    digests
    initialization values

For example, a byte sequence:

    DE AD BE EF

is simply a human-friendly hexadecimal rendering of:

    11011110 10101101 10111110 11101111
""")


crypto_bytes = bytes.fromhex("DE AD BE EF")

print(
    "Hex    :",
    crypto_bytes.hex(" ").upper()
)

print(
    "Binary :",
    " ".join(format(x, "08b") for x in crypto_bytes)
)


# ============================================================
# 108. MODULAR EXPONENTIATION
# ============================================================

print("\n" + "=" * 72)
print("MODULAR EXPONENTIATION")
print("=" * 72)

print("""
Modular arithmetic becomes especially important when dealing with
large integers.

Instead of computing a huge value first:

    a^b

and then taking the remainder, efficient algorithms calculate:

    a^b mod m

without constructing the complete gigantic integer.

Python's pow() supports:

    pow(a, b, m)

which computes:

    a^b mod m
""")


print("3^100 mod 17 =", pow(3, 100, 17))
print("7^200 mod 13 =", pow(7, 200, 13))


# ============================================================
# 109. DIVISIBILITY AND BASE REPRESENTATION
# ============================================================

print("\n" + "=" * 72)
print("DIVISIBILITY PATTERNS")
print("=" * 72)

print("""
The representation of a number can reveal divisibility properties.

In decimal:

    divisibility by 10 -> last digit is 0
    divisibility by 2  -> last digit is even
    divisibility by 5  -> last digit is 0 or 5

In binary:

    divisibility by 2 -> least significant bit is 0
    divisibility by 4 -> last two bits are 00
    divisibility by 8 -> last three bits are 000

This follows directly from positional weights.
""")


for value in [8, 12, 16, 24, 32]:
    print(
        f"{value:>2} -> {value:08b}"
    )


# ============================================================
# 110. SIGNIFICANCE OF THE LEAST SIGNIFICANT BIT
# ============================================================

print("\n" + "=" * 72)
print("LEAST SIGNIFICANT BIT")
print("=" * 72)

print("""
The least significant bit, or LSB, is the bit representing 2^0.

It has value:

    1

For an unsigned integer:

    LSB = 0 -> even
    LSB = 1 -> odd

Therefore:

    number & 1

can be used to test whether an integer is odd.
""")


for number in range(10):
    print(
        f"{number}: "
        f"LSB={number & 1}"
    )


# ============================================================
# 111. MOST SIGNIFICANT BIT
# ============================================================

print("\n" + "=" * 72)
print("MOST SIGNIFICANT BIT")
print("=" * 72)

print("""
The most significant bit is the highest-position bit in a fixed-width
representation.

In unsigned numbers, it contributes a positive power of two.

In two's-complement signed numbers, the MSB has a special negative
weight:

    -2^(n-1)

The remaining bits have positive weights.
""")


print("""
8-bit two's complement weights:

    -128 64 32 16 8 4 2 1

Therefore:

    10000000 = -128
    11000000 = -128 + 64 = -64
    11111111 = -128 + 127 = -1
""")


# ============================================================
# 112. TWO'S COMPLEMENT AS WEIGHTED BITS
# ============================================================

def twos_complement_weighted_value(binary):
    bits = len(binary)

    value = 0

    for index, bit in enumerate(binary):
        if index == 0:
            weight = -(2 ** (bits - 1))
        else:
            weight = 2 ** (bits - index - 1)

        value += int(bit) * weight

    return value


for binary in ["10000000", "11000000", "11111111", "10101010"]:
    print(
        binary,
        "->",
        twos_complement_weighted_value(binary)
    )


# ============================================================
# 113. FLOATING-POINT EXPONENT BIAS
# ============================================================

print("\n" + "=" * 72)
print("FLOATING-POINT EXPONENT BIAS")
print("=" * 72)

print("""
IEEE-style floating-point formats use a biased exponent.

For binary32:

    exponent field = 8 bits
    bias = 127

For a normal number:

    actual exponent
    = stored exponent - 127

For example, if the stored exponent is:

    130

then:

    actual exponent = 130 - 127 = 3
""")


stored_exponent = 130
bias = 127

print(
    "Stored exponent:",
    stored_exponent
)

print(
    "Actual exponent:",
    stored_exponent - bias
)


# ============================================================
# 114. IEEE-754 BINARY32 FIELD STRUCTURE
# ============================================================

print("\n" + "=" * 72)
print("IEEE-754 BINARY32 FIELD STRUCTURE")
print("=" * 72)

print("""
Binary32:

    sign       exponent        fraction
      1 bit       8 bits          23 bits

Total:

    1 + 8 + 23 = 32 bits

For normal finite numbers:

    value =
        (-1)^sign
        * 1.fraction
        * 2^(exponent-bias)

The exponent field has special values:

    all zeros:
        zero/subnormal

    all ones:
        infinity/NaN

Normal finite numbers occupy the remaining exponent patterns.
""")


# ============================================================
# 115. IEEE-754 BINARY64 FIELD STRUCTURE
# ============================================================

print("\n" + "=" * 72)
print("IEEE-754 BINARY64 FIELD STRUCTURE")
print("=" * 72)

print("""
Binary64:

    sign       exponent        fraction
      1 bit      11 bits          52 bits

Total:

    1 + 11 + 52 = 64 bits

Exponent bias:

    1023
""")


print("Binary64 total bits:", 1 + 11 + 52)
print("Binary64 exponent bias:", 1023)


# ============================================================
# 116. INTEGER REPRESENTATION WITH DIFFERENT WIDTHS
# ============================================================

print("\n" + "=" * 72)
print("SAME VALUE AT DIFFERENT WIDTHS")
print("=" * 72)

value = -42

for bits in [8, 16, 32]:
    print(
        f"{bits:>2}-bit: "
        f"{fixed_width_twos_complement(value, bits)}"
    )


# ============================================================
# 117. UNSIGNED INTERPRETATION OF SIGNED PATTERNS
# ============================================================

print("\n" + "=" * 72)
print("SIGNED/UNSIGNED CASTING CONCEPT")
print("=" * 72)

print("""
Suppose an 8-bit pattern is:

    11110110

As unsigned:

    246

As signed two's complement:

    -10

A low-level language can reinterpret the same bits as signed or
unsigned depending on the type used.

This is an interpretation issue rather than a change to the physical
bit pattern.
""")


pattern = "11110110"

print("Pattern:", pattern)
print("Unsigned:", int(pattern, 2))
print("Signed:", signed_from_twos(pattern))


# ============================================================
# 118. MODULO AND FIXED-WIDTH INTEGER STORAGE
# ============================================================

print("\n" + "=" * 72)
print("FIXED-WIDTH INTEGER AS MODULAR VALUE")
print("=" * 72)

print("""
An n-bit unsigned storage location can represent exactly one residue
class modulo 2^n for every stored bit pattern.

For 8 bits:

    0, 1, ..., 255

represent the 256 possible residues modulo 256.

If an arithmetic operation produces 256, the low 8 bits represent:

    0 mod 256

This mathematical viewpoint makes wraparound behavior precise.
""")


for value in [256, 257, 300, 511, 512]:
    print(
        f"{value} mod 256 = {value % 256}"
    )


# ============================================================
# 119. BASE-N ADDITION GENERALIZATION
# ============================================================

print("\n" + "=" * 72)
print("GENERAL BASE ADDITION")
print("=" * 72)

print("""
In base b, addition proceeds from right to left.

Whenever a column reaches b or more, carry is generated.

For example in base 8:

    7 + 1 = 10₈

In hexadecimal:

    F + 1 = 10₁₆

The carry rule is therefore:

    carry = floor(column_sum / base)

and:

    result_digit = column_sum mod base
""")


def add_digits(a, b, base):
    total = a + b

    return (
        total // base,
        total % base
    )


for base in [2, 8, 10, 16]:
    carry, digit = add_digits(base - 1, 1, base)

    print(
        f"Base {base}: "
        f"carry={carry}, digit={digit}"
    )


# ============================================================
# 120. GENERAL BASE SUBTRACTION
# ============================================================

print("\n" + "=" * 72)
print("GENERAL BASE SUBTRACTION")
print("=" * 72)

print("""
When subtracting in base b and a digit is too small, borrow one unit
from the next position.

That borrowed unit has value:

    b

in the current position.

For example, in binary:

    borrowed value = 2

In decimal:

    borrowed value = 10

In hexadecimal:

    borrowed value = 16
""")


# ============================================================
# 121. NUMBER SYSTEM TERMINOLOGY
# ============================================================

print("\n" + "=" * 72)
print("IMPORTANT TERMINOLOGY")
print("=" * 72)

terms = {
    "Bit": "Binary digit, either 0 or 1.",
    "Nibble": "Four bits.",
    "Byte": "Eight bits.",
    "Radix": "Another name for the base of a positional system.",
    "MSB": "Most significant bit.",
    "LSB": "Least significant bit.",
    "Carry": "A value propagated to the next higher position during addition.",
    "Borrow": "A value taken from the next higher position during subtraction.",
    "Overflow": "Result outside the representable range.",
    "Underflow": "Result too small for the chosen numerical representation.",
    "Precision": "Number of distinguishable significant values/digits supported.",
    "Range": "Smallest to largest representable value.",
    "Significand": "Significant portion of a floating-point representation.",
    "Exponent": "Power controlling floating-point scale.",
    "Radix point": "Point separating positive and negative positional powers.",
}

for term, definition in terms.items():
    print(f"{term:>15}: {definition}")


# ============================================================
# 122. FINAL COMPUTATIONAL DEMONSTRATION
# ============================================================

print("\n" + "=" * 72)
print("INTEGRATED NUMBER SYSTEM DEMONSTRATION")
print("=" * 72)

number = 2026

print("\nDecimal:")
print(number)

print("\nBinary:")
print(decimal_integer_to_base(number, 2))

print("\nOctal:")
print(decimal_integer_to_base(number, 8))

print("\nHexadecimal:")
print(decimal_integer_to_base(number, 16))

print("\nBinary -> Decimal:")
binary = decimal_integer_to_base(number, 2)
print(base_to_decimal(binary, 2))

print("\nHexadecimal -> Decimal:")
hexadecimal = decimal_integer_to_base(number, 16)
print(base_to_decimal(hexadecimal, 16))

print("\n8-bit unsigned lower byte:")
lower_byte = number % 256
print(lower_byte)
print(format(lower_byte, "08b"))

print("\n16-bit two's complement:")
print(fixed_width_twos_complement(number, 16))

print("\nHexadecimal byte representation:")
print(number.to_bytes(4, "big").hex(" ").upper())


# ============================================================
# 123. DIRECT RELATIONSHIP BETWEEN REPRESENTATIONS
# ============================================================

print("\n" + "=" * 72)
print("RELATIONSHIP BETWEEN MAJOR REPRESENTATIONS")
print("=" * 72)

print("""
A single numerical value may be represented in several ways.

For example:

    Decimal:
        255

    Binary:
        11111111

    Octal:
        377

    Hexadecimal:
        FF

The value is the same.

The notation changes.

When fixed-width signed representation is introduced, interpretation
also becomes important.

For example, the same eight bits:

    11111111

can mean:

    255 unsigned

or:

    -1 signed two's complement.

Thus numerical value, representation, width, and interpretation must
be distinguished carefully.
""")


# ============================================================
# 124. END OF SCRIPT
# ============================================================

print("\n" + "=" * 72)
print("END OF NUMBER SYSTEM STUDY SCRIPT")
print("=" * 72)
