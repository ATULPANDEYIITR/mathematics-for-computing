# Information Theory: Information, Entropy, Uncertainty and Self-Information

## 1. Technical Scope

Information theory is the mathematical study of information representation, uncertainty, communication and efficient encoding. It provides a quantitative framework for understanding how much information an observation carries and how efficiently information can be represented.

This project implements the fundamental probability-based concepts of information theory across Python, JavaScript, C++17, Java 17 and PostgreSQL.

The central concepts are:

- Information and uncertainty.
- Probability distributions.
- Self-information.
- Shannon entropy.
- Maximum and normalized entropy.
- Joint entropy.
- Conditional entropy.
- Mutual information.
- Cross-entropy.
- Kullback-Leibler divergence.
- Empirical probability estimation.
- Huffman source coding.

All primary information measurements use bits unless another logarithm base is explicitly selected.

## 2. Information and Uncertainty

Information measures the reduction in uncertainty associated with observing an outcome.

Consider a discrete random variable X with possible outcomes:

X = {x1, x2, ..., xn}

Each outcome has a probability P(x), where:

- P(x) is greater than or equal to zero.
- P(x) is less than or equal to one.
- The probabilities of all possible outcomes sum to one.

A probability distribution represents the uncertainty associated with a random variable.

A highly predictable source has concentrated probability mass. A source with equally likely outcomes has greater uncertainty when the number of possible outcomes is fixed.

Information theory distinguishes the information associated with one observation from the average uncertainty of an entire source.

## 3. Self-Information

Self-information, also called information content or surprisal, quantifies the information associated with a particular event.

The mathematical definition is:

I(x) = -log₂ P(x)

Where:

- I(x) is the self-information of outcome x.
- P(x) is the probability of that outcome.
- The logarithm base determines the information unit.

For base 2, the measurement is expressed in bits.

### Interpretation

| Probability | Self-information |
|---:|---:|
| 1.00 | 0 bits |
| 0.50 | 1 bit |
| 0.25 | 2 bits |
| 0.125 | 3 bits |
| 0.0625 | 4 bits |

A certain event provides zero new information because its occurrence was already known.

A less probable event carries more information when observed.

An event with probability zero has infinite mathematical self-information. Such an event cannot occur under the specified probability model.

### Implementation

The five implementations calculate self-information through logarithmic operations.

Important validation conditions include:

- Probability must be finite.
- Probability must belong to the interval [0, 1].
- The logarithm base must be positive and different from one.
- Zero probability requires explicit handling.

The Python, JavaScript, C++ and Java implementations return positive infinity for an impossible event rather than attempting to calculate the logarithm of zero.

The PostgreSQL implementation uses the corresponding `self_information()` function.

## 4. Shannon Entropy

Shannon entropy measures the expected self-information of a discrete random variable.

Its mathematical definition is:

H(X) = -Σ P(x) log₂ P(x)

Entropy is an average over all possible outcomes, not the information content of one particular observation.

For a discrete source with four outcomes:

| Outcome | Probability | Self-information |
|---|---:|---:|
| A | 0.50 | 1 bit |
| B | 0.25 | 2 bits |
| C | 0.125 | 3 bits |
| D | 0.125 | 3 bits |

The expected entropy is:

H(X) = (0.50 × 1) + (0.25 × 2) + (0.125 × 3) + (0.125 × 3)

H(X) = 1.75 bits

This distribution is used consistently in the five implementations.

### Important properties

1. Entropy is non-negative.
2. Entropy equals zero for a deterministic distribution.
3. Entropy reaches its maximum when all outcomes are equally probable.
4. Entropy is affected by the probability distribution, not by the names assigned to outcomes.
5. Entropy is measured in bits when logarithms use base two.

For n possible outcomes:

H(X) ≤ log₂(n)

The upper bound represents maximum uncertainty for a fixed number of outcomes.

### Maximum entropy

For a distribution containing n possible outcomes:

Hmax(X) = log₂(n)

For four equally probable outcomes:

Hmax(X) = 2 bits

The sample distribution has an entropy of 1.75 bits, which is below its maximum of 2 bits.

### Normalized entropy

Normalized entropy expresses actual entropy relative to its maximum.

Hnormalized(X) = H(X) / log₂(n)

Its value belongs to [0, 1] for a valid finite discrete distribution.

- Zero indicates complete certainty.
- One indicates maximum uncertainty.
- Intermediate values indicate partial uncertainty.

For a single possible outcome, normalized entropy is defined as zero.

## 5. Joint Entropy

Joint entropy measures the uncertainty associated with two random variables considered together.

For random variables X and Y:

H(X,Y) = -ΣxΣy P(x,y) log₂ P(x,y)

A joint distribution describes the probability of combinations of outcomes.

The project uses a weather and temperature example:

| Weather | Temperature | Joint probability |
|---|---|---:|
| Sunny | Hot | 0.30 |
| Sunny | Cold | 0.20 |
| Rainy | Hot | 0.10 |
| Rainy | Cold | 0.40 |

The four probabilities sum to one.

Joint entropy measures the uncertainty of the complete outcome pair rather than either variable independently.

### Marginal distributions

A marginal distribution describes one variable without retaining the other variable's individual outcomes.

For example:

P(X = Sunny) = 0.30 + 0.20 = 0.50

P(X = Rainy) = 0.10 + 0.40 = 0.50

The implementations calculate marginal distributions by aggregating joint probabilities.

This operation is important because conditional entropy and mutual information depend on marginal and joint probability calculations.

## 6. Conditional Entropy

Conditional entropy measures the remaining uncertainty about one random variable when another variable is known.

H(X|Y) = H(X,Y) - H(Y)

It describes how much uncertainty remains about X after observing Y.

Similarly:

H(Y|X) = H(X,Y) - H(X)

Conditional entropy has an important distinction from ordinary entropy:

- H(X) measures uncertainty without additional information.
- H(X|Y) measures uncertainty when Y is available.

If knowing Y completely determines X, then H(X|Y) is zero.

If X and Y are independent, then:

H(X|Y) = H(X)

The implementations calculate conditional entropy by grouping joint outcomes according to the conditioning variable, constructing conditional distributions and weighting each group's entropy by its marginal probability.

This provides an explicit implementation of the mathematical definition:

H(X|Y) = -ΣxΣy P(x,y) log₂ P(x|y)

## 7. Mutual Information

Mutual information measures how much information one random variable provides about another.

I(X;Y) = H(X) - H(X|Y)

An equivalent expression is:

I(X;Y) = H(X) + H(Y) - H(X,Y)

Mutual information is symmetric:

I(X;Y) = I(Y;X)

### Interpretation

| Relationship | Mutual information |
|---|---|
| Independent variables | Zero |
| Partially dependent variables | Positive |
| Perfectly predictable relationship | Maximum relative to the individual variable entropies |

Mutual information is non-negative and satisfies:

I(X;Y) ≤ min(H(X), H(Y))

It is useful in:

- Feature selection.
- Statistical dependence analysis.
- Communication systems.
- Signal processing.
- Information retrieval.
- Data exploration.
- Predictive variable analysis.

Mutual information measures statistical dependence, not necessarily causation.

The C++ implementation uses explicit marginal and joint calculations. Java provides a dedicated `JointInformation` service. JavaScript uses Maps to represent joint outcomes, while Python uses tuple-based joint distributions. PostgreSQL provides `calculate_mutual_information()`.

## 8. Cross-Entropy

Cross-entropy measures the expected coding cost when observations follow an actual distribution P but are evaluated using another distribution Q.

H(P,Q) = -Σx P(x) log₂ Q(x)

Where:

- P represents the actual distribution.
- Q represents the predicted distribution.

Cross-entropy is commonly used to evaluate probabilistic predictions.

Consider:

| Outcome | Actual probability | Predicted probability |
|---|---:|---:|
| A | 0.50 | 0.40 |
| B | 0.30 | 0.40 |
| C | 0.20 | 0.20 |

Cross-entropy measures the expected information cost when the predicted distribution is used to represent outcomes generated by the actual distribution.

Important distinctions:

- Entropy evaluates the actual distribution against itself.
- Cross-entropy evaluates one distribution using another distribution.
- Cross-entropy cannot be smaller than the entropy of the actual distribution for valid distributions.

If an actual event has positive probability but its predicted probability is zero, cross-entropy becomes infinite.

The implementations explicitly handle this condition.

## 9. Kullback-Leibler Divergence

Kullback-Leibler divergence measures the difference between two probability distributions.

DKL(P||Q) = Σx P(x) log₂(P(x)/Q(x))

It is related to entropy and cross-entropy:

DKL(P||Q) = H(P,Q) - H(P)

### Interpretation

A KL divergence of zero indicates identical probability distributions.

A positive value indicates a difference between the distributions.

KL divergence is:

- Non-negative.
- Zero when the distributions are identical.
- Asymmetric.
- Not a mathematical distance metric.

In general:

DKL(P||Q) ≠ DKL(Q||P)

The direction matters because the actual distribution P is being evaluated relative to Q.

Applications include:

- Probabilistic model evaluation.
- Distribution comparison.
- Statistical estimation.
- Information compression.
- Model calibration.
- Distribution shift analysis.

The project uses the same actual and predicted probability examples across its implementations.

An important edge case occurs when Q assigns zero probability to an outcome for which P assigns positive probability. The divergence is then infinite.

## 10. Empirical Probability Estimation

A probability distribution can be estimated from observed data.

For an outcome x:

P̂(x) = Count(x) / N

Where:

- Count(x) is the number of times x occurs.
- N is the total number of observations.
- P̂(x) is the empirical probability estimate.

Example observations:

`success, success, failure, success, failure, success`

The resulting distribution is:

| Outcome | Frequency | Probability |
|---|---:|---:|
| Success | 4 | 0.6667 |
| Failure | 2 | 0.3333 |

Empirical entropy can then be calculated from the estimated probabilities.

The Python implementation uses `Counter`, JavaScript uses `Map`, and Java uses collection-based frequency aggregation through its streaming service.

The C++ implementation maintains incremental counts in an ordered map.

PostgreSQL stores observations as relational records and creates empirical probability distributions through the `build_empirical_distribution()` procedure.

### Laplace smoothing

Empirical distributions can assign zero probability to outcomes that have not yet been observed.

Laplace smoothing reduces this problem.

P̂(x) = (Count(x) + α) / (N + αK)

Where:

- α is the smoothing parameter.
- N is the observation count.
- K is the number of possible outcomes.

For α = 1, every possible outcome receives one additional count.

This approach is implemented in Python and JavaScript.

Smoothing is particularly useful when estimated probabilities are used in cross-entropy or KL divergence calculations.

## 11. Huffman Coding

Huffman coding is a lossless variable-length source-coding algorithm.

It assigns shorter binary codewords to more probable outcomes and longer codewords to less probable outcomes.

Its objective is to minimize expected codeword length among binary prefix codes for a known discrete source distribution.

### Coding mechanism

1. Create one node for every source outcome.
2. Insert the nodes into a minimum-priority queue.
3. Remove the two nodes with the smallest probabilities.
4. Combine them into a parent node.
5. Insert the parent back into the priority queue.
6. Repeat until one root remains.
7. Assign zero and one to the two branches.
8. Traverse the tree to obtain codewords.

### Example

The four-outcome distribution is:

| Symbol | Probability |
|---|---:|
| A | 0.50 |
| B | 0.25 |
| C | 0.125 |
| D | 0.125 |

The implementation constructs a binary Huffman tree and generates a valid prefix code.

The precise codeword assignments may differ when equal-probability nodes are resolved differently.

### Expected code length

L = Σx P(x) l(x)

Where l(x) is the number of bits in the codeword assigned to x.

For a binary Huffman code:

H(X) ≤ L < H(X) + 1

For the sample distribution, an optimal construction can achieve an expected code length of 1.75 bits, equal to its source entropy.

### Prefix-free property

A code is prefix-free when no valid codeword is the prefix of another valid codeword.

This property enables unambiguous decoding without requiring separators between consecutive codewords.

The Python implementation uses `heapq`, JavaScript uses a custom minimum heap, C++ uses `priority_queue`, and Java uses `PriorityQueue`.

The implementations use deterministic tie-breaking where applicable to improve reproducibility.

## 12. Implementation Architecture

The five implementations address the same mathematical domain through different engineering structures.

| Language | Main design | Distinct engineering perspective |
|---|---|---|
| Python | Functions, dataclasses, dictionaries and exceptions | Mathematical analysis and source coding |
| JavaScript | Maps, EventEmitter, asynchronous processing and Promises | Event-driven entropy monitoring |
| C++17 | STL containers, priority queues and smart pointers | Efficient source-coding and numerical computation |
| Java 17 | Records, interfaces, immutable distributions and services | Enterprise-oriented domain modeling |
| PostgreSQL | Relational schema, SQL functions, procedures and views | Persistent probability and information analysis |

### Python implementation

The Python script separates probability validation from information calculations.

Its major components include:

- `validate_probability()`
- `validate_distribution()`
- `self_information()`
- `entropy()`
- `marginal_distribution()`
- `conditional_entropy()`
- `mutual_information()`
- `cross_entropy()`
- `kl_divergence()`
- `empirical_distribution()`
- `huffman_codes()`

The `HuffmanNode` dataclass provides ordered priority-queue nodes.

The implementation uses `math.fsum()` for more accurate summation of floating-point values.

Assertions verify important mathematical invariants.

### JavaScript implementation

The JavaScript implementation uses native `Map` structures to preserve explicit outcome keys.

Its `EntropyMonitor` class supports continuous observation processing.

The event-driven workflow is:

Observation → Count Update → Probability Estimation → Entropy Calculation → Event Emission

The asynchronous stream processor divides observations into batches and yields control between batches.

This structure allows an entropy-monitoring process to coexist with other event-loop operations.

The implementation uses Node.js standard-library modules and does not require npm dependencies.

### C++17 implementation

The C++ implementation emphasizes explicit domain modeling and efficient algorithms.

Its major components include:

- `Distribution`
- `JointDistribution`
- `InformationError`
- `HuffmanEncoder`
- `OnlineEntropyEstimator`

`priority_queue` provides the minimum-weight selection mechanism for Huffman construction.

`shared_ptr` manages the dynamically constructed Huffman tree.

The online estimator updates symbol frequencies incrementally rather than storing the entire observation history.

### Java 17 implementation

The Java implementation uses explicit domain types.

Records represent:

- `Outcome`
- `Observation`
- `JointOutcome`
- `Metric`

The `ProbabilityDistribution` class validates and exposes an immutable probability map.

The `InformationMetric` interface separates metric behavior from its implementation.

The `JointInformation` service handles marginal, conditional, joint and mutual information calculations.

The `DistributionComparison` service handles cross-entropy and KL divergence.

The `HuffmanCoder` class encapsulates source coding.

The `StreamingEntropyService` maintains synchronized observation counts.

This separation supports testing, controlled state changes and clear responsibilities between domain objects and calculation services.

### PostgreSQL implementation

The database models information-theoretic data as relational entities.

Its primary relationships are:

Experiments
    → Outcomes
    → Observations

Experiments
    → Probability Distributions
    → Distribution Probabilities

Experiments
    → Joint Distributions
    → Joint Probabilities

Experiments
    → Information Metrics

The schema uses:

- Primary keys for record identification.
- Foreign keys for referential integrity.
- Unique constraints for experiment and outcome identity.
- Check constraints for probability ranges.
- Indexes for observation and distribution retrieval.
- Functions for information calculations.
- Procedures for empirical probability generation.
- Views for entropy reporting.
- Transactions for controlled database execution.

Probability sums require aggregate validation because ordinary row-level CHECK constraints cannot enforce totals across multiple records.

The `validate_distribution()` function performs this aggregate validation.

## 13. Mathematical Relationships

The principal relationships implemented in the project are:

| Concept | Mathematical relationship |
|---|---|
| Self-information | I(x) = -log₂ P(x) |
| Entropy | H(X) = -Σ P(x)log₂P(x) |
| Maximum entropy | Hmax(X) = log₂(n) |
| Joint entropy | H(X,Y) = -ΣΣ P(x,y)log₂P(x,y) |
| Conditional entropy | H(X\|Y) = H(X,Y) - H(Y) |
| Mutual information | I(X;Y) = H(X) - H(X\|Y) |
| Cross-entropy | H(P,Q) = -ΣP(x)log₂Q(x) |
| KL divergence | DKL(P\|\|Q) = H(P,Q) - H(P) |
| Expected code length | L = ΣP(x)l(x) |

These equations describe related but distinct information-theoretic quantities.

Self-information applies to individual outcomes. Entropy describes average uncertainty. Conditional entropy incorporates known information. Mutual information quantifies shared information. Cross-entropy and KL divergence compare probability models. Huffman coding converts source probabilities into variable-length binary representations.

## 14. Validation and Edge Cases

Reliable information calculations require explicit input validation.

The implementations address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty distribution | Reject |
| Negative probability | Reject |
| Probability greater than one | Reject |
| Probabilities not summing to one | Reject |
| NaN or infinite probability | Reject |
| Probability equal to zero | Handle without logarithm errors |
| Probability equal to one | Zero self-information |
| Single-outcome distribution | Zero entropy |
| Invalid logarithm base | Reject |
| Zero predicted probability with positive actual probability | Infinite cross-entropy and KL divergence |
| Empty observation stream | Reject empirical estimation |
| Unknown Huffman symbol | Reject encoding |
| Non-matching comparison outcomes | Reject comparison |
| Floating-point rounding differences | Use numerical tolerance |

Probability validation is performed before the principal information calculations.

This is important because mathematically meaningful entropy and divergence values require valid probability distributions.

## 15. Performance Considerations

The principal computational costs depend on the number of outcomes, observations and joint states.

| Operation | Typical complexity |
|---|---|
| Probability validation | O(n) |
| Self-information | O(1) |
| Shannon entropy | O(n) |
| Marginal distribution | O(n) expected with hash-based storage |
| Joint entropy | O(n) |
| Conditional entropy | O(n) expected with grouping |
| Mutual information | O(n) expected with grouping |
| Cross-entropy | O(n) |
| KL divergence | O(n) |
| Empirical estimation | O(N) expected |
| Huffman tree construction | O(n log n) |
| Huffman code generation | O(n) |
| Online frequency update | O(1) expected with hash-based storage |

Here, n represents the number of distinct outcomes or joint states, and N represents the number of observations.

Important practical considerations:

- Dense joint distributions can become expensive when the number of variables increases.
- Large vocabularies require careful memory management.
- Repeated entropy calculations can benefit from cached counts or probability estimates.
- Floating-point arithmetic introduces small numerical errors.
- Sparse distributions should avoid unnecessary storage of zero-probability states.
- Large-scale streaming systems may require windowed or distributed aggregation.

The implementations favor transparent calculations and standard-library data structures rather than introducing external dependencies.

## 16. Security and Data Integrity

Probability calculations can be affected by incorrect, manipulated or incomplete input data.

Important operational controls include:

- Validate every probability before calculation.
- Restrict access to observation records.
- Preserve the provenance of observed data.
- Avoid accepting untrusted serialized numeric values without validation.
- Use parameterized database operations when integrating SQL functions into applications.
- Apply database permissions according to operational responsibilities.
- Use transactions for related database changes.
- Monitor unexpected changes in empirical distributions.
- Avoid treating statistical dependence as proof of causation.

Information theory itself does not provide data confidentiality or integrity protection. Its mathematical concepts can support cryptographic analysis, communication engineering and statistical monitoring, but these applications require additional security mechanisms.

## 17. Practical Applications

### Communication systems

Entropy measures the average information produced by a communication source.

Huffman coding demonstrates how source probabilities can support efficient lossless representation.

### Data compression

Variable-length coding assigns fewer bits to common symbols and more bits to rare symbols.

The expected code length can be compared with source entropy to evaluate coding efficiency.

### Machine learning

Cross-entropy evaluates probabilistic predictions.

KL divergence measures differences between probability distributions.

Mutual information can help identify informative variables.

### Cybersecurity

Information-theoretic measures can support analysis of randomness, statistical patterns and probability distributions.

Entropy measurements must be interpreted carefully. High entropy alone does not establish that a random-number generator is cryptographically secure.

### Research and statistics

Joint entropy and mutual information provide quantitative descriptions of relationships between random variables.

They can support feature analysis, uncertainty estimation and probabilistic modeling.

### Operational monitoring

The streaming implementations demonstrate how empirical probability distributions and entropy can be updated as observations arrive.

Changes in entropy may indicate changes in the distribution of observed events. Such changes require contextual investigation before they are interpreted as anomalies.

## 18. Limitations

The implementations focus on discrete probability distributions.

Continuous random variables require probability density functions and differential entropy, which has different mathematical properties from discrete Shannon entropy.

Other limitations include:

- Empirical probabilities depend on the available observation sample.
- Small datasets can produce unstable estimates.
- Laplace smoothing introduces a modeling assumption.
- KL divergence depends on the direction of comparison.
- Huffman coding assumes an available source probability model.
- Huffman coding does not necessarily achieve the performance of more advanced arithmetic or range coding systems.
- Basic online estimators retain frequency information for every observed category.
- The PostgreSQL model validates distributions when calculation functions are called rather than automatically enforcing a cross-row probability sum after every individual insert.
- Floating-point calculations require numerical tolerances.
- The implementations do not claim that statistical uncertainty is equivalent to cryptographic unpredictability.

The project therefore separates mathematical definitions, computational procedures, data validation and operational interpretation.

## 19. Execution Requirements

| Deliverable | Runtime |
|---|---|
| Python | Python 3.10 or later |
| JavaScript | Node.js 18 or later |
| C++17 | Compiler with C++17 support |
| Java | Java 17 or later |
| PostgreSQL | PostgreSQL 15 or later |

The Python, JavaScript, C++17 and Java 17 implementations use standard-library functionality.

The PostgreSQL script creates the `information_theory` schema, its relational structures, functions, procedures, sample data and reporting views.

The sample calculations use the same underlying probability models to make the mathematical results comparable across programming languages.
