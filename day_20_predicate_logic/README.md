# Predicate Logic: Predicates, Quantifiers, Universal Quantification, and Existential Quantification

## Topic introduction

Predicate logic extends propositional logic by allowing statements to describe objects, their properties, and relationships between objects.

A proposition is a complete statement that has a truth value. For example:

- `5 is greater than 2`
- `7 is prime`
- `Alice is employed`

Predicate logic introduces variables so that a statement can describe a whole class of objects.

For example, `Even(x)` can represent the predicate "x is even."

The expression `Even(4)` is true, while `Even(5)` is false.

The variable `x` does not have a meaningful interpretation until a domain and an assignment or quantifier are supplied.

The two central quantifiers are:

- Universal quantifier: `∀`, read as "for every" or "for all"
- Existential quantifier: `∃`, read as "there exists" or "there is at least one"

Thus:

`∀x Even(x)`

means that every object in the specified domain is even.

`∃x Even(x)`

means that at least one object in the specified domain is even.

The meaning of a quantified statement depends on the domain over which its variables range. A predicate without an explicitly understood domain can therefore be ambiguous.

---

## Fundamental concepts

### Proposition

A proposition is a statement that is either true or false.

Examples:

- `2 + 2 = 4` is true.
- `7 < 3` is false.
- `10 is prime` is false.

A proposition does not contain an unbound variable whose value still needs to be supplied.

### Predicate

A predicate is an expression that becomes a proposition when its variables receive values.

For example:

`Prime(x)`

can mean "x is prime."

For a particular value:

`Prime(7)`

is true.

`Prime(8)`

is false.

A predicate can have one variable, two variables, or more.

Examples:

- `Even(x)` is unary.
- `LessThan(x, y)` is binary.
- `Between(x, y, z)` could be ternary.

### Domain

The domain is the collection of objects over which variables range.

For example, consider:

`∀x Even(x)`

If the domain is `{2, 4, 6, 8}`, the statement is true.

If the domain is `{1, 2, 3, 4}`, the statement is false.

The predicate has not changed. The interpretation of the quantified statement changed because the domain changed.

### Variable

A variable represents an object from the domain.

In:

`P(x)`

`x` is a variable.

A variable can be free or bound.

### Free variable

A variable is free when it is not controlled by a quantifier in the relevant expression.

In:

`P(x)`

`x` is free.

The expression cannot be evaluated as a complete quantified statement until a value or assignment for `x` is supplied.

### Bound variable

A variable is bound when it occurs within the scope of a quantifier that binds it.

In:

`∀x P(x)`

`x` is bound by `∀x`.

In:

`∃x P(x)`

`x` is bound by `∃x`.

The Python, JavaScript, and C++ implementations model this idea operationally by assigning each quantified variable every value in a finite domain.

---

## Universal quantification

The universal quantifier is written as:

`∀`

The expression:

`∀x P(x)`

means:

"P(x) is true for every x in the domain."

For a finite domain:

`D = {1, 2, 3, 4}`

the statement:

`∀x Even(x)`

is false because `1` is a counterexample.

A universal statement can therefore be disproved by finding a single counterexample.

The Python implementation expresses this using `forall()` and internally uses the behavior of `all()`.

The JavaScript implementation uses `Array.prototype.every()`.

The C++ implementation provides a generic template function named `forall()` that stops when it encounters a counterexample.

This short-circuit behavior is important because there is no need to inspect the remaining objects after a universal statement has already been disproved.

---

## Existential quantification

The existential quantifier is written as:

`∃`

The expression:

`∃x P(x)`

means:

"There is at least one x in the domain for which P(x) is true."

For:

`D = {1, 2, 3, 4}`

the statement:

`∃x Even(x)`

is true because `2` is a witness.

A witness is a particular object that demonstrates the truth of an existential statement.

The implementations provide witness-searching functions that return an object satisfying the predicate.

Existential evaluation can also short-circuit. Once a witness is found, the remaining domain elements do not need to be examined.

---

## Universal versus existential quantification

The difference between the two quantifiers is fundamental.

| Expression | Meaning |
|---|---|
| `∀x P(x)` | P is true for every x |
| `∃x P(x)` | P is true for at least one x |
| `¬∀x P(x)` | It is not true that P holds for every x |
| `¬∃x P(x)` | There is no x for which P holds |

Consider:

`D = {1, 2, 3, 4}`

and `Even(x)`.

Then:

`∀x Even(x)`

is false.

But:

`∃x Even(x)`

is true.

Confusing these two quantifiers is one of the most common beginner errors in predicate logic.

---

## Counterexamples

A counterexample is an object that disproves a universal claim.

Suppose:

`∀x Even(x)`

is asserted over:

`{2, 4, 6, 7, 8}`

The value `7` is a counterexample.

The Python function `find_counterexample()` returns such an object.

The same concept appears in the JavaScript implementation through `findCounterexample()` and in the C++ implementation through its generic `find_counterexample()` function.

A useful general rule is:

`∀x P(x)` is false exactly when there exists some x such that `¬P(x)` is true.

Symbolically:

`¬∀x P(x) ↔ ∃x ¬P(x)`

This is one of the most important relationships between the two quantifiers.

---

## Witnesses

An existential statement is supported by a witness.

For:

`∃x Prime(x)`

over:

`{1, 2, 3, 4, 5}`

the value `2` can be a witness.

A witness does not have to be unique.

For:

`∃x Even(x)`

over:

`{2, 4, 6}`

all three objects are witnesses.

An existential claim requires only one.

This is why existential evaluation can stop after the first successful predicate evaluation.

---

## Negating universal quantification

The correct logical transformation is:

`¬∀x P(x) ↔ ∃x ¬P(x)`

The meaning is:

"It is not true that everyone has property P" is equivalent to "someone does not have property P."

For example:

`¬∀x Even(x)`

means that at least one object is not even.

It does not mean:

`∀x ¬Even(x)`

The second expression says that no object is even, which is much stronger.

The Python, JavaScript, and C++ implementations explicitly evaluate both sides of the equivalence.

---

## Negating existential quantification

The corresponding rule is:

`¬∃x P(x) ↔ ∀x ¬P(x)`

The meaning is:

"There does not exist an object having property P" is equivalent to "every object lacks property P."

For example:

`¬∃x Prime(x)`

means that no object in the domain is prime.

This is equivalent to:

`∀x ¬Prime(x)`

These rules are the quantified form of De Morgan-style reasoning.

---

## Vacuous truth

A subtle property of universal quantification appears with an empty domain.

Consider:

`D = ∅`

Then:

`∀x P(x)`

is true for the empty domain under standard first-order semantics.

The reason is that a universal statement is false only when a counterexample exists. An empty domain contains no counterexample.

In contrast:

`∃x P(x)`

is false over an empty domain because an existential statement requires a witness.

The implementations explicitly demonstrate both cases.

This behavior is sometimes called vacuous truth.

---

## Implication

An implication has the form:

`P → Q`

It means:

"If P is true, then Q must be true."

The truth condition can be expressed as:

`P → Q ≡ ¬P ∨ Q`

The only false case is:

`P = true`

and:

`Q = false`

This matters when implication is placed inside a universal statement.

For example:

`∀x (Even(x) → Positive(x))`

does not mean that every x is even.

It means that whenever an object is even, that object must be positive.

Objects that are not even do not violate the implication.

The three implementations use the equivalent expression `not P or Q` internally.

---

## Logical equivalence

Two expressions are logically equivalent when they have the same truth value under every relevant interpretation.

Examples demonstrated by the implementations include:

`P → Q ≡ ¬P ∨ Q`

`¬∀x P(x) ≡ ∃x ¬P(x)`

`¬∃x P(x) ≡ ∀x ¬P(x)`

`¬¬P ≡ P`

The programs verify these relationships computationally over finite domains.

Finite testing is useful for learning and experimentation, but checking a finite set of cases is not the same as proving a formula valid over every possible interpretation.

---

## Binary predicates and relations

A binary predicate takes two arguments.

For example:

`LessThan(x, y)`

represents the relation "x is less than y."

For the domain:

`{1, 2, 3}`

the statement:

`∃x∃y (x < y)`

is true.

There are many pairs satisfying the relation, including `(1,2)` and `(1,3)`.

By contrast:

`∀x∀y (x < y)`

is false because `x < x` is false.

The implementations use nested iteration to model these quantifiers.

---

## Nested quantifiers

Nested quantifiers combine multiple quantifiers.

Consider:

`∀x∃y P(x,y)`

This means:

"For every x, there exists at least one y such that P(x,y) is true."

The value of `y` is allowed to depend on `x`.

Compare this with:

`∃x∀y P(x,y)`

This means:

"There exists one particular x that works for every y."

The difference is substantial.

For example, over `{1,2,3,4}`:

`∀x∃y (x ≤ y)`

is true because for each x, that same x can serve as a suitable y.

But:

`∃x∀y (x ≤ y)`

is also true in this particular example because `1` is less than or equal to every member of the domain.

A different predicate can make the two formulas differ.

The important conceptual point is that quantifier order controls dependency and scope.

---

## Why quantifier order matters

In general:

`∀x∃y P(x,y)`

cannot simply be rewritten as:

`∃y∀x P(x,y)`

The first statement permits a different y for each x.

The second requires one y that works for every x.

This distinction appears throughout mathematics, algorithms, databases, verification, artificial intelligence, and formal specifications.

For example:

`∀user ∃permission`

could mean every user has some permission.

`∃permission ∀user`

could mean one single permission is available to every user.

These statements describe different requirements.

---

## Multiple variables

Predicate logic can express relationships among many objects.

For example:

`∀x∃y (y > x)`

means:

"For every x, there is a y greater than x."

Whether this is true depends on the domain.

For a finite domain `{1,2,3,4}`, it is false because there is no element greater than `4`.

For the positive integers, it is true because for every x, `x + 1` is greater than x.

This demonstrates an important point: the truth of quantified formulas depends on the interpretation and domain.

---

## Translation from English to predicate logic

Predicate logic is frequently used to formalize natural-language requirements.

Consider:

"Every qualified employee is employed."

Define:

`Qualified(x)`

and:

`Employed(x)`

The statement becomes:

`∀x (Qualified(x) → Employed(x))`

Another statement:

"At least one employee is qualified."

becomes:

`∃x (Employee(x) ∧ Qualified(x))`

Another:

"No employee is inactive."

can be represented as:

`∀x (Employee(x) → Active(x))`

or equivalently:

`¬∃x (Employee(x) ∧ ¬Active(x))`

The distinction between these expressions matters when translating requirements accurately.

---

## Python implementation

The Python implementation provides the most flexible educational model.

The function `forall()` represents universal quantification over a finite iterable.

The function `exists()` represents existential quantification.

For example, conceptually:

`forall(numbers, is_even)`

corresponds to:

`∀x Even(x)`

and:

`exists(numbers, is_even)`

corresponds to:

`∃x Even(x)`

Python's built-in `all()` and `any()` make this particularly natural.

The script also includes:

- Unary predicates
- Binary predicates
- Quantifier negation
- Nested quantifiers
- Counterexample extraction
- Witness extraction
- Vacuous truth
- Logical implication
- Relation properties
- Formula objects
- Finite-model evaluation
- Practical authorization rules
- Complexity demonstrations
- Assertions for logical laws

### Formula objects

The Python implementation goes beyond simple functions by defining a small hierarchy:

- `Formula`
- `PredicateFormula`
- `NotFormula`
- `AndFormula`
- `OrFormula`
- `ImpliesFormula`
- `UniversalFormula`
- `ExistentialFormula`

This resembles the abstract syntax structure of a logical expression.

For example, an implication can contain two formulas, while a universal formula contains a variable, a domain, and a body.

This illustrates how a logical expression can be represented as data rather than only as executable code.

---

## JavaScript implementation

JavaScript demonstrates the same logical concepts in a language commonly used for web and application development.

The `forall()` function uses `Array.prototype.every()`.

The `exists()` function uses `Array.prototype.some()`.

This makes the connection between finite quantification and collection processing particularly direct.

The implementation also demonstrates:

- Arrow functions
- Classes
- Object construction
- Sets
- Higher-order functions
- Short-circuit array operations
- Formula object hierarchies
- Nested quantification
- Relation testing
- Practical authorization rules
- Error reporting through exceptions
- Logical equivalence tests

### JavaScript-specific perspective

JavaScript's functional array methods provide a useful connection between predicate logic and collection operations.

For example:

`numbers.every(isEven)`

has the same finite-domain interpretation as:

`∀x Even(x)`

while:

`numbers.some(isEven)`

corresponds to:

`∃x Even(x)`

This does not mean JavaScript's array methods are themselves a complete implementation of first-order logic. They provide finite-domain operational counterparts for common quantified expressions.

---

## C++ case study

The C++ implementation presents predicate logic through a security access-control scenario.

The modeled system contains:

- Employees
- Departments
- Age
- Active status
- Training status
- Security clearance
- Access requests
- Authentication state
- Roles
- Resources

The purpose is to demonstrate how logical predicates can describe operational policies.

### Employee predicates

The case study defines predicates such as:

`is_adult(employee)`

`is_active(employee)`

`is_trained(employee)`

`has_sufficient_clearance(employee)`

These can be combined into:

`can_enter_secure_area(employee)`

The resulting policy is approximately:

`Adult(x) ∧ Active(x) ∧ Trained(x) ∧ ClearanceAtLeast2(x)`

This is a conjunction of predicates describing conditions that must all hold.

### Universal policy

The program evaluates:

`∀x Adult(x)`

using the generic C++ `forall()` function.

If one employee is under the required age, the statement becomes false.

The program can then identify a violating employee.

### Existential policy

The program also evaluates:

`∃x CanEnterSecureArea(x)`

This is true when at least one employee satisfies the complete access predicate.

The first employee satisfying the predicate is a witness.

### Conditional policy

The program evaluates:

`∀x (Trained(x) → Active(x))`

A counterexample must satisfy:

`Trained(x)`

and:

`¬Active(x)`

The case study deliberately includes such a condition so that the program can demonstrate how a universal implication can fail.

### Authorization policy

The program models a simplified rule requiring:

- Authentication
- Active account status
- Administrator role

The resulting predicate is used to decide whether a request receives access.

This is an educational logical model rather than a complete production authorization mechanism.

---

## Finite models

A finite model provides:

- A finite domain
- Interpretations of predicates and relations

For example:

`D = {1,2,3,4,5}`

with:

`Even(x)`

and:

`Prime(x)`

defined over that domain.

The statement:

`∀x (Even(x) → Positive(x))`

can then be evaluated by checking every object in the finite model.

Finite models are especially useful for learning because every quantifier can be implemented as iteration.

They are also useful for testing candidate formulas and exploring counterexamples.

---

## Satisfiability and validity

A formula is satisfiable if there is an interpretation or assignment under which it is true.

For a finite domain, a unary predicate can be tested for satisfiability using:

`∃x P(x)`

A formula is universally valid within a specific finite interpretation when:

`∀x P(x)`

is true.

There is an important distinction between:

- Being true in one finite model
- Being true in every model

A finite program can exhaustively evaluate a finite model, but first-order validity in general is a deeper logical problem than simply running a loop over one dataset.

---

## Relation properties

Relations can themselves be described using predicates and quantifiers.

### Reflexivity

A relation R is reflexive when:

`∀x R(x,x)`

Equality is reflexive because every object is equal to itself.

### Symmetry

A relation R is symmetric when:

`∀x∀y (R(x,y) → R(y,x))`

If x is related to y, y must also be related to x.

### Transitivity

A relation R is transitive when:

`∀x∀y∀z ((R(x,y) ∧ R(y,z)) → R(x,z))`

Equality satisfies all three properties.

The Python and C++ implementations explicitly evaluate these properties over finite domains.

---

## Scope and variable binding

Quantifier scope determines which occurrences of a variable are controlled by the quantifier.

For example:

`∀x (P(x) ∧ Q(x))`

binds both occurrences of x inside the expression.

A variable name can be reused in nested scopes, but this can reduce readability.

Using distinct names such as:

`∀x ∃y R(x,y)`

usually makes the dependency structure clearer.

The distinction between free and bound variables is essential when constructing or manipulating formulas programmatically.

---

## Common mistakes

### Mistaking existential quantification for universal quantification

Incorrect reasoning:

"At least one employee is trained, therefore every employee is trained."

From:

`∃x Trained(x)`

it does not follow that:

`∀x Trained(x)`

### Incorrectly negating a universal statement

Incorrect:

`¬∀x P(x) = ∀x ¬P(x)`

Correct:

`¬∀x P(x) = ∃x ¬P(x)`

### Incorrectly negating an existential statement

Incorrect:

`¬∃x P(x) = ∃x ¬P(x)`

Correct:

`¬∃x P(x) = ∀x ¬P(x)`

### Swapping quantifier order

In general:

`∀x∃y P(x,y)`

does not mean the same thing as:

`∃y∀x P(x,y)`

The first permits y to depend on x. The second requires one y that works for every x.

### Ignoring the domain

A predicate's meaning cannot be interpreted correctly without knowing what objects the variables range over.

### Confusing implication with conjunction

`P → Q`

does not mean:

`P ∧ Q`

An implication can be true when P is false.

### Assuming an existential witness must be unique

`∃x P(x)` requires at least one witness, not exactly one.

"Exactly one" requires a stronger statement involving both existence and uniqueness.

---

## Edge cases

### Empty domain

For the standard finite-domain implementation:

`∀x P(x)`

evaluates to true over an empty domain.

`∃x P(x)`

evaluates to false.

### Single-element domain

If the domain contains only one object, universal and existential statements can sometimes have the same truth value for a predicate because both refer to that one object.

This does not make the quantifiers logically identical.

### Duplicate values in a programming collection

Mathematically, a domain is usually treated as a set of objects. A JavaScript array or Python list can contain duplicates.

For a pure predicate with no side effects, duplicates generally do not change the truth value of `all()` or `any()`, although they can change the amount of work performed.

### Short-circuiting

Universal evaluation can stop at the first counterexample.

Existential evaluation can stop at the first witness.

This affects performance while preserving the logical result.

### Empty inner domain

For nested quantifiers, an empty inner domain has important consequences.

`∀x∃y P(x,y)`

fails when the inner domain is empty unless the outer domain is also empty.

`∃x∀y P(x,y)`

can become true for an outer witness because `∀y P(x,y)` is vacuously true over an empty inner domain.

This is one reason domain assumptions matter in formal reasoning.

---

## Performance considerations

For a domain of size `n`:

- A single quantifier generally requires up to `O(n)` predicate evaluations.
- Two nested quantifiers can require up to `O(n²)`.
- Three nested quantifiers can require up to `O(n³)`.
- k directly nested finite quantifiers can require up to `O(n^k)` evaluations.

Short-circuiting can reduce actual execution time.

For example, a universal statement may terminate immediately when its first object is a counterexample.

An existential statement may terminate after examining only one object if that object is a witness.

The worst case still requires examining a large portion or all of the search space.

This combinatorial behavior is one reason automated reasoning can become computationally expensive.

---

## Implementation considerations

The three implementations use different programming styles.

### Python

Python emphasizes readability and abstraction.

The `forall()` and `exists()` functions are generic because they accept a domain and predicate function.

Python's higher-order functions make it easy to construct quantified expressions dynamically.

The formula class hierarchy demonstrates how a logical expression can be represented as an object structure.

### JavaScript

JavaScript demonstrates the connection between predicates and collection processing.

`every()` and `some()` provide concise finite-domain quantifier operations.

JavaScript classes demonstrate how formula structures can be represented in an object-oriented application.

### C++

C++ emphasizes generic programming, explicit data structures, and strong control over implementation details.

The templated `forall()` and `exists()` functions can work with different containers.

The security case study uses structures, vectors, lambdas, templates, optional values, and standard algorithms.

---

## Security considerations

Predicate logic is useful for expressing security requirements, but a logical model is not automatically a secure implementation.

A policy such as:

`Authenticated(x) ∧ Active(x) ∧ Admin(x)`

can describe an intended authorization rule.

A real system must also protect:

- Identity credentials
- Authentication mechanisms
- Authorization enforcement points
- Session state
- Audit records
- Role assignment
- Permission changes
- Revocation
- Secrets
- Network communication
- Application state
- Input validation

A formally correct policy can still be undermined by an implementation vulnerability.

The C++ case study therefore treats its authorization predicates as an educational model rather than a complete access-control system.

---

## Debugging considerations

When debugging quantified logic, inspect the domain first.

For a universal claim:

1. Identify the predicate.
2. Evaluate it for each object.
3. Find the first false result.
4. Treat that object as a counterexample.

For an existential claim:

1. Identify the predicate.
2. Evaluate it for each object.
3. Stop when a true result is found.
4. Treat that object as a witness.

For nested quantifiers, inspect each level separately.

For:

`∀x∃y P(x,y)`

the useful debugging question is:

"For which x could I not find a suitable y?"

For:

`∃x∀y P(x,y)`

the useful question is:

"Which x, if any, works for every y?"

This approach makes nested formulas much easier to analyze.

---

## Practical applications

Predicate logic is relevant to many technical areas.

### Database queries

Database systems frequently express conditions over rows and relationships.

A query can be understood conceptually as selecting objects satisfying predicates.

### Software verification

Formal specifications can express requirements such as:

`∀request Valid(request)`

or:

`∀state Safe(state)`

### Access control

Authorization policies can be represented using predicates for:

- Identity
- Role
- Permission
- Resource
- Authentication state
- Account state

### Automated reasoning

Rule engines and theorem-proving systems manipulate logical expressions and relationships between predicates.

### Artificial intelligence

Knowledge representation can use entities, properties, relations, and quantified rules.

### Mathematics

Definitions and theorems frequently use universal and existential quantification.

For example:

"For every positive integer n, there exists a larger positive integer."

can be represented as:

`∀n (PositiveInteger(n) → ∃m (PositiveInteger(m) ∧ m > n))`

### Requirements engineering

Natural-language requirements can be converted into logical constraints that can be analyzed for contradictions, missing conditions, and counterexamples.

---

## Important distinctions

### Predicate versus proposition

`Even(x)` is a predicate.

`Even(4)` is a proposition.

### Universal versus existential

`∀x P(x)` requires every object to satisfy P.

`∃x P(x)` requires at least one object to satisfy P.

### Witness versus counterexample

A witness supports an existential statement.

A counterexample disproves a universal statement.

### Scope versus value

The scope of a quantifier determines where its variable is bound.

The value assigned to a variable determines which object is being evaluated.

### Finite evaluation versus general logical validity

A program can exhaustively evaluate a formula over a finite domain.

That does not automatically establish truth over every possible model.

---

## Advanced considerations

Predicate logic becomes substantially more expressive when functions, relations, equality, nested quantifiers, and multiple predicates are combined.

For example:

`∀x (Employee(x) → ∃y (Manager(y) ∧ Supervises(y,x)))`

states that every employee has at least one manager who supervises that employee.

Another example:

`∃x (Manager(x) ∧ ∀y (Employee(y) → Supervises(x,y)))`

states that there exists one manager who supervises every employee.

The order of quantifiers creates a dependency relationship.

In the first expression, the manager may vary from employee to employee.

In the second, one manager must work for every employee.

This dependency distinction is central to more advanced formal reasoning.

---

## Formula representation

The Python and JavaScript implementations demonstrate a simplified abstract syntax structure.

A formula can be represented as a tree.

For example:

`∀x (Even(x) → Positive(x))`

can conceptually be represented as:

- Universal quantifier
  - Variable: x
  - Body:
    - Implication
      - Predicate: Even(x)
      - Predicate: Positive(x)

This representation is useful for interpreters, theorem provers, static analyzers, rule engines, and symbolic reasoning systems.

The programmatic representation separates the structure of a logical statement from the process of evaluating it.

---

## Limitations of the implementations

The three programs deliberately operate primarily over finite domains.

They do not implement a complete first-order theorem prover.

They do not provide unrestricted symbolic quantification over infinite mathematical structures.

They do not attempt to solve general first-order theorem proving.

They also use ordinary programming functions as predicate implementations rather than defining a complete formal semantics for arbitrary first-order languages.

The implementations are therefore best understood as executable finite-domain models that demonstrate the core mechanics and reasoning patterns of predicate logic.

---

## Best practices

When writing or implementing predicate logic:

- Define the domain explicitly.
- Give predicates precise meanings.
- Use meaningful variable names.
- Keep quantifier scope clear.
- Distinguish universal claims from existential claims.
- Search for counterexamples to universal statements.
- Search for witnesses for existential statements.
- Be careful when negating quantified formulas.
- Never reorder quantifiers without checking the semantic consequences.
- Separate the logical rule from the programming mechanism implementing it.
- Test edge cases such as empty and singleton domains.
- Use short-circuit evaluation where appropriate.
- Document assumptions about the domain.
- Distinguish finite-model testing from general logical proof.
- Treat security predicates as policy expressions rather than complete security controls.

---

## Core reference

| Symbol or expression | Meaning |
|---|---|
| `P(x)` | Predicate involving x |
| `P(x,y)` | Binary predicate or relation |
| `∀x P(x)` | P is true for every x |
| `∃x P(x)` | P is true for at least one x |
| `¬P(x)` | P(x) is false |
| `P(x) ∧ Q(x)` | Both predicates are true |
| `P(x) ∨ Q(x)` | At least one predicate is true |
| `P(x) → Q(x)` | If P(x), then Q(x) |
| `P(x) ↔ Q(x)` | P(x) and Q(x) have equal truth values |
| `¬∀x P(x)` | Equivalent to `∃x ¬P(x)` |
| `¬∃x P(x)` | Equivalent to `∀x ¬P(x)` |
| `∀x∃y P(x,y)` | Every x has at least one suitable y |
| `∃x∀y P(x,y)` | One x works for every y |

---

## Execution

The Python file can be executed with a standard Python 3 installation.

The JavaScript file can be executed in a modern JavaScript runtime such as Node.js.

The C++ program is designed for C++17 or later and uses the standard library.

All three implementations contain executable demonstrations rather than relying solely on explanatory text.

The output shows truth values, witnesses, counterexamples, relation properties, quantifier behavior, logical equivalences, complexity examples, and the security-oriented case study.
