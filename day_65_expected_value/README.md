# Expected Value and Moments

## 1. Mathematical Foundation

Expected value is the probability-weighted average of a random variable's possible outcomes. It represents the long-run average value associated with a probability model.

For a discrete random variable \(X\) with outcomes \(x_1, x_2, \ldots, x_n\), the expectation is:

\[
E[X] = \sum_{i=1}^{n}x_iP(X=x_i)
\]

The probability distribution must satisfy:

\[
P(X=x_i)\geq 0
\]

\[
\sum_{i=1}^{n}P(X=x_i)=1
\]

Expected value does not necessarily represent the most likely outcome or an outcome that can actually occur.

### Example: Fair Six-Sided Die

Each face has probability \(1/6\).

\[
E[X]=\frac{1+2+3+4+5+6}{6}
\]

\[
E[X]=3.5
\]

The value 3.5 is not a possible result of one throw. It is the theoretical average over repeated independent throws.

## 2. Expectation of a Function

For a function \(g(X)\), the expectation is:

\[
E[g(X)] = \sum_i g(x_i)P(X=x_i)
\]

This property allows the calculation of expected squared values, expected utility, financial losses, and other transformations.

The first raw moment is the expected value:

\[
\mu'_1=E[X]
\]

The second raw moment is:

\[
\mu'_2=E[X^2]
\]

The linearity of expectation is:

\[
E[aX+b]=aE[X]+b
\]

For multiple random variables:

\[
E[X+Y]=E[X]+E[Y]
\]

This relationship holds even when the variables are dependent.

## 3. Variance

Variance measures the dispersion of outcomes around their expected value.

\[
Var(X)=E[(X-\mu)^2]
\]

Where:

\[
\mu=E[X]
\]

An equivalent computational expression is:

\[
Var(X)=E[X^2]-(E[X])^2
\]

Variance is expressed in squared units.

For the fair six-sided die:

\[
E[X]=3.5
\]

\[
E[X^2]=\frac{1^2+2^2+3^2+4^2+5^2+6^2}{6}
\]

\[
E[X^2]=\frac{91}{6}
\]

Therefore:

\[
Var(X)=\frac{91}{6}-3.5^2
\]

\[
Var(X)=\frac{35}{12}
\]

A deterministic random variable has zero variance because every possible observation equals its expected value.

## 4. Standard Deviation

Standard deviation is the positive square root of variance.

\[
\sigma=\sqrt{Var(X)}
\]

For the fair die:

\[
\sigma=\sqrt{\frac{35}{12}}
\]

\[
\sigma\approx1.707825
\]

Standard deviation is expressed in the same units as the original variable. This makes it easier to interpret than variance.

Variance and standard deviation describe dispersion, not the probability of a specific outcome.

## 5. Moments of a Probability Distribution

Moments provide additional information about the shape and characteristics of a probability distribution.

Two important categories are raw moments and central moments.

### 5.1 Raw Moments

The \(r\)-th raw moment is:

\[
\mu'_r=E[X^r]
\]

For a discrete distribution:

\[
\mu'_r=\sum_i x_i^rP(X=x_i)
\]

| Order | Mathematical expression | Interpretation |
|---|---|---|
| First | \(E[X]\) | Expected value |
| Second | \(E[X^2]\) | Second raw moment |
| Third | \(E[X^3]\) | Third raw moment |
| Fourth | \(E[X^4]\) | Fourth raw moment |

The second raw moment is used to calculate variance.

### 5.2 Central Moments

The \(r\)-th central moment is:

\[
\mu_r=E[(X-\mu)^r]
\]

Central moments measure distribution characteristics relative to the mean.

| Order | Expression | Interpretation |
|---|---|---|
| First | \(E[X-\mu]\) | Always zero |
| Second | \(E[(X-\mu)^2]\) | Variance |
| Third | \(E[(X-\mu)^3]\) | Asymmetry information |
| Fourth | \(E[(X-\mu)^4]\) | Tail and concentration information |

The first central moment is always zero:

\[
E[X-\mu]=0
\]

The second central moment equals variance:

\[
\mu_2=Var(X)
\]

## 6. Skewness

Skewness measures the asymmetry of a probability distribution.

\[
\gamma_1=\frac{\mu_3}{\sigma^3}
\]

Interpretation:

- Zero skewness: zero third standardized central moment.
- Positive skewness: greater influence from the upper tail.
- Negative skewness: greater influence from the lower tail.

Zero skewness does not necessarily imply a symmetric distribution.

Skewness is useful in financial return analysis because unusually large losses and gains can create asymmetric distributions.

## 7. Kurtosis

Kurtosis measures the standardized fourth central moment.

\[
\beta_2=\frac{\mu_4}{\sigma^4}
\]

Excess kurtosis is:

\[
\gamma_2=\beta_2-3
\]

The distinction is important:

| Measure | Formula |
|---|---|
| Kurtosis | \(\mu_4/\sigma^4\) |
| Excess kurtosis | \(\mu_4/\sigma^4-3\) |

A normal distribution has kurtosis 3 and excess kurtosis 0.

Higher kurtosis can indicate greater sensitivity to extreme observations, but it does not independently describe the complete tail behavior of a distribution.

## 8. Conditional Expectation

Conditional expectation calculates the expected value after restricting the probability space to an event.

For an event \(A\) with positive probability:

\[
E[X\mid A]=
\frac{E[X\mathbf{1}_A]}{P(A)}
\]

For a discrete distribution:

\[
E[X\mid A]=
\frac{\sum_{x_i\in A}x_iP(X=x_i)}
{\sum_{x_i\in A}P(X=x_i)}
\]

The denominator must be positive.

### Investment Example

Consider the following investment outcomes:

| Return | Probability |
|---:|---:|
| -1000 | 0.10 |
| -200 | 0.20 |
| 300 | 0.40 |
| 1000 | 0.20 |
| 2500 | 0.10 |

Expected return:

\[
E[X]=(-1000)(0.10)+(-200)(0.20)
\]

\[
+(300)(0.40)+(1000)(0.20)+(2500)(0.10)
\]

\[
E[X]=310
\]

The probability of a positive return is:

\[
P(X>0)=0.70
\]

The conditional expected return given a positive outcome is:

\[
E[X\mid X>0]
=
\frac{300(0.40)+1000(0.20)+2500(0.10)}
{0.70}
\]

\[
E[X\mid X>0]\approx742.857143
\]

This separates the unconditional expected return from the expected return under a specific condition.

## 9. Joint Distributions, Covariance, and Correlation

A joint probability distribution describes two random variables simultaneously.

For discrete variables \(X\) and \(Y\):

\[
P(X=x,Y=y)
\]

The joint probabilities must sum to one.

### 9.1 Covariance

Covariance measures how two variables vary together.

\[
Cov(X,Y)=E[(X-E[X])(Y-E[Y])]
\]

An equivalent expression is:

\[
Cov(X,Y)=E[XY]-E[X]E[Y]
\]

Interpretation:

- Positive covariance: variables tend to move together.
- Negative covariance: variables tend to move in opposite directions.
- Zero covariance: no linear covariance relationship.

Zero covariance does not necessarily imply independence.

### 9.2 Correlation

Pearson correlation standardizes covariance.

\[
\rho_{X,Y}=
\frac{Cov(X,Y)}{\sigma_X\sigma_Y}
\]

Its value lies between -1 and +1 when both standard deviations are positive.

Correlation is dimensionless, unlike covariance.

Correlation is undefined when either variable has zero variance.

## 10. Empirical Expectation and Sample Statistics

Theoretical expectation is calculated from a probability model.

Empirical expectation is estimated using observed data.

For observations \(x_1,x_2,\ldots,x_n\):

\[
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
\]

Population-style empirical variance:

\[
\sigma_n^2=
\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2
\]

Sample variance:

\[
s^2=
\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2
\]

The denominator distinction matters:

- Divide by \(n\) when describing the complete observed dataset as a population.
- Divide by \(n-1\) when calculating the conventional unbiased estimator of population variance from a sample of independent observations.

These are different statistical quantities.

## 11. Monte Carlo Estimation

Monte Carlo simulation approximates theoretical expectation by repeated random sampling.

For \(N\) simulated observations:

\[
\hat{E}[X]=\frac{1}{N}\sum_{i=1}^{N}X_i
\]

Under independent, identically distributed sampling with finite variance:

\[
SE(\hat{E}[X])=\frac{\sigma}{\sqrt{N}}
\]

Increasing the number of simulations generally reduces sampling uncertainty.

The Python implementation uses `random.choices()` with probability weights.

The JavaScript implementation uses a seeded linear congruential random generator and cumulative probability intervals.

The C++ implementation uses `std::mt19937` and `std::discrete_distribution`.

The Java implementation uses `java.util.Random` and cumulative probability selection.

These approaches produce reproducible demonstrations when their seeds and execution conditions are fixed. They are not cryptographically secure random generators.

## 12. Portfolio Expected Value and Risk

Expected portfolio return is calculated as:

\[
E[R_p]=\sum_{i=1}^{n}w_iE[R_i]
\]

Where:

- \(w_i\) represents the asset weight.
- \(E[R_i]\) represents the expected asset return.
- The weights sum to one.

For independent asset returns:

\[
Var(R_p)=\sum_{i=1}^{n}w_i^2Var(R_i)
\]

For correlated assets, the full expression is:

\[
Var(R_p)=
\sum_{i=1}^{n}\sum_{j=1}^{n}
w_iw_jCov(R_i,R_j)
\]

The independence assumption in the C++ and Java portfolio demonstrations is explicitly identified. The PostgreSQL portfolio view uses the same assumption.

Ignoring covariance for correlated assets can substantially misrepresent portfolio risk.

## 13. Python Implementation

The Python program uses an object-oriented probability model.

| Component | Responsibility |
|---|---|
| `Outcome` | Immutable outcome and probability record |
| `DiscreteDistribution` | Probability validation and distribution calculations |
| `Statistics` | Structured statistical results |
| `expectation()` | General expectation of a transformed variable |
| `raw_moment()` | Raw moment calculation |
| `central_moment()` | Central moment calculation |
| `joint_covariance()` | Joint covariance calculation |
| `correlation()` | Pearson correlation |
| `empirical_statistics()` | Observed-data statistics |
| `monte_carlo_expectation()` | Simulation-based estimation |

The implementation validates finite values, probability bounds, probability totals, conditional events, and moment orders.

It also distinguishes theoretical and simulated expectations.

The calculations for a finite discrete distribution require \(O(n)\) time for each expectation or moment, where \(n\) is the number of outcomes.

The implementation stores outcomes in an immutable tuple, preventing accidental changes to the probability model after construction.

## 14. JavaScript Implementation

The JavaScript program uses an event-driven financial assessment architecture.

| Component | Responsibility |
|---|---|
| `Distribution` | Probability model and statistical calculations |
| `JointDistribution` | Covariance and correlation |
| `RandomGenerator` | Reproducible pseudo-random numbers |
| `MonteCarloEngine` | Probability-weighted simulation |
| `RiskAssessmentService` | Asynchronous assessment and result management |

`RiskAssessmentService` extends Node.js `EventEmitter`.

An `assessmentCompleted` event communicates that a distribution has been analyzed.

The service maintains reports in a `Map`, allowing retrieval by distribution name.

The implementation uses frozen outcome objects and validates numerical values before processing.

The simulation is intentionally implemented separately from the theoretical distribution calculations. This permits comparisons between analytical and numerical estimates.

JavaScript uses IEEE 754 floating-point numbers. Financial systems requiring exact currency arithmetic should use integer minor units or a suitable decimal arithmetic implementation rather than relying on unrestricted floating-point calculations.

## 15. C++17 Implementation

The C++ implementation emphasizes explicit domain modeling and computational control.

| Component | Responsibility |
|---|---|
| `Outcome` | Outcome and probability structure |
| `Distribution` | Validated discrete distribution |
| `Statistics` | Statistical result structure |
| `JointDistribution` | Joint probability analysis |
| `MonteCarloSimulator` | Random sampling |
| `Portfolio` | Weighted return and risk calculation |

The program uses:

- `std::vector` for outcome storage.
- `std::mt19937` for reproducible pseudo-random generation.
- `std::discrete_distribution` for probability-weighted sampling.
- Exceptions for invalid models and failed calculations.
- `std::pow` and `std::sqrt` for moment and dispersion calculations.

The design separates probability validation from statistical computation.

A distribution is validated once during construction. Subsequent expectation and moment calculations operate directly on its stored outcomes.

This avoids repeatedly validating an unchanged distribution during normal analytical operations.

## 16. Java 17 Implementation

The Java program represents an enterprise-oriented risk analytics service.

| Component | Responsibility |
|---|---|
| `Outcome` | Immutable probability record |
| `Statistics` | Statistical result record |
| `JointOutcome` | Joint distribution record |
| `RiskPolicy` | Configurable acceptance conditions |
| `RiskDecision` | Risk evaluation result |
| `Distribution` | Statistical domain model |
| `JointDistribution` | Joint statistical calculations |
| `RiskPolicyService` | Policy evaluation |
| `MonteCarloService` | Simulation |
| `PortfolioService` | Portfolio analytics |

Java records provide concise immutable domain objects.

Collections are defensively copied to prevent external modifications to stored probability data.

The policy service evaluates two independent conditions:

1. Standard deviation must not exceed the configured maximum.
2. Expected return must meet the configured minimum.

The resulting risk category and acceptance decision are separate outputs.

A distribution can have an acceptable expected return but excessive risk. It can also have relatively low risk but insufficient expected return.

This distinction prevents the expected value from being treated as the sole measure of financial suitability.

## 17. PostgreSQL Implementation

The SQL implementation models probability analytics using relational structures.

### 17.1 Database Relationships

    distributions
        |
        +---- distribution_outcomes
        |
        +---- joint_outcomes
        |
        +---- observations

    risk_policies

    portfolio_assets

The `distributions` table identifies each probability model.

The `distribution_outcomes` table stores possible values and their probabilities.

The `joint_outcomes` table stores pairs of outcomes and joint probabilities.

The `observations` table stores actual measurements for empirical analysis.

Risk policies and portfolio assets are represented independently from the probability models.

### 17.2 Integrity Constraints

The database enforces:

- Primary key uniqueness.
- Foreign key relationships.
- Unique outcomes within each distribution.
- Probability bounds between zero and one.
- Positive probability tolerances.
- Nonnegative portfolio standard deviations.
- Portfolio weight bounds.

A probability constraint on an individual row cannot guarantee that the probabilities across multiple rows sum to one.

The `validate_distribution()` function therefore checks the aggregate probability total.

The application must execute this validation after completing the outcome records and before using the distribution for analysis.

### 17.3 Statistical Functions

| Function | Purpose |
|---|---|
| `expected_value()` | First raw moment |
| `raw_moment()` | Arbitrary raw moment |
| `central_moment()` | Arbitrary central moment |
| `distribution_variance()` | Second central moment |
| `distribution_stddev()` | Square root of variance |
| `conditional_expectation()` | Expected value above a threshold |
| `joint_statistics()` | Joint means, covariance, correlation |
| `evaluate_risk_policy()` | Financial policy assessment |

The `distribution_statistics` view consolidates expected value, variance, standard deviation, skewness, and kurtosis.

The `empirical_statistics` view uses PostgreSQL aggregate functions to calculate population and sample statistics.

The SQL script includes indexes on distribution identifiers and outcome values to support common retrieval and aggregation operations.

## 18. Important Statistical Distinctions

| Concept | Meaning | Mathematical basis |
|---|---|---|
| Expected value | Probability-weighted average | \(E[X]\) |
| Variance | Dispersion around the mean | \(E[(X-\mu)^2]\) |
| Standard deviation | Square root of variance | \(\sqrt{Var(X)}\) |
| Raw moment | Moment about zero | \(E[X^r]\) |
| Central moment | Moment about the mean | \(E[(X-\mu)^r]\) |
| Skewness | Standardized third central moment | \(\mu_3/\sigma^3\) |
| Kurtosis | Standardized fourth central moment | \(\mu_4/\sigma^4\) |
| Conditional expectation | Expectation under an event | \(E[X\mid A]\) |
| Covariance | Joint variation | \(E[(X-\mu_X)(Y-\mu_Y)]\) |
| Correlation | Standardized covariance | \(Cov(X,Y)/(\sigma_X\sigma_Y)\) |

These concepts describe different properties of probability distributions and should not be used interchangeably.

## 19. Edge Cases and Numerical Considerations

### Invalid probability totals

A discrete distribution whose probabilities sum to something other than one is invalid.

The implementations reject such distributions rather than silently normalizing the supplied probabilities.

### Negative outcomes

Negative outcomes are mathematically valid.

They are essential for representing financial losses, negative returns, and operational costs.

### Zero variance

When all possible outcomes are identical:

\[
Var(X)=0
\]

Standard deviation is also zero.

Skewness and kurtosis are undefined because their formulas divide by powers of standard deviation.

The implementations return a null or undefined statistical result rather than manufacturing a value.

### Zero-probability conditional events

Conditional expectation is undefined when the conditioning event has zero probability.

The implementations explicitly reject such calculations.

### Numerical precision

Floating-point arithmetic can introduce rounding errors.

The implementations use probability tolerances and finite-value validation.

For very large outcome magnitudes or extremely small probabilities, additional numerical safeguards may be necessary.

PostgreSQL `NUMERIC` provides decimal arithmetic, whereas the programming-language examples primarily use floating-point values.

### Sample size

Monte Carlo estimates fluctuate between simulations.

A fixed random seed provides reproducibility, not statistical certainty.

Simulation accuracy must be assessed using sample size, variance, and estimation error.

## 20. Computational Complexity

Let:

- \(n\) represent the number of possible outcomes.
- \(N\) represent the number of simulation trials.
- \(m\) represent the number of joint outcomes.

| Operation | Time complexity |
|---|---:|
| Distribution validation | \(O(n)\) |
| Expected value | \(O(n)\) |
| Raw moment | \(O(n)\) |
| Central moment | \(O(n)\) after mean calculation |
| Variance | \(O(n)\) |
| Standard deviation | \(O(n)\) |
| Conditional expectation | \(O(n)\) |
| Joint covariance | \(O(m)\) |
| Joint correlation | \(O(m)\) |
| Monte Carlo sampling | \(O(N)\) for fixed-size distributions |

For repeated simulations over a large distribution, cumulative probability intervals can be precomputed.

Binary search can then select outcomes in \(O(\log n)\) time per trial, reducing simulation complexity to \(O(n+N\log n)\) after preprocessing.

## 21. Practical Applications

Expected value and moments are useful in:

- Financial investment evaluation.
- Portfolio return estimation.
- Insurance claim analysis.
- Credit risk modeling.
- Operational risk assessment.
- Reliability engineering.
- Manufacturing quality control.
- Business decision analysis.
- Forecasting and uncertainty measurement.
- Simulation-based decision systems.

Expected value identifies the probability-weighted outcome, while variance and higher moments describe uncertainty and distribution shape.

A sound risk assessment uses these measures together rather than relying exclusively on the expected value.
