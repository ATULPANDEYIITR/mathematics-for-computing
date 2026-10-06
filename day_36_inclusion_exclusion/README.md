# Inclusion-Exclusion Principle: Overlapping Sets and Counting Applications

## Scope

This project develops the inclusion-exclusion principle as a counting mechanism for overlapping sets.

The central problem is simple: adding the sizes of overlapping sets counts shared elements more than once. Inclusion-exclusion corrects that overcounting by alternating addition and subtraction of intersections.

For two sets:

`|A ∪ B| = |A| + |B| - |A ∩ B|`

For three sets:

`|A ∪ B ∪ C| = |A| + |B| + |C| - |A ∩ B| - |A ∩ C| - |B ∩ C| + |A ∩ B ∩ C|`

The alternating signs are not an arbitrary formula pattern. They compensate for repeated counting. An element belonging to two sets is initially counted twice and therefore needs one subtraction. An element belonging to three sets is initially counted three times, is subtracted three times through pairwise intersections, and therefore needs one final addition.

The implementations in this project deliberately approach the principle from different technical directions rather than translating one program into five languages.

---

## Mathematical mechanism

Suppose a population contains three sets `A`, `B`, and `C`.

An element belonging only to `A` appears once in the single-set terms.

An element belonging to both `A` and `B` appears twice in the single-set terms. Subtracting `A ∩ B` removes one duplicate.

An element belonging to all three sets appears three times in the single-set terms. It is then subtracted once for each of the three pairwise intersections, producing a temporary count of zero. The triple intersection is therefore added once to restore the element.

This produces the general form:

`|A₁ ∪ A₂ ∪ ... ∪ Aₙ| = Σ|Aᵢ| - Σ|Aᵢ ∩ Aⱼ| + Σ|Aᵢ ∩ Aⱼ ∩ Aₖ| - ...`

The sign of an intersection containing `k` sets is positive when `k` is odd and negative when `k` is even.

---

## Overlapping sets versus exclusive categories

Inclusion-exclusion normally answers an "at least one" question.

For example, `|A ∪ B ∪ C|` counts every element that belongs to one, two, or three sets exactly once.

That is different from asking for exact categories.

For three sets, the mutually exclusive categories are:

| Category | Meaning |
|---|---|
| None | The element belongs to no set |
| Only A | The element belongs to A but not B or C |
| Only B | The element belongs to B but not A or C |
| Only C | The element belongs to C but not A or B |
| Exactly two | The element belongs to two sets but not all three |
| All three | The element belongs to A, B, and C |
| At least one | The union of all three sets |

The Python implementation derives these categories directly from the supplied intersections. The JavaScript implementation determines membership counts dynamically from actual `Set` objects. The Java implementation represents the same distinction as explicit domain state.

This distinction matters because a union count cannot be interpreted as an exact-category count.

---

## General inclusion-exclusion

For `n` arbitrary finite sets, every non-empty subset of the sets can contribute an intersection term.

There are:

`2ⁿ - 1`

non-empty subsets.

Therefore a direct implementation that explicitly evaluates every intersection has exponential growth in the number of sets.

The Python, JavaScript, and C++ implementations demonstrate this mechanism using bitmasks. A bit at position `i` indicates that set `i` participates in the current intersection.

For example, a mask representing sets `A` and `C` selects exactly those two sets. The number of selected sets determines the sign of the term.

This representation is convenient because it turns the mathematical collection of subsets into a compact computational representation.

The exponential behavior is important. Inclusion-exclusion is mathematically elegant, but the general form is not automatically efficient for a large number of arbitrary sets.

---

## Python implementation

The Python program emphasizes direct executable experimentation with the principle.

Its set-based implementation calculates intersections for every non-empty subset of the supplied sets. The `explain_general_inclusion_exclusion` function exposes the individual terms, their signs, and their contributions, which makes the alternating structure observable rather than hiding it inside one expression.

The Python implementation also contains a three-set category model. It calculates:

- only-A membership
- only-B membership
- only-C membership
- exactly-two membership
- exactly-three membership
- none
- at-least-one membership

The divisibility implementation demonstrates an important structured application. Instead of constructing explicit sets of integers, it treats the set of multiples of a divisor as a mathematical set.

For example:

`A = {x : 2 divides x}`

and

`B = {x : 3 divides x}`

have an intersection consisting of numbers divisible by both 2 and 3. That is equivalent to divisibility by `lcm(2, 3)`.

The Python program therefore calculates the intersection of divisibility conditions using least common multiples rather than constructing potentially large sets.

The coprimality example uses the distinct prime factors of a number. An integer is not coprime to the base when it is divisible by at least one prime factor of that base. Inclusion-exclusion then counts the complement of those overlapping divisibility conditions.

The derangement implementation applies inclusion-exclusion to permutations. A forbidden event is defined for each position: the item remains fixed in its original position. Intersections represent multiple simultaneously fixed positions.

---

## JavaScript implementation

The JavaScript program uses native `Set` objects as the primary representation of finite mathematical sets.

This is particularly appropriate for the topic because JavaScript's `Set` directly represents unique membership. The implementation defines intersection and union operations and then applies the inclusion-exclusion formula independently of direct union construction.

The event-driven component uses an `SetAnalysisEventBus`. After an analysis is completed, the analyzer emits an `analysisCompleted` event. This demonstrates a JavaScript-specific way to separate the calculation from consumers of the result.

The survey case uses three overlapping populations represented as `Set` objects. The same data can be examined through both union size and exact membership categories.

JavaScript's `BigInt` is used for factorial and derangement calculations. This avoids the precision problems that ordinary JavaScript `Number` values encounter when integer calculations become larger than the exact-integer range.

The divisibility implementation uses `gcd` and `lcm`, allowing inclusion-exclusion to operate on arithmetic conditions without materializing every integer in a set.

---

## C++ case study

The C++ implementation models a repository-like governance scenario in which software artifacts can have several independent violations:

- vulnerable dependencies
- missing documentation
- failed security scans

The important mathematical issue is that one artifact can appear in multiple violation sets.

If 38 artifacts have dependency problems, 43 have documentation problems, and 39 have security problems, directly adding these populations does not give the number of affected artifacts because an artifact with two or three violations appears multiple times.

`GovernanceEngine` constructs explicit `std::set<int>` collections for the three conditions and calculates their union through inclusion-exclusion.

The same engine also classifies artifacts by exact membership. An artifact with one violated condition is separated from an artifact with exactly two violations and from one violating all three conditions.

This demonstrates the relationship between the union calculation and the more detailed membership partition.

The C++ implementation uses `std::set_intersection` to calculate intersection contents. This is a deliberate choice for the case study because artifact identity matters. The program is not merely demonstrating an arithmetic formula; it is modeling a system in which individual artifacts can be inspected.

The arithmetic portion then changes perspective. For divisibility, explicit set construction is unnecessary. The intersection of multiples is represented by an LCM, which makes the calculation substantially more compact.

---

## Java enterprise model

The Java implementation represents overlapping membership as a domain problem rather than a collection of independent calculations.

`EligibilityRule` defines a closed set of eligibility conditions:

- active subscription
- verified identity
- recent purchase

A `Customer` contains the rules currently satisfied by that customer.

`RulePolicy` implements the `EligibilityPolicy` interface. This separates the concept of a rule from the service that evaluates a population.

`EligibilityService` evaluates each customer and determines how many policies are satisfied. The result is represented by `MembershipReport`, which explicitly records none, exactly one, exactly two, all three, and at-least-one populations.

`EnumSet` is appropriate for this domain because the set of possible rules is known at compile time. It provides compact membership representation while preventing arbitrary strings from silently becoming valid rules.

The constructor defensively copies the supplied rule set. This matters because `EnumSet` is mutable, while the `Customer` record is intended to represent stable state.

The Java implementation also includes the arithmetic form of inclusion-exclusion and a derangement calculation, but its main emphasis is domain modeling and explicit policy representation.

---

## SQL relational model

The PostgreSQL script models the problem through three core relations.

`participant` represents the population.

`activity_set` represents mathematical sets.

`activity_membership` represents the many-to-many relationship between participants and sets.

The composite primary key:

`PRIMARY KEY (participant_id, activity_id)`

prevents the same participant from being inserted into the same set more than once.

Foreign keys ensure that memberships cannot reference nonexistent participants or nonexistent sets.

The indexes on `(activity_id, participant_id)` and `(participant_id, activity_id)` support the two principal access directions:

- finding participants belonging to a particular set
- finding all sets containing a particular participant

The SQL script independently calculates the union directly with `COUNT(DISTINCT participant_id)` and through the three-set inclusion-exclusion expression.

Keeping these calculations separate is useful when validating a database implementation because agreement between independent formulations provides evidence that the intersection logic is correct.

---

## SQL exact-membership analysis

The SQL query that groups participants by `COUNT(m.activity_id)` converts overlapping membership into mutually exclusive categories.

A count of zero represents the complement of the union.

A count of one represents exactly one set.

A count of two represents exactly two sets.

A count of three represents membership in all three sets.

This is different from merely counting the union because the union intentionally discards the number of sets to which each participant belongs.

The database therefore supports both questions:

`How many participants belong to at least one set?`

and:

`How many participants belong to exactly two sets?`

Those questions require different interpretations of the same membership relation.

---

## Divisibility applications

Inclusion-exclusion is particularly useful when sets are defined by divisibility.

For numbers from `1` through `N`, let:

`A = numbers divisible by a`

`B = numbers divisible by b`

Then:

`|A| = floor(N/a)`

`|B| = floor(N/b)`

and:

`|A ∩ B| = floor(N/lcm(a,b))`

Therefore:

`|A ∪ B| = floor(N/a) + floor(N/b) - floor(N/lcm(a,b))`

For three divisors, pairwise LCMs and the three-way LCM appear in the alternating formula.

The SQL, Python, JavaScript, and C++ implementations all demonstrate this type of counting, although each uses its language's natural mechanisms.

The important structural observation is that arithmetic replaces explicit set construction. This is what makes the technique useful for large numerical ranges.

---

## Probability interpretation

The same principle applies to events.

For two events:

`P(A ∪ B) = P(A) + P(B) - P(A ∩ B)`

The subtraction is necessary for the same reason as in cardinality counting: outcomes in the intersection are included in both `P(A)` and `P(B)`.

The principle does not require the events to be independent.

In fact, assuming independence merely to calculate `P(A ∩ B)` can be incorrect. If independence is known, then:

`P(A ∩ B) = P(A)P(B)`

but the inclusion-exclusion formula itself remains valid regardless of independence.

---

## Derangements

A derangement is a permutation in which no element remains in its original position.

For a permutation of `n` objects, define `Aᵢ` as the event that position `i` is fixed.

The desired result is:

`n! - |A₁ ∪ A₂ ∪ ... ∪ Aₙ|`

Applying inclusion-exclusion gives:

`Dₙ = Σ (-1)^k C(n,k)(n-k)!`

where `k` ranges from zero through `n`.

The reason this works is that choosing `k` fixed positions leaves `(n-k)!` ways to arrange the remaining elements.

The Python, JavaScript, C++, and Java implementations calculate these values directly.

For example:

`D₄ = 9`

There are 24 permutations of four objects, but only nine have no fixed position.

---

## Complexity

For `n` arbitrary sets, direct inclusion-exclusion has `2ⁿ - 1` non-empty intersection terms.

The main cost is not merely calculating an intersection. It is the number of combinations of sets that must be considered.

The bitmask implementations therefore have exponential complexity in the number of sets.

Arithmetic applications can behave much better when the problem has exploitable structure. Divisibility is one example because an intersection can be represented by an LCM.

The practical lesson is that inclusion-exclusion should not be treated as a single algorithm with one fixed implementation strategy. The mathematical principle stays constant, while the computational representation can change substantially according to the structure of the sets.

---

## Edge cases

The implementations deliberately account for several boundary conditions.

An empty collection of sets has an empty union in the finite-set implementations.

An empty intersection is not treated as an ordinary mathematical set selected by a bitmask; only non-empty combinations contribute to the inclusion-exclusion sum.

Duplicate divisors are removed in the arithmetic implementations because repeating the same set as a separate condition would distort the intended interpretation.

Invalid negative divisors are rejected.

An intersection cannot be larger than any of the sets that contain it.

Probability values must remain within the interval `[0, 1]`.

Derangements include the boundary value:

`D₀ = 1`

This follows from the fact that there is exactly one permutation of the empty set, and it vacuously has no fixed positions.

---

## Common implementation errors

A frequent error is simply adding set sizes:

`|A| + |B| + |C|`

without subtracting intersections.

Another error is subtracting pairwise intersections but forgetting the triple intersection. That produces an incorrect result for elements belonging to all three sets.

A related error occurs when an exact-category question is answered using a union. A union answers "at least one", not "exactly one" or "exactly two".

For divisibility problems, using the product of divisors instead of their LCM can also be wrong. The product equals the LCM only when the relevant divisors are pairwise coprime.

Finally, direct inclusion-exclusion over a large number of arbitrary sets can become computationally infeasible because of its exponential number of terms.

---

## Practical interpretation

The central value of inclusion-exclusion is controlled correction of overlap.

The same structure appears when counting:

- people satisfying multiple survey criteria
- records matching multiple filters
- numbers satisfying multiple divisibility conditions
- outcomes satisfying multiple probability events
- permutations violating multiple position restrictions
- database entities belonging to overlapping categories

The mathematical operation is the same in each case, but the implementation should reflect how membership is represented.

Explicit finite sets are appropriate when individual elements matter.

Bitmasks are useful when the number of sets is moderate and subset enumeration is required.

Arithmetic transformations are preferable when sets have number-theoretic structure.

Relational membership tables are appropriate when set membership must be persisted, queried, constrained, and indexed.

Domain objects and policies are useful when overlapping conditions form part of an enterprise decision process.
