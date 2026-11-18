# Sampling Theory: Statistical Design and Analysis

## 1. Domain Overview

Sampling theory provides mathematical and practical methods for selecting a subset of observations from a defined population. The objective is to obtain information about the population while controlling sampling uncertainty, operational cost, and potential selection errors.

The implementations use an enterprise workforce population containing employee identifiers, departments, ages, incomes, and numerical outcomes.

The central workflow is:

Population definition
        |
        v
Eligibility assessment
        |
        v
Sampling design
        |
        v
Sample-size determination
        |
        v
Sample selection
        |
        v
Response collection
        |
        v
Representation and bias diagnostics
        |
        v
Statistical estimation
        |
        v
Quality assessment and reporting

Four distinct concepts are examined:

- Random sampling determines how observations are selected.
- Stratified sampling ensures representation across defined population groups.
- Sampling bias concerns systematic differences between the selected or responding observations and the intended population.
- Sample-size determination establishes how many observations are needed to achieve a specified statistical precision.

A large sample does not automatically produce an unbiased estimate. The quality of a sampling design depends on its population frame, selection mechanism, inclusion probabilities, response behavior, and statistical analysis.

## 2. Population, Sampling Frame, and Sample

### Population

A population is the complete collection of units about which an investigation intends to make statements.

The example population contains 1,000 employees distributed across four departments:

| Department | Population proportion |
|---|---:|
| Engineering | 40% |
| Finance | 20% |
| Operations | 25% |
| Research | 15% |

Each employee has a unique identifier and associated characteristics.

### Sampling frame

A sampling frame is the operational list from which units can actually be selected.

The intended population and the sampling frame are not necessarily identical.

For example, a survey targeting all employees may use an employee register that excludes contractors. This creates undercoverage if contractors belong to the intended population.

Other frame problems include:

- Duplicate records.
- Outdated records.
- Ineligible observations.
- Missing population groups.
- Incorrect identifiers.
- Incomplete demographic information.

The PostgreSQL implementation separates population snapshots from individual population units. Eligibility is explicitly recorded, allowing the selection process to operate against a defined frame.

### Sample

A sample is the subset selected from the sampling frame.

Let:

- \(N\) = population size.
- \(n\) = sample size.
- \(f=n/N\) = sampling fraction.

For a population of 1,000 employees and a sample of 100:

\[
f=\frac{100}{1000}=0.10
\]

The sampling fraction is 10%.

A sample is useful only when its selection mechanism and resulting observations support the intended population inference.

## 3. Random Sampling

Simple random sampling selects observations using a probability mechanism.

Every population unit has an equal probability of selection when sampling without replacement:

\[
P(i\in S)=\frac{n}{N}
\]

For a population of 1,000 and a sample of 100:

\[
P(i\in S)=0.10
\]

The defining characteristic is the selection probability, not merely the appearance of randomness.

### Sampling without replacement

Once an observation has been selected, it cannot be selected again.

The Python implementation uses `random.sample()`, the JavaScript implementation uses Fisher-Yates shuffling, and the C++ implementation uses `std::shuffle`.

The SQL implementation ranks eligible population units using a deterministic hash based on their identifiers and the configured seed.

These approaches provide reproducible simulations or selections under their respective execution environments.

### Random seeds

A seed initializes a pseudorandom number generator.

Using the same seed and unchanged input data makes a simulation reproducible.

This is important for:

- Statistical experiments.
- Debugging.
- Comparing sampling methods.
- Automated testing.
- Reproducing research results.

A pseudorandom seed does not make a selection cryptographically secure.

The JavaScript implementation demonstrates a separate cryptographically secure random index using Node.js `crypto.randomInt()`.

For sensitive operational selection, random-number generation, access controls, auditability, and protection against manipulation must be considered independently.

### Sampling with and without replacement

| Characteristic | With replacement | Without replacement |
|---|---|---|
| Previously selected unit | May appear again | Cannot appear again |
| Number of unique observations | May be smaller than n | Exactly n |
| Selection dependence | Independent draws under the usual design | Sequential draws are dependent |
| Typical application | Bootstrap resampling | Population surveys |

The implementations primarily use sampling without replacement.

## 4. Stratified Sampling

Stratified sampling divides a population into mutually exclusive groups called strata.

The strata are defined using characteristics that are relevant to the research question.

For the workforce population, department is the stratification variable.

The four strata are:

- Engineering.
- Finance.
- Operations.
- Research.

A random sample is selected separately within each stratum.

### Proportional allocation

Proportional allocation maintains the population proportions within the sample.

The allocation for stratum \(h\) is:

\[
n_h=n\frac{N_h}{N}
\]

Where:

- \(N_h\) = population size of stratum h.
- \(n_h\) = sample size assigned to stratum h.
- \(N\) = total population size.
- \(n\) = total sample size.

For a sample of 100:

| Department | Population | Allocation |
|---|---:|---:|
| Engineering | 400 | 40 |
| Finance | 200 | 20 |
| Operations | 250 | 25 |
| Research | 150 | 15 |
| Total | 1,000 | 100 |

This design preserves the population's department distribution.

### Integer allocation

The theoretical allocation may produce fractional sample sizes.

The implementations use largest-remainder allocation:

1. Calculate the exact allocation for each stratum.
2. Take the integer floor.
3. Assign remaining observations according to fractional remainders.
4. Ensure that the requested total is maintained.
5. Prevent an allocation from exceeding its stratum population.

The implementations also ensure that every non-empty stratum receives at least one observation when the sample size permits it.

This constraint means that proportional allocation can require adjustment when the sample is small or the strata are highly unequal.

### Equal allocation

Equal allocation assigns approximately the same number of observations to every stratum.

It is useful when small groups need sufficient observations for separate analysis.

It does not preserve the population proportions.

Consequently, an unweighted average of the resulting observations may not represent the overall population.

### Weighted estimation

For proportional or disproportionate stratified sampling, the population mean is estimated using population weights:

\[
\bar{y}_{st}=
\sum_{h=1}^{H}W_h\bar{y}_h
\]

Where:

\[
W_h=\frac{N_h}{N}
\]

And \(\bar{y}_h\) is the sample mean within stratum h.

This is essential when different strata receive different sampling fractions.

The Python and Java implementations calculate a population-weighted estimate.

The PostgreSQL implementation stores stratum allocations and inclusion probabilities, allowing weighted estimates to be constructed from the selected observations.

### Optimal allocation

When the objective is to minimize sampling variance under a fixed budget, Neyman allocation can be considered:

\[
n_h \propto N_h S_h
\]

Where \(S_h\) represents the within-stratum standard deviation.

If stratum-specific collection costs differ, a cost-adjusted allocation can be used:

\[
n_h \propto \frac{N_h S_h}{\sqrt{c_h}}
\]

Where \(c_h\) is the cost of collecting an observation in stratum h.

The database defines `OPTIMAL` as an allocation method category, but the executable allocation procedures implement proportional allocation rather than Neyman optimization.

An optimal allocation requires reliable variance estimates and, when costs are relevant, reliable cost information.

## 5. Systematic Sampling

Systematic sampling selects observations at approximately regular intervals from an ordered sampling frame.

The interval is:

\[
k=\frac{N}{n}
\]

A randomized starting position determines the first observation.

Subsequent positions are separated by the interval.

For example, when \(N=1,000\) and \(n=100\):

\[
k=10
\]

The sample selects approximately every tenth observation after the randomized start.

### Advantages

- Simple operational implementation.
- Efficient selection from ordered lists.
- Easy to integrate into large administrative datasets.
- Lower computational overhead than repeatedly shuffling a complete population.

### Periodicity risk

Systematic sampling can produce biased or unrepresentative results if the frame contains periodic structure associated with the selection interval.

For example, if employee records are ordered according to recurring shift patterns, selecting every tenth record may repeatedly select similar shifts.

Randomizing the starting position does not eliminate every periodicity problem.

The ordering of the sampling frame must therefore be examined before selection.

## 6. Sampling Bias

Sampling bias occurs when the selection or response mechanism systematically favors certain population units over others.

It differs from random sampling error.

Sampling error results from observing a subset rather than the complete population. Sampling bias concerns systematic distortions in the selection process or resulting observations.

### Major forms of bias

| Bias type | Mechanism | Example |
|---|---|---|
| Undercoverage | Some population groups are absent from the frame | Contractors excluded from an employee study |
| Selection bias | Selection probabilities are systematically unequal or inappropriate | Only easily accessible employees are selected |
| Nonresponse bias | Selected units respond differently from nonrespondents | Employees with lower satisfaction avoid the survey |
| Survivorship bias | Only units surviving a selection condition are analyzed | Only currently employed individuals are included |
| Voluntary response bias | Participation depends on self-selection | Only highly dissatisfied employees complete an open survey |
| Measurement bias | Measurements systematically differ from actual values | One department uses an inconsistent survey scale |

### Representation diagnostics

The implementations calculate the difference between sample and population proportions.

For group h:

\[
D_h=\hat{W}_h-W_h
\]

Where:

- \(\hat{W}_h\) = observed sample proportion.
- \(W_h\) = actual population proportion.

A positive difference indicates overrepresentation.

A negative difference indicates underrepresentation.

The Python and JavaScript implementations report these differences for department groups.

The SQL view `v_stratum_representation` provides the equivalent database analysis.

### Important distinction

Representation similarity does not prove that a sample is unbiased.

A sample can reproduce population department proportions while remaining biased within each department.

For example, a survey may select the correct proportion of engineering employees but disproportionately select senior engineers.

The analysis should therefore consider additional variables related to selection and the study outcome.

### Nonresponse bias

Nonresponse occurs when selected population units do not provide usable responses.

A response rate can be calculated as:

\[
RR=\frac{\text{Completed responses}}
{\text{Selected eligible units}}
\]

A low response rate does not automatically prove nonresponse bias.

Bias arises when the response mechanism is associated with the outcome or relevant population characteristics.

The implementations distinguish selection from response collection and record response and nonresponse states separately.

### Weighting

Inverse-probability weighting can adjust for unequal inclusion probabilities.

The weight for observation i is:

\[
w_i=\frac{1}{\pi_i}
\]

Where \(\pi_i\) is its inclusion probability.

The weighted mean is:

\[
\bar{y}_w=
\frac{\sum_i w_i y_i}
{\sum_i w_i}
\]

For nonresponse adjustments, additional response-probability weights may be necessary.

Weighting cannot automatically correct unmeasured selection mechanisms or a sampling frame that excludes important population groups.

## 7. Sample Size Determination

Sample-size determination establishes the number of observations required for a specified level of statistical precision.

It depends on:

- Population size.
- Confidence level.
- Margin of error.
- Expected population variability.
- Expected response rate.
- Sampling design.
- Analysis objectives.
- Operational cost.

A larger sample generally reduces sampling variability, but the relationship is not linear.

Increasing a sample fourfold approximately halves the standard error under comparable independent sampling conditions.

### Cochran's formula for proportions

For an estimated population proportion:

\[
n_0=
\frac{Z^2p(1-p)}{e^2}
\]

Where:

- \(Z\) = critical value for the confidence level.
- \(p\) = expected population proportion.
- \(e\) = acceptable margin of error.

For 95% confidence:

\[
Z=1.96
\]

When the expected proportion is unknown, using \(p=0.5\) gives the largest variance and therefore a conservative sample-size estimate for this formula.

With a 5% margin of error:

\[
n_0=
\frac{1.96^2(0.5)(0.5)}{0.05^2}
\]

The initial estimate is approximately 385 observations.

### Finite population correction

When sampling without replacement from a finite population, the initial estimate can be adjusted:

\[
n=
\frac{n_0}{1+\frac{n_0-1}{N}}
\]

For a population of 1,000:

\[
n=
\frac{384.16}
{1+\frac{383.16}{1000}}
\]

The adjusted requirement is approximately 278 observations.

The Python, JavaScript, Java, and PostgreSQL implementations calculate this adjustment.

The C++ implementation provides the corresponding calculation.

### Sample size for a population mean

When the objective is estimating a mean:

\[
n_0=
\left(\frac{Z\sigma}{e}\right)^2
\]

Where:

- \(\sigma\) = estimated population standard deviation.
- \(e\) = acceptable absolute error.

A pilot study or previous dataset can provide an estimate of \(\sigma\).

The Python and Java implementations include this calculation.

### Nonresponse adjustment

The recruitment target must account for expected nonresponse.

\[
n_{\text{recruit}}=
\frac{n_{\text{required}}}{r}
\]

Where r is the expected response rate.

For a required sample of 278 and an expected response rate of 85%:

\[
n_{\text{recruit}}=
\frac{278}{0.85}
\]

The recruitment target is 328 observations after rounding upward.

Recruitment targets should also respect the eligible population size and available operational resources.

## 8. Estimation and Sampling Uncertainty

### Sample mean

The sample mean estimates the population mean:

\[
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
\]

### Sample variance

The sample variance measures dispersion:

\[
s^2=
\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}
\]

The denominator \(n-1\) provides the conventional unbiased estimator of population variance under independent, identically distributed sampling.

### Standard error

For simple random sampling without replacement:

\[
SE(\bar{x})=
\frac{s}{\sqrt{n}}
\sqrt{\frac{N-n}{N-1}}
\]

The second term is the finite population correction.

When the sample represents a negligible fraction of a very large population, this correction approaches one.

### Confidence interval

An approximate 95% confidence interval is:

\[
\bar{x}\pm1.96SE(\bar{x})
\]

This is a normal approximation.

For small samples, a Student-t critical value is generally more appropriate when estimating a mean and using the sample standard deviation.

The implementations use the normal critical value for the demonstration.

Their intervals are educational estimates and should not be treated as universally valid inference procedures for complex survey designs.

## 9. Distinction Between the Five Implementations

The implementations address the same statistical domain through different engineering approaches.

| File | Primary engineering perspective |
|---|---|
| Python | Statistical experimentation and reusable sampling algorithms |
| JavaScript | Event-driven sampling workflows and asynchronous execution |
| C++17 | Efficient domain-oriented sampling and governance evaluation |
| Java 17 | Enterprise services, immutable domain records, and policy evaluation |
| PostgreSQL | Persistent population frames, sampling workflows, constraints, and reporting |

### Python

The Python program uses dataclasses, enumerations, dictionaries, sets, and standard-library statistical functions.

`SamplingTheory` implements three sampling methods.

`SampleSizeCalculator` handles sample-size determination and nonresponse adjustment.

`BiasDiagnostics` measures representation differences and computes weighted estimates.

The implementation also includes input validation and deterministic synthetic data.

### JavaScript

The JavaScript implementation separates population management, random-number generation, sampling algorithms, statistical analysis, and workflow orchestration.

`EventEmitter` provides lifecycle events:

- `sampling:started`
- `sampling:completed`
- `sampling:failed`

`SamplingWorkflow` uses asynchronous execution and rejects duplicate completed workflows.

The deterministic generator supports repeatable simulations, while Node.js cryptographic randomness is demonstrated separately.

### C++17

The C++ implementation emphasizes explicit domain structures and efficient standard-library operations.

`SamplingEngine` owns the population and implements random, stratified, and systematic sampling.

`ProtectionResult` stores statistical estimates.

`GovernanceEngine` demonstrates policy-based eligibility evaluation, keeping independent approval decisions, status checks, and repository-level restrictions separate from the sampling algorithms.

The sampling engine uses STL containers and algorithms rather than external statistical libraries.

### Java 17

The Java implementation uses records for immutable domain values.

The principal services are:

- `SampleSizeCalculator`
- `SamplingService`
- `StatisticalService`
- `EnterpriseMergePolicy`

Stratum reports are calculated using collection operations and streams.

The enterprise policy model demonstrates how independent requirements can be evaluated and how failure reasons can be returned without terminating the complete evaluation process.

### PostgreSQL

The database represents a persistent sampling workflow.

The principal relational entities are:

| Table | Responsibility |
|---|---|
| `population` | Defines population snapshots |
| `population_unit` | Stores individual population units |
| `sampling_design` | Records sampling methods and parameters |
| `sampling_stratum` | Stores population group sizes and allocations |
| `sample_selection` | Records selected observations and inclusion probabilities |
| `quality_check` | Stores validation results |
| `sample_size_plan` | Records sample-size calculations |
| `statistical_estimate` | Persists statistical estimates |
| `sampling_audit` | Records workflow events |

The database includes:

- Primary and foreign keys.
- Unique constraints.
- Check constraints.
- Performance-oriented indexes.
- Response validation triggers.
- Population snapshot protection.
- Sample-size functions.
- Allocation functions.
- Sampling procedures.
- Reporting views.
- Transaction handling.

## 10. Database Workflow and Integrity

The database separates population definition from sampling execution.

This is important because a sampling result must be associated with the exact population frame from which it was selected.

A sampling design references a specific population snapshot.

The selection table stores each selected unit once per design and records its inclusion probability.

For simple random sampling:

\[
\pi_i=\frac{n}{N}
\]

For proportional or disproportionate stratified sampling:

\[
\pi_{hi}=\frac{n_h}{N_h}
\]

These probabilities support weighted analysis and provide an auditable description of the selection design.

### State management

A design can have the following states:

| State | Meaning |
|---|---|
| DRAFT | Design is being prepared |
| APPROVED | Design has been authorized |
| RUNNING | Sampling is executing |
| COMPLETED | Selection has finished |
| FAILED | Execution encountered an error |
| CANCELLED | Design was cancelled |

The executable procedures enforce a draft-to-running-to-completed workflow for the demonstrated sampling operations.

A production system should implement authorization for the transition to `APPROVED`, and enforce immutable design parameters after execution begins.

### Transaction handling

Sampling operations should be atomic.

If a sampling procedure fails, the transaction must not leave a partially populated sample.

PostgreSQL transaction handling provides this protection when the procedure is invoked inside an appropriate transaction boundary.

The demonstration includes a savepoint and rollback to show how a temporary operation can be reversed.

## 11. Validation and Failure Conditions

Sampling systems must handle invalid input and operational failure explicitly.

| Condition | Expected handling |
|---|---|
| Empty population | Reject the sampling operation |
| Sample size of zero | Reject the design |
| Sample larger than population | Reject the design |
| Duplicate population identifiers | Reject the frame |
| Empty stratum | Reject invalid group information |
| Sample smaller than number of strata | Reject mandatory representation |
| Invalid confidence level | Reject statistical calculation |
| Zero margin of error | Reject sample-size calculation |
| Missing response value | Reject responded status |
| Insufficient observations | Prevent variance estimation |
| Invalid inclusion probability | Enforce database constraint |
| Closed population snapshot | Prevent frame modification |

These checks distinguish data-quality problems from statistical limitations.

A failed sampling operation should also generate sufficient diagnostic information for investigation without exposing sensitive population records.

## 12. Sampling Bias Versus Sampling Error

These concepts should not be treated as interchangeable.

| Property | Sampling error | Sampling bias |
|---|---|---|
| Nature | Random variation | Systematic distortion |
| Main source | Selecting a subset | Selection, coverage, response, or measurement mechanism |
| Reduced by increasing sample size | Generally | Not necessarily |
| Measurable using standard error | Under the specified design | Not fully |
| Requires design correction | Not always | Usually |

A very large sample can have low sampling variance while producing a systematically incorrect estimate.

For example, surveying 90% of the available engineering employees cannot establish an accurate workforce-wide estimate if finance, operations, and research employees are systematically excluded.

Improving frame coverage and selection design is more important than merely increasing the number of observations in such a situation.

## 13. Performance and Complexity

Let N represent population size, n represent sample size, and H represent the number of strata.

| Operation | Approximate complexity |
|---|---|
| Simple random sampling by shuffling | O(N log N) |
| Simple random sampling by partial selection | O(N) expected for hash-based selection or appropriate selection algorithms |
| Stratified grouping | O(N) expected |
| Sorting strata for allocation | O(H log H) |
| Systematic selection after frame preparation | O(n) |
| Mean calculation | O(n) |
| Variance calculation | O(n) |
| Representation diagnostics | O(N+n) expected |
| Sample-size calculation | O(1) |

The Python and JavaScript implementations shuffle the full population before selecting observations, which is straightforward but uses additional memory.

For very large populations, partial-selection algorithms, database-side sampling, reservoir sampling, or streaming methods may be more appropriate.

The PostgreSQL implementation uses indexes on population identifiers, eligibility, strata, and selection status to support common retrieval patterns.

For large databases, query plans should be examined using `EXPLAIN (ANALYZE, BUFFERS)`.

## 14. Security and Research Governance

Sampling systems may contain personal, employment, financial, or other sensitive information.

Important controls include:

- Restricting access to population-level records.
- Separating identifiers from analytical attributes.
- Using pseudonymous external references.
- Restricting access to sampling designs and audit records.
- Protecting random seeds when their disclosure could permit manipulation.
- Recording population snapshot dates.
- Preventing unauthorized frame modification.
- Validating input values before persistence.
- Limiting export of identifiable records.
- Applying retention and deletion policies.

A random seed and a reproducible selection procedure support auditability, but they do not provide confidentiality.

The PostgreSQL script includes an example of a restricted reader role. Actual deployment permissions should follow least-privilege principles and separate operational responsibilities.

## 15. Limitations and Interpretation

The implementations are designed to demonstrate core sampling methods and associated statistical workflows.

Several limitations are important.

**Normal confidence intervals:** The demonstrations use normal critical values. Small samples and highly skewed distributions may require alternative inference procedures.

**Complex survey designs:** Cluster sampling, multistage sampling, unequal probability designs, and replicate-weight variance estimation are not fully implemented.

**Nonresponse adjustment:** Recording nonresponse and calculating recruitment targets do not establish that nonresponse bias has been removed.

**Optimal allocation:** The domain includes an optimal allocation category, but the executable allocation algorithm is proportional.

**Systematic sampling:** Periodic population ordering can compromise representativeness.

**Weighting:** Inclusion-probability weighting does not automatically correct coverage errors or unmeasured nonresponse mechanisms.

**Reproducibility:** Identical seeds do not guarantee identical results across different programming-language random-number generators.

**Database randomness:** The PostgreSQL hash-based random ordering provides deterministic selection for the stored seed and population identifiers. It is not a cryptographic randomization protocol.

**Finite population correction:** The simple correction used in the implementations is appropriate for the demonstrated simple random sampling assumptions. Stratified designs require variance calculations that account for their separate strata and allocation.

## 16. Practical Applications

The implemented methods apply to several operational and research situations.

| Application | Sampling approach | Main consideration |
|---|---|---|
| Employee satisfaction survey | Stratified random sampling | Department representation |
| Customer feedback study | Simple random sampling | Complete customer frame |
| Production quality inspection | Systematic sampling | Production-order periodicity |
| Healthcare population research | Stratified sampling | Clinical and demographic representation |
| Market research | Random or stratified sampling | Coverage and nonresponse |
| Financial risk assessment | Stratified sampling | Representation of risk categories |
| Academic research | Probability sampling | Population inference and uncertainty |
| Large administrative surveys | Weighted sampling | Inclusion and response probabilities |

The selection method should be determined by the research objective, population structure, available sampling frame, and required statistical precision rather than convenience alone.

## 17. Execution Requirements

| Implementation | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10+ | None |
| JavaScript | Node.js 18+ | None |
| C++17 | C++17 compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 15+ | None |

The Python script executes its demonstration through the main entry point.

The JavaScript file executes the asynchronous workflow through `main()`.

The C++ program uses standard C++17 headers.

The Java program is self-contained in `SamplingTheoryEnterprise.java`.

The SQL script creates the `sampling` schema, defines its database objects, inserts the synthetic population, executes three sampling workflows, and produces statistical and quality reports.

The SQL script is intended for execution in a dedicated database because it creates schema-level objects and demonstration records.
