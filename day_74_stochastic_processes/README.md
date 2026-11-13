# Stochastic Processes: Random Walks, Markov Chains and State Transitions

## 1. Domain and Mathematical Foundations

A stochastic process is a collection of random variables indexed by time or another ordered parameter. It describes systems whose evolution contains uncertainty.

Unlike a deterministic system, where an initial condition and fixed rules uniquely determine subsequent states, a stochastic system describes multiple possible outcomes with associated probabilities.

A discrete-time stochastic process can be represented as:

\[
X_0,X_1,X_2,\ldots,X_t
\]

where \(X_t\) represents the state of a system at time \(t\).

Examples include:

- Daily weather conditions.
- Financial market movements.
- Equipment reliability.
- Customer movement between service categories.
- Network congestion.
- Population dynamics.
- Inventory fluctuations.
- Disease progression.

Three concepts form the foundation of the implementations:

| Concept | Mathematical representation | Purpose |
|---|---|---|
| Stochastic process | \(X_t\) | Represents a system evolving under uncertainty |
| Random walk | \(X_{t+1}=X_t+Y_t\) | Models cumulative random movement |
| Markov chain | \(P(X_{t+1}\mid X_t)\) | Models probabilistic state transitions |

The implementations use discrete time and finite-state Markov chains, with a one-dimensional bounded random walk as a separate model.

## 2. Probability and State Transitions

A state represents a condition that a system can occupy.

For example, a computer system might have the following states:

- Operational
- Degraded
- Failed

A transition describes movement from one state to another.

The transition probability is:

\[
P_{ij}=P(X_{t+1}=j\mid X_t=i)
\]

For a finite-state Markov chain, the transition matrix is:

\[
P=
\begin{bmatrix}
p_{11}&p_{12}&\cdots&p_{1n}\\
p_{21}&p_{22}&\cdots&p_{2n}\\
\vdots&\vdots&\ddots&\vdots\\
p_{n1}&p_{n2}&\cdots&p_{nn}
\end{bmatrix}
\]

Every transition probability must satisfy:

\[
0\leq p_{ij}\leq 1
\]

Every row must sum to one:

\[
\sum_{j=1}^{n}p_{ij}=1
\]

This condition ensures that the system has a complete probability distribution for its next state.

### Example: Weather transitions

The weather model contains three states:

- Sunny
- Cloudy
- Rainy

Its transition matrix is:

\[
P=
\begin{bmatrix}
0.70&0.20&0.10\\
0.30&0.40&0.30\\
0.20&0.30&0.50
\end{bmatrix}
\]

The first row indicates that a sunny day has a 70% probability of remaining sunny, a 20% probability of becoming cloudy and a 10% probability of becoming rainy on the next observation.

These probabilities are illustrative model assumptions, not empirical weather forecasts.

## 3. Random Walks

A random walk is a stochastic process in which the next position depends on the current position and a random movement.

A one-dimensional random walk can be expressed as:

\[
X_{t+1}=X_t+Y_t
\]

where:

\[
Y_t=
\begin{cases}
+1 & \text{with probability }p\\
-1 & \text{with probability }1-p
\end{cases}
\]

For a symmetric random walk:

\[
p=0.5
\]

The expected movement per step is:

\[
E[Y_t]=p-(1-p)=2p-1
\]

The variance of an individual movement is:

\[
Var(Y_t)=4p(1-p)
\]

For independent movements, the expected position after \(n\) steps is:

\[
E[X_n]=X_0+n(2p-1)
\]

The variance is:

\[
Var(X_n)=4np(1-p)
\]

For a symmetric walk, the expected displacement is zero, although individual paths may move substantially away from the starting position.

### Bounded random walks

A bounded random walk restricts movement within lower and upper boundaries.

For example:

\[
-5\leq X_t\leq 5
\]

If the process reaches either boundary, it terminates.

Such a boundary is an absorbing state.

The implementations demonstrate bounded random walks using:

- Python's `RandomWalk` class.
- JavaScript's `RandomWalkAnalyzer`.
- The C++17 random movement simulation.
- PostgreSQL position states and transition rules.

A practical application is modeling the movement of a financial variable within predefined risk boundaries.

## 4. Markov Chains

A Markov chain is a stochastic process satisfying the Markov property.

The Markov property states:

\[
P(X_{t+1}\mid X_t,X_{t-1},\ldots,X_0)
=
P(X_{t+1}\mid X_t)
\]

The next state depends on the current state rather than the complete history of previous states.

This property does not mean that the system has no historical information. It means that the current state contains sufficient information for predicting its next transition under the specified model.

### Important distinctions

| Term | Meaning |
|---|---|
| State | A possible system condition |
| Transition | Movement between states |
| Transition probability | Probability of a particular movement |
| Transition matrix | Complete representation of transition probabilities |
| Initial distribution | Probability distribution at time zero |
| State distribution | Probability distribution at a particular time |
| Markov property | Conditional independence from earlier history given the current state |
| Time-homogeneous chain | Transition probabilities remain constant over time |
| Time-inhomogeneous chain | Transition probabilities depend on time |

The implementations primarily use time-homogeneous transition matrices.

### State distribution evolution

If the initial distribution is represented by a row vector:

\[
\pi_0=
\begin{bmatrix}
p_1&p_2&\cdots&p_n
\end{bmatrix}
\]

then:

\[
\pi_{t+1}=\pi_tP
\]

After \(t\) transitions:

\[
\pi_t=\pi_0P^t
\]

This provides the theoretical probability distribution of the system state at a future time.

It differs from a single simulation path, which represents only one possible realization.

## 5. Absorbing States

An absorbing state is a state that cannot be left after it is entered.

For state \(i\):

\[
P_{ii}=1
\]

and:

\[
P_{ij}=0,\quad j\neq i
\]

The reliability model contains:

- Operational
- Degraded
- Failed

Its transition matrix is:

\[
P=
\begin{bmatrix}
0.65&0.25&0.10\\
0.30&0.40&0.30\\
0&0&1
\end{bmatrix}
\]

The failed state is absorbing.

This model represents an irreversible failure process. It does not represent maintenance or recovery after failure.

### Transient and absorbing states

Transient states are states from which the process can eventually leave.

Absorbing states are terminal states.

For a chain with transient states followed by absorbing states, the transition matrix can be partitioned into canonical form:

\[
P=
\begin{bmatrix}
Q&R\\
0&I
\end{bmatrix}
\]

Where:

- \(Q\) represents transitions between transient states.
- \(R\) represents transitions from transient to absorbing states.
- \(I\) represents absorbing-state self-transitions.

When absorption occurs with probability one, the fundamental matrix is:

\[
N=(I-Q)^{-1}
\]

The expected number of visits to transient states is represented by \(N\).

The expected time until absorption is:

\[
t=N\mathbf{1}
\]

The absorption probabilities are:

\[
B=NR
\]

These expressions provide analytical solutions for finite absorbing Markov chains when the inverse exists.

The implementations use simulation and Monte Carlo estimation rather than calculating the fundamental matrix.

## 6. Stationary Distributions

A stationary distribution is a probability vector that remains unchanged after a transition:

\[
\pi=\pi P
\]

Subject to:

\[
\sum_i\pi_i=1
\]

and:

\[
\pi_i\geq0
\]

A stationary distribution describes long-run state probabilities under appropriate conditions.

For the weather transition matrix, the stationary distribution is approximately:

| State | Stationary probability |
|---|---:|
| Sunny | 0.48 |
| Cloudy | 0.30 |
| Rainy | 0.22 |

These values describe the long-run distribution implied by the specified transition probabilities.

A stationary distribution does not automatically guarantee convergence from every initial distribution.

Important conditions include:

- Irreducibility.
- Aperiodicity.
- Positive recurrence for general state spaces.

The Python implementation estimates a limiting distribution through repeated matrix-vector multiplication.

This is a numerical approximation. It does not independently establish convergence or uniqueness.

Periodic chains can oscillate rather than converge under ordinary repeated iteration.

## 7. Monte Carlo Simulation

Monte Carlo simulation uses repeated random experiments to estimate properties of a stochastic system.

Suppose \(N\) independent experiments produce \(S\) occurrences of a specified event.

The estimated probability is:

\[
\hat p=\frac{S}{N}
\]

The estimated standard error is:

\[
SE(\hat p)=
\sqrt{\frac{\hat p(1-\hat p)}{N}}
\]

An approximate 95% confidence interval is:

\[
\hat p\pm1.96SE(\hat p)
\]

The implementations estimate the probability that the reliability process eventually reaches the failed state within a specified number of transitions.

The distinction between two events is important:

- Eventual absorption: the process eventually reaches the absorbing state.
- Finite-horizon absorption: the process reaches the absorbing state within the maximum simulation period.

A simulation that does not reach the failed state within the specified horizon does not prove that failure can never occur.

### Simulation accuracy

Accuracy depends on:

- Number of experiments.
- Quality of the random-number generator.
- Independence between experiments.
- Correct transition probabilities.
- Simulation horizon.
- Correct identification of absorbing states.

A larger experiment count generally reduces Monte Carlo sampling error.

It does not correct an incorrectly specified stochastic model.

## 8. Python Implementation

The Python file provides a simulation-oriented mathematical framework.

### Main components

| Component | Responsibility |
|---|---|
| `ProcessType` | Identifies the supported process categories |
| `Transition` | Represents a state transition and its probability |
| `SimulationResult` | Stores the simulation output |
| `MarkovChain` | Validates and executes finite-state Markov chains |
| `RandomWalk` | Implements bounded one-dimensional random movement |
| `MonteCarloAnalyzer` | Estimates absorption probability |
| `build_weather_chain()` | Creates the weather model |
| `build_absorbing_chain()` | Creates the reliability model |

### Transition validation

The constructor verifies:

- Non-empty state definitions.
- Valid destination states.
- Finite transition probabilities.
- Probability bounds.
- Row probability totals.

A transition matrix with an invalid row is rejected before simulation.

### Reproducibility

The `random.Random` generator receives an optional seed.

The same initial conditions and seed reproduce the same simulation path within the same compatible Python implementation.

Each Monte Carlo experiment receives a separate seed derived from a master random generator.

This makes experiment execution reproducible without reusing the same random sequence for every trial.

### Statistical analysis

The stationary distribution method repeatedly applies the transition matrix.

The Monte Carlo analyzer reports:

- Experiment count.
- Successful absorption count.
- Estimated probability.
- Standard error.
- Approximate confidence interval.
- Mean absorption time.
- Final-state frequencies.

### File handling

The script saves the results in `stochastic_results.json`.

JSON output supports downstream reporting and programmatic analysis.

The output filename is restricted to the current working directory.

### Execution

The script requires Python 3.10 or later and no external dependencies.

It performs assertions before executing the demonstrations.

## 9. JavaScript Implementation

The JavaScript implementation uses an event-driven simulation architecture.

It separates transition modeling, simulation execution and statistical analysis.

### Main components

| Component | Responsibility |
|---|---|
| `RandomGenerator` | Reproducible pseudorandom values |
| `TransitionModel` | Validated transition configuration |
| `SimulationEngine` | Asynchronous process execution |
| `RandomWalkAnalyzer` | Bounded random walk |
| `StatisticalAnalyzer` | Descriptive statistical analysis |
| `monteCarloAbsorption()` | Repeated absorption experiments |
| `ProcessState` | Simulation lifecycle states |

### Event-driven execution

The simulation engine extends Node.js `EventEmitter`.

It exposes the following events:

- `started`
- `transition`
- `completed`
- `failed`

A transition event contains:

- Run identifier.
- Step number.
- Previous state.
- Current state.

This design separates simulation execution from event consumers.

A reporting component can subscribe to transitions without changing the underlying transition model.

### Asynchronous behavior

The `run()` method returns a Promise.

It supports:

- Asynchronous execution.
- Optional transition delays.
- Cancellation through `AbortSignal`.
- Error propagation.
- Cleanup of active simulation tracking.

The event-driven architecture is useful for simulations that must publish state changes to monitoring or visualization systems.

### Security and reliability

The implementation validates transition configurations and simulation limits.

It also uses:

- Immutable event payloads.
- Controlled report file permissions.
- Separate simulation seeds.
- Explicit error states.
- Structured result objects.

The built-in pseudorandom generator is intended for reproducible simulation, not cryptographic security.

## 10. C++17 Implementation

The C++17 program introduces explicit domain modeling and a separate repository governance demonstration alongside stochastic simulation.

### Main components

| Component | Responsibility |
|---|---|
| `State` | Enumerates reliability states |
| `Transition` | Represents an outgoing probability edge |
| `SimulationResult` | Stores a complete simulated path |
| `MarkovModel` | Stores and validates the transition graph |
| `ReliabilityAnalyzer` | Estimates failure probability |
| `GovernancePolicy` | Defines repository merge requirements |
| `MergeEligibilityEngine` | Evaluates merge eligibility |

### State representation

The implementation uses an enumeration rather than string-based state identifiers.

This provides:

- Compile-time state categories.
- Reduced string comparison overhead.
- Explicit domain modeling.
- More predictable state handling.

The transition graph uses an `unordered_map` for state lookup.

Outgoing edges are stored in vectors.

This makes transition evaluation proportional to the number of outgoing edges of the current state.

For a chain with \(n\) states and \(m\) transitions, constructing and validating the graph requires approximately:

\[
O(n+m)
\]

A single transition selection requires:

\[
O(d)
\]

where \(d\) is the number of outgoing transitions from the current state.

### Random-number generation

The implementation uses:

- `mt19937_64` for pseudorandom sequences.
- `bernoulli_distribution` for random-walk movements.
- `uniform_real_distribution` for transition selection.

The generator is initialized with a seed for repeatable experiments.

The generator is not intended for security-sensitive randomness.

### Reliability analysis

The reliability analyzer executes independent simulation experiments.

It estimates the probability of reaching the absorbing failure state and calculates an approximate confidence interval.

It also reports mean absorption time among successful experiments.

The mean is conditional on reaching the target within the simulation horizon.

### Repository governance engine

The C++ program includes a separate merge-eligibility model.

It evaluates:

- Pull Request state.
- Draft status.
- Source branch synchronization.
- Merge conflicts.
- Approval count.
- Open review conversations.
- Required status checks.
- Linear-history requirements.

This demonstration is separate from the stochastic transition model.

It illustrates how deterministic policy evaluation differs from probabilistic state evolution.

## 11. Java 17 Implementation

The Java implementation provides an enterprise-oriented domain architecture.

It uses records, enums, interfaces, immutable collections and service classes.

### Domain structure

| Type | Purpose |
|---|---|
| `State` | Defines system states |
| `RunStatus` | Defines simulation lifecycle |
| `Transition` | Represents probability edges |
| `SimulationEvent` | Represents state-transition events |
| `SimulationConfiguration` | Defines execution parameters |
| `SimulationResult` | Stores immutable simulation results |
| `TransitionMatrix` | Validates and stores transition definitions |
| `SimulationListener` | Defines event notification behavior |
| `SimulationService` | Executes stochastic simulations |
| `MonteCarloService` | Performs statistical estimation |

### Immutable domain objects

Java records provide concise immutable data structures.

The `Transition` record validates probability bounds.

The `SimulationConfiguration` record validates the execution limit.

The `SimulationResult` record defensively copies its path.

The transition matrix uses an `EnumMap` for state-keyed storage.

Its internal collections are exposed through immutable views.

### Service separation

The simulation service is responsible for executing transitions.

The Monte Carlo service is responsible for running repeated experiments and calculating estimates.

The listener interface separates event reporting from simulation mechanics.

This structure supports testing and future integration with enterprise monitoring systems.

### Enterprise governance

The Java implementation also contains:

- `ApprovalPolicy`
- `RepositoryChange`
- `EligibilityResult`
- `MergeEligibilityService`

The governance service evaluates deterministic merge requirements.

The approval policy is immutable after construction.

The merge-eligibility service reports every detected policy violation rather than returning only a Boolean.

This distinction supports auditability and operational troubleshooting.

## 12. PostgreSQL Implementation

The PostgreSQL implementation stores stochastic models and simulation execution history in relational form.

### Relational architecture

The database follows this relationship:

`Stochastic Process → Process States → Transition Rules`

`Stochastic Process → Simulation Runs → State Observations`

`Experiment Batch → Experiment Results → Simulation Runs`

### Main tables

| Table | Purpose |
|---|---|
| `stochastic_process` | Defines stochastic processes |
| `process_state` | Stores possible states |
| `transition_rule` | Stores transition probabilities |
| `simulation_run` | Records individual simulation executions |
| `state_observation` | Records chronological state observations |
| `experiment_batch` | Defines Monte Carlo experiment groups |
| `experiment_result` | Stores experiment outcomes |

### Referential integrity

Primary keys identify database records.

Foreign keys enforce relationships between processes, states, transition definitions and simulation executions.

Unique constraints prevent duplicate state definitions and duplicate transitions for the same source-destination pair.

Check constraints enforce:

- Probability bounds.
- Non-negative execution counts.
- Valid lifecycle statuses.
- Valid experiment configuration.
- Chronological consistency.

### Transition validation

The `validate_transition_distribution()` function checks whether every state has an outgoing probability distribution that sums to one.

A deferred constraint trigger checks transition distributions at transaction commit.

This permits multiple transition records to be inserted in one transaction before the complete distribution is validated.

The separate state-ownership trigger prevents transitions from connecting states belonging to unrelated processes.

An absorbing-state trigger checks that a declared absorbing state has the correct self-transition when transition definitions already exist.

### Simulation execution

The `simulate_markov_chain()` function performs the following operations:

1. Validates the initial state.
2. Acquires a transaction-level advisory lock for the process.
3. Validates transition distributions.
4. Creates a simulation run.
5. Records the initial state.
6. Generates random transition values.
7. Selects the next state according to cumulative probabilities.
8. Records every observation.
9. Stops when an absorbing state is reached or the maximum step count is exhausted.
10. Updates the final simulation status.

The function returns the generated run identifier.

The maximum-step constraint prevents an unbounded simulation loop.

### Monte Carlo execution

The `experiment_batch` table defines the experiment configuration.

The `execute_experiment_batch()` procedure executes the configured number of simulations.

Each experiment receives a separate seed derived from the batch seed.

The results table stores:

- Experiment identifier.
- Simulation run.
- Target-state outcome.
- Absorption time when the target is reached.

### Reporting

The database provides views and analytical queries for:

- Transition distributions.
- Simulation summaries.
- Empirical state frequencies.
- Empirical transition probabilities.
- Mean simulation length.
- Target-state frequency.
- Absorption statistics.

Window functions and common table expressions support transition-frequency analysis.

Indexes support process-based retrieval, state lookup and chronological observation access.

### Transaction behavior

The simulation function participates in the caller's transaction.

An exception propagates to the caller, allowing the transaction to roll back rather than silently retaining a partially completed run.

The advisory lock coordinates simulations against concurrent changes to a process's transition definitions.

The lock is transaction-scoped and does not replace database permissions or a separate model-versioning strategy.

### Reproducibility limitation

PostgreSQL's `setseed()` controls session-level pseudorandom behavior.

It is not a complete independent random-stream management system.

The SQL implementation demonstrates seeded simulation within a PostgreSQL execution context, but does not promise identical random sequences across PostgreSQL versions, different execution environments or concurrent session arrangements.

The schema also assumes a single active transition configuration per process. A production system requiring historical reproducibility should introduce immutable model versions and associate every simulation run with its exact transition-matrix version.

## 13. Relationship Between the Implementations

The five source files approach the same mathematical domain from different engineering perspectives.

| Implementation | Primary perspective | Distinctive capability |
|---|---|---|
| Python | Mathematical simulation | Validation, statistical estimation and numerical iteration |
| JavaScript | Event-driven execution | Events, asynchronous execution and cancellation |
| C++17 | Efficient domain modeling | Typed states, transition graph and Monte Carlo engine |
| Java 17 | Enterprise architecture | Immutable domain types, services and policy evaluation |
| PostgreSQL | Persistent stochastic workflow | Relational storage, integrity enforcement and analytical reporting |

All implementations support the central idea of stochastic state evolution.

Their internal representations differ because their engineering objectives differ.

## 14. Important Mathematical and Computational Distinctions

### Randomness versus uncertainty

Randomness describes the probabilistic mechanism used to generate outcomes.

Uncertainty also includes incomplete knowledge about the actual transition probabilities.

A simulation can accurately implement a specified probability model while the model itself remains uncertain.

### Theoretical probability versus empirical frequency

The transition matrix contains theoretical probabilities.

Simulation observations produce empirical frequencies.

For sufficiently large samples under suitable assumptions, empirical frequencies can approach their theoretical probabilities.

Finite experiments will generally exhibit sampling variation.

### State distribution versus sample path

A state distribution describes probabilities across all possible states at a specified time.

A sample path describes one realized sequence of states.

The Python stationary-distribution method operates on probability distributions.

The simulation methods operate on individual sample paths.

### Absorbing state versus low-probability state

A low-probability transition is still possible.

An absorbing state has a probability of one of remaining in itself and zero probability of leaving.

These concepts must not be treated as interchangeable.

### Discrete versus continuous time

The implementations use discrete-time processes.

A continuous-time Markov chain uses transition rates rather than a discrete transition matrix.

Its evolution is commonly described using a generator matrix \(Q\).

For continuous-time processes:

\[
P(t)=e^{Qt}
\]

The current implementations do not implement continuous-time simulation.

## 15. Performance Considerations

The principal computational costs are:

| Operation | Complexity |
|---|---|
| Transition matrix validation | \(O(n+m)\) |
| One transition using cumulative probabilities | \(O(d)\) |
| Simulation of \(T\) transitions | \(O(Td)\) |
| Monte Carlo with \(N\) experiments | \(O(NTd)\) |
| Dense matrix-vector multiplication | \(O(n^2)\) |
| Sparse matrix-vector multiplication | \(O(m)\) |

Where:

- \(n\) is the number of states.
- \(m\) is the number of defined transitions.
- \(d\) is the number of outgoing transitions for a state.
- \(T\) is the maximum simulation horizon.
- \(N\) is the experiment count.

For large sparse Markov chains, adjacency-list representations are generally more memory-efficient than dense transition matrices.

For very large Monte Carlo workloads, independent experiment batches can be distributed across workers.

Care must be taken to assign independent random streams to parallel workers.

## 16. Validation, Security and Failure Handling

The implementations enforce important configuration and execution constraints.

### Validation rules

- Probabilities must be finite.
- Probability values must lie between zero and one.
- Transition distributions must sum to one.
- Every destination must be a defined state.
- Initial states must belong to the selected model.
- Simulation horizons must be non-negative.
- Absorbing states must have valid self-transition definitions.

### Failure scenarios

| Failure condition | Expected handling |
|---|---|
| Invalid probability | Reject model configuration |
| Unknown state | Reject simulation |
| Missing transition | Reject model validation |
| Invalid simulation horizon | Reject execution |
| Invalid target state | Reject absorption analysis |
| Reached absorbing state | Stop simulation |
| Maximum horizon reached | Return finite-horizon result |
| File-writing failure | Propagate execution error |
| Database constraint violation | Reject transaction |
| Simulation exception | Roll back caller transaction |

### Security considerations

Stochastic simulations do not automatically provide secure randomness.

The pseudorandom generators in these implementations are designed for repeatability and simulation rather than cryptographic protection.

For security-sensitive applications:

- Use cryptographically secure random generators where appropriate.
- Restrict database access to authorized roles.
- Protect stored simulation data.
- Validate external model configurations.
- Prevent unauthorized transition-matrix modification.
- Maintain model-version and execution audit records.
- Apply resource limits to expensive simulations.

## 17. Practical Applications

| Application | States | Stochastic mechanism |
|---|---|---|
| Weather modeling | Sunny, cloudy, rainy | Markov transitions |
| Equipment reliability | Operational, degraded, failed | Absorbing Markov chain |
| Financial movement | Price levels or return categories | Random walk or Markov model |
| Customer behavior | Visitor, active, inactive | State transitions |
| Network monitoring | Normal, congested, unavailable | Markov chain |
| Inventory analysis | Stock levels | Random walk and state transitions |
| Disease progression | Health categories | Multistate Markov process |
| Queueing systems | Number of customers | Birth-death process |

These applications require domain-specific assumptions and validated transition probabilities.

A simple Markov model should not be assumed to capture every relevant dependency in a real-world system.

## 18. Limitations of the Implementations

The five implementations focus on discrete-time finite-state processes.

They do not provide a complete stochastic modeling platform.

Specific limitations include:

- No continuous-time Markov chain engine.
- No general Brownian motion implementation.
- No Gaussian process implementation.
- No hidden Markov model inference.
- No Bayesian transition-probability estimation.
- No automatic model fitting from historical observations.
- No statistical hypothesis-testing framework.
- No advanced variance-reduction techniques.
- No formal proof of convergence for numerical stationary-distribution estimation.
- No automatic identification of non-ergodic chains.

The Monte Carlo confidence intervals use the normal approximation and may be inaccurate with very small sample sizes or probabilities close to zero or one.

The SQL database does not provide immutable model-version snapshots.

The JavaScript event engine uses an in-memory execution model and does not persist intermediate events independently.

These limitations define the intended scope: an executable study of random walks, Markov chains, state transitions, absorption and simulation-based probability estimation.
