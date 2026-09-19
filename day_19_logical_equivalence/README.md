# Logical equivalence

## Topic scope

Logical equivalence is the study of propositions that have the same truth value for every possible assignment of their variables. This implementation set focuses on four central transformation families:

- De Morgan's laws
- Implication equivalences
- Distributive laws
- Absorption laws

The implementations also connect these laws with truth tables, Boolean algebra, symbolic expression trees, tautologies, contradictions, contingencies, counterexamples, normal forms, Boolean circuits, rule engines, query conditions, security policies, validation, and computational complexity.

The Python implementation provides a broad educational treatment with executable symbolic logic structures. The JavaScript implementation emphasizes application-oriented symbolic evaluation and integration patterns. The C++ implementation develops an industry-style access-control policy engine using an expression-tree architecture.

## Fundamental concepts

### Proposition

A proposition is a statement that has exactly one of two classical truth values:

- True
- False

Examples include:

- `P`: "The request is authenticated."
- `Q`: "The request is authorized."
- `R`: "The account is suspended."

A proposition is not required to be factually true. It must simply have a definite truth value under the logical model being used.

### Boolean values

Classical propositional logic uses two truth values:

- `T` for true
- `F` for false

The implementations use the native Boolean types of Python, JavaScript, and C++.

### Negation

Negation reverses a proposition's truth value.

The notation is:

`~P`

If `P` is true, `~P` is false. If `P` is false, `~P` is true.

### Conjunction

Conjunction corresponds to logical AND.

The notation is:

`P AND Q`

The result is true only when both `P` and `Q` are true.

### Disjunction

Disjunction corresponds to logical OR.

The notation is:

`P OR Q`

The result is true when at least one operand is true.

### Exclusive OR

Exclusive OR, or XOR, is true when exactly one operand is true.

`P XOR Q`

Its Boolean representation can be written as:

`(P OR Q) AND ~(P AND Q)`

### Implication

Material implication is written:

`P -> Q`

It is false only when `P` is true and `Q` is false.

| P | Q | P -> Q |
|---|---|--------|
| F | F | T |
| F | T | T |
| T | F | F |
| T | T | T |

The unusual-looking rows where a false antecedent produces a true implication are a consequence of the formal definition of material implication.

### Biconditional

A biconditional is written:

`P <-> Q`

It is true when both propositions have the same truth value.

It can also be expressed as:

`(P -> Q) AND (Q -> P)`

## Logical equivalence

Two propositions `P` and `Q` are logically equivalent when they produce the same truth value under every possible assignment of their variables.

Notation commonly includes:

`P <-> Q`

or

`P ≡ Q`

A practical computational test is:

1. Collect every variable appearing in either expression.
2. Generate every possible Boolean assignment.
3. Evaluate both expressions for every assignment.
4. Compare their results.
5. If no assignment produces different values, the expressions are equivalent.

For `n` independent Boolean variables, there are `2^n` assignments.

For example:

`~(P AND Q)`

and

`~P OR ~Q`

are equivalent because every possible assignment gives the same result.

## Why truth tables matter

A truth table gives an exhaustive semantic verification for a finite propositional expression.

For two variables there are:

`2^2 = 4`

assignments.

For three variables there are:

`2^3 = 8`

assignments.

For ten variables there are:

`2^10 = 1024`

assignments.

The Python, JavaScript, and C++ implementations contain automated equivalence checkers that use this method.

Truth-table verification is particularly useful for:

- learning logical identities
- validating transformations
- generating counterexamples
- testing Boolean conditions
- verifying small policy expressions
- checking compiler or query rewrites
- studying digital logic

Its main limitation is exponential growth in the number of variables.

## Core laws of Boolean algebra

### Identity laws

`P AND T ≡ P`

`P OR F ≡ P`

The identity element leaves the proposition unchanged.

### Domination laws

`P AND F ≡ F`

`P OR T ≡ T`

A dominating value determines the result regardless of `P`.

### Idempotent laws

`P AND P ≡ P`

`P OR P ≡ P`

Repeating the same condition does not change the result.

### Complement laws

`P AND ~P ≡ F`

`P OR ~P ≡ T`

A proposition and its negation cannot both be true, while at least one of them must be true in classical two-valued logic.

### Double negation

`~~P ≡ P`

Applying negation twice restores the original proposition.

### Commutative laws

`P AND Q ≡ Q AND P`

`P OR Q ≡ Q OR P`

The order of operands does not change the result.

### Associative laws

`(P AND Q) AND R ≡ P AND (Q AND R)`

`(P OR Q) OR R ≡ P OR (Q OR R)`

Parenthesization can be changed when the same associative operator is used.

These laws are useful when restructuring expressions before applying more specialized transformations.

# De Morgan's laws

De Morgan's laws describe how negation interacts with conjunction and disjunction.

## First De Morgan law

`~(P AND Q) ≡ ~P OR ~Q`

The negation of a conjunction becomes a disjunction of negated operands.

The Python implementation constructs both expressions symbolically and checks them against every possible assignment.

The JavaScript implementation performs the same semantic verification through its `Proposition` hierarchy.

The C++ implementation applies the law to an access-control denial expression.

## Second De Morgan law

`~(P OR Q) ≡ ~P AND ~Q`

The negation of a disjunction becomes a conjunction of negated operands.

These two laws can be remembered as a transformation pattern:

- Negate every operand.
- Change AND to OR.
- Change OR to AND.

For example:

`~(P AND Q AND R)`

becomes:

`~P OR ~Q OR ~R`

Similarly:

`~(P OR Q OR R)`

becomes:

`~P AND ~Q AND ~R`

## Practical interpretation

Suppose access requires:

`Authenticated AND Authorized AND NOT Suspended`

The negation of access is:

`NOT (Authenticated AND Authorized AND NOT Suspended)`

Applying De Morgan's law gives:

`NOT Authenticated OR NOT Authorized OR Suspended`

The two expressions have exactly the same Boolean meaning.

This type of transformation is useful when an application needs to express a positive condition and its failure condition separately.

# Implication equivalence

## Implication elimination

The most important implication identity is:

`P -> Q ≡ ~P OR Q`

This allows implication to be expressed using only NOT and OR.

The Python, JavaScript, and C++ implementations all demonstrate this equivalence.

## Contrapositive

An implication is equivalent to its contrapositive:

`P -> Q ≡ ~Q -> ~P`

For example:

`RequestValid -> IdentityVerified`

is equivalent to:

`NOT IdentityVerified -> NOT RequestValid`

The equivalence is semantic. It does not mean that the two statements have the same wording or the same practical interpretation in every natural-language context.

## Converse

The converse of:

`P -> Q`

is:

`Q -> P`

The converse is not generally equivalent to the original implication.

The C++ case study explicitly checks both the contrapositive and the converse and reports a counterexample for the converse.

This distinction is one of the most common sources of error when manipulating implications.

## Negated implication

The negation of an implication has an especially useful form:

`~(P -> Q) ≡ P AND ~Q`

This follows directly from implication elimination:

`~(P -> Q)`

becomes:

`~(~P OR Q)`

Applying De Morgan's law gives:

`~~P AND ~Q`

and double negation gives:

`P AND ~Q`

Therefore, an implication fails exactly when its antecedent is true and its consequent is false.

# Distributive laws

Boolean algebra has two important distributive laws.

## AND over OR

`P AND (Q OR R)`

is equivalent to:

`(P AND Q) OR (P AND R)`

The Python, JavaScript, and C++ implementations verify this transformation.

## OR over AND

`P OR (Q AND R)`

is equivalent to:

`(P OR Q) AND (P OR R)`

Both directions are valid in Boolean algebra.

These laws are important because they allow an expression to be reorganized into particular structural forms.

## Connection with normal forms

Distributive laws are central to transformations into:

- Conjunctive Normal Form
- Disjunctive Normal Form

Conjunctive Normal Form, or CNF, is an AND of OR clauses.

For example:

`(P OR Q) AND (~P OR R)`

Disjunctive Normal Form, or DNF, is an OR of AND terms.

For example:

`(P AND ~Q) OR (~P AND R)`

De Morgan's laws help move negations toward individual variables, while distributive laws restructure the expression.

# Absorption laws

Absorption laws eliminate redundant logical structure.

## First absorption law

`P OR (P AND Q) ≡ P`

If `P` is already sufficient to make the OR expression true, the additional `P AND Q` term cannot introduce a result that was not already covered by `P`.

## Second absorption law

`P AND (P OR Q) ≡ P`

If `P` is already required by the outer AND, the additional OR condition does not alter the result.

## Why absorption matters

Absorption can reduce an expression without changing its semantics.

For example:

`Verified OR (Verified AND Premium)`

simplifies to:

`Verified`

The original expression may appear more specific because it contains `Premium`, but the `Premium` condition is redundant in the presence of the outer `Verified` disjunction.

This is useful in:

- policy simplification
- Boolean circuit optimization
- query condition rewriting
- rule-engine optimization
- configuration validation
- symbolic algebra systems

# Python implementation

The Python program is designed as a standalone study file.

It starts with direct Boolean functions such as `logical_and`, `logical_or`, and `logical_implies`. These functions make the fundamental semantics visible without requiring a symbolic expression system.

The program then introduces an object-oriented expression hierarchy.

The base `Proposition` class represents a symbolic Boolean expression. Concrete types include:

- `Variable`
- `Constant`
- `Not`
- `And`
- `Or`
- `Implies`
- `Iff`
- `Xor`

Each expression supports:

- evaluation against an assignment
- variable discovery
- readable string representation
- composition with other expressions

For example, expressions can be composed conceptually as:

`p & q`

and:

`p.implies(q)`

The expression objects form a tree. An expression such as:

`~(P AND Q)`

is represented by a `Not` node containing an `And` node, which contains two `Variable` nodes.

This structure is useful because logical expressions can be inspected and evaluated recursively.

## Python equivalence checker

The `are_equivalent` function collects variables from both expressions and evaluates them against every possible assignment.

For small expressions this gives an exact semantic answer.

The `find_counterexample` function performs a related operation. Instead of returning only whether expressions are equivalent, it returns the first assignment under which their values differ.

A counterexample is sufficient to disprove logical equivalence.

## Python implication rewriting

The `rewrite_implication` function recursively eliminates implication operators.

For:

`P -> Q`

it produces:

`~P OR Q`

For a biconditional, the implementation represents the expression using two implications.

This demonstrates an important symbolic-processing technique: a complex operator can be replaced with a combination of more primitive operators while preserving semantics.

## Python law suite

The automated verification suite checks:

- De Morgan's first law
- De Morgan's second law
- implication elimination
- contrapositive equivalence
- both distributive laws
- both absorption laws

This is stronger than checking only one example because the checker evaluates every possible assignment.

# JavaScript implementation

The JavaScript implementation uses an object-oriented expression hierarchy similar to the Python implementation, but it emphasizes JavaScript-specific application behavior.

The main classes are:

- `Proposition`
- `Variable`
- `Constant`
- `Not`
- `And`
- `Or`
- `Xor`
- `Implies`
- `Iff`

JavaScript's native Boolean operators are demonstrated through functions such as `logicalImplies`.

The symbolic expressions are represented as objects. The `variables()` method returns a `Set`, allowing the application to collect distinct variables without manually managing duplicates.

## JavaScript truth-table generation

`generateAssignments()` creates all Boolean assignments for a collection of variables.

The number of generated assignments is:

`2^n`

where `n` is the number of distinct variables.

The implementation uses bit operations to generate combinations efficiently for small truth tables.

## JavaScript counterexamples

`findCounterexample()` compares two expressions and returns an assignment where they disagree.

For example, comparing:

`P -> Q`

with:

`Q -> P`

produces a counterexample because the converse is not generally equivalent to the original implication.

## JavaScript asynchronous integration

The file also contains an asynchronous wrapper around equivalence checking.

The logical calculation itself is not inherently asynchronous, but application-level systems may perform equivalence checking as part of:

- browser interfaces
- server requests
- background jobs
- policy validation services
- interactive editors

Returning a `Promise` allows the synchronous logical engine to fit naturally into an asynchronous application architecture.

## JavaScript rule engine

The `Rule` and `RuleEngine` classes demonstrate how symbolic Boolean conditions can become application policies.

A rule has:

- a name
- a Boolean condition
- a Boolean result

The engine evaluates the conditions against an assignment and returns the rules that fire.

This demonstrates how propositional logic can move from mathematical notation into executable decision systems.

# C++ case study

## Problem being modeled

The C++ program models a protected-resource access-control system.

Access is granted when:

`Authenticated AND Authorized AND NOT Suspended`

The system must be able to:

- represent the policy
- evaluate the policy
- express denial as the negation of access
- transform the denial condition using De Morgan's law
- verify that the transformed condition is equivalent
- evaluate multiple user states
- identify invalid input
- protect against excessively large truth-table requests

## Expression-tree architecture

The C++ program uses an abstract `Expression` class.

Each expression provides:

- `evaluate()`
- `variables()`
- `toString()`

The implementation uses `std::shared_ptr` through the `ExpressionPtr` alias.

The concrete expression types include:

- `Variable`
- `Constant`
- `UnaryExpression`
- `BinaryExpression`

The expression hierarchy is an abstract syntax tree for Boolean logic.

For example, the access policy can be represented conceptually as:

`AND(AND(Authenticated, Authorized), NOT(Suspended))`

Each node evaluates its children recursively.

## Operator representation

The `Operator` enumeration contains:

- `Not`
- `And`
- `Or`
- `Xor`
- `Implies`
- `Iff`

The binary expression evaluator implements the semantic behavior of each operator.

Implication is evaluated according to:

`P -> Q ≡ ~P OR Q`

The implementation also takes advantage of short-circuit behavior.

For implication, if `P` is false, the result is immediately true.

For conjunction, if the left operand is false, the right operand does not need to be evaluated.

For disjunction, if the left operand is true, the right operand does not need to be evaluated.

## Access-control transformation

The original access condition is:

`Authenticated AND Authorized AND NOT Suspended`

The negated condition is:

`NOT (Authenticated AND Authorized AND NOT Suspended)`

Applying De Morgan's laws produces:

`NOT Authenticated OR NOT Authorized OR Suspended`

The C++ program verifies the equivalence exhaustively.

This demonstrates an important engineering principle: a policy can be transformed for readability or implementation purposes while preserving its formal Boolean semantics.

## Policy decisions

The case study evaluates several assignments.

A user who is:

`Authenticated = true`

`Authorized = true`

`Suspended = false`

satisfies the access condition.

A user who is unauthorized, unauthenticated, or suspended does not satisfy the complete access condition.

The expression evaluator does not infer missing security information. It requires explicit assignments for the variables that occur in the expression.

# Important distinctions

## Equivalence versus implication

Logical equivalence means that two expressions have identical truth values for every assignment.

Implication is a relationship between propositions and is itself a proposition.

`P -> Q`

does not mean:

`P <-> Q`

Equivalence requires both directions:

`(P -> Q) AND (Q -> P)`

## Implication versus converse

Original:

`P -> Q`

Converse:

`Q -> P`

These are generally not equivalent.

## Implication versus contrapositive

Original:

`P -> Q`

Contrapositive:

`~Q -> ~P`

These are logically equivalent.

## Negating an implication

Correct:

`~(P -> Q) ≡ P AND ~Q`

Incorrect transformations commonly arise when the negation is distributed without first eliminating implication.

## De Morgan's laws versus distribution

De Morgan's laws transform negation:

`~(P AND Q) ≡ ~P OR ~Q`

Distribution changes the structural relationship between operators:

`P AND (Q OR R) ≡ (P AND Q) OR (P AND R)`

They serve different purposes even though both can be used during Boolean simplification.

## Absorption versus distribution

Distribution expands or restructures an expression.

Absorption removes redundant structure.

For example:

`P OR (P AND Q)`

does not need distribution to simplify. Absorption directly gives:

`P`

# Tautology, contradiction, and contingency

A tautology is true for every assignment.

Example:

`P OR ~P`

A contradiction is false for every assignment.

Example:

`P AND ~P`

A contingency is true for some assignments and false for others.

Example:

`P -> Q`

The Python, JavaScript, and C++ implementations contain classification logic for these three categories.

# Counterexamples

A counterexample is a specific variable assignment under which two supposedly equivalent expressions produce different results.

Suppose someone claims:

`P -> Q ≡ Q -> P`

Take:

`P = true`

`Q = false`

Then:

`P -> Q = false`

while:

`Q -> P = true`

Therefore the two expressions cannot be logically equivalent.

A single valid counterexample disproves universal equivalence.

This makes counterexample generation a practical debugging tool for Boolean transformations.

# Edge cases

## Constant expressions

The logical system supports:

`T`

and:

`F`

They contain no variables and therefore require no assignment.

Examples:

`T AND P ≡ P`

`F OR P ≡ P`

## Missing variable values

An expression containing `P` cannot be correctly evaluated if the assignment does not provide a value for `P`.

The Python and JavaScript implementations explicitly validate this condition.

The C++ implementation throws an exception for a missing variable assignment.

## Empty variable names

The C++ implementation rejects empty variable names because a symbolic variable needs an identifiable name.

The Python and JavaScript versions similarly treat variable names as explicit identifiers in their respective object models.

## Large variable sets

Exhaustive equivalence testing requires `2^n` assignments.

This becomes expensive rapidly.

The C++ case study therefore protects the demonstration against requests involving more than 20 variables when generating complete truth tables.

This limit is an engineering safeguard for the sample program rather than a mathematical limitation of propositional logic.

# Common mistakes

## Incorrect De Morgan transformation

Incorrect:

`~(P AND Q) ≡ ~P AND ~Q`

Correct:

`~(P AND Q) ≡ ~P OR ~Q`

## Forgetting to negate every operand

For:

`~(P OR Q OR R)`

the correct result is:

`~P AND ~Q AND ~R`

Every operand must be negated.

## Confusing converse and contrapositive

For:

`P -> Q`

the contrapositive is:

`~Q -> ~P`

The converse is:

`Q -> P`

Only the contrapositive is generally equivalent to the original implication.

## Assuming visual similarity implies equivalence

Two expressions may look structurally similar but have different truth tables.

Formal verification should be based on semantics rather than appearance.

## Ignoring operator precedence

Expressions involving multiple operators should be parenthesized when the intended grouping is important.

For example:

`P OR Q AND R`

can be ambiguous to readers unfamiliar with the chosen precedence convention.

Explicit parentheses make the intended structure clear:

`P OR (Q AND R)`

# Normal forms

## Conjunctive Normal Form

CNF is an AND of OR clauses.

Example:

`(P OR Q) AND (~P OR R)`

CNF is useful in:

- SAT solving
- constraint systems
- symbolic reasoning
- automated verification
- database-style Boolean conditions

## Disjunctive Normal Form

DNF is an OR of AND terms.

Example:

`(P AND ~Q) OR (~P AND R)`

DNF can represent the conditions under which an expression evaluates to true.

De Morgan's laws and distributive laws are central tools when transforming expressions toward these forms.

# Boolean circuits

Logical expressions can be implemented as circuits.

For example:

`~(P AND Q)`

corresponds to an AND gate followed by a NOT gate.

De Morgan's law gives the equivalent circuit:

`~P OR ~Q`

This corresponds to two NOT gates followed by an OR gate.

Because the expressions are logically equivalent, their output is identical for every possible input combination.

This relationship is important in:

- digital circuit design
- hardware optimization
- FPGA logic
- processor design
- embedded systems
- Boolean synthesis

# Query conditions

Logical equivalence is also relevant when software systems rewrite conditions.

For example:

`NOT (AgeEligible AND Verified)`

can be rewritten as:

`NOT AgeEligible OR NOT Verified`

A query optimizer or application may prefer one form because of implementation characteristics, readability, or execution strategy.

The logical transformation itself does not guarantee that two database queries will have identical performance. Semantic equivalence and execution cost are separate concerns.

# Security considerations

Boolean equivalence can be useful when reviewing security policies.

Consider:

`Authenticated AND Authorized AND NOT Suspended`

Its negation is:

`NOT Authenticated OR NOT Authorized OR Suspended`

The transformation is logically correct.

Security engineering still requires more than Boolean correctness. A production authorization system must account for:

- identity verification
- authorization data integrity
- policy precedence
- state consistency
- secure defaults
- audit logging
- input validation
- race conditions
- failure handling
- privilege boundaries
- policy update procedures

A mathematically equivalent expression can still be used incorrectly if the surrounding application supplies incorrect state or applies the policy at the wrong point.

# Performance considerations

## Truth-table approach

For `n` variables:

`Number of assignments = 2^n`

This makes exhaustive equivalence checking exponential in the number of variables.

For small expressions this is simple and reliable.

For larger symbolic systems, alternative techniques may include:

- canonical Boolean representations
- Binary Decision Diagrams
- SAT-based equivalence checking
- symbolic simplification
- algebraic normalization
- memoization
- expression hashing

These methods have different performance characteristics and implementation complexity.

## Short-circuit evaluation

The C++ implementation uses short-circuit evaluation for AND, OR, and implication.

For:

`P AND Q`

if `P` is false, `Q` cannot change the result.

For:

`P OR Q`

if `P` is true, `Q` cannot change the result.

For:

`P -> Q`

if `P` is false, the result is immediately true.

Short-circuiting can reduce unnecessary computation.

## Expression trees

Expression trees allow recursive evaluation and systematic transformations.

The cost of evaluating one expression for one assignment is generally related to the number of nodes in the expression tree.

Exhaustive equivalence checking multiplies that cost by the number of assignments.

# Implementation considerations

## Python

Python is useful for educational symbolic logic because:

- Boolean syntax is concise.
- Classes can represent expression trees clearly.
- Sets and dictionaries simplify variable and assignment management.
- Exceptions make validation straightforward.
- Higher-level abstractions allow the mathematical structure to remain visible.

The Python implementation favors readability and experimentation.

## JavaScript

JavaScript is useful when logical expressions become part of application interfaces and web systems.

The implementation demonstrates:

- classes
- `Set`
- object-based assignments
- Promises
- asynchronous functions
- application-oriented rule evaluation
- runtime error handling

The JavaScript design can naturally be connected to browser applications or Node.js services.

## C++

C++ provides explicit control over object architecture and resource representation.

The case study demonstrates:

- abstract classes
- virtual functions
- smart pointers
- enumerations
- STL containers
- exceptions
- structured result types
- recursive expression evaluation
- explicit workload protection

The C++ implementation is particularly suitable for demonstrating how Boolean logic can become part of a larger systems-oriented component.

# Real-world applications

Logical equivalence appears in many technical areas.

## Digital logic

Circuit designers can replace one gate arrangement with another equivalent arrangement.

## Compilers

Compilers may transform conditions while preserving program semantics.

## Query optimization

Database systems can transform predicates when the resulting query remains semantically equivalent.

## Access-control systems

Authorization rules can be expressed, transformed, audited, and tested as Boolean conditions.

## Configuration systems

Complex feature and environment conditions can be simplified using Boolean identities.

## Rule engines

Business rules can be represented as propositional expressions and evaluated against structured input.

## Verification

Formal verification systems use logical transformations to reason about system behavior.

## SAT solving

Many computational problems are translated into Boolean formulas whose structure is manipulated using equivalence-preserving transformations.

## Digital hardware

Logic synthesis uses Boolean identities to produce equivalent circuits with desirable area, power, timing, or implementation characteristics.

# Design trade-offs

## Exhaustive verification

Advantages:

- straightforward
- mathematically direct
- easy to explain
- produces concrete counterexamples
- complete for finite propositional expressions

Limitations:

- exponential number of assignments
- unsuitable for large variable counts without optimization
- repeated expression evaluation can become expensive

## Symbolic simplification

Advantages:

- may dramatically reduce expression size
- can avoid enumerating every assignment
- useful for large structured expressions

Limitations:

- requires more complex algorithms
- simplification itself can be computationally expensive
- some transformations require careful canonicalization

## Expression trees

Advantages:

- natural representation of nested logic
- supports recursive evaluation
- supports transformation passes
- preserves structural information

Limitations:

- creates object or node overhead
- equivalent expressions can have different tree structures
- semantic equivalence cannot be inferred solely from tree shape

# Testing strategy

A robust logical-equivalence implementation should test several categories.

## Identity tests

Examples:

`P AND T ≡ P`

`P OR F ≡ P`

## Negation tests

Examples:

`~~P ≡ P`

`P AND ~P ≡ F`

`P OR ~P ≡ T`

## De Morgan tests

Examples:

`~(P AND Q) ≡ ~P OR ~Q`

`~(P OR Q) ≡ ~P AND ~Q`

## Implication tests

Examples:

`P -> Q ≡ ~P OR Q`

`P -> Q ≡ ~Q -> ~P`

`~(P -> Q) ≡ P AND ~Q`

## Distribution tests

Examples:

`P AND (Q OR R) ≡ (P AND Q) OR (P AND R)`

`P OR (Q AND R) ≡ (P OR Q) AND (P OR R)`

## Absorption tests

Examples:

`P OR (P AND Q) ≡ P`

`P AND (P OR Q) ≡ P`

## Negative tests

A testing system should also verify that known non-equivalent expressions are rejected.

For example:

`P -> Q`

must not be classified as equivalent to:

`Q -> P`

A counterexample should be available.

# Relationship among the four primary topics

The four requested equivalence families complement one another.

De Morgan's laws primarily control how negation moves through AND and OR.

Implication equivalence replaces implication with primitive Boolean operators and provides the contrapositive transformation.

Distributive laws reorganize AND and OR relationships.

Absorption laws eliminate redundant structures.

A complex simplification can therefore use several laws in sequence.

For example, a transformation may first eliminate implication, then move negations inward using De Morgan's laws, then distribute operators, and finally remove redundant terms using absorption.

The validity of each step can be verified semantically by checking that the expression before and after the transformation has identical truth values.

# Conceptual model of equivalence checking

The central computational model used throughout the three implementations is:

1. Represent a Boolean expression.
2. Determine its variables.
3. Generate all possible Boolean assignments.
4. Evaluate the expression under each assignment.
5. Compare two expressions assignment by assignment.
6. Return equivalence if every result matches.
7. Otherwise return a counterexample.

This approach directly implements the mathematical definition of logical equivalence.

# Important limitation of classical propositional logic

The examples use classical two-valued propositional logic.

Each proposition has exactly one truth value:

`True`

or:

`False`

Real systems can involve richer semantics, including:

- unknown values
- null values
- three-valued logic
- probabilistic conditions
- temporal conditions
- fuzzy logic
- non-classical logics

For example, SQL uses three-valued logic involving `TRUE`, `FALSE`, and `UNKNOWN`. A Boolean identity that is valid under classical two-valued semantics may require separate analysis when transferred directly into another logical system.

Therefore, an equivalence should always be interpreted within the semantics of the system in which it is being applied.

# Files represented by the implementations

The Python program is a comprehensive executable study of logical equivalence and provides symbolic expression classes, truth-table generation, equivalence checking, counterexamples, law verification, classification, rewriting, rule evaluation, Boolean circuit interpretation, query conditions, and security-policy examples.

The JavaScript file provides an application-oriented symbolic logic engine with JavaScript classes, `Set`-based variable collection, truth-table generation, counterexample detection, asynchronous integration, validation, and a rule engine.

The C++ program develops the subject as a technical case study around access-control policy evaluation. It demonstrates expression trees, smart pointers, recursive evaluation, short-circuit behavior, exhaustive semantic comparison, counterexample reporting, exception handling, complexity protection, and policy transformation.

# Compilation and execution

## Python

Run the Python implementation with:

`python logical_equivalence.py`

No third-party Python package is required.

## JavaScript

Run the JavaScript implementation with a modern Node.js runtime:

`node logical_equivalence.js`

No third-party npm package is required.

## C++

Compile with C++17 or later:

`g++ -std=c++17 -O2 logical_equivalence.cpp -o logical_equivalence`

Then execute the resulting program.

The C++ implementation uses only the standard library.
