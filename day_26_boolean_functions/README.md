# Boolean Functions: Truth Tables, Boolean Function Representation, Minterms, and Maxterms

## 1. Topic Introduction

A Boolean function is a mathematical function whose variables and output take values from the Boolean domain:

- `0` or `1`
- `false` or `true`

Boolean functions are fundamental to digital electronics, computer architecture, processor design, control systems, hardware description, switching theory, databases, software conditions, security policies, and discrete mathematics.

A Boolean function maps one or more Boolean inputs to exactly one Boolean output.

For `n` Boolean variables, there are `2^n` possible input combinations.

For example, three variables `A`, `B`, and `C` have:

`2^3 = 8`

possible input combinations.

Each complete truth table assigns either `0` or `1` to each of those eight combinations. Consequently, the number of distinct three-variable Boolean functions is:

`2^8 = 256`

The central subjects demonstrated in this repository are:

- Boolean variables
- Boolean operations
- Boolean functions
- Truth tables
- Binary row indexing
- Function representation
- Minterms
- Maxterms
- Canonical Sum of Products
- Canonical Product of Sums
- Functional equivalence
- Don't-care conditions
- Minterm adjacency
- Boolean simplification concepts
- Quine-McCluskey-style combination
- Practical Boolean decision systems
- Validation and exhaustive testing
- Complexity considerations

---

## 2. Fundamental Boolean Concepts

### 2.1 Boolean Variables

A Boolean variable has only two possible values.

A variable `A` may therefore be:

`A = 0`

or

`A = 1`

In programming, these values are commonly represented as `false` and `true`.

---

### 2.2 Boolean Constants

The two Boolean constants are:

- `0`, representing false
- `1`, representing true

A Boolean function can contain constants as well as variables.

Examples:

`F = A`

`F = 0`

`F = 1`

---

## 3. Basic Boolean Operations

The three fundamental Boolean operations are NOT, AND, and OR.

Other important operations include XOR and XNOR.

### 3.1 NOT

NOT reverses a Boolean value.

`NOT 0 = 1`

`NOT 1 = 0`

In Boolean algebra, complement is often written with an apostrophe:

`A'`

Therefore:

`A + A' = 1`

and

`A · A' = 0`

---

### 3.2 AND

AND produces `1` only when every input is `1`.

For two variables:

| A | B | A AND B |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Boolean notation:

`AB`

or

`A · B`

---

### 3.3 OR

OR produces `1` when at least one input is `1`.

| A | B | A OR B |
|---|---|--------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Boolean notation:

`A + B`

The plus symbol here means Boolean OR, not ordinary arithmetic addition.

---

### 3.4 XOR

Exclusive OR produces `1` when the inputs are different.

| A | B | A XOR B |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

XOR is commonly written:

`A ⊕ B`

XOR is important in parity circuits, adders, error detection, cryptography-related constructions, and bit manipulation.

---

### 3.5 XNOR

XNOR produces `1` when the inputs are equal.

| A | B | A XNOR B |
|---|---|----------|
| 0 | 0 | 1 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

XNOR is also called logical equivalence.

---

## 4. Boolean Functions

A Boolean function maps Boolean inputs to a Boolean output.

For example:

`F(A,B,C) = AB + AC + BC`

is a three-variable Boolean function.

This particular function is a majority function because it is `1` whenever at least two inputs are `1`.

Its truth table is:

| A | B | C | F |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 0 |
| 0 | 1 | 0 | 0 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 1 |
| 1 | 1 | 0 | 1 |
| 1 | 1 | 1 | 1 |

The Python, JavaScript, and C++ implementations all construct and evaluate this type of Boolean function programmatically.

---

## 5. Truth Tables

A truth table lists every possible combination of Boolean inputs and records the corresponding output.

For `n` variables:

`Number of rows = 2^n`

Examples:

| Variables | Rows |
|-----------|------|
| 1 | 2 |
| 2 | 4 |
| 3 | 8 |
| 4 | 16 |
| 5 | 32 |
| 10 | 1024 |

A truth table is an exhaustive representation of a Boolean function.

For a small number of variables, it is one of the most direct ways to verify a Boolean expression.

---

## 6. Truth-Table Row Indexing

Rows can be numbered using binary values.

For three variables:

| A | B | C | Decimal index |
|---|---|---|---------------|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 2 |
| 0 | 1 | 1 | 3 |
| 1 | 0 | 0 | 4 |
| 1 | 0 | 1 | 5 |
| 1 | 1 | 0 | 6 |
| 1 | 1 | 1 | 7 |

The input `101` is binary representation of decimal `5`.

Therefore the row `A=1, B=0, C=1` corresponds to index `5`.

This indexing system is essential for minterms and maxterms.

---

## 7. Minterms

A minterm is an AND/product term containing every variable exactly once.

Each variable appears either:

- uncomplemented, or
- complemented.

For three variables:

| Index | Binary | Minterm |
|------:|:------:|---------|
| 0 | 000 | `A'B'C'` |
| 1 | 001 | `A'B'C` |
| 2 | 010 | `A'BC'` |
| 3 | 011 | `A'BC` |
| 4 | 100 | `AB'C'` |
| 5 | 101 | `AB'C` |
| 6 | 110 | `ABC'` |
| 7 | 111 | `ABC` |

The defining property of a minterm is that it evaluates to `1` for exactly one input combination.

For example:

`m5 = AB'C`

is `1` only when:

`A=1, B=0, C=1`

All other input combinations make `m5` equal to `0`.

---

## 8. Constructing a Minterm

The binary representation determines whether a variable is complemented.

For `m5`:

`5 = 101₂`

Therefore:

- A = 1, so use `A`
- B = 0, so use `B'`
- C = 1, so use `C`

Therefore:

`m5 = AB'C`

This rule is implemented directly in all three programs.

---

## 9. Canonical Sum of Products

A Boolean function can be represented by the sum of all minterms for which the output is `1`.

This is called canonical Sum of Products, or canonical SOP.

Suppose:

`F=1`

for rows:

`1, 3, 5, 7`

Then:

`F = Σm(1,3,5,7)`

Expanded:

`F = A'B'C + A'BC + AB'C + ABC`

This expression is canonical because every product term contains every variable.

The Python and JavaScript implementations construct canonical SOP expressions directly from a truth table. The C++ implementation performs the same operation in the practical case study.

---

## 10. Why Minterms Work

Each minterm identifies one exact row.

If:

`F = Σm(1,3,5)`

then:

- row 1 contributes `1`
- row 3 contributes `1`
- row 5 contributes `1`
- every other row contributes `0`

The OR operation combines these individual cases.

Therefore:

`F = m1 + m3 + m5`

produces `1` whenever any one of those specified input combinations occurs.

---

## 11. Maxterms

A maxterm is an OR/sum term containing every variable exactly once.

Each maxterm evaluates to `0` for exactly one input combination.

For three variables:

| Index | Binary | Maxterm |
|------:|:------:|---------|
| 0 | 000 | `(A + B + C)` |
| 1 | 001 | `(A + B + C')` |
| 2 | 010 | `(A + B' + C)` |
| 3 | 011 | `(A + B' + C')` |
| 4 | 100 | `(A' + B + C)` |
| 5 | 101 | `(A' + B + C')` |
| 6 | 110 | `(A' + B' + C)` |
| 7 | 111 | `(A' + B' + C')` |

The polarity rule for maxterms is the opposite of the direct minterm construction.

For a maxterm, an input value of `0` produces the uncomplemented variable, while an input value of `1` produces the complemented variable.

---

## 12. Example of a Maxterm

Consider row `5`:

`101`

For `M5`:

- A = 1, so use `A'`
- B = 0, so use `B`
- C = 1, so use `C'`

Therefore:

`M5 = (A' + B + C')`

Evaluate it at `A=1, B=0, C=1`:

`M5 = (0 + 0 + 0) = 0`

For every other input combination, at least one term becomes `1`, so the maxterm evaluates to `1`.

---

## 13. Canonical Product of Sums

A Boolean function can also be represented using the rows where its output is `0`.

This produces canonical Product of Sums, or canonical POS.

Suppose:

`F=0`

at rows:

`0, 2, 4, 6`

Then:

`F = ΠM(0,2,4,6)`

Expanded:

`F = (A+B+C)(A+B'+C)(A'+B+C)(A'+B'+C)`

The AND operation combines the maxterms.

Because every listed maxterm is zero at one specific row, the complete product is zero at all specified zero rows.

---

## 14. Minterm and Maxterm Relationship

For a complete truth table without don't-care conditions:

- rows where `F=1` identify minterms
- rows where `F=0` identify maxterms

For `n` variables:

`Number of minterm indices + number of maxterm indices = 2^n`

For example, if a three-variable function has:

`F=1`

at rows:

`1,3,5,7`

then the minterms are:

`Σm(1,3,5,7)`

and the zero rows are:

`0,2,4,6`

so the maxterms are:

`ΠM(0,2,4,6)`

---

## 15. Minterm Versus Maxterm

| Property | Minterm | Maxterm |
|----------|---------|---------|
| Basic operation | AND | OR |
| Product/sum | Product term | Sum term |
| Contains every variable | Yes | Yes |
| Unique row behavior | Equals `1` at one row | Equals `0` at one row |
| Canonical form | SOP | POS |
| Index notation | `Σm` | `ΠM` |
| Derived from | Rows where output is `1` | Rows where output is `0` |

The most important distinction is:

**Minterm identifies a row where the function is 1.**

**Maxterm identifies a row where the function is 0.**

---

## 16. Boolean Function Representation

The same Boolean function can be represented in multiple equivalent ways.

Common representations include:

1. Boolean expression
2. Truth table
3. Logic-gate network
4. Canonical SOP
5. Canonical POS
6. Minterm index set
7. Maxterm index set
8. Binary output vector

For example:

`F = AB + AC + BC`

can be represented by its truth table and by:

`F = Σm(3,5,6,7)`

The zero rows are:

`0,1,2,4`

so an equivalent canonical POS representation is:

`F = ΠM(0,1,2,4)`

---

## 17. Boolean Algebra Laws

Several identities are fundamental when manipulating Boolean functions.

### Identity Laws

`A + 0 = A`

`A · 1 = A`

### Null Laws

`A + 1 = 1`

`A · 0 = 0`

### Idempotent Laws

`A + A = A`

`A · A = A`

### Complement Laws

`A + A' = 1`

`A · A' = 0`

### Double Complement

`(A')' = A`

### Commutative Laws

`A + B = B + A`

`AB = BA`

### Associative Laws

`A + (B + C) = (A + B) + C`

`A(BC) = (AB)C`

### Distributive Laws

`A(B+C) = AB + AC`

`A + BC = (A+B)(A+C)`

The second distributive identity differs from ordinary arithmetic intuition and is particularly important in Boolean algebra.

---

## 18. De Morgan's Laws

The two fundamental De Morgan identities are:

`(AB)' = A' + B'`

and

`(A+B)' = A'B'`

The implementations verify these identities exhaustively for every two-input combination.

These identities are important when converting between logic-gate structures and when transforming SOP and POS expressions.

---

## 19. Functional Equivalence

Two Boolean expressions are functionally equivalent when they produce the same output for every possible input combination.

For example:

`AB + AC + BC`

and

`A(B+C) + BC`

are equivalent.

Truth-table comparison is a direct way to prove equivalence for a finite number of Boolean variables.

The programs implement exhaustive equivalence checking.

For `n` variables, exhaustive comparison requires evaluating:

`2^n`

input combinations.

---

## 20. Don't-Care Conditions

A don't-care condition is an input combination for which the required output is not constrained.

It is commonly represented by:

`X`

A Boolean specification can therefore contain:

- ON-set: outputs required to be `1`
- OFF-set: outputs required to be `0`
- Don't-care set: either `0` or `1` is acceptable

For example:

`ON = {1,3,5}`

`OFF = {0,2,7}`

`DC = {4,6}`

The three implementations validate that these sets do not overlap.

Don't-care values can be used during minimization to obtain simpler logic.

A don't-care is not automatically equivalent to `1`. It means that either output is acceptable for the particular specification.

---

## 21. Minterm Adjacency

Two minterms are adjacent when their binary representations differ in exactly one position.

For example:

`m5 = 101`

and

`m7 = 111`

differ only in the middle bit.

Therefore they are adjacent.

The Hamming distance between the binary representations is `1`.

This concept is important for:

- Karnaugh maps
- Boolean minimization
- Quine-McCluskey procedures
- Logic optimization

The implementations calculate this adjacency explicitly.

---

## 22. Quine-McCluskey-Style Combination

The Quine-McCluskey method provides a systematic Boolean minimization procedure.

One central operation is combining terms that differ in exactly one variable.

For example:

`101`

and

`111`

can combine into:

`1-1`

The dash means that the corresponding variable is no longer required.

This is equivalent to algebraically eliminating the variable that changes between the two terms.

The provided implementations demonstrate the fundamental combination mechanism rather than presenting an incomplete symbolic minimizer.

A complete minimization algorithm must also handle:

- grouping
- repeated combination
- prime implicant identification
- essential prime implicant selection
- coverage analysis
- don't-care handling
- final expression construction

---

## 23. Python Implementation

The Python implementation is designed as a broad educational reference.

It demonstrates:

- Boolean operators
- Function definitions
- Higher-order function use
- Truth-table generation
- Binary row indexing
- Minterm construction
- Maxterm construction
- Canonical SOP
- Canonical POS
- Function equivalence
- Boolean specifications
- Don't-care conditions
- Hamming distance
- Minterm adjacency
- Implicant combination
- Exhaustive testing
- Edge-case validation

The `TruthTable` class stores:

- variable names
- input rows
- output values

The `generate_truth_table()` function automatically generates all `2^n` combinations.

The `binary_index()` function converts a binary input vector to the corresponding decimal row number.

For example:

`[1,0,1]`

becomes:

`5`

The `minterm_expression()` function converts the index into the corresponding canonical product term.

The `maxterm_expression()` function performs the corresponding maxterm construction.

---

## 24. Python Minterm Demonstration

The Python implementation constructs:

`m0` through `m7`

for three variables.

The resulting expressions are:

`m0 = A'B'C'`

`m1 = A'B'C`

`m2 = A'BC'`

`m3 = A'BC`

`m4 = AB'C'`

`m5 = AB'C`

`m6 = ABC'`

`m7 = ABC`

The same underlying algorithm works for a different number of variables.

---

## 25. Python Canonical Representation

The Python script first evaluates a function for every truth-table row.

It then divides the rows into:

- rows producing `1`
- rows producing `0`

The first group becomes the minterm index set.

The second group becomes the maxterm index set.

The canonical SOP and POS are then reconstructed from these index sets.

The implementation verifies that both canonical forms reproduce the original function.

This creates an important round-trip test:

`Function → Truth Table → Minterms/Maxterms → Canonical Form → Same Outputs`

---

## 26. JavaScript Implementation

The JavaScript implementation focuses on practical execution patterns and JavaScript-specific behavior.

It demonstrates:

- Boolean expressions
- Functions
- Classes
- Arrays
- Sets
- Promises
- Async functions
- Error handling
- Truth-table construction
- Canonical representations
- Don't-care specifications
- Minterm adjacency
- Implicant combination
- Exhaustive testing

The `TruthTable` class represents the same conceptual structure as the Python implementation, but uses JavaScript arrays and class methods.

The `Set` data structure is particularly useful for representing collections of minterm indices because membership testing is a central operation when evaluating canonical forms.

---

## 27. JavaScript Asynchronous Example

The JavaScript file includes an asynchronous policy-check example.

This demonstrates an important practical distinction.

Boolean logic itself is synchronous mathematics:

`S = DA + E`

But a software system implementing that policy may involve asynchronous operations such as:

- reading a device state
- receiving authorization information
- querying a service
- processing an event
- validating a request

The Boolean decision can therefore be embedded inside an asynchronous application without changing the underlying Boolean function.

The example uses a Promise and an `async` function without requiring an external package.

---

## 28. C++ Case Study

The C++ implementation models an activation controller.

The system has three Boolean inputs:

`D = door closed`

`A = authorization valid`

`E = emergency override`

The output is:

`S = DA + E`

This means:

- normal activation requires the door to be closed and authorization to be valid
- emergency override independently permits activation

The purpose of this case study is to demonstrate how a Boolean function can become part of a larger software-controlled decision system.

---

## 29. C++ Architecture

The C++ implementation separates responsibilities into several components.

### `binaryIndex()`

Converts Boolean input vectors into decimal row indices.

### `indexToBits()`

Performs the reverse conversion.

### `TruthTable`

Stores variables, input rows, and outputs.

### `mintermExpression()`

Builds symbolic minterms.

### `maxtermExpression()`

Builds symbolic maxterms.

### `extractCanonicalRepresentation()`

Separates the truth-table rows into minterms and maxterms.

### `canonicalSOP()`

Creates canonical Sum of Products.

### `canonicalPOS()`

Creates canonical Product of Sums.

### `BooleanSpecification`

Validates ON-set, OFF-set, and don't-care sets.

### `Implicant`

Represents a Quine-McCluskey-style pattern.

### `ActivationController`

Implements the practical control policy.

---

## 30. C++ Data Structures

The case study uses standard C++ library containers.

`std::vector`

is used for ordered Boolean input vectors, truth-table rows, and variable names.

`std::set`

is used for unique minterm sets, maxterm sets, and don't-care sets.

`std::string`

represents symbolic variable names and implicant patterns.

`std::function`

allows Boolean functions to be passed as callable objects.

These choices keep the case study self-contained and avoid external dependencies.

---

## 31. C++ Validation

The C++ implementation performs explicit validation.

Examples include:

- rejecting Boolean values other than `0` and `1`
- rejecting invalid minterm indices
- rejecting invalid maxterm indices
- rejecting invalid variable counts
- rejecting overlapping ON/OFF sets
- rejecting overlapping don't-care conditions
- checking canonical SOP equivalence
- checking canonical POS equivalence

Exceptions such as `std::invalid_argument`, `std::out_of_range`, and `std::runtime_error` are used for failure conditions.

---

## 32. Edge Cases

Important Boolean-function edge cases include constant functions.

### Constant Zero

A function that always returns `0` has no minterms.

Its canonical SOP is:

`0`

Every truth-table row is a zero row, so its canonical POS contains every maxterm.

### Constant One

A function that always returns `1` contains every minterm.

Its canonical SOP can be represented simply as:

`1`

It has no zero rows, so the canonical POS simplifies to:

`1`

These cases are explicitly tested by all implementations.

---

## 33. Common Mistakes

### Mistake 1: Confusing Minterms and Maxterms

A minterm is associated with a row where the function is `1`.

A maxterm is associated with a row where the function is `0`.

---

### Mistake 2: Reversing Complement Rules

For a minterm:

- input `1` → uncomplemented variable
- input `0` → complemented variable

For a maxterm:

- input `0` → uncomplemented variable
- input `1` → complemented variable

---

### Mistake 3: Treating `Σm` as a Maxterm Representation

`Σm(...)` denotes the indices of minterms used in canonical SOP.

`ΠM(...)` denotes the indices of maxterms used in canonical POS.

---

### Mistake 4: Forgetting All Variables

A canonical minterm must contain every variable exactly once.

A canonical maxterm must also contain every variable exactly once.

---

### Mistake 5: Treating Don't-Care as Always 1

A don't-care condition means either output is acceptable.

It may be treated as `0` or `1` during optimization when the specification permits it.

---

### Mistake 6: Assuming a Simplified Expression Is Automatically Canonical

A simplified Boolean expression may omit variables from individual terms.

That is normal for a minimized expression.

Canonical forms require every term to contain every variable.

---

### Mistake 7: Using Arithmetic Intuition

Boolean `+` represents OR.

Boolean multiplication represents AND.

Therefore Boolean algebra is not ordinary arithmetic.

---

## 34. Important Distinction: Canonical Versus Simplified Forms

Canonical forms are systematic representations.

For example:

`F = Σm(1,3,5,7)`

is canonical because every minterm explicitly identifies a complete input combination.

A simplified expression might be:

`F = C`

if those minterms happen to correspond exactly to the rows where `C=1`.

The simplified expression can be much shorter.

Canonical forms are useful for:

- systematic representation
- truth-table conversion
- algorithmic processing
- minimization algorithms
- theoretical analysis

Simplified forms are useful for:

- reducing hardware
- reducing logic operations
- improving readability
- reducing implementation cost
- optimizing circuits

---

## 35. Performance Considerations

Truth-table generation has exponential growth.

For `n` variables:

`Rows = 2^n`

This means exhaustive evaluation becomes increasingly expensive as the number of variables grows.

For example:

| Variables | Rows |
|----------:|-----:|
| 10 | 1,024 |
| 15 | 32,768 |
| 20 | 1,048,576 |
| 25 | 33,554,432 |
| 30 | 1,073,741,824 |

The number of possible Boolean functions grows even faster:

`2^(2^n)`

This is a double-exponential growth rate.

Therefore truth tables are excellent for small Boolean functions but become impractical for large numbers of variables.

---

## 36. Complexity of Exhaustive Equivalence Checking

To compare two Boolean functions by truth tables, every possible input combination must be evaluated.

The time complexity is approximately:

`O(2^n)`

where `n` is the number of variables.

This is practical for small functions.

For large systems, symbolic methods, algebraic simplification, Binary Decision Diagrams, SAT-based methods, or specialized hardware-design tools can be more appropriate.

---

## 37. Security Considerations

Boolean functions frequently appear in authorization and access-control logic.

For example:

`Access = Authenticated AND Authorized`

or:

`Allow = ValidCredential AND RequiredRole`

Such expressions are useful for modeling policy decisions.

A Boolean expression alone is not a complete security mechanism.

A production security system also requires appropriate:

- authentication
- authorization
- credential protection
- input validation
- trusted execution
- logging
- auditing
- failure handling
- protection against tampering
- protection of communication channels

The C++ activation-controller example therefore treats the Boolean expression as the policy decision component rather than the complete security architecture.

---

## 38. Implementation Considerations

A production Boolean-function implementation should consider:

### Input Validation

Invalid values should be rejected rather than silently interpreted.

### Deterministic Representation

Variable ordering must remain consistent.

For example:

`A,B,C`

must always map to the same bit positions when minterm indices are calculated.

### Edge Cases

Constant `0`, constant `1`, empty sets, complete sets, and don't-care conditions must be handled correctly.

### Testing

Truth-table-based exhaustive testing is particularly useful for small Boolean functions because every possible input can be checked.

### Maintainability

Boolean rules should be expressed using meaningful names when they represent business or system policies.

For example:

`doorClosed`

is more understandable in application code than an unexplained variable such as `x1`.

---

## 39. Real-World Applications

Boolean functions are used extensively in:

- digital logic circuits
- CPUs
- ALUs
- memory-control logic
- multiplexers
- decoders
- encoders
- state machines
- hardware controllers
- communication systems
- error detection
- parity generation
- authorization rules
- software condition evaluation
- embedded systems
- industrial control
- robotics
- automation
- network policy systems
- database filtering
- search conditions
- decision engines

The same mathematical principles apply whether the function is implemented using logic gates, software expressions, hardware description languages, or control-system rules.

---

## 40. Relationship Between Software and Digital Logic

A Boolean expression such as:

`F = AB + C`

can be interpreted mathematically, electronically, or programmatically.

In Boolean algebra:

`F = AB + C`

In Python-like syntax:

`F = (A and B) or C`

In JavaScript:

`const F = (A && B) || C;`

In C++:

`int F = (A && B) || C;`

The syntax differs, but the underlying truth function can be identical.

This is one reason Boolean algebra is important in both computer science and digital electronics.

---

## 41. Testing Strategy

For a small Boolean function, exhaustive testing is preferable to testing only a few representative cases.

For three variables there are only:

`2^3 = 8`

possible combinations.

Therefore every input can be tested.

The implementations use this approach to verify:

- Boolean identities
- truth-table construction
- canonical SOP
- canonical POS
- function equivalence
- edge cases

For larger functions, exhaustive testing may become impractical because of exponential growth.

---

## 42. Practical Interpretation of the C++ Case Study

The activation controller demonstrates a useful modeling process:

1. Identify real-world Boolean conditions.
2. Assign one Boolean variable to each condition.
3. Define the policy mathematically.
4. Generate the truth table.
5. Identify the ON-set.
6. Identify the OFF-set.
7. Convert the function to canonical SOP.
8. Convert it to canonical POS.
9. Verify equivalent representations.
10. Test edge cases.
11. Validate input conditions.
12. Consider implementation and security constraints.

For the case study:

`D = door closed`

`A = authorization valid`

`E = emergency override`

and:

`S = DA + E`

The mathematical function can then be analyzed independently of the programming language used to implement it.

---

## 43. Core Formulas

For `n` Boolean variables:

`Number of truth-table rows = 2^n`

`Number of possible Boolean functions = 2^(2^n)`

For canonical SOP:

`F = Σm(indices where F=1)`

For canonical POS:

`F = ΠM(indices where F=0)`

For a minterm:

`1` at exactly one input row.

For a maxterm:

`0` at exactly one input row.

For exhaustive equivalence checking:

`O(2^n)`

input combinations must be considered.

---

## 44. Implementation Coverage

The Python implementation emphasizes algorithmic construction and testing.

The JavaScript implementation emphasizes executable application-level behavior, classes, collections, and asynchronous integration.

The C++ implementation emphasizes a structured technical case study with strong type checking, standard-library data structures, exception handling, and a realistic control-policy architecture.

All three implementations independently demonstrate the same underlying Boolean principles so that the mathematical concepts can be compared across programming environments.
