# Descriptive Statistics

## 1. Project Overview

This project implements a descriptive statistics system across Python, JavaScript, C++17, Java 17, and PostgreSQL.

It examines the distribution, central tendency, dispersion, and relative position of numerical observations.

The system implements six principal statistical concepts:

| Statistical measure | Purpose |
|---|---|
| Mean | Measures arithmetic central tendency |
| Median | Identifies the middle observation |
| Mode | Identifies the most frequently occurring value |
| Variance | Measures squared dispersion around the mean |
| Standard deviation | Expresses dispersion in the original measurement unit |
| Quantiles | Divide an ordered dataset into specified proportions |

The implementations use operational performance measurements, employee performance observations, customer ratings, and production response times.

The objective is to establish a consistent statistical workflow while demonstrating language-specific approaches to numerical processing, validation, data structures, and reporting.

## 2. Mathematical Foundations

Let a numerical dataset contain:

\[
X = \{x_1,x_2,\ldots,x_n\}
\]

where:

- \(x_i\) represents an individual observation.
- \(n\) represents the number of observations.
- \(\bar{x}\) represents the arithmetic mean.

### 2.1 Mean

The arithmetic mean is the sum of all observations divided by the number of observations.

\[
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
\]

Example:

Dataset: 2, 4, 4, 4, 5, 5, 7, 9

\[
\bar{x}=\frac{40}{8}=5
\]

The mean uses every observation and is sensitive to unusually large or small values.

### 2.2 Median

The median is the middle observation after sorting the dataset.

For an odd number of observations:

\[
Median=x_{\left(\frac{n+1}{2}\right)}
\]

For an even number of observations:

\[
Median=
\frac{x_{(n/2)}+x_{(n/2+1)}}{2}
\]

For the example dataset:

Sorted observations:

2, 4, 4, 4, 5, 5, 7, 9

\[
Median=\frac{4+5}{2}=4.5
\]

The median is less sensitive to extreme observations than the mean.

### 2.3 Mode

The mode is the observation occurring most frequently.

For the example dataset:

| Value | Frequency |
|---:|---:|
| 2 | 1 |
| 4 | 3 |
| 5 | 2 |
| 7 | 1 |
| 9 | 1 |

Therefore:

\[
Mode=4
\]

A dataset can have:

- No repeated mode, when all observations occur once.
- One mode, when one observation has the highest frequency.
- Multiple modes, when several observations share the highest frequency.

The implementations return all equally frequent modes.

### 2.4 Population Variance

Population variance measures the average squared deviation from the population mean.

\[
\sigma^2=
\frac{\sum_{i=1}^{N}(x_i-\mu)^2}{N}
\]

Where:

- \(N\) is the population size.
- \(\mu\) is the population mean.
- \(\sigma^2\) is population variance.

For the example dataset:

\[
\sigma^2=4
\]

Population variance is appropriate when the available observations represent the complete population being studied.

### 2.5 Sample Variance

Sample variance estimates population variability from a sample.

\[
s^2=
\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}
\]

The denominator is \(n-1\), rather than \(n\).

This correction is known as Bessel's correction.

It compensates for the loss of one degree of freedom when the population mean is estimated from the sample.

For the example dataset:

\[
s^2=\frac{32}{7}\approx4.5714
\]

Sample variance requires at least two observations.

### 2.6 Standard Deviation

Standard deviation is the square root of variance.

Population standard deviation:

\[
\sigma=\sqrt{\sigma^2}
\]

Sample standard deviation:

\[
s=\sqrt{s^2}
\]

Unlike variance, standard deviation uses the original measurement unit.

For example, when observations represent milliseconds, standard deviation is also measured in milliseconds.

### 2.7 Quantiles

Quantiles divide an ordered dataset into specified proportions.

A quantile probability \(p\) identifies the observation below which approximately a proportion \(p\) of the dataset lies.

This project implements linear interpolation using the R-7 convention.

For sorted observations:

\[
h=(n-1)p
\]

Let:

\[
j=\lfloor h\rfloor
\]

\[
g=h-j
\]

The quantile is:

\[
Q(p)=x_{j+1}+g(x_{j+2}-x_{j+1})
\]

The implementation uses zero-based indexing internally.

Important quantiles include:

| Quantile | Meaning |
|---|---|
| Q1 | 25th percentile |
| Q2 | 50th percentile or median |
| Q3 | 75th percentile |
| P90 | 90th percentile |
| P95 | 95th percentile |
| P99 | 99th percentile |

Different statistical software packages support different quantile conventions. Results should therefore identify the convention used.

### 2.8 Interquartile Range

The interquartile range measures the spread of the middle 50% of observations.

\[
IQR=Q3-Q1
\]

It is less affected by extreme values than the total range.

### 2.9 Outlier Detection

The implementations use the conventional 1.5 IQR rule.

Lower boundary:

\[
L=Q1-1.5(IQR)
\]

Upper boundary:

\[
U=Q3+1.5(IQR)
\]

Observations satisfying either condition are flagged:

\[
x_i<L
\]

or

\[
x_i>U
\]

An outlier flag is an analytical signal, not proof that an observation is incorrect.

Extreme observations can represent legitimate operational events.

## 3. Statistical Concepts and Their Distinctions

| Concept | Measures | Sensitivity to extreme observations |
|---|---|---|
| Mean | Arithmetic center | High |
| Median | Positional center | Low |
| Mode | Frequency concentration | Depends on frequency distribution |
| Variance | Squared dispersion | High |
| Standard deviation | Dispersion in original units | High |
| Quantiles | Relative position | Generally lower than mean-based measures |
| IQR | Middle 50% spread | Low |

These measures should be interpreted together.

For example, a large difference between mean and median can indicate a skewed distribution.

A high standard deviation indicates substantial variability, but does not independently establish whether the underlying observations are abnormal.

## 4. Processing Architecture

The five implementations use different engineering approaches.

The common analytical workflow is:

Dataset ingestion  
→ Numeric validation  
→ Observation storage  
→ Frequency calculation  
→ Sorting  
→ Central tendency  
→ Dispersion  
→ Quantile calculation  
→ Outlier identification  
→ Statistical reporting

### 4.1 Python Architecture

The Python implementation uses object-oriented statistical processing.

Principal components:

| Component | Responsibility |
|---|---|
| `Dataset` | Immutable dataset representation |
| `RunningStatistics` | Incremental statistical calculations |
| `DescriptiveStatistics` | Statistical analysis |
| `VarianceType` | Population and sample variance selection |
| `StatisticsError` | Statistical validation failures |

Python capabilities demonstrated:

- Dataclasses and enums.
- Lists, dictionaries, and counters.
- Type annotations.
- Exception handling.
- CSV processing.
- JSON reporting.
- Standard-library statistics.
- Assertions for correctness testing.

Welford's algorithm updates the running mean and the accumulated squared deviations without repeatedly calculating the full dataset variance.

For each new observation:

\[
\delta=x-\bar{x}_{old}
\]

\[
\bar{x}_{new}=\bar{x}_{old}+\frac{\delta}{n}
\]

\[
M2_{new}=M2_{old}+\delta(x-\bar{x}_{new})
\]

Variance is obtained by dividing the accumulated value by the appropriate population or sample denominator.

This approach is useful when observations arrive incrementally.

### 4.2 JavaScript Architecture

The JavaScript implementation provides an event-driven statistical engine.

Its principal components are:

- `StatisticsEngine`
- `StatisticsError`
- `VarianceType`
- Asynchronous CSV ingestion.
- EventEmitter-based observation notifications.

The `Map` structure maintains observation frequencies.

The event system emits updated observation information as new measurements arrive.

Private class fields protect internal statistical state.

Batch ingestion validates all incoming values before modifying the dataset.

Asynchronous file reading uses Node.js streams and `readline`, avoiding the need to load an entire CSV file into memory before parsing.

The implementation also enforces a configurable observation limit.

### 4.3 C++17 Architecture

The C++ implementation uses a compact numerical analysis design.

Principal components:

- `Observation`
- `StatisticalSummary`
- `VarianceType`
- `DescriptiveStatistics`

The STL provides:

- `vector` for observations.
- `map` for frequency distributions.
- `sort` for ordering.
- `accumulate` for summation.
- Standard algorithms for minimum and maximum operations.

`long double` is used for intermediate summation and squared-deviation calculations to reduce numerical error.

The implementation validates non-finite input and handles insufficient sample sizes through exceptions.

Its principal trade-off is that observations are retained and sorted, which makes repeated quantile calculations efficient but requires additional memory.

### 4.4 Java 17 Architecture

The Java implementation uses an enterprise-oriented service structure.

| Component | Responsibility |
|---|---|
| `Measurement` | Validated observation record |
| `AnalysisPolicy` | Data-quality policy contract |
| `MeasurementQualityPolicy` | Observation eligibility |
| `StatisticalDataset` | Statistical calculations |
| `AnalyticsService` | Coordinates validation and reporting |
| `StatisticsReport` | Immutable statistical output |
| `QualityResult` | Data-quality assessment |
| `QualityStatus` | Acceptance state |

Java records provide immutable representations for measurements and reports.

The policy interface separates data-quality decisions from numerical calculations.

This distinction allows statistical processing to be reused under different operational acceptance policies.

The service blocks report generation when the quality policy is not satisfied.

### 4.5 PostgreSQL Architecture

The database implementation separates datasets, observations, quality policies, and analysis executions.

Principal relational entities:

| Table or view | Purpose |
|---|---|
| `datasets` | Dataset metadata |
| `observations` | Individual numeric measurements |
| `quality_policies` | Validation and eligibility conditions |
| `analysis_runs` | Historical analysis execution |
| `frequency_distribution` | Observation frequencies |
| `descriptive_summary` | Aggregate statistical measures |
| `statistical_outliers` | Outlier observations |

Database mechanisms include:

- Primary and foreign keys.
- Unique constraints.
- Check constraints.
- Indexes.
- Enumerated types.
- Stored functions.
- Stored procedures.
- Triggers.
- Views.
- Common table expressions.
- Transactions.

PostgreSQL's ordered-set aggregate `PERCENTILE_CONT` calculates interpolated quantiles.

`VAR_POP` and `VAR_SAMP` distinguish population and sample variance.

`STDDEV_POP` and `STDDEV_SAMP` provide their respective standard deviations.

## 5. Statistical Processing Rules

The implementations follow consistent analytical rules.

| Operation | Processing rule |
|---|---|
| Dataset validation | Reject empty datasets |
| Numeric validation | Reject invalid and non-finite values |
| Mean | Arithmetic average |
| Median | Middle position or average of two middle values |
| Mode | Return all equally frequent maximum-frequency values |
| Population variance | Divide by n |
| Sample variance | Divide by n - 1 |
| Standard deviation | Square root of variance |
| Quantiles | R-7 linear interpolation |
| Outlier detection | 1.5 IQR boundaries |

A dataset with one observation can have a population variance of zero.

Its sample variance is undefined.

A dataset with identical observations has zero variance and zero standard deviation.

A dataset with no repeated observations has no unique mode under the convention used here.

## 6. Practical Analytical Scenario

The implementations use measurements from operational performance monitoring.

Example dataset:

| Observation | Measurement |
|---:|---:|
| 1 | 12 |
| 2 | 15 |
| 3 | 18 |
| 4 | 20 |
| 5 | 15 |
| 6 | 22 |
| 7 | 25 |
| 8 | 18 |
| 9 | 30 |
| 10 | 35 |
| 11 | 18 |
| 12 | 40 |
| 13 | 45 |
| 14 | 50 |
| 15 | 55 |
| 16 | 60 |

The system calculates:

- Arithmetic mean.
- Median.
- Mode.
- Population and sample variance.
- Population and sample standard deviation.
- Quartiles.
- Percentiles.
- Interquartile range.
- Frequency distribution.
- Potential outliers.

The same analytical process can be applied to employee performance, response times, customer satisfaction, production measurements, and other numerical datasets.

The unit of measurement must remain consistent within a dataset.

## 7. Data Quality and Validation

Statistical accuracy depends on the quality of the underlying observations.

The implementations enforce several input conditions:

- Observations must be numeric.
- NaN and infinity are rejected.
- Empty datasets are rejected.
- Quantile probabilities must lie between zero and one.
- Percentages must lie between zero and one hundred.
- Sample variance requires at least two observations.
- Outlier multipliers must be non-negative.

The Java implementation additionally applies explicit operational data-quality policies.

The PostgreSQL implementation applies database-level constraints and triggers.

These mechanisms reduce the likelihood that invalid measurements enter an analytical workflow.

A validation failure should be distinguished from a statistically unusual but valid observation.

## 8. Performance and Complexity

Let:

- \(n\) represent the number of observations.
- \(k\) represent the number of distinct values.

| Operation | Typical complexity |
|---|---|
| Observation insertion | O(1) amortized |
| Frequency update | O(1) average with hash maps |
| Sorting | O(n log n) |
| Mean | O(n) |
| Median after sorting | O(1) |
| Mode using frequency map | O(k) |
| Variance using stored mean | O(n) |
| Quantile after sorting | O(1) |
| Outlier detection after sorting | O(n) |
| Frequency reporting | O(k log k) when ordered |

The implementations retain observations to support exact quantile calculations and repeated statistical queries.

For very large streaming datasets, retaining every observation can become expensive.

Welford's algorithm supports incremental mean and variance calculations without retaining the entire dataset.

Exact quantiles generally require retaining or externally sorting observations. Approximate quantile algorithms can reduce memory requirements for very large data streams, but they introduce estimation error and are not implemented here.

## 9. Numerical Accuracy

Floating-point calculations have finite precision.

Potential numerical problems include:

- Loss of precision when summing large values.
- Cancellation when subtracting nearly equal quantities.
- Overflow in squared differences.
- Small rounding differences across programming languages.
- Differences in percentile interpolation conventions.

The implementations use several mitigation techniques:

| Implementation | Numerical strategy |
|---|---|
| Python | Welford's incremental variance algorithm |
| JavaScript | Welford's incremental variance algorithm |
| C++17 | Extended-precision intermediate arithmetic |
| Java 17 | Compensated summation |
| PostgreSQL | Fixed-precision `NUMERIC` observations and database aggregates |

These methods improve numerical reliability but do not make all floating-point operations exact.

## 10. Testing and Failure Conditions

The source implementations include validation and testing for:

- Repeated observations.
- Multiple modes.
- Unique observations.
- Identical observations.
- Single-observation datasets.
- Invalid numeric values.
- Invalid quantile probabilities.
- Invalid sample variance requests.
- Data-quality policy violations.
- Missing CSV values.
- Maximum dataset capacity.

Expected behavior:

| Condition | Expected behavior |
|---|---|
| Empty dataset | Reject |
| Invalid number | Reject |
| NaN or infinity | Reject |
| Single observation | Population variance equals zero |
| Single observation sample variance | Reject |
| No repeated values | Empty mode result |
| Multiple maximum frequencies | Return all modes |
| Invalid percentile | Reject |
| Identical observations | Zero variance |
| Outlier observation | Flag for investigation |

The Python implementation includes executable assertions.

The Java implementation includes statistical assertions.

The C++ implementation demonstrates exception handling.

The JavaScript implementation demonstrates batch validation and asynchronous failure handling.

The PostgreSQL implementation demonstrates trigger-based validation and transactional error handling.

## 11. Execution

### Python

Run the default example:

`python descriptive_statistics.py`

Run the built-in tests:

`python descriptive_statistics.py --test`

Import a CSV dataset:

`python descriptive_statistics.py --csv data.csv --column value`

Export a JSON report:

`python descriptive_statistics.py --output statistics.json`

### JavaScript

Run:

`node descriptive_statistics.js`

Import a CSV file:

`node descriptive_statistics.js measurements.csv`

The default implementation uses Node.js built-in modules and does not require third-party packages.

### C++17

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic descriptive_statistics.cpp -o descriptive_statistics`

Run:

`./descriptive_statistics`

### Java 17

Compile:

`javac DescriptiveStatistics.java`

Run:

`java DescriptiveStatistics`

### PostgreSQL

Execute the SQL script using a PostgreSQL client.

The script creates the `descriptive_stats` schema, its tables, constraints, indexes, functions, procedures, triggers, views, and demonstration records.

It uses a transaction to maintain consistency during database setup and sample processing.

## 12. Limitations and Interpretation

Descriptive statistics summarize observed data. They do not independently establish causal relationships, statistical significance, or predictive accuracy.

Several limitations require consideration:

**Mean and median:** A single central measure cannot fully describe a distribution.

**Mode:** Continuous measurements can have many unique values, making exact-value frequency less informative.

**Variance:** Variance is expressed in squared measurement units and can be difficult to interpret directly.

**Standard deviation:** A standard deviation does not establish that observations follow a normal distribution.

**Quantiles:** Different interpolation conventions can produce different numerical results.

**Outliers:** The 1.5 IQR rule identifies unusual observations but does not establish whether they are errors.

**Missing observations:** Skipping missing CSV measurements can introduce bias if missingness is systematic.

**Data volume:** Exact sorting and quantile calculation require additional memory and computational resources.

**Data types:** The implementations primarily use floating-point values. PostgreSQL uses `NUMERIC` for stored observations, so minor precision differences may occur across implementations.

The statistical results should therefore be interpreted in relation to the measurement process, sampling design, data quality, and operational context.
