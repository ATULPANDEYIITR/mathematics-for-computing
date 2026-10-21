# Number Theory Fundamentals

This learning artifact develops four closely connected foundations of elementary number theory: divisibility, prime and composite classification, factorization, and the greatest common divisor. The five implementations use the same mathematical definitions but apply them to different technical settings.

The central relationship is:

**Divisibility → Factors → Prime Structure → Greatest Common Divisor**

A positive integer `d` divides an integer `n` when `n % d = 0`. Factors are divisors of a number. A prime has exactly two positive divisors, `1` and itself. A composite integer greater than `1` has additional positive divisors. The greatest common divisor, or GCD, is the largest positive integer dividing every member of a given collection.

---

## Mathematical Model

| Concept | Operational definition | Implementation use |
|---|---|---|
| Divisibility | `a` divides `b` when `b mod a = 0` | Validation of numerical relationships |
| Factor | Positive integer dividing another integer | Divisor enumeration |
| Prime | Integer greater than `1` with exactly two positive divisors | Identifier classification |
| Composite | Integer greater than `1` that is not prime | Structural classification |
| Prime factorization | Representation as a product of primes | Structural analysis |
| GCD | Largest positive common divisor | Equal partitioning and compatibility |
| Coprime | Two integers whose GCD is `1` | Independence of divisibility structure |
| LCM | Smallest positive common multiple | Synchronizing periodic quantities |

The implementations deliberately distinguish `0` and `1` from prime and composite numbers. Zero is divisible by every nonzero integer, but it is neither prime nor composite. One is a unit with only one positive divisor, so it is also neither prime nor composite.

---

## Divisibility

The basic operation is remainder evaluation:

`a ∣ b` if and only if `b mod a = 0`.

The implementations reject zero as a divisor because division by zero is undefined. Negative divisors are mathematically valid, but the factorization and divisor-enumeration APIs focus on positive integers because positive divisors provide the standard canonical representation.

The Python, JavaScript, C++, and SQL implementations all use the remainder operator for direct divisibility checks.

For example, `3 ∣ 36` is true because `36 mod 3 = 0`, while `5 ∤ 36` because `36 mod 5 = 1`.

Divisibility is useful as a primitive validation operation. It is also the basis for finding factors, testing composite numbers, and establishing common divisors.

---

## Factors and Efficient Divisor Enumeration

For a positive integer `n`, a direct algorithm could test every integer from `1` through `n`. That is unnecessary.

If `d` is a divisor of `n`, then:

`n = d × (n / d)`

Therefore, divisors occur in pairs. At least one member of each pair is no greater than `sqrt(n)`. The implementations test candidates only through the square root and add both members of every discovered pair.

For `36`, the pairs are:

`1 × 36`

`2 × 18`

`3 × 12`

`4 × 9`

`6 × 6`

This gives the positive divisor set:

`{1, 2, 3, 4, 6, 9, 12, 18, 36}`

The divisor-enumeration algorithm therefore requires approximately `O(sqrt(n))` candidate checks rather than `O(n)` checks.

The C++ implementation uses `candidate <= n / candidate` instead of `candidate * candidate <= n`. This avoids multiplying two potentially large values before the comparison.

---

## Prime and Composite Classification

A positive integer greater than `1` is prime if no integer other than `1` and itself divides it.

Testing every candidate up to `n - 1` is unnecessary. If `n` were composite, it would have a factor pair whose smaller member is at most `sqrt(n)`. Therefore, testing candidates through the square root is sufficient.

The implementations first handle small and even values:

- Values below `2` are not prime.
- `2` is prime.
- Every even value greater than `2` is composite.
- Odd candidates from `3` through `sqrt(n)` are then tested.

This produces an `O(sqrt(n))` trial-division primality test.

It is appropriate for educational and moderate-sized integer workloads. It is not a suitable general-purpose primality test for cryptographic-scale integers, where specialized algorithms and arbitrary-precision arithmetic are required.

---

## Prime Factorization

Every integer greater than `1` can be expressed as a product of prime powers.

For example:

`360 = 2³ × 3² × 5`

The factorization implementations repeatedly divide by `2`, then test odd candidates. When the remaining value becomes greater than `1` after trial division, that remainder is prime and becomes the final factor.

The factorization representation is:

`prime → exponent`

For `360`, this becomes:

`2 → 3`

`3 → 2`

`5 → 1`

This representation avoids storing repeated copies of the same prime and makes exponent-based analysis straightforward.

Trial division can still become expensive when a large input is prime or has a large prime factor. The implementations therefore make the performance limitation explicit rather than presenting trial division as a universal factorization method.

---

## Greatest Common Divisor

The GCD is the largest positive integer that divides two or more integers.

For example:

`gcd(252, 105) = 21`

because:

`252 = 21 × 12`

and:

`105 = 21 × 5`

### Euclid's Algorithm

The implementations use Euclid's algorithm rather than enumerating all factors:

`gcd(a, b) = gcd(b, a mod b)`

The process continues until the second value becomes zero. The remaining first value is the GCD.

For `252` and `105`:

`252 mod 105 = 42`

`105 mod 42 = 21`

`42 mod 21 = 0`

Therefore:

`gcd(252, 105) = 21`

The algorithm has logarithmic behavior with respect to the magnitude of its inputs and is substantially more efficient than computing every divisor when only the GCD is required.

The implementations explicitly reject `gcd(0, 0)` because no unique greatest positive common divisor exists for that pair.

---

## Equal Partitioning

A practical use of the GCD is determining the largest common unit that can divide several quantities.

Suppose three workloads contain:

`84`, `126`, and `210`

Their common divisor is:

`gcd(84, 126, 210) = 42`

Thus `42` is the largest unit that can divide all three quantities exactly.

The corresponding group counts are:

- `84 / 42 = 2`
- `126 / 42 = 3`
- `210 / 42 = 5`

The C++ and Java programs use this interpretation in repository-oriented workload scenarios, while the Python program demonstrates it directly.

---

## Python Implementation

The Python implementation provides a reusable number-theory module and an executable demonstration.

Its main mechanisms include:

| Mechanism | Purpose |
|---|---|
| `divides()` | Tests a divisibility relationship |
| `divisors()` | Enumerates positive divisors using paired factors |
| `is_prime()` | Performs square-root-bounded primality testing |
| `is_composite()` | Separates composite values from primes |
| `prime_factors()` | Produces prime-to-exponent mappings |
| `gcd_euclid()` | Computes a two-value GCD |
| `gcd_many()` | Extends the GCD operation across an iterable |
| `lcm()` | Computes the least common multiple using the GCD |
| `NumberProfile` | Groups classification and factorization data |
| validation exceptions | Reject invalid mathematical domains explicitly |

Python's arbitrary-precision integer behavior is useful for values larger than machine-sized integers. It does not remove algorithmic limitations: trial division remains expensive for sufficiently large inputs.

The script also demonstrates controlled failure handling for zero divisors, non-positive factorization inputs, invalid divisor enumeration, and the undefined `(0, 0)` GCD.

---

## JavaScript Implementation

The JavaScript implementation uses a complementary data-processing style rather than reproducing the Python structure.

`Map` is used for prime factorization because a prime maps naturally to its exponent. `Object.freeze()` is used for generated number profiles so consumers cannot accidentally mutate the returned analysis object.

The implementation also uses:

- array mapping for profile construction,
- filtering for prime selection,
- destructuring assignment inside Euclid's algorithm,
- explicit custom errors for mathematical-domain failures,
- safe-integer validation.

JavaScript's `Number` type can represent integers exactly only within the safe integer range. The implementation therefore rejects values outside `Number.MAX_SAFE_INTEGER` instead of silently performing inaccurate arithmetic.

For larger exact values, a production implementation should use `BigInt` consistently throughout the computation. Mixing `Number` and `BigInt` arithmetic without explicit conversion is unsafe and can itself produce runtime failures.

---

## C++ Governance-Oriented Case Study

The C++ program treats numeric analysis as a component of a repository-oriented resource planner.

`RepositoryIdentifier` models a repository with:

- a positive numeric identifier,
- an organization,
- a repository name.

`GovernancePartitionPlanner` processes those identifiers and reports their mathematical structure.

This provides a coherent use of the number-theory operations rather than presenting isolated language demonstrations.

The implementation uses:

- `std::vector` for collections,
- `std::map` for prime-to-exponent factorization,
- `std::sort` for ordered divisors,
- exceptions for invalid domain states,
- `long long` for fixed-width integer storage.

The divisor algorithm avoids `i * i` in its loop condition. This is important because multiplication can overflow even when the original value is representable.

The C++ program also demonstrates the distinction between algorithmic efficiency and integer range. `long long` provides a fixed signed 64-bit range, so very large mathematical integers require arbitrary-precision support rather than simply increasing loop bounds.

---

## Java Enterprise Domain Model

The Java implementation models number theory through explicit domain objects and policies.

`Repository` represents a validated repository identifier. `ReviewBatch` represents two positive quantities whose largest common assignment unit is calculated using the GCD.

The `NumberPolicy` interface separates a mathematical rule from the service that evaluates it. Two concrete policies are provided:

- `PrimeIdentifierPolicy`
- `DivisibleByPolicy`

`RepositoryGovernanceService` evaluates all configured policies and reports violations. This makes the mathematical rule explicit instead of embedding every condition directly inside a single procedural method.

Java records provide compact immutable domain values for repository and workload data. Collections returned by profiles are copied into immutable representations so callers cannot modify internal state accidentally.

Streams are used for policy evaluation and violation reporting. Exceptions represent domain failures such as invalid repository identifiers, invalid divisors, empty collections, and undefined GCD operations.

The implementation uses `long`, which has a fixed 64-bit range. A production service requiring values beyond that range should use `java.math.BigInteger` and adapt the algorithms accordingly.

---

## PostgreSQL Relational Model

The PostgreSQL implementation represents number-theoretic information as relational data rather than treating the database as a passive storage layer.

The principal relationships are:

`repository_identifiers`
→ `factorization_runs`
→ `prime_factors`

A repository identifier can have multiple recorded factorization runs, while each factorization can contain multiple prime factors with their corresponding exponents.

`workload_batches` stores two quantities and uses a trigger to calculate their GCD before insertion or update.

### Database Rules

The database enforces important invariants with:

- primary keys,
- foreign keys,
- unique constraints,
- positive-value checks,
- positive exponent checks,
- valid classification checks.

This prevents invalid states from depending exclusively on application code.

The `number_theory_gcd()` function implements Euclid's algorithm inside PostgreSQL. The `number_theory_is_prime()` function implements square-root-bounded trial division. `number_theory_classify()` derives the mathematical classification from those primitives.

The `number_theory_factor_count()` function calculates the total number of prime factors with multiplicity. For example, `360 = 2³ × 3² × 5` has six prime factors when multiplicity is counted.

---

## SQL Queries and Analytical Workflow

The SQL script includes queries for:

- divisibility filtering,
- prime/composite classification,
- factorization reporting,
- common-divisor analysis between repository identifiers,
- classification aggregation,
- trigger-derived GCD values,
- direct mathematical validation.

A common-divisor CTE compares repository identifiers pairwise and computes their GCD. Only pairs sharing a non-trivial common divisor are reported.

This demonstrates a useful distinction between mathematical computation and relational analysis:

**Mathematical function**

`number_theory_gcd(a, b)`

**Relational workflow**

select entities → form relevant pairs → apply GCD → filter meaningful relationships → report results

Indexes are applied to columns used for direct numerical lookup and prime-factor lookup. The schema does not add indexes merely for completeness.

---

## Transaction and Integrity Behavior

The SQL script includes a transaction containing both valid and invalid workload operations.

The invalid workload has a zero quantity and violates the positive-quantity constraint. The database catches the resulting constraint failure inside a nested procedural block and continues the outer transaction.

This illustrates an important production principle: mathematical validity that is part of a data invariant should be enforced at the database boundary as well as in application code.

Application validation provides early feedback. Database constraints protect persisted state when multiple applications, scripts, services, or administrative operations can write to the same database.

---

## Distinguishing the Implementations

The five source files intentionally approach the same mathematical domain from different engineering perspectives.

| File | Primary perspective | Distinctive mechanism |
|---|---|---|
| Python | Mathematical workflow and simulation | Functions, dataclass profiles, exception-driven validation |
| JavaScript | Event-oriented data processing | `Map`, immutable profiles, array operations, safe-integer checks |
| C++17 | Performance-oriented case study | Explicit classes, fixed-width integers, overflow-aware bounds |
| Java 17 | Enterprise domain modeling | Records, interfaces, policies, immutable collections, streams |
| PostgreSQL | Persistent relational workflow | Constraints, functions, trigger, views, CTEs, transactions |

The algorithms remain mathematically consistent, but their surrounding architecture differs.

---

## Edge Cases

Several values require explicit treatment.

| Input | Classification | Reason |
|---|---|---|
| Negative integer | Neither prime nor composite | Prime/composite definitions apply to positive integers greater than `1` |
| `0` | Neither prime nor composite | It has infinitely many integer divisors under standard divisibility |
| `1` | Unit | It has exactly one positive divisor |
| `2` | Prime | Its positive divisors are `1` and `2` |
| `0` as divisor | Invalid operation | Division remainder by zero is undefined |
| `gcd(0, n)` for `n ≠ 0` | `abs(n)` | Every integer divides zero |
| `gcd(0, 0)` | Undefined | No unique greatest positive common divisor |

The implementations intentionally distinguish invalid operations from valid mathematical edge cases.

---

## Complexity and Limitations

| Operation | Typical method | Time complexity |
|---|---|---|
| Divisibility | Remainder | `O(1)` |
| Divisor enumeration | Search through `sqrt(n)` | `O(sqrt(n))` |
| Trial-division primality | Search through `sqrt(n)` | `O(sqrt(n))` |
| Trial factorization | Repeated trial division | Up to `O(sqrt(n))` candidate work |
| GCD | Euclid's algorithm | `O(log(min(a,b)))` |
| Multi-value GCD | Repeated pairwise GCD | Approximately logarithmic per reduction |

The square-root algorithms are useful for fundamentals and moderate values. They are not intended as high-performance factoring systems for enormous integers.

The main implementation-specific limitations are also significant:

- Python integers support arbitrary precision, but factorization remains computationally expensive.
- JavaScript `Number` requires safe-integer validation; `BigInt` is required for larger exact integers.
- C++ `long long` and Java `long` have fixed-width ranges.
- PostgreSQL `BIGINT` is also limited to signed 64-bit values.
- Trial division is unsuitable for cryptographic-scale factorization.

---

## Practical Relationship Between the Concepts

The four principal concepts form a dependency chain rather than four unrelated topics.

```text
                Integer n
                    |
          +---------+---------+
          |                   |
      Divisibility        Classification
          |                   |
       Factors        +-------+-------+
          |            |             |
   Prime factors     Prime       Composite
          |
   Prime structure
          |
      +---+---+
      |       |
     GCD     LCM
      |
 Equal common
   partition
