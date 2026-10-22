# Euclidean Algorithm: GCD, Extended Euclidean Algorithm, and Bézout Identity

## Scope

This project treats the Euclidean Algorithm as a family of related number-theoretic procedures rather than as a single GCD calculation.

The implementations cover:

| Area | Technical focus |
|---|---|
| Classical Euclidean Algorithm | Repeated remainder reduction for computing the greatest common divisor |
| Extended Euclidean Algorithm | Propagation of coefficient sequences while computing the GCD |
| Bézout Identity | Certification that `ax + by = gcd(a,b)` |
| Modular Inverse | Deriving an inverse from Bézout coefficients when the GCD is `1` |
| Linear Diophantine Equations | Determining solvability and constructing one integer solution |
| Validation | Checking mathematical invariants instead of trusting calculated values |
| Failure handling | Rejecting impossible modular inverses and unsolvable equations |
| Large integers | Avoiding unnecessary precision loss in JavaScript and Java |
| Database representation | Persisting operands, certificates, solutions, states, and verification results in PostgreSQL |

The central mathematical relationship is:

`gcd(a,b) = gcd(b, a mod b)`

The Euclidean Algorithm repeatedly applies this reduction until the second operand becomes zero. The remaining non-negative operand is the GCD.

The extended algorithm retains additional information during the same reduction. It produces integers `x` and `y` such that:

`ax + by = gcd(a,b)`

This equation is the Bézout identity.

## Mathematical Model

For positive integers `a` and `b`, one Euclidean reduction step has the form:

`a = qb + r`

where:

`0 <= r < b`

The next state is:

`(b,r)`

The GCD does not change because every common divisor of `a` and `b` also divides `r = a - qb`, and every common divisor of `b` and `r` also divides `a = qb + r`.

For example:

`1071 = 2 * 462 + 147`

`462 = 3 * 147 + 21`

`147 = 7 * 21 + 0`

Therefore:

`gcd(1071,462) = 21`

The extended algorithm associates coefficient pairs with the remainders. For the same input it can produce coefficients satisfying:

`1071x + 462y = 21`

The coefficients are not unique across arbitrary representations of related equations, but the algorithm provides one valid pair efficiently.

## Classical GCD Versus Extended GCD

The classical algorithm only needs the remainder state.

Conceptually:

`r(i+1) = r(i-1) mod r(i)`

The extended version also maintains two coefficient sequences. If a remainder is represented as:

`r = a*s + b*t`

then the next quotient is used to update the coefficients together with the remainder.

This distinction matters because the ordinary GCD answers:

`What is the greatest common divisor?`

The extended algorithm answers:

`What is the greatest common divisor, and which coefficients prove the Bézout identity?`

The second result supports additional operations such as modular inversion and linear Diophantine equations.

## Bézout Identity

For nonzero integers `a` and `b`, there always exist integers `x` and `y` satisfying:

`ax + by = gcd(a,b)`

The Python, JavaScript, C++, Java, and PostgreSQL implementations all verify this identity explicitly.

This verification is important because a numerical GCD alone does not prove that the extended coefficients were propagated correctly.

For example, if an implementation returns:

`gcd = 2`

`x = -1`

`y = 2`

for `a = 6` and `b = 4`, then:

`6(-1) + 4(2) = 2`

so the certificate is valid.

A certificate can therefore be treated as a mathematical integrity record rather than merely an intermediate computational result.

## Modular Inverse

A number `a` has a multiplicative inverse modulo `m` exactly when:

`gcd(a,m) = 1`

The extended Euclidean algorithm gives:

`ax + my = 1`

Reducing this equation modulo `m` gives:

`ax ≡ 1 (mod m)`

Therefore `x mod m` is the modular inverse.

The implementations use this mechanism rather than searching through candidate values.

For example:

`17^(-1) mod 3120`

exists because:

`gcd(17,3120) = 1`

The returned coefficient is normalized into the interval appropriate for the modulus.

The failure case:

`inverse(6 mod 15)`

is rejected because:

`gcd(6,15) = 3`

and therefore no integer `x` can satisfy:

`6x ≡ 1 (mod 15)`

## Linear Diophantine Equations

The implementations also solve equations of the form:

`ax + by = c`

An integer solution exists exactly when:

`gcd(a,b) divides c`

The extended Euclidean algorithm first produces:

`ax0 + by0 = gcd(a,b)`

If:

`c = k * gcd(a,b)`

then multiplying the Bézout coefficients by `k` gives one solution:

`x = kx0`

`y = ky0`

The Python, JavaScript, Java, C++, and PostgreSQL implementations validate the resulting equation rather than merely returning the calculated coefficients.

For:

`35x + 15y = 10`

the GCD is `5`, and because `5` divides `10`, an integer solution exists.

For:

`6x + 10y = 7`

the GCD is `2`, and because `2` does not divide `7`, the equation is rejected.

## Python Implementation

The Python program is a self-contained arithmetic case study built around `EuclideanAlgorithm`.

It provides:

- Iterative GCD calculation.
- Recursive GCD calculation.
- Extended GCD with a frozen `ExtendedGCDResult` data model.
- Bézout identity verification.
- Modular inverse calculation.
- Linear Diophantine equation solving.
- Euclidean reduction tracing.
- Batch validation against Python's `math.gcd`.
- Explicit failure tests.
- Self-tests for normal, zero, negative, and large-integer cases.

The `ExtendedGCDResult` object keeps the original operands, GCD, and coefficients together. Its `is_valid()` method directly evaluates the Bézout identity.

The iterative extended algorithm is preferred for the main implementation because extremely long Euclidean sequences should not depend on Python recursion depth.

The script also distinguishes invalid input types from mathematical failures. A non-integer input is a type error, while a missing modular inverse is a mathematical domain failure.

## JavaScript Implementation

The JavaScript implementation deliberately uses `BigInt`.

JavaScript `Number` values are floating-point numbers and cannot exactly represent every integer above `Number.MAX_SAFE_INTEGER`. Number-based arithmetic would therefore be inappropriate for a general-purpose exact integer implementation.

`BigInt` preserves exact integer semantics for the operations required by the Euclidean algorithm.

The implementation contains:

- `ExtendedGCDResult` for Bézout certificates.
- Exact GCD and extended-GCD calculations.
- Positive modulo normalization.
- Modular inverse evaluation.
- Diophantine equation solving.
- An event bus for operation lifecycle events.
- An `ArithmeticService` that emits start, completion, and failure events.
- Self-tests.
- Large-integer examples.

The event-driven design provides a different perspective from the Python implementation. An arithmetic operation is treated as a service event rather than simply as a function call.

The event bus can record or route operational information without embedding logging behavior directly inside the mathematical algorithm.

## C++ Implementation

The C++ program models an arithmetic certificate service.

`ExtendedGCDResult` stores the mathematical result and exposes a `valid()` method for Bézout verification.

The implementation uses `__int128` for intermediate coefficient calculations. This is important because two signed 64-bit operands can produce intermediate coefficient values that need more working space even when the original operands fit in `int64_t`.

The program also handles the special `INT64_MIN` absolute-value problem. Negating the minimum signed 64-bit value directly can overflow. The `magnitude()` implementation therefore performs the conversion safely in unsigned space.

The C++ program demonstrates:

- GCD calculation.
- Extended GCD.
- Bézout certificates.
- Modular inverses.
- Linear Diophantine equations.
- Explicit overflow checks.
- Domain-error handling.
- An audit trail.
- Assertions covering mathematical invariants.

This implementation treats arithmetic correctness and numeric-range safety as separate concerns.

## Java Implementation

The Java program models the algorithm as an enterprise arithmetic policy service.

`BigInteger` is used instead of primitive integer types. This avoids fixed-width overflow and makes the implementation suitable for calculations whose operands and coefficients exceed the range of `long`.

The domain model includes:

- `BezoutCertificate`
- `DiophantineSolution`
- `ServiceResult`
- `OperationStatus`
- `FailureReason`
- `Policy`
- `BezoutIntegrityPolicy`
- `ArithmeticAuditLog`

The `ServiceResult` model separates successful results from explicit rejection states.

This is useful in enterprise workflows where a mathematical failure such as "no modular inverse exists" is a valid business outcome rather than an unexpected programming exception.

The `BezoutIntegrityPolicy` represents certificate validation independently from the algorithm that produced the certificate.

The implementation therefore separates:

`calculation -> certificate -> policy evaluation -> service result`

This makes the mathematical domain behavior explicit without requiring external frameworks.

## PostgreSQL Implementation

The PostgreSQL script represents the algorithm as a persistent relational workflow.

The main entities are:

| Table | Purpose |
|---|---|
| `arithmetic_jobs` | Records the type and lifecycle state of each arithmetic operation |
| `bezout_certificates` | Stores operands, GCD values, and Bézout coefficients |
| `modular_inverse_requests` | Stores inverse requests, results, and mathematical rejection reasons |
| `diophantine_requests` | Stores equations, solutions, solvability, and failure reasons |

The database uses constraints to enforce mathematical integrity.

The `bezout_identity_holds` check constraint verifies:

`a*x + b*y = gcd`

The modular inverse consistency constraint requires an invertible request to have:

`gcd = 1`

and:

`value * inverse mod modulus = 1`

The Diophantine consistency constraint requires a successful solution to satisfy the original equation.

These constraints prevent the database from accepting records that contradict the mathematical result.

## PostgreSQL Functions

`calculate_extended_gcd()` implements the extended Euclidean algorithm inside PostgreSQL using PL/pgSQL.

It returns:

- the GCD,
- coefficient `x`,
- coefficient `y`.

`normalize_mod()` converts a remainder into a non-negative modular representation.

`solve_linear_diophantine()` uses the extended-GCD result to determine whether an equation is solvable and, when it is, constructs one solution.

The database therefore performs more than passive storage. It contains executable mathematical logic and integrity rules.

## Recursive CTE Euclidean Trace

The SQL script also contains a recursive CTE that exposes the Euclidean remainder chain.

The recursive state consists of:

`(a,b,step_number)`

Each iteration replaces the pair with:

`(b, a mod b)`

The result makes the mathematical reduction visible as relational rows.

This is useful when the database must expose calculation history or produce an audit-oriented explanation of how a GCD was obtained.

## Transactional Behavior

The SQL script demonstrates a transaction with a savepoint around an invalid modular inverse request.

The transaction can temporarily record the operation, roll back to the savepoint, and then record the mathematically rejected result in a controlled state.

This illustrates the distinction between:

- database transaction failure,
- application-level mathematical rejection,
- persistent recording of a rejected operation.

A non-invertible number is not a database error. It is a valid request whose mathematical result is rejection.

## Complexity

For inputs `a` and `b`, the Euclidean algorithm runs in:

`O(log(min(|a|, |b|)))`

remainder steps in the standard complexity analysis.

The extended Euclidean algorithm has the same asymptotic number of reduction steps, with additional arithmetic required for coefficient propagation.

For ordinary machine integers, the arithmetic operations are effectively constant-time under the fixed-width model. For arbitrary-precision integers, the cost also depends on operand size and multiplication or division complexity.

The Java and JavaScript implementations use arbitrary-precision arithmetic, so their practical cost depends on the number of digits as well as the number of Euclidean iterations.

## Edge Cases

The implementations explicitly handle:

- `gcd(0,0)`.
- `gcd(0,b)`.
- `gcd(a,0)`.
- Negative operands.
- Non-coprime modular-inverse inputs.
- Modulus values less than or equal to one.
- Unsolvable Diophantine equations.
- Zero coefficients.
- Very large integer values.
- Invalid input types in Python.
- Fixed-width overflow concerns in C++.
- Exact-integer limitations of JavaScript `Number`.

For `(0,0)`, the GCD convention used by the implementations is `0`. The extended certificate `(0,0,1,0)` is not unique, so applications should treat coefficient representation separately from the GCD convention.

## Validation Strategy

Every implementation validates the central invariant:

`a*x + b*y = gcd(a,b)`

The self-tests also compare the extended result with the independently calculated GCD.

The modular inverse is checked by:

`(a * inverse) mod m = 1`

The Diophantine solver is checked by substituting the returned values back into:

`ax + by = c`

This approach catches coefficient-propagation errors that could remain hidden if only the final GCD were tested.

## Relationship Between the Components

The dependency chain is:

`Euclidean Algorithm`
    
`→ GCD`
    
`→ Extended Euclidean Algorithm`
    
`→ Bézout coefficients`
    
`→ Modular inverse / Diophantine solution`

The classical algorithm establishes the GCD.

The extended algorithm adds coefficient information.

The Bézout identity provides the mathematical certificate.

A modular inverse is a specialized Bézout result where the GCD is one.

A linear Diophantine solution is obtained by scaling a Bézout representation when the target is divisible by the GCD.

This separation prevents the four concepts from being treated as interchangeable algorithms.

## Security and Production Considerations

Exact arithmetic matters when the result controls cryptographic or protocol behavior. Floating-point arithmetic should not be used for exact GCD, Bézout, or modular-inverse calculations.

Inputs should be bounded when exposed through a network service. Arbitrary-precision arithmetic prevents ordinary numeric overflow but does not eliminate resource-exhaustion risks from extremely large operands.

For cryptographic workloads, timing behavior can matter. The basic Euclidean and extended Euclidean algorithms are suitable for general mathematical computation, but cryptographic implementations may require algorithms specifically designed for side-channel resistance and constant-time behavior.

Database constraints should remain aligned with application-level validation. Application checks provide useful error messages, while database constraints protect persisted data when multiple clients or services write to the same database.

Audit records should avoid storing sensitive operands or derived values when the surrounding application treats them as confidential.

## Practical Workflow

A typical exact-arithmetic service can be represented as:

`Input operands`

`→ Validate representation and domain`

`→ Run Euclidean reduction`

`→ Produce GCD`

`→ Optionally propagate Bézout coefficients`

`→ Verify ax + by = gcd`

`→ Apply the requested operation`

`→ Verify the derived result`

`→ Return or persist the result`

For a modular inverse, the additional rule is:

`gcd(a,m) = 1`

For a linear Diophantine equation, the additional rule is:

`gcd(a,b) divides c`

The implementations consistently enforce these conditions rather than attempting to produce a result when the mathematical conditions are not satisfied.

## File Behavior

The Python script provides the most direct algorithmic and testing-oriented implementation.

The JavaScript file adds exact `BigInt` arithmetic and event-driven operation processing.

The C++ program emphasizes numeric representation, intermediate overflow protection, certificate validation, and low-level control.

The Java program emphasizes domain modeling, explicit policy evaluation, typed failure states, and arbitrary-precision arithmetic.

The PostgreSQL script moves the mathematical model into persistent relational structures, database functions, constraints, views, recursive CTEs, and transactions.

Together, the implementations present the Euclidean Algorithm as both a mathematical procedure and a reusable computational primitive whose correctness can be represented, verified, and persisted.
