# Prime Numbers: Factorization, Sieve Methods, and Prime Distributions

## Scope

This project studies three connected but distinct aspects of prime-number computation:

- **Prime factorization** decomposes a composite integer into powers of prime factors.
- **Sieve methods** generate many primes efficiently by marking composite candidates.
- **Prime distributions** examine how frequently primes occur and how gaps between consecutive primes behave.

The implementations use the same mathematical foundations but deliberately use different computational perspectives. Python emphasizes a reusable analysis toolkit, JavaScript emphasizes exact `BigInt` processing and asynchronous segmented analysis, C++ implements a compact computational engine, Java models a domain-oriented prime-analysis service, and PostgreSQL treats prime information as relational data with database-enforced integrity.

## Mathematical model

A prime number is an integer greater than one with exactly two positive divisors: one and itself.

The fundamental theorem of arithmetic states that every integer greater than one has a unique prime factorization:

`n = p₁^e₁ × p₂^e₂ × ... × pₖ^eₖ`

For example:

`360 = 2³ × 3² × 5`

The exponent records how many times a prime divides the number. Factorization therefore provides more information than a simple primality test.

Prime generation addresses a different problem. Instead of examining one number and testing possible divisors, a sieve works over a range of integers and eliminates known composite values. This makes sieve methods particularly effective when many primality results are required.

Prime distribution studies the locations of primes rather than the factors of individual composite values. If `π(x)` denotes the number of primes less than or equal to `x`, the prime number theorem gives the asymptotic approximation:

`π(x) ~ x / ln(x)`

The corresponding approximate local density of primes near a large value `x` is:

`1 / ln(x)`

This is an asymptotic approximation, not an exact formula for the number of primes in a particular finite interval.

## Relationship between the three areas

The computational relationship can be represented as:

`Integer`
→ `Primality / Factorization`

`Integer Range`
→ `Sieve`
→ `Prime Set`

`Prime Set`
→ `Counting / Density / Gaps`
→ `Distribution Analysis`

Factorization and sieving solve different computational problems. Trial division can factor a single moderate-sized integer, while the sieve amortizes work across a complete interval. Distribution analysis normally consumes a generated prime sequence rather than generating primes through a separate mathematical process.

## Python implementation

The Python script provides a complete analysis workflow.

`is_prime()` performs deterministic trial division for values within Python's ordinary integer representation. Even divisors are handled separately, after which only odd candidates up to the square root are tested.

`prime_factorization()` performs repeated division. Removing all factors of two first reduces the subsequent search space to odd divisors. The factorization is stored as a dictionary mapping each prime to its exponent.

`verify_factorization()` reconstructs the integer from the factor dictionary. This provides an executable integrity check instead of assuming that the factorization algorithm is correct.

`sieve_of_eratosthenes()` uses a `bytearray` to represent composite candidates. Starting from each discovered prime, multiples beginning at its square are marked. Earlier multiples must already have been handled by smaller prime factors.

`segmented_sieve()` separates prime generation into two ranges. It first generates base primes through the square root of the upper bound and then marks composite values only inside the requested interval. This avoids allocating a full sieve from zero to a potentially large upper bound.

`analyze_prime_distribution()` calculates prime count, empirical density, average consecutive-prime gap, and largest observed gap. It also calculates the `1 / ln(x)` density estimate so finite observations can be compared with the asymptotic model.

The randomized factorization test generates additional integers and verifies that their reconstructed values match the originals. This tests the algorithm beyond a few fixed examples.

The implementation is intentionally dependency-free. Python's arbitrary-precision integers are useful for factorization because integer overflow is not an ordinary concern, although computation time can still become prohibitive for large difficult-to-factor integers.

## JavaScript implementation

The JavaScript implementation uses two numerical models.

Normal `Number` values are restricted to `Number.MAX_SAFE_INTEGER` for factorization. This prevents silent loss of integer precision. The script rejects values outside that exact range rather than producing unreliable results.

For larger exact integers, `BigInt` is used. `bigIntPrimeFactorization()` therefore demonstrates a JavaScript-specific distinction between floating-point numeric values and arbitrary-size integer values.

The sieve uses `Uint8Array` for compact typed storage. Each array position represents whether a candidate is composite.

The segmented sieve follows the same mathematical idea as the Python implementation but is organized around JavaScript's runtime model.

`analyzeInBatches()` demonstrates asynchronous processing. Each range is processed independently and `setImmediate()` yields control back to the Node.js event loop. This matters when a large prime-analysis workload must coexist with other event-driven application work.

The asynchronous workflow does not make the mathematical computation faster by itself. Its purpose is to prevent a long synchronous loop from monopolizing the event loop.

## C++ implementation

The C++ program models prime computation as a performance-oriented numerical case study.

`std::vector<bool>` is used for sieve state because the standard specialization stores Boolean values compactly. The implementation also uses integer division in expressions such as `divisor <= n / divisor` to avoid overflow that could occur with `divisor * divisor`.

The C++ factorization uses `std::map` so factors remain ordered. The resulting representation makes mathematical output deterministic.

The segmented sieve stores only the requested interval plus the base primes needed to identify composites. Its memory requirement is approximately proportional to:

`O(sqrt(high) + high - low + 1)`

A complete sieve through `high` instead requires storage proportional to `high`.

The implementation uses `unsigned __int128` during factorization verification. This is an implementation-specific wider integer type available on common GCC and Clang environments. It protects the reconstruction check from overflowing a 64-bit value before comparison.

The program also demonstrates exception-based failure handling for invalid factorization requests and malformed ranges.

## Java implementation

The Java implementation uses explicit domain modeling.

`PrimeRange` is a record representing an immutable validated interval. Invalid ranges are rejected during construction rather than being passed deeper into the system.

`DistributionReport` is another record that captures calculated metrics as an immutable result.

`PrimeRepository` defines the prime-generation contract, while `SievePrimeRepository` provides the concrete sieve and segmented-sieve algorithms. This separation allows the computational source to be replaced without changing the service-level analysis rules.

`AnalysisPolicy` makes supported operations explicit. `PrimeService` validates the active policy before performing factorization or distribution analysis. This models a controlled service boundary rather than treating every operation as an unrestricted utility function.

Java collections are used for factor maps and prime sequences. Streams are used specifically where they improve aggregation of prime gaps rather than being introduced merely for syntactic variation.

The enterprise-oriented design makes validation and failure states explicit:

- Values below two cannot be factorized as positive prime products.
- Distribution analysis requires a meaningful upper bound.
- Prime factors are independently validated.
- Disabled analysis policies cause explicit service-level failures.

## PostgreSQL implementation

The PostgreSQL model represents prime computation as persistent relational information.

The main entities are:

| Table | Purpose |
| --- | --- |
| `prime_numbers` | Stores verified prime values |
| `factorizations` | Represents a factorization operation for an integer |
| `factor_components` | Stores each prime factor and exponent |
| `prime_distribution_runs` | Stores aggregate distribution measurements |
| `prime_gaps` | Stores consecutive-prime gap observations |

The relationships preserve the distinction between an integer being analyzed and the individual prime components of its factorization.

The `prime_numbers` table contains a database-level `CHECK` constraint using the immutable `is_prime()` function. This means the database does not merely store values that application code claims are prime.

`factor_components` has a composite primary key consisting of the factorized number and prime factor. This prevents duplicate factor rows for the same prime.

The positive-exponent constraint prevents meaningless factor entries such as exponent zero.

`factorize_number()` is a PostgreSQL set-returning function. It produces factor rows that can be consumed directly by SQL queries.

`populate_factorization()` creates the factorization records and their associated prime components. The verification function reconstructs the mathematical value from the stored factors.

The trigger keeps the `verified` state synchronized when factor components change. The design illustrates a database-enforced integrity boundary rather than depending entirely on client-side validation.

## Sieve mechanics

The classical Sieve of Eratosthenes begins with candidate integers and repeatedly marks multiples of discovered primes.

For a prime `p`, marking begins at `p²` because every smaller multiple of `p` has a smaller prime factor and has therefore already been marked.

For a limit `n`, the classical sieve has approximately:

- Time complexity: `O(n log log n)`
- Space complexity: `O(n)`

Its major strength is high throughput when many primes up to one upper bound are required.

A segmented sieve changes the memory trade-off. Base primes up to `sqrt(high)` are generated once, then only a selected interval is represented. This is particularly useful for large ranges where allocating an array for every integer below the upper bound is undesirable.

## Prime factorization mechanics

Trial-division factorization repeatedly tests candidate divisors.

For an integer `n`, once a divisor `p` is found, every occurrence of `p` is removed. The process continues until the remaining value is one or a prime greater than one.

Testing divisors only while:

`d² <= remaining`

is sufficient. If the remaining composite value had no divisor at or below its square root, it could not be composite.

The practical performance of trial division depends strongly on the number being factored. It is suitable for moderate integers and educational implementations, but it is not an appropriate general-purpose method for factoring arbitrary cryptographic-size integers.

## Prime distributions

The scripts calculate the empirical prime density:

`number of primes in range / number of candidate integers`

and compare it with the prime number theorem's local approximation:

`1 / ln(x)`

They also calculate gaps between consecutive primes:

`gapᵢ = pᵢ₊₁ - pᵢ`

A gap is an observed property of a finite prime sequence. A large gap does not imply that primes stop occurring after that point, and a small gap does not imply a uniform local density.

The distribution analysis therefore treats measured counts and gaps as empirical data rather than replacing exact computation with the asymptotic estimate.

## Validation and failure handling

The implementations deliberately reject invalid mathematical states.

Values below two are not considered prime and cannot have the positive prime factorization modeled here.

Factorization validation checks that every stored factor is prime, every exponent is positive, and the product of all prime powers reconstructs the original integer.

Sieve boundaries are validated before allocation. A reversed range is rejected instead of producing an ambiguous result.

The JavaScript implementation rejects unsafe `Number` integers and provides `BigInt` for exact larger integer input.

The C++ implementation guards arithmetic expressions that could overflow and reports operational errors through exceptions.

The PostgreSQL model adds constraints and transactional behavior so invalid records cannot silently become persistent database state.

## Performance considerations

A single primality test by trial division takes approximately `O(sqrt(n))` divisor checks in the worst case.

Trial-division factorization has similar worst-case behavior for a single integer, although repeatedly removing small factors can make many practical cases much faster.

The classical sieve is much more efficient when a complete prime set through `n` is required:

`O(n log log n)` time and `O(n)` space.

The segmented sieve retains approximately the same aggregate marking behavior while reducing memory usage for a selected interval.

Prime distribution calculations are inexpensive once the prime sequence exists. Counting primes is linear in the generated sequence, and calculating consecutive gaps is also linear in the number of primes.

Memory can become the dominant constraint for very large ordinary sieves. Segmentation addresses this by limiting the active composite array to a manageable interval.

## Security and production considerations

Prime-number computation is not automatically cryptographic just because it uses primes.

The trial-division implementations are deterministic educational and analytical tools. They should not be presented as replacements for cryptographic prime-generation algorithms.

For security-sensitive systems, exact integer ranges, random-number quality, side-channel behavior, and cryptographic algorithms require separate engineering controls.

The JavaScript implementation's `Number` validation is especially important because integer precision errors can silently corrupt factorization results.

Database functions should also be granted only the permissions required by the application. The PostgreSQL model demonstrates integrity enforcement, but authorization, auditing, connection security, and operational backup policies remain deployment concerns.

## Edge cases and limitations

The smallest prime is `2`. There are no primes below it.

Prime factorization of `1` is intentionally rejected because the factorization model requires an integer whose prime factors multiply to the target.

A prime input produces a single factor with exponent one.

A power such as `1024` produces a single repeated prime factor:

`1024 = 2¹⁰`

Numbers containing several distinct prime factors demonstrate the separation between factor identity and exponent.

A finite prime list may have no gap when it contains fewer than two primes. The distribution implementations therefore return a zero largest gap and zero average gap for that case.

The prime number theorem describes asymptotic behavior. Its estimate should not be interpreted as an exact prime count for small or medium values.

## Executable workflow

The implementations follow a common mathematical workflow while retaining language-specific designs:

`Input integer`
→ `Validation`
→ `Primality or factorization`

`Upper bound`
→ `Sieve`
→ `Prime sequence`

`Prime sequence`
→ `Count`
→ `Density`
→ `Consecutive gaps`
→ `Distribution report`

For large intervals:

`Upper interval`
→ `Base primes <= sqrt(high)`
→ `Segmented marking`
→ `Primes in requested interval`

This separation makes the distinction between individual-number analysis, bulk prime generation, and statistical examination of generated primes explicit.
