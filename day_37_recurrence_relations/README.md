# Recurrence Relations: Linear, Homogeneous, and Non-Homogeneous Recurrences

## Topic Scope

A recurrence relation defines a sequence by relating a term to one or more preceding terms. The central distinction in this implementation set is between the structure of a **linear recurrence**, the special case of a **homogeneous recurrence**, and the broader class of **non-homogeneous recurrences**.

A linear recurrence of order `k` can be written as

`a_n = c_1 a_(n-1) + c_2 a_(n-2) + ... + c_k a_(n-k) + f(n)`

where the coefficients `c_1, ..., c_k` do not depend on the sequence values and `f(n)` is an external forcing term.

When `f(n) = 0`, the recurrence is homogeneous:

`a_n = c_1 a_(n-1) + ... + c_k a_(n-k)`

When `f(n)` is not identically zero, the recurrence is non-homogeneous:

`a_n = c_1 a_(n-1) + ... + c_k a_(n-k) + f(n)`

The distinction is mathematical rather than merely terminological. The homogeneous recurrence is governed entirely by its previous sequence values. A non-homogeneous recurrence contains an additional contribution that must be modeled separately.

The six artifacts use different computational perspectives to make these distinctions explicit.

## Core Mathematical Structure

A recurrence is not completely specified by its recurrence equation alone. Initial conditions are required to determine a particular sequence.

For an order-two recurrence such as

`a_n = 3a_(n-1) - 2a_(n-2)`

two initial values are required, such as `a_0 = 1` and `a_1 = 3`.

For an order-three recurrence, three initial values are required. In general, an order-`k` recurrence requires `k` initial terms.

The Python, JavaScript, C++, and Java implementations therefore validate that the number of initial terms equals the recurrence order. The SQL implementation represents initial terms separately from recurrence coefficients so that the database can inspect and validate the mathematical definition.

## Linear Recurrences

Linearity means that previous sequence terms occur only to the first power and are multiplied by fixed coefficients. Terms such as `a_(n-1)^2`, `a_(n-1) * a_(n-2)`, or `sin(a_(n-1))` would make the recurrence nonlinear.

A first-order linear recurrence can have the form

`a_n = 2a_(n-1) + 5`.

A second-order linear recurrence can have the form

`a_n = a_(n-1) + a_(n-2)`.

Higher-order recurrences extend the same structure by adding more historical terms.

The implementation uses coefficient arrays ordered by lag. For example, `[3, -2]` represents

`a_n = 3a_(n-1) - 2a_(n-2)`.

This representation is useful computationally because the same recurrence engine can process first-order, second-order, or higher-order linear recurrences without changing the evaluation algorithm.

## Homogeneous Recurrences

A homogeneous linear recurrence contains no independent forcing term.

The Fibonacci recurrence is the canonical example:

`F_n = F_(n-1) + F_(n-2)`

with `F_0 = 0` and `F_1 = 1`.

The recurrence is homogeneous because the right-hand side consists entirely of previous Fibonacci values.

The Python implementation represents this with `forcing=lambda n: 0`. The JavaScript implementation uses a default zero forcing function. The C++ and Java implementations also explicitly pass zero forcing for homogeneous models.

This design is intentional. The zero forcing function is not merely an implementation convenience. It makes the difference between the mathematical recurrence coefficients and an external contribution explicit.

## Characteristic Equation

For a homogeneous linear recurrence, an important analytical technique is the characteristic equation.

Consider

`a_n = 3a_(n-1) - 2a_(n-2)`.

Assume a solution of the form

`a_n = r^n`.

Substitution gives

`r^n = 3r^(n-1) - 2r^(n-2)`.

Dividing by `r^(n-2)` gives

`r^2 - 3r + 2 = 0`.

The characteristic polynomial factors as

`(r - 1)(r - 2) = 0`.

The roots are therefore `1` and `2`.

Because the roots are distinct, the general homogeneous solution has the form

`a_n = A(1^n) + B(2^n)`.

The constants `A` and `B` are determined from the initial conditions.

The Python implementation includes exact rational arithmetic for this common second-order case. The C++ and Java implementations demonstrate the same characteristic-equation reasoning while using companion matrices for actual term evaluation.

## Repeated and Complex Roots

Characteristic roots do not always consist of distinct real values.

If a second-order recurrence has a repeated root `r`, the homogeneous solution takes the form

`a_n = (A + Bn)r^n`.

For higher-order recurrences, a root with multiplicity `m` introduces polynomial factors up to degree `m - 1`.

Complex roots can occur as conjugate pairs when the recurrence has real coefficients. Such roots can be expressed in polar form, producing oscillatory sequence behavior.

The executable implementations concentrate on recurrence evaluation and the distinct-root second-order case rather than pretending that a small custom root solver is a complete symbolic algebra system. The matrix method remains valid without requiring explicit characteristic-root calculation.

## Non-Homogeneous Recurrences

A non-homogeneous recurrence adds an independent forcing term.

For example:

`a_n = 2a_(n-1) + n`.

The term `n` is not another historical sequence value. It represents an external contribution that changes with the index.

Other forcing functions can include constants, exponentials, periodic values, polynomial expressions, or externally measured quantities.

The Python implementation demonstrates:

`a_n = 2a_(n-1) + n`

`a_n = 2a_(n-1) + 5`

and

`a_n = 2a_(n-1) + 2^n`.

The JavaScript implementation uses a non-homogeneous demand model in which a seasonal adjustment is added after the historical contribution has been calculated.

The C++ and Java implementations use a distribution-demand scenario. A campaign effect is represented separately from historical demand:

`D_n = D_(n-1) + D_(n-2) + campaign(n)`.

This is a useful modeling distinction because the campaign contribution is not another recurrence coefficient.

## Homogeneous and Particular Components

A non-homogeneous linear recurrence is commonly analyzed as the combination of a homogeneous solution and a particular solution.

The structure is

`general solution = homogeneous solution + particular solution`.

The homogeneous component satisfies the associated equation obtained by setting the forcing term to zero.

For

`a_n = 2a_(n-1) + n`,

the associated homogeneous equation is

`a_n = 2a_(n-1)`.

A particular solution is then chosen to account for the `n` forcing term.

The implementation set emphasizes this relationship computationally by keeping the forcing function separate. That representation is useful even when a closed-form particular solution is not calculated.

## Direct Iterative Evaluation

The simplest general-purpose evaluation strategy is forward iteration.

Given the initial terms, calculate the next term from the previous `k` terms and continue until the requested index is reached.

For fixed recurrence order `k`, generating the first `n` terms requires approximately `O(nk)` arithmetic operations.

This is the primary general-purpose strategy in the Python, JavaScript, C++, and Java implementations because it supports arbitrary forcing functions without requiring a symbolic transformation.

It also has a practical advantage: every generated value can be validated immediately.

## Recursive Evaluation and Memoization

The Fibonacci recurrence naturally leads to a recursive implementation:

`F_n = F_(n-1) + F_(n-2)`.

A naive recursive function repeatedly evaluates the same subproblems. For example, calculating `F_5` requires `F_3` and `F_4`, while `F_4` independently calculates `F_3` again.

This causes exponential growth in the number of recursive calls.

Memoization stores already calculated terms. Each sequence position is calculated once, reducing the work for a Fibonacci-style progression to linear time through the requested index.

The Python implementation includes naive recursion, memoization, and iterative evaluation to make this computational distinction concrete.

The JavaScript implementation uses a `Map` as the memoization cache.

## Companion Matrices

A homogeneous order-`k` recurrence can be transformed into a first-order vector recurrence.

For

`a_n = c_1a_(n-1) + c_2a_(n-2) + ... + c_ka_(n-k)`,

define a state vector containing the current term and required historical terms.

For a second-order recurrence:

`[a_n, a_(n-1)]^T`

can be obtained from the previous state using a companion matrix.

For

`a_n = c_1a_(n-1) + c_2a_(n-2)`,

the transition matrix is

`[[c_1, c_2], [1, 0]]`.

Repeated application becomes matrix exponentiation.

The Python, JavaScript, C++, and Java implementations contain companion-matrix machinery. This gives a common mathematical mechanism while allowing each programming language to express it differently.

## Fast Exponentiation

Computing a matrix raised to a large power does not require multiplying the matrix by itself once for every exponent value.

Binary exponentiation repeatedly squares the current matrix and uses only the powers corresponding to set bits in the exponent.

This reduces the number of matrix-power stages from linear in the exponent to logarithmic in the exponent.

For fixed recurrence order, the recurrence can therefore be evaluated through a matrix power using `O(log n)` matrix multiplications. The actual arithmetic cost depends on matrix dimension and the size of the resulting numbers.

This distinction is particularly important for very large indices.

## Exact Arithmetic and Numeric Limits

Recurrence sequences can grow rapidly.

Fibonacci values grow exponentially, so ordinary fixed-width integer types eventually overflow. Java's `long` and C++'s `long long` have finite ranges. JavaScript's `Number` is an IEEE-754 floating-point type and cannot represent every integer exactly beyond its safe integer range.

The JavaScript implementation therefore includes a `BigInt` Fibonacci evaluator for exact large integer values.

The Python implementation naturally benefits from arbitrary-precision integers.

The C++ and Java demonstrations explicitly detect or discuss arithmetic limits. The Java implementation uses `Math.addExact` and `Math.multiplyExact` so integer overflow becomes a controlled domain exception rather than silently producing an incorrect value.

## Sequence Validation

A recurrence can be used as a consistency rule for observed data.

Suppose the proposed rule is

`a_n = a_(n-1) + a_(n-2)`.

An observed sequence can be checked by calculating the expected value at every position after the initial conditions.

The Python implementation returns explicit mismatches containing the index, expected value, and observed value.

JavaScript returns mismatch objects.

The C++ implementation reports the first invalid position.

Java exposes validation as a service operation.

This distinction matters in practical systems because recurrence evaluation predicts values, while recurrence validation tests whether observed values conform to the mathematical model.

## Practical Demand Model

The C++, Java, Python, and JavaScript artifacts use recurrence relations to represent demand or population-style evolution.

A homogeneous model might represent purely historical dependence:

`D_n = D_(n-1) + D_(n-2)`.

A non-homogeneous model can represent an external campaign:

`D_n = D_(n-1) + D_(n-2) + campaign(n)`.

The historical coefficients describe how previous periods influence the next value. The forcing function describes a separate external effect.

That separation prevents a campaign adjustment from being incorrectly interpreted as a permanent change to the historical recurrence coefficients.

## Python Implementation

The Python program provides the broadest mathematical laboratory.

`LinearRecurrence` is a reusable representation of a recurrence definition. It stores coefficients, initial terms, and a forcing function.

`generate()` performs direct evaluation and supports both homogeneous and non-homogeneous equations.

The script also contains memoized Fibonacci evaluation, companion-matrix exponentiation, a second-order characteristic-root calculation using `Fraction`, sequence validation, a population model, and a reusable `RecurrenceEngine`.

The population model demonstrates a non-homogeneous recurrence whose external adjustment depends on the period.

The implementation deliberately avoids third-party dependencies so that the mathematical mechanisms can be inspected and executed directly.

## JavaScript Implementation

The JavaScript program approaches recurrence processing through Node.js-oriented mechanisms.

`LinearRecurrence` provides the mathematical model, while `RecurrenceMonitor` introduces an event-driven processing layer.

Events such as `started`, `term`, `completed`, and `failure` allow recurrence evaluation to be observed without embedding monitoring logic directly inside the mathematical definition.

The implementation also demonstrates memoization through `Map`, exact large Fibonacci values through `BigInt`, companion matrices, characteristic roots, sequence validation, and asynchronous processing.

The asynchronous demand example illustrates an important distinction: asynchronous application behavior does not alter the recurrence mathematics. It changes how data or computation can be integrated into an application.

## C++ Case Study

The C++ program presents a distribution-center demand model.

`RecurrenceModel` owns the coefficients and initial conditions and provides direct recurrence evaluation.

The forcing function is passed independently. This allows the same recurrence coefficients to represent a homogeneous model when the forcing function returns zero and a non-homogeneous model when an external campaign adjustment is supplied.

The case study validates both generated and deliberately corrupted sequences.

The companion-matrix implementation provides fast homogeneous evaluation. The program also performs domain validation to reject negative demand values and uses exceptions for malformed recurrence definitions and invalid matrix operations.

The implementation uses C++17 standard-library facilities only.

## Java Enterprise Model

The Java program separates mathematical data from domain services.

`RecurrenceDefinition` is an immutable record containing coefficients, initial terms, and the forcing function.

`RecurrenceType` explicitly distinguishes homogeneous and non-homogeneous models.

`RecurrenceService` performs generation, validation, and homogeneous nth-term evaluation.

The service also uses checked arithmetic operations such as `Math.addExact` and `Math.multiplyExact` so overflow becomes an explicit failure state.

The demand-forecast scenario models historical demand plus campaign effects. The Java structure demonstrates how recurrence rules can become explicit domain objects rather than being scattered through conditional statements.

## SQL Data Model

The PostgreSQL implementation stores recurrence information relationally.

`recurrence_definition` identifies the recurrence and records its order and type.

`recurrence_coefficient` stores each coefficient by lag.

`recurrence_initial_term` stores the initial conditions required to start the sequence.

`recurrence_forcing` stores external contributions independently from recurrence coefficients.

`generated_term` stores calculated sequence values.

This separation is important because a forcing term has a different mathematical role from a historical coefficient.

Primary keys prevent duplicate coefficients, initial terms, forcing values, and generated values for the same recurrence and index. Foreign keys maintain relationships between definitions and their components. Check constraints reject invalid orders, lags, and negative indexes.

## Recursive SQL Evaluation

PostgreSQL recursive common table expressions are used to calculate sequence values inside the database.

For Fibonacci-style evaluation, the recursive state contains the previous two values. Each recursive step shifts the state and calculates the next value.

The non-homogeneous examples explicitly add the forcing term to the historical recurrence result.

This demonstrates that recurrence relations can be implemented inside a relational database when sequence generation is part of a data-processing workflow.

## Database-Level Validation

The SQL script uses window functions such as `LAG` to expose previous sequence values.

For a second-order recurrence, the database can compare the stored current value with the value predicted from the two preceding values plus the appropriate forcing contribution.

This makes the database capable of identifying an invalid generated term without depending entirely on application-level validation.

The script also includes a transaction that inserts an intentionally inconsistent generated value and then rolls the transaction back.

## Performance Considerations

For direct generation, the dominant factor is the number of requested terms multiplied by recurrence order.

For a fixed-order recurrence, direct iteration is efficient when many consecutive terms are needed.

Memoization is useful when recursive evaluation repeatedly requests overlapping subproblems.

Matrix exponentiation is useful when the recurrence is homogeneous and a distant individual term is required. Its logarithmic exponentiation depth is particularly valuable for large indices.

Closed forms can be computationally attractive, but floating-point implementations can lose precision. A mathematically simple formula is not automatically a numerically reliable implementation.

For rapidly growing integer sequences, arbitrary-precision arithmetic may dominate execution time regardless of the recurrence algorithm.

## Common Modeling Errors

A recurrence equation without enough initial conditions is incomplete. An order-two recurrence requires two initial values.

A forcing term should not be confused with another recurrence coefficient. In

`a_n = 2a_(n-1) + n`,

the `2` describes dependence on the previous sequence value, while `n` is an external contribution.

Changing the initial conditions changes the particular sequence even when the recurrence coefficients remain identical.

A sequence that approximately follows a recurrence may still fail exact validation because of measurement noise or rounding.

Floating-point recurrence evaluation can accumulate numerical error, particularly when terms grow rapidly or when large values are repeatedly added and multiplied.

## Failure Conditions

The implementations explicitly reject malformed recurrence definitions, mismatched coefficient and initial-term counts, negative indexes, invalid sequence lengths, incompatible matrices, and invalid generated domain values.

The Java implementation additionally treats integer overflow as an explicit error.

The JavaScript implementation checks finite numeric results and provides `BigInt` for exact large integer calculations.

The Python implementation uses validation and arbitrary-precision integers while retaining explicit input checks.

The SQL model uses constraints and relational integrity to prevent structurally invalid recurrence records.

## Security and Production Considerations

A recurrence engine should not assume that supplied coefficients or initial values are trustworthy. Production systems should validate ranges before allowing a recurrence to generate extremely large values.

Unbounded recursive SQL generation can consume excessive database resources. Production queries should impose explicit term limits.

Large matrix exponents should be constrained when matrix values can grow rapidly.

Applications accepting recurrence definitions from external users should validate coefficient count, initial-condition count, forcing-function representation, numeric bounds, and requested sequence length before execution.

A forcing function should not be allowed to execute arbitrary application code merely because it represents `f(n)`. In production systems, externally supplied forcing behavior should normally be represented as controlled data or a predefined policy rather than arbitrary executable code.

## Relationship Between the Three Core Areas

The concepts have a strict relationship:

**Linear recurrence** describes the structural form of the dependency on previous terms.

**Homogeneous recurrence** is the linear case where the independent forcing term is zero.

**Non-homogeneous recurrence** is the linear case where an external forcing contribution is present.

The practical workflow therefore begins with the recurrence structure, establishes the initial conditions, identifies whether a forcing term exists, chooses an evaluation strategy, and then validates generated or observed sequence values against the mathematical rule.
