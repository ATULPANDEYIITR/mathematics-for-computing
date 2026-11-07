# Advanced Distributions

## Project Overview

This project implements four important probability distributions used in statistical modeling, reliability engineering, Bayesian inference, and hypothesis testing.

The distributions are:

1. Poisson distribution
2. Gamma distribution
3. Beta distribution
4. Chi-square distribution

Five independent implementations provide statistical calculations, numerical algorithms, simulation, validation, and database-based statistical workflows.

| Implementation | Main responsibility |
|---|---|
| Python | Distribution modeling, simulation, Bayesian updating, and hypothesis testing |
| JavaScript | Event-driven statistical experiments and deterministic random sampling |
| C++17 | Numerical computation, statistical sampling, and performance-oriented modeling |
| Java 17 | Enterprise-oriented distribution services and immutable statistical results |
| PostgreSQL | Persistent statistical experiments, Bayesian reporting, and goodness-of-fit evaluation |

## 1. Probability Distribution Fundamentals

A probability distribution describes how probabilities are assigned to possible outcomes of a random variable.

There are two fundamental categories.

### Discrete distributions

A discrete random variable takes countable values.

Its probability mass function (PMF) defines:

\[
P(X=k)
\]

The Poisson distribution belongs to this category.

### Continuous distributions

A continuous random variable can take values across an interval.

Its probability density function (PDF) describes probability density rather than the probability of an individual point.

For a continuous variable:

\[
P(a \leq X \leq b)
=
\int_a^b f(x)\,dx
\]

The Gamma, Beta, and Chi-square distributions are continuous distributions.

Their cumulative distribution function is:

\[
F(x)=P(X\leq x)
\]

For a continuous distribution:

\[
P(a<X\leq b)=F(b)-F(a)
\]

A PDF and a CDF serve different purposes. A PDF describes density, whereas a CDF gives accumulated probability.

## 2. Poisson Distribution

### Purpose

The Poisson distribution models the number of events occurring within a fixed interval of time, distance, area, or another measurable exposure.

Examples include:

- Customer arrivals per hour.
- Server requests per minute.
- Equipment failures per month.
- Network incidents per monitoring interval.
- Manufacturing defects per production batch.

The distribution is based on a rate parameter:

\[
\lambda>0
\]

Here, \(\lambda\) represents the expected event count within the specified interval.

### Probability mass function

\[
P(X=k)=
\frac{e^{-\lambda}\lambda^k}{k!}
\]

Where:

- \(k\) is a nonnegative integer.
- \(\lambda\) is the expected event count.
- \(e\) is the exponential constant.
- \(k!\) is the factorial of the event count.

### Cumulative distribution function

The Poisson CDF can be expressed using the regularized upper incomplete gamma function:

\[
F(k)=P(X\leq k)
=
Q(k+1,\lambda)
\]

In the implementations, the same result is calculated through the regularized lower incomplete gamma function with reversed arguments:

\[
F(k)=P(k+1,\lambda)
\]

Here, the capital \(P\) denotes the regularized lower incomplete gamma function.

### Statistical properties

| Property | Formula |
|---|---|
| Mean | \(\lambda\) |
| Variance | \(\lambda\) |
| Standard deviation | \(\sqrt{\lambda}\) |
| Support | \(0,1,2,\ldots\) |

An important property is that the theoretical mean equals the theoretical variance.

### Implementation

The Python implementation provides `PoissonDistribution`, with PMF, CDF, moments, and random sampling.

JavaScript and Java implement Poisson sampling using Knuth's algorithm for smaller rates and transformed rejection sampling for larger rates.

C++17 uses the standard library's `std::poisson_distribution`.

PostgreSQL implements `poisson_pmf()` and `poisson_cdf()` for direct database calculations.

### Practical interpretation

For a service receiving an average of 4.5 requests per minute:

\[
X\sim Poisson(4.5)
\]

The probability of receiving exactly three requests is:

\[
P(X=3)=
\frac{e^{-4.5}(4.5)^3}{3!}
\]

The probability of receiving no more than five requests is:

\[
P(X\leq5)
\]

This can help establish operational thresholds and capacity planning assumptions.

The Poisson model assumes a constant event rate and independent events. It may be inappropriate when events cluster or the rate changes substantially over time.

## 3. Gamma Distribution

### Purpose

The Gamma distribution models positive continuous quantities, particularly waiting times, durations, and aggregated positive measurements.

Applications include:

- Time until multiple events occur.
- Equipment repair duration.
- Insurance claim amounts under suitable models.
- Service completion times.
- Reliability and survival analysis.

It has two principal parameters:

- Shape: \(\alpha>0\)
- Scale: \(\theta>0\)

The shape controls the distribution's form, while the scale controls its horizontal spread.

### Probability density function

\[
f(x)=
\frac{x^{\alpha-1}e^{-x/\theta}}
{\Gamma(\alpha)\theta^\alpha}
\]

For:

\[
x>0
\]

The Gamma function is:

\[
\Gamma(\alpha)=
\int_0^\infty
t^{\alpha-1}e^{-t}\,dt
\]

For positive integers:

\[
\Gamma(n)=(n-1)!
\]

### Cumulative distribution function

\[
F(x)=
P\left(\alpha,\frac{x}{\theta}\right)
\]

Where \(P(a,x)\) is the regularized lower incomplete gamma function.

### Statistical properties

| Property | Formula |
|---|---|
| Mean | \(\alpha\theta\) |
| Variance | \(\alpha\theta^2\) |
| Standard deviation | \(\theta\sqrt{\alpha}\) |
| Support | \(x\geq0\) |

### Important distinction: Shape and rate

Some statistical systems parameterize the Gamma distribution using shape and rate rather than shape and scale.

The conversion is:

\[
\text{Rate}=\frac{1}{\theta}
\]

A Gamma distribution with shape 3 and scale 2 has the same distribution as one with shape 3 and rate 0.5.

Confusing these parameterizations produces incorrect density and probability calculations.

### Implementation

The implementations provide:

- Gamma PDF.
- Gamma CDF.
- Theoretical moments.
- Random sampling.
- Positive-parameter validation.
- Boundary handling at zero.

The random sampling implementations use the Marsaglia-Tsang method, with a transformation for shape parameters below one.

C++17 uses `std::gamma_distribution`.

PostgreSQL provides `gamma_pdf()` and `gamma_cdf()`.

### Practical example

Suppose equipment repair time is modeled as:

\[
X\sim Gamma(3,2)
\]

The expected repair duration is:

\[
E[X]=3\times2=6
\]

The variance is:

\[
Var(X)=3\times2^2=12
\]

The probability of completing a repair within five time units is obtained using:

\[
P(X\leq5)=F(5)
\]

The result can support service-level analysis and maintenance planning.

## 4. Beta Distribution

### Purpose

The Beta distribution models an unknown probability or proportion.

Its support is bounded:

\[
0\leq x\leq1
\]

It is particularly important in Bayesian statistics because it is a conjugate prior for the Bernoulli and Binomial likelihoods.

Applications include:

- Website conversion rates.
- Product defect probabilities.
- Customer response rates.
- Model accuracy uncertainty.
- Success probabilities in experiments.

Its parameters are:

\[
\alpha>0,\qquad\beta>0
\]

### Probability density function

\[
f(x)=
\frac{x^{\alpha-1}(1-x)^{\beta-1}}
{B(\alpha,\beta)}
\]

Where the Beta function is:

\[
B(\alpha,\beta)=
\frac{\Gamma(\alpha)\Gamma(\beta)}
{\Gamma(\alpha+\beta)}
\]

### Cumulative distribution function

\[
F(x)=I_x(\alpha,\beta)
\]

Where \(I_x\) is the regularized incomplete beta function.

### Statistical properties

| Property | Formula |
|---|---|
| Mean | \(\frac{\alpha}{\alpha+\beta}\) |
| Variance | \(\frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}\) |
| Support | \([0,1]\) |

### Shape interpretation

Different parameter combinations create different distribution shapes.

| Parameters | General behavior |
|---|---|
| \(\alpha=\beta=1\) | Uniform distribution |
| \(\alpha>1,\beta>1\) | Interior concentration |
| \(\alpha<1,\beta<1\) | Concentration near boundaries |
| \(\alpha>\beta\) | Greater concentration toward one |
| \(\alpha<\beta\) | Greater concentration toward zero |

The exact shape also depends on the magnitude of both parameters.

### Bayesian updating

Consider a website conversion experiment.

Assume the prior distribution is:

\[
p\sim Beta(2,2)
\]

Suppose the experiment observes:

- 45 successful conversions.
- 55 unsuccessful conversions.

The posterior parameters become:

\[
\alpha_{posterior}=\alpha_{prior}+45
\]

\[
\beta_{posterior}=\beta_{prior}+55
\]

Therefore:

\[
p\mid Data\sim Beta(47,57)
\]

The posterior mean is:

\[
E[p\mid Data]=\frac{47}{104}
\]

\[
E[p\mid Data]\approx0.451923
\]

The posterior distribution represents uncertainty about the conversion probability after observing the experiment.

### Why this matters

A frequentist estimate of the conversion rate is:

\[
\hat p=\frac{45}{100}=0.45
\]

The Bayesian posterior mean incorporates prior information.

The difference is important when sample sizes are small or previous information is meaningful.

### Implementation

The Python, JavaScript, C++17, and Java implementations provide Beta PDF, CDF, moments, and random sampling.

The JavaScript and Java implementations construct Beta samples using two Gamma random variables:

\[
X\sim Gamma(\alpha,1)
\]

\[
Y\sim Gamma(\beta,1)
\]

\[
Z=\frac{X}{X+Y}
\]

Then:

\[
Z\sim Beta(\alpha,\beta)
\]

The PostgreSQL implementation supports Beta probability calculations and stores experiment observations with posterior reporting.

## 5. Chi-square Distribution

### Purpose

The Chi-square distribution is used extensively in statistical inference.

It arises from the sum of squared independent standard normal random variables.

If:

\[
Z_1,Z_2,\ldots,Z_k
\]

are independent standard normal variables, then:

\[
X=\sum_{i=1}^{k}Z_i^2
\]

follows a Chi-square distribution with \(k\) degrees of freedom.

### Probability density function

\[
f(x)=
\frac{x^{k/2-1}e^{-x/2}}
{2^{k/2}\Gamma(k/2)}
\]

For:

\[
x\geq0
\]

The degrees of freedom parameter is:

\[
k>0
\]

### Cumulative distribution function

\[
F(x)=
P\left(\frac{k}{2},\frac{x}{2}\right)
\]

Where \(P\) is the regularized lower incomplete gamma function.

### Statistical properties

| Property | Formula |
|---|---|
| Mean | \(k\) |
| Variance | \(2k\) |
| Standard deviation | \(\sqrt{2k}\) |
| Support | \(x\geq0\) |
| Degrees of freedom | \(k>0\) |

### Applications

The Chi-square distribution is commonly used for:

- Goodness-of-fit tests.
- Tests of independence.
- Tests of homogeneity.
- Variance inference under normality assumptions.

The distribution also appears in likelihood-ratio procedures and other asymptotic statistical tests.

## 6. Chi-square Goodness-of-Fit Testing

The goodness-of-fit test evaluates whether observed categorical frequencies are consistent with specified expected frequencies.

The hypotheses are:

- Null hypothesis: The observed data are consistent with the specified probability model.
- Alternative hypothesis: The observed data are inconsistent with the specified model.

### Pearson Chi-square statistic

\[
\chi^2=
\sum_{i=1}^{n}
\frac{(O_i-E_i)^2}{E_i}
\]

Where:

- \(O_i\) is the observed frequency.
- \(E_i\) is the expected frequency.
- \(n\) is the number of categories.

For a goodness-of-fit test with no estimated parameters:

\[
df=n-1
\]

If parameters are estimated from the same data, the degrees of freedom generally become:

\[
df=n-1-m
\]

Where \(m\) is the number of independently estimated parameters, subject to the assumptions of the test.

### Example

Consider the following observed and expected frequencies.

| Category | Observed | Expected |
|---|---:|---:|
| A | 48 | 50 |
| B | 32 | 30 |
| C | 15 | 15 |
| D | 5 | 5 |

The statistic is:

\[
\chi^2=
\frac{(48-50)^2}{50}
+
\frac{(32-30)^2}{30}
+
\frac{(15-15)^2}{15}
+
\frac{(5-5)^2}{5}
\]

\[
\chi^2=0.213333
\]

Degrees of freedom:

\[
df=4-1=3
\]

The p-value is the upper-tail probability:

\[
p=P(\chi^2_{df}\geq0.213333)
\]

The decision uses:

\[
p<0.05
\]

If the p-value is below the significance level, reject the null hypothesis.

Otherwise, there is insufficient evidence to reject it.

### Important assumptions

- Observations should be independent.
- Categories should be mutually exclusive.
- Expected frequencies should generally be sufficiently large.
- Categories with small expected counts may require pooling.
- Estimated model parameters must be reflected in the degrees of freedom.

The supplied implementations enforce expected frequencies of at least five. This is a conservative educational validation rule, not a universal mathematical requirement.

## 7. Numerical Algorithms

Accurate distribution calculations require special mathematical functions.

The implementations avoid repeatedly evaluating factorials or directly integrating complicated probability densities.

### Log-gamma approximation

The Gamma function grows rapidly.

Directly calculating:

\[
\Gamma(x)
\]

can produce overflow for relatively large inputs.

Instead, the implementations use:

\[
\log\Gamma(x)
\]

A Lanczos approximation provides a numerically convenient method for evaluating this function.

This is particularly important for:

- Poisson PMF calculations.
- Gamma PDF calculations.
- Beta normalization.
- Chi-square PDF calculations.

### Regularized incomplete gamma function

The regularized lower incomplete gamma function is:

\[
P(a,x)=\frac{\gamma(a,x)}{\Gamma(a)}
\]

It is used in:

- Poisson CDF.
- Gamma CDF.
- Chi-square CDF.

The implementations use two numerical approaches.

| Region | Method |
|---|---|
| \(x<a+1\) | Infinite-series expansion |
| \(x\geq a+1\) | Continued fraction for the complementary probability |

This division improves convergence and numerical stability.

### Regularized incomplete beta function

The regularized incomplete beta function is:

\[
I_x(a,b)=\frac{B_x(a,b)}{B(a,b)}
\]

The implementations evaluate it using a continued fraction.

Symmetry is used to avoid poorly conditioned calculations:

\[
I_x(a,b)=1-I_{1-x}(b,a)
\]

The implementation selects the appropriate evaluation region based on the input parameters.

### Numerical limitations

Floating-point calculations have finite precision.

Potential issues include:

- Underflow for extremely small probabilities.
- Overflow for extreme parameters.
- Loss of precision when subtracting values close to one.
- Slow convergence for extreme parameter combinations.
- Infinite density at some distribution boundaries.

The implementations use logarithmic density calculations, convergence limits, small denominators, and input validation to reduce these problems.

They are educational numerical implementations, not replacements for independently validated statistical libraries in safety-critical or regulated analysis.

## 8. Random Sampling and Simulation

Analytical calculations describe theoretical probability behavior.

Simulation provides an empirical way to examine that behavior.

The implementations compare theoretical moments against sampled observations.

### Monte Carlo workflow

The simulation process is:

1. Initialize a random number generator.
2. Select a probability distribution.
3. Generate observations.
4. Calculate empirical mean.
5. Calculate empirical variance.
6. Compare empirical and theoretical results.
7. Inspect minimum and maximum values.

### Theoretical versus empirical moments

The sample mean is:

\[
\bar{x}=\frac{1}{N}\sum_{i=1}^{N}x_i
\]

The population-form empirical variance used by the implementations is:

\[
\sigma^2_{empirical}
=
\frac{1}{N}\sum_{i=1}^{N}(x_i-\bar{x})^2
\]

This denominator is \(N\), not \(N-1\).

The distinction matters when comparing a simulation estimate with the theoretical population variance.

### Reproducibility

The implementations use fixed seeds in their demonstrations.

A fixed seed allows the same pseudorandom sequence to be reproduced within the same generator implementation.

The Python implementation uses a seeded `random.Random` instance.

JavaScript implements a deterministic xorshift32 generator.

C++17 uses `std::mt19937_64`.

Java uses `java.util.Random`.

The same seed does not imply identical samples across different languages because the underlying random-number generators and sampling algorithms differ.

## 9. Implementation Architecture

### Python

The Python implementation uses immutable dataclasses to represent distribution parameters.

Each distribution provides:

- Parameter validation.
- PMF or PDF.
- CDF.
- Mean.
- Variance.
- Random sampling.

The implementation separates shared mathematical functions from distribution-specific behavior.

`chi_square_goodness_of_fit()` provides an independent hypothesis-testing workflow.

`simulate()` provides a common interface for empirical analysis.

Assertions verify fundamental distribution properties.

### JavaScript

The JavaScript implementation uses classes and a `Map` to register distributions.

A dedicated `RandomSource` class manages seeded random generation.

The statistical experiment runner uses asynchronous execution and `Promise.all()` to collect independent simulation reports.

The design separates:

- Numerical calculations.
- Distribution state.
- Random-number generation.
- Experiment execution.
- Statistical decision-making.

### C++17

The C++ implementation emphasizes domain modeling and standard-library facilities.

It uses:

- Classes for distributions.
- Structs for statistical results.
- `std::vector` for simulation observations.
- STL algorithms for aggregation.
- Exceptions for validation and failure handling.
- `<random>` for statistical sampling.

The standard library provides Poisson and Gamma sampling directly.

Beta sampling is implemented through the relationship between independent Gamma variables.

### Java 17

The Java implementation defines a `Distribution` interface.

The four distributions implement a common statistical contract.

A separate `StatisticalService` handles goodness-of-fit testing.

Records provide immutable result representations for:

- Goodness-of-fit evaluations.
- Simulation summaries.

The architecture separates distribution behavior from statistical services and experiment execution.

### PostgreSQL

The database implementation provides persistent statistical workflows.

Its principal components are:

| Database object | Responsibility |
|---|---|
| `distribution_registry` | Distribution metadata |
| `bayesian_experiments` | Prior parameters and observed outcomes |
| `bayesian_posterior_report` | Posterior parameter and moment calculations |
| `simulation_runs` | Simulation metrics |
| `goodness_of_fit_tests` | Hypothesis-testing results |
| `goodness_of_fit_categories` | Observed and expected category frequencies |

Database functions implement numerical calculations.

A procedure updates Bayesian experiment observations.

A trigger validates simulation records before insertion or modification.

Indexes support distribution-based simulation reporting and test-category retrieval.

Transactions protect related database changes from partial completion.

The SQL implementation does not attempt to generate random simulation samples inside PostgreSQL. Simulation metrics can be generated by the application implementations and persisted in `simulation_runs`.

## 10. Cross-Distribution Comparison

| Characteristic | Poisson | Gamma | Beta | Chi-square |
|---|---|---|---|---|
| Type | Discrete | Continuous | Continuous | Continuous |
| Main purpose | Event counts | Positive durations | Probabilities | Statistical inference |
| Parameters | \(\lambda\) | \(\alpha,\theta\) | \(\alpha,\beta\) | \(k\) |
| Support | Nonnegative integers | Nonnegative real values | Zero to one | Nonnegative real values |
| Main function | PMF | PDF | PDF | PDF |
| Mean | \(\lambda\) | \(\alpha\theta\) | \(\frac{\alpha}{\alpha+\beta}\) | \(k\) |
| Variance | \(\lambda\) | \(\alpha\theta^2\) | \(\frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}\) | \(2k\) |

### Important mathematical relationships

The Gamma and Chi-square distributions are directly related.

If:

\[
X\sim Gamma(\alpha,\theta)
\]

and:

\[
\alpha=\frac{k}{2},\qquad\theta=2
\]

then:

\[
X\sim\chi^2_k
\]

The Beta and Gamma distributions are also related through the ratio of two independent Gamma random variables with a common scale.

The Poisson and Gamma distributions are connected through event-count and waiting-time models in Poisson processes.

These relationships explain why the same special functions and sampling techniques appear in multiple implementations.

## 11. Validation and Failure Handling

The source files validate important mathematical constraints.

| Validation | Expected behavior |
|---|---|
| Negative Poisson rate | Reject |
| Zero Gamma shape | Reject |
| Negative Gamma scale | Reject |
| Zero Beta alpha | Reject |
| Negative Beta beta | Reject |
| Zero degrees of freedom | Reject |
| Negative Poisson count | PMF and CDF return zero |
| Negative continuous support | PDF returns zero |
| Beta CDF at zero | Return zero |
| Beta CDF at one | Return one |
| Invalid significance level | Reject |
| Negative observed frequency | Reject |
| Expected frequency below five | Reject |
| Mismatched frequency totals | Reject |
| Numerical non-convergence | Raise an error |

Boundary behavior is explicitly handled because probability densities can approach zero or infinity at distribution boundaries.

A density of infinity at a single point does not imply that the probability of that individual point is positive.

## 12. Performance Considerations

The numerical methods are designed to avoid unnecessary expensive operations.

| Operation | Typical computational behavior |
|---|---|
| Log-gamma approximation | Constant number of arithmetic operations |
| Gamma CDF | Iterative series or continued fraction |
| Beta CDF | Iterative continued fraction |
| Poisson PMF | Constant number of special-function operations |
| Goodness-of-fit calculation | \(O(n)\) |
| Simulation | \(O(N)\) |
| Simulation storage | \(O(N)\) for retained observations |

The simulation implementations retain observations to calculate empirical statistics.

For large-scale production simulations, online aggregation can reduce memory usage to \(O(1)\) for mean and variance calculations, excluding any additional quantile or histogram structures.

Database indexes improve retrieval performance but increase storage and write overhead.

## 13. Security and Production Considerations

Statistical calculations can affect business decisions, operational planning, and scientific conclusions.

Production systems should consider the following controls:

- Validate all externally supplied distribution parameters.
- Reject NaN and infinite values where unsupported.
- Apply upper bounds to computationally expensive inputs.
- Protect stored experiment observations through database access controls.
- Use parameterized SQL when accepting external input.
- Maintain experiment identifiers and execution timestamps.
- Preserve random seeds for reproducible experiments.
- Record the distribution parameterization used in each experiment.
- Document significance levels and degrees-of-freedom assumptions.
- Avoid treating a non-significant result as proof that the null hypothesis is true.
- Validate numerical routines against trusted reference calculations before operational deployment.

The database schema provides structural integrity, but production authorization, role management, and audit policies must be configured separately.

## 14. Execution

| File | Execution |
|---|---|
| Python | `python advanced_distributions.py` |
| JavaScript | `node advanced_distributions.js` |
| C++17 | `g++ -std=c++17 -O2 advanced_distributions.cpp -o advanced_distributions` followed by `./advanced_distributions` |
| Java 17 | `javac AdvancedDistributions.java` followed by `java AdvancedDistributions` |
| PostgreSQL | Execute the SQL script using a PostgreSQL client connected to the target database |

The Python, JavaScript, C++17, and Java 17 implementations require no third-party packages.

The PostgreSQL implementation requires a database account with permission to create schemas, tables, functions, procedures, triggers, and views.
