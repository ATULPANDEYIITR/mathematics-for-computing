# Law of Large Numbers: Weak Law, Strong Law, and Simulation

## 1. Mathematical Foundation

The Law of Large Numbers (LLN) describes the behavior of sample averages as the number of observations increases.

Let \(X_1, X_2, \ldots, X_n\) be random variables with a common population mean \(\mu\).

The sample mean is:

\[
\overline{X}_n =
\frac{1}{n}\sum_{i=1}^{n}X_i
\]

The central result is that, under suitable assumptions, the sample mean approaches the population mean as the sample size increases.

\[
\overline{X}_n \rightarrow \mu
\]

The LLN provides the mathematical basis for estimating population characteristics using observed data.

Examples include:

- Estimating the probability of a successful transaction.
- Measuring average customer expenditure.
- Estimating average processing time.
- Calculating defect rates in manufacturing.
- Estimating average insurance claims.
- Evaluating Monte Carlo simulation results.
- Measuring empirical probabilities in scientific experiments.

The LLN concerns convergence of averages. It does not state that individual observations become closer to the population mean.

## 2. Weak Law of Large Numbers

The Weak Law of Large Numbers (WLLN) states that the sample mean converges to the population mean in probability.

For every \(\epsilon > 0\):

\[
\lim_{n\rightarrow\infty}
P\left(
|\overline{X}_n-\mu|\geq\epsilon
\right)=0
\]

This means that the probability of a sample mean deviating from the population mean by a fixed positive amount approaches zero as the sample size increases.

### 2.1 Interpretation

Consider repeated experiments involving a fair coin.

Define:

\[
X_i =
\begin{cases}
1 & \text{if the result is heads}\\
0 & \text{if the result is tails}
\end{cases}
\]

For a fair coin:

\[
E[X_i]=0.5
\]

\[
Var(X_i)=0.25
\]

The sample mean represents the observed proportion of heads.

\[
\overline{X}_n =
\frac{\text{Number of heads}}{n}
\]

As the number of independent tosses increases, the probability that the observed proportion differs substantially from 0.5 decreases.

This does not mean every experiment produces a monotonically improving sequence of sample means.

A sample mean can move away from the population mean when additional observations are introduced.

### 2.2 Chebyshev's Inequality

A common mathematical route to establishing the WLLN uses Chebyshev's inequality.

For a random variable with finite variance:

\[
P(|X-\mu|\geq\epsilon)
\leq
\frac{Var(X)}{\epsilon^2}
\]

For independent observations with common mean \(\mu\) and variance \(\sigma^2\):

\[
Var(\overline{X}_n)=\frac{\sigma^2}{n}
\]

Therefore:

\[
P(|\overline{X}_n-\mu|\geq\epsilon)
\leq
\frac{\sigma^2}{n\epsilon^2}
\]

The upper bound approaches zero as \(n\) increases.

This establishes convergence in probability under the independent, common-mean, finite-variance assumptions used here.

Chebyshev's inequality provides an upper bound, not an exact probability.

The empirical probability obtained from simulation may be substantially smaller than the bound.

## 3. Strong Law of Large Numbers

The Strong Law of Large Numbers (SLLN) states that the sample mean converges to the population mean almost surely under appropriate assumptions.

For an independent and identically distributed sequence with finite expected absolute value:

\[
E[|X_1|]<\infty
\]

the strong law gives:

\[
P\left(
\lim_{n\rightarrow\infty}
\overline{X}_n=\mu
\right)=1
\]

Almost-sure convergence means that the probability of the sample-mean sequence failing to converge to the population mean is zero.

It does not mean that every mathematically possible sequence converges.

### 3.1 Interpretation

The strong law focuses on one indefinitely growing sequence of observations.

For example:

- Generate one sequence of coin tosses.
- Calculate the mean after each observation.
- Record the running mean at selected sample sizes.
- Examine its relationship with the theoretical probability.

The resulting sequence illustrates convergence.

A finite simulation cannot establish the SLLN itself. The theorem is a mathematical statement about an infinite sequence.

### 3.2 Running Mean

The running mean can be updated recursively.

\[
\overline{X}_n =
\overline{X}_{n-1}
+
\frac{X_n-\overline{X}_{n-1}}{n}
\]

This update avoids recalculating the sum of all previous observations.

It requires constant additional memory and constant time per observation.

## 4. Weak Law and Strong Law: Key Differences

| Property | Weak Law | Strong Law |
|---|---|---|
| Convergence | In probability | Almost surely |
| Main object | Probability of deviation | Infinite sample-mean sequence |
| Interpretation | Large samples become increasingly reliable in probability | A typical infinite realization converges |
| Typical analysis | Repeated independent experiments | One growing observation sequence |
| Simulation | Repeated Monte Carlo trials | Running averages |
| Mathematical strength | Weaker convergence statement | Stronger convergence statement |
| Relationship | SLLN implies WLLN under standard probability assumptions | WLLN does not generally imply SLLN |

The two laws describe related but different forms of convergence.

They should not be treated as interchangeable.

## 5. Convergence Concepts

### 5.1 Convergence in Probability

A sequence of random variables \(Y_n\) converges in probability to \(Y\) if:

\[
\forall\epsilon>0,\quad
P(|Y_n-Y|\geq\epsilon)\rightarrow0
\]

For the LLN, \(Y_n\) represents the sample mean and \(Y\) represents the population mean.

### 5.2 Almost-Sure Convergence

A sequence \(Y_n\) converges almost surely to \(Y\) when:

\[
P\left(
\lim_{n\rightarrow\infty}Y_n=Y
\right)=1
\]

The convergence is evaluated along the sequence of observations rather than through a probability calculation at each fixed sample size.

### 5.3 Important Distinction

The following statements are not equivalent:

- Most sufficiently large samples have means close to the population mean.
- A single infinite sequence of sample means converges to the population mean with probability one.

The first describes convergence in probability. The second describes almost-sure convergence.

## 6. Simulation Methodology

The implementations use Monte Carlo experiments to examine the mathematical behavior of sample means.

Three distributions are included.

| Distribution | Population Mean | Population Variance |
|---|---:|---:|
| Bernoulli(0.5) | 0.5 | 0.25 |
| Uniform(0,1) | 0.5 | 1/12 |
| Normal(0,1) | 0 | 1 |
| Constant(7) | 7 | 0 |

### 6.1 Bernoulli Distribution

A Bernoulli random variable takes one of two values:

\[
X =
\begin{cases}
1 & \text{with probability }p\\
0 & \text{with probability }1-p
\end{cases}
\]

Its mean and variance are:

\[
E[X]=p
\]

\[
Var(X)=p(1-p)
\]

The implementation uses \(p=0.5\).

### 6.2 Uniform Distribution

A continuous uniform random variable on \([0,1]\) has:

\[
E[X]=\frac{1}{2}
\]

\[
Var(X)=\frac{1}{12}
\]

It provides a continuous distribution for comparing convergence behavior.

### 6.3 Normal Distribution

A standard normal random variable has:

\[
E[X]=0
\]

\[
Var(X)=1
\]

The simulation uses a standard normal random-number generator.

### 6.4 Constant Distribution

A constant random variable always takes the same value.

For \(X=7\):

\[
E[X]=7
\]

\[
Var(X)=0
\]

Every sample mean is exactly 7.

This is an important edge case because the sample mean has no statistical variation.

## 7. Monte Carlo Experiment Design

The WLLN experiment uses multiple independent trials at each sample size.

The default sample sizes are:

\[
n\in\{10,50,100,500,1000,5000,10000\}
\]

For each sample size:

1. Generate independent observations.
2. Calculate the sample mean.
3. Calculate the absolute deviation from the population mean.
4. Calculate the squared deviation.
5. Determine whether the deviation exceeds the specified tolerance.
6. Repeat the experiment.
7. Estimate the probability of exceeding the tolerance.
8. Compare the empirical probability with the Chebyshev upper bound.

The empirical deviation probability is:

\[
\widehat{P} =
\frac{
\text{Number of experiments exceeding tolerance}
}{
\text{Total experiments}
}
\]

The empirical mean absolute error is:

\[
MAE =
\frac{1}{R}
\sum_{j=1}^{R}
|\overline{X}_{n,j}-\mu|
\]

where \(R\) is the number of repeated experiments.

The empirical mean squared error is:

\[
MSE =
\frac{1}{R}
\sum_{j=1}^{R}
(\overline{X}_{n,j}-\mu)^2
\]

For independent observations with finite variance:

\[
E[(\overline{X}_n-\mu)^2]
=
\frac{\sigma^2}{n}
\]

Thus, the theoretical mean squared error decreases at a rate proportional to \(1/n\).

## 8. Python Implementation

The Python program provides a modular simulation framework.

### 8.1 Domain Modeling

`Distribution` defines supported probability distributions.

`ExperimentConfig` stores:

- Distribution type.
- Sample sizes.
- Number of Monte Carlo trials.
- Deviation tolerance.
- Random seed.

`DistributionSpec` contains the theoretical mean, variance, and sampling function.

Immutable dataclasses prevent accidental modification of experiment configuration.

### 8.2 Weak Law Implementation

`repeated_means()` performs repeated independent experiments.

It records:

- Mean absolute error.
- Empirical mean squared error.
- Observed deviation probability.
- Chebyshev upper bound.

The function returns structured dictionaries suitable for JSON serialization.

### 8.3 Strong Law Implementation

`run_slln_experiment()` generates one growing sequence of observations.

It maintains a cumulative sum and records the sample mean at predefined checkpoints.

This demonstrates the distinction between repeated experiments and a single growing sequence.

### 8.4 Validation and Reporting

The implementation includes:

- Positive sample-size validation.
- Unique and increasing sample-size validation.
- Finite tolerance validation.
- Empty-sample rejection.
- Statistical assertions.
- Deterministic random seeds.
- Atomic JSON report writing.
- Exception handling.

The program creates `lln_results.json`.

## 9. JavaScript Implementation

The JavaScript implementation uses an event-driven simulation architecture.

### 9.1 Random Number Generation

`SeededRandom` implements a deterministic pseudorandom number generator.

The normal distribution uses the Box-Muller transformation.

Given independent uniform random values \(U_1\) and \(U_2\):

\[
Z=
\sqrt{-2\ln U_1}
\cos(2\pi U_2)
\]

This generates a standard normal variate under the idealized uniform-input assumptions.

### 9.2 Event-Driven Experiment Execution

`MonteCarloEngine` extends Node.js `EventEmitter`.

It publishes:

| Event | Meaning |
|---|---|
| `started` | Experiment execution begins |
| `sample-completed` | One sample-size group finishes |
| `completed` | Experiment report is available |
| `failed` | Experiment execution fails |

The event model separates simulation execution from reporting and monitoring.

### 9.3 Online Statistics

`OnlineStatistics` implements Welford's algorithm.

For each observation:

\[
\delta=x_n-\mu_{n-1}
\]

\[
\mu_n=\mu_{n-1}+\frac{\delta}{n}
\]

\[
M_{2,n}=M_{2,n-1}
+\delta(x_n-\mu_n)
\]

The algorithm calculates a running mean and sample variance without storing the complete observation sequence.

This reduces memory consumption for large experiments.

### 9.4 Asynchronous Processing

The engine yields to the Node.js event loop between sample-size groups.

An `AbortController` supports cancellation between groups.

Cancellation does not interrupt an individual synchronous trial loop. A production implementation requiring immediate cancellation would need smaller processing batches or worker threads.

The program writes `lln_results_js.json`.

## 10. C++17 Implementation

The C++ implementation emphasizes explicit statistical domain modeling and efficient numerical processing.

### 10.1 Domain Structures

`DistributionSpec` represents a probability distribution.

`ExperimentConfig` represents simulation parameters.

`Result` stores the measurements for one sample size.

The `DistributionType` enum prevents unsupported distribution identifiers.

### 10.2 Random Number Generation

The implementation uses:

- `std::mt19937_64` for pseudorandom number generation.
- `std::uniform_real_distribution` for uniform values.
- `std::normal_distribution` for Gaussian observations.

A fixed seed supports reproducible experiments within the same implementation and compatible standard-library behavior.

### 10.3 Numerical Processing

`OnlineStatistics` uses Welford's algorithm.

The simulation stores aggregate error measurements rather than every generated observation.

This is particularly useful when the total number of observations becomes large.

### 10.4 Failure Handling

The program validates:

- Sample-size ordering.
- Duplicate sample sizes.
- Positive trial counts.
- Positive finite tolerances.
- Valid statistical observations.

CSV output is first written to a temporary file and then renamed to the final report path.

The generated file is `lln_results_cpp.csv`.

## 11. Java 17 Implementation

The Java implementation models statistical experiments as enterprise-oriented domain objects.

### 11.1 Records and Immutable Configuration

The implementation uses Java records for:

- `DistributionSpec`
- `ExperimentConfig`
- `ExperimentResult`
- `StrongLawObservation`
- `ExperimentReport`

The configuration defensively copies its sample-size list.

This prevents external modifications from changing the experiment after validation.

### 11.2 Experiment Lifecycle

An experiment has four relevant states:

| State | Meaning |
|---|---|
| CREATED | Experiment has been initialized |
| RUNNING | Statistical calculations are in progress |
| COMPLETED | Calculations finished successfully |
| FAILED | Execution terminated with an error |

The transition service rejects invalid state changes.

For example, a completed experiment cannot return to the running state.

### 11.3 Statistical Service

`StatisticalService` separates domain configuration from experiment execution.

It provides:

- Distribution lookup.
- Random sampling.
- Weak-law calculations.
- Strong-law calculations.
- Chebyshev probability bounds.
- Immutable report construction.

The implementation uses an `EnumMap` for distribution lookup.

### 11.4 Report Persistence

`ReportWriter` serializes experiment results into JSON.

It writes to a temporary file before publishing the final report.

The implementation attempts an atomic move and falls back to a regular replacement when the filesystem does not support atomic moves.

The generated report is `lln_results_java.json`.

## 12. PostgreSQL Implementation

The PostgreSQL implementation stores statistical experiment metadata and measured outcomes in relational tables.

### 12.1 Relational Architecture

The database follows this relationship:

    distributions
         |
         v
      experiments
         |
         +--------------------------+
         |                          |
         v                          v
    experiment_sample_sizes   running_observations
         |
         v
    monte_carlo_trials
         |
         v
    weak_law_summary

The strong-law observations are stored independently from repeated weak-law trials.

This separation reflects the different experimental structures of the two convergence demonstrations.

### 12.2 Main Tables

| Table | Responsibility |
|---|---|
| `distributions` | Theoretical distribution parameters |
| `experiments` | Experiment configuration and lifecycle |
| `experiment_sample_sizes` | Configured sample sizes |
| `monte_carlo_trials` | Independent repeated experiments |
| `running_observations` | Sequential observations and running means |

### 12.3 Integrity Constraints

The schema uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Positive-value constraints.
- Finite-value checks.
- JSONB validation.
- Experiment lifecycle triggers.
- Statistical consistency triggers.

The Monte Carlo trigger checks whether the recorded absolute and squared errors correspond to the sample mean and theoretical population mean.

The running-observation trigger validates the relationship between the cumulative sum, observation index, running mean, and theoretical mean.

### 12.4 Experiment Lifecycle

Experiments follow these transitions:

    CREATED
       |
       v
    RUNNING
       |
       +-----------> COMPLETED
       |
       +-----------> FAILED
       |
       +-----------> CANCELLED

Terminal states cannot be reopened through ordinary status updates.

### 12.5 Stored Function

`chebyshev_probability_bound()` calculates:

\[
\min\left(
1,\frac{\sigma^2}{n\epsilon^2}
\right)
\]

It validates the variance, sample size, and tolerance.

### 12.6 Stored Procedure

`create_experiment()` creates an experiment and its associated sample-size records.

The procedure validates its inputs and creates the related records within the caller's transaction.

### 12.7 Reporting Views

`weak_law_summary` aggregates repeated experiments.

`strong_law_summary` retrieves running-mean observations.

These views separate data storage from statistical reporting.

### 12.8 Query Capabilities

The SQL script demonstrates:

- Distribution retrieval.
- Experiment history.
- Weak-law evaluation.
- Strong-law convergence reporting.
- Error aggregation.
- Empirical probability comparisons.
- Trial-count validation.
- Completion eligibility.
- Invalid parameter handling.
- State-transition validation.
- Transaction and savepoint handling.

The included records are deterministic demonstration data rather than outputs from a live random-number simulation.

## 13. Statistical Interpretation and Edge Cases

### 13.1 Increasing Sample Size Does Not Guarantee Monotonic Improvement

The LLN does not require every new observation to reduce the absolute error.

For example:

\[
\overline{X}_{10}=0.50
\]

A subsequent observation can change the running mean to:

\[
\overline{X}_{11}=0.545
\]

The sample mean temporarily moves away from 0.50.

This does not contradict either law.

### 13.2 Finite-Sample Probability

The empirical deviation probability is an estimate based on a finite number of repeated experiments.

It may fluctuate between runs.

A fixed random seed improves reproducibility but does not eliminate Monte Carlo sampling uncertainty.

### 13.3 Chebyshev Bound Is Conservative

The Chebyshev bound is valid under finite-variance assumptions but can be loose.

An observed deviation probability substantially below the bound is not evidence of an implementation error.

### 13.4 Dependence Between Observations

The standard independent-observation derivation uses:

\[
Var(\overline{X}_n)=\frac{\sigma^2}{n}
\]

This relationship does not generally hold for dependent observations.

Correlation can change the effective amount of information in a sample.

### 13.5 Infinite Variance

The finite-variance Chebyshev argument cannot be applied when the population variance is infinite.

Some versions of the WLLN and SLLN have weaker or different assumptions.

The laws must therefore be selected according to the actual distributional properties.

### 13.6 Finite Simulation Versus Mathematical Proof

Simulation provides numerical evidence about convergence behavior.

It cannot establish convergence for an infinite sequence.

A numerical experiment should be interpreted as an illustration of a theorem, not as a replacement for its mathematical proof.

## 14. Performance and Numerical Considerations

| Technique | Benefit |
|---|---|
| Running sums | Avoid repeated summation |
| Welford's algorithm | Stable online variance calculation |
| Fixed random seeds | Reproducibility |
| Aggregate statistics | Reduced memory usage |
| Configurable sample sizes | Controlled computational cost |
| Independent trial loops | Clear Monte Carlo experiment boundaries |
| Indexed relational queries | Efficient reporting |
| Immutable configuration | Consistent experiment parameters |
| Atomic file replacement | Reduced risk of partial reports |

For \(R\) trials and sample size \(n\), the principal simulation cost is:

\[
O(Rn)
\]

For multiple sample sizes \(n_1,\ldots,n_k\), the approximate computational cost is:

\[
O\left(
R\sum_{j=1}^{k}n_j
\right)
\]

The online statistical aggregation requires constant additional memory per aggregate.

The simulation itself still requires computation proportional to the number of generated observations.

## 15. Security and Operational Considerations

The statistical programs do not require external network access.

Their principal operational risks concern configuration, reproducibility, data integrity, and report storage.

Important controls include:

- Validate sample sizes before starting expensive experiments.
- Reject non-finite observations and invalid tolerances.
- Use bounded experiment sizes to prevent excessive resource consumption.
- Keep experiment configuration separate from measured observations.
- Avoid treating a random seed as a security credential.
- Restrict write access to report directories.
- Avoid loading untrusted serialized objects.
- Preserve experiment metadata for reproducibility.
- Validate externally supplied statistical records.
- Use database transactions for related experiment records.
- Distinguish theoretical parameters from empirical measurements.

The pseudorandom generators used here are designed for statistical simulation, not cryptographic security.

## 16. Running the Implementations

### Python

Requirements: Python 3.10 or later.

Run:

`python law_of_large_numbers.py`

Generated report: `lln_results.json`.

### JavaScript

Requirements: Node.js 18 or later.

Run:

`node law_of_large_numbers.js`

Generated report: `lln_results_js.json`.

### C++17

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic law_of_large_numbers.cpp -o lln`

Run:

`./lln`

On Windows:

`lln.exe`

Generated report: `lln_results_cpp.csv`.

### Java 17

Compile:

`javac LawOfLargeNumbers.java`

Run:

`java LawOfLargeNumbers`

Generated report: `lln_results_java.json`.

### PostgreSQL

Execute the SQL script using a PostgreSQL client connected to a database where the executing role has permission to create schemas, tables, functions, procedures, and triggers.

The script creates the `probability` schema and commits the demonstration records and reporting objects.

## 17. Learning Outcomes

The five implementations demonstrate distinct aspects of the Law of Large Numbers:

| Implementation | Primary Focus |
|---|---|
| Python | Mathematical simulation, validation, and structured reporting |
| JavaScript | Event-driven Monte Carlo execution and asynchronous processing |
| C++17 | Numerical computation and efficient statistical aggregation |
| Java 17 | Immutable experiment models and controlled lifecycle transitions |
| PostgreSQL | Relational statistical records, integrity enforcement, and reporting |

The central mathematical distinction remains:

\[
\boxed{
\text{WLLN: Convergence in Probability}
}
\]

\[
\boxed{
\text{SLLN: Almost-Sure Convergence}
}
\]

Both laws explain why sample averages become reliable estimators of population means under their respective mathematical assumptions.
