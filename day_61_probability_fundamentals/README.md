# Probability Fundamentals

## Scope

This project develops finite probability models from first principles through executable implementations. The central model consists of a sample space, outcomes, event sets, probability assignments, and experiments that produce observations.

The four primary mathematical ideas are treated as distinct mechanisms:

| Concept | Role |
|---|---|
| Experiment | A repeatable procedure whose possible results are modeled |
| Sample space | The complete set of possible outcomes |
| Event | A subset of the sample space representing a condition of interest |
| Probability axioms | Rules that make probability assignments mathematically valid |

The implementations also connect exact probability calculations with simulation. Exact calculations use a declared probability distribution, while simulations estimate probabilities from repeated observations.

## Mathematical Model

A finite probability space is represented as:

`(Ω, P)`

where `Ω` is the sample space and `P` assigns a probability to each outcome.

For a finite sample space:

`P(Ω) = 1`

`P(A) >= 0`

For mutually exclusive events `A` and `B`:

`P(A ∪ B) = P(A) + P(B)`

For arbitrary events:

`P(A ∪ B) = P(A) + P(B) - P(A ∩ B)`

The complement satisfies:

`P(Aᶜ) = 1 - P(A)`

For an event `B` with positive probability:

`P(A | B) = P(A ∩ B) / P(B)`

These rules are implemented rather than merely described.

## Experiments and Sample Spaces

An experiment defines the process that generates an observation. A sample space defines what observations are possible.

The source implementations use a six-sided die as the primary finite model. Its sample space is:

`Ω = {1, 2, 3, 4, 5, 6}`

For a fair die:

`P(1) = P(2) = ... = P(6) = 1/6`

This distinction matters because the experiment is operational while the sample space is mathematical. A die-rolling procedure generates results, while the probability model describes those possible results and their probabilities.

The Python implementation represents the sample space through the `SampleSpace` dataclass. It validates that every declared outcome has a probability, that probabilities are within `[0, 1]`, and that their total is one.

The JavaScript implementation stores outcomes and probabilities in a `Map`. Its `ProbabilitySpace` validates the distribution before any event calculation is permitted.

The C++17 implementation uses `std::map<int, double>` for deterministic ordering and direct probability lookup.

The Java 17 implementation uses a generic `ProbabilitySpace<T>`, allowing the same mathematical structure to support different outcome types.

## Events

An event is a subset of the sample space.

For the die model:

`E = {2, 4, 6}`

represents the event that the result is even.

Another event is:

`Q = {2, 3, 5}`

representing a prime result.

The source implementations explicitly model event membership rather than encoding events as informal conditions only.

The important event operations are:

| Operation | Mathematical meaning |
|---|---|
| Union | `A ∪ B`, either event occurs |
| Intersection | `A ∩ B`, both conditions occur |
| Complement | `Aᶜ`, the event does not occur |

The implementations validate that event outcomes belong to the associated sample space. This prevents an event such as `{7}` from being silently evaluated against a six-sided die.

## Probability Axioms

The probability model enforces three fundamental properties.

### Non-negativity

Every outcome has:

`P(x) >= 0`

The implementations reject negative probabilities.

### Normalization

The complete sample space has probability one:

`P(Ω) = 1`

The Python, JavaScript, C++, Java, and PostgreSQL implementations validate the total probability.

### Additivity

For disjoint events, probabilities add directly.

For overlapping events, the intersection must be removed once:

`P(A ∪ B) = P(A) + P(B) - P(A ∩ B)`

The die example has:

`P(even) = 1/2`

`P(prime) = 1/2`

`P(even ∩ prime) = 1/6`

Therefore:

`P(even ∪ prime) = 1/2 + 1/2 - 1/6 = 5/6`

The code calculates the union from sets rather than hard-coding the result.

## Complement Events

The complement contains every sample-space outcome not contained in the original event.

For:

`E = {2, 4, 6}`

the complement is:

`Eᶜ = {1, 3, 5}`

The implementations derive this set from the complete sample space. This prevents accidental inclusion of values that are not valid outcomes.

The resulting probability satisfies:

`P(Eᶜ) = 1 - P(E) = 1/2`

## Conditional Probability

Conditional probability changes the reference space from all outcomes to the outcomes satisfying the condition.

The implementation evaluates:

`P(A | B) = P(A ∩ B) / P(B)`

For the die:

`prime = {2, 3, 5}`

`even = {2, 4, 6}`

Their intersection is `{2}`.

Therefore:

`P(prime | even) = (1/6) / (1/2) = 1/3`

A zero-probability conditioning event is rejected because division by zero does not define a conditional probability in this finite model.

## Simulation

Exact probability and empirical probability serve different purposes.

An exact calculation uses the declared model:

`P(6) = 1/6`

A simulation performs repeated trials and calculates:

`estimated probability = successes / trials`

The Python implementation uses `random.Random` with an explicit seed so the demonstration is reproducible.

The JavaScript implementation uses Node.js cryptographic randomness for its die simulation. The `Experiment` class emits progress and completion events, separating experiment execution from reporting.

The C++17 implementation uses `std::mt19937_64` and `std::uniform_int_distribution`.

The Java implementation uses `Random` with an explicit seed.

The simulation results will not necessarily equal the theoretical probability. Random variation is expected. Increasing the number of trials generally reduces the typical sampling error.

## Binomial Experiment

The source files also evaluate the probability of exactly `k` successes in `n` independent trials with success probability `p`.

The formula is:

`P(X = k) = C(n, k) p^k (1-p)^(n-k)`

For five fair coin flips and exactly three heads:

`P(X = 3) = C(5, 3)(0.5)^3(0.5)^2`

which gives:

`0.3125`

The implementations calculate the binomial coefficient multiplicatively rather than constructing a large factorial. This avoids unnecessary intermediate growth.

## Python Implementation

The Python program is organized around explicit mathematical domain objects.

### `SampleSpace`

`SampleSpace` is a frozen dataclass containing:

- the finite set of outcomes
- the probability assigned to every outcome

Validation occurs during object construction. Invalid distributions cannot become active probability models.

### `Event`

`Event` stores a name and an immutable outcome set. Functions such as `union`, `intersection`, and `complement` return new events rather than mutating existing events.

### Exact calculations

The program implements:

- event probability
- complement probability
- union
- intersection
- conditional probability
- binomial probability

The implementation uses standard Python collections and exceptions rather than external packages.

### Simulation

`estimate_probability` accepts an experiment function and an event predicate. This separates the mechanism generating observations from the definition of the event being measured.

The same simulation function can therefore be used for a coin, die, or another finite experiment.

### Validation

Assertions test:

- normalization
- impossible events
- certain events
- event intersections
- event unions
- complements
- conditional probability
- binomial probability
- rejection of invalid distributions

## JavaScript Implementation

The JavaScript program uses Node.js standard-library facilities and an event-driven simulation design.

### `ProbabilitySpace`

The probability model uses `Map`, providing explicit key-value association between outcomes and probabilities.

The constructor performs validation before the object can be used.

### `EventSet`

`EventSet` uses `Set` for mathematical membership operations. Union and intersection are therefore implemented using native set behavior rather than array scanning.

### Event-driven experiment execution

The `Experiment` class extends Node.js `EventEmitter`.

It emits:

- `progress` during a large simulation
- `complete` after all trials

This separates experiment execution from consumers interested in monitoring progress.

### Randomness

The simulation uses `crypto.randomBytes` to produce a random unsigned 32-bit value. The value is scaled into the unit interval and converted into a die outcome.

This is intentionally different from the seeded pseudo-random generators used by the other implementations.

### Failure handling

Invalid trial counts, invalid probabilities, invalid events, and zero-probability conditional events generate explicit errors.

## C++17 Implementation

The C++ program presents probability calculations alongside a separate governance-oriented engineering case study.

### Probability representation

`ProbabilitySpace` uses `std::map<int, double>`. Construction validates the probability distribution.

`std::set<int>` represents event outcomes.

The standard library algorithms `set_union`, `set_intersection`, and `set_difference` implement event algebra.

### Numerical validation

Calculations compare floating-point values against a small tolerance rather than requiring exact binary floating-point equality.

This is important because values such as `1.0 / 6.0` cannot be represented exactly in binary floating-point.

### Simulation

`std::mt19937_64` supplies pseudo-random values and `std::uniform_int_distribution<int>` models the die.

The seed makes the demonstration reproducible.

### Governance case study

The additional domain model demonstrates how a finite decision system can use explicit states and policy conditions.

The `PullRequest` structure contains:

- source branch
- target branch
- commits
- reviews
- status checks
- unresolved conversations
- source-branch synchronization state

`BranchProtection` contains repository-level constraints.

`MergeEligibilityEngine` evaluates these conditions independently.

The governance model is separate from the probability model. It is included as an engineering case study showing how discrete state and Boolean conditions can be represented with C++ structures, enums, containers, and algorithms.

## Java 17 Implementation

The Java implementation uses stronger domain modeling and immutable records.

### Generic probability space

`ProbabilitySpace<T>` is generic, so its mathematical operations are not restricted to integer outcomes.

The constructor copies the supplied map into an immutable representation.

### Records

Java records model compact domain values:

- `Review`
- `StatusCheck`
- `BranchProtectionPolicy`
- `PullRequest`
- `Event`

This makes state explicit while reducing accidental mutation.

### Experiment service

`Experiment<T>` contains a seeded random generator and estimates event probabilities through repeated trials.

The generator and event predicate are passed into the estimation operation, separating the source of observations from the condition being measured.

### Governance service

`MergeEligibilityService` evaluates merge eligibility using:

- Pull Request state
- source and target branches
- commit presence
- branch synchronization
- eligible approvals
- required status checks
- unresolved conversations

The service counts only approvals from eligible reviewers. An approval by an ineligible reviewer does not satisfy the policy.

A failing status check blocks eligibility even when the required human approvals exist.

This provides an explicit example of a rule-based finite state and policy system without mixing those rules into the probability calculations.

## PostgreSQL Implementation

The PostgreSQL script models probability as relational data.

### Core tables

The database contains:

| Table | Purpose |
|---|---|
| `sample_spaces` | Defines finite probability models |
| `outcomes` | Stores possible outcomes and probabilities |
| `events` | Defines event sets |
| `event_outcomes` | Associates outcomes with events |
| `experiments` | Records repeated experiments |
| `experiment_results` | Stores observed frequencies |
| `probability_policies` | Stores acceptance thresholds for empirical results |

Foreign keys preserve the relationships between these entities.

### Constraints

Outcome probabilities are constrained to `[0, 1]`.

Experiment trial counts and observed counts must be positive or zero where appropriate.

Unique constraints prevent duplicate outcomes within one sample space and duplicate event membership.

A trigger checks that an event and its selected outcome belong to the same sample space.

This prevents a logically invalid relationship such as assigning outcome `7` from one probability model to an event belonging to another model.

### Probability functions

`event_probability` calculates the probability of an event by summing the probabilities of its associated outcomes.

`validate_sample_space_probabilities` verifies that a populated sample space has probabilities summing to one.

These functions put important validation close to the stored data.

### Views

`event_probability_report` provides event-level probability reporting.

`experiment_distribution_report` compares theoretical and empirical probabilities for recorded trials.

The latter makes it possible to inspect simulation accuracy without changing the underlying observations.

### CTE-based evaluation

The script uses common table expressions to evaluate:

- event probabilities
- complements
- union relationships
- intersections
- conditional probability
- simulation accuracy

The conditional probability query calculates the intersection first and divides it by the probability of the conditioning event.

### Transactions

The probability-space validation is executed inside a transaction. This provides an explicit database workflow for validating the model as a unit.

## Distinguishing Exact and Empirical Probability

Exact probability describes the mathematical model.

Empirical probability describes observed data.

They can be compared as:

`error = empirical_probability - theoretical_probability`

The PostgreSQL reporting view calculates this difference for every outcome.

The `probability_policies` table demonstrates a practical acceptance rule. A simulation can be considered acceptable when its maximum absolute error remains below a declared tolerance.

The tolerance is a policy decision, not a mathematical axiom.

## Edge Cases

The implementations explicitly handle several invalid conditions.

### Empty sample space

A probability model without outcomes cannot satisfy normalization and is rejected.

### Negative probabilities

Negative probability assignments violate the probability axioms and are rejected.

### Probabilities greater than one

An individual event probability cannot exceed one. Such assignments are rejected.

### Probability total not equal to one

A distribution such as `{A: 0.7, B: 0.7}` is invalid because its total is `1.4`.

### Unknown event outcomes

An event containing an outcome outside its sample space is rejected.

### Zero-probability conditional event

`P(A | B)` cannot be evaluated when `P(B) = 0` using the implemented finite formula.

### Invalid trial counts

Simulation functions reject zero or negative trial counts because no meaningful empirical estimate can be produced.

### Floating-point comparison

The implementations use tolerances when comparing calculated probability totals. This avoids false failures caused by floating-point representation.

## Complexity and Performance

For a finite sample space containing `n` outcomes:

- calculating an event probability is `O(k)` for an event with `k` outcomes
- set union is approximately `O(n log n)` for ordered C++ sets
- set intersection is approximately `O(n log n)` for ordered C++ sets
- complement construction is proportional to the sample-space size
- a simulation with `T` trials is `O(T)`

The PostgreSQL implementation uses indexes on foreign-key and association columns that are used by event and experiment queries.

The source implementations intentionally avoid unnecessary external dependencies because the mathematical model is small enough to implement with standard language facilities.

## Security and Reliability Considerations

Probability calculations themselves are not security controls. The main reliability concern is preserving the integrity of the probability model and distinguishing mathematical assumptions from observations.

The implementations therefore:

- validate input probabilities
- reject unknown outcomes
- reject invalid trial counts
- avoid silently correcting invalid distributions
- use explicit error handling
- keep mathematical operations deterministic where reproducibility is useful
- separate theoretical probabilities from empirical observations

The JavaScript simulation uses Node.js cryptographic randomness for its demonstration. This should not be interpreted as proof that the surrounding application is cryptographically secure.

Simulation results should not be treated as exact mathematical probabilities.

## Relationship Between the Five Implementations

The five source files implement the same mathematical foundations from different engineering perspectives.

| Implementation | Primary perspective |
|---|---|
| Python | Dataclass-based probability model and reusable simulation functions |
| JavaScript | Set-based event operations and event-driven experiment execution |
| C++17 | STL-based event algebra, numerical validation, and structured systems case study |
| Java 17 | Generic immutable domain types, records, and service-oriented policy evaluation |
| PostgreSQL | Relational probability model, constraints, functions, triggers, views, and analytical queries |

The implementations are deliberately not identical translations. Each language uses structures that fit its runtime and programming model.

## Operational Flow

The complete conceptual workflow is:

`Experiment`
  
`↓`

`Sample Space`

`↓`

`Outcome Probabilities`

`↓`

`Event Definition`

`↓`

`Event Operations`

`↓`

`Exact Probability`

`↓`

`Repeated Trials`

`↓`

`Empirical Probability`

`↓`

`Theoretical vs Empirical Evaluation`

The same workflow can be represented relationally:

`sample_spaces → outcomes → events → event_outcomes`

and for observations:

`experiments → experiment_results`

This separation preserves the distinction between what the probability model says should happen and what an experiment actually observed.

## Practical Interpretation

A probability model is only meaningful when its sample space and probability assignments correspond to the experiment being studied.

A fair die and a loaded die have the same possible outcomes but different probability assignments.

Likewise, a simulation can produce a frequency close to `1/6` without proving that the underlying die is fair. The empirical result is evidence produced by the experiment, while fairness is a property assumed by the theoretical model.

The project therefore keeps three layers separate:

1. The experiment defines how observations are generated.
2. The probability model assigns mathematical probabilities to possible outcomes.
3. The empirical analysis compares observed frequencies with the theoretical model.

That separation is the central design principle shared across the five implementations.
