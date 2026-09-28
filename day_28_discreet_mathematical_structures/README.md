# Discrete Mathematical Structures in Computer Science

## Topic Scope

Discrete mathematical structures provide the formal language used to describe finite and countable objects, relationships between objects, logical rules, computational processes, and structures manipulated by algorithms.

This implementation set develops the topic through three programming languages:

- Python emphasizes mathematical modeling, executable verification, compact algorithms, and direct representation of sets, relations, functions, graphs, logic, and combinatorial structures.
- JavaScript emphasizes `Set`, `Map`, first-class functions, closures, functional programming, object-oriented modeling, asynchronous state transitions, and application-oriented representations.
- C++ develops an industry-style university computing platform that combines sets, relations, functions, graphs, partial orders, authorization rules, course dependencies, state machines, validation, and error handling.

The implementations are executable rather than merely descriptive. Mathematical properties are repeatedly expressed as program predicates and verified through assertions.

---

# 1. Fundamental Idea of Discrete Mathematics

Discrete mathematics studies mathematical objects that are separate or countable rather than continuously varying.

Typical discrete objects include:

- integers
- finite sets
- strings
- graphs
- trees
- relations
- functions
- logical propositions
- Boolean values
- finite sequences
- combinatorial arrangements
- algebraic structures
- state-transition systems

Computer science is fundamentally discrete because computers operate on finite representations, symbolic states, bits, data structures, instructions, and algorithms.

Examples of direct relationships include:

| Mathematical concept | Computer science application |
|---|---|
| Set | Collection of users, permissions, features, states |
| Relation | Database relationship, dependency, association |
| Function | Program function, deterministic transformation, mapping |
| Logic | Conditions, validation, access control |
| Graph | Network, dependency system, social connection |
| Tree | File system, syntax tree, search tree |
| Partial order | Task dependencies, version relationships |
| Equivalence relation | Grouping equivalent states or objects |
| Boolean algebra | Digital circuits and logical expressions |
| Counting | Complexity, combinations, search spaces |
| Recurrence | Recursive algorithms and dynamic programming |

---

# 2. Sets

## 2.1 Definition

A set is a collection of distinct objects.

If an object `x` belongs to set `A`, the notation is:

`x ∈ A`

If it does not belong:

`x ∉ A`

The order of elements in a mathematical set does not matter, and duplicate elements do not create additional members.

For example:

`A = {1, 2, 3}`

is the same set as:

`{3, 1, 2}`

The cardinality of a finite set is the number of distinct elements:

`|A| = 3`

---

## 2.2 Python Representation

The Python implementation uses the built-in `set` type.

The script demonstrates:

- membership
- union
- intersection
- difference
- symmetric difference
- subset
- superset
- cardinality
- empty sets
- immutable `frozenset`

The expressions correspond closely to mathematical notation:

- `A | B` represents `A ∪ B`
- `A & B` represents `A ∩ B`
- `A - B` represents `A - B`
- `A ^ B` represents symmetric difference
- `A <= B` tests subset
- `A >= B` tests superset

Python sets are hash-based, so average-case membership testing is approximately constant time.

---

## 2.3 JavaScript Representation

JavaScript uses the built-in `Set` object.

The JavaScript implementation provides explicit functions for:

- union
- intersection
- difference
- symmetric difference
- subset checking

JavaScript's `Set` also removes duplicates automatically.

A JavaScript `Set` is particularly useful when an application needs uniqueness and efficient membership operations.

---

# 3. Power Sets

The power set of `A`, written `P(A)` or sometimes `2^A`, is the set of all subsets of `A`.

If:

`|A| = n`

then:

`|P(A)| = 2^n`

For:

`A = {1, 2, 3}`

there are:

`2^3 = 8`

subsets.

Both Python and JavaScript implement power-set generation using bit masks.

A bit mask provides a compact computational representation of subset selection. Each bit indicates whether the corresponding element belongs to a particular subset.

This connects a combinatorial definition directly to an algorithm.

The exponential number of subsets is also an important complexity consideration. Even when the implementation of generating each subset is efficient, the number of results itself grows exponentially.

---

# 4. Cartesian Products

The Cartesian product of sets `A` and `B` is:

`A × B = {(a,b) | a ∈ A and b ∈ B}`

If the sets are finite:

`|A × B| = |A| × |B|`

Cartesian products are important because binary relations are defined as subsets of Cartesian products.

For example, if:

`A = {A,B}`

and:

`B = {1,2,3}`

then:

`A × B`

contains six ordered pairs.

Python uses `itertools.product`, while JavaScript uses nested iteration.

---

# 5. Relations

## 5.1 Definition

A binary relation from `A` to `B` is a subset of:

`A × B`

A relation on `A` is a subset of:

`A × A`

For example:

`R = {(1,1), (1,2), (2,2)}`

is a relation on `{1,2}`.

Relations are more general than functions. A relation may connect one input to several outputs or no outputs at all.

---

# 6. Properties of Relations

The major relation properties demonstrated in the implementations are reflexivity, symmetry, antisymmetry, and transitivity.

## 6.1 Reflexive

A relation `R` on `A` is reflexive if:

`∀a ∈ A, (a,a) ∈ R`

Every element must relate to itself.

The relation `≤` on the integers is reflexive because:

`a ≤ a`

for every integer `a`.

---

## 6.2 Irreflexive

A relation is irreflexive if:

`∀a ∈ A, (a,a) ∉ R`

Strict inequality `<` is an example.

No number is strictly less than itself.

---

## 6.3 Symmetric

A relation is symmetric if:

`aRb ⇒ bRa`

If `(a,b)` belongs to the relation, `(b,a)` must also belong.

Mutual friendship can be modeled as a symmetric relation if friendship is explicitly defined as mutual.

---

## 6.4 Antisymmetric

A relation is antisymmetric if:

`aRb ∧ bRa ⇒ a=b`

Antisymmetry does not mean that reverse pairs never occur.

It means that if both directions occur, the two elements must actually be the same.

The subset relation `⊆` is antisymmetric.

---

## 6.5 Asymmetric

A relation is asymmetric if:

`aRb ⇒ ¬(bRa)`

for all relevant pairs.

A strict ordering such as `<` is asymmetric.

---

## 6.6 Transitive

A relation is transitive if:

`aRb ∧ bRc ⇒ aRc`

The relation `≤` is transitive.

Transitivity is especially important for dependency and ordering structures.

---

# 7. Equivalence Relations

An equivalence relation is a relation that is:

1. reflexive
2. symmetric
3. transitive

Equivalence relations express a formal concept of "being equivalent."

The implementations use congruence modulo an integer.

For a positive integer `n`:

`a ≡ b (mod n)`

when:

`a mod n = b mod n`

For example, modulo 3:

`1 ≡ 4 (mod 3)`

and:

`2 ≡ 5 (mod 3)`

---

# 8. Equivalence Classes

An equivalence relation partitions a set into equivalence classes.

For a representative `a`, its equivalence class is:

`[a] = {x | xRa}`

Modulo 3 divides the example domain into classes corresponding to residues:

- residue 0
- residue 1
- residue 2

A partition has three essential characteristics:

1. every element belongs to at least one block
2. no element belongs to two different blocks
3. the blocks together cover the original set

Equivalence classes are useful in:

- duplicate detection
- canonicalization
- clustering
- compiler transformations
- state minimization
- quotient structures
- modular arithmetic

---

# 9. Partial Orders

A partial order is a relation that is:

- reflexive
- antisymmetric
- transitive

A partially ordered set is called a poset.

Common examples include:

- subset inclusion
- divisibility
- dependency relationships
- prerequisite relationships
- version precedence

Unlike a total order, a partial order does not require every pair of elements to be comparable.

For example, two unrelated tasks may both precede a third task without either task preceding the other.

---

# 10. Minimal and Maximal Elements

For a poset:

- a minimal element has no distinct element strictly below it
- a maximal element has no distinct element strictly above it

A minimal element does not necessarily have to be the unique smallest element.

Likewise, a maximal element does not necessarily have to be the unique largest element.

This distinction matters in dependency systems where multiple tasks may be independently executable.

---

# 11. Topological Ordering

A directed acyclic graph can be topologically ordered.

A topological ordering places every prerequisite before the item that depends on it.

If:

`A → B`

then `A` must occur before `B`.

The implementations use topological sorting to represent course prerequisites.

For example:

`Sets → Relations → Databases`

requires Sets before Relations and Relations before Databases.

The algorithm used is based on indegree and a queue.

Its time complexity with an adjacency-list representation is:

`O(V + E)`

where:

- `V` is the number of vertices
- `E` is the number of edges

A directed cycle makes a topological ordering impossible.

The C++ case study explicitly creates a cycle and verifies that it is detected.

---

# 12. Functions

## 12.1 Definition

A function from `A` to `B` is written:

`f: A → B`

Every element of the domain `A` must map to exactly one element of the codomain `B`.

Three important terms are:

- domain
- codomain
- image or range

The image is the subset of the codomain actually produced by the function.

---

# 13. Function Versus Relation

Every function can be represented as a relation, but not every relation is a function.

A relation is a function when every input has exactly one output.

For example:

`{(a,1), (b,2), (c,3)}`

is a function.

But:

`{(a,1), (a,2)}`

is not a function because `a` has two outputs.

This distinction is fundamental in mathematical modeling and software design.

---

# 14. Injective Functions

A function is injective if different inputs produce different outputs.

Formally:

`f(a) = f(b) ⇒ a = b`

Equivalently:

`a ≠ b ⇒ f(a) ≠ f(b)`

An injective function does not collapse two distinct domain elements into the same output.

The Python, JavaScript, and C++ implementations verify injectivity by checking whether all output values are distinct.

---

# 15. Surjective Functions

A function `f: A → B` is surjective if every element of `B` is reached.

Formally:

`∀b ∈ B, ∃a ∈ A such that f(a)=b`

The codomain matters.

The same mapping can be surjective onto one codomain but not another.

This is why the implementations explicitly accept a codomain when testing surjectivity.

---

# 16. Bijective Functions

A function is bijective if it is both:

- injective
- surjective

A bijection establishes a one-to-one correspondence between two sets.

Finite bijections have inverse functions.

If:

`f(a)=b`

then:

`f⁻¹(b)=a`

The implementations reject inverse construction for non-bijective mappings.

---

# 17. Function Composition

For:

`g: A → B`

and:

`f: B → C`

the composition is:

`f ∘ g`

and:

`(f ∘ g)(x)=f(g(x))`

The order is important.

The rightmost function is applied first.

The JavaScript implementation uses higher-order functions to create compositions dynamically.

---

# 18. First-Class Functions and Closures

JavaScript treats functions as values.

A function can be:

- stored in a variable
- passed to another function
- returned from a function
- stored in a collection

A closure is a function that retains access to variables from its surrounding lexical environment.

The JavaScript example `createMultiplier` returns a function that remembers its multiplier.

This is a direct connection between mathematical functions and practical software abstractions.

---

# 19. Propositional Logic

A proposition is a declarative statement that has a truth value.

The basic logical operators include:

| Symbol | Meaning |
|---|---|
| `¬p` | NOT |
| `p ∧ q` | AND |
| `p ∨ q` | OR |
| `p ⊕ q` | XOR |
| `p → q` | implication |
| `p ↔ q` | biconditional |

Material implication can be expressed as:

`p → q ≡ ¬p ∨ q`

This means an implication is false only when `p` is true and `q` is false.

---

# 20. Truth Tables

A truth table enumerates every possible assignment of truth values.

For `n` Boolean variables there are:

`2^n`

assignments.

Therefore, truth-table methods become expensive as the number of variables grows.

The implementations use exhaustive enumeration for small examples.

This is mathematically precise but not always computationally scalable.

---

# 21. Tautologies, Contradictions, and Contingencies

A tautology is true for every possible assignment.

Example:

`p ∨ ¬p`

A contradiction is false for every possible assignment.

Example:

`p ∧ ¬p`

A contingency is true for some assignments and false for others.

The Python and JavaScript implementations explicitly classify expressions by enumerating assignments.

---

# 22. Logical Equivalence

Two propositions are logically equivalent if they have identical truth values for every assignment.

Notation:

`P ≡ Q`

De Morgan's law provides an important example:

`¬(p ∧ q) ≡ ¬p ∨ ¬q`

The implementations verify this equality for every possible combination of `p` and `q`.

---

# 23. Predicate Logic

Propositional logic treats complete statements as atomic units.

Predicate logic introduces variables and predicates.

For example:

`P(x): x is even`

allows statements such as:

`∀x P(x)`

and:

`∃x P(x)`

The universal quantifier `∀` means "for every."

The existential quantifier `∃` means "there exists."

In software:

- Python's `all()` naturally models finite universal quantification.
- Python's `any()` naturally models finite existential quantification.
- JavaScript's `Array.prototype.every()` models a finite universal condition.
- JavaScript's `Array.prototype.some()` models a finite existential condition.

---

# 24. Counterexamples

To disprove a universal statement:

`∀x P(x)`

it is sufficient to find one `x` for which:

`¬P(x)`

That `x` is a counterexample.

The Python implementation explicitly searches for counterexamples to a candidate mathematical statement.

This idea is fundamental to mathematical proof and software testing.

A test suite that finds one invalid input does not prove every other input is valid, but it can immediately disprove an overly broad claim.

---

# 25. Logical Inference

The implementations demonstrate implication and a practical form of modus ponens.

The standard pattern is:

`p`

`p → q`

therefore:

`q`

Inference rules provide the formal foundation for reasoning systems, program verification, access policies, and automated decision procedures.

---

# 26. Boolean Algebra

Boolean algebra treats logical values using algebraic operations.

Important identities include:

### Identity laws

`p ∧ True = p`

`p ∨ False = p`

### Complement laws

`p ∧ ¬p = False`

`p ∨ ¬p = True`

### Idempotent laws

`p ∧ p = p`

`p ∨ p = p`

### Absorption laws

`p ∨ (p ∧ q) = p`

`p ∧ (p ∨ q) = p`

### Distributive laws

`p ∧ (q ∨ r) = (p ∧ q) ∨ (p ∧ r)`

`p ∨ (q ∧ r) = (p ∨ q) ∧ (p ∨ r)`

These structures are central to:

- digital logic
- circuit simplification
- Boolean conditions
- database queries
- access control
- compiler transformations

---

# 27. Normal Forms

A logical expression can be represented in standard structural forms.

## Conjunctive Normal Form

CNF is an AND of OR clauses.

For example:

`(p ∨ q) ∧ (¬p ∨ r)`

## Disjunctive Normal Form

DNF is an OR of AND terms.

Normal forms are important in automated reasoning, satisfiability problems, digital logic, and symbolic computation.

---

# 28. Recursion

A recursively defined object is specified in terms of smaller instances of itself.

Factorial provides a classic recurrence:

`0! = 1`

and:

`n! = n(n-1)!`

The Python, JavaScript, and C++ implementations demonstrate recursive factorial calculation.

Recursion connects directly to mathematical recurrence relations and recursive algorithms.

---

# 29. Fibonacci Recurrence

The Fibonacci sequence is defined by:

`F(0)=0`

`F(1)=1`

and:

`F(n)=F(n-1)+F(n-2)`

A naive recursive implementation repeatedly calculates the same values.

This creates exponential growth in the number of recursive calls.

Memoization stores already-computed values and avoids repeated work.

The JavaScript implementation demonstrates memoization with a `Map`.

The Python implementation also contrasts recursive and iterative approaches.

---

# 30. Mathematical Induction and Program Verification

Mathematical induction has two major components:

1. base case
2. inductive step

A statement is established for an initial value and then shown to remain valid when moving from one case to the next.

The Python implementation computationally checks:

`1 + 2 + ... + n = n(n+1)/2`

for a finite range.

This is not itself an infinite mathematical proof. It demonstrates how a mathematical invariant can be translated into executable verification.

This distinction is important:

- testing many cases provides evidence
- mathematical proof establishes universal validity under stated assumptions

---

# 31. Graphs

A graph is commonly represented as:

`G = (V,E)`

where:

- `V` is the set of vertices
- `E` is the set of edges

Graphs model:

- computer networks
- dependency systems
- road networks
- social relationships
- recommendation systems
- state transitions
- workflow systems

The Python and JavaScript implementations use adjacency lists.

The C++ case study uses a `map<string, set<string>>` adjacency representation.

---

# 32. Breadth-First Search

Breadth-first search explores vertices level by level.

A queue is used to maintain the frontier.

For an adjacency-list graph:

`O(V + E)`

time is required when each vertex and edge is processed a bounded number of times.

BFS is useful for:

- shortest paths in unweighted graphs
- reachability
- level discovery
- network exploration

---

# 33. Depth-First Search

Depth-first search explores one branch before returning to alternative branches.

It can be implemented recursively or with an explicit stack.

DFS is useful for:

- cycle detection
- connected components
- graph traversal
- topological reasoning
- search problems

The Python and JavaScript implementations use explicit stacks for a practical iterative implementation.

---

# 34. Trees

A tree is a connected graph with no cycles.

A rooted tree gives each non-root node a parent.

A binary search tree adds the ordering invariant:

- values in the left subtree are smaller
- values in the right subtree are larger

The Python implementation builds a binary search tree and verifies the ordering invariant through inorder traversal.

For a correctly structured binary search tree, inorder traversal produces values in sorted order.

The important practical limitation is that an ordinary BST can become unbalanced.

A highly unbalanced tree can approach linear search behavior.

Balanced tree structures address this issue by maintaining stronger structural constraints.

---

# 35. Algebraic Structures

An algebraic structure consists of a set together with one or more operations satisfying specified properties.

Important structures include:

- semigroups
- monoids
- groups
- rings
- fields

The implementations demonstrate modular arithmetic.

For residues modulo 5, addition modulo 5 is closed:

`a + b mod 5 ∈ {0,1,2,3,4}`

The additive identity is:

`0`

Every element has an additive inverse.

This provides a concrete computational view of a finite group.

---

# 36. Closure

An operation is closed over a set if applying the operation to members of the set always produces another member of the set.

For example, integer addition is closed over the integers.

Ordinary integer division is not closed over the integers because:

`1 / 2`

is not an integer.

Closure is one of the first properties to check when defining an algebraic structure.

---

# 37. Matrices

Matrices are rectangular collections of values.

The Python implementation demonstrates:

- dimension validation
- matrix addition
- matrix multiplication

For matrix multiplication:

`A(m×n) × B(n×p)`

the number of columns in `A` must equal the number of rows in `B`.

The result has dimension:

`m×p`

Matrix structures are important in:

- graph algorithms
- linear transformations
- dynamic programming
- state representations
- numerical computing
- adjacency matrices

---

# 38. Counting

Discrete mathematics provides formal counting tools.

## Permutations

The number of ordered selections of `r` objects from `n` objects is:

`P(n,r) = n!/(n-r)!`

## Combinations

The number of unordered selections is:

`C(n,r) = n!/(r!(n-r)!)`

The implementations calculate both forms.

The distinction is whether order matters.

For example:

- selecting president and secretary: order matters
- selecting two committee members: order does not matter

---

# 39. Pigeonhole Principle

The pigeonhole principle states that if more than `n` objects are placed into `n` boxes, at least one box contains at least two objects.

The Python implementation distributes values according to their remainder modulo 3.

Ten objects placed into three remainder classes must produce at least one class containing multiple objects.

The principle appears in:

- hashing
- collision reasoning
- data structures
- combinatorics
- impossibility proofs

---

# 40. Relations and Databases

The relational database model has a strong mathematical relationship with set and relation theory.

A database table can be viewed as a relation consisting of tuples.

For example, a student relation may contain tuples such as:

`(student_id, name, department)`

An enrollment relation can connect:

`student_id`

to:

`course_id`

The implementations model this relationship explicitly.

Foreign-key validation corresponds to requiring that every referenced identifier exists in the appropriate relation.

This illustrates how abstract relation theory becomes a practical data-integrity mechanism.

---

# 41. C++ Case Study

## Problem Being Modeled

The C++ program models a university computing platform with several interacting components:

1. users
2. roles
3. permissions
4. course prerequisites
5. workflow states
6. mathematical functions
7. logical policies

This makes the case study substantially closer to a real system than isolated mathematical examples.

---

# 42. C++ Set Layer

The C++ program defines a generic alias:

`Set<T>`

using `std::set`.

It implements:

- union
- intersection
- difference
- subset checking

`std::set` maintains sorted unique values.

Its lookup operations generally have logarithmic complexity:

`O(log n)`

This differs from Python's hash-based set and JavaScript's built-in `Set`, whose membership behavior is generally designed around average constant-time hash-table-style operations.

The exact implementation and guarantees depend on the language runtime and data structure.

---

# 43. C++ Relation Layer

The relation is represented as:

`std::set<pair<A,B>>`

This gives a direct representation of ordered pairs.

The program verifies:

- reflexivity
- symmetry
- antisymmetry
- transitivity
- partial-order status

This representation is appropriate for small and moderate finite relations where explicit pairs are useful.

For very large sparse systems, specialized graph or database representations may be more appropriate.

---

# 44. C++ Function Layer

`FiniteFunction<Domain, Codomain>` models a finite mathematical function.

It stores:

- a mapping
- a codomain

The class checks:

- injectivity
- surjectivity
- bijectivity

It also provides:

- `apply()`
- `inverse()`

The inverse operation rejects non-bijective functions.

This is important because a general function does not necessarily possess an inverse function.

---

# 45. C++ Authorization System

The authorization component models:

`User → Role`

and:

`Role → Permission`

These are relations or mappings represented through standard library containers.

For example:

`admin → {read, write, delete}`

and:

`alice → {admin}`

Effective permissions are computed as the union of permissions belonging to the user's assigned roles.

This demonstrates several mathematical ideas simultaneously:

- sets
- relations
- functions
- unions
- Boolean conditions
- finite mappings

---

# 46. Authorization as Logic

The security policy has the form:

`authenticated ∧ active ∧ permitted`

Access is granted only when all three predicates are true.

This is a practical Boolean formula.

The same pattern appears in:

- authorization systems
- feature flags
- input validation
- firewall policies
- workflow rules
- database constraints

A security implementation must also consider authentication, authorization, least privilege, auditability, input validation, secure defaults, and failure behavior. The mathematical expression alone does not constitute a complete security architecture.

---

# 47. Course Prerequisite System

Course prerequisites form a directed relation.

If:

`A → B`

then A must be completed before B.

This relationship is naturally represented as a directed graph.

The C++ `CourseCatalog` converts the prerequisite relation into a directed graph and performs topological sorting.

The system also explicitly tests a cyclic dependency:

`A → B → C → A`

Since the graph contains a cycle, no valid topological order exists.

This is a practical example of how a mathematical property can become an application-level validation rule.

---

# 48. Workflow State Machine

The C++ implementation also represents application states:

- created
- queued
- processing
- completed
- failed
- cancelled

The permitted state transitions form a relation.

For example:

`created → queued`

is valid.

But:

`completed → processing`

is invalid.

The program rejects invalid transitions.

This is a finite-state-machine interpretation of a relation.

State machines are common in:

- payment processing
- job queues
- deployment systems
- order processing
- authentication flows
- network protocols
- user-interface workflows

---

# 49. JavaScript Asynchronous State Transitions

JavaScript extends the state-machine example with `Promise` and `async`/`await`.

The asynchronous function:

`transition(currentState, nextState)`

validates the relation before returning the new state.

This is useful because real applications frequently perform state transitions after asynchronous operations such as:

- network requests
- database operations
- timers
- user actions
- background processing

The mathematical transition relation remains the same even though the software execution model is asynchronous.

---

# 50. Python Implementation Structure

The Python script progresses from simple mathematical objects to integrated applications.

Major components include:

- `powerset`
- Cartesian-product generation
- relation-property predicates
- equivalence-class construction
- partial-order validation
- topological sorting
- function classification
- function composition
- inverse construction
- truth tables
- logical-equivalence checking
- predicate evaluation
- Boolean algebra
- recursion
- graph traversal
- binary search trees
- modular arithmetic
- matrices
- counting
- database-style relations
- authorization modeling
- relation closures
- formal assertions

Python is particularly effective here because mathematical concepts can be represented with compact syntax.

---

# 51. JavaScript Implementation Structure

The JavaScript implementation focuses on language features that become valuable when mathematical structures are embedded in applications.

It demonstrates:

- `Set`
- `Map`
- higher-order functions
- closures
- `map`
- `filter`
- `reduce`
- object-oriented classes
- truth-table generation
- graph classes
- topological sorting
- memoization
- asynchronous transitions
- application-style validation

The `FiniteFunction` class provides an object-oriented representation of a finite function.

The `Graph` class provides an object-oriented representation of graph operations.

The state-machine section demonstrates how mathematical transition relations interact with JavaScript's asynchronous programming model.

---

# 52. C++ Implementation Structure

The C++ program emphasizes explicit data structures, type safety, modular design, validation, and system-level implementation.

Major components are:

- generic set operations
- generic relation predicates
- finite function class
- directed graph class
- authorization system
- Boolean logic functions
- equivalence classes
- counting functions
- workflow state machine
- course catalog
- exception handling
- assertions

C++ is useful for this case study because the language makes data representation, generic types, object lifetime, algorithmic complexity, and standard-library data structures explicit.

---

# 53. Important Distinctions

## Relation vs Function

A relation may associate one input with many outputs.

A function assigns exactly one output to every domain element.

## Injective vs Surjective

Injective:

Different inputs produce different outputs.

Surjective:

Every codomain element is reached.

## Bijective

Both injective and surjective.

## Symmetric vs Antisymmetric

Symmetric:

`aRb ⇒ bRa`

Antisymmetric:

`aRb ∧ bRa ⇒ a=b`

These are not opposites.

A relation can be neither, one, or both depending on its structure.

## Minimal vs Minimum

A minimum element must be less than or equal to every element.

A minimal element merely has no strictly smaller comparable element.

A poset may contain multiple minimal elements.

## Maximal vs Maximum

A maximum is above every element.

A maximal element has no strictly larger comparable element.

A poset may contain multiple maximal elements.

---

# 54. Edge Cases

The implementations deliberately handle several edge cases.

## Empty Set

The empty set has:

`|∅| = 0`

Its power set contains exactly one element:

`P(∅) = {∅}`

Therefore:

`|P(∅)| = 1 = 2^0`

## Singleton Set

A singleton contains exactly one element.

## Duplicate Values

Set representations remove duplicates.

## Non-Bijection Inverse

Attempting to invert a non-bijective finite function raises an error.

## Invalid Matrix Dimensions

Matrix multiplication requires compatible dimensions.

## Cyclic Dependency

A cycle prevents topological sorting.

## Invalid Workflow Transition

A state transition outside the defined transition relation is rejected.

## Invalid Counting Arguments

Permutation and combination functions reject cases where:

`r > n`

or inputs are otherwise invalid.

## Negative Factorial

Factorial is defined for non-negative integers in the implementations.

---

# 55. Relation Closures

A closure adds the minimum required relationships needed to obtain a desired property.

## Reflexive Closure

Add:

`(a,a)`

for every element that lacks its self-pair.

## Symmetric Closure

For every:

`(a,b)`

add:

`(b,a)`

when missing.

## Transitive Closure

For every:

`aRb`

and:

`bRc`

ensure:

`aRc`

The Python implementation computes transitive closure iteratively.

Transitive closure is important for:

- reachability
- dependency analysis
- prerequisite systems
- graph algorithms
- database reasoning

---

# 56. Performance Considerations

Discrete mathematics frequently exposes the complexity of algorithms.

Important examples in these implementations include:

| Operation | Typical complexity |
|---|---:|
| Python set membership | Average `O(1)` |
| JavaScript Set membership | Average `O(1)` expected behavior |
| C++ `std::set` lookup | `O(log n)` |
| BFS with adjacency list | `O(V + E)` |
| DFS with adjacency list | `O(V + E)` |
| Topological sorting | `O(V + E)` |
| Power-set generation | `O(2^n)` output scale |
| Truth-table enumeration | `O(2^n)` assignments |
| Naive Fibonacci | Exponential growth |
| Memoized Fibonacci | Approximately `O(n)` states |
| Ordinary BST | Average dependent on tree shape |
| Unbalanced BST worst case | `O(n)` search |
| Balanced search tree | Typically `O(log n)` search |

The precise constant factors and guarantees depend on implementation and workload.

---

# 57. Exponential Growth

Two particularly important exponential patterns appear throughout discrete mathematics:

`2^n`

for subsets or Boolean assignments, and recursive branching such as naive Fibonacci.

This matters because an algorithm can be mathematically correct but computationally impractical.

Examples include:

- brute-force Boolean satisfiability
- exhaustive subset enumeration
- combinatorial search
- naive recursive algorithms

Understanding the underlying mathematical growth helps determine when optimization is required.

---

# 58. Security Considerations

Mathematical logic is useful for specifying security rules, but correct logic does not automatically guarantee a secure system.

Important implementation considerations include:

- validate all inputs
- distinguish authentication from authorization
- use least privilege
- reject invalid states
- fail safely
- avoid ambiguous permission semantics
- maintain audit records where appropriate
- protect credentials and secrets
- avoid trusting client-side authorization checks alone
- enforce authorization on trusted server-side boundaries

The authorization examples demonstrate the logical structure of permission checks without claiming to provide a complete production security architecture.

---

# 59. Common Mistakes

### Treating a relation as a function

A relation may contain multiple outputs for one input. A function may not.

### Ignoring the codomain

Surjectivity is defined relative to the codomain.

### Confusing antisymmetry with asymmetry

Antisymmetry permits `(a,a)`.

Asymmetry does not.

### Assuming every partial order is total

A partial order permits incomparable elements.

### Assuming every function has an inverse

Only bijective functions have ordinary two-sided inverses.

### Confusing testing with proof

Testing finite examples cannot establish an unrestricted mathematical theorem.

### Ignoring cycles in dependency systems

Topological sorting requires an acyclic directed graph.

### Assuming recursion is automatically efficient

A recursive mathematical definition can produce a computationally expensive algorithm.

### Ignoring data-structure choice

The mathematical operation may be the same while implementation complexity differs significantly.

---

# 60. Design Considerations

A mathematical model should be translated into software deliberately.

Questions to consider include:

1. What are the objects?
2. What constitutes equality?
3. Is uniqueness required?
4. Is ordering meaningful?
5. Is the relationship one-to-one, one-to-many, or many-to-many?
6. What invariants must always hold?
7. What invalid states must be rejected?
8. What are the expected input sizes?
9. Which operations are frequent?
10. What data structure provides suitable complexity?

For example, a mathematical set can be implemented with several different data structures depending on requirements.

A hash-based set emphasizes fast average membership.

An ordered tree-based set maintains ordering and provides logarithmic operations.

The mathematical abstraction remains a set even though the computational representation differs.

---

# 61. Production Considerations

A production implementation requires more than mathematical correctness.

Important considerations include:

- input validation
- error handling
- logging
- testing
- performance monitoring
- deterministic behavior where required
- concurrency control
- persistence
- data integrity
- security boundaries
- API contracts
- resource limits
- graceful failure

Mathematical structures are useful because they provide precise specifications that can be checked against implementation behavior.

---

# 62. Testing Mathematical Properties

The implementations use assertions to turn mathematical claims into executable tests.

Examples include:

- set identities
- relation properties
- function classification
- logical equivalence
- recurrence values
- matrix operations
- counting formulas
- graph invariants
- state-transition constraints

This is a practical form of specification-driven programming.

A mathematical invariant can often be expressed as a Boolean predicate.

For example:

`inorder(BST) is sorted`

can become an executable assertion.

---

# 63. Conceptual Relationship Between the Three Languages

| Area | Python | JavaScript | C++ |
|---|---|---|---|
| Sets | Built-in `set` | `Set` | `std::set` |
| Maps | `dict` | `Map` | `std::map` |
| Relations | `set` of tuples | `Set` of encoded pairs | `set<pair<...>>` |
| Functions | Functions and dictionaries | Functions, closures, `Map` | Typed class and callable logic |
| Logic | Boolean expressions | Boolean expressions | Boolean expressions |
| Graphs | Dictionaries of sets | `Map` of `Set` | `map` of `set` |
| Recursion | Direct and compact | Direct and functional | Explicit typed implementation |
| Errors | Exceptions | Exceptions | Exceptions |
| Testing | `assert` | `console.assert` | `assert` |
| Async modeling | Not central here | `Promise`, `async`, `await` | State machine modeling |
| Genericity | Dynamic typing and generics via typing | Dynamic language | Templates and static typing |

The mathematical concepts are language-independent, while their computational representations differ.

---

# 64. Real-World Applications

Discrete mathematical structures appear throughout computer science.

## Algorithms

Graphs, trees, relations, recurrence relations, and combinatorics form the mathematical foundation of algorithm design.

## Databases

Relations, tuples, keys, constraints, and joins have direct mathematical interpretations.

## Cybersecurity

Boolean logic, relations, sets, access-control models, and state machines are used to specify security policies.

## Software Engineering

Finite-state machines and dependency graphs help model workflows and system behavior.

## Compilers

Formal languages, syntax trees, grammars, relations, and graph algorithms are fundamental.

## Networking

Graphs model connectivity, routing, and reachability.

## Artificial Intelligence and Data Processing

Sets, relations, graphs, logic, probability-related structures, and combinatorial search support many computational methods.

## Digital Systems

Boolean algebra provides the formal basis for digital logic and circuit simplification.

## Operating Systems

Processes, resources, dependency relationships, states, and scheduling can be represented using discrete structures.

---

# 65. Implementation-Specific Educational Focus

## Python

The Python implementation is strongest as a mathematical laboratory.

It demonstrates how compact language features can express formal concepts directly.

Particularly important examples include:

- set algebra
- truth tables
- relation predicates
- function classification
- graph traversal
- recursive definitions
- mathematical assertions

## JavaScript

The JavaScript implementation emphasizes mathematical structures embedded into application behavior.

Particularly important examples include:

- `Set`
- `Map`
- higher-order functions
- closures
- object-oriented structures
- graph traversal
- memoization
- asynchronous state transitions

## C++

The C++ implementation emphasizes an integrated system design.

The university platform connects:

- users
- roles
- permissions
- course dependencies
- workflow states
- mathematical functions
- graph algorithms
- formal validation

The program also demonstrates type-aware modeling, exceptions, assertions, and standard-library data structures.

---

# 66. Mathematical Invariants in Software

An invariant is a property that should remain true during the operation of a system.

Examples from the implementations include:

- a set contains no duplicates
- a bijection maps distinct inputs to distinct outputs
- a BST's inorder traversal remains sorted
- a permission must belong to the defined permission set
- a workflow can only move along permitted transitions
- every course dependency must reference known courses
- a topological ordering must respect every dependency edge

Invariants are valuable because they provide a precise definition of correctness.

---

# 67. Formal Versus Computational Reasoning

Mathematical reasoning and computational reasoning complement each other.

A mathematical definition tells us what a structure means.

An algorithm specifies how to manipulate that structure.

An implementation represents the algorithm in a programming language.

Tests verify selected behaviors.

Proofs establish properties under formal assumptions.

For example:

1. A partial order is mathematically defined by three properties.
2. A program checks those three properties.
3. A graph algorithm uses the ordering.
4. Assertions verify selected cases.
5. A proof can establish correctness of the algorithm independently of individual tests.

This distinction is central to rigorous computer science.

---

# 68. Key Formal Relationships

The implementations collectively establish the following conceptual chain:

`Set → Cartesian Product → Relation`

`Relation + one-output constraint → Function`

`Function + injectivity + surjectivity → Bijection`

`Relation + reflexive + symmetric + transitive → Equivalence Relation`

`Equivalence Relation → Partition`

`Relation + reflexive + antisymmetric + transitive → Partial Order`

`Directed Acyclic Graph → Topological Ordering`

`Boolean Propositions → Logic`

`Predicates + Quantifiers → Predicate Logic`

`Vertices + Edges → Graph`

`Graph + hierarchical constraints → Tree or dependency structure`

`Set + operation + algebraic laws → Algebraic Structure`

These relationships explain why discrete mathematics is not merely a collection of unrelated topics. Many concepts are constructed from earlier ones.

---

# 69. Practical Interpretation

A useful way to interpret the entire implementation set is to treat mathematical structures as formal data models.

A set answers:

"What objects exist?"

A relation answers:

"How can two objects be connected?"

A function answers:

"Which single output does each input produce?"

A graph answers:

"How are many objects connected?"

A partial order answers:

"Which objects must precede or contain other objects?"

Logic answers:

"When is a condition true?"

A state-transition relation answers:

"Which changes are permitted?"

Counting answers:

"How many possible configurations exist?"

Complexity analysis answers:

"How does the computational cost grow as the structure becomes larger?"

These questions occur repeatedly in real software systems.

---

# 70. Executable Verification Included

The Python implementation verifies:

- set identities
- relation properties
- equivalence relations
- partial orders
- function properties
- logical equivalence
- recurrence calculations
- matrix operations
- counting formulas
- graph invariants
- authorization rules

The JavaScript implementation verifies:

- set behavior
- logical identities
- finite-function properties
- recursion
- graph algorithms
- topological ordering
- asynchronous state transitions
- application-level policy conditions

The C++ implementation verifies:

- mathematical set operations
- relation properties
- finite functions
- inverse construction
- equivalence classes
- graph dependencies
- cycle detection
- authorization rules
- state-machine constraints
- counting formulas
- exception behavior

This creates a direct relationship between mathematical definitions and executable behavior.

---

# 71. Important Limitations of the Examples

The implementations intentionally use finite domains for computational demonstrations.

Some mathematical concepts have infinite domains, while the programs necessarily operate on finite representations.

Truth-table enumeration is exact for the selected variables but does not scale well with large numbers of variables.

Power-set generation is inherently exponential because the output itself contains exponentially many subsets.

The basic binary search tree is not self-balancing.

The authorization system models logical permission relationships but is not a complete identity, credential, auditing, or distributed-security system.

The database examples model relational concepts in memory rather than implementing a complete database engine.

The mathematical abstractions remain useful even when production implementations require substantially more infrastructure.

---

# 72. Core Competencies Demonstrated

The three implementations establish practical understanding of:

- finite set theory
- set algebra
- Cartesian products
- relations
- relation properties
- equivalence relations
- equivalence classes
- partitions
- partial orders
- minimal and maximal elements
- functions
- injective mappings
- surjective mappings
- bijections
- inverse functions
- composition
- propositions
- logical connectives
- truth tables
- tautologies
- contradictions
- logical equivalence
- predicate logic
- quantifiers
- inference
- Boolean algebra
- normal forms
- recursion
- induction-oriented verification
- graphs
- trees
- graph traversal
- topological sorting
- algebraic structures
- matrices
- counting
- pigeonhole reasoning
- database relations
- finite-state machines
- authorization logic
- algorithmic complexity
- invariants
- executable verification
