# Joint Distributions: Probability and Statistical Analysis

## 1. Technical Scope

Joint distributions describe the probability behavior of two random variables considered together.

This project implements discrete and continuous joint distributions using Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover:

- Joint probability mass functions (PMF).
- Joint probability density functions (PDF).
- Marginal probability distributions.
- Conditional probability distributions.
- Expected values.
- Variance.
- Expected products.
- Covariance.
- Correlation.
- Statistical independence.
- Bivariate normal distributions.
- Probability validation and numerical edge cases.

The central distinction is between the probability of a combination of outcomes and the probability distribution of an individual variable.

## 2. Mathematical Foundations

### 2.1 Random Variables

Let X and Y represent two random variables.

For an employee performance analysis:

- X: Training level.
- Y: Assessment outcome.

The joint distribution describes the probability associated with each possible pair of values.

For example:

| X | Y | Joint probability |
|---:|---:|---:|
| 0 | 0 | 0.10 |
| 0 | 1 | 0.15 |
| 1 | 0 | 0.20 |
| 1 | 1 | 0.30 |
| 2 | 0 | 0.05 |
| 2 | 1 | 0.20 |
| | **Total** | **1.00** |

The joint probability is written as:

\[
P(X=x,Y=y)
\]

A valid joint probability distribution must satisfy:

\[
P(X=x,Y=y)\geq 0
\]

and

\[
\sum_x\sum_y P(X=x,Y=y)=1
\]

These conditions apply to discrete joint distributions.

### 2.2 Joint Probability Mass Function

A joint PMF assigns a probability to every possible combination of discrete outcomes.

\[
p_{X,Y}(x,y)=P(X=x,Y=y)
\]

The probability of an event involving multiple combinations is obtained by summing the corresponding joint probabilities.

For example:

\[
P(X=1,Y=1)=0.30
\]

The probability that X equals 1, regardless of Y, requires summing all combinations with X equal to 1.

### 2.3 Joint Probability Density Function

For continuous random variables, probabilities are described through a joint PDF.

\[
f_{X,Y}(x,y)
\]

A valid joint density must satisfy:

\[
f_{X,Y}(x,y)\geq 0
\]

and

\[
\int_{-\infty}^{\infty}
\int_{-\infty}^{\infty}
f_{X,Y}(x,y)\,dx\,dy=1
\]

For a region A:

\[
P((X,Y)\in A)
=
\iint_A f_{X,Y}(x,y)\,dx\,dy
\]

A PDF value is a density, not the probability of an individual continuous outcome.

For continuous random variables:

\[
P(X=x,Y=y)=0
\]

at any individual point.

## 3. Marginal Distributions

A marginal distribution describes one variable without retaining the other variable's specific value.

### 3.1 Discrete Marginal PMF

The marginal distribution of X is obtained by summing across all possible values of Y.

\[
P(X=x)=\sum_y P(X=x,Y=y)
\]

Similarly:

\[
P(Y=y)=\sum_x P(X=x,Y=y)
\]

Using the example joint PMF:

| X | P(X) |
|---:|---:|
| 0 | 0.25 |
| 1 | 0.50 |
| 2 | 0.25 |

The marginal distribution of Y is:

| Y | P(Y) |
|---:|---:|
| 0 | 0.35 |
| 1 | 0.65 |

Both marginal distributions must independently sum to one.

### 3.2 Continuous Marginal PDF

The continuous marginal densities are calculated by integration.

\[
f_X(x)=\int_{-\infty}^{\infty}f_{X,Y}(x,y)\,dy
\]

\[
f_Y(y)=\int_{-\infty}^{\infty}f_{X,Y}(x,y)\,dx
\]

This operation removes the other variable from the joint density.

## 4. Conditional Distributions

Conditional distributions describe the probability behavior of one variable when another variable has a specified value.

For discrete random variables:

\[
P(Y=y\mid X=x)
=
\frac{P(X=x,Y=y)}{P(X=x)}
\]

The denominator must be positive.

Similarly:

\[
P(X=x\mid Y=y)
=
\frac{P(X=x,Y=y)}{P(Y=y)}
\]

For continuous variables, conditional density is:

\[
f_{Y|X}(y|x)
=
\frac{f_{X,Y}(x,y)}{f_X(x)}
\]

provided that the marginal density in the denominator is positive.

The implementations provide conditional distributions for discrete PMFs and reject undefined conditioning events.

## 5. Expected Values and Variance

### 5.1 Expected Value

The expected value is the probability-weighted average of a random variable.

For a discrete variable:

\[
E[X]=\sum_x xP(X=x)
\]

For the joint distribution:

\[
E[Y]=\sum_y yP(Y=y)
\]

The joint expectation of the product is:

\[
E[XY]=\sum_x\sum_y xyP(X=x,Y=y)
\]

### 5.2 Variance

Variance measures dispersion around the expected value.

\[
Var(X)=E[X^2]-(E[X])^2
\]

Similarly:

\[
Var(Y)=E[Y^2]-(E[Y])^2
\]

An equivalent expression is:

\[
Var(X)=E[(X-E[X])^2]
\]

Variance is always nonnegative.

## 6. Covariance

Covariance measures the direction of linear variation between two random variables.

\[
Cov(X,Y)=E[(X-E[X])(Y-E[Y])]
\]

An equivalent computational formula is:

\[
Cov(X,Y)=E[XY]-E[X]E[Y]
\]

Interpretation:

| Covariance | Interpretation |
|---|---|
| Positive | Variables tend to increase together. |
| Negative | One variable tends to increase as the other decreases. |
| Zero | No linear covariance is present. |

Zero covariance does not generally establish independence.

The implementations calculate covariance directly from the joint distribution rather than relying on independently supplied sample statistics.

## 7. Correlation

Correlation is the standardized form of covariance.

\[
\rho_{X,Y}
=
\frac{Cov(X,Y)}
{\sqrt{Var(X)Var(Y)}}
\]

Its value must lie within:

\[
-1\leq \rho_{X,Y}\leq 1
\]

Interpretation:

| Correlation | Meaning |
|---:|---|
| +1 | Perfect positive linear relationship |
| Between 0 and +1 | Positive linear relationship |
| 0 | No linear correlation |
| Between -1 and 0 | Negative linear relationship |
| -1 | Perfect negative linear relationship |

Correlation is undefined if either variable has zero variance.

Correlation measures linear association, not every possible type of dependence.

## 8. Statistical Independence

Two random variables are independent when their joint distribution equals the product of their marginal distributions.

For discrete variables:

\[
P(X=x,Y=y)=P(X=x)P(Y=y)
\]

For continuous variables:

\[
f_{X,Y}(x,y)=f_X(x)f_Y(y)
\]

Independence implies zero covariance when the relevant moments exist.

The reverse implication is not generally true.

A useful distinction is:

- Independence describes the complete probabilistic relationship.
- Covariance describes linear joint variation.
- Correlation standardizes that linear variation.

The code implementations test independence by comparing joint probabilities against products of marginal probabilities.

## 9. Bivariate Normal Distribution

The continuous example uses a bivariate normal distribution.

It is parameterized by:

- Mean of X: \(\mu_X\).
- Mean of Y: \(\mu_Y\).
- Standard deviation of X: \(\sigma_X\).
- Standard deviation of Y: \(\sigma_Y\).
- Correlation: \(\rho\).

Its joint PDF is:

\[
\begin{aligned}
f(x,y)
=&\frac{1}{2\pi\sigma_X\sigma_Y\sqrt{1-\rho^2}}\\
&\times\exp\left(
-\frac{1}{2(1-\rho^2)}
\left[
z_X^2-2\rho z_Xz_Y+z_Y^2
\right]
\right)
\end{aligned}
\]

where:

\[
z_X=\frac{x-\mu_X}{\sigma_X}
\]

\[
z_Y=\frac{y-\mu_Y}{\sigma_Y}
\]

The covariance is:

\[
Cov(X,Y)=\rho\sigma_X\sigma_Y
\]

The example uses:

| Parameter | Value |
|---|---:|
| Mean X | 70 |
| Mean Y | 75 |
| Standard deviation X | 10 |
| Standard deviation Y | 12 |
| Correlation | 0.65 |
| Covariance | 78 |

The correlation must satisfy:

\[
-1<\rho<1
\]

The implementation uses this restriction to ensure a nondegenerate bivariate normal density.

## 10. Implementation Architecture

### Python

The Python implementation uses:

- `dataclasses` for immutable outcome records.
- Dictionaries for joint PMFs.
- `defaultdict` for marginal aggregation.
- Classes for distribution behavior.
- Exceptions for invalid probability models.
- Assertions for numerical validation.

The `DiscreteJointDistribution` class manages the complete discrete probability model.

The `BivariateNormal` class separately implements continuous density calculations.

This separation prevents PMF and PDF calculations from being treated as interchangeable.

### JavaScript

The JavaScript implementation uses:

- `Map` for joint probability storage.
- `Set` for event listeners.
- Classes for distribution and density models.
- Immutable parameter objects.
- Promises and asynchronous execution.
- Node.js assertions.
- Event-driven completion notifications.

The event emitter separates statistical processing from notification behavior.

The distribution model validates its inputs before storing probability values.

### C++17

The C++ implementation uses:

- `struct` for outcome records.
- `std::map` for joint probability storage.
- STL containers for marginal distributions.
- Exception-based validation.
- Modular statistical methods.
- Standard numerical functions.

The ordered map provides deterministic outcome traversal and logarithmic lookup.

The implementation uses direct mathematical calculations rather than external numerical libraries.

### Java 17

The Java implementation uses:

- Records for immutable domain objects.
- Interfaces for analytical behavior.
- `Map` for joint probability storage.
- Streams for statistical aggregation.
- Collections for immutable distribution results.
- Custom runtime exceptions.
- A separate continuous distribution class.

`DistributionMetrics` groups the computed statistical measures into one immutable result.

The analytical interface separates the distribution contract from its implementation.

### PostgreSQL

The SQL implementation uses the `joint_statistics` schema.

Its main relational objects are:

| Database object | Responsibility |
|---|---|
| `variables` | Variable definitions |
| `joint_distributions` | Distribution metadata |
| `joint_distribution_variables` | Variable relationships |
| `joint_probability_atoms` | Discrete joint probabilities |
| `bivariate_normal_parameters` | Continuous distribution parameters |
| `marginal_x` | Marginal distribution of X |
| `marginal_y` | Marginal distribution of Y |
| `joint_distribution_metrics` | Statistical aggregation |

The database provides reusable functions for PMF validation, conditional probability, independence evaluation, and continuous density calculations.

## 11. PostgreSQL Processing Workflow

The database workflow follows this structure:

Distribution Definition
        |
        v
Variable Registration
        |
        v
Joint Probability Records
        |
        v
Probability Validation
        |
        v
Marginal Aggregation
        |
        v
Conditional Probability
        |
        v
Expected Values and Variances
        |
        v
Covariance and Correlation
        |
        v
Independence Evaluation
        |
        v
Statistical Reporting

## SQL Implementation Details

The SQL script includes:

- Primary and foreign keys.
- Unique outcome constraints.
- Nonnegative probability constraints.
- Correlation range constraints.
- Indexes for distribution and outcome retrieval.
- Views for reusable statistical calculations.
- Functions for conditional probability and validation.
- A transaction demonstrating a valid independent distribution.
- A controlled invalid-probability example.

The PMF validation function checks the sum of probabilities across all records belonging to a distribution.

A row-level check constraint cannot independently guarantee that the sum of multiple rows equals one. Therefore, total-probability validation is implemented as a separate database operation.

For concurrent production ingestion, probability-set publication should be protected through controlled transactions, appropriate locking, and an immutable finalized-distribution state. The supplied validation function is not itself a concurrency-control mechanism.

## 12. Validation and Edge Cases

The implementations address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty joint distribution | Reject |
| Negative probability | Reject |
| Probability greater than one | Reject |
| Probability total differs from one | Reject |
| Duplicate outcome | Reject |
| Undefined conditional probability | Reject |
| Zero variance | Reject correlation calculation |
| Invalid standard deviation | Reject |
| Correlation outside valid range | Reject |
| Non-finite input | Reject |
| Missing joint outcome | Return zero probability |

Floating-point calculations can produce small numerical discrepancies.

A tolerance is therefore used when validating probability totals and independence.

The tolerance should be selected according to the numerical precision and scale of the application. It should not be used to conceal materially invalid probability models.

## 13. Computational Complexity

Let:

- \(n\) represent the number of distinct joint outcomes.
- \(a\) represent the number of distinct X values.
- \(b\) represent the number of distinct Y values.

| Operation | Python dictionary | JavaScript Map | C++ ordered map | Java HashMap |
|---|---|---|---|---|
| Joint lookup | Average O(1) | Average O(1) | O(log n) | Average O(1) |
| Marginal X | O(n) | O(n) | O(n log a) | Expected O(n) |
| Marginal Y | O(n) | O(n) | O(n log b) | Expected O(n) |
| Expectation | O(a) or O(b) | O(a) or O(b) | O(a) or O(b) | O(a) or O(b) |
| Covariance | O(n) | O(n) | O(n) | O(n) |
| Independence | O(ab + n) | O(ab + n) | O(ab log n) | Expected O(ab) |

These figures describe the implemented data structures and their typical behavior.

The SQL implementation relies on database aggregation, indexes, and query planning. Its actual performance depends on table cardinality, indexes, data distribution, and execution plans.

For large joint distributions, sparse representations are generally preferable when most possible combinations have zero probability.

## 14. Security and Production Considerations

Probability data can be sensitive when it represents employee, financial, operational, or medical outcomes.

Production deployments should consider:

- Restricting database access through appropriate roles.
- Validating external inputs before insertion.
- Using parameterized SQL queries.
- Preventing unauthorized modification of finalized distributions.
- Recording distribution versions and publication timestamps.
- Separating model parameters from observed outcomes.
- Retaining sufficient numerical precision.
- Auditing changes to probability records.
- Avoiding disclosure of sensitive individual-level observations.

The supplied examples use synthetic data and do not require external services.

For high-volume numerical workloads, optimized matrix operations, specialized numerical libraries, and database-side aggregation may be appropriate.

## 15. Practical Interpretation

Joint distributions provide a foundation for understanding relationships between multiple random variables.

Marginal distributions describe individual variables, conditional distributions describe probabilities under known conditions, covariance quantifies joint linear variation, and correlation standardizes that relationship.

A joint distribution contains more information about the relationship between variables than their separate marginal distributions.

This distinction is important in statistical modeling, risk analysis, forecasting, scientific research, and operational decision-making.
