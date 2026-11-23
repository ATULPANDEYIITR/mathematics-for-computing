# Multivariate Statistics: Multiple Regression, Multivariate Distributions, and Covariance Structures

## 1. Project Overview

This project implements three connected areas of multivariate statistics across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The central objective is to understand relationships between multiple quantitative variables, estimate statistical models, describe their joint variability, and evaluate observations against multivariate probability distributions.

The implementations use a business analytics scenario involving:

- Advertising expenditure.
- Employee training hours.
- Monthly sales performance.

The second scenario uses two correlated measurements to demonstrate multivariate normal distributions and statistical anomaly detection.

The project distinguishes three statistical concepts:

| Statistical area | Primary objective | Main techniques |
|---|---|---|
| Multiple regression | Explain or predict an outcome using several predictors | OLS, coefficients, residuals, R-squared |
| Multivariate distributions | Describe the joint probability behaviour of variables | Multivariate normal distribution, density, Mahalanobis distance |
| Covariance structures | Measure joint variability and dependence | Covariance matrix, correlation matrix, Cholesky decomposition |

These techniques are related but answer different statistical questions.

## 2. Mathematical Foundations

### 2.1 Random vectors

Univariate statistics describe one variable at a time.

Multivariate statistics considers a collection of random variables represented by a random vector:

\[
X =
\begin{bmatrix}
X_1\\
X_2\\
\vdots\\
X_p
\end{bmatrix}
\]

For the business scenario:

\[
X =
\begin{bmatrix}
\text{Advertising}\\
\text{Training Hours}\\
\text{Sales}
\end{bmatrix}
\]

The variables may have different units, distributions, means, and variances. Their joint behaviour is important because changes in one variable may be associated with changes in another.

### 2.2 Mean vector

The population mean vector is:

\[
\boldsymbol{\mu}=E[X]
\]

Its sample estimate is:

\[
\bar X =
\begin{bmatrix}
\bar X_1\\
\bar X_2\\
\vdots\\
\bar X_p
\end{bmatrix}
\]

where:

\[
\bar X_j=\frac{1}{n}\sum_{i=1}^{n}X_{ij}
\]

Each element represents the average value of one variable.

### 2.3 Covariance

Covariance measures the direction and magnitude of joint linear variation between two variables.

The sample covariance is:

\[
s_{ij}=
\frac{1}{n-1}
\sum_{k=1}^{n}
(X_{ki}-\bar X_i)(X_{kj}-\bar X_j)
\]

Interpretation:

- Positive covariance indicates that variables tend to increase together.
- Negative covariance indicates that one variable tends to increase when the other decreases.
- Near-zero covariance indicates limited linear co-variation.

Zero covariance does not necessarily imply independence.

Covariance depends on measurement units. A covariance involving expenditure measured in thousands differs numerically from one involving expenditure measured in individual currency units.

### 2.4 Covariance matrix

The covariance matrix collects all pairwise covariances:

\[
\Sigma=
\begin{bmatrix}
\sigma_{11}&\sigma_{12}&\cdots&\sigma_{1p}\\
\sigma_{21}&\sigma_{22}&\cdots&\sigma_{2p}\\
\vdots&\vdots&\ddots&\vdots\\
\sigma_{p1}&\sigma_{p2}&\cdots&\sigma_{pp}
\end{bmatrix}
\]

Its diagonal contains variances:

\[
\sigma_{ii}=\operatorname{Var}(X_i)
\]

Its off-diagonal elements contain covariances:

\[
\sigma_{ij}=\operatorname{Cov}(X_i,X_j)
\]

Important properties:

- It is symmetric.
- Its diagonal elements are nonnegative.
- It is positive semidefinite for valid population covariance structures.
- It may be singular when variables are linearly dependent.

The sample covariance matrix in the implementations uses the unbiased denominator \(n-1\).

### 2.5 Correlation matrix

Correlation standardizes covariance:

\[
\rho_{ij}=
\frac{\operatorname{Cov}(X_i,X_j)}
{\sigma_i\sigma_j}
\]

The sample correlation matrix has values between -1 and +1.

| Correlation | Interpretation |
|---|---|
| +1 | Perfect positive linear relationship |
| Between 0 and +1 | Positive linear association |
| 0 | No linear association |
| Between -1 and 0 | Negative linear association |
| -1 | Perfect negative linear relationship |

Correlation is dimensionless, making it useful for comparing relationships between variables with different units.

Correlation does not establish causation.

## 3. Multiple Linear Regression

### 3.1 Definition

Multiple linear regression estimates the relationship between one dependent variable and two or more independent variables.

The general model is:

\[
Y=\beta_0+\beta_1X_1+\beta_2X_2+
\cdots+\beta_pX_p+\epsilon
\]

Where:

- \(Y\) is the dependent variable.
- \(X_1,\ldots,X_p\) are predictors.
- \(\beta_0\) is the intercept.
- \(\beta_j\) represents a predictor coefficient.
- \(\epsilon\) is the random error term.

The implemented business model is:

\[
Sales=\beta_0+
\beta_1(Advertising)+
\beta_2(Training)+\epsilon
\]

The coefficients describe conditional associations, holding the other included predictors constant.

A regression coefficient should not automatically be interpreted as a causal effect.

### 3.2 Matrix representation

The model can be represented as:

\[
Y=X\beta+\epsilon
\]

The design matrix includes a column of ones for the intercept:

\[
X=
\begin{bmatrix}
1&x_{11}&x_{12}\\
1&x_{21}&x_{22}\\
\vdots&\vdots&\vdots\\
1&x_{n1}&x_{n2}
\end{bmatrix}
\]

The ordinary least squares estimator is:

\[
\hat{\beta}=(X^TX)^{-1}X^TY
\]

This estimator minimizes the residual sum of squares:

\[
RSS=\sum_{i=1}^{n}(Y_i-\hat Y_i)^2
\]

The normal equations are implemented in all five programming environments.

The implementations use Gaussian elimination with partial pivoting to solve the coefficient system. Explicit matrix inversion is avoided.

This improves numerical handling compared with directly computing an inverse, although normal equations can still be unstable when predictors are highly correlated.

For production applications involving poorly conditioned or large design matrices, QR decomposition or singular value decomposition is preferable.

### 3.3 Regression coefficients

The intercept estimates the expected response when all predictors equal zero.

Each slope coefficient estimates the change in predicted response associated with a one-unit increase in that predictor while other included predictors remain fixed.

For example:

\[
\hat Y=\hat\beta_0+
\hat\beta_1X_1+
\hat\beta_2X_2
\]

A positive \(\hat\beta_1\) indicates a positive conditional association between advertising and predicted sales.

The magnitude must be interpreted using the measurement units and scale of the predictor.

### 3.4 Predictions

For a new observation:

\[
\hat Y_{new}=
\hat\beta_0+
\hat\beta_1X_{1,new}+
\hat\beta_2X_{2,new}
\]

The Python, JavaScript, and Java implementations expose prediction operations through their regression models or services.

Prediction outside the observed predictor range is extrapolation and may be unreliable.

### 3.5 Model evaluation

**Coefficient of determination**

\[
R^2=1-\frac{RSS}{TSS}
\]

Where:

\[
TSS=\sum_{i=1}^{n}(Y_i-\bar Y)^2
\]

R-squared measures the proportion of observed target variation explained by the fitted model relative to an intercept-only baseline.

**Adjusted R-squared**

\[
R^2_{adj}=
1-(1-R^2)\frac{n-1}{n-p-1}
\]

Adjusted R-squared accounts for the number of predictors and penalizes unnecessary model complexity.

**Mean squared error**

\[
MSE=\frac{1}{n}\sum_{i=1}^{n}(Y_i-\hat Y_i)^2
\]

**Root mean squared error**

\[
RMSE=\sqrt{MSE}
\]

RMSE expresses prediction error in the original target measurement units.

**Residual variance**

\[
\hat\sigma^2=
\frac{RSS}{n-p-1}
\]

Residual variance uses the residual degrees of freedom after estimating the intercept and predictor coefficients.

The implementations distinguish training MSE from residual variance.

### 3.6 Regression assumptions

The conventional inferential interpretation of ordinary least squares depends on assumptions that should be assessed separately.

| Assumption | Meaning | Potential problem |
|---|---|---|
| Linearity | Conditional mean is linear in the model parameters | Systematic residual patterns |
| Independence | Errors are independent across observations | Serial or clustered dependence |
| Homoscedasticity | Error variance is constant | Heteroscedastic residuals |
| No perfect multicollinearity | Predictors are not exact linear combinations | Non-identifiable coefficients |
| Exogeneity | Predictors are uncorrelated with the error | Biased coefficient estimates |
| Normal errors | Conditional errors are normally distributed for conventional small-sample inference | Invalid classical small-sample tests |

Normality of errors is not required for calculating OLS coefficients.

The supplied regression implementations calculate coefficients and descriptive evaluation measures. They do not claim to perform complete statistical inference.

## 4. Multicollinearity

Multicollinearity occurs when predictors are strongly linearly associated.

It can produce:

- Unstable coefficient estimates.
- Large coefficient standard errors.
- Sensitivity to individual observations.
- Difficulty separating individual predictor contributions.

The Python implementation includes variance inflation factor calculations.

For predictor \(j\):

\[
VIF_j=\frac{1}{1-R_j^2}
\]

Here, \(R_j^2\) comes from regressing predictor \(j\) on all remaining predictors.

A VIF of 1 indicates no linear relationship with the other predictors. Increasing values indicate increasing multicollinearity.

VIF thresholds are diagnostic conventions rather than universal decision rules.

The C++17, JavaScript, Java, and PostgreSQL implementations focus on regression estimation and covariance analysis rather than providing a complete multicollinearity diagnostic framework.

## 5. Multivariate Probability Distributions

### 5.1 Definition

A multivariate distribution describes the joint probability behaviour of several random variables.

Unlike separate univariate distributions, it incorporates the relationships between variables.

A major example is the multivariate normal distribution:

\[
X\sim N_p(\mu,\Sigma)
\]

Where:

- \(p\) is the number of dimensions.
- \(\mu\) is the mean vector.
- \(\Sigma\) is the covariance matrix.

The covariance matrix determines the scale, orientation, and dependence structure of the distribution.

### 5.2 Multivariate normal probability density

The multivariate normal density is:

\[
f(x)=
\frac{
\exp\left(
-\frac12(x-\mu)^T\Sigma^{-1}(x-\mu)
\right)
}{
(2\pi)^{p/2}|\Sigma|^{1/2}
}
\]

The formula requires a symmetric positive-definite covariance matrix.

The density is a probability density, not the probability of an exact continuous observation.

Probabilities are obtained by integrating the density over a region.

### 5.3 Determinant and positive definiteness

The determinant of the covariance matrix measures generalized variance.

For a valid nonsingular multivariate normal covariance matrix:

\[
|\Sigma|>0
\]

Positive definiteness ensures that the density is mathematically valid and that the covariance matrix has an invertible structure.

The implementations use Cholesky decomposition to test positive definiteness.

### 5.4 Cholesky decomposition

For a symmetric positive-definite matrix:

\[
\Sigma=LL^T
\]

Where \(L\) is lower triangular.

Cholesky decomposition is useful for:

- Testing covariance matrix validity.
- Efficiently solving linear systems.
- Calculating determinants.
- Computing Mahalanobis distance.
- Generating multivariate normal observations.

The implementation calculates the lower-triangular factor without explicitly calculating the covariance inverse.

### 5.5 Mahalanobis distance

Euclidean distance treats all dimensions equally and ignores their covariance structure.

Mahalanobis distance accounts for variance and correlation:

\[
D_M(x)=
\sqrt{(x-\mu)^T\Sigma^{-1}(x-\mu)}
\]

It measures how far an observation is from the multivariate mean in covariance-adjusted units.

Its advantages include:

- Accounting for different measurement scales.
- Accounting for correlations.
- Identifying observations unusual relative to the joint distribution.
- Supporting multivariate anomaly detection.

An observation that appears unusual in one variable may be normal in the joint distribution, or the reverse.

### 5.6 Anomaly detection

The implementations classify observations using a configurable Mahalanobis distance threshold.

The classification rule is:

\[
D_M(x)>c
\]

Where \(c\) is the configured threshold.

A distance threshold is not automatically a calibrated statistical significance level.

For a known multivariate normal distribution, squared Mahalanobis distance follows a chi-squared distribution with \(p\) degrees of freedom:

\[
D_M^2\sim\chi_p^2
\]

This relationship supports probability-based threshold selection when the distributional assumptions are appropriate.

When parameters are estimated from the same sample, the reference distribution requires additional consideration.

Practical applications should calibrate thresholds using validation observations and account for false-positive costs.

## 6. Covariance Structures and Multivariate Dependence

Covariance structures describe how the variability of one variable relates to the variability of other variables.

Three important structures are:

**Diagonal covariance**

\[
\Sigma=
\begin{bmatrix}
\sigma_1^2&0\\
0&\sigma_2^2
\end{bmatrix}
\]

This represents zero covariance between the variables.

For a jointly multivariate normal distribution, zero covariance implies independence.

**Compound symmetry**

\[
\Sigma=
\begin{bmatrix}
\sigma^2&\rho\sigma^2\\
\rho\sigma^2&\sigma^2
\end{bmatrix}
\]

This represents equal marginal variances and a common pairwise covariance.

**Unstructured covariance**

\[
\Sigma=
\begin{bmatrix}
\sigma_1^2&\sigma_{12}\\
\sigma_{12}&\sigma_2^2
\end{bmatrix}
\]

Each variance and covariance is estimated independently, subject to symmetry and positive-definiteness constraints.

The project estimates an unstructured sample covariance matrix.

The SQL implementation persists pairwise covariance and correlation values in relational form.

## 7. Programming Implementation Architecture

### 7.1 Python

Python provides a compact implementation of the statistical workflow.

| Component | Implementation |
|---|---|
| Matrix validation | `validate_matrix()` |
| Matrix multiplication | `matmul()` |
| Linear equation solver | `solve_linear_system()` |
| Sample covariance | `covariance_matrix()` |
| Correlation | `correlation_matrix()` |
| Matrix factorization | `cholesky()` |
| Multiple regression | `multiple_regression()` |
| Multicollinearity | `variance_inflation_factors()` |
| Multivariate density | `multivariate_normal_density()` |
| Random sampling | `generate_multivariate_normal()` |

The `RegressionResult` dataclass stores the fitted model and its evaluation metrics.

The implementation uses deterministic random sampling through a fixed seed.

Assertions and exception handling validate statistical invariants and reject invalid numerical inputs.

The Python implementation additionally calculates VIF, providing a diagnostic perspective on predictor dependence.

### 7.2 JavaScript

The JavaScript implementation emphasizes streaming statistics and event-driven monitoring.

Its central component is `OnlineCovariance`.

It implements the multivariate extension of Welford's algorithm.

Instead of storing every observation, it incrementally updates:

- Observation count.
- Mean vector.
- Cross-product matrix.

For each new observation, it updates the mean and cross-products using the difference between the observation and the previous mean.

The resulting sample covariance is:

\[
S=\frac{M_2}{n-1}
\]

Where \(M_2\) represents the accumulated centered cross-products.

This approach avoids storing the full dataset.

The `StatisticalMonitor` class uses Node.js `EventEmitter` to separate statistical processing from downstream event handling.

Its events include:

- `observation`
- `normal`
- `anomaly`

This architecture is suitable for streaming analytics and monitoring systems.

The report-export function uses the Node.js filesystem API and restricts filenames to a safe pattern.

### 7.3 C++17

The C++ implementation emphasizes explicit mathematical operations and computational efficiency.

Its architecture separates:

- `MatrixOperations`
- `CovarianceAnalyzer`
- `MultipleRegression`
- `CholeskyDecomposition`
- `MultivariateDistribution`
- `AnomalyDetector`

STL vectors represent matrices and vectors.

The matrix solver uses partial pivoting and rejects singular systems.

The anomaly detector evaluates observations using a previously defined covariance structure.

The random sampling example uses the Mersenne Twister generator and standard normal distribution.

This implementation illustrates how statistical operations can be integrated into a strongly typed numerical processing system.

### 7.4 Java 17

The Java implementation emphasizes enterprise-oriented service separation and explicit result structures.

Its major components are:

| Component | Responsibility |
|---|---|
| `MatrixService` | Matrix operations, validation, linear solving, Cholesky decomposition |
| `RegressionService` | Regression fitting and prediction |
| `CovarianceService` | Mean, covariance, and correlation calculations |
| `MultivariateNormalService` | Density and Mahalanobis distance |
| `StatisticalMonitoringService` | Observation classification |
| `RegressionResult` | Immutable regression results |
| `CovarianceResult` | Covariance and correlation results |
| `MonitoringEvent` | Statistical monitoring outcome |

Java records represent result objects.

The service-based structure separates numerical calculations from business-facing operations.

The monitoring layer uses explicit states:

- `NORMAL`
- `ANOMALY`

The model validates its covariance structure during initialization.

This provides a foundation for integrating statistical calculations into larger enterprise applications.

### 7.5 PostgreSQL

The PostgreSQL implementation represents the statistical workflow through relational structures.

Its schema contains:

| Table | Purpose |
|---|---|
| `datasets` | Dataset metadata and operational status |
| `observations` | Predictor and response measurements |
| `regression_models` | Fitted regression coefficients and evaluation metrics |
| `covariance_structures` | Persisted pairwise covariance and correlation |
| `distribution_profiles` | Mean vectors and covariance parameters |
| `distribution_evaluations` | Mahalanobis distances, density values, and classifications |

The implementation also includes:

- Primary and foreign keys.
- Unique constraints.
- Measurement validation.
- Performance-oriented indexes.
- Descriptive statistics views.
- Covariance and correlation views.
- Regression functions.
- Prediction functions.
- Multivariate density calculations.
- Anomaly evaluation.
- Transaction handling.

The database regression implementation is intentionally restricted to two predictors and an intercept.

It calculates sufficient statistics directly from the observations rather than constructing a complete design matrix in memory.

The augmented three-variable normal-equation system is solved through Gaussian elimination.

The distribution functions use explicit two-dimensional covariance algebra.

These limitations make the database implementation suitable for demonstrating relational statistical workflows without introducing an external numerical extension.

## 8. End-to-End Statistical Workflow

The complete analytical process follows this sequence:

**Stage 1: Data preparation**

Collect observations containing predictors and dependent variables.

Validate:

- Observation counts.
- Variable dimensions.
- Numeric values.
- Missing or non-finite values.
- Valid measurement ranges.

**Stage 2: Descriptive analysis**

Calculate:

- Means.
- Variances.
- Standard deviations.
- Minimum and maximum values.

**Stage 3: Covariance analysis**

Estimate the covariance and correlation matrices.

Identify relationships between predictors and potential multicollinearity.

**Stage 4: Regression estimation**

Construct the design matrix and estimate OLS coefficients.

Calculate fitted values and residuals.

**Stage 5: Model evaluation**

Calculate R-squared, adjusted R-squared, MSE, RMSE, and residual variance.

Assess assumptions separately before making inferential claims.

**Stage 6: Distribution estimation**

Define the mean vector and covariance matrix.

Validate positive definiteness through Cholesky decomposition.

**Stage 7: Multivariate evaluation**

Calculate Mahalanobis distances and multivariate normal densities.

Classify observations using an explicitly configured threshold.

**Stage 8: Reporting**

Persist statistical results, regression coefficients, covariance values, and observation classifications.

## 9. Computational Complexity

Let:

- \(n\) represent the number of observations.
- \(p\) represent the number of predictors.
- \(k\) represent the number of variables in a covariance structure.

| Operation | Time complexity | Additional space |
|---|---:|---:|
| Mean calculation | \(O(np)\) | \(O(p)\) |
| Covariance calculation | \(O(np^2)\) | \(O(p^2)\) |
| Correlation calculation | \(O(p^2)\) | \(O(p^2)\) |
| Matrix multiplication | \(O(p^3)\) for square matrices | \(O(p^2)\) |
| Gaussian elimination | \(O(p^3)\) | \(O(p^2)\) |
| Cholesky decomposition | \(O(k^3)\) | \(O(k^2)\) |
| Mahalanobis distance after factorization | \(O(k^2)\) | \(O(k)\) |
| Multivariate density after factorization | \(O(k^2)\) | \(O(k)\) |
| Online covariance update | \(O(p^2)\) per observation | \(O(p^2)\) |

For the general regression implementation, forming the normal equations requires approximately:

\[
O(np^2+p^3)
\]

The normal-equation method is computationally convenient for small and moderate predictor dimensions but may worsen numerical conditioning.

QR and SVD methods are preferable for ill-conditioned designs.

The JavaScript online covariance implementation requires fixed memory proportional to the square of the variable count, independently of the number of observations.

## 10. Validation and Failure Conditions

The implementations explicitly address important numerical and statistical failures.

| Failure condition | Detection mechanism | Expected behaviour |
|---|---|---|
| Empty matrix | Input validation | Reject operation |
| Inconsistent dimensions | Matrix validation | Reject operation |
| Non-finite observations | Numeric validation | Reject operation |
| Insufficient observations | Sample-size validation | Reject estimation |
| Singular design matrix | Pivot validation | Reject regression |
| Constant dependent variable | Total sum of squares | Reject R-squared calculation |
| Constant predictor | Correlation validation | Reject correlation |
| Non-symmetric covariance matrix | Symmetry check | Reject factorization |
| Non-positive-definite covariance | Cholesky decomposition | Reject distribution evaluation |
| Invalid prediction dimensions | Model validation | Reject prediction |
| Invalid anomaly threshold | Threshold validation | Reject monitoring configuration |

A singular covariance matrix may occur when variables are perfectly dependent or when the number of observations is insufficient relative to the number of variables.

Regularization or dimension reduction may be necessary in these situations.

The project does not silently replace invalid covariance matrices with arbitrary values.

## 11. Statistical and Engineering Limitations

The implementations demonstrate core computational techniques rather than a complete statistical inference platform.

Important limitations include:

- No automatic missing-data imputation.
- No categorical predictor encoding.
- No automatic feature scaling.
- No heteroscedasticity-consistent standard errors.
- No regression coefficient confidence intervals.
- No hypothesis-testing framework.
- No automatic model selection.
- No complete residual diagnostic suite.
- No cross-validation framework.
- No automatic covariance shrinkage.
- No mixture-distribution estimation.
- No generalized linear models.

The PostgreSQL implementation supports two predictors, while the Python, JavaScript, C++17, and Java implementations support arbitrary predictor counts subject to numerical and sample-size constraints.

The JavaScript implementation uses online covariance accumulation, making it appropriate for incremental data processing.

The other implementations demonstrate batch statistical estimation.

A production statistical platform should also consider:

- Numerical precision.
- Reproducible data preparation.
- Model versioning.
- Dataset provenance.
- Access control.
- Data retention.
- Model validation.
- Monitoring of distribution shifts.
- Detection of changing covariance structures.

## 12. Security and Data Governance

Statistical systems frequently process commercially sensitive or personally identifiable measurements.

Production deployments should apply the following controls:

- Restrict access to observation tables.
- Separate model-fitting permissions from prediction permissions.
- Validate imported numeric data.
- Use parameterized SQL for application-supplied values.
- Protect exported statistical reports.
- Maintain dataset provenance.
- Record model-fitting timestamps.
- Prevent unauthorized modification of fitted models.
- Apply appropriate retention and deletion policies.
- Avoid exposing sensitive observations through diagnostic logs.

Statistical validity and data security are separate requirements. A mathematically correct model does not establish that its underlying data were collected, processed, or accessed appropriately.

## 13. Practical Applications

| Application | Multivariate technique | Practical use |
|---|---|---|
| Business analytics | Multiple regression | Sales prediction |
| Financial risk | Covariance matrices | Portfolio risk measurement |
| Manufacturing | Multivariate distributions | Process monitoring |
| Cybersecurity | Mahalanobis distance | Multivariate anomaly detection |
| Healthcare research | Multivariate regression | Analysis of multiple explanatory variables |
| Marketing analytics | Correlation structures | Understanding predictor relationships |
| Quality engineering | Multivariate normal models | Joint process variation |
| Operations research | Covariance estimation | Understanding correlated operational measures |

The choice of statistical method depends on the research question, data structure, model assumptions, and operational decision being supported.

## 14. Execution Requirements

| Deliverable | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10+ | None |
| JavaScript | Node.js 18+ | None |
| C++17 | C++17-compatible compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14+ | None |

The Python, JavaScript, C++, and Java implementations are standalone programs.

The JavaScript implementation creates `multivariate_report.json` in its execution directory.

The PostgreSQL script creates the `multivariate_stats` schema, inserts demonstration records, executes analytical functions, and displays reporting queries.

The SQL script uses a transaction for its database workflow.

For repeated execution, existing demonstration records are protected against duplication through dataset and distribution-profile uniqueness constraints, while new regression models and evaluation records are created as separate historical records.
