# Conditional Distributions

## 1. Mathematical Foundations

A conditional distribution describes the probability behavior of one random variable when information about another random variable is available.

Let \(X\) and \(Y\) be random variables defined on the same probability space.

The joint distribution describes their combined behavior:

\[
P(X=x,Y=y)
\]

The marginal distribution describes the behavior of one variable independently of the observed value of the other:

\[
P(X=x)=\sum_y P(X=x,Y=y)
\]

Conditional distributions incorporate information about an event or random variable.

For a discrete random variable:

\[
P(Y=y\mid X=x)
=
\frac{P(X=x,Y=y)}{P(X=x)}
\]

This expression is defined when:

\[
P(X=x)>0
\]

Conditional distributions are useful in statistical inference, risk analysis, forecasting, classification, Bayesian reasoning, reliability engineering, and decision-making under uncertainty.

## 2. Four Important Distinctions

The implementations distinguish four related statistical concepts.

| Concept | Mathematical representation | Meaning |
|---|---|---|
| Joint distribution | \(P(X=x,Y=y)\) | Probability of two outcomes occurring together |
| Marginal distribution | \(P(Y=y)\) | Probability of an outcome without conditioning on another variable |
| Conditional distribution | \(P(Y=y\mid X=x)\) | Probability of an outcome given an observed condition |
| Conditional density | \(f_{Y\mid X}(y\mid x)\) | Density of a continuous variable given another variable |

These concepts are related but are not interchangeable.

A joint probability is not a conditional probability. A marginal probability is not a conditional density. Their mathematical definitions and normalization requirements differ.

---

## 3. Discrete Conditional Distributions

A discrete random variable takes values from a finite or countable set.

Its probability mass function (PMF) assigns probability to each possible outcome.

For two discrete random variables, the joint PMF is:

\[
p_{X,Y}(x,y)=P(X=x,Y=y)
\]

The marginal distribution of \(X\) is:

\[
p_X(x)=\sum_y p_{X,Y}(x,y)
\]

The marginal distribution of \(Y\) is:

\[
p_Y(y)=\sum_x p_{X,Y}(x,y)
\]

The conditional PMF of \(Y\) given \(X=x\) is:

\[
p_{Y\mid X}(y\mid x)
=
\frac{p_{X,Y}(x,y)}{p_X(x)}
\]

The resulting conditional probabilities must satisfy:

\[
\sum_y p_{Y\mid X}(y\mid x)=1
\]

### Example: Study performance

Consider two random variables:

- \(X\): study category.
- \(Y\): examination outcome.

Each variable takes values from 0 to 2.

The joint probability distribution is:

| X | Y | Joint probability |
|---:|---:|---:|
| 0 | 0 | 0.10 |
| 0 | 1 | 0.10 |
| 0 | 2 | 0.05 |
| 1 | 0 | 0.05 |
| 1 | 1 | 0.20 |
| 1 | 2 | 0.15 |
| 2 | 0 | 0.05 |
| 2 | 1 | 0.10 |
| 2 | 2 | 0.20 |
| **Total** | | **1.00** |

The marginal probability of \(X=1\) is:

\[
P(X=1)=0.05+0.20+0.15=0.40
\]

The conditional probabilities are:

\[
P(Y=0\mid X=1)=\frac{0.05}{0.40}=0.125
\]

\[
P(Y=1\mid X=1)=\frac{0.20}{0.40}=0.50
\]

\[
P(Y=2\mid X=1)=\frac{0.15}{0.40}=0.375
\]

Therefore:

| Y | Conditional probability |
|---:|---:|
| 0 | 0.125 |
| 1 | 0.500 |
| 2 | 0.375 |
| **Total** | **1.000** |

This demonstrates how conditioning changes the probability distribution.

### Conditional PMF in the implementations

| Language | Implementation |
|---|---|
| Python | `conditional_pmf_y_given_x()` |
| JavaScript | `conditional()` |
| C++17 | `conditionalYGivenX()` |
| Java 17 | `conditionalPMF()` |
| PostgreSQL | `conditional_pmf_y_given_x()` |

Each implementation checks whether the conditioning event has positive probability before calculating the conditional distribution.

An event with zero probability cannot be used as the denominator of the ordinary conditional PMF formula.

---

## 4. Conditional Expectation

Conditional expectation represents the expected value of a random variable when information about another variable is available.

For a discrete random variable:

\[
E[Y\mid X=x]
=
\sum_y yP(Y=y\mid X=x)
\]

Using the examination example:

\[
E[Y\mid X=1]
=
0(0.125)+1(0.50)+2(0.375)
\]

Therefore:

\[
\boxed{E[Y\mid X=1]=1.25}
\]

The conditional expectation is the weighted average of possible outcomes using conditional probabilities.

### Conditional expectation as a random variable

When conditioning on \(X\), the expression:

\[
E[Y\mid X]
\]

is itself a random variable.

Its value depends on the observed value of \(X\).

For the example:

| X | P(X) | E[Y\|X=x] |
|---:|---:|---:|
| 0 | 0.25 | 0.80 |
| 1 | 0.40 | 1.25 |
| 2 | 0.35 | 1.428571 |

This distinction is important:

- \(E[Y\mid X=x]\) is a numerical value for a specified condition.
- \(E[Y\mid X]\) is a random variable determined by \(X\).

### Practical applications

Conditional expectation is used for:

- Estimating expected financial losses given market conditions.
- Predicting demand given seasonal information.
- Estimating system failures given operating conditions.
- Calculating expected examination outcomes given study categories.
- Estimating operational performance given workload.

---

## 5. Conditional Variance

Conditional variance measures the uncertainty remaining in a random variable after conditioning on another variable.

For a discrete distribution:

\[
Var(Y\mid X=x)
=
\sum_y
(y-E[Y\mid X=x])^2
P(Y=y\mid X=x)
\]

An equivalent computational expression is:

\[
Var(Y\mid X=x)
=
E[Y^2\mid X=x]
-
(E[Y\mid X=x])^2
\]

For \(X=1\), the conditional expectation is 1.25.

The conditional variance is:

\[
Var(Y\mid X=1)
=
(0-1.25)^2(0.125)
\]

\[
+(1-1.25)^2(0.50)
\]

\[
+(2-1.25)^2(0.375)
\]

Therefore:

\[
\boxed{Var(Y\mid X=1)=0.4375}
\]

### Interpretation

Conditional expectation and conditional variance describe different properties.

| Measure | Interpretation |
|---|---|
| Conditional expectation | Expected outcome under a specified condition |
| Conditional variance | Remaining uncertainty under that condition |
| Low conditional variance | Outcomes are concentrated around the conditional mean |
| High conditional variance | Outcomes are more dispersed |

A condition can change the expected value without necessarily reducing uncertainty.

Similarly, two conditions can produce the same conditional expectation but different conditional variances.

---

## 6. Continuous Conditional Distributions

Continuous random variables are described using probability density functions rather than probability mass functions.

Let \(X\) and \(Y\) have joint density:

\[
f_{X,Y}(x,y)
\]

The marginal density of \(X\) is:

\[
f_X(x)
=
\int_{-\infty}^{\infty}
f_{X,Y}(x,y)\,dy
\]

The conditional density of \(Y\) given \(X=x\) is:

\[
\boxed{
f_{Y\mid X}(y\mid x)
=
\frac{f_{X,Y}(x,y)}{f_X(x)}
}
\]

This expression requires:

\[
f_X(x)>0
\]

The conditional density must integrate to one:

\[
\int_{-\infty}^{\infty}
f_{Y\mid X}(y\mid x)\,dy=1
\]

### Important distinction

For a continuous random variable:

\[
P(X=x)=0
\]

for an individual point under an absolutely continuous distribution.

The conditional density is therefore defined through a density ratio or an appropriate conditional probability model, not by directly dividing two point probabilities.

Conditional density values are not themselves probabilities. Probabilities are obtained by integrating density over intervals.

---

## 7. Bivariate Normal Conditional Distribution

The implementations include a bivariate normal model.

Let:

\[
\begin{pmatrix}
X\\
Y
\end{pmatrix}
\sim
N
\left(
\begin{pmatrix}
\mu_X\\
\mu_Y
\end{pmatrix},
\begin{pmatrix}
\sigma_X^2 & \rho\sigma_X\sigma_Y\\
\rho\sigma_X\sigma_Y & \sigma_Y^2
\end{pmatrix}
\right)
\]

Where:

- \(\mu_X\): mean of X.
- \(\mu_Y\): mean of Y.
- \(\sigma_X\): standard deviation of X.
- \(\sigma_Y\): standard deviation of Y.
- \(\rho\): correlation coefficient.

The conditional distribution is:

\[
\boxed{
Y\mid X=x
\sim
N(\mu_{Y\mid X},\sigma_{Y\mid X}^2)
}
\]

The conditional mean is:

\[
\boxed{
\mu_{Y\mid X}
=
\mu_Y+
\rho\frac{\sigma_Y}{\sigma_X}(x-\mu_X)
}
\]

The conditional variance is:

\[
\boxed{
\sigma_{Y\mid X}^2
=
\sigma_Y^2(1-\rho^2)
}
\]

The conditional density is:

\[
f_{Y\mid X}(y\mid x)
=
\frac{1}{\sqrt{2\pi\sigma_{Y\mid X}^2}}
\exp
\left(
-\frac{(y-\mu_{Y\mid X})^2}
{2\sigma_{Y\mid X}^2}
\right)
\]

### Numerical example

Consider:

| Parameter | Value |
|---|---:|
| \(\mu_X\) | 10 |
| \(\mu_Y\) | 50 |
| \(\sigma_X\) | 2 |
| \(\sigma_Y\) | 8 |
| \(\rho\) | 0.75 |
| Observed X | 12 |

The conditional mean becomes:

\[
50+
0.75\frac{8}{2}(12-10)
\]

\[
\boxed{\mu_{Y\mid X=12}=56}
\]

The conditional variance is:

\[
8^2(1-0.75^2)
\]

\[
\boxed{\sigma_{Y\mid X}^2=28}
\]

Thus:

\[
Y\mid X=12\sim N(56,28)
\]

The conditional standard deviation is:

\[
\sqrt{28}\approx5.2915
\]

This shows how observing \(X\) changes the distribution of \(Y\).

---

## 8. Law of Total Expectation

The law of total expectation connects conditional expectation with unconditional expectation.

\[
\boxed{
E[Y]=E[E[Y\mid X]]
}
\]

For discrete \(X\):

\[
E[Y]
=
\sum_x P(X=x)E[Y\mid X=x]
\]

Using the example:

\[
E[Y]
=
0.25(0.80)
+
0.40(1.25)
+
0.35(1.428571)
\]

\[
\boxed{E[Y]=1.15}
\]

The result is identical to calculating the expectation directly from the marginal distribution of \(Y\).

### Practical significance

This identity allows a complex expected value to be decomposed into smaller conditional calculations.

It is useful when:

- Outcomes are grouped by operating conditions.
- Financial losses are estimated across economic scenarios.
- Demand forecasts are calculated for different customer segments.
- Risk models use conditional expected losses.

All five implementations verify this identity using the same discrete example.

---

## 9. Law of Total Variance

The law of total variance decomposes unconditional uncertainty into two components.

\[
\boxed{
Var(Y)
=
E[Var(Y\mid X)]
+
Var(E[Y\mid X])
}
\]

The first component is:

\[
E[Var(Y\mid X)]
\]

It represents the expected uncertainty remaining within each condition.

The second component is:

\[
Var(E[Y\mid X])
\]

It represents variation between conditional expectations.

### Interpretation

| Component | Statistical meaning |
|---|---|
| Expected conditional variance | Within-condition variability |
| Variance of conditional expectations | Between-condition variability |
| Total variance | Combined unconditional variability |

This decomposition is important in hierarchical statistical models, grouped data analysis, forecasting, and variance-component analysis.

It also explains why conditioning can reduce uncertainty: information about \(X\) separates within-condition variation from between-condition variation.

The implementations calculate the two components independently and compare their sum against the directly calculated marginal variance.

---

## 10. Conditional Covariance

Conditional covariance measures the relationship between two random variables under a specified condition.

For example, the conditional covariance of \(Y\) and \(Z\) given \(X\) is:

\[
Cov(Y,Z\mid X)
=
E[
(Y-E[Y\mid X])
(Z-E[Z\mid X])
\mid X
]
\]

It is distinct from ordinary covariance:

\[
Cov(X,Y)=E[(X-E[X])(Y-E[Y])]
\]

The Python, C++17, and Java implementations calculate ordinary covariance for their discrete joint distributions.

This provides an additional measure of dependence between the modeled variables.

---

## 11. Implementation Architecture

### Python

The Python implementation uses:

| Component | Responsibility |
|---|---|
| `DiscreteJointDistribution` | Joint PMF and conditional probability calculations |
| `ConditionalStatistics` | Immutable conditional statistical results |
| `BivariateNormal` | Continuous conditional density calculations |
| `DistributionError` | Invalid distribution and conditioning failures |
| `run_examples()` | End-to-end execution and validation |

Python uses dictionaries for PMF representation and `math.fsum()` for more accurate floating-point summation.

It also includes reproducible conditional sampling and JSON export.

### JavaScript

The JavaScript implementation uses an event-driven service architecture.

| Component | Responsibility |
|---|---|
| `JointDistribution` | Joint and conditional probability management |
| `BivariateNormal` | Conditional density and approximate CDF |
| `ConditionalAnalysisService` | Asynchronous statistical analysis |
| `EventEmitter` | Analysis completion and failure notifications |
| Node.js file system | Structured JSON output |

The service records successful analysis events and separates calculation failures from application-level execution.

The conditional CDF uses a numerical approximation rather than an external statistical package.

### C++17

The C++ implementation emphasizes explicit mathematical computation and value-oriented domain modeling.

| Component | Responsibility |
|---|---|
| `Outcome` | Joint probability record |
| `Statistics` | Conditional statistical result |
| `DiscreteJointDistribution` | Discrete probability calculations |
| `BivariateNormal` | Continuous conditional density |
| `DistributionError` | Validation and calculation failures |

The implementation uses STL containers and algorithms while avoiding third-party dependencies.

### Java 17

The Java implementation follows an enterprise-oriented service design.

| Component | Responsibility |
|---|---|
| `Outcome` record | Immutable probability observation |
| `ConditionalResult` record | Immutable analysis result |
| `ConditionalDistribution` | Distribution contract |
| `DiscreteJointDistribution` | Joint and conditional probability model |
| `BivariateNormal` | Continuous probability model |
| `AnalysisService` | Statistical execution and audit history |

Immutable records help prevent accidental modification of published statistical results.

The service synchronizes access to its audit history.

### PostgreSQL

The SQL implementation provides a relational model for probability distributions.

| Database object | Purpose |
|---|---|
| `distribution_models` | Distribution metadata |
| `joint_probability_observations` | Joint PMF records |
| `bivariate_normal_parameters` | Continuous distribution parameters |
| `marginal_x_distribution` | Marginal PMF of X |
| `marginal_y_distribution` | Marginal PMF of Y |
| `conditional_pmf_y_given_x()` | Conditional PMF retrieval |
| `conditional_statistics()` | Conditional expectation and variance |
| `joint_covariance()` | Joint covariance calculation |
| `total_expectation_y()` | Law of total expectation |
| `total_variance_y()` | Law of total variance |
| `normal_conditional_density()` | Bivariate normal conditional density |
| `conditional_statistics_report` | Reusable conditional reporting |

The database uses primary keys, foreign keys, unique constraints, check constraints, indexes, SQL functions, views, and transactions.

Discrete probabilities use `NUMERIC` to reduce decimal representation errors. Continuous density calculations use `DOUBLE PRECISION`.

---

## 12. Execution and Data Processing Workflow

The implementations follow this general statistical workflow:

    Define distribution parameters or joint observations
                         |
                         v
              Validate input parameters
                         |
                         v
                Validate normalization
                         |
                         v
                 Calculate marginals
                         |
                         v
             Select conditioning variable
                         |
                         v
             Check conditioning probability
                         |
                         v
             Calculate conditional PMF
                         |
                         v
           Calculate conditional expectation
                         |
                         v
             Calculate conditional variance
                         |
                         v
             Verify mathematical identities
                         |
                         v
                Generate statistical report

The continuous distribution workflow uses the specified bivariate normal parameters to calculate conditional mean, conditional variance, and conditional density.

---

## 13. Validation and Failure Conditions

Probability calculations require explicit validation.

| Failure condition | Required handling |
|---|---|
| Empty joint distribution | Reject input |
| Negative probability | Reject input |
| Probability greater than one | Reject input |
| Joint probabilities not summing to one | Reject distribution |
| Zero conditioning probability | Reject conditional calculation |
| Invalid standard deviation | Reject continuous model |
| Correlation outside valid bounds | Reject continuous model |
| Non-finite numerical input | Reject calculation |
| Invalid distribution parameters | Prevent statistical execution |

The implementations use a numerical tolerance when validating probability normalization and mathematical identities.

This is necessary because floating-point arithmetic can introduce small numerical differences.

The database also validates the total probability of a published discrete distribution through an explicit validation function.

The SQL normalization check is performed when requested rather than through a row-level constraint. A row-level check cannot independently enforce a sum across multiple records.

---

## 14. Computational Complexity

Let:

- \(n\) represent the number of joint probability observations.
- \(k\) represent the number of distinct conditioning values.
- \(m\) represent the number of distinct conditional outcomes.

| Operation | Typical complexity |
|---|---|
| Joint probability lookup in dictionary/map | \(O(1)\) average |
| Marginal calculation using direct scanning | \(O(n)\) |
| Conditional PMF using direct scanning | \(O(n)\) |
| Conditional expectation from a PMF | \(O(m)\) |
| Conditional variance from a PMF | \(O(m)\) |
| Total expectation using repeated scans | \(O(kn)\) |
| Total variance using repeated scans | \(O(kn)\) |
| Conditional normal density | \(O(1)\) |

The Python, C++, and Java implementations favor transparent calculations over maintaining multiple derived indexes.

The JavaScript implementation uses maps for joint outcome storage but still scans the joint observations when aggregating conditional distributions.

For large datasets, pre-aggregated marginal distributions and indexed conditional probability tables can substantially reduce repeated computation.

PostgreSQL composite indexes support filtering by distribution identifier and conditioning value.

---

## 15. Statistical and Operational Limitations

### Discrete versus continuous models

A discrete PMF assigns probability directly to outcomes.

A continuous density describes probability concentration over a range. A density value cannot be interpreted directly as the probability of an individual point.

### Conditional model assumptions

The bivariate normal implementation assumes:

- Both variables follow a joint normal distribution.
- The covariance matrix is positive definite.
- Both standard deviations are positive.
- Correlation lies strictly between -1 and 1.

The conditional normal formulas are not automatically applicable to arbitrary joint distributions.

### Numerical precision

Floating-point calculations can produce small numerical discrepancies.

Probability normalization checks therefore use tolerances.

For high-precision applications, numerical integration and more advanced statistical libraries may be necessary.

### Simulation

The Python implementation uses a fixed random seed for reproducibility.

Simulated sample statistics are estimates, not exact theoretical values.

Differences between simulated and theoretical moments are expected because of finite sample sizes.

### Data quality

A mathematically normalized joint distribution is not necessarily a statistically valid model of a real-world population.

The source data, sampling process, measurement definitions, and modeling assumptions must also be evaluated.

---

## 16. Practical Applications

| Application | Conditioning variable | Variable of interest |
|---|---|---|
| Financial risk | Market condition | Portfolio loss |
| Healthcare analytics | Patient characteristics | Clinical outcome |
| Demand forecasting | Season or economic condition | Product demand |
| Reliability engineering | Operating temperature | Equipment lifetime |
| Educational analytics | Study category | Examination outcome |
| Cybersecurity | Threat category | Expected incident severity |
| Cloud operations | Workload level | Infrastructure response time |
| Insurance | Policy characteristics | Expected claim amount |

Conditional expectation provides estimates of expected outcomes under known conditions.

Conditional variance measures the remaining uncertainty under those conditions.

Conditional density provides a continuous probabilistic description when the variables are modeled using continuous distributions.

These measures should be interpreted together when evaluating uncertainty and making decisions based on observed information.
