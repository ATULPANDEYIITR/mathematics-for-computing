# Continuous Distributions: Uniform, Exponential, and Normal

## 1. Project Overview

This project implements three fundamental continuous probability distributions across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover probability calculations, mathematical properties, random sampling, statistical estimation, simulation, and distribution monitoring.

The three distributions represent different types of uncertainty:

| Distribution | Parameters | Typical application |
|---|---|---|
| Uniform | Lower bound `a`, upper bound `b` | Random values with equal likelihood over a bounded interval |
| Exponential | Rate `λ` | Waiting times and time between independent events |
| Normal | Mean `μ`, standard deviation `σ` | Measurement variation and approximately symmetric natural phenomena |

Each implementation includes parameter validation, boundary handling, numerical calculations, and practical statistical analysis.

---

## 2. Mathematical Foundations

### 2.1 Continuous Random Variables

A continuous random variable can take any value within a specified interval or domain.

Unlike a discrete random variable, its probability is described through a probability density function.

For a continuous random variable `X`:

- `P(X = x) = 0` for any individual point.
- Probabilities are calculated over intervals.
- The total area under its probability density function equals one.

The probability of an interval is:

\[
P(a \leq X \leq b)
=
\int_a^b f(x)\,dx
\]

where `f(x)` is the probability density function.

The cumulative distribution function is:

\[
F(x)=P(X\leq x)
\]

For continuous distributions:

\[
P(a\leq X\leq b)=F(b)-F(a)
\]

The distinction between density and probability is important. A PDF value can exceed one because it represents density, not the probability of an individual observation.

### 2.2 Probability Density Function

The PDF describes how probability is distributed over the variable's domain.

Its principal properties are:

\[
f(x)\geq 0
\]

and

\[
\int_{-\infty}^{\infty}f(x)\,dx=1
\]

The PDF is useful for examining local probability concentration.

### 2.3 Cumulative Distribution Function

The CDF measures the probability that a random variable does not exceed a given value.

\[
F(x)=\int_{-\infty}^{x}f(t)\,dt
\]

Its properties include:

- It is non-decreasing.
- Its values lie between zero and one.
- Its limit at negative infinity is zero.
- Its limit at positive infinity is one.

### 2.4 Quantile Function

The quantile function is the inverse of the CDF.

\[
Q(p)=F^{-1}(p)
\]

It identifies the value below which a specified proportion of observations is expected to fall.

For example, the 95th percentile corresponds to:

\[
Q(0.95)
\]

Quantiles are useful for service-level thresholds, measurement limits, risk analysis, and operational capacity planning.

---

## 3. Uniform Distribution

### 3.1 Definition

A continuous uniform distribution assigns constant probability density throughout a bounded interval.

It is represented as:

\[
X\sim U(a,b)
\]

where:

- `a` is the lower bound.
- `b` is the upper bound.
- `a < b`.

### 3.2 Probability Density Function

\[
f(x)=
\begin{cases}
\frac{1}{b-a}, & a\leq x\leq b\\
0, & \text{otherwise}
\end{cases}
\]

The density is constant throughout the interval.

### 3.3 Cumulative Distribution Function

\[
F(x)=
\begin{cases}
0, & x<a\\
\frac{x-a}{b-a}, & a\leq x<b\\
1, & x\geq b
\end{cases}
\]

### 3.4 Mean

\[
E[X]=\frac{a+b}{2}
\]

### 3.5 Variance

\[
Var(X)=\frac{(b-a)^2}{12}
\]

### 3.6 Standard Deviation

\[
\sigma=\frac{b-a}{\sqrt{12}}
\]

### 3.7 Quantile Function

\[
Q(p)=a+p(b-a)
\]

### 3.8 Example

Consider a processing-duration variable uniformly distributed between zero and 100 minutes.

\[
X\sim U(0,100)
\]

Its mean is:

\[
E[X]=50
\]

Its variance is:

\[
Var(X)=\frac{100^2}{12}
=833.3333
\]

The probability of a duration between 20 and 80 minutes is:

\[
P(20\leq X\leq80)
=
\frac{80-20}{100}
=0.60
\]

### 3.9 Practical Applications

- Randomized scheduling.
- Simulation of bounded uncertainty.
- Initial-value generation.
- Modeling equally likely outcomes within known limits.
- Testing software under varying input conditions.

A uniform distribution is not appropriate when values are more likely near the center or when the process has a long waiting-time tail.

---

## 4. Exponential Distribution

### 4.1 Definition

The exponential distribution models non-negative waiting times between independent events occurring at a constant average rate.

It is represented as:

\[
X\sim Exp(\lambda)
\]

where:

\[
\lambda>0
\]

The parameter `λ` is the event rate, not the mean waiting time.

The relationship is:

\[
E[X]=\frac{1}{\lambda}
\]

### 4.2 Probability Density Function

\[
f(x)=
\begin{cases}
\lambda e^{-\lambda x}, & x\geq0\\
0, & x<0
\end{cases}
\]

The density decreases exponentially as waiting time increases.

### 4.3 Cumulative Distribution Function

\[
F(x)=
\begin{cases}
0, & x<0\\
1-e^{-\lambda x}, & x\geq0
\end{cases}
\]

### 4.4 Survival Function

The survival function measures the probability that the waiting time exceeds a specified value.

\[
S(x)=P(X>x)=e^{-\lambda x}
\]

It is particularly useful in reliability and service-arrival analysis.

### 4.5 Mean

\[
E[X]=\frac{1}{\lambda}
\]

### 4.6 Variance

\[
Var(X)=\frac{1}{\lambda^2}
\]

### 4.7 Standard Deviation

\[
\sigma=\frac{1}{\lambda}
\]

The exponential distribution has equal mean and standard deviation.

### 4.8 Quantile Function

\[
Q(p)=\frac{-\ln(1-p)}{\lambda}
\]

The quantile approaches infinity as `p` approaches one.

### 4.9 Hazard Function

The hazard function measures the instantaneous event rate conditional on survival up to a particular time.

\[
h(x)=\frac{f(x)}{S(x)}
\]

For the exponential distribution:

\[
h(x)=\lambda
\]

Its constant hazard rate is a defining property.

### 4.10 Memoryless Property

The exponential distribution has a unique memoryless property.

\[
P(X>s+t\mid X>s)=P(X>t)
\]

This means that the remaining waiting time has the same distribution regardless of how long the system has already waited.

For a service arrival rate of:

\[
\lambda=0.2
\]

the expected waiting time is:

\[
E[X]=5
\]

The probability that waiting time exceeds five units is:

\[
P(X>5)=e^{-0.2(5)}
=e^{-1}
\]

\[
P(X>5)\approx0.3679
\]

### 4.11 Practical Applications

- Time between customer arrivals.
- Time between independent equipment failures under a constant hazard assumption.
- Waiting-time models.
- Queueing systems.
- Reliability analysis.
- Event-arrival simulations.

The exponential model assumes a constant event rate. It is unsuitable when the failure rate changes with age or when events exhibit strong dependence.

---

## 5. Normal Distribution

### 5.1 Definition

The normal distribution is a continuous, symmetric, bell-shaped probability distribution.

It is represented as:

\[
X\sim N(\mu,\sigma^2)
\]

where:

- `μ` is the mean.
- `σ` is the standard deviation.
- `σ²` is the variance.

### 5.2 Probability Density Function

\[
f(x)=
\frac{1}{\sigma\sqrt{2\pi}}
e^{-\frac{(x-\mu)^2}{2\sigma^2}}
\]

The curve is symmetric around the mean.

### 5.3 Cumulative Distribution Function

\[
F(x)=
\Phi\left(\frac{x-\mu}{\sigma}\right)
\]

where `Φ` is the standard normal CDF.

The CDF can also be expressed using the error function:

\[
F(x)=
\frac{1}{2}
\left[
1+
erf\left(
\frac{x-\mu}{\sigma\sqrt{2}}
\right)
\right]
\]

### 5.4 Mean

\[
E[X]=\mu
\]

### 5.5 Variance

\[
Var(X)=\sigma^2
\]

### 5.6 Standardization

A normal observation can be converted into a standard normal score using:

\[
Z=\frac{X-\mu}{\sigma}
\]

The standardized variable follows:

\[
Z\sim N(0,1)
\]

The Z-score indicates the number of standard deviations an observation lies from the mean.

### 5.7 Empirical Interpretation

The empirical 68–95–99.7 rule describes the approximate proportion of observations within standard-deviation intervals.

| Interval | Approximate probability |
|---|---:|
| `μ ± 1σ` | 68.27% |
| `μ ± 2σ` | 95.45% |
| `μ ± 3σ` | 99.73% |

These are approximations rather than exact probabilities.

### 5.8 Quantile Function

The normal quantile function is:

\[
Q(p)=\mu+\sigma\Phi^{-1}(p)
\]

The inverse standard normal CDF generally requires numerical approximation or a statistical library.

The implementations use the Acklam rational approximation, with Newton refinement.

### 5.9 Example

Suppose measurement values follow:

\[
X\sim N(50,10^2)
\]

For an observation of 70:

\[
Z=\frac{70-50}{10}=2
\]

The observation is two standard deviations above the mean.

The cumulative probability is approximately:

\[
P(X\leq70)=0.97725
\]

### 5.10 Practical Applications

- Measurement variation.
- Quality control.
- Standardized scores.
- Error modeling.
- Statistical inference.
- Confidence intervals.
- Approximate modeling of aggregated natural variation.

A normal distribution has support over the entire real number line. It can therefore assign nonzero probability to negative values even when the real-world variable cannot be negative. Such situations may require a different model.

---

## 6. Comparison of the Three Distributions

| Property | Uniform | Exponential | Normal |
|---|---|---|---|
| Domain | `[a,b]` | `[0,∞)` | `(-∞,∞)` |
| Shape | Constant density | Right-skewed | Symmetric |
| Parameters | `a,b` | `λ` | `μ,σ` |
| Mean | `(a+b)/2` | `1/λ` | `μ` |
| Variance | `(b-a)²/12` | `1/λ²` | `σ²` |
| Support bounded | Yes | Lower-bounded | No |
| Symmetric | Yes | No | Yes |
| Constant hazard | Not applicable | Yes | No |
| Common application | Bounded uncertainty | Waiting time | Measurement variation |

### 6.1 Distribution Selection

The appropriate distribution depends on the mechanism producing the observations.

- Use uniform when all values within a bounded interval are equally likely.
- Use exponential when modeling waiting times generated by a constant-rate event process.
- Use normal when observations are reasonably symmetric around a central value.

Distribution selection should be supported by domain knowledge and empirical assessment rather than convenience alone.

---

## 7. Random Sampling and Simulation

### 7.1 Random Sampling

Random sampling generates observations from a specified probability distribution.

Each implementation provides a random sampling mechanism.

| Distribution | Sampling method |
|---|---|
| Uniform | Uniform pseudo-random number generation |
| Exponential | Inverse transform sampling |
| Normal | Box-Muller transformation or runtime Gaussian generation |

### 7.2 Inverse Transform Sampling

If `U` is uniformly distributed between zero and one, a random variable can be generated through:

\[
X=F^{-1}(U)
\]

For an exponential distribution:

\[
X=\frac{-\ln(1-U)}{\lambda}
\]

This transformation produces exponential observations from uniform random values.

### 7.3 Box-Muller Transformation

The Box-Muller transformation generates normally distributed observations using two independent uniform random variables.

\[
Z_1=
\sqrt{-2\ln U_1}
\cos(2\pi U_2)
\]

\[
Z_2=
\sqrt{-2\ln U_1}
\sin(2\pi U_2)
\]

Both values follow the standard normal distribution.

A general normal observation is obtained through:

\[
X=\mu+\sigma Z
\]

### 7.4 Reproducibility

A fixed pseudo-random seed allows the same random sequence to be reproduced within a particular random-number implementation.

This supports:

- Regression testing.
- Debugging.
- Experiment comparison.
- Simulation verification.

The same seed does not guarantee identical sequences across different programming languages because their random-number algorithms differ.

Simulation random generators are not suitable for cryptographic secrets or security-sensitive token generation.

---

## 8. Statistical Analysis of Simulated Observations

The five source implementations provide descriptive and inferential analysis.

### 8.1 Sample Mean

\[
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
\]

The sample mean estimates the theoretical expected value.

### 8.2 Sample Variance

\[
s^2=
\frac{1}{n-1}
\sum_{i=1}^{n}(x_i-\bar{x})^2
\]

The denominator `n - 1` provides the conventional unbiased sample variance estimator.

### 8.3 Sample Standard Deviation

\[
s=\sqrt{s^2}
\]

### 8.4 Empirical Probability

For an interval `[a,b]`, the empirical probability is:

\[
\hat{P}(a\leq X\leq b)
=
\frac{
\sum_{i=1}^{n}I(a\leq x_i\leq b)
}{n}
\]

where `I` is an indicator function.

The empirical probability should approach the theoretical probability as the sample size increases under appropriate sampling assumptions.

### 8.5 Confidence Interval for the Mean

For sufficiently large independent samples, an approximate normal-based confidence interval is:

\[
\bar{x}\pm z_{\alpha/2}\frac{s}{\sqrt{n}}
\]

For a 95% interval:

\[
z_{\alpha/2}\approx1.96
\]

The Python, JavaScript, C++, and Java implementations use this approximation.

For small samples from a normal population with unknown variance, a Student's t critical value is preferable.

A confidence interval describes uncertainty in an estimated population mean. It does not mean that 95% of individual observations lie within that interval.

---

## 9. Empirical Distribution Assessment

### 9.1 Empirical CDF

The empirical CDF estimates the probability distribution from observed data.

\[
F_n(x)=
\frac{1}{n}
\sum_{i=1}^{n}I(X_i\leq x)
\]

It can be compared with the theoretical CDF.

### 9.2 Kolmogorov-Smirnov Distance

The implementations calculate the empirical two-sided CDF distance:

\[
D_n=\sup_x|F_n(x)-F(x)|
\]

The value measures the largest observed difference between the empirical and theoretical CDFs.

A smaller value indicates closer empirical agreement.

The calculated distance is a statistic, not a calibrated p-value. Formal hypothesis testing requires an appropriate null distribution and critical values. When distribution parameters are estimated from the same sample, the standard one-sample KS calibration is not directly applicable without adjustment.

### 9.3 Histogram

A histogram divides the observation range into bins.

Each bin records the number of observations within its interval.

Histograms help identify:

- Distribution shape.
- Skewness.
- Unusual observations.
- Possible outliers.
- Differences between empirical and theoretical patterns.

Bin width affects interpretation. Too few bins can hide important features, while too many can produce a noisy display.

---

## 10. Python Implementation

### 10.1 Architecture

The Python implementation uses an object-oriented distribution model.

The principal components are:

| Component | Responsibility |
|---|---|
| `ContinuousDistribution` | Common distribution interface |
| `UniformDistribution` | Uniform mathematical operations |
| `ExponentialDistribution` | Exponential mathematical operations |
| `NormalDistribution` | Normal mathematical operations |
| `SampleStatistics` | Immutable descriptive statistics |
| `DistributionError` | Parameter and operation validation |
| `calculate_statistics()` | Sample aggregation |
| `confidence_interval_mean()` | Mean interval estimation |
| `ks_empirical_distance()` | Empirical distribution comparison |
| `histogram()` | Frequency aggregation |

### 10.2 Implementation Decisions

The implementation uses:

- Dataclasses for immutable distribution parameters.
- Enums for distribution classification.
- `random.Random` for reproducible sampling.
- `math.erfc` for the standard normal CDF.
- `statistics` for descriptive calculations.
- Acklam approximation for inverse normal calculations.
- Assertions for mathematical and validation tests.

### 10.3 Execution

The program runs the three distributions with 100,000 observations each.

It reports theoretical and empirical statistics, interval probabilities, confidence intervals, KS distances, and histograms.

No third-party Python package is required.

---

## 11. JavaScript Implementation

### 11.1 Architecture

The JavaScript implementation emphasizes event-loop compatibility, deterministic simulation, and memory-efficient monitoring.

| Component | Responsibility |
|---|---|
| `RandomGenerator` | Seeded pseudo-random generation |
| `Distribution` | Common distribution interface |
| `UniformDistribution` | Uniform model |
| `ExponentialDistribution` | Exponential model |
| `NormalDistribution` | Normal model |
| `OnlineStatistics` | Incremental statistical aggregation |
| `DistributionMonitor` | Interval monitoring |
| `analyzeInBatches()` | Asynchronous simulation |

### 11.2 Seeded Random Generation

The implementation uses Mulberry32 to generate reproducible pseudo-random values.

The generator supports uniform, exponential, and normal sampling.

The normal sampler uses Box-Muller transformation.

### 11.3 Online Statistics

Welford's algorithm calculates sample mean and variance incrementally.

The update mechanism is:

\[
\delta=x_n-\bar{x}_{n-1}
\]

\[
\bar{x}_n=\bar{x}_{n-1}+\frac{\delta}{n}
\]

\[
M_{2,n}=M_{2,n-1}
+\delta(x_n-\bar{x}_n)
\]

The sample variance is:

\[
s^2=\frac{M_2}{n-1}
\]

This approach avoids retaining the entire observation array when only aggregate statistics are required.

### 11.4 Asynchronous Processing

The batch simulation function periodically yields to the Node.js event loop.

This reduces the likelihood that a large simulation monopolizes the event loop.

The implementation does not claim that asynchronous execution automatically makes numerical calculations parallel.

---

## 12. C++17 Implementation

### 12.1 Architecture

The C++ program uses polymorphism and explicit domain modeling.

| Component | Responsibility |
|---|---|
| `ContinuousDistribution` | Abstract distribution interface |
| `UniformDistribution` | Uniform model |
| `ExponentialDistribution` | Exponential model |
| `NormalDistribution` | Normal model |
| `RandomSource` | Random-number generation |
| `RunningStatistics` | Incremental descriptive statistics |
| `HistogramBin` | Histogram representation |
| `SimulationResult` | Simulation output |

### 12.2 Random Generation

The implementation uses:

- `std::mt19937_64`
- `std::uniform_real_distribution`
- `std::exponential_distribution`
- `std::normal_distribution`

The standard library handles the distribution-specific sampling algorithms.

### 12.3 Polymorphism

The abstract interface defines common operations.

Concrete distribution classes implement the same mathematical operations while preserving their different parameterizations and support.

This enables a common simulation function to process different distribution types.

### 12.4 Memory Management

The program reserves observation-vector capacity before simulation.

This reduces repeated dynamic allocations.

Online statistics are also maintained to avoid unnecessary repeated aggregation.

### 12.5 Error Handling

The implementation uses a custom exception type to reject invalid distribution parameters, probabilities, sample sizes, and intervals.

---

## 13. Java 17 Implementation

### 13.1 Enterprise Scenario

The Java implementation models a statistical service used for operational analysis.

Its three distributions represent:

- Bounded processing-duration uncertainty.
- Time between service arrivals.
- Measurement variation around a target.

### 13.2 Domain Architecture

| Component | Responsibility |
|---|---|
| `ContinuousDistribution` | Distribution contract |
| `DistributionType` | Distribution classification |
| `Interval` | Validated analysis interval |
| `DistributionReport` | Immutable simulation result |
| `SimulationService` | Execution and reporting |
| `OnlineStatistics` | Incremental aggregation |
| `executeBatch()` | Concurrent distribution analysis |

### 13.3 Records and Immutable Results

Java records provide immutable result structures.

The `DistributionReport` record carries:

- Distribution classification.
- Sample count.
- Theoretical mean and variance.
- Empirical mean and variance.
- Standard deviation.
- Minimum and maximum.
- Theoretical and empirical probabilities.
- Mean confidence interval.
- Empirical KS distance.

### 13.4 Concurrent Execution

The three simulation jobs execute independently through `CompletableFuture`.

An `ExecutorService` manages the worker threads.

Each job owns its random generator and statistical state, avoiding shared mutable random-generation state.

The service waits for all tasks before producing the consolidated report.

Failures are propagated through `CompletionException` and converted into domain-specific errors.

### 13.5 Operational Considerations

The implementation separates:

- Distribution parameters.
- Simulation execution.
- Statistical calculations.
- Immutable reporting.
- Concurrent orchestration.

This separation makes the design easier to extend with additional distribution models and operational reporting policies.

---

## 14. PostgreSQL Implementation

### 14.1 Database Architecture

The SQL implementation models a relational statistical simulation workflow.

The schema is:

`continuous_stats`

The primary entities are:

| Table | Purpose |
|---|---|
| `distribution_registry` | Stores distribution definitions and parameters |
| `simulation_runs` | Stores simulation configuration and lifecycle state |
| `observations` | Stores generated numerical observations |

### 14.2 Entity Relationships

The logical relationship is:

Distribution Registry

→ Simulation Runs

→ Observations

One distribution can have multiple simulation runs.

One simulation run can contain multiple observations.

The foreign keys enforce referential integrity.

### 14.3 Distribution Parameter Constraints

The distribution registry uses an enum to distinguish the three distribution families.

Its check constraints enforce:

**Uniform**

\[
a<b
\]

**Exponential**

\[
\lambda>0
\]

**Normal**

\[
\sigma>0
\]

The database also rejects non-finite parameter values.

### 14.4 Mathematical SQL Functions

The schema implements:

| Function | Purpose |
|---|---|
| `uniform_pdf()` | Uniform density |
| `uniform_cdf()` | Uniform cumulative probability |
| `uniform_quantile()` | Uniform inverse CDF |
| `exponential_pdf()` | Exponential density |
| `exponential_cdf()` | Exponential cumulative probability |
| `exponential_quantile()` | Exponential inverse CDF |
| `normal_pdf()` | Normal density |
| `normal_cdf()` | Normal cumulative probability |
| `normal_quantile()` | Normal inverse CDF |

The normal CDF uses an error-function approximation.

The normal quantile uses bisection on the standardized interval `[-40,40]`.

### 14.5 Simulation Lifecycle

Simulation runs follow explicit states:

`CREATED → RUNNING → COMPLETED`

A failure can produce:

`CREATED → FAILED`

or:

`RUNNING → FAILED`

Triggers enforce valid state transitions.

Completed and failed runs cannot be reopened through ordinary updates.

Observations can only be inserted into running simulations.

The completion procedure verifies that the expected number of observations has been stored.

### 14.6 Observation Integrity

Each observation contains:

- Simulation identifier.
- Observation sequence number.
- Observed value.
- Observation timestamp.

The unique constraint on `(simulation_id, observation_number)` prevents duplicate sequence numbers within a simulation.

The observation trigger verifies that the simulation is running and that the observation number does not exceed the requested sample count.

### 14.7 Analytical Views

The database provides:

- `distribution_parameters`
- `simulation_statistics`
- `interval_probability_report`
- `distribution_quantile_report`
- `simulation_quality_report`

These views support reporting without requiring applications to reconstruct every aggregation query.

### 14.8 Performance

The implementation creates indexes for:

- Distribution and simulation status.
- Simulation-based observation retrieval.
- Observation-value filtering.
- Observation ordering.

For large-scale workloads, bulk insertion, partitioning, and materialized aggregates can reduce reporting overhead.

---

## 15. Numerical Accuracy and Edge Cases

### 15.1 Uniform Distribution

Important validation conditions:

- The lower bound must be smaller than the upper bound.
- Both parameters must be finite.
- The CDF must return zero below the lower bound.
- The CDF must return one at and above the upper bound.

### 15.2 Exponential Distribution

Important validation conditions:

- The rate must be strictly positive.
- Negative observations have zero density.
- The CDF is zero for non-positive values.
- The quantile at probability one is positive infinity.

The implementations use numerically stable expressions such as `log1p()` and `expm1()` where available.

### 15.3 Normal Distribution

Important validation conditions:

- The mean must be finite.
- The standard deviation must be finite and strictly positive.
- The CDF and PDF must handle large positive and negative standardized values.
- The inverse CDF must handle probabilities zero and one explicitly.

### 15.4 Floating-Point Limitations

All five implementations use floating-point arithmetic.

Small differences can occur because of:

- Different random-number algorithms.
- Different mathematical library implementations.
- Approximation errors.
- Floating-point rounding.
- Different inverse-CDF methods.

Cross-language simulation outputs should be compared statistically rather than expecting identical individual random observations.

---

## 16. Complexity and Performance

Let `n` represent the number of simulated observations and `k` the number of histogram bins.

| Operation | Time complexity | Additional space |
|---|---:|---:|
| PDF evaluation | O(1) | O(1) |
| CDF evaluation | O(1) | O(1) |
| Uniform quantile | O(1) | O(1) |
| Exponential quantile | O(1) | O(1) |
| Normal quantile approximation | O(1) | O(1) |
| Random sample generation | O(n) | O(1) per observation |
| Online mean and variance | O(n) | O(1) |
| Histogram | O(n + k) | O(k) |
| Empirical CDF at one value | O(n) | O(1) |
| Empirical KS distance | O(n log n) | O(n) |

The C++ and Java implementations retain observations for KS analysis.

The Python implementation also retains observations for histogram and empirical comparisons.

The JavaScript implementation demonstrates streaming aggregation for its primary monitoring workflow.

The PostgreSQL implementation stores observations relationally, which supports repeatable analysis and SQL-based reporting but requires additional storage and indexing.

---

## 17. Testing and Validation

The implementations include mathematical assertions and invalid-input tests.

The principal validation cases are:

| Test | Expected behavior |
|---|---|
| Uniform density inside the interval | Positive constant density |
| Uniform density outside the interval | Zero |
| Uniform CDF below lower bound | Zero |
| Uniform CDF above upper bound | One |
| Exponential density for negative values | Zero |
| Exponential CDF at zero | Zero |
| Exponential rate equal to zero | Rejected |
| Normal CDF at its mean | Approximately 0.5 |
| Normal quantile at 0.5 | Equal to the mean |
| Normal standard deviation equal to zero | Rejected |
| Probability below zero | Rejected |
| Probability above one | Rejected |
| Empty statistical sample | Rejected |
| Invalid interval | Rejected |

The theoretical mean and variance are also compared with empirical estimates.

For sufficiently large independent samples, empirical estimates should generally approach their corresponding theoretical values.

---

## 18. Security and Production Considerations

Statistical simulation and production data handling have different security requirements.

The implementations use pseudo-random generators for simulation, not cryptographic operations.

For production use:

- Do not use simulation random generators for passwords, authentication tokens, or cryptographic keys.
- Validate externally supplied parameters.
- Limit requested sample counts to prevent excessive CPU and memory consumption.
- Avoid accepting non-finite numerical inputs.
- Use parameterized SQL queries in application integrations.
- Restrict database write privileges.
- Protect stored observations where they contain sensitive operational information.
- Monitor failed simulation runs.
- Maintain consistent random seeds and configuration metadata for reproducibility.
- Apply database retention policies to large observation datasets.

The PostgreSQL schema provides structural integrity controls, but production deployments should also enforce role-based permissions and operational access policies.

---

## 19. Limitations

The implementations are designed for mathematical learning and reproducible simulation rather than replacing specialized statistical systems.

Important limitations include:

1. The JavaScript error-function approximation is less accurate than a high-precision numerical implementation.
2. The C++ and Java random generators are not guaranteed to produce identical values across languages.
3. The confidence intervals use a normal approximation.
4. The empirical KS distance is not a calibrated hypothesis-test p-value.
5. The exponential model assumes a constant hazard rate.
6. The normal model permits negative values and unbounded tails.
7. The uniform model assumes constant density over a specified interval.
8. PostgreSQL stores individual observations, which can become expensive for very large simulations.
9. The PostgreSQL normal quantile uses a bounded standardized bisection search and finite floating-point precision.
10. The simulations do not establish that a selected theoretical distribution accurately describes a real-world dataset.

A distribution should be selected and evaluated using the underlying process, empirical observations, model assumptions, and intended statistical application.
