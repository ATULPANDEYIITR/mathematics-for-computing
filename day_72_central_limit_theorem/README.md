# Central Limit Theorem: Sampling Distributions and Approximation Techniques

## 1. Statistical Foundation

The Central Limit Theorem (CLT) describes the behavior of sums and averages of random variables.

For a population with finite mean \(\mu\) and finite variance \(\sigma^2\), consider independent and identically distributed random variables:

\[
X_1,X_2,\ldots,X_n
\]

The sample mean is:

\[
\bar X=\frac{1}{n}\sum_{i=1}^{n}X_i
\]

Its expected value and variance are:

\[
E(\bar X)=\mu
\]

\[
Var(\bar X)=\frac{\sigma^2}{n}
\]

The standard error is:

\[
SE(\bar X)=\frac{\sigma}{\sqrt n}
\]

Under the appropriate CLT assumptions, the standardized sample mean converges in distribution to the standard normal distribution:

\[
\frac{\bar X-\mu}{\sigma/\sqrt n}
\xrightarrow{d}N(0,1)
\]

This result does not require the original population to be normally distributed.

A population can be Bernoulli, exponential, uniform, or strongly right-skewed. The sampling distribution of its sample mean can become approximately normal as the sample size increases.

The approximation is asymptotic. A sample size of 30 is not a universal guarantee of normality.

## 2. Population Distribution and Sampling Distribution

These distributions describe different statistical objects.

| Property | Population distribution | Sampling distribution |
|---|---|---|
| Represents | Individual population observations | A statistic across repeated samples |
| Random variable | \(X\) | \(\bar X\) |
| Mean | \(\mu\) | \(\mu\) |
| Variance | \(\sigma^2\) | \(\sigma^2/n\) |
| Standard deviation | \(\sigma\) | \(\sigma/\sqrt n\) |
| Main purpose | Describe population variability | Describe estimator variability |

Suppose a population has mean 100 and standard deviation 20.

For samples of size 25:

\[
E(\bar X)=100
\]

\[
SE(\bar X)=\frac{20}{\sqrt{25}}=4
\]

For samples of size 100:

\[
SE(\bar X)=\frac{20}{\sqrt{100}}=2
\]

The expected sample mean remains unchanged, but its variability decreases.

The sampling distribution is not obtained by examining individual population values. It is obtained by repeatedly drawing samples, calculating the statistic for each sample, and examining the resulting collection of statistics.

## 3. Assumptions and Conditions

The classical CLT is commonly applied under these conditions:

- Observations are independent.
- Observations follow the same distribution in the standard IID formulation.
- The population has a finite mean.
- The population has finite variance.
- The sample size is sufficiently large for the required approximation accuracy.

Independence is particularly important.

Repeatedly drawing observations with replacement from a population provides independent draws under the usual random sampling model.

Sampling without replacement from a finite population introduces dependence between observations. When the sampling fraction is small, the independence approximation is often reasonable. When a substantial proportion of the population is sampled, the finite population correction should be considered.

For highly skewed or heavy-tailed populations, convergence can be slow. A larger sample may be required.

## 4. Sampling With and Without Replacement

### Sampling with replacement

An observation is returned to the population after selection.

Consequently:

- The same observation can be selected multiple times.
- Every draw has the same population distribution.
- Draws are independent under the sampling model.
- The standard error of the sample mean is:

\[
SE=\frac{\sigma}{\sqrt n}
\]

### Sampling without replacement

An observation cannot be selected again during the same sample.

For a finite population of size \(N\), the finite population correction is:

\[
FPC=\sqrt{\frac{N-n}{N-1}}
\]

The standard error becomes:

\[
SE=\frac{\sigma}{\sqrt n}
\sqrt{\frac{N-n}{N-1}}
\]

When \(n=N\), the entire population has been observed and the sampling error of the population mean is zero.

The finite population correction should not be applied indiscriminately to independent sampling with replacement.

## 5. Approximation Techniques

The implementations examine several approaches to statistical approximation.

### 5.1 Normal approximation

For a sufficiently large sample:

\[
\bar X\approx N\left(\mu,\frac{\sigma^2}{n}\right)
\]

For a standardized statistic:

\[
Z=\frac{\bar X-\mu}{\sigma/\sqrt n}
\]

The standard normal cumulative distribution function is:

\[
\Phi(z)=P(Z\leq z)
\]

For a normal approximation:

\[
P(a\leq\bar X\leq b)
\approx
\Phi\left(\frac{b-\mu}{SE}\right)
-
\Phi\left(\frac{a-\mu}{SE}\right)
\]

Python uses the standard library's error function. JavaScript and Java implement numerical approximations, while C++ uses the standard library complementary error function.

### 5.2 Standard error approximation

The theoretical standard error uses the population standard deviation.

In practical statistical work, the population standard deviation may be unknown. It is then estimated using the sample standard deviation:

\[
\widehat{SE}=\frac{s}{\sqrt n}
\]

For finite population sampling without replacement, the estimated standard error can also incorporate the finite population correction.

### 5.3 Confidence intervals

When the population standard deviation is known, a normal-based confidence interval for the population mean is:

\[
\bar X\pm z_{\alpha/2}\frac{\sigma}{\sqrt n}
\]

For a 95% interval:

\[
\bar X\pm1.96\frac{\sigma}{\sqrt n}
\]

When the population standard deviation is estimated, a Student's t critical value is generally appropriate under the corresponding assumptions:

\[
\bar X\pm t_{\alpha/2,n-1}\frac{s}{\sqrt n}
\]

The supplied implementations use a normal critical value of approximately 1.96 for their principal coverage experiments. These experiments should not be interpreted as exact small-sample t procedures.

### 5.4 Bootstrap percentile approximation

Bootstrap resampling estimates sampling uncertainty using the observed sample.

Its procedure is:

1. Start with an observed sample.
2. Draw a bootstrap sample of the same size with replacement.
3. Calculate the statistic.
4. Repeat the process many times.
5. Sort the bootstrap statistics.
6. Extract the required percentile boundaries.

For a 95% percentile interval, the approximate boundaries are the 2.5th and 97.5th percentiles.

Bootstrap estimation is useful when analytical sampling distributions are difficult to derive.

It does not automatically solve problems caused by biased sampling, insufficient data, dependent observations, or extreme heavy-tailed distributions.

### 5.5 Empirical convergence diagnostics

The implementations compare the simulated sampling distribution against its theoretical normal approximation.

The Kolmogorov-Smirnov distance is:

\[
D_n=\sup_x|F_n(x)-F(x)|
\]

Where:

- \(F_n(x)\) is the empirical cumulative distribution function.
- \(F(x)\) is the theoretical normal cumulative distribution function.

A smaller distance indicates closer empirical agreement.

The reported distance is a descriptive approximation diagnostic. It is not automatically a calibrated hypothesis test, particularly when theoretical parameters are estimated or simulation assumptions are violated.

## 6. Population Types and Experimental Design

The four population generators represent different distribution shapes.

| Population | Distribution | Statistical characteristics |
|---|---|---|
| Bernoulli | Binary | Discrete outcomes with a success probability |
| Exponential | Continuous | Positive observations with right skew |
| Uniform | Continuous | Equal probability over a bounded interval |
| Highly skewed | Transformed exponential | Strong right skew and a longer upper tail |

The Bernoulli population uses:

\[
P(X=1)=0.3
\]

Its theoretical parameters are:

\[
\mu=p=0.3
\]

\[
\sigma^2=p(1-p)=0.21
\]

For an exponential distribution with rate \(\lambda=1\):

\[
\mu=1
\]

\[
\sigma^2=1
\]

The uniform population over \([0,100]\) has:

\[
\mu=50
\]

\[
\sigma^2=\frac{100^2}{12}
\]

These examples allow the same sampling methodology to be evaluated under different population characteristics.

## 7. Python Implementation

The Python script uses an object-oriented statistical model with standard-library components.

| Component | Responsibility |
|---|---|
| `DistributionType` | Identifies population distribution families |
| `SamplingMethod` | Separates replacement policies |
| `Population` | Stores observations and population parameters |
| `SamplingResult` | Represents simulation results |
| `create_population()` | Generates experimental populations |
| `draw_sample()` | Performs random sampling |
| `theoretical_standard_error()` | Calculates theoretical sampling variability |
| `monte_carlo_sampling_distribution()` | Generates repeated sample means |
| `bootstrap_interval()` | Calculates bootstrap percentile intervals |
| `approximation_diagnostics()` | Compares empirical and theoretical distributions |
| `convergence_study()` | Evaluates several sample sizes |
| `save_results()` | Produces JSON and CSV reports |

The implementation uses `random.Random` with fixed seeds to support reproducibility.

Population variance is calculated with the population denominator \(N\). Empirical sampling-distribution standard deviation uses the sample denominator \(R-1\), where \(R\) is the number of repetitions.

The script also checks sample-size constraints and invalid confidence interval parameters.

Output files are stored in `clt_results`.

## 8. JavaScript Implementation

The JavaScript implementation adopts an asynchronous event-driven design.

Its central components are:

| Component | Responsibility |
|---|---|
| `SeededRandom` | Reproducible random-number generation |
| `Population` | Validated population construction |
| `OnlineStatistics` | Streaming mean and variance |
| `SamplingEngine` | Sample generation and Monte Carlo execution |
| `evaluateNormalApproximation()` | Normal-model diagnostics |
| `bootstrapInterval()` | Bootstrap percentile approximation |
| `measureCoverage()` | Empirical interval coverage |
| `saveReport()` | Persistent JSON reporting |

### Streaming computation

Welford's online algorithm calculates variance without storing all observations:

\[
\delta=x-\bar x_{old}
\]

\[
\bar x_{new}=\bar x_{old}+\frac{\delta}{n}
\]

\[
M_{2,new}=M_{2,old}+\delta(x-\bar x_{new})
\]

The sample variance is:

\[
s^2=\frac{M_2}{n-1}
\]

This reduces numerical cancellation and supports large streaming calculations.

### Asynchronous execution

The simulation is divided into batches.

`setImmediate()` allows Node.js to process other event-loop work between batches. `EventEmitter` publishes progress information without coupling monitoring logic to the sampling algorithm.

The JSON report stores experiment metrics rather than every generated sample mean.

## 9. C++17 Implementation

The C++ implementation emphasizes numerical computation, memory management, and efficient statistical processing.

| Component | Responsibility |
|---|---|
| `Population` | Validated population domain object |
| `OnlineStatistics` | Incremental statistical aggregation |
| `SamplingEngine` | Random sample generation |
| `ConfidenceInterval` | Interval representation |
| `ExperimentResult` | Experiment output |
| `normalCDF()` | Standard normal probability calculation |
| `kolmogorovSmirnovDistance()` | Empirical distribution comparison |
| `confidenceCoverage()` | Coverage measurement |
| `generatePopulation()` | Distribution generation |

The program uses:

- `std::vector` for observation storage.
- `std::mt19937_64` for reproducible pseudorandom generation.
- `std::shuffle` for sampling without replacement.
- `std::accumulate` for numerical aggregation.
- `std::erfc` for normal probability calculations.
- `std::max` and `std::sort` for diagnostics.

The implementation separates population construction, sampling, estimation, and reporting.

Welford's algorithm reduces the need to retain intermediate statistics.

Sampling without replacement uses a shuffled population and truncates the resulting vector. This approach is straightforward but requires additional memory proportional to population size.

## 10. Java 17 Implementation

The Java implementation models a statistical experiment as an enterprise-oriented service.

Its principal domain types include:

- `Population`
- `ExperimentConfiguration`
- `ConfidenceInterval`
- `ExperimentResult`
- `ExperimentStatus`
- `SamplingPolicy`

Java records provide immutable representations for experiment configuration and results.

`PopulationFactory` generates controlled statistical populations.

`SamplingService` performs sampling and calculates theoretical standard errors.

`ApproximationService` implements normal probability calculations, confidence intervals, and empirical distribution diagnostics.

`BootstrapService` calculates percentile intervals.

`ExperimentService` manages experiment execution and failure states.

The implementation uses `SplittableRandom` for seeded random generation and Java collections for observation management.

The experiment service distinguishes successful completion from execution failure. Validation errors are propagated through a dedicated exception hierarchy.

The implementation is intentionally sequential within an experiment. Parallel Monte Carlo execution would require independent random streams and carefully controlled aggregation to preserve reproducibility.

## 11. PostgreSQL Implementation

The database models the statistical experiment lifecycle.

### Relational structure

| Table | Purpose |
|---|---|
| `experiment` | Population parameters and sampling configuration |
| `sampling_run` | Individual repeated sampling experiments |
| `sample_observation` | Recorded values belonging to a sample |
| `sampling_distribution_summary` | Aggregated sampling-distribution metrics |

The primary relationship is:

    experiment
        |
        +---- sampling_run
                  |
                  +---- sample_observation

    experiment
        |
        +---- sampling_distribution_summary

### Integrity mechanisms

Primary keys identify database records.

Foreign keys preserve experiment-to-run and run-to-observation relationships.

Unique constraints prevent duplicate run numbers and observation positions within the same run.

Check constraints enforce positive sample sizes, valid confidence levels, and nonnegative variance.

The observation trigger prevents writes to finalized runs and rejects observations beyond configured sample capacity.

The `finalize_sampling_run` procedure verifies sample completeness before calculating the sample mean, sample variance, standard error, and confidence interval.

The `calculate_sampling_summary` procedure aggregates completed runs and compares empirical and theoretical sampling variability.

### Database reporting

The database provides:

- Experiment retrieval.
- Completed-sample validation.
- Sampling-distribution aggregation.
- Confidence interval coverage.
- Normal approximation eligibility screening.
- Normal probability calculations.
- Experiment performance reporting.

The CTE-based diagnostic query separates sample-level calculations from report presentation.

The SQL script stores representative observations. It does not claim to perform the thousands of random trials executed by the programming-language implementations.

## 12. Four Distinct Statistical and Computational Concerns

The implementations distinguish four important levels of statistical reasoning.

| Concern | Question | Appropriate mechanism |
|---|---|---|
| Population | What does the original data distribution look like? | Population statistics |
| Sampling | How does a statistic vary across repeated samples? | Sampling distribution |
| Approximation | How closely does a theoretical distribution represent the statistic? | CLT and normal approximation |
| Estimation | How uncertain is an estimate based on observed data? | Standard errors, confidence intervals, bootstrap |

Confusing these levels can produce incorrect conclusions.

For example, a highly skewed population does not imply that the sampling distribution of its mean must remain highly skewed for every sample size.

Likewise, a large sample does not eliminate systematic sampling bias.

## 13. Practical Interpretation

### Sample size and convergence

The sample sizes examined are:

\[
n\in\{2,5,10,30,50,100\}
\]

For each population, the experiments compare:

- Empirical mean of the sample means.
- Theoretical population mean.
- Empirical standard deviation of sample means.
- Theoretical standard error.
- Normal approximation distance.
- Confidence interval coverage.

A successful simulation should generally show empirical sampling-distribution means approaching the population mean and empirical standard deviations approaching the theoretical standard error as the number of Monte Carlo repetitions increases.

Increasing sample size decreases the standard error according to the inverse square-root relationship.

Increasing the number of Monte Carlo repetitions improves the precision of estimated simulation metrics. These are different effects.

### Confidence interval coverage

A nominal 95% confidence interval does not mean that a particular calculated interval has a 95% probability of containing the fixed population mean.

It means that, under the assumptions of the interval procedure, repeated application of the method should capture the population parameter approximately 95% of the time.

Observed coverage can differ from 95% because of:

- Small samples.
- Strong skewness.
- Inaccurate normal approximations.
- Unknown population variance.
- Dependence between observations.
- Finite simulation repetitions.

### Monte Carlo uncertainty

Simulation results are estimates themselves.

For a simulated coverage proportion \(\hat p\) based on \(R\) independent trials, its approximate standard error is:

\[
SE(\hat p)=\sqrt{\frac{\hat p(1-\hat p)}{R}}
\]

Consequently, a reported coverage of 0.94 from 1,000 trials is not evidence that the true coverage is exactly 94%.

## 14. Complexity and Performance

Let:

- \(N\) represent population size.
- \(n\) represent sample size.
- \(R\) represent Monte Carlo repetitions.
- \(B\) represent bootstrap repetitions.

| Operation | Time complexity | Additional memory |
|---|---:|---:|
| Population construction | \(O(N)\) | \(O(N)\) |
| One sample with replacement | \(O(n)\) | \(O(n)\) if stored |
| One sample without replacement | \(O(N)\) for full shuffle | \(O(N)\) |
| Monte Carlo sampling | \(O(Rn)\) | \(O(R)\) for stored means |
| Online statistics | \(O(R)\) | \(O(1)\) |
| Sorting for KS diagnostics | \(O(R\log R)\) | \(O(R)\) |
| Bootstrap estimation | \(O(Bn)\) | \(O(B)\) |

The C++ and Python implementations store sampling means to calculate distribution diagnostics.

The JavaScript implementation uses online statistics during simulation but retains means for its empirical distribution comparison.

For large production workloads, simulations can be divided into independent batches. Each batch can return a count, mean, and second central moment. These partial statistics can then be combined using mathematically correct aggregation formulas.

Database storage should generally contain experiment metadata and aggregate results rather than every intermediate random value unless observation-level auditability is required.

## 15. Validation and Failure Conditions

The implementations explicitly handle the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty population | Reject construction |
| Population with fewer than two values | Reject construction |
| Non-finite observations | Reject input |
| Zero or negative sample size | Reject experiment |
| Insufficient Monte Carlo repetitions | Reject execution |
| Sample larger than finite population | Reject sampling |
| Negative standard error | Reject interval calculation |
| Zero population variance | Recognize degenerate sampling distribution |
| Insufficient bootstrap data | Reject bootstrap |
| Incomplete database sample | Prevent finalization |
| Observation beyond configured sample size | Reject database insert |
| Repeated database finalization | Reject operation |

These validations prevent invalid statistical assumptions from silently entering the calculations.

## 16. Security, Reproducibility, and Operational Controls

Although these experiments are statistical rather than security-sensitive applications, operational safeguards remain important.

- Use fixed random seeds when reproducibility is required.
- Do not expose database credentials in source files.
- Use restricted database roles for experiment execution.
- Apply transaction boundaries to related database operations.
- Validate externally supplied sample sizes and repetition counts.
- Limit simulation workloads to prevent excessive memory and CPU consumption.
- Preserve experiment parameters alongside calculated results.
- Distinguish synthetic populations from actual observed datasets.
- Record the random seed and sampling policy for reproducibility.
- Avoid presenting a normal approximation as an exact distribution.

A fixed pseudorandom seed makes a simulation repeatable within the same implementation and compatible execution environment. It does not make the generated observations independent of the underlying pseudorandom generator's limitations.

## 17. Limitations

The implementations provide controlled educational and computational models rather than a complete statistical inference library.

Important limitations include:

- The normal approximation uses a fixed critical value for its principal confidence interval experiments.
- The examples assume independent observations under the with-replacement sampling model.
- The finite population correction is implemented for simple random sampling without replacement.
- The practical sample-size threshold of 30 is only a screening heuristic.
- The bootstrap implementation uses percentile intervals rather than bias-corrected or studentized intervals.
- The Kolmogorov-Smirnov distance is used descriptively and does not establish that a population satisfies CLT assumptions.
- Synthetic populations do not reproduce every property of real-world datasets.
- Heavy-tailed distributions with infinite variance require different theoretical treatment.
- The SQL implementation persists representative observations and calculated results rather than generating a complete Monte Carlo experiment internally.

The most important statistical distinction remains the difference between the distribution of individual observations and the distribution of a statistic calculated from repeated samples.
