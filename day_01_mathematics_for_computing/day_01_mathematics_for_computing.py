# ============================================================
# MATHEMATICAL FOUNDATIONS
# ============================================================
#
# Topics Covered:
# 1. Numbers
# 2. Number systems
# 3. Arithmetic
# 4. Mathematical notation
# 5. Expressions
# 6. Equations
# 7. Variables
# 8. Constants
# 9. Operators
# 10. Order of operations
# 11. Integer arithmetic
# 12. Floating-point arithmetic
# 13. Exact arithmetic
# 14. Fractions
# 15. Powers and roots
# 16. Absolute values
# 17. Comparisons
# 18. Boolean mathematics
# 19. Algebraic thinking
# 20. Expressions vs equations
# 21. Rearranging equations
# 22. Function notation
# 23. Mathematical notation vs Python syntax
# 24. Numerical precision
# 25. Overflow and large numbers
# 26. Modulo arithmetic
# 27. Advanced operator behavior
# 28. Mathematical reasoning exercises
# 29. Computing-oriented examples
#
# Recommended environment:
# Python 3.x
# Jupyter Notebook
#
# ============================================================


print("=" * 70)
print("MATHEMATICAL FOUNDATIONS")
print("=" * 70)

print("""
This lesson builds the mathematical language required for computing.

We will start with:
    numbers
    arithmetic
    notation
    variables
    constants
    operators

Then we will gradually move toward:
    algebra
    equations
    functions
    numerical precision
    modular arithmetic
    computational reasoning

The goal is not simply to perform calculations.

The goal is to understand how mathematics is represented,
evaluated, manipulated, and implemented in a computer.
""")


# ============================================================
# 1. WHAT IS MATHEMATICS?
# ============================================================

print("\n" + "=" * 70)
print("1. WHAT IS MATHEMATICS?")
print("=" * 70)

print("""
Mathematics is a formal system used to describe:

    quantity
    structure
    relationships
    patterns
    change
    space
    uncertainty
    logic

Computing depends heavily on mathematics.

Examples:

    Algorithms        -> mathematical procedures
    Machine Learning  -> linear algebra + probability + calculus
    Cryptography      -> number theory
    Databases         -> logic + set theory
    Computer Graphics -> geometry + linear algebra
    Statistics        -> probability + mathematical analysis
    Optimization      -> calculus + linear algebra
""")


# ============================================================
# 2. WHAT IS A NUMBER?
# ============================================================

print("\n" + "=" * 70)
print("2. NUMBERS")
print("=" * 70)

print("""
A number represents a quantity or mathematical value.

Examples:

    0
    1
    2
    10
    -5
    3.14
    1/2

Numbers can belong to different mathematical sets.
""")


# ============================================================
# 3. NATURAL NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("3. NATURAL NUMBERS")
print("=" * 70)

print("""
Natural numbers are counting numbers.

Depending on convention:

    N = {1, 2, 3, 4, 5, ...}

Some mathematical conventions include zero:

    N = {0, 1, 2, 3, 4, ...}

Python representation:
""")

natural_numbers = list(range(1, 11))

print("Natural numbers:", natural_numbers)


# ============================================================
# 4. WHOLE NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("4. WHOLE NUMBERS")
print("=" * 70)

print("""
Whole numbers can be thought of as:

    0, 1, 2, 3, 4, ...

They contain zero and positive integers.
""")

whole_numbers = list(range(0, 11))

print("Whole numbers:", whole_numbers)


# ============================================================
# 5. INTEGERS
# ============================================================

print("\n" + "=" * 70)
print("5. INTEGERS")
print("=" * 70)

print("""
Integers include:

    negative numbers
    zero
    positive numbers

Examples:

    ..., -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, ...

Mathematical notation:

    Z

Python:
""")

integers = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]

print(integers)


# ============================================================
# 6. RATIONAL NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("6. RATIONAL NUMBERS")
print("=" * 70)

print("""
A rational number can be written as:

        p
    x = -
        q

where:

    p and q are integers
    q != 0

Examples:

    1/2
    3/4
    -5/7
    10/3

Every integer is also rational because:

    5 = 5/1
""")

from fractions import Fraction

r1 = Fraction(1, 2)
r2 = Fraction(3, 4)
r3 = Fraction(-5, 7)

print("1/2 =", r1)
print("3/4 =", r2)
print("-5/7 =", r3)


# ============================================================
# 7. IRRATIONAL NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("7. IRRATIONAL NUMBERS")
print("=" * 70)

print("""
Irrational numbers cannot be represented as:

        p
        -
        q

where p and q are integers.

Examples:

    sqrt(2)
    pi
    e

Their decimal representations do not terminate
and do not repeat periodically.
""")

import math

print("sqrt(2) =", math.sqrt(2))
print("pi      =", math.pi)
print("e       =", math.e)


# ============================================================
# 8. REAL NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("8. REAL NUMBERS")
print("=" * 70)

print("""
Real numbers include:

    rational numbers
    irrational numbers

Examples:

    -10
    0
    2
    1/2
    sqrt(2)
    pi

The real number system is commonly represented by:

    R
""")


# ============================================================
# 9. COMPLEX NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("9. COMPLEX NUMBERS")
print("=" * 70)

print("""
Complex numbers have the form:

    a + bi

where:

    a = real part
    b = imaginary coefficient
    i = sqrt(-1)

Python uses j instead of i.
""")

z = 3 + 4j

print("Complex number:", z)
print("Real part:", z.real)
print("Imaginary part:", z.imag)

print("""
For:

    z = 3 + 4i

we have:

    Re(z) = 3
    Im(z) = 4
""")


# ============================================================
# 10. NUMBER TYPES IN PYTHON
# ============================================================

print("\n" + "=" * 70)
print("10. PYTHON NUMBER TYPES")
print("=" * 70)

a = 10
b = 3.14
c = 2 + 3j

print("a =", a, "| type =", type(a))
print("b =", b, "| type =", type(b))
print("c =", c, "| type =", type(c))


# ============================================================
# 11. ARITHMETIC
# ============================================================

print("\n" + "=" * 70)
print("11. ARITHMETIC")
print("=" * 70)

print("""
Arithmetic deals with operations on numbers.

Basic arithmetic operations:

    Addition
    Subtraction
    Multiplication
    Division
    Exponentiation
    Modulo
""")

x = 20
y = 6

print("x =", x)
print("y =", y)

print("Addition       :", x + y)
print("Subtraction    :", x - y)
print("Multiplication :", x * y)
print("Division       :", x / y)
print("Power          :", x ** y)
print("Modulo         :", x % y)


# ============================================================
# 12. ADDITION
# ============================================================

print("\n" + "=" * 70)
print("12. ADDITION")
print("=" * 70)

print("""
Addition combines quantities.

Mathematical notation:

    a + b

Example:

    5 + 3 = 8
""")

print(5 + 3)
print(100 + 250)
print(-5 + 10)


# ============================================================
# 13. SUBTRACTION
# ============================================================

print("\n" + "=" * 70)
print("13. SUBTRACTION")
print("=" * 70)

print("""
Subtraction represents difference.

    a - b

Example:

    10 - 4 = 6
""")

print(10 - 4)
print(4 - 10)
print(-5 - 3)


# ============================================================
# 14. MULTIPLICATION
# ============================================================

print("\n" + "=" * 70)
print("14. MULTIPLICATION")
print("=" * 70)

print("""
Multiplication represents repeated addition
and scaling.

    a * b

Example:

    4 * 3 = 12
""")

print(4 * 3)
print(7 * 8)
print(-5 * 4)


# ============================================================
# 15. DIVISION
# ============================================================

print("\n" + "=" * 70)
print("15. DIVISION")
print("=" * 70)

print("""
Division determines how many times one quantity
fits into another.

    a / b

provided b != 0.

Example:

    10 / 2 = 5
""")

print(10 / 2)
print(7 / 2)
print(20 / 4)


# ============================================================
# 16. INTEGER DIVISION
# ============================================================

print("\n" + "=" * 70)
print("16. INTEGER / FLOOR DIVISION")
print("=" * 70)

print("""
Python provides:

    //

This performs floor division.

Example:

    7 // 2 = 3

because:

    7 / 2 = 3.5

and floor(3.5) = 3.
""")

print("7 / 2  =", 7 / 2)
print("7 // 2 =", 7 // 2)

print("-7 / 2  =", -7 / 2)
print("-7 // 2 =", -7 // 2)

print("""
Important:

Floor division rounds toward negative infinity,
not simply toward zero.

Therefore:

    -7 // 2 = -4
""")


# ============================================================
# 17. MODULO
# ============================================================

print("\n" + "=" * 70)
print("17. MODULO")
print("=" * 70)

print("""
Modulo gives the remainder after division.

    a % b

Example:

    17 % 5 = 2

because:

    17 = 5 * 3 + 2
""")

print("17 % 5 =", 17 % 5)
print("20 % 4 =", 20 % 4)
print("25 % 7 =", 25 % 7)


# ============================================================
# 18. MODULO AND EVEN/ODD
# ============================================================

print("\n" + "=" * 70)
print("18. EVEN AND ODD NUMBERS")
print("=" * 70)

print("""
An integer n is even if:

    n % 2 == 0

An integer n is odd if:

    n % 2 == 1
""")

numbers = range(1, 11)

for number in numbers:
    if number % 2 == 0:
        print(number, "is even")
    else:
        print(number, "is odd")


# ============================================================
# 19. POWERS
# ============================================================

print("\n" + "=" * 70)
print("19. EXPONENTIATION")
print("=" * 70)

print("""
Exponentiation represents repeated multiplication.

    a^n

Example:

    2^5 = 32

Python:

    2 ** 5
""")

print("2^5 =", 2 ** 5)
print("3^4 =", 3 ** 4)
print("10^3 =", 10 ** 3)


# ============================================================
# 20. NEGATIVE EXPONENTS
# ============================================================

print("\n" + "=" * 70)
print("20. NEGATIVE EXPONENTS")
print("=" * 70)

print("""
A negative exponent means reciprocal.

    a^(-n) = 1 / a^n

Example:

    2^(-3)
    = 1 / 2^3
    = 1/8
""")

print("2^-3 =", 2 ** -3)
print("10^-2 =", 10 ** -2)


# ============================================================
# 21. FRACTIONAL EXPONENTS
# ============================================================

print("\n" + "=" * 70)
print("21. FRACTIONAL EXPONENTS")
print("=" * 70)

print("""
Fractional powers represent roots.

    a^(1/2) = sqrt(a)

    a^(1/3) = cube_root(a)
""")

print("sqrt(25) =", 25 ** (1 / 2))
print("cube root of 27 =", 27 ** (1 / 3))


# ============================================================
# 22. ROOTS
# ============================================================

print("\n" + "=" * 70)
print("22. ROOTS")
print("=" * 70)

print("""
A square root of x is a number r such that:

    r^2 = x

Example:

    sqrt(49) = 7

because:

    7^2 = 49
""")

print("sqrt(49) =", math.sqrt(49))
print("sqrt(100) =", math.sqrt(100))


# ============================================================
# 23. ABSOLUTE VALUE
# ============================================================

print("\n" + "=" * 70)
print("23. ABSOLUTE VALUE")
print("=" * 70)

print("""
Absolute value represents distance from zero.

    |5| = 5
    |-5| = 5

Python:

    abs()
""")

print(abs(5))
print(abs(-5))
print(abs(-100))


# ============================================================
# 24. MATHEMATICAL NOTATION
# ============================================================

print("\n" + "=" * 70)
print("24. MATHEMATICAL NOTATION")
print("=" * 70)

print("""
Mathematics uses symbols to express ideas compactly.

Examples:

    x + y
    2x
    x^2
    x / y
    x <= y
    x != y

Mathematical notation is not exactly the same
as programming syntax.
""")

print("""
Mathematics:

    2x

Python:

    2 * x

Mathematics:

    x^2

Python:

    x ** 2
""")


# ============================================================
# 25. EXPRESSIONS
# ============================================================

print("\n" + "=" * 70)
print("25. EXPRESSIONS")
print("=" * 70)

print("""
An expression is a combination of values,
variables, operators, and function calls
that produces a value.

Examples:

    5 + 3
    x * 10
    (a + b) / 2
    x ** 2
""")

x = 10

expression1 = 5 + 3
expression2 = x * 10
expression3 = (x + 5) / 2
expression4 = x ** 2

print(expression1)
print(expression2)
print(expression3)
print(expression4)


# ============================================================
# 26. EXPRESSIONS HAVE VALUES
# ============================================================

print("\n" + "=" * 70)
print("26. EXPRESSIONS PRODUCE VALUES")
print("=" * 70)

print("""
Consider:

    10 + 20

The expression evaluates to:

    30

Similarly:

    5 * 7

evaluates to:

    35
""")

print(10 + 20)
print(5 * 7)


# ============================================================
# 27. VARIABLES
# ============================================================

print("\n" + "=" * 70)
print("27. VARIABLES")
print("=" * 70)

print("""
A variable is a named reference to a value.

Mathematics:

    x = 10

Python:

    x = 10
""")

x = 10

print("x =", x)


# ============================================================
# 28. VARIABLE REASSIGNMENT
# ============================================================

print("\n" + "=" * 70)
print("28. VARIABLE REASSIGNMENT")
print("=" * 70)

x = 10

print("Initial x:", x)

x = 20

print("New x:", x)

print("""
The statement:

    x = 20

does not mean mathematical equality
in the same sense as an equation.

In Python, it means:

    assign the value 20 to x.
""")


# ============================================================
# 29. MULTIPLE VARIABLES
# ============================================================

print("\n" + "=" * 70)
print("29. MULTIPLE VARIABLES")
print("=" * 70)

length = 10
width = 5

area = length * width

print("Length:", length)
print("Width :", width)
print("Area  :", area)


# ============================================================
# 30. CONSTANTS
# ============================================================

print("\n" + "=" * 70)
print("30. CONSTANTS")
print("=" * 70)

print("""
A mathematical constant has a fixed value.

Examples:

    pi
    e
    sqrt(2)

Python does not enforce immutable constants
through a special constant keyword.

Conventionally, uppercase names are used.
""")

PI = math.pi
E = math.e

print("PI =", PI)
print("E  =", E)


# ============================================================
# 31. MATHEMATICAL CONSTANTS VS VARIABLES
# ============================================================

print("\n" + "=" * 70)
print("31. CONSTANTS VS VARIABLES")
print("=" * 70)

print("""
Variable:

    x = 10

The value associated with x can be changed.

Constant convention:

    PI = 3.14159...

The mathematical value of pi does not change.

In Python, uppercase naming communicates intent.
""")


# ============================================================
# 32. OPERATORS
# ============================================================

print("\n" + "=" * 70)
print("32. OPERATORS")
print("=" * 70)

print("""
Operators perform operations.

Arithmetic operators:

    +
    -
    *
    /
    //
    %
    **

Comparison operators:

    ==
    !=
    >
    <
    >=
    <=

Logical operators:

    and
    or
    not
""")


# ============================================================
# 33. COMPARISON OPERATORS
# ============================================================

print("\n" + "=" * 70)
print("33. COMPARISON OPERATORS")
print("=" * 70)

a = 10
b = 20

print("a == b:", a == b)
print("a != b:", a != b)
print("a > b :", a > b)
print("a < b :", a < b)
print("a >= b:", a >= b)
print("a <= b:", a <= b)


# ============================================================
# 34. BOOLEAN VALUES
# ============================================================

print("\n" + "=" * 70)
print("34. BOOLEAN MATHEMATICS")
print("=" * 70)

print("""
A Boolean value has two possible states:

    True
    False

Boolean logic is fundamental to:

    programming
    algorithms
    digital circuits
    databases
    artificial intelligence
""")

print(10 > 5)
print(10 < 5)


# ============================================================
# 35. LOGICAL OPERATORS
# ============================================================

print("\n" + "=" * 70)
print("35. LOGICAL OPERATORS")
print("=" * 70)

age = 25
has_id = True

print("Age >= 18:", age >= 18)
print("Has ID:", has_id)

print("Eligible:",
      age >= 18 and has_id)


# ============================================================
# 36. ORDER OF OPERATIONS
# ============================================================

print("\n" + "=" * 70)
print("36. ORDER OF OPERATIONS")
print("=" * 70)

print("""
Mathematics follows rules for evaluating expressions.

A common hierarchy is:

    1. Parentheses
    2. Exponents
    3. Multiplication and division
    4. Addition and subtraction

Example:

    2 + 3 * 4

First:

    3 * 4 = 12

Then:

    2 + 12 = 14
""")

print("2 + 3 * 4 =", 2 + 3 * 4)


# ============================================================
# 37. PARENTHESES
# ============================================================

print("\n" + "=" * 70)
print("37. PARENTHESES")
print("=" * 70)

print("""
Parentheses explicitly control evaluation.

Compare:

    2 + 3 * 4

with:

    (2 + 3) * 4
""")

print("2 + 3 * 4 =", 2 + 3 * 4)
print("(2 + 3) * 4 =", (2 + 3) * 4)


# ============================================================
# 38. EXPONENT PRECEDENCE
# ============================================================

print("\n" + "=" * 70)
print("38. EXPONENT PRECEDENCE")
print("=" * 70)

print("""
Exponentiation has higher precedence than
multiplication.

Example:

    2 + 3 ** 2

First:

    3 ** 2 = 9

Then:

    2 + 9 = 11
""")

print(2 + 3 ** 2)


# ============================================================
# 39. MIXED EXPRESSION
# ============================================================

print("\n" + "=" * 70)
print("39. COMPLEX EXPRESSION")
print("=" * 70)

expression = (5 + 3) ** 2 / (4 - 2)

print("Expression:")
print("(5 + 3) ** 2 / (4 - 2)")
print("Result:", expression)


# ============================================================
# 40. LEFT-TO-RIGHT EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("40. LEFT-TO-RIGHT EVALUATION")
print("=" * 70)

print("""
Operators with the same precedence are generally
evaluated according to their associativity.

For multiplication and division:

    20 / 5 * 2

is evaluated left-to-right:

    (20 / 5) * 2
    = 4 * 2
    = 8
""")

print(20 / 5 * 2)


# ============================================================
# 41. SUBTRACTION ASSOCIATIVITY
# ============================================================

print("\n" + "=" * 70)
print("41. SUBTRACTION")
print("=" * 70)

print("""
Subtraction is not associative.

Compare:

    (10 - 5) - 2 = 3

and:

    10 - (5 - 2) = 7
""")

print("(10 - 5) - 2 =", (10 - 5) - 2)
print("10 - (5 - 2) =", 10 - (5 - 2))


# ============================================================
# 42. DIVISION ASSOCIATIVITY
# ============================================================

print("\n" + "=" * 70)
print("42. DIVISION")
print("=" * 70)

print("""
Division is also not associative.

    (100 / 10) / 2 = 5

while:

    100 / (10 / 2) = 20
""")

print("(100 / 10) / 2 =", (100 / 10) / 2)
print("100 / (10 / 2) =", 100 / (10 / 2))


# ============================================================
# 43. ALGEBRAIC EXPRESSIONS
# ============================================================

print("\n" + "=" * 70)
print("43. ALGEBRAIC EXPRESSIONS")
print("=" * 70)

print("""
Algebra uses symbols to represent unknown
or variable quantities.

Example:

    2x + 5

If:

    x = 10

then:

    2(10) + 5
    = 20 + 5
    = 25
""")

x = 10

result = 2 * x + 5

print("2x + 5 =", result)


# ============================================================
# 44. ALGEBRAIC TRANSLATION
# ============================================================

print("\n" + "=" * 70)
print("44. TRANSLATING MATHEMATICS INTO PYTHON")
print("=" * 70)

print("""
Mathematics       Python

x + y             x + y
x - y             x - y
xy                x * y
x/y               x / y
x^2               x ** 2
sqrt(x)           math.sqrt(x)
|x|               abs(x)
""")


# ============================================================
# 45. EQUATIONS
# ============================================================

print("\n" + "=" * 70)
print("45. EQUATIONS")
print("=" * 70)

print("""
An equation states that two expressions are equal.

Example:

    2x + 5 = 15

The goal can be to determine x.

Subtract 5:

    2x = 10

Divide by 2:

    x = 5
""")

x = 5

print("Checking:")
print(2 * x + 5)
print("Expected:", 15)


# ============================================================
# 46. EQUATION VS EXPRESSION
# ============================================================

print("\n" + "=" * 70)
print("46. EXPRESSION VS EQUATION")
print("=" * 70)

print("""
Expression:

    2x + 5

It produces a value when x is known.

Equation:

    2x + 5 = 15

It asserts equality and can be solved for x.

This distinction is extremely important.
""")


# ============================================================
# 47. SOLVING LINEAR EQUATIONS
# ============================================================

print("\n" + "=" * 70)
print("47. LINEAR EQUATION")
print("=" * 70)

print("""
General linear equation:

    ax + b = c

Solving:

    ax = c - b

Therefore:

    x = (c - b) / a

provided:

    a != 0
""")

a = 4
b = 8
c = 28

x = (c - b) / a

print("Equation:")
print(f"{a}x + {b} = {c}")
print("x =", x)


# ============================================================
# 48. VERIFYING AN EQUATION
# ============================================================

print("\n" + "=" * 70)
print("48. VERIFYING SOLUTIONS")
print("=" * 70)

left_side = a * x + b
right_side = c

print("Left side :", left_side)
print("Right side:", right_side)
print("Solution valid:", left_side == right_side)


# ============================================================
# 49. EQUATION WITH TWO VARIABLES
# ============================================================

print("\n" + "=" * 70)
print("49. TWO VARIABLES")
print("=" * 70)

print("""
Consider:

    x + y = 10

There are many solutions:

    x=1, y=9
    x=2, y=8
    x=3, y=7
    ...

One equation with two unknowns generally
does not uniquely determine both variables.
""")

x = 3
y = 7

print("x + y =", x + y)


# ============================================================
# 50. FUNCTIONS
# ============================================================

print("\n" + "=" * 70)
print("50. FUNCTION NOTATION")
print("=" * 70)

print("""
A function maps inputs to outputs.

Mathematical notation:

    f(x) = x^2 + 2x + 1

Python:
""")

def f(x):
    return x ** 2 + 2 * x + 1


for value in [0, 1, 2, 5]:
    print(f"f({value}) =", f(value))


# ============================================================
# 51. FUNCTION INPUT AND OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("51. FUNCTION INPUTS AND OUTPUTS")
print("=" * 70)

print("""
For:

    f(x) = x^2

Input:

    x = 5

Output:

    f(5) = 25
""")

def square(x):
    return x ** 2

print(square(5))


# ============================================================
# 52. MATHEMATICAL CONSTANTS
# ============================================================

print("\n" + "=" * 70)
print("52. IMPORTANT MATHEMATICAL CONSTANTS")
print("=" * 70)

print("""
Common constants include:

    pi
    e
    sqrt(2)
    sqrt(3)
    golden ratio

These appear throughout mathematics,
science, engineering, and computing.
""")

golden_ratio = (1 + math.sqrt(5)) / 2

print("pi =", math.pi)
print("e =", math.e)
print("sqrt(2) =", math.sqrt(2))
print("golden ratio =", golden_ratio)


# ============================================================
# 53. ROUNDING
# ============================================================

print("\n" + "=" * 70)
print("53. ROUNDING")
print("=" * 70)

print("""
Rounding converts a number to a chosen precision.

Python:

    round(number)
    round(number, digits)
""")

value = 3.141592653589793

print("Original:", value)
print("2 decimals:", round(value, 2))
print("4 decimals:", round(value, 4))


# ============================================================
# 54. FLOATING-POINT NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("54. FLOATING-POINT NUMBERS")
print("=" * 70)

print("""
Computers commonly represent real numbers using
floating-point representation.

This is efficient but not always exact.

Example:
""")

print(0.1 + 0.2)

print("""
You may see:

    0.30000000000000004

instead of exactly:

    0.3

This happens because many decimal fractions cannot
be represented exactly in binary floating-point.
""")


# ============================================================
# 55. FLOATING-POINT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("55. FLOATING-POINT COMPARISON")
print("=" * 70)

a = 0.1 + 0.2
b = 0.3

print("a == b:", a == b)

print("""
For numerical computation, tolerance-based comparison
is often safer.
""")

print("Difference:", abs(a - b))
print("Close enough:", math.isclose(a, b))


# ============================================================
# 56. EXACT FRACTION ARITHMETIC
# ============================================================

print("\n" + "=" * 70)
print("56. EXACT FRACTIONS")
print("=" * 70)

f1 = Fraction(1, 10)
f2 = Fraction(2, 10)

result = f1 + f2

print("1/10 + 2/10 =", result)

print("""
Fractions are useful when exact rational arithmetic
is required.
""")


# ============================================================
# 57. DECIMAL ARITHMETIC
# ============================================================

print("\n" + "=" * 70)
print("57. DECIMAL ARITHMETIC")
print("=" * 70)

from decimal import Decimal

d1 = Decimal("0.1")
d2 = Decimal("0.2")

print(d1 + d2)

print("""
Decimal can be useful for applications such as:

    financial calculations
    accounting
    monetary systems

where decimal semantics matter.
""")


# ============================================================
# 58. INTEGER PRECISION
# ============================================================

print("\n" + "=" * 70)
print("58. LARGE INTEGERS")
print("=" * 70)

large_number = 10 ** 100

print("10^100 =")
print(large_number)

print("""
Python integers can represent arbitrarily large integers
subject to available memory.

This differs from fixed-width integer types commonly
used in lower-level languages and hardware.
""")


# ============================================================
# 59. SCIENTIFIC NOTATION
# ============================================================

print("\n" + "=" * 70)
print("59. SCIENTIFIC NOTATION")
print("=" * 70)

print("""
Scientific notation expresses numbers as:

    a x 10^n

Example:

    3 x 10^8

Python:
""")

speed_of_light = 3e8

print(speed_of_light)


# ============================================================
# 60. NEGATIVE NUMBERS
# ============================================================

print("\n" + "=" * 70)
print("60. NEGATIVE NUMBERS")
print("=" * 70)

print("""
Negative numbers represent quantities below a reference point.

Examples:

    temperature
    debt
    coordinate positions
    changes
""")

temperature = -5
balance_change = -100

print("Temperature:", temperature)
print("Balance change:", balance_change)


# ============================================================
# 61. NUMBER LINE
# ============================================================

print("\n" + "=" * 70)
print("61. NUMBER LINE")
print("=" * 70)

print("""
On a number line:

    negative numbers < zero < positive numbers

For example:

    -5 < -2 < 0 < 3 < 10
""")

numbers = [-5, -2, 0, 3, 10]

for n in numbers:
    print(n)


# ============================================================
# 62. INEQUALITIES
# ============================================================

print("\n" + "=" * 70)
print("62. INEQUALITIES")
print("=" * 70)

print("""
Inequalities express relationships such as:

    x > 5
    x < 10
    x >= 3
    x <= 20
""")

x = 7

print("x > 5 :", x > 5)
print("x < 10:", x < 10)


# ============================================================
# 63. CHAINED COMPARISONS
# ============================================================

print("\n" + "=" * 70)
print("63. CHAINED COMPARISONS")
print("=" * 70)

x = 7

print(5 < x < 10)

print("""
Python allows:

    5 < x < 10

which corresponds mathematically to:

    5 < x AND x < 10
""")


# ============================================================
# 64. DISTRIBUTIVE PROPERTY
# ============================================================

print("\n" + "=" * 70)
print("64. DISTRIBUTIVE PROPERTY")
print("=" * 70)

print("""
Mathematical property:

    a(b + c) = ab + ac
""")

a = 5
b = 3
c = 7

left = a * (b + c)
right = a * b + a * c

print("Left :", left)
print("Right:", right)
print("Equal:", left == right)


# ============================================================
# 65. COMMUTATIVE PROPERTY
# ============================================================

print("\n" + "=" * 70)
print("65. COMMUTATIVE PROPERTY")
print("=" * 70)

print("""
Addition:

    a + b = b + a

Multiplication:

    a * b = b * a
""")

a = 7
b = 9

print(a + b == b + a)
print(a * b == b * a)


# ============================================================
# 66. ASSOCIATIVE PROPERTY
# ============================================================

print("\n" + "=" * 70)
print("66. ASSOCIATIVE PROPERTY")
print("=" * 70)

print("""
Addition:

    (a + b) + c = a + (b + c)

Multiplication:

    (a * b) * c = a * (b * c)
""")

a = 2
b = 3
c = 4

print((a + b) + c == a + (b + c))
print((a * b) * c == a * (b * c))


# ============================================================
# 67. IDENTITY ELEMENTS
# ============================================================

print("\n" + "=" * 70)
print("67. IDENTITY ELEMENTS")
print("=" * 70)

print("""
For addition:

    a + 0 = a

Therefore 0 is the additive identity.

For multiplication:

    a * 1 = a

Therefore 1 is the multiplicative identity.
""")

a = 25

print(a + 0)
print(a * 1)


# ============================================================
# 68. ZERO PROPERTY
# ============================================================

print("\n" + "=" * 70)
print("68. ZERO PROPERTY")
print("=" * 70)

print("""
For multiplication:

    a * 0 = 0
""")

print(100 * 0)
print(-500 * 0)


# ============================================================
# 69. ORDER OF OPERATIONS EXERCISES
# ============================================================

print("\n" + "=" * 70)
print("69. ORDER OF OPERATIONS EXERCISES")
print("=" * 70)

expressions = [
    "2 + 3 * 4",
    "(2 + 3) * 4",
    "2 ** 3 + 4",
    "10 - 2 * 3",
    "(10 - 2) * 3",
    "100 / 5 * 2",
    "100 / (5 * 2)",
]

for expression in expressions:
    print(expression, "=", eval(expression))


# ============================================================
# 70. AVOIDING EVAL IN REAL APPLICATIONS
# ============================================================

print("\n" + "=" * 70)
print("70. IMPORTANT PYTHON NOTE")
print("=" * 70)

print("""
The eval() function was used above only for demonstration.

Do NOT use eval() on untrusted user input.

For example, an application should not blindly execute:

    eval(user_input)

because this can create serious security problems.

In real programs, construct expressions safely
using explicit operations or specialized parsers.
""")


# ============================================================
# 71. PEMDAS / BODMAS
# ============================================================

print("\n" + "=" * 70)
print("71. PEMDAS / BODMAS")
print("=" * 70)

print("""
Different educational traditions use different acronyms.

PEMDAS:

    Parentheses
    Exponents
    Multiplication
    Division
    Addition
    Subtraction

BODMAS:

    Brackets
    Orders
    Division
    Multiplication
    Addition
    Subtraction

The important idea is the precedence structure,
not the acronym itself.
""")


# ============================================================
# 72. OPERATOR PRECEDENCE IN PYTHON
# ============================================================

print("\n" + "=" * 70)
print("72. PYTHON OPERATOR PRECEDENCE")
print("=" * 70)

print("""
A simplified precedence hierarchy is:

    parentheses
    exponentiation
    unary + and -
    multiplication/division/floor/modulo
    addition/subtraction
    comparisons
    not
    and
    or

When in doubt, use parentheses.
""")

result = 2 + 3 * 4 ** 2

print("2 + 3 * 4 ** 2 =", result)


# ============================================================
# 73. UNARY OPERATORS
# ============================================================

print("\n" + "=" * 70)
print("73. UNARY OPERATORS")
print("=" * 70)

x = 5

print("+x =", +x)
print("-x =", -x)

print("""
Unary operators act on one operand.

Examples:

    +x
    -x
    not x
""")


# ============================================================
# 74. COMPOUND ASSIGNMENT
# ============================================================

print("\n" + "=" * 70)
print("74. COMPOUND ASSIGNMENT")
print("=" * 70)

x = 10

x += 5
print("x += 5 ->", x)

x -= 2
print("x -= 2 ->", x)

x *= 3
print("x *= 3 ->", x)

x /= 2
print("x /= 2 ->", x)

print("""
These are shorthand forms:

    x += 5
    means:
    x = x + 5
""")


# ============================================================
# 75. TYPE CONVERSION
# ============================================================

print("\n" + "=" * 70)
print("75. TYPE CONVERSION")
print("=" * 70)

integer_value = 10
float_value = float(integer_value)

print(integer_value, type(integer_value))
print(float_value, type(float_value))

print("""
Common conversions:

    int()
    float()
    complex()
""")


# ============================================================
# 76. INTEGER TO FLOAT
# ============================================================

print("\n" + "=" * 70)
print("76. INTEGER AND FLOAT INTERACTION")
print("=" * 70)

print(type(10))
print(type(10.0))

print(10 + 2.5)
print(type(10 + 2.5))


# ============================================================
# 77. MATHEMATICAL VALIDITY
# ============================================================

print("\n" + "=" * 70)
print("77. MATHEMATICAL VALIDITY")
print("=" * 70)

print("""
Not every expression is mathematically valid.

Example:

    10 / 0

Division by zero is undefined.
""")

try:
    print(10 / 0)
except ZeroDivisionError:
    print("Cannot divide by zero.")


# ============================================================
# 78. DOMAIN RESTRICTIONS
# ============================================================

print("\n" + "=" * 70)
print("78. DOMAIN RESTRICTIONS")
print("=" * 70)

print("""
Mathematical expressions may have restrictions.

Example:

    f(x) = 1/x

requires:

    x != 0

because division by zero is undefined.
""")

def reciprocal(x):
    if x == 0:
        raise ValueError("x cannot be zero")
    return 1 / x

print(reciprocal(5))


# ============================================================
# 79. SQUARE ROOT DOMAIN
# ============================================================

print("\n" + "=" * 70)
print("79. SQUARE ROOT DOMAIN")
print("=" * 70)

print("""
Within the real number system:

    sqrt(x)

requires:

    x >= 0

For negative values, complex numbers may be required.
""")

print(math.sqrt(25))


# ============================================================
# 80. COMPLEX SQUARE ROOT
# ============================================================

print("\n" + "=" * 70)
print("80. COMPLEX NUMBERS AND ROOTS")
print("=" * 70)

print("""
Python's cmath module can work with complex square roots.
""")

import cmath

print("sqrt(-1) =", cmath.sqrt(-1))


# ============================================================
# 81. ALGEBRAIC SUBSTITUTION
# ============================================================

print("\n" + "=" * 70)
print("81. SUBSTITUTION")
print("=" * 70)

print("""
Suppose:

    x = 3
    y = 5

and:

    2x + y^2

Substitute:

    2(3) + 5^2
    = 6 + 25
    = 31
""")

x = 3
y = 5

result = 2 * x + y ** 2

print(result)


# ============================================================
# 82. PERIMETER
# ============================================================

print("\n" + "=" * 70)
print("82. COMPUTING EXAMPLE: PERIMETER")
print("=" * 70)

length = 10
width = 5

perimeter = 2 * (length + width)

print("Perimeter:", perimeter)


# ============================================================
# 83. AREA
# ============================================================

print("\n" + "=" * 70)
print("83. COMPUTING EXAMPLE: AREA")
print("=" * 70)

area = length * width

print("Area:", area)


# ============================================================
# 84. CIRCLE AREA")
# ============================================================

print("\n" + "=" * 70)
print("84. CIRCLE AREA")
print("=" * 70)

radius = 5

circle_area = math.pi * radius ** 2

print("Radius:", radius)
print("Area:", circle_area)


# ============================================================
# 85. DISTANCE FORMULA
# ============================================================

print("\n" + "=" * 70)
print("85. DISTANCE BETWEEN TWO POINTS")
print("=" * 70)

print("""
For points:

    (x1, y1)
    (x2, y2)

distance:

    d = sqrt((x2-x1)^2 + (y2-y1)^2)
""")

x1, y1 = 1, 2
x2, y2 = 4, 6

distance = math.sqrt(
    (x2 - x1) ** 2 +
    (y2 - y1) ** 2
)

print("Distance:", distance)


# ============================================================
# 86. AVERAGE
# ============================================================

print("\n" + "=" * 70)
print("86. ARITHMETIC MEAN")
print("=" * 70)

print("""
For n values:

    x1, x2, ..., xn

mean:

          x1 + x2 + ... + xn
    mean = -----------------
                  n
""")

values = [10, 20, 30, 40, 50]

mean = sum(values) / len(values)

print("Values:", values)
print("Mean:", mean)


# ============================================================
# 87. PERCENTAGES
# ============================================================

print("\n" + "=" * 70)
print("87. PERCENTAGES")
print("=" * 70)

print("""
Percentage means "per hundred".

    25% = 25 / 100 = 0.25

Example:

    20% of 500

    = 0.20 * 500
    = 100
""")

percentage = 20 / 100
result = percentage * 500

print(result)


# ============================================================
# 88. PERCENTAGE CHANGE
# ============================================================

print("\n" + "=" * 70)
print("88. PERCENTAGE CHANGE")
print("=" * 70)

old_value = 100
new_value = 125

percentage_change = (
    (new_value - old_value) /
    old_value
) * 100

print("Percentage change:", percentage_change, "%")


# ============================================================
# 89. RATIOS
# ============================================================

print("\n" + "=" * 70)
print("89. RATIOS")
print("=" * 70)

print("""
A ratio compares quantities.

Example:

    2 : 3

means:

    2/3
""")

a = 2
b = 3

ratio = a / b

print("Ratio as decimal:", ratio)


# ============================================================
# 90. PROPORTIONS
# ============================================================

print("\n" + "=" * 70)
print("90. PROPORTIONS")
print("=" * 70)

print("""
A proportion states that two ratios are equal.

    a/b = c/d

Cross multiplication gives:

    ad = bc
""")

a = 2
b = 3
c = 4
d = 6

print(a * d == b * c)


# ============================================================
# 91. MODULAR ARITHMETIC
# ============================================================

print("\n" + "=" * 70)
print("91. MODULAR ARITHMETIC")
print("=" * 70)

print("""
Modular arithmetic works with remainders.

Example:

    17 mod 5 = 2

We can write:

    17 ≡ 2 (mod 5)

This concept is fundamental to:

    cryptography
    hashing
    cyclic systems
    computer science
    algorithms
""")

print(17 % 5)


# ============================================================
# 92. CYCLIC BEHAVIOR
# ============================================================

print("\n" + "=" * 70)
print("92. MODULO AS A CYCLE")
print("=" * 70)

print("""
Modulo can model cycles.

For a 12-hour clock:

    hour % 12

can help model repeating positions.
""")

for hour in range(1, 25):
    print(hour, "->", hour % 12)


# ============================================================
# 93. POWERFUL INTEGER EXPRESSION
# ============================================================

print("\n" + "=" * 70)
print("93. INTEGER EXPRESSION")
print("=" * 70)

a = 17
b = 5

quotient = a // b
remainder = a % b

print("a =", a)
print("b =", b)
print("quotient =", quotient)
print("remainder =", remainder)

print(
    "Verification:",
    a == b * quotient + remainder
)


# ============================================================
# 94. MATHEMATICAL INVARIANTS
# ============================================================

print("\n" + "=" * 70)
print("94. INVARIANTS")
print("=" * 70)

print("""
An invariant is a property that remains unchanged
under a specified operation or process.

Example:

    n % 2

determines parity.

Adding 2 preserves parity:

    n % 2 == (n + 2) % 2
""")

for n in range(10):
    print(
        n,
        n % 2,
        (n + 2) % 2,
        n % 2 == (n + 2) % 2
    )


# ============================================================
# 95. SYMBOLIC MATHEMATICS WITH SYMPY
# ============================================================

print("\n" + "=" * 70)
print("95. SYMBOLIC MATHEMATICS")
print("=" * 70)

print("""
Python can also perform symbolic mathematics.

A popular library is SymPy.

It can represent:

    variables
    expressions
    equations
    derivatives
    integrals
    matrices
    symbolic solutions
""")

try:
    import sympy as sp

    x = sp.symbols("x")

    expression = 2 * x + 5

    print("Expression:", expression)

    equation = sp.Eq(2 * x + 5, 15)

    print("Equation:", equation)

    solution = sp.solve(equation, x)

    print("Solution:", solution)

except ImportError:
    print("SymPy is not installed.")
    print("Install using: pip install sympy")


# ============================================================
# 96. SYMBOLIC EXPANSION
# ============================================================

print("\n" + "=" * 70)
print("96. ALGEBRAIC EXPANSION")
print("=" * 70)

try:
    import sympy as sp

    x = sp.symbols("x")

    expression = (x + 2) ** 2

    print("Original:", expression)
    print("Expanded:", sp.expand(expression))

except ImportError:
    pass


# ============================================================
# 97. SYMBOLIC FACTORIZATION
# ============================================================

print("\n" + "=" * 70)
print("97. FACTORIZATION")
print("=" * 70)

try:
    import sympy as sp

    x = sp.symbols("x")

    expression = x ** 2 + 5 * x + 6

    print("Expression:", expression)
    print("Factorized:", sp.factor(expression))

except ImportError:
    pass


# ============================================================
# 98. SYMBOLIC SIMPLIFICATION
# ============================================================

print("\n" + "=" * 70)
print("98. SIMPLIFICATION")
print("=" * 70)

try:
    import sympy as sp

    x = sp.symbols("x")

    expression = (x ** 2 - 1) / (x - 1)

    print("Expression:", expression)
    print("Simplified:", sp.simplify(expression))

except ImportError:
    pass


# ============================================================
# 99. EQUATION SYSTEM
# ============================================================

print("\n" + "=" * 70)
print("99. SYSTEM OF EQUATIONS")
print("=" * 70)

print("""
Consider:

    x + y = 10
    x - y = 2

Adding the equations:

    2x = 12

Therefore:

    x = 6

Then:

    y = 4
""")

try:
    import sympy as sp

    x, y = sp.symbols("x y")

    equations = [
        sp.Eq(x + y, 10),
        sp.Eq(x - y, 2)
    ]

    solution = sp.solve(equations, [x, y])

    print(solution)

except ImportError:
    pass


# ============================================================
# 100. MATHEMATICAL REASONING
# ============================================================

print("\n" + "=" * 70)
print("100. MATHEMATICAL REASONING")
print("=" * 70)

print("""
A good mathematical problem-solving process is:

    1. Identify known values.
    2. Identify unknown values.
    3. Identify relationships.
    4. Translate the problem into notation.
    5. Build expressions/equations.
    6. Solve.
    7. Verify.
    8. Interpret the result.
""")


# ============================================================
# 101. PRACTICE PROBLEM
# ============================================================

print("\n" + "=" * 70)
print("101. PRACTICE PROBLEM")
print("=" * 70)

print("""
A product costs 800.

A discount of 15% is applied.

Find the final price.
""")

price = 800
discount_rate = 15 / 100

discount = price * discount_rate
final_price = price - discount

print("Original price:", price)
print("Discount:", discount)
print("Final price:", final_price)


# ============================================================
# 102. REVERSE CALCULATION
# ============================================================

print("\n" + "=" * 70)
print("102. REVERSE CALCULATION")
print("=" * 70)

print("""
Suppose final price is 680 after a 15% discount.

Original price x satisfies:

    0.85x = 680

Therefore:

    x = 680 / 0.85
""")

final_price = 680
original_price = final_price / 0.85

print("Original price:", original_price)


# ============================================================
# 103. UNIT CONVERSION
# ============================================================

print("\n" + "=" * 70)
print("103. UNIT CONVERSION")
print("=" * 70)

print("""
Mathematics is also used for converting units.

Example:

    1 kilometer = 1000 meters

Therefore:

    kilometers * 1000 = meters
""")

kilometers = 5
meters = kilometers * 1000

print(kilometers, "km =", meters, "m")


# ============================================================
# 104. DIMENSIONAL THINKING
# ============================================================

print("\n" + "=" * 70)
print("104. DIMENSIONAL THINKING")
print("=" * 70)

print("""
Units provide an important sanity check.

If:

    distance = 100 km
    time = 2 hours

then:

    speed = distance / time

Units:

    km / hour

""")

distance = 100
time = 2

speed = distance / time

print("Speed:", speed, "km/h")


# ============================================================
# 105. ERROR CHECKING
# ============================================================

print("\n" + "=" * 70)
print("105. SANITY CHECKING")
print("=" * 70)

print("""
Mathematical results should be checked.

If a 100 rupee item receives a 10% discount,
a result of 500 rupees is obviously suspicious.

Good mathematical computing includes:

    calculation
    verification
    interpretation
    sanity checking
""")


# ============================================================
# 106. NESTED EXPRESSIONS
# ============================================================

print("\n" + "=" * 70)
print("106. NESTED EXPRESSIONS")
print("=" * 70)

x = 5
y = 3
z = 2

result = ((x + y) * z) ** 2

print("Result:", result)


# ============================================================
# 107. BOOLEAN ALGEBRA
# ============================================================

print("\n" + "=" * 70)
print("107. BOOLEAN ALGEBRA")
print("=" * 70)

print("""
Boolean algebra operates on:

    True
    False

Operations include:

    AND
    OR
    NOT
""")

P = True
Q = False

print("P AND Q:", P and Q)
print("P OR Q :", P or Q)
print("NOT P  :", not P)


# ============================================================
# 108. TRUTH TABLE
# ============================================================

print("\n" + "=" * 70)
print("108. TRUTH TABLE")
print("=" * 70)

print("P      Q      P AND Q      P OR Q")

for P in [False, True]:
    for Q in [False, True]:
        print(
            P,
            Q,
            P and Q,
            P or Q
        )


# ============================================================
# 109. COMPUTATIONAL THINKING
# ============================================================

print("\n" + "=" * 70)
print("109. COMPUTATIONAL THINKING")
print("=" * 70)

print("""
Mathematical foundations train you to think in terms of:

    inputs
    transformations
    outputs
    constraints
    relationships
    invariants
    verification

For example:

    input -> expression -> output

This pattern appears everywhere in computing.
""")


# ============================================================
# 110. FINAL CONCEPT MAP
# ============================================================

print("\n" + "=" * 70)
print("110. FINAL CONCEPT MAP")
print("=" * 70)

print("""
NUMBERS
|
+-- Natural
+-- Whole
+-- Integer
+-- Rational
+-- Irrational
+-- Real
+-- Complex
|
ARITHMETIC
|
+-- Addition
+-- Subtraction
+-- Multiplication
+-- Division
+-- Modulo
+-- Powers
+-- Roots
|
ALGEBRA
|
+-- Variables
+-- Constants
+-- Expressions
+-- Equations
+-- Inequalities
+-- Functions
|
OPERATORS
|
+-- Arithmetic
+-- Comparison
+-- Logical
+-- Assignment
|
EVALUATION
|
+-- Parentheses
+-- Exponents
+-- Multiplication / Division
+-- Addition / Subtraction
|
COMPUTATIONAL MATHEMATICS
|
+-- Floating point
+-- Exact fractions
+-- Decimal arithmetic
+-- Symbolic mathematics
+-- Modular arithmetic
+-- Boolean algebra
""")


# ============================================================
# 111. FINAL CHECKLIST
# ============================================================

print("\n" + "=" * 70)
print("111. LEARNING CHECKLIST")
print("=" * 70)

checklist = [
    "Understand natural numbers",
    "Understand integers",
    "Understand rational numbers",
    "Understand irrational numbers",
    "Understand real numbers",
    "Understand complex numbers",
    "Perform arithmetic",
    "Use modulo",
    "Use floor division",
    "Understand powers",
    "Understand roots",
    "Understand absolute value",
    "Understand mathematical notation",
    "Understand expressions",
    "Understand equations",
    "Understand variables",
    "Understand constants",
    "Understand operators",
    "Understand precedence",
    "Understand associativity",
    "Translate algebra into Python",
    "Solve basic equations",
    "Verify mathematical results",
    "Understand floating-point limitations",
    "Use fractions for exact arithmetic",
    "Understand modular arithmetic",
    "Understand Boolean logic",
    "Use symbolic mathematics"
]

for i, item in enumerate(checklist, start=1):
    print(f"{i:02d}. {item}")


# ============================================================
# 112. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("END OF MATHEMATICAL FOUNDATIONS")
print("=" * 70)

print("""
You have completed the mathematical foundation layer.

The next major mathematical areas for computing are:

    1. Sets
    2. Logic
    3. Functions
    4. Relations
    5. Proof techniques
    6. Combinatorics
    7. Discrete mathematics
    8. Number theory
    9. Linear algebra
    10. Probability
    11. Statistics
    12. Calculus
    13. Optimization

Do not memorize formulas blindly.

Learn to ask:

    What does this symbol mean?
    What type of number is involved?
    What are the constraints?
    What operation is being performed?
    In what order are operations evaluated?
    What assumptions are being made?
    Can the result be verified?

That mindset is the foundation of mathematical thinking in computing.
""")
