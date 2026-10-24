# Modular Arithmetic: Congruences, Addition, Multiplication, and Powers

## Overview

Modular arithmetic studies integer calculations in which values are identified by their remainders after division by a positive integer called the modulus.

For a modulus \(n > 0\), every integer \(a\) has a unique normalized representative in the range \(0 \leq r < n\). The normalized representative is

\[
r = a \bmod n
\]

For example, \(-17\) has normalized representative \(3\) modulo \(5\), because \(-17 = (-4)\cdot 5 + 3\).

The five source implementations provide different perspectives on the same mathematical system:

- Python models immutable residue classes and implements arithmetic operations with validation.
- JavaScript adds an event-driven service that records successful and failed requests.
- C++17 implements arithmetic using fixed-width unsigned integers and overflow-conscious algorithms.
- Java 17 uses `BigInteger`, explicit domain types, and resource policies.
- PostgreSQL persists arithmetic requests, evaluates them through database functions, and reports successful and failed operations.

## Mathematical foundations

### Congruences

Two integers \(a\) and \(b\) are congruent modulo \(n\) when their difference is divisible by \(n\):

\[
a \equiv b \pmod n
\iff n \mid (a-b)
\]

Equivalently,

\[
a \bmod n = b \bmod n
\]

For example,

\[
17 \equiv 2 \pmod 5
\]

because both integers have remainder \(2\) after normalization.

Congruence is an equivalence relation. It is reflexive, symmetric, and transitive. It partitions the integers into residue classes. For modulus \(5\), the five classes have representatives \(0,1,2,3,4\).

A residue class represents all integers that are congruent modulo the same modulus. Consequently, `Residue(-2, 7)` and `Residue(5, 7)` represent the same class.

### Modular addition

Modular addition combines two values and reduces the result:

\[
(a+b)\bmod n
\]

For example,

\[
(123+(-45))\bmod 17 = 10
\]

The result remains in the normalized range. Addition is associative and commutative, and the zero residue is its identity element.

### Modular multiplication

Modular multiplication computes

\[
(a\cdot b)\bmod n
\]

For example,

\[
(123\cdot456)\bmod97 = 46
\]

The implementation can reduce operands before multiplying because congruence is preserved under addition and multiplication. This property also supports repeated-doubling algorithms when intermediate products need to be controlled.

### Modular powers

Modular exponentiation computes

\[
a^e \bmod n
\]

A direct calculation of \(a^e\) can create extremely large intermediate values. Binary exponentiation instead repeatedly squares the base and halves the exponent. It performs \(O(\log e)\) multiplication steps for a nonnegative exponent \(e\).

For instance,

\[
3^{100}\bmod7 = 4
\]

A negative exponent requires a multiplicative inverse:

\[
a^{-k}\bmod n = (a^{-1})^k\bmod n
\]

The inverse exists precisely when

\[
\gcd(a,n)=1
\]

For example, \(3^{-1}\bmod11=4\), since \(3\cdot4=12\equiv1\pmod{11}\). The value \(6\) has no inverse modulo \(9\), because \(\gcd(6,9)=3\).

## Implementation architecture

The implementations share mathematical rules but make different choices about numeric representation, failure reporting, and operational responsibilities.

| Implementation | Numeric model | Main engineering focus |
|---|---|---|
| Python | Arbitrary-precision integers | Readable algorithms, immutable residue values, and assertions |
| JavaScript | `BigInt` | Event-driven request processing and observer isolation |
| C++17 | `uint64_t` and signed inputs | Fixed-width arithmetic and overflow-aware operations |
| Java 17 | `BigInteger` | Domain modeling, explicit policies, and structured results |
| PostgreSQL | `NUMERIC` | Persistence, constraints, transactional evaluation, and reporting |

## Python implementation

The Python script is a self-contained arithmetic library with an executable test suite.

### Arithmetic functions

- `normalize` converts an integer into its canonical residue.
- `congruent` compares normalized representatives.
- `modular_add` and `modular_multiply` implement residue operations.
- `modular_power` uses binary exponentiation.
- `extended_gcd` returns the greatest common divisor and Bézout coefficients.
- `modular_inverse` uses the extended Euclidean algorithm to find an inverse.
- `modular_sum` reduces each accumulated result rather than retaining an unreduced running total.

`ModularArithmeticError` distinguishes invalid mathematical inputs from ordinary execution.

### Residue objects

The frozen `Residue` dataclass represents a normalized value together with its modulus. Construction validates and normalizes the value. Addition and multiplication reject operands with different moduli, preventing invalid operations between unrelated residue systems.

The class overloads `+`, `*`, and `**`, allowing arithmetic to be expressed using domain objects while keeping the underlying calculations explicit.

### Validation and testing

`run_tests` checks negative inputs, congruences, arithmetic operations, inverses, invalid moduli, and non-invertible values. A bounded set of additional tests compares the custom arithmetic implementations against Python's native integer calculations.

The tests are executable through the script's main entry point. The arithmetic functions can also be imported into other Python programs.

## JavaScript implementation

The JavaScript file uses `BigInt` for exact integer arithmetic. Ordinary JavaScript `Number` values cannot represent every large integer exactly, so they are not suitable for unrestricted modular arithmetic.

### Encapsulation

`Residue` uses private fields for its value and modulus. Its constructor normalizes the value, while its methods enforce equal moduli before combining residues. The object exposes read-only getters instead of allowing callers to modify its internal state.

### Event-driven evaluation

`ArithmeticService` accepts named operations and returns structured results containing a sequence number, operation name, success status, and result or error message.

The service supports event listeners registered through `on`. A returned unsubscribe function removes the listener. Completion and failure events let consumers observe operations without coupling reporting code to the arithmetic functions.

Listener exceptions are caught independently. An observer failure therefore does not invalidate a successful arithmetic calculation or prevent subsequent listeners from running.

### Failure behavior

Invalid operation names and mathematical failures are returned as failed results. The service records the request sequence even when an operation fails, making the order of execution observable.

The implementation uses synchronous arithmetic. Event notifications do not make the calculations asynchronous, and no external packages are required.

## C++17 implementation

The C++ program presents a fixed-width arithmetic engine for applications that need explicit control over integer representation.

### Numeric representation

The implementation uses `uint64_t` for moduli, normalized residues, and nonnegative exponents. Signed input normalization handles negative values without directly negating the minimum representable signed integer.

The `add` function avoids overflowing an unsigned sum by comparing the first operand with the distance to the modulus. `multiply` uses repeated doubling, keeping its reduced operands within the modulus range.

### Exponentiation and inverses

`power` applies binary exponentiation. `inverse` first checks that the operands are coprime, then uses the extended Euclidean algorithm with signed 128-bit intermediate coefficients.

The inverse calculation uses `__int128`, which is supported by common GCC and Clang environments but is not part of standard C++17. The program therefore compiles as C++17 with a compiler that provides this extension.

### Scenario and error handling

`ArithmeticCase` groups named test inputs and their modulus. The main function processes normalization, addition, multiplication, and congruence cases, then demonstrates exponentiation and inversion.

`ModularArithmeticError` represents invalid arithmetic requests. A failed inverse is reported without terminating the remainder of the demonstration, while unexpected top-level exceptions produce a nonzero exit code.

The implementation avoids unnecessary allocation and third-party libraries. Its fixed-width representation is efficient, but callers must ensure values fit the selected types.

## Java 17 implementation

The Java program models modular arithmetic as a service that applies explicit request validation and configurable policies.

### Domain types

`Operation` identifies the supported arithmetic operations. `Outcome` separates successful execution, invalid requests, and mathematical failures.

`ArithmeticRequest` is an immutable record containing the operation, operands, exponent, and modulus. Its compact constructor validates required values and enforces operation-specific operand requirements.

`ArithmeticResult` is another record. It carries the outcome, an optional numerical result, and a descriptive message.

### Policy evaluation

`ArithmeticPolicy` defines a contract for request acceptance. `ResourcePolicy` limits operand sizes, modulus size, and exponent size using `BigInteger.bitLength()`.

`ModularArithmeticService` evaluates every configured policy before executing an operation. A single rejection prevents calculation. This structure allows different deployments to impose different resource limits without rewriting the arithmetic algorithms.

### Exact arithmetic

`BigInteger` provides arbitrary-precision integers. Its `mod` method returns a nonnegative residue for a positive modulus, `modInverse` computes modular inverses, and `modPow` performs modular exponentiation.

Negative exponents are handled by calculating the modular inverse before exponentiation. A missing inverse becomes a structured failure rather than an unhandled application error.

The service is stateless across requests. It can be reused by application components, while resource policies help limit computationally expensive inputs. These policies do not replace authentication, request-rate limits, or application-level authorization.

## PostgreSQL implementation

The SQL script turns modular arithmetic into a persistent request-processing workflow. It creates the `modular_lab` schema and uses PostgreSQL functions, relational constraints, indexes, and a reporting view.

### Relational model

`modulus_registry` stores supported moduli and their descriptions. Each modulus is positive and unique.

`arithmetic_requests` stores individual operations, their operands, their modulus reference, and their execution state. A foreign key connects each request to a registered modulus.

The `required_operands` constraint ensures that each operation has the appropriate inputs. The `result_state` constraint ties the request status to its result, error message, and completion timestamp.

A pending request has no result or error. A successful request has a result and completion timestamp. A failed request has an error message and completion timestamp.

### Database functions

`normalize_mod` produces canonical residues and rejects invalid integer operands or moduli.

`gcd_integer` implements the Euclidean algorithm. `inverse_mod` uses extended Euclid to calculate an inverse and rejects inputs whose greatest common divisor is not one.

`power_mod` implements binary exponentiation. For negative exponents, it first computes the inverse. It therefore rejects negative powers when the base is not invertible modulo the selected modulus.

`evaluate_request` locks a request with `FOR UPDATE`, checks that it is pending, and executes the appropriate operation. Successful calculations are persisted as successful results. Domain errors are recorded as failed requests.

### Transactional behavior

The demonstration inserts sample moduli and requests, then evaluates pending requests in identifier order. The final transaction commits the resulting states and makes the reporting queries available.

The row lock prevents two concurrent workers from evaluating the same request simultaneously. The state check prevents an already processed request from being processed again.

The exception handler inside `evaluate_request` records arithmetic failures. Database errors outside that protected evaluation block can still abort the surrounding transaction.

### Reporting and query performance

The `request_report` view joins each request to its modulus. The script uses it for request retrieval and result inspection.

The aggregation query groups requests by operation and status, making failure patterns visible. The eligibility query uses `gcd_integer` to identify whether inverses exist for inverse operations and negative powers.

The recent-request index supports time-ordered retrieval. The composite status-and-operation index supports filtered operational reports. The primary keys and unique modulus constraint provide their own indexes.

The database model records arithmetic requests and outcomes. It is not a general symbolic mathematics engine, and its numeric precision and scale must be selected carefully for a specific deployment.

## Cross-implementation consistency

The examples intentionally use the same mathematical rules while reflecting each language's capabilities.

- Negative values are normalized into the range from zero through modulus minus one.
- Congruence compares residue classes, not the original integer representations.
- Addition and multiplication reduce their results modulo the modulus.
- Binary exponentiation avoids calculating a full, potentially enormous power.
- Inversion requires coprimality between the value and modulus.
- A negative exponent requires an inverse.
- Invalid moduli are rejected before arithmetic is performed.
- Failures are exposed through exceptions or structured results, depending on the implementation.

The tests include cases that succeed and cases that must fail. This is important because modular arithmetic has domain restrictions that cannot be captured by calculating a remainder alone.

## Complexity and operational limitations

Let \(k\) denote the bit length of an integer operand and \(e\) a nonnegative exponent.

| Operation | Algorithmic behavior |
|---|---|
| Normalization | One remainder operation |
| Congruence | Two normalizations and a comparison |
| Addition | One reduced addition |
| Multiplication | \(O(\log b)\) doubling steps for the repeated-doubling implementations |
| Exponentiation | \(O(\log e)\) modular multiplication steps |
| Extended Euclid | A number of division steps logarithmic in the operand magnitudes |
| Database reporting | Depends on the number of matching requests and available indexes |

These operation counts do not imply constant execution time. Big-integer multiplication and division become more expensive as operands grow. Database queries also depend on row counts, transaction contention, and query plans.

The Python and JavaScript repeated-doubling multiplication routines use more iterations than native multiplication for ordinary small operands. They are included to illustrate bounded intermediate arithmetic. Java's `BigInteger` methods and the C++ implementation's arithmetic strategy make different performance trade-offs.

## Security considerations

Modular arithmetic is important in cryptography, but these educational implementations are not complete cryptographic systems.

- Do not use the routines as substitutes for vetted cryptographic libraries.
- Do not assume execution time is independent of secret values. The implementations are not designed to provide constant-time guarantees.
- Apply input-size and execution-time limits when arithmetic requests can come from untrusted callers.
- Validate input types and reject invalid moduli and undefined inverses.
- Avoid exposing detailed internal errors to unauthorized external clients.
- Protect database access with suitable privileges and application-level authorization.
- Treat the Java resource policy as a computational safeguard, not an access-control mechanism.
- Consider numeric limits, transaction isolation, and denial-of-service risks when deploying database-backed calculations.

Correct modular arithmetic is a necessary component of many cryptographic algorithms, but secure cryptographic implementations require additional properties, careful protocol design, and dedicated security review.
