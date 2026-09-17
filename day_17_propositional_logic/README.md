# Propositional Logic: AND, OR, NOT, Implication, Biconditional, and Precedence

## Introduction

Propositional logic is a formal system for representing and reasoning about statements that have one of two truth values: true or false.

A proposition is a declarative statement that can be assigned a definite truth value. For example, `5 > 2` is true, while `10 < 3` is false.

The central connectives examined in this project are:

- AND, written as `P ∧ Q`
- OR, written as `P ∨ Q`
- NOT, written as `¬P`
- implication, written as `P → Q`
- biconditional, written as `P ↔ Q`
- precedence rules that determine how compound expressions are interpreted

The three implementations approach the same subject from different perspectives:

- The Python implementation develops the concepts progressively and includes reusable truth-table, satisfiability, equivalence, parsing, and reasoning utilities.
- The JavaScript implementation emphasizes executable Boolean logic, symbolic expressions, recursive-descent parsing, validation, and application-level policy evaluation.
- The C++ implementation develops a structured expression engine and applies it to an enterprise authorization case study with explicit data structures, polymorphism, validation, testing, and complexity analysis.

---

## Fundamental terminology

### Proposition

A proposition is a declarative statement that is either true or false.

Examples:

- `P: 7 > 3`
- `Q: 12 is an even number`
- `R: 15 < 4`

A proposition cannot simultaneously be both true and false within the same interpretation.

Questions and commands are normally not propositions. For example, "What time is it?" does not have a truth value by itself.

### Atomic proposition

An atomic proposition is a proposition that is treated as a single logical unit.

If:

- `P = "The server is online"`
- `Q = "The database is available"`

then `P` and `Q` are atomic propositions.

### Compound proposition

A compound proposition is formed by combining propositions using logical connectives.

For example:

`P ∧ Q`

is a compound proposition formed from `P` and `Q`.

### Truth value

A proposition has one of two classical truth values:

- `True`
- `False`

The implementations represent these values using Boolean types.

---

## The AND connective

AND is called conjunction.

It is written:

`P ∧ Q`

The expression is true only when both `P` and `Q` are true.

| P | Q | P ∧ Q |
|---|---|-------|
| False | False | False |
| False | True | False |
| True | False | False |
| True | True | True |

The Python implementation uses `p and q`. JavaScript uses `p && q`, and C++ uses `p && q`.

A practical authorization condition can use AND to require several conditions simultaneously:

`authenticated ∧ account_active ∧ mfa_verified`

Every condition must be satisfied.

---

## The OR connective

OR is called disjunction.

It is written:

`P ∨ Q`

In propositional logic, OR normally means inclusive OR. The result is true when at least one operand is true, including the case where both are true.

| P | Q | P ∨ Q |
|---|---|-------|
| False | False | False |
| False | True | True |
| True | False | True |
| True | True | True |

This differs from exclusive OR.

Exclusive OR, or XOR, is true only when exactly one operand is true:

`P XOR Q`

The implementations demonstrate XOR using inequality between Boolean values.

---

## The NOT connective

NOT is called negation.

It is written:

`¬P`

It reverses the truth value.

| P | ¬P |
|---|----|
| False | True |
| True | False |

Python uses `not`, JavaScript uses `!`, and C++ uses `!`.

For example:

`NOT authenticated`

represents the condition that authentication is false.

---

## Implication

Implication is written:

`P → Q`

It is read as:

"P implies Q"

or:

"If P, then Q."

Material implication is defined by:

`P → Q ≡ ¬P ∨ Q`

Its truth table is:

| P | Q | P → Q |
|---|---|-------|
| False | False | True |
| False | True | True |
| True | False | False |
| True | True | True |

The only false case is when `P` is true and `Q` is false.

This behavior is important because implication does not automatically express causation. It is a truth-functional relationship.

For example:

`P = "A number is divisible by 4"`

`Q = "A number is even"`

The implication:

`P → Q`

states that every number satisfying `P` also satisfies `Q`.

It does not state that divisibility by 4 physically causes evenness.

---

## Converse, inverse, and contrapositive

Given:

`P → Q`

there are four related expressions.

### Original

`P → Q`

### Converse

`Q → P`

The converse is not generally equivalent to the original implication.

### Inverse

`¬P → ¬Q`

The inverse is not generally equivalent to the original implication.

### Contrapositive

`¬Q → ¬P`

The contrapositive is logically equivalent to the original implication:

`P → Q ≡ ¬Q → ¬P`

The Python and JavaScript implementations explicitly calculate these forms.

---

## Necessary and sufficient conditions

For:

`P → Q`

`P` is sufficient for `Q`.

If `P` is true, that is enough to establish `Q`.

`Q` is necessary for `P`.

If `P` is true, `Q` must also be true.

This distinction is important in mathematics, software requirements, security rules, and formal specifications.

A common error is to treat a sufficient condition as though it were also necessary. That requires the reverse implication:

`Q → P`

When both directions hold, the relationship can be expressed as a biconditional.

---

## Biconditional

The biconditional is written:

`P ↔ Q`

It is read:

"P if and only if Q."

It is true when both propositions have the same truth value.

| P | Q | P ↔ Q |
|---|---|-------|
| False | False | True |
| False | True | False |
| True | False | False |
| True | True | True |

The biconditional can be expressed as:

`(P → Q) ∧ (Q → P)`

It can also be expressed as:

`(P ∧ Q) ∨ (¬P ∧ ¬Q)`

The Python, JavaScript, and C++ implementations verify the equivalence of these definitions.

---

## Logical precedence

Compound expressions can contain several connectives.

A conventional precedence hierarchy is:

1. NOT
2. AND
3. OR
4. implication
5. biconditional

Thus:

`¬P ∨ Q ∧ R`

is interpreted as:

`(¬P) ∨ (Q ∧ R)`

rather than:

`(¬P ∨ Q) ∧ R`

Parentheses override precedence.

For example:

`(¬P ∨ Q) ∧ R`

has an explicitly different structure.

Explicit parentheses are especially important in security policies and production software because a mathematically valid expression can still be misunderstood by a reader.

---

## Implication associativity

Implication is commonly treated as right-associative.

Therefore:

`P → Q → R`

is interpreted as:

`P → (Q → R)`

rather than:

`(P → Q) → R`

The Python parser and JavaScript parser implement this behavior explicitly through recursive parsing of the right side of an implication.

This is an important distinction because the two expressions can produce different results.

---

## Truth tables

A truth table lists every possible combination of truth values for the variables in a formula.

For `n` independent Boolean variables, there are:

`2^n`

possible assignments.

For example:

| Variables | Assignments |
|-----------|-------------|
| 1 | 2 |
| 2 | 4 |
| 3 | 8 |
| 4 | 16 |
| 5 | 32 |
| 10 | 1,024 |
| 20 | 1,048,576 |

The implementations generate truth tables programmatically rather than manually entering rows.

Truth tables are useful for:

- checking definitions
- proving small logical equivalences
- identifying counterexamples
- classifying formulas
- verifying authorization policies
- validating transformations

Their main limitation is exponential growth.

---

## Tautologies, contradictions, and contingencies

A formula is a tautology when it is true under every possible assignment.

Example:

`P ∨ ¬P`

A formula is a contradiction when it is false under every possible assignment.

Example:

`P ∧ ¬P`

A contingency is true for some assignments and false for others.

Example:

`P`

The Python, JavaScript, and C++ implementations classify formulas using generated truth tables.

---

## Logical equivalence

Two formulas are logically equivalent when they have the same truth value under every possible assignment.

Logical equivalence is written:

`A ≡ B`

For example:

`P → Q`

is equivalent to:

`¬P ∨ Q`

The implementations test equivalence by evaluating both formulas against every possible assignment.

For small formulas, exhaustive comparison is straightforward. For large formulas, more sophisticated symbolic or SAT-based techniques may be required.

---

## Important logical laws

### Identity laws

`P ∧ True ≡ P`

`P ∨ False ≡ P`

### Domination laws

`P ∨ True ≡ True`

`P ∧ False ≡ False`

### Idempotent laws

`P ∨ P ≡ P`

`P ∧ P ≡ P`

### Complement laws

`P ∨ ¬P ≡ True`

`P ∧ ¬P ≡ False`

### Double negation

`¬¬P ≡ P`

### De Morgan's laws

`¬(P ∧ Q) ≡ ¬P ∨ ¬Q`

`¬(P ∨ Q) ≡ ¬P ∧ ¬Q`

### Absorption laws

`P ∨ (P ∧ Q) ≡ P`

`P ∧ (P ∨ Q) ≡ P`

The Python, JavaScript, and C++ implementations use executable assertions to verify important laws.

---

## Python implementation

The Python implementation begins with direct Boolean expressions and progressively builds a small propositional-logic framework.

### Core operators

The functions `logical_and`, `logical_or`, `logical_not`, `implies`, and `iff` directly represent the principal connectives.

Python's `and`, `or`, and `not` provide natural implementations of the corresponding logical operations.

Implication is implemented as:

`(not p) or q`

because:

`P → Q ≡ ¬P ∨ Q`

Biconditional is implemented using Boolean equality:

`p == q`

because two Boolean values are equal exactly when they have the same truth value.

### Truth-table generation

The `truth_table` function uses `itertools.product` to enumerate every combination of Boolean values.

For three variables, eight assignments are evaluated.

This approach is transparent and appropriate for educational and small-scale verification tasks.

### Classification

The `classify_expression` function determines whether a formula is a tautology, contradiction, or contingency.

It evaluates the formula for every possible assignment and examines the complete set of results.

### Equivalence

The `equivalent` function compares two formulas under every possible assignment.

The function returns `True` only if every row produces the same result.

### Counterexamples

The `find_counterexample` function returns an assignment where two formulas differ.

This is particularly useful when a suspected equivalence is false.

For example, `P → Q` and `Q → P` are not equivalent. The assignment `P=True, Q=False` demonstrates the difference.

### Satisfiability

The `satisfying_assignments` function searches for assignments that make a formula true.

A formula with at least one satisfying assignment is satisfiable.

A formula with no satisfying assignment is unsatisfiable.

### Expression trees

The Python implementation defines symbolic expression classes including:

- `Variable`
- `UnaryNot`
- `Binary`
- `Literal`

An expression tree represents the logical structure explicitly.

For example:

`¬P ∨ (Q ∧ R)`

can be represented as a tree whose root is OR, whose left child is NOT, and whose right child is AND.

This representation is more suitable for symbolic manipulation than storing a formula as a plain string.

### Recursive-descent parser

The Python implementation includes a parser supporting expressions such as:

`NOT P OR Q AND R`

and:

`(P OR Q) AND (NOT P OR R)`

The parser separates syntax from evaluation.

Its grammar establishes the precedence hierarchy:

- biconditional
- implication
- OR
- AND
- NOT
- atomic variables

The parser also treats implication as right-associative.

---

## JavaScript implementation

The JavaScript implementation complements the Python implementation by demonstrating the same logical concepts using JavaScript's Boolean model and application-oriented structures.

### Native Boolean operators

JavaScript provides:

- `&&` for logical AND
- `||` for logical OR
- `!` for logical NOT

Implication and biconditional are implemented as functions because JavaScript has no dedicated operators for them.

### Truth-table generation

The `booleanAssignments` function generates all possible Boolean assignments recursively.

The `truthTable` function then evaluates an expression against those assignments.

This demonstrates how a language-level Boolean model can be combined with higher-level logical reasoning.

### Strict validation

JavaScript has truthy and falsy values.

For example, values such as:

- `0`
- `""`
- `null`
- `undefined`

can participate in Boolean contexts even though they are not actual Boolean values.

The `requireBoolean` function demonstrates strict validation for security-sensitive policy evaluation.

This is useful when a logical policy must distinguish the actual Boolean value `false` from malformed or unexpected input.

### Symbolic expressions

The JavaScript implementation contains classes for:

- variables
- negation
- binary expressions

The `evaluate` method evaluates an expression against an assignment object.

This creates an expression-tree model similar to the Python and C++ implementations while using JavaScript class syntax.

### Recursive-descent parser

The JavaScript parser tokenizes an input string and constructs an expression tree.

Supported operators include:

- `NOT`
- `AND`
- `OR`
- `->`
- `<->`

Parentheses are supported.

The parser is structured by precedence level. This means that parsing is not dependent on JavaScript's own operator precedence.

That distinction is important because propositional implication and biconditional are not native JavaScript operators.

### Short-circuit evaluation

JavaScript evaluates `&&` and `||` using short-circuit semantics.

For:

`false && expression`

the second expression is not evaluated.

For:

`true || expression`

the second expression is not evaluated.

Short-circuit evaluation can improve performance and can also prevent unnecessary or unsafe operations.

---

## C++ case study

The C++ implementation develops a reusable propositional expression engine and applies it to an enterprise access-control scenario.

### Problem being modeled

The system grants access only when all of the following are satisfied:

`authenticated`

AND

`account_active`

AND

`mfa_verified`

AND

`administrator OR resource_owner`

AND

`NOT emergency_lock`

The complete policy is:

`authenticated ∧ account_active ∧ mfa_verified ∧ (administrator ∨ resource_owner) ∧ ¬emergency_lock`

This is a realistic structure for a Boolean authorization rule because several independent conditions must hold simultaneously.

### Design approach

The C++ program represents logical expressions as objects.

The abstract `Expression` class defines a common interface for:

- evaluation
- textual description
- variable collection

Concrete classes include:

- `VariableExpression`
- `ConstantExpression`
- `NotExpression`
- `BinaryExpression`

This is an expression-tree architecture.

### Expression tree

The tree represents the actual logical structure instead of depending on a textual expression alone.

For example, the access policy contains a subtree for:

`administrator OR resource_owner`

and another subtree for:

`NOT emergency_lock`

These subtrees are combined with AND expressions.

The structure makes precedence explicit.

### Polymorphism

The `Expression` base class provides a common interface.

Derived classes implement their own evaluation behavior.

This allows the policy engine to operate on a generic `ExpressionPtr` without needing to know whether the object represents a variable, constant, negation, conjunction, disjunction, implication, or biconditional.

### Smart pointers

The implementation uses `std::shared_ptr`.

This avoids manual `new` and `delete` operations and allows expression nodes to be composed safely into trees.

For this small case study, shared ownership is convenient because multiple expression-building operations can refer to immutable subexpressions.

### Immutable-style expressions

Expression nodes are not modified after construction.

Their `evaluate` methods operate on an external `Assignment`.

This separates:

- formula structure
- input values
- evaluation results

The same formula can therefore be evaluated repeatedly under different assignments.

---

## Policy evaluation

The `UserContext` structure contains Boolean attributes such as:

- `authenticated`
- `account_active`
- `mfa_verified`
- `administrator`
- `resource_owner`
- `emergency_lock`

The `AccessPolicy` converts this context into an assignment and evaluates the expression tree.

This creates a clean separation between domain data and logical policy.

Example scenarios include:

### Administrator

An authenticated administrator with an active account, valid MFA, and no emergency lock satisfies the policy.

### Resource owner

A non-administrator resource owner can satisfy the policy when the identity and account conditions are also satisfied.

### Unauthenticated user

An administrator flag by itself does not bypass the authentication requirement.

### Missing MFA

A user who has not completed MFA fails the policy even when other conditions are satisfied.

### Emergency lock

The emergency-lock condition explicitly overrides otherwise valid access conditions.

### Inactive account

An inactive account fails even if authentication, MFA, and authorization role conditions are satisfied.

---

## Argument validity

An argument is valid when there is no assignment under which all premises are true while the conclusion is false.

The C++ implementation demonstrates Modus Ponens:

`P → Q`

`P`

therefore:

`Q`

The program also tests the invalid converse-style argument:

`P → Q`

`Q`

therefore:

`P`

The latter is invalid because the assignment:

`P = False`

`Q = True`

satisfies the premises but makes the conclusion false.

---

## Entailment

A set of premises entails a conclusion when every assignment satisfying the premises also satisfies the conclusion.

For a single premise:

`P`

and conclusion:

`Q`

the entailment does not hold because there are assignments where `P` is true and `Q` is false.

For:

`P ∧ Q`

and conclusion:

`P`

the entailment does hold.

The Python and JavaScript implementations demonstrate this reasoning directly through exhaustive assignments.

---

## Satisfiability

A formula is satisfiable when at least one assignment makes it true.

For example:

`P ∨ Q`

is satisfiable because several assignments make it true.

A contradiction such as:

`P ∧ ¬P`

is unsatisfiable.

The implementations find satisfying assignments by exhaustive enumeration.

This is conceptually related to the SAT problem, where the objective is to determine whether a Boolean formula has at least one satisfying assignment.

---

## CNF and DNF

Two important normal forms are Conjunctive Normal Form and Disjunctive Normal Form.

### Conjunctive Normal Form

CNF is an AND of OR clauses.

Example:

`(P ∨ Q) ∧ (¬P ∨ R)`

Each clause is an OR expression, and the clauses are combined with AND.

CNF is important in SAT solving and constraint-processing systems.

### Disjunctive Normal Form

DNF is an OR of AND terms.

Example:

`(P ∧ Q) ∨ (¬P ∧ R)`

The Python implementation contains examples of both structures.

---

## Common mistakes

### Treating implication as equivalence

`P → Q` does not imply:

`Q → P`

The reverse direction requires separate justification.

### Confusing implication with causation

Material implication is a truth-functional connective. It does not by itself express a causal mechanism.

### Confusing OR with XOR

`P ∨ Q` is true when both propositions are true.

XOR requires exactly one true operand.

### Ignoring precedence

An expression such as:

`P OR Q AND R`

is normally interpreted as:

`P OR (Q AND R)`

not:

`(P OR Q) AND R`

### Forgetting parentheses

Even when precedence is formally defined, complicated expressions should use explicit parentheses when the logical structure matters.

### Treating arbitrary values as Booleans

This is especially important in JavaScript.

A value that is truthy is not necessarily the Boolean value `true`.

### Assuming a local example proves an equivalence

A formula may produce the same result for a few selected assignments while differing elsewhere.

Logical equivalence requires agreement under every possible assignment.

---

## Edge cases

### False implication

`True → False` is the only false row in the implication truth table.

### False antecedent

Both:

`False → False`

and:

`False → True`

are true under material implication.

### Biconditional with equal values

Both:

`False ↔ False`

and:

`True ↔ True`

are true.

### Repeated variables

Expressions can contain the same variable more than once.

For example:

`P ∨ P`

is equivalent to:

`P`

### Missing assignments

A symbolic evaluator cannot correctly evaluate a variable if no value has been provided for it.

The implementations deliberately raise errors rather than silently guessing a value.

### Empty or malformed expressions

A parser should reject unexpected tokens, unmatched parentheses, unsupported operators, and incomplete expressions.

The Python and JavaScript parsers include explicit syntax-error handling.

---

## Performance considerations

Truth-table enumeration requires:

`2^n`

assignments for `n` independent variables.

This exponential growth is the principal limitation of naive exhaustive evaluation.

For small formulas, exhaustive enumeration has significant advantages:

- simple implementation
- deterministic behavior
- complete coverage
- easy verification
- useful counterexamples

For large formulas, enumerating every assignment may become impractical.

More advanced approaches include:

- SAT solving
- Binary Decision Diagrams
- symbolic simplification
- constraint propagation
- memoization
- CNF transformation
- incremental solving
- Tseitin-style encodings

The appropriate technique depends on formula size, structure, and application requirements.

---

## Short-circuit evaluation

Programming-language Boolean operators often use short-circuit evaluation.

For AND:

`False AND X`

is already false, so `X` does not need to be evaluated.

For OR:

`True OR X`

is already true, so `X` does not need to be evaluated.

Python, JavaScript, and C++ support short-circuit behavior for their native logical operators.

Short-circuiting can reduce unnecessary work and can avoid evaluating expressions with side effects or failure conditions.

A symbolic logic engine may choose different evaluation semantics depending on its requirements, especially if expression evaluation has side effects.

---

## Security considerations

Boolean logic frequently appears in:

- access-control systems
- authentication policies
- authorization rules
- firewall conditions
- feature permissions
- validation systems
- compliance rules
- workflow conditions

Security-sensitive policies should be explicit and auditable.

A rule such as:

`authenticated ∧ (administrator ∨ owner)`

is structurally different from an ambiguously written expression such as:

`authenticated ∧ administrator ∨ owner`

Depending on the evaluation rules, the second expression can grant access under conditions that were not intended.

Useful implementation practices include:

- explicit parentheses
- strict input validation
- deny-by-default policies where appropriate
- exhaustive tests for small policies
- logging of policy decisions
- deterministic evaluation
- clear variable names
- separation of policy definition from input data
- validation of parser input
- avoidance of ambiguous textual policy formats

The implementations demonstrate strict Boolean validation and explicit expression structures.

---

## Implementation considerations

### Python

Python is particularly convenient for teaching propositional logic because Boolean expressions have readable syntax and the standard library provides convenient tools such as `itertools.product`.

Its concise syntax makes truth-table generation and exhaustive testing straightforward.

### JavaScript

JavaScript is useful for application-level Boolean logic because Boolean expressions are directly relevant to browser applications, web services, validation, UI state, and authorization logic.

Its truthy/falsy model also demonstrates why strict Boolean validation can matter in application code.

### C++

C++ provides stronger control over data structures, object lifetimes, polymorphism, and performance.

The C++ case study uses these capabilities to construct a reusable expression-tree engine and apply it to a realistic policy system.

---

## Python concepts demonstrated

The Python implementation covers:

- Boolean values
- AND
- OR
- NOT
- implication
- biconditional
- XOR
- precedence
- associativity
- truth tables
- tautologies
- contradictions
- contingencies
- logical equivalence
- counterexamples
- logical laws
- necessary and sufficient conditions
- inference rules
- entailment
- argument validity
- satisfiability
- expression trees
- symbolic formulas
- recursive-descent parsing
- error handling
- validation
- brute-force complexity
- practical authorization policies

---

## JavaScript concepts demonstrated

The JavaScript implementation covers:

- JavaScript Boolean operators
- implication and biconditional functions
- XOR
- truth-table generation
- formula classification
- logical equivalence
- logical laws
- implication relationships
- argument validity
- satisfiability
- counterexample detection
- expression-tree classes
- strict Boolean validation
- short-circuit evaluation
- tokenization
- recursive-descent parsing
- precedence-aware parsing
- right-associative implication
- entailment
- enterprise policy evaluation

---

## C++ concepts demonstrated

The C++ implementation covers:

- Boolean operators
- truth-table enumeration
- expression interfaces
- polymorphism
- variables
- constants
- negation
- binary operators
- expression trees
- smart pointers
- symbolic evaluation
- variable collection
- tautology/contradiction/contingency classification
- logical equivalence
- counterexample search
- satisfiability
- argument validity
- enterprise authorization
- structured policy contexts
- exception handling
- assertions
- short-circuit evaluation
- complexity analysis

---

## Important distinctions

| Concept | Meaning |
|---|---|
| AND | Both operands must be true |
| OR | At least one operand must be true |
| NOT | Reverses a truth value |
| XOR | Exactly one operand is true |
| Implication | False only when antecedent is true and consequent is false |
| Biconditional | True when both operands have the same truth value |
| Tautology | True under every assignment |
| Contradiction | False under every assignment |
| Contingency | True under some assignments and false under others |
| Equivalence | Two formulas have identical truth behavior |
| Satisfiability | At least one assignment makes a formula true |
| Entailment | Every assignment satisfying the premises satisfies the conclusion |
| Converse | Reverses the direction of an implication |
| Inverse | Negates both sides of an implication |
| Contrapositive | Negates and reverses an implication |

---

## Real-world relevance

Propositional logic provides a foundation for many systems that make decisions from Boolean conditions.

Examples include:

### Access control

`authenticated ∧ (administrator ∨ owner)`

### Authentication requirements

`password_valid ∧ mfa_verified`

### Transaction approval

`authenticated ∧ account_active ∧ sufficient_balance`

### Feature availability

`licensed ∧ enabled ∧ ¬maintenance_mode`

### Network filtering

`trusted_source ∧ approved_protocol ∧ ¬blocked_address`

### Software validation

`input_present ∧ format_valid ∧ within_range`

These examples are simplified models. Production systems may require richer policy languages, temporal logic, probabilistic rules, role hierarchies, attribute-based access control, or external policy engines.

---

## Design trade-offs

### Direct Boolean expressions

Advantages:

- simple
- fast
- readable
- easy to execute

Limitations:

- difficult to inspect structurally
- difficult to parse dynamically
- difficult to transform symbolically

### Expression trees

Advantages:

- explicit structure
- easy recursive evaluation
- suitable for symbolic manipulation
- supports structural validation

Limitations:

- more implementation complexity
- additional memory for nodes
- requires careful ownership design

### String-based expressions

Advantages:

- convenient for configuration
- human-readable
- easy to store

Limitations:

- requires tokenization and parsing
- malformed input must be rejected
- operator precedence must be defined
- security-sensitive systems must validate accepted syntax carefully

The Python and JavaScript implementations demonstrate parsing, while the C++ case study primarily constructs its expression tree programmatically.

---

## Precedence-aware grammar

The parser implementations conceptually use the following hierarchy:

`expression := biconditional`

`biconditional := implication ("<->" implication)*`

`implication := disjunction ("->" implication)?`

`disjunction := conjunction ("OR" conjunction)*`

`conjunction := negation ("AND" negation)*`

`negation := "NOT" negation | atom`

`atom := variable | "(" expression ")"`

This grammar gives NOT the highest precedence among the supported connectives and biconditional the lowest.

The recursive definition of implication makes it right-associative.

---

## Testing strategy

A propositional-logic implementation can be tested at several levels.

### Unit tests

Test each connective independently.

Examples:

`AND(True, True) = True`

`AND(True, False) = False`

`NOT(True) = False`

`True → False = False`

`True ↔ True = True`

### Law-based tests

Verify known equivalences such as:

`P → Q ≡ ¬P ∨ Q`

and:

`¬(P ∧ Q) ≡ ¬P ∨ ¬Q`

### Exhaustive tests

For small formulas, evaluate every possible assignment.

This provides complete coverage over the formula's Boolean input space.

### Counterexample testing

When equivalence fails, return an assignment showing the difference.

This provides concrete evidence of why two expressions are not equivalent.

### Application tests

For authorization policies, test cases should cover:

- valid administrator
- valid resource owner
- unauthenticated user
- inactive account
- missing MFA
- emergency lock
- unauthorized user

The C++ case study includes these scenarios directly.

---

## Limitations of the implementations

The implementations intentionally use exhaustive evaluation for educational clarity.

They are not intended to replace optimized industrial SAT solvers or full-featured policy engines for large formulas.

The major limitations are:

- exponential truth-table growth
- limited expression syntax
- no quantifiers
- no temporal operators
- no probabilistic semantics
- no first-order variables
- no automated CNF optimizer
- no industrial SAT-solving heuristics

These limitations distinguish propositional logic from more expressive logical systems.

---

## Relation to other forms of logic

Propositional logic treats complete statements as atomic Boolean units.

It does not directly represent internal structure such as:

"Every employee has an account."

That type of statement requires quantified variables and belongs to predicate or first-order logic.

Similarly, statements about time, probability, uncertainty, knowledge, or necessity may require other formal systems.

Propositional logic remains an important foundation because many complex systems ultimately contain Boolean decision structures.

---

## Practical interpretation of implication

A particularly important conceptual distinction is the difference between:

`P → Q`

and:

`P ↔ Q`

Implication establishes one direction:

`P` is sufficient for `Q`.

Biconditional establishes both directions:

`P → Q`

and:

`Q → P`

Therefore, replacing implication with biconditional can substantially strengthen a requirement.

For example:

`administrator → privileged`

does not mean:

`privileged → administrator`

A privileged user might satisfy the policy through another permitted role.

---

## Practical interpretation of precedence

Consider:

`authenticated ∧ administrator ∨ owner`

If AND has higher precedence than OR, the expression means:

`(authenticated ∧ administrator) ∨ owner`

This allows `owner` to satisfy the expression even when authentication is false.

A different intended policy might be:

`authenticated ∧ (administrator ∨ owner)`

The second structure requires authentication in both authorization paths.

This illustrates why logical precedence is not merely an academic issue. The grouping of Boolean conditions can alter real system behavior.

---

## Files

The four implementation artifacts are intended to correspond directly:

- Python: comprehensive learning and verification implementation
- JavaScript: application-oriented Boolean and parser implementation
- C++: structured enterprise authorization case study
- README: conceptual and technical explanation of the implementations

Each implementation is self-contained and uses only its respective language's standard capabilities.
