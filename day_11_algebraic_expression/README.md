# Algebraic expressions

## Topic introduction

Algebraic expressions provide a systematic way to represent mathematical relationships using numbers, variables, operators, and grouping symbols.

A simple expression such as `3x + 5` contains a variable, a coefficient, a constant, and an addition operation. More complicated expressions can contain powers, multiple terms, parentheses, fractions, and products of polynomials.

The accompanying Python script develops these ideas computationally. It begins with basic terminology and classification and progresses to polynomial arithmetic, expansion, algebraic identities, factorization, polynomial division, the remainder theorem, the factor theorem, parsing, exact arithmetic, validation, testing, and implementation considerations.

The central theme is that algebraic manipulation follows precise structural rules. The Python implementation represents a polynomial as a mapping between exponents and coefficients, allowing these rules to be demonstrated through executable operations rather than only symbolic descriptions.

## Fundamental terminology

### Variable

A variable is a symbol representing a value that may vary.

Examples:

- `x`
- `y`
- `t`

The script uses `x` as its primary polynomial variable.

### Constant

A constant is a fixed numerical quantity.

Examples:

- `7`
- `-3`
- `1/2`

In the expression `4x² - 3x + 7`, the number `7` is a constant term.

### Coefficient

A coefficient is the numerical factor associated with a variable term.

In:

`6x³`

the coefficient is `6`.

In:

`-x²`

the coefficient is `-1`, even though the `1` is normally omitted in written notation.

### Term

A term is a component of an algebraic expression separated from other terms by addition or subtraction.

For:

`3x² - 5x + 7`

the terms are:

- `3x²`
- `-5x`
- `7`

### Factor

A factor is a multiplicative component of an expression.

For:

`(x + 2)(x + 3)`

the expressions `x + 2` and `x + 3` are factors.

The distinction between terms and factors is important. Terms are separated by addition or subtraction, whereas factors are separated by multiplication.

## Monomials, binomials, trinomials, and polynomials

The number of non-zero terms provides a common classification.

### Monomial

A monomial contains exactly one non-zero term.

Examples:

- `7x`
- `-3x²`
- `12`
- `1/2 x⁴`

### Binomial

A binomial contains exactly two non-zero terms.

Examples:

- `x + 4`
- `3x² - 7`
- `5x³ + 2x`

### Trinomial

A trinomial contains exactly three non-zero terms.

Examples:

- `x² + 5x + 6`
- `2x³ - x + 4`

### Polynomial

A polynomial is a finite sum of terms whose variable powers are non-negative integers.

Examples:

- `3x⁴ - 2x² + x - 8`
- `x³ + 5`
- `7`

Expressions such as `1/x`, `x⁻²`, and `√x` are not polynomials in `x` because they involve negative or non-integer powers.

## Degree of a polynomial

The degree of a non-zero polynomial is the greatest exponent having a non-zero coefficient.

For:

`5x⁴ - 3x² + 7x - 1`

the degree is `4`.

Examples:

| Polynomial | Degree |
|---|---:|
| `7` | 0 |
| `3x + 2` | 1 |
| `x² - 4` | 2 |
| `2x³ + x` | 3 |
| `5x⁶ - 2` | 6 |

The zero polynomial requires a convention because it has no greatest non-zero exponent. The script uses `-1` as a computational convention.

Degree and number of terms are different concepts. For example, `x⁵ + 1` has degree 5 but only two terms.

## Standard form

A polynomial is normally written in descending powers of the variable.

For example:

`4 + 3x³ - 2x + x²`

is written in standard form as:

`3x³ + x² - 2x + 4`

The Python `Polynomial` class automatically produces this ordering when displaying an expression.

## Like and unlike terms

Like terms have identical variable parts and exponents.

Examples of like terms:

- `3x²`
- `-7x²`
- `1/2x²`

Examples of unlike terms:

- `3x`
- `3x²`

and:

- `5`
- `5x`

Only like terms can be combined directly.

For example:

`3x² + 5x² = 8x²`

but:

`3x² + 5x`

cannot be reduced to a single term.

## Polynomial representation in Python

The script represents a polynomial using a dictionary whose keys are exponents and whose values are coefficients.

For:

`3x² - 5x + 7`

the conceptual representation is:

`{2: 3, 1: -5, 0: 7}`

This representation is called sparse because terms with zero coefficients do not need to be stored.

The `Polynomial` class provides methods for:

- determining degree
- retrieving coefficients
- adding polynomials
- subtracting polynomials
- multiplying polynomials
- raising polynomials to non-negative integer powers
- evaluating polynomials
- differentiating
- integrating
- scaling
- polynomial division
- comparing polynomials

## Addition of polynomials

Polynomial addition is based on combining coefficients of like powers.

Consider:

`(3x² + 5x - 2) + (4x² - x + 7)`

Group like terms:

`(3x² + 4x²) + (5x - x) + (-2 + 7)`

Therefore:

`7x² + 4x + 5`

The implementation performs this by matching dictionary keys representing exponents.

A missing exponent has an implicit coefficient of zero.

For example:

`5x³ + 2`

can be viewed as:

`5x³ + 0x² + 0x + 2`

This makes coefficient-wise addition straightforward.

## Subtraction of polynomials

Subtraction is implemented as addition of the additive inverse:

`A - B = A + (-B)`

For:

`(5x² + 4x + 2) - (2x² + x + 3)`

the result is:

`3x² + 3x - 1`

When subtracting an expression in parentheses, the sign of every term must be considered.

For example:

`-(x - 4)`

becomes:

`-x + 4`

not:

`-x - 4`

## Multiplication of polynomials

Polynomial multiplication uses the distributive property.

The fundamental rule is:

`a(b + c) = ab + ac`

For two polynomials, every term in the first polynomial is multiplied by every term in the second.

For example:

`(x + 3)(x + 5)`

becomes:

`x² + 5x + 3x + 15`

and therefore:

`x² + 8x + 15`

For individual powers:

`xᵐ × xⁿ = xᵐ⁺ⁿ`

More generally:

`(axᵐ)(bxⁿ) = abxᵐ⁺ⁿ`

The Python implementation applies this rule to every pair of terms and combines terms that produce the same exponent.

## Expansion

Expansion transforms a product into a sum.

For example:

`(x + 2)(x + 5)`

expands to:

`x² + 7x + 10`

Expansion is useful when:

- collecting like terms
- comparing coefficients
- differentiating a polynomial
- integrating a polynomial
- evaluating its standard form

Factored form can be more useful when identifying roots or solving equations.

## Powers of polynomials

The script supports non-negative integer powers.

For example:

`(x + 2)²`

is calculated as:

`(x + 2)(x + 2)`

which produces:

`x² + 4x + 4`

Negative powers are rejected because they generally produce rational expressions rather than polynomials.

## Algebraic identities

Algebraic identities are equalities that remain true for every value for which both sides are defined.

### Square of a sum

`(a + b)² = a² + 2ab + b²`

### Square of a difference

`(a - b)² = a² - 2ab + b²`

### Difference of squares

`a² - b² = (a - b)(a + b)`

### Sum of cubes

`a³ + b³ = (a + b)(a² - ab + b²)`

### Difference of cubes

`a³ - b³ = (a - b)(a² + ab + b²)`

These identities can be used in two opposite directions.

Expansion uses:

`(a + b)² → a² + 2ab + b²`

Factorization uses:

`a² + 2ab + b² → (a + b)²`

## A common identity error

A frequent mistake is:

`(a + b)² = a² + b²`

This is incorrect.

The correct expansion is:

`(a + b)² = a² + 2ab + b²`

The middle term is essential.

For example:

`(x + 3)²`

is:

`x² + 6x + 9`

not:

`x² + 9`.

## Substitution and evaluation

Evaluating a polynomial means replacing its variable with a specific value.

For:

`P(x) = 2x² - 3x + 1`

at `x = 4`:

`P(4) = 2(4²) - 3(4) + 1`

`= 32 - 12 + 1`

`= 21`

The script provides an `evaluate()` method.

It uses Horner's method rather than separately computing every power.

For:

`ax³ + bx² + cx + d`

Horner's form is:

`((ax + b)x + c)x + d`

This reduces repeated exponentiation and gives evaluation time proportional to the degree.

## Negative substitution values

Negative values require careful interpretation.

For example:

`(-3)² = 9`

whereas under conventional mathematical precedence:

`-3² = -9`

because exponentiation occurs before the unary negative sign.

When programming or manually substituting negative values, parentheses should be used explicitly.

## Factorization

Factorization reverses multiplication.

For example:

`x² + 5x + 6`

can be written as:

`(x + 2)(x + 3)`

because:

`(x + 2)(x + 3) = x² + 5x + 6`

Factorization is useful for:

- solving polynomial equations
- finding roots
- simplifying expressions
- identifying structural relationships
- recognizing algebraic identities

## Common-factor extraction

The first factorization technique to check is a common factor.

For:

`6x³ + 9x²`

the greatest common factor is:

`3x²`

Therefore:

`6x³ + 9x² = 3x²(2x + 3)`

The script identifies common powers of `x` and common numerical factors where possible.

Extracting a common factor first can expose another factorization pattern.

## Factorization by grouping

Grouping is useful for four-term expressions.

Consider:

`x³ + 3x² + 2x + 6`

Group the terms:

`x³ + 3x² + 2x + 6`

`= x²(x + 3) + 2(x + 3)`

Now the common factor is visible:

`= (x² + 2)(x + 3)`

The script contains a simple grouping implementation for suitable cubic four-term polynomials.

## Difference of squares

The identity:

`a² - b² = (a - b)(a + b)`

provides a direct factorization method.

Examples:

`x² - 9`

becomes:

`(x - 3)(x + 3)`

and:

`4x² - 25`

becomes:

`(2x - 5)(2x + 5)`.

The expression must contain a subtraction of two perfect squares.

An expression such as:

`x² + 9`

does not factor over the real numbers using the difference-of-squares identity.

## Perfect-square trinomials

The patterns are:

`a² + 2ab + b² = (a + b)²`

and:

`a² - 2ab + b² = (a - b)²`.

For example:

`x² + 6x + 9`

is:

`(x + 3)²`.

Similarly:

`x² - 8x + 16`

is:

`(x - 4)²`.

A useful recognition process is:

1. Check whether the first term is a square.
2. Check whether the final term is a square.
3. Determine the expected middle term.
4. Compare the actual middle term with that value.

## Quadratic factorization

A quadratic has the general form:

`ax² + bx + c`

where `a` is non-zero.

For simple monic quadratics:

`x² + bx + c`

one can search for two numbers whose:

- product is `c`
- sum is `b`

For example:

`x² + 5x + 6`

requires numbers whose product is `6` and sum is `5`.

Those numbers are `2` and `3`, giving:

`(x + 2)(x + 3)`.

The script implements a transparent integer-root search based on candidates related to the Rational Root Theorem.

This is an educational implementation rather than a complete symbolic factorization engine.

## Sum and difference of cubes

The two identities are particularly important because the sign pattern can be easy to confuse.

For a sum:

`a³ + b³ = (a + b)(a² - ab + b²)`

For a difference:

`a³ - b³ = (a - b)(a² + ab + b²)`

For example:

`x³ + 8`

becomes:

`x³ + 2³`

and therefore:

`(x + 2)(x² - 2x + 4)`.

Similarly:

`x³ - 8`

becomes:

`(x - 2)(x² + 2x + 4)`.

## Polynomial division

Polynomial division follows the structure:

`P(x) = D(x)Q(x) + R(x)`

where:

- `P(x)` is the dividend
- `D(x)` is the divisor
- `Q(x)` is the quotient
- `R(x)` is the remainder

The remainder must have a degree smaller than the divisor.

The Python implementation uses polynomial long division.

For example, if:

`P(x) = x³ - 6x² + 11x - 6`

is divided by:

`x - 1`

the quotient is:

`x² - 5x + 6`

and the remainder is zero.

The zero remainder proves that `x - 1` is a factor.

## Remainder theorem

The Remainder Theorem states:

When `P(x)` is divided by `x - a`, the remainder is `P(a)`.

Therefore, instead of performing polynomial long division, the remainder can be calculated directly by evaluating the polynomial at `a`.

For example, if:

`P(x) = x² - 5x + 6`

then the remainder when dividing by `x - 2` is:

`P(2) = 4 - 10 + 6 = 0`.

## Factor theorem

The Factor Theorem follows directly from the Remainder Theorem.

`x - a` is a factor of `P(x)` if and only if:

`P(a) = 0`.

Thus, if:

`P(2) = 0`

then:

`x - 2`

is a factor of `P(x)`.

This relationship connects three concepts:

`P(a) = 0`

means:

`a is a root`

which means:

`x - a is a factor`.

## Roots and factors

A root is a value of the variable that makes a polynomial equal to zero.

For:

`P(x) = (x - 2)(x + 3)`

the roots are:

`x = 2`

and:

`x = -3`.

The corresponding factors are:

`x - 2`

and:

`x + 3`.

Factorized form makes roots particularly easy to identify.

## Polynomial derivative

The derivative of a polynomial can be calculated term by term.

The basic rule is:

`d/dx (axⁿ) = naxⁿ⁻¹`

For example:

`P(x) = 4x³ - 2x + 7`

has derivative:

`P'(x) = 12x² - 2`.

The constant disappears because the derivative of a constant is zero.

The script includes polynomial differentiation as an advanced structural operation.

## Polynomial integral

The corresponding integration rule is:

`∫ axⁿ dx = a/(n+1)xⁿ⁺¹ + C`

For example:

`∫ 6x² dx = 2x³ + C`.

The script represents the polynomial portion of the integral and allows an integration constant to be supplied.

## Exact arithmetic

The script uses Python's `Fraction` type for rational coefficients.

For example:

`1/2 + 1/3`

is represented exactly as:

`5/6`.

Exact arithmetic is valuable in symbolic algebra because floating-point numbers can introduce rounding errors.

For example, many decimal fractions cannot be represented exactly in binary floating-point arithmetic.

Symbolic polynomial operations generally benefit from exact coefficients whenever practical.

## Expression parsing

The script includes a small recursive-descent parser.

It accepts expressions containing:

- numbers
- `x`
- `+`
- `-`
- `*`
- `/`
- `^`
- parentheses
- unary plus
- unary minus

Examples include:

`x² + 2x + 1`

represented programmatically as:

`x^2 + 2*x + 1`

and:

`(x + 2)(x - 3)`

represented as:

`(x + 2)*(x - 3)`.

The parser converts textual input into a structured `Polynomial` object.

## Operator precedence

The parser recognizes mathematical precedence.

The implemented structure is:

1. Parentheses
2. Unary operators
3. Exponentiation
4. Multiplication and division
5. Addition and subtraction

For example:

`2*x + 3*x^2`

is interpreted as:

`2x + 3x²`

rather than:

`(2x + 3x)²`.

Explicit parentheses can always be used when a different grouping is intended.

## Why explicit parsing matters

Arbitrary expression evaluation is dangerous in software.

Passing untrusted input directly to Python's `eval()` can execute arbitrary Python expressions.

The script avoids this approach.

Instead, it:

- tokenizes input
- recognizes only an explicitly defined grammar
- restricts the variable to `x`
- restricts supported operators
- rejects unsupported syntax
- rejects invalid polynomial operations
- raises controlled exceptions

This is an example of allowlisting accepted input rather than executing unrestricted input.

## Edge cases

### Zero polynomial

The expression:

`0`

is represented by an empty coefficient dictionary after zero coefficients are removed.

The script uses degree `-1` as a computational convention.

### Constant polynomial

A non-zero constant such as:

`7`

has degree zero.

### Missing powers

In:

`5x⁴ + 2x`

the coefficients of `x³` and `x²` are implicitly zero.

### Cancellation

The expression:

`x² - x²`

becomes:

`0`.

### Division by zero

Division by the zero polynomial is undefined and raises an exception.

### Negative powers

Expressions such as:

`x⁻¹`

are not polynomials.

### Fractional powers

Expressions such as:

`x^(1/2)`

are not polynomial expressions.

### Division by a variable

A polynomial divided by `x` is not necessarily a polynomial.

For example:

`(x² + 1)/x`

contains:

`1/x`

and therefore is a rational expression rather than a polynomial.

The parser restricts polynomial division to division by constants.

## Important distinctions

### Expression versus equation

An expression:

`3x + 2`

is a mathematical expression.

An equation:

`3x + 2 = 11`

asserts equality between two expressions.

### Expression versus identity

An identity is an equality that holds for every permitted value.

For example:

`(x + 1)² = x² + 2x + 1`

is an identity.

### Expansion versus factorization

Expansion transforms:

`(x + 2)(x + 3)`

into:

`x² + 5x + 6`.

Factorization reverses the process:

`x² + 5x + 6`

into:

`(x + 2)(x + 3)`.

### Degree versus term count

`x⁵ + 1` has degree 5 and two terms.

`x² + x + 1` has degree 2 and three terms.

These properties should not be confused.

### Coefficient versus factor

In:

`6x²`

the coefficient is `6`.

The expression can also be viewed as the product:

`6 × x²`.

The coefficient is a particular numerical part of the factorization, whereas a factor can be any multiplicative component.

## Common mistakes

### Adding exponents during addition

Incorrect:

`x² + x³ = x⁵`

Correct:

`x² + x³`

The exponents are added when multiplying powers with the same base, not when adding terms.

### Incorrect multiplication of powers

Incorrect:

`x² × x³ = x⁶`

Correct:

`x² × x³ = x⁵`

because:

`xᵐ × xⁿ = xᵐ⁺ⁿ`.

### Combining unlike terms

Incorrect:

`3x + 2 = 5x`

Correct:

`3x + 2`

The terms have different variable structures.

### Incorrect square expansion

Incorrect:

`(a + b)² = a² + b²`

Correct:

`(a + b)² = a² + 2ab + b²`.

### Sign errors

Incorrect:

`-(x - 4) = -x - 4`

Correct:

`-(x - 4) = -x + 4`.

### Cancelling terms instead of factors

Cancellation applies to factors, not arbitrary terms separated by addition.

For example, in:

`(x + 2)/x`

the `x` cannot simply be cancelled from the entire numerator because the numerator is a sum rather than a product containing `x` as a common factor.

## Best practices for algebraic manipulation

A systematic approach reduces errors.

1. Identify the structure of the expression.
2. Look for parentheses.
3. Check for a common factor.
4. Check for recognizable identities.
5. Expand only when expansion serves a purpose.
6. Combine like terms.
7. Arrange the polynomial in standard form.
8. Verify the result through substitution or reverse multiplication.

Factorization should generally begin by checking for a common factor before applying more specialized identities.

## Verification

The script provides two forms of verification.

### Symbolic verification

Two `Polynomial` objects are compared by their normalized coefficient dictionaries.

For example:

`(x + 5)²`

and:

`x² + 10x + 25`

produce identical polynomial representations.

This is stronger than checking a few numerical values.

### Numerical cross-checking

A symbolic identity can also be evaluated at selected values.

For example, both sides can be evaluated at:

- `x = -10`
- `x = -1`
- `x = 0`
- `x = 1`
- `x = 10`

If they produce different values, the identity is definitely incorrect.

Numerical testing alone cannot prove that two arbitrary expressions are identical for all possible values, but it is useful for debugging.

## Performance considerations

The sparse dictionary representation avoids storing zero coefficients.

If a polynomial contains `n` stored terms and another contains `m` stored terms:

- addition is approximately `O(n + m)`
- naive multiplication is approximately `O(nm)`

Polynomial evaluation through Horner's method requires approximately `O(d)` operations for a degree-`d` polynomial.

Polynomial long division depends on the degrees and number of terms in the dividend and divisor.

For large symbolic computations, more specialized representations and algorithms may be appropriate. The implementation in the script prioritizes transparency and educational value.

## Implementation considerations

The `Polynomial` class uses immutable-style mathematical operations that return new polynomial objects rather than unexpectedly modifying existing expressions.

The internal representation automatically removes zero coefficients. This ensures that equivalent expressions have a consistent representation.

For example:

`x² + 2x - 2x`

is normalized to:

`x²`.

This normalization makes equality comparisons and subsequent operations more reliable.

The class also provides exact coefficient handling through `Fraction`, reducing numerical ambiguity for rational coefficients.

## Testing

The script includes automated unit tests covering:

- addition
- subtraction
- multiplication
- powers
- evaluation
- differentiation
- integration
- expression parsing
- operator precedence
- parentheses
- polynomial division
- the remainder theorem
- factorization identities
- the zero polynomial
- division by zero
- negative exponents
- unsupported variables
- invalid characters
- invalid polynomial division

Testing algebraic software is particularly important because a small sign or exponent error can propagate through many later calculations.

## Practical applications

Algebraic expressions and polynomials are used extensively in:

- equation solving
- geometry
- physics
- engineering
- economics
- finance
- statistics
- computer graphics
- numerical analysis
- optimization
- signal processing
- control systems
- scientific computing
- computer algebra systems

Polynomial models are particularly useful because they can represent nonlinear relationships while remaining computationally manageable.

## Real-world relevance of factorization and expansion

Factorization can expose structural information that is hidden in expanded form.

For example:

`x² - 9`

does not immediately show its roots as clearly as:

`(x - 3)(x + 3)`.

The factorized form immediately identifies:

`x = 3`

and:

`x = -3`

as roots.

Conversely, expanded form is often preferable when comparing coefficients or applying operations such as differentiation.

Therefore, expansion and factorization are not competing representations. They are complementary forms suited to different mathematical tasks.
