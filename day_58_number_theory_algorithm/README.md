# Number Theory Algorithms

This project implements fundamental and advanced number-theory algorithms across Python, JavaScript, C++17, Java 17, and PostgreSQL. The implementations focus on fast exponentiation, primality testing, modular arithmetic, factorization, greatest common divisors, modular inverses, and Euler's totient function.

The five implementations use the same mathematical domain while deliberately applying different engineering approaches.

## Scope

The central computational model is:

`a^e mod m`

where direct exponentiation can become prohibitively large, while binary exponentiation reduces the number of multiplication steps to `O(log e)`.

The project also covers:

| Area | Purpose |
|---|---|
| Euclidean algorithm | Computes `gcd(a, b)` efficiently |
| Extended Euclidean algorithm | Finds Bézout coefficients and supports modular inverses |
| Fast exponentiation | Computes modular powers in logarithmic time |
| Modular inverse | Finds `a^-1 mod m` when `gcd(a, m) = 1` |
| Trial-division primality | Deterministic primality testing for practical integer sizes |
| Miller-Rabin | Efficient primality testing for large candidates |
| Prime factorization | Represents an integer as prime factors and exponents |
| Euler's totient | Counts positive integers up to `n` that are coprime to `n` |
| Chinese remainder theorem | Combines compatible congruence systems |
| Modular arithmetic | Encapsulates repeated operations under one modulus |

## Mathematical Workflow

The implementations follow a dependency-oriented relationship:

`Input`
  
`↓`

`Validation`
  
`↓`

`GCD / Factorization / Primality`
  
`↓`

`Modular Arithmetic`
  
`↓`

`Fast Modular Exponentiation`
  
`↓`

`Inverse / Totient / CRT`
  
`↓`

`Validated Result`

The algorithms are related, but they solve different problems. GCD determines divisibility relationships. Primality determines whether an integer has non-trivial factors. Factorization exposes those factors. Modular exponentiation computes powers under a modulus. A modular inverse exists only when the relevant GCD is one.

## Fast Exponentiation

Naive exponentiation performs repeated multiplication and can require `O(e)` multiplications.

Binary exponentiation uses the binary representation of the exponent.

For example, if:

`e = 13 = 1101₂`

then:

`a^13 = a^8 × a^4 × a`

The algorithm repeatedly squares the current base and consumes one exponent bit at a time.

The implementation maintains:

- a current result
- a reduced base
- a remaining exponent
- the modulus

Whenever the current exponent bit is one, the current base is multiplied into the result. The base is then squared and the exponent is shifted right.

The time complexity is `O(log e)` modular multiplications.

The modular reduction is performed after multiplication rather than constructing the complete value of `a^e`.

## Modular Arithmetic

A modulus must be positive in all implementations.

The expression:

`a mod m`

normalizes a value into the modular range used by the implementation.

The main invariant for a computed residue is:

`0 <= result < m`

A zero exponent is valid. For positive modulus:

`a^0 mod m = 1 mod m`

Therefore the result is `1` except when `m = 1`, where the residue is `0`.

Negative exponents are rejected by the fast-exponentiation APIs because they require modular inversion before exponentiation.

## Greatest Common Divisor

The Euclidean algorithm repeatedly replaces:

`(a, b)`

with:

`(b, a mod b)`

until the second value becomes zero.

The remaining first value is the GCD.

Its running time is logarithmic in the magnitude of the input under the standard integer model.

The extended Euclidean algorithm also produces integers `x` and `y` satisfying:

`ax + by = gcd(a, b)`

These coefficients are the basis of modular inverse calculation.

## Modular Inverses

A modular inverse of `a` modulo `m` is a value `x` satisfying:

`ax ≡ 1 mod m`

The inverse exists exactly when:

`gcd(a, m) = 1`

For example:

`7^-1 mod 26 = 15`

because:

`7 × 15 = 105`

and:

`105 mod 26 = 1`

The Python, C++, and Java implementations explicitly model the GCD condition. The Java implementation also uses `BigInteger.modInverse` for arbitrary-precision arithmetic.

## Primality Testing

Two different approaches are implemented.

### Trial Division

Trial division handles small and moderate integers directly.

Even values greater than two are rejected immediately. Odd divisors are then tested up to the square root of the candidate.

Testing only up to the square root is sufficient because if a composite integer has a factor larger than its square root, it must also have a corresponding factor smaller than the square root.

The complexity is approximately `O(sqrt(n))` trial divisions in the worst case.

### Miller-Rabin

Miller-Rabin decomposes:

`n - 1 = d × 2^s`

where `d` is odd.

A candidate base is tested through repeated modular exponentiation. Composite values eventually reveal a witness to compositeness.

The Python and JavaScript versions use repeated witnesses. The C++ implementation uses a deterministic witness set appropriate for the unsigned 64-bit domain.

The Java implementation uses `BigInteger.isProbablePrime`, which provides a high-confidence primality test for arbitrary-precision integers.

The two primality approaches are deliberately distinct:

| Method | Strength | Limitation |
|---|---|---|
| Trial division | Simple and deterministic | Slow for large candidates |
| Miller-Rabin | Fast for large candidates | Requires probabilistic or bounded-domain assumptions |

## Prime Factorization

Factorization repeatedly removes each discovered prime factor.

For:

`360`

the representation is:

`2^3 × 3^2 × 5`

The factorization output stores the prime and its exponent rather than storing repeated copies of the same factor.

The implementations stop trial division once the current divisor exceeds the square-root boundary of the remaining value. If a remaining value greater than one survives, it is itself prime.

This representation is useful for calculations such as Euler's totient.

## Euler's Totient Function

Euler's totient `φ(n)` counts integers in the range `1` through `n` that are relatively prime to `n`.

If the distinct prime factors of `n` are `p1, p2, ..., pk`, then:

`φ(n) = n × Π(1 - 1/p)`

The implementations compute the result by starting with `n` and subtracting the corresponding fraction for every distinct prime factor.

For:

`36 = 2^2 × 3^2`

the result is:

`φ(36) = 36 × (1 - 1/2) × (1 - 1/3) = 12`

## Chinese Remainder Theorem

The Python implementation also includes a Chinese remainder theorem solver.

It accepts congruences such as:

`x ≡ 2 mod 3`

`x ≡ 3 mod 5`

`x ≡ 2 mod 7`

and produces:

`x = 23`

as the smallest non-negative solution.

The implementation validates that the moduli are pairwise coprime before constructing the combined solution.

This provides a concrete example of how modular inverses and modular multiplication can be composed into a higher-level number-theoretic algorithm.

## Python Implementation

The Python file provides the broadest algorithmic model.

It contains:

- `gcd`
- `extended_gcd`
- `modular_inverse`
- binary modular exponentiation
- sieve of Eratosthenes
- trial-division primality testing
- Miller-Rabin testing
- prime factorization
- Euler's totient
- Chinese remainder theorem
- a `ModularArithmetic` dataclass
- explicit validation exceptions
- assertions and executable checks

Python's arbitrary-precision integers allow large intermediate values without fixed-width integer overflow.

The `dataclass` provides a compact immutable representation of a modulus-bound arithmetic service.

The example workflow also tests invalid exponents, invalid moduli, nonexistent inverses, and non-coprime CRT moduli.

## JavaScript Implementation

The JavaScript file emphasizes event-driven and asynchronous processing.

It uses:

- `Map` for factorization results
- `Set`-like collection behavior through arrays and structured data
- `BigInt` for large modular arithmetic
- Node.js `crypto` for secure random candidate selection
- `EventEmitter` for operation events
- `Promise.all` for asynchronous batch primality evaluation
- explicit custom error types

The implementation separates ordinary safe-integer APIs from `BigInt` arithmetic.

This distinction is important because JavaScript's `Number` type cannot represent every integer exactly beyond the safe-integer boundary. Large modular calculations therefore use `BigInt`.

The service emits `completed` and `rejected` events, allowing computational outcomes to be observed without embedding logging into every algorithmic operation.

## C++17 Implementation

The C++ program treats number theory as a computational engine with explicit error handling and fixed-width integer constraints.

It uses:

- structs for request and decision records
- `std::map` for prime factorization
- STL containers
- exception-based validation
- unsigned 64-bit arithmetic
- deterministic Miller-Rabin witnesses
- `unsigned __int128` for safe multiplication before modular reduction

The `multiplyMod` function is important for large 64-bit operands. Multiplying two `uint64_t` values directly can overflow before the modulus is applied. The implementation therefore widens the intermediate product before taking the remainder.

The C++ Miller-Rabin implementation uses a bounded-domain deterministic witness set appropriate for unsigned 64-bit values. This differs from the probabilistic strategy used by the Python implementation.

A request-evaluation layer validates modular computation before executing it, making the program a coherent technical case study rather than a collection of unrelated functions.

## Java 17 Implementation

The Java implementation models number-theory operations as an enterprise-style service.

It contains:

- domain records
- an operation-state enum
- a validation policy interface
- a concrete validation policy
- a service class
- custom validation exceptions
- immutable request and result records
- stream-based reporting
- `BigInteger` arithmetic

The explicit state model is:

`RECEIVED → VALIDATED → EXECUTED`

or:

`RECEIVED → REJECTED`

This makes invalid mathematical inputs visible as domain states rather than silently producing incorrect values.

Java's `BigInteger` is used when arbitrary precision matters. This is particularly useful for modular exponentiation where fixed-width multiplication could overflow.

## PostgreSQL Implementation

The PostgreSQL script represents number-theory computation as persistent relational data.

The schema contains:

- `algorithm_runs`
- `prime_results`
- `prime_factors`
- `modular_requests`

An enum defines execution states:

`received`

`validated`

`executed`

`rejected`

Database constraints reject impossible states such as negative exponents and non-positive moduli.

A trigger performs early validation for modular requests.

The `modular_power` function implements binary exponentiation directly in PL/pgSQL rather than relying on a generic external procedure.

The database also exposes:

- GCD calculation
- trial-division primality testing
- Euler's totient
- request processing
- reporting views
- aggregate queries
- validation queries
- transactional execution

The factorization table uses a composite primary key:

`(number_value, prime_factor)`

This ensures that one number cannot contain duplicate factor rows for the same prime.

## Validation and Failure Handling

The implementations reject mathematically invalid inputs instead of silently returning misleading results.

Important invalid cases include:

| Input | Result |
|---|---|
| Modulus `<= 0` | Rejected |
| Negative exponent | Rejected |
| Modular inverse with non-coprime operands | Rejected |
| Factorization of zero | Rejected |
| Totient of a non-positive integer | Rejected |
| CRT with non-coprime moduli | Rejected |
| Primality input below two | Composite/non-prime result |

Zero itself is not prime.

One is not prime.

The modular inverse of an element does not exist merely because a modulus is supplied. Coprimality is required.

## Complexity

| Algorithm | Typical complexity |
|---|---|
| GCD | `O(log min(a,b))` |
| Extended GCD | `O(log min(a,b))` |
| Binary exponentiation | `O(log e)` modular multiplications |
| Trial division | `O(sqrt(n))` |
| Miller-Rabin | `O(k log^3 n)` under a conventional bit-complexity view |
| Basic factorization | Approximately `O(sqrt(n))` trial divisions |
| Euler totient using factors | Dependent on factorization cost |
| Sieve | `O(n log log n)` |
| CRT for `k` pairwise-coprime moduli | Polynomial in the number and size of inputs |

The exact practical cost depends on integer representation and multiplication complexity.

## Security Considerations

Number-theoretic algorithms are frequently used in security-sensitive systems, but correctness alone does not make an implementation cryptographically secure.

Important considerations include:

- Avoid using ordinary pseudo-random generators for cryptographic key generation.
- The JavaScript implementation uses Node.js `crypto.randomBytes` for random Miller-Rabin bases.
- Large integer arithmetic must avoid accidental precision loss.
- Fixed-width multiplication must account for overflow.
- Modular inverses must verify coprimality.
- Inputs should be bounded when exposed through public APIs.
- Extremely large primality or factorization requests can consume substantial CPU time.
- Timing characteristics can matter when secret values are involved.
- The examples are algorithmic learning artifacts and are not substitutes for audited cryptographic implementations.

The C++ implementation's widened multiplication specifically addresses integer-overflow risk. The JavaScript implementation uses `BigInt` when exact large integer arithmetic is required.

## Database Integrity

The PostgreSQL model places mathematical input rules at the database boundary.

The relevant constraints include:

- positive modular values
- non-negative exponents
- positive factorization targets
- positive prime factors
- positive factor exponents

The trigger marks invalid modular requests as rejected.

The processing function locks the selected request with `FOR UPDATE` before changing its workflow state. This prevents concurrent transactions from independently processing the same request state without coordination.

The reporting view translates persisted execution states into operational workflow descriptions.

## Distinct Engineering Perspectives

The five files intentionally solve the same mathematical domain through different implementation models.

| Language | Primary perspective |
|---|---|
| Python | Algorithm library with validation and executable checks |
| JavaScript | Event-driven service with asynchronous processing |
| C++17 | High-performance fixed-width computational engine |
| Java 17 | Enterprise domain model with explicit policies and states |
| PostgreSQL | Persistent relational workflow with database-enforced rules |

The algorithms are shared conceptually, but the implementations are not mechanical translations.

The Python implementation emphasizes compact mathematical composition.

The JavaScript implementation emphasizes asynchronous operation and exact `BigInt` processing.

The C++ implementation emphasizes deterministic bounded-domain arithmetic and overflow control.

The Java implementation emphasizes explicit domain types, policies, and state transitions.

The PostgreSQL implementation emphasizes persistence, constraints, transactions, triggers, and reporting.

## Practical Workflow

A typical computation can be represented as:

`Receive integer inputs`
  
`↓`

`Validate domain constraints`
  
`↓`

`Select algorithm`
  
`↓`

`Perform modular or integer arithmetic`
  
`↓`

`Check mathematical invariants`
  
`↓`

`Persist or return result`

For primality:

`Candidate`
  
`↓`

`Small-value checks`
  
`↓`

`Trial division or Miller-Rabin`
  
`↓`

`Prime / Composite decision`

For modular exponentiation:

`Base + Exponent + Modulus`
  
`↓`

`Normalize base`
  
`↓`

`Process exponent bits`
  
`↓`

`Square and multiply`
  
`↓`

`Return residue`

For modular inversion:

`a + m`
  
`↓`

`Compute gcd(a,m)`
  
`↓`

`gcd = 1?`
  
`├─ No → reject`
  
`└─ Yes → use Bézout coefficient`
  
`↓`

`Normalize inverse`

## Edge Cases

The implementations explicitly account for several boundary conditions.

`n < 2` is never classified as prime.

A modulus of one is mathematically valid for modular exponentiation and produces residue zero.

A zero exponent is valid for non-zero positive moduli.

A modular inverse is rejected when the operands are not coprime.

Factorization terminates when the remaining value is itself prime.

The C++ implementation avoids direct multiplication overflow during modular multiplication.

The JavaScript implementation avoids unsafe `Number` arithmetic for large modular values by switching to `BigInt`.

The Java implementation uses arbitrary-precision `BigInteger` operations for large values.

The PostgreSQL implementation enforces core input constraints at the database level rather than relying only on application validation.

## Educational Structure

The implementations progress from basic arithmetic to composed algorithms.

The fundamental layer contains GCD and modular reduction.

The next layer introduces binary exponentiation and primality testing.

The factorization layer exposes prime structure.

The inverse and totient operations reuse GCD and factorization concepts.

The CRT implementation demonstrates composition of modular inverses, multiplication, and congruence relationships.

The database and service layers then demonstrate how these mathematical operations can be placed inside realistic software workflows.

The resulting artifacts keep mathematical correctness, validation, representation, performance, and failure handling connected rather than treating each algorithm as an isolated example.
