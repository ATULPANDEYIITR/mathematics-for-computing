# Statistical Estimation

## 1. Introduction

Statistical estimation is the process of using sample observations to infer unknown characteristics of a population. Since collecting information from an entire population is often expensive, time-consuming, or impractical, statistical methods use representative samples to estimate population parameters.

This project implements a statistical estimation system across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover three connected areas:

- **Point estimation:** Producing a single numerical estimate of an unknown population parameter.
- **Interval estimation:** Producing a range of plausible parameter values together with a specified confidence level.
- **Estimator evaluation:** Assessing the statistical properties and performance of estimation procedures.

The implementations use continuous observations, binary observations, normally distributed simulation data, and exponential distribution samples.

## 2. Statistical Foundations

### 2.1 Population and Sample

A population is the complete collection of observations or entities under investigation.

A sample is a subset of that population used for statistical analysis.

For example, a company may want to estimate the average productivity score of all employees. Measuring every employee may be impractical, so it collects observations from a representative group.

The distinction is important:

| Concept | Meaning |
|---|---|
| Population | Complete group under investigation |
| Sample | Selected observations from the population |
| Population parameter | Numerical characteristic of the population |
| Sample statistic | Numerical quantity calculated from sample observations |
| Estimator | Statistical rule used to estimate a parameter |
| Estimate | Numerical result obtained from an estimator |

A parameter is generally unknown, whereas a sample statistic can be calculated from available observations.

### 2.2 Parameter and Estimator

Let a population contain an unknown mean represented by:

\[
\mu
\]

The sample contains observations:

\[
X_1,X_2,\ldots,X_n
\]

An estimator is a function of these observations.

The arithmetic sample mean is:

\[
\bar X=\frac{1}{n}\sum_{i=1}^{n}X_i
\]

The estimator is the mathematical rule. The calculated value is the estimate.

For observations:

\[
10,12,13,15,16
\]

The estimated mean is:

\[
\bar X=\frac{10+12+13+15+16}{5}
\]

\[
\bar X=13.2
\]

The result 13.2 is an estimate of the unknown population mean, not necessarily the exact population mean.

## 3. Point Estimation

Point estimation produces one numerical value for an unknown population parameter.

### 3.1 Estimation of Population Mean

The sample mean is:

\[
\bar X=\frac{\sum X_i}{n}
\]

It is widely used because it is unbiased under independent and identically distributed sampling with a finite population mean.

Its standard error is:

\[
SE(\bar X)=\frac{\sigma}{\sqrt n}
\]

When the population standard deviation is unknown, it is estimated using the sample standard deviation:

\[
\widehat{SE}(\bar X)=\frac{s}{\sqrt n}
\]

Increasing sample size generally decreases the standard error.

### 3.2 Estimation of Population Variance

Population variance measures dispersion around the population mean.

\[
\sigma^2=E[(X-\mu)^2]
\]

Two important sample-based estimators are implemented.

**Unbiased sample variance**

\[
S^2=\frac{\sum_{i=1}^{n}(X_i-\bar X)^2}{n-1}
\]

The denominator \(n-1\) applies Bessel's correction.

Under independent and identically distributed sampling with finite variance:

\[
E[S^2]=\sigma^2
\]

**Maximum likelihood variance estimator**

For normally distributed observations with an unknown mean:

\[
\hat{\sigma}_{MLE}^{2}
=
\frac{\sum_{i=1}^{n}(X_i-\bar X)^2}{n}
\]

This estimator is the maximum likelihood estimator of population variance.

Its finite-sample bias is:

\[
Bias(\hat{\sigma}_{MLE}^{2})
=
-\frac{\sigma^2}{n}
\]

The two estimators differ in their denominators and statistical properties.

| Characteristic | Unbiased variance | MLE variance |
|---|---|---|
| Denominator | \(n-1\) | \(n\) |
| Finite-sample bias | Zero | Generally negative |
| Primary principle | Unbiased estimation | Maximum likelihood |
| Small-sample behavior | Corrects downward bias | Typically smaller |
| Consistency | Yes under standard assumptions | Yes under standard assumptions |

### 3.3 Estimation of Population Proportion

A population proportion describes the fraction of population members possessing a specified characteristic.

For binary observations:

\[
X_i\in\{0,1\}
\]

The sample proportion is:

\[
\hat p=\frac{x}{n}
\]

Where:

- \(x\) represents the number of successes.
- \(n\) represents the total number of observations.
- \(\hat p\) represents the estimated population proportion.

For 20 observations containing 12 successes:

\[
\hat p=\frac{12}{20}=0.60
\]

The sample proportion is the maximum likelihood estimator of the success probability in a Bernoulli model.

Its standard error is estimated by:

\[
SE(\hat p)=
\sqrt{\frac{\hat p(1-\hat p)}{n}}
\]

This approximation requires care when sample sizes are small or estimated proportions are close to zero or one.

### 3.4 Method of Moments

The method of moments estimates unknown parameters by equating theoretical population moments with corresponding sample moments.

Consider an exponential distribution with rate parameter \(\lambda\).

Its theoretical mean is:

\[
E[X]=\frac{1}{\lambda}
\]

Equating this with the sample mean gives:

\[
\bar X=\frac{1}{\lambda}
\]

Therefore:

\[
\hat\lambda_{MOM}=\frac{1}{\bar X}
\]

The Python implementation includes this estimator explicitly.

### 3.5 Maximum Likelihood Estimation

Maximum likelihood estimation selects parameter values that maximize the likelihood of observing the available sample.

For independent exponential observations:

\[
f(x;\lambda)=\lambda e^{-\lambda x},
\quad x\geq 0,\lambda>0
\]

The likelihood function is:

\[
L(\lambda)=
\lambda^n e^{-\lambda\sum X_i}
\]

The log-likelihood is:

\[
\ell(\lambda)=
n\ln(\lambda)-\lambda\sum X_i
\]

Differentiating and equating to zero:

\[
\frac{d\ell}{d\lambda}
=
\frac{n}{\lambda}-\sum X_i=0
\]

Thus:

\[
\hat\lambda_{MLE}=
\frac{n}{\sum X_i}
=
\frac{1}{\bar X}
\]

For the exponential distribution, the method-of-moments estimator and maximum likelihood estimator are identical.

Their agreement in this particular model does not imply that the two estimation methods always produce identical results.

## 4. Properties of Estimators

An estimator should be assessed through its statistical properties rather than only through the numerical estimate it produces.

### 4.1 Unbiasedness

An estimator is unbiased when its expected value equals the parameter being estimated.

\[
E[\hat\theta]=\theta
\]

Its bias is:

\[
Bias(\hat\theta)=E[\hat\theta]-\theta
\]

An unbiased estimator has zero bias.

For example, the sample mean is unbiased for the population mean under independent and identically distributed sampling with a finite mean.

### 4.2 Variance

Estimator variance measures how much estimates vary across repeated samples.

\[
Var(\hat\theta)=
E[(\hat\theta-E[\hat\theta])^2]
\]

A smaller estimator variance indicates greater precision across repeated samples.

Variance is not the same as the variance of individual population observations.

The variance of observations describes population dispersion. The variance of an estimator describes the variability of the estimation procedure.

### 4.3 Mean Squared Error

Mean squared error measures the average squared difference between an estimator and its true parameter.

\[
MSE(\hat\theta)=
E[(\hat\theta-\theta)^2]
\]

The bias-variance decomposition is:

\[
MSE(\hat\theta)=
Var(\hat\theta)+Bias(\hat\theta)^2
\]

This relationship is useful when comparing unbiased and biased estimators.

An estimator with a small amount of bias may have a lower MSE if its variance is sufficiently reduced.

### 4.4 Consistency

An estimator is consistent when it converges in probability to the true parameter as sample size increases.

\[
\hat\theta_n\xrightarrow{P}\theta
\]

Consistency concerns long-run behavior as the sample size grows.

An estimator may be biased for every finite sample size and still be consistent.

### 4.5 Efficiency

Efficiency compares the variance of estimators under specified assumptions.

An efficient estimator achieves the smallest possible variance within the relevant estimator class or attains an applicable information bound.

Efficiency comparisons require the same statistical model, target parameter, and regularity assumptions.

### 4.6 Sufficiency

A sufficient statistic contains all sample information relevant to a parameter under a specified statistical model.

For normally distributed observations with known variance, the sample mean is sufficient for the unknown population mean.

Sufficiency is a property of a statistic relative to a statistical model, not a general statement that a statistic summarizes every aspect of a dataset.

## 5. Interval Estimation

A point estimate gives one value, while an interval estimate provides a range.

A confidence interval is constructed through a procedure that has a specified long-run coverage probability under its assumptions.

A 95% confidence interval does not mean that the fixed population parameter has a 95% probability of being inside an already calculated frequentist interval.

It means that repeated applications of the procedure would cover the true parameter approximately 95% of the time under the assumed model.

### 5.1 Normal Confidence Interval for the Mean

When the population standard deviation is known, the normal-based interval is:

\[
\bar X\pm z_{\alpha/2}
\frac{\sigma}{\sqrt n}
\]

Where:

- \(\bar X\) is the sample mean.
- \(\sigma\) is the known population standard deviation.
- \(n\) is the sample size.
- \(z_{\alpha/2}\) is the standard normal critical value.

When the population standard deviation is unknown, a normal-based approximation may use the sample standard deviation:

\[
\bar X\pm z_{\alpha/2}
\frac{s}{\sqrt n}
\]

This is an approximation, particularly for smaller samples.

### 5.2 Student's t Confidence Interval

When the population standard deviation is unknown and the sample is drawn independently from a normal population, the Student's t interval is:

\[
\bar X\pm t_{\alpha/2,n-1}
\frac{s}{\sqrt n}
\]

The t distribution has heavier tails than the standard normal distribution for finite degrees of freedom.

As degrees of freedom increase, it approaches the standard normal distribution.

The implementations calculate Student's t critical values numerically through the regularized incomplete beta function and bisection.

This avoids relying on hard-coded critical values for individual sample sizes.

### 5.3 Confidence Interval for a Population Proportion

The simple Wald interval is:

\[
\hat p\pm z_{\alpha/2}
\sqrt{\frac{\hat p(1-\hat p)}{n}}
\]

The Wald interval can perform poorly when sample sizes are small or proportions are near the boundaries.

The project therefore implements the Wilson score interval.

Its adjusted denominator is:

\[
D=1+\frac{z^2}{n}
\]

Its center is:

\[
C=
\frac{\hat p+\frac{z^2}{2n}}{D}
\]

Its margin is:

\[
M=
\frac{z}{D}
\sqrt{
\frac{\hat p(1-\hat p)}{n}
+
\frac{z^2}{4n^2}
}
\]

The resulting interval is:

\[
[C-M,C+M]
\]

The lower and upper limits are restricted to the valid probability range:

\[
0\leq p\leq 1
\]

### 5.4 Bootstrap Confidence Interval

Bootstrap estimation uses repeated resampling with replacement from the observed sample.

For each bootstrap repetition:

1. Draw a sample of size \(n\) with replacement.
2. Calculate the required statistic.
3. Store the calculated estimate.
4. Repeat the process a specified number of times.
5. Sort the bootstrap estimates.
6. Select the relevant empirical quantiles.

The percentile bootstrap interval is:

\[
[
Q_{\alpha/2},
Q_{1-\alpha/2}
]
\]

The implementations use 5,000 bootstrap repetitions in their demonstration workflows.

A fixed random seed provides reproducibility.

Bootstrap intervals are not universally reliable. They depend on the representativeness of the original sample and may perform poorly for small samples, extreme statistics, dependent observations, or distributions with substantial boundary effects.

## 6. Relationship Between Point and Interval Estimation

Point and interval estimation are related but answer different statistical questions.

| Feature | Point estimation | Interval estimation |
|---|---|---|
| Output | Single numerical value | Lower and upper bounds |
| Main purpose | Estimate parameter location | Quantify estimation uncertainty |
| Example | Sample mean | 95% confidence interval |
| Sampling variability | Reflected indirectly | Incorporated through interval construction |
| Interpretation | Estimated parameter value | Range produced by an uncertainty procedure |

An interval is normally centered around a point estimate in standard symmetric mean intervals.

Wilson and bootstrap intervals need not be symmetric around their point estimates.

## 7. Python Implementation

The Python program provides a modular statistical calculation system using standard-library features.

### 7.1 Main Components

| Component | Responsibility |
|---|---|
| `PointEstimate` | Stores a point estimate and its metadata |
| `ConfidenceInterval` | Stores interval limits and confidence level |
| `EstimatorEvaluation` | Stores estimator performance metrics |
| `IntervalMethod` | Identifies interval calculation methods |
| `validate_sample()` | Checks sample validity |
| `mean_estimator()` | Calculates the sample mean |
| `variance_estimator()` | Calculates sample or MLE variance |
| `proportion_estimator()` | Calculates a binary sample proportion |
| `student_t_quantile()` | Calculates Student's t critical values |
| `mean_confidence_interval()` | Calculates mean confidence intervals |
| `wilson_proportion_interval()` | Calculates Wilson intervals |
| `bootstrap_mean_interval()` | Performs percentile bootstrap estimation |
| `evaluate_estimator()` | Calculates bias, variance, and MSE |

### 7.2 Implementation Decisions

Dataclasses provide structured estimation results.

Enums prevent inconsistent method names.

The statistical functions validate observations before performing calculations.

The Student's t quantile implementation uses numerical inversion rather than a table of predefined values.

The bootstrap implementation uses a local seeded random-number generator.

The final results are stored in `estimation_results.json`.

The program also performs assertions for important calculations and invalid-input conditions.

## 8. JavaScript Implementation

The JavaScript implementation uses an event-driven estimation architecture.

### 8.1 Main Components

| Component | Responsibility |
|---|---|
| `EstimationRegistry` | Registers and executes estimators |
| `EstimationError` | Represents estimation failures |
| `SeededRandom` | Produces reproducible pseudo-random values |
| `mean()` | Calculates arithmetic mean |
| `variance()` | Calculates variance |
| `studentTQuantile()` | Calculates Student's t quantiles |
| `meanInterval()` | Calculates confidence intervals |
| `wilsonInterval()` | Estimates binary proportions |
| `bootstrapInterval()` | Executes asynchronous bootstrap resampling |
| `evaluateEstimator()` | Evaluates estimation performance |

### 8.2 Event-Driven Processing

The registry extends Node.js `EventEmitter`.

Its principal events are:

- `registered`
- `estimationStarted`
- `estimationCompleted`
- `estimationFailed`

This separates estimator execution from application monitoring.

The bootstrap implementation uses asynchronous yielding through `setImmediate()` to reduce event-loop blocking during repeated resampling.

The implementation also uses `Map` for estimator registration and result tracking.

### 8.3 Failure Handling

The registry rejects:

- Empty samples.
- Non-finite observations.
- Unknown estimators.
- Duplicate estimator registrations.
- Invalid estimator return values.
- Duplicate estimation request names.

Estimation results are retained in memory and exported as JSON.

The in-memory registry is suitable for demonstration and small applications, but production systems requiring durable records need persistent storage.

## 9. C++17 Implementation

The C++ program models statistical estimation through a dedicated `StatisticalEstimation` class.

### 9.1 Main Components

| Component | Responsibility |
|---|---|
| `EstimatorType` | Identifies point estimation methods |
| `IntervalType` | Identifies interval estimation methods |
| `Estimate` | Stores point estimation results |
| `ConfidenceInterval` | Stores interval limits |
| `EstimatorMetrics` | Stores estimator performance measures |
| `StatisticalEstimation` | Provides statistical operations |

### 9.2 Technical Decisions

STL vectors store observations and bootstrap samples.

STL algorithms calculate sums and sort bootstrap estimates.

The Mersenne Twister random-number generator provides reproducible bootstrap sampling.

The implementation uses numerical integration-related special-function calculations through the incomplete beta function to calculate Student's t quantiles.

The public interface is separated from private validation and numerical calculation functions.

### 9.3 Performance Characteristics

For a sample of size \(n\):

| Operation | Time complexity |
|---|---|
| Mean calculation | \(O(n)\) |
| Variance calculation | \(O(n)\) |
| Proportion calculation | \(O(n)\) |
| Normal quantile approximation | \(O(1)\) |
| Student's t quantile | \(O(I \times B)\) |
| Bootstrap estimation | \(O(Bn+ B\log B)\) |
| Estimator evaluation | \(O(Rn)\) |

Here:

- \(I\) represents numerical inversion iterations.
- \(B\) represents bootstrap repetitions.
- \(R\) represents estimator simulation repetitions.

Bootstrap sorting contributes to the computational cost.

The implementation avoids unnecessary copies in internal calculations where practical, although the validation layer returns a copied vector for a straightforward ownership model.

## 10. Java 17 Implementation

The Java implementation adopts an enterprise-oriented architecture.

It separates statistical calculation, validation policy, request processing, and result representation.

### 10.1 Domain Types

| Type | Purpose |
|---|---|
| `EstimationMethod` | Identifies the statistical method |
| `EstimationStatus` | Represents execution states |
| `PointEstimate` | Immutable point estimate record |
| `ConfidenceInterval` | Immutable interval record |
| `EstimatorEvaluation` | Immutable estimator evaluation record |
| `Estimator` | Defines a point-estimation contract |
| `EstimationPolicy` | Defines validation requirements |
| `DefaultEstimationPolicy` | Implements default validation |
| `EstimationService` | Coordinates estimation requests |

### 10.2 Enterprise Workflow

The service follows this sequence:

```text
Estimation Request
        |
        v
Request Validation
        |
        v
Dataset Validation
        |
        v
Estimator Execution
        |
        v
Point Estimate
        |
        v
Optional Confidence Interval
        |
        v
Audit Record

The service uses request identifiers to reject duplicate submissions.

It stores completed results in an in-memory audit registry.

Immutable records prevent callers from directly modifying completed estimation results.

### **10.3 Policy-Based Validation**

The validation interface allows different estimation policies to be implemented without modifying the statistical algorithms.

For example, a future policy may require:

- A minimum sample size.
- Approved data sources.
- A particular estimator for a given parameter.
- Restrictions on unsupported distributions.
- Additional numerical precision requirements.

The current implementation provides the default finite-observation policy.

The audit registry is in-memory and does not provide distributed transactions, persistent auditing, or concurrent request coordination.

## **11. PostgreSQL Implementation**

The PostgreSQL implementation models a relational statistical estimation workflow.

It separates datasets, observations, estimation requests, point estimates, confidence intervals, estimator definitions, and evaluation records.

### **11.1 Database Architecture**

```text
ESTIMATOR DEFINITIONS
        |
        v
ESTIMATION REQUESTS
        |
        +-------------------+
        |                   |
        v                   v
     DATASETS          REQUEST STATUS
        |
        v
    OBSERVATIONS
        |
        v
  POINT ESTIMATES
        |
        v
 CONFIDENCE INTERVALS

DATASETS
    |
    v
ESTIMATOR EVALUATIONS
```

### **11.2 Main Tables**

| Table | Purpose |
|---|---|
| `estimator_definitions` | Stores available estimation methods |
| `datasets` | Stores dataset metadata and lifecycle state |
| `observations` | Stores individual sample observations |
| `estimation_requests` | Tracks estimation operations |
| `point_estimates` | Stores calculated parameter estimates |
| `confidence_intervals` | Stores calculated interval bounds |
| `estimator_evaluations` | Stores estimator performance measurements |

### **11.3 Dataset Lifecycle**

Datasets use four states:

| State | Meaning |
|---|---|
| `DRAFT` | Observations may be added or modified |
| `VALIDATED` | Dataset validation has succeeded |
| `ACTIVE` | Dataset is available for estimation |
| `ARCHIVED` | Dataset is retained but unavailable for modification |

The validation function checks that observations exist and that binary datasets contain only zero and one.

A trigger prevents observation changes after validation.

The activation procedure only permits validated datasets to become active.

### **11.4 Estimation Request Lifecycle**

An estimation request follows:

```text
PENDING
   |
   v
RUNNING
   |
   +----------+
   |          |
   v          v
COMPLETED  REJECTED
```

The processing procedure:

1. Locks the selected request.
2. Confirms that the request is pending.
3. Checks estimator availability.
4. Checks dataset activation.
5. Calculates the requested point estimate.
6. Stores the result.
7. Calculates a supported confidence interval where applicable.
8. Marks the request completed.

A database exception prevents partial successful processing from being committed when the procedure is executed in a transaction.

### **11.5 Database Functions**

| Function | Purpose |
|---|---|
| `validate_dataset()` | Validates sample data |
| `calculate_sample_statistics()` | Calculates descriptive sample statistics |
| `calculate_point_estimate()` | Calculates supported point estimates |
| `normal_quantile()` | Calculates normal critical values |
| `student_t_quantile()` | Calculates Student's t critical values |
| `calculate_mean_interval()` | Calculates mean confidence intervals |
| `calculate_wilson_interval()` | Calculates Wilson proportion intervals |

### **11.6 Database Procedures**

`activate_dataset()` manages dataset activation.

`process_estimation_request()` executes the complete estimation workflow.

`reject_estimation_request()` records a rejection reason for eligible requests.

### **11.7 Database Views**

`estimation_report` combines estimation requests, datasets, estimator definitions, point estimates, and confidence intervals.

`dataset_summary` calculates observation counts, sample means, unbiased variances, maximum likelihood variances, and sample standard deviations.

These views provide a reporting layer without requiring repeated manual joins.

### **11.8 Database Integrity and Performance**

The database uses:

- Primary keys for entity identification.
- Foreign keys for relational integrity.
- Unique constraints for request codes and observation positions.
- Check constraints for valid confidence levels and parameter ranges.
- Triggers for observation lifecycle enforcement.
- Indexes for dataset retrieval, request status, and interval lookup.

The observation index supports ordered retrieval within a dataset.

The request status index supports operational monitoring.

For larger datasets, partitioning, bulk loading, parallel aggregation, and more specialized indexing may become relevant.

## **12. Comparing Estimation Methods**

The following table summarizes the methods implemented in the project.

| Method | Target | Main principle | Important condition |
|---|---|---|---|
| Arithmetic mean | Population mean | Average observations | Finite sample mean |
| Unbiased variance | Population variance | Bessel correction | At least two observations |
| MLE variance | Normal population variance | Likelihood maximization | Normal model for the stated MLE |
| Sample proportion | Bernoulli probability | Fraction of successes | Binary observations |
| Method of moments | Distribution parameter | Match sample and population moments | Appropriate finite moments |
| Exponential MLE | Exponential rate | Maximize likelihood | Non-negative exponential observations |
| Normal interval | Population mean | Normal critical value | Known variance for exact standard formulation |
| Student's t interval | Population mean | Student's t distribution | Independent normal sample for exact finite-sample coverage |
| Wilson interval | Population proportion | Score-based inversion | Independent Bernoulli observations |
| Bootstrap interval | Statistical parameter | Empirical resampling distribution | Representative sample and suitable bootstrap assumptions |

## **13. Practical Statistical Considerations**

### **13.1 Sample Representativeness**

A large sample does not automatically produce a reliable estimate.

Selection bias, measurement errors, missing observations, and non-response can produce misleading estimates even when sample size is substantial.

### **13.2 Independence**

Several calculations assume independent observations.

Repeated measurements from the same subject, time-series observations, clustered samples, and correlated observations may require alternative standard errors and sampling procedures.

### **13.3 Distributional Assumptions**

The Student's t interval has exact finite-sample coverage under independent normal sampling.

For non-normal populations, its behavior depends on sample size, skewness, tail behavior, and other characteristics.

The normal approximation should not automatically be treated as exact.

### **13.4 Numerical Precision**

Floating-point computations can introduce rounding errors.

The numerical implementations use double-precision arithmetic and iterative calculations.

Very large or extremely small observations may require numerically stable algorithms or higher-precision arithmetic.

### **13.5 Randomness and Reproducibility**

Bootstrap and simulation procedures depend on pseudo-random sampling.

Fixed seeds allow repeated executions to produce reproducible results within the same implementation and random-number algorithm.

A seed does not make statistical results universally identical across different programming languages or random-number generators.

### **13.6 Confidence Level and Interval Width**

Higher confidence levels generally produce wider intervals for the same estimation procedure and dataset.

Increasing sample size generally reduces interval width when other assumptions remain unchanged.

Interval width is a useful measure of precision, but it does not independently establish that the statistical model is appropriate.

## **14. Validation and Failure Conditions**

The five implementations include checks for common invalid operations.

| Condition | Expected behavior |
|---|---|
| Empty sample | Reject estimation |
| Non-finite observation | Reject estimation |
| Single observation for unbiased variance | Reject estimation |
| Invalid confidence level | Reject interval calculation |
| Non-binary proportion data | Reject proportion calculation |
| Negative exponential observation | Reject exponential estimation |
| All-zero exponential sample | Reject rate MLE |
| Invalid bootstrap repetition count | Reject bootstrap calculation |
| Unsupported estimation method | Reject request |
| Inactive database dataset | Reject database processing |
| Invalid binary database observations | Reject dataset validation |
| Duplicate estimation request identifier | Reject duplicate request |

Validation protects the calculation layer from invalid input but does not establish that the sample is unbiased or representative.

## **15. Execution Requirements**

### **Python**

- Python 3.10 or later.
- Standard-library dependencies only.
- Execute the script directly.
- Produces `estimation_results.json`.

### **JavaScript**

- Node.js 18 or later.
- Standard-library dependencies only.
- Uses CommonJS module syntax.
- Produces `estimation_results.json`.

### **C++17**

- A C++17-compatible compiler.
- Standard C++ library only.
- Compile using the C++17 language standard.

### **Java 17**

- Java Development Kit 17.
- No third-party dependencies.
- The source file is named `StatisticalEstimation.java`.

### **PostgreSQL**

- PostgreSQL 14 or later.
- Database privileges to create a schema, tables, functions, procedures, and triggers.
- Execute the SQL script within a transaction-capable PostgreSQL session.

## **16. Limitations and Interpretation**

The implementations provide a focused estimation framework rather than a complete statistical analysis platform.

The following limitations are important:

- The implemented mean intervals do not automatically handle unknown population structures or complex survey designs.
- The Wilson interval assumes independent Bernoulli observations.
- The bootstrap implementation uses percentile intervals rather than bias-corrected or accelerated bootstrap intervals.
- The exponential distribution estimator assumes the stated distributional model.
- The estimator simulation evaluates a sample mean under a normally distributed synthetic population.
- The PostgreSQL implementation provides deterministic estimation workflows but does not implement a general-purpose statistical distribution engine.
- The JavaScript and Java audit registries are in-memory.
- Numerical quantile implementations should be tested against independent reference calculations before use in high-stakes statistical applications.
- None of the implementations automatically detects sampling bias, measurement errors, or model misspecification.

The statistical validity of an estimate depends on the data-generating process, sampling design, estimator assumptions, and interpretation of uncertainty. An executable calculation is not, by itself, evidence that those assumptions are satisfied.
