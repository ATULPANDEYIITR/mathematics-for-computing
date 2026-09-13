# Inequalities: Linear, Quadratic, Absolute-Value Inequalities, and Intervals

## Topic overview

An inequality describes a relationship between quantities using comparison symbols such as `<`, `>`, `<=`, and `>=`. Unlike an equation, which commonly identifies values satisfying an equality, an inequality usually describes a set of values.

The Python script develops inequality reasoning from elementary comparisons and interval notation to linear inequalities, compound inequalities, quadratic inequalities, absolute-value inequalities, sign analysis, logical operations, rational inequalities, numerical considerations, systems of inequalities, and practical applications.

The central mathematical idea is that an inequality defines a **solution set**. That solution set can be represented algebraically, with interval notation, as a union of intervals, or geometrically on a number line.

## Fundamental comparison relations

The four basic inequality relations are:

- `x < a`: `x` is less than `a`.
- `x > a`: `x` is greater than `a`.
- `x <= a`: `x` is less than or equal to `a`.
- `x >= a`: `x` is greater than or equal to `a`.

The equality relation is written as `x = a`.

The distinction between strict and non-strict inequalities determines whether a boundary value belongs to the solution set.

For example:

- `x > 3` excludes `3`.
- `x >= 3` includes `3`.
- `x < 3` excludes `3`.
- `x <= 3` includes `3`.

This distinction is represented directly by open and closed endpoints in interval notation.

## Intervals

An interval is a compact representation of a continuous set of real numbers.

The major forms are:

| Inequality | Interval |
|---|---|
| `a < x < b` | `(a, b)` |
| `a <= x <= b` | `[a, b]` |
| `a <= x < b` | `[a, b)` |
| `a < x <= b` | `(a, b]` |
| `x < b` | `(-∞, b)` |
| `x <= b` | `(-∞, b]` |
| `x > a` | `(a, ∞)` |
| `x >= a` | `[a, ∞)` |

Parentheses indicate that an endpoint is excluded. Square brackets indicate that an endpoint is included.

Infinity is never included as an endpoint because infinity is not a real number. Consequently, intervals extending toward infinity always use parentheses at the infinite side.

The `Interval` class in the script represents these sets computationally and provides a `contains()` method for membership testing.

## Linear inequalities

A linear inequality contains a variable only to the first power.

A general linear inequality can be written as

`ax + b < 0`

or with any of the other three inequality relations.

The ordinary algebraic operations used for equations also apply to inequalities, with one essential exception:

**Multiplying or dividing both sides by a negative number reverses the inequality symbol.**

For example:

`-2x < -6`

Dividing by `-2` gives

`x > 3`

The direction changes from `<` to `>`.

This rule follows from the ordering of the real numbers. Multiplication by a negative number reverses the order of two real numbers.

### Linear inequality algorithm

For an expression

`ax + b relation 0`

the boundary occurs at

`x = -b/a`

when `a` is nonzero.

If `a > 0`, the relation keeps its direction when solving for `x`.

If `a < 0`, the relation reverses.

If `a = 0`, the variable disappears and the problem becomes a statement about a constant. Such a statement is either always true or always false.

The script explicitly handles this degenerate case rather than attempting division by zero.

## Compound linear inequalities

A compound inequality contains two simultaneous conditions.

For example:

`2 < x + 1 <= 7`

Subtracting `1` from all three parts gives:

`1 < x <= 6`

The solution is

`(1, 6]`

Every operation must be applied consistently to every part of the compound inequality.

A second important form is a disjunction:

`x < a or x > b`

This describes values outside a central interval.

For example:

`x < 2 or x > 7`

has solution

`(-∞, 2) ∪ (7, ∞)`

## Fractions and exact arithmetic

Inequalities frequently produce rational boundaries.

For example:

`x/3 - 2/5 >= 1/5`

gives

`x/3 >= 3/5`

and therefore

`x >= 9/5`.

The script uses Python's `Fraction` type for several exact calculations. This avoids unnecessary floating-point approximation when a boundary is rational.

Exact arithmetic is particularly useful when a result such as `9/5` carries mathematical meaning that should not be converted immediately into a decimal approximation.

## Special linear cases

A coefficient of zero produces a constant inequality.

For example:

`0x + 5 > 0`

reduces to

`5 > 0`

which is always true. Therefore every real number satisfies the original inequality.

By contrast:

`0x - 5 > 0`

reduces to

`-5 > 0`

which is false. Therefore the solution set is empty.

These cases demonstrate why symbolic algorithms must handle zero coefficients explicitly.

## Quadratic inequalities

A quadratic inequality has the general form

`ax² + bx + c relation 0`

where `a` is nonzero.

The key difference from a linear inequality is that the expression can change sign at multiple critical points.

The corresponding quadratic equation

`ax² + bx + c = 0`

provides the critical values.

The quadratic formula is

`x = (-b ± √(b² - 4ac)) / (2a)`

The quantity

`D = b² - 4ac`

is the discriminant.

### Discriminant cases

If `D < 0`, there are no real roots.

If `D = 0`, there is one repeated real root.

If `D > 0`, there are two distinct real roots.

The discriminant therefore gives immediate information about the possible structure of a quadratic inequality.

## Sign analysis for quadratic inequalities

Finding the roots is not sufficient to solve a quadratic inequality.

Suppose

`f(x) = (x - 2)(x - 3)`

and the problem is

`f(x) > 0`.

The roots `2` and `3` divide the real number line into three regions:

`(-∞, 2)`

`(2, 3)`

`(3, ∞)`

Within each region, the sign of the polynomial is constant. A representative test value from each region determines its sign.

For this example:

- Values below `2` make the product positive.
- Values between `2` and `3` make the product negative.
- Values above `3` make the product positive.

Therefore:

`(x - 2)(x - 3) > 0`

has solution

`(-∞, 2) ∪ (3, ∞)`.

For a relation such as `>=`, the roots are included because the polynomial equals zero there.

## Factoring versus the quadratic formula

Factoring is often the fastest approach when a quadratic factors cleanly.

For example:

`x² - 5x + 6`

factors as

`(x - 2)(x - 3)`.

The quadratic formula is more general and works even when convenient integer factorization is unavailable.

Vertex analysis is useful when the geometric behavior of the parabola is important. The vertex occurs at

`x = -b/(2a)`.

If `a > 0`, the parabola opens upward.

If `a < 0`, it opens downward.

The leading coefficient therefore helps determine whether the quadratic is positive outside its roots or between its roots when two distinct real roots exist.

## Repeated roots

A repeated root has even multiplicity.

For example:

`(x - 2)²`

is never negative. It touches zero at `x = 2` but does not cross the horizontal axis.

Therefore the sign does not change when crossing a root of even multiplicity.

By contrast:

`(x - 2)³`

changes sign at `x = 2` because the root has odd multiplicity.

Root multiplicity is an important tool in polynomial sign analysis.

## Quadratics with no real roots

A quadratic with no real roots does not cross the x-axis.

For example:

`x² + 1`

is always positive over the real numbers.

Similarly:

`-x² - 1`

is always negative.

The sign of the leading coefficient determines which side of zero the expression occupies when there are no real roots.

## Absolute value

The absolute value of a real number is its distance from zero.

For a real number `x`:

`|x| = x` when `x >= 0`

and

`|x| = -x` when `x < 0`.

The geometric interpretation is particularly useful for inequalities.

The expression

`|x - a|`

represents the distance between `x` and `a`.

This makes absolute-value inequalities naturally interpretable as distance conditions.

## Absolute-value inequality rules

For `r >= 0`:

`|x - a| < r`

means that `x` is less than distance `r` from `a`.

Therefore:

`a - r < x < a + r`

Similarly:

`|x - a| <= r`

gives

`a - r <= x <= a + r`.

For an exterior condition:

`|x - a| > r`

means that `x` is farther than `r` from `a`.

Therefore:

`x < a - r or x > a + r`.

Likewise:

`|x - a| >= r`

gives

`x <= a - r or x >= a + r`.

The script implements these rules directly.

## Absolute-value equations versus inequalities

The equation

`|x - 4| = 3`

asks for points exactly three units away from `4`.

Therefore:

`x = 7 or x = 1`.

An inequality such as

`|x - 4| < 3`

asks for every point within three units of `4`, giving

`1 < x < 7`.

The distinction is important:

- Equality generally produces boundary points.
- A less-than inequality produces an interior interval.
- A greater-than inequality produces an exterior set.

## Absolute-value inequalities with linear expressions

Expressions such as

`|2x - 6| <= 4`

can be converted into a compound inequality:

`-4 <= 2x - 6 <= 4`.

After solving:

`1 <= x <= 5`.

The transformation works because the absolute value is constrained between a nonnegative lower and upper distance.

For an inequality such as

`|3x + 2| > 8`

the appropriate approach is to split the problem:

`3x + 2 > 8`

or

`3x + 2 < -8`.

This produces an exterior solution set.

## Negative absolute-value thresholds

Absolute value can never be negative.

Therefore, if `r < 0`:

`|x-a| < r`

has no solutions.

`|x-a| <= r`

also has no solutions.

Conversely:

`|x-a| > r`

and

`|x-a| >= r`

are automatically true for every real `x` when the negative threshold is considered appropriately.

The zero case is especially important:

`|x-a| < 0` has no solution.

`|x-a| <= 0` gives exactly `x = a`.

`|x-a| > 0` gives every real number except `a`.

`|x-a| >= 0` is true for every real number.

## Squaring inequalities

Squaring is not automatically an order-preserving operation over all real numbers.

For example:

`-3 < 2`

is true, but

`(-3)² < 2²`

becomes

`9 < 4`

which is false.

Squaring can be used safely when the relevant quantities are known to be nonnegative.

This principle is important in more advanced absolute-value problems.

For example:

`|2x - 1| > |x + 3|`

has nonnegative quantities on both sides. Squaring preserves the inequality:

`(2x - 1)² > (x + 3)²`.

The resulting quadratic inequality can then be solved using factoring and sign analysis.

## Intersections and unions

Two important set operations are intersection and union.

The intersection

`A ∩ B`

contains values belonging to both sets.

The union

`A ∪ B`

contains values belonging to at least one of the sets.

For inequalities:

`x > 2 and x < 7`

corresponds to the intersection

`(2, ∞) ∩ (-∞, 7)`

which is

`(2, 7)`.

By contrast:

`x < 2 or x > 7`

corresponds to

`(-∞, 2) ∪ (7, ∞)`.

Understanding these logical relationships is essential when combining inequalities.

## De Morgan's laws

The complement of a conjunction follows:

`NOT (A AND B) = (NOT A) OR (NOT B)`.

The complement of a disjunction follows:

`NOT (A OR B) = (NOT A) AND (NOT B)`.

For example:

`NOT (x >= 2 AND x <= 5)`

means that `x` is not in `[2, 5]`.

Therefore:

`x < 2 or x > 5`.

The complement of `[2, 5]` is consequently:

`(-∞, 2) ∪ (5, ∞)`.

These rules explain many of the logical structures encountered in inequality solving.

## Rational inequalities

A rational inequality contains a quotient of expressions.

For example:

`(x - 2)/(x + 1) > 0`.

Two types of critical points must be considered:

- Values that make the numerator zero.
- Values that make the denominator zero.

The numerator is zero at `x = 2`.

The denominator is zero at `x = -1`.

The denominator restriction is especially important because `x = -1` is undefined and can never be included in the solution.

The critical points divide the number line into regions where the rational expression has a constant sign.

This is the same sign-analysis principle used for polynomial inequalities, with the additional requirement of excluding denominator zeros.

## Polynomial sign analysis

For a factored polynomial such as

`(x - 1)(x + 2)(x - 4) >= 0`

the critical points are:

`-2`, `1`, and `4`.

They divide the number line into four regions.

A representative value from each region determines the sign. Since the polynomial can only change sign at a root, the sign remains constant inside each open region.

The roots themselves must be checked separately to determine whether they are included.

For `>= 0`, all real roots of the expression are included.

## Parameterized inequalities

Consider:

`ax > b`.

The result depends on the sign of `a`.

If `a > 0`:

`x > b/a`.

If `a < 0`:

`x < b/a`.

If `a = 0`, division by `a` is impossible and the original inequality must be evaluated separately.

This is a general lesson in symbolic mathematics: parameters can change the logical structure of a solution, so their possible values must be considered.

## Inequalities as predicates

An inequality can be treated computationally as a Boolean predicate.

For example:

`x² - 4 >= 0`

can be represented by a function that returns `True` or `False` for a supplied value.

Testing integer values demonstrates the behavior:

- `x = -3`: true
- `x = -2`: true
- `x = -1`: false
- `x = 0`: false
- `x = 1`: false
- `x = 2`: true
- `x = 3`: true

The exact solution is:

`(-∞, -2] ∪ [2, ∞)`.

Computational testing is useful for verification, but finite testing alone cannot prove a continuous real-number solution set.

## Validation and representative points

A solution interval contains infinitely many real values, so testing several values cannot mathematically prove an interval solution.

It can, though, detect common implementation errors.

For polynomial and rational inequalities, representative-point testing is especially useful because the sign is constant within each critical region.

A robust verification strategy is:

1. Identify critical points.
2. Divide the number line into regions.
3. Test a representative point from each region.
4. Test the critical points separately.
5. Compare the computed result with the expected interval structure.

## Number-line reasoning

A number line gives a geometric representation of a solution set.

Open endpoints indicate excluded boundary values.

Closed endpoints indicate included boundary values.

For example:

`x > 3`

uses an open endpoint at `3`.

`x >= 3`

uses a closed endpoint at `3`.

For a quadratic inequality, the critical points divide the number line into regions. The sign pattern can then be marked across the regions.

The script includes a text-based number-line approximation for integer sample points. This is only a visualization aid because the real number line is continuous.

## Monotonicity and transformations

Inequality solving is closely related to monotonic functions.

If a function is strictly increasing, it preserves order:

`a < b` implies `f(a) < f(b)`.

If a function is strictly decreasing, it reverses order:

`a < b` implies `f(a) > f(b)`.

This explains why certain transformations preserve inequality direction while others reverse it.

For positive numbers:

`x < y`

implies

`x² < y²`

when both values are nonnegative.

The logarithm is increasing on its domain:

`0 < x < y`

implies

`log(x) < log(y)`.

The exponential function is also increasing:

`x < y`

implies

`e^x < e^y`.

Recognizing monotonicity is useful when solving inequalities involving functions beyond polynomials.

## Systems of linear inequalities

A system combines multiple constraints.

For example:

`x >= 0`

`y >= 0`

`x + y <= 10`

`2x + y <= 14`.

Instead of describing a one-dimensional interval, these constraints describe a region in the plane.

A point is feasible only when it satisfies every constraint simultaneously.

This concept is fundamental to optimization and linear programming.

## Real-world applications

Inequalities naturally model constraints.

### Business break-even analysis

Suppose revenue is:

`R = 80x`

and cost is:

`C = 50x + 900`.

Profit is:

`P = R - C`

so:

`P = 30x - 900`.

For a nonnegative profit:

`30x - 900 >= 0`.

Therefore:

`x >= 30`.

The inequality identifies the minimum number of units required to avoid a loss.

### Measurement tolerance

If a measurement must remain within `0.05` units of `10`, the condition is:

`|x - 10| <= 0.05`.

This gives:

`9.95 <= x <= 10.05`.

Absolute-value inequalities are therefore natural models for tolerances and acceptable deviations.

### Temperature constraints

If a process requires temperature between `18°C` and `24°C`:

`18 <= T <= 24`.

The equivalent tolerance representation is:

`|T - 21| <= 3`.

Both describe the same interval.

### Threshold conditions

A promotion that requires spending at least `500` is represented by:

`s >= 500`.

Its interval is:

`[500, ∞)`.

A promotion requiring spending strictly above `500` is represented by:

`s > 500`.

Its interval is:

`(500, ∞)`.

The choice between strict and non-strict inequality directly determines whether the threshold value qualifies.

## Important distinctions

### Equation versus inequality

An equation generally asks where two expressions are equal.

An inequality asks where one expression is greater than, less than, or equal to another.

For example:

`x² = 9`

has two solutions:

`x = -3` and `x = 3`.

But:

`x² >= 9`

has infinitely many solutions:

`x <= -3 or x >= 3`.

### Single interval versus union

`[2, 7]` is one continuous interval.

`(-∞, 2) ∪ (7, ∞)` is a union of two disjoint intervals.

A union is necessary when the solution has separated regions.

### Strict versus non-strict

`>` and `<` exclude equality.

`>=` and `<=` include equality.

The endpoint notation must match this distinction.

### Zero versus undefined

A polynomial can equal zero at a root, and that root may be included depending on the inequality.

A rational expression is undefined wherever its denominator equals zero. Such a value is always excluded.

## Common mistakes

### Forgetting to reverse the inequality

Incorrect:

`-2x > 8 -> x > -4`

Correct:

`-2x > 8 -> x < -4`.

### Treating a quadratic inequality like an equation

Solving

`x² - 9 = 0`

only finds the boundary points.

For

`x² - 9 > 0`

the intervals outside the roots must also be analyzed.

### Incorrect endpoint notation

For `x > 4`, the interval is `(4, ∞)`, not `[4, ∞)`.

For `x >= 4`, the interval is `[4, ∞)`.

### Forgetting denominator restrictions

In

`(x - 2)/(x + 1) > 0`,

`x = -1` must be excluded because the expression is undefined there.

### Confusing absolute-value equations with inequalities

`|x-a| = r` identifies points at an exact distance.

`|x-a| < r` identifies all points inside the distance.

`|x-a| > r` identifies points outside the distance.

### Testing only one quadratic region

A quadratic can be positive in one region and negative in another. Testing a single point is not sufficient when multiple critical points exist.

### Squaring without sign analysis

Squaring can change the logical meaning of an inequality when negative values are possible.

The signs of both sides must be considered before using squaring as an equivalent transformation.

## Edge cases

The script explicitly addresses several important edge cases.

A zero linear coefficient can produce an inequality that is always true or always false.

A quadratic can have no real roots, one repeated root, or two distinct roots.

An absolute-value threshold can be negative, zero, or positive.

A rational expression can contain undefined critical points.

An interval can be bounded, unbounded, open, closed, or half-open.

Floating-point calculations can produce tiny numerical discrepancies around theoretically exact boundaries.

These cases matter because a general-purpose solver cannot assume that every problem has the simplest standard structure.

## Numerical precision

Python floating-point values use finite binary representations. Some decimal values cannot be represented exactly.

For example, the result of:

`0.1 + 0.2`

is not represented internally in exactly the same way as the mathematical number `0.3`.

For numerical inequality calculations, comparisons near a boundary may therefore require a tolerance.

The script demonstrates `math.isclose()` for approximate comparison.

For rational educational examples, `Fraction` is preferable because it preserves exact rational values.

## Implementation design

The script separates several mathematical responsibilities into distinct functions and classes.

The `Interval` class stores:

- left endpoint
- right endpoint
- left endpoint inclusion
- right endpoint inclusion

It also provides membership testing and interval notation.

The `Quadratic` class stores:

- coefficient `a`
- coefficient `b`
- coefficient `c`

and provides:

- evaluation
- discriminant calculation
- real-root calculation

The quadratic inequality solver uses the following conceptual pipeline:

1. Validate the relation.
2. Calculate the discriminant.
3. Determine real critical points.
4. Divide the number line into sign regions.
5. Test representative values.
6. Select regions satisfying the requested relation.
7. Include roots when required by `<=` or `>=`.

The absolute-value solver instead uses the geometric distance interpretation and handles negative and zero thresholds explicitly.

## Performance considerations

For a single linear inequality, the computational work is constant time.

For a quadratic inequality, the principal operations are also constant time because the polynomial degree is fixed.

For a general polynomial or rational expression with many critical points, the sign-analysis approach requires sorting the critical points. If there are `n` distinct critical points, sorting generally requires `O(n log n)` time.

Once the critical points are ordered, evaluating one representative point per region requires approximately `O(n)` evaluations.

The mathematical degree of the expression, the number of distinct roots, and the cost of evaluating the expression therefore influence performance.

## Exactness and symbolic limitations

The educational implementation uses standard Python arithmetic rather than a complete computer algebra system.

It can exactly represent rational coefficients using `Fraction`, but irrational roots are represented numerically using floating-point square roots.

This means that expressions involving complicated irrational or symbolic structures may require additional symbolic techniques in a full computer algebra implementation.

The script deliberately focuses on transparent mathematical algorithms rather than hiding the reasoning inside a symbolic solver.

## Security and input considerations

The script does not execute arbitrary user-provided Python expressions and does not depend on external files or network services.

This design avoids risks associated with dynamically evaluating untrusted expressions.

If a production inequality application accepted mathematical expressions from users, it would need explicit parsing and validation rather than passing raw input to Python's `eval()`.

A secure parser should define an allowed grammar, permitted operators, supported functions, variable names, numeric formats, and error behavior.

## Debugging considerations

When an inequality implementation produces an unexpected result, the most useful debugging information usually includes:

- the original expression
- the simplified expression
- all critical points
- domain restrictions
- the sign of each interval
- endpoint inclusion decisions
- representative test values
- the final interval representation

For quadratic and rational inequalities, a sign chart is especially effective because it reveals whether an error occurred in root detection, sign evaluation, or endpoint handling.

## Verification strategy

The script contains assertion-based tests covering:

- positive linear coefficients
- negative linear coefficients
- quadratic sign regions
- absolute-value intervals
- negative absolute-value thresholds
- interval membership
- open and closed endpoints

These tests do not replace mathematical proof. They verify that the implemented computational rules behave consistently for selected cases.

A robust mathematical implementation should combine algorithmic reasoning with representative test cases and explicit edge-case tests.

## Practical solving framework

A reliable general procedure for inequalities is:

1. Identify the type of inequality.
2. Simplify the expressions.
3. Preserve domain restrictions.
4. Isolate the variable where direct algebra is appropriate.
5. Reverse the relation when multiplying or dividing by a negative quantity.
6. For polynomial expressions, identify real zeros.
7. For rational expressions, identify both zeros and undefined points.
8. Divide the number line into critical regions.
9. Determine the sign on each region.
10. Check whether critical points satisfy the original relation.
11. Express the result using interval notation or a union of intervals.
12. Test representative values from the proposed solution and its complement.

This procedure unifies many apparently different inequality problems under the same solution-set perspective.
