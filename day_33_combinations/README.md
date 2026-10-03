# Combinations: Binomial Coefficients and Pascal's Triangle

## Topic scope

Combinations count selections in which order does not matter. The central mathematical object is the binomial coefficient

`C(n,k) = n! / (k!(n-k)!)`

where `n` is the number of available objects and `k` is the number selected.

This topic connects three closely related ideas:

- **Binomial coefficients** provide the numerical count of `k`-element selections from `n` distinct objects.
- **Combinations** interpret that coefficient as an unordered selection problem.
- **Pascal's triangle** provides a recursive and visual structure in which row `n` contains `C(n,0)` through `C(n,n)`.

The three implementations approach the same mathematics from different technical directions. Python emphasizes exact computation, mathematical identities, dynamic programming, and probability. JavaScript emphasizes exact `BigInt` arithmetic, generators, event-driven processing, and asynchronous request handling. C++ presents a capacity-planning case study in which committee selection and audit sampling depend directly on binomial coefficients.

---

## Mathematical foundation

A permutation treats order as significant. A combination does not.

Suppose five engineers are eligible for a three-person committee. The committee `{A, B, C}` is the same committee as `{C, A, B}`. The ordering of the selected members does not create a new outcome.

The number of such committees is

`C(5,3) = 5! / (3!2!) = 10`.

The factorial formula is useful because it exposes the relationship between permutations and combinations. There are `n!` ordered arrangements, but every particular set of `k` selected objects can be arranged in `k!` ways, while the unselected objects can be arranged in `(n-k)!` ways. Dividing by both sources of redundant ordering gives the binomial coefficient.

The coefficient also satisfies the symmetry relation

`C(n,k) = C(n,n-k)`.

Selecting `k` objects is equivalent to deciding which `n-k` objects are excluded.

The boundary coefficients are

`C(n,0) = 1`

and

`C(n,n) = 1`.

There is exactly one way to select nothing and exactly one way to select every available object.

---

## Pascal's triangle

Pascal's triangle organizes binomial coefficients by value of `n`.

The first rows are represented as:

    1
    1 1
    1 2 1
    1 3 3 1
    1 4 6 4 1
    1 5 10 10 5 1

Row `n` contains

`C(n,0), C(n,1), ..., C(n,n)`.

The interior of each row follows Pascal's recurrence:

`C(n,k) = C(n-1,k-1) + C(n-1,k)`.

For example,

`C(5,2) = C(4,1) + C(4,2) = 4 + 6 = 10`.

This recurrence is important computationally because it allows an entire coefficient table to be constructed without factorials. It is also the basis of the dynamic-programming implementation used by the Python and C++ programs.

Pascal's triangle therefore has both mathematical and algorithmic significance. The same structure that explains why the coefficients have their values can also be used to compute and cache them.

---

## Binomial coefficients versus combinations

The terminology describes different perspectives on the same mathematical quantity.

A **binomial coefficient** is the numerical value `C(n,k)`.

A **combination** is an interpretation of that value as the number of unordered selections.

For example, if a repository team has eight eligible contributors and three people must be selected for an architecture review group, then

`C(8,3) = 56`

means there are 56 distinct groups when membership order is irrelevant.

The coefficient does not say which particular group should be selected. It only determines how many possible groups exist.

---

## Python implementation

The Python program implements several ways to calculate the same coefficient.

`combination_factorial()` directly follows the factorial definition. It is mathematically transparent, but factorials calculate considerably more information than is required for one coefficient.

`combination_multiplicative()` uses the recurrence

`C(n,k) = C(n,k-1) * (n-k+1) / k`

in an integer-preserving form. It also replaces `k` with `min(k,n-k)`, exploiting symmetry to reduce the number of iterations.

`combination_recursive()` demonstrates Pascal's recurrence directly. Without memoization, this approach repeatedly solves the same subproblems.

`combination_memoized()` retains previously calculated coefficients in a dictionary. This converts the repeated recursive structure into a dynamic-programming computation.

The program also implements `pascal_row()` and `pascal_triangle()`. These functions construct coefficients from adjacent entries rather than using factorials.

### Combination generation

`combinations_without_replacement()` uses backtracking to produce actual unordered selections. The increasing index constraint is important: after selecting an item at index `i`, later recursion only considers indexes greater than `i`. This prevents the same selection from appearing in multiple orders.

For example, selecting `Python`, `SQL`, and `C++` does not separately generate `C++`, `Python`, `SQL`, because those represent the same unordered combination.

The number of generated results is expected to equal `C(n,k)`.

### Probability

The Python program applies combinations to sampling without replacement through the hypergeometric distribution.

For a population containing `K` target objects and `N-K` non-target objects, a sample of size `n` containing exactly `k` target objects has probability

`[C(K,k) C(N-K,n-k)] / C(N,n)`.

The implementation uses `fractions.Fraction`, so the result remains an exact rational number instead of being converted immediately to a floating-point approximation.

This distinction matters when exact probability values are useful for validation or reproducible calculations.

### Identity verification

The Python program explicitly verifies:

- `C(n,k) = C(n,n-k)` for symmetry.
- Pascal's recurrence.
- `sum C(n,k) = 2^n`.
- The hockey-stick identity.

The row-sum identity follows from the binomial theorem with both variables equal to one:

`(1+1)^n = sum C(n,k) = 2^n`.

The hockey-stick identity is represented as

`C(r,r) + C(r+1,r) + ... + C(n,r) = C(n+1,r+1)`.

These checks turn mathematical properties into executable assertions of the implementation's correctness.

---

## JavaScript implementation

The JavaScript implementation uses `BigInt` deliberately.

JavaScript's ordinary `Number` type cannot represent every integer exactly. Binomial coefficients become large very quickly, so silently converting a large coefficient to `Number` can produce an incorrect result.

For example, the JavaScript program represents coefficients as values such as `52n` rather than `52` whenever the value is part of exact integer arithmetic.

`combinationMultiplicative()` performs exact multiplicative computation with `BigInt`.

### Generator-based combinations

The JavaScript `combinations()` function is a generator. Instead of requiring every combination to be stored in memory at once, it can yield one selection at a time.

This is particularly relevant because the number of combinations can be enormous.

For example, `C(100,50)` is extremely large. A program that attempted to materialize all of those selections would have a completely different memory profile from a program that consumes them incrementally.

The generator therefore demonstrates an important distinction between:

- calculating how many combinations exist, and
- actually constructing every combination.

The first can be cheap relative to the second.

### Duplicate-value handling

The `uniqueCombinations()` function illustrates a modeling issue that ordinary combinations alone do not resolve.

If an input contains repeated values such as `API`, `API`, `Database`, and `Cache`, positional combinations can produce duplicate value-level selections. Converting the values to a `Set` changes the domain so that equal values are treated as the same available type.

This is different from ordinary combinations of distinct objects. The correct interpretation depends on whether the input represents individual objects or categories/types.

### Event-driven coefficient processing

`CombinationEngine` provides a small event system using `Map` and `Set`.

Consumers can subscribe to events such as `calculationStarted`, `calculationCompleted`, and `calculationFailed`.

The arithmetic itself remains deterministic and synchronous. The event layer separates calculation from monitoring behavior. This is useful when a combinatorial calculation is part of a larger service in which logging, metrics, user-interface updates, or auditing must observe the operation without being embedded in the arithmetic function.

### Asynchronous request audit

`auditCombinationRequests()` introduces an asynchronous boundary around coefficient requests. It demonstrates how exact combinatorial calculations can participate in a request-processing workflow without turning the arithmetic itself into asynchronous mathematics.

Invalid requests are captured as structured failures rather than causing the entire request batch to terminate.

---

## C++ case study: project planning and audit sampling

The C++ program models a technical planning system with two practical uses for combinations.

### Committee planning

A project contains a fixed pool of eligible engineers. A committee must be selected without assigning positions within the committee.

For twelve eligible engineers and a four-person committee, the number of possible committees is

`C(12,4)`.

The `CommitteePlanner` class validates domain rules before calculating the coefficient. It rejects an empty committee and rejects a committee larger than the available population.

This separates mathematical validity from application-level policy. Mathematically, `C(n,0)` is valid and equals one. The planning application can still impose a rule that a real committee must contain at least one member.

### Actual committee generation

`CombinationGenerator` produces concrete committee memberships using recursive backtracking.

The recursion maintains a current selection and a starting index. Increasing the starting index after each choice guarantees that the same members cannot be emitted in a different order.

The generator therefore corresponds directly to the mathematical interpretation of a combination.

The program also prints the generated committees for a small example so that the relationship between the coefficient and actual selections can be inspected.

### Audit sampling

The second application is an audit sample.

Suppose a population contains twenty records, five of which are high-risk. Four records are selected without replacement. The probability of exactly two high-risk records is

`[C(5,2) C(15,2)] / C(20,4)`.

The C++ implementation calculates the numerator and denominator separately and reduces the resulting fraction using a greatest-common-divisor algorithm.

This case demonstrates why combinations naturally appear in sampling problems: each unordered sample of four records represents one possible sample outcome.

---

## Integer representation and exactness

Combinatorial coefficients grow rapidly.

Even moderate values of `n` can produce coefficients much larger than ordinary machine integers.

The Python implementation benefits from Python's arbitrary-precision integers, so its exact coefficient calculations continue beyond fixed-width integer limits.

JavaScript uses `BigInt` because `Number` is not sufficient for arbitrary exact integer arithmetic.

The C++ implementation uses `unsigned __int128` for a wider fixed-width range than `uint64_t`. This is useful for the case study but is not arbitrary precision. A sufficiently large coefficient can still overflow the representation.

A production C++ system requiring coefficients beyond the fixed-width range would need an arbitrary-precision integer representation and explicit overflow policies.

---

## Computational strategies

### Factorial formula

The factorial formula is conceptually direct:

`C(n,k) = n! / (k!(n-k)!)`.

Its main weakness is unnecessary intermediate computation. If only `C(1000,2)` is needed, calculating `1000!` is vastly more work than calculating the coefficient through a multiplicative recurrence.

### Multiplicative computation

The multiplicative approach requires approximately `min(k,n-k)` iterations.

It is generally preferable for computing one coefficient because symmetry reduces the loop length.

The implementation also performs exact integer division at each step rather than converting the result to floating point.

### Pascal dynamic programming

Constructing all rows through row `n` requires `O(n²)` coefficient operations and `O(n²)` storage when the complete triangle is retained.

The advantage is reuse. After the table has been constructed, any stored `C(n,k)` can be retrieved directly.

If only the final row is needed, memory can be reduced to `O(n)` by retaining only the previous row while constructing the next row.

### Combination generation

Generating all `k`-element selections is fundamentally different from calculating `C(n,k)`.

The number of results itself is `C(n,k)`, so an algorithm that outputs every combination necessarily performs at least enough work to represent those outputs.

This is why a system should not generate every combination merely to determine how many exist.

---

## Important identities

### Symmetry

`C(n,k) = C(n,n-k)`

This reflects the equivalence between selecting `k` objects and excluding `n-k` objects.

### Pascal recurrence

`C(n,k) = C(n-1,k-1) + C(n-1,k)`

Every interior coefficient is the sum of the two coefficients immediately above it in Pascal's triangle.

### Row sum

`C(n,0) + C(n,1) + ... + C(n,n) = 2^n`

This follows directly from the binomial theorem.

### Binomial theorem

For non-negative integer `n`,

`(a+b)^n = sum from k=0 to n of C(n,k)a^(n-k)b^k`.

For example,

`(2+3)^5`

can be evaluated through the coefficients in row five:

`1, 5, 10, 10, 5, 1`.

The expansion is

`1(2^5) + 5(2^4)(3) + 10(2^3)(3^2) + 10(2^2)(3^3) + 5(2)(3^4) + 1(3^5)`.

The implementations evaluate this computationally rather than treating the theorem as a purely symbolic statement.

---

## Boundary conditions and validation

The mathematically valid domain for an ordinary binomial coefficient is

`n >= 0`

and

`0 <= k <= n`.

The implementations explicitly validate these conditions.

Important boundary values include:

`C(0,0) = 1`

`C(n,0) = 1`

`C(n,n) = 1`

`C(n,1) = n`

`C(n,n-1) = n`.

Requests such as `C(5,8)` are rejected because eight objects cannot be selected from a set containing only five objects.

The probability implementations also validate population size, number of target items, sample size, and requested number of target items. A mathematically valid coefficient can still be invalid within a particular sampling model, so both mathematical and domain validation are necessary.

---

## Common modeling mistakes

### Treating order as significant

If a committee has members Alice, Bob, and Chen, the sequence `Alice, Bob, Chen` is not a different committee from `Chen, Alice, Bob`.

Using permutations instead of combinations would overcount the possible committees.

### Confusing combinations with repeated selection

Ordinary `C(n,k)` assumes a selection of `k` positions from `n` distinct available objects without replacement.

If repetition is allowed, a different counting model may be required. For example, selecting `k` items from `n` types with unlimited repetition uses

`C(n+k-1,k)`.

That formula describes multisets rather than ordinary subsets.

### Converting large coefficients to floating point

Large coefficients may not be exactly representable in floating-point formats.

The Python and JavaScript implementations therefore use exact integer representations for coefficient calculations. Floating-point conversion is used only where an approximate probability display is explicitly requested.

### Generating selections to count them

If the objective is only to determine the number of possible committees, generating every committee is unnecessary.

`C(n,k)` provides the count directly.

Actual combination generation should be reserved for cases where the individual selections are required for later processing.

---

## Practical interpretation

Combinations occur whenever the identity of selected objects matters but their order does not.

Examples directly represented by the implementations include:

- selecting members of a project committee;
- determining the number of possible audit samples;
- calculating exact probabilities for sampling without replacement;
- constructing coefficients for polynomial expansion;
- validating combinatorial identities;
- enumerating small sets of possible team configurations.

The important modeling question is not simply "Which formula should be used?" It is first to determine whether the outcome is ordered, whether objects can be repeated, whether selections are made with or without replacement, and whether the system needs only a count or every concrete selection.

Once those rules are established, the binomial coefficient provides the appropriate mathematical representation for ordinary unordered selection without replacement.

---

## Implementation relationship

The three programs intentionally use different technical approaches.

The **Python implementation** focuses on mathematical breadth. It contains factorial, multiplicative, recursive, memoized, dynamic-programming, probability, identity-validation, and combination-generation implementations. Python's arbitrary-precision integers make it suitable for exact coefficient demonstrations.

The **JavaScript implementation** focuses on runtime behavior. `BigInt` preserves exact integer coefficients, generators support lazy combination enumeration, `Map` and `Set` support event and duplicate-value handling, and asynchronous processing models a coefficient service workflow.

The **C++ implementation** focuses on a coherent system design. A committee planner validates application rules, a recursive generator produces concrete selections, Pascal's triangle stores reusable coefficients, and an audit module uses combinations to calculate exact sampling probabilities.

These approaches demonstrate that the same mathematical object can have different implementation concerns depending on the programming environment and system requirements.

---

## Production considerations

A production combinatorial service should establish explicit limits on `n` and `k`. Although the mathematical definition permits arbitrarily large values, computation, memory, serialization, and response time remain finite.

A service that accepts user-controlled values should reject unreasonable requests before allocating a large Pascal table or attempting to enumerate an enormous number of combinations.

Exact integer representation should be selected according to the expected coefficient range. Silent conversion from exact integers to floating-point values can introduce incorrect results.

For combination enumeration, lazy processing is preferable when consumers can process one selection at a time. Materializing all combinations should be limited to domains where the result count is known to be manageable.

Probability calculations should retain exact fractions when reproducibility or auditing matters, converting to decimal form only at presentation boundaries.

For dynamic programming, storing the complete Pascal triangle is appropriate when many coefficients from the same range are repeatedly queried. If only one row or one coefficient is required, multiplicative computation generally avoids unnecessary storage.
