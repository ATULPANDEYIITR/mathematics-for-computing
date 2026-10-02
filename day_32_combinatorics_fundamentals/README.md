# Combinatorics Fundamentals

## Scope

This repository develops the foundations of finite counting through three closely related ideas:

- the **sum rule**, which combines mutually exclusive alternatives;
- the **product rule**, which counts sequential choices;
- the **multiplication principle**, the general idea that a complete outcome can be constructed by making choices at multiple stages.

The implementations extend these foundations into dependent choices, permutations, combinations, restricted identifiers, inclusion-exclusion, grid paths, probability, exact large-integer computation, and practical configuration systems.

The central distinction is structural:

> If an outcome belongs to one of several mutually exclusive alternatives, counts are added. If an outcome is assembled by making one choice at each of several stages, the stage counts are multiplied.

That distinction determines which counting method is appropriate.

---

## Counting as a Model of a Finite Outcome Space

A counting problem begins by defining precisely what constitutes one outcome.

Suppose a deployment configuration contains:

- one environment,
- one geographical region,
- one deployment window.

If there are 3 environments, 4 regions, and 5 deployment windows, a complete configuration is a triple such as `("production", "India", "night")`.

The set of all such triples is a Cartesian product. Its cardinality is

`3 × 4 × 5 = 60`.

The important point is that the calculation does not require generating all 60 configurations. The structure of the choices is sufficient.

This is the practical value of combinatorial reasoning: a potentially large outcome space can often be counted from its construction rules without enumerating every element.

---

## The Sum Rule

The sum rule applies when alternatives are mutually exclusive.

If a task can be completed through one of several disjoint categories, and the categories contain `a`, `b`, and `c` possible outcomes, then the total is

`a + b + c`.

For example, suppose a platform exposes:

- 5 public-cloud deployment routes,
- 3 private-cloud deployment routes,
- 2 edge deployment routes.

If a deployment uses exactly one route, the categories are alternatives. The total number of routes is therefore

`5 + 3 + 2 = 10`.

The crucial condition is exclusivity.

If one outcome can simultaneously belong to two categories, direct addition may count it more than once. In that situation, the sum rule alone is insufficient and overlap must be handled explicitly.

The Python implementation demonstrates the sum rule with mutually exclusive environment and service choices. The C++ case study applies the same structure to deployment channels.

---

## The Product Rule and Multiplication Principle

The product rule applies when an outcome is formed by a sequence of choices.

If the first stage has `a` choices, the second has `b` choices, and the third has `c` choices, then the number of complete outcomes is

`a × b × c`.

For example, a deployment configuration might select:

`environment → region → deployment window`

with:

`3 × 4 × 5 = 60`

possible configurations.

This is the multiplication principle.

The choices do not need to be independent in the probabilistic sense. What matters is that every complete outcome can be constructed by following the defined stages, and the number of available choices at each stage is known.

When the number of available choices changes after an earlier choice, the product still applies, but the factors must reflect the changing availability.

---

## Dependent Choices

Consider selecting two distinct reviewers from six available reviewers.

The first reviewer can be selected in 6 ways.

After that selection, only 5 reviewers remain for the second position.

Therefore:

`6 × 5 = 30`

ordered assignments.

This is different from `6 × 6`, because the second choice depends on the first selection.

The Python implementation uses this structure for reviewer assignments. The JavaScript implementation expresses the same mathematical idea through a dedicated function that decreases the available population at every position.

Dependent choices appear frequently in practical combinatorics:

- assigning people to distinct roles;
- creating identifiers without repeated characters;
- selecting ordered resources without replacement;
- arranging distinct objects;
- assigning ranked positions.

The important modeling step is to determine how many choices remain at each stage.

---

## Sum Rule Versus Product Rule

These rules answer different structural questions.

| Structure | Operation | Example |
| --- | --- | --- |
| Mutually exclusive alternatives | Addition | Public cloud OR private cloud |
| Sequential choices | Multiplication | Environment AND region AND window |
| Sequential choices with shrinking availability | Multiplication with changing factors | First reviewer AND second distinct reviewer |
| Overlapping alternatives | Inclusion-exclusion or another overlap method | Users with Python OR SQL skills |

The words **OR** and **AND** can be useful clues, but they are not sufficient by themselves.

The mathematical question is whether the alternatives are disjoint and whether a complete outcome is formed by selecting components from multiple stages.

---

## Cartesian Products

A Cartesian product constructs every possible combination by taking one element from each input collection.

For example:

`{development, staging} × {India, Europe} × {rolling, blue-green}`

contains:

`2 × 2 × 2 = 8`

configurations.

The JavaScript implementation contains a reusable `cartesianProduct` function. It constructs the combinations explicitly and then compares the number of generated configurations with the product-rule calculation.

This illustrates two complementary approaches:

- **Enumeration** produces every actual outcome.
- **Counting** determines how many outcomes exist without producing them.

Enumeration is useful for small spaces and verification. Counting formulas become essential when the space is too large to enumerate.

---

## Permutations

A permutation counts ordered selections without replacement.

Selecting `r` distinct objects from `n` objects gives:

`P(n,r) = n × (n-1) × ... × (n-r+1)`.

For example:

`P(6,2) = 6 × 5 = 30`.

Order matters.

If reviewers A and B are assigned to two different roles, `(A,B)` and `(B,A)` are different assignments.

The Python program implements permutation counting iteratively. The C++ case study uses the same principle for reviewer-role assignments.

This extension follows directly from the product rule because every position represents another stage with fewer available choices.

---

## Combinations

A combination counts selections where order does not matter.

The standard formula is:

`C(n,r) = n! / (r!(n-r)!)`.

For example:

`C(5,2) = 10`.

The pair `{A,B}` is the same selection as `{B,A}`.

The relationship between permutations and combinations is important:

`P(n,r) = C(n,r) × r!`.

The permutation first counts ordered selections. Dividing by the number of possible orderings removes the ordering distinction.

The Python implementation uses `itertools.combinations` to enumerate small examples and `math.comb` for the mathematical calculation.

The JavaScript implementation uses an exact `BigInt` implementation so that large integer results are not silently rounded by the floating-point `Number` type.

---

## Restricted Counting

Many practical counting problems impose restrictions.

For a four-digit code:

- the first digit cannot be zero;
- the remaining positions may contain any digit;
- repetition may or may not be allowed.

If repetition is allowed, the count is:

`9 × 10 × 10 × 10`.

The first position has 9 choices because zero is excluded. Each subsequent position has 10 choices.

If repetition is forbidden, the count becomes:

`9 × 9 × 8 × 7`.

After choosing the first digit, only 9 unused digits remain for the second position, followed by 8 and then 7.

The Python and JavaScript implementations use these changing factors directly instead of generating every possible code.

---

## Repeated Elements

When objects are indistinguishable, ordinary permutation counting can overcount.

For the word `LEVEL`, there are five positions, but `L` occurs twice and `E` occurs twice.

The number of distinct arrangements is:

`5! / (2! × 2!) = 30`.

The denominator removes duplicate arrangements created by exchanging identical copies.

The Python implementation computes element frequencies using a dictionary and then divides by the factorial of each repeated frequency.

This is different from the distinct-object permutation problem because the identity of repeated objects cannot be used to distinguish arrangements.

---

## Inclusion-Exclusion

The sum rule assumes disjoint sets.

When two sets overlap, direct addition counts the intersection twice.

For sets `A` and `B`:

`|A ∪ B| = |A| + |B| - |A ∩ B|`.

For example, suppose:

- 80 developers know Python;
- 65 developers know SQL;
- 35 developers know both.

The number who know Python or SQL is:

`80 + 65 - 35 = 110`.

The subtraction is necessary because the 35 developers with both skills were included once in the Python count and once in the SQL count.

The Python, JavaScript, and C++ implementations each include an explicit inclusion-exclusion calculation with validation that the intersection cannot exceed either participating set.

Inclusion-exclusion is therefore not another version of the product rule. It addresses a different structural issue: overlapping alternatives.

---

## Grid Path Counting

A shortest path through a rectangular grid can be represented as a sequence of right and down moves.

Suppose a path requires:

- 4 right moves;
- 3 down moves.

Every path contains 7 moves. The problem is to determine which 4 of the 7 positions contain right moves.

Therefore:

`C(7,4) = 35`.

The Python and JavaScript implementations calculate this without enumerating the paths.

This example demonstrates how a product-style sequence can lead naturally to a combination problem when the order of identical move types is not independently labeled.

---

## Counting and Probability

Counting provides the size of a finite sample space when outcomes are equally likely.

If there are `N` total outcomes and `F` favorable outcomes, then:

`P(event) = F / N`.

For two-digit numbers from 10 through 99, there are 90 possible outcomes.

Nine of them are multiples of ten:

`10, 20, ..., 90`.

Therefore:

`P(multiple of 10) = 9 / 90 = 0.1`.

The probability calculation itself is simple. The combinatorial work lies in defining and counting the complete outcome space and the favorable subset.

The Python implementation validates both values before performing the division, preventing an empty sample space or an impossible favorable count from being silently accepted.

---

## Python Implementation

The Python program is organized around reusable counting functions rather than a collection of unrelated syntax demonstrations.

The `sum_rule` function validates non-negative integer cardinalities and adds mutually exclusive alternatives.

The `product_rule` function multiplies stage counts and represents the multiplication principle directly.

The program then builds on these primitives with:

- `permutation_count` for ordered selections;
- `combination_count` for unordered selections;
- `inclusion_exclusion_two_sets` for overlapping groups;
- `repeated_arrangement_count` for repeated objects;
- `grid_path_count` for shortest grid paths;
- `probability_from_count` for probabilities derived from finite counts;
- `service_plan_count` for a sum of internal product counts.

The `ServicePlan` data class demonstrates a particularly useful structure. Each service plan contains its own number of regions and environments. The number of configurations for an individual plan is a product, while the total across mutually exclusive plans is a sum.

The program also deliberately compares mathematical counting with enumeration for a small binary-string space. Enumeration is restricted to small lengths because the number of binary strings grows as `2^n`.

Validation is treated as part of the implementation. Negative cardinalities, impossible selections, empty probability spaces, invalid intersections, and inappropriate parameter relationships are rejected rather than producing misleading results.

---

## JavaScript Implementation

The JavaScript implementation takes a different perspective by using language-specific mechanisms.

The `cartesianProduct` function builds combinations dynamically from arrays. This demonstrates how a product space can be constructed rather than merely counted.

The program uses `Set` objects for validation of acceptable environments, regions, and deployment windows. A small event bus then emits `configuration:selected` and `configuration:rejected` events. The `ConfigurationCounter` listens to these events and maintains accepted and rejected counts.

This event-driven model is useful because JavaScript frequently processes streams of events rather than a fixed mathematical dataset.

The asynchronous section uses `Promise.all` to collect choice counts from multiple simulated sources. Only after all sources return validated values is the product rule applied.

Large combinatorial values use `BigInt`. JavaScript's ordinary `Number` representation cannot exactly represent every integer beyond its safe-integer range, so a combinatorial calculation that exceeds that range can silently lose precision if implemented with ordinary numbers.

The implementation therefore uses `factorialBigInt`, `permutationBigInt`, and `combinationBigInt` for exact integer arithmetic.

---

## C++ Governance Case Study

The C++ implementation models a deployment governance engine.

A deployment configuration consists of:

`channel × region × environment × deployment window`.

The available deployment channels are treated as mutually exclusive alternatives. Each channel has its own number of regions, environments, and deployment windows.

For an individual channel, the configuration count is a product:

`regions × environments × deployment windows`.

Across channels, the counts are added because a deployment uses one channel.

The resulting structure is therefore:

`sum of channel-specific products`.

This is a useful example of combining the two fundamental rules rather than treating them as isolated formulas.

### Governance model

The `DeploymentGovernanceEngine` evaluates actual deployment requests.

Its policy contains constraints such as:

- production requires two distinct reviewers;
- staging requires at least one reviewer;
- validation checks must pass;
- direct production pushes are prohibited.

The engine validates a request and returns an `EvaluationResult` containing both an acceptance state and a concrete reason.

This is deliberately separate from the mathematical counting functions. Counting determines the size of the configuration space, while governance determines whether a particular configuration is acceptable.

### Reviewer assignment

Reviewer roles are modeled as distinct positions.

Selecting two reviewers from six for ordered roles produces:

`6 × 5 = 30`.

This is a dependent product because the second reviewer cannot reuse the person already assigned to the first position.

### Capability overlap

The case study also contains an inclusion-exclusion calculation for engineers who have platform or security capability.

The intersection is subtracted once because simple addition counts engineers possessing both capabilities twice.

### Overflow handling

The C++ implementation uses `std::uint64_t` and checked arithmetic.

Counting can grow extremely quickly. A product of otherwise valid counts can exceed the representable integer range. `checkedAdd` and `checkedMultiply` detect overflow before returning an invalid result.

For very large production combinatorial calculations, arbitrary-precision arithmetic would be appropriate. The case study intentionally keeps the core implementation within the standard C++17 library.

---

## Why Counting Beats Enumeration

Suppose a system has:

`20 environments × 50 regions × 12 deployment windows`.

The configuration count is:

`20 × 50 × 12 = 12,000`.

Generating 12,000 objects may be reasonable.

If the same structure expands to:

`100 environments × 200 regions × 50 windows × 10 deployment modes`,

the space contains:

`10,000,000` configurations.

A formula can calculate that number almost immediately without creating ten million objects.

The distinction matters even more when combinations involve hundreds or thousands of elements. Enumeration can become computationally and operationally expensive while a closed-form count may remain inexpensive.

Counting does not replace enumeration in every application. Enumeration is necessary when the actual outcomes must be inspected, filtered, stored, or processed. Counting is preferable when only the cardinality of the space is required.

---

## Common Modeling Errors

### Adding sequential choices

A configuration with 3 environments and 4 regions is not counted as `3 + 4`.

A complete configuration contains one environment and one region, so the correct structure is:

`3 × 4`.

### Multiplying exclusive alternatives

If a user selects either one of 5 public-cloud routes or one of 3 private-cloud routes, the alternatives are not two stages.

The correct count is:

`5 + 3`.

Multiplication would incorrectly model the selection as if both routes were required simultaneously.

### Ignoring changing availability

If an item cannot be reused, the number of available choices changes.

Using `n × n` when the second choice must differ from the first overcounts the result.

The correct structure is:

`n × (n-1)`.

### Counting overlapping groups by direct addition

If 30 people belong to both groups, adding the group sizes counts those 30 people twice.

Inclusion-exclusion is required.

### Confusing permutations and combinations

If positions or roles are distinct, order matters and permutations are appropriate.

If only membership in a group matters, order does not matter and combinations are appropriate.

### Enumerating when only a count is needed

Generating every possible outcome can consume significant memory and processing time. A counting formula should be preferred when the application only needs the cardinality.

---

## Edge Cases and Validation

A reliable counting implementation should validate its assumptions.

The implementations reject or handle conditions such as:

- negative numbers of choices;
- selecting more objects than exist;
- an intersection larger than one of its participating sets;
- an empty probability sample space;
- repeated-element assumptions that do not hold;
- arithmetic overflow;
- invalid restricted-position configurations.

These checks are not mathematical decoration. A counting result is meaningful only when the input model corresponds to the actual problem.

---

## Performance Considerations

The basic sum rule requires linear work in the number of alternatives:

`O(k)` for `k` alternatives.

The basic product rule also requires:

`O(k)`

operations for `k` stages.

An iterative permutation calculation for `P(n,r)` requires approximately:

`O(r)`

multiplications.

A combination calculation can use the symmetry:

`C(n,r) = C(n,n-r)`

to reduce the number of iterations to approximately:

`O(min(r,n-r))`.

Enumeration has fundamentally different behavior. A Cartesian product with stage sizes `n1, n2, ..., nk` contains:

`n1 × n2 × ... × nk`

outcomes.

Consequently, generating the complete product can become infeasible even though calculating its cardinality is inexpensive.

---

## Exact Arithmetic

Combinatorial values grow rapidly.

For example, factorial growth means that even moderate values of `n` can produce very large integers.

The JavaScript implementation uses `BigInt` because ordinary `Number` arithmetic is based on IEEE-754 floating-point representation and cannot exactly represent every large integer.

The C++ implementation instead uses checked `std::uint64_t` arithmetic. This provides exact results within the available range and explicit overflow detection beyond that range.

The Python implementation benefits from Python's arbitrary-precision integers, so integer counts can grow beyond fixed-width machine integer limits, subject to available memory and execution time.

The choice of integer representation is therefore part of the correctness of a combinatorial program.

---

## Relationship Between the Core Concepts

The concepts form a progression rather than three interchangeable labels.

**Counting principles** provide the structural reasoning used to model finite outcome spaces.

**The sum rule** handles mutually exclusive alternatives.

**The product rule** handles multi-stage construction of a complete outcome.

**The multiplication principle** describes the general mechanism behind the product rule: each additional stage multiplies the number of complete outcomes by the number of choices available at that stage.

From this foundation, more advanced counting methods emerge naturally.

Distinct ordered selections become permutations.

Unordered selections become combinations.

Overlapping alternatives require inclusion-exclusion.

Restrictions change the number of available choices at particular stages.

Repeated elements require duplicate arrangements to be removed.

Probability can then use counted outcome spaces to determine event likelihoods when the required equal-likelihood assumptions hold.

---

## Practical Interpretation

A useful way to approach a new counting problem is to first describe how one valid outcome is constructed.

If the outcome is formed by choosing one alternative from a set of disjoint cases, the structure suggests addition.

If the outcome is constructed through several choices, the structure suggests multiplication.

If later choices depend on earlier choices, determine the number of remaining choices at every stage.

If multiple categories overlap, identify the duplicated outcomes before adding their counts.

If order does not matter, remove the ordering distinction.

If objects repeat, account for indistinguishable arrangements.

The implementations are designed around these structural decisions rather than around memorizing isolated formulas.
