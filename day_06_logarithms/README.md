# Logarithms: Notation, Properties, Change of Base, Natural Logarithms, and Computational Applications

## 1. Introduction

A logarithm is the inverse operation of exponentiation. It answers the question:

> What exponent must be applied to a given base to produce a particular positive number?

The defining relationship is

    b^y = x  <=>  log_b(x) = y

where:

- `b` is the logarithm base.
- `x` is the logarithm argument.
- `y` is the logarithm value.

For example,

    2^5 = 32

therefore,

    log_2(32) = 5

Logarithms are important because they transform multiplicative and exponential relationships into additive and linear relationships. This makes them useful in algebra, calculus, numerical computation, information theory, scientific measurement, statistics, probability, algorithms, and data analysis.

The accompanying Python script develops logarithms from their elementary definition through numerical stability techniques and computational applications.

---

## 2. Logarithm Notation

The expression

    log_b(x)

is read as "the logarithm of x to base b."

It means the unique real number `y` satisfying

    b^y = x

For example:

    log_2(8) = 3
    log_5(25) = 2
    log_10(1000) = 3

The exponent is the central quantity represented by a logarithm.

### Exponential and logarithmic forms

The two equivalent forms are:

    b^y = x

and

    log_b(x) = y

Changing between these forms is one of the most important elementary logarithm skills.

---

## 3. Restrictions on a Real Logarithm

For `log_b(x)` to be a real-valued logarithm, three conditions must hold:

    b > 0
    b != 1
    x > 0

### Why must the base be positive?

A standard real logarithm requires a positive base. Negative bases introduce complications involving whether arbitrary real exponents are defined.

### Why cannot the base equal 1?

If the base were 1,

    1^y = 1

for every real `y`.

There would therefore be no unique exponent for values other than 1, and infinitely many exponents for the value 1.

### Why must the argument be positive?

For a positive real base, real exponentiation does not produce negative values or zero. Therefore a real logarithm cannot have zero or a negative argument.

The Python script explicitly validates these restrictions before evaluating logarithms.

---

## 4. Common and Natural Logarithms

Two logarithm bases are especially important.

### Common logarithm

The common logarithm has base 10:

    log_10(x)

It is commonly written as:

    log(x)

when the context makes the base clear.

Examples:

    log_10(10) = 1
    log_10(100) = 2
    log_10(1000) = 3

Common logarithms are especially useful for decimal orders of magnitude and logarithmic measurement scales.

### Natural logarithm

The natural logarithm has base `e`:

    ln(x) = log_e(x)

where

    e ≈ 2.718281828459045

The natural logarithm is fundamental to calculus, continuous growth, probability, statistics, differential equations, and numerical computation.

In Python:

    math.log(x)

computes the natural logarithm.

---

## 5. Fundamental Logarithm Identities

Several identities follow directly from the inverse relationship between exponentiation and logarithms.

### Logarithm of 1

    log_b(1) = 0

because

    b^0 = 1

### Logarithm of the base

    log_b(b) = 1

because

    b^1 = b

### Inverse relationships

    log_b(b^x) = x

and

    b^(log_b(x)) = x

These identities express the fact that logarithms and exponentiation are inverse operations.

The script evaluates these identities numerically and verifies the inverse relationships.

---

## 6. Product Rule

For positive `x` and `y`:

    log_b(xy) = log_b(x) + log_b(y)

The multiplication of quantities becomes addition in logarithmic space.

Suppose:

    x = b^m
    y = b^n

Then:

    xy = b^m b^n
       = b^(m+n)

Taking the logarithm gives:

    log_b(xy) = m + n
              = log_b(x) + log_b(y)

This identity is one of the central reasons logarithms are useful in computation.

---

## 7. Quotient Rule

For positive `x` and `y`:

    log_b(x/y) = log_b(x) - log_b(y)

Division becomes subtraction.

If:

    x = b^m
    y = b^n

then:

    x/y = b^(m-n)

and therefore:

    log_b(x/y) = m - n

The script demonstrates the rule numerically.

---

## 8. Power Rule

For positive `x`:

    log_b(x^k) = k log_b(x)

An exponent becomes a multiplier.

For example:

    log_2(8^3)
    = 3 log_2(8)
    = 3 * 3
    = 9

This rule is particularly useful when simplifying expressions and solving equations.

---

## 9. An Important Non-Property

A common mistake is assuming that logarithms distribute over addition.

In general:

    log_b(x + y) != log_b(x) + log_b(y)

There is no equivalent addition rule analogous to the product rule.

The valid transformation is:

    log_b(xy) = log_b(x) + log_b(y)

not:

    log_b(x+y) = log_b(x) + log_b(y)

The script explicitly contrasts correct and incorrect expressions.

---

## 10. Change of Base

A logarithm can be expressed using any other valid logarithm base:

    log_b(x) = log_k(x) / log_k(b)

Two especially useful forms are:

    log_b(x) = ln(x) / ln(b)

and

    log_b(x) = log_10(x) / log_10(b)

This is called the change-of-base formula.

### Why it matters computationally

Programming environments may provide natural, common, or binary logarithms directly rather than arbitrary-base logarithms.

For example:

    math.log(x) / math.log(b)

computes `log_b(x)`.

Python also provides:

    math.log(x, b)

and specialized functions:

    math.log2(x)
    math.log10(x)

The script compares these approaches.

---

## 11. Python Logarithm Functions

The standard `math` module provides several logarithm-related functions.

### Natural logarithm

    math.log(x)

computes:

    ln(x)

### Logarithm with a specified base

    math.log(x, base)

computes:

    log_base(x)

### Binary logarithm

    math.log2(x)

computes:

    log_2(x)

This is particularly important in computer science.

### Common logarithm

    math.log10(x)

computes:

    log_10(x)

### Numerically stable `log1p`

    math.log1p(x)

computes:

    ln(1+x)

with improved numerical behavior when `x` is very close to zero.

---

## 12. Numerical Precision and `log1p`

Floating-point arithmetic cannot represent every real number exactly.

Consider:

    1 + 1e-16

Depending on floating-point precision, the addition may round to exactly 1.

This makes the naive calculation

    math.log(1 + x)

potentially less accurate when `x` is extremely small.

The specialized function

    math.log1p(x)

is designed for this situation.

This is an example of an important computational principle:

> Mathematically equivalent formulas do not necessarily have equivalent numerical stability.

The script compares `math.log(1+x)` with `math.log1p(x)`.

---

## 13. Solving Exponential Equations

Consider:

    b^x = c

Taking logarithms gives:

    log_b(b^x) = log_b(c)

Therefore:

    x = log_b(c)

Using natural logarithms:

    x = ln(c) / ln(b)

The Python function `solve_exponential_equation()` implements this transformation.

For example:

    2^x = 64

gives:

    x = log_2(64)
      = 6

---

## 14. Solving Logarithmic Equations

Consider:

    log_b(x) = c

Convert to exponential form:

    x = b^c

For example:

    log_2(x) = 7

gives:

    x = 2^7
      = 128

The script implements this relationship directly.

---

## 15. Linear Logarithmic Equations

An equation such as

    2 log_10(x) + 3 = 7

can first be rearranged:

    2 log_10(x) = 4

then:

    log_10(x) = 2

and therefore:

    x = 10^2
      = 100

The important computational principle is to isolate the logarithm before converting it into exponential form.

---

## 16. Domain Checking in Logarithmic Equations

Domain restrictions must be considered before accepting algebraic solutions.

For:

    log(x - 3)

the argument must be positive:

    x - 3 > 0

therefore:

    x > 3

For:

    log(2x + 1)

the condition is:

    2x + 1 > 0

so:

    x > -1/2

An algebraic manipulation may produce a candidate that does not belong to the original domain. Such candidates must be rejected.

The script demonstrates domain checking for several logarithmic expressions.

---

## 17. Logarithmic Inequalities

The direction of logarithmic inequalities depends on the base.

### Base greater than 1

If:

    b > 1

then `log_b(x)` is increasing.

Therefore:

    x_1 < x_2

implies:

    log_b(x_1) < log_b(x_2)

### Base between 0 and 1

If:

    0 < b < 1

then `log_b(x)` is decreasing.

Therefore:

    x_1 < x_2

implies:

    log_b(x_1) > log_b(x_2)

This reversal is a major exception that must be remembered when solving inequalities.

---

## 18. Logarithmic Graphs

The graph

    y = log_b(x)

has:

- Domain `(0, infinity)`
- Range `(-infinity, infinity)`
- Vertical asymptote `x = 0`
- x-intercept `(1, 0)`

It is the inverse of:

    y = b^x

For `b > 1`, the graph increases.

For `0 < b < 1`, the graph decreases.

The script evaluates representative points for several bases to make these behaviors explicit.

---

## 19. Logarithmic Transformations

A transformed logarithmic function can have the form:

    y = A log_b(x - h) + k

where:

- `A` controls vertical scaling and reflection.
- `h` shifts the graph horizontally.
- `k` shifts the graph vertically.
- `b` controls the fundamental logarithmic behavior.

The domain condition is:

    x - h > 0

therefore:

    x > h

The vertical asymptote becomes:

    x = h

The script implements transformed logarithmic functions and checks their domains.

---

## 20. Calculus and Natural Logarithms

The derivative of the natural logarithm is:

    d/dx ln(x) = 1/x

For an arbitrary base:

    d/dx log_b(x) = 1 / (x ln(b))

The natural logarithm is especially convenient in calculus because its derivative has the simple form `1/x`.

The script compares numerical derivatives with analytical derivatives.

---

## 21. Logarithmic Differentiation

Logarithmic differentiation is useful when a function contains products, quotients, or variable exponents.

Consider:

    y = x^x

Taking the natural logarithm:

    ln(y) = x ln(x)

Differentiate:

    y'/y = ln(x) + 1

Therefore:

    y' = x^x [ln(x) + 1]

The script calculates this derivative analytically and compares it with a numerical finite-difference approximation.

---

## 22. Decibels

Decibels use logarithms to express ratios on a compressed scale.

For power ratios:

    dB = 10 log_10(P2/P1)

For amplitude ratios:

    dB = 20 log_10(A2/A1)

The difference between the coefficients `10` and `20` is important.

The power relationship and amplitude relationship are not interchangeable.

Logarithmic measurement is useful because physical quantities can span many orders of magnitude.

---

## 23. pH

The pH scale is logarithmic:

    pH = -log_10([H+])

where `[H+]` is the hydrogen ion concentration.

For example, if:

    [H+] = 10^-7

then:

    pH = 7

The negative sign reverses the direction so that increasing hydrogen ion concentration corresponds to decreasing pH.

---

## 24. Logarithmic Measurement Scales

Many measurement systems represent multiplicative changes using additive differences.

If:

    D = log_b(R)

then:

    R = b^D

Thus a difference of one unit on the logarithmic scale corresponds to multiplication by the base.

For a base-10 scale:

    difference = 1 -> ratio = 10
    difference = 2 -> ratio = 100
    difference = 3 -> ratio = 1000

This makes logarithmic scales useful for quantities spanning large numerical ranges.

---

## 25. Binary Logarithms

Computer science frequently uses:

    log_2(n)

A binary logarithm answers:

> How many times must 2 be multiplied by itself to reach n?

For powers of two:

    log_2(1) = 0
    log_2(2) = 1
    log_2(4) = 2
    log_2(8) = 3
    log_2(16) = 4

Binary logarithms are especially important for algorithms and information theory.

---

## 26. Logarithms and Bits

If there are `N` equally likely possibilities, the information required to distinguish among them is:

    log_2(N)

bits.

Examples:

    2 possibilities -> 1 bit
    4 possibilities -> 2 bits
    8 possibilities -> 3 bits
    256 possibilities -> 8 bits

For arbitrary `N`, the mathematical value may not be an integer. If a fixed-length binary representation must distinguish all possibilities, the required number of whole bits is generally related to:

    ceil(log_2(N))

---

## 27. Shannon Entropy

For probabilities `p_1, p_2, ..., p_n`, Shannon entropy is:

    H(X) = -sum(p_i log_b(p_i))

When the base is 2, entropy is measured in bits.

The Python implementation treats zero-probability terms specially because:

    p log(p)

approaches zero as `p` approaches zero from the positive side.

The probabilities must be nonnegative and must sum to 1.

Entropy is not simply the number of possible outcomes. It incorporates their probability distribution.

A uniform distribution has maximum entropy among distributions over the same finite number of outcomes.

---

## 28. Binary Search and O(log n)

Binary search repeatedly divides a sorted search interval approximately in half.

After one step:

    n -> n/2

After two steps:

    n -> n/4

After `k` steps:

    n -> n/2^k

When the remaining size reaches approximately 1:

    n / 2^k ≈ 1

which implies:

    2^k ≈ n

and therefore:

    k ≈ log_2(n)

This is why binary search has logarithmic time complexity:

    O(log n)

The script implements binary search and records its comparisons.

---

## 29. Growth Rates

Important growth-rate relationships include:

    log n << sqrt(n) << n << n log n << n^2 << 2^n

for sufficiently large `n`.

A logarithm grows extremely slowly compared with a linear function.

For example:

    log_2(1,000,000) ≈ 19.93

while:

    1,000,000

is one million.

This difference explains why logarithmic-time algorithms can remain efficient as input sizes grow.

---

## 30. Logarithms in Balanced Trees

A balanced tree has logarithmic height.

For a branching factor `b`, the approximate number of levels required to accommodate `n` nodes is:

    log_b(n)

Increasing the branching factor reduces the required height.

This principle appears in structures such as balanced search trees and multiway tree designs.

The exact height of a particular data structure depends on its structural rules, so `log_b(n)` should be interpreted as a mathematical scale rather than automatically as an exact implementation-specific height.

---

## 31. Digit Counting

For a positive integer `n`, the number of decimal digits is:

    floor(log_10(n)) + 1

For example:

    n = 999

gives:

    floor(log_10(999)) + 1
    = 2 + 1
    = 3

Zero is a special case because `log_10(0)` is undefined, while zero has one decimal digit.

Similarly, the number of binary digits of a positive integer is:

    floor(log_2(n)) + 1

The script handles zero and negative values explicitly.

---

## 32. Powers of Two

For a positive integer `n`, being a power of two means:

    n = 2^k

for some integer `k`.

A common bitwise test is:

    n > 0 and (n & (n - 1)) == 0

The logarithmic interpretation is:

    log_2(n)

is an integer precisely when `n` is an exact power of two.

Floating-point logarithms should not be used blindly for exact integer classification when an exact integer or bitwise method is available.

---

## 33. Compound Growth

An exponential growth model can be written:

    A = P b^t

To solve for time:

    A/P = b^t

then:

    t = log_b(A/P)

or:

    t = ln(A/P) / ln(b)

This applies to population models, financial growth, repeated percentage changes, and other multiplicative processes.

---

## 34. Compound Interest

For periodic compounding:

    A = P(1 + r/n)^(nt)

where:

- `P` is the principal.
- `r` is the annual rate.
- `n` is the number of compounding periods per year.
- `t` is time.
- `A` is the final amount.

To solve for `t`:

    t =
    ln(A/P)
    /
    [n ln(1+r/n)]

The script demonstrates this calculation.

---

## 35. Continuous Compounding

Continuous compounding is modeled by:

    A = Pe^(rt)

Natural logarithms arise naturally when solving this model.

For example:

    ln(A/P) = rt

and therefore:

    t = ln(A/P) / r

The natural logarithm is closely associated with continuous exponential growth because `e^x` is its own derivative.

---

## 36. Half-Life

A half-life model can be written:

    fraction = (1/2)^t

where `t` is measured in half-lives.

To find the number of half-lives needed to reach a fraction `f`:

    t = log_(1/2)(f)

Using natural logarithms:

    t = ln(f) / ln(1/2)

For example, reaching 1% remaining requires several half-lives because exponential decay is multiplicative rather than linear.

---

## 37. Orders of Magnitude

The quantity:

    floor(log_10(x))

identifies the decimal order of magnitude for positive `x`.

Examples:

    1000 = 10^3
    log_10(1000) = 3

    0.001 = 10^-3
    log_10(0.001) = -3

Logarithms therefore provide a natural language for comparing values separated by powers of ten.

---

## 38. Log-Domain Arithmetic

Suppose:

    x > 0
    y > 0

Then:

    ln(xy) = ln(x) + ln(y)

Instead of multiplying potentially enormous values, one can sometimes work with their logarithms and add:

    log_product = log_x + log_y

This is called working in the log domain.

It is useful when products contain many factors or when direct multiplication could overflow.

The final result can be recovered with exponentiation when necessary.

---

## 39. Log Probabilities

Products of probabilities can become extremely small.

For example:

    p1 * p2 * p3 * ... * pn

may underflow in floating-point arithmetic when many probabilities are multiplied.

Taking logarithms gives:

    ln(p1 p2 ... pn)
    =
    ln(p1) + ln(p2) + ... + ln(pn)

This converts multiplication into addition and often provides better numerical behavior.

The script demonstrates both direct multiplication and logarithmic-domain computation.

---

## 40. Geometric Mean

For positive values:

    x_1, x_2, ..., x_n

the geometric mean is:

    (x_1 x_2 ... x_n)^(1/n)

Using logarithms:

    ln(G)
    =
    [ln(x_1) + ln(x_2) + ... + ln(x_n)] / n

Therefore:

    G = exp(mean(ln(x_i)))

This formulation is computationally useful for multiplicative quantities and growth factors.

The geometric mean should not be confused with the arithmetic mean.

---

## 41. Log-Sum-Exp

A particularly important numerical problem is computing:

    ln(exp(x_1) + exp(x_2) + ... + exp(x_n))

The naive implementation can overflow when the `x_i` values are large.

Let:

    m = max(x_i)

Then:

    ln(sum(exp(x_i)))
    =
    m + ln(sum(exp(x_i - m)))

Since every `x_i - m <= 0`, the exponentials are much safer to calculate.

This is known as the log-sum-exp trick.

The script implements `log_sum_exp()` and compares it with the naive formulation.

---

## 42. Stable Two-Term Log Addition

For two numbers:

    ln(exp(a) + exp(b))

the stable form is obtained by taking:

    m = max(a,b)

and computing:

    m + ln(1 + exp(min(a,b)-m))

The implementation uses `math.log1p()` to improve accuracy when the second term is small.

This technique is important when calculations must remain in logarithmic space.

---

## 43. Log-Softmax

Given values called logits:

    x_1, x_2, ..., x_n

softmax probabilities are:

    exp(x_i) / sum(exp(x_j))

The logarithm of the softmax is:

    x_i - log(sum(exp(x_j)))

Using log-sum-exp makes the computation much more stable.

The script implements:

    log_softmax(values)

and exponentiates its result to verify that the resulting probabilities sum to approximately 1.

---

## 44. Floating-Point Overflow and Underflow

Direct exponential computation can fail for sufficiently large values.

For example:

    exp(1000)

cannot be represented as a normal Python floating-point number and raises an overflow error.

Very small exponentials can instead underflow toward zero.

Logarithmic representations can retain useful information about magnitude without constructing the enormous or tiny number itself.

This is one of the most important computational advantages of logarithmic representations.

---

## 45. Extreme Products

Suppose a calculation requires:

    10^100 * 10^120 * 10^90

The result is around:

    10^310

which is beyond the approximate maximum range of a standard IEEE-754 double-precision floating-point value.

In logarithmic form:

    ln(product)
    =
    100 ln(10)
    + 120 ln(10)
    + 90 ln(10)

The calculation remains manageable because the huge product itself does not need to be constructed.

---

## 46. Logarithmic Interpolation

Ordinary interpolation assumes equal additive spacing.

Logarithmic interpolation assumes equal spacing in logarithmic space.

For a positive variable `x`, a normalized logarithmic position between `x_min` and `x_max` is:

    t =
    [log(x) - log(x_min)]
    /
    [log(x_max) - log(x_min)]

This is useful when values span multiple orders of magnitude.

For example, on a base-10 scale, the points:

    1, 10, 100, 1000

are equally spaced logarithmically even though they are not equally spaced linearly.

---

## 47. Logarithmic Bucketing

Logarithmic buckets group values by multiplicative scale.

For base 10:

    1 <= x < 10      -> bucket 0
    10 <= x < 100    -> bucket 1
    100 <= x < 1000  -> bucket 2

The bucket can be obtained using:

    floor(log_10(x))

for positive values.

This technique can be useful for visualizations, metrics, distributions, and systems where numerical values span several orders of magnitude.

---

## 48. Exponential Relationships and Linearization

Suppose:

    y = A b^x

Taking the natural logarithm gives:

    ln(y) = ln(A) + x ln(b)

This has the form:

    Y = c + mx

where:

    Y = ln(y)
    c = ln(A)
    m = ln(b)

Therefore an exponential relationship becomes a linear relationship after taking logarithms.

The parameters can then be recovered using:

    A = exp(c)

and:

    b = exp(m)

The script demonstrates this transformation and estimates an exponential model using ordinary least squares on the transformed values.

---

## 49. Numerical Root Finding

Not every logarithmic equation has a convenient closed-form solution.

Numerical methods can solve equations of the form:

    f(x) = 0

The script demonstrates two methods.

### Newton-Raphson

Newton's method uses:

    x_(n+1) = x_n - f(x_n)/f'(x_n)

It can converge very quickly when the initial estimate is good and the derivative behaves well.

Potential problems include:

- Zero derivatives.
- Poor initial guesses.
- Divergence.
- Convergence to an unintended root.
- Domain violations.

### Bisection

Bisection repeatedly divides an interval in half.

It requires a sign change across the initial interval and is generally much more robust than Newton's method.

Its convergence is slower but predictable.

The script uses both approaches on logarithmic equations.

---

## 50. Error Sensitivity

For:

    f(x) = ln(x)

the derivative is:

    f'(x) = 1/x

For a small change `dx`:

    d(ln x) ≈ dx/x

Thus the absolute change in the logarithm is approximately the relative change in the original value.

This property explains why logarithms are closely related to relative error and percentage changes.

---

## 51. Bases Between Zero and One

A logarithm base does not have to be greater than one.

Any:

    0 < b < 1

is valid.

For example:

    log_(1/2)(8) = -3

because:

    (1/2)^(-3) = 8

The important difference is monotonicity:

- Bases greater than 1 produce increasing logarithms.
- Bases between 0 and 1 produce decreasing logarithms.

---

## 52. Complex Logarithms

The real logarithm requires:

    x > 0

Complex analysis extends logarithms to complex arguments.

For a nonzero complex number:

    z = r e^(i theta)

a complex logarithm has the form:

    log(z) = ln(r) + i(theta + 2*pi*k)

where `k` is any integer.

Therefore the complex logarithm is inherently multi-valued.

Programming libraries such as Python's `cmath` select a principal branch for their standard complex logarithm.

This is fundamentally different from the ordinary real logarithm.

---

## 53. Logarithmic Distance

For positive values, a multiplicative distance can be defined as:

    |ln(x/y)|

This has a useful property: multiplicative changes have the same distance regardless of scale.

For example, comparing:

    1 and 2

and:

    100 and 200

produces the same logarithmic distance because both pairs differ by a factor of two.

This is useful when relative rather than absolute differences matter.

---

## 54. Performance Considerations

Logarithm functions involve transcendental numerical operations and are more computationally expensive than simple arithmetic such as addition.

Important principles include:

- Avoid computing the same logarithm repeatedly when the input is unchanged.
- Use specialized functions such as `log2`, `log10`, and `log1p` when appropriate.
- Prefer mathematically stable formulations.
- Do not optimize logarithm calls prematurely without measuring the actual workload.
- Preserve correctness and numerical stability before micro-optimizing.

The script includes a small timing benchmark using `time.perf_counter()`.

Benchmark results depend on hardware, Python version, operating system, and workload, so a single execution time should not be treated as a universal performance measurement.

---

## 55. Security and Reliability Considerations

Logarithms can occur in security-related computations such as entropy estimates, search-space calculations, probabilistic scoring, and anomaly detection.

Important considerations include:

### Validate inputs

A logarithm must not be evaluated on invalid domains.

### Do not use dynamic evaluation

Numeric input should be parsed using safe conversion functions such as:

    float(text)

rather than executing arbitrary input.

### Maintain numerical stability

Probability calculations can become unstable when probabilities are extremely small. Log-domain methods can mitigate underflow.

### Understand entropy correctly

The logarithm of a search space does not automatically describe the practical security of a password or authentication system. Real security also depends on randomness, attack models, rate limits, password reuse, implementation quality, and other factors.

### Avoid floating-point assumptions

Two mathematically equal calculations may differ by a small floating-point error. Numerical comparisons should use appropriate tolerances when exact equality is not guaranteed.

---

## 56. Common Mistakes

### Mistake 1: Incorrect product rule

Incorrect:

    log(xy) = log(x) * log(y)

Correct:

    log(xy) = log(x) + log(y)

### Mistake 2: Incorrect quotient rule

Incorrect:

    log(x/y) = log(x) / log(y)

Correct:

    log(x/y) = log(x) - log(y)

### Mistake 3: Incorrect addition rule

Incorrect:

    log(x+y) = log(x) + log(y)

There is no such general identity.

### Mistake 4: Ignoring the domain

Expressions such as:

    log(x-5)

require:

    x > 5

### Mistake 5: Forgetting the base

The value of a logarithm depends on its base.

For example:

    log_2(100)

and:

    log_10(100)

are different numbers.

### Mistake 6: Confusing `ln` and `log10`

In Python:

    math.log(x)

means the natural logarithm.

The common logarithm is:

    math.log10(x)

### Mistake 7: Using a naive exponential sum

Computing:

    log(sum(exp(x)))

directly can overflow.

The log-sum-exp transformation is safer.

---

## 57. Limitations

Real logarithms cannot directly accept:

- Zero arguments.
- Negative arguments.
- Invalid bases.
- Base 1.

Floating-point implementations also have finite precision and finite numerical ranges.

Mathematical identities may be exact while their floating-point implementations produce tiny numerical errors.

Complex logarithms require branch conventions and are fundamentally more complicated than real logarithms.

Approximation formulas such as `log(n)` for algorithmic complexity describe asymptotic behavior rather than exact operation counts.

---

## 58. Important Distinctions

| Concept | Meaning |
|---|---|
| `log_b(x)` | Exponent required to obtain `x` from `b` |
| `ln(x)` | Logarithm with base `e` |
| `log10(x)` | Logarithm with base 10 |
| `log2(x)` | Logarithm with base 2 |
| Product rule | Multiplication becomes addition |
| Quotient rule | Division becomes subtraction |
| Power rule | Exponent becomes multiplication |
| Change of base | Converts a logarithm to another base |
| Log domain | Represents positive quantities by their logarithms |
| Log-sum-exp | Stable computation of a logarithm of exponential sums |
| Entropy | Expected information measured using logarithms |
| `O(log n)` | Logarithmic asymptotic growth |
| `log1p(x)` | Stable computation of `ln(1+x)` |
| Complex logarithm | Extension of logarithms to complex numbers |

---

## 59. Practical Computational Patterns Demonstrated

The Python script contains complete implementations for:

- Arbitrary-base logarithms.
- Base validation.
- Exponential equation solving.
- Logarithmic equation solving.
- Logarithmic transformations.
- Numerical derivatives.
- Logarithmic differentiation examples.
- Decibel calculations.
- pH calculations.
- Shannon entropy.
- Binary search.
- Digit counting.
- Power-of-two testing.
- Compound growth.
- Half-life calculations.
- Log-domain arithmetic.
- Log-sum-exp.
- Log-softmax.
- Stable two-term logarithmic addition.
- Geometric mean.
- Logarithmic interpolation.
- Logarithmic bucketing.
- Newton-Raphson root finding.
- Bisection root finding.
- Linear regression after logarithmic transformation.
- Input validation.
- Numerical property tests.

Each implementation is designed to expose the mathematical relationship rather than merely calculate an isolated answer.

---

## 60. Implementation Principles

A reliable logarithm implementation should follow several rules:

1. Validate the logarithm base.
2. Validate the logarithm argument.
3. Use an appropriate logarithm base for the problem.
4. Use specialized numerical functions where available.
5. Preserve numerical stability for extreme values.
6. Use log-domain arithmetic for products of very small or very large positive quantities when appropriate.
7. Check original domains after solving logarithmic equations.
8. Avoid treating floating-point calculations as exact symbolic mathematics.
9. Use stable formulations such as log-sum-exp for exponential sums.
10. Use exact integer or bitwise operations when exact discrete properties are required.

---

## 61. Mathematical Relationships Used in the Script

The principal formulas implemented are:

    b^x = y
    <=> log_b(y) = x

    log_b(1) = 0

    log_b(b) = 1

    log_b(xy) = log_b(x) + log_b(y)

    log_b(x/y) = log_b(x) - log_b(y)

    log_b(x^k) = k log_b(x)

    log_b(x) = ln(x) / ln(b)

    d/dx ln(x) = 1/x

    d/dx log_b(x) = 1 / (x ln(b))

    pH = -log_10([H+])

    dB_power = 10 log_10(P2/P1)

    dB_amplitude = 20 log_10(A2/A1)

    H(X) = -sum(p_i log_b(p_i))

    digits_10(n) = floor(log_10(n)) + 1

    digits_2(n) = floor(log_2(n)) + 1

    t = ln(target/initial) / ln(growth_factor)

    log(sum(exp(x_i)))
    =
    m + log(sum(exp(x_i-m)))

    log_softmax(x_i)
    =
    x_i - log(sum(exp(x_j)))

---

## 62. Running the Script

The script requires Python and uses only the standard library.

Run it with:

    python logarithms.py

The program prints mathematical demonstrations, numerical calculations, validation examples, computational applications, numerical-stability examples, and tests sequentially.

The script is intentionally executable as a single standalone file. No external dataset, package, configuration file, or input file is required.

---

## 63. Scope of the Computational Treatment

The script treats logarithms as both a mathematical object and a computational tool.

The elementary sections establish the definition, notation, restrictions, identities, equations, inequalities, and graph behavior.

The intermediate sections connect logarithms with calculus, growth, scientific scales, information theory, and algorithmic complexity.

The advanced sections focus on numerical computation, floating-point limitations, log-domain arithmetic, log-sum-exp, log-softmax, root finding, transformed regression, complex logarithms, and stable numerical implementation.

This progression reflects the central role of logarithms in moving between exponential and linear representations while also demonstrating why logarithmic formulations can be essential for reliable numerical computation.
