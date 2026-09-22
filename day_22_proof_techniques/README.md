# Proof techniques

## Topic introduction

Proof techniques are systematic methods for establishing that a mathematical statement follows from definitions, assumptions, axioms, and previously established results. A proof is different from experimentation. A collection of examples can provide evidence that a statement may be true, while a proof explains why the statement must hold throughout the domain specified by the theorem.

A rigorous proof begins by identifying the logical structure of a proposition. Statements may contain implications, equivalences, universal quantifiers, existential quantifiers, negations, and combinations of these forms. The logical structure strongly influences the appropriate proof strategy. A statement of the form `P -> Q` may be proved directly or through its contrapositive. An `if and only if` statement requires both directions. An existential statement requires a witness or another argument establishing existence. A uniqueness statement normally requires both existence and a proof that two possible candidates cannot be different.

The three implementations in this study approach proof techniques from different computational perspectives. The Python program provides a broad mathematical laboratory containing direct proofs, contradiction, cases, induction, strong induction, the well-ordering principle, the pigeonhole principle, invariants, extremal reasoning, counterexamples, and algorithmic correctness. The JavaScript program emphasizes executable logic, asynchronous validation, structured proof records, recursion, and algorithmic behavior. The C++ implementation develops a realistic network-routing case study in which mathematical reasoning is connected to graph invariants, reachability, Dijkstra's algorithm, validation, failure conditions, and correctness contracts.

## Fundamental concepts

### Proposition, predicate, hypothesis, and conclusion

A proposition is a statement that has a definite truth value. For example, `8 is even` is true, while `9 is even` is false.

A predicate is an expression whose truth depends on one or more variables. The expression `n is even` is a predicate over integers. Once a value is substituted for `n`, it becomes a proposition.

An implication has the form `P -> Q`, read as "if P, then Q". The hypothesis is `P`, and the conclusion is `Q`. The implication is false only when `P` is true and `Q` is false.

The Python and JavaScript programs implement an `implication` function to make this logical rule executable. The truth table demonstrates that logical implication is not equivalent to ordinary causal language. When the hypothesis is false, the implication is considered true under classical propositional logic.

A biconditional has the form `P <-> Q` and means that both implications hold:

`P -> Q`

and

`Q -> P`

The implementations use biconditional reasoning for the statement that an integer is divisible by 6 if and only if it is divisible by both 2 and 3.

### Definitions matter

A proof should use mathematical definitions precisely. For example, an integer `n` is even when there exists an integer `k` such that `n = 2k`. This definition gives a direct route to many parity proofs.

If `a` and `b` are even, then there are integers `m` and `n` such that:

`a = 2m`

`b = 2n`

Therefore:

`a + b = 2m + 2n = 2(m+n)`

Since `m+n` is an integer, `a+b` is even.

The Python and JavaScript direct-proof examples explicitly calculate the witness `m+n`.

## Direct proof

A direct proof begins with the hypotheses and transforms them through valid deductions until the desired conclusion is obtained.

The general structure is:

1. Assume the hypotheses.
2. Apply definitions and established results.
3. Perform valid algebraic or logical transformations.
4. Reach the conclusion.

Direct proofs are often the most transparent approach when the hypothesis naturally contains information that can be transformed into the desired conclusion.

The Python implementation of `direct_proof_sum_of_even_numbers` demonstrates this structure computationally. It validates that both inputs are even, extracts the integers obtained after dividing by two, and reconstructs the sum in the form `2(m+n)`.

The JavaScript implementation follows the same mathematical reasoning while representing the result as an object containing a witness and a validity flag.

A computational demonstration should not be confused with the mathematical proof itself. Testing `14 + 22`, `18 + 26`, or any other finite collection of examples does not establish the theorem for all even integers. The algebraic argument establishes the general result.

## Proof by contrapositive

The contrapositive of:

`P -> Q`

is:

`not Q -> not P`

An implication and its contrapositive are logically equivalent.

This technique is useful when proving the original implication directly is awkward but showing that failure of the conclusion forces failure of the hypothesis is straightforward.

Consider:

"If an integer is divisible by 4, then it is even."

The contrapositive is:

"If an integer is not even, then it is not divisible by 4."

An odd integer cannot be divisible by 4 because every multiple of 4 has the form `4k = 2(2k)`, which is even.

The Python and JavaScript implementations calculate both the original implication and its contrapositive over finite test ranges. This demonstrates logical equivalence while keeping the mathematical distinction clear.

A common mistake is confusing the contrapositive with the converse. The converse of `P -> Q` is `Q -> P`. The converse is not generally equivalent to the original statement.

For example:

"If a number is divisible by 4, then it is even"

does not imply:

"If a number is even, then it is divisible by 4."

The number 6 is an immediate counterexample to the converse.

## Proof by contradiction

Proof by contradiction begins by assuming that the desired conclusion is false and then deriving an impossibility.

The classical proof that the square root of 2 is irrational follows this structure.

Assume:

`sqrt(2) = p/q`

where `p` and `q` are positive integers with no common factor.

Squaring gives:

`p² = 2q²`

Therefore `p²` is even, which implies that `p` is even. Write:

`p = 2k`

Substitution produces:

`4k² = 2q²`

and therefore:

`q² = 2k²`

so `q` is also even.

This means both `p` and `q` have a factor of 2, contradicting the assumption that the fraction was in lowest terms.

The Python implementation records the logical structure of this argument rather than attempting to approximate irrationality with floating-point arithmetic. This is an important implementation decision because numerical approximation cannot establish irrationality.

Contradiction proofs are especially useful when the negation of the desired result creates a restrictive structure that eventually violates a known property.

## Proof by cases

Proof by cases divides a domain into exhaustive alternatives and establishes the desired result separately in each case.

Parity is a standard example. Every integer is either even or odd.

For an integer `n`:

Case 1:

`n = 2k`

Then:

`n² = 4k²`

so `n²` is even.

Case 2:

`n = 2k + 1`

Then:

`n² = 4k² + 4k + 1`

so `n²` is odd.

Therefore an integer and its square have the same parity.

A valid case analysis requires the cases to cover the entire domain relevant to the theorem. It is not sufficient to choose convenient examples. The Python and JavaScript programs explicitly distinguish the even and odd cases.

Case analysis also appears in the C++ routing case study. Network nodes are classified according to incoming and outgoing connectivity. The classification illustrates how a finite set of mutually distinguishable structural cases can be handled systematically.

## Biconditional proofs

An `if and only if` theorem contains two implications.

To prove:

`P iff Q`

prove:

`P -> Q`

and:

`Q -> P`

For integers, the statement:

`6 divides n iff 2 divides n and 3 divides n`

requires both directions.

The first direction follows because if `n = 6k`, then:

`n = 2(3k)`

and:

`n = 3(2k)`

The reverse direction uses the fact that 2 and 3 are relatively prime and their least common multiple is 6.

The implementations test both directions independently. This distinction is important because proving only one direction establishes an implication, not an equivalence.

## Existence proofs

An existential proposition has the form:

`There exists x such that P(x).`

A constructive existence proof supplies a specific object satisfying the property.

For example:

"There exists an integer whose square is divisible by 16."

Choose:

`x = 4`

Then:

`x² = 16`

and 16 divides 16.

The Python and JavaScript programs expose the witness directly.

Not every existence theorem requires a simple explicit witness. Some existence proofs establish that an object must exist without constructing it directly. Such proofs can involve counting, compactness, contradiction, or other mathematical principles.

## Uniqueness proofs

A uniqueness theorem normally has two components:

1. Prove that at least one object exists.
2. Prove that any two objects satisfying the required property must be equal.

For the additive identity in the integers, suppose `e` is an additive identity. Then:

`0 + e = 0`

Since `0 + e = e`, it follows that:

`e = 0`

Therefore any additive identity must equal zero.

The Python program presents this as a uniqueness argument. The central idea is that a uniqueness proof compares arbitrary candidates rather than merely showing that one candidate works.

## Counterexamples

A universal statement has the general form:

`For every x, P(x).`

To disprove such a statement, it is sufficient to find one valid value for which `P(x)` is false.

The statement:

"Every prime number is odd"

is false because 2 is prime and even.

The Python and JavaScript programs implement counterexample search. The C++ case study also uses validation failures to illustrate how one violating input can invalidate an assumed property.

Counterexamples are particularly valuable during theorem development. They can expose an incorrect conjecture, identify missing hypotheses, and reveal why a seemingly reasonable generalization fails.

A counterexample does not prove the negation of every possible related statement. It specifically disproves the universal proposition whose domain and property have been stated.

## Mathematical induction

Mathematical induction is designed for propositions indexed by the positive integers or another well-founded sequence.

A standard induction proof contains:

### Base case

Show the proposition holds for the initial value.

### Induction hypothesis

Assume the proposition holds for an arbitrary index `k`.

### Inductive step

Use the hypothesis to establish the proposition for `k+1`.

Consider:

`1 + 2 + ... + n = n(n+1)/2`

The base case is:

`1 = 1(2)/2`

Assuming:

`1 + 2 + ... + k = k(k+1)/2`

then:

`1 + 2 + ... + k + (k+1)`

equals:

`k(k+1)/2 + (k+1)`

which simplifies to:

`(k+1)(k+2)/2`

This proves the next case.

The Python and JavaScript programs calculate the iterative sum and compare it with the closed-form expression for finite values. These calculations illustrate the theorem, while the induction argument provides the general proof.

A frequent mistake is treating repeated testing as induction. Testing values from 1 through 10 does not prove a theorem for every positive integer. Induction requires a logical base case and a valid implication from one case to the next.

## Strong induction

Strong induction strengthens the induction hypothesis.

Instead of assuming only that the theorem holds for `k`, strong induction assumes that it holds for every relevant value smaller than `k`.

This is useful when the construction of the current case naturally depends on several smaller cases.

The prime factorization theorem provides a useful example. Every integer `n >= 2` is either prime or composite. If it is composite, it can be written:

`n = ab`

where both factors are smaller than `n`.

The factorization of those smaller factors can then be obtained recursively.

The Python and JavaScript programs implement recursive prime factorization. The recursion mirrors the logical structure of strong induction because the recursive argument is strictly smaller than the original integer.

The critical termination property is that a recursive call does not remain at the same value. A proof of termination often uses a well-founded measure that decreases on every recursive step.

## Well-ordering principle

The well-ordering principle states that every nonempty set of positive integers contains a least element.

It is closely related to mathematical induction.

A computational search that scans positive integers from smallest to largest illustrates this principle:

`1, 2, 3, 4, ...`

When the first value satisfying a predicate is found, no smaller positive integer satisfies it.

The Python implementation searches for the smallest positive integer whose square exceeds 100. The resulting value is 11.

The program demonstrates the search mechanism, while the mathematical principle explains why a nonempty set of positive integers has a least member.

Well-ordering arguments frequently appear in proofs involving minimal counterexamples. A contradiction can be obtained by assuming that a counterexample exists, selecting the smallest counterexample, and showing that a smaller counterexample must also exist.

## Pigeonhole principle

The pigeonhole principle states that if more than `n` objects are placed into `n` categories, at least one category contains at least two objects.

The principle is simple but powerful.

If five objects are placed into four boxes, a collision is unavoidable.

The Python, JavaScript, and C++ programs demonstrate this concept using modular buckets or hash buckets. When multiple objects map to the same bucket, a collision occurs.

The C++ routing case study intentionally uses a small number of hash buckets so that the structural principle becomes visible.

The important distinction is between guaranteed collision and observed collision. If the number of objects exceeds the number of buckets, a collision is mathematically guaranteed. If fewer objects are present, a collision may still occur, but it is not forced by the basic pigeonhole principle.

## Invariants

An invariant is a property that remains true throughout a process.

Loop invariants are central to proving algorithm correctness.

A typical proof has three parts:

1. Initialization: show the invariant is true before the loop begins.
2. Maintenance: show that one iteration preserves the invariant.
3. Termination: show that when the loop ends, the invariant plus the termination condition establishes the desired result.

The Python implementation demonstrates an invariant while removing elements from a sequence. The sum of removed elements plus the sum of remaining elements remains equal to the original sum.

The Euclidean algorithm provides a stronger mathematical example:

`gcd(a,b) = gcd(b, a mod b)`

The algorithm repeatedly applies this identity until the second argument becomes zero. The remaining first argument is the greatest common divisor.

The C++ routing case study uses invariants in breadth-first search and Dijkstra's algorithm. These invariants connect abstract proof reasoning directly to practical software correctness.

## Algorithmic correctness

Algorithm correctness commonly involves two questions:

### Partial correctness

If the algorithm terminates, does its result satisfy the specification?

### Termination

Does the algorithm eventually stop for every valid input?

Together these establish total correctness.

Binary search provides a clear example.

For a sorted array, the algorithm maintains the invariant:

"If the target exists, it remains inside the current search interval."

Each iteration eliminates approximately half of the remaining candidates.

The Python, JavaScript, and C++ examples all use this reasoning. The C++ program applies the same proof-oriented thinking to Dijkstra's shortest-path algorithm.

## C++ case study: network routing system

The C++ program models a directed network containing gateways, routers, databases, and backup infrastructure.

The network is represented using an adjacency list:

`source -> destination, weight`

Each edge has a positive weight representing a routing cost.

The implementation uses:

- `unordered_map` for adjacency storage
- `vector` for outgoing edges
- `queue` for breadth-first traversal
- `priority_queue` for Dijkstra's algorithm
- `unordered_set` for visited nodes
- `optional` for values that may not exist
- exceptions for invalid inputs and violated assumptions

The design separates network representation from algorithms that operate on the network.

### Network invariants

The first invariant requires every edge to have a positive weight and a destination that exists in the network.

This invariant is not merely a formatting preference. It is connected to the correctness assumptions of the shortest-path algorithm.

Dijkstra's algorithm requires nonnegative edge weights. The case study uses strictly positive weights, which satisfies the requirement.

If an invalid edge were accepted, the program would violate the precondition under which its shortest-path proof is valid.

### Reachability

Breadth-first search determines whether a destination is reachable from a source.

Its invariant is:

"Every node in the visited set is reachable from the source."

Whenever a new node is added to the visited set, it has been discovered through an existing edge from an already reachable node. This preserves the invariant.

The algorithm terminates because every node is added to the visited set at most once.

Its time complexity is:

`O(V + E)`

where `V` is the number of vertices and `E` is the number of edges.

### Dijkstra's algorithm

Dijkstra's algorithm finds shortest paths from a source in a graph with nonnegative edge weights.

The implementation initializes every distance to infinity and the source distance to zero.

The priority queue always selects the currently smallest tentative distance.

The key correctness argument is based on a greedy invariant:

"For every permanently processed vertex, the recorded distance is the shortest possible distance from the source."

Because edge weights are nonnegative, a shorter path through an unprocessed vertex cannot unexpectedly produce a smaller distance after the current minimum has been selected.

The implementation also handles stale priority-queue entries. An older queue entry may contain a distance that is no longer the best known value. Such entries are ignored.

With a binary heap, the standard complexity is:

`O((V + E) log V)`

for the adjacency-list implementation.

### Path reconstruction

Dijkstra's algorithm records a predecessor for each improved destination. The predecessor map allows the final route to be reconstructed by walking backward from the destination to the source.

The implementation checks for a broken predecessor chain and protects against unexpected cycles.

The reconstructed route is independently evaluated with `calculatePathCost`. The calculated route cost must equal the distance reported by Dijkstra's algorithm.

This creates a useful postcondition:

`reconstructed path cost = computed shortest distance`

The equality acts as a consistency check between two components of the implementation.

## Python implementation

The Python program functions as the broadest mathematical study file.

It demonstrates:

- propositions
- predicates
- implication
- biconditional logic
- direct proof
- contrapositive
- contradiction
- cases
- existence
- constructive witnesses
- uniqueness
- counterexamples
- induction
- strong induction
- well-ordering
- pigeonhole reasoning
- invariants
- extremal reasoning
- binary-search correctness
- exhaustive finite verification
- Euclidean algorithm correctness
- structural induction

The `BinaryTreeNode` example provides a structural-induction perspective. An empty tree forms the base case. A nonempty tree consists of a root and two subtrees, allowing the recursive implementation to follow the same structure as the proof.

The Python file also includes a proof checklist that emphasizes hypotheses, quantifiers, definitions, proof strategy, boundary cases, and logical validity.

## JavaScript implementation

The JavaScript file emphasizes executable representations of proof structures.

Its logical functions demonstrate implication and biconditional reasoning. The direct proof, contrapositive, cases, counterexample, existence, and induction sections show how mathematical statements can be encoded as executable predicates.

The asynchronous validation example is useful from an application-development perspective. It shows that mathematical validation can be incorporated into an asynchronous workflow while preserving explicit error handling.

The `ProofRecord` class demonstrates an object-oriented representation of a proof statement, technique, validity status, and justification.

The JavaScript binary-search implementation checks its sorted-input precondition before executing the algorithm. This illustrates a software-engineering principle closely connected to mathematical proof: an algorithm's correctness depends on clearly stated assumptions.

The performance comparison also demonstrates that correctness and efficiency are distinct properties. An algorithm can be correct but computationally inappropriate for a particular scale of input.

## Important distinctions

### Proof versus example

An example demonstrates that a proposition works for one input.

A proof demonstrates why it works for every input in the stated domain.

### Proof versus computation

A program can exhaustively verify a finite domain. It cannot normally prove a theorem over an infinite domain simply by testing a large number of cases.

### Contrapositive versus converse

For `P -> Q`:

- Contrapositive: `not Q -> not P`
- Converse: `Q -> P`

The contrapositive is logically equivalent to the original implication. The converse is not generally equivalent.

### Existence versus uniqueness

Existence means at least one valid object exists.

Uniqueness means no more than one valid object exists.

A uniqueness theorem generally requires both.

### Necessary versus sufficient conditions

If `P -> Q`, then `P` is sufficient for `Q`, while `Q` is necessary for `P`.

This terminology becomes particularly important when interpreting conditions in mathematical theorems and software specifications.

### Verification versus validation

Verification asks whether an implementation satisfies its stated specification.

Validation asks whether the specification and implementation address the intended problem.

Proof techniques primarily support verification, while system design also requires careful validation of requirements.

## Common mistakes

### Affirming the consequent

Invalid reasoning:

`P -> Q`

`Q`

Therefore:

`P`

The fact that `Q` occurred does not establish that `P` caused it or that `P` must be true.

### Assuming the conclusion

A proof must not use the conclusion as an unstated premise. Circular reasoning can appear convincing when intermediate statements merely restate what the proof is supposed to establish.

### Incomplete induction

An induction proof without a valid base case is incomplete.

An induction proof with a base case but no logically valid induction step is also incomplete.

### Insufficient cases

Cases must cover the relevant domain. Selecting a few convenient cases does not constitute exhaustive case analysis.

### Testing instead of proving

Testing thousands of values can reveal a counterexample, but passing tests do not automatically establish a universal theorem.

### Ignoring preconditions

Algorithms such as binary search and Dijkstra's algorithm depend on assumptions. Binary search requires sorted data. Dijkstra's standard correctness argument requires nonnegative edge weights.

### Using numerical approximation for exact claims

Floating-point arithmetic is unsuitable for proving statements such as the irrationality of square root of 2. Exact symbolic reasoning is required.

## Edge cases and exceptions

Proofs and implementations must address boundary conditions.

For parity, zero is even because it is divisible by 2.

For prime factorization, values below 2 are not prime and therefore require explicit handling.

For binary search, an empty array is a valid input and should produce "not found" rather than an indexing error.

For network routing, an unknown node must be rejected or reported as unreachable according to the API contract.

For Dijkstra's algorithm, negative edges violate the algorithm's standard correctness assumptions. The C++ case study rejects invalid edge weights at insertion time.

For uniqueness proofs, it is important to distinguish "there is at most one" from "there is exactly one". The latter requires existence as well.

## Performance considerations

Proof selection and algorithm design are related but distinct.

A direct proof may be mathematically simple while an implementation based on brute-force enumeration may be computationally expensive.

Binary search demonstrates how a correctness invariant can coexist with logarithmic search complexity.

The Euclidean algorithm provides an efficient implementation of greatest-common-divisor computation. Each iteration reduces the problem using the remainder operation.

BFS operates in `O(V + E)` time with an adjacency-list representation.

Dijkstra's algorithm using a binary heap operates in approximately `O((V + E) log V)` time.

Prime factorization by trial division is suitable for educational examples but is not an efficient general-purpose integer-factorization strategy for very large integers.

Exhaustive verification has complexity proportional to the size of the tested domain. For an infinite domain, exhaustive verification cannot be completed by finite execution.

## Security and reliability considerations

Proof techniques are relevant to software security because security-critical code depends on assumptions about inputs, state transitions, and invariants.

Input validation can enforce mathematical preconditions before an algorithm executes.

Invariants can identify states that should never occur during normal execution.

Assertions can detect violations during testing and development.

Postcondition checks can compare independently derived results.

Counterexample generation can expose incorrect assumptions.

A proof does not automatically establish that a complete software system is secure. Real systems also involve memory safety, authentication, authorization, concurrency, cryptographic assumptions, implementation errors, deployment configuration, and external dependencies.

Formal reasoning is strongest when the specification itself is precise and the implementation can be related clearly to that specification.

## Implementation considerations

The Python implementation prioritizes readability and broad mathematical coverage.

The JavaScript implementation emphasizes executable logic, application-oriented validation, asynchronous execution, and object-oriented representation.

The C++ implementation emphasizes explicit data structures, type safety, exception handling, algorithmic performance, and an industry-style graph-processing scenario.

These differences demonstrate that proof techniques are independent of a programming language. The mathematical argument can remain stable while the implementation model changes.

The same invariant can appear in different programming environments. The representation changes, but the logical obligation remains.

## Practical applications

Proof techniques appear throughout computer science and engineering.

In algorithms, proofs establish correctness and complexity properties.

In data structures, invariants establish that operations preserve representation requirements.

In databases, constraints and transaction invariants help maintain consistency.

In networking, reachability, routing, and protocol state machines can be analyzed using invariants and state-transition reasoning.

In cryptography, security arguments establish what an adversary can or cannot infer under specified assumptions.

In distributed systems, invariants and impossibility arguments help characterize system behavior under failures and concurrency.

In software verification, preconditions and postconditions connect implementation behavior to specifications.

In formal methods, mathematical proof can be used to establish properties of programs and hardware systems with substantially greater rigor than ordinary testing.

## Best practices for writing proofs

State the proposition precisely before beginning the argument.

Identify the domain of every variable.

Separate hypotheses from the conclusion.

Use definitions explicitly when they provide the bridge between assumptions and conclusions.

Choose the proof technique based on the structure of the proposition rather than forcing every theorem into the same method.

For direct proofs, make each transformation explicit enough to verify.

For contradiction, state the assumption being negated and identify the exact contradiction.

For contrapositive proofs, clearly state the transformed implication.

For case analysis, establish that the cases are exhaustive.

For induction, prove the base case and preserve the induction hypothesis correctly.

For existence proofs, identify the witness or the principle establishing existence.

For uniqueness proofs, compare arbitrary candidates rather than only examining one candidate.

For algorithm proofs, define invariants, preconditions, postconditions, and termination arguments.

Use counterexamples to test conjectures before investing in a full proof.

Avoid treating computational experiments as substitutes for general mathematical reasoning.

## Relationship between mathematical proof and program correctness

A program can embody a mathematical argument without itself being a complete formal proof.

The binary-search implementation maintains a search interval containing every possible location of the target. The Dijkstra implementation maintains distance information under nonnegative-edge assumptions. The Euclidean algorithm preserves the greatest common divisor.

These structures show how mathematical reasoning becomes an engineering tool.

A well-designed algorithm is easier to verify when its invariants are explicit. A well-designed API is easier to reason about when its preconditions and postconditions are explicit. A well-designed data structure is easier to maintain when its representation invariants are clearly stated.

The central relationship is therefore structural: a proof explains why a property must hold, while an implementation realizes a process whose behavior is intended to satisfy that property.
