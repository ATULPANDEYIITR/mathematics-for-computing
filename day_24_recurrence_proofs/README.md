# Recurrence Proofs

## Topic scope

This repository studies three closely related ideas:

- recursive definitions
- recurrence relations
- induction-based recurrence proofs

The implementations use Python, JavaScript, and C++ to connect mathematical definitions with executable algorithms. The examples progress from elementary recursive sequences to divide-and-conquer algorithms, recurrence-tree reasoning, substitution-style verification, strong induction, and structural induction.

The central principle is that recursion describes how an object or computation is constructed from smaller instances, while a recurrence describes how the value, cost, or size of an instance depends on smaller instances.

A recurrence by itself is not necessarily a solution. It must be interpreted with its base cases, domain, recurrence rule, and intended quantity.

---

## Recursive definitions

A recursive definition specifies an object using smaller instances of the same object. A complete recursive definition normally contains:

1. a base case
2. one or more recursive cases
3. a rule that moves from the recursive case toward a base case

### Factorial

The factorial function is defined by:

`0! = 1`

and, for `n >= 1`:

`n! = n(n - 1)!`

The Python, JavaScript, and C++ implementations directly encode this definition.

For example, evaluating `5!` follows:

`5! = 5 × 4!`

`4! = 4 × 3!`

`3! = 3 × 2!`

`2! = 2 × 1!`

`1! = 1 × 0!`

`0! = 1`

Therefore:

`5! = 120`

The recursive definition is mathematically concise, but the implementation also has practical constraints. Each recursive call consumes stack space, and fixed-width integer types can overflow for sufficiently large factorials.

### Fibonacci numbers

The Fibonacci sequence is defined by:

`F(0) = 0`

`F(1) = 1`

`F(n) = F(n - 1) + F(n - 2)`

The direct recursive implementation follows the definition exactly.

The problem is that the recursion tree contains repeated subproblems. Computing `F(5)`, for example, requires `F(3)` and `F(2)` multiple times.

This creates a difference between mathematical structure and computational efficiency. A recurrence may be simple to state while producing an inefficient naive implementation.

---

## Recurrence relations

A recurrence relation defines a value using values at smaller arguments.

A recurrence normally consists of:

- the quantity being defined
- one or more base cases
- a recursive equation
- a domain
- sometimes additional restrictions

For example:

`T(0) = 0`

`T(n) = T(n - 1) + n`

defines the triangular numbers.

The first values are:

`T(0) = 0`

`T(1) = 1`

`T(2) = 3`

`T(3) = 6`

`T(4) = 10`

The corresponding closed form is:

`T(n) = n(n + 1)/2`

The Python and C++ programs implement both the recurrence and the closed form. The JavaScript program also provides both implementations.

---

## Recursive definitions versus recurrences

The two concepts are closely related but are not identical.

A recursive definition focuses on defining a mathematical object.

A recurrence relation focuses on a sequence, function, or numerical quantity through smaller instances.

An algorithm's running time can also be described by a recurrence.

For example, binary search has approximately:

`T(n) = T(n/2) + Theta(1)`

The recurrence describes computational cost rather than the value being searched for.

Merge sort has:

`T(n) = 2T(n/2) + Theta(n)`

The two recursive calls account for the two halves, while the linear term represents merging.

---

## Base cases

Base cases are essential because recursion must eventually stop.

A recursive definition without a valid terminating condition may produce:

- infinite recursion
- stack overflow
- non-terminating computation
- invalid mathematical definitions

For factorial, the base case is:

`0! = 1`

For Fibonacci, the base cases are:

`F(0) = 0`

`F(1) = 1`

For binary search, an empty search interval is a base condition indicating that the target is absent.

For merge sort, a list with zero or one element is already sorted.

The correct base case is part of both the mathematical definition and the implementation.

---

## Recurrence expansion

One standard method for analyzing a recurrence is repeated substitution or expansion.

Consider:

`T(n) = T(n - 1) + n`

Expanding once gives:

`T(n) = T(n - 2) + (n - 1) + n`

Expanding again gives:

`T(n) = T(n - 3) + (n - 2) + (n - 1) + n`

Continuing until the base case gives:

`T(n) = T(0) + 1 + 2 + ... + n`

The sum is:

`1 + 2 + ... + n = n(n + 1)/2`

Therefore:

`T(n) = T(0) + n(n + 1)/2`

If `T(0) = 0`, then:

`T(n) = n(n + 1)/2`

The Python and JavaScript implementations contain functions that print expansion steps for this recurrence.

---

## Closed forms

A closed form expresses a recursively defined sequence without recursive references.

For the arithmetic recurrence:

`a(0) = c`

`a(n) = a(n - 1) + d`

the closed form is:

`a(n) = c + nd`

For the power-of-two recurrence:

`P(0) = 1`

`P(n) = 2P(n - 1)`

the closed form is:

`P(n) = 2^n`

For the Towers of Hanoi recurrence:

`H(0) = 0`

`H(n) = 2H(n - 1) + 1`

the closed form is:

`H(n) = 2^n - 1`

A closed form can make growth easier to analyze, but deriving it requires mathematical reasoning.

---

## Mathematical induction

Mathematical induction is a proof method for propositions indexed by integers.

A standard induction proof contains:

### Base case

Show that the proposition is true for the initial value.

### Inductive hypothesis

Assume the proposition is true for an arbitrary valid value `n`.

### Inductive step

Using the assumption, prove that the proposition is true for the next value, usually `n + 1`.

### Conclusion

If the base case and inductive implication are established under the appropriate domain conditions, the proposition holds for all values reached by the induction.

The Python and JavaScript programs represent these components with an `InductionProof` abstraction.

The C++ implementation performs equivalent induction-oriented checks.

---

## Induction proof of the triangular-number formula

Consider the recursive definition:

`T(0) = 0`

`T(n) = T(n - 1) + n`

We want to prove:

`T(n) = n(n + 1)/2`

### Base case

For `n = 0`:

`T(0) = 0`

and:

`0(0 + 1)/2 = 0`

Therefore the proposition is true at the base case.

### Inductive hypothesis

Assume:

`T(n) = n(n + 1)/2`

### Inductive step

From the recurrence:

`T(n + 1) = T(n) + (n + 1)`

Using the inductive hypothesis:

`T(n + 1) = n(n + 1)/2 + (n + 1)`

Factor:

`T(n + 1) = (n + 1)(n/2 + 1)`

Therefore:

`T(n + 1) = (n + 1)(n + 2)/2`

which is the required formula for `n + 1`.

The programs implement the algebraic transformation computationally. The finite checks are useful for testing the implementation, but the symbolic inductive argument is what constitutes the mathematical proof.

---

## Induction proof of a recurrence-defined exponential sequence

Consider:

`P(0) = 1`

`P(n) = 2P(n - 1)`

The proposed closed form is:

`P(n) = 2^n`

The base case is:

`P(0) = 1 = 2^0`

Assume:

`P(n) = 2^n`

Then:

`P(n + 1) = 2P(n)`

Using the hypothesis:

`P(n + 1) = 2(2^n)`

Therefore:

`P(n + 1) = 2^(n + 1)`

The recurrence and the closed form are therefore consistent.

---

## Recurrence proofs for algorithmic complexity

Recurrences are particularly important in algorithm analysis.

When a recursive algorithm is designed, its execution can often be represented by a recurrence.

A typical process is:

1. identify the size of the original problem
2. determine the number of recursive subproblems
3. determine the size of each subproblem
4. determine the non-recursive work
5. define the base-case cost
6. solve or bound the recurrence

For example, binary search approximately halves the problem and performs constant additional work:

`T(n) = T(n/2) + Theta(1)`

This leads to:

`T(n) = Theta(log n)`

---

## Binary search

The recursive binary-search implementation works on a sorted sequence.

At every step:

- the middle element is inspected
- if it is the target, the search ends
- if the target is larger, the left half is discarded
- if the target is smaller, the right half is discarded

The problem size therefore changes approximately from `n` to `n/2`.

The recurrence is:

`T(n) = T(n/2) + Theta(1)`

Repeated expansion gives:

`T(n) = T(n/4) + Theta(1) + Theta(1)`

and eventually:

`T(n) = T(1) + Theta(log n)`

so:

`T(n) = Theta(log n)`

Both recursive and iterative versions are included.

The iterative version avoids recursive stack growth while preserving the same asymptotic running time.

---

## Merge sort

Merge sort divides an input into two approximately equal halves.

Each half is recursively sorted, and the two sorted halves are merged.

Its recurrence is:

`T(n) = 2T(n/2) + Theta(n)`

The recursion depth is logarithmic:

`log_2(n)`

At every level, the total merging work is proportional to `n`.

Therefore:

`T(n) = Theta(n log n)`

The Python, JavaScript, and C++ implementations all demonstrate this divide-and-conquer structure.

The C++ implementation explicitly separates the recursive sorting operation from the merge operation, making the source of each part of the recurrence visible.

---

## Quicksort and input-dependent recurrences

Quicksort demonstrates why a recurrence can depend on how an algorithm partitions its input.

For a balanced partition:

`T(n) = 2T(n/2) + Theta(n)`

which gives:

`Theta(n log n)`

For a highly unbalanced partition:

`T(n) = T(n - 1) + Theta(n)`

Expanding produces approximately:

`n + (n - 1) + (n - 2) + ... + 1`

which is:

`Theta(n^2)`

The implementations use the final array element as the pivot. This choice makes the worst-case behavior easy to demonstrate, especially when the input is already ordered or has an unfavorable distribution.

The important point is that an algorithm does not necessarily have one recurrence independent of all inputs. The recurrence can depend on the structure of recursive subproblems.

---

## Towers of Hanoi

The Towers of Hanoi problem provides a classic recurrence:

`H(0) = 0`

`H(n) = 2H(n - 1) + 1`

To move `n` disks:

1. move the top `n - 1` disks
2. move the largest disk
3. move the `n - 1` disks again

Therefore:

`H(n) = H(n - 1) + 1 + H(n - 1)`

and:

`H(n) = 2H(n - 1) + 1`

The closed form is:

`H(n) = 2^n - 1`

The exponential growth shows why increasing the number of disks quickly becomes computationally impractical.

---

## Recursion trees

A recursion tree represents recursive calls as a tree.

Consider:

`T(n) = 2T(n/2) + c`

At the first level there is one problem.

At the next level there are two subproblems.

At the next level there are four.

After `k` levels there are approximately:

`2^k`

subproblems.

Because the problem size becomes `n/2^k`, the recursion reaches constant-size problems after approximately:

`log_2(n)`

levels.

The number of leaves is therefore proportional to `n`.

The recurrence-tree implementation in each relevant program evaluates small instances directly so the structure can be observed numerically.

---

## Substitution method

The substitution method attempts to prove an asymptotic upper or lower bound by assuming a candidate bound and verifying that the recurrence preserves it.

Suppose:

`T(n) = 2T(n/2) + n`

and we suspect:

`T(n) = O(n log n)`

A proof may propose:

`T(n) <= cn log n`

for a suitable constant `c`.

The inductive step substitutes the proposed bound into the recurrence:

`T(n) <= 2c(n/2)log(n/2) + n`

which becomes:

`T(n) <= cn(log n - 1) + n`

and:

`T(n) <= cn log n - cn + n`

For a sufficiently large constant `c`, the negative term can absorb the linear term.

The exact constants and base cases must be handled carefully.

The implementations include finite substitution-style checks. These checks demonstrate the mechanics of testing a candidate bound, but finite numerical verification alone does not prove an asymptotic statement for every valid `n`.

---

## Strong induction

Ordinary induction often uses the immediately preceding case:

`P(n) -> P(n + 1)`

Strong induction permits the inductive step to assume that all earlier valid cases have already been established.

A useful example is the claim that every integer `n >= 2` can be represented as:

`2a + 3b`

for non-negative integers `a` and `b`.

The recursive characterization can use:

`P(n) = P(n - 2) OR P(n - 3)`

because subtracting either 2 or 3 reduces the problem to a smaller integer.

The Python, JavaScript, and C++ implementations use memoized recursion to evaluate this relation.

A strong-induction proof can establish suitable base cases such as:

`2 = 2`

`3 = 3`

`4 = 2 + 2`

Then a larger value can be reduced to a previously established case.

---

## Structural induction

Structural induction is an induction technique for recursively defined structures.

Instead of proving a statement for every integer, the proof follows the way the structure itself is constructed.

Binary trees are a natural example.

A recursive tree definition can be represented as:

- an empty tree
- a node containing a value and zero or more subtrees

For the binary-tree implementations, the recursive definition of size is:

`size(empty) = 0`

`size(node) = 1 + size(left) + size(right)`

Height is defined by:

`height(empty) = 0`

`height(node) = 1 + max(height(left), height(right))`

The programs also verify:

`nodes = leaves + internal nodes`

A structural proof follows the tree construction rather than treating the tree as an arbitrary flat collection.

---

## Python implementation

The Python script provides the broadest mathematical study implementation.

It includes:

- recursive factorial
- direct recursive Fibonacci
- memoized Fibonacci
- iterative Fibonacci
- recursive arithmetic sequences
- closed-form arithmetic sequences
- recursive powers of two
- triangular numbers
- Towers of Hanoi
- recurrence expansion
- recursion-tree evaluation
- recursive and iterative binary search
- merge sort
- quicksort
- induction-proof data structures
- strong induction
- structural induction on binary trees
- substitution-style finite checks
- Master-Theorem classification
- edge-case checks
- executable assertions

Python is useful for recurrence studies because recursive definitions can often be represented with very little syntactic overhead. Dictionaries, caching, lists, and classes also make it straightforward to experiment with different recurrence structures.

The Python implementation uses `functools.lru_cache` for memoized Fibonacci and for selected recurrence calculations.

---

## JavaScript implementation

The JavaScript implementation emphasizes the same mathematical structures while also demonstrating JavaScript-specific execution patterns.

It includes:

- recursive functions
- default parameters
- `Map`-based memoization
- arrays
- classes
- recursive tree objects
- divide-and-conquer sorting
- iterative and recursive search
- error handling
- assertions
- recurrence-tree evaluation
- induction-oriented verification

JavaScript's `Map` provides a convenient representation of a memoization table. The `TreeNode` class demonstrates how recursively defined mathematical structures can be represented as object graphs.

The implementation is executable with a standard Node.js runtime and does not require external packages.

---

## C++ case study

The C++ program models a document-indexing service.

The system contains records with:

- document ID
- category
- priority

Records are validated, stored, sorted, and searched.

The major components are:

- `DocumentRecord`
- `DocumentIndex`
- recursive binary search
- merge sort
- quicksort
- recursive numerical definitions
- memoized Fibonacci
- binary-tree structures
- recurrence-tree evaluation
- Master-Theorem classification
- substitution-style checks
- executable assertions

### Problem being modeled

A document-processing system needs an ordered index so records can be located efficiently.

The processing pipeline is:

1. receive records
2. validate records
3. store records
4. build the sorted index
5. search the index
6. calculate a cumulative priority metric

Sorting establishes the precondition needed by binary search.

### Data structure

`DocumentRecord` stores the domain data.

`DocumentIndex` owns a collection of records and exposes operations for:

- insertion
- index construction
- binary search
- retrieving records
- calculating cumulative priority work

The vector provides contiguous storage and supports efficient sorting and indexed access.

### Sorting

The case study includes merge sort and quicksort independently so their recurrence structures can be compared.

Merge sort uses:

`T(n) = 2T(n/2) + Theta(n)`

Quicksort's recurrence depends on partition quality.

### Searching

Once the records are sorted by ID, binary search reduces the search interval by approximately half at each step:

`T(n) = T(n/2) + Theta(1)`

This gives logarithmic search time.

### Validation

The case study rejects:

- negative document IDs
- negative priorities
- empty categories

This demonstrates an important implementation distinction: mathematical assumptions should be enforced when invalid input would violate the system's invariants.

### Failure conditions

Searching for an absent ID returns `std::nullopt`.

An invalid record causes an exception.

The main function catches standard exceptions and returns a non-zero exit status for an unexpected runtime failure.

### Memory management

The binary-tree demonstration uses dynamically allocated nodes. A dedicated `deleteTree` function recursively releases every node.

The recursive memory-management procedure follows the same structure as the tree itself.

In production C++, smart pointers would often be preferable for ownership management, but raw pointers make the structural recursion explicit in this educational case study.

---

## Recurrence-solving techniques

Several techniques are represented in the implementations.

### Direct expansion

Repeatedly replace the recurrence with its recursive definition until a base case is reached.

This is useful for simple recurrences such as:

`T(n) = T(n - 1) + n`

### Recursion trees

Represent recursive calls as levels of a tree.

This is particularly useful for divide-and-conquer recurrences such as:

`T(n) = 2T(n/2) + n`

### Substitution

Propose a bound and use induction to prove that the recurrence satisfies the bound.

Typical goals include:

`T(n) = O(f(n))`

`T(n) = Omega(f(n))`

or:

`T(n) = Theta(f(n))`

### Master Theorem

For recurrences of the form:

`T(n) = aT(n/b) + f(n)`

the critical exponent is:

`log_b(a)`

The standard polynomial comparison considers the growth of `f(n)` relative to:

`n^(log_b(a))`

The implementations classify the three standard Master-Theorem cases.

---

## Master Theorem cases

For:

`T(n) = aT(n/b) + Theta(n^d)`

let:

`p = log_b(a)`

### Case 1

If:

`d < p`

then:

`T(n) = Theta(n^p)`

The recursive subproblems dominate the non-recursive work.

### Case 2

If:

`d = p`

then:

`T(n) = Theta(n^p log n)`

The work is balanced across recursion levels.

Merge sort is the canonical example:

`T(n) = 2T(n/2) + Theta(n)`

Here:

`a = 2`

`b = 2`

`d = 1`

and:

`log_2(2) = 1`

so the recurrence falls into Case 2.

### Case 3

If:

`d > p`

then, subject to the regularity condition required by the theorem:

`T(n) = Theta(n^d)`

The non-recursive work dominates.

The Master Theorem does not apply automatically to every recurrence. Unequal recursive subproblem sizes, non-polynomial terms, unusual additive terms, and recurrences that violate the theorem's assumptions require other analysis techniques.

---

## Unequal recursive subproblems

Consider:

`T(n) = T(2n/3) + T(n/3) + Theta(n)`

The recursive subproblem sizes are not both `n/b` for the same fixed `b`.

Therefore the basic Master Theorem does not directly apply.

The Python implementation includes an uneven divide-and-conquer function to illustrate this distinction.

In such cases, methods such as recursion-tree analysis, substitution, or more general recurrence-solving techniques may be appropriate.

The exact mathematical assumptions of the chosen method must be checked rather than applying a familiar formula mechanically.

---

## Memoization

Memoization stores results of previously solved subproblems.

Naive Fibonacci follows:

`T(n) = T(n - 1) + T(n - 2) + Theta(1)`

The two recursive branches overlap heavily.

Memoization computes each relevant Fibonacci value once.

The mathematical recurrence remains:

`F(n) = F(n - 1) + F(n - 2)`

but the amount of computational work changes dramatically.

This illustrates a fundamental distinction:

**A recurrence describing a mathematical value is not necessarily the same thing as the recurrence describing the optimized algorithm's running time.**

The same mathematical sequence can have multiple implementations with very different time and space complexity.

---

## Recursive versus iterative implementation

Recursion is often the clearest way to express a recursive definition.

Iteration can be more efficient operationally when the recursion does not provide a necessary structural advantage.

For Fibonacci:

- naive recursion has exponential work
- memoized recursion has approximately linear work
- iterative Fibonacci has linear time and constant auxiliary state

Python does not perform general tail-call optimization, so tail-recursive functions can still consume stack frames.

C++ and JavaScript also have practical stack limits, although the exact limits and runtime behavior vary by implementation.

An algorithm should therefore not be made recursive merely because its mathematical definition is recursive.

---

## Edge cases

Recurrence implementations must define their behavior at boundaries.

Important examples include:

### Empty input

Binary search on an empty collection should terminate immediately.

Merge sort on an empty collection should return an empty collection.

### Singleton input

A one-element collection is already sorted.

### Zero

Many recursive mathematical definitions use zero as the base case.

### Negative arguments

The implementations reject negative values for functions whose domain is defined here as the non-negative integers.

### Missing search values

Binary search returns `-1` in the Python and JavaScript implementations and `-1` or `std::nullopt` in the C++ case-study contexts where appropriate.

### Integer overflow

Fixed-width integer types have finite ranges.

The mathematical expression `2^n` is unbounded over the integers, but a C++ `long long` has a finite maximum value.

Python integers automatically grow to arbitrary precision, subject to memory limitations.

JavaScript's `Number` type represents integers exactly only within its safe-integer range. Large exact integer computations may require `BigInt`.

---

## Common mistakes

### Omitting the base case

A recursive function without a terminating condition may not terminate.

### Using an incorrect base case

Even if recursion terminates, an incorrect base value changes every later result.

### Proving examples instead of proving a general statement

Checking:

`P(0), P(1), ..., P(100)`

does not prove `P(n)` for every integer `n`.

Finite testing verifies an implementation over a finite domain. Mathematical induction establishes a general proposition under its assumptions.

### Confusing induction with recursion

Recursion is a definition or computational technique.

Induction is a proof technique.

They are closely related, but they serve different purposes.

### Applying the Master Theorem mechanically

The recurrence must match the theorem's form and assumptions.

### Ignoring floors and ceilings

Real algorithms frequently use:

`floor(n/2)`

or:

`ceil(n/2)`

These usually do not change many standard asymptotic classifications, but they matter when proving exact identities or handling small inputs.

### Ignoring input-dependent behavior

Quicksort is a major example. Its recurrence depends on partition sizes.

### Ignoring stack usage

A recurrence may predict efficient time while a recursive implementation still has substantial stack-space requirements.

---

## Exact complexity versus asymptotic complexity

A recurrence can be used to derive an exact formula or an asymptotic bound.

For example:

`H(n) = 2H(n - 1) + 1`

with:

`H(0) = 0`

has the exact solution:

`H(n) = 2^n - 1`

Therefore:

`H(n) = Theta(2^n)`

The exact expression gives more information than the asymptotic classification, but asymptotic notation is often more useful for comparing growth rates at large input sizes.

---

## Big-O, Big-Omega, and Big-Theta

### Big-O

`T(n) = O(f(n))`

means that `f(n)` is an asymptotic upper bound up to constant factors beyond a sufficiently large threshold.

### Big-Omega

`T(n) = Omega(f(n))`

means that `f(n)` is an asymptotic lower bound up to constant factors.

### Big-Theta

`T(n) = Theta(f(n))`

means that `f(n)` is both an asymptotic upper and lower bound.

For merge sort:

`T(n) = Theta(n log n)`

describes the asymptotic growth of the running time.

For binary search:

`T(n) = Theta(log n)`

describes the logarithmic reduction in search work.

For worst-case quicksort:

`T(n) = Theta(n^2)`

describes the recurrence generated by maximally unbalanced partitions under the implementation used here.

---

## Correctness and complexity are different questions

A recurrence can analyze how much work an algorithm performs, but it does not automatically establish correctness.

A complete algorithmic analysis may require separate arguments for:

- termination
- functional correctness
- invariants
- time complexity
- space complexity
- input constraints
- failure behavior

Induction is often useful for correctness.

Recurrence analysis is often useful for complexity.

The two methods frequently appear together in recursive algorithm design.

---

## Security considerations

Recursion itself is not a security mechanism.

In software systems, recursive algorithms can introduce operational risks.

### Resource exhaustion

Deep recursion can consume stack memory and terminate unexpectedly.

### Untrusted input

If an attacker can control input that determines recursion depth, the application should enforce reasonable limits where appropriate.

### Algorithmic complexity attacks

An attacker may attempt to provide inputs that trigger an unfavorable recurrence.

Quicksort is a well-known example because poor pivot behavior can produce highly unbalanced recursive partitions.

### Denial of service

Algorithms with exponential recurrence growth can become impractical for surprisingly small input sizes.

Systems processing untrusted input should establish input limits, time budgets, or algorithm choices appropriate to the threat model.

### Integer overflow

When recurrence calculations are implemented using fixed-width integer types, overflow can produce incorrect values.

C++ implementations should select suitable integer types and validate ranges when exact arithmetic is required.

---

## Performance considerations

The principal performance questions are:

- How many recursive subproblems are generated?
- How quickly does each subproblem shrink?
- How much non-recursive work occurs at each level?
- How deep is the recursion tree?
- Are subproblems repeated?
- How much auxiliary memory is required?

### Binary search

Time:

`Theta(log n)`

Auxiliary recursive stack:

`O(log n)` in the recursive implementation.

### Merge sort

Time:

`Theta(n log n)`

Auxiliary memory:

`O(n)` for the vector-based merge implementation, in addition to recursion overhead.

### Naive Fibonacci

Time:

exponential

The exact growth depends on the recurrence and implementation details.

### Memoized Fibonacci

Time:

approximately `O(n)`

Auxiliary storage:

`O(n)`

### Iterative Fibonacci

Time:

`O(n)`

Auxiliary state:

`O(1)`

### Quicksort

Balanced recursion:

`Theta(n log n)`

Worst-case recursion:

`Theta(n^2)`

The stack depth can also become linear in the worst case.

---

## Implementation considerations

### Python

Python is convenient for expressing mathematical recurrences directly.

Its arbitrary-precision integers are useful when the mathematical value exceeds ordinary machine-integer ranges, although very large calculations can still consume substantial resources.

Python recursion is constrained by interpreter recursion limits and stack behavior.

### JavaScript

JavaScript's recursive functions closely resemble mathematical definitions.

`Map` is convenient for memoization.

For exact integer computations outside the safe `Number` range, `BigInt` should be considered.

### C++

C++ provides explicit control over:

- integer types
- memory
- data structures
- ownership
- recursion
- exception handling

The trade-off is that the programmer must manage more low-level implementation details.

---

## Design principles demonstrated

### Match implementation structure to mathematical structure

A direct recursive implementation is often useful when teaching or validating a recursive definition.

### Separate correctness from optimization

Memoization changes computational efficiency without changing the mathematical definition.

### Identify the source of each recurrence term

For:

`T(n) = 2T(n/2) + n`

the `2T(n/2)` term represents two recursive subproblems and `n` represents current-level work.

### Treat base cases as first-class requirements

Base cases define both termination and initial mathematical values.

### Check assumptions

A recurrence-solving technique is valid only when its conditions are satisfied.

### Use the simplest suitable implementation

An iterative solution may be preferable when recursion adds stack overhead without providing meaningful structural clarity.

---

## Important distinctions

| Concept | Meaning |
|---|---|
| Recursive definition | Defines an object through smaller instances |
| Recurrence relation | Relates a value to smaller values |
| Recursive algorithm | Computes a result through recursive calls |
| Recurrence for runtime | Describes computational cost recursively |
| Mathematical induction | Proves propositions over an inductively defined domain |
| Strong induction | Allows all earlier cases in the inductive step |
| Structural induction | Follows the recursive structure of an object |
| Recursion tree | Visualizes recursive subproblems and work |
| Closed form | Expresses a recurrence-defined quantity directly |
| Memoization | Avoids repeated computation of overlapping subproblems |
| Master Theorem | Solves selected divide-and-conquer recurrence forms |

---

## Relationship between recursion and induction

Recursion and induction are connected by a deep structural relationship.

A recursive program typically solves a problem by reducing it to smaller problems.

An inductive proof establishes a property by reducing the proof obligation to smaller or previously established cases.

A recursive definition can therefore suggest the natural structure of an induction proof.

For example, a binary tree is recursively constructed from subtrees. A structural induction proof naturally assumes the desired property for those subtrees and then proves it for the larger tree.

This correspondence is especially important in algorithms, data structures, formal verification, and theoretical computer science.

---

## Practical applications

Recurrence relations and induction-based reasoning appear in:

- divide-and-conquer algorithms
- sorting
- searching
- tree algorithms
- dynamic programming
- combinatorial counting
- algorithm correctness proofs
- complexity analysis
- parsing
- compiler structures
- recursive data processing
- distributed algorithms
- computational geometry
- graph algorithms
- formal methods
- discrete mathematics

The techniques are useful whenever a problem has a natural relationship between an instance and smaller instances.

---

## Limitations of recurrence analysis

A recurrence is an abstraction.

It may ignore:

- cache behavior
- memory bandwidth
- branch prediction
- allocation costs
- input parsing
- operating-system scheduling
- parallel execution
- hardware-specific behavior
- constant factors
- implementation-specific library details

Asymptotic analysis remains useful because it describes growth as input size becomes large, but it should not be mistaken for a complete performance model.

Similarly, a recurrence can be mathematically correct while its implementation is incorrect because of boundary errors, overflow, invalid input handling, or incorrect base cases.

---

## Verification strategy used in the implementations

The programs include executable assertions and checks for:

- recursive versus closed-form sequence values
- recursive versus memoized Fibonacci
- recursive versus iterative Fibonacci
- binary-search correctness
- sorting correctness
- induction-oriented algebraic transformations
- strong-induction examples
- structural tree identities
- recurrence-tree behavior
- Master-Theorem classifications
- substitution-style finite bounds
- application-level input validation
- missing-record handling

These checks provide practical evidence that the implementations behave as intended for selected finite inputs.

They do not replace formal proofs.

---

## Files and their roles

### Python script

The Python implementation is the primary mathematical laboratory. It provides a large collection of recursive definitions, recurrence examples, proof-oriented abstractions, algorithm implementations, and finite verification routines.

### JavaScript file

The JavaScript implementation demonstrates that the same mathematical structures can be represented with functions, classes, arrays, `Map` objects, and runtime assertions.

### C++ program

The C++ implementation develops an industry-style document-indexing case study while integrating recursive algorithms, data structures, validation, memory management, and recurrence analysis.

The three implementations therefore demonstrate the distinction between mathematical recurrence structure and language-specific engineering decisions.

---

## Example recurrence reference table

| Problem | Recurrence | Result |
|---|---|---|
| Factorial work | `T(n) = T(n-1) + Theta(1)` | `Theta(n)` |
| Binary search | `T(n) = T(n/2) + Theta(1)` | `Theta(log n)` |
| Merge sort | `T(n) = 2T(n/2) + Theta(n)` | `Theta(n log n)` |
| Towers of Hanoi | `H(n) = 2H(n-1) + 1` | `Theta(2^n)` |
| Worst-case quicksort | `T(n) = T(n-1) + Theta(n)` | `Theta(n^2)` |
| Naive Fibonacci | `T(n) = T(n-1) + T(n-2) + Theta(1)` | Exponential |
| Memoized Fibonacci | each state computed once | `O(n)` time |

---

## Conceptual workflow for recurrence proofs

A rigorous recurrence analysis can be organized as follows:

1. Define the quantity precisely.
2. State the domain.
3. Identify every base case.
4. Identify the recursive relationship.
5. Determine whether the recurrence describes values or computational cost.
6. Expand the recurrence when direct iteration is informative.
7. Construct a recursion tree when the recursive structure is divide-and-conquer.
8. Select a suitable solving method.
9. Check the assumptions of that method.
10. Use induction when proving the proposed closed form or asymptotic bound.
11. Check boundary conditions.
12. Distinguish finite computational verification from a general mathematical proof.
13. Consider implementation limits such as stack depth and integer range.
14. Analyze time and auxiliary space separately.

This workflow prevents a common error: obtaining a plausible formula without proving that the formula actually satisfies the original recurrence and its base cases.

---

## Exact recurrence versus implementation recurrence

A mathematical sequence may have one recurrence while an implementation has a different running-time recurrence.

For example, Fibonacci satisfies:

`F(n) = F(n-1) + F(n-2)`

The naive implementation performs both recursive calls every time.

Memoization changes the computation by ensuring each subproblem is solved once.

Iteration changes the implementation again by storing only the necessary previous values.

The mathematical object has not changed. The computational process has.

This distinction is essential when moving from discrete mathematics to algorithm analysis.

---

## Formal proof versus executable verification

An executable program can test many values.

For example, a program can verify:

`T(n) = n(n + 1)/2`

for `n = 0` through `1000`.

That does not establish the statement for all natural numbers.

A formal induction proof instead establishes:

- the base case
- the general inductive implication

The code is valuable for detecting implementation mistakes and illustrating proof transformations, but mathematical validity comes from the logical argument and its assumptions.

---

## Production relevance

Recurrence reasoning is directly relevant to production engineering when recursive or divide-and-conquer algorithms are used.

Before deploying such an algorithm, engineers may need to determine:

- expected input sizes
- maximum recursion depth
- worst-case input behavior
- memory requirements
- time complexity
- failure conditions
- integer ranges
- whether memoization is affordable
- whether an iterative alternative is preferable
- whether adversarial inputs can trigger unfavorable recursion
- whether workload characteristics justify the selected algorithm

The C++ document-index case study demonstrates this transition from mathematical recurrence to a software component with validation, data modeling, sorting, searching, error handling, and resource considerations.

---

## Core mathematical takeaway

A recurrence provides a precise relationship between a problem and smaller problems.

An induction proof provides a way to establish that a recursively described proposition holds across its domain.

For recursive algorithms, these ideas combine:

`recursive structure -> recurrence -> recurrence analysis -> proof of bound or correctness`

Understanding each stage separately makes it possible to distinguish a recursive definition, an algorithm's runtime behavior, and the mathematical proof used to justify the resulting claim.
