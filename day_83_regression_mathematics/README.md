# Regression Mathematics: Simple Linear Regression, Least Squares and Residuals

## 1. Mathematical Foundation

Regression analysis studies the relationship between a dependent variable and one or more independent variables.

Simple linear regression uses one independent variable, X, to explain or predict one dependent variable, Y.

The mathematical model is:

\[
Y_i = \beta_0 + \beta_1 X_i + \epsilon_i
\]

Where:

- \(Y_i\): observed dependent variable.
- \(X_i\): independent variable.
- \(\beta_0\): population intercept.
- \(\beta_1\): population slope.
- \(\epsilon_i\): random error term.

The estimated regression equation is:

\[
\hat{Y}_i = b_0 + b_1X_i
\]

Where:

- \(\hat{Y}_i\): estimated dependent variable.
- \(b_0\): estimated intercept.
- \(b_1\): estimated slope.

The regression line represents the estimated linear relationship between X and Y.

### Example

Consider the relationship between study hours and examination scores.

| Study hours (X) | Examination score (Y) |
|---:|---:|
| 1 | 2.1 |
| 2 | 3.9 |
| 3 | 6.2 |
| 4 | 7.8 |
| 5 | 10.1 |
| 6 | 11.9 |
| 7 | 14.2 |
| 8 | 15.8 |

The independent variable is study hours. The dependent variable is examination score.

The objective is to estimate how examination scores change with study hours.

## 2. Descriptive Statistics

Regression calculations begin with descriptive statistics.

### Arithmetic mean

The mean represents the central value of a dataset.

\[
\bar X = \frac{\sum X_i}{n}
\]

\[
\bar Y = \frac{\sum Y_i}{n}
\]

Where \(n\) represents the number of observations.

### Variance

Sample variance measures the dispersion of observations around their mean.

\[
S_X^2 =
\frac{\sum(X_i-\bar X)^2}{n-1}
\]

\[
S_Y^2 =
\frac{\sum(Y_i-\bar Y)^2}{n-1}
\]

### Covariance

Covariance measures the direction of the joint variation between two variables.

\[
Cov(X,Y) =
\frac{\sum(X_i-\bar X)(Y_i-\bar Y)}{n-1}
\]

Interpretation:

- Positive covariance: X and Y tend to increase together.
- Negative covariance: X tends to increase when Y decreases.
- Zero covariance: no linear covariance is observed.

Covariance magnitude depends on the measurement scales. Correlation provides a standardized measure of linear association.

## 3. Least Squares Estimation

The Least Squares Method estimates the regression coefficients by minimizing the sum of squared residuals.

For each observation:

\[
e_i = Y_i-\hat Y_i
\]

The objective function is:

\[
SSE = \sum_{i=1}^{n}(Y_i-\hat Y_i)^2
\]

Substituting the regression equation:

\[
SSE =
\sum_{i=1}^{n}
(Y_i-b_0-b_1X_i)^2
\]

The optimal coefficients minimize this expression.

### Slope calculation

The Ordinary Least Squares slope is:

\[
b_1 =
\frac{\sum(X_i-\bar X)(Y_i-\bar Y)}
{\sum(X_i-\bar X)^2}
\]

The numerator represents the centered cross-product between X and Y.

The denominator represents the centered sum of squares of X.

The slope measures the estimated change in Y associated with a one-unit increase in X.

### Intercept calculation

\[
b_0 = \bar Y-b_1\bar X
\]

The intercept is the predicted value of Y when X equals zero.

Its practical interpretation depends on whether zero is meaningful and falls within the relevant data range.

### Regression equation

After calculating the coefficients:

\[
\hat Y=b_0+b_1X
\]

The equation can be used to calculate fitted values and make predictions.

## 4. Residuals

A residual is the difference between an observed dependent-variable value and its corresponding fitted value.

\[
e_i=Y_i-\hat Y_i
\]

Residuals are important because they measure the errors remaining after fitting the regression line.

### Residual interpretation

| Residual | Interpretation |
|---|---|
| Positive | Observed value exceeds fitted value |
| Negative | Observed value is below fitted value |
| Zero | Observed value equals fitted value |
| Large absolute value | Observation has a relatively large prediction error |

### Residual properties

For Ordinary Least Squares regression containing an intercept:

\[
\sum e_i \approx 0
\]

The approximation accounts for floating-point computation.

The fitted regression line also passes through:

\[
(\bar X,\bar Y)
\]

These properties provide useful mathematical validation checks.

### Residual analysis

Residual analysis helps investigate whether a linear regression model is appropriate.

Important patterns include:

- Random scatter around zero: consistent with an appropriate conditional-mean specification.
- Curved pattern: possible nonlinear relationship.
- Increasing spread: possible heteroscedasticity.
- Large isolated residuals: potential outliers.
- Sequential patterns: possible dependence between observations.

Residual patterns should be investigated rather than automatically treated as proof of a particular problem.

## 5. Sum of Squares Decomposition

Three important quantities describe regression variation.

### Total Sum of Squares

SST measures the total variation of observed Y values around their mean.

\[
SST=\sum(Y_i-\bar Y)^2
\]

### Regression Sum of Squares

SSR measures variation explained by the fitted regression line.

\[
SSR=\sum(\hat Y_i-\bar Y)^2
\]

### Error Sum of Squares

SSE measures variation remaining in the residuals.

\[
SSE=\sum(Y_i-\hat Y_i)^2
\]

For Ordinary Least Squares with an intercept:

\[
\boxed{SST=SSR+SSE}
\]

This decomposition is a fundamental regression identity.

It provides a useful consistency check for implementations.

The identity does not necessarily hold for regression without an intercept or for other fitting methods.

## 6. Regression Evaluation Metrics

### Coefficient of Determination

R-squared measures the proportion of observed variation in Y explained by the fitted regression model.

\[
R^2=1-\frac{SSE}{SST}
\]

For ordinary least squares with an intercept and nonconstant Y:

\[
0\leq R^2\leq1
\]

Interpretation:

- Values near 1 indicate that the fitted model explains a large proportion of observed variation.
- Values near 0 indicate that the fitted model explains relatively little variation.

R-squared does not establish causation, prove that the model assumptions hold, or guarantee accurate predictions on new observations.

### Mean Squared Error

\[
MSE=\frac{SSE}{n}
\]

MSE measures average squared prediction error.

### Root Mean Squared Error

\[
RMSE=\sqrt{\frac{SSE}{n}}
\]

RMSE expresses prediction error in the same units as Y.

Larger errors receive greater weight because residuals are squared.

### Mean Absolute Error

\[
MAE=\frac{1}{n}\sum|Y_i-\hat Y_i|
\]

MAE represents average absolute prediction error.

Unlike RMSE, MAE does not square residuals.

RMSE and MAE are useful complementary measures because they respond differently to large errors.

## 7. Model Assumptions and Limitations

Simple linear regression relies on assumptions that should be considered before interpreting the results.

| Assumption | Meaning |
|---|---|
| Linearity | Conditional mean of Y is linear in X |
| Independent errors | Error terms are independent under the assumed sampling structure |
| Zero conditional mean | Expected error given X is zero |
| Homoscedasticity | Conditional error variance is constant |
| Normality | Errors are normally distributed when exact classical small-sample inference is required |

Normality is not required to calculate OLS coefficients.

It is relevant to certain classical hypothesis tests and confidence intervals.

Other important limitations include:

- Outliers can substantially influence the estimated slope.
- Extrapolation beyond the observed X range may be unreliable.
- Omitted variables can produce misleading relationships.
- Measurement errors can affect coefficient estimates.
- A high R-squared does not establish a causal relationship.
- A linear model may be unsuitable when the true relationship is nonlinear.

The implementations calculate descriptive regression metrics. They do not automatically establish the assumptions or provide inferential guarantees.

## 8. Python Implementation

The Python implementation uses object-oriented design and standard-library numerical functionality.

### Main components

| Component | Responsibility |
|---|---|
| Observation | Validates an individual X-Y pair |
| DescriptiveStatistics | Stores means, variances and covariance |
| RegressionMetrics | Stores model evaluation results |
| LinearRegressionModel | Stores fitted parameters and prediction methods |
| SimpleLinearRegression | Performs OLS estimation |
| load_csv | Loads observations from a CSV dataset |
| display_model | Displays coefficients, metrics and residuals |
| run_tests | Checks mathematical properties and validation failures |

### Implementation mechanics

The regression engine calculates centered X and Y values before estimating the slope.

It uses `math.fsum()` for more accurate accumulation of floating-point values.

This is useful when datasets contain many observations or when sums involve values with different magnitudes.

The model stores:

- Estimated slope.
- Estimated intercept.
- Fitted values.
- Residuals.
- SSE, SSR and SST.
- R-squared.
- RMSE and MAE.

Prediction is separated from model fitting, allowing the fitted model to be reused.

The CSV loader validates column names, numeric conversion and dataset availability.

## 9. JavaScript Implementation

The JavaScript implementation emphasizes asynchronous processing and event-driven dataset management.

### Main components

| Component | Responsibility |
|---|---|
| Observation | Immutable validated observation |
| RegressionDataset | Stores observations and manages dataset versions |
| OrdinaryLeastSquares | Fits the regression model |
| RegressionModel | Provides predictions and residual reports |
| processStream | Processes asynchronous observation streams |
| observationStream | Demonstrates asynchronous data delivery |

### Event-driven behavior

The dataset extends Node.js `EventEmitter`.

It emits events when observations are added, batches are inserted or the dataset is cleared.

The regression service captures a dataset snapshot before fitting.

This avoids mixing different dataset states during a model calculation.

The batch insertion operation validates all records before modifying the dataset.

This provides atomic validation behavior at the application level.

### Asynchronous execution

The `fitAsync()` method schedules model fitting through the Node.js event loop.

The implementation demonstrates asynchronous processing and error propagation through Promises.

It does not make the numerical calculation parallel. CPU-intensive regression workloads may require worker threads or a separate processing service.

## 10. C++17 Implementation

The C++17 implementation focuses on numerical computation and resource-efficient data structures.

### Main components

| Component | Responsibility |
|---|---|
| Observation | Stores X and Y |
| ResidualRecord | Stores actual, fitted and residual values |
| RegressionMetrics | Stores evaluation statistics |
| RegressionEngine | Performs OLS and prediction |
| runTests | Validates mathematical properties |

### Numerical design

The implementation uses:

- `std::vector` for observation storage.
- `std::isfinite` for numeric validation.
- `std::clamp` for bounded R-squared output.
- `std::move` for ownership transfer.
- Kahan summation for selected accumulated quantities.

Centered calculations reduce numerical difficulties associated with raw sums.

The regression engine uses a model lifecycle state to prevent prediction before fitting.

### Complexity

For \(n\) observations:

| Operation | Time complexity |
|---|---|
| Dataset validation | O(n) |
| Mean calculation | O(n) |
| Slope estimation | O(n) |
| Intercept calculation | O(1) |
| Fitted-value calculation | O(n) |
| Residual calculation | O(n) |
| Prediction | O(1) |
| Batch prediction | O(k) |

The principal storage requirement is O(n), including observations, fitted values and residuals.

## 11. Java 17 Implementation

The Java implementation models regression as an enterprise-oriented service.

It separates data management, validation, model estimation and model reporting.

### Main components

| Component | Responsibility |
|---|---|
| Observation record | Immutable observation |
| RegressionDataset | Dataset storage and version tracking |
| ValidationService | Applies dataset validation policies |
| RegressionModel | Immutable fitted model |
| RegressionService | Coordinates fitting and model lifecycle |
| Metrics record | Stores regression evaluation statistics |
| ModelSnapshot | Captures model version and parameters |

### Domain separation

The dataset is responsible for storing observations.

The validation service enforces eligibility requirements.

The regression service performs OLS estimation and manages fitted model state.

The regression model contains the resulting coefficients and prediction behavior.

This separation reduces coupling between data collection and numerical computation.

### Model lifecycle

The service uses three states:

- `UNFITTED`: No successful model has been established.
- `FITTED`: A valid model has been produced.
- `FAILED`: The latest fitting attempt failed.

The model snapshot records the dataset version used for fitting.

This supports basic model traceability.

A production implementation would also persist dataset hashes, model configuration, execution timestamps, validation results and access-control information.

## 12. PostgreSQL Implementation

The PostgreSQL implementation models regression as a relational data-processing workflow.

### Database relationship

Dataset  
→ Observations  
→ Regression Model  
→ Model Residuals  
→ Performance Reporting

### Relational entities

| Table | Purpose |
|---|---|
| datasets | Dataset metadata and lifecycle |
| observations | Independent and dependent variable pairs |
| regression_models | Fitted regression coefficients and metrics |
| model_residuals | Fitted values and residual records |

### Dataset integrity

The schema uses:

- Primary keys to identify records.
- Foreign keys to enforce relationships.
- Unique constraints to prevent duplicate observation numbers within a dataset.
- Check constraints to reject invalid numerical and model values.
- Indexes to support dataset and model retrieval.

### Regression function

The `fit_linear_regression()` function performs OLS calculations inside PostgreSQL.

Its workflow is:

1. Verify that the dataset exists and is active.
2. Calculate observation count and means.
3. Calculate centered sums of squares and cross-products.
4. Estimate slope and intercept.
5. Calculate fitted values and residuals.
6. Calculate SSE, SSR, SST and evaluation metrics.
7. Validate the sum-of-squares identity.
8. Register a new model version.
9. Persist observation-level residual records.

The function raises exceptions when the dataset is ineligible or calculations fail.

PostgreSQL transactions ensure that a failed fitting operation does not leave partially committed model results.

### Reporting views

`regression_performance` provides model-level metrics.

`residual_analysis` provides observation-level fitted values and residuals.

`residual_summary` aggregates residual statistics for model-level inspection.

### Prediction function

`predict_linear()` retrieves model coefficients and calculates a predicted dependent-variable value for a supplied X.

It validates both the input and the existence of the requested model.

## 13. Mathematical Relationships Across Implementations

The five source files implement the same central mathematical model using different engineering approaches.

| Mathematical concept | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Observations | Dataclass | Class | Struct | Record | Table |
| Dataset validation | Exceptions | Validation methods | Exceptions | Validation service | Constraints and functions |
| Slope | Centered sums | Centered sums | Centered sums | Centered sums | Aggregate calculations |
| Intercept | Mean-based calculation | Mean-based calculation | Mean-based calculation | Mean-based calculation | Mean-based calculation |
| Fitted values | Tuple | Frozen array | Vector | Immutable list | Relational records |
| Residuals | Tuple | Frozen array | Vector | Immutable list | Residual table |
| R-squared | Metrics object | Metrics object | Metrics structure | Metrics record | Model table |
| Prediction | Model method | Model method | Engine method | Model method | SQL function |

All implementations follow the same mathematical definition, while their software architecture differs according to each language's capabilities.

## 14. Practical Interpretation

Consider the study-hours dataset.

The fitted slope estimates the average change in examination score associated with one additional study hour.

The intercept estimates the fitted examination score at zero study hours.

The residual for an observation indicates how far the actual examination score differs from the fitted score.

R-squared measures the proportion of observed examination-score variation explained by the fitted linear relationship.

RMSE and MAE quantify prediction error in examination-score units.

These quantities answer different questions:

- Slope: How much does the fitted outcome change when X increases by one unit?
- Intercept: What outcome does the fitted equation estimate at X = 0?
- Residual: How far is an observed value from its fitted value?
- SSE: How much squared error remains?
- SSR: How much variation is explained by the fitted line?
- SST: How much total variation exists?
- R-squared: What proportion of total variation is explained?
- RMSE: What is the root average squared prediction error?
- MAE: What is the average absolute prediction error?

The distinction between association, prediction and causation is essential when interpreting regression results.

A fitted linear relationship describes the observed statistical relationship under the model. It does not independently establish that changes in X cause changes in Y.

## 15. Testing and Numerical Reliability

The implementations include tests for:

- Correct slope estimation.
- Correct intercept estimation.
- Perfect linear relationships.
- R-squared equal to one for a perfect fit.
- Prediction at a new independent-variable value.
- Residual summation.
- Constant independent-variable rejection.
- Invalid numeric inputs.
- Sum-of-squares decomposition.

Numerical reliability requires particular attention when values are extremely large, extremely small or differ substantially in magnitude.

Centered calculations reduce some numerical problems but do not eliminate all floating-point limitations.

For large-scale production datasets, additional considerations include:

- Input range validation.
- Missing-value policies.
- Outlier investigation.
- Model versioning.
- Dataset provenance.
- Reproducibility.
- Independent validation data.
- Prediction monitoring.
- Access control.
- Audit logging.

The implementations establish the mathematical and computational foundation for simple linear regression while keeping estimation, residual analysis, prediction and model evaluation as distinct operations.
