# Probability Inequalities

## Markov, Chebyshev, Jensen, and Chernoff Bounds

## 1. Mathematical Foundation

Probability inequalities provide upper or lower limits on probabilities when the complete probability distribution is unavailable or when calculating an exact probability is computationally expensive.

They are particularly useful in:

- Statistical inference.
- Reliability engineering.
- Risk analysis.
- Machine learning.
- Randomized algorithms.
- Performance guarantees.
- Concentration of measure.
- Large-scale probabilistic systems.

The implementations use finite discrete probability distributions to make mathematical assumptions, calculations, and exact probabilities directly verifiable.

A discrete random variable \(X\) is represented by outcomes \(x_i\) and probabilities \(p_i\), satisfying:

\[
p_i \geq 0
\]

\[
\sum_{i=1}^{n}p_i=1
\]

The expectation is:

\[
E[X]=\sum_{i=1}^{n}x_ip_i
\]

The variance is:

\[
\operatorname{Var}(X)
=
E[(X-E[X])^2]
\]

Equivalently:

\[
\operatorname{Var}(X)=E[X^2]-E[X]^2
\]

The four inequalities use different mathematical properties of random variables. They are not interchangeable.

## 2. Markov Inequality

Markov's inequality provides an upper bound on the probability that a nonnegative random variable reaches or exceeds a positive threshold.

For \(X\geq 0\) and \(a>0\):

\[
\boxed{
P(X\geq a)\leq\frac{E[X]}{a}
}
\]

### Mathematical mechanism

A nonnegative random variable cannot have a large probability of exceeding a threshold without having a sufficiently large expectation.

The inequality follows from:

\[
X\geq a\mathbf{1}_{X\geq a}
\]

Taking expectations:

\[
E[X]\geq aP(X\geq a)
\]

Rearranging produces the Markov bound.

### Example

Suppose an operational incident count has an expected value of 2 incidents.

For a threshold of 4:

\[
P(X\geq4)\leq\frac{2}{4}
\]

\[
P(X\geq4)\leq0.5
\]

The bound guarantees that the probability cannot exceed 50%.

### Assumptions and limitations

- The random variable must be nonnegative.
- Its expectation must exist and be finite.
- The threshold must be positive.
- The inequality does not require independence.
- The bound may be loose because it uses only the first moment.

The Python, JavaScript, C++17, Java 17, and PostgreSQL implementations reject negative-valued distributions when applying Markov's inequality.

## 3. Chebyshev Inequality

Chebyshev's inequality bounds the probability that a random variable deviates from its expected value by at least a specified amount.

For a random variable with finite variance and \(t>0\):

\[
\boxed{
P(|X-E[X]|\geq t)
\leq
\frac{\operatorname{Var}(X)}{t^2}
}
\]

### Mathematical mechanism

Chebyshev's inequality applies Markov's inequality to the nonnegative random variable:

\[
Y=(X-E[X])^2
\]

The event:

\[
|X-E[X]|\geq t
\]

is equivalent to:

\[
(X-E[X])^2\geq t^2
\]

Therefore:

\[
P(|X-E[X]|\geq t)
\leq
\frac{E[(X-E[X])^2]}{t^2}
\]

The numerator is the variance.

### Standard deviation formulation

If:

\[
t=k\sigma
\]

where \(\sigma\) is the standard deviation, then:

\[
\boxed{
P(|X-\mu|\geq k\sigma)\leq\frac{1}{k^2}
}
\]

For example, when \(k=2\):

\[
P(|X-\mu|\geq2\sigma)\leq0.25
\]

This result does not require a normal distribution.

### Important distinctions

- Markov bounds an upper-tail event for a nonnegative variable.
- Chebyshev bounds a two-sided deviation from the mean.
- Chebyshev requires finite variance.
- Chebyshev does not require symmetry, independence, or a particular distribution family.

The implementations calculate both the theoretical bound and the exact deviation probability for finite distributions.

## 4. Jensen Inequality

Jensen's inequality describes the relationship between a convex function evaluated at an expected value and the expectation of that function.

For a convex function \(f\):

\[
\boxed{
f(E[X])\leq E[f(X)]
}
\]

### Mathematical mechanism

Convexity means that the function lies below its secant lines.

For two points \(x_1,x_2\) and \(0\leq\lambda\leq1\):

\[
f(\lambda x_1+(1-\lambda)x_2)
\leq
\lambda f(x_1)+(1-\lambda)f(x_2)
\]

The finite-distribution form follows by applying this property to a weighted combination of outcomes.

### Example: Squared function

Consider:

\[
f(x)=x^2
\]

Since:

\[
f''(x)=2>0
\]

the function is convex.

Jensen's inequality becomes:

\[
(E[X])^2\leq E[X^2]
\]

Using the variance identity:

\[
E[X^2]-(E[X])^2=\operatorname{Var}(X)
\]

Therefore:

\[
\operatorname{Var}(X)\geq0
\]

This demonstrates the connection between Jensen's inequality and nonnegative variance.

### Additional convex functions

The implementations support:

| Function | Expression | Convexity |
|---|---|---|
| Square | \(x^2\) | Convex on the real line |
| Exponential | \(e^x\) | Convex on the real line |
| Absolute value | \(|x|\) | Convex on the real line |

### Practical applications

Jensen's inequality appears in:

- Expected loss calculations.
- Optimization.
- Statistical estimation.
- Information theory.
- Risk aggregation.
- Machine learning objective functions.

A function's convexity and domain must be established independently. Evaluating the inequality numerically does not prove that an arbitrary function is convex.

## 5. Chernoff Inequality

Chernoff bounds provide exponential upper bounds on tail probabilities using moment-generating functions.

The moment-generating function of a random variable \(X\) is:

\[
M_X(\lambda)=E[e^{\lambda X}]
\]

When it exists, the logarithm of the MGF is:

\[
K_X(\lambda)=\log M_X(\lambda)
\]

For any \(\lambda\geq0\), Markov's inequality gives:

\[
P(X\geq a)
=
P(e^{\lambda X}\geq e^{\lambda a})
\]

Consequently:

\[
P(X\geq a)
\leq
e^{-\lambda a}M_X(\lambda)
\]

Taking the infimum over nonnegative parameters:

\[
\boxed{
P(X\geq a)
\leq
\inf_{\lambda\geq0}
e^{-\lambda a}M_X(\lambda)
}
\]

The equivalent logarithmic formulation is:

\[
\boxed{
P(X\geq a)
\leq
\inf_{\lambda\geq0}
\exp(K_X(\lambda)-\lambda a)
}
\]

### Numerical optimization

The implementations search a bounded interval:

\[
0\leq\lambda\leq\lambda_{\max}
\]

They evaluate the logarithmic objective at equally spaced parameter values and select the smallest resulting bound.

This is a numerical approximation to the infimum, not a proof that the globally optimal parameter has been identified.

The Chernoff result remains a valid upper bound for every tested nonnegative parameter. The minimum over the tested parameters is also a valid bound.

A bounded parameter search may be less tight than an unrestricted optimization.

### Numerical stability

Direct evaluation of exponential functions can overflow.

For example:

\[
e^{1000}
\]

cannot be represented using ordinary double-precision floating-point arithmetic.

The implementations use log-sum-exp:

\[
\log\left(\sum_i e^{z_i}\right)
=
m+\log\left(\sum_i e^{z_i-m}\right)
\]

where:

\[
m=\max_i z_i
\]

This reduces numerical overflow and improves the stability of MGF calculations.

### Binomial example

Consider independent Bernoulli random variables:

\[
X_i\sim\operatorname{Bernoulli}(p)
\]

Their sum is:

\[
S_n=\sum_{i=1}^{n}X_i
\]

For independent, identically distributed trials:

\[
S_n\sim\operatorname{Binomial}(n,p)
\]

Its MGF is:

\[
M_{S_n}(\lambda)
=
(1-p+pe^\lambda)^n
\]

Therefore:

\[
P(S_n\geq a)
\leq
\inf_{\lambda\geq0}
e^{-\lambda a}
(1-p+pe^\lambda)^n
\]

The implementations calculate the exact finite binomial distribution and compare the numerical Chernoff bound against the exact upper-tail probability.

## 6. Relationship Between the Four Inequalities

| Property | Markov | Chebyshev | Jensen | Chernoff |
|---|---|---|---|---|
| Primary purpose | Upper-tail probability | Deviation probability | Convex expectation comparison | Exponential tail probability |
| Main mathematical quantity | Mean | Variance | Convex function | MGF |
| Nonnegative variable required | Yes | No | No | No for the general upper-tail MGF form |
| Requires finite variance | No | Yes | No, provided required expectations exist | Not necessarily |
| Independence required | No | No | No | No for the general MGF inequality |
| Typical output | Probability bound | Probability bound | Expectation inequality | Probability bound |

Their relationship can be understood through the information they use.

- Markov uses the first moment.
- Chebyshev uses the second central moment.
- Jensen compares a transformed expectation with a transformation of the expectation.
- Chernoff uses exponential moments and parameter optimization.

Chebyshev can be derived using Markov's inequality. Chernoff can also be derived using Markov's inequality, but on an exponential transformation of the random variable.

Jensen is conceptually different because it establishes an expectation inequality rather than directly bounding a tail probability.

## 7. Python Implementation

The Python script provides a reusable probability analysis model.

### Components

| Component | Responsibility |
|---|---|
| `DiscreteDistribution` | Stores outcomes and probabilities |
| `ProbabilityError` | Represents validation failures |
| `BoundType` | Identifies inequality categories |
| `markov_bound()` | Calculates Markov's bound |
| `chebyshev_bound()` | Calculates Chebyshev's bound |
| `jensen_inequality()` | Evaluates the convex expectation relationship |
| `log_mgf()` | Calculates the logarithmic MGF |
| `chernoff_bound()` | Searches for a numerical Chernoff bound |
| `bernoulli_sum_distribution()` | Constructs an exact binomial distribution |
| `empirical_probability()` | Calculates observed event frequency |

The distribution is immutable after construction.

This prevents probability values from being changed without revalidation.

The script includes deterministic sampling, assertions, input validation, exception handling, and exact probability calculations.

### Execution

Requirements:

- Python 3.10 or later.
- Python standard library.

Run the file using:

`python probability_inequalities.py`

The program runs its validation tests before displaying the probability analysis.

## 8. JavaScript Implementation

The JavaScript implementation uses an event-driven architecture.

### Main components

| Component | Responsibility |
|---|---|
| `Distribution` | Immutable probability model |
| `ProbabilityEngine` | Experiment registration and evaluation |
| `EventEmitter` | Evaluation lifecycle notifications |
| `markov()` | Markov bound |
| `chebyshev()` | Chebyshev bound |
| `jensen()` | Convex function evaluation |
| `logMGF()` | Stable logarithmic MGF |
| `chernoff()` | Numerical exponential bound |
| `binomialDistribution()` | Binomial probability generation |

The engine emits events when an experiment is registered, evaluated, or fails.

Asynchronous evaluation uses a Promise and yields to the Node.js event loop.

A running-state guard prevents overlapping batch evaluations through the same engine instance.

The deterministic sampling mechanism makes experiments reproducible.

### Execution

Requirements:

- Node.js 18 or later.
- No npm dependencies.

Run:

`node probability_inequalities.js`

The event-driven structure separates probability calculations from experiment orchestration.

## 9. C++17 Implementation

The C++ implementation emphasizes domain modeling, type safety, and explicit numerical operations.

### Main components

| Component | Responsibility |
|---|---|
| `Outcome` | Represents an outcome and probability |
| `Distribution` | Maintains validated outcomes and moments |
| `Inequality` | Identifies the mathematical bound |
| `BoundResult` | Stores calculation results |
| `ProbabilityEngine` | Coordinates inequality evaluation |
| `createBinomial()` | Generates binomial distributions |

The `Distribution` class calculates the expectation and variance once during construction.

This avoids repeatedly traversing the distribution when these values are requested.

The engine supports:

- Markov validation.
- Chebyshev deviation analysis.
- Jensen expectation comparison.
- Chernoff parameter search.
- Exact upper-tail probability calculation.
- Named experiment registration.
- Exception-based failure handling.

The standard library `map` provides named distribution lookup, while STL algorithms support validation and aggregation.

### Execution

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic probability_inequalities.cpp -o probability_inequalities`

Run:

`./probability_inequalities`

On Windows:

`probability_inequalities.exe`

## 10. Java 17 Implementation

The Java implementation represents probability analysis as an enterprise-oriented service.

### Domain model

| Type | Responsibility |
|---|---|
| `Outcome` record | Immutable probability outcome |
| `BoundResult` record | Immutable inequality result |
| `ExperimentReport` record | Consolidated experiment report |
| `ExperimentStatus` | Tracks experiment lifecycle |
| `InequalityService` | Executes mathematical calculations |
| `ExperimentRegistry` | Manages registered experiments |
| `ProbabilityReportingService` | Coordinates evaluations |
| `ConvexFunction` | Defines the convex function contract |

### Experiment lifecycle

The service uses the following state transitions:

`REGISTERED → VALIDATED → EVALUATED`

A failed calculation produces:

`VALIDATED → FAILED`

An experiment is validated before its results are stored in the report.

The reporting service distinguishes an unavailable Markov result from a valid numerical result. This matters when the distribution includes negative outcomes.

The Java records and defensive collection copies prevent accidental changes to evaluated data.

### Policy and validation considerations

The mathematical service enforces:

- Valid probability totals.
- Finite outcomes.
- Positive thresholds.
- Positive deviations.
- Nonnegative values for Markov.
- Valid MGF parameters.
- Convexity contracts for Jensen.
- Consistent result ranges.

The implementation also includes a binomial distribution generator and assertion-based validation.

### Execution

Requirements:

- Java 17.

Compile:

`javac ProbabilityInequalities.java`

Run:

`java -ea ProbabilityInequalities`

The `-ea` option enables Java assertions.

## 11. PostgreSQL Implementation

The SQL implementation provides a relational probability analysis system.

It stores probability distributions, outcomes, experiments, mathematical functions, and calculated bounds.

### Relational architecture

The principal relationship is:

`Distributions → Outcomes → Experiments → Inequality Evaluations`

The Jensen-specific relationship is:

`Experiments → Jensen Evaluations → Convex Functions`

### Database objects

| Database object | Purpose |
|---|---|
| `distributions` | Stores probability distribution metadata |
| `outcomes` | Stores values and their probabilities |
| `experiments` | Stores evaluation thresholds and states |
| `inequality_evaluations` | Stores calculated probability bounds |
| `convex_functions` | Registers supported convex functions |
| `jensen_evaluations` | Stores Jensen comparisons |

### Validation mechanisms

The database uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Probability check constraints.
- Finite-number checks.
- Indexes.
- Validation functions.
- Triggers.
- Stored procedures.

The distribution validation function verifies that the probabilities sum to one within a numerical tolerance.

The outcome trigger invalidates the normalization state whenever the underlying distribution changes.

This prevents a previously validated distribution from remaining marked as normalized after an outcome modification.

### Stored calculations

The SQL functions implement:

- `distribution_mean()`
- `distribution_variance()`
- `distribution_expectation()`
- `exact_upper_probability()`
- `exact_deviation_probability()`
- `calculate_markov()`
- `calculate_chebyshev()`
- `calculate_jensen()`
- `calculate_chernoff()`

The `evaluate_experiment()` procedure coordinates validation and calculation within a database transaction.

If a calculation fails, the experiment is marked as failed and the exception is propagated.

The evaluation upsert mechanism allows an experiment to be recalculated without creating duplicate inequality results.

### Reporting

The script creates two views:

- `distribution_statistics`
- `evaluation_report`

It also includes CTE-based evaluation eligibility reporting and grouped statistics.

The sample dataset contains:

1. A nonnegative operational-risk distribution.
2. A binomial failure distribution.
3. A symmetric distribution containing negative and positive outcomes.

The third distribution demonstrates why Markov's inequality cannot be applied indiscriminately.

### Execution

Requirements:

- PostgreSQL 14 or later.
- Permission to create a schema, tables, functions, triggers, and procedures.

Execute the complete SQL file in a PostgreSQL database.

The script uses a transaction to keep the database setup and sample evaluation workflow consistent.

## 12. Probability Distribution and Bound Validation

An inequality bound must be compared against the actual event probability whenever an exact probability is available.

For an upper-tail bound:

\[
P(X\geq a)\leq B
\]

the validation condition is:

\[
P_{\text{exact}}(X\geq a)\leq B
\]

For Chebyshev's inequality:

\[
P(|X-\mu|\geq t)\leq B
\]

the comparison must use the two-sided deviation probability, not the upper-tail probability.

For Jensen's inequality:

\[
f(E[X])\leq E[f(X)]
\]

the validation compares the two expectation values.

These are different event and expectation calculations. Comparing the wrong quantities can produce misleading validation results.

## 13. Edge Cases and Failure Conditions

| Condition | Expected behavior |
|---|---|
| Empty distribution | Reject construction |
| Probabilities do not sum to one | Reject construction |
| Negative probability | Reject construction |
| Non-finite outcome | Reject construction |
| Markov threshold equals zero | Reject calculation |
| Negative-valued variable in Markov | Reject calculation |
| Chebyshev deviation equals zero | Reject calculation |
| Invalid MGF parameter | Reject calculation |
| Overflow-prone exponential calculation | Use logarithmic calculations |
| Invalid convexity assumption | Jensen result cannot be treated as mathematically established |
| Numerical optimization reaches search limit | Report the best tested parameter |
| Exact probability exceeds a claimed upper bound | Flag the result for investigation |

A calculated bound should never be interpreted independently of its assumptions.

## 14. Computational Complexity

Let:

- \(n\) represent the number of discrete outcomes.
- \(s\) represent the number of Chernoff parameter evaluations.
- \(m\) represent the number of Monte Carlo observations.

| Operation | Time complexity | Space complexity |
|---|---:|---:|
| Distribution validation | \(O(n)\) | \(O(1)\) auxiliary |
| Expectation | \(O(n)\) | \(O(1)\) |
| Variance | \(O(n)\) | \(O(1)\) |
| Markov | \(O(n)\) | \(O(1)\) auxiliary |
| Chebyshev | \(O(n)\) | \(O(1)\) auxiliary |
| Jensen | \(O(n)\) | \(O(1)\) auxiliary |
| One MGF evaluation | \(O(n)\) | \(O(n)\) in the implementations using term arrays |
| Chernoff grid search | \(O(ns)\) | \(O(n)\) |
| Monte Carlo sampling | \(O(mn)\) in the supplied linear-search implementations | \(O(m)\) |

The Chernoff implementations use a fixed search interval and a configurable number of steps.

A more sophisticated implementation can use derivative-based optimization or a one-dimensional convex optimization algorithm where the necessary regularity conditions hold.

The SQL implementation evaluates MGF terms through relational aggregation, avoiding the need to transfer individual outcomes to an application process.

## 15. Practical Interpretation

Probability bounds are most useful when their assumptions match the actual problem.

### Markov

Appropriate when:

- A variable is nonnegative.
- Its expectation is known.
- A basic upper-tail guarantee is sufficient.

### Chebyshev

Appropriate when:

- The mean and variance are known.
- A two-sided deviation guarantee is required.
- The distribution family is unknown.

### Jensen

Appropriate when:

- A transformation is convex.
- The expectation of a transformed variable is important.
- An optimization or risk aggregation problem involves nonlinear functions.

### Chernoff

Appropriate when:

- An MGF exists.
- Exponential tail behavior is useful.
- A tighter probability guarantee is needed.
- Numerical parameter optimization is computationally feasible.

The distinction between a theoretical guarantee and an empirical estimate remains essential. An observed frequency from simulated data does not replace a mathematically established upper bound.

## 16. Limitations of the Implementations

The implementations intentionally use finite discrete distributions.

This makes exact probabilities and expectations available for verification, but it does not directly implement continuous probability density functions.

Other limitations include:

- Floating-point arithmetic introduces rounding errors.
- Chernoff optimization uses a bounded parameter grid.
- Jensen validation relies on a caller-supplied convexity assumption.
- The binomial generators impose practical limits on the number of trials.
- Monte Carlo estimates are subject to sampling variation.
- The PostgreSQL implementation stores calculated results rather than maintaining a complete symbolic probability model.
- Independence is not inferred merely from a list of marginal distributions.

For independent random variables, the product of individual MGFs can be used to derive the MGF of their sum when the required expectations exist. This relationship must not be applied to dependent variables without an appropriate joint-distribution model.

The central requirement in every implementation is to preserve the mathematical assumptions associated with each inequality.
