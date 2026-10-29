# Cryptographic Mathematics: RSA, Modular Exponentiation, and Repository Governance

## Scope

This project studies the mathematical foundation of RSA through executable implementations in Python, JavaScript, C++17, Java 17, and PostgreSQL.

The central mathematical chain is:

`p, q → n = pq → φ(n) = (p-1)(q-1) → e → d = e⁻¹ mod φ(n)`

Encryption uses:

`c = mᵉ mod n`

Decryption uses:

`m = cᵈ mod n`

The implementations expose modular arithmetic, modular inverses, repeated-squaring exponentiation, prime generation, RSA key construction, validation, integer encryption and decryption, and Chinese Remainder Theorem based decryption.

The repository-governance scenario is used as a separate engineering case study in the C++ and Java implementations and in the relational model. It does not change the RSA mathematics.

## Mathematical Model

RSA begins with two distinct prime numbers `p` and `q`.

The modulus is:

`n = p × q`

Euler's totient for distinct primes is:

`φ(n) = (p - 1)(q - 1)`

The public exponent `e` must satisfy:

`gcd(e, φ(n)) = 1`

The private exponent `d` is the modular inverse of `e`:

`ed ≡ 1 (mod φ(n))`

The public key is `(n, e)`.

The private key contains `d` and, in practical implementations, the prime factors and related CRT parameters.

For a valid message representative `m` satisfying `0 ≤ m < n`:

`c = mᵉ mod n`

and:

`m = cᵈ mod n`

The correctness depends on the relationship between `e`, `d`, and the factorization of `n`.

## Modular Exponentiation

Directly calculating `aᵇ` before reducing modulo `n` creates unnecessarily large intermediate values.

The implementations use binary exponentiation:

1. Start with result `1`.
2. Reduce the base modulo `n`.
3. Inspect the lowest exponent bit.
4. Multiply the result by the current base when that bit is set.
5. Square the base modulo `n`.
6. Shift the exponent right.
7. Continue until the exponent becomes zero.

The number of multiplication stages is proportional to `log₂(b)` rather than `b`.

Python implements this algorithm explicitly with arbitrary-precision integers. JavaScript uses `BigInt`. C++17 uses `unsigned __int128` for safe multiplication while keeping the demonstration modulus within the 64-bit range. Java uses `BigInteger`. PostgreSQL uses `NUMERIC` so the database implementation does not depend on fixed-width machine arithmetic.

## Extended Euclidean Algorithm

The extended Euclidean algorithm produces integers `x` and `y` satisfying:

`ax + by = gcd(a,b)`

When `gcd(a,m) = 1`, the coefficient `x` gives the modular inverse:

`a⁻¹ ≡ x mod m`

The project validates the classic example:

`17⁻¹ mod 3120 = 2753`

because:

`17 × 2753 = 46801`

and:

`46801 mod 3120 = 1`.

RSA uses this operation when deriving `d` from `e` and `φ(n)`.

## Prime Generation

The Python, JavaScript, C++17, and Java implementations generate probable primes for the educational key-generation workflow.

Python, JavaScript, and C++17 expose Miller-Rabin style primality testing. Java delegates probable-prime testing to `BigInteger`, which provides an established arbitrary-precision implementation.

A probable-prime test does not mean that a demonstration implementation should be treated as a complete production key-generation system. Production cryptographic systems require carefully reviewed random generation, approved key sizes, side-channel protections, secure parameter selection, and standardized cryptographic padding.

## RSA Key Construction

The generated key pair follows these stages:

`p, q`
→ calculate `n`
→ calculate `φ(n)`
→ select `e = 65537`
→ verify `gcd(e, φ(n)) = 1`
→ calculate `d = e⁻¹ mod φ(n)`
→ validate `ed mod φ(n) = 1`

The public key contains `n` and `e`.

The private representation retains `d`, `p`, `q`, and `φ(n)` because those values are useful for validation and CRT-based decryption.

The source programs deliberately expose the mathematical values so the relationship between the parameters can be inspected.

## Chinese Remainder Theorem

The Python, JavaScript, C++17, and Java implementations include CRT-based decryption.

Instead of computing:

`cᵈ mod n`

directly, the private exponent is reduced separately:

`dₚ = d mod (p-1)`

`dq = d mod (q-1)`

Then:

`mₚ = cᵈᵖ mod p`

`m_q = cᵈᑫ mod q`

The two residues are recombined into a result modulo `n`.

This can substantially reduce the cost of private-key operations because calculations are performed modulo the smaller prime factors.

CRT reconstruction also creates an important implementation concern: incorrect recombination can produce a mathematically invalid result. The implementations therefore compare CRT decryption with ordinary modular exponentiation during validation.

## Integer and Text Boundaries

RSA textbook arithmetic operates on integer representatives.

Every implementation validates:

`0 ≤ m < n`

before encryption.

This boundary is important because modular RSA does not accept an arbitrary integer outside the representative range as a distinct message.

The Python implementation also converts UTF-8 text to an integer and back for a small demonstration. The JavaScript implementation performs a similar conversion using `Buffer`.

This is intentionally separate from production message encryption. Real RSA encryption does not normally encrypt arbitrary application text directly with textbook RSA.

## Security Boundary

The source files demonstrate RSA mathematics rather than a complete secure cryptographic protocol.

The implementations intentionally expose textbook RSA operations so that the algebra is observable.

Textbook RSA has important security limitations. Deterministic encryption leaks equality of plaintext representatives and does not provide the semantic-security properties expected from modern public-key encryption.

Production RSA encryption normally uses standardized padding such as RSA-OAEP. Signature systems use appropriate signature padding and verification procedures rather than treating encryption and signatures as interchangeable operations.

Production systems also require:

- cryptographically secure random number generation
- sufficiently large RSA moduli
- secure private-key storage
- side-channel protections
- strict key validation
- standardized padding
- careful error handling
- protection against fault attacks
- controlled serialization of key material

The small parameters in the C++ demonstration exist to keep the arithmetic compatible with a compact standalone program. They are not production security parameters.

## Python Implementation

The Python file models the mathematics directly with standard-library facilities.

Important mechanisms include:

- `dataclass` records for public and private key material
- `extended_gcd` for Bézout coefficients
- `mod_inverse` for computing `d`
- `modular_pow` for binary exponentiation
- Miller-Rabin style probable-prime testing
- random prime generation
- RSA key construction
- ordinary decryption
- CRT-optimized decryption
- UTF-8 integer conversion
- explicit validation exceptions
- assertions for arithmetic and round-trip correctness

The program validates both ordinary and CRT decryption against the original message.

Its explicit modular exponentiation implementation makes the computational structure visible while still using Python's built-in `pow` internally where appropriate for primality testing and CRT operations.

## JavaScript Implementation

The JavaScript file uses Node.js standard-library functionality and `BigInt`.

The design differs from the Python implementation by treating RSA processing as an asynchronous service operation.

Important mechanisms include:

- `BigInt` for exact integer arithmetic
- Node's `crypto.randomBytes` for random candidate generation
- `Map`-like object-oriented domain behavior through class methods
- asynchronous processing through a Promise and `setImmediate`
- explicit RSA validation
- CRT decryption
- binary modular exponentiation
- UTF-8 `Buffer` conversion
- structured error propagation

The asynchronous `evaluatePolicy` function demonstrates how an RSA computation can be placed behind an event-driven application boundary without changing the underlying mathematics.

## C++17 Implementation

The C++ program uses a repository-governance scenario as its primary domain model while retaining a complete RSA mathematical implementation.

The RSA side uses:

- strongly typed integer aliases
- `unsigned __int128` for modular multiplication
- Miller-Rabin style primality testing
- extended Euclid
- modular inverse
- binary modular exponentiation
- RSA key validation
- CRT decryption

The governance side models:

- Pull Request state
- reviews
- status checks
- branch protection
- merge eligibility

The `GovernanceEngine` evaluates whether a Pull Request can merge based on multiple independent conditions.

A stale source branch blocks merge eligibility even when approvals and status checks are otherwise valid. This distinguishes branch state from review decisions.

## Java 17 Implementation

The Java program uses an enterprise-oriented domain model.

Records represent immutable domain values such as:

- `StatusCheck`
- `Review`
- `BranchProtectionPolicy`
- `PullRequest`
- `RSAKeyPair`
- `Decision`

The `RSAService` encapsulates key generation, encryption, decryption, validation, and CRT operations.

The governance side uses a `MergePolicy` interface and an `EnterpriseMergePolicy` implementation. This separates the decision contract from the policy implementation.

Java's `BigInteger` provides arbitrary-precision arithmetic and modular operations. This makes the RSA implementation independent of machine integer width.

The merge decision explicitly returns both eligibility and failure reasons. This is useful in enterprise systems because a rejected operation should identify the policy conditions that prevented it.

## PostgreSQL Implementation

The PostgreSQL implementation represents the mathematical and repository domains relationally.

The `rsa_math` schema contains:

- `key_parameters`
- `rsa_operations`
- `repositories`
- `branches`
- `commits`
- `pull_requests`
- `reviewers`
- `reviews`
- `review_comments`
- `conversations`
- `status_checks`
- `branch_protection_policies`
- `required_status_checks`
- `approval_requirements`
- `merge_events`

Database constraints enforce structural rules such as:

- distinct source and target branches
- `n = p × q`
- `φ(n) = (p-1)(q-1)`
- valid Pull Request states
- positive line numbers
- non-empty review content
- valid merge methods
- non-negative approval requirements

## PostgreSQL Mathematical Functions

The database defines:

`modular_pow(base, exponent, modulus)`

for repeated-squaring modular exponentiation.

`extended_gcd(a, b)` returns Bézout coefficients.

`modular_inverse(value, modulus)` calculates an inverse when the greatest common divisor is one.

`validate_rsa_key(key_id)` checks the stored RSA relationships.

The sample RSA parameters use:

`p = 61`

`q = 53`

Therefore:

`n = 3233`

and:

`φ(n) = 3120`.

The sample public exponent is:

`e = 17`

and the private exponent is:

`d = 2753`.

The database then evaluates the classic RSA example:

`65¹⁷ mod 3233 = 2790`

followed by:

`2790²⁷⁵³ mod 3233 = 65`.

## Relational Repository Model

The repository model separates different types of state rather than storing merge eligibility as a single permanent flag.

The relationship is:

`Repository`
→ `Branches`
→ `Commits`
→ `Pull Requests`
→ `Reviews`
→ `Review Comments`
→ `Conversations`
→ `Status Checks`
→ `Branch Protection`
→ `Merge Eligibility`
→ `Merge Event`

A Pull Request identifies a proposed change between a source branch and a target branch.

Commits describe the branch history involved in that proposal.

Reviews represent reviewer decisions.

Review comments represent discussion attached to particular review activity.

Conversations track issues that may remain unresolved.

Status checks represent automated conditions.

Branch-protection policies represent repository-level enforcement.

Merge eligibility combines these independent facts.

## Pull Requests

A Pull Request is the workflow object for proposing a change from one branch into another.

The model records:

- repository
- source branch
- target branch
- head commit
- base commit
- state
- synchronization state
- merge-conflict state
- timestamps

The lifecycle represented by the schema includes draft, open, changes requested, approved, closed, and merged states.

A draft represents a proposal that is not yet ready for normal merge processing.

An open Pull Request is available for review and policy evaluation.

A Pull Request can become blocked because the source branch is no longer synchronized with the target or because a merge conflict exists.

Closing and merging are separate terminal outcomes.

Reopening a Pull Request is a state transition rather than a new review object. Review and policy state must therefore be evaluated against the current branch and policy conditions.

## Code Review

Code Review evaluates the proposed changes.

The database separates reviews from Pull Requests because one Pull Request can have multiple reviews and each reviewer can submit decisions.

The supported review states are:

- `COMMENTED`
- `APPROVED`
- `CHANGES_REQUESTED`
- `DISMISSED`

Review comments contain a file path, optional line number, body, and resolution state.

Conversations represent discussion that can remain unresolved independently of the approval count.

Review quality depends on examining the change against correctness, security, maintainability, tests, compatibility, and the intended scope of the Pull Request.

A reviewer should evaluate the proposed change rather than treating the existence of a Pull Request as evidence that the change is acceptable.

## Approvals

An approval is a review decision, not the same thing as a Pull Request.

The model counts only effective approvals when determining merge eligibility.

A review that has been dismissed does not provide an effective approval.

A review associated with an inactive reviewer does not satisfy the modeled reviewer condition.

An approval requirement can specify a minimum number of approvals.

This distinction prevents the system from treating an old approval as an unconditional permission to merge.

When the branch changes materially, repository policy may require the approval state to be reevaluated. The database represents the current review and policy facts separately so that this decision is not hidden inside a static approval flag.

## Branch Protection

Branch Protection enforces repository-level conditions.

The model supports:

- required approvals
- required status checks
- resolved-conversation requirements
- direct-push restrictions
- force-push restrictions
- branch-deletion restrictions
- linear-history requirements
- administrator bypass configuration

A protected target branch can require a Pull Request rather than permitting direct modification.

Required status checks are stored separately from the actual status-check results. This allows a policy to declare that `unit-tests` and `security-scan` are mandatory while the Pull Request records whether those checks actually passed.

Branch protection therefore operates at a different layer from code review.

## Distinction Between the Four Areas

The four concepts have separate responsibilities:

| Area | Primary responsibility |
|---|---|
| Pull Request | Proposes and tracks a change between branches |
| Code Review | Evaluates the proposed changes and records discussion |
| Approvals | Records explicit review decisions that can satisfy approval requirements |
| Branch Protection | Enforces repository-level conditions before merge |

The relationship is:

`Pull Request`
→ provides the workflow

`Code Review`
→ evaluates the change

`Approval`
→ records a review decision

`Branch Protection`
→ enforces repository policy

`Merge Eligibility`
→ evaluates the combined current state

This separation prevents one concept from being used as a substitute for another.

## Merge Eligibility

Merge eligibility is a derived decision.

A Pull Request can have valid approvals while remaining ineligible because:

- the source branch is stale
- a merge conflict exists
- a required status check failed
- a required conversation remains unresolved
- the required approval count is not satisfied
- the branch-history policy is violated

This is why merge eligibility should not be modeled as simply `approved = true`.

The PostgreSQL view `merge_eligibility` calculates the decision from current relational state.

The C++ governance engine calculates the same type of decision from domain objects.

The Java policy service returns a decision object containing both the boolean result and explicit failure reasons.

## Failure Handling

The implementations deliberately test invalid conditions.

Examples include:

- RSA messages outside `0 ≤ m < n`
- non-invertible modular values
- invalid RSA key relationships
- equal RSA prime factors
- invalid Pull Request source and target branches
- stale branches
- merge conflicts
- dismissed approvals
- unresolved conversations
- failed required checks
- insufficient approvals

The PostgreSQL script uses a transaction to demonstrate a failing status check. The state is rolled back after the eligibility query, preserving the original valid state.

## Performance Considerations

Binary modular exponentiation requires `O(log e)` exponentiation stages.

RSA private-key operations can be accelerated with CRT because exponentiation occurs modulo `p` and `q` rather than directly modulo `n`.

Prime generation is probabilistic and its cost depends on the candidate size and primality-testing process.

The PostgreSQL implementation uses indexes for access patterns centered on:

- Pull Request repository and state
- review state per Pull Request
- required status checks
- unresolved conversations

The relational eligibility view performs aggregation across review, status-check, and conversation data. For a large production repository service, additional indexing and precomputed policy state may be appropriate depending on workload.

## Edge Cases

The source implementations handle several important boundaries.

RSA:

- zero message representatives
- maximum valid representative `n-1`
- message value `n`
- non-invertible values
- equal prime factors
- invalid exponent relationships
- failed round-trip validation

Repository governance:

- draft Pull Requests
- closed or merged Pull Requests
- stale source branches
- merge conflicts
- missing approvals
- dismissed reviews
- unresolved conversations
- failed required checks
- optional status checks
- linear-history requirements

These conditions are intentionally evaluated independently.

## Practical Interpretation

RSA mathematics explains how public and private exponents are related through modular arithmetic.

Pull Requests, reviews, approvals, and branch protection describe a separate governance problem in which independently stored facts are combined into a final decision.

The common engineering principle is explicit state and validation.

For RSA, the key relationships must satisfy mathematical invariants.

For repository governance, the current branch, review, approval, status-check, and protection states must satisfy policy invariants.

Neither domain should collapse independent conditions into an unexplained boolean.

## File Responsibilities

| File | Primary responsibility |
|---|---|
| Python | Direct RSA mathematical model, key generation, validation, integer/text processing, and CRT |
| JavaScript | BigInt RSA model with Node.js randomness, asynchronous processing, and event-driven application behavior |
| C++17 | RSA arithmetic plus a repository governance and merge-eligibility engine |
| Java 17 | Enterprise domain model using records, interfaces, immutable collections, policy objects, and explicit decisions |
| PostgreSQL | Relational RSA arithmetic, repository state, review records, branch protection, constraints, triggers, transactions, and eligibility reporting |

## Operational Boundary

The programs are educational mathematical and systems models.

The small RSA parameters used in demonstrations must not be interpreted as secure production keys.

A production cryptographic system should use established cryptographic primitives and implementations, standardized encoding and padding schemes, appropriate key sizes, secure key storage, protected random generation, and security review.

The repository-governance model likewise represents policy evaluation rather than a complete implementation of any particular hosting platform's authorization system. Its purpose is to make the distinct states and enforcement relationships explicit.
