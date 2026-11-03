# Random Variables: Discrete and Continuous Probability Models

## 1. Domain and scope

A random variable is a numerical function that assigns a value to each possible outcome of a random experiment. It provides a mathematical way to represent uncertainty and describe the likelihood of different numerical outcomes.

This project implements two principal categories:

- **Discrete random variables:** variables whose possible values form a finite or countable set.
- **Continuous random variables:** variables whose possible values occupy an interval or collection of intervals on the real number line.

The five implementations use probability distributions to model operational failures, API response times, and sensor measurement errors.

The project distinguishes theoretical probability models from empirical observations. Theoretical distributions describe the assumed behavior of a random variable. Empirical statistics describe values collected through observation or simulation.

## 2. Discrete random variables

A discrete random variable has a set of distinct possible outcomes called its support.

For example, consider four independent service requests. Each request has a probability of 0.10 of failing.

Let \(X\) represent the number of failed requests.

The possible values are:

\[
X \in \{0,1,2,3,4\}
\]

The probability mass function assigns a probability to each supported value:

\[
p_X(x)=P(X=x)
\]

A PMF must satisfy two conditions:

\[
p_X(x)\geq 0
\]

\[
\sum_{x\in S}p_X(x)=1
\]

where \(S\) is the support of the random variable.

For the four-request example, the probabilities are:

| Failed requests | Probability |
|---:|---:|
| 0 | 0.6561 |
| 1 | 0.2916 |
| 2 | 0.0486 |
| 3 | 0.0036 |
| 4 | 0.0001 |

The distribution is binomial because it represents the number of successes in a fixed number of independent Bernoulli trials. Here, a failure is treated as the event being counted.

For a binomial random variable:

\[
P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}
\]

where:

- \(n\) is the number of trials.
- \(k\) is the number of counted events.
- \(p\) is the probability of the counted event.
- \(1-p\) is the probability of the alternative outcome.

The expectation and variance are:

\[
E[X]=np
\]

\[
Var(X)=np(1-p)
\]

For four requests with a failure probability of 0.10:

\[
E[X]=4(0.10)=0.4
\]

\[
Var(X)=4(0.10)(0.90)=0.36
\]

The expectation is a long-run average, not a prediction that exactly 0.4 failures will occur in one group of four requests.

### Implementation decisions

The Python and JavaScript implementations use dictionaries and maps to associate each support value with its probability. The C++ and Java implementations use sorted collections of outcome-probability pairs.

The implementations verify that:
- Support values are numeric and finite.
- Probabilities are finite and lie between zero and one.
- Each support value occurs only once.
- The probability total is equal to one within a defined floating-point tolerance.

Zero-probability outcomes are permitted. They do not contribute to expectation, variance, or sampling.

The cumulative probabilities are precomputed. This allows PMF and CDF calculations to avoid repeatedly scanning the entire support.

## 3. Continuous random variables

A continuous random variable can take values throughout a continuous interval.

The API response-time model represents a continuous variable \(Y\), measured in milliseconds.

A normal distribution is used with:

\[
Y\sim N(120,25^2)
\]

Here, 120 is the mean and 25 is the standard deviation.

The probability density function is:

\[
f_Y(y)=
\frac{1}{\sigma\sqrt{2\pi}}
e^{-\frac{(y-\mu)^2}{2\sigma^2}}
\]

where:

- \(\mu\) is the mean.
- \(\sigma\) is the standard deviation.
- \(\sigma^2\) is the variance.

The PDF describes the density of probability near a point. It does not provide the probability of observing exactly that value.

For a continuous random variable:

\[
P(Y=y)=0
\]

for an individual point \(y\).

Probabilities are calculated over intervals:

\[
P(a\leq Y\leq b)=\int_a^b f_Y(y)\,dy
\]

The total area under a valid probability density function is one:

\[
\int_{-\infty}^{\infty}f_Y(y)\,dy=1
\]

### Normal distribution properties

For a normal random variable:

\[
E[Y]=\mu
\]

\[
Var(Y)=\sigma^2
\]

The Python implementation uses the standard-library error function to calculate the normal CDF. C++, JavaScript, Java, and PostgreSQL use numerical approximations or standard mathematical functions appropriate to their runtime.

The continuous model calculates:

- Density at 150 milliseconds.
- Cumulative probability at 150 milliseconds.
- Probability of response time exceeding 180 milliseconds.

The upper-tail probability is obtained from the CDF:

\[
P(Y>180)=1-F_Y(180)
\]

### Uniform distribution

The sensor-error example uses a continuous uniform distribution:

\[
Z\sim U(-2,2)
\]

Every interval of equal length inside the bounds has the same probability.

Its PDF is:

\[
f_Z(z)=
\begin{cases}
\frac{1}{b-a}, & a\leq z\leq b\\
0, & \text{otherwise}
\end{cases}
\]

Its CDF is:

\[
F_Z(z)=
\begin{cases}
0, & z<a\\
\frac{z-a}{b-a}, & a\leq z<b\\
1, & z\geq b
\end{cases}
\]

Its expectation and variance are:

\[
E[Z]=\frac{a+b}{2}
\]

\[
Var(Z)=\frac{(b-a)^2}{12}
\]

For the interval \([-2,2]\):

\[
E[Z]=0
\]

\[
Var(Z)=\frac{16}{12}=\frac{4}{3}
\]

The probability of an error between -1 and 1 is:

\[
P(-1\leq Z\leq1)=F_Z(1)-F_Z(-1)=0.5
\]

## 4. Cumulative distribution function

The cumulative distribution function is applicable to both discrete and continuous random variables.

It is defined as:

\[
F_X(x)=P(X\leq x)
\]

The CDF is non-decreasing and satisfies:

\[
\lim_{x\rightarrow-\infty}F_X(x)=0
\]

\[
\lim_{x\rightarrow\infty}F_X(x)=1
\]

For a discrete variable, the CDF adds probability masses up to the requested value:

\[
F_X(x)=\sum_{t\leq x}P(X=t)
\]

It is a step function because probability is concentrated at individual support values.

For a continuous variable, the CDF is the accumulated area under the PDF:

\[
F_X(x)=\int_{-\infty}^{x}f_X(t)\,dt
\]

It is continuous for the normal and uniform distributions implemented in this project.

| Property | Discrete variable | Continuous variable |
|---|---|---|
| Probability function | PMF | PDF |
| Individual value probability | Can be positive | Zero |
| CDF | Sum of probability masses | Integral of density |
| Typical support | Integers or countable values | Real-valued intervals |
| Probability of an interval | Sum of relevant masses | Area under the PDF |

The CDF also provides probabilities for intervals and upper-tail events:

\[
P(a<X\leq b)=F_X(b)-F_X(a)
\]

\[
P(X>x)=1-F_X(x)
\]

For discrete variables, interval endpoints must be interpreted carefully. The difference \(F_X(b)-F_X(a)\) corresponds to \(P(a<X\leq b)\), not necessarily \(P(a\leq X\leq b)\).

## 5. Expectation and variance

Expectation describes the probability-weighted long-run average of a random variable.

For a discrete variable:

\[
E[X]=\sum_x xp_X(x)
\]

For a continuous variable:

\[
E[X]=\int_{-\infty}^{\infty}xf_X(x)\,dx
\]

Variance measures dispersion around the expectation:

\[
Var(X)=E[(X-E[X])^2]
\]

An equivalent expression is:

\[
Var(X)=E[X^2]-E[X]^2
\]

The implementations compute theoretical expectation and variance directly from their probability models.

Empirical mean and variance are calculated separately from collected observations. They may differ from theoretical values because a finite sample does not reproduce the exact distribution.

## 6. Monte Carlo sampling

Monte Carlo simulation estimates probabilities by repeatedly generating observations from a probability distribution.

For an event \(A\), the estimate is:

\[
\hat{P}(A)=\frac{m}{N}
\]

where:

- \(N\) is the number of generated observations.
- \(m\) is the number of observations satisfying the event.

For the operational example, the discrete simulation estimates:

\[
P(X\geq2)
\]

The continuous simulation estimates:

\[
P(Y>180)
\]

The standard error of a Monte Carlo probability estimate is approximated by:

\[
SE(\hat{p})=
\sqrt{\frac{\hat{p}(1-\hat{p})}{N}}
\]

Increasing the sample count generally reduces sampling error. The improvement is proportional to the inverse square root of the sample count, so reducing standard error by approximately half requires roughly four times as many observations.

Monte Carlo estimates are empirical approximations. They are not replacements for an exact PMF, PDF, or CDF when an analytical distribution is available.

## 7. Python implementation

The Python script defines a common `RandomVariable` abstraction and separate discrete and continuous implementations.

### Discrete model

`DiscreteRandomVariable` stores:
- A sorted support.
- A PMF dictionary.
- Cumulative probabilities.
- Theoretical mean and variance.

`pmf(x)` returns the probability associated with an exact support value. Unsupported values return zero.

`cdf(x)` uses binary search over the sorted support and precomputed cumulative probabilities.

Sampling uses the inverse cumulative probability method.

### Continuous models

`ContinuousRandomVariable` defines the PDF interface.

`NormalRandomVariable` implements a normal PDF, CDF, and sampling method. The CDF uses `math.erf`.

`UniformRandomVariable` calculates the constant density inside its interval and implements the piecewise CDF.

### Simulation and testing

`binomial_distribution()` builds a binomial PMF using the combination formula.

`estimate_probability()` executes Monte Carlo sampling and returns an immutable `MonteCarloEstimate` containing the estimate, success count, sample count, and standard error.

`RunningStatistics` uses Welford's algorithm. It maintains a running mean and variance without retaining every observation.

`validate_implementations()` tests mathematical properties and confirms that invalid probability totals and invalid normal parameters are rejected.

Run the script with:

- `python random_variables.py`
- `python random_variables.py --samples 100000`
- `python random_variables.py --samples 100000 --seed 42`

The seed supports reproducible debugging and comparison between runs.

## 8. JavaScript implementation

The JavaScript implementation emphasizes event-driven processing rather than simply reproducing the Python structure.

### Distribution objects

`DiscreteDistribution` validates outcome records and builds an immutable outcome list, a `Map` for PMF access, and a cumulative probability array.

`NormalDistribution` implements PDF, CDF, and Box-Muller sampling.

`UniformDistribution` calculates interval probabilities and produces bounded observations.

The binomial factory uses a recurrence to calculate consecutive binomial probabilities without repeatedly evaluating factorials.

### Event-driven monitoring

`EventBus` separates observation generation from observation processing.

A producer publishes an observation event containing a variable name and a numerical value.

`ProbabilityMonitor` subscribes to those events and updates its own `OnlineStatistics` instance.

The unsubscribe function removes a listener when monitoring ends. The `finally` block ensures that the example releases its subscriptions even if sampling fails.

`sampleStream()` is an asynchronous generator. It allows callers to consume samples incrementally without constructing a large array of all observations.

### Numerical and operational controls

The JavaScript implementation:
- Rejects non-finite distribution parameters.
- Rejects invalid probabilities.
- Verifies random-source output is within the interval \([0,1)\).
- Rejects unreasonable sample counts.
- Uses a deterministic seeded generator for repeatable experiments.
- Uses online statistics to control memory consumption.

The seeded generator is intended for simulation. It is not a cryptographic random-number generator.

Run the file using:

- `node random_variables.js`
- `node random_variables.js 50000`

## 9. C++17 implementation

The C++ program uses virtual interfaces and STL containers to model probability distributions.

`RandomVariable` defines the common operations:

- `mean()`
- `variance()`
- `cdf()`
- `sample()`

`DiscreteRandomVariable` stores sorted support values, probability masses, and cumulative probabilities in vectors.

`ContinuousRandomVariable` extends the common abstraction with `pdf()`.

`NormalRandomVariable` uses the standard mathematical error function through `erfc` to calculate the normal CDF.

`UniformRandomVariable` implements bounded continuous density and cumulative probability.

### Sampling and statistics

The binomial factory calculates its PMF through a recurrence relation. This avoids repeatedly computing large factorials.

Discrete sampling uses a uniform draw and binary search over cumulative probabilities.

The generic Monte Carlo function accepts a distribution and an event predicate. It can estimate probabilities for different event definitions without changing the distribution classes.

`OnlineStatistics` uses Welford's algorithm to calculate sample statistics in constant memory.

### Performance characteristics

For a discrete support containing \(k\) values:

| Operation | Complexity |
|---|---:|
| Distribution construction | \(O(k\log k)\) |
| PMF lookup | \(O(\log k)\) |
| CDF lookup | \(O(\log k)\) |
| Sampling after construction | \(O(\log k)\) |
| Mean and variance calculation | \(O(k)\) |

A Monte Carlo run with \(N\) samples takes \(O(N\log k)\) time for this discrete sampler.

Continuous normal and uniform sampling use the standard-library random distributions.

Compile and run using:

- `g++ -std=c++17 -O2 -Wall -Wextra -pedantic random_variables.cpp -o random_variables`
- `./random_variables`
- `./random_variables 50000`

The program uses `std::mt19937_64` with a fixed seed for reproducibility. It is not suitable for cryptographic randomness.

## 10. Java 17 enterprise implementation

The Java implementation models probability calculations as part of an enterprise risk-assessment workflow.

### Domain interfaces

`RandomVariable` defines shared behavior.

`DiscreteVariable` adds the PMF operation.

`ContinuousVariable` adds the PDF operation.

This design preserves the distinction between probability mass and probability density rather than presenting them as interchangeable methods.

`Outcome` is a record representing one discrete support value and its probability.

Distribution objects use immutable collections to prevent accidental modification of the probability model after validation.

### Probability policies

The enterprise example evaluates the probability of excessive request failures.

The event is:

\[
P(X>1)
\]

Two active policies impose different maximum acceptable probabilities:

| Policy | Maximum probability |
|---|---:|
| Operations limit | 10% |
| Critical service limit | 7.5% |

Every active policy is evaluated independently. The overall assessment is rejected when at least one active policy fails.

This illustrates the difference between a probability calculation and a business decision. The distribution calculates the probability; policy objects specify what probability is acceptable.

`RiskEvaluation` records the modeled probability, threshold, individual policy results, final decision, and evaluation time.

Inactive policies do not participate. An assessment without an active policy is rejected by the service with an explicit exception.

### State and validation controls

The service rejects missing variable names, missing distributions, non-finite thresholds, duplicate active policy identifiers, and invalid policy probability limits.

The distribution and policy records are immutable after construction.

The example also evaluates a normal latency distribution against a service-level probability threshold.

Compile and run using:

- `javac Main.java`
- `java Main`

Assertions can be enabled with `java -ea Main`.

## 11. PostgreSQL relational model

The SQL implementation represents probability distributions as relational data rather than as in-memory objects.

The schema is `random_variable_lab`.

### Entity relationships

The principal relationship is:

`random_variables`
- `discrete_outcomes`
- `continuous_parameters`
- `observations`

A random variable has one type: discrete or continuous.

A discrete variable has multiple support values and associated probabilities.

A continuous variable has a parameter record identifying its distribution family and parameters.

Observations reference the variable from which they were obtained.

### Table design

| Table | Purpose |
|---|---|
| `random_variables` | Distribution identity, description, and type |
| `discrete_outcomes` | Discrete support and probability masses |
| `continuous_parameters` | Normal or uniform parameters |
| `observations` | Collected sample values |

Primary keys and foreign keys protect relationships between the records.

The `discrete_outcomes` table uses a composite primary key consisting of the distribution ID and support value. This prevents duplicate support values within one distribution.

Check constraints validate probability ranges and distribution parameters.

A continuous normal distribution requires a positive standard deviation. A uniform distribution requires an upper bound greater than its lower bound.

### Deferred probability validation

A PMF can contain several rows, so checking its total after each inserted row would reject an otherwise valid multi-row transaction.

The SQL script uses a deferred constraint trigger.

The trigger checks the complete PMF when the transaction is committed:

\[
\sum_xP(X=x)=1
\]

This ensures that a completed transaction cannot leave an invalid probability total.

A separate trigger verifies that discrete outcomes belong to discrete variables and continuous parameters belong to continuous variables.

### Observation integrity

The observation trigger checks that a discrete observation belongs to the variable's support.

For example, `failed_requests` supports only:

\[
\{0,1,2,3,4\}
\]

An observation with value 9 is rejected.

Continuous observations are checked for the existence of corresponding continuous parameters. They are not restricted to a finite support because their distributions are defined over continuous domains.

### Database functions

| Function | Purpose |
|---|---|
| `probability_mass_function` | Retrieve a discrete probability mass |
| `discrete_cdf` | Calculate a discrete cumulative probability |
| `normal_pdf` | Calculate normal density |
| `uniform_pdf` | Calculate uniform density |
| `normal_cdf` | Approximate the normal cumulative probability |
| `uniform_cdf` | Calculate uniform cumulative probability |
| `probability_density_function` | Dispatch to the appropriate continuous PDF |
| `cumulative_distribution_function` | Dispatch to the applicable CDF |
| `expected_value` | Calculate theoretical expectation |
| `theoretical_variance` | Calculate theoretical variance |
| `draw_discrete` | Generate one discrete observation |

The normal CDF uses an Abramowitz-Stegun approximation. It is suitable for the example's reporting and threshold calculations, but it is not intended to replace high-precision numerical computation in applications requiring tighter numerical tolerances.

`draw_discrete()` uses PostgreSQL's `random()` function and cumulative probabilities. This is a simulation mechanism, not a cryptographic random-number facility.

### Stored procedure and transactions

`record_observation()` provides a controlled database operation for recording observations.

It uses an upsert keyed by distribution ID and sample number. The observation trigger still validates the resulting row.

The sample-data section runs within a transaction. The deferred PMF validation executes at commit.

The final invalid-observation demonstration uses a savepoint. The expected validation error is handled within a PL/pgSQL exception block, allowing the demonstration transaction to continue and complete without retaining the invalid observation.

### Reporting views

`distribution_catalog` joins distribution metadata to continuous parameters and theoretical moments.

`observation_statistics` aggregates empirical observations using:
- `COUNT`
- `AVG`
- `VAR_SAMP`
- `STDDEV_SAMP`
- `MIN`
- `MAX`

Indexes on the observation table support retrieval by distribution and capture time, as well as queries filtering on observed values.

## 12. Theoretical versus empirical probability

The project keeps mathematical models and sampled data separate.

| Measure | Meaning |
|---|---|
| PMF | Theoretical probability of an exact discrete outcome |
| PDF | Theoretical probability density at a continuous value |
| CDF | Theoretical probability of a value not exceeding a threshold |
| Expected value | Theoretical probability-weighted mean |
| Theoretical variance | Model-based measure of dispersion |
| Empirical mean | Average of collected observations |
| Empirical variance | Dispersion estimated from collected observations |
| Monte Carlo probability | Estimated event probability from simulated observations |

For example, the normal model specifies a theoretical mean of 120 milliseconds. A finite sample of generated response times may have a slightly different empirical mean.

Differences between theoretical and empirical results are expected. They become smaller on average with larger representative samples, subject to the assumptions of the probability model and the sampling process.

## 13. Edge cases and technical limitations

### Probability validation

A probability distribution must not contain negative probabilities or a total probability materially different from one.

Floating-point implementations use a small numerical tolerance because decimal values cannot always be represented exactly in binary floating-point arithmetic.

The database uses a numeric type for discrete probabilities and an explicit tolerance when validating their total.

### Invalid parameters

The implementations reject:
- Empty discrete support.
- Duplicate discrete support values.
- Invalid probability totals.
- Probabilities outside the interval from zero to one.
- Normal distributions with zero or negative standard deviation.
- Uniform distributions with equal or reversed bounds.
- NaN values used as mathematical inputs.
- Invalid sampling counts.
- Invalid observation values for discrete variables.

Infinite CDF inputs are handled as limiting values where supported. Distribution parameters themselves must remain finite.

### Continuous PDF boundaries

The PDF at a particular point is not an event probability.

For continuous distributions, assigning a nonzero probability to an individual point would be mathematically incorrect.

Uniform PDF values at the interval endpoints do not change any interval probability because individual points have zero probability under a continuous distribution. The endpoint convention is used consistently for evaluation in the examples.

### Distribution assumptions

The binomial model assumes independent trials with a constant success probability.

The normal model assumes a symmetric, bell-shaped distribution with the specified mean and standard deviation.

The uniform model assumes equal probability density throughout the specified interval.

Real operational data may violate these assumptions. A suitable distribution should be selected based on the data-generating process rather than convenience.

### Numerical precision

Normal CDF calculations use different numerical implementations across the five files.

The Python implementation uses `math.erf`, and the C++ implementation uses `erfc`. JavaScript and Java use an approximation to the error function. PostgreSQL uses an approximation specifically for the normal CDF.

Small discrepancies between numerical results are possible.

### Random sampling and security

The seeded random generators in the Python, JavaScript, C++17, and Java examples provide reproducible simulation runs.

They are not intended for generating security tokens, cryptographic keys, or other security-sensitive random values.

PostgreSQL's `random()` is also intended for simulation rather than cryptographic use.

### Database limitations

The SQL schema focuses on normal and uniform continuous distributions and discrete PMFs. It does not attempt to implement every possible probability distribution.

The observation table stores representative numerical measurements. A production analytics system may also require source identifiers, collection methods, units, sampling windows, data-quality status, and access-control policies.

The schema-level probability validation protects completed discrete distribution transactions. Changes to parent metadata and multi-table model changes should be performed through controlled transactions.

## 14. File responsibilities and execution

| File | Main responsibility | Primary technical mechanisms |
|---|---|---|
| `random_variables.py` | Mathematical model and simulation | Abstract classes, dataclasses, dictionaries, binary search, Monte Carlo estimation, assertions |
| `random_variables.js` | Event-driven observation processing | Classes, maps, sets, event bus, asynchronous generators, online statistics |
| `random_variables.cpp` | Efficient distribution calculations | C++17 classes, virtual interfaces, STL vectors, binary search, random distributions |
| `Main.java` | Enterprise probability assessment | Interfaces, records, immutable collections, policy evaluation, domain exceptions |
| `random_variables.sql` | Persistent probability and observation model | Relational constraints, triggers, functions, procedures, transactions, views, indexes |

The examples use the same core scenarios so that theoretical probability calculations, simulation results, and database reports can be compared across implementations.
