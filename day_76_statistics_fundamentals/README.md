# Statistics Fundamentals: Population, Sample, Parameters, Statistics and Sampling

## 1. Statistical Foundations

Statistics provides methods for collecting, organizing, analyzing and interpreting numerical information. Its central purpose is to extract meaningful information from observations while accounting for uncertainty.

A statistical investigation begins with a defined population. When observing every population member is impractical, a subset is selected through a sampling procedure. The resulting observations are analyzed to estimate population characteristics.

The fundamental relationship is:

**Population → Sampling Frame → Sample → Sample Statistics → Population Inference**

The distinction between a population parameter and a sample statistic is essential. A parameter describes the population, whereas a statistic is calculated from observed sample data.

## 2. Population

A population is the complete collection of individuals, objects, events or observations relevant to a statistical investigation.

Examples include:

- All students enrolled at a university during an academic year.
- All transactions processed by a banking system during a month.
- All manufacturing units produced during a production period.
- All registered customers of a service organization.
- All hospitals participating in a defined research investigation.

Population size is represented by \(N\).

For a finite population:

\[
N = \text{Number of population units}
\]

### Population characteristics

A population must have a clearly defined scope.

| Characteristic | Description |
|---|---|
| Population identity | The group being investigated |
| Population size | Total number of eligible units |
| Observation unit | Individual entity being measured |
| Reference period | Time period covered |
| Eligibility | Conditions for inclusion |
| Sampling frame | Operational list of eligible units |

The sampling frame is the practical representation of the population used for selection. It may not perfectly represent the target population.

Coverage errors occur when eligible units are missing, duplicated or incorrectly included.

### Population parameters

A parameter is a numerical characteristic of the complete population.

**Population mean**

\[
\mu = \frac{\sum_{i=1}^{N}X_i}{N}
\]

**Population variance**

\[
\sigma^2 =
\frac{\sum_{i=1}^{N}(X_i-\mu)^2}{N}
\]

**Population standard deviation**

\[
\sigma = \sqrt{\sigma^2}
\]

**Population total**

\[
T = \sum_{i=1}^{N}X_i
\]

These quantities are fixed for a defined population and measurement period, although their values may be unknown.

The Python, JavaScript, C++17 and Java 17 implementations calculate population parameters from complete population records. The PostgreSQL implementation calculates the same quantities through aggregate functions.

## 3. Sample

A sample is a subset of population units selected for statistical investigation.

Sample size is represented by \(n\).

\[
1 \leq n \leq N
\]

Sampling reduces the cost and time required for data collection. It also makes investigations possible when observing every population unit is impractical.

### Sample characteristics

- A sample must originate from a defined population.
- Each selected observation must be identifiable.
- Selection must follow a documented procedure.
- Sample size must satisfy the population constraints.
- Duplicate observations must be prevented when sampling without replacement.
- Missing observations and non-response must be documented.

### Sample statistics

A statistic is calculated from sample observations.

**Sample mean**

\[
\bar{x} = \frac{\sum_{i=1}^{n}x_i}{n}
\]

**Sample variance**

\[
s^2 =
\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}
\]

**Sample standard deviation**

\[
s = \sqrt{s^2}
\]

The sample variance uses \(n-1\) rather than \(n\). This is Bessel's correction, which provides an unbiased estimator of population variance under independent random sampling from an identically distributed population.

### Population and sample comparison

| Feature | Population | Sample |
|---|---|---|
| Meaning | Entire defined group | Selected subset |
| Size | \(N\) | \(n\) |
| Mean | \(\mu\) | \(\bar{x}\) |
| Variance | \(\sigma^2\) | \(s^2\) |
| Standard deviation | \(\sigma\) | \(s\) |
| Numerical quantity | Parameter | Statistic |
| Purpose | Describe the complete group | Estimate population characteristics |

A sample statistic may differ from the corresponding population parameter because of sampling variability.

## 4. Parameters and Statistics

Parameters and statistics are related but are not interchangeable.

A population parameter describes the underlying population. A sample statistic summarizes the observed sample and may be used as an estimator of the parameter.

| Population parameter | Sample statistic |
|---|---|
| Population mean \(\mu\) | Sample mean \(\bar{x}\) |
| Population variance \(\sigma^2\) | Sample variance \(s^2\) |
| Population standard deviation \(\sigma\) | Sample standard deviation \(s\) |
| Population proportion \(P\) | Sample proportion \(\hat{p}\) |
| Population total \(T\) | Estimated sample-based total |

For a binary characteristic, the sample proportion is:

\[
\hat{p} = \frac{x}{n}
\]

where \(x\) represents the number of observations satisfying the defined condition.

### Estimation

An estimator is a statistical procedure used to estimate an unknown parameter.

For simple random sampling, the sample mean is an unbiased estimator of the population mean:

\[
E(\bar{x}) = \mu
\]

An estimator is unbiased when its expected value equals the parameter being estimated.

Other desirable properties include:

- Consistency: estimates approach the parameter as sample size increases under appropriate assumptions.
- Efficiency: an estimator has relatively low variance among comparable unbiased estimators.
- Robustness: an estimator is less sensitive to violations of assumptions or extreme observations.

The choice of estimator must account for the sampling design. A simple unweighted sample mean is not necessarily appropriate for unequal-probability sampling.

## 5. Descriptive Statistics

Descriptive statistics summarize observed data without automatically making conclusions about an entire population.

### Measures of central tendency

**Mean**

The arithmetic average of observations.

**Median**

The middle observation after sorting the values. For an even number of observations, it is the average of the two middle observations.

**Mode**

The most frequently occurring value.

### Measures of dispersion

**Range**

\[
R = X_{\max} - X_{\min}
\]

**Variance**

Measures the average squared deviation from the mean, using either the population or sample denominator.

**Standard deviation**

Expresses dispersion in the same measurement units as the original variable.

**Interquartile range**

\[
IQR = Q_3-Q_1
\]

The interquartile range measures the spread of the middle 50% of observations.

### Quantiles

Quantiles divide ordered observations according to specified probabilities.

| Quantile | Interpretation |
|---|---|
| \(Q_1\) | 25th percentile |
| \(Q_2\) | 50th percentile |
| \(Q_3\) | 75th percentile |
| \(P_{90}\) | 90th percentile |

The implementations use linear interpolation for quantile calculations where provided.

Different statistical packages may use different quantile conventions. Results should therefore document the chosen method.

## 6. Sampling Methods

Sampling methods determine how population units are selected.

The choice depends on population structure, sampling-frame quality, research objectives, available resources and the precision required.

### 6.1 Simple Random Sampling

Simple random sampling gives every population unit an equal probability of selection.

For a fixed-size sample selected without replacement:

\[
P(i\text{ selected}) = \frac{n}{N}
\]

For a particular subset of \(n\) units:

\[
P(\text{subset}) =
\frac{1}{\binom{N}{n}}
\]

Characteristics:

- Each population unit has an equal inclusion probability.
- Selection is based on randomization.
- Duplicate selection is prevented without replacement.
- Sample selection is independent of the observed outcome values.

Advantages:

- Straightforward statistical interpretation.
- Simple implementation.
- Suitable for a well-defined population with a complete sampling frame.

Limitations:

- Every population unit must be represented in the sampling frame.
- Small subgroups may receive inadequate representation by chance.
- Large or geographically distributed populations may be expensive to survey.

The implementations use reproducible pseudorandom number generators to make sample selection repeatable for a specified seed and population ordering.

### 6.2 Systematic Sampling

Systematic sampling selects units at regular intervals from an ordered sampling frame after choosing a random starting position.

The approximate sampling interval is:

\[
k = \frac{N}{n}
\]

For example, a population of 1,000 units and a sample size of 100 gives:

\[
k = \frac{1000}{100} = 10
\]

A random starting position determines the initial selection, followed by regularly spaced units.

Advantages:

- Simple operational procedure.
- Efficient for ordered population registers.
- Convenient for continuous production monitoring.

Limitations:

- Periodic patterns in the sampling frame can introduce bias.
- Ordering may influence the representativeness of the sample.
- Random-start and interval assumptions must be documented.

Systematic sampling should not be applied blindly to populations with meaningful periodic structure.

### 6.3 Stratified Random Sampling

Stratified sampling divides a population into mutually exclusive groups called strata.

A random sample is then selected independently from each stratum.

Examples of possible strata include:

- Academic departments.
- Geographic regions.
- Customer categories.
- Age groups.
- Organizational divisions.

For proportional allocation:

\[
n_h = n\frac{N_h}{N}
\]

where:

- \(N_h\) is the population size of stratum \(h\).
- \(n_h\) is its allocated sample size.
- \(N\) is the total population size.
- \(n\) is the total requested sample size.

The allocations must satisfy:

\[
\sum_{h=1}^{H}n_h=n
\]

Fractional allocations are converted into integer sample counts using a largest-remainder allocation procedure in the implementations.

For stratified sampling, the population mean estimator is:

\[
\bar{x}_{st} =
\sum_{h=1}^{H}W_h\bar{x}_h
\]

where:

\[
W_h=\frac{N_h}{N}
\]

This weighted estimator accounts for differences in stratum sizes.

Advantages:

- Ensures representation from defined subgroups.
- Can improve precision when strata are internally homogeneous.
- Supports subgroup-level reporting.

Limitations:

- Requires accurate stratum membership.
- Requires sufficient sample allocation to each stratum.
- Incorrect weighting can produce biased estimates.

### 6.4 Cluster Sampling

Cluster sampling divides a population into naturally occurring groups called clusters.

Examples include:

- Schools within districts.
- Hospitals within regions.
- Branch offices within a banking network.
- Production facilities within an industrial organization.

In one-stage cluster sampling, selected clusters are observed in their entirety.

Cluster sampling differs from stratified sampling:

| Feature | Stratified sampling | Cluster sampling |
|---|---|---|
| Grouping | Strata | Clusters |
| Selection | Units selected within every stratum | Clusters selected |
| Objective | Improve representation and precision | Reduce operational costs |
| Group coverage | Every represented stratum | Only selected clusters |
| Typical use | Diverse population subgroups | Geographically distributed populations |

The Python implementation includes one-stage cluster selection. Its results should not be interpreted using the ordinary simple-random-sampling variance formula without accounting for cluster selection and intracluster correlation.

## 7. Sampling Distribution

A sampling distribution is the probability distribution of a statistic across repeated samples selected under the same sampling design.

For example, repeatedly drawing samples of equal size from the same population produces multiple sample means.

The distribution of these means is the sampling distribution of the sample mean.

For independent observations with finite variance:

\[
E(\bar{x})=\mu
\]

\[
Var(\bar{x})=\frac{\sigma^2}{n}
\]

Therefore:

\[
SE(\bar{x})=\frac{\sigma}{\sqrt{n}}
\]

The standard error measures the variability of an estimator across repeated samples.

It is not the same as the standard deviation of individual observations.

### Central Limit Theorem

Under suitable independence and finite-variance conditions, the sampling distribution of the sample mean approaches a normal distribution as sample size increases.

This result supports many standard inferential procedures.

The required sample size for a sufficiently accurate normal approximation depends on the population distribution, dependence structure and estimator. There is no universal sample-size threshold.

### Sampling simulation

The JavaScript implementation performs repeated random sampling and calculates sample means.

The resulting estimates are used to calculate:

- Mean of the sampling distribution.
- Standard deviation of the sampling distribution.
- Number of simulation repetitions.

The simulation illustrates the relationship between sample size and sampling variability.

## 8. Standard Error and Finite Population Correction

For simple random sampling without replacement, the estimated standard error of the sample mean can incorporate the finite population correction.

\[
SE(\bar{x}) =
\frac{s}{\sqrt{n}}
\sqrt{\frac{N-n}{N-1}}
\]

where:

- \(s\) is the sample standard deviation.
- \(n\) is the sample size.
- \(N\) is the population size.

The correction factor is:

\[
FPC =
\sqrt{\frac{N-n}{N-1}}
\]

When the sample represents a very small proportion of the population, the correction has little effect.

When a large proportion of the finite population is sampled, the correction reduces the estimated standard error.

For a census, where \(n=N\), the sampling error associated with observing only a subset disappears.

This does not eliminate measurement errors, non-response errors, processing errors or coverage errors.

The standard-error implementation uses the finite population correction for simple random sampling. Applying the same formula to stratified, cluster or unequal-probability samples without adjustment is not statistically justified.

## 9. Confidence Intervals

A confidence interval provides a range of plausible values for an unknown population parameter under a specified statistical procedure and its assumptions.

For an approximately normal estimator:

\[
\bar{x}\pm z_{\alpha/2}SE(\bar{x})
\]

Common standard normal critical values are:

| Confidence level | Critical value |
|---|---:|
| 90% | 1.645 |
| 95% | 1.960 |
| 99% | 2.576 |

A 95% confidence procedure means that, under its assumptions, approximately 95% of intervals constructed through repeated sampling would contain the fixed population parameter.

It does not mean that the population parameter has a 95% probability of being inside an already calculated frequentist confidence interval.

The implementations use normal critical values for demonstration. When sample sizes are small and population variance is estimated, a Student's t critical value may be more appropriate.

## 10. Sample-Size Determination

Sample-size planning identifies the number of observations required to estimate a parameter with a specified margin of error and confidence level.

For estimating a population mean using an assumed population standard deviation:

\[
n_0 =
\left(
\frac{z\sigma}{E}
\right)^2
\]

where:

- \(z\) is the critical value.
- \(\sigma\) is the assumed population standard deviation.
- \(E\) is the desired margin of error.

For a finite population, the corrected sample size is:

\[
n =
\frac{n_0}
{1+\frac{n_0-1}{N}}
\]

The result is rounded upward to the next integer.

Sample-size planning must also consider:

- Expected non-response.
- Design effects.
- Unequal selection probabilities.
- Subgroup reporting requirements.
- Measurement precision.
- Available resources.

A sample-size calculation is not a guarantee of representativeness. A large biased sample can produce worse estimates than a smaller, properly designed sample.

## 11. Implementation Architecture

The five source files provide different engineering perspectives on the same statistical domain.

### Python: Statistical Modeling and Simulation

The Python implementation provides a complete statistical workflow using standard-library components.

| Component | Responsibility |
|---|---|
| `Unit` | Represents an individual population observation |
| `Population` | Maintains and validates the population |
| `Sample` | Represents selected observations |
| `DescriptiveStatistics` | Calculates descriptive measures |
| `PopulationParameters` | Calculates population characteristics |
| `SamplingEngine` | Executes sampling procedures |
| `StatisticalInference` | Calculates standard errors and intervals |
| `export_results` | Produces a JSON report |

The program uses dataclasses and enums to make domain structures explicit.

It includes:

- Simple random sampling.
- Systematic sampling.
- Proportional stratified sampling.
- One-stage cluster sampling.
- Confidence intervals.
- Bootstrap estimation.
- Sample-size determination.
- Validation assertions.
- JSON reporting.

The bootstrap procedure resamples observations with replacement and calculates the empirical distribution of sample means.

Its interval is a percentile-based bootstrap approximation, not a substitute for a carefully selected inferential method.

### JavaScript: Event-Driven Statistical Processing

The JavaScript implementation focuses on reproducible asynchronous processing.

| Component | Responsibility |
|---|---|
| `RandomGenerator` | Reproducible pseudorandom selection |
| `Population` | Immutable population storage |
| `Statistics` | Descriptive calculations |
| `SamplingService` | Sampling algorithms |
| `Inference` | Estimation and uncertainty |
| `SamplingPipeline` | Event-driven workflow |
| `simulateSamplingDistribution` | Repeated sampling simulation |

The population uses `Map` for indexed grouping and duplicate detection.

The sampling pipeline emits:

- `sampling:started`
- `sampling:completed`
- `sampling:failed`

The event-driven architecture separates statistical processing from audit and reporting operations.

The asynchronous simulation periodically yields to the Node.js event loop. It does not create parallel computation or guarantee isolation from other operations.

The report is written through a temporary file followed by a rename operation.

### C++17: Numerical and Algorithmic Implementation

The C++ implementation emphasizes explicit domain modeling and computational control.

| Component | Responsibility |
|---|---|
| `Observation` | Individual data record |
| `Population` | Validated population storage |
| `Statistics` | Numerical statistical operations |
| `SamplingEngine` | Random, systematic and stratified selection |
| `InferenceEngine` | Standard error and confidence intervals |
| `Sample` | Immutable-by-convention selection result |

The implementation uses:

- `std::vector` for observation storage.
- `std::set` for identifier validation.
- `std::map` for stratum grouping.
- `std::mt19937` for reproducible pseudorandom selection.
- STL algorithms for sorting, aggregation and selection.
- `long double` for more accurate intermediate summation.

The sampling engine uses explicit validation and exceptions to handle invalid population and sample configurations.

### Java 17: Enterprise Statistical Workflow

The Java implementation uses domain-oriented architecture and policy-based sampling.

| Component | Responsibility |
|---|---|
| `Observation` | Immutable observation record |
| `PopulationRepository` | Population access and validation |
| `Statistics` | Descriptive statistical service |
| `SamplingPolicy` | Sampling strategy contract |
| `SimpleRandomPolicy` | Random selection |
| `SystematicPolicy` | Interval-based selection |
| `StratifiedPolicy` | Proportional allocation |
| `InferenceService` | Statistical inference |
| `SamplingWorkflow` | State transitions and audit |

Java records provide immutable domain objects.

The `SamplingPolicy` interface separates the sampling algorithm from workflow execution.

The workflow uses the following states:

`CREATED → VALIDATED → SAMPLED → ANALYZED`

A failed workflow can enter `FAILED`, and terminal states cannot be reused.

The architecture separates data validation, sample selection, analysis and workflow reporting.

### PostgreSQL: Relational Statistical Management

The PostgreSQL implementation models a complete sampling workflow.

The schema separates population data, sampling projects, selected observations and analytical results.

| Database object | Responsibility |
|---|---|
| `population` | Population definitions |
| `population_strata` | Population subgroup definitions |
| `population_units` | Individual population records |
| `sampling_projects` | Sampling configurations |
| `sample_units` | Selected population units |
| `sample_analysis` | Calculated sample statistics |
| `sampling_audit` | Workflow transition history |

The database implements:

- Primary and foreign keys.
- Unique and check constraints.
- Population eligibility.
- Sample-to-population integrity.
- Sampling procedures.
- Aggregate statistical functions.
- Reporting views.
- Workflow auditing.
- Transactional processing.

PostgreSQL aggregate functions calculate population and sample statistics directly from stored observations.

The sampling procedures use SQL window functions and common table expressions to organize selection and allocation.

## 12. Database Sampling Workflow

The relational workflow follows this structure:

Population
→ Population Strata
→ Population Units
→ Sampling Project
→ Sample Selection
→ Sample Units
→ Sample Analysis
→ Statistical Reporting
→ Audit History

### Population registration

A population is created with a defined name, description and type.

Strata are associated with the population.

Individual units are inserted with:

- External identifier.
- Stratum membership.
- Cluster identifier.
- Numerical observation.
- Eligibility status.

### Sampling project registration

A sampling project specifies:

- Population.
- Sampling method.
- Requested sample size.
- Random seed.
- Confidence level.
- Workflow status.

### Sample selection

The appropriate stored procedure selects observations and records their inclusion probabilities where supported by the implemented design.

The simple random sampling procedure uses random ordering and selection without replacement.

The systematic sampling procedure selects units using a random starting position and fixed interval.

The stratified procedure uses proportional allocation and largest-remainder adjustment.

### Analysis

The analysis procedure calculates:

- Sample size.
- Sample mean.
- Sample variance.
- Sample standard deviation.
- Standard error.
- Confidence interval.

Results are stored separately from the population and sample records.

This separation preserves the distinction between original observations and derived statistical results.

## 13. Important Statistical Distinctions

Several concepts must remain separate during statistical analysis.

| Concept | Meaning |
|---|---|
| Population | Complete target group |
| Sampling frame | Operational representation of the population |
| Sample | Selected subset |
| Parameter | Population characteristic |
| Statistic | Sample-derived numerical measure |
| Estimator | Procedure for estimating a parameter |
| Estimate | Numerical result from an estimator |
| Sampling error | Difference arising from observing a sample rather than the complete population |
| Standard deviation | Dispersion of observations |
| Standard error | Dispersion of an estimator across repeated samples |
| Confidence interval | Interval produced by an inferential procedure |
| Sampling bias | Systematic distortion caused by the selection process |

A sample can be large without being representative.

A sampling frame can be complete while measurements are inaccurate.

A statistic can be correctly calculated while its interpretation is invalid because the sampling design was ignored.

These distinctions are central to sound statistical practice.

## 14. Validation and Edge Cases

The implementations account for several operational and statistical failure conditions.

| Condition | Expected handling |
|---|---|
| Empty population | Reject population creation |
| Empty sample | Reject sample creation |
| Duplicate population IDs | Reject duplicate records |
| Duplicate sample IDs | Reject sample selection |
| Sample size greater than population | Reject selection |
| Zero sample size | Reject selection |
| Non-finite numerical value | Reject observation |
| Sample variance with one observation | Reject calculation |
| Invalid confidence level | Reject inference request |
| Invalid quantile probability | Reject quantile calculation |
| Missing stratum representation | Reject stratified allocation |
| Ineligible population unit | Prevent sample selection |
| Sample from another population | Reject database insertion |
| Incomplete sampling workflow | Prevent analysis |

Validation should occur both at the application layer and the database layer.

Application validation provides clear operational errors. Database constraints protect data integrity when records are inserted through different application paths.

## 15. Performance and Computational Complexity

Let:

- \(N\) denote population size.
- \(n\) denote sample size.
- \(H\) denote the number of strata.
- \(B\) denote the number of bootstrap repetitions.

| Operation | Typical time complexity |
|---|---|
| Population validation | \(O(N)\) |
| Mean calculation | \(O(N)\) |
| Variance calculation | \(O(N)\) |
| Median | \(O(N\log N)\) |
| Quantile using sorting | \(O(N\log N)\) |
| Simple random sampling | \(O(N)\) in the shuffle-based implementations |
| Systematic sampling | \(O(n)\) after frame ordering |
| Stratified allocation | \(O(N+H\log H)\), excluding selection costs |
| Bootstrap simulation | \(O(Bn)\) |
| Sample reporting | \(O(n)\) for basic aggregates |

Database query performance depends on the population size, index selectivity, sorting operations, execution plans and concurrent workload.

For very large datasets:

- Avoid loading the complete population into application memory unnecessarily.
- Use database-side aggregation.
- Use indexed population identifiers.
- Keep sampling-frame ordering deterministic where reproducibility is required.
- Record random seeds and sampling-design metadata.
- Use approximate quantile algorithms only when their error characteristics are acceptable.
- Partition large populations when access patterns justify it.

## 16. Security, Integrity and Reproducibility

Statistical datasets may contain personal, financial, educational or operational information.

Production implementations should enforce:

- Role-based database access.
- Least-privilege permissions.
- Encryption in transit and at rest.
- Appropriate data retention.
- Restricted access to individual observations.
- Audit trails for sampling and analysis.
- Validation of imported records.
- Separation of identifiable information from analytical datasets.
- Protection of exported statistical reports.

Random seeds improve reproducibility but are not security controls.

The pseudorandom generators used in these educational implementations are not cryptographically secure and must not be used for security-sensitive random selection.

Reproducibility also requires recording:

- Population definition.
- Population snapshot or version.
- Sampling frame.
- Eligibility rules.
- Sampling algorithm.
- Random seed.
- Sample size.
- Selection ordering.
- Software and algorithm versions.

A seed alone is insufficient if the population ordering or population contents change.

## 17. Limitations of the Implementations

The implementations demonstrate fundamental statistical methods rather than a complete survey-analysis platform.

Important limitations include:

- Normal critical values are used for confidence intervals instead of general Student's t distributions.
- Stratified confidence intervals are not implemented with stratum-specific variance estimators.
- Cluster sampling is demonstrated only in the Python implementation.
- The Python cluster-sample inference must not be interpreted as a design-correct cluster variance estimator.
- Unequal-probability and probability-proportional-to-size sampling are not implemented.
- Non-response adjustment is not implemented.
- Missing-data imputation is not implemented.
- Survey weights and complex multistage sampling are not fully implemented.
- PostgreSQL random selection is intended for educational reproducibility rather than cryptographic security or large-scale production randomization.
- The JavaScript and Java implementations use normal approximations for supported confidence levels.

The database uses a finite-population correction in its analysis procedure based on the selected sample count and eligible population count. This calculation is suitable for the demonstrated simple random sampling design; it is not a general variance estimator for all sampling methods.

The practical selection and analysis of a statistical sample must always reflect the actual sampling design.

## 18. Execution Requirements

| Deliverable | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10+ | None |
| JavaScript | Node.js 18+ | None |
| C++17 | C++17 compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14+ | None |

### Python

Save the Python implementation as `statistics_fundamentals.py`.

Run using Python. The script performs validation tests, generates population and sampling reports, and writes `statistics_results.json`.

### JavaScript

Save the JavaScript implementation as `statistics_fundamentals.js`.

Run using Node.js. The program performs event-driven sampling, executes a sampling-distribution simulation and writes `statistics_report.json`.

### C++17

Save the C++ implementation as `statistics_fundamentals.cpp`.

Compile with a C++17-compatible compiler. The program runs validation tests and produces population, sample and inference reports.

### Java 17

Save the Java implementation as `StatisticsFundamentals.java`.

Compile and execute the public class using Java 17.

### PostgreSQL

Save the SQL implementation as `statistics_fundamentals.sql`.

Execute against a PostgreSQL database using a role permitted to create schemas, types, tables, functions, procedures, triggers and views.

The SQL script uses a transaction for schema creation, data insertion, sampling and reporting operations.

The transaction should be executed as one unit to preserve workflow consistency.

## 19. Educational Outcomes

The implementations provide practical understanding of:

- Defining a statistical population.
- Building and validating a sampling frame.
- Distinguishing populations from samples.
- Calculating population parameters.
- Calculating sample statistics.
- Understanding unbiased estimation.
- Selecting observations through different sampling designs.
- Understanding sampling distributions.
- Calculating standard errors.
- Applying finite population corrections.
- Constructing confidence intervals.
- Determining required sample sizes.
- Managing reproducible sampling workflows.
- Maintaining statistical data integrity in relational databases.

The central statistical principle is that the quality of an inference depends not only on the numerical calculations but also on the population definition, sampling design, data quality and assumptions used to interpret the results.
