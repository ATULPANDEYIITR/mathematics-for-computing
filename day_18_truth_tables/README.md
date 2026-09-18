# Truth tables, tautologies, contradictions, and contingencies

## Topic introduction

A truth table is a systematic representation of the truth values of a propositional formula for every possible assignment of truth values to its component propositions.

For a proposition such as `p`, there are two possible values:

- `True`
- `False`

With two independent propositions, `p` and `q`, there are `2² = 4` possible assignments. With three propositions there are `2³ = 8` assignments. In general, a truth table containing `n` independent propositions has `2ⁿ` rows.

Truth tables provide a precise method for evaluating propositional formulas. They can establish whether a formula is always true, always false, or dependent on the particular truth values assigned to its propositions.

The three central classifications in this topic are:

| Classification | Definition |
|---|---|
| Tautology | A formula that is true for every possible truth assignment |
| Contradiction | A formula that is false for every possible truth assignment |
| Contingency | A formula that is true for some assignments and false for others |

The three implementations in this repository approach the topic from different perspectives. Python develops a complete educational logic engine with parsing and structural formula evaluation. JavaScript emphasizes executable application-level logic and asynchronous processing. C++ develops an industry-style access-control case study in which truth tables are used to validate security policy equivalence.

---

## Fundamental concepts

### Proposition

A proposition is a declarative statement that has exactly one truth value under a given interpretation.

Examples include:

- `p`: "The server is available."
- `q`: "The user is authenticated."
- `r`: "The request originates from a trusted network."

A question, command, or expression without a definite truth value is not treated as a proposition in classical propositional logic.

### Boolean truth values

Classical propositional logic uses two truth values:

- `True`
- `False`

In Python these are represented by `True` and `False`.

In JavaScript they are represented by `true` and `false`.

In C++ they are represented by `true` and `false`.

Formal logic should distinguish these values from programming-language concepts such as integers, strings, null values, or truthy and falsy objects.

### Logical operator

A logical operator combines or transforms propositions.

The principal operators demonstrated by the implementations are:

| Logical notation | Meaning | Programming interpretation |
|---|---|---|
| `¬p` | NOT | Negation |
| `p ∧ q` | AND | Both must be true |
| `p ∨ q` | OR | At least one must be true |
| `p ⊕ q` | XOR | Exactly one is true |
| `p → q` | Implication | If `p`, then `q` |
| `p ↔ q` | Biconditional | `p` and `q` have the same truth value |

---

## Truth-table construction

The fundamental rule is:

`n` independent propositions produce `2ⁿ` rows.

For two propositions, `p` and `q`, the assignments are:

| p | q |
|---|---|
| False | False |
| False | True |
| True | False |
| True | True |

A formula column is then calculated from each row.

For example:

| p | q | p ∧ q |
|---|---|---|
| False | False | False |
| False | True | False |
| True | False | False |
| True | True | True |

The Python implementation generates assignments programmatically with `itertools.product`. The JavaScript implementation generates the same assignments using binary row indices. The C++ implementation generates assignments by enumerating integer bit patterns.

The different mechanisms produce the same mathematical result.

---

## NOT

Negation reverses the truth value.

| p | ¬p |
|---|---|
| False | True |
| True | False |

Python uses `not`.

JavaScript uses `!`.

C++ uses `!`.

The implementations deliberately use direct Boolean operations so that the connection between formal notation and executable behavior remains visible.

---

## AND

Conjunction `p ∧ q` is true only when both operands are true.

| p | q | p ∧ q |
|---|---|---|
| False | False | False |
| False | True | False |
| True | False | False |
| True | True | True |

AND is useful for representing conditions that must all be satisfied.

For example:

`valid_badge ∧ completed_training`

means access requires both a valid badge and completed training.

---

## OR

Disjunction `p ∨ q` is true when at least one operand is true.

| p | q | p ∨ q |
|---|---|---|
| False | False | False |
| False | True | True |
| True | False | True |
| True | True | True |

This is inclusive OR. When both inputs are true, the result remains true.

This differs from XOR.

---

## XOR

Exclusive OR is represented as `p ⊕ q`.

It is true when the operands have different truth values.

| p | q | p ⊕ q |
|---|---|---|
| False | False | False |
| False | True | True |
| True | False | True |
| True | True | False |

The Python and JavaScript implementations express XOR as inequality between Boolean values. The C++ implementation uses the same semantic rule.

XOR is useful when exactly one condition must be true.

---

## Material implication

Implication is represented as:

`p → q`

It is false only when `p` is true and `q` is false.

| p | q | p → q |
|---|---|---|
| False | False | True |
| False | True | True |
| True | False | False |
| True | True | True |

The important equivalence is:

`p → q ≡ ¬p ∨ q`

The implementations explicitly calculate implication using this definition.

This sometimes appears counterintuitive because an implication is true whenever the antecedent is false. Classical material implication does not mean that the antecedent causes the consequent. It is a truth-functional connective.

---

## Biconditional

The biconditional is:

`p ↔ q`

It is true when both propositions have the same truth value.

| p | q | p ↔ q |
|---|---|---|
| False | False | True |
| False | True | False |
| True | False | False |
| True | True | True |

It can be expressed as:

`(p → q) ∧ (q → p)`

It is also equivalent to:

`(p ∧ q) ∨ (¬p ∧ ¬q)`

---

## Operator precedence

When formulas contain multiple operators, grouping matters.

The implementations use the following precedence from strongest to weakest:

1. NOT
2. AND
3. XOR
4. OR
5. implication
6. biconditional

For example:

`p ∨ q ∧ r`

is interpreted as:

`p ∨ (q ∧ r)`

rather than:

`(p ∨ q) ∧ r`

Parentheses should be used whenever the intended grouping could be unclear.

---

## Tautologies

A tautology is true under every possible assignment.

A fundamental example is the law of excluded middle:

`p ∨ ¬p`

| p | ¬p | p ∨ ¬p |
|---|---|---|
| False | True | True |
| True | False | True |

There is no row producing `False`.

The implementations classify this formula as a tautology.

Other tautologies demonstrated include:

`¬(p ∧ ¬p)`

`¬(p ∧ q) ↔ (¬p ∨ ¬q)`

`¬(p ∨ q) ↔ (¬p ∧ ¬q)`

`(p → q) ↔ (¬p ∨ q)`

`(p → q) ↔ (¬q → ¬p)`

A truth-table test provides a direct verification because every possible assignment is examined.

---

## Contradictions

A contradiction is false under every possible assignment.

The standard example is:

`p ∧ ¬p`

| p | ¬p | p ∧ ¬p |
|---|---|---|
| False | True | False |
| True | False | False |

There is no assignment under which a proposition and its negation are simultaneously true in classical Boolean logic.

A contradiction is sometimes called an unsatisfiable formula because no satisfying assignment exists.

---

## Contingencies

A contingency is neither a tautology nor a contradiction.

For example:

`p ∧ q`

has the table:

| p | q | p ∧ q |
|---|---|---|
| False | False | False |
| False | True | False |
| True | False | False |
| True | True | True |

It is true on one row and false on three rows.

Therefore it is a contingency.

Many practical business, security, engineering, and software rules are contingencies because their results depend on input conditions.

---

## Python implementation

The Python program develops the most complete general-purpose educational implementation.

### Basic operations

The functions `logical_not`, `logical_and`, `logical_or`, `logical_xor`, `logical_implies`, and `logical_iff` directly implement the fundamental connectives.

The implementation of implication is:

`(not antecedent) or consequent`

This explicitly reflects the logical identity:

`p → q ≡ ¬p ∨ q`

### Assignment generation

The function `generate_assignments` produces every possible combination of Boolean values.

For `n` variables it generates `2ⁿ` dictionaries.

For example, two variables generate:

`{"p": False, "q": False}`

`{"p": False, "q": True}`

`{"p": True, "q": False}`

`{"p": True, "q": True}`

This provides the foundation for exhaustive truth-table evaluation.

### Formula classification

The Python function `classify_truth_values` checks the complete result column.

If every value is true, it returns `tautology`.

If every value is false, it returns `contradiction`.

Otherwise it returns `contingency`.

This is mathematically equivalent to checking:

`∀ assignment, formula = True`

for a tautology and:

`∀ assignment, formula = False`

for a contradiction.

### Formula objects

The `Formula` hierarchy represents logical expressions structurally.

The major classes are:

- `Formula`
- `Variable`
- `Not`
- `BinaryFormula`

Convenience constructors provide:

- `And`
- `Or`
- `Xor`
- `Implies`
- `Iff`

This is more flexible than writing every expression as a Python lambda because a formula can expose its variables, evaluate itself, and produce a textual representation.

### Formula trees

A formula such as:

`p ∧ (q ∨ ¬r)`

is represented as a tree.

The root is an AND operation. Its left child is `p`. Its right child is an OR operation. The OR operation has `q` and `¬r` as children.

This representation is an abstract syntax tree in a simple form.

Structural representations are important because real logic engines, compilers, rule engines, query optimizers, and symbolic reasoning systems generally operate on structured expressions rather than unstructured text.

---

## Python parser

The Python implementation contains a complete parser for a practical textual notation.

Supported operators include:

- `!` or `~` for NOT
- `&` for AND
- `|` for OR
- `^` for XOR
- `->` for implication
- `<->` for biconditional
- parentheses for grouping

Examples include:

`p | ~p`

`p & (q | ~r)`

`(p -> q) <-> (~p | q)`

The parser separates tokenization from grammatical parsing.

The implication operator is treated as right-associative:

`p -> q -> r`

is interpreted as:

`p -> (q -> r)`

This is an important implementation detail because changing associativity changes the resulting formula tree.

The parser also rejects malformed expressions such as incomplete operators, unmatched parentheses, unsupported symbols, and empty formulas.

---

## Logical equivalence

Two formulas are logically equivalent when they produce the same truth value for every possible assignment to their variables.

The notation is:

`P ≡ Q`

The Python and JavaScript implementations test equivalence by evaluating both formulas over the union of their variables.

For example:

`p → q`

and:

`¬p ∨ q`

are equivalent.

A counterexample is an assignment where two formulas produce different values. If a counterexample exists, the formulas are not logically equivalent.

This provides a constructive way of disproving equivalence.

---

## Important logical laws

The implementations verify several classical laws.

### Law of excluded middle

`p ∨ ¬p`

This is a tautology in classical propositional logic.

### Law of contradiction

`¬(p ∧ ¬p)`

This is also a tautology.

### Double negation

`¬¬p ≡ p`

### De Morgan's laws

`¬(p ∧ q) ≡ ¬p ∨ ¬q`

and:

`¬(p ∨ q) ≡ ¬p ∧ ¬q`

### Implication replacement

`p → q ≡ ¬p ∨ q`

### Contrapositive

`p → q ≡ ¬q → ¬p`

### Commutativity

`p ∧ q ≡ q ∧ p`

`p ∨ q ≡ q ∨ p`

### Associativity

`(p ∧ q) ∧ r ≡ p ∧ (q ∧ r)`

### Distributivity

`p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)`

Truth tables provide a direct method for verifying each identity.

---

## Satisfiability

A formula is satisfiable if at least one assignment makes it true.

Examples:

`p ∧ q`

is satisfiable because `p=True` and `q=True` satisfies it.

`p ∨ ¬p`

is satisfiable because every assignment satisfies it.

`p ∧ ¬p`

is not satisfiable because no assignment makes it true.

Therefore:

- every tautology is satisfiable;
- every contradiction is unsatisfiable;
- every contingency is satisfiable but not valid.

---

## Counterexamples

A counterexample is a particular assignment that disproves a universal claim.

Suppose someone claims:

`p ∧ q ≡ p`

The assignment:

`p=True, q=False`

produces:

`p ∧ q = False`

while:

`p = True`

Therefore the claim is false.

The Python and JavaScript implementations provide explicit counterexample searches. The C++ implementation uses the same principle when comparing security policies.

A counterexample is often more useful than merely returning "false" because it identifies the precise conditions under which two rules differ.

---

## Argument validity

A logical argument has premises and a conclusion.

For example:

`p → q`

`p`

Therefore:

`q`

This is the classical rule of modus ponens.

An argument is valid when there is no possible assignment where all premises are true and the conclusion is false.

The implementations test exactly this condition.

To find an invalid argument, search for:

`premises all true ∧ conclusion false`

If such an assignment exists, it is a counterexample to the argument.

This connects truth tables to formal reasoning.

---

## Canonical disjunctive normal form

A canonical disjunctive normal form, or canonical DNF, can be constructed from the true rows of a truth table.

For every true row:

1. Create a conjunction containing every variable.
2. Use the variable itself when its row value is true.
3. Use its negation when its row value is false.
4. OR all such conjunctions together.

For example, if a formula is true only for:

`p=True, q=False`

its canonical DNF contains:

`p ∧ ¬q`

Canonical DNF is sometimes called a sum-of-products representation.

The Python, JavaScript, and C++ implementations demonstrate generation of canonical DNF.

---

## Canonical conjunctive normal form

Canonical CNF is constructed from false rows.

For every false row:

1. Create a disjunction containing every variable.
2. Use the negated variable when its row value is true.
3. Use the variable itself when its row value is false.
4. AND all clauses together.

Canonical CNF is sometimes called a product-of-sums representation.

The DNF and CNF generated from a truth table are logically equivalent to the original formula.

---

## JavaScript implementation

The JavaScript program provides a second executable implementation with a stronger emphasis on application-level behavior.

### Assignment generation

JavaScript generates truth assignments using integer row indices.

For `n` variables, the row index is interpreted as an `n`-bit binary number.

For two variables, the four binary combinations correspond to:

`00`

`01`

`10`

`11`

Each bit becomes one proposition's truth value.

This method is compact and demonstrates the relationship between binary representation and truth-table construction.

### Object-oriented formulas

JavaScript defines:

- `Formula`
- `Variable`
- `Not`
- `BinaryFormula`

The implementation uses inheritance and method overriding.

Each formula knows how to:

- evaluate itself;
- identify its variables;
- represent itself as text.

This demonstrates how propositional expressions can be modeled as application objects.

### JavaScript Boolean behavior

JavaScript has truthy and falsy values, so formal logic code should be careful.

For example:

`Boolean(1)` is `true`.

`Boolean(0)` is `false`.

But a formal truth-table engine should normally store actual Boolean values rather than depend on implicit coercion.

The implementation uses strict Boolean semantics and `===` where equality is required.

---

## JavaScript bit vectors

The `TruthVector` class represents an entire truth-table result column as a bit pattern.

For a four-row table, a vector such as:

`0101`

can encode the result for all four assignments.

Logical operations can then be mapped to bitwise operations:

- AND → `&`
- OR → `|`
- XOR → `^`
- NOT → complemented bits restricted to the table mask

This demonstrates an important implementation optimization: multiple Boolean results can be processed as bits rather than individual Boolean objects.

JavaScript's ordinary bitwise operators operate on 32-bit signed integers, so the example intentionally limits the Number-based vector implementation. The program also demonstrates `BigInt` for larger integer bit patterns.

---

## JavaScript asynchronous evaluation

The JavaScript implementation includes an asynchronous truth-table evaluator using `Promise.all`.

The example does not need a network connection. Its purpose is architectural.

In an application, a formula evaluator might depend on:

- a policy service;
- a database;
- a remote rule engine;
- a permission service;
- an external configuration source.

An asynchronous design can evaluate independent rows concurrently when such external dependencies exist.

For purely local Boolean operations, asynchronous execution normally adds overhead rather than improving performance. The synchronous approach is preferable when computation is inexpensive and self-contained.

---

## C++ case study

The C++ implementation develops a realistic security access-control scenario.

Four Boolean variables represent:

- `A`: valid badge
- `B`: completed security training
- `C`: approved network
- `D`: allowed operating period

The original policy is:

`(A ∧ B ∧ C) ∨ (A ∧ B ∧ D)`

The same policy can be factored:

`A ∧ B ∧ (C ∨ D)`

A truth table can verify that the two expressions produce exactly the same result for every possible combination of the four conditions.

This is a useful application of truth tables because the question is not merely whether a formula looks algebraically similar. The complete truth table establishes semantic equivalence over the defined Boolean inputs.

---

## C++ system design

The case study separates the problem into components.

### Formula abstraction

The abstract `Formula` class provides:

- `evaluate`
- `variables`
- `name`

Derived classes implement:

- variables;
- negation;
- binary logical operators.

This creates a small expression-tree framework.

### Assignment generation

`generateAssignments` creates every possible combination of the variables.

For four variables, it produces:

`2⁴ = 16`

rows.

The implementation uses bit positions in an integer to generate these assignments efficiently.

### Classification

`classifyFormula` evaluates every row and tracks whether at least one true and at least one false result has appeared.

It can stop early once both have been found because the formula is then known to be a contingency.

This is a small optimization compared with always evaluating the entire classification state.

### Equivalence testing

`logicallyEquivalent` searches for counterexamples.

If no counterexample exists, the formulas are equivalent over their complete shared variable domain.

### Argument validation

`argumentIsValid` searches for an assignment in which every premise is true while the conclusion is false.

Finding such an assignment immediately proves invalidity.

---

## Access-control policy

The case study models a rule such as:

A user may access a protected system if:

- the user has a valid badge;
- the user has completed security training;
- and either the network is approved or the access occurs during an allowed period.

The corresponding factored policy is:

`A ∧ B ∧ (C ∨ D)`

The program also contains an intentionally different policy:

`A ∧ B ∧ C ∧ D`

The truth-table comparison identifies an input combination where the two policies disagree.

This demonstrates why logical equivalence matters in software engineering. Two policy implementations that appear related may have materially different behavior for particular input combinations.

---

## Why counterexamples matter in policy systems

Suppose a policy is changed during a refactoring operation.

Original:

`(A ∧ B ∧ C) ∨ (A ∧ B ∧ D)`

Refactored:

`A ∧ B ∧ C ∧ D`

The second expression is stricter. It rejects cases where `C` is false but `D` is true.

A truth-table comparison reveals exactly those cases.

This technique can be used in:

- authorization engines;
- firewall rule validation;
- configuration management;
- feature flags;
- eligibility systems;
- workflow rules;
- compliance systems;
- access-control systems;
- business-rule engines.

The Boolean model does not by itself establish whether a policy is appropriate. It establishes whether the implemented logical expressions are equivalent under the modeled conditions.

---

## Edge cases

### Zero variables

A general truth-table generator may encounter a formula containing no variables.

The number of assignments is:

`2⁰ = 1`

This corresponds to the single empty assignment in an exhaustive Boolean model.

### Single variable

A one-variable formula has two rows.

This is sufficient to distinguish many basic tautologies and contradictions.

### Missing assignments

The Python, JavaScript, and C++ formula implementations validate that a variable required by a formula has an associated truth value.

A missing variable is an evaluation error rather than a logical `False` value.

### Invalid expressions

The Python parser rejects:

- empty expressions;
- incomplete operators;
- missing closing parentheses;
- unsupported characters;
- malformed formulas.

This is preferable to silently assigning an arbitrary meaning.

### Operator precedence

Expressions without explicit parentheses can be misinterpreted if different systems use different precedence rules.

The Python parser defines a specific precedence hierarchy. Production systems should document their grammar precisely.

### Large variable counts

Exhaustive truth tables grow exponentially.

For:

`n = 10`

there are:

`1,024`

rows.

For:

`n = 20`

there are:

`1,048,576`

rows.

For:

`n = 30`

there are:

`1,073,741,824`

rows.

For larger values, exhaustive enumeration becomes impractical.

---

## Complexity considerations

Let:

- `n` = number of independent variables;
- `m` = amount of work required to evaluate one formula.

A naive exhaustive truth-table evaluation requires approximately:

`O(2ⁿ × m)`

time.

If every row is retained, memory can approach:

`O(2ⁿ × n)`

for explicit assignments.

A streaming evaluator can reduce assignment-storage requirements because rows can be processed one at a time.

Formula simplification can reduce `m`.

Bit-vector techniques can process multiple truth-table rows simultaneously, reducing practical execution cost for small or moderate formulas.

The fundamental exponential growth in the number of possible assignments remains.

---

## Bit-vector representation

Truth tables have a useful connection to binary data.

Suppose a formula has four rows and its results are:

`False, True, True, False`

These can be represented as:

`0110`

Logical operations on result vectors correspond to Boolean operations across every row.

This can make equivalence testing extremely compact.

For small truth tables, a complete Boolean function can even be represented as an integer bit mask.

This technique is useful for:

- Boolean function analysis;
- logic minimization;
- hardware simulation;
- lookup-table implementations;
- exhaustive small-state verification;
- educational logic engines.

The JavaScript implementation demonstrates this directly, while the C++ implementation emphasizes explicit row-based evaluation for readability and system modeling.

---

## Logical equivalence versus syntactic equality

Two formulas can look different while representing the same Boolean function.

For example:

`p → q`

and:

`¬p ∨ q`

are syntactically different but logically equivalent.

Truth-table equivalence compares behavior rather than textual appearance.

This distinction is fundamental in:

- compiler optimization;
- query optimization;
- symbolic logic;
- circuit simplification;
- rule-engine optimization;
- formal verification.

A transformation is safe only when it preserves the relevant semantics.

---

## Tautology versus validity

A tautology is a property of a formula.

An argument is valid when no interpretation makes all premises true and the conclusion false.

These concepts are related but not identical.

For example:

`p ∨ ¬p`

is a tautology.

For an argument, validity concerns the relationship between multiple formulas.

An argument with premises `P₁, P₂, ..., Pₙ` and conclusion `C` is valid when:

`(P₁ ∧ P₂ ∧ ... ∧ Pₙ) → C`

is a tautology.

The implementations use direct counterexample search rather than requiring the user to manually construct this combined formula.

---

## Tautology versus satisfiability

A tautology is true under every assignment.

A satisfiable formula is true under at least one assignment.

Therefore:

`tautology ⟹ satisfiable`

but:

`satisfiable ⇏ tautology`

A contingency is satisfiable but not a tautology.

A contradiction is unsatisfiable.

These relationships can be expressed as:

| Formula type | At least one true row | At least one false row |
|---|---:|---:|
| Tautology | Yes | No |
| Contradiction | No | Yes |
| Contingency | Yes | Yes |

---

## Common mistakes

### Confusing implication with conjunction

`p → q`

is not the same as:

`p ∧ q`

Implication is false only for `p=True, q=False`.

Conjunction is true only for `p=True, q=True`.

### Treating implication as causation

The truth-functional connective `→` does not express physical causation.

It defines a Boolean relationship.

### Confusing OR and XOR

Inclusive OR allows both operands to be true.

XOR requires different truth values.

### Forgetting parentheses

`p ∨ q ∧ r`

is not generally equivalent to:

`(p ∨ q) ∧ r`

### Assuming different syntax means different logic

`p → q` and `¬p ∨ q` look different but are logically equivalent.

### Testing only selected rows

Checking a few rows is not enough to prove a formula is a tautology.

A universal claim requires all possible assignments unless a separate mathematical proof establishes the result.

### Ignoring variable count

Truth-table size grows as `2ⁿ`, not `n²` or `n`.

### Confusing a false formula with an invalid program

A formula can legitimately evaluate to false for a particular assignment.

A programming error occurs when the implementation does not correctly represent the intended formula.

---

## Limitations

Truth tables are exact and intuitive for small propositional systems, but exhaustive enumeration does not scale well.

The central limitation is exponential growth.

A formula involving 5 variables has:

`32`

rows.

A formula involving 15 variables has:

`32,768`

rows.

A formula involving 25 variables has:

`33,554,432`

rows.

A formula involving 40 variables has:

`1,099,511,627,776`

rows.

At such sizes, practical systems require more advanced techniques such as symbolic representations, SAT solving, binary decision diagrams, constraint propagation, or algebraic simplification.

These techniques are outside the core implementation, but the truth-table programs establish the semantic foundation against which such methods can be understood.

---

## Performance considerations

For small formulas, direct exhaustive evaluation is usually preferable because it is simple, deterministic, and easy to verify.

Useful optimizations include:

- streaming assignments rather than storing all rows;
- short-circuit Boolean evaluation;
- simplifying formulas before enumeration;
- caching repeated subexpressions;
- representing truth columns as bit vectors;
- stopping classification early when both true and false values have been observed;
- stopping equivalence testing immediately after a counterexample is found.

The Python implementation demonstrates early classification termination and bit-vector evaluation.

The JavaScript implementation demonstrates bit masks and asynchronous evaluation.

The C++ implementation demonstrates efficient row generation and early counterexample detection.

---

## Security considerations

Truth tables can help validate Boolean security policies, but they do not by themselves provide complete security.

A real access-control system also requires consideration of:

- identity verification;
- authentication;
- authorization;
- credential storage;
- session management;
- privilege boundaries;
- audit logging;
- input validation;
- secure defaults;
- policy versioning;
- configuration integrity;
- race conditions;
- availability;
- operational monitoring.

A truth table can establish that two Boolean policies are equivalent for the modeled variables. It cannot establish that the variables themselves were obtained securely or that the overall system is secure.

The C++ case study therefore treats truth-table analysis as one component of policy verification rather than as a complete security mechanism.

---

## Implementation considerations

### Python

Python is well suited to educational logic engines because:

- Boolean syntax is concise;
- dictionaries make assignments easy to inspect;
- `itertools.product` directly expresses Cartesian-product enumeration;
- classes can represent formula trees with relatively little code;
- exceptions make parser errors straightforward to handle.

The Python implementation is particularly useful for exploring the mathematical structure of formulas.

### JavaScript

JavaScript is useful when Boolean logic is part of:

- web applications;
- browser interfaces;
- client-side validation;
- interactive rule editors;
- event-driven applications;
- asynchronous services.

The implementation also demonstrates JavaScript-specific concerns involving truthiness, strict equality, bitwise operations, and asynchronous execution.

### C++

C++ is useful when logical evaluation is integrated into:

- systems software;
- embedded applications;
- high-performance rule engines;
- security infrastructure;
- simulation;
- performance-sensitive applications.

The C++ case study uses classes, polymorphism, standard containers, explicit error handling, and integer-based assignment enumeration.

---

## Python, JavaScript, and C++ comparison

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Primary role | Logic engine and parser | Application-oriented Boolean engine | Industry-style policy case study |
| Formula representation | Classes and dataclasses | Classes and inheritance | Polymorphic class hierarchy |
| Assignment generation | `itertools.product` | Binary row indices | Integer bit patterns |
| Parsing | Complete parser | Programmatic formula construction | Programmatic formula construction |
| Error handling | Exceptions | Exceptions and rejected promises | Exceptions |
| Bit-vector example | Truth-vector class | Truth-vector class with Number | Integer-based enumeration |
| Asynchronous behavior | Not central | Promise-based demonstration | Not required |
| Security scenario | General logic | General application logic | Access-control policy |
| Normal forms | DNF and CNF | DNF and CNF | DNF and CNF |
| Argument validity | Yes | Yes | Yes |

The implementations are intentionally not identical copies. Each language highlights mechanisms that are natural in its own programming environment.

---

## Advanced conceptual relationships

### Boolean functions

A propositional formula defines a Boolean function.

For `n` variables, the function has:

`2ⁿ`

possible input combinations.

Each formula therefore corresponds to a truth vector containing one output value for each input combination.

Different formulas can represent the same Boolean function. This is exactly what logical equivalence captures.

### Functional completeness

Some collections of logical operators are sufficient to express every Boolean function.

For example, the operators AND, OR, and NOT form a functionally complete set.

Since:

`p → q ≡ ¬p ∨ q`

implication can also be expressed through NOT and OR.

Similarly, many other operator systems can express the same Boolean functions.

### Normal forms

Every Boolean function can be represented by a canonical DNF and a canonical CNF.

The truth table provides a direct construction method:

- true rows determine DNF terms;
- false rows determine CNF clauses.

This establishes a connection between truth-table reasoning and symbolic Boolean representation.

### Formal verification

A formula equivalence check can be interpreted as a small exhaustive verification problem.

For two formulas `P` and `Q`, the goal is to establish:

`∀ assignments, P = Q`

A single counterexample disproves the property.

The same general pattern appears in software verification:

`∀ valid inputs, implementation_A(input) = implementation_B(input)`

For small finite domains, exhaustive enumeration can provide complete verification.

---

## Real-world relevance

Truth tables provide a foundation for reasoning about systems where decisions can be reduced to Boolean conditions.

Applications include:

- digital logic;
- CPU control logic;
- authorization rules;
- firewall policies;
- business rules;
- access-control systems;
- configuration validation;
- feature flags;
- eligibility rules;
- workflow conditions;
- automated testing;
- formal verification;
- software specification;
- rule engines;
- Boolean circuit analysis.

The access-control example illustrates how a seemingly simple Boolean expression can represent a real policy whose behavior must remain consistent during refactoring.

Truth-table construction is especially valuable when requirements contain phrases such as:

- "if and only if";
- "unless";
- "either";
- "both";
- "at least one";
- "exactly one";
- "only if";
- "if";
- "provided that".

These natural-language conditions can easily be translated incorrectly. Writing the corresponding Boolean expression and testing its complete truth table makes the resulting behavior explicit.

---

## Relationship between "if" and "only if"

Natural-language requirements frequently cause logical errors.

"If `p`, then `q`" normally corresponds to:

`p → q`

"p only if q" also corresponds to:

`p → q`

"p if q" corresponds to:

`q → p`

"If and only if" corresponds to:

`p ↔ q`

The direction of implication matters.

For example:

"Access is granted only if the user is authenticated"

means:

`AccessGranted → Authenticated`

It does not necessarily mean:

`Authenticated → AccessGranted`

An authenticated user may still be denied for another reason.

Truth tables are useful for making these distinctions explicit.

---

## Production considerations

A production rule engine should normally separate:

- policy definition;
- policy parsing;
- policy validation;
- policy evaluation;
- logging;
- configuration;
- testing;
- deployment;
- version management.

Truth-table generation is most appropriate for policies with a manageable number of independent Boolean variables.

For larger policies, exhaustive enumeration may be replaced or supplemented by symbolic techniques and automated satisfiability procedures.

Regardless of the implementation strategy, the semantic model remains important: a policy should have a precise definition of what inputs it accepts and what result it produces.

The C++ case study demonstrates this principle by defining explicit variables and comparing policy implementations over the complete finite input space.

---

## Key distinctions

| Concept | Meaning |
|---|---|
| Proposition | A statement with a truth value |
| Formula | A structured combination of propositions and operators |
| Truth table | All possible input assignments and resulting outputs |
| Tautology | True for every assignment |
| Contradiction | False for every assignment |
| Contingency | True for some assignments and false for others |
| Satisfiable | True for at least one assignment |
| Unsatisfiable | True for no assignment |
| Logical equivalence | Same result for every assignment |
| Counterexample | Assignment that disproves a universal claim |
| Valid argument | No assignment has all premises true and conclusion false |
| DNF | OR of conjunction terms |
| CNF | AND of disjunction clauses |

---

## Files

The repository contains three executable implementations:

- Python: complete propositional-logic engine, parser, formula tree, truth-table generator, classification, equivalence testing, normal forms, satisfiability, argument validity, and bit-vector representation.
- JavaScript: application-oriented Boolean engine, object-oriented formulas, truth-table generation, normal forms, asynchronous evaluation, JavaScript-specific Boolean behavior, and bit-mask processing.
- C++: complete access-control policy case study with formula objects, truth-table generation, policy equivalence testing, counterexample detection, argument validity, normal forms, and complexity analysis.

The three implementations collectively demonstrate that truth tables are not merely a classroom notation. They are a precise computational representation of finite Boolean behavior and can be used to test logical rules, validate transformations, identify contradictions, and expose counterexamples.
