# Chinese Remainder Theorem: Congruence Systems and Computational Applications

## Scope

This project implements the Chinese Remainder Theorem (CRT) as a computational subject rather than as a collection of isolated mathematical examples.

The five source files model the same mathematical foundations from different engineering perspectives:

| File | Primary role | Main implementation |
|---|---|---|
| Python | Mathematical toolkit and executable demonstrations | Coprime CRT, generalized CRT, linear congruences, modular inverses, RSA-style recombination |
| JavaScript | BigInt and asynchronous computational model | CRT construction, generalized merging, modular exponentiation, concurrent result evaluation |
| C++17 | Systems-oriented implementation | CRT engine with overflow protection, generalized merging, modular arithmetic, governance-style case study |
| Java 17 | Enterprise domain model | Immutable records, explicit services, policies, review state, and CRT computation |
| PostgreSQL | Relational computational model | Congruence-compatible repository governance data model plus executable CRT-related workflow reporting |

The mathematical core is the solution of systems such as:

`x ≡ a₁ (mod m₁)`

`x ≡ a₂ (mod m₂)`

through a single congruence:

`x ≡ r (mod M)`

where `M` is the relevant product or least common multiple of the moduli.

## Mathematical Model

A congruence

`x ≡ a (mod m)`

means that `m` divides `x - a`. Equivalently, `x` and `a` belong to the same residue class modulo `m`.

For pairwise-coprime positive moduli `m₁, m₂, ..., mₙ`, the classical CRT states that the system has exactly one solution modulo:

`M = m₁m₂...mₙ`

Define:

`Mᵢ = M / mᵢ`

and choose `yᵢ` such that:

`Mᵢyᵢ ≡ 1 (mod mᵢ)`

Then a solution is:

`x ≡ Σ aᵢMᵢyᵢ (mod M)`

The implementations calculate the modular inverses rather than relying on hard-coded inverses.

## Generalized CRT

Pairwise coprimality is sufficient for the classical construction but is not necessary for every solvable system.

Two congruences

`x ≡ a (mod m)`

and

`x ≡ b (mod n)`

are compatible precisely when:

`a ≡ b (mod gcd(m,n))`

When they are compatible, the two congruences can be merged into one congruence modulo:

`lcm(m,n)`

The Python, JavaScript, and Java implementations explicitly support this generalized form. The C++ implementation also performs compatibility checking and rejects an inconsistent system.

For example:

`x ≡ 2 (mod 6)`

`x ≡ 8 (mod 9)`

is compatible because `gcd(6,9) = 3` and `2 ≡ 8 (mod 3)`.

The merged result is:

`x ≡ 44 (mod 18)`

This distinction is important because blindly applying the pairwise-coprime construction to non-coprime moduli can require an inverse that does not exist.

## Modular Inverses

The extended Euclidean algorithm finds integers `x` and `y` satisfying:

`ax + my = gcd(a,m)`

If `gcd(a,m) = 1`, then:

`ax ≡ 1 (mod m)`

so `x` is a modular inverse of `a`.

All computational implementations use this relationship to construct CRT solutions.

A modular inverse does not exist when the operands are not coprime. This is treated as a validation failure rather than being silently approximated.

## Linear Congruences

The Python implementation also solves:

`ax ≡ b (mod m)`

using:

`d = gcd(a,m)`

A solution exists only when `d` divides `b`.

After division by `d`, the reduced equation has an invertible coefficient. There can be multiple residue-class solutions modulo `m`, and the Python implementation returns all distinct solutions.

This provides a useful bridge between basic modular arithmetic and CRT systems.

## Computational Applications

CRT is valuable when one large modular computation can be decomposed into several smaller computations.

The source files include an RSA-style recombination example. Given two relatively prime factors `p` and `q`, a private modular exponentiation can be evaluated separately modulo `p` and `q`, followed by CRT recombination.

The computational pattern is:

`large modular computation`

`→ computation modulo p`

`→ computation modulo q`

`→ CRT recombination`

The example uses deliberately small educational values. It is not a secure cryptographic implementation.

In practical cryptographic systems, CRT can reduce the cost of RSA private operations because arithmetic over smaller moduli is generally cheaper than performing the complete operation directly modulo the product.

## Python Implementation

The Python file is organized around immutable `dataclass` domain objects.

`Congruence` validates the modulus and normalizes the remainder. `CRTResult` represents the resulting residue class and provides a verification method.

The mathematical functions are separated by responsibility:

| Function | Purpose |
|---|---|
| `extended_gcd` | Computes Bézout coefficients |
| `mod_inverse` | Computes a modular inverse |
| `solve_coprime_crt` | Implements classical CRT |
| `merge_congruences` | Combines two compatible congruences |
| `solve_general_crt` | Handles non-coprime compatible systems |
| `solve_linear_congruence` | Solves one linear congruence |
| `verify` | Checks the result against every original constraint |

Python's arbitrary-precision integers make the implementation suitable for large mathematical examples without an explicit fixed-width integer limit.

The executable demonstration also exercises inconsistent systems and verifies computed results with assertions.

## JavaScript Implementation

The JavaScript file uses `BigInt` throughout the modular arithmetic path.

Using ordinary JavaScript `Number` values for large integer products can introduce precision loss because `Number` is floating-point. `BigInt` avoids this problem for integer calculations within its supported range.

The JavaScript implementation provides:

- `Congruence` validation and normalization
- Extended Euclidean arithmetic
- Modular inverses
- Classical CRT
- Generalized CRT
- Modular exponentiation
- Result verification
- Asynchronous status-check evaluation

The asynchronous section deliberately separates independent computational checks using promises. This demonstrates how CRT computation can coexist with event-driven application logic without mixing floating-point arithmetic into the mathematical layer.

## C++17 Implementation

The C++ implementation uses strongly typed structures and explicit exception handling.

The central types are `Congruence`, `CRTResult`, and `EGCD`.

The implementation uses `__int128` for intermediate multiplication even though the public result type is `int64_t`. This matters because an expression such as:

`remainder × partial × inverse`

can overflow 64-bit arithmetic before the final value is reduced modulo `M`.

The program therefore distinguishes between:

- intermediate arithmetic capacity
- final result capacity
- invalid modular input
- missing modular inverses
- inconsistent congruences
- combined-modulus overflow

The `solveGeneralCRT` function merges congruences progressively. Each successful merge replaces two constraints with an equivalent single constraint whose modulus is their least common multiple.

The program also contains a small governance-oriented case study to demonstrate how an independently computed eligibility predicate can be represented as a deterministic engine. This is intentionally separate from the mathematical CRT implementation.

## Java 17 Implementation

The Java implementation emphasizes explicit domain modeling.

Java records represent immutable mathematical and governance data:

- `Congruence`
- `CRTResult`
- `Review`
- `StatusCheck`
- `BranchPolicy`
- `PullRequest`

`CRTService` owns mathematical operations, while `GovernanceService` owns repository-policy evaluation.

This separation prevents unrelated policy concepts from becoming part of the mathematical CRT algorithm.

`BigInteger` is used because Java primitive integer types have fixed widths. CRT products can grow quickly as the number and size of moduli increase.

The enterprise-style section models approval eligibility, current-commit approvals, status checks, conflict state, unresolved conversations, and linear-history requirements. These rules are independent from CRT but demonstrate the same engineering principle of composing independently validated conditions into a final decision.

## PostgreSQL Implementation

The PostgreSQL file provides a relational repository-governance model containing:

- repositories
- repository users
- branches
- commits
- Pull Requests
- reviews
- review comments
- status checks
- branch-protection policies
- approval requirements
- reviewer roles

Primary keys and foreign keys establish the entity relationships.

Check constraints restrict enumerated workflow states such as `open`, `merged`, `approved`, `changes_requested`, `passed`, and `failed`.

Indexes target concrete access patterns:

- Pull Requests by target branch and state
- reviews by Pull Request and review state
- status checks by Pull Request and status
- unresolved review comments

The `merge_eligibility` function evaluates several independent conditions and reports both the final decision and the reason for failure.

The database therefore distinguishes:

`Pull Request state`

from:

`review decisions`

from:

`status-check results`

from:

`branch-protection policy`

from:

`final merge eligibility`

The transactional section locks the eligibility result before changing the Pull Request state and target branch head. This prevents the example merge operation from treating eligibility as an unrelated read followed by an unchecked write.

## Validation and Failure Conditions

The implementations deliberately reject invalid states rather than silently producing misleading results.

Important failure conditions include:

| Condition | Treatment |
|---|---|
| Empty congruence system | Rejected |
| Modulus ≤ 1 | Rejected |
| Missing modular inverse | Rejected |
| Non-coprime moduli in classical CRT | Rejected |
| Incompatible non-coprime congruences | Rejected |
| Large fixed-width intermediate value | Overflow protection in C++ |
| Large Java integer product | Handled with `BigInteger` |
| JavaScript large integer arithmetic | Handled with `BigInt` |
| Failed repository status check | Merge ineligible |
| Stale approval | Not counted |
| Merge conflict | Merge ineligible |
| Unresolved required conversation | Merge ineligible |
| Required linear history violated | Merge ineligible |

## Complexity

For `n` pairwise-coprime congruences, the direct CRT construction requires pairwise-coprimality checks that take `O(n²)` greatest-common-divisor operations.

Once coprimality is established, the construction requires one modular inverse per congruence and a linear pass over the system.

The generalized merge approach processes congruences sequentially. Each merge requires greatest-common-divisor and modular-inverse calculations.

The cost of arithmetic itself depends on the number of bits in the operands. This is particularly important for large cryptographic moduli, where multiplication and division are substantially more expensive than operations on machine-sized integers.

## Security Considerations

CRT is a mathematical technique, not a complete security mechanism.

For cryptographic applications:

- cryptographically secure parameter generation is required
- private values must not be logged
- modular arithmetic must use appropriate constant-time implementations where side-channel resistance matters
- invalid or malicious inputs must be validated
- RSA-CRT implementations require protections against fault attacks
- test examples must not be mistaken for production cryptographic keys

The sample RSA-style values are intentionally small and public.

The source implementations focus on mathematical correctness and software engineering rather than production cryptography.

## Relationship Between the Implementations

The implementations intentionally do not form language-for-language translations.

Python emphasizes a reusable mathematical toolkit and executable verification.

JavaScript emphasizes arbitrary-precision `BigInt` arithmetic combined with asynchronous application behavior.

C++ emphasizes explicit resource and overflow considerations and uses fixed-width integer types with wider intermediates.

Java emphasizes immutable enterprise domain types and service boundaries.

PostgreSQL demonstrates how related computational state can be normalized, constrained, indexed, evaluated, and committed transactionally.

The shared mathematical relationship is:

`Congruence constraints`
`        ↓`
`Modular compatibility`
`        ↓`
`CRT construction or progressive merging`
`        ↓`
`Canonical residue`
`        ↓`
`Verification`
`        ↓`
`Computational application`

## Practical Distinctions

The classical CRT should be used directly when the moduli are pairwise coprime.

The generalized CRT should be used when moduli may share factors. Compatibility must be checked before attempting to compute an inverse.

A CRT result is not a single unrestricted integer. It represents a residue class modulo the combined modulus.

For example:

`x ≡ 23 (mod 105)`

represents every integer of the form:

`23 + 105k`

for integer `k`.

The canonical representative stored by the implementations is normally selected in the range from `0` through `M - 1`.

This distinction is essential when verifying a result because many different integers satisfy the same congruence system while representing the same residue class.
