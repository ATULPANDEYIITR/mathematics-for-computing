# Advanced Recurrences: Divide and Conquer, Recursion Trees, and the Master Theorem

## Technical scope

A recurrence describes a quantity in terms of smaller instances of the same problem. In algorithm analysis, that quantity is usually the number of operations or the running time of an algorithm.

Divide-and-conquer algorithms solve a problem by dividing it into smaller subproblems, solving those subproblems recursively, and combining their results. Their costs often follow the recurrence

\[
T(n)=aT(n/b)+f(n)
\]

where:

- \(n\) is the input size.
- \(a\) is the number of recursive subproblems.
- \(b>1\) is the factor by which the input size shrinks.
- \(f(n)\) represents the work performed outside the recursive calls.
- \(T(1)\) specifies the base-case cost.

The recurrence is a model of algorithmic work. It does not automatically represent elapsed time on a parallel computer, where scheduling, network communication, resource contention, and unequal task durations can change observed performance.

This collection examines recurrence evaluation, recursion-tree analysis, asymptotic classification, numerical validation, and the implementation choices needed to analyze such models reliably.

## Recurrence structure and its interpretation

The parameters \(a\), \(b\), and \(f(n)\) describe different aspects of an algorithm.

| Component | Meaning | Example |
|---|---|---|
| \(a\) | Number of recursive calls | Merge sort makes two recursive calls. |
| \(b\) | Input shrink factor | Each merge-sort subproblem has approximately half the original input size. |
| \(f(n)\) | Nonrecursive work | Merging two sorted halves requires linear work. |
| \(T(1)\) | Cost of a base case | A single-element input can be handled in constant time. |

Merge sort is commonly modeled as

\[
T(n)=2T(n/2)+\Theta(n)
\]

Binary search follows

\[
T(n)=T(n/2)+\Theta(1)
\]

A recurrence with quadratic nonrecursive work,

\[
T(n)=2T(n/2)+\Theta(n^2),
\]

has a different asymptotic structure even though its branching factor and shrink factor are identical to those of merge sort.

The recursive-call structure alone is insufficient to determine complexity. The local work \(f(n)\) must also be analyzed.

## Recursion trees

A recursion tree expands a recurrence into levels. Each node represents a subproblem, and the cost associated with that node is the work performed outside its recursive descendants.

For

\[
T(n)=2T(n/2)+n,
\]

the root contributes \(n\) units of work. The next level contains two nodes, each processing approximately \(n/2\) elements. Its aggregate work is therefore

\[
2(n/2)=n.
\]

The same pattern continues while the input sizes remain evenly divisible. Each internal level contributes approximately \(n\), and the tree has logarithmic depth.

Consequently, the total work is

\[
T(n)=\Theta(n\log n).
\]

A recursion tree provides a direct explanation for the result: there are logarithmically many levels, and each level contributes linear work.

### Tree depth and node count

For an idealized recurrence with \(a\) children per node and a shrink factor of \(b\), the number of nodes at depth \(i\) is

\[
a^i.
\]

The subproblem size at that depth is approximately

\[
\frac{n}{b^i}.
\]

The recursion reaches constant-size subproblems when

\[
\frac{n}{b^i}\approx 1,
\]

which gives a depth of approximately

\[
\log_b n.
\]

The number of leaves is approximately

\[
a^{\log_b n}=n^{\log_b a}.
\]

This quantity becomes central to the Master Theorem because it describes the order of the total contribution from the leaves when base-case costs are constant.

### Why level costs matter

The number of nodes is not the same as the amount of work. If every node at a level has subproblem size \(m\), and each node performs \(f(m)\) local work, then the aggregate cost of the level is approximately

\[
a^i f(n/b^i).
\]

Summing the costs across all levels produces the total cost. This sum can be dominated by the leaves, distributed evenly across levels, or dominated by the root and other upper levels.

The Python and C++ implementations expose the per-level quantities separately. The JavaScript implementation provides a complementary representation suitable for asynchronous workload analysis. The Java implementation models each recurrence as a validated workload policy.

## The Master Theorem

For the standard recurrence

\[
T(n)=aT(n/b)+\Theta(n^p),
\]

define the critical exponent

\[
c=\log_b a.
\]

The comparison between \(p\) and \(c\) determines which contribution dominates under the theorem's assumptions.

### Case 1: Recursive leaves dominate

When

\[
p<\log_b a,
\]

the standard Master Theorem gives

\[
T(n)=\Theta(n^{\log_b a}).
\]

The nonrecursive work grows more slowly than the aggregate contribution associated with the leaves.

For example,

\[
T(n)=4T(n/2)+\Theta(n)
\]

has critical exponent \(\log_2 4=2\). The linear combine cost is asymptotically smaller than the quadratic leaf contribution, so the solution is

\[
T(n)=\Theta(n^2).
\]

### Case 2: Each level contributes equally

When

\[
p=\log_b a,
\]

the basic theorem gives

\[
T(n)=\Theta(n^p\log n).
\]

Merge sort is a representative example:

\[
T(n)=2T(n/2)+\Theta(n).
\]

Here, the critical exponent is one, and the local work is linear. Each level contributes linear work, and there are logarithmically many levels.

### Case 3: Nonrecursive work dominates

When

\[
p>\log_b a,
\]

the usual polynomial form of the Master Theorem gives

\[
T(n)=\Theta(n^p)
\]

provided the required regularity condition holds.

For a common formulation, the condition requires some constant \(q<1\) such that, for sufficiently large \(n\),

\[
a f(n/b)\le qf(n).
\]

This condition prevents the recursive contribution from growing so quickly that the expected dominance of \(f(n)\) fails.

For example,

\[
T(n)=2T(n/2)+\Theta(n^2)
\]

has a quadratic nonrecursive cost and a critical exponent of one. The regularity condition holds for the usual quadratic cost function, giving

\[
T(n)=\Theta(n^2).
\]

A program that labels a recurrence as a Case 3 candidate must not imply that the regularity condition has been proved. The supplied implementations distinguish the candidate classification from the assumptions needed for the conclusion.

## Polynomial-logarithmic extensions

Some algorithms have nonrecursive work of the form

\[
f(n)=\Theta(n^p\log^k n).
\]

When \(p=\log_b a\) and \(k\ge 0\), a standard extended form yields

\[
T(n)=\Theta(n^p\log^{k+1}n).
\]

For example,

\[
T(n)=2T(n/2)+\Theta(n\log^2 n)
\]

has solution

\[
T(n)=\Theta(n\log^3 n).
\]

The additional logarithmic factor comes from summing the contributions across the recursion levels.

The Python implementation includes an extended classifier for nonnegative logarithmic powers. It deliberately does not claim to cover arbitrary functions, negative logarithmic powers, oscillating costs, or every extended version of the theorem.

## Python implementation

The Python program combines executable recurrence models with analytical classification.

### Recurrence model

The `Recurrence` data class records the branching factor, shrink factor, local-cost function, and base-case cost. Its validation rules reject invalid recurrence parameters and nonpositive input sizes.

The `cost` method evaluates an integer recurrence using memoization. Memoization avoids recomputing the same subproblem size in the evaluation model. The ceiling-based subproblem size defines a particular integer recurrence, which can differ in detail from the idealized asymptotic model.

The `tree_levels` method reports depth, node count, subproblem size, and aggregate combine work. Its purpose is to expose the cost distribution across levels rather than simply print a final complexity label.

### Classification and numerical checks

The `master_theorem` function compares the polynomial exponent with the critical exponent. It handles the three basic polynomial cases and identifies the regularity condition as a requirement for Case 3.

The `extended_master_theorem` function considers nonnegative logarithmic powers in the standard polynomial-logarithmic form.

The `substitution_check` function compares a computed recurrence cost with a proposed upper bound for selected input sizes. This is a debugging aid, not a mathematical proof. Testing finitely many inputs cannot establish an asymptotic bound for all sufficiently large inputs.

### Limitations

The script uses floating-point logarithms for exponent comparisons and integer operation counts for recurrence evaluation. These are different representations of the problem.

The integer recurrence uses a specific ceiling convention, whereas the tree model uses an idealized level structure. Small discrepancies are expected for non-power-of-two inputs. The script makes these modeling decisions visible instead of treating every computed value as a universal runtime prediction.

## JavaScript implementation

The JavaScript file focuses on recurrence models that can be integrated into asynchronous data-processing systems.

### Memoized evaluation

`RecurrenceModel` validates the recurrence parameters and stores computed values in a `Map`. The memoization key is the subproblem size, which is sufficient for this deterministic recurrence because every occurrence of the same size has the same cost.

JavaScript's `Number` type represents integers exactly only through `Number.MAX_SAFE_INTEGER`. The implementation checks computed costs and node counts before accepting them. Larger workloads require a different representation, such as `BigInt`, with corresponding changes to arithmetic and formatting.

### Tree reporting

The tree method records node counts and aggregate level work. `summarizeTree` converts these measurements into a report, while `displayTree` presents the levels as a table.

The parallel test-sharding example uses a branching factor of four and constant local scheduling overhead. It illustrates a workload in which the number of parallel tasks can grow quickly even when the local overhead per node remains constant.

The model does not equate task count with elapsed time. A real parallel service must also account for available workers, queueing, communication, synchronization, and task imbalance.

### Asynchronous evaluation

`processRecurrenceJobs` uses `Promise.all` to evaluate a collection of recurrence jobs through an asynchronous interface. The result ordering follows the input job ordering, not the order in which promises complete.

The current calculation is CPU-bound and synchronous once a job begins. Promises do not automatically make a CPU-heavy recurrence faster. Worker threads or separate processes would be needed to distribute substantial CPU computation across execution contexts.

## C++ case study: partition-and-combine processing

The C++ program models a distributed data-processing service with three workload profiles:

- **Parallel partition-and-combine:** two half-size tasks and linear local work.
- **Single-branch search:** one half-size task and constant local work.
- **Quadratic transformation:** two half-size tasks and quadratic local work.

The `RecurrenceEngine` encapsulates each recurrence definition and provides memoized cost evaluation and tree-level reporting.

### Arithmetic safety

The implementation checks unsigned addition and multiplication before evaluating large operation counts. This is important because integer overflow can otherwise produce a plausible-looking but incorrect cost.

The quadratic combine function also checks multiplication before calculating \(n^2\). Its validation protects the local-cost calculation, while the engine's checked arithmetic protects aggregation of child and local costs.

### Architecture and trade-offs

The model separates recurrence definitions from the evaluator. This allows a workload to change its branching factor, shrink factor, or local-cost function without changing the tree-reporting logic.

Memoization improves repeated cost evaluation when the same subproblem sizes recur. It does not eliminate the potentially large number of nodes in a fully expanded recursion tree. Exact evaluation may become expensive or exceed the supported integer range for large branching factors.

The classification function uses floating-point logarithms to calculate the critical exponent. Its result is an analytical classification, not an automatic proof of every theorem assumption.

The case study is useful for understanding algorithmic work in partitioned services. It is not a latency simulator: actual distributed execution requires measurements of parallelism, scheduling overhead, communication, and resource availability.

## Java implementation: workload policies and validated evaluation

The Java program uses explicit domain types to represent recurrence analysis.

`WorkloadPolicy` encapsulates the name, branching factor, shrink factor, local-cost function, and base-case cost. Its constructor validates the parameters before an evaluator can use them.

`CostEvaluator` performs memoized recurrence evaluation and creates an immutable list of `TreeLevel` records. Java records make the relationship between a tree level's measurements explicit, while `Math.addExact` and `Math.multiplyExact` detect arithmetic overflow.

### State and failure handling

A recurrence policy is immutable after construction. Evaluation state is held separately in the evaluator's memoization map. This separation makes the model easier to test and prevents a change to one workload's parameters from silently changing another workload.

The program rejects invalid input sizes and reports arithmetic overflow. The quadratic example demonstrates that a mathematically defined recurrence can still exceed the limits of a chosen machine representation.

### Enterprise relevance

A production analytics platform can associate each workload with a validated recurrence model, then compare predicted operation counts with observed execution metrics. Such estimates can inform capacity planning, but they must be calibrated against the actual implementation.

The Java implementation keeps analytical classification separate from measured execution. This prevents a theoretical asymptotic bound from being mistaken for a service-level latency guarantee.

## PostgreSQL implementation: recurrence definitions and observations

The SQL script stores recurrence models, tree-level measurements, and observed workload runs in separate relational tables.

### Relational structure

`recurrence_models` stores the recurrence parameters and the polynomial exponent of local work. Its check constraints reject invalid branching factors, shrink factors, and negative costs.

`tree_levels` stores one row per recurrence, input size, and depth. Its composite primary key prevents duplicate level records for the same model and input size. The foreign key ensures that every recorded level belongs to an existing recurrence model.

`observed_runs` stores operation counts, elapsed time, environment information, and execution timestamps. Keeping measured results separate from analytical predictions makes it possible to compare models against observations without confusing the two.

### Queries and indexing

The `recurrence_analysis` view computes the critical exponent using natural logarithms:

\[
\log_b a=\frac{\ln a}{\ln b}.
\]

It compares that exponent with the polynomial exponent and returns a classification and expected complexity form.

The tree aggregation query sums recorded level costs and reports tree depth. The observation query retrieves execution measurements by model and input size.

The index on `(recurrence_id, executed_at DESC)` supports queries that retrieve a model's most recent runs. The tree-level index supports queries filtered by input size and recurrence.

### Transactional behavior and integrity

The script creates the schema, inserts sample records, evaluates analytical classifications, and demonstrates constraint enforcement within a transaction.

The nested exception block catches the expected check-constraint violation for an invalid shrink factor. The invalid row is rejected without aborting the surrounding transaction.

The stored sample execution times and operation counts are illustrative. They are not measurements from a real distributed service, and they should not be used for capacity forecasts.

The SQL tree stores an idealized model of per-level work. For non-power-of-two input sizes, the rounding convention and the interpretation of uneven subproblems must be chosen consistently before the resulting aggregate is treated as an exact recurrence evaluation.

## Comparing the analytical methods

| Method | Primary purpose | Main limitation |
|---|---|---|
| Direct recurrence evaluation | Computes a defined cost for a selected input size. | Results depend on the exact integer recurrence and arithmetic representation. |
| Recursion tree | Explains how work is distributed across levels. | Uneven subproblems and rounding can complicate the idealized tree. |
| Master Theorem | Establishes asymptotic bounds for supported recurrence forms. | Its hypotheses must hold; not every recurrence matches its standard form. |
| Numerical bound checking | Finds counterexamples and implementation errors at tested sizes. | Finite testing cannot prove an asymptotic bound. |
| Observed performance analysis | Measures actual behavior in an implementation or environment. | Measurements include implementation and system effects beyond the mathematical recurrence. |

These methods answer different questions. A recurrence evaluator calculates a defined model, a tree explains its structure, the Master Theorem provides a mathematical asymptotic result, and empirical measurements characterize an actual system.

## Common analytical errors

### Confusing depth with total work

A tree can have logarithmic depth while containing a polynomial number of nodes. Binary search has one recursive child per level, so its total work is logarithmic. A recurrence with many children can have the same depth but substantially greater total work.

### Ignoring local work

Two recurrences with the same values of \(a\) and \(b\) can have different solutions because their \(f(n)\) terms differ. Always include partitioning, merging, copying, aggregation, or other nonrecursive operations when those costs are part of the algorithm.

### Applying Case 3 without checking regularity

The inequality \(p>\log_b a\) identifies the expected combine-dominated case for a standard polynomial recurrence, but the theorem's regularity assumptions still matter. An implementation should not label a candidate as a proven bound without checking those assumptions.

### Treating numerical agreement as proof

An observed pattern over several input sizes can support a hypothesis, but it cannot establish a general asymptotic result. A proof requires mathematical reasoning about the recurrence and its assumptions.

### Ignoring arithmetic and model boundaries

Integer overflow, floating-point rounding, ceiling division, base-case definitions, and non-power-of-two input sizes can affect computed examples. These are implementation concerns separate from asymptotic analysis, but they matter when using software to investigate recurrence behavior.

## Performance and production considerations

Recurrence analysis helps explain operation growth, but it does not by itself determine wall-clock performance or memory consumption.

A complete performance model may need to consider:

- The cost of creating and scheduling recursive tasks.
- The number of tasks that can run concurrently.
- Communication and synchronization between subtasks.
- Unequal subproblem sizes and unbalanced recursion.
- Additional memory allocated at each level.
- The costs of caching, memoization, and intermediate results.
- The limits of integer and floating-point representations.

For sequential algorithms, the recurrence commonly models total work. For parallel algorithms, total work and critical-path depth should be distinguished. A recurrence with many independent children may expose substantial parallelism while still requiring significant total work.

The appropriate analytical method depends on the question being investigated. Use recursion trees to understand the source of the cost, the Master Theorem when its assumptions apply, exact recurrence evaluation for defined finite models, and empirical measurements when the behavior of a real implementation is the concern.
