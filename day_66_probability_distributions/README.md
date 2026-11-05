# Probability Distributions

## Overview

Probability distributions describe the possible outcomes of random experiments and assign probabilities to those outcomes.

This project implements four discrete probability distributions:

1. Bernoulli distribution
2. Binomial distribution
3. Geometric distribution
4. Negative Binomial distribution

The implementations cover probability mass functions, cumulative distribution functions, theoretical moments, random sampling, empirical frequency analysis, parameter validation, and operational probability calculations.

The five source implementations use different engineering approaches:

| Implementation | Primary focus |
|---|---|
| Python | Statistical modeling, reusable classes, simulation, and validation |
| JavaScript | Event-driven simulation and asynchronous reporting |
| C++17 | Efficient statistical computation and reproducible simulation |
| Java 17 | Enterprise distribution services, immutable reports, and policy evaluation |
| PostgreSQL | Relational experiment management, integrity enforcement, and statistical reporting |

## 1. Mathematical Foundations

A discrete random variable takes values from a finite or countably infinite set.

A probability mass function (PMF) defines:

\[
P(X=x)
\]

A valid PMF satisfies:

\[
P(X=x)\geq 0
\]

and

\[
\sum_x P(X=x)=1
\]

The cumulative distribution function (CDF) is:

\[
F(x)=P(X\leq x)
\]

For discrete distributions:

\[
F(x)=\sum_{k\leq x}P(X=k)
\]

The probability of an outcome being at least a threshold \(a\) is:

\[
P(X\geq a)=1-F(a-1)
\]

Two important measures describe the distribution's behavior.

**Expected value:**

\[
E[X]=\sum_x xP(X=x)
\]

**Variance:**

\[
Var(X)=E[(X-E[X])^2]
\]

The standard deviation is:

\[
\sigma=\sqrt{Var(X)}
\]

These measures describe the theoretical behavior of a random variable. They are not necessarily equal to the corresponding measurements obtained from a finite simulation.

---

## 2. Bernoulli Distribution

### Concept

A Bernoulli distribution models one random experiment with exactly two possible outcomes:

- Success: 1
- Failure: 0

The probability of success is \(p\).

The probability of failure is \(1-p\).

### Probability mass function

\[
P(X=x)=p^x(1-p)^{1-x}
\]

where:

\[
x\in\{0,1\}
\]

More explicitly:

\[
P(X=1)=p
\]

\[
P(X=0)=1-p
\]

### Expected value

\[
E[X]=p
\]

### Variance

\[
Var(X)=p(1-p)
\]

### Example: Transaction success

Suppose an online payment has a 95% probability of succeeding.

\[
p=0.95
\]

Therefore:

\[
P(X=1)=0.95
\]

\[
P(X=0)=0.05
\]

The expected value is:

\[
E[X]=0.95
\]

The variance is:

\[
Var(X)=0.95(0.05)=0.0475
\]

### Applications

- Payment success or failure
- Server availability
- Customer response
- Product defect detection
- Binary classification outcomes
- Authentication success or failure

### Implementation

The Python, JavaScript, C++, and Java implementations provide:

- PMF evaluation for outcomes 0 and 1
- CDF calculation
- Random sampling
- Mean and variance calculation
- Invalid outcome handling

The PostgreSQL implementation provides `bernoulli_pmf()` for analytical probability calculations.

---

## 3. Binomial Distribution

### Concept

A binomial distribution counts the number of successes in a fixed number of independent Bernoulli trials.

It requires two parameters:

- \(n\): number of independent trials
- \(p\): probability of success in each trial

The random variable represents the total number of successes.

Its support is:

\[
X\in\{0,1,\ldots,n\}
\]

### Assumptions

A binomial experiment requires:

1. A fixed number of trials.
2. Two possible outcomes per trial.
3. Independent trials.
4. Constant success probability.
5. Successes are counted across all trials.

If these assumptions are not satisfied, the binomial model may be inappropriate.

### Probability mass function

\[
P(X=k)=
\binom{n}{k}p^k(1-p)^{n-k}
\]

where:

\[
\binom{n}{k}=\frac{n!}{k!(n-k)!}
\]

### Expected value

\[
E[X]=np
\]

### Variance

\[
Var(X)=np(1-p)
\]

### Example: Successful payment transactions

Suppose a payment platform processes 20 independent transactions.

Each transaction has a success probability of 0.95.

Parameters:

\[
n=20
\]

\[
p=0.95
\]

The expected number of successful transactions is:

\[
E[X]=20(0.95)=19
\]

The variance is:

\[
Var(X)=20(0.95)(0.05)=0.95
\]

The probability of exactly 18 successful transactions is:

\[
P(X=18)=
\binom{20}{18}(0.95)^{18}(0.05)^2
\]

The probability of at least 18 successful transactions is:

\[
P(X\geq18)=
P(X=18)+P(X=19)+P(X=20)
\]

This is useful for evaluating transaction reliability against operational targets.

### Implementation

The implementations support:

- Binomial coefficient calculation
- PMF evaluation
- CDF calculation
- Sampling through repeated Bernoulli trials
- Theoretical moments
- Probability of achieving at least a specified number of successes

The C++ and PostgreSQL implementations use logarithmic combinations to reduce numerical problems associated with large factorials.

---

## 4. Geometric Distribution

### Concept

A geometric distribution models the number of independent Bernoulli trials required to obtain the first success.

Its parameter is:

\[
p=P(\text{success})
\]

Its support is:

\[
X\in\{1,2,3,\ldots\}
\]

Unlike the Bernoulli distribution, it does not describe only one trial. It describes the waiting time until the first successful trial.

### Probability mass function

\[
P(X=k)=(1-p)^{k-1}p
\]

The first \(k-1\) trials must fail, and trial \(k\) must succeed.

### Cumulative distribution function

\[
F(k)=1-(1-p)^k
\]

for \(k\geq1\).

### Expected value

\[
E[X]=\frac{1}{p}
\]

### Variance

\[
Var(X)=\frac{1-p}{p^2}
\]

### Example: Network connection attempts

Suppose a network connection attempt succeeds with probability 0.25.

The probability that the first attempt succeeds is:

\[
P(X=1)=0.25
\]

The probability that the first success occurs on the third attempt is:

\[
P(X=3)=(0.75)^2(0.25)
\]

\[
P(X=3)=0.140625
\]

The probability of success within five attempts is:

\[
P(X\leq5)=1-(0.75)^5
\]

The expected number of attempts is:

\[
E[X]=\frac{1}{0.25}=4
\]

### Memoryless property

The geometric distribution has an important memoryless property:

\[
P(X>s+t\mid X>s)=P(X>t)
\]

The probability of waiting another \(t\) trials does not depend on how many unsuccessful trials have already occurred.

This property follows from the assumption that each trial is independent and has the same success probability.

### Applications

- Network reconnection attempts
- First successful login
- First successful customer conversion
- Equipment failure detection
- First successful transmission
- Retry-based workflows

### Implementation

The implementations provide:

- PMF and CDF calculations
- Waiting-time sampling
- Theoretical expected waiting time
- Variance and standard deviation
- Boundary handling for probabilities of zero and one

When \(p=0\), no finite first-success waiting time exists. The implementations represent the theoretical moments as infinity and reject attempts to generate a finite waiting-time sample.

---

## 5. Negative Binomial Distribution

### Concept

The negative binomial distribution models the number of independent Bernoulli trials required to obtain a specified number of successes.

It generalizes the geometric distribution.

Its parameters are:

- \(r\): required number of successes
- \(p\): probability of success in each trial

Its support is:

\[
X\in\{r,r+1,r+2,\ldots\}
\]

The geometric distribution is a special case when:

\[
r=1
\]

### Probability mass function

\[
P(X=k)=
\binom{k-1}{r-1}
p^r(1-p)^{k-r}
\]

where:

\[
k\geq r
\]

The coefficient represents the possible arrangements of the first \(r-1\) successes among the first \(k-1\) trials, with the final trial producing the required success.

### Expected value

\[
E[X]=\frac{r}{p}
\]

### Variance

\[
Var(X)=\frac{r(1-p)}{p^2}
\]

### Example: Customer support resolution

Suppose a support team resolves a customer issue on any attempt with probability 0.6.

The organization wants to measure the number of attempts required to obtain five successful resolutions.

Parameters:

\[
r=5
\]

\[
p=0.6
\]

Expected number of attempts:

\[
E[X]=\frac{5}{0.6}=8.3333
\]

Variance:

\[
Var(X)=\frac{5(0.4)}{0.6^2}
\]

\[
Var(X)=5.5556
\]

The probability of completing exactly five successful resolutions in eight attempts is:

\[
P(X=8)=
\binom{7}{4}(0.6)^5(0.4)^3
\]

The probability of completing five successes within eight attempts is:

\[
P(X\leq8)=
\sum_{k=5}^{8}
\binom{k-1}{4}(0.6)^5(0.4)^{k-5}
\]

### Applications

- Number of attempts required for multiple successful connections
- Customer acquisition
- Quality inspection
- Repeated testing
- Support case resolution
- Sales conversion processes

### Implementation

The source files implement:

- Required-success parameter validation
- PMF and CDF
- Trial-based simulation
- Mean and variance calculations
- Minimum support validation
- Probability of achieving a required success count within a specified number of attempts

The negative binomial implementation is distinct from the binomial implementation.

A binomial distribution counts successes within a fixed number of trials.

A negative binomial distribution counts trials required to achieve a fixed number of successes.

---

## 6. Comparison of the Four Distributions

| Property | Bernoulli | Binomial | Geometric | Negative Binomial |
|---|---|---|---|---|
| Main purpose | One binary trial | Count successes | Wait for first success | Wait for r successes |
| Parameters | p | n, p | p | r, p |
| Random variable | Binary outcome | Number of successes | Number of trials | Number of trials |
| Minimum value | 0 | 0 | 1 | r |
| Maximum value | 1 | n | Unbounded | Unbounded |
| Mean | p | np | 1/p | r/p |
| Variance | p(1-p) | np(1-p) | (1-p)/p² | r(1-p)/p² |
| Fixed trials | One | Yes | No | No |
| Fixed successes | No | No | One | r |

### Important relationships

The Bernoulli distribution is the fundamental binary experiment.

The binomial distribution is the sum of independent Bernoulli random variables:

\[
X=\sum_{i=1}^{n}X_i
\]

The geometric distribution describes the waiting time for the first success.

The negative binomial distribution extends this waiting-time model to multiple required successes.

For \(r=1\):

\[
NegativeBinomial(1,p)=Geometric(p)
\]

These relationships provide a consistent framework for selecting an appropriate probability model.

---

## 7. Implementation Architecture

### Python

The Python implementation uses an object-oriented statistical model.

Its primary components are:

| Component | Responsibility |
|---|---|
| `ProbabilityDistribution` | Common distribution interface |
| `BernoulliDistribution` | Binary outcome model |
| `BinomialDistribution` | Fixed-trial success counting |
| `GeometricDistribution` | First-success waiting time |
| `NegativeBinomialDistribution` | Multiple-success waiting time |
| `DistributionStatistics` | Mean, variance, and standard deviation |
| `ProbabilityError` | Invalid parameter and sampling errors |

The implementation also includes:

- Dataclasses for statistical results
- An enum for distribution identification
- Seeded random sampling
- Frequency aggregation using `Counter`
- Maximum-likelihood estimation of Bernoulli probability
- Probability-at-least calculations
- Automated assertions

The empirical Bernoulli estimate is:

\[
\hat p=\frac{\text{Observed successes}}{\text{Total observations}}
\]

This is the maximum-likelihood estimate when the observations are independent Bernoulli trials.

### JavaScript

The JavaScript implementation provides an event-driven simulation architecture.

Important components include:

- `Distribution`: shared statistical behavior
- `RandomGenerator`: reproducible pseudorandom sampling
- Four specialized distribution classes
- `SimulationService`: simulation execution and reporting
- `EventEmitter`: completion notifications

The simulation service emits a `completed` event after a successful simulation.

This separates the calculation process from monitoring and reporting.

The implementation uses asynchronous execution at the service boundary and structured result objects for downstream processing.

Its pseudorandom generator is intended for reproducible simulations, not cryptographic security.

### C++17

The C++ implementation emphasizes computational efficiency and explicit domain modeling.

Its main structures are:

- `ProbabilityError`
- `Statistics`
- `SimulationResult`
- `Distribution`
- Four derived distribution classes

The standard library provides:

- `std::mt19937` for reproducible pseudorandom sequences
- `std::bernoulli_distribution`
- `std::binomial_distribution`
- `std::geometric_distribution`
- `std::negative_binomial_distribution`
- `std::map` for ordered outcome frequencies
- `std::lgamma` for logarithmic factorial calculations

C++ standard-library geometric and negative binomial distributions use their own parameterization conventions.

The implementation explicitly converts the standard library's negative-binomial failure count into the total number of trials:

\[
TotalTrials=RequiredSuccesses+Failures
\]

This preserves the project's total-trials convention.

### Java 17

The Java implementation models probability calculations as an enterprise service.

Its components include:

- `DiscreteDistribution` interface
- `BaseDistribution` abstract class
- Immutable `Statistics` record
- Immutable `SimulationReport` record
- `SimulationStatus` enum
- `SimulationService`
- `OperationalPolicy`
- `PolicyEvaluator`

The simulation service manages the following state transitions:

`CREATED → RUNNING → COMPLETED`

A runtime failure produces:

`RUNNING → FAILED`

The service also uses immutable report objects and sorted frequency maps to provide stable reporting results.

The policy evaluator determines whether a geometric distribution satisfies minimum success probability and maximum expected-attempt requirements.

This separates statistical calculations from operational decision rules.

---

## 8. PostgreSQL Database Design

The PostgreSQL implementation uses the `probability_lab` schema.

It models probability experiments and their observations as relational data.

### Entity relationships

The database contains three main entities.

**Distribution types**

Stores the supported probability models and their descriptions.

**Experiments**

Stores:

- Experiment name
- Distribution type
- Success probability
- Trial count
- Required successes
- Sample size
- Execution status
- Creation and completion timestamps

**Observations**

Stores individual experiment outcomes.

Relationship:

`Distribution Types → Experiments → Observations`

One distribution type can be associated with multiple experiments.

One experiment can contain multiple observations.

### Integrity enforcement

The schema uses:

- Primary keys
- Foreign keys
- Check constraints
- Unique constraints
- Indexes
- Trigger-based validation

The experiment constraints enforce valid probability values and distribution-specific parameters.

The observation trigger enforces the mathematical support of each distribution.

Examples:

| Distribution | Valid outcomes |
|---|---|
| Bernoulli | 0 or 1 |
| Binomial | 0 through n |
| Geometric | 1 or greater |
| Negative Binomial | r or greater |

An observation that violates its distribution's support is rejected.

### Database functions

| Function | Purpose |
|---|---|
| `log_combination()` | Calculates logarithmic binomial coefficients |
| `bernoulli_pmf()` | Calculates Bernoulli probabilities |
| `binomial_pmf()` | Calculates binomial probabilities |
| `geometric_pmf()` | Calculates geometric probabilities |
| `geometric_cdf()` | Calculates geometric cumulative probabilities |
| `negative_binomial_pmf()` | Calculates negative binomial probabilities |
| `negative_binomial_cdf()` | Calculates negative binomial cumulative probabilities |
| `distribution_statistics()` | Calculates theoretical moments |

The functions are marked immutable where their results depend exclusively on their input parameters.

This allows PostgreSQL to treat them as deterministic calculations.

### Transactional observation processing

The `record_observations()` procedure:

1. Locks the relevant experiment row.
2. Checks whether the experiment exists.
3. Rejects finalized experiments.
4. Validates the observation batch size.
5. Changes the experiment status to `RUNNING`.
6. Inserts observations.
7. Relies on the observation trigger to enforce support constraints.

The procedure executes transactionally.

If an invalid outcome causes an exception, the entire procedure call is rolled back.

This prevents partial insertion of an invalid batch.

### Reporting

The database includes two reporting views.

`empirical_distribution_report` calculates:

- Number of observations
- Empirical mean
- Empirical variance
- Standard deviation
- Minimum outcome
- Maximum outcome

`outcome_frequency_report` calculates:

- Outcome frequencies
- Empirical probabilities
- Experiment-level frequency distributions

The reporting queries compare theoretical and empirical moments.

This supports model validation and operational reporting.

---

## 9. Theoretical and Empirical Probability

Theoretical probabilities are calculated from distribution parameters.

Empirical probabilities are calculated from observed frequencies.

For an outcome \(x\):

\[
\hat P(X=x)=\frac{Frequency(x)}{N}
\]

where \(N\) is the number of observations.

For example, if 920 out of 1,000 transactions succeed:

\[
\hat p=\frac{920}{1000}=0.92
\]

If the theoretical success probability is 0.95, the difference is:

\[
0.92-0.95=-0.03
\]

This difference does not automatically establish that the probability model is incorrect.

Possible explanations include:

- Random sampling variation
- Changes in operating conditions
- Dependence between observations
- Incorrect model assumptions
- Incorrect parameter estimates
- Data collection errors

A larger sample generally provides a more stable empirical estimate, provided the underlying assumptions remain valid.

---

## 10. Numerical Stability and Performance

Probability calculations can become numerically difficult when trial counts or required success counts become large.

### Factorial growth

The binomial coefficient contains factorials:

\[
\binom{n}{k}=\frac{n!}{k!(n-k)!}
\]

Direct factorial calculations can exceed the available numerical range.

The C++ and PostgreSQL implementations use logarithmic factorial calculations.

The identity is:

\[
\ln\binom{n}{k}
=
\ln(n!)
-\ln(k!)
-\ln((n-k)!)
\]

The resulting probability is obtained by exponentiating the logarithmic expression.

### Complexity

Let:

- \(n\) represent the number of binomial trials.
- \(r\) represent required negative binomial successes.
- \(N\) represent simulation sample size.
- \(K\) represent the number of evaluated outcomes.

| Operation | Time complexity |
|---|---|
| Bernoulli PMF | O(1) |
| Bernoulli sampling | O(1) |
| Binomial PMF with direct coefficient calculation | O(min(k,n-k)) |
| Binomial sampling | O(n) per sample |
| Geometric sampling | Expected O(1/p) trial operations |
| Negative binomial sampling | Expected O(r/p) trial operations |
| Simulation | O(N × cost per sample) |
| Frequency aggregation | O(N log K) with ordered maps |

### Numerical limitations

The implementations use floating-point arithmetic.

Very small probabilities can underflow to zero.

Very large support values can cause overflow or loss of precision in factorial and combinatorial calculations.

The provided implementations are appropriate for educational and moderate-scale statistical workflows. Large-scale statistical applications may require specialized numerical libraries and more stable CDF algorithms.

---

## 11. Edge Cases and Failure Handling

Probability distributions have important boundary conditions.

| Condition | Expected behavior |
|---|---|
| p = 0 | Success is impossible |
| p = 1 | Every trial succeeds |
| Negative n | Invalid binomial parameters |
| Negative r | Invalid negative binomial parameters |
| r = 0 | Invalid under the implemented negative binomial definition |
| Binomial outcome below 0 | Probability equals zero |
| Binomial outcome above n | Probability equals zero |
| Geometric outcome below 1 | Probability equals zero |
| Negative binomial outcome below r | Probability equals zero |
| Empty empirical dataset | Estimation rejected |
| Empty observation batch | Database procedure rejected |
| Observation after experiment completion | Database trigger or procedure rejects the operation |

When \(p=0\), the geometric and negative binomial distributions have no finite waiting time.

Their theoretical means and variances are infinite.

When \(p=1\), the geometric distribution always returns one trial, while the negative binomial distribution always returns exactly \(r\) trials.

---

## 12. Statistical Validation

The implementations include tests for representative probability calculations.

| Test | Expected result |
|---|---:|
| Bernoulli PMF, p = 0.3, x = 1 | 0.3 |
| Bernoulli PMF, p = 0.3, x = 0 | 0.7 |
| Binomial PMF, n = 5, p = 0.5, k = 2 | 0.3125 |
| Geometric PMF, p = 0.25, k = 1 | 0.25 |
| Geometric CDF, p = 0.25, k = 2 | 0.4375 |
| Negative Binomial PMF, r = 3, p = 0.5, k = 4 | 0.1875 |
| Negative Binomial CDF, r = 3, p = 0.5, k = 4 | 0.3125 |

A valid PMF must satisfy the normalization condition:

\[
\sum_x P(X=x)=1
\]

For an infinite-support distribution, the complete probability sum is taken over all possible outcomes.

A finite range of PMF values may sum to less than one because probability remains outside that range.

Simulation validation compares empirical statistics against theoretical statistics.

The comparison should account for sampling variation rather than expecting exact equality.

---

## 13. Security and Production Considerations

Probability calculations can support operational decisions, but their inputs and assumptions must be controlled.

Important production controls include:

- Validate all external parameters.
- Reject probabilities outside the interval [0, 1].
- Restrict database access according to user roles.
- Avoid accepting untrusted SQL expressions.
- Use parameterized queries in application integrations.
- Preserve experiment configuration and execution timestamps.
- Keep raw observations separate from derived statistics.
- Use reproducible seeds for controlled testing.
- Avoid using ordinary pseudorandom generators for cryptographic applications.
- Monitor unexpected changes in empirical probabilities.
- Document independence and constant-probability assumptions.
- Apply appropriate access controls to business observations.

A statistical model should not be treated as a guarantee of future operational performance.

The validity of its results depends on the quality of the data and the suitability of its assumptions.

---

## 14. Execution

### Python

Requirements: Python 3.10 or later.

Save the implementation as `probability_distributions.py`.

Execute:

`python probability_distributions.py`

No third-party packages are required.

### JavaScript

Requirements: Node.js 18 or later.

Save the implementation as `probability_distributions.js`.

Execute:

`node probability_distributions.js`

No npm packages are required.

### C++17

Save the implementation as `probability_distributions.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic probability_distributions.cpp -o probability_distributions`

Execute:

`./probability_distributions`

### Java 17

Save the implementation as `ProbabilityDistributionApp.java`.

Compile:

`javac ProbabilityDistributionApp.java`

Execute:

`java ProbabilityDistributionApp`

### PostgreSQL

Requirements: PostgreSQL 15 or later.

Execute the complete SQL script using a PostgreSQL client connected to the intended database.

The script creates the `probability_lab` schema, its tables, statistical functions, triggers, procedure, views, and sample experiment data.

The analytical queries can be executed after the schema has been initialized.

The database role requires permission to create schemas, tables, functions, procedures, and triggers.

---

## 15. Practical Model Selection

Selecting a probability distribution depends on what the random variable measures.

| Business question | Appropriate distribution |
|---|---|
| Will one payment succeed? | Bernoulli |
| How many payments succeed among 100 transactions? | Binomial |
| How many attempts until the first successful connection? | Geometric |
| How many attempts until five successful connections? | Negative Binomial |

The distinction is based on the structure of the experiment:

- Bernoulli models one binary trial.
- Binomial models successes across a fixed number of trials.
- Geometric models waiting time until the first success.
- Negative Binomial models waiting time until a specified number of successes.

All four models rely on Bernoulli success and failure outcomes, but they answer different statistical questions.
