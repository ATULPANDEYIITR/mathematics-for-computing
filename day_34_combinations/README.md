# Combinations, Binomial Coefficients, and Pascal's Triangle

This project develops a practical treatment of combinations through three complementary implementations:

- `combinations.py` builds exact binomial coefficients, generates Pascal's triangle, verifies combinatorial identities, enumerates subsets, and applies combinations to a binomial probability calculation.
- `combinations.js` focuses on JavaScript-specific numerical behavior, using `BigInt` when exact integer arithmetic exceeds the reliable range of `Number`. It also uses a generator and an event-driven workflow around combinatorial operations.
- `combinations.cpp` models a repository-governance scenario in which eligible engineers form review committees. The program distinguishes the theoretical number of committees from committees satisfying an organizational diversity constraint.

The mathematical core is the binomial coefficient

`C(n,r) = n! / (r!(n-r)!)`

where `n` is the population size and `r` is the number of selected elements. A combination does not distinguish between different orderings of the same selected elements. Selecting Asha, Chen, and Divya therefore represents the same combination as selecting Divya, Asha, and Chen.

The implementations use the equivalent notation `C(n,r)` throughout.

## Combinations

A combination answers a selection question:

> How many distinct groups of `r` objects can be selected from `n` objects when order does not matter?

For example, selecting three reviewers from six eligible reviewers produces

`C(6,3) = 20`

possible committees before any additional policy constraint is applied.

This distinction from permutation is fundamental. A permutation would treat different ordering as meaningful. A combination treats the selected set as the result.

The boundary conditions are important:

- `C(n,0) = 1` because there is exactly one empty selection.
- `C(n,n) = 1` because there is exactly one way to select everybody.
- `C(n,r) = C(n,n-r)` because choosing the selected elements is equivalent to choosing the elements left out.
- Values with `r < 0` or `r > n` are rejected by the implementations because they do not represent ordinary `r`-element selections from an `n`-element population.

## Computing Binomial Coefficients

The factorial definition is mathematically direct:

`C(n,r) = n! / (r!(n-r)!)`

The Python implementation provides `combination_factorial()` to make this definition explicit. Python's arbitrary-precision integers make the calculation exact even when the coefficient becomes very large.

The multiplicative implementation is more targeted:

`C(n,r) = ((n-r+1)(n-r+2)...n) / r!`

The implementation first replaces `r` with `min(r,n-r)`. This uses the symmetry of binomial coefficients to reduce the number of iterations.

The Python implementation also contains a factor-reduction version that cancels common factors between numerator and denominator before multiplying. This demonstrates an important arithmetic design principle: the mathematical expression and the computational representation do not have to use the same intermediate values.

The recursive implementation uses Pascal's recurrence:

`C(n,r) = C(n-1,r-1) + C(n-1,r)`

with the boundary case `C(n,0) = C(n,n) = 1`. Memoization is required for the recursive form to remain practical. Without memoization, the same subproblems are repeatedly recalculated and the recursion grows exponentially.

For production code, the multiplicative or language-standard exact implementation is normally preferable to recursive evaluation when the objective is simply to obtain one coefficient.

## Pascal's Triangle

Pascal's triangle organizes all binomial coefficients into rows.

The beginning of the triangle is:

    1
    1 1
    1 2 1
    1 3 3 1
    1 4 6 4 1
    1 5 10 10 5 1

Row `n` contains

`C(n,0), C(n,1), ..., C(n,n)`.

Every interior value is the sum of the two values immediately above it:

`C(n,r) = C(n-1,r-1) + C(n-1,r)`.

The Python program constructs the triangle row by row. Each new row begins and ends with `1`, while interior positions are obtained from adjacent values in the previous row.

The JavaScript implementation uses a generator for Pascal's triangle. This is significant for large structures because the caller can consume rows incrementally instead of requiring the entire triangle to exist in memory at once.

The C++ implementation stores rows in vectors and uses the multiplicative recurrence to construct each row.

## Important Binomial Identities

### Symmetry

The identity

`C(n,r) = C(n,n-r)`

states that choosing `r` objects is equivalent to deciding which `n-r` objects are excluded.

The implementations verify this identity across many small values.

This is not merely a mathematical curiosity. It is also an optimization. If `r` is close to `n`, replacing it with `n-r` substantially reduces the number of multiplicative steps.

### Pascal's recurrence

The recurrence

`C(n,r) = C(n-1,r-1) + C(n-1,r)`

is the structural rule behind Pascal's triangle.

It can be understood through a particular element. Every `r`-element subset of an `n`-element population either contains a chosen final element or does not contain it.

If it contains that element, the remaining `r-1` elements can be chosen in `C(n-1,r-1)` ways.

If it does not contain that element, all `r` elements come from the other `n-1` objects, giving `C(n-1,r)` possibilities.

The two cases are disjoint and exhaustive, so their counts add.

### Row sums

Every row satisfies

`sum(C(n,r), r=0..n) = 2^n`.

The reason is that every element has two independent states in a subset: included or excluded. With `n` elements, there are therefore `2^n` subsets.

The Python and JavaScript programs verify this relationship.

## Enumerating Actual Combinations

A coefficient tells us how many combinations exist. It does not itself produce the combinations.

The Python implementation separates these concerns.

`choose_subsets()` uses backtracking to construct every `r`-element subset. At each decision point, the algorithm selects an item and recursively considers later items. Because subsequent selections only move forward through the input list, the same subset cannot be produced in multiple orderings.

For six reviewers and a committee size of three, the generator produces exactly twenty committees, matching `C(6,3)`.

The JavaScript implementation uses the same combinatorial idea but exposes the result as an array and integrates enumeration with an event-driven workflow object.

Enumeration has an unavoidable output cost. If there are `C(n,r)` valid combinations, producing all of them requires at least proportional work simply to emit those results. A formula can calculate the count much more cheaply than an algorithm can list every combination.

## Binomial Probability

Combinations also appear in the binomial probability distribution.

For exactly `k` successes in `n` independent trials with success probability `p`:

`P(X=k) = C(n,k) p^k (1-p)^(n-k)`.

The Python implementation calculates this expression in `probability_exactly_k_successes()`.

The combination coefficient accounts for the number of different positions in which the `k` successes can occur. The probability of any particular sequence containing `k` successes and `n-k` failures is `p^k(1-p)^(n-k)`. Multiplying the two quantities accounts for every distinct sequence with exactly `k` successes.

The implementation validates that `p` lies between zero and one and that `k` is a valid count of successes.

## Python Implementation

The Python program is designed as an executable mathematical laboratory rather than a collection of disconnected examples.

Its coefficient implementations provide several computational perspectives:

- `combination_factorial()` directly reflects the factorial definition.
- `combination_multiplicative()` reduces the amount of arithmetic required by using symmetry.
- `combination_gcd_reduced()` demonstrates explicit factor cancellation.
- `combination_recursive()` implements Pascal's recurrence with memoization.

`pascal_triangle()` constructs multiple rows, while `pascal_row()` computes one row directly.

The program verifies symmetry, Pascal's recurrence, and row sums rather than merely printing numerical examples. The self-test suite compares independent coefficient implementations across a range of values, which helps detect arithmetic or boundary-condition errors.

The subset-selection example models the selection of a reviewer committee. The example is combinatorial rather than an API integration: it demonstrates how a mathematical count can be connected to a real selection problem without confusing theoretical possibilities with an operational policy.

Python's arbitrary-precision integers are particularly useful here. Values such as `C(100,50)` are represented exactly without overflowing a fixed-width integer type.

## JavaScript Implementation

JavaScript requires special treatment because ordinary `Number` values use IEEE 754 floating-point representation.

Although integer values are exactly represented only within the safe-integer range, binomial coefficients grow rapidly. A calculation can therefore appear numerically plausible while no longer representing the exact integer.

The file provides two separate approaches:

- `combinationNumber()` is intended for values that remain within JavaScript's safe integer range.
- `combinationBigInt()` uses `BigInt` to maintain exact integer arithmetic for larger coefficients.

The two functions deliberately do not silently mix numeric types. This avoids a class of JavaScript errors caused by attempting arithmetic between `Number` and `BigInt`.

The Pascal triangle is exposed through `pascalTriangle()`, a generator function. This demonstrates lazy row production: a caller can process one row and then request the next rather than allocating the entire structure.

The `CombinationEventBus` and `CombinatorialWorkflow` classes provide an event-driven perspective. A calculation emits an event describing the coefficient that was produced, while subset generation emits information about the number of generated combinations.

This event model is useful when combinatorial calculations form part of a larger JavaScript application. The calculation itself remains separate from consumers that may log results, update a user interface, or record metrics.

## C++ Repository Governance Case Study

The C++ program uses combinations to model a repository governance problem.

A repository has a set of potential reviewers. Each reviewer has:

- a name,
- an organizational team,
- an eligibility state.

A `RepositoryPolicy` specifies the number of approvals required, whether reviewers must come from distinct teams, and which teams are excluded.

`GovernanceEngine::eligibleReviewers()` applies eligibility and team-exclusion rules before any combinatorial calculation occurs.

This separation is important. `C(n,r)` answers how many selections can be made from a specified population. It does not decide who belongs to that population.

For example, if six reviewers are eligible and three approvals are required, the theoretical committee count is `C(6,3) = 20`.

The program then applies a separate diversity constraint. When distinct teams are required, committees containing two reviewers from the same team are rejected during enumeration.

This produces two different quantities:

- the unconstrained mathematical count, which answers how many three-person committees exist;
- the policy-valid count, which answers how many of those committees satisfy the repository's governance rule.

That distinction is important in real systems. A binomial coefficient should not be mistaken for a complete policy engine.

## Reviewer Eligibility and Combinatorial Population

The C++ case study deliberately filters reviewers before applying `C(n,r)`.

An ineligible reviewer is not equivalent to an eligible reviewer who simply has a lower probability of being selected. The person is outside the candidate population for that policy.

Similarly, excluding an entire team changes `n`, the population size. The coefficient must therefore be recalculated against the resulting eligible set.

This illustrates a general modeling rule:

> Apply population constraints before interpreting a combinatorial count.

Post-selection constraints are different. The requirement that selected reviewers come from distinct teams cannot be represented by simply changing `r`; it constrains which subsets are valid.

The program therefore calculates the theoretical coefficient and then performs explicit enumeration when the additional policy requires examination of each candidate committee.

## Complexity and Performance

For a single coefficient, the multiplicative approach performs approximately `O(min(r,n-r))` iterations.

Using `min(r,n-r)` matters because of binomial symmetry. For example, calculating `C(1000,990)` directly with `r=990` would perform many unnecessary iterations, while calculating the equivalent `C(1000,10)` needs only ten.

Constructing one Pascal row requires `O(n)` stored coefficients.

Constructing all rows through row `n` requires `O(n^2)` coefficient storage if every row is retained. If only the current row is needed, the algorithm can use `O(n)` memory.

Enumerating all combinations has output-sensitive complexity. The number of outputs itself is `C(n,r)`, so no algorithm that explicitly emits every result can avoid work proportional to the number of generated combinations.

This difference between counting and enumerating is fundamental:

`C(n,r)` can be computed without constructing every subset.

## Exact Arithmetic

Large coefficients create different implementation concerns in each language.

Python integers automatically expand beyond machine-word limits, so the Python program can calculate very large exact coefficients without a special integer type.

JavaScript requires an explicit choice between `Number` and `BigInt`. `Number` is convenient for values within its safe integer range, while `BigInt` is required when exact integer arithmetic exceeds that range.

The C++ program uses `unsigned long long` and explicitly checks for overflow before multiplication. Its implementation is therefore exact only within the capacity of that type. When a coefficient exceeds that capacity, the program raises a controlled error rather than returning a silently corrupted value.

This is a production concern: integer overflow is not merely a mathematical issue. It can change counts and invalidate decisions derived from those counts.

## Edge Cases and Failure Conditions

The implementations explicitly address several boundary cases.

`C(0,0)` is valid and equals one. There is exactly one way to select no objects from an empty population: the empty selection.

`C(n,0)` and `C(n,n)` both equal one.

A request such as `C(5,6)` is rejected because six elements cannot be selected from a population of five.

Negative `n` or `r` values are rejected by the Python and JavaScript validation functions.

The JavaScript implementation also detects when a `Number` result is outside the safe integer range and directs the caller toward `BigInt`.

The C++ implementation detects fixed-width arithmetic overflow and raises `CombinationError`.

These checks prevent invalid input and numeric limitations from being disguised as legitimate combinatorial results.

## Common Modeling Mistakes

A frequent mistake is using permutations when order does not matter. If a review committee consists of Asha, Chen, and Divya, the order in which those names are listed does not create a different committee.

Another mistake is assuming that `C(n,r)` accounts for eligibility rules. It does not. The value is meaningful only after `n` has been defined as the correct candidate population.

A further mistake is assuming that every additional policy can be represented by changing `r`. A distinct-team requirement, for example, depends on the composition of the selected set. It is a constraint over combinations rather than a different committee size.

Another implementation error is calculating factorials unnecessarily for very large values. Factorials can become enormous even when the final coefficient is substantially smaller. The multiplicative approach limits intermediate work.

In JavaScript, treating large coefficients as ordinary `Number` values can silently lose integer precision. Exact combinatorial code should choose `BigInt` when the required values exceed the safe integer range.

## Relationship Between the Three Implementations

The Python implementation emphasizes mathematical breadth and executable verification. It exposes several ways to calculate coefficients and connects combinations to subset generation and probability.

The JavaScript implementation emphasizes runtime-specific behavior. Exact `BigInt` arithmetic, lazy generators, event emission, and class-based workflow modeling show how the same mathematical mechanism behaves in an application-oriented JavaScript environment.

The C++ implementation treats combinations as a component inside a policy engine. Its focus is the distinction between theoretical combinations and combinations satisfying real constraints such as eligibility and team diversity.

The mathematical invariant remains the same across the implementations:

`C(n,r) = C(n,n-r)`

and

`C(n,r) = C(n-1,r-1) + C(n-1,r)`.

The engineering decisions around those invariants differ because Python, JavaScript, and C++ provide different numeric and architectural facilities.

## Practical Interpretation

Combinations are useful whenever a system must reason about unordered selections.

In the C++ case study, the selected set represents a possible reviewer committee. In the Python program, the same abstraction is used for explicit subset generation and binomial probability. In the JavaScript program, it becomes a reusable computational service with event notifications and lazy data production.

The central distinction is between **counting possibilities** and **validating possibilities**.

A binomial coefficient counts all `r`-element selections from a population of size `n`. Additional domain rules may reduce the set of valid selections. When those rules depend only on the population and selection size, a closed-form combinatorial expression may be sufficient. When they depend on the composition of individual selections, explicit filtering or a specialized counting algorithm may be required.

This distinction allows the implementations to use combinations as a precise mathematical primitive without treating the coefficient itself as a substitute for domain-specific validation.
