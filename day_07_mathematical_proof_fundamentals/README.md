# Mathematical Proof Fundamentals

## Introduction

Mathematical proof is a structured method for establishing that a statement is true under specified assumptions. A proof is not merely a collection of examples, calculations, observations, or numerical experiments. It is a logically valid argument showing that the conclusion follows from accepted definitions, assumptions, axioms, and previously established results.

This study material develops the foundations of mathematical proof through executable Python examples. The script covers statements, propositions, assumptions, conclusions, logical implication, direct proof, universal and existential claims, counterexamples, edge cases, contrapositive reasoning, contradiction, proof by cases, proof by exhaustion, common errors, and the distinction between computational testing and mathematical proof.

Python is used as a practical tool for exploring mathematical ideas. The code can verify individual cases, search finite domains for counterexamples, validate assumptions, and demonstrate algebraic relationships. These computational activities support mathematical reasoning, but finite testing does not prove a statement concerning infinitely many objects.

## Statements

A statement is a declarative sentence that has a definite truth value.

A mathematical statement must be either true or false.

Examples of statements include:

- `2 + 3 = 5`
- `10 < 4`
- `7 is prime`
- `0 > 1`

The first and third statements are true. The second and fourth statements are false.

Not every sentence is a mathematical statement. Questions and commands do not normally have truth values.

Examples include:

- What is your name?
- Close the door.

An expression containing an unspecified variable may also fail to be a proposition until the variable is given a value or a domain and quantifier are specified.

For example:

`x + 2 = 7`

is not a proposition by itself because its truth depends on `x`.

When `x = 5`, the statement is true. When `x = 4`, it is false.

The Python script demonstrates this distinction by evaluating expressions after assigning values to variables.

## Propositions

A proposition is a statement that has a truth value of either true or false.

Examples:

- `13 is prime` is true.
- `21 is prime` is false.

A proposition can be represented computationally using a Boolean value. The script defines a `Proposition` class containing:

- a textual description
- a truth value

This mirrors the mathematical idea that a proposition is a claim whose truth status can be determined.

Propositions form the basic components of logical arguments and mathematical proofs.

## Compound Propositions

Simple propositions can be combined using logical operators.

The principal operations include:

### Conjunction

The statement `P AND Q` is true only when both `P` and `Q` are true.

In Python, conjunction is represented using:

    P and Q

### Disjunction

The statement `P OR Q` is true when at least one of the propositions is true.

In Python:

    P or Q

### Negation

The negation of `P` reverses its truth value.

In Python:

    not P

### Implication

A conditional statement has the form:

`If P, then Q`

or symbolically:

`P → Q`

The implication is false only when `P` is true and `Q` is false.

A logical implication is equivalent to:

`NOT P OR Q`

The script implements implication using:

    return (not p) or q

This definition is important because many mathematical theorems have conditional form.

### Biconditional

A biconditional states that two propositions have the same truth value.

Symbolically:

`P ↔ Q`

It is often read as:

`P if and only if Q`

A biconditional represents two implications:

- `P → Q`
- `Q → P`

Both directions must be established.

## Assumptions, Hypotheses, and Conclusions

Many mathematical statements have the form:

`If P, then Q`

The first part, `P`, is commonly called:

- the assumption
- the hypothesis
- the premise
- the antecedent

The second part, `Q`, is called:

- the conclusion
- the consequent

Consider the statement:

`If a and b are odd integers, then a + b is even.`

The assumptions are:

- `a` is an integer.
- `b` is an integer.
- `a` is odd.
- `b` is odd.

The conclusion is:

`a + b is even.`

A correct proof starts from the permitted assumptions and derives the conclusion. It must not silently assume facts that have not been justified.

The Python examples separate assumptions and conclusions explicitly and use logical implication to model the conditional statement.

## Definitions as Proof Tools

Definitions are central to mathematical proof.

Many direct proofs begin by replacing a mathematical term with its formal definition.

### Even Integers

An integer `n` is even if there exists an integer `k` such that:

`n = 2k`

### Odd Integers

An integer `n` is odd if there exists an integer `k` such that:

`n = 2k + 1`

### Divisibility

For integers `a` and `b`, with the usual nonzero divisor convention, `a` divides `b` when there exists an integer `k` such that:

`b = ak`

Definitions provide a bridge between an abstract property and algebraic manipulation.

For example, if `n` is even, a proof can write:

`n = 2k`

for some integer `k`.

The expression can then be substituted into the desired conclusion.

## Direct Proof

A direct proof establishes a conclusion by beginning with the assumptions and making a sequence of logically valid deductions.

The general structure is:

1. Assume the hypotheses.
2. Apply relevant definitions.
3. Use algebraic or logical rules.
4. Establish intermediate facts.
5. Derive the conclusion.

### Example: The Square of an Even Integer Is Even

The theorem states:

`If n is an even integer, then n² is even.`

Assume `n` is even.

By definition, there exists an integer `k` such that:

`n = 2k`

Square both sides:

`n² = (2k)²`

Therefore:

`n² = 4k²`

Rewrite this as:

`n² = 2(2k²)`

Since `2k²` is an integer, `n²` has the form `2m` for an integer `m`.

Therefore `n²` is even.

The essential feature of this proof is that `n` is arbitrary. The argument applies to every even integer because every even integer can be written as `2k`.

The Python script demonstrates the algebra for selected values while explicitly distinguishing these examples from the general proof.

## Direct Proof: Sum of Two Even Integers

The theorem is:

`The sum of two even integers is even.`

Assume:

`a = 2m`

and:

`b = 2n`

where `m` and `n` are integers.

Then:

`a + b = 2m + 2n`

Factor out `2`:

`a + b = 2(m + n)`

Because the sum of two integers is an integer, `m + n` is an integer.

Therefore `a + b` is even.

The script tests this relationship using positive, negative, and zero values.

## Direct Proof: Sum of Two Odd Integers

Suppose `a` and `b` are odd.

Then:

`a = 2m + 1`

and:

`b = 2n + 1`

Adding:

`a + b = 2m + 2n + 2`

Factor out `2`:

`a + b = 2(m + n + 1)`

The expression inside the parentheses is an integer.

Therefore the sum is even.

This example demonstrates how the formal definition of oddness produces a direct proof.

## Direct Proof: Product of Two Odd Integers

Suppose:

`a = 2m + 1`

and:

`b = 2n + 1`

Then:

`ab = (2m + 1)(2n + 1)`

Expanding:

`ab = 4mn + 2m + 2n + 1`

Factor the even terms:

`ab = 2(2mn + m + n) + 1`

The quantity inside the parentheses is an integer.

Therefore `ab` has the form:

`2k + 1`

for an integer `k`.

Thus `ab` is odd.

## Divisibility Proofs

Divisibility proofs often rely directly on the definition of divisibility.

Consider:

`If a divides b and b divides c, then a divides c.`

The assumption `a divides b` means:

`b = am`

for some integer `m`.

The assumption `b divides c` means:

`c = bn`

for some integer `n`.

Substitute the first equation into the second:

`c = (am)n`

Therefore:

`c = a(mn)`

Since the product of two integers is an integer, `mn` is an integer.

Thus `a` divides `c`.

The script implements a divisibility function and tests this property on selected integer triples.

## Universal Statements

A universal statement claims that every object in a specified domain satisfies a property.

Its general form is:

`For every x in D, P(x)`

A universal statement is strong because one failure is sufficient to disprove it.

For example:

`For every integer n, n² ≥ 0`

This statement is true.

A proof requires reasoning that applies to an arbitrary integer, not merely checking selected values.

Python can test:

`n² ≥ 0`

over a finite range such as `-10` through `10`.

Such testing confirms that the property holds for the tested values. It does not prove the statement for all integers because the set of integers is infinite.

## Existential Statements

An existential statement claims that at least one object satisfies a property.

Its form is:

`There exists x in D such that P(x)`

A single valid witness can establish an existential statement.

For example:

`There exists an integer n such that n² = 49.`

The integer `7` is a witness because:

`7² = 49`

The integer `-7` is also a witness.

The script implements a function that searches a finite domain for a witness satisfying a predicate.

A witness is valid only when:

- it belongs to the specified domain
- it satisfies the required property

## Counterexamples

A counterexample is an example that disproves a universal statement.

Suppose the claim is:

`Every prime number is odd.`

The number `2` is prime.

The number `2` is not odd.

Therefore `2` is a counterexample.

One counterexample is sufficient because a universal statement requires every element of the domain to satisfy the property.

The script includes a general counterexample search mechanism that searches for an element satisfying the assumptions while violating the conclusion.

For a statement of the form:

`If A(x), then B(x)`

a counterexample must satisfy:

- `A(x)` is true
- `B(x)` is false

An example where the assumption is false does not disprove the conditional.

## Finding Counterexamples

To disprove a universal statement:

`For every x, P(x)`

search for an object `x` such that:

`P(x)` is false.

For example, consider the false claim:

`For every integer n, n² > n`

Take `n = 0`.

Then:

`0² = 0`

The claim would require:

`0 > 0`

which is false.

Therefore `0` is a counterexample.

The value `1` is also a counterexample because:

`1² = 1`

and:

`1 > 1`

is false.

The script automatically searches a finite range for such counterexamples.

## Examples Are Not General Proofs

Testing examples is useful, but examples and proofs serve different purposes.

Examples can:

- illustrate a statement
- reveal patterns
- expose errors
- discover counterexamples
- check calculations

A finite number of successful examples does not prove a statement about infinitely many objects.

For example, testing the statement:

`n² ≥ n`

for `n = 1, 2, 3, ..., 10`

shows that the statement holds for those values.

This does not establish the result for every possible integer.

A mathematical proof must provide reasoning that applies to the entire intended domain.

## Reversing an Implication

A common mistake is to assume that the reverse of a true implication is automatically true.

Suppose:

`If n is divisible by 4, then n is even.`

This is true.

The converse is:

`If n is even, then n is divisible by 4.`

This is false.

The integer `2` is even but is not divisible by `4`.

Therefore `2` is a counterexample to the converse.

A proof of:

`P → Q`

does not automatically prove:

`Q → P`

These are separate statements.

## Converse, Inverse, and Contrapositive

For a conditional statement:

`P → Q`

the associated statements are:

### Converse

`Q → P`

### Inverse

`NOT P → NOT Q`

### Contrapositive

`NOT Q → NOT P`

The original statement and the contrapositive are logically equivalent.

The converse and inverse are logically equivalent to each other.

The original statement is not generally equivalent to the converse.

The script evaluates these forms using Boolean truth values.

## Contrapositive Reasoning

Sometimes a direct proof is difficult, but the contrapositive is easier.

To prove:

`P → Q`

one may instead prove:

`NOT Q → NOT P`

For example:

`If n is even, then n² is even.`

The contrapositive is:

`If n² is odd, then n is odd.`

Since a statement and its contrapositive are logically equivalent, proving either one establishes the other.

The script computationally compares the truth of a conditional and its contrapositive over selected integer values.

## Proof by Contradiction

Proof by contradiction begins by assuming that the desired statement is false.

The reasoning then derives a contradiction with a known fact, assumption, or logical principle.

The structure is:

1. State the claim to be proved.
2. Assume the claim is false.
3. Deduce consequences of that assumption.
4. Reach an impossibility or contradiction.
5. Conclude that the assumption of falsity was impossible.

A classical example is the proof that the square root of `2` is irrational.

The proof assumes that the square root of `2` can be expressed as a fraction in lowest terms.

Algebraic reasoning then shows that both the numerator and denominator must be even.

That contradicts the assumption that the fraction was in lowest terms.

Therefore the original assumption must be false.

The script uses a numerical approximation of the square root of `2` only to illustrate an important limitation: decimal approximation is not a proof of irrationality.

## Quantifiers and Proof Strategy

Quantifiers determine what kind of proof or disproof is required.

### Universal Quantifier

`For every x, P(x)`

To prove it, the argument must establish the property for arbitrary elements of the domain.

To disprove it, one valid counterexample is sufficient.

### Existential Quantifier

`There exists x such that P(x)`

To prove it, one valid witness is often sufficient.

To disprove it, one must establish that no object in the domain satisfies the property.

For infinite domains, disproving an existential statement usually requires a general argument.

Confusing universal and existential statements is a common source of incorrect reasoning.

## Edge Cases

An edge case is a boundary or exceptional value that may require special treatment.

Consider:

`n / n = 1`

This statement is true for nonzero `n`.

It is undefined when:

`n = 0`

A proof that divides by a variable or expression must establish that the divisor is nonzero.

The Python script raises an exception when attempting to divide zero by itself, demonstrating how computational validation can reflect mathematical domain restrictions.

Mathematical proofs must identify domain restrictions before applying operations.

## Domain Restrictions

Every statement has an intended domain.

Examples include:

- integers
- real numbers
- positive integers
- nonzero real numbers
- matrices of a specified size

A statement can change from true to false when its domain changes.

For example:

`Every nonzero real number divided by itself equals 1`

is true.

The statement:

`Every real number divided by itself equals 1`

is false because zero is included.

The script demonstrates domain validation with the real square root function, which requires a nonnegative input.

## Vacuous Truth

A conditional statement:

`P → Q`

is logically true whenever `P` is false.

This is called vacuous truth.

Consider:

`If an integer is both even and odd, then it is divisible by 100.`

Under ordinary parity definitions, no integer is both even and odd.

Therefore there is no integer for which the hypothesis is true and the conclusion is false.

The implication is therefore logically true for every integer.

Vacuous truth can seem counterintuitive because the conclusion may have no meaningful connection to the hypothesis in practice. It follows directly from the formal truth conditions for implication.

## Proof by Cases

Proof by cases divides a problem into cases that collectively cover every possibility.

For example, every integer is either:

- even
- odd

To prove that every integer square has a definite parity, consider both cases.

If `n` is even, then `n²` is even.

If `n` is odd, then `n²` is odd.

Because every integer belongs to one of these cases, the argument covers all integers.

A valid proof by cases requires:

- exhaustive cases
- correct reasoning within each case
- no unaddressed possibilities

The script demonstrates this principle using a parity-based conditional structure.

## Proof by Exhaustion

Proof by exhaustion checks every possibility in a genuinely finite domain.

For example, the last digit of an integer must be one of:

`0, 1, 2, 3, 4, 5, 6, 7, 8, 9`

There are only ten possible cases.

The script squares each possible final digit and verifies that the resulting final digit belongs to:

`0, 1, 4, 5, 6, 9`

Because all ten possibilities are checked, the finite analysis is exhaustive.

Proof by exhaustion is valid only when the domain has been completely covered.

Testing a large but finite sample of an infinite domain is not proof by exhaustion.

## Circular Reasoning

Circular reasoning occurs when the conclusion is assumed directly or indirectly as part of the argument intended to prove it.

An invalid pattern is:

1. Assume the conclusion.
2. Manipulate the conclusion.
3. State that the conclusion is true.

This does not establish the desired result.

A proof must begin from accepted assumptions and independently justified facts.

When debugging a proof, it is useful to ask:

- Where was the conclusion first introduced?
- Was it derived from the assumptions?
- Was an equivalent form of the conclusion silently assumed?

## Counterexample Search in Python

The script defines a general function for searching a finite domain for a counterexample to a conditional claim.

A conditional statement has the form:

`If assumption(x), then conclusion(x)`

A counterexample must satisfy:

`assumption(x) = True`

and:

`conclusion(x) = False`

The script represents this computationally as a search through a finite iterable.

This approach is useful for:

- testing proposed theorems
- finding simple counterexamples
- debugging conjectures
- validating finite-domain properties

The search result must be interpreted carefully. Failure to find a counterexample in a finite domain does not prove that no counterexample exists elsewhere.

## Testing Versus Proving

Computational testing and mathematical proof have different purposes.

### Computational Testing

Useful for:

- checking examples
- finding counterexamples
- discovering patterns
- validating implementations
- detecting arithmetic errors

### Mathematical Proof

Required to establish general claims over infinite or unrestricted domains.

A program may verify that:

`If n is even, then n² is even`

for every integer from `-1000` through `1000`.

This is strong evidence that the implementation behaves as expected.

It does not prove the theorem for all integers.

The mathematical proof works because every even integer, regardless of magnitude, can be represented as:

`n = 2k`

for an arbitrary integer `k`.

## Mathematical Claims as Software Objects

The script includes a `ConditionalClaim` class that represents statements of the form:

`If assumption(x), then conclusion(x)`

The class stores:

- a claim name
- an assumption predicate
- a conclusion predicate

It provides methods for:

- checking whether the conditional holds for a specific value
- searching for counterexamples in a finite domain

This design demonstrates the distinction between the logical structure of a mathematical statement and the computational process used to evaluate instances.

A formal proof system would require substantially more structure because it must verify derivations symbolically rather than merely evaluate examples.

## Assertion-Based Property Testing

The script uses Python assertions to check selected mathematical properties over finite ranges.

Examples include:

- even integers have even squares
- odd integers have odd squares
- the sum of two even integers is even

Assertions are useful for detecting implementation errors.

For example, if the `is_even` function were incorrectly implemented, finite-domain assertions could reveal the problem.

Assertions do not replace mathematical proofs. They validate the behavior of code on selected inputs.

## Common Mistakes in Mathematical Proof

### Checking Examples Only

A list of examples cannot prove a statement over an infinite domain.

### Assuming the Conclusion

A proof cannot use the desired conclusion as an unproved starting point.

### Reversing an Implication

From:

`P → Q`

it does not follow automatically that:

`Q → P`

### Ignoring the Domain

A theorem about positive integers cannot automatically be applied to all integers.

### Dividing by Zero

Before dividing by an expression, a proof must establish that the expression is nonzero.

### Invalid Counterexamples

A counterexample must belong to the stated domain and satisfy the hypothesis when disproving a conditional statement.

### Confusing Existential and Universal Claims

One witness may prove an existential statement, but one successful example does not prove a universal statement.

### Unjustified Integer Claims

When a proof introduces an expression such as:

`m + n`

it must rely on the fact that integers are closed under addition.

Similarly, products of integers remain integers.

These closure properties often complete direct proofs.

### Treating Approximation as Exact Proof

Numerical values, decimal expansions, and floating-point calculations are approximations unless exact mathematical reasoning establishes the required result.

## Implementation Considerations

When mathematical concepts are represented in Python, implementation details matter.

### Integer Arithmetic

Python integers have arbitrary precision, which makes them useful for many elementary number-theoretic examples.

### Floating-Point Arithmetic

Floating-point values are approximations and may introduce rounding errors.

A floating-point calculation should not be treated as exact proof of an algebraic identity without understanding numerical limitations.

### Input Validation

Mathematical functions should validate domain restrictions.

Examples include:

- preventing division by zero
- rejecting negative inputs for real square roots
- distinguishing valid divisors from zero

### Predicate Functions

The script uses functions such as:

- `is_even`
- `is_odd`
- `is_prime`
- `divides`

Predicate functions return Boolean values and correspond naturally to mathematical properties.

This makes logical relationships easier to represent and test.

## Performance Considerations

Most examples in the script use small finite ranges.

The computational cost of testing a property depends on:

- the size of the domain
- the complexity of the predicate
- the number of nested loops

The primality function, for example, tests possible divisors up to approximately the square root of the input.

Counterexample searches stop when the first counterexample is found, which can improve performance.

For mathematical exploration, finite testing should use ranges large enough to expose likely boundary cases without confusing computational coverage with proof.

## Security and Reliability Considerations

Although elementary proof exercises do not normally involve conventional security risks, reliable mathematical software still requires careful treatment of assumptions and inputs.

Potential reliability issues include:

- invalid domains
- division by zero
- integer versus floating-point interpretation
- overflow in languages with fixed-width integers
- incorrect assumptions about finite testing
- unvalidated user input

Python avoids ordinary fixed-width integer overflow for standard integers, but performance and memory usage can still become significant when extremely large values are used.

Reliable implementations should make domain restrictions explicit.

## Real-World Relevance

Proof fundamentals are relevant far beyond classroom mathematics.

They support reasoning in:

- algorithms
- computer science
- software verification
- cryptography
- data validation
- formal logic
- engineering
- scientific modeling

Direct proofs establish that a result follows from known assumptions.

Counterexamples identify false generalizations and expose missing conditions.

Case analysis ensures that all relevant possibilities are considered.

Contrapositive and contradiction provide alternative strategies when direct reasoning is difficult.

Computational testing complements proof by helping identify patterns, edge cases, and implementation errors.

The central principle remains the same: a mathematical conclusion must follow logically from clearly stated assumptions using valid reasoning.
