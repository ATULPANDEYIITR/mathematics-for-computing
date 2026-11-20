# Hypothesis Testing: Statistical Inference and Decision-Making

## 1. Introduction

Hypothesis testing is a statistical inference procedure used to evaluate whether observed sample evidence is sufficiently inconsistent with a specified population assumption.

It provides a structured method for making decisions under uncertainty. Applications include manufacturing quality control, clinical research, financial analysis, marketing experiments, scientific studies and operational performance evaluation.

The central components are:

- Null hypothesis.
- Alternative hypothesis.
- Test statistic.
- Sampling distribution.
- P-value.
- Significance level.
- Critical region.
- Statistical decision.
- Confidence interval.

The five implementations demonstrate a common statistical workflow through Python, JavaScript, C++17, Java 17 and PostgreSQL.

## 2. Fundamental Concepts

### 2.1 Statistical hypotheses

A statistical hypothesis is a statement about a population parameter, such as its mean, proportion or variance.

Hypothesis testing compares two competing statements.

**Null hypothesis (H0)**

The null hypothesis represents the reference assumption being evaluated.

For a population mean:

H0: μ = 100

This states that the population mean equals 100.

**Alternative hypothesis (H1 or Ha)**

The alternative hypothesis represents the competing claim.

Three common alternatives are:

| Type | Mathematical expression | Interpretation |
|---|---|---|
| Two-sided | μ ≠ 100 | The population mean differs from 100 |
| Right-tailed | μ > 100 | The population mean exceeds 100 |
| Left-tailed | μ < 100 | The population mean is below 100 |

The alternative hypothesis must be selected before examining the results. Selecting the direction after observing the data can inflate the false-positive risk.

### 2.2 Statistical population and sample

A population is the complete set of observations or entities under investigation.

A sample is a subset of that population used to estimate population characteristics.

For example:

- Population: All production units manufactured by a factory.
- Sample: Twenty production units selected for quality assessment.
- Population mean: The actual average production measurement.
- Sample mean: The average measurement calculated from the selected units.

Statistical inference uses sample evidence to evaluate population-level assumptions.

### 2.3 Test statistic

A test statistic measures the difference between the observed sample result and the result expected under the null hypothesis.

The one-sample Z-test uses:

z = (x̄ - μ0) / (σ / √n)

Where:

| Symbol | Meaning |
|---|---|
| x̄ | Observed sample mean |
| μ0 | Mean specified by the null hypothesis |
| σ | Known population standard deviation |
| n | Sample size |
| σ / √n | Standard error |
| z | Standardized test statistic |

A large absolute Z-statistic indicates that the observed sample mean is relatively far from the hypothesized population mean.

The direction of the statistic also matters for one-sided tests.

## 3. Understanding P-values

The p-value measures the probability, assuming the null hypothesis and statistical model are correct, of obtaining a test statistic at least as extreme as the observed statistic in the direction specified by the alternative hypothesis.

It is not the probability that the null hypothesis is true.

It is also not the probability that the result occurred by chance without qualification.

For a standard normal test:

**Two-sided test**

p = 2 × P(Z ≥ |z|)

**Right-tailed test**

p = P(Z ≥ z)

**Left-tailed test**

p = P(Z ≤ z)

The implementations use the normal cumulative distribution function and its upper-tail equivalent to calculate these probabilities.

### 3.1 Example p-value interpretation

| P-value | Interpretation |
|---|---|
| 0.001 | Strong evidence against H0 |
| 0.010 | Evidence against H0 |
| 0.030 | Evidence against H0 at 5% significance |
| 0.050 | At the 5% decision threshold |
| 0.080 | Insufficient evidence at 5% significance |
| 0.500 | Sample evidence is not unusual under H0 |

The strength of evidence cannot be determined from an isolated p-value without considering the research design, sample size, assumptions and practical effect.

## 4. Significance Level and Statistical Decisions

The significance level, represented by α, is the maximum Type I error probability permitted by the testing procedure under its assumptions.

Common values are:

| Alpha | Significance level |
|---|---|
| 0.10 | 10% |
| 0.05 | 5% |
| 0.01 | 1% |
| 0.001 | 0.1% |

The conventional 5% significance level is frequently used, but the appropriate threshold should be established according to the research context.

The decision rule is:

- If p-value ≤ α, reject H0.
- If p-value > α, fail to reject H0.

Failing to reject the null hypothesis does not establish that the null hypothesis is true.

It indicates that the available evidence does not meet the predefined rejection criterion.

### 4.1 Critical values

Critical values divide the sampling distribution into rejection and non-rejection regions.

For a two-sided Z-test with α = 0.05, the approximate critical values are:

z = -1.96 and z = +1.96

The null hypothesis is rejected when:

|z| > 1.96

For one-sided tests, the critical region is located in only one tail.

P-value and critical-value approaches provide equivalent decisions when they use the same test, assumptions and significance level.

## 5. Type I and Type II Errors

Hypothesis testing involves two important decision errors.

| Actual condition | Reject H0 | Fail to reject H0 |
|---|---|---|
| H0 is true | Type I error | Correct decision |
| H0 is false | Correct decision | Type II error |

### Type I error

A Type I error occurs when a true null hypothesis is rejected.

Its probability is controlled by the significance level under the assumptions of the test.

For α = 0.05, the procedure has a 5% Type I error rate in repeated applications when the null hypothesis is true and the test assumptions hold.

### Type II error

A Type II error occurs when a false null hypothesis is not rejected.

Its probability is represented by β.

The probability of detecting a specified effect is called statistical power.

Power = 1 - β

For example, a power of 0.80 represents an 80% probability of rejecting the null hypothesis for a particular alternative effect size, assuming the specified statistical model.

Power is influenced by:

- Sample size.
- Effect size.
- Population variability.
- Significance level.
- Statistical test selection.
- Experimental design.

Increasing sample size generally improves power when other factors remain unchanged.

## 6. Confidence Intervals

A confidence interval estimates a range of plausible population parameter values.

For a known population standard deviation, the two-sided confidence interval for the mean is:

x̄ ± z(α/2) × (σ / √n)

For a 95% confidence interval, the critical Z-value is approximately 1.96.

A 95% confidence interval procedure has 95% long-run coverage under its assumptions.

It does not mean that the fixed population parameter has a 95% probability of lying inside a particular already-calculated interval.

For a matching two-sided Z-test, exclusion of the null value from the confidence interval corresponds to rejection at the same significance level.

## 7. One-Sample Z-Test

The primary statistical procedure implemented across the source files is the one-sample Z-test.

It evaluates whether a population mean differs from a specified reference mean when the population standard deviation is known.

### Practical scenario

A manufacturing facility historically targets 100 units of production output per measurement period.

A sample of 20 observations is collected.

The research question is whether the actual population mean differs from 100.

The hypotheses are:

H0: μ = 100

H1: μ ≠ 100

Assumed population standard deviation:

σ = 8

Significance level:

α = 0.05

The procedure calculates:

1. Sample size.
2. Sample mean.
3. Standard error.
4. Z-statistic.
5. Two-sided p-value.
6. Confidence interval.
7. Statistical decision.

The result provides evidence about whether the observed difference is statistically significant.

The statistical conclusion must remain separate from operational conclusions. A statistically significant difference may be too small to matter practically.

### 7.1 Assumptions

The one-sample Z-test requires:

- Quantitative observations.
- Independent observations.
- A known population standard deviation.
- An appropriate normal sampling distribution for the sample mean.
- A properly specified null hypothesis.

The normal sampling distribution can arise from a normally distributed population or, under suitable conditions, from the central limit theorem.

A small sample from a strongly non-normal population may not satisfy the required assumptions.

When the population standard deviation is unknown, a one-sample t-test is generally more appropriate.

## 8. Multiple Hypothesis Testing

Testing multiple hypotheses introduces an additional statistical problem.

When many independent tests are conducted, the probability of obtaining at least one false positive increases.

For m independent tests with significance level α, the probability of at least one Type I error under the global null is:

1 - (1 - α)^m

For 20 independent tests at α = 0.05:

1 - (0.95)^20

This probability is approximately 0.642.

### 8.1 Bonferroni correction

The Bonferroni method controls the family-wise error rate by dividing the overall significance level by the number of tests.

Adjusted alpha = α / m

For five tests with an overall alpha of 0.05:

Adjusted alpha = 0.05 / 5 = 0.01

A hypothesis is rejected when its original p-value is at most 0.01.

The adjusted p-value can also be expressed as:

Adjusted p-value = min(1, m × original p-value)

Bonferroni correction is simple and conservative, particularly when many hypotheses are evaluated.

It does not require independence between the tests to provide family-wise error control when the individual tests satisfy their specified error guarantees.

## 9. Python Implementation

The Python implementation uses the standard library and provides a complete statistical workflow.

### Main components

| Component | Responsibility |
|---|---|
| `Alternative` | Represents the alternative hypothesis |
| `Decision` | Stores the statistical decision |
| `Hypothesis` | Validates the null mean and alpha |
| `TestResult` | Stores calculated test results |
| `normal_cdf()` | Calculates normal cumulative probability |
| `calculate_p_value()` | Evaluates the appropriate tail probability |
| `critical_z()` | Calculates a normal critical value |
| `one_sample_z_test()` | Performs the statistical test |
| `bonferroni_correction()` | Adjusts multiple-test significance |
| `simulate_null_distribution()` | Estimates Type I error through simulation |
| `calculate_sample_size()` | Estimates sample size for a specified effect and power |

The immutable dataclasses separate statistical configuration from calculated results.

Enums prevent inconsistent representations of test direction and decision states.

The implementation also validates observations, significance levels, population standard deviation and p-values.

### Simulation

The simulation repeatedly generates samples from a population whose mean equals the null-hypothesis mean.

It estimates the proportion of rejected null hypotheses.

This provides an empirical estimate of Type I error.

Because the simulation uses a finite number of repetitions, its estimated error rate may differ from the theoretical significance level.

## 10. JavaScript Implementation

The JavaScript implementation focuses on event-driven experiment management.

Its statistical calculations complement the Python implementation, while its architecture emphasizes asynchronous execution and experiment lifecycle management.

### Main components

| Component | Responsibility |
|---|---|
| `HypothesisTest` | Evaluates a one-sample Z-test |
| `MultipleTesting` | Applies Bonferroni correction |
| `Experiment` | Manages an individual experiment |
| `ExperimentRegistry` | Stores and executes experiments |
| `ExperimentState` | Tracks experiment lifecycle |
| `EventEmitter` | Publishes execution events |

The experiment lifecycle is:

CREATED → RUNNING → COMPLETED

An execution failure results in:

RUNNING → FAILED

The registry uses a `Map` for experiment identification and retrieval.

`Promise.allSettled()` permits independent experiments to execute concurrently without allowing one failed experiment to prevent the results of other experiments from being collected.

The implementation validates input data before statistical calculations.

Its normal distribution function uses a numerical approximation, so its p-values have finite approximation accuracy. For high-precision statistical production systems, a validated numerical statistics library should replace the approximation.

## 11. C++17 Implementation

The C++ implementation emphasizes explicit statistical domain modeling and controlled state management.

### Main components

| Component | Responsibility |
|---|---|
| `Hypothesis` | Represents statistical assumptions |
| `TestResult` | Stores statistical output |
| `StatisticalEngine` | Executes the Z-test |
| `MultipleTesting` | Evaluates corrected significance |
| `Experiment` | Stores experiment configuration and state |
| `ExperimentManager` | Registers and processes experiments |

The `enum class` definitions provide strongly typed alternatives, decisions and experiment states.

The `std::vector` container stores observations.

The `std::map` container provides ordered experiment identification.

The numerical implementation uses `std::erfc`, reducing the need for a custom approximation of the standard normal tail probability.

Exceptions handle invalid statistical configurations and execution errors.

The experiment manager records failed executions separately from successful evaluations.

This distinction prevents a failed computation from being presented as a statistically non-significant result.

## 12. Java 17 Implementation

The Java implementation models statistical testing as an enterprise service.

It separates statistical methods, experiment configuration, execution and audit records.

### Main components

| Component | Responsibility |
|---|---|
| `Hypothesis` | Immutable hypothesis definition |
| `ConfidenceInterval` | Represents confidence bounds |
| `TestResult` | Immutable evaluation result |
| `StatisticalTest` | Statistical testing interface |
| `NormalDistribution` | Normal probability calculations |
| `OneSampleZTest` | Implements the statistical procedure |
| `MultipleTestingService` | Applies multiple-test correction |
| `Experiment` | Controls execution state |
| `ExperimentService` | Registers and executes experiments |
| `AuditEvent` | Records experiment activities |

Java records provide compact immutable domain structures.

The `StatisticalTest` interface permits different statistical procedures to be introduced without changing the experiment service.

The experiment service maintains an audit trail of registration, execution and failure events.

The synchronized execution method prevents concurrent execution of the same experiment instance.

The implementation also uses immutable observation lists to prevent changes to the sample after experiment registration.

The normal distribution implementation uses a numerical approximation of the complementary error function. Its numerical precision is limited by that approximation.

## 13. PostgreSQL Database Design

The PostgreSQL implementation models hypothesis testing as a relational workflow.

### 13.1 Database entities

| Table | Purpose |
|---|---|
| `experiments` | Stores experiment definitions and lifecycle status |
| `hypotheses` | Stores null hypotheses and alternative hypotheses |
| `observations` | Stores individual sample measurements |
| `test_results` | Stores calculated statistical outcomes |
| `experiment_audit` | Records experiment lifecycle changes |

### 13.2 Entity relationships

Repository-style experiment organization is not required for statistical analysis. The relational structure instead follows the statistical hierarchy:

Experiment
→ Hypotheses
→ Observations
→ Statistical Results
→ Reporting

An experiment may contain multiple hypotheses.

Each hypothesis contains multiple observations.

Each completed statistical evaluation produces a separate result record.

This design preserves the distinction between raw sample measurements and calculated statistical outcomes.

### 13.3 Integrity controls

The database uses:

- Primary keys for entity identification.
- Foreign keys for relational integrity.
- Unique constraints for experiment and observation identifiers.
- Check constraints for significance levels and p-values.
- Indexes for experiment status and hypothesis-based retrieval.
- Triggers for observation validation and audit recording.
- Transactions for experiment processing.

The observation trigger prevents changes when an experiment is in an inappropriate lifecycle state.

The result table preserves individual evaluation records rather than overwriting previous results.

### 13.4 Database statistical functions

The SQL implementation includes:

| Function | Purpose |
|---|---|
| `normal_cdf()` | Calculates cumulative normal probability |
| `normal_survival()` | Calculates upper-tail probability |
| `calculate_p_value()` | Calculates one-sided or two-sided p-values |
| `calculate_critical_z()` | Determines the critical normal value |
| `execute_z_test()` | Performs a one-sample Z-test |

The `process_experiment()` procedure coordinates the evaluation of all hypotheses belonging to an experiment.

The procedure updates experiment state and handles execution failures.

### 13.5 Reporting

The database provides:

- Experiment readiness reporting.
- Insufficient-observation detection.
- Statistical result retrieval.
- Significant and non-significant test aggregation.
- Bonferroni multiple-testing evaluation.
- Audit history retrieval.

The reporting views separate operational experiment information from statistical result presentation.

## 14. Relationship Between Statistical Significance and Practical Significance

Statistical significance and practical significance represent different questions.

**Statistical significance** asks whether the observed evidence meets a predefined statistical rejection criterion.

**Practical significance** asks whether the estimated effect is sufficiently large to matter in the real-world context.

For example, a manufacturing process may produce a statistically significant increase of 0.2 units.

That difference may have little operational value despite a small p-value.

Conversely, an important operational difference may fail to achieve statistical significance when the sample is too small.

Research reports should therefore include:

- Estimated effect size.
- Confidence interval.
- Sample size.
- P-value.
- Significance level.
- Study assumptions.
- Practical interpretation.

A p-value should not be used as a replacement for effect-size analysis.

## 15. Important Distinctions

| Concept | What it represents | What it does not represent |
|---|---|---|
| Null hypothesis | Reference population assumption | Proof of equality |
| Alternative hypothesis | Competing statistical claim | Guaranteed research finding |
| Test statistic | Standardized evidence measure | Probability of H0 |
| P-value | Tail probability under H0 | Probability that H0 is true |
| Alpha | Predefined Type I error threshold | Probability that a particular result is false |
| Statistical significance | Decision under a statistical procedure | Practical importance |
| Confidence interval | Interval generated by a coverage procedure | Probability statement about a fixed parameter |
| Type I error | Rejecting a true H0 | Failing to detect an effect |
| Type II error | Failing to reject a false H0 | Accepting H0 as true |
| Statistical power | Probability of detecting a specified effect | Guaranteed detection |

## 16. Edge Cases and Failure Conditions

The implementations address several important failure conditions.

| Condition | Expected handling |
|---|---|
| Empty sample | Reject execution |
| One observation | Reject execution |
| Invalid alpha | Reject configuration |
| Zero population standard deviation | Reject configuration |
| Negative population standard deviation | Reject configuration |
| NaN or infinite observations | Reject input |
| Invalid alternative hypothesis | Reject configuration |
| P-value outside [0, 1] | Reject multiple-testing input |
| Duplicate experiment identifier | Reject registration |
| Experiment executed twice | Reject invalid state transition |
| Insufficient SQL observations | Raise execution exception |
| SQL processing failure | Mark experiment as failed |

A failed statistical evaluation must not be interpreted as evidence supporting either hypothesis.

## 17. Performance and Security Considerations

### Performance

The statistical calculations operate on a sample of size n.

| Operation | Time complexity |
|---|---|
| Sample mean calculation | O(n) |
| Standard error calculation | O(1) |
| Z-statistic calculation | O(1) |
| P-value calculation | O(1) |
| Bonferroni correction | O(m) |
| Experiment lookup using a hash map | Expected O(1) |
| Ordered experiment lookup using a tree map | O(log e) |

Here:

- n represents the sample size.
- m represents the number of statistical tests.
- e represents the number of registered experiments.

For large datasets, database aggregation and indexed retrieval reduce unnecessary transfer of raw observations into application memory.

### Security

Statistical experiment systems should protect:

- Confidential sample observations.
- Research participant information.
- Experiment ownership.
- Statistical result integrity.
- Audit history.
- Database access credentials.

Applications should use parameterized SQL, role-based permissions, restricted database privileges and encrypted connections.

Sensitive observations should not be written to application logs.

Experiment configurations and results should be retained with sufficient metadata to support reproducibility and independent verification.

## 18. Limitations of the Implementations

The five implementations focus on one-sample Z-testing and Bonferroni correction.

They do not implement every statistical testing procedure.

Important methods outside the current implementation include:

- One-sample t-test.
- Independent two-sample t-test.
- Paired t-test.
- Chi-square test.
- ANOVA.
- Mann-Whitney U test.
- Wilcoxon signed-rank test.
- Fisher's exact test.
- Pearson correlation significance testing.
- Regression coefficient hypothesis testing.
- Bootstrap hypothesis testing.
- Permutation testing.
- False discovery rate correction using Benjamini-Hochberg.

The implementations assume a known population standard deviation and independent observations.

The sample-size calculation in Python is an approximate normal-theory calculation for a two-sided one-sample test.

The JavaScript and Java numerical distribution approximations have lower precision than dedicated high-accuracy statistical implementations.

The PostgreSQL workflow also requires careful transaction and permission management in production. Its audit trigger records lifecycle changes, but a production audit system should restrict direct modification and deletion of historical records.

The choice of statistical procedure must be determined by the research question, measurement scale, sampling design, distributional assumptions and dependence structure.

## 19. Execution

| File | Runtime | Execution |
|---|---|---|
| Python | Python 3.10+ | `python hypothesis_testing.py` |
| JavaScript | Node.js 18+ | `node hypothesis_testing.js` |
| C++17 | C++17 compiler | `g++ -std=c++17 -O2 hypothesis_testing.cpp -o hypothesis_testing` |
| Java | Java 17 | `javac HypothesisTesting.java` followed by `java HypothesisTesting` |
| PostgreSQL | PostgreSQL 15+ | Execute the SQL script using `psql` |

The Python, JavaScript, C++17 and Java implementations use standard language capabilities without third-party dependencies.

The SQL implementation creates a dedicated schema and its associated statistical workflow.

## 20. Educational Outcomes

The implementations demonstrate the progression from statistical assumptions to computational evaluation and structured reporting.

The central workflow is:

Research Question
→ Null and Alternative Hypotheses
→ Sampling Design
→ Sample Observations
→ Test Statistic
→ P-value
→ Significance Comparison
→ Statistical Decision
→ Confidence Interval
→ Interpretation
→ Audit and Reporting

The essential discipline in hypothesis testing is to define the research question, assumptions, alternative hypothesis and significance threshold before evaluating the observed data. Statistical conclusions must remain consistent with the test design and the limitations of the available evidence.
