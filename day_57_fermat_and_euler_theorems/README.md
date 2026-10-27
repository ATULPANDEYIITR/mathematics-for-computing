# Fermat and Euler Theorems

## Scope

This project implements the core computational ideas behind Fermat's Little Theorem, Euler's Theorem, and Euler's phi function.

The four mathematical mechanisms are deliberately separated:

| Mechanism | Role |
|---|---|
| Euler phi function `phi(n)` | Counts integers from `1` through `n` that are coprime to `n` |
| Fermat's Little Theorem | For prime `p` and `gcd(a,p)=1`, establishes `a^(p-1) ≡ 1 mod p` |
| Euler's Theorem | For `gcd(a,n)=1`, establishes `a^phi(n) ≡ 1 mod n` |
| Modular inverse | Finds `x` such that `a*x ≡ 1 mod n` when `gcd(a,n)=1` |

The implementations use exact integer arithmetic and include validation for invalid moduli, composite inputs to Fermat's theorem, non-coprime values, and non-invertible residues.

## Mathematical Relationship

Euler's theorem generalizes the exponent reduction represented by Fermat's Little Theorem.

For a prime `p`:

`phi(p) = p - 1`

Therefore Euler's theorem becomes:

`a^phi(p) ≡ 1 mod p`

which is the same congruence supplied by Fermat's Little Theorem for values of `a` not divisible by `p`.

The important distinction is the modulus condition:

- Fermat's Little Theorem uses a prime modulus.
- Euler's Theorem works with any positive modulus when the base is coprime to that modulus.
- Euler's phi function determines the exponent used by Euler's theorem.
- A modular inverse exists when the base and modulus have greatest common divisor `1`.

## Euler Phi Function

For a positive integer `n`, Euler's phi function counts values in the range `1` through `n` that are relatively prime to `n`.

Examples:

| `n` | `phi(n)` | Coprime values |
|---:|---:|---|
| 5 | 4 | 1, 2, 3, 4 |
| 8 | 4 | 1, 3, 5, 7 |
| 12 | 4 | 1, 5, 7, 11 |
| 15 | 8 | 1, 2, 4, 7, 8, 11, 13, 14 |

The implementations calculate phi from the distinct prime factors of `n` using:

`phi(n) = n * product(1 - 1/p)`

for each distinct prime factor `p` of `n`.

The algorithms first remove repeated factors, then apply each factor exactly once.

## Fermat's Little Theorem

The Python, JavaScript, C++17, and Java 17 implementations validate prime moduli before applying Fermat's theorem.

For a prime `p` and `p` not dividing `a`:

`a^(p-1) mod p = 1`

The examples test several small prime moduli and use binary modular exponentiation rather than constructing the potentially enormous integer `a^(p-1)`.

The implementation rejects a composite modulus for the theorem-specific operation instead of silently treating Euler's theorem and Fermat's theorem as interchangeable.

## Euler's Theorem

Euler's theorem uses the phi function directly.

For:

`gcd(a,n) = 1`

the implementation verifies:

`a^phi(n) mod n = 1`

A non-coprime base is explicitly reported as outside the theorem's applicability conditions.

For example, `5` and `12` are coprime, so Euler's theorem applies. The pair `6` and `12` is not coprime, so the theorem does not provide the stated congruence.

This distinction is important because Euler's theorem is conditional on relative primality rather than merely on the modulus being positive.

## Binary Modular Exponentiation

All executable implementations use repeated squaring for modular exponentiation.

The basic state transition is:

`result = result * base mod modulus`

when the current exponent bit is `1`, followed by:

`base = base * base mod modulus`

and division of the exponent by two.

This reduces exponentiation from a number of multiplications proportional to the exponent itself to approximately `O(log exponent)` modular multiplications.

The technique also avoids constructing the complete power before applying the modulus.

## Modular Inverses

The project computes modular inverses with the extended Euclidean algorithm.

For:

`a*x ≡ 1 mod n`

an inverse exists exactly when:

`gcd(a,n) = 1`

The examples compare the extended-Euclidean result with the Euler-theorem expression:

`a^(-1) ≡ a^(phi(n)-1) mod n`

when `a` and `n` are coprime.

For example:

`3^(-1) mod 10 = 7`

because:

`3 * 7 mod 10 = 1`

A pair such as `6` and `15` is rejected because their greatest common divisor is `3`.

## RSA-Style Relationship

The source files include a small RSA-style mathematical workflow to show how the theorems connect to modular inverses.

The example uses:

- `p = 61`
- `q = 53`
- `n = p*q = 3233`
- `phi(n) = 3120`
- `e = 17`
- `d = 2753`

The private exponent satisfies:

`e*d ≡ 1 mod phi(n)`

A message is exponentiated with the public exponent and then with the private exponent. The recovered message is checked against the original.

This is a mathematical demonstration, not a production cryptographic implementation.

## Python Implementation

The Python file provides a self-contained number-theory module implemented with standard-library functionality.

Key components include:

| Component | Purpose |
|---|---|
| `mod_pow` | Binary modular exponentiation |
| `phi` | Euler phi calculation |
| `fermat_little_theorem` | Prime-modulus Fermat validation |
| `euler_theorem` | Coprime-modulus Euler validation |
| `modular_inverse` | Extended Euclidean inverse |
| `inverse_using_euler` | Euler-theorem inverse calculation |
| `RSAExample` | Encapsulates an RSA-style mathematical workflow |

The script uses `dataclass` for the RSA example and assertions for internal consistency checks.

The examples also exercise invalid composite moduli and non-invertible values.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library facilities and `BigInt` so that integer arithmetic is not forced through JavaScript's floating-point `Number` representation.

The file separates several responsibilities:

- `gcd` handles greatest common divisors.
- `modPow` performs exact modular exponentiation.
- `isPrime` validates Fermat inputs.
- `phi` calculates Euler's totient.
- `extendedGcd` provides inverse calculation.
- `RepositoryMathDemo` demonstrates asynchronous event-driven evaluation and records evaluation events.
- The main workflow validates successful and failing cases.

`BigInt` values are used consistently for mathematical inputs, preventing accidental loss of integer precision for values outside the exact integer range of ordinary JavaScript numbers.

The Node.js `crypto` module is used only to generate an audit identifier. It is not used to implement the mathematical operations.

## C++17 Implementation

The C++17 program models the mathematical workflow as a technical case study.

It uses:

- `struct` types for mathematical results and policies.
- STL vectors and pairs for test cases.
- Exception handling for invalid inputs.
- Assertions for theorem invariants.
- Explicit repository-style policy validation around theorem checks.

The `RepositoryGovernance` structure evaluates a collection of prime moduli with Fermat's theorem and composite or general moduli with Euler's theorem.

The implementation uses unsigned 64-bit integers for the educational parameter sizes. It explicitly notes that production cryptographic arithmetic needs overflow-safe multiplication and additional side-channel protections.

## Java 17 Implementation

The Java implementation uses explicit enterprise-style domain boundaries.

The principal components are:

| Type | Responsibility |
|---|---|
| `Theorem` | Enumerates supported theorem policies |
| `ModularEvaluation` | Immutable evaluation result using a record |
| `NumberTheoryException` | Domain-specific failure type |
| `NumberTheoryService` | Core arithmetic and theorem operations |
| `RepositoryGovernanceService` | Evaluates a collection of modulus policies |
| `RsaStyleWorkflow` | Encapsulates RSA-style state and transitions |

The service layer distinguishes theorem applicability from theorem validity.

For example, a non-coprime pair can be represented as not eligible for Euler's theorem rather than incorrectly being represented as a failed mathematical theorem.

The RSA-style class validates its prime factors and public exponent before calculating the private exponent.

## PostgreSQL Model

The PostgreSQL script represents the mathematical domain relationally.

The main entities are:

| Table or object | Purpose |
|---|---|
| `number_sets` | Stores classified mathematical inputs |
| `theorem_evaluations` | Records theorem evaluation results and applicability |
| `modular_inverses` | Stores validated modular inverse relationships |
| `phi_report` | Reports phi values for stored numbers |
| `merge_eligibility_style_report` | Presents theorem evaluation states |
| `gcd_bigint` | Database implementation of the Euclidean algorithm |
| `mod_pow` | Database implementation of repeated-squaring exponentiation |
| `is_prime` | Trial-division primality test |
| `euler_phi` | Prime-factor-based phi calculation |
| `modular_inverse` | Extended Euclidean inverse |
| `evaluate_theorem` | Unified theorem evaluation function |

The database applies primary keys, foreign keys, uniqueness rules, positive-value checks, and inverse-value validation.

The `validate_inverse` trigger prevents an inconsistent inverse from being stored as valid. A stored inverse must satisfy:

`a*x mod n = 1`

The SQL script also demonstrates transaction boundaries when inserting an inverse derived from the extended Euclidean calculation.

## Relational Workflow

The database workflow follows the mathematical dependency chain:

`Number`
→ `Prime Factors`
→ `Euler Phi`
→ `Coprimality`
→ `Theorem Applicability`
→ `Modular Exponentiation`
→ `Theorem Result`
→ `Inverse or Cryptographic Use`

The data model keeps the original base, modulus, gcd, phi value, exponent, modular result, applicability, and final theorem state so that a result can be inspected rather than treated as an opaque Boolean.

## Edge Cases

The implementations deliberately handle several failure conditions.

| Case | Treatment |
|---|---|
| `n <= 0` for phi | Rejected |
| Modulus `0` | Rejected |
| Negative exponent | Rejected |
| Composite modulus for Fermat-specific validation | Rejected |
| Base not coprime to modulus for Euler's theorem | Marked not applicable |
| Non-invertible residue | Rejected or represented with no inverse |
| Invalid RSA-style prime factors | Rejected |
| Public exponent not coprime to `phi(n)` | Rejected |
| Message outside RSA-style modulus range | Rejected |

These conditions distinguish mathematical invalidity from a theorem simply not applying to a particular input.

## Performance

Binary modular exponentiation requires `O(log e)` iterations for exponent `e`.

The phi implementation factors the input through trial division. Its practical cost depends strongly on the size and factor structure of the input.

The primality checks in the educational implementations use trial division up to the square root of the candidate. This is appropriate for small demonstration values but is not a scalable primality-testing strategy for cryptographic-sized integers.

The PostgreSQL functions perform the same mathematical operations inside the database, which is useful for reproducible relational evaluation but should not be interpreted as a replacement for specialized arbitrary-precision cryptographic libraries.

## Security Considerations

The mathematical properties implemented here are fundamental to public-key cryptography, but the programs are not production cryptographic libraries.

Important limitations include:

- Small demonstration primes are intentionally insecure.
- Textbook RSA lacks secure padding.
- Trial division is unsuitable for generating or validating cryptographic primes at production scale.
- Integer multiplication may overflow fixed-width C++ and Java types for sufficiently large operands.
- Modular exponentiation implementations shown here are not designed as constant-time cryptographic primitives.
- Secure cryptographic systems require carefully generated parameters and established algorithms.
- Real applications should use vetted cryptographic providers rather than constructing cryptographic protocols from these educational functions.

The security value of the implementation is therefore in understanding the mathematical dependencies and failure conditions, not in deploying the example RSA workflow for confidential data.

## Conceptual Distinctions

The project maintains the following distinctions:

| Concept | Question answered |
|---|---|
| Euler phi function | How many residues are relatively prime to `n`? |
| Fermat's Little Theorem | What exponent identity holds for a prime modulus? |
| Euler's Theorem | What exponent identity holds for a coprime residue modulo any positive `n`? |
| Modular inverse | Which value reverses multiplication modulo `n`? |
| Modular exponentiation | How can large powers be evaluated efficiently modulo `n`? |

These mechanisms are related, but each has a separate mathematical condition and computational purpose.

## Practical Workflow

A typical evaluation proceeds as follows:

`Choose n`
→ `Factor or analyze n`
→ `Calculate phi(n)`
→ `Choose a`
→ `Calculate gcd(a,n)`
→ `Check theorem applicability`
→ `Perform modular exponentiation`
→ `Validate congruence`
→ `Use inverse when gcd(a,n)=1`

For a prime modulus, Fermat's theorem provides the exponent `p-1`.

For a general modulus with a coprime base, Euler's theorem provides the exponent `phi(n)`.

For inversion, the extended Euclidean algorithm provides the inverse directly, while Euler's theorem supplies an alternative exponentiation-based construction when the coprimality condition holds.

## Files

| File | Main implementation |
|---|---|
| Python | Functional number-theory toolkit, validation, dataclass-based RSA-style workflow |
| JavaScript | BigInt arithmetic, asynchronous evaluation, event recording, validation |
| C++17 | STL-based mathematical case study and policy evaluation engine |
| Java 17 | Domain-oriented service model with records, enums, exceptions, and explicit workflow state |
| PostgreSQL | Relational number-theory model with functions, constraints, triggers, views, transactions, and reports |

## Educational Coverage

The five implementations collectively cover:

- Greatest common divisor
- Prime validation
- Euler's phi function
- Reduced residue systems
- Fermat's Little Theorem
- Euler's Theorem
- Binary modular exponentiation
- Extended Euclidean algorithm
- Modular inverses
- The relationship between `p-1` and `phi(p)`
- RSA-style exponent relationships
- Validation and failure handling
- Relational storage of mathematical evaluations
- Performance trade-offs
- Cryptographic implementation limitations
