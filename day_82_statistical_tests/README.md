# Statistical Tests: t-test, z-test, Chi-square Test and ANOVA

## 1. Statistical Testing Framework

Statistical hypothesis testing provides a formal method for evaluating claims about populations using sample observations.

A statistical test compares observed evidence against a null hypothesis and quantifies how compatible the observations are with that hypothesis.

The four major categories implemented in this project are:

| Test | Primary purpose | Data type | Main statistic |
|---|---|---|---|
| t-test | Compare population means when population variance is unknown | Quantitative | t |
| z-test | Test population means or proportions using a known standard error | Quantitative or binary | z |
| Chi-square test | Evaluate categorical frequencies and associations | Categorical | χ² |
| ANOVA | Compare means across multiple independent groups | Quantitative | F |

These tests answer different statistical questions. Selecting a test requires identifying the research question, measurement scale, sample structure, sampling assumptions and available population information.

## 2. Hypothesis Testing Fundamentals

### 2.1 Null and Alternative Hypotheses

The null hypothesis, represented by H0, describes a reference condition such as equality, independence or a specified population parameter.

The alternative hypothesis, represented by H1 or Ha, describes the departure being investigated.

For a two-sided mean comparison:

- H0: μ = μ0
- H1: μ ≠ μ0

For a directional comparison:

- H0: μ ≤ μ0
- H1: μ > μ0

The statistical test must be selected according to the research question before inspecting the result.

### 2.2 Significance Level

The significance level, α, specifies the maximum probability of a Type I error under the testing procedure.

A common choice is:

α = 0.05

A Type I error occurs when a true null hypothesis is rejected.

A Type II error occurs when a false null hypothesis is not rejected.

Statistical power is the probability of correctly rejecting a false null hypothesis.

Power depends on:

- Sample size.
- Effect magnitude.
- Population variability.
- Significance level.
- Test design.
- Direction of the alternative hypothesis.

A statistically insignificant result does not establish that two populations are identical.

### 2.3 Test Statistic

A test statistic measures the discrepancy between observed data and the null hypothesis, expressed in units determined by its sampling distribution.

Examples include:

- t-statistic for t-tests.
- z-statistic for z-tests.
- Chi-square statistic for categorical frequency tests.
- F-statistic for ANOVA.

### 2.4 P-value

A p-value represents the probability, assuming the null hypothesis and model assumptions are true, of observing a test statistic at least as extreme as the one obtained.

It is not:

- The probability that H0 is true.
- The probability that the observed finding occurred by chance.
- The magnitude of the treatment effect.
- The probability that the result will replicate.

The decision rule for a conventional significance test is:

- If p < α, reject H0.
- If p ≥ α, fail to reject H0.

The distinction between failing to reject and accepting the null hypothesis is important.

### 2.5 Confidence Intervals

A confidence interval provides a range of parameter values compatible with the observed data under the specified confidence procedure.

A 95% confidence procedure has a long-run coverage interpretation: across repeated applications under its assumptions, approximately 95% of the resulting intervals contain the true parameter.

Confidence intervals help communicate estimation uncertainty and practical relevance beyond a binary significance decision.

## 3. t-tests

A t-test evaluates hypotheses about population means when the population standard deviation is unknown and must be estimated from sample data.

The Student's t-distribution accounts for uncertainty introduced by estimating population variability.

### 3.1 One-Sample t-test

The one-sample t-test compares a sample mean with a specified reference population mean.

Example:

A manufacturer claims that the average production measurement equals 50 units. A sample is collected to investigate whether the population mean differs from that value.

The test statistic is:

t = (x̄ - μ0) / (s / √n)

Where:

| Symbol | Meaning |
|---|---|
| x̄ | Sample mean |
| μ0 | Hypothesized population mean |
| s | Sample standard deviation |
| n | Sample size |
| df | Degrees of freedom, n - 1 |

The null hypothesis is:

H0: μ = μ0

The alternative hypothesis for a two-sided test is:

H1: μ ≠ μ0

The implementation calculates:

- Sample mean.
- Sample variance.
- Standard error.
- t-statistic.
- Degrees of freedom.
- Two-sided p-value.
- Standardized mean difference.
- Confidence interval for the mean difference.

### 3.2 Independent Two-Sample t-test

An independent two-sample t-test compares the means of two unrelated populations.

Example:

A research team compares production measurements from a control process and an improved process.

The two groups contain different observational units.

The Welch test statistic is:

t = (x̄1 - x̄2) / √(s1²/n1 + s2²/n2)

The Welch-Satterthwaite approximation estimates the degrees of freedom:

df = (s1²/n1 + s2²/n2)² / [(s1²/n1)²/(n1-1) + (s2²/n2)²/(n2-1)]

Welch's test does not require equal population variances.

It is generally a suitable default for independent mean comparisons when equal variance cannot be justified.

The pooled-variance t-test is another formulation. It assumes equal population variances and uses a pooled variance estimate.

The Python implementation supports both approaches.

### 3.3 Paired t-test

A paired t-test evaluates the mean of within-pair differences.

Example:

A performance study measures the same participants before and after an intervention.

The difference for each participant is:

di = Afteri - Beforei

The test becomes a one-sample t-test on the difference observations:

t = d̄ / (sd / √n)

Degrees of freedom:

df = n - 1

The observations must be meaningfully paired.

Treating paired observations as independent discards the within-subject relationship and can produce incorrect uncertainty estimates.

### 3.4 t-test Assumptions

Important assumptions include:

- Quantitative outcome measurements.
- Appropriate sampling and study design.
- Independent observations where required.
- Approximately normal sampling behavior for small samples.
- Absence of severe influential outliers.
- Equal population variances for the pooled independent t-test.

The paired test requires the differences, rather than the original measurements independently, to satisfy the relevant distribution assumptions.

Large samples can improve the robustness of mean-based inference, but they do not eliminate problems caused by dependence, biased sampling or severe data contamination.

## 4. z-tests

A z-test uses the standard normal distribution to evaluate a hypothesis about a population parameter.

For a one-sample population mean test with known population standard deviation:

z = (x̄ - μ0) / (σ / √n)

Where:

| Symbol | Meaning |
|---|---|
| x̄ | Sample mean |
| μ0 | Hypothesized population mean |
| σ | Known population standard deviation |
| n | Sample size |

The two-sided p-value is:

p = 2P(Z ≥ |z|)

The implementation uses the standard normal cumulative distribution and complementary error function.

### 4.1 When to Use a z-test

A z-test is appropriate for a mean comparison when population standard deviation is genuinely known and the sampling model is appropriate.

It is also used for large-sample proportion inference when the relevant normal approximation conditions hold.

The sample size alone does not automatically make a test a z-test. The assumptions and parameter estimation method determine the appropriate procedure.

### 4.2 z-test and t-test Distinction

| Characteristic | z-test | t-test |
|---|---|---|
| Population standard deviation | Known for the implemented mean test | Unknown |
| Variability | Uses σ | Uses sample estimate s |
| Reference distribution | Standard normal | Student's t |
| Degrees of freedom | Not applicable | Required |
| Typical application | Known population variance | Estimated population variance |

As degrees of freedom increase, the t-distribution approaches the standard normal distribution.

### 4.3 Limitations

The implemented z-test addresses a one-sample mean comparison.

It does not implement the separate one-proportion, two-proportion or two-sample mean z-test formulations.

These procedures have different standard-error calculations and should not be substituted without examining the sampling design.

## 5. Chi-square Tests

Chi-square tests examine categorical frequency data.

They compare observed frequencies with expected frequencies under a specified probability model.

The general statistic is:

χ² = Σ (O - E)² / E

Where:

- O represents an observed frequency.
- E represents its expected frequency.

The chi-square distribution provides the reference distribution for the statistic under the relevant null hypothesis and assumptions.

### 5.1 Chi-square Goodness-of-Fit Test

The goodness-of-fit test examines whether observed categorical frequencies differ from a specified expected distribution.

Example:

A manufacturer expects four production categories to occur equally frequently.

For a total of 200 observations, expected frequencies are:

| Category | Expected frequency |
|---|---:|
| A | 50 |
| B | 50 |
| C | 50 |
| D | 50 |

Observed frequencies:

| Category | Observed frequency |
|---|---:|
| A | 45 |
| B | 55 |
| C | 50 |
| D | 50 |

The degrees of freedom, when no distribution parameters are estimated from the observations, are:

df = k - 1

Where k is the number of categories.

When parameters are estimated from the data, the degrees of freedom must be adjusted appropriately.

### 5.2 Chi-square Test of Independence

The independence test investigates whether two categorical variables are statistically associated.

Example:

A market research organization examines the relationship between customer segment and product preference.

A contingency table contains:

| Customer segment | Preference A | Preference B |
|---|---:|---:|
| Segment 1 | 40 | 20 |
| Segment 2 | 30 | 50 |

The expected frequency for a cell is:

Eij = (Row Total × Column Total) / Grand Total

Degrees of freedom:

df = (r - 1)(c - 1)

Where:

- r is the number of rows.
- c is the number of columns.

A statistically significant result indicates evidence against independence.

It does not establish causation or identify the direction of an association.

### 5.3 Cramer's V

Cramer's V measures the strength of association in a contingency table.

V = √[χ² / (n × min(r - 1, c - 1))]

Where n represents the total frequency.

Cramer's V is useful because statistical significance alone does not describe the practical magnitude of an association.

### 5.4 Chi-square Assumptions

Important requirements include:

- Frequency-based categorical observations.
- Mutually exclusive categories.
- Independent observational units.
- Positive expected frequencies.
- An appropriate expected-frequency approximation.

The conventional chi-square approximation can become unreliable when expected cell counts are sparse.

For a 2 × 2 table, Fisher's exact test may be more appropriate under sparse conditions.

For larger tables, exact or Monte Carlo procedures may be required.

The implementations validate zero expected frequencies but do not automatically replace the asymptotic test with an exact procedure.

## 6. Analysis of Variance (ANOVA)

Analysis of Variance compares the means of multiple groups.

One-way ANOVA evaluates whether at least one group population mean differs from the others.

Example:

A manufacturer compares three production lines to determine whether their average output measurements differ.

The null hypothesis is:

H0: μ1 = μ2 = μ3 = ... = μk

The alternative hypothesis is:

H1: At least one population mean differs.

### 6.1 ANOVA Components

ANOVA divides total variability into two components.

Between-group variability measures differences among group means.

Within-group variability measures variation among observations belonging to the same group.

Total sum of squares:

SST = SSB + SSW

Between-group sum of squares:

SSB = Σ ni(x̄i - x̄)²

Within-group sum of squares:

SSW = Σ Σ(xij - x̄i)²

Where:

- ni represents the sample size of group i.
- x̄i represents the mean of group i.
- x̄ represents the grand mean.
- xij represents an individual observation.

### 6.2 Mean Squares

Between-group mean square:

MSB = SSB / (k - 1)

Within-group mean square:

MSW = SSW / (N - k)

Where:

- k is the number of groups.
- N is the total number of observations.

### 6.3 F-statistic

The ANOVA statistic is:

F = MSB / MSW

The statistic follows an F-distribution under the null hypothesis and the model assumptions.

Its degrees of freedom are:

- Numerator: k - 1.
- Denominator: N - k.

A large F-statistic provides evidence against equal population means.

### 6.4 Effect Size: Eta-Squared

Eta-squared measures the proportion of total observed variation associated with group membership.

η² = SSB / SST

The result ranges from zero to one when total variability is positive.

A larger value indicates that a greater proportion of observed variation is associated with differences among the groups.

### 6.5 ANOVA Assumptions

One-way ANOVA commonly relies on:

- Independent observations.
- Approximately normal residual distributions within groups.
- Homogeneity of population variances.
- Quantitative dependent variables.
- Appropriate sampling and experimental design.

Severe variance inequality can make conventional ANOVA inappropriate.

Welch's ANOVA provides an alternative when population variances differ.

The implementations cover conventional one-way ANOVA rather than Welch's ANOVA.

### 6.6 Post-Hoc Comparisons

A significant ANOVA result establishes that not all population means are equal.

It does not identify which specific groups differ.

Post-hoc procedures can investigate individual comparisons.

Examples include:

- Tukey's honestly significant difference procedure.
- Bonferroni-adjusted pairwise tests.
- Holm-adjusted comparisons.
- Games-Howell comparisons for unequal variances.

The implementations include Bonferroni adjustment for collections of p-values.

They do not implement Tukey's or Games-Howell procedures.

## 7. Comparison of Statistical Tests

| Research question | Recommended test | Important condition |
|---|---|---|
| Is one sample mean different from a reference? | One-sample t-test | Population variance estimated |
| Are two independent means different? | Independent t-test | Independent groups |
| Are two related measurements different? | Paired t-test | Valid paired observations |
| Is a sample mean different from a reference with known population SD? | z-test | Known population SD |
| Does an observed categorical distribution match an expected distribution? | Chi-square goodness-of-fit | Frequency observations |
| Are two categorical variables associated? | Chi-square independence | Contingency table |
| Do three or more independent group means differ? | One-way ANOVA | Independent groups and conventional ANOVA assumptions |

## 8. Multiple Hypothesis Testing

Running several statistical tests increases the probability of obtaining at least one false positive.

For m independent tests, each conducted at significance level α, the family-wise probability of at least one Type I error is:

FWER = 1 - (1 - α)^m

The Bonferroni method adjusts the threshold:

αadjusted = α / m

An equivalent adjusted p-value is:

padjusted = min(1, m × p)

The project implements adjusted p-values using this second formulation.

Bonferroni correction controls the family-wise error rate without requiring independence among the tests, although it can be conservative.

The Holm procedure is another family-wise error correction that is generally less conservative.

False discovery rate procedures address a different objective and should not be confused with family-wise error control.

## 9. Python Implementation

The Python file provides a self-contained numerical statistical engine.

### 9.1 Core Components

| Component | Responsibility |
|---|---|
| `StatisticalError` | Invalid input and statistical configuration |
| `TestResult` | Immutable representation of test output |
| `TestType` | Classification of supported tests |
| `validate_sample` | Observation validation |
| `variance` | Sample variance estimation |
| `regularized_beta` | Incomplete beta evaluation |
| `regularized_gamma_q` | Upper incomplete gamma evaluation |
| `t_two_sided_p` | Two-sided t-distribution probability |
| `chi_square_p` | Chi-square upper-tail probability |
| `f_distribution_p` | F-distribution upper-tail probability |

### 9.2 Numerical Algorithms

The implementation uses:

- Continued fractions for the incomplete beta function.
- Series expansion and continued fractions for the incomplete gamma function.
- Log-gamma evaluation for numerical stability.
- Binary search for the t-distribution critical value.

These calculations avoid requiring SciPy or another external statistical package.

### 9.3 Validation

The script checks:

- Minimum sample sizes.
- Finite observations.
- Valid significance levels.
- Positive expected frequencies.
- Rectangular contingency tables.
- Matching paired sample lengths.
- Nonzero sampling variance.
- Positive degrees of freedom.

The examples also include numerical assertions.

### 9.4 Performance

Most sample-based calculations have linear complexity in the number of observations.

- Mean: O(n).
- Variance: O(n).
- One-sample t-test: O(n).
- Welch t-test: O(n + m).
- Paired t-test: O(n).
- One-way ANOVA: O(N).
- Chi-square contingency calculation: O(rc).

The distribution calculations use iterative numerical methods with bounded convergence loops.

For repeated analysis of large datasets, intermediate statistics should be cached when the underlying observations have not changed.

## 10. JavaScript Implementation

The JavaScript implementation adopts an event-driven experiment-management approach.

### 10.1 Numerical Engine

The `Statistics` object provides:

- Descriptive statistics.
- Distribution probability calculations.
- Welch independent t-test.
- Paired t-test.
- One-sample z-test.
- Chi-square independence.
- One-way ANOVA.

Its incomplete beta and incomplete gamma implementations support the relevant distribution probabilities.

### 10.2 Experiment Management

The `Experiment` class extends Node.js `EventEmitter`.

It manages experiments through a private `Map`.

The event lifecycle includes:

| Event | Meaning |
|---|---|
| `registered` | Experiment accepted |
| `started` | Execution initiated |
| `completed` | Result successfully calculated |
| `failed` | Execution encountered an error |

The manager supports asynchronous execution using Promises.

`executeAll()` applies bounded batches to prevent uncontrolled task creation.

`Promise.allSettled()` ensures that one failed experiment does not automatically discard successful results from other experiments.

### 10.3 State Management

Each experiment contains:

- Unique identifier.
- Statistical function.
- Immutable metadata.

The manager returns structured execution results.

This separation makes it possible to distinguish experiment registration, execution and reporting.

### 10.4 Practical Considerations

An event-driven design is useful when multiple independent statistical analyses must be processed.

For production deployment, additional controls should include:

- Persistent experiment records.
- Structured logging.
- Request authentication.
- Execution time limits.
- Data access controls.
- Numerical precision validation.
- Versioned statistical procedures.

The implementation is a local execution model rather than a distributed statistical processing platform.

## 11. C++17 Implementation

The C++ program emphasizes explicit domain modeling and computational control.

### 11.1 Statistical Engine

`StatisticalEngine` contains the core statistical algorithms.

The implementation uses:

- `vector` for observations.
- `struct` for result representation.
- `enum class` for test categories.
- STL algorithms for descriptive statistics.
- Exceptions for invalid statistical conditions.

The engine provides:

- One-sample t-test.
- Welch independent t-test.
- Paired t-test.
- One-sample z-test.
- Chi-square independence.
- Chi-square goodness-of-fit.
- One-way ANOVA.

### 11.2 Governance Engine

`GovernanceEngine` separates statistical computation from result management.

It stores completed test results and produces:

- Tabular reports.
- Statistical decisions.
- Bonferroni-adjusted p-values.

This separation avoids coupling numerical algorithms to reporting logic.

### 11.3 Numerical Stability

The program uses:

- `lgamma()` for logarithmic gamma evaluation.
- `erfc()` for normal distribution probabilities.
- Continued fractions for incomplete beta calculations.
- Incomplete gamma calculations for chi-square probabilities.
- Bounded iterative convergence.

The approach reduces numerical overflow and underflow risks associated with direct factorial and gamma calculations.

### 11.4 Resource Considerations

The implementation uses contiguous dynamic arrays through `std::vector`.

This supports efficient sequential processing and avoids unnecessary allocation of complex objects.

The principal calculations are linear in observation count, except for the numerical distribution evaluation.

The program requires a C++17-compatible compiler and no third-party dependencies.

## 12. Java 17 Implementation

The Java implementation uses enterprise-oriented domain structures and explicit statistical policies.

### 12.1 Domain Model

| Type | Purpose |
|---|---|
| `TestCategory` | Identifies the statistical procedure |
| `StatisticalException` | Represents domain validation errors |
| `TestPolicy` | Defines significance requirements |
| `TestResult` | Immutable statistical result |
| `Sample` | Validated observation collection |
| `StatisticalTest` | Common test execution interface |
| `Distribution` | Numerical distribution calculations |
| `TestService` | Statistical computation service |
| `ExperimentRegistry` | Experiment registration and execution |
| `ResearchReport` | Reporting and multiple-testing adjustment |

### 12.2 Immutable Structures

Java records represent:

- Samples.
- Test results.
- Statistical policies.

`List.copyOf()` prevents external modification of registered sample observations.

This makes result processing easier to reason about and reduces accidental state mutation.

### 12.3 Service Separation

`TestService` owns statistical calculations.

`ExperimentRegistry` manages experiment registration and asynchronous execution.

`ResearchReport` manages result collection and reporting.

This structure separates domain logic from orchestration and presentation.

### 12.4 Asynchronous Execution

`CompletableFuture` supports asynchronous experiment processing.

Independent experiments can execute concurrently.

The implementation uses immutable result records, which reduces shared mutable state during concurrent reporting.

A production application should also configure:

- A dedicated execution pool.
- Maximum concurrency.
- Cancellation behavior.
- Persistent execution status.
- Retry rules.
- Timeouts.
- Transaction boundaries for stored results.

### 12.5 Enterprise Validation

The implementation validates sample size, finite observations, significance levels, contingency table dimensions and distribution parameters.

It also rejects invalid statistical states such as zero within-group variance in conventional ANOVA.

## 13. PostgreSQL Implementation

The database implementation models a relational research workflow.

### 13.1 Relational Architecture

The principal relationships are:

Researchers → Experiments → Samples → Observations

Experiments → Test Results

Experiments → Test Audit

The database separates raw observations from calculated results.

This distinction is important for research reproducibility.

A calculated p-value should never replace the underlying observations.

### 13.2 Researchers

The `researchers` table identifies the individual responsible for an experiment.

Each experiment references a researcher through a foreign key.

This supports accountability and researcher-level reporting.

### 13.3 Experiments

The `experiments` table stores:

- Experiment identifier.
- Experiment code.
- Researcher.
- Test category.
- Significance level.
- Null hypothesis.
- Alternative hypothesis.
- Execution status.
- Creation and completion timestamps.

The experiment status follows a controlled lifecycle:

REGISTERED → RUNNING → COMPLETED

An experiment can also enter the FAILED state.

Terminal-state protection prevents completed or failed experiments from being silently reopened through ordinary status updates.

### 13.4 Samples and Observations

The `samples` table associates observations with a particular experiment.

The `observations` table stores individual measurements.

This normalized structure avoids duplicating experiment information for every measurement.

The database also supports:

- Sample roles.
- Category labels.
- Paired observation identifiers.
- Observation timestamps.

The sample statistics view calculates:

- Sample size.
- Mean.
- Variance.
- Standard deviation.
- Minimum.
- Maximum.

### 13.5 Test Results

The `test_results` table stores:

- Test statistic.
- P-value.
- Degrees of freedom.
- Effect size.
- Confidence level.
- Statistical decision.
- Calculation timestamp.

A unique constraint ensures one stored result per experiment in this implementation.

The result is linked to its originating experiment.

### 13.6 Numerical Database Functions

The SQL script implements:

| Function | Purpose |
|---|---|
| `log_gamma` | Logarithmic gamma evaluation |
| `beta_fraction` | Continued-fraction evaluation |
| `beta_regularized` | Regularized incomplete beta |
| `gamma_q` | Upper incomplete gamma |
| `normal_cdf` | Normal cumulative distribution |
| `normal_two_sided_p` | Two-sided normal probability |
| `t_two_sided_p` | Two-sided t probability |
| `chi_square_p` | Chi-square upper-tail probability |
| `f_distribution_p` | F-distribution upper-tail probability |

These functions support statistical calculations directly inside PostgreSQL.

### 13.7 Database Transactions

The execution workflow uses explicit transactions.

The intended sequence is:

1. Validate experiment eligibility.
2. Mark the experiment as running.
3. Retrieve the observations.
4. Calculate the statistical result.
5. Insert the result.
6. Mark the experiment completed.
7. Commit the transaction.

If a calculation or database operation fails, the transaction can be rolled back.

This prevents a partially persisted experiment result.

### 13.8 Indexing

Indexes support common retrieval patterns.

Examples include:

- Researcher and experiment date.
- Experiment status and category.
- Observations by sample.
- Paired observations.
- Results by p-value.
- Audit records by experiment and timestamp.

The appropriate indexes depend on actual query frequency and table size.

Excessive indexing increases storage consumption and write overhead.

### 13.9 Database Limitations

The database script demonstrates the principal research workflow and selected test procedures.

The one-sample t-test, Welch test, z-test and one-way ANOVA have execution functions.

The chi-square independence routine also illustrates categorical matrix construction, but its sample representation requires consistent row and column pairing. A production contingency table should use an explicit cell-level schema with separate row and column category identifiers.

The schema does not implement every statistical procedure.

Specifically:

- The SQL workflow does not implement paired t-test execution.
- Chi-square goodness-of-fit is represented by the distribution function but has no dedicated execution function.
- The SQL ANOVA function uses conventional one-way ANOVA.
- The z-test function implements a one-sample mean test.
- Exact tests for sparse contingency tables are not included.
- Confidence interval calculations are not persisted by the execution functions.

These limitations distinguish the implemented database operations from the broader statistical capabilities of the programming-language implementations.

## 14. Effect Sizes and Practical Significance

Statistical significance and practical significance are different concepts.

A very large sample can produce a small p-value for a negligible effect.

A smaller sample can fail to detect a practically important effect because of insufficient statistical power.

The project includes several effect-size measures.

| Test | Effect size |
|---|---|
| One-sample t-test | Standardized mean difference |
| Independent t-test | Standardized mean difference where available |
| Chi-square independence | Cramer's V |
| Chi-square goodness-of-fit | Square root of chi-square divided by total frequency |
| ANOVA | Eta-squared |

Effect sizes should be interpreted using the subject domain, study design and measurement scale.

Universal numerical thresholds are not appropriate for every research application.

## 15. Assumption Checking and Research Quality

A valid statistical calculation does not guarantee a valid scientific conclusion.

Statistical assumptions must be examined independently.

### 15.1 Independence

Independence concerns the relationship between observations.

Repeated measurements, clustered samples and related subjects require appropriate statistical models.

Ignoring dependence can underestimate uncertainty.

### 15.2 Normality

Normality is particularly relevant for small-sample mean-based inference.

Useful diagnostic approaches include:

- Histograms.
- Q-Q plots.
- Residual analysis.
- Shapiro-Wilk testing.

A normality test should not be used as an automatic decision mechanism without considering sample size and the study design.

### 15.3 Homogeneity of Variance

Conventional independent t-tests and one-way ANOVA can rely on equal population variances.

Levene's test and Brown-Forsythe procedures can investigate variance equality.

Welch procedures provide alternatives when unequal variances are plausible.

### 15.4 Outliers

Extreme observations can strongly influence:

- Means.
- Variances.
- t-statistics.
- F-statistics.
- Standard errors.

Outliers should be investigated using data provenance and measurement context.

Removing observations solely because they change a p-value introduces analytical bias.

### 15.5 Sample Selection

Statistical inference is only as credible as the sampling and experimental design.

Convenience sampling, missing observations, nonresponse and selection bias can limit population-level conclusions even when the mathematical calculations are correct.

## 16. Security, Reproducibility and Operational Controls

Research analytics systems should protect the integrity and confidentiality of their observations and results.

Important controls include:

- Role-based database access.
- Restricted modification of completed experiments.
- Parameterized database queries.
- Audit logging.
- Controlled observation retention.
- Secure backup and recovery.
- Versioned statistical methods.
- Reproducible data transformations.
- Explicit missing-data handling.
- Recorded significance levels and hypotheses.

For sensitive research data, access should follow the principle of least privilege.

Statistical outputs may also disclose sensitive information when sample groups are very small.

Aggregation and disclosure controls should therefore be considered before reporting results.

## 17. Reproducibility and Interpretation

A reproducible statistical experiment should retain:

1. Research question.
2. Null and alternative hypotheses.
3. Sampling methodology.
4. Original observations.
5. Data-cleaning procedures.
6. Selected statistical test.
7. Test assumptions.
8. Significance level.
9. Test statistic.
10. Degrees of freedom.
11. P-value.
12. Effect size.
13. Confidence interval where applicable.
14. Multiple-testing adjustment.
15. Software and method version.

A statistical result should be interpreted within this complete context.

A low p-value without effect-size information, sampling context and assumption assessment is insufficient for a strong research conclusion.

## 18. Execution and File Organization

The six deliverables are designed as independent implementations.

| File | Runtime | Primary role |
|---|---|---|
| `statistical_tests.py` | Python 3.10+ | Numerical statistical toolkit |
| `statistical_tests.js` | Node.js 18+ | Event-driven experiment processing |
| `statistical_tests.cpp` | C++17 compiler | Computational statistical engine |
| `StatisticalTests.java` | Java 17 | Enterprise research analytics |
| `statistical_tests.sql` | PostgreSQL 15+ | Relational research workflow |
| `README.md` | Markdown | Statistical concepts and implementation documentation |

The programming-language implementations require no third-party packages.

The PostgreSQL implementation uses standard PostgreSQL procedural language capabilities and built-in mathematical functions.

Each source implementation provides its own sample datasets and executable examples.

The numerical algorithms use floating-point approximations. Results may differ slightly between implementations because of floating-point precision, convergence tolerances and distribution-function approximations.

For regulated, clinical or high-stakes research, numerical implementations should be independently validated against established statistical reference procedures and documented test datasets before operational use.
