# Equations: linear, quadratic, polynomial, and systems of equations

## Introduction

An equation is a mathematical statement that two expressions are equal. Solving an equation means finding the values of its variables that make the equality true.

This study file develops equation-solving methods from elementary algebra through numerical polynomial methods and systems of linear equations. The accompanying Python program implements the principal methods directly rather than relying on a symbolic mathematics package.

The central computational workflow is:

**model → transform → solve → verify → interpret**

Verification is an important part of equation solving. Algebraic transformations can introduce restrictions or extraneous candidates, while numerical methods produce approximations rather than exact symbolic values.

The major equation families covered are:

- Linear equations
- Quadratic equations
- Polynomial equations
- Systems of linear equations

The script also addresses related ideas that are important when implementing equation solvers, including domain restrictions, numerical precision, polynomial evaluation, synthetic division, root multiplicity, Gaussian elimination, rank, numerical root finding, and solution verification.

## Fundamental terminology

### Expression

An expression is a combination of numbers, variables, operators, and functions without an equality requirement.

Examples include:

- `3x + 5`
- `x² - 4x + 7`
- `2a + 3b`

An expression represents a mathematical quantity.

### Equation

An equation contains an equality relation.

Example:

`3x + 5 = 20`

The objective is to determine the value or values of `x` that make both sides equal.

### Variable

A variable represents an unknown or changeable quantity.

In:

`4x + 7 = 19`

`x` is the variable.

### Coefficient

A coefficient is the numerical factor multiplying a variable.

In:

`7x² - 3x + 5`

the coefficient of `x²` is `7` and the coefficient of `x` is `-3`.

### Constant

A constant is a term without a variable.

In:

`4x² - 8x + 11`

`11` is the constant term.

### Solution

A solution is a value that satisfies the original equation.

For:

`2x + 4 = 10`

the solution is `x = 3`, because:

`2(3) + 4 = 10`

### Root or zero

For a polynomial equation written as:

`p(x) = 0`

a value `r` is a root when:

`p(r) = 0`

The terms root, zero, and solution are closely related in polynomial equations.

## Linear equations

A linear equation in one variable can be written as:

`ax + b = 0`

where `a` and `b` are constants and `a` is not zero.

Solving gives:

`x = -b/a`

The defining property of a linear equation is that the variable has degree one.

For example:

`3x + 5 = 20`

Subtracting `5` from both sides gives:

`3x = 15`

Dividing by `3` gives:

`x = 5`

The Python script represents a more general form:

`ax + b = cx + d`

Moving variable terms to one side and constants to the other gives:

`(a-c)x = d-b`

Therefore:

`x = (d-b)/(a-c)`

provided `a-c` is not zero.

## Linear equation edge cases

A linear equation does not always have exactly one solution.

Consider:

`7x + 3 = 7x + 8`

Subtracting `7x` from both sides produces:

`3 = 8`

This is impossible, so the equation has no solution.

Now consider:

`7x + 3 = 7x + 3`

Subtracting `7x` produces:

`3 = 3`

This statement is always true. Every value of `x` satisfies the equation, so there are infinitely many solutions.

The three principal cases are:

| Condition | Result |
|---|---|
| Nonzero variable coefficient | One solution |
| Zero variable coefficient and false constant statement | No solution |
| Zero variable coefficient and true constant statement | Infinitely many solutions |

This distinction is important in software because an equation solver cannot always return a single numerical value.

## Equations with parentheses

The distributive property allows parentheses to be expanded.

For:

`3(2x - 4) = x + 8`

distribution gives:

`6x - 12 = x + 8`

Then:

`5x = 20`

and:

`x = 4`

A frequent algebraic error is distributing multiplication to only one term. The correct rule is:

`k(a+b) = ka + kb`

Every term inside the parentheses must be multiplied.

## Fractions and decimals

Linear equations can contain fractional or decimal coefficients.

For:

`x/3 + 2 = 6`

subtracting `2` gives:

`x/3 = 4`

Multiplying by `3` gives:

`x = 12`

For equations with multiple fractions, multiplying the entire equation by a common denominator can simplify the calculation. The operation must apply to every term on both sides.

Decimal equations can be solved in the same manner, although numerical representations require care when implemented in software.

## Valid equation transformations

Equality is preserved when the same valid operation is applied to both sides.

If:

`A = B`

then:

`A + C = B + C`

and:

`A - C = B - C`

Multiplication by a nonzero value also preserves equality:

`kA = kB`

Division is valid when the divisor is nonzero:

`A/k = B/k`

where:

`k ≠ 0`

The restriction against division by zero is fundamental.

Some transformations are not reversible over the intended domain. This is particularly important for squaring, taking roots, multiplying by expressions that may be zero, and applying inverse functions.

## Extraneous solutions

An extraneous solution is a candidate generated during algebraic manipulation that does not satisfy the original equation.

For example:

`sqrt(x) = -2`

Squaring both sides produces:

`x = 4`

But substituting `4` into the original equation gives:

`sqrt(4) = 2`

not `-2`.

Therefore `x = 4` is not a solution of the original equation.

The important principle is:

**Every candidate should be checked against the original equation when a transformation may have changed the solution set.**

## Quadratic equations

A quadratic equation has the general form:

`ax² + bx + c = 0`

where:

`a ≠ 0`

The quadratic formula is:

`x = (-b ± sqrt(b² - 4ac)) / (2a)`

The expression:

`b² - 4ac`

is the **discriminant**.

The discriminant determines the nature of the roots.

| Discriminant | Roots |
|---|---|
| `D > 0` | Two distinct real roots |
| `D = 0` | One repeated real root |
| `D < 0` | Two complex conjugate roots |

The Python implementation uses `cmath.sqrt`, allowing the same formula to handle negative discriminants.

## Factoring quadratics

Some quadratic equations can be solved efficiently through factorization.

Consider:

`x² - 5x + 6 = 0`

The polynomial factors as:

`(x - 2)(x - 3) = 0`

The zero-product property states that if:

`AB = 0`

then:

`A = 0`

or:

`B = 0`

Therefore:

`x = 2`

or:

`x = 3`

Factoring can be faster than the quadratic formula when the factors are easy to identify, but it is not always practical for arbitrary coefficients.

## Completing the square

A quadratic can be rewritten in vertex form:

`a(x-h)² + k`

For:

`ax² + bx + c`

the x-coordinate of the vertex is:

`h = -b/(2a)`

and the corresponding y-coordinate is obtained by evaluating the polynomial at `h`.

The Python function for completing the square returns the parameters required for this representation.

Completing the square is useful for:

- Finding the vertex
- Finding the axis of symmetry
- Understanding the graph
- Deriving the quadratic formula
- Transforming quadratic expressions

## Vertex and axis of symmetry

For:

`y = ax² + bx + c`

the vertex has x-coordinate:

`x = -b/(2a)`

The axis of symmetry is the vertical line:

`x = -b/(2a)`

If `a > 0`, the parabola opens upward and the vertex is a minimum.

If `a < 0`, the parabola opens downward and the vertex is a maximum.

The vertex is particularly useful in optimization problems.

## Quadratic edge cases

A solver should not automatically assume that every expression written with an `x²` position is genuinely quadratic.

If:

`a = 0`

then:

`ax² + bx + c = 0`

reduces to:

`bx + c = 0`

which is a linear equation.

If both `a` and `b` are zero, the equation becomes:

`c = 0`

This gives two possibilities:

- `c = 0`: infinitely many solutions
- `c ≠ 0`: no solution

The Python implementation explicitly handles these cases.

## Vieta's relations

For:

`ax² + bx + c = 0`

with roots `r₁` and `r₂`:

`r₁ + r₂ = -b/a`

and:

`r₁r₂ = c/a`

These relationships are useful for checking calculated roots.

For:

`2x² - 7x + 3 = 0`

the sum of the roots must be:

`7/2`

and their product must be:

`3/2`

A numerical root solver can therefore use these identities as additional consistency checks.

## Polynomial equations

A polynomial has the general form:

`aₙxⁿ + aₙ₋₁xⁿ⁻¹ + ... + a₂x² + a₁x + a₀`

where the coefficients are constants and the exponent of the variable is a nonnegative integer.

The degree is the highest exponent with a nonzero coefficient.

Examples:

- Degree 0: `7`
- Degree 1: `3x + 2`
- Degree 2: `x² - 4`
- Degree 3: `x³ - 2x + 1`
- Degree 4: `2x⁴ + x² - 9`

The Python `Polynomial` class stores coefficients in ascending order of power.

For:

`3x³ - 2x + 5`

the internal representation is:

`[5, -2, 0, 3]`

The position of each coefficient corresponds to its exponent.

## Polynomial evaluation

A polynomial can be evaluated directly from its definition.

For:

`p(x) = 3x³ - 2x + 5`

substituting `x = 2` gives:

`p(2) = 3(2³) - 2(2) + 5`

The implementation uses **Horner's method** instead.

The same polynomial can be evaluated as:

`((3x + 0)x - 2)x + 5`

Horner's method reduces the number of multiplications and is efficient for numerical evaluation.

It also avoids explicitly calculating every power separately.

## Polynomial addition, subtraction, and multiplication

Polynomial addition combines coefficients belonging to the same power.

For example:

`(3x² + 2x + 1) + (x² - 4x + 5)`

gives:

`4x² - 2x + 6`

Polynomial multiplication uses the distributive property. Every term in the first polynomial is multiplied by every term in the second polynomial.

The implementation performs this through coefficient convolution.

If the first polynomial has degree `m` and the second has degree `n`, the product has degree at most:

`m + n`

## Polynomial differentiation

For:

`p(x) = a₀ + a₁x + a₂x² + ...`

the derivative is:

`p'(x) = a₁ + 2a₂x + 3a₃x² + ...`

Differentiation is important for:

- Newton-Raphson root finding
- Optimization
- Curve analysis
- Finding stationary points
- Numerical methods

The Python `derivative()` method applies the power rule directly to the coefficient representation.

## Polynomial integration

An antiderivative can be computed term by term.

For:

`aₙxⁿ`

the integral is:

`aₙxⁿ⁺¹/(n+1)`

plus an arbitrary constant.

The Python implementation allows the integration constant to be specified explicitly.

## The factor theorem

The factor theorem states:

`p(r) = 0`

if and only if:

`x-r`

is a factor of `p(x)`.

For example, if:

`p(1) = 0`

then:

`x-1`

is a factor.

This provides a direct connection between evaluating a polynomial and factoring it.

## The remainder theorem

When a polynomial `p(x)` is divided by:

`x-r`

the remainder is:

`p(r)`

This is useful because evaluating a polynomial is much simpler than performing full polynomial division.

The script demonstrates this using:

`x³ - 6x² + 11x - 6`

When evaluated at `x = 1`, the result is zero. Therefore `x-1` is a factor.

## Synthetic division

Synthetic division is an efficient method for dividing a polynomial by a linear factor:

`x-r`

It is especially useful after finding a root.

If:

`p(x) = (x-r)q(x)`

then synthetic division can calculate `q(x)` without carrying out full polynomial long division.

The script uses synthetic division for:

- Root verification
- Polynomial deflation
- Factorization
- Root multiplicity detection

## Rational-root theorem

For a polynomial with integer coefficients:

`aₙxⁿ + ... + a₀`

any rational root in lowest terms:

`p/q`

must satisfy:

- `p` divides the constant term `a₀`
- `q` divides the leading coefficient `aₙ`

This does not mean every candidate is a root. It only produces a finite set of possible rational roots.

For:

`x³ - 6x² + 11x - 6`

the possible integer roots include divisors of `6`. Testing them reveals:

`1, 2, 3`

as actual roots.

The polynomial therefore factors as:

`(x-1)(x-2)(x-3)`

## Polynomial deflation

Once a root `r` is known, dividing the polynomial by:

`x-r`

reduces its degree by one.

This process is called polynomial deflation.

For example:

`p(x) = (x-1)(x-2)(x-3)`

After dividing by `x-1`, the remaining polynomial is:

`(x-2)(x-3)`

Repeated deflation can expose the remaining factors.

For numerical computation, deflation must be used carefully because rounding errors can accumulate.

## Root multiplicity

A root can occur more than once.

For:

`(x-2)³`

the value `x = 2` is a root of multiplicity three.

Expanding gives:

`x³ - 6x² + 12x - 8`

Repeated synthetic division by `x-2` reveals the multiplicity.

Multiplicity affects numerical root-finding because repeated roots generally behave differently from simple roots. Newton's method, for example, can converge more slowly near a multiple root.

## Numerical root finding

Not every polynomial has convenient rational roots.

Consider:

`x³ - x - 2 = 0`

Testing simple integer candidates does not produce a root.

Numerical methods can approximate its real root.

Two methods implemented in the script are:

- Newton-Raphson
- Bisection

## Newton-Raphson method

Newton-Raphson uses:

`xₙ₊₁ = xₙ - f(xₙ)/f'(xₙ)`

The method begins with an initial guess and repeatedly uses the tangent line to improve the estimate.

For a sufficiently good starting point and a well-behaved function, Newton's method can converge very quickly.

The method has important limitations.

It can encounter problems when:

- The derivative is zero or close to zero
- The initial guess is poor
- The function has complicated local behavior
- The root is repeated
- Iterates move into an undesirable region

The Python implementation explicitly checks for a nearly zero derivative.

## Bisection method

Bisection is based on the intermediate value principle.

If a continuous function satisfies:

`f(a)f(b) < 0`

then there is at least one root between `a` and `b`.

Bisection repeatedly divides the interval in half and retains the subinterval containing a sign change.

Advantages include:

- Strong convergence guarantees under its assumptions
- Simple implementation
- No derivative required
- Predictable behavior

Its main disadvantage is speed. It usually converges more slowly than Newton-Raphson.

## Newton-Raphson versus bisection

| Property | Newton-Raphson | Bisection |
|---|---|---|
| Requires derivative | Yes | No |
| Requires initial interval | No | Yes |
| Requires sign change | No | Yes |
| Typical speed | Very fast near root | Predictable but slower |
| Robustness | More sensitive | High under valid assumptions |
| Main risk | Poor initial guess or small derivative | Invalid interval |
| Typical use | Fast refinement | Reliable bracketing |

A practical numerical solver can combine methods rather than treating one method as universally superior.

## Complex polynomial roots

A polynomial of degree `n` has `n` complex roots when roots are counted with multiplicity, according to the fundamental theorem of algebra.

Not all of these roots need to be real.

For example:

`x² + 1 = 0`

has roots:

`x = i`

and:

`x = -i`

The script includes a Durand-Kerner implementation for approximating all complex roots of a polynomial.

The method simultaneously updates multiple root estimates rather than solving each root independently.

The update for a root approximation `zᵢ` is based on:

`zᵢ(new) = zᵢ - p(zᵢ) / Π(zᵢ-zⱼ)`

where the product is taken over the other root approximations.

Numerical behavior can become difficult when roots are repeated or extremely close together.

## Polynomial long division

Polynomial long division follows the same conceptual structure as ordinary integer long division.

For:

`dividend = divisor × quotient + remainder`

the remainder must have lower degree than the divisor.

The script implements long division independently from synthetic division.

The two methods are useful in different situations:

- Synthetic division is especially efficient for division by `x-r`.
- Polynomial long division works for general polynomial divisors.

## Systems of equations

A system contains multiple equations involving common variables.

For example:

`2x + 3y = 13`

`4x - y = 5`

A solution must satisfy both equations simultaneously.

Geometrically, two linear equations in two variables represent two lines.

Their relationship determines the number of solutions.

### Unique solution

Two nonparallel lines intersect once.

The system has exactly one solution.

### No solution

Parallel distinct lines never intersect.

The system has no solution.

### Infinitely many solutions

Coincident lines represent the same equation.

Every point on that line satisfies both equations.

The system has infinitely many solutions.

## Substitution

Substitution solves one equation for a variable and substitutes that expression into another equation.

For example:

`2x + 3y = 13`

can be rearranged as:

`y = (13 - 2x)/3`

That expression can then be substituted into the second equation.

Substitution is especially useful when one equation already isolates a variable or can be isolated with little work.

## Elimination

Elimination combines equations so that one variable cancels.

For:

`2x + 3y = 13`

`4x - y = 5`

multiplying the second equation by `3` gives:

`12x - 3y = 15`

Adding the first equation gives:

`14x = 28`

so:

`x = 2`

Substitution then gives:

`y = 3`

The Python implementation also uses determinant-based formulas for a 2×2 system.

## Determinant method for a 2×2 system

For:

`a₁x + b₁y = c₁`

`a₂x + b₂y = c₂`

the determinant is:

`D = a₁b₂ - a₂b₁`

If:

`D ≠ 0`

the system has a unique solution.

The determinant method gives:

`x = (c₁b₂ - c₂b₁)/D`

and:

`y = (a₁c₂ - a₂c₁)/D`

When `D = 0`, the equations do not have a unique intersection. Additional consistency checks are required to distinguish between no solution and infinitely many solutions.

## Gaussian elimination

Gaussian elimination generalizes elimination to larger systems.

An augmented matrix represents a system such as:

`a₁₁x₁ + a₁₂x₂ + ... = b₁`

through rows containing the coefficients and right-hand side.

For example, a three-variable system can be represented as:

`[a b c d]`

`[e f g h]`

`[i j k l]`

where the last column contains the right-hand side.

Gaussian elimination uses elementary row operations to transform the matrix into a simpler form.

The principal operations are:

- Swap two rows
- Multiply a row by a nonzero value
- Add a multiple of one row to another row

These operations preserve the solution set.

## Partial pivoting

Numerical Gaussian elimination can be sensitive to floating-point arithmetic.

Partial pivoting chooses the row with the largest absolute coefficient in the current pivot column and exchanges it into the pivot position.

This reduces the risk of dividing by a very small number and generally improves numerical stability.

The Python Gaussian-elimination implementation performs partial pivoting.

## Rank and system classification

For:

`Ax = b`

let:

- `rank(A)` be the rank of the coefficient matrix
- `rank([A|b])` be the rank of the augmented matrix
- `n` be the number of variables

The system can be classified using:

### No solution

`rank(A) < rank([A|b])`

The augmented matrix contains information that is inconsistent with the coefficient equations.

### Infinitely many solutions

`rank(A) = rank([A|b]) < n`

The system is consistent but does not contain enough independent equations to determine every variable uniquely.

### Unique solution

`rank(A) = rank([A|b]) = n`

There is enough independent information to determine all variables.

The Python script includes a rank calculation based on row reduction.

## Three-variable systems

The same elimination principles apply to three or more variables.

For example:

`x + y + z = 6`

`2x - y + z = 3`

`x + 2y - z = 2`

can be represented as an augmented matrix and solved using Gaussian elimination.

This approach generalizes naturally to larger linear systems.

## Absolute-value equations

Absolute-value equations introduce multiple cases.

For:

`|x-3| = 5`

the expression inside the absolute value can equal either `5` or `-5`.

Therefore:

`x-3 = 5`

or:

`x-3 = -5`

giving:

`x = 8`

or:

`x = -2`

If the right-hand side is negative, an equation such as:

`|x-3| = -1`

has no real solution because an absolute value cannot be negative.

## Rational equations and domain restrictions

Consider:

`1/(x-2) = 3`

The original equation requires:

`x ≠ 2`

because division by zero is undefined.

Multiplying through by `x-2` gives:

`1 = 3(x-2)`

which produces:

`x = 7/3`

The result is valid because:

`7/3 ≠ 2`

Domain restrictions should be identified before manipulation and checked again when candidate solutions are produced.

## Polynomial applications

Polynomial equations occur in many mathematical and practical models.

Examples include:

- Motion and trajectory calculations
- Geometric optimization
- Engineering models
- Approximation methods
- Signal and control models
- Financial and economic models
- Computer graphics
- Numerical analysis
- Scientific computing

A quadratic projectile model is included in the script.

The height is modeled as:

`h(t) = h₀ + v₀t - (g/2)t²`

Finding when the projectile reaches the ground requires solving:

`h(t) = 0`

The quadratic formula can then provide the candidate times.

Only physically meaningful values, such as nonnegative time, should be retained.

## Word problems and systems

Systems of equations are useful when multiple unknown quantities are connected by multiple relationships.

The script contains a ticket-revenue example:

`a + s = 120`

`15a + 8s = 1320`

where `a` represents adult tickets and `s` represents student tickets.

The first equation describes the total number of tickets.

The second equation describes total revenue.

Solving both equations simultaneously determines the two unknown quantities.

The important modeling principle is that the equations should represent the original problem before algebraic solving begins.

## Numerical precision

Python's standard floating-point numbers use finite binary representations.

Some decimal values cannot be represented exactly in binary floating point.

For example, the mathematical value:

`0.1 + 0.2`

is exactly:

`0.3`

but a binary floating-point implementation may store an approximation.

Therefore numerical equation solvers should generally avoid relying on exact equality for floating-point results.

Instead of:

`value == expected`

a numerical implementation can use a tolerance such as:

`abs(value - expected) <= tolerance`

The appropriate tolerance depends on the scale and conditioning of the problem.

## Verification of numerical roots

Suppose a numerical method produces:

`x ≈ 1.5213797068`

for:

`x³ - x - 2 = 0`

The approximation should be substituted back into the polynomial.

The residual is:

`|p(x)|`

A small residual indicates that the approximation satisfies the equation closely.

Residual checks do not replace mathematical reasoning, but they are an important engineering practice when implementing numerical solvers.

## Conditioning

A problem can be mathematically well-defined but numerically sensitive.

Two lines that are almost parallel can have a unique intersection, yet small changes in their coefficients can cause large changes in the intersection point.

This is a **conditioning** issue.

An ill-conditioned problem is sensitive to small input errors.

This differs from an unstable algorithm. Conditioning describes the mathematical sensitivity of the problem itself, while numerical stability describes how an algorithm responds to finite-precision arithmetic.

The script includes a near-parallel system to illustrate this distinction.

## Performance considerations

For ordinary one-variable linear and quadratic equations, direct formulas are computationally inexpensive.

Polynomial operations have costs that depend on degree.

For polynomial multiplication using the straightforward coefficient-convolution approach, multiplying degree-`m` and degree-`n` polynomials requires approximately:

`O(mn)`

coefficient multiplications.

Horner's method evaluates a degree-`n` polynomial in:

`O(n)`

arithmetic operations.

Gaussian elimination for an `n × n` dense system generally requires:

`O(n³)`

arithmetic operations.

The memory requirement for a dense matrix is approximately:

`O(n²)`

The direct implementations in the script prioritize transparency and educational correctness rather than specialized high-performance numerical linear algebra.

## Security and robustness considerations

Equation solvers are mathematical programs, but robust implementations still require defensive input handling.

Important considerations include:

- Reject division by zero.
- Validate polynomial degree assumptions.
- Validate matrix dimensions.
- Detect inconsistent systems.
- Avoid infinite numerical loops.
- Limit numerical iteration counts.
- Use convergence tolerances.
- Check derivatives before Newton-Raphson division.
- Verify numerical results.
- Respect domain restrictions.
- Avoid evaluating arbitrary user-provided Python expressions as code.

The final point is particularly important for interactive equation calculators. A program should not pass unrestricted user text directly to Python's `eval()` function unless it has been safely parsed and restricted.

## Common mistakes

### Moving a term without changing its sign

When a term is moved from one side of an equation to the other through addition or subtraction, its sign changes because an operation is being performed on both sides.

### Distributing incorrectly

Incorrect:

`3(x - 4) = 3x - 4`

Correct:

`3(x - 4) = 3x - 12`

### Dividing by zero

Division by zero is undefined. An equation solver must detect this situation rather than silently producing a result.

### Treating every quadratic as having two real roots

A negative discriminant produces complex roots rather than real roots.

### Forgetting that `a` must be nonzero

The quadratic formula applies to a genuine quadratic equation. If `a = 0`, the equation has lower degree.

### Ignoring domain restrictions

A candidate solution may make an original denominator zero or violate another domain requirement.

### Accepting extraneous solutions

Squaring, multiplying by variable expressions, or other non-equivalent transformations can produce candidates that do not satisfy the original equation.

### Assuming numerical roots are exact

A numerical root is generally an approximation.

### Confusing no solution with infinitely many solutions

`0 = 5` is false and represents no solution.

`0 = 0` is always true and can represent infinitely many solutions.

### Ignoring numerical conditioning

A solver can return a mathematically valid result that is highly sensitive to small input changes.

## Exact versus numerical methods

Exact algebraic methods and numerical methods serve different purposes.

Exact methods include:

- Algebraic rearrangement
- Factoring
- Quadratic formula
- Rational-root theorem
- Symbolic polynomial division

Numerical methods include:

- Bisection
- Newton-Raphson
- Durand-Kerner
- Floating-point Gaussian elimination

Exact methods can preserve mathematical structure but may become complicated for high-degree equations.

Numerical methods can handle complicated equations efficiently but introduce approximation and convergence considerations.

A production mathematical system often needs both perspectives.

## Comparison of equation types

| Equation type | Typical form | Main methods |
|---|---|---|
| Linear | `ax + b = 0` | Isolation and rearrangement |
| Quadratic | `ax² + bx + c = 0` | Factoring, completing square, quadratic formula |
| Polynomial | `aₙxⁿ + ... + a₀ = 0` | Factoring, division, numerical methods |
| 2×2 linear system | Two equations in `x` and `y` | Substitution, elimination, determinants |
| Larger linear system | `Ax = b` | Gaussian elimination, matrix methods |
| Rational equation | Fractions involving variables | Domain analysis and algebraic transformation |
| Absolute-value equation | `|f(x)| = c` | Case analysis |

## Implementation design

The Python program is organized into independent functions and classes.

The `LinearEquation` class handles equations of the form:

`ax + b = cx + d`

The `QuadraticEquation` class provides:

- Discriminant calculation
- Root classification
- Root calculation
- Vertex calculation
- Axis of symmetry
- Root verification

The `Polynomial` class provides:

- Coefficient representation
- Evaluation
- Addition
- Subtraction
- Multiplication
- Differentiation
- Integration
- Scaling

Additional functions implement:

- Synthetic division
- Polynomial long division
- Rational-root candidates
- Polynomial deflation
- Root multiplicity
- Newton-Raphson
- Bisection
- Durand-Kerner
- Substitution
- Determinant-based 2×2 solving
- Gaussian elimination
- Matrix rank
- System classification

This separation makes the mathematical algorithms independently testable.

## Testing and verification

The script includes an automated test section.

The tests verify:

- Linear solutions
- Linear edge cases
- Quadratic roots
- Complex quadratic roots
- Polynomial evaluation
- Polynomial derivatives
- Synthetic division
- Rational roots
- Numerical root convergence
- Two-variable systems
- Infinite-solution systems
- No-solution systems
- Gaussian elimination
- Polynomial long division
- Repeated roots

Testing is particularly important for equation solvers because algebraic formulas can appear correct while implementation details such as signs, coefficient ordering, pivot selection, and numerical tolerances are incorrect.

## Reference formulas

### Linear equation

`ax + b = 0`

`x = -b/a`

with:

`a ≠ 0`

### General linear equation

`ax + b = cx + d`

`x = (d-b)/(a-c)`

when:

`a-c ≠ 0`

### Quadratic equation

`ax² + bx + c = 0`

`x = (-b ± sqrt(b² - 4ac))/(2a)`

### Discriminant

`D = b² - 4ac`

### Quadratic vertex

`xᵥ = -b/(2a)`

`yᵥ = f(xᵥ)`

### Quadratic root relationships

`r₁ + r₂ = -b/a`

`r₁r₂ = c/a`

### Newton-Raphson

`xₙ₊₁ = xₙ - f(xₙ)/f'(xₙ)`

### Bisection

For a continuous function with a sign change:

`f(a)f(b) < 0`

repeatedly replace the interval by the half containing the sign change.

### Two-variable determinant

`D = a₁b₂ - a₂b₁`

### Two-variable solution

`x = (c₁b₂ - c₂b₁)/D`

`y = (a₁c₂ - a₂c₁)/D`

when:

`D ≠ 0`

### Rank classification

`rank(A) < rank([A|b])` means no solution.

`rank(A) = rank([A|b]) < n` means infinitely many solutions.

`rank(A) = rank([A|b]) = n` means a unique solution.

## Practical interpretation

Equation solving is not only about applying formulas. A reliable solution process distinguishes several layers:

**Modeling**

Translate the real situation into mathematical expressions and equations.

**Transformation**

Apply mathematically valid operations while preserving relevant domain restrictions.

**Solving**

Use an appropriate exact or numerical method.

**Verification**

Substitute the candidate back into the original equation or system.

**Interpretation**

Determine whether the mathematical solution makes sense within the original context.

This distinction becomes increasingly important as equations become more complicated. A mathematically valid root may be physically impossible, a numerical approximation may be insufficiently accurate, and a transformed equation may contain candidates that are not valid for the original problem.

The accompanying Python script demonstrates these principles through executable implementations rather than treating equation solving as a collection of isolated formulas.
