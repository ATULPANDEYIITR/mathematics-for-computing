# Solving Recurrences: Iteration, Substitution, and Characteristic Equations

## Scope

A recurrence relation defines a quantity in terms of values at smaller input sizes or earlier states. Solving a recurrence means finding a form that describes the quantity without repeatedly evaluating every preceding state.

This project concentrates on three closely related techniques:

- **Iteration**, where the recurrence is repeatedly expanded until a recognizable sum or pattern appears.
- **Substitution**, where the recurrence is expanded into progressively deeper forms and the resulting algebraic pattern is identified and verified.
- **Characteristic equations**, where a linear homogeneous recurrence is converted into a polynomial equation whose roots determine the form of the solution.

The implementations also distinguish first-order recurrences, second-order recurrences, homogeneous and non-homogeneous terms, distinct characteristic roots, repeated roots, recurrence validation, and algorithmic evaluation strategies.

The examples use computational workloads, dependency growth, and Fibonacci-style sequences because these settings make the relationship between recurrence structure, closed form, and computational complexity explicit.

---

## Recurrence Structure

A first-order recurrence depends on one previous state. A typical form is

`T(n) = aT(n-1) + f(n)`

where `a` controls the contribution from the previous state and `f(n)` supplies new work at state `n`.

A second-order recurrence depends on two previous states:

`T(n) = aT(n-1) + bT(n-2) + f(n)`

The initial conditions are part of the mathematical definition. For a first-order recurrence, one initial value such as `T(0)` is normally sufficient. A second-order recurrence requires two independent initial values, commonly `T(0)` and `T(1)`.

The recurrence and its initial conditions must be considered together. The recurrence specifies the transition rule, while the initial values select one particular sequence from the family of possible solutions.

---

## Iteration

Iteration, also called repeated substitution or expansion, starts with the recurrence and repeatedly replaces the previous term.

Consider:

`T(n) = T(n-1) + n`

with `T(0) = 10`.

Expanding once gives:

`T(n) = T(n-2) + (n-1) + n`

Further expansion produces:

`T(n) = T(0) + 1 + 2 + ... + n`

The recurrence has therefore been converted into a summation. The known sum

`1 + 2 + ... + n = n(n+1)/2`

produces:

`T(n) = 10 + n(n+1)/2`

The Python implementation constructs this recurrence directly and compares every generated value against the derived closed form. The JavaScript implementation provides a substitution trace so the changing recurrence depth can be observed programmatically.

Iteration is especially useful when expansion exposes a familiar arithmetic, geometric, or polynomial sum.

---

## Geometric Growth Through Substitution

A recurrence such as

`T(n) = 2T(n-1) + 1`

behaves differently.

Repeated expansion gives:

`T(n) = 2^k T(n-k) + (2^(k-1) + ... + 2 + 1)`

Taking `k = n` reaches the base case:

`T(n) = 2^n T(0) + 2^n - 1`

For `T(0)=5`:

`T(n) = 6(2^n) - 1`

The important feature is that the contribution from the original state is multiplied by `2` at every expansion. The resulting geometric progression explains exponential growth directly.

The Python and JavaScript implementations calculate both the recurrence and the closed form, allowing the algebraic pattern to be validated rather than merely stated.

---

## First-Order Linear Recurrences

For the general recurrence

`T(n) = aT(n-1) + b`

with `a != 1`, repeated substitution produces:

`T(n) = a^nT(0) + b(1 + a + a^2 + ... + a^(n-1))`

Using the geometric-series identity:

`1 + a + ... + a^(n-1) = (a^n - 1)/(a - 1)`

gives:

`T(n) = a^nT(0) + b(a^n - 1)/(a - 1)`

The special case `a = 1` must be handled separately:

`T(n) = T(0) + bn`

because the geometric-series denominator would otherwise be zero.

This distinction is implemented explicitly in the Python, JavaScript, and Java programs. It is not treated as a minor arithmetic exception because it changes the mathematical form of the solution.

---

## Non-Homogeneous Recurrences

A recurrence is homogeneous when the recurrence contains only previous values of the unknown sequence. A non-homogeneous recurrence contains an additional forcing term.

For example:

`T(n) = 3T(n-1) + 4`

can be separated into:

`T(n) = T_h(n) + T_p(n)`

The associated homogeneous recurrence is:

`T_h(n) = 3T_h(n-1)`

For a constant forcing term, a constant particular solution can be tested:

`T_p(n) = k`

Substitution gives:

`k = 3k + 4`

so:

`k = -2`

The complete solution therefore has the form:

`T(n) = C(3^n) - 2`

The initial condition determines `C`.

The Java implementation models this decomposition through a dedicated closed-form solver. The SQL implementation stores the derivation method separately from the recurrence definition so that a non-homogeneous solution is not confused with a homogeneous characteristic-root solution.

---

## Characteristic Equations

For a second-order homogeneous recurrence:

`T(n) = pT(n-1) + qT(n-2)`

assume a solution of the form:

`T(n) = r^n`

Substitution gives:

`r^n = pr^(n-1) + qr^(n-2)`

After dividing by `r^(n-2)`:

`r^2 - pr - q = 0`

This polynomial is the **characteristic equation**.

Its roots determine the structure of the recurrence solution.

For:

`T(n) = 5T(n-1) - 6T(n-2)`

the characteristic equation is:

`r^2 - 5r + 6 = 0`

which factors as:

`(r-2)(r-3) = 0`

The roots are `2` and `3`.

Because the roots are distinct, the general solution is:

`T(n) = C1(2^n) + C2(3^n)`

The initial values determine `C1` and `C2`.

---

## Distinct Roots

For distinct roots `r1` and `r2`, the general second-order solution is:

`T(n) = C1(r1^n) + C2(r2^n)`

The constants satisfy:

`C1 + C2 = T(0)`

and

`C1r1 + C2r2 = T(1)`

The Python, JavaScript, C++, and Java implementations explicitly solve these equations rather than hard-coding the constants for one sequence.

This separation is important because the roots describe the family of possible solutions, while the initial conditions identify the particular sequence being studied.

---

## Repeated Characteristic Roots

A repeated root requires a different solution form.

Consider:

`T(n) = 4T(n-1) - 4T(n-2)`

The characteristic equation is:

`r^2 - 4r + 4 = 0`

which factors as:

`(r-2)^2 = 0`

There is only one distinct root, `r=2`, but it has multiplicity two.

The correct solution is:

`T(n) = (C1 + C2n)2^n`

The factor `n` is essential. Simply using `C1(2^n) + C2(2^n)` does not provide two independent solutions because both terms are multiples of the same sequence.

With `T(0)=2` and `T(1)=8`:

`C1 = 2`

and:

`8 = (2+C2)2`

so:

`C2 = 2`

The resulting sequence is:

`T(n) = 2(1+n)2^n`

The repeated-root case receives separate implementations in Python, JavaScript, C++, and Java because it is mathematically distinct from the distinct-root case.

---

## Fibonacci as a Characteristic-Equation Example

The Fibonacci recurrence is:

`F(n) = F(n-1) + F(n-2)`

with:

`F(0)=0`

and:

`F(1)=1`

Its characteristic equation is:

`r^2-r-1=0`

The roots are:

`phi = (1+sqrt(5))/2`

and:

`psi = (1-sqrt(5))/2`

The resulting closed form is:

`F(n) = (phi^n - psi^n)/sqrt(5)`

This is an important example because it connects recurrence solving to algorithmic complexity. A recurrence can be evaluated by directly generating every previous state, by memoizing recursive states, or by using matrix exponentiation.

---

## Evaluation Strategies and Complexity

Solving a recurrence mathematically and evaluating it computationally are related but distinct tasks.

For a recurrence whose states must be generated sequentially, iterative dynamic programming generally requires `O(n)` time.

Memoization also computes `O(n)` distinct states when every state from the base case through `n` is needed. It avoids repeated recursive work but retains a cache and recursive call structure.

Matrix exponentiation can reduce the number of matrix multiplications to `O(log n)` for suitable fixed-order linear recurrences. The Python, JavaScript, C++, and Java implementations demonstrate this technique for Fibonacci.

A characteristic closed form can appear to require only constant arithmetic for one requested `n`, but the practical cost depends on the numerical representation. Floating-point powers can lose precision for large values, while arbitrary-precision integers can preserve exact integer results at increased computational cost.

---

## Python Implementation

The Python program is the broadest mathematical implementation.

It contains:

- Generic iterative recurrence evaluation through `evaluate_recurrence`.
- Explicit additive and multiplicative recurrence examples.
- Expansion traces representing repeated substitution.
- A general first-order closed-form solver.
- Validation of first-order formulas against generated values.
- Characteristic-root calculations for quadratic equations.
- Coefficient solving for distinct characteristic roots.
- Separate handling of repeated roots.
- Non-homogeneous recurrence solutions with constant forcing.
- Polynomial forcing through the recurrence `T(n)=T(n-1)+n²`.
- Validation of second-order recurrence sequences.
- Comparison between naive recursive Fibonacci, memoization, iterative evaluation, and matrix exponentiation.
- Exact matrix calculations using Python integers.
- Assertions that detect discrepancies between recurrence evaluation and derived formulas.

The program is designed so that mathematical formulas are tested against executable recurrence generation.

---

## JavaScript Implementation

The JavaScript implementation emphasizes runtime-specific techniques while retaining the mathematical distinctions.

The generic recurrence evaluator accepts a transition function and an initial state. This allows recurrence definitions to be passed as executable behavior rather than embedding every recurrence into one large function.

The `RecurrenceEmitter` class provides an event-driven representation. It emits a `computed` event whenever a new recurrence state is generated and a `complete` event when the requested state has been reached. This is useful for recurrence visualizers, monitoring systems, and interactive computational workflows.

JavaScript's ordinary `Number` type is not sufficient for arbitrary exact integer recurrence values because integers above `2^53 - 1` cannot all be represented exactly. The program therefore includes a `BigInt` Fibonacci implementation.

Matrix exponentiation also uses `BigInt`, preserving exact integer Fibonacci values while demonstrating binary exponentiation.

---

## C++ Case Study

The C++ program models a repository-style build workload forecasting service.

A staged workload uses:

`T(n)=T(n-1)+n`

to represent additional work introduced by successive processing stages.

A branching workload uses:

`T(n)=3T(n-1)+2`

to demonstrate a non-homogeneous first-order recurrence.

A dependency-growth model uses:

`T(n)=5T(n-1)-6T(n-2)`

whose characteristic roots are `2` and `3`.

A repeated dependency factor uses:

`T(n)=4T(n-1)-4T(n-2)`

whose characteristic equation contains the repeated root `2`.

The C++ design separates recurrence models from sequence generation. `RecurrenceModel` defines the transition contract, while concrete classes provide recurrence-specific behavior.

The characteristic-equation implementation calculates roots and solves the constants for distinct roots. The repeated-root implementation explicitly uses the `(C1+C2n)r^n` form.

The validation engine checks generated second-order states against the recurrence coefficients. This provides a practical safeguard against indexing errors or incorrect transition logic.

The Fibonacci portion contrasts sequential evaluation with matrix exponentiation. Overflow is explicitly considered for `unsigned long long`, illustrating why mathematical recurrence growth must also be considered from a systems-programming perspective.

---

## Java Enterprise-Oriented Implementation

The Java implementation uses explicit domain types to separate recurrence definitions, generated results, characteristic roots, closed-form solutions, validation reports, and mathematical strategies.

`RecurrenceDefinition` represents the mathematical contract and initial conditions.

`RecurrenceEvaluator` performs state-by-state evaluation.

`CharacteristicEquation` isolates root calculation.

`ClosedFormSolver` contains distinct mathematical solution mechanisms for first-order, distinct-root, repeated-root, and constant-forcing cases.

`RecurrenceValidator` compares generated values with recurrence expectations and returns structured validation issues rather than relying only on printed output.

The Java implementation also uses immutable records for mathematical data such as characteristic roots, recurrence definitions, validation issues, and matrix values.

`BigInteger` is used for exact Fibonacci calculations because floating-point values are unsuitable for preserving arbitrary large integer recurrence values.

Streams are used only after recurrence states have been generated, where they provide useful aggregation operations such as average and maximum without changing the underlying recurrence mathematics.

---

## SQL Data Model

The PostgreSQL implementation treats recurrence analysis as a relational data domain.

`recurrence_definition` stores the recurrence order, coefficients, forcing term, initial conditions, and mathematical description. Check constraints prevent a first-order definition from being represented as though it required a second-order coefficient.

`evaluation_strategy` stores the computational strategy separately from the recurrence itself. This makes it possible to associate the same mathematical recurrence with different evaluation techniques and complexity characteristics.

`recurrence_value` stores individual states `T(n)`, together with expected values and validation status. The composite primary key `(recurrence_id, n)` prevents duplicate states for the same recurrence.

`characteristic_root` stores characteristic roots and their multiplicities. This is important because a repeated root represents a different solution structure from two distinct roots.

`closed_form_solution` records the derived solution form and the method used to obtain it. Iteration, characteristic equations, and non-homogeneous decomposition are represented as different derivation methods.

Indexes support searches by recurrence and state number and searches for invalid generated states.

---

## Database-Level Validation

The SQL script demonstrates that recurrence correctness can be checked directly against stored mathematical expectations.

For the distinct-root recurrence:

`T(n)=5T(n-1)-6T(n-2)`

with `T(0)=1` and `T(1)=4`, solving for the constants gives:

`T(n)=-2^n+2(3^n)`

The SQL script generates expected values from this expression and stores them alongside generated states.

A deliberately invalid state is inserted with a value that does not match the closed form. The validation report identifies it as a mismatch.

This distinction is useful in a data-processing environment: a recurrence definition describes the rule, a generated value records an observed or calculated state, and validation determines whether the state conforms to the rule.

---

## Transactional Behavior

The SQL script includes a transaction that inserts a temporary invalid state, queries it, and then performs `ROLLBACK`.

The transaction demonstrates that validation experiments can be isolated from the persistent dataset.

This is particularly useful when recurrence calculations are part of a larger database workflow where experimental calculations should not permanently alter validated mathematical records.

---

## Iteration Versus Closed Form

Iteration and closed form answer different practical questions.

Iteration is useful when:

- Every intermediate state is needed.
- The recurrence itself represents the natural computational process.
- The closed form is difficult to derive or unnecessary.
- Dynamic programming can reuse earlier states.

A closed form is useful when:

- Only a particular state is needed.
- The expression is mathematically tractable.
- The arithmetic representation provides sufficient precision.
- The formula exposes asymptotic growth directly.

For example, generating every Fibonacci state from `F(0)` to `F(100)` is straightforward. A matrix-power approach reduces the number of recurrence-state transitions needed to reach the requested index.

---

## Substitution and Characteristic Equations Are Not Interchangeable

Repeated substitution expands the recurrence itself. It is especially effective for first-order recurrences and recurrences whose expansions form recognizable sums or products.

Characteristic equations apply specifically to linear homogeneous recurrences of the appropriate constant-coefficient form.

For example:

`T(n)=2T(n-1)+1`

contains a forcing term and therefore cannot be solved by treating the entire recurrence as though it were homogeneous. The associated homogeneous recurrence can be solved separately, after which a particular solution accounts for the forcing term.

For:

`T(n)=5T(n-1)-6T(n-2)`

there is no forcing term, so the characteristic equation directly determines the homogeneous solution.

The methods therefore solve related problems but should not be applied indiscriminately.

---

## Common Mathematical Errors

A common mistake is to expand a recurrence correctly but stop before the base case has been substituted. A valid derivation must connect the expanded recurrence to a known initial condition.

Another error is losing coefficients during repeated substitution. In a recurrence such as `T(n)=2T(n-1)+1`, the constant terms form a geometric series rather than a simple count of `n` additions.

A frequent characteristic-equation error is using `r^n` without properly shifting the exponents before division. For a second-order recurrence, the expression must be divided by the smallest common power, resulting in a quadratic polynomial.

Repeated roots require the `n` multiplier. When a characteristic root has multiplicity two, the solution is `(C1+C2n)r^n`, not merely `(C1+C2)r^n`.

Initial conditions must also match the order of the recurrence. A second-order recurrence requires enough independent initial values to determine its constants.

---

## Numerical Considerations

Mathematical equality and machine arithmetic are not identical.

Floating-point implementations can accumulate rounding errors when characteristic roots are raised to large powers. Expressions involving subtraction between large nearly equal quantities can also lose significant digits.

The Python implementation benefits from arbitrary-precision integers for integer recurrences.

The JavaScript implementation uses `BigInt` for exact large Fibonacci values.

The Java implementation uses `BigInteger`.

The C++ implementation explicitly checks the representational limits of `unsigned long long` for Fibonacci generation.

These choices demonstrate an important distinction: deriving a correct recurrence solution does not automatically guarantee that a particular numerical representation can evaluate that solution exactly.

---

## Practical Interpretation of Growth

For a homogeneous linear recurrence, the characteristic root with the largest absolute magnitude generally determines the dominant exponential growth when its coefficient is non-zero and cancellation does not remove it.

For the roots `2` and `3`, a solution of the form:

`C1(2^n)+C2(3^n)`

is eventually dominated by the `3^n` component when `C2` is non-zero.

For a repeated root:

`(C1+C2n)r^n`

contains both exponential growth through `r^n` and an additional polynomial factor `n`.

This is why repeated-root recurrences can grow faster than a simple `C*r^n` solution with the same root magnitude.

---

## Relationship Between the Three Core Techniques

Iteration reveals structure by repeatedly expanding the recurrence.

Substitution formalizes the expansion process and allows the resulting pattern to be connected to a closed form and then verified against the base case.

Characteristic equations provide a systematic algebraic method for constant-coefficient linear homogeneous recurrences.

A practical recurrence-analysis workflow therefore depends on the structure of the recurrence:

`T(n)=T(n-1)+n`

naturally exposes a summation through iteration.

`T(n)=2T(n-1)+1`

naturally exposes a geometric progression through substitution.

`T(n)=5T(n-1)-6T(n-2)`

naturally leads to a characteristic polynomial.

`T(n)=4T(n-1)-4T(n-2)`

requires the repeated-root form because the characteristic polynomial has multiplicity two.

The implementations preserve these distinctions rather than presenting all recurrences as instances of one generic formula.

---

## Files and Execution

The Python program requires Python 3 and uses only the standard library. Run it with `python <filename>.py`.

The JavaScript program runs with a modern Node.js runtime using `node <filename>.js`.

The C++ program requires C++17 or later and can be compiled with a command such as `g++ -std=c++17 <filename>.cpp -o recurrence_case_study`.

The Java program requires Java 17 or later. Compile it with `javac SolvingRecurrences.java` and run it with `java SolvingRecurrences`.

The SQL script targets PostgreSQL and creates its own `recurrence_lab` schema. It removes an existing schema of the same name at the beginning so the demonstration starts from a deterministic database state.

---

## Implementation Boundaries

The examples intentionally focus on linear recurrences and their direct solution techniques.

The characteristic-equation implementations assume constant coefficients and real roots where the program explicitly requires real-valued solutions. Complex-root recurrences require a complex-number representation and are not silently treated as real roots.

The database implementation stores mathematical expressions as descriptive text rather than attempting to become a general symbolic algebra engine. Numeric recurrence states are calculated using PostgreSQL numeric arithmetic.

The executable programs validate their mathematical results through independent recurrence evaluation wherever practical. This prevents a closed-form implementation and its validation from depending entirely on the same calculation path.
