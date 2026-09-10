# Functions fundamentals

## Topic introduction

A function is a mathematical rule that assigns exactly one output to every permitted input. Functions are central to mathematics and computer science because they provide a precise way to describe dependence, transformation, calculation, lookup, and correspondence.

A function is commonly written as

    f : A -> B

where:

- `A` is the **domain**
- `B` is the **codomain**
- `f(x)` is the output associated with input `x`
- the **range**, or image, is the set of outputs that are actually produced

The Python study script develops these ideas from elementary definitions to finite-set classification, inverse functions, composition, cardinality, proof techniques, edge cases, computational implementation, and practical applications.

## The defining property of a function

A relation from a set `A` to a set `B` is a function if every element of `A` is assigned exactly one element of `B`.

The phrase **exactly one** contains two requirements:

1. Every domain element must have an output.
2. No domain element may have two different outputs.

For example,

    {(1, "a"), (2, "b"), (3, "b")}

is a function from `{1, 2, 3}` to `{"a", "b"}`.

Input `3` and input `2` may both produce `"b"`. That is allowed.

By contrast,

    {(1, "a"), (1, "b"), (2, "c")}

is not a function because input `1` has two different outputs.

Likewise,

    {(1, "a"), (2, "b")}

is not a function from `{1, 2, 3}` because input `3` has no output.

The script implements this definition directly with `is_function_relation()`.

## Relation and function

A **relation** is a set of ordered pairs. It does not necessarily satisfy the one-output-per-input rule.

Every function is therefore a relation, but not every relation is a function.

For a relation to define a function from `A` to `B`, each `x` in `A` must occur as the first coordinate of exactly one pair.

This distinction is fundamental because many mathematical relationships are relations without being functions in a particular direction.

For example, the relation describing the square relationship

    {(2, 4), (-2, 4)}

is a valid relation. It can be part of the function `f(x) = x²`, because each input has one output.

If the relation is reversed,

    {(4, 2), (4, -2)}

the input `4` has two different outputs. It therefore does not define a function from the output set back to the input set.

## Domain

The **domain** is the set of permitted inputs.

If

    f : A -> B

then `A` is the domain of `f`.

For example,

    f : {1, 2, 3} -> {a, b, c}

with

    f(1) = a
    f(2) = b
    f(3) = b

has domain

    {1, 2, 3}

The formula associated with a function does not necessarily determine the complete domain. The domain must be considered as part of the function's specification.

For example,

    f(x) = 1 / (x - 2)

cannot use `x = 2` when working over the real numbers because division by zero is undefined.

Its real-valued domain is therefore

    R \ {2}

Similarly,

    f(x) = sqrt(x - 3)

has real domain

    [3, infinity)

and

    f(x) = ln(x)

has real domain

    (0, infinity)

## Codomain

The **codomain** is the target set specified for the function.

For

    f : A -> B

the codomain is `B`.

The codomain is not automatically equal to the range.

Consider

    f : {1, 2, 3} -> {a, b, c, d}

with

    1 -> a
    2 -> b
    3 -> b

The range is

    {a, b}

while the codomain is

    {a, b, c, d}

The values `c` and `d` are permitted targets but are never produced.

This distinction is essential when defining a surjective function.

## Range

The **range** is the set of actual outputs.

For

    f : A -> B

the range is

    {f(x) : x in A}

The range is always a subset of the codomain.

If every codomain element is reached, the range equals the codomain. If at least one codomain element is not reached, the range is a proper subset of the codomain.

For a finite function, the script computes the range using the distinct values in the mapping.

## Function notation

The notation

    f : A -> B

states that `f` maps elements of `A` into elements of `B`.

If

    f(x) = 2x + 3

then:

    f(0) = 3
    f(2) = 7
    f(-1) = 1

The symbol `f` denotes the function. The expression `f(x)` denotes its value at the particular input `x`.

It is useful to distinguish the function itself from an individual function value.

## Mapping representation

Finite functions can be represented using ordered pairs, tables, mapping diagrams, dictionaries, or explicit rules.

For example,

    1 -> a
    2 -> b
    3 -> b

can be represented by the ordered-pair set

    {(1, a), (2, b), (3, b)}

The Python `FiniteFunction` class represents the same structure using a dictionary together with explicit domain and codomain sets.

This representation makes it possible to inspect:

- the domain
- the codomain
- the range
- individual function values
- preimages
- injectivity
- surjectivity
- bijectivity
- inverse functions

## Image and preimage

The **image** of a subset `S` of the domain is

    f(S) = {f(x) : x in S}

The image tells us which outputs are generated by the selected inputs.

The **preimage** of a subset `T` of the codomain is

    f⁻¹(T) = {x in A : f(x) belongs to T}

The preimage notation does not require an inverse function to exist.

For example, with

    f(x) = x²

the preimage of `{4}` over the real numbers is

    {-2, 2}

This is well-defined even though `f` does not have an inverse function on all of `R`.

The distinction between a preimage and an inverse function is important.

## Injective functions

A function `f : A -> B` is **injective**, or **one-to-one**, if distinct inputs always produce distinct outputs.

The formal definition is

    f(x₁) = f(x₂) implies x₁ = x₂

An equivalent statement is

    x₁ != x₂ implies f(x₁) != f(x₂)

An injective function never maps two different domain elements to the same output.

For example,

    f(x) = 2x + 1

is injective over the real numbers.

Suppose

    2x₁ + 1 = 2x₂ + 1

Then

    2x₁ = 2x₂

and therefore

    x₁ = x₂

so the function is injective.

By contrast,

    f(x) = x²

is not injective over the real numbers because

    f(2) = 4
    f(-2) = 4

while

    2 != -2

Injectivity is therefore a property of a function together with its domain, not merely of the formula.

## Surjective functions

A function `f : A -> B` is **surjective**, or **onto**, if every element of the codomain is reached by at least one domain element.

Formally,

    for every y in B, there exists x in A such that f(x) = y

The equivalent finite-set condition is

    range(f) = codomain(f)

Consider

    f : {1, 2, 3} -> {a, b}

with

    1 -> a
    2 -> b
    3 -> a

Both `a` and `b` are reached, so the function is surjective.

It is not injective because both `1` and `3` map to `a`.

## Bijective functions

A function is **bijective** when it is both injective and surjective.

For a bijection:

- every domain element has exactly one output
- every codomain element has at least one preimage
- injectivity ensures that no codomain element has more than one preimage

Consequently, every codomain element has exactly one preimage.

A bijection establishes a one-to-one correspondence between its domain and codomain.

For finite sets of equal size, the following are equivalent:

    injective
    surjective
    bijective

when referring to functions between those two equally sized finite sets.

## Preimages and the three classifications

The preimage of a codomain element provides a useful unified interpretation.

For an injective function, every codomain element has **at most one** preimage.

For a surjective function, every codomain element has **at least one** preimage.

For a bijective function, every codomain element has **exactly one** preimage.

A non-surjective function has at least one codomain element with no preimage.

A non-injective function has at least one codomain element with multiple preimages.

The script demonstrates this using its `fibers()` and `preimage_sizes()` functions.

## Inverse functions

A function has an inverse function when it is bijective between the relevant sets.

If

    f : A -> B

is bijective, then

    f⁻¹ : B -> A

satisfies

    f⁻¹(f(x)) = x

for every `x` in `A`, and

    f(f⁻¹(y)) = y

for every `y` in `B`.

The inverse reverses the original mapping.

If

    f(a) = b

then

    f⁻¹(b) = a

For example, if

    f(x) = 2x + 3

then

    f⁻¹(x) = (x - 3) / 2

The inverse function should not be confused with the reciprocal.

The reciprocal is

    1 / f(x)

whereas the inverse function is the function that reverses the original input-output relationship.

## Why non-bijective functions do not have ordinary inverse functions

Consider

    f(x) = x²

over the real numbers.

Both

    f(2) = 4

and

    f(-2) = 4

If the mapping were reversed, the input `4` would need to produce both `2` and `-2`.

That violates the definition of a function.

Therefore `x²` does not have an inverse function from `R` to `R`.

The problem can be solved by restricting the domain.

Consider

    f : [0, infinity) -> [0, infinity)

with

    f(x) = x²

Now the function is bijective, and its inverse is

    f⁻¹(x) = sqrt(x)

The domain restriction removes the duplicate negative inputs.

## Domain restrictions can change classification

The formula alone does not determine whether a function is injective or surjective.

Consider

    f(x) = x²

From `R` to `R`:

    not injective
    not surjective

From `R` to `[0, infinity)`:

    not injective
    surjective

From `[0, infinity)` to `[0, infinity)`:

    injective
    surjective
    bijective

Thus both domain and codomain matter.

This is one of the most important conceptual points in the topic.

## Function equality

Two functions are formally equal when their relevant structure and assignments agree.

For finite functions, this means:

- the domains are equal
- the codomains are equal
- the output assigned to every input is equal

For example, the rule

    f(x) = x²

can describe different functions depending on the declared codomain.

The functions

    f : R -> R

and

    g : R -> [0, infinity)

use the same formula but have different codomains. Their formal specifications are therefore different.

## Cardinality

The **cardinality** of a finite set is its number of elements.

If

    |A| = m
    |B| = n

then the number of all possible functions from `A` to `B` is

    n^m

Each domain element independently chooses one of the `n` codomain elements.

For example, from a two-element set to another two-element set:

    2² = 4

functions exist.

The number of injective functions from an `m`-element domain to an `n`-element codomain is

    n(n-1)(n-2)...(n-m+1)

when `m <= n`.

Equivalently,

    n! / (n-m)!

The number of bijections between two sets of size `n` is

    n!

The script implements these counting formulas and verifies them by exhaustive enumeration for small sets.

## Pigeonhole principle

The **pigeonhole principle** states that if more than `n` objects are placed into `n` boxes, at least one box must contain at least two objects.

For functions, if

    |A| > |B|

then every function from `A` to `B` must have a collision.

A collision means that distinct inputs produce the same output.

Therefore an injective function from a larger finite set into a smaller finite set cannot exist.

Conversely, if

    |A| < |B|

then a function from `A` to `B` cannot be surjective because there are not enough domain elements to reach every codomain element.

## Infinite sets

Finite-set intuition does not always transfer directly to infinite sets.

Consider

    f : N -> N
    f(n) = n + 1

where

    N = {0, 1, 2, 3, ...}

The function is injective because

    n₁ + 1 = n₂ + 1

implies

    n₁ = n₂

It is not surjective because `0` has no preimage.

This is possible even though both the domain and codomain are infinite sets with the same cardinality.

The finite theorem

    equal finite cardinalities + injectivity => surjectivity

should therefore not be applied to infinite sets without additional reasoning.

## Standard mathematical examples

### Identity function

The identity function on a set `A` is

    id_A(x) = x

It is always bijective from `A` to itself.

### Constant function

A constant function has the form

    f(x) = c

If the domain contains more than one element, it is not injective.

It is surjective only when the codomain consists solely of the value `c`.

### Linear function

A real-valued function

    f(x) = ax + b

with `a != 0` is bijective from `R` to `R`.

When `a = 0`, the function becomes constant and is neither injective nor surjective from `R` to `R`.

### Quadratic function

The function

    f(x) = x²

is neither injective nor surjective from `R` to `R`.

With appropriate domain and codomain restrictions, it can become bijective.

### Absolute value

The function

    f(x) = |x|

is surjective from `R` to `[0, infinity)` but is not injective on `R`.

### Cubic function

The function

    f(x) = x³

is bijective from `R` to `R`.

It is strictly increasing, which establishes injectivity, and every real value has a real cube root, which establishes surjectivity.

## Piecewise functions

A **piecewise function** uses different formulas on different parts of the domain.

For example,

    f(x) = x²       when x < 0
           x + 1    when x >= 0

is a valid function because every real input satisfies exactly one of the conditions.

A piecewise definition can fail to define a function if:

- an input satisfies no condition
- an input satisfies multiple conditions that produce different outputs

The conditions are therefore part of the mathematical definition.

## Graphical interpretation

The **vertical line test** determines whether a graph represents `y` as a function of `x`.

If a vertical line intersects a graph more than once, the graph does not define a function of `x`.

For example,

    y = x²

passes the vertical line test.

The relation

    x = y²

does not define `y` as a single-valued function of `x` over all nonnegative `x`, because a value such as `x = 4` corresponds to

    y = 2
    y = -2

The vertical line test is about whether a relation is a function.

The **horizontal line test** is associated with injectivity. If every horizontal line intersects the graph at most once, the function is injective.

## Algebraic test for injectivity

A standard proof begins by assuming

    f(x₁) = f(x₂)

and then showing

    x₁ = x₂

For a linear function,

    f(x) = ax + b

with `a != 0`:

    ax₁ + b = ax₂ + b
    ax₁ = ax₂
    x₁ = x₂

Therefore the function is injective.

For

    f(x) = x²

the equation

    x₁² = x₂²

gives

    (x₁ - x₂)(x₁ + x₂) = 0

Therefore either

    x₁ = x₂

or

    x₁ = -x₂

The second possibility prevents injectivity on domains containing both positive and negative versions of the same number.

## Monotonicity and injectivity

A strictly increasing function on an interval is injective.

A strictly decreasing function on an interval is also injective.

For a strictly increasing function,

    x₁ < x₂

implies

    f(x₁) < f(x₂)

so two different inputs cannot produce the same output.

Strictness matters. A non-strictly increasing function can have a flat region and therefore fail to be injective.

## Algebraic test for surjectivity

To prove that

    f : A -> B

is surjective, select an arbitrary `y` in the codomain and solve

    y = f(x)

for `x`.

The resulting value must belong to the domain.

For

    f(x) = 2x + 3

from `R` to `R`:

    y = 2x + 3
    x = (y - 3) / 2

Every real `y` produces a real `x`, so the function is surjective.

For

    f(x) = x²

from `R` to `R`, negative values of `y` cannot be reached. Therefore the function is not surjective.

## Composition

If

    f : A -> B

and

    g : B -> C

then the composition

    g o f : A -> C

is defined by

    (g o f)(x) = g(f(x))

The order matters.

For example,

    f(x) = x + 1
    g(x) = 2x

gives

    (g o f)(x) = 2x + 2

while

    (f o g)(x) = 2x + 1

Therefore composition is generally not commutative.

The Python script implements both ordinary callable composition and finite-function composition.

## Composition and injectivity

If `f` and `g` are injective and their domains and codomains are compatible, then

    g o f

is injective.

Suppose

    g(f(x₁)) = g(f(x₂))

Since `g` is injective,

    f(x₁) = f(x₂)

Since `f` is injective,

    x₁ = x₂

Therefore the composition is injective.

## Composition and surjectivity

If `f` and `g` are both surjective, then

    g o f

is surjective.

For every `c` in the codomain of `g`, surjectivity of `g` gives a value `b` such that

    g(b) = c

Surjectivity of `f` then gives an `a` such that

    f(a) = b

Therefore

    g(f(a)) = c

and every element of the final codomain is reached.

## Composition of bijections

The composition of two bijections is itself a bijection.

If

    f : A -> B

and

    g : B -> C

are bijective, then

    g o f : A -> C

is bijective.

The inverse satisfies

    (g o f)⁻¹ = f⁻¹ o g⁻¹

The order reverses because the operations must be undone in reverse order.

The script verifies this relationship using finite mappings.

## Restriction

A **restriction** keeps the same rule while reducing the domain.

If `f` is defined on `A` and `S` is a subset of `A`, the restriction `f|S` has domain `S` and satisfies

    f|S(x) = f(x)

for every `x` in `S`.

Restrictions can change injectivity.

The function

    f(x) = x²

is not injective on `R`, but its restriction to `[0, infinity)` is injective.

Restrictions can also affect surjectivity depending on the codomain.

## Extension

An **extension** enlarges the domain while preserving existing values.

If `f` is defined on `S` and `g` is defined on a larger set `T`, where

    S subset T

then `g` extends `f` when

    g(x) = f(x)

for every `x` in `S`.

An extension can change injectivity because newly added inputs may produce outputs already used by existing inputs.

## Function versus inverse relation

A function can have well-defined preimages without having an inverse function.

For

    f(x) = x²

the preimage of `4` is

    {-2, 2}

The preimage is a set containing two inputs.

An inverse function would require a single output for the input `4`, so an inverse function does not exist on the unrestricted real domain.

This distinction is especially important when interpreting the notation `f⁻¹`.

## Edge case: empty domain

The empty function

    f : empty_set -> B

is a valid function for every codomain `B`.

There are no domain elements for which the function rule could fail.

The empty function is injective.

It is surjective only when the codomain is also empty.

Therefore

    empty_set -> empty_set

is bijective.

These cases demonstrate why formal definitions are preferable to informal intuition.

## Edge case: singleton sets

If

    A = {a}
    B = {b}

then the only possible function is

    a -> b

It is automatically injective and surjective, and therefore bijective.

A function from a nonempty singleton domain to a larger codomain is injective but not surjective.

A function from a larger nonempty domain to a singleton codomain is surjective but not injective.

## Domain validation in programming

A mathematical function is only defined on its domain.

A programming implementation should therefore enforce domain conditions where appropriate.

For example, division by zero is undefined:

    f(x) = 1/x

The script's `reciprocal_shifted()` function explicitly rejects `x = 2` for the related expression `1/(x-2)`.

This is an example of preserving a mathematical domain contract in software.

## Codomain validation in programming

A finite function implementation can validate that every output belongs to its declared codomain.

For example,

    f : {1,2} -> {a,b}

cannot legitimately assign

    f(1) = c

because `c` is outside the codomain.

The `FiniteFunction` class checks this during construction.

This is useful because inconsistent mathematical specifications can be detected immediately rather than during later classification.

## Computational representation

The script defines a generic `FiniteFunction` class containing:

- `mapping`
- `domain`
- `codomain`

It provides methods for:

- evaluating the function
- obtaining the range
- obtaining the graph
- testing injectivity
- testing surjectivity
- testing bijectivity
- finding preimages
- constructing an inverse

The class uses Python dictionaries and sets because these structures provide a natural representation for finite functions.

Dictionary keys and set members must be hashable in Python. This is a programming implementation constraint, not a restriction imposed by the mathematical definition of a function.

## Finite injectivity testing

The script demonstrates two approaches.

A direct definition-based approach compares every pair of distinct inputs.

For `n` inputs, this requires approximately

    O(n²)

comparisons.

A faster approach stores observed outputs in a set. If an output appears again, injectivity fails.

The expected complexity is

    O(n)

for hashable outputs.

The direct implementation is valuable for understanding the definition, while the set-based implementation is preferable for larger finite datasets.

## Finite surjectivity testing

For finite functions, surjectivity can be checked by computing the range and comparing it with the codomain:

    range == codomain

With hash-based sets, this can generally be performed in expected linear time in the number of mappings.

## Numerical considerations

Computational equality and mathematical equality are not always identical when floating-point arithmetic is involved.

Mathematical reasoning may establish exact equality, while floating-point computation may introduce small representation errors.

For exact educational examples, integer values, strings, and rational numbers represented by `Fraction` are useful.

Sampling numerical points can discover counterexamples, but sampling alone generally cannot prove a universal property over an infinite domain.

## Proof versus computation

The script deliberately uses computation to illustrate mathematical ideas, but computational experiments and mathematical proofs have different roles.

A finite exhaustive test can completely classify a finite function.

For an infinite domain, testing many values cannot generally prove that a function is injective or surjective.

For example, testing `x²` at many points can reveal collisions, but a mathematical proof explains why collisions necessarily occur for the entire relevant domain.

Similarly, checking a few outputs cannot establish surjectivity over an infinite codomain.

## Counterexamples

Counterexamples are especially powerful for disproving universal claims.

To disprove injectivity, find two distinct inputs such that

    x₁ != x₂

but

    f(x₁) = f(x₂)

For example,

    f(-2) = f(2) = 4

disproves injectivity of `x²` over a domain containing both `-2` and `2`.

To disprove surjectivity, identify a codomain element that has no preimage.

For `x² : R -> R`, any negative real number is such a counterexample.

## One-to-one, many-to-one, and one-to-many

**One-to-one** generally refers to injectivity.

**Many-to-one** describes a valid function in which multiple inputs can share an output.

For example,

    1 -> a
    2 -> a
    3 -> b

is many-to-one.

**One-to-many** is not a function in the usual direction because one input would have multiple outputs.

A one-to-many relationship can still be a valid relation, but it is not a function from the first set to the second.

## Into and onto

The term **onto** means surjective.

A function is onto when every codomain element is reached.

The term **into** is sometimes used informally for a function whose range is a proper subset of its codomain.

For precise work, it is better to state the actual properties:

- injective
- surjective
- bijective
- neither

rather than relying on potentially ambiguous terminology.

## Real-world applications

Functions are widely used to model real systems.

### Lookup systems

A mapping such as

    employee -> employee_id

can be treated as a function when every employee has exactly one selected identifier.

If distinct employees must have distinct identifiers, the mapping should be injective.

### Pricing systems

A product code can map to a selected price:

    product_code -> price

The exact interpretation depends on the system's rules, including whether multiple prices can exist for different contexts.

### Student records

A mapping such as

    student_id -> grade

can be a function when the assessment and grading context are fixed.

### Unit conversion

A conversion such as

    meters -> centimeters

is naturally modeled as a function on a specified numerical domain.

### Coordinate transformations

A coordinate transformation can be represented as a function from one coordinate space to another.

Bijectivity is especially useful when a transformation must be reversible.

### Encryption and reversible transformations

Reversible transformations are naturally associated with bijections because every valid output must uniquely identify the original input.

Real cryptographic systems contain many additional requirements beyond mathematical bijectivity, so a proof of bijectivity alone does not establish security.

### Hash functions

A hash function typically maps a large input space into a smaller fixed-size output space.

If there are more possible inputs than possible outputs, the pigeonhole principle guarantees collisions.

Therefore a general fixed-size hash function cannot be mathematically injective over an unlimited input space.

Security of cryptographic hashes instead depends on computational properties such as the difficulty of finding useful collisions.

### Database identifiers

A mapping from records to unique identifiers can be viewed as injective when distinct records must receive distinct identifiers.

This provides a useful mathematical interpretation of uniqueness constraints.

## Security considerations

Function theory provides useful abstractions for security, but mathematical properties should not be confused with complete security guarantees.

Injectivity can matter when distinct objects must remain distinguishable.

Surjectivity matters when every valid target must be reachable.

Bijectivity is particularly important for reversible transformations.

Hash functions are intentionally many-to-one when their input space is larger than their output space. Their security depends on computational hardness rather than mathematical injectivity.

Domain validation is also important in software. Inputs outside a mathematically valid domain can cause undefined operations, unexpected behavior, or security vulnerabilities when validation is incomplete.

## Common mistakes

### Confusing range and codomain

The range is the set of actual outputs.

The codomain is the declared target set.

They are equal only for a surjective function.

### Assuming a formula has only one classification

Classification depends on the domain and codomain.

The formula

    x²

can represent a non-surjective function, a surjective function, or a bijection depending on the specified sets.

### Assuming every function has an inverse

Only bijective functions have inverse functions on their full specified domain and codomain.

### Confusing inverse and reciprocal

The inverse function reverses input-output assignments.

The reciprocal is `1/f(x)`.

They are different concepts.

### Treating a relation as a function

A relation fails to be a function if an input has zero outputs or multiple distinct outputs.

### Using finite intuition for infinite sets

For finite sets of equal cardinality, injectivity and surjectivity are equivalent.

For infinite sets, this equivalence cannot be assumed.

### Ignoring domain restrictions

Expressions involving division, square roots, logarithms, and other restricted operations require appropriate domains.

### Treating numerical sampling as proof

Testing many values may provide evidence but cannot generally prove a property over an infinite domain.

## Proof strategies

### Proving injectivity

Start with

    f(x₁) = f(x₂)

and derive

    x₁ = x₂

for arbitrary domain elements.

### Proving surjectivity

Start with an arbitrary codomain value `y`.

Solve

    y = f(x)

and show that the resulting `x` belongs to the domain.

### Proving bijectivity

Prove both injectivity and surjectivity.

Another method is to construct a two-sided inverse.

### Disproving injectivity

Find one collision:

    x₁ != x₂
    f(x₁) = f(x₂)

### Disproving surjectivity

Find one codomain element that has no preimage.

## Function fibers

For an output `y`, its **fiber** or preimage is

    f⁻¹({y})

The fibers of a function partition the domain according to equal output values.

For an injective function, every nonempty fiber contains exactly one element.

For a many-to-one function, some fibers contain multiple elements.

For a surjective function, every codomain fiber is nonempty.

For a bijection, every codomain fiber contains exactly one domain element.

This provides a unified interpretation of the three main classifications.

## Mathematical and programming functions

A pure programming function resembles a mathematical function when the same explicit input always produces the same output and there are no relevant external side effects.

For example,

    square(5) = 25

is straightforwardly modeled as a mathematical function.

Programming functions can also:

- modify global state
- read files
- access networks
- use randomness
- depend on time
- mutate objects
- print output

Such operations introduce behavior beyond a pure mathematical input-output mapping.

The distinction is important when applying mathematical function concepts to software design.

## Function composition in software

Composition also has a direct programming interpretation.

If one operation produces the input expected by another operation, the functions can be composed:

    final(x) = third(second(first(x)))

This is a function pipeline.

Clear domain and codomain specifications help ensure that each stage receives an appropriate input.

## Design considerations

When specifying a function, the following questions should be explicit:

1. What are the valid inputs?
2. What outputs are allowed?
3. Does every input produce exactly one output?
4. What is the actual range?
5. Are distinct inputs required to remain distinct?
6. Must every target output be reachable?
7. Does the transformation need to be reversible?
8. Are there undefined inputs?
9. Are numerical approximations involved?
10. Does the implementation preserve the mathematical specification?

These questions prevent many classification and implementation errors.

## The finite-function implementation

The Python script provides a complete `FiniteFunction` abstraction.

Its constructor validates:

- equality between mapping keys and domain
- membership of every output in the codomain

Its methods implement:

- evaluation
- range calculation
- graph generation
- injectivity testing
- surjectivity testing
- bijectivity testing
- preimage calculation
- inverse construction

The script also contains functions for:

- relation validation
- finite function generation
- counting all functions
- counting injections
- counting surjections
- counting bijections
- composition
- restriction
- diagnostic reporting
- counterexample discovery
- fast injectivity checking
- automated assertions

## Counting functions

For finite sets `A` and `B` with

    |A| = m
    |B| = n

there are

    n^m

functions from `A` to `B`.

If `m <= n`, the number of injective functions is

    n! / (n-m)!

If `m = n`, the number of bijections is

    n!

The number of surjective functions from an `m`-element set onto an `n`-element set can be calculated by inclusion-exclusion:

    sum from k=0 to n of
    (-1)^k C(n,k)(n-k)^m

when `m >= n`.

The script implements the binomial coefficient and surjection formula and also generates small finite functions exhaustively to verify the counts.

## Important relationships

Several relationships connect the main concepts.

For any function:

    range is a subset of codomain

For injectivity:

    every output has at most one preimage

For surjectivity:

    every codomain element has at least one preimage

For bijectivity:

    every codomain element has exactly one preimage

For finite sets:

    |A| > |B|
    => no injection A -> B

    |A| < |B|
    => no surjection A -> B

For finite sets of equal size:

    injection <=> surjection <=> bijection

For bijections:

    an inverse function exists

For compositions:

    injective + injective => injective composition

    surjective + surjective => surjective composition

    bijective + bijective => bijective composition

For inverse composition:

    (g o f)⁻¹ = f⁻¹ o g⁻¹

## Practical classification procedure

For a finite mapping, the classification process can be performed systematically.

First, verify that every domain element has exactly one output.

Second, verify that all outputs belong to the codomain.

Third, calculate the range.

Fourth, inspect whether any output occurs more than once.

If no output is repeated, the function is injective.

Fifth, compare the range with the codomain.

If they are equal, the function is surjective.

If both conditions hold, the function is bijective.

If the function is bijective, an inverse function can be constructed by reversing every mapping pair.

## Edge-case significance

The empty set and singleton sets are not merely technical curiosities. They demonstrate that formal definitions must be applied consistently.

The empty function is injective because there are no two distinct domain elements that could violate injectivity.

The empty function from the empty set to a nonempty codomain is not surjective because its range is empty.

The unique function from a singleton to a singleton is bijective.

These examples help clarify why logical definitions are more reliable than informal descriptions.

## Real-world relevance

The concepts in the script provide a mathematical foundation for understanding:

- data mappings
- lookup tables
- identifiers
- database uniqueness
- reversible transformations
- coordinate transformations
- unit conversions
- hashing and collisions
- input validation
- software function composition
- deterministic computations
- transformation pipelines
- mathematical modeling

The most important principle is that a function is not determined only by its formula. A complete function specification includes its domain, codomain, and assignment rule. Injectivity and surjectivity must therefore always be interpreted relative to the sets between which the function is defined.
