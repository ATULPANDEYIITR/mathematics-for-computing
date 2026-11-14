# Advanced Probability: Martingales, Stationary Distributions, Ergodicity and Stochastic Modeling

## Mathematical Scope

This project develops a computational framework for studying discrete-time stochastic processes, with particular emphasis on finite-state Markov chains, stationary probability distributions, ergodicity and martingales.

A stochastic process is a sequence of random variables defined on a probability space:

\[
X_0,X_1,X_2,\ldots
\]

The process describes the evolution of a random system over time. Its behavior is determined by the underlying probability structure, transition mechanisms and information available at each time.

The implementations use a three-state weather process as their principal example:

- Sunny
- Cloudy
- Rainy

The weather example provides a consistent transition model for comparing theoretical probabilities, numerical calculations and simulated observations.

## Mathematical Foundations

### Probability distributions and expectation

A discrete random variable \(X\) has probability mass function:

\[
p(x)=P(X=x)
\]

The probabilities satisfy:

\[
p(x)\geq 0
\]

and

\[
\sum_x p(x)=1
\]

The expectation of a discrete random variable is:

\[
E[X]=\sum_x xp(x)
\]

Its variance is:

\[
Var(X)=E[(X-E[X])^2]
\]

The Python implementation includes reusable functions for normalization, categorical sampling, expectation and variance.

The other implementations concentrate on stochastic transition systems and their computational analysis.

### Stochastic processes

A stochastic process represents a collection of random variables indexed by time.

Different processes are distinguished by their dependence structures, state spaces and transition mechanisms.

Important categories include:

| Process | Main characteristic |
|---|---|
| Independent process | Observations are independent |
| Markov process | Future behavior depends on the present state |
| Stationary process | Joint distributions remain invariant under time shifts |
| Martingale | Conditional future expectation equals the present value |
| Random walk | Successive changes follow a specified random increment distribution |

These categories describe different mathematical properties. A process can possess more than one property.

## Markov Chains

### Definition

A discrete-time Markov chain satisfies the Markov property:

\[
P(X_{n+1}=j\mid X_n=i,X_{n-1},\ldots,X_0)
=
P(X_{n+1}=j\mid X_n=i)
\]

The current state contains all information from the past needed to determine the conditional distribution of the next state.

For a finite-state Markov chain, transition probabilities are represented by a matrix:

\[
P=
\begin{bmatrix}
p_{11}&p_{12}&\cdots&p_{1n}\\
p_{21}&p_{22}&\cdots&p_{2n}\\
\vdots&\vdots&\ddots&\vdots\\
p_{n1}&p_{n2}&\cdots&p_{nn}
\end{bmatrix}
\]

Each entry represents:

\[
p_{ij}=P(X_{t+1}=j\mid X_t=i)
\]

Every entry must be nonnegative, and every row must sum to one:

\[
\sum_jp_{ij}=1
\]

The matrix is therefore row-stochastic.

### Weather transition model

The implementations use:

| Current state | Sunny | Cloudy | Rainy |
|---|---:|---:|---:|
| Sunny | 0.70 | 0.20 | 0.10 |
| Cloudy | 0.25 | 0.50 | 0.25 |
| Rainy | 0.20 | 0.30 | 0.50 |

For example:

\[
P(X_{t+1}=\text{Rainy}\mid X_t=\text{Sunny})=0.10
\]

The model represents a conditional transition mechanism, not a claim about actual meteorological frequencies.

### Distribution evolution

Let the initial probability distribution be a row vector:

\[
\pi_0=
\begin{bmatrix}
p_1&p_2&\cdots&p_n
\end{bmatrix}
\]

The distribution after one transition is:

\[
\pi_1=\pi_0P
\]

After \(k\) transitions:

\[
\pi_k=\pi_0P^k
\]

This relationship is implemented in all four programming-language models.

### Transition simulation

A simulated transition selects a destination state according to the probability distribution associated with the current state.

The procedure is:

1. Read the current state.
2. Obtain its transition probabilities.
3. Generate a random value.
4. Select the destination using cumulative probabilities.
5. Record the transition.
6. Continue from the destination state.

Simulation produces an individual realization of the stochastic process.

It does not directly calculate the theoretical probability distribution.

## Stationary Distributions

### Definition

A stationary distribution is a probability vector that remains unchanged after applying the transition matrix:

\[
\pi P=\pi
\]

It also satisfies:

\[
\sum_i\pi_i=1
\]

and

\[
\pi_i\geq0
\]

The stationary distribution describes an invariant probability distribution of the Markov chain.

It is not automatically the distribution reached from every initial condition. That stronger convergence property requires additional assumptions.

### Power iteration

The implementations estimate stationary distributions through repeated matrix multiplication:

\[
\pi^{(k+1)}=\pi^{(k)}P
\]

The computation begins with a uniform probability distribution.

Convergence is measured using the maximum absolute difference:

\[
\epsilon_k=
\max_i
|\pi_i^{(k+1)}-\pi_i^{(k)}|
\]

The calculation stops when:

\[
\epsilon_k<\epsilon
\]

where \(\epsilon\) is the numerical tolerance.

The final distribution is also checked against the stationary equation.

A small residual indicates numerical agreement with the invariant-distribution equation.

### Important distinction

A stationary distribution and convergence to a stationary distribution are separate concepts.

A periodic irreducible chain can possess a stationary distribution while ordinary power iteration oscillates instead of converging.

The implementations explicitly report non-convergence instead of incorrectly presenting an intermediate iteration as a converged solution.

### Long-run rewards

Suppose each state has an associated reward:

\[
r(1),r(2),\ldots,r(n)
\]

For a chain with stationary distribution \(\pi\), the stationary expected reward is:

\[
E_\pi[r(X)]
=
\sum_i\pi_i r(i)
\]

The weather model uses state rewards:

| State | Reward |
|---|---:|
| Sunny | 100 |
| Cloudy | 60 |
| Rainy | 20 |

The expected long-run reward is calculated by multiplying each reward by its stationary probability.

For an irreducible positive recurrent chain, the stationary distribution also describes the long-run proportion of time spent in each state under the ergodic theorem.

## Irreducibility, Periodicity and Ergodicity

These concepts describe different properties of a Markov chain.

### Irreducibility

A Markov chain is irreducible if every state can be reached from every other state with positive probability in some finite number of transitions.

For states \(i\) and \(j\), this means:

\[
\exists n\geq0:
(P^n)_{ij}>0
\]

Irreducibility is a communication property.

The implementations represent the chain as a directed graph:

- Vertices represent states.
- Directed edges represent positive-probability transitions.
- Graph reachability determines whether states communicate.

Breadth-first search is used to examine reachability.

For a chain with \(n\) states, a single graph traversal has complexity:

\[
O(n^2)
\]

when the transition matrix is examined directly.

Checking reachability from every state has complexity:

\[
O(n^3)
\]

for a dense matrix representation.

### Periodicity

The period of a state is:

\[
d(i)=\gcd\{n\geq1:(P^n)_{ii}>0\}
\]

In an irreducible chain, every state has the same period.

A chain is aperiodic when:

\[
d(i)=1
\]

An irreducible chain with period greater than one is periodic.

The implementations calculate the period using graph distances and the greatest common divisor of transition-distance differences.

### Ergodicity

For a finite-state Markov chain, irreducibility and aperiodicity imply the existence of a unique stationary distribution and convergence toward it from every initial distribution.

A finite irreducible chain is positive recurrent automatically.

Under these conditions:

\[
\lim_{n\to\infty}P^n_{ij}=\pi_j
\]

The long-run empirical frequency of state \(j\) also converges to its stationary probability under the standard ergodic theorem.

The weather model is irreducible because all states communicate. It is aperiodic because every state has a positive self-transition probability.

### Comparison of chain structures

| Property | Ergodic weather model | Periodic model | Absorbing model |
|---|---|---|---|
| Irreducible | Yes | Yes | No |
| Aperiodic | Yes | No | Not applicable to the whole chain |
| Unique stationary distribution | Yes | Yes | Yes for the supplied absorbing model |
| Power iteration convergence | Yes | Not guaranteed | May depend on initialization and structure |
| Convergence from every initial distribution | Yes | Not in ordinary discrete time | Yes for the supplied absorbing model |

The periodic example alternates deterministically between two states:

\[
A\rightarrow B\rightarrow A
\]

Its period is two.

Its stationary distribution is:

\[
\pi=(0.5,0.5)
\]

Yet a distribution concentrated entirely on state \(A\) alternates between the two states and does not converge to the stationary distribution at each individual time step.

The absorbing example contains a transient state and an absorbing state. It illustrates why irreducibility must not be assumed for every stochastic model.

## Martingales

### Definition

A martingale is a stochastic process:

\[
M_0,M_1,M_2,\ldots
\]

adapted to a filtration:

\[
\mathcal F_0\subseteq
\mathcal F_1\subseteq
\mathcal F_2\subseteq\cdots
\]

It satisfies three conditions:

**Adaptation**

\[
M_n\text{ is }\mathcal F_n\text{-measurable}
\]

**Integrability**

\[
E[|M_n|]<\infty
\]

**Conditional expectation**

\[
E[M_{n+1}\mid\mathcal F_n]=M_n
\]

The filtration represents the information available up to each time.

A martingale therefore has no predictable conditional increase or decrease based on the information currently available.

### Martingale difference sequence

A martingale difference sequence is:

\[
D_{n+1}=M_{n+1}-M_n
\]

Its defining conditional expectation is:

\[
E[D_{n+1}\mid\mathcal F_n]=0
\]

This is the mechanism implemented in the Python, JavaScript, C++17 and Java 17 files.

### Constructing a martingale from a Markov chain

Let the transition-dependent reward be:

\[
R(X_n,X_{n+1})
\]

Define its conditional expectation:

\[
g(i)=
\sum_jP_{ij}R(i,j)
\]

The centered increment is:

\[
D_{n+1}
=
R(X_n,X_{n+1})-g(X_n)
\]

Define:

\[
M_0=0
\]

and:

\[
M_n=\sum_{k=0}^{n-1}D_{k+1}
\]

Then:

\[
E[D_{n+1}\mid\mathcal F_n]=0
\]

Consequently:

\[
E[M_{n+1}\mid\mathcal F_n]=M_n
\]

The implementations calculate conditional reward means directly from the transition matrix and verify that the probability-weighted expected increment is zero for each state.

### Martingale versus ordinary random walk

A random walk is not automatically a martingale.

For a random walk:

\[
S_n=S_0+\sum_{k=1}^{n}Y_k
\]

the martingale property requires the appropriate conditional mean of each increment to be zero:

\[
E[Y_{n+1}\mid\mathcal F_n]=0
\]

If the increments have a nonzero predictable conditional mean, centering them is necessary.

The Markov-chain construction provides this centering mechanism.

### Martingale limitations

A martingale does not imply:

- Independent increments.
- Identically distributed increments.
- Constant variance.
- Stationarity.
- Almost-sure convergence without further assumptions.

The conditional expectation property is the defining requirement.

## Stationarity: A Separate Concept

Stationarity refers to invariance of probability distributions under time shifts.

For a strictly stationary process:

\[
(X_{t_1},\ldots,X_{t_k})
\]

has the same joint distribution as:

\[
(X_{t_1+h},\ldots,X_{t_k+h})
\]

for every admissible shift \(h\).

A weakly stationary process requires:

1. Constant finite mean.
2. Finite variance.
3. Autocovariance depending only on the time difference.

A Markov chain initialized with its stationary distribution is strictly stationary when its transition mechanism is time-homogeneous.

A chain that has not been initialized with its stationary distribution can still possess a stationary distribution without its observed process being stationary.

Stationarity of a distribution must therefore be distinguished from stationarity of a particular realization.

## Stochastic Simulation and Numerical Estimation

### Monte Carlo estimation

A stochastic simulation generates sample paths from a probability model.

For a trajectory:

\[
X_0,X_1,\ldots,X_N
\]

the empirical state frequency is:

\[
\widehat{\pi}_i=
\frac{1}{N+1}
\sum_{t=0}^{N}
\mathbf 1(X_t=i)
\]

For an ergodic finite-state Markov chain:

\[
\widehat{\pi}_i\rightarrow\pi_i
\]

almost surely as the simulation length increases.

The simulation therefore provides an empirical approximation to the theoretical stationary distribution.

### Error measurement

The implementations calculate maximum absolute distribution error:

\[
E_{\max}=
\max_i|\widehat{\pi}_i-\pi_i|
\]

The total variation distance is:

\[
d_{TV}(\pi,\widehat{\pi})
=
\frac12\sum_i|\pi_i-\widehat{\pi}_i|
\]

Both metrics compare theoretical and empirical distributions.

They measure different aspects of distributional discrepancy.

### Reproducibility

A fixed random seed allows a stochastic experiment to be repeated under the same random-number generator and implementation.

The Python implementation uses `random.Random`.

The JavaScript implementation uses a deterministic Mulberry32 generator.

The C++17 implementation uses `std::mt19937_64`.

The Java 17 implementation uses `SplittableRandom`.

Different languages and generators are not expected to produce identical random sequences from the same numerical seed.

Reproducibility within each implementation is the relevant requirement.

### Simulation versus exact computation

| Method | Purpose | Main limitation |
|---|---|---|
| Matrix multiplication | Exact distribution propagation up to numerical precision | Matrix operations become expensive for large state spaces |
| Stationary power iteration | Numerical stationary distribution | Periodicity can prevent convergence |
| Monte Carlo simulation | Empirical process behavior | Sampling variability |
| Graph reachability | Communication structure | Does not estimate transition probabilities |
| Martingale verification | Conditional mean identity | Does not establish independence or convergence |

## Implementation Architecture

The five source files implement different computational perspectives on the same mathematical domain.

### Python: Probability analysis and mathematical experimentation

The Python program provides the most direct mathematical interface.

Main components:

| Component | Responsibility |
|---|---|
| `MarkovChain` | Transition validation, distribution evolution and simulation |
| `StationaryResult` | Stationary solver output |
| `MartingaleAnalyzer` | Conditional means and martingale increments |
| `SimulationResult` | Empirical state and transition frequencies |
| `ChainClassification` | Structural classification |
| `compare_distributions` | Numerical comparison |

The implementation uses dataclasses, enumerations, dictionaries, tuples, sets and standard-library numerical functions.

Its graph algorithms use iterative traversal to avoid recursion-depth problems.

### JavaScript: Event-driven stochastic execution

The JavaScript implementation uses an event-driven architecture.

Its main components are:

| Component | Responsibility |
|---|---|
| `RandomGenerator` | Reproducible categorical sampling |
| `MarkovModel` | Immutable state and transition configuration |
| `MartingaleProcess` | Conditional reward centering |
| `OnlineStatistics` | Incremental visit and transition counts |
| `StochasticSimulator` | Asynchronous simulation and event publication |

The simulator emits:

- `started`
- `transition`
- `progress`
- `completed`
- `failed`

Simulation batches periodically yield control through `setImmediate`.

This avoids monopolizing the Node.js event loop during long simulations.

The model configuration is validated before execution.

### C++17: Numerical and graph-oriented computation

The C++ implementation emphasizes efficient data structures and explicit computational control.

Its main components include:

| Component | Responsibility |
|---|---|
| `MarkovChain` | Matrix validation and state transitions |
| `StationaryResult` | Numerical convergence reporting |
| `SimulationResult` | Trajectory and transition counts |
| `MartingaleAnalyzer` | Conditional reward calculations |
| `Classification` | Ergodicity classification |

The implementation uses:

- `std::vector` for matrices and distributions.
- `std::queue` for graph traversal.
- `std::gcd` for periodicity calculations.
- `std::discrete_distribution` for transition sampling.
- `std::mt19937_64` for reproducible random generation.
- Exceptions for invalid mathematical configurations.

### Java 17: Enterprise stochastic modeling

The Java implementation emphasizes domain separation, immutable results and service-oriented processing.

Its main components include:

| Component | Responsibility |
|---|---|
| `Transition` | Validated transition record |
| `MarkovModel` | Immutable probability model |
| `StationaryResult` | Stationary computation output |
| `MartingaleService` | Martingale validation and evaluation |
| `SimulationService` | Controlled stochastic execution |
| `SimulationReport` | Immutable simulation result |
| `ChainType` | Chain classification |
| `SimulationStatus` | Simulation lifecycle |

The transition model is built from explicit domain records rather than accepting an unstructured matrix as its only input.

The simulation service separates model configuration, execution and reporting.

### PostgreSQL: Relational stochastic modeling

The database implementation stores stochastic models and their observed behavior.

Its relational structure is:

    stochastic_models
          |
          v
      model_states
          |
          v
      transitions
          |
          +----------------------+
          |                      |
          v                      v
      simulations          probability analysis
          |
          v
    trajectory_observations
          |
          v
    martingale_observations
          |
          v
       reporting

The schema contains:

| Table | Purpose |
|---|---|
| `stochastic_models` | Model identity and lifecycle |
| `model_states` | State definitions and rewards |
| `transitions` | Directed transition probabilities |
| `simulations` | Simulation execution metadata |
| `trajectory_observations` | Observed state sequence |
| `martingale_observations` | Reward and centered increments |

The database includes:

- Primary and foreign keys.
- Unique constraints.
- Probability-range checks.
- Model-specific state relationships.
- Transition matrix validation.
- Activation procedures.
- Stationary distribution computation.
- Long-run reward calculation.
- Trajectory validation triggers.
- Simulation completion procedures.
- Reporting views.
- Transaction-based sample execution.

The stationary distribution function uses PL/pgSQL loops and array-based numerical calculations.

It checks transition row sums before performing power iteration.

The trajectory trigger verifies that every recorded transition is permitted by the model.

## Database Integrity and Operational Rules

### Probability integrity

A transition probability must satisfy:

\[
0\leq p_{ij}\leq1
\]

The sum of outgoing probabilities must satisfy:

\[
\sum_jp_{ij}=1
\]

The individual probability constraint is enforced through a table-level check.

The complete row-sum condition is enforced through the model activation procedure.

This distinction is necessary because an ordinary row-level `CHECK` constraint cannot validate the aggregate of multiple transition records.

### Model lifecycle

The database uses the following model statuses:

| Status | Meaning |
|---|---|
| Draft | Model configuration is being assembled |
| Validated | Model has passed validation |
| Active | Model is eligible for operational use |
| Retired | Model is no longer operational |

The supplied activation procedure accepts draft and validated models after verifying their transition matrices.

### Simulation lifecycle

A simulation follows:

    CREATED
       |
       v
    RUNNING
       |
       +----------+
       |          |
       v          v
    COMPLETED   FAILED

The completion procedure checks whether the number of recorded trajectory observations matches the requested number of transitions plus the initial state.

The trajectory trigger also checks model membership and transition feasibility.

### Transaction handling

The sample workflow inserts simulation metadata, records its initial state, inserts subsequent observations and completes the simulation within a transaction.

A failure during the workflow can be handled through transaction rollback.

The database's transaction ensures that the sample workflow does not leave a partially committed simulation when a statement fails.

## Important Edge Cases

### Invalid probability matrices

A matrix is invalid when:

- It is not square.
- It contains negative probabilities.
- It contains probabilities greater than one.
- A probability is not finite.
- A row does not sum to one.

All four programming-language implementations reject invalid matrices.

### Periodic chains

The alternating two-state example has period two.

It has a stationary distribution, but ordinary power iteration does not converge from the uniform distribution.

The implementation reports the failure to converge rather than incorrectly declaring the chain to have no stationary distribution.

### Reducible chains

The absorbing example contains a transient state and an absorbing state.

It illustrates the possibility of non-unique stationary distributions in more general reducible models.

The specific supplied absorbing model has a unique stationary distribution concentrated on its absorbing state.

### Impossible observed transitions

A trajectory cannot contain a transition whose probability is zero under the configured model.

The database trigger rejects such observations.

The programming-language implementations also validate transitions when processing martingale paths.

### Numerical precision

Floating-point calculations introduce rounding errors.

The implementations use configurable convergence tolerances and independent stationary residual calculations.

The PostgreSQL implementation uses double precision for iterative numerical calculations and numeric columns for stored transition probabilities and rewards.

### Simulation length

A short trajectory may produce an empirical distribution that differs substantially from its stationary distribution.

Longer trajectories generally improve estimation for an ergodic model, but observations are dependent.

The number of transitions is not equivalent to the number of independent observations.

## Computational Complexity

Let:

- \(n\) be the number of states.
- \(T\) be the number of simulated transitions.
- \(K\) be the number of stationary iterations.

For dense transition matrices:

| Operation | Time complexity |
|---|---|
| Transition matrix validation | \(O(n^2)\) |
| One distribution multiplication | \(O(n^2)\) |
| Stationary power iteration | \(O(Kn^2)\) |
| One graph traversal | \(O(n^2)\) |
| Irreducibility checking | \(O(n^3)\) |
| Period calculation after graph distances | \(O(n^2)\) |
| Stochastic simulation | \(O(Tn)\) with linear categorical selection |
| Empirical state counting | \(O(T+n)\) |

The current implementations favor clarity and explicit numerical validation.

For large sparse Markov chains, adjacency-list storage and sparse matrix multiplication can reduce memory and computational costs.

## Security and Reliability Considerations

The programs are mathematical simulation tools, not security-sensitive probability services.

Their operational safeguards include:

- Validation of externally supplied probabilities.
- Rejection of invalid state references.
- Explicit iteration limits.
- Reproducible simulation seeds.
- Immutable model configurations where appropriate.
- Exception handling.
- Numerical convergence reporting.
- Database foreign-key enforcement.
- Transactional simulation workflows.
- Validation of recorded transitions.

For production use, additional controls would be necessary when probability models are supplied by external users or stored in shared databases.

These include access restrictions, model-version tracking, audit records, concurrency control, input-size limits and protection against resource-intensive model configurations.

Random-number generator selection must also reflect the intended application. The supplied generators are appropriate for reproducible simulation experiments, not cryptographic security.

## Execution

### Python

Requirements:

- Python 3.10 or later.
- Standard library only.

Execute the complete Python source file using the Python interpreter.

### JavaScript

Requirements:

- Node.js 18 or later.
- No npm packages.

Execute the JavaScript source file using Node.js.

### C++17

Requirements:

- C++17-compatible compiler.
- Standard C++ library.

Compile with the C++17 language standard and execute the resulting program.

### Java 17

Requirements:

- JDK 17 or later.
- No third-party dependencies.

The source declares `AdvancedProbability` as its public class.

Compile and execute it using the Java 17 compiler and runtime.

### PostgreSQL

Requirements:

- PostgreSQL 14 or later.
- Permission to create schemas, tables, procedures, functions and triggers.

Execute the SQL script against a PostgreSQL database.

The script creates a dedicated schema and sample models. Its initial schema reset is destructive to an existing schema with the same name, so it should be executed in a dedicated learning or testing database.

## Learning Outcomes and Conceptual Distinctions

The implementations establish the following relationships:

| Concept | Mathematical or operational role |
|---|---|
| Probability distribution | Describes uncertainty over possible outcomes |
| Stochastic process | Describes random evolution over time |
| Markov property | Restricts dependence on historical information |
| Transition matrix | Encodes one-step conditional probabilities |
| Stationary distribution | Describes an invariant probability vector |
| Irreducibility | Describes communication among states |
| Periodicity | Describes restrictions on return times |
| Ergodicity | Supports long-run distributional convergence and frequency results |
| Martingale | Describes a process with unchanged conditional expectation |
| Martingale difference | Represents a zero conditional-mean increment |
| Monte Carlo simulation | Estimates behavior through generated sample paths |
| Numerical residual | Measures the accuracy of an approximate mathematical solution |

The central distinction is that stationary distributions describe invariant probability structures, ergodicity establishes conditions for long-run convergence and time-average behavior, and martingales describe conditional expectation dynamics.

These properties can coexist within the same stochastic system, but none should be substituted for another.
