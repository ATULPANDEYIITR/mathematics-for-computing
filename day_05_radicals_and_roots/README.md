# Radicals and Roots

## Introduction

Radicals and roots are fundamental concepts in arithmetic, algebra, geometry, trigonometry, and higher mathematics. A radical represents a root operation, such as a square root, cube root, or nth root. Roots are closely connected to exponents because a root can be expressed as a fractional exponent.

The Python study script develops the subject from basic definitions through exact radical simplification, radical arithmetic, rationalization, radical equations, complex roots, numerical accuracy, algorithm design, testing, and practical applications.

The implementation uses only Python's standard library and demonstrates the mathematical ideas through executable functions, classes, algorithms, validation logic, examples, and tests.

---

## 1. Fundamental Concept of a Root

An nth root of a number is a value that, when raised to the nth power, produces the original number.

For example:

- The square root of 25 is 5 because \(5^2 = 25\).
- The cube root of 27 is 3 because \(3^3 = 27\).
- The fifth root of 32 is 2 because \(2^5 = 32\).

The script implements:

- `square_root()`
- `cube_root()`
- `nth_root_real()`

These functions distinguish between even-degree and odd-degree roots.

For real numbers, an even-degree root requires a non-negative radicand. Therefore:

\[
\sqrt{25}=5
\]

but:

\[
\sqrt{-25}
\]

has no real value.

Odd-degree roots behave differently. Every real number has a real odd-degree root:

\[
\sqrt[3]{-27}=-3
\]

because:

\[
(-3)^3=-27
\]

---

## 2. Principal Roots

The notation \(\sqrt{x}\) normally denotes the principal square root. The principal square root is non-negative.

Thus:

\[
\sqrt{49}=7
\]

not \(-7\).

This must be distinguished from solving the equation:

\[
x^2=49
\]

which has two real solutions:

\[
x=7
\]

and

\[
x=-7
\]

The script demonstrates this distinction with `solve_square_equation()`.

The difference is important because a root notation identifies a particular value, while an equation asks for all values satisfying the equation.

---

## 3. Perfect Powers

A perfect square is an integer of the form:

\[
k^2
\]

Examples include:

\[
0,\ 1,\ 4,\ 9,\ 16,\ 25,\ 36
\]

A perfect cube has the form:

\[
k^3
\]

Examples include:

\[
-8,\ -1,\ 0,\ 1,\ 8,\ 27
\]

More generally, a perfect nth power is an integer that can be written as:

\[
k^n
\]

The script provides both approximate and exact methods for determining whether an integer is a perfect power.

`is_perfect_square()` uses Python's exact integer square-root functionality. `is_perfect_power_exact()` uses an exact integer nth-root algorithm rather than relying solely on floating-point exponentiation.

---

## 4. Prime Factorization and Radical Simplification

Prime factorization is one of the most important tools for simplifying radicals.

Consider:

\[
\sqrt{72}
\]

The prime factorization is:

\[
72=2^3\times3^2
\]

Group the factors into pairs because this is a square root:

\[
\sqrt{72}
=
\sqrt{2^3\times3^2}
\]

Separate complete pairs:

\[
=
\sqrt{2^2\times2\times3^2}
\]

Extract the complete squares:

\[
=2\times3\sqrt2
\]

Therefore:

\[
\boxed{\sqrt{72}=6\sqrt2}
\]

The script implements this process through:

- `prime_factorization()`
- `simplify_radical()`
- `Radical`

The same principle generalizes to nth roots. For a cube root, factors are extracted in groups of three. For a fifth root, factors are extracted in groups of five.

For example:

\[
\sqrt[3]{54}
=
\sqrt[3]{27\times2}
=
3\sqrt[3]{2}
\]

---

## 5. General Radical Simplification Rule

Suppose a radicand has prime factorization:

\[
N=p_1^{e_1}p_2^{e_2}\cdots p_k^{e_k}
\]

For an nth root, divide each exponent into groups of \(n\).

For example:

\[
\sqrt[3]{432}
\]

Since:

\[
432=2^4\times3^3
\]

the exponent decomposition is:

\[
2^4=2^3\times2
\]

and:

\[
3^3
\]

Therefore:

\[
\sqrt[3]{432}
=
2\times3\sqrt[3]{2}
\]

or:

\[
\boxed{6\sqrt[3]{2}}
\]

The implementation extracts:

\[
\left\lfloor\frac{e}{n}\right\rfloor
\]

copies of a prime outside the radical and leaves:

\[
e\bmod n
\]

copies inside.

---

## 6. Exact Radical Representation

The `Radical` dataclass represents a radical using three components:

- coefficient
- degree
- radicand

For example:

\[
6\sqrt2
\]

is represented conceptually as:

- coefficient = 6
- degree = 2
- radicand = 2

Similarly:

\[
3\sqrt[3]{2}
\]

is represented by:

- coefficient = 3
- degree = 3
- radicand = 2

This representation is useful because exact symbolic structure can be preserved instead of immediately converting everything to floating-point numbers.

Canonical representation is important for determining whether two radicals are structurally equivalent.

For example:

\[
\sqrt8
\]

and:

\[
2\sqrt2
\]

are mathematically equal. After canonicalization, both have the same internal form.

---

## 7. Laws of Radicals

For suitable real values:

\[
\sqrt{ab}=\sqrt a\sqrt b
\]

and, when the denominator is positive:

\[
\frac{\sqrt a}{\sqrt b}
=
\sqrt{\frac ab}
\]

These rules follow from the relationship between roots and fractional exponents.

A critical restriction is that radicals do not distribute over addition:

\[
\sqrt{a+b}\ne\sqrt a+\sqrt b
\]

in general.

For example:

\[
\sqrt{9+16}=\sqrt{25}=5
\]

while:

\[
\sqrt9+\sqrt{16}=3+4=7
\]

The script explicitly demonstrates this common mistake.

---

## 8. Addition and Subtraction of Radicals

Only like radicals can be directly combined.

For example:

\[
3\sqrt2+5\sqrt2=8\sqrt2
\]

The coefficients are added while the common radical remains unchanged.

Unlike radicals such as:

\[
\sqrt2+\sqrt3
\]

cannot be simplified into a single radical using ordinary radical addition.

A subtle case occurs when the radicals are not initially in simplified form:

\[
\sqrt8+\sqrt{18}
\]

Simplify each term:

\[
\sqrt8=2\sqrt2
\]

and:

\[
\sqrt{18}=3\sqrt2
\]

Therefore:

\[
\sqrt8+\sqrt{18}
=
5\sqrt2
\]

The script's `add_radicals()` function requires radicals to have compatible canonical structures before they are combined.

---

## 9. Multiplication of Radicals

For radicals of the same degree:

\[
\sqrt a\sqrt b=\sqrt{ab}
\]

Coefficients multiply normally.

For example:

\[
\sqrt6\sqrt{15}
=
\sqrt{90}
\]

and:

\[
\sqrt{90}=3\sqrt{10}
\]

The script implements this process through `multiply_radicals()`.

Multiplication is structurally different from addition. Unlike radicals cannot generally be combined by addition, but radicals can often be multiplied and then simplified.

---

## 10. Division of Radicals

Division must respect the restriction that the denominator cannot be zero.

For example:

\[
\frac{\sqrt{18}}{\sqrt2}
=
\sqrt9
=
3
\]

The script includes numerical radical division and checks for zero denominators.

A denominator containing a radical is often rationalized when a conventional exact algebraic form is required.

---

## 11. Rational Exponents

Roots and fractional exponents express the same mathematical relationship under the appropriate domain conditions.

The fundamental identity is:

\[
a^{1/n}=\sqrt[n]{a}
\]

More generally:

\[
a^{m/n}=\left(\sqrt[n]{a}\right)^m
\]

For example:

\[
16^{1/2}=4
\]

\[
27^{1/3}=3
\]

and:

\[
32^{2/5}=4
\]

because:

\[
\sqrt[5]{32}=2
\]

and:

\[
2^2=4
\]

The script implements fractional powers through `rational_power()` and explicitly checks whether the requested real-valued operation is defined.

---

## 12. Root and Exponent Laws

Roots can be understood as fractional exponents.

For positive real values:

\[
\sqrt[n]{a}=a^{1/n}
\]

Therefore:

\[
\sqrt[n]{a}\sqrt[n]{b}
=
a^{1/n}b^{1/n}
=
(ab)^{1/n}
\]

Nested roots also follow exponent multiplication:

\[
\sqrt[m]{\sqrt[n]{a}}
=
a^{1/(mn)}
=
\sqrt[mn]{a}
\]

The script demonstrates this relationship numerically.

Domain restrictions must still be considered when working with negative real numbers and even roots.

---

## 13. Rationalization

Rationalization transforms an expression so that its denominator contains no radical.

A simple example is:

\[
\frac1{\sqrt2}
\]

Multiply numerator and denominator by \(\sqrt2\):

\[
\frac1{\sqrt2}
\times
\frac{\sqrt2}{\sqrt2}
=
\frac{\sqrt2}{2}
\]

Thus:

\[
\boxed{\frac1{\sqrt2}=\frac{\sqrt2}{2}}
\]

The script implements this concept through `rationalize_single_square_root_denominator()`.

Rationalization is an algebraic transformation. It does not change the value of the expression.

---

## 14. Rationalization Using Conjugates

When the denominator contains a binomial such as:

\[
a+\sqrt b
\]

the appropriate multiplier is its conjugate:

\[
a-\sqrt b
\]

The product is:

\[
(a+\sqrt b)(a-\sqrt b)
=
a^2-b
\]

because of the difference-of-squares identity:

\[
(x+y)(x-y)=x^2-y^2
\]

For example:

\[
\frac1{3+\sqrt2}
\]

can be multiplied by:

\[
\frac{3-\sqrt2}{3-\sqrt2}
\]

giving:

\[
\frac{3-\sqrt2}{9-2}
=
\frac{3-\sqrt2}{7}
\]

The denominator is now rational.

---

## 15. Nested Radicals

A nested radical contains one radical inside another.

For example:

\[
\sqrt{2+\sqrt3}
\]

Some nested radicals can be transformed into sums or differences of simpler radicals.

A useful pattern is:

\[
\sqrt{a+2\sqrt b}
\]

Suppose it can be written as:

\[
\sqrt m+\sqrt n
\]

Squaring gives:

\[
m+n+2\sqrt{mn}
\]

Therefore:

\[
m+n=a
\]

and:

\[
mn=b
\]

The script's `simplify_nested_square_root()` function solves the resulting quadratic relationship for integer \(m\) and \(n\) when possible.

For example:

\[
\sqrt{5+2\sqrt6}
=
\sqrt3+\sqrt2
\]

because:

\[
3+2=5
\]

and:

\[
3\times2=6
\]

Not every nested radical has such a simple decomposition.

---

## 16. Radical Equations

A radical equation contains an unknown inside a radical.

For example:

\[
\sqrt{x+1}=3
\]

Squaring both sides gives:

\[
x+1=9
\]

so:

\[
x=8
\]

The candidate must still be checked in the original equation.

This becomes especially important when squaring can introduce extraneous solutions.

A safe workflow is:

1. Determine the domain.
2. Isolate the radical where possible.
3. Square or raise both sides to the required power.
4. Solve the resulting algebraic equation.
5. Substitute every candidate into the original equation.
6. Reject candidates that do not satisfy the original equation.

The script demonstrates this process with `solve_sqrt_linear_equation()` and `verify_radical_equation_solution()`.

---

## 17. Extraneous Solutions

Squaring an equation is not always a reversible operation.

If:

\[
a=b
\]

then:

\[
a^2=b^2
\]

is true.

But the reverse implication is not always true because:

\[
a^2=b^2
\]

allows:

\[
a=b
\]

or:

\[
a=-b
\]

Therefore, solving an equation after squaring can produce candidates that were not solutions of the original equation.

This is why original-equation verification is essential in radical equations.

---

## 18. Absolute Value and Square Roots

One of the most important radical identities is:

\[
\sqrt{x^2}=|x|
\]

not simply \(x\).

For example:

\[
\sqrt{(-7)^2}
=
\sqrt{49}
=
7
\]

while:

\[
x=-7
\]

The correct relationship is:

\[
\sqrt{x^2}=|x|
\]

For non-negative \(x\), this reduces to:

\[
\sqrt{x^2}=x
\]

For negative \(x\), it becomes:

\[
\sqrt{x^2}=-x
\]

The distinction is fundamental when simplifying algebraic expressions.

---

## 19. Domains of Radical Expressions

Domain restrictions depend on the root degree and the surrounding expression.

For a square root:

\[
\sqrt x
\]

the real domain is:

\[
x\ge0
\]

For a cube root:

\[
\sqrt[3]x
\]

every real \(x\) is permitted.

For:

\[
\frac1{\sqrt x}
\]

the condition is stricter:

\[
x>0
\]

The square root requires:

\[
x\ge0
\]

but the denominator cannot equal zero, so \(x=0\) must also be excluded.

Similarly:

\[
\sqrt{x-3}
\]

requires:

\[
x\ge3
\]

while:

\[
\frac1{\sqrt{x-3}}
\]

requires:

\[
x>3
\]

Domain analysis must occur before manipulating radical expressions.

---

## 20. Negative Radicands and Complex Numbers

Over the real numbers:

\[
\sqrt{-9}
\]

is undefined.

Complex numbers introduce the imaginary unit:

\[
i^2=-1
\]

Therefore:

\[
\sqrt{-9}=3i
\]

Python represents the imaginary unit using `j`, so the corresponding value is:

```text
3j
