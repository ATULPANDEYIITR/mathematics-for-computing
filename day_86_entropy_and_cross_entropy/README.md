# Entropy and Cross-Entropy in Mathematics for Computing

## 1. Mathematical Foundations

Information theory provides mathematical methods for measuring uncertainty, information content, and differences between probability distributions.

Entropy and cross-entropy are fundamental to information processing, statistical inference, machine learning, data compression, and probabilistic modeling.

This implementation examines three central measures:

- Shannon entropy
- Cross-entropy
- Kullback-Leibler divergence

It also implements binary entropy, joint entropy, conditional entropy, and mutual information to establish their relationships.

All calculations use logarithms with base 2. Therefore, information measurements are expressed in bits.

## 2. Probability Distributions

A discrete probability distribution assigns a probability to every possible event in a finite sample space.

For a random variable \(X\), its probability distribution is:

\[
P(X=x_i)=p_i
\]

A valid distribution satisfies:

\[
0\leq p_i\leq 1
\]

and:

\[
\sum_{i=1}^{n}p_i=1
\]

Consider a classification problem with three possible outcomes:

| Class | Actual probability |
|---|---:|
| A | 0.50 |
| B | 0.30 |
| C | 0.20 |

The distribution represents the observed probability of each outcome.

A predictive model might produce:

| Class | Predicted probability |
|---|---:|
| A | 0.40 |
| B | 0.40 |
| C | 0.20 |

These distributions describe different things:

- The actual distribution represents the reference probability model.
- The predicted distribution represents the model's probability estimates.

The comparison between them is the basis of cross-entropy and KL divergence.

## 3. Shannon Entropy

Shannon entropy measures the expected uncertainty of a discrete random variable.

Its mathematical definition is:

\[
H(X)=-\sum_{i=1}^{n}p_i\log_2(p_i)
\]

For an individual event with probability \(p(x)\), its self-information is:

\[
I(x)=-\log_2 p(x)
\]

An unlikely event carries more information when it occurs than a highly probable event.

Entropy calculates the expected self-information across the entire distribution.

### Interpretation

- Low entropy indicates a concentrated probability distribution.
- High entropy indicates a more dispersed probability distribution.
- Zero entropy indicates a certain outcome.
- Maximum entropy occurs for a uniform distribution over a fixed number of outcomes.

For a distribution containing \(n\) possible outcomes:

\[
H(X)\leq \log_2 n
\]

Equality holds when every outcome has probability \(1/n\).

### Example

For a fair binary variable:

\[
P(X=0)=0.5
\]

\[
P(X=1)=0.5
\]

Therefore:

\[
H(X)=
-0.5\log_2(0.5)
-0.5\log_2(0.5)
\]

\[
H(X)=1\text{ bit}
\]

For a deterministic variable:

\[
P(X=0)=1
\]

\[
P(X=1)=0
\]

Its entropy is:

\[
H(X)=0
\]

A zero-probability event contributes zero to the entropy sum. This follows from the limiting convention:

\[
\lim_{p\rightarrow 0^+}p\log_2 p=0
\]

### Binary Entropy Function

The entropy of a Bernoulli random variable is:

\[
H_b(p)=
-p\log_2p
-(1-p)\log_2(1-p)
\]

Its maximum is one bit at \(p=0.5\).

The Python, JavaScript, C++, and Java implementations calculate this function directly.

## 4. Cross-Entropy

Cross-entropy measures the expected information required when the probability distribution used for encoding or prediction is \(Q\), while the actual distribution is \(P\).

Its definition is:

\[
H(P,Q)=
-\sum_x P(x)\log_2 Q(x)
\]

Here:

- \(P(x)\) represents the reference probability.
- \(Q(x)\) represents the estimated or predicted probability.

Cross-entropy evaluates how well a predicted distribution represents the actual distribution.

### Example

Consider:

\[
P=(0.5,0.3,0.2)
\]

\[
Q=(0.4,0.4,0.2)
\]

The cross-entropy is:

\[
H(P,Q)=
-[
0.5\log_2(0.4)
+
0.3\log_2(0.4)
+
0.2\log_2(0.2)
]
\]

The result is approximately:

\[
H(P,Q)=1.521928\text{ bits}
\]

Cross-entropy is frequently used as a loss function in probabilistic classification.

A lower cross-entropy generally indicates better probabilistic predictions for a fixed reference distribution.

### Zero-Probability Condition

An important edge case occurs when:

\[
P(x)>0
\]

but:

\[
Q(x)=0
\]

The corresponding cross-entropy term becomes infinite.

This represents a prediction that assigns no probability to an event that can actually occur.

The implementations explicitly detect this condition rather than attempting to calculate the logarithm of zero.

## 5. Kullback-Leibler Divergence

KL divergence measures the information difference between two probability distributions.

It is defined as:

\[
D_{KL}(P\parallel Q)=
\sum_x P(x)
\log_2\frac{P(x)}{Q(x)}
\]

It can also be expressed as:

\[
D_{KL}(P\parallel Q)=
H(P,Q)-H(P)
\]

Consequently:

\[
\boxed{H(P,Q)=H(P)+D_{KL}(P\parallel Q)}
\]

This identity is implemented and tested in all four programming languages.

### Mathematical Properties

KL divergence has several important properties.

| Property | Mathematical interpretation |
|---|---|
| Non-negativity | \(D_{KL}(P\parallel Q)\geq 0\) |
| Identity | \(D_{KL}(P\parallel P)=0\) |
| Asymmetry | \(D_{KL}(P\parallel Q)\neq D_{KL}(Q\parallel P)\) in general |
| Support condition | Positive probability under P requires positive probability under Q for finite divergence |
| Dependence on ordering | The reference distribution must be specified |

KL divergence is not a mathematical distance metric because it does not generally satisfy symmetry or the triangle inequality.

### Interpretation

KL divergence quantifies the additional expected information associated with using \(Q\) instead of \(P\).

It is useful for:

- Comparing statistical distributions.
- Evaluating probabilistic models.
- Variational inference.
- Distribution matching.
- Measuring changes between probability models.
- Studying differences between learned and reference distributions.

## 6. Relationship Between the Three Measures

The three central concepts have distinct purposes.

| Measure | Main question | Mathematical expression |
|---|---|---|
| Shannon entropy | How uncertain is P? | \(H(P)\) |
| Cross-entropy | How well does Q represent P? | \(H(P,Q)\) |
| KL divergence | How different is Q from P? | \(D_{KL}(P\parallel Q)\) |

Their relationship is:

\[
H(P,Q)=H(P)+D_{KL}(P\parallel Q)
\]

This equation separates two components:

1. The intrinsic uncertainty of the actual distribution.
2. The additional information cost resulting from the predicted distribution.

For a fixed actual distribution, minimizing cross-entropy is equivalent to minimizing KL divergence.

## 7. Joint Entropy

Joint entropy measures the uncertainty associated with two random variables considered together.

For discrete variables \(X\) and \(Y\):

\[
H(X,Y)=
-\sum_x\sum_y
P(x,y)\log_2P(x,y)
\]

Consider:

| X | Y | Joint probability |
|---|---|---:|
| X0 | Y0 | 0.40 |
| X0 | Y1 | 0.10 |
| X1 | Y0 | 0.10 |
| X1 | Y1 | 0.40 |

The probabilities form a joint distribution because their sum is one.

The marginal distributions are obtained by summing rows and columns.

For example:

\[
P(X=x)=\sum_yP(x,y)
\]

\[
P(Y=y)=\sum_xP(x,y)
\]

The joint distribution allows the implementation to investigate statistical dependence between variables.

## 8. Conditional Entropy

Conditional entropy measures the remaining uncertainty in one random variable after another variable is known.

The mathematical expression is:

\[
H(Y\mid X)=
H(X,Y)-H(X)
\]

Interpretation:

- Zero conditional entropy indicates that knowing X completely determines Y.
- Higher conditional entropy indicates greater remaining uncertainty about Y.
- Independent variables satisfy \(H(Y\mid X)=H(Y)\).

Conditional entropy is useful for evaluating the predictive information contained in one variable about another.

The implementations calculate conditional entropy using joint and marginal distributions.

## 9. Mutual Information

Mutual information measures the information shared between two random variables.

Its definition is:

\[
I(X;Y)=
H(X)+H(Y)-H(X,Y)
\]

An equivalent expression is:

\[
I(X;Y)=H(Y)-H(Y\mid X)
\]

Important properties include:

- Mutual information is non-negative.
- It is symmetric.
- It equals zero when the variables are statistically independent.
- It measures statistical dependence, including nonlinear dependence.

Mutual information is particularly useful in:

- Feature selection.
- Information retrieval.
- Statistical dependence analysis.
- Data processing.
- Machine learning.
- Communication systems.

The joint distribution example produces positive mutual information because the variables are dependent.

## 10. Probability Smoothing

Probability smoothing addresses zero-frequency problems in estimated distributions.

Additive smoothing, also called Laplace smoothing when the pseudocount is one, modifies the probabilities as follows:

\[
q_i=\frac{p_i+\alpha}{1+n\alpha}
\]

Where:

- \(p_i\) is the original probability.
- \(\alpha\) is the smoothing parameter.
- \(n\) is the number of possible outcomes.

For positive \(\alpha\), every event receives a nonzero probability.

This is useful when estimating probabilities from limited observations.

The implementations reject invalid smoothing parameters and verify that the resulting probabilities sum to one.

Smoothing changes the original probability model. Its parameter should therefore be selected according to the estimation problem rather than treated as an automatic correction.

## 11. Entropy and Machine Learning

### Classification Loss

For a classification model, let the predicted probability of the correct class be \(q_y\).

The negative log-likelihood loss is:

\[
L=-\log_2(q_y)
\]

For a dataset of \(N\) examples, the average categorical cross-entropy is:

\[
L=
-\frac{1}{N}
\sum_{i=1}^{N}
\sum_{c=1}^{C}
y_{ic}\log_2(q_{ic})
\]

Where:

- \(N\) is the number of examples.
- \(C\) is the number of classes.
- \(y_{ic}\) is the actual target indicator.
- \(q_{ic}\) is the predicted probability.

For one-hot targets, only the probability assigned to the correct class contributes to the loss.

A confident incorrect prediction receives a larger penalty than an uncertain prediction.

### Practical Classification Example

Suppose the actual class is B.

A model produces:

| Class | Predicted probability |
|---|---:|
| A | 0.15 |
| B | 0.70 |
| C | 0.15 |

The classification loss is:

\[
L=-\log_2(0.70)
\]

\[
L\approx0.514573\text{ bits}
\]

This demonstrates why probabilistic classification evaluates confidence, not only the predicted class label.

## 12. Python Implementation

The Python script provides a mathematical simulation environment using standard-library components.

### Implemented components

| Component | Responsibility |
|---|---|
| `Distribution` | Immutable probability representation |
| `ProbabilityError` | Invalid probability handling |
| `entropy()` | Shannon entropy |
| `cross_entropy()` | Cross-entropy |
| `kl_divergence()` | KL divergence |
| `binary_entropy()` | Bernoulli entropy |
| `smooth_distribution()` | Additive smoothing |
| `joint_entropy()` | Joint entropy |
| `conditional_entropy_y_given_x()` | Conditional entropy |
| `mutual_information()` | Shared information |
| `classification_loss()` | Negative log-likelihood |

The script also:

- Validates probability dimensions.
- Checks probability normalization.
- Handles zero-probability events.
- Uses assertions to verify mathematical identities.
- Saves numerical results in JSON format.

### Execution

Run the script with Python 3:

`python entropy_analysis.py`

The program creates `entropy_analysis.json` containing the principal numerical results.

## 13. JavaScript Implementation

The JavaScript implementation uses a different computational architecture.

### Main components

| Component | Responsibility |
|---|---|
| `ProbabilityDistribution` | Map-based probability storage |
| `OnlineEstimator` | Incremental frequency estimation |
| `MetricEngine` | Metric calculation and event publication |
| `evaluateBatch()` | Asynchronous batch processing |
| `smooth()` | Probability smoothing |
| `conditionalEntropy()` | Joint distribution analysis |

The `OnlineEstimator` stores event counts rather than retaining every observation.

For a fixed event space, updating a count requires constant time.

This makes the estimator suitable for streaming frequency data.

The `MetricEngine` uses a listener-based architecture. Applications can subscribe to evaluation events and receive calculated metrics.

Batch processing uses promises and bounded batches to avoid creating an unnecessarily large number of pending operations.

### Execution

Run with Node.js:

`node entropy.js`

The program writes `entropy_results.json`.

## 14. C++17 Implementation

The C++ program emphasizes explicit domain modeling and computational control.

### Main components

| Component | Responsibility |
|---|---|
| `Distribution` | Validated probability vector |
| `JointDistribution` | Joint and marginal probabilities |
| `EntropyEngine` | Metric evaluation |
| `Evaluation` | Structured metric results |
| `ProbabilityError` | Domain-specific exception |
| `classificationLoss()` | Classification loss |

The implementation uses STL vectors for probability storage and performs calculations without external dependencies.

The joint distribution class maintains marginal probability vectors during construction.

This avoids repeatedly reconstructing the marginals when multiple information measures are requested.

The evaluation structure checks:

\[
H(P,Q)=H(P)+D_{KL}(P\parallel Q)
\]

The program also includes exception handling, smoothing, and validation tests.

### Compilation

Compile using a C++17-compatible compiler:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic entropy.cpp -o entropy`

Execute:

`./entropy`

On Windows:

`entropy.exe`

## 15. Java 17 Implementation

The Java implementation models probability analysis as an enterprise-oriented service.

### Main components

| Component | Responsibility |
|---|---|
| `ProbabilityDistribution` | Immutable probability record |
| `EvaluationPolicy` | Evaluation restrictions |
| `EvaluationResult` | Structured evaluation outcome |
| `EntropyService` | Mathematical calculations |
| `JointDistribution` | Joint and conditional analysis |
| `ClassificationService` | Classification loss and batch evaluation |
| `ProbabilityException` | Domain validation errors |

Java records represent immutable domain values.

The policy object separates mathematical calculation from evaluation acceptance.

For example, a policy can require finite cross-entropy and impose a maximum acceptable loss.

The evaluation service distinguishes:

- Valid evaluation.
- Infinite loss.
- Policy rejection.

This distinction matters because an infinite cross-entropy value is a mathematical result, while policy rejection is an operational decision.

### Execution

Compile:

`javac EntropyAnalytics.java`

Run:

`java EntropyAnalytics`

The program requires Java 17.

## 16. PostgreSQL Implementation

The SQL implementation models probability distributions and their evaluation as relational data.

### Database structure

| Table | Purpose |
|---|---|
| `probability_distribution` | Distribution metadata |
| `probability_event` | Individual event probabilities |
| `joint_probability` | Joint probability observations |
| `evaluation_policy` | Evaluation restrictions |
| `entropy_evaluation` | Stored metric results |

### Relationships

The relational structure is:

`probability_distribution`

→ `probability_event`

→ `entropy_evaluation`

`probability_distribution`

→ `joint_probability`

`evaluation_policy`

→ `entropy_evaluation`

A distribution can contain multiple events. An evaluation references one actual distribution, one predicted distribution, and one evaluation policy.

### Database functions

| Function | Operation |
|---|---|
| `validate_distribution()` | Verify normalization |
| `validate_joint_distribution()` | Verify joint probabilities |
| `calculate_entropy()` | Shannon entropy |
| `calculate_cross_entropy()` | Cross-entropy |
| `calculate_kl_divergence()` | KL divergence |
| `calculate_joint_entropy()` | Joint entropy |
| `calculate_conditional_entropy()` | Conditional entropy |
| `calculate_mutual_information()` | Mutual information |

The `evaluate_distribution_pair` procedure performs the evaluation workflow and stores its results.

The reporting views provide distribution validation and evaluation summaries.

### Integrity and performance

Primary keys, foreign keys, unique constraints, and check constraints protect relational integrity.

Indexes support distribution lookups, event retrieval, and evaluation reporting.

Probability normalization is validated through database functions because it depends on aggregating multiple rows. A row-level check constraint alone cannot enforce that the complete distribution sums to one.

The SQL script uses transactional execution for its sample workflow.

### Execution

Run the complete script against PostgreSQL:

`psql -U postgres -d your_database -f entropy.sql`

The database user must have permission to create the schema, tables, functions, procedures, and views.

## 17. Complexity and Performance

Let:

- \(n\) represent the number of events.
- \(r\) represent the number of observations.
- \(m\times k\) represent the dimensions of a joint probability matrix.

| Operation | Time complexity | Auxiliary space |
|---|---:|---:|
| Probability validation | \(O(n)\) | \(O(1)\) |
| Shannon entropy | \(O(n)\) | \(O(1)\) |
| Cross-entropy | \(O(n)\) | \(O(1)\) |
| KL divergence | \(O(n)\) | \(O(1)\) |
| Binary entropy | \(O(1)\) | \(O(1)\) |
| Additive smoothing | \(O(n)\) | \(O(n)\) |
| Joint entropy | \(O(mk)\) | \(O(1)\) beyond input |
| Marginal calculation | \(O(mk)\) | \(O(m+k)\) |
| Mutual information | \(O(mk)\) | \(O(m+k)\) |
| Online frequency update | \(O(1)\) average with hash maps | \(O(n)\) |

The JavaScript and Python implementations use dictionaries or maps for event-frequency storage.

The C++ and Java implementations use arrays or vectors for numerical operations.

For large distributions, dense arrays offer predictable memory access and low indexing overhead. Sparse representations are more appropriate when most possible events have zero probability.

For database workloads, indexes improve retrieval but introduce storage and write overhead.

## 18. Numerical Accuracy and Failure Conditions

Probability calculations involve floating-point arithmetic.

The implementations account for several important cases.

| Condition | Expected behavior |
|---|---|
| Probability below zero | Reject |
| Probability above one | Reject |
| Non-finite probability | Reject |
| Probabilities not summing to one | Reject |
| Empty distribution | Reject |
| Mismatched event spaces | Reject |
| Zero actual probability | Entropy contribution is zero |
| Zero predicted probability for an actual event | Infinite cross-entropy and KL divergence |
| Invalid smoothing parameter | Reject |
| Numerical rounding near zero | Clamp tiny negative KL results to zero |

Normalization checks use tolerances because floating-point arithmetic cannot always represent decimal probabilities exactly.

For high-dimensional probability models, production implementations should also consider compensated summation and more specialized numerical methods.

## 19. Security and Production Considerations

Probability calculations may be part of sensitive analytical systems.

Relevant engineering controls include:

- Validate all externally supplied probability values.
- Reject malformed probability vectors and matrices.
- Enforce database access restrictions.
- Use parameterized database operations in application integrations.
- Avoid trusting client-provided evaluation results.
- Record the actual and predicted distribution versions.
- Preserve the evaluation policy associated with each result.
- Monitor infinite losses and unusually large divergences.
- Avoid exposing sensitive individual-level observations in analytical reports.
- Use bounded batch processing for large evaluation workloads.

A probability distribution should be treated as an identifiable analytical input rather than an unstructured collection of numbers.

Reproducible evaluations require retaining the distributions, metric definitions, numerical conventions, and applicable policy.

## 20. Conceptual Distinctions

The following distinctions are essential when using information theory in computing.

| Concept | Meaning |
|---|---|
| Probability | Likelihood assigned to an event |
| Self-information | Information content of an individual event |
| Entropy | Expected uncertainty of a distribution |
| Cross-entropy | Expected coding or prediction cost using another distribution |
| KL divergence | Additional expected information relative to a reference distribution |
| Joint entropy | Uncertainty in two variables together |
| Conditional entropy | Remaining uncertainty after observing another variable |
| Mutual information | Shared information between variables |
| Smoothing | Modification of estimated probabilities to avoid zero-frequency problems |
| Negative log-likelihood | Loss associated with the probability assigned to the observed outcome |

These concepts are related mathematically but are not interchangeable.

In particular, entropy measures uncertainty within a distribution, cross-entropy evaluates a predicted distribution against a reference distribution, and KL divergence isolates the additional information cost associated with the difference between those distributions.
