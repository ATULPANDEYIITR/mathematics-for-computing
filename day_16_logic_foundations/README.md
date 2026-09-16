# Logic foundations

## Introduction

Propositional logic is a formal system for representing and evaluating statements that have truth values. It provides a precise way to combine simple propositions into compound propositions and determine when those combinations are true or false.

This implementation set studies four closely related foundations:

- statements and propositions
- truth values
- logical connectives
- compound logical expressions

The three implementations approach the subject from different technical perspectives. Python emphasizes concise experimentation and formal verification. JavaScript demonstrates Boolean logic in an application-oriented and event-driven language. C++ develops a more structured policy-engine case study using classes, expression trees, validation, and exhaustive logical analysis.

The examples use Boolean truth values:

- `True` or `False` in Python
- `true` or `false` in JavaScript
- `true` or `false` in C++

The central mathematical idea is simple: a proposition has a truth value, and logical connectives combine propositions according to precisely defined rules.

---

## Statements and propositions

A **statement** is a declarative sentence that makes an assertion.

A **proposition** is a statement that can be assigned exactly one truth value under a specified interpretation.

For example:

- `2 + 2 = 4` is a proposition and is true.
- `7 is even` is a proposition and is false.
- `Python is a programming language` is a proposition and is true.

Not every sentence is a proposition.

A question such as `What time is it?` does not assert something that can simply be classified as true or false.

A command such as `Close the door.` is an instruction rather than a proposition.

An open sentence such as `x > 5` is not normally a complete proposition until a value or domain interpretation for `x` is supplied.

This distinction is important because propositional logic operates on truth-valued assertions rather than arbitrary sentences.

---

## Truth values

Classical propositional logic uses two truth values:

- true
- false

This is called **bivalent logic** because each proposition receives one of two possible truth values.

A Python representation is:

`p = True`

A JavaScript representation is:

`const p = true;`

A C++ representation is:

`bool p = true;`

The two truth values can be represented mathematically as `T` and `F`.

For one proposition there are two possible assignments:

| p |
|---|
| F |
| T |

For two propositions there are four possible assignments:

| p | q |
|---|---|
| F | F |
| F | T |
| T | F |
| T | T |

For `n` independent Boolean propositions, there are `2^n` possible truth assignments.

---

## Atomic and compound propositions

An **atomic proposition** is a basic proposition that is not constructed from smaller propositions using logical connectives.

If:

`p = "The server is available"`

then `p` is atomic.

A **compound proposition** combines propositions.

For example:

`p ∧ q`

is a compound proposition.

A more complex expression is:

`(p ∧ q) ∨ ¬r`

The Python implementation represents this with:

`(p and q) or (not r)`

The JavaScript implementation uses:

`(p && q) || !r`

The C++ implementation constructs an expression tree representing the same logical structure.

---

## Logical connectives

Logical connectives are operators that construct new propositions from existing propositions.

The principal connectives demonstrated in the implementations are:

| Logical notation | Name | Meaning |
|---|---|---|
| `¬p` | negation | not p |
| `p ∧ q` | conjunction | p and q |
| `p ∨ q` | disjunction | p or q |
| `p ⊕ q` | exclusive OR | exactly one is true |
| `p → q` | implication | if p, then q |
| `p ↔ q` | biconditional | p if and only if q |

---

## Negation

The negation of `p` is written:

`¬p`

It reverses the truth value.

| p | ¬p |
|---|---|
| F | T |
| T | F |

Python uses:

`not p`

JavaScript and C++ use:

`!p`

The implementations define explicit functions for negation so the mathematical operation can be separated from the surrounding application code.

---

## Conjunction

A conjunction is written:

`p ∧ q`

It is true only when both propositions are true.

| p | q | p ∧ q |
|---|---|---|
| F | F | F |
| F | T | F |
| T | F | F |
| T | T | T |

Python:

`p and q`

JavaScript:

`p && q`

C++:

`p && q`

A conjunction is useful for policies where every required condition must be satisfied.

For example:

`authenticated ∧ administrator ∧ accountActive`

requires all three conditions to be true.

---

## Disjunction

A disjunction is written:

`p ∨ q`

In ordinary propositional logic, this is **inclusive OR**. It is true when at least one operand is true.

| p | q | p ∨ q |
|---|---|---|
| F | F | F |
| F | T | T |
| T | F | T |
| T | T | T |

Python:

`p or q`

JavaScript:

`p || q`

C++:

`p || q`

Inclusive OR must be distinguished from exclusive OR.

---

## Exclusive OR

Exclusive OR is written:

`p ⊕ q`

It is true when exactly one operand is true.

| p | q | p ⊕ q |
|---|---|---|
| F | F | F |
| F | T | T |
| T | F | T |
| T | T | F |

The Python and JavaScript implementations represent this as inequality between Boolean values.

C++ represents the same idea using `!=`.

Exclusive OR is useful when two alternatives are mutually exclusive.

---

## Implication

Implication is written:

`p → q`

and read as:

`If p, then q.`

Its truth table is:

| p | q | p → q |
|---|---|---|
| F | F | T |
| F | T | T |
| T | F | F |
| T | T | T |

The only false case is when the antecedent is true and the consequent is false.

A fundamental equivalence is:

`p → q ≡ ¬p ∨ q`

The implementations use this equivalence directly.

The terminology is:

- `p` is the antecedent
- `q` is the consequent

Implication should not be confused with causation. In formal propositional logic, `p → q` describes a truth-functional relationship. It does not by itself establish that `p causes q`.

---

## Biconditional

The biconditional is written:

`p ↔ q`

and read as:

`p if and only if q`

It is true when both propositions have the same truth value.

| p | q | p ↔ q |
|---|---|---|
| F | F | T |
| F | T | F |
| T | F | F |
| T | T | T |

A useful equivalence is:

`p ↔ q ≡ (p → q) ∧ (q → p)`

This means a biconditional contains two implications.

---

## Operator precedence

Logical expressions can contain several connectives.

A commonly used precedence order is:

1. negation
2. conjunction
3. disjunction
4. implication
5. biconditional

For example:

`¬p ∨ q ∧ r`

is interpreted as:

`¬p ∨ (q ∧ r)`

Parentheses are preferred when they improve clarity.

The implementations deliberately use parentheses in compound expressions because application code benefits from explicit grouping.

---

## Truth tables

A **truth table** enumerates every possible assignment of truth values to the propositions in a formula.

For `n` variables, a complete truth table has:

`2^n`

rows.

The implementations contain reusable truth-table generators.

Python uses `itertools.product`.

JavaScript recursively generates all assignments.

C++ generates assignments by interpreting the bits of an integer mask.

The C++ approach makes the relationship between Boolean assignments and binary representation explicit.

For example, three variables require:

`2^3 = 8`

assignments.

Truth tables are useful for:

- evaluating formulas
- proving logical equivalence
- finding counterexamples
- identifying tautologies
- identifying contradictions
- checking argument validity
- studying satisfiability

---

## Tautologies

A **tautology** is a proposition that is true for every possible assignment of its variables.

The classic example is the law of excluded middle:

`p ∨ ¬p`

Its truth table is:

| p | ¬p | p ∨ ¬p |
|---|---|---|
| F | T | T |
| T | F | T |

The implementations automatically verify this property.

A tautology is not merely true under one example. It remains true under every possible assignment.

---

## Contradictions

A **contradiction** is a proposition that is false for every possible assignment.

The classic example is:

`p ∧ ¬p`

| p | ¬p | p ∧ ¬p |
|---|---|---|
| F | T | F |
| T | F | F |

The implementations classify such expressions as contradictions.

---

## Contingencies

A **contingency** is neither a tautology nor a contradiction.

Its truth depends on the assignment.

For example:

`p ∧ q`

is true when both propositions are true and false in all other assignments.

The implementations automatically distinguish these three classifications.

---

## Logical equivalence

Two formulas are **logically equivalent** when they have the same truth value for every possible assignment.

Logical equivalence is written:

`A ≡ B`

A truth-table test can establish equivalence by comparing the result of both formulas on every row.

The implementations verify several standard equivalences.

For example:

`¬(p ∧ q) ≡ ¬p ∨ ¬q`

and:

`¬(p ∨ q) ≡ ¬p ∧ ¬q`

These are De Morgan's laws.

---

## De Morgan's laws

The first law is:

`¬(p ∧ q) ≡ ¬p ∨ ¬q`

The second law is:

`¬(p ∨ q) ≡ ¬p ∧ ¬q`

They are important because they allow logical expressions to be transformed without changing their truth conditions.

These transformations appear in:

- programming conditions
- database predicates
- access-control rules
- digital circuits
- query optimization
- automated reasoning

The implementations verify both laws exhaustively.

---

## Important logical laws

The programs verify several standard laws.

### Double negation

`¬¬p ≡ p`

### Identity laws

`p ∧ True ≡ p`

`p ∨ False ≡ p`

### Domination laws

`p ∧ False ≡ False`

`p ∨ True ≡ True`

### Idempotent laws

`p ∧ p ≡ p`

`p ∨ p ≡ p`

### Complement laws

`p ∨ ¬p ≡ True`

`p ∧ ¬p ≡ False`

### Commutative laws

`p ∧ q ≡ q ∧ p`

`p ∨ q ≡ q ∨ p`

### Associative laws

`(p ∧ q) ∧ r ≡ p ∧ (q ∧ r)`

`(p ∨ q) ∨ r ≡ p ∨ (q ∨ r)`

### Distributive laws

`p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)`

`p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)`

These laws are useful for simplifying formulas and transforming expressions into forms suitable for automated processing.

---

## Implication, converse, inverse, and contrapositive

Given:

`p → q`

the **converse** is:

`q → p`

The **inverse** is:

`¬p → ¬q`

The **contrapositive** is:

`¬q → ¬p`

The original proposition is logically equivalent to its contrapositive:

`p → q ≡ ¬q → ¬p`

The converse and inverse are also logically equivalent:

`q → p ≡ ¬p → ¬q`

But the original implication is not generally equivalent to its converse or inverse.

The programs explicitly test these relationships rather than assuming them.

---

## Arguments

An argument consists of premises and a conclusion.

For example:

`p → q`

`p`

therefore:

`q`

This is **modus ponens**.

A truth-table approach establishes validity by searching for a row where:

- every premise is true
- the conclusion is false

If such a row exists, the argument is invalid.

If no such row exists, the argument is valid.

This is the method used by all three implementations.

---

## Invalid reasoning and counterexamples

Consider:

`p → q`

`q`

therefore:

`p`

This is called **affirming the consequent** and is not generally valid.

A counterexample is:

`p = False`

`q = True`

Then:

`p → q`

is true, and `q` is true, but `p` is false.

The programs contain a counterexample-search function that automatically finds such assignments.

Counterexamples are especially useful because one assignment is sufficient to disprove a claimed universal logical relationship.

---

## Satisfiability

A formula is **satisfiable** if at least one assignment makes it true.

A formula is **unsatisfiable** if no assignment makes it true.

A tautology is necessarily satisfiable because every assignment satisfies it.

A contradiction is unsatisfiable because no assignment satisfies it.

The programs implement exhaustive satisfiability analysis.

For:

`(p ∨ q) ∧ (¬p ∨ r)`

the program enumerates all assignments and returns those that satisfy the formula.

---

## Conjunctive normal form

A formula is in **conjunctive normal form**, or CNF, when it is an AND of clauses, with each clause being an OR of literals.

Example:

`(p ∨ q) ∧ (¬p ∨ r)`

A **literal** is either a variable or its negation.

Examples:

- `p`
- `¬p`
- `q`
- `¬q`

CNF is important in automated reasoning and satisfiability solving.

The Python implementation demonstrates canonical construction from truth-table information.

---

## Disjunctive normal form

A formula is in **disjunctive normal form**, or DNF, when it is an OR of terms, with each term being an AND of literals.

Example:

`(p ∧ q) ∨ (¬p ∧ r)`

Canonical DNF can be constructed by taking every truth-table row where the formula is true and creating one conjunction corresponding to that row.

The Python implementation contains functions for generating canonical DNF and CNF representations.

---

## Python implementation

The Python script begins with direct Boolean functions:

- `logical_not`
- `logical_and`
- `logical_or`
- `logical_xor`
- `implication`
- `biconditional`

These functions provide a transparent mapping between mathematical notation and executable Boolean operations.

The script then develops generic truth-table generation through:

`truth_table()`

This function receives a sequence of variable names and a callable expression. It evaluates the expression against every possible assignment.

The script builds on this mechanism to implement:

- tautology detection
- contradiction detection
- contingency detection
- logical equivalence
- argument validity
- counterexample search
- satisfiability

This design illustrates an important programming principle: a small general-purpose evaluator can support many higher-level logical analyses.

---

## Python expression trees

The Python implementation introduces an object-oriented formula representation.

The base class is:

`Formula`

Concrete classes include:

- `Variable`
- `Not`
- `And`
- `Or`
- `Implies`
- `Iff`

A formula such as:

`(p ∧ q) ∨ ¬r`

is represented as a tree:

- the root is `Or`
- the left child is `And`
- the `And` node contains `p` and `q`
- the right child is `Not`
- the `Not` node contains `r`

This representation separates the logical structure from a particular textual syntax.

It can therefore support future operations such as symbolic simplification, serialization, expression validation, or alternative evaluation strategies.

---

## Python validation

The function `require_boolean()` demonstrates strict validation.

This matters because Python permits many objects to participate in Boolean contexts.

For example, values such as integers, strings, lists, and dictionaries have truthiness rules.

Formal propositional logic, by contrast, normally expects a truth value.

A strict logical API should therefore decide whether it accepts arbitrary truthy and falsy objects or only actual Boolean values.

The example deliberately uses:

`type(value) is bool`

rather than relying only on truthiness.

---

## JavaScript implementation

The JavaScript implementation focuses on the relationship between formal Boolean logic and application-level JavaScript behavior.

It provides the same core logical operations but also demonstrates an important language-specific distinction.

In JavaScript:

`&&`

and:

`||`

are short-circuit operators that return operands rather than always returning Boolean values.

For example, an expression involving numbers may produce a number rather than `true` or `false`.

Therefore:

`Boolean(expression)`

can be used when an actual Boolean value is required.

The implementation explicitly validates inputs using `typeof value === "boolean"` for strict logical operations.

---

## JavaScript truth-table generation

JavaScript does not have a direct standard-library equivalent of Python's `itertools.product`, so the implementation constructs Boolean assignments recursively.

For `n` variables, the recursive generator creates every one of the `2^n` combinations.

The resulting assignments are objects such as:

`{ p: true, q: false }`

This demonstrates how a mathematical Cartesian-product concept can be implemented using recursive program structure.

---

## JavaScript higher-order functions

JavaScript functions are first-class values.

The implementation uses this property to represent logical rules as functions.

For example, an array of rules can be processed with:

`every()`

or:

`some()`

This produces reusable application-level constructs such as:

- all security rules must pass
- at least one alternative rule must pass

This corresponds closely to conjunction and disjunction when the rule functions themselves return Boolean values.

---

## JavaScript asynchronous evaluation

Real applications frequently obtain Boolean facts from asynchronous sources.

Examples include:

- authentication services
- databases
- policy services
- network APIs
- configuration systems

The JavaScript implementation uses `Promise.all()` and `async`/`await` to obtain several facts concurrently.

The important distinction is that asynchronous data acquisition is separate from logical evaluation.

Once the required facts have been obtained, the Boolean policy can be evaluated using ordinary propositional operations.

---

## C++ case study

The C++ implementation models a security policy engine.

The scenario contains access requests with Boolean properties:

- authentication status
- administrator status
- account status
- multi-factor authentication status
- trusted-network status

The basic policy is:

`authenticated ∧ administrator ∧ accountActive`

The stronger policy is:

`authenticated ∧ administrator ∧ accountActive ∧ multiFactorAuthenticated ∧ networkTrusted`

The purpose is not to model a complete production identity system. It demonstrates how formal logical conditions can become explicit software policy rules.

---

## C++ data structures

The C++ implementation uses:

`std::map<std::string, bool>`

for a logical assignment.

An assignment might conceptually contain:

`p = true`

`q = false`

The map makes variable names explicit and permits expression-tree nodes to retrieve values by name.

The implementation also uses:

`std::set<std::string>`

to collect the variables contained in an expression.

This allows an expression to determine its own variable set.

---

## C++ expression-tree design

The C++ expression hierarchy contains an abstract base class:

`Formula`

with operations for:

- evaluating a formula
- obtaining the variables contained in the formula

Concrete classes represent:

- variables
- negation
- conjunction
- disjunction
- implication
- biconditional

Polymorphism allows the evaluator to work with a common `Formula` interface.

`std::shared_ptr<const Formula>` is used as the expression pointer type.

The `const` qualification communicates that evaluation does not modify the expression tree.

The constructors validate required operands and reject null expression nodes.

---

## C++ policy abstraction

The policy engine defines an abstract:

`AccessPolicy`

interface.

Concrete policies implement:

`authorize()`

and:

`name()`

This separates the policy interface from individual policy definitions.

`BasicAdminPolicy` expresses the simpler conjunction.

`StrongAdminPolicy` adds additional Boolean requirements.

This design allows different logical policies to be selected through a common interface.

The case study demonstrates how formal logical expressions can become independently testable policy components rather than being scattered throughout application code.

---

## Transaction policy

The C++ case study also models a business rule:

`accountActive ∧ (amountWithinLimit ∨ managerApproved)`

This expresses a common logical structure:

- one mandatory condition
- at least one of two alternative conditions

The same structure occurs in many application domains.

For example, a process may require:

`identityVerified ∧ (biometricApproved ∨ hardwareTokenApproved)`

The exact policy depends on the application, but the underlying logical structure is the same.

---

## Edge cases

The implementations explicitly handle several edge cases.

### Missing variable values

An expression referring to a variable that is absent from its assignment should not silently invent a value.

The Python and C++ expression implementations raise errors for missing variables.

The JavaScript implementation does the same through explicit validation.

### Constant formulas

A formula with no variables has one possible empty assignment in the truth-table model.

The implementation demonstrates constant true and constant false formulas.

### Invalid Boolean inputs

Formal Boolean logic expects truth values. Application code may receive arbitrary values.

The implementations demonstrate strict validation to prevent accidental coercion.

### Empty truth tables

Although a conventional user-facing truth table generally contains named variables, a zero-variable formula is still a meaningful mathematical edge case.

---

## Common mistakes

### Treating questions as propositions

A question does not normally have a truth value merely because it is grammatically a sentence.

### Treating commands as propositions

An instruction is not ordinarily a proposition.

### Confusing inclusive OR and XOR

`p ∨ q` is true when both are true.

`p ⊕ q` is false when both are true.

### Reversing implication

`p → q` does not generally imply `q → p`.

### Confusing converse and contrapositive

The converse of:

`p → q`

is:

`q → p`

The contrapositive is:

`¬q → ¬p`

Only the contrapositive is guaranteed to be equivalent to the original implication.

### Assuming a true consequent proves the antecedent

From:

`p → q`

and:

`q`

one cannot generally conclude:

`p`.

This is the error demonstrated by affirming the consequent.

### Ignoring parentheses

A compound formula should be grouped explicitly when precedence could be misunderstood.

### Confusing programming truthiness with formal truth

Python, JavaScript, and C++ all have language-specific Boolean behavior.

Formal propositional logic is stricter: propositions have truth values rather than arbitrary truthy objects.

---

## Python, JavaScript, and C++ comparison

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Boolean type | `bool` | `boolean` | `bool` |
| Negation | `not` | `!` | `!` |
| AND | `and` | `&&` | `&&` |
| OR | `or` | `||` | `||` |
| XOR demonstration | `!=` | Boolean inequality | `!=` |
| Truth-table generation | `itertools.product` | recursive generation | bit-mask enumeration |
| Expression model | dataclasses/classes | class hierarchy | polymorphic class hierarchy |
| Main emphasis | formal experimentation | application behavior | structured system design |
| External packages | none | none | standard library only |

The mathematical semantics remain the same when actual Boolean values are used, but the programming languages have different operational behavior.

---

## Short-circuit evaluation

Formal logical notation describes truth conditions.

Programming languages also specify evaluation behavior.

For example, programming languages commonly use short-circuit evaluation.

For conjunction:

`False AND expression`

the second expression may not need to be evaluated because the complete result is already known to be false.

For disjunction:

`True OR expression`

the second expression may not need to be evaluated because the result is already known to be true.

This matters when the second operand:

- performs I/O
- modifies state
- performs an expensive computation
- may throw an exception
- calls another service

Therefore, logical equivalence at the Boolean level does not automatically imply identical operational behavior when expressions have side effects.

---

## Performance considerations

Truth-table enumeration has exponential complexity.

For `n` variables:

`2^n`

assignments must be considered.

The growth is:

| Variables | Assignments |
|---:|---:|
| 1 | 2 |
| 2 | 4 |
| 3 | 8 |
| 4 | 16 |
| 5 | 32 |
| 6 | 64 |
| 7 | 128 |
| 8 | 256 |
| 9 | 512 |
| 10 | 1,024 |
| 15 | 32,768 |

This exponential growth makes exhaustive enumeration practical only for relatively small formulas.

For larger propositional systems, specialized algorithms and representations are normally required.

The case-study implementations intentionally use exhaustive enumeration because it is transparent and directly demonstrates the semantics.

---

## Complexity of expression evaluation

If an expression tree contains `m` logical nodes, evaluating the tree generally requires work proportional to the number of nodes visited.

A single evaluation is therefore approximately:

`O(m)`

for a straightforward tree traversal.

If exhaustive truth-table evaluation is performed over `n` variables, there are `2^n` assignments, giving a basic total cost around:

`O(2^n × m)`

ignoring language-specific constants and optimizations.

This distinction is important:

- evaluating one known assignment can be relatively inexpensive
- evaluating every assignment can become exponentially expensive

---

## Security considerations

Logical expressions frequently appear in security policies.

Examples include:

`authenticated ∧ accountActive`

or:

`authenticated ∧ administrator ∧ MFA`

Logical mistakes in such conditions can have security consequences.

Important engineering practices include:

- validate policy inputs
- make policy conditions explicit
- test both allowed and denied cases
- test boundary conditions
- use counterexamples for invalid assumptions
- avoid accidental type coercion
- separate policy evaluation from data retrieval
- record policy versions where auditability is required
- avoid hidden side effects inside policy expressions
- review changes to authorization conditions carefully

The code in this repository demonstrates logical policy evaluation but does not constitute a complete identity, authentication, authorization, or security architecture.

---

## Implementation considerations

A logical system can be implemented at several abstraction levels.

A simple application can directly use Boolean expressions.

A reusable logic library can represent formulas as an abstract syntax tree.

A larger reasoning system can use symbolic representations and specialized algorithms.

The expression-tree approach used in the C++ implementation has an important advantage: the structure of a formula becomes explicit.

For example, these expressions have different structures:

`(p ∧ q) ∨ r`

and:

`p ∧ (q ∨ r)`

Although both contain the same variables and connectives, their tree structures differ.

Explicit expression trees make transformations and structural analysis possible without depending on the original source-code formatting.

---

## Testing strategy

Logical software benefits from exhaustive testing for small formulas.

The implementations use truth tables to test:

- tautologies
- contradictions
- equivalences
- implication transformations
- argument validity

This is stronger than testing only a few hand-selected examples.

For a formula with a small number of variables, every possible assignment can be checked.

The programs also use assertion-style verification for important laws.

This provides an executable demonstration that the implemented operations agree with the expected logical identities.

---

## Real-world applications

Propositional logic is a foundation for many computational systems.

### Access control

Rules such as:

`authenticated ∧ administrator`

are direct Boolean conditions.

### Database queries

Conditions in query predicates often combine Boolean expressions using AND, OR, and NOT.

### Software validation

Input validation frequently combines several conditions.

### Digital circuits

Boolean operations correspond closely to logical gates such as:

- NOT
- AND
- OR
- XOR

### Configuration systems

Feature flags and deployment conditions can be expressed as Boolean formulas.

### Rule engines

Business rules can be represented as combinations of propositions.

### Automated reasoning

SAT and related systems operate on propositional formulas.

### Policy systems

Security, compliance, and authorization policies often contain nested Boolean conditions.

---

## Important distinctions

### Proposition vs predicate

A proposition has a truth value under an interpretation.

A predicate is a function or relation whose truth may depend on its arguments.

For example:

`x > 5`

is commonly treated as a predicate or open sentence until `x` is specified.

### Implication vs causation

`p → q` does not mean that `p causes q`.

It specifies a truth-functional condition.

### Logical equivalence vs textual equality

Two formulas can look different while being logically equivalent.

For example:

`¬(p ∧ q)`

and:

`¬p ∨ ¬q`

have different syntax but identical truth tables.

### Boolean programming vs formal logic

Programming Boolean operators can have evaluation-order and type-coercion behavior that formal propositional logic does not have.

When building a logic engine, these differences must be considered explicitly.

---

## Limitations of the implementations

The examples implement classical two-valued propositional logic.

They do not attempt to model:

- many-valued logic
- fuzzy logic
- intuitionistic logic
- modal logic
- temporal logic
- first-order quantifiers
- probabilistic logic
- natural-language semantic ambiguity

The truth-table approach also does not scale efficiently to large numbers of independent variables because of exponential growth.

The policy case study is a logical demonstration rather than a complete enterprise security architecture.

---

## Structure of the repository

A typical arrangement is:

`logic_foundations.py`

`logic_foundations.js`

`logic_foundations.cpp`

`README.md`

The Python file provides the broadest mathematical exploration.

The JavaScript file focuses on language semantics and application-oriented evaluation.

The C++ file provides the most explicit system-oriented architecture through a policy engine and polymorphic expression representation.

---

## Running the Python implementation

The Python implementation uses only the standard library.

Run:

`python logic_foundations.py`

The script prints examples, truth tables, logical classifications, equivalence checks, counterexamples, satisfiability results, and application-level policy evaluations.

---

## Running the JavaScript implementation

The JavaScript implementation is compatible with a modern JavaScript runtime.

Run:

`node logic_foundations.js`

The program demonstrates Boolean operations, truth tables, logical equivalence, argument validity, expression trees, application rules, asynchronous evaluation, and automated tests.

---

## Compiling the C++ implementation

The C++ case study uses C++17 standard-library facilities.

Compile:

`g++ -std=c++17 -O2 logic_foundations.cpp -o logic_foundations`

Run:

`./logic_foundations`

On Windows, the resulting executable can be started using:

`logic_foundations.exe`

The program evaluates logical expressions, verifies laws, searches for counterexamples, analyzes satisfiability, and executes the access-control case study.

---

## Conceptual relationship among the three implementations

The three programs share the same mathematical foundation but emphasize different implementation concerns.

Python provides concise notation and makes exhaustive experimentation easy.

JavaScript demonstrates how Boolean logic interacts with dynamic language semantics, higher-order functions, and asynchronous application code.

C++ demonstrates how logical expressions can become components of a structured system. Its expression hierarchy separates syntax-like structure from evaluation, while its access-policy classes show how logical conditions can be encapsulated behind interfaces.

The central abstraction remains unchanged:

`propositions → logical connectives → compound formula → evaluation`

The implementation architecture changes according to the capabilities and idioms of each programming language.

---

## Core formulas demonstrated

The implementations directly demonstrate the following formulas:

`¬p`

`p ∧ q`

`p ∨ q`

`p ⊕ q`

`p → q`

`p ↔ q`

`(p ∧ q) ∨ ¬r`

`p → q ≡ ¬p ∨ q`

`p ↔ q ≡ (p → q) ∧ (q → p)`

`¬(p ∧ q) ≡ ¬p ∨ ¬q`

`¬(p ∨ q) ≡ ¬p ∧ ¬q`

`p ∨ ¬p`

`p ∧ ¬p`

`p → q ≡ ¬q → ¬p`

These formulas connect the mathematical definitions directly to executable implementations.

---

## Key implementation principles

The examples illustrate several general principles of logic-oriented software:

1. Represent truth values explicitly.
2. Keep compound rules readable.
3. Use parentheses to make grouping unambiguous.
4. Validate inputs when strict Boolean semantics are required.
5. Use exhaustive truth tables for small formulas.
6. Use counterexamples to disprove universal claims.
7. Separate data retrieval from logical evaluation.
8. Represent complex formulas structurally when symbolic processing is required.
9. Test logical identities rather than relying solely on sample cases.
10. Account for the exponential growth of exhaustive truth-table evaluation.

These principles apply from small Boolean utilities to larger rule and policy systems.
