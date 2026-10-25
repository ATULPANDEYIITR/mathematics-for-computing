# Modular Inverses and the Extended Euclidean Algorithm

## Purpose

A modular inverse provides a way to solve multiplication equations under modular arithmetic. It is fundamental to modular division, congruences, cryptographic algorithms, and computations involving finite rings.

For integers \(a\) and \(m\), an inverse of \(a\) modulo \(m\) is an integer \(x\) satisfying

\[
ax \equiv 1 \pmod m.
\]

Equivalently, \(ax-1\) must be divisible by \(m\). When an inverse exists, its canonical representative is the unique value in the range \(0 \le x < m\).

The five implementations cover inverse calculation, mathematical verification, modular exponentiation, validation, and database-backed result tracking.

## 1. Mathematical Foundations

### Modular arithmetic

Two integers \(u\) and \(v\) are congruent modulo \(m\) when their difference is divisible by \(m\):

\[
u \equiv v \pmod m.
\]

For example, \(17 \equiv 6 \pmod {11}\).

Multiplication respects congruence, so reducing intermediate results modulo \(m\) preserves the final remainder. This property makes it possible to perform large modular computations without constructing unnecessarily large powers.

### Multiplicative inverses

An integer has a multiplicative inverse modulo \(m\) exactly when it is relatively prime to \(m\):

\[
\gcd(a,m)=1.
\]

For example, the inverse of \(3\) modulo \(11\) is \(4\), because

\[
3 \cdot 4 = 12 \equiv 1 \pmod {11}.
\]

The inverse of \(6\) modulo \(15\) does not exist because \(\gcd(6,15)=3\). No integer multiple of \(6\) has remainder \(1\) modulo \(15\).

The modulus must be greater than one in these implementations. A negative input value is permitted, provided the modulus satisfies the validation rules.

### Extended Euclidean algorithm

The Euclidean algorithm repeatedly replaces a pair of integers with a smaller pair while preserving their greatest common divisor. The extended version also calculates coefficients \(x\) and \(y\) such that

\[
ax+my=\gcd(a,m).
\]

If the greatest common divisor equals one, then

\[
ax+my=1.
\]

Taking both sides modulo \(m\) gives

\[
ax \equiv 1 \pmod m.
\]

Therefore, the inverse is \(x \bmod m\).

The algorithm works with composite moduli as well as prime moduli. A prime modulus makes every nonzero residue invertible, but a composite modulus can contain nonzero residues that have no inverse.

### Modular exponentiation

For nonnegative exponent \(e\), binary exponentiation computes \(a^e \bmod m\) using repeated squaring. It requires \(O(\log e)\) modular multiplications.

A negative exponent requires an inverse:

\[
a^{-e} \equiv (a^{-1})^e \pmod m.
\]

Consequently, negative modular exponents are valid only when the base is invertible under the selected modulus.

## 2. Python Implementation

The Python script provides reusable arithmetic functions, explicit validation, a result dataclass, error handling, and executable assertions.

### Main components

- `extended_gcd(a, b)` returns the greatest common divisor and Bézout coefficients.
- `modular_inverse(a, modulus)` calculates a normalized inverse or raises `ModularInverseError`.
- `inverse_or_none(a, modulus)` returns `None` when an inverse cannot be calculated.
- `modular_power(base, exponent, modulus)` supports positive, zero, and negative exponents.
- `run_tests()` verifies known results and checks a range of values against the greatest-common-divisor condition.

The implementation uses Python integers, which support arbitrary-precision arithmetic. The built-in three-argument `pow` function performs modular exponentiation efficiently for nonnegative exponents.

The test loop checks that every reported inverse satisfies the defining congruence and that non-coprime inputs are rejected.

## 3. JavaScript Implementation

The JavaScript file uses `BigInt` for exact integer calculations. Ordinary JavaScript `Number` values cannot represent every integer exactly, so using them for unrestricted modular arithmetic can produce incorrect results.

### Main components

- `extendedGcd` calculates the Bézout coefficients.
- `modularInverse` returns a canonical residue and rejects non-invertible inputs.
- `modularPower` implements binary exponentiation.
- `InverseRegistry` caches inverse results by normalized residue for repeated lookups under one modulus.
- `report` produces immutable result objects that record the input, inverse, and verification status.

The registry distinguishes an inverse equal to zero from the absence of an inverse by storing either a `BigInt` or `null`. A `Map` provides direct cache access, while normalization ensures equivalent residues share a cache entry.

The program includes known-result assertions and a bounded exhaustive test. All arithmetic inputs must be `BigInt` values, preventing silent mixing of integer types.

## 4. C++17 Implementation

The C++ program combines modular arithmetic with a repository merge-governance case study. These are separate computational concerns: the arithmetic functions calculate inverses, while the governance engine evaluates whether a proposed repository change satisfies a configured set of conditions.

### Arithmetic engine

`BezoutResult` holds the greatest common divisor and two coefficients. `extendedGcd` uses an iterative algorithm, and `modularInverse` returns an `optional<int64>` because an inverse might not exist.

The implementation rejects `INT64_MIN`, whose absolute value cannot be represented as a signed 64-bit integer. Intermediate products can also overflow the fixed-width type for sufficiently large inputs, so the arithmetic demonstration is intended for bounded values rather than unrestricted cryptographic calculations.

### Repository governance engine

The repository scenario contains:

- A Pull Request with source and target branches, commits, synchronization state, and conflict status.
- A branch policy specifying required approvals, required checks, and history restrictions.
- Reviews with reviewer eligibility, authorship, dismissal, and decision state.
- Status checks with required or optional status and pass or fail outcomes.
- An eligibility result containing every detected blocking condition.

The evaluator rejects closed or draft requests, unresolved conflicts, unsynchronized branches, unresolved discussions, missing approvals, requested changes, and failing required checks.

The example first evaluates a request with a failing integration check, then updates the check, and finally dismisses an approval to show how eligibility changes.

This is a teaching model rather than a complete implementation of a hosting provider's governance rules. It does not model real identities, branch permissions, webhook events, or the complete history of approval invalidation.

## 5. Java 17 Implementation

The Java program uses `BigInteger` to support large exact integers without fixed-width overflow. Records represent immutable domain values, enums restrict workflow states to defined choices, and an interface separates review policy from the merge-evaluation service.

### Arithmetic components

`extendedGcd` returns a `BezoutResult` record. `modularInverse` validates the modulus and rejects non-coprime inputs. `modularPower` uses repeated squaring and supports negative exponents by first calculating the modular inverse.

### Enterprise governance components

`PullRequest`, `BranchPolicy`, `Reviewer`, `Review`, and `StatusCheck` provide explicit domain types.

`StandardReviewPolicy` defines which reviews count as approvals and which decisions block merging. A review does not count if its reviewer is ineligible, is the author, or the review has been dismissed or marked stale.

`MergeEligibilityService` evaluates the request and returns an immutable `Eligibility` result. Its list of reasons allows callers to identify multiple simultaneous failures rather than receiving only the first error.

The sample policy requires two current eligible approvals, passing required checks, and linear history. The author’s approval does not count toward the threshold. The program also demonstrates a dismissed approval.

This design makes the review-counting rule independently replaceable without changing the arithmetic implementation or the merge-evaluation service.

## 6. PostgreSQL Implementation

The SQL script models arithmetic inputs and results in relational tables and implements the extended Euclidean algorithm with PL/pgSQL.

### Relational model

| Table | Purpose |
|---|---|
| `modulus_registry` | Stores valid moduli and their descriptions. |
| `inverse_requests` | Records input values, requesters, and timestamps. |
| `inverse_results` | Stores the greatest common divisor, Bézout coefficients, and optional inverse. |

Foreign keys connect requests to registered moduli and results to their originating requests. Constraints ensure that a stored inverse exists exactly when the stored greatest common divisor is one.

An index on `(modulus_id, requested_at DESC)` supports queries that retrieve recent requests for a particular modulus.

### Database functions and trigger

`extended_gcd` returns the greatest common divisor and Bézout coefficients. `modular_inverse` returns a normalized inverse or `NULL` when the input is not invertible. `modular_power` implements binary exponentiation, including negative exponents when an inverse exists.

The `inverse_request_after_insert` trigger calculates the result when a request is inserted. Because the trigger operates in the same transaction as the insert, a failed transaction rolls back both the request and its result.

The `inverse_verification` view independently evaluates the Bézout identity and inverse equation. Reporting queries count successful and unsuccessful requests by modulus.

The final transaction demonstrates rollback using a nested PL/pgSQL exception block. The test row should not remain after the exception is handled.

The database uses `NUMERIC` for exact integer arithmetic, but the declared precision limit remains finite. It is not an unlimited arbitrary-precision cryptographic engine, and input sizes should be bounded in production.

## 7. Distinguishing the Mechanisms

| Mechanism | Purpose | Important condition |
|---|---|---|
| Greatest common divisor | Determines whether an inverse can exist | \(\gcd(a,m)=1\) |
| Extended Euclidean algorithm | Finds the Bézout coefficients | Exact integer division |
| Modular inverse | Solves \(ax \equiv 1 \pmod m\) | The value and modulus must be coprime |
| Modular exponentiation | Calculates a power modulo a modulus | Negative exponents require an inverse |
| Result verification | Checks a computed inverse | \(ax \bmod m=1\) |
| Result caching | Avoids repeating a calculation for the same residue and modulus | Cache keys must include the modulus context |
| Database constraints | Prevents inconsistent stored results | The stored inverse must agree with the stored GCD state |

## 8. Complexity and Engineering Considerations

Let \(m\) be the modulus and \(e\) the exponent.

- The Euclidean algorithm performs \(O(\log \min(|a|,|m|))\) remainder steps for nonzero inputs.
- The extended algorithm has the same asymptotic number of steps as the ordinary Euclidean algorithm.
- Binary modular exponentiation performs \(O(\log |e|)\) modular multiplication steps for a nonzero exponent.
- The C++ and Java governance evaluators process \(r\) reviews and \(c\) status checks in \(O(r+c)\) time.
- The JavaScript registry uses expected constant-time map access, excluding the cost of calculating a missing inverse.

These complexity descriptions count arithmetic operations. The bit cost of arbitrary-precision multiplication and division also depends on operand size.

### Security and reliability

Modular inverse calculation is not automatically suitable for every cryptographic use. The algorithms here are designed for mathematical correctness and learning, not guaranteed constant-time execution. Timing behavior, input size, and error messages may reveal information in sensitive environments.

For cryptographic implementations:

- Use established cryptographic libraries for key operations.
- Avoid assuming that arbitrary-precision arithmetic is constant-time.
- Validate modulus and input sizes.
- Keep secret values out of diagnostic output.
- Test non-coprime inputs and negative values.
- Verify computed results independently where correctness is critical.
- Avoid caching secret-dependent intermediate values without an explicit security review.

The most important invariant is simple: an inverse is valid only when its product with the original value has remainder one under the selected modulus.
