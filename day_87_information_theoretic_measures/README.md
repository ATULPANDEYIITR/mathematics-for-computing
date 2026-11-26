# Information-Theoretic Measures

## Mutual Information, Conditional Entropy, and Information Gain

**Technical domain:** Information Theory, Probability, Statistics, Machine Learning, Feature Selection

**Implementations:** Python, JavaScript, C++17, Java 17, PostgreSQL

**Primary objective:** Quantify uncertainty in categorical variables, measure statistical dependence, evaluate the predictive relevance of features, and identify useful variables for classification.

---

## 1. Mathematical Foundations

Information theory provides mathematical tools for measuring uncertainty and information shared between random variables.

The implementations use Shannon information theory and express information quantities in bits by default.

The three central concepts are:

1. Entropy measures uncertainty in a random variable.
2. Conditional entropy measures remaining uncertainty when another variable is known.
3. Mutual information measures how much information one variable provides about another.

Information gain expresses the reduction in target uncertainty resulting from observing a feature.

These quantities are related but have different interpretations and applications.

### 1.1 Probability distributions

A discrete random variable \(X\) takes values from a finite or countable set:

\[
X=\{x_1,x_2,\ldots,x_n\}
\]

Its probability distribution satisfies:

\[
P(X=x_i)\geq 0
\]

\[
\sum_i P(X=x_i)=1
\]

For observed categorical data, probabilities can be estimated using relative frequencies:

\[
P(x_i)=\frac{\text{Count}(x_i)}{N}
\]

where \(N\) represents the total number of observations.

For example, consider:

| Outcome | Frequency | Probability |
|---|---:|---:|
| Heads | 50 | 0.50 |
| Tails | 50 | 0.50 |

This represents a uniform binary distribution.

---

## 2. Shannon Entropy

### 2.1 Definition

Shannon entropy measures the average uncertainty associated with a discrete random variable.

\[
H(X)=-\sum_{x\in X}P(x)\log_2P(x)
\]

The logarithm base determines the measurement unit.

| Logarithm base | Measurement unit |
|---|---|
| Base 2 | Bits |
| Base e | Nats |
| Base 10 | Hartleys |

A probability of zero contributes zero to entropy because:

\[
\lim_{p\rightarrow 0^+}p\log(p)=0
\]

### 2.2 Numerical examples

**Example A: Certain outcome**

Suppose a variable always takes the value A.

\[
P(A)=1
\]

\[
H(X)=-1\log_2(1)=0
\]

There is no uncertainty.

**Example B: Fair binary outcome**

\[
P(A)=P(B)=0.5
\]

\[
H(X)=-(0.5\log_2 0.5+
0.5\log_2 0.5)
\]

\[
H(X)=1\text{ bit}
\]

**Example C: Unequal binary distribution**

\[
P(A)=0.9,\quad P(B)=0.1
\]

\[
H(X)=
-0.9\log_2(0.9)
-0.1\log_2(0.1)
\]

\[
H(X)\approx 0.469
\]

The uncertainty is lower because one outcome is considerably more likely.

### 2.3 Important properties

- Entropy is non-negative.
- A constant random variable has zero entropy.
- Entropy reaches its maximum for a uniform distribution over a fixed number of outcomes.
- For a variable with \(k\) possible outcomes:

\[
0\leq H(X)\leq \log_2(k)
\]

- Entropy describes uncertainty, not the importance or usefulness of a variable.

### 2.4 Implementation

The five implementations calculate entropy using observed frequencies rather than requiring users to supply probabilities manually.

The implementations reject empty datasets, invalid observations, and invalid logarithm bases.

The Python implementation also exposes a probability-distribution data class and a frequency-based constructor.

The Java implementation uses immutable probability records and validates that supplied probabilities sum to one.

---

## 3. Joint Entropy

Joint entropy measures the uncertainty associated with two random variables considered together.

\[
H(X,Y)=
-\sum_x\sum_y
P(x,y)\log_2P(x,y)
\]

The joint distribution represents the probability of observing a particular combination of values.

### Example

Consider two binary variables:

| X | Y | Probability |
|---|---|---:|
| 0 | 0 | 0.5 |
| 1 | 1 | 0.5 |

The joint entropy is:

\[
H(X,Y)=1\text{ bit}
\]

Both variables contain the same information, so observing the pair does not increase uncertainty beyond one bit.

For independent variables:

\[
H(X,Y)=H(X)+H(Y)
\]

For dependent variables:

\[
H(X,Y)\leq H(X)+H(Y)
\]

Joint entropy is used in the implementations to verify relationships between marginal and conditional uncertainty.

---

## 4. Conditional Entropy

### 4.1 Definition

Conditional entropy measures the remaining uncertainty in a random variable after another variable has been observed.

\[
H(Y|X)=
-\sum_x\sum_y
P(x,y)\log_2P(y|x)
\]

An equivalent expression is:

\[
H(Y|X)=H(X,Y)-H(X)
\]

Another useful representation is:

\[
H(Y|X)=
\sum_x P(x)H(Y|X=x)
\]

This weighted formulation is particularly useful for categorical datasets.

### 4.2 Interpretation

Suppose a classification dataset contains a target variable representing whether a customer purchases a product.

A feature represents the customer's membership category.

The conditional entropy answers:

How much uncertainty remains about the purchase decision after knowing the membership category?

| Situation | Conditional entropy |
|---|---:|
| Membership completely determines purchase | 0 |
| Membership provides no information | Equal to target entropy when independent |
| Membership provides partial information | Between 0 and target entropy |

### 4.3 Fundamental inequality

\[
H(Y|X)\leq H(Y)
\]

Knowing an additional variable cannot increase the theoretical conditional uncertainty of the target.

This property assumes the same underlying joint probability distribution. Estimated finite-sample values can still be affected by sampling variability.

### 4.4 Implementation mechanism

The implementations group target observations according to feature values.

For every group:

1. Determine the number of observations.
2. Calculate the group's probability.
3. Calculate the entropy of the target within that group.
4. Multiply the entropy by the group probability.
5. Sum the weighted values.

This approach avoids constructing unnecessary probability matrices.

---

## 5. Mutual Information

### 5.1 Definition

Mutual information quantifies the information shared between two random variables.

\[
I(X;Y)=H(Y)-H(Y|X)
\]

It can also be expressed as:

\[
I(X;Y)=H(X)+H(Y)-H(X,Y)
\]

A probability-based formulation is:

\[
I(X;Y)=
\sum_x\sum_y
P(x,y)
\log_2
\frac{P(x,y)}{P(x)P(y)}
\]

Mutual information is equivalent to the Kullback-Leibler divergence between the joint distribution and the product of its marginal distributions:

\[
I(X;Y)=
D_{KL}(P(X,Y)\parallel P(X)P(Y))
\]

### 5.2 Interpretation

Mutual information measures how much knowing one variable reduces uncertainty about another.

| Relationship | Mutual information |
|---|---:|
| Independent variables | 0 |
| Identical fair binary variables | 1 bit |
| Perfectly dependent variables | Equal to the entropy of either variable |
| Partially dependent variables | Positive value below the relevant entropy bound |

The measure is symmetric:

\[
I(X;Y)=I(Y;X)
\]

This symmetry distinguishes mutual information from directional prediction accuracy.

Mutual information does not establish causation.

### 5.3 Important distinction

A feature can have high mutual information with a target without being causally responsible for the target.

For example, two variables may share information because both are influenced by an unobserved third variable.

Feature selection based on mutual information should therefore not be interpreted as causal discovery.

---

## 6. Conditional Mutual Information

Conditional mutual information measures the information shared between two variables after accounting for a third variable.

\[
I(X;Y|Z)=H(Y|Z)-H(Y|X,Z)
\]

Its probability-based definition is:

\[
I(X;Y|Z)=
\sum_{x,y,z}
P(x,y,z)
\log_2
\frac{P(x,y|z)}
{P(x|z)P(y|z)}
\]

### Interpretation

Consider:

- X: A customer interaction feature.
- Y: Purchase outcome.
- Z: Customer segment.

Conditional mutual information evaluates how much information X provides about Y when the customer segment is already known.

This is useful when investigating:

- Conditional dependence.
- Redundant features.
- Feature relationships within subpopulations.
- Potential confounding structures.
- Conditional feature relevance.

### Important properties

\[
I(X;Y|Z)\geq 0
\]

If X and Y are conditionally independent given Z:

\[
I(X;Y|Z)=0
\]

Conditional independence does not necessarily imply unconditional independence.

The implementations calculate conditional mutual information through differences in conditional entropy.

---

## 7. Information Gain

### 7.1 Definition

Information gain measures the reduction in target entropy resulting from observing a feature.

\[
IG(Y,X)=H(Y)-H(Y|X)
\]

Therefore:

\[
IG(Y,X)=I(X;Y)
\]

For the same observations and probability estimates, information gain and mutual information are mathematically equivalent.

Their distinction is primarily contextual:

| Measure | Typical interpretation |
|---|---|
| Mutual information | General statistical dependence between variables |
| Information gain | Reduction in uncertainty about a selected target after observing a feature |

### 7.2 Decision-tree application

Information gain is commonly used to select splitting attributes in decision-tree algorithms.

At a node, a decision-tree algorithm evaluates candidate features and selects a feature that provides a large reduction in target entropy.

For a candidate feature X:

\[
IG(Y,X)=H(Y)-H(Y|X)
\]

The selected feature partitions the observations into groups.

The process is repeated within child nodes until a stopping condition is reached.

### 7.3 Example: Weather classification

The source files implement a categorical weather dataset containing:

| Feature | Possible categories |
|---|---|
| Outlook | Sunny, Overcast, Rain |
| Temperature | Hot, Mild, Cool |
| Humidity | High, Normal |
| Wind | Weak, Strong |
| Target | Yes, No |

The target represents the classification outcome.

Each feature is evaluated independently against the target.

The analysis calculates:

- Target entropy.
- Conditional target entropy.
- Mutual information.
- Information gain.
- Normalized mutual information.

Features are ranked in descending order of information gain.

The highest-ranked feature is the strongest initial candidate under the selected information-gain criterion.

The ranking does not establish that the feature is universally optimal for every subsequent decision-tree node.

---

## 8. Normalized Mutual Information

Mutual information is measured in bits and depends on the uncertainty of the variables.

Normalized mutual information provides a scale-adjusted measure.

The implementations use:

\[
NMI(X,Y)=
\frac{2I(X;Y)}{H(X)+H(Y)}
\]

For non-degenerate variables:

\[
0\leq NMI(X,Y)\leq 1
\]

Interpretation:

| NMI | Interpretation |
|---:|---|
| 0 | No measured mutual information |
| Between 0 and 1 | Partial information sharing |
| 1 | Perfect information sharing |

For two constant variables, the implementations define NMI as 1 because the variables are identical in their observed values.

This convention should be considered when comparing datasets containing constant variables.

Normalized mutual information is useful for comparing dependence across variables with different entropy levels.

Different normalization conventions exist, so comparisons should use the same definition.

---

## 9. Relationship Between Information Measures

The principal mathematical relationships are:

\[
H(Y|X)=H(X,Y)-H(X)
\]

\[
I(X;Y)=H(Y)-H(Y|X)
\]

\[
I(X;Y)=H(X)+H(Y)-H(X,Y)
\]

\[
IG(Y,X)=I(X;Y)
\]

\[
I(X;Y|Z)=H(Y|Z)-H(Y|X,Z)
\]

These relationships allow independent verification of implementations.

For example, mutual information can be calculated through either marginal and conditional entropy or joint entropy.

If the calculations use the same empirical distribution, the results should agree within numerical precision.

### Conceptual relationship

    Observed categorical data
              |
              v
       Probability estimates
              |
              v
         Shannon entropy
              |
        +-----+------+
        |            |
        v            v
    Joint entropy  Conditional entropy
        |            |
        +-----+------+
              |
              v
        Mutual information
              |
              v
        Information gain
              |
              v
        Feature ranking
              |
              v
       Feature selection

Conditional mutual information extends this structure by conditioning on an additional variable.

---

## 10. Implementation Architecture

The five source files provide different engineering perspectives on the same mathematical domain.

| File | Primary responsibility | Distinct engineering approach |
|---|---|---|
| Python | Statistical analysis and feature ranking | Dataclasses, dictionaries, exceptions, JSON export, assertions |
| JavaScript | Event-driven analysis pipeline | Maps, asynchronous execution, EventEmitter, immutable results |
| C++17 | Computational analysis engine | STL containers, templates, generic mathematical operations |
| Java 17 | Enterprise analytical service | Records, immutable collections, domain exceptions, service classes |
| PostgreSQL | Persistent analytical workflow | Relational modeling, SQL functions, constraints, triggers, reporting |

### 10.1 Python

The Python implementation provides:

- `ProbabilityDistribution` for probability validation.
- `entropy()` for Shannon entropy.
- `joint_entropy()` for joint uncertainty.
- `conditional_entropy()` for remaining uncertainty.
- `mutual_information()` for shared information.
- `conditional_mutual_information()` for conditional dependence.
- `information_gain()` for feature evaluation.
- `normalized_mutual_information()` for scale-adjusted comparison.
- `InformationAnalyzer` for feature ranking and selection.

The analyzer separates mathematical calculations from dataset management.

`FeatureResult` stores the measurements for one feature.

The export mechanism writes structured JSON results.

The test suite verifies mathematical identities, invalid distributions, empty datasets, and mismatched observation counts.

### 10.2 JavaScript

The JavaScript implementation emphasizes event-driven execution.

Its main components are:

| Component | Responsibility |
|---|---|
| `distribution()` | Estimate categorical probabilities |
| `entropy()` | Calculate Shannon entropy |
| `conditionalEntropy()` | Calculate conditional uncertainty |
| `mutualInformation()` | Measure shared information |
| `conditionalMutualInformation()` | Evaluate conditional dependence |
| `InformationEngine` | Manage analytical operations |
| `AnalysisPipeline` | Coordinate asynchronous execution |
| `exportResults()` | Persist analytical results |

`AnalysisPipeline` extends Node.js `EventEmitter`.

It publishes three events:

- `started`
- `completed`
- `failed`

This design allows other application components to respond to analysis events without being tightly coupled to the statistical calculations.

The export operation uses exclusive file creation to prevent accidental overwriting.

### 10.3 C++17

The C++ implementation emphasizes generic computation and explicit domain modeling.

`InformationMetrics` provides template-based operations that can work with different comparable categorical types.

The `Dataset` class validates feature dimensions.

`FeatureEvaluation` represents the analytical output.

`GovernanceEngine` coordinates feature evaluation, ranking, and selection.

The implementation uses:

- `std::map` for frequency aggregation.
- `std::vector` for observation storage.
- `std::pair` for joint categorical outcomes.
- STL sorting for feature ranking.
- Exceptions for invalid input and execution failures.

The computational design minimizes unnecessary intermediate data structures.

### 10.4 Java 17

The Java implementation uses an enterprise-oriented architecture.

Its domain model contains:

- `Dataset`
- `ProbabilityEntry`
- `ProbabilityModel`
- `FeatureScore`
- `AnalysisReport`
- `AnalysisStatus`

Records provide compact data structures with constructor-level validation.

Immutable lists and maps prevent accidental modification of the dataset during analysis.

`InformationCalculator` provides the mathematical functions.

`FeatureAnalysisService` coordinates calculations and returns an `AnalysisReport`.

This separation supports extension into larger analytical applications where data ingestion, calculation, persistence, and reporting are separate responsibilities.

### 10.5 PostgreSQL

The database implementation models the complete analytical workflow.

Its schema contains:

| Table | Responsibility |
|---|---|
| `datasets` | Dataset metadata and lifecycle |
| `features` | Feature definitions |
| `observations` | Observation identifiers and target values |
| `feature_observations` | Feature values for individual observations |
| `analysis_results` | Persisted information-theoretic measurements |

The observation identifier connects feature values belonging to the same original sample.

This is essential because mutual information depends on the joint distribution, not merely on independent feature-frequency totals.

The database enforces referential integrity using primary keys and foreign keys.

Check constraints prevent invalid observation counts and invalid measurement values.

Indexes support dataset-level retrieval, feature-frequency aggregation, and analytical reporting.

---

## 11. PostgreSQL Analytical Workflow

The database implementation follows this sequence:

    Create dataset
          |
          v
    Define features
          |
          v
    Insert target observations
          |
          v
    Insert feature observations
          |
          v
    Validate dataset completeness
          |
          v
    Calculate entropy
          |
          v
    Calculate conditional entropy
          |
          v
    Calculate mutual information
          |
          v
    Calculate information gain
          |
          v
    Rank features
          |
          v
    Store analysis results
          |
          v
    Generate analytical reports

### 11.1 Dataset validation

The `validate_dataset()` function checks:

- The dataset contains observations.
- At least one feature is active.
- Every observation has a value for every active feature.
- The feature observations belong to the correct dataset.

Incomplete datasets are rejected before analytical processing.

This prevents incomplete feature records from silently changing probability estimates.

### 11.2 Database functions

| Function | Purpose |
|---|---|
| `calculate_entropy()` | Shannon entropy |
| `calculate_conditional_entropy()` | Conditional entropy |
| `calculate_joint_entropy()` | Joint entropy |
| `calculate_mutual_information()` | Mutual information |
| `calculate_conditional_mutual_information()` | Conditional mutual information |
| `calculate_information_gain()` | Information gain |
| `calculate_normalized_mi()` | Normalized mutual information |
| `validate_dataset()` | Dataset completeness validation |
| `evaluate_feature()` | Individual feature evaluation |

### 11.3 Stored analysis

The `store_feature_analysis()` procedure persists analytical measurements in `analysis_results`.

This separates calculated values from the original observations.

It also allows historical analysis records to be queried without recalculating every measurement for each report.

The procedure runs within the transaction established by its caller.

For large production datasets, analytical execution should use appropriately sized transactions and explicit operational controls.

---

## 12. Algorithmic Complexity

Let:

- \(N\) = number of observations.
- \(K\) = number of distinct categories.
- \(F\) = number of features.
- \(C\) = number of distinct joint category combinations.

### 12.1 Entropy

Frequency aggregation requires processing each observation.

With hash-based frequency aggregation:

\[
O(N)
\]

The entropy calculation processes the resulting category frequencies:

\[
O(K)
\]

The total expected time complexity is:

\[
O(N+K)=O(N)
\]

Auxiliary space:

\[
O(K)
\]

The Python and JavaScript implementations use hash-based frequency aggregation.

The C++ implementation uses ordered maps, resulting in approximately:

\[
O(N\log K)
\]

for frequency aggregation.

### 12.2 Conditional entropy

The observations are grouped by the conditioning variable.

Expected hash-based time complexity:

\[
O(N)
\]

Auxiliary storage can approach:

\[
O(N+K)
\]

because grouped implementations retain observations or category frequencies for individual groups.

### 12.3 Mutual information

Using:

\[
I(X;Y)=H(Y)-H(Y|X)
\]

The operation requires entropy and conditional entropy calculations.

Expected time complexity:

\[
O(N)
\]

for a single pair of categorical variables with hash-based aggregation.

### 12.4 Feature ranking

Evaluating F features independently:

\[
O(FN)
\]

Sorting the resulting feature scores:

\[
O(F\log F)
\]

Combined expected complexity:

\[
O(FN+F\log F)
\]

The feature ranking implementation does not require training a complete decision tree.

### 12.5 Database performance

The PostgreSQL implementation uses grouped aggregation and indexed observation retrieval.

Performance depends on:

- Dataset size.
- Number of features.
- Number of distinct categories.
- Distribution of categorical values.
- Available memory.
- Index selectivity.
- Query execution plans.

For high-volume analytical workloads, grouped aggregation, partitioning, batch ingestion, and pre-aggregated frequency tables may be necessary.

---

## 13. Edge Cases and Validation

Information-theoretic calculations require careful input validation.

The implementations address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty observations | Reject |
| Unequal column lengths | Reject |
| Negative probability | Reject |
| Probability greater than one | Reject |
| Probabilities not summing to one | Reject |
| Constant variable | Entropy equals zero |
| Perfectly dependent variables | Mutual information equals relevant entropy |
| Independent variables | Mutual information equals zero |
| Missing categorical observations | Reject in the supplied implementations |
| Invalid logarithm base | Reject |
| Unknown feature name | Reject |
| No active features | Reject |
| Incomplete database observation | Reject |

### 13.1 Floating-point precision

Floating-point arithmetic can produce small numerical deviations.

For example, a theoretically zero mutual information value might be represented by a very small positive or negative number.

The implementations use small tolerances and clamp insignificant negative values to zero.

Clamping should not replace validation of the underlying probability calculations.

### 13.2 Missing observations

The supplied implementations reject missing categorical values instead of automatically treating them as a category.

This is a deliberate design decision.

In practical analytical systems, missing-value treatment must be specified before calculating information measures.

Possible strategies include:

- Excluding incomplete observations.
- Assigning a separate missing category.
- Applying an explicit imputation policy.
- Reporting missingness as a separate feature.

Different policies can produce different information estimates.

### 13.3 High-cardinality variables

A feature with many unique values can produce misleadingly high empirical information gain.

An identifier that uniquely identifies every observation can perfectly predict the observed target within the sample.

This does not mean that the identifier provides useful predictive information for future observations.

High-cardinality features therefore require additional controls.

---

## 14. Statistical Limitations and Practical Considerations

### 14.1 Empirical estimation bias

The implementations calculate information measures from observed frequencies.

These are empirical estimates of population quantities.

When sample sizes are small, empirical mutual information can be positively biased, particularly when the number of categories is large.

Feature rankings may change as the sample size increases.

Possible approaches for more rigorous analysis include:

- Permutation testing.
- Bootstrap confidence intervals.
- Bias-corrected estimators.
- Bayesian probability estimation.
- Cross-validation.
- Independent test datasets.

These procedures are not implemented in the supplied programs.

### 14.2 Overfitting

A feature can obtain a high information gain because of accidental relationships in a training dataset.

A reliable feature-selection process should evaluate stability across different samples.

A practical workflow separates:

1. Training observations.
2. Validation observations.
3. Independent test observations.

Feature selection should be performed using training data only.

Using the test dataset to select features introduces information leakage.

### 14.3 Correlated features

Two features can contain overlapping information.

Selecting both does not necessarily improve a predictive model.

For example, two different measurements may encode nearly identical categorical distinctions.

Mutual information can be used to investigate individual feature-target relationships, while conditional mutual information can help examine additional information supplied by a feature after another variable is known.

### 14.4 Continuous variables

The supplied implementations primarily support discrete categorical observations.

Continuous variables require an estimation strategy.

Common approaches include:

- Discretization.
- Histogram-based estimation.
- Kernel density estimation.
- Nearest-neighbor mutual information estimation.
- Parametric distribution models.

Discretization can simplify computation, but bin boundaries influence the estimated information.

---

## 15. Security and Production Considerations

Information-theoretic analysis may involve commercially sensitive or personal datasets.

A production implementation should enforce:

- Access control for dataset ingestion.
- Authorization for analytical execution.
- Secure database credentials.
- Encryption in transit and at rest.
- Input validation.
- Controlled file permissions.
- Audit logging.
- Retention policies.
- Restricted access to exported analytical results.

The Python and JavaScript implementations export analysis results to local files.

The JavaScript implementation uses exclusive file creation and restrictive file permissions where supported by the operating system.

The SQL implementation uses relational constraints and parameterized database functions.

The SQL functions operate on supplied arrays and do not dynamically execute SQL constructed from categorical values.

Production deployments should also consider whether information measures themselves expose sensitive characteristics of a dataset.

An information score does not provide a privacy guarantee.

---

## 16. Verification and Expected Behavior

The implementations include mathematical tests based on known probability relationships.

| Test | Input characteristics | Expected result |
|---|---|---:|
| Fair binary variable | Equal probabilities | Entropy = 1 bit |
| Constant variable | One observed category | Entropy = 0 |
| Identical fair binary variables | Perfect dependence | MI = 1 bit |
| Independent binary variables | Uniform independent combinations | MI = 0 |
| Identical deterministic variables | Perfect prediction | Conditional entropy = 0 |
| Identical fair binary variables | Identical joint outcomes | Joint entropy = 1 bit |
| Invalid distribution | Probabilities sum to more than one | Validation failure |
| Mismatched observations | Unequal column lengths | Validation failure |

### Execution requirements

| Implementation | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10+ | None |
| JavaScript | Node.js 18+ | None |
| C++17 | C++17-compatible compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14+ | None |

The Java source uses Java 17 record features and the Java 17 collection API.

The C++ source uses standard C++17 language features and the standard template library.

The SQL source uses PostgreSQL-specific functions, procedures, enums, triggers, arrays, and window functions.

---

## 17. Practical Applications

Information-theoretic measures are applicable across several analytical domains.

| Domain | Application |
|---|---|
| Machine learning | Decision-tree feature selection |
| Data science | Feature relevance analysis |
| Cybersecurity | Analysis of categorical event dependencies |
| Fraud detection | Evaluation of transaction characteristics |
| Medical analytics | Investigation of relationships between clinical categories and outcomes |
| Information retrieval | Evaluation of information shared between terms and document categories |
| Data engineering | Assessment of categorical-variable redundancy |
| Research statistics | Quantification of statistical dependence |

For example, a fraud-detection dataset may contain:

- Transaction category.
- Merchant category.
- Transaction location.
- Device category.
- Fraud classification.

Information gain can rank these variables according to their empirical information about the fraud label.

The ranking is an analytical screening result, not proof of causation or a complete measure of predictive performance.

---

## 18. Core Terminology

| Term | Definition |
|---|---|
| Random variable | A variable whose possible outcomes have associated probabilities |
| Probability distribution | Assignment of probabilities to possible outcomes |
| Shannon entropy | Average uncertainty in a random variable |
| Joint entropy | Uncertainty associated with multiple variables together |
| Conditional entropy | Remaining uncertainty after observing another variable |
| Mutual information | Information shared between two variables |
| Conditional mutual information | Information shared between two variables given a third |
| Information gain | Reduction in target entropy after observing a feature |
| Normalized mutual information | Scale-adjusted measure of shared information |
| Cardinality | Number of distinct values in a variable |
| Empirical distribution | Probability distribution estimated from observed data |
| Feature selection | Process of selecting useful predictor variables |
| Information leakage | Unintended use of information that should not be available during model training |
| High-cardinality feature | Feature containing many distinct categories |

---

## 19. Technical Distinctions

The measures should not be treated as interchangeable concepts.

| Concept | What it measures | Typical use |
|---|---|---|
| Entropy | Uncertainty in one variable | Distribution analysis |
| Joint entropy | Uncertainty in multiple variables | Joint distribution analysis |
| Conditional entropy | Uncertainty remaining after observing another variable | Predictability analysis |
| Mutual information | Shared information between variables | Dependence analysis |
| Conditional mutual information | Additional dependence after conditioning | Conditional relationship analysis |
| Information gain | Reduction in target uncertainty | Feature selection |
| Normalized mutual information | Relative information sharing | Comparative analysis |

The mathematical equivalence between mutual information and information gain does not eliminate their different analytical contexts.

Mutual information is a general measure of statistical dependence.

Information gain is commonly presented as a target-oriented criterion for selecting features or evaluating decision-tree splits.

---

## 20. Final Implementation Scope

The five implementations provide complementary representations of the same information-theoretic framework.

The Python program emphasizes experimentation, validation, and structured analytical output.

The JavaScript program demonstrates asynchronous event-driven analysis.

The C++17 program demonstrates generic mathematical operations and efficient categorical aggregation.

The Java 17 program demonstrates immutable domain models and service-oriented analytical processing.

The PostgreSQL implementation demonstrates persistent dataset management, integrity enforcement, mathematical functions, analytical procedures, and reporting.

Together, the implementations establish the mathematical and computational relationships between entropy, conditional entropy, mutual information, conditional mutual information, normalized mutual information, and information gain.
