# Advanced Number Theory

## Quadratic Residues, Discrete Logarithms and Computational Number Theory

This project implements important algorithms from computational number theory across Python, JavaScript, C++17, Java 17 and PostgreSQL.

The central mathematical setting is modular arithmetic over prime fields. The implementations investigate quadratic characters, modular square roots, multiplicative groups, integer factorization and discrete logarithms.

The project connects mathematical definitions with executable algorithms, computational limits, result verification and structured processing.

## 1. Mathematical Foundation

### 1.1 Modular arithmetic

For an integer modulus \(n>1\), two integers are congruent when:

\[
a\equiv b\pmod n
\]

This means that \(n\) divides \(a-b\).

Every integer has a canonical residue in:

\[
\mathbb Z_n=\{0,1,\ldots,n-1\}
\]

The modular multiplication operation is:

\[
(a\cdot b)\bmod n
\]

Modular exponentiation calculates:

\[
a^k\bmod n
\]

Binary exponentiation reduces the number of multiplication operations from \(O(k)\) to \(O(\log k)\).

The implementations use iterative binary exponentiation, reducing intermediate results after each multiplication.

### 1.2 Extended Euclidean algorithm

The Euclidean algorithm computes:

\[
\gcd(a,b)
\]

The extended version finds integers \(x\) and \(y\) satisfying:

\[
ax+by=\gcd(a,b)
\]

A modular multiplicative inverse exists precisely when:

\[
\gcd(a,n)=1
\]

In that case:

\[
a^{-1}a\equiv1\pmod n
\]

The extended Euclidean algorithm is important in modular division, BSGS giant-step calculations and the Chinese Remainder Theorem.

The implementations explicitly reject non-invertible values instead of silently returning an incorrect result.

## 2. Quadratic Residues

### 2.1 Definition

Let \(p\) be an odd prime.

An integer \(a\) is a quadratic residue modulo \(p\) if there exists an integer \(x\) such that:

\[
x^2\equiv a\pmod p
\]

If no such \(x\) exists, \(a\) is a quadratic nonresidue.

For example, modulo 11:

\[
5^2=25\equiv3\pmod{11}
\]

Therefore, 3 is a quadratic residue.

The solutions of:

\[
x^2\equiv3\pmod{11}
\]

are:

\[
x\in\{5,6\}
\]

A nonzero quadratic residue modulo an odd prime generally has two distinct square roots. Zero has one distinct root.

### 2.2 Legendre symbol

The Legendre symbol provides a classification of an integer relative to an odd prime:

\[
\left(\frac ap\right)=
\begin{cases}
0 & p\mid a\\
1 & a\text{ is a quadratic residue}\\
-1 & a\text{ is a quadratic nonresidue}
\end{cases}
\]

Euler's criterion provides a computational method:

\[
\left(\frac ap\right)
\equiv
a^{(p-1)/2}\pmod p
\]

For nonzero \(a\), the modular result is either 1 or \(p-1\).

The software converts these results into the corresponding Legendre classifications.

### 2.3 Important properties

The Legendre symbol has several useful properties.

Multiplicativity:

\[
\left(\frac{ab}{p}\right)
=
\left(\frac ap\right)
\left(\frac bp\right)
\]

For a nonzero residue:

\[
\left(\frac{a^2}{p}\right)=1
\]

Quadratic reciprocity states that for distinct odd primes \(p\) and \(q\):

\[
\left(\frac pq\right)
\left(\frac qp\right)
=
(-1)^{\frac{p-1}{2}\frac{q-1}{2}}
\]

This relationship provides a systematic way to transform quadratic-character calculations between prime moduli.

The Python implementation includes an explicit quadratic reciprocity verification.

### 2.4 Tonelli-Shanks algorithm

Euler's criterion identifies whether a nonzero value is a quadratic residue. It does not directly provide its square roots.

The Tonelli-Shanks algorithm solves:

\[
x^2\equiv a\pmod p
\]

It is particularly useful for odd primes that are not congruent to 3 modulo 4.

First, decompose:

\[
p-1=q2^s
\]

where \(q\) is odd.

Find a quadratic nonresidue \(z\), then initialize:

\[
c=z^q\bmod p
\]

\[
x=a^{(q+1)/2}\bmod p
\]

\[
t=a^q\bmod p
\]

Repeated updates reduce the exponent of the residual element until \(t=1\).

The resulting value satisfies:

\[
x^2\equiv a\pmod p
\]

The second root is:

\[
p-x
\]

The implementation handles:

- Zero input.
- Quadratic residues.
- Quadratic nonresidues.
- The characteristic-two field.
- Invalid prime moduli.
- Verification of every returned root.

The algorithm also has a simpler branch for:

\[
p\equiv3\pmod4
\]

In this case:

\[
x=a^{(p+1)/4}\bmod p
\]

### 2.5 Practical significance

Quadratic residues are relevant to:

- Primality-related algorithms.
- Modular equation solving.
- Cryptographic parameter analysis.
- Finite-field computations.
- Cryptographic protocols using quadratic-character properties.

Quadratic residue classification and modular square-root computation are separate operations: the first determines existence, while the second constructs the solution.

## 3. Computational Number Theory

Computational number theory studies algorithms that solve integer and modular arithmetic problems efficiently.

Two important tasks in this project are integer factorization and primality testing.

### 3.1 Miller-Rabin primality testing

Miller-Rabin is a probabilistic primality-testing algorithm.

Represent:

\[
n-1=d2^s
\]

where \(d\) is odd.

For a selected witness \(a\), evaluate:

\[
a^d\bmod n
\]

A composite number can be identified through modular exponentiation and repeated squaring.

The algorithm rejects composite candidates when their witness conditions fail.

The implementations use the established seven-witness set for deterministic testing across the unsigned 64-bit range in C++17 and the corresponding deterministic range in Python and JavaScript.

For larger inputs, Python, JavaScript and Java provide probabilistic primality checks.

The distinction matters:

- A deterministic result is guaranteed within the validated integer range.
- A probable-prime result has a bounded probability of accepting a composite.
- A primality assertion stored in a database is not automatically a mathematical proof.

### 3.2 Pollard Rho factorization

Given an integer:

\[
N=p_1^{e_1}p_2^{e_2}\cdots p_k^{e_k}
\]

integer factorization attempts to recover its prime-power components.

Pollard Rho uses a sequence generated from a polynomial:

\[
f(x)=x^2+c\pmod N
\]

Cycle detection and greatest-common-divisor calculations are used to identify nontrivial factors.

The implementations use Floyd cycle detection.

Once a factor is discovered, the original integer is split into smaller integers. Recursive or stack-based processing continues until every factor is classified as prime.

The factorization result is represented as:

| Component | Meaning |
|---|---|
| Prime | A prime factor of the original integer |
| Exponent | Number of occurrences of that prime |
| Prime power | The factor raised to its recorded exponent |
| Reconstruction | Product of all prime powers |

For example:

\[
60=2^2\cdot3\cdot5
\]

Pollard Rho is useful when complete trial division would be unnecessarily expensive.

Its practical running time depends heavily on the size of the smallest nontrivial factor. It is not a polynomial-time general-purpose factorization algorithm.

### 3.3 Factorization and subgroup structure

Prime factorization becomes especially important when studying finite groups.

If a cyclic group has order:

\[
n=q_1^{e_1}q_2^{e_2}\cdots q_k^{e_k}
\]

its structure provides an opportunity to decompose certain computational problems into smaller prime-power components.

This property is central to the Pohlig-Hellman algorithm.

The computational implementations reuse integer factorization to derive the prime-power decomposition of a multiplicative group order.

## 4. Discrete Logarithms

### 4.1 Definition

Consider a multiplicative group generated by an element \(g\).

The discrete logarithm problem asks for an integer \(x\) satisfying:

\[
g^x\equiv h\pmod p
\]

Here:

- \(p\) is a prime modulus.
- \(g\) is the base or group generator.
- \(h\) is the target element.
- \(x\) is the unknown exponent.

Ordinary exponentiation calculates \(h\) from \(g\) and \(x\).

The discrete logarithm problem attempts to recover \(x\) from \(g\) and \(h\).

This inverse problem has significant relevance to cryptography.

### 4.2 Multiplicative order

The multiplicative order of an element \(g\) modulo \(p\) is the smallest positive integer \(r\) satisfying:

\[
g^r\equiv1\pmod p
\]

For a prime modulus:

\[
r\mid p-1
\]

The implementation starts with \(p-1\), factors that integer, and repeatedly removes prime factors when the smaller exponent still produces one.

The supplied group order must be exact when running Pohlig-Hellman.

Using an order that is merely a multiple of the actual order can invalidate the discrete-logarithm decomposition.

### 4.3 Baby-Step Giant-Step

Baby-Step Giant-Step is a meet-in-the-middle algorithm.

The target equation is:

\[
g^x\equiv h\pmod p
\]

Let:

\[
m=\lceil\sqrt n\rceil
\]

where \(n\) is the group order.

Represent the unknown exponent as:

\[
x=im+j
\]

where:

\[
0\leq j<m
\]

Rearranging gives:

\[
g^j\equiv h(g^{-m})^i\pmod p
\]

The algorithm consists of two phases.

**Baby steps**

Store the values:

\[
g^j\bmod p
\]

in a hash table, together with their corresponding exponents.

**Giant steps**

Calculate:

\[
h(g^{-m})^i\bmod p
\]

and search the baby-step table for a matching residue.

A match identifies the exponent:

\[
x=im+j
\]

The implementation verifies the recovered exponent before accepting it.

Complexity:

| Resource | Complexity |
|---|---|
| Time | \(O(\sqrt n)\) |
| Memory | \(O(\sqrt n)\) |
| Exponent verification | \(O(\log n)\) modular multiplications |

BSGS is practical for moderate subgroup orders but becomes expensive as the group grows.

The implementations enforce memory limits before building the lookup table.

### 4.4 Pohlig-Hellman algorithm

Pohlig-Hellman exploits the factorization of a cyclic group order.

Suppose:

\[
n=\prod_{i=1}^{k}q_i^{e_i}
\]

For each prime-power component, the original discrete logarithm is reduced to a smaller subgroup problem.

For:

\[
q^e\mid n
\]

the projected base and target are:

\[
g_q=g^{n/q^e}
\]

\[
h_q=h^{n/q^e}
\]

The algorithm recovers the exponent modulo \(q^e\) using successive base-\(q\) digits.

The partial exponent is lifted one digit at a time.

After obtaining:

\[
x\equiv x_i\pmod{q_i^{e_i}}
\]

for every prime-power component, the results are combined using the Chinese Remainder Theorem.

The final exponent is verified by evaluating:

\[
g^x\bmod p
\]

Pohlig-Hellman is especially effective when the group order has small prime factors.

A group with a large prime-order component does not receive the same computational advantage.

### 4.5 Chinese Remainder Theorem

For pairwise coprime moduli:

\[
m_1,m_2,\ldots,m_k
\]

the Chinese Remainder Theorem combines congruences:

\[
x\equiv a_i\pmod{m_i}
\]

into one congruence modulo:

\[
M=\prod_{i=1}^{k}m_i
\]

This makes it possible to reconstruct the discrete logarithm from its prime-power components.

The implementations verify that the moduli are pairwise coprime and that the final result satisfies the original modular equation.

## 5. Relationship Between the Mathematical Components

The three major areas serve different purposes.

| Area | Primary question | Main algorithm |
|---|---|---|
| Quadratic residues | Does a modular square root exist? | Legendre symbol |
| Modular square roots | What are the solutions? | Tonelli-Shanks |
| Computational primality | Is an integer prime? | Miller-Rabin |
| Integer factorization | Which primes divide an integer? | Pollard Rho |
| Multiplicative order | What is the smallest exponent producing one? | Factor reduction |
| Discrete logarithms | Which exponent produces a target element? | BSGS |
| Smooth-order discrete logarithms | How can the problem be decomposed? | Pohlig-Hellman |
| Congruence reconstruction | How are component solutions combined? | CRT |

These algorithms are related through modular arithmetic, but their computational objectives are not interchangeable.

## 6. Implementation Architecture

### 6.1 Python

The Python implementation provides a mathematical workbench.

Its main architectural components are:

| Component | Responsibility |
|---|---|
| `modular_power()` | Binary modular exponentiation |
| `extended_gcd()` | Bézout coefficients |
| `modular_inverse()` | Modular division |
| `is_probable_prime()` | Miller-Rabin testing |
| `factor_integer()` | Pollard Rho factorization |
| `legendre_symbol()` | Quadratic-character classification |
| `modular_square_roots()` | Tonelli-Shanks |
| `multiplicative_order()` | Exact element-order calculation |
| `baby_step_giant_step()` | Direct discrete logarithm |
| `pohlig_hellman()` | Prime-power decomposition and reconstruction |
| `NumberTheoryWorkbench` | Computation coordination |
| `DiscreteLogJob` | Computation lifecycle |

Python dictionaries provide the BSGS lookup table.

Sets and tuples help represent mathematical results without introducing unnecessary duplicate values.

Dataclasses represent immutable field parameters and residue reports.

The job model distinguishes:

- `PENDING`
- `RUNNING`
- `SOLVED`
- `NO_SOLUTION`
- `FAILED`

Self-tests verify both expected results and failure conditions.

### 6.2 JavaScript

The JavaScript implementation emphasizes structured asynchronous processing.

It uses `BigInt` for integer arithmetic because JavaScript's ordinary `Number` type cannot represent arbitrary large integers exactly.

Its event-driven service uses Node.js `EventEmitter`.

Important events include:

| Event | Purpose |
|---|---|
| `job:created` | A computation has been registered |
| `job:running` | Processing has started |
| `job:completed` | A terminal result is available |
| `job:failed` | An execution error occurred |
| `factorization:completed` | Integer factorization finished |
| `quadratic-residue:completed` | Residue evaluation finished |

The `NumberTheoryWorkbench` maintains a job map and generates unique identifiers.

Asynchronous entry points yield to the event loop before executing their computations. The underlying algorithms still execute on the main thread.

For CPU-intensive workloads, worker threads would be necessary to avoid blocking other application tasks.

The modular arithmetic routines use `BigInt` throughout to avoid accidental conversion into floating-point values.

### 6.3 C++17

The C++ implementation focuses on fixed-width arithmetic and low-level computational efficiency.

Its architecture uses:

| Component | Responsibility |
|---|---|
| `u64` | Unsigned 64-bit integers |
| `u128` | Intermediate multiplication |
| `modular_power()` | Binary exponentiation |
| `Factorizer` | Pollard Rho |
| `SquareRootResult` | Modular square-root result |
| `baby_step_giant_step()` | Hash-table discrete logarithm |
| `pohlig_hellman()` | Prime-power subgroup processing |
| `RepositoryNumberTheoryCaseStudy` | Integrated computational workflow |

An unsigned 128-bit intermediate prevents ordinary 64-bit multiplication from overflowing before reduction modulo the prime.

The implementation uses `std::unordered_map` for BSGS and ordered maps for prime-power factorizations.

It restricts prime-field inputs to the positive signed 64-bit range to maintain safe arithmetic boundaries in the extended Euclidean implementation.

C++17's native integer operations and STL containers provide a different performance-oriented perspective from Python and JavaScript.

### 6.4 Java 17

The Java implementation provides a service-oriented computational architecture.

Its core domain types are:

| Type | Responsibility |
|---|---|
| `PrimeField` | Validated prime modulus |
| `ComputationPolicy` | Computational resource limits |
| `Factorization` | Immutable prime-power representation |
| `SquareRootResult` | Classification and roots |
| `DiscreteLogResult` | Verified exponent and algorithm |
| `DiscreteLogJob` | Explicit job state |
| `FactorizationService` | Pollard Rho |
| `ArithmeticService` | Mathematical operations |
| `DiscreteLogService` | Discrete-log job execution |

Java's `BigInteger` supports arbitrary-precision integer arithmetic.

Records provide immutable data structures for field and computational results.

The `DiscreteLogJob` restricts state transitions:

\[
PENDING\rightarrow RUNNING
\]

From `RUNNING`, the job can move to exactly one terminal state:

\[
SOLVED,\quad NO\_SOLUTION,\quad FAILED
\]

A completed job cannot be restarted or moved into another state.

This makes the Java implementation suitable as a domain-modeling example for computational services.

### 6.5 PostgreSQL

The PostgreSQL implementation models number-theory computations relationally.

It separates prime parameters, factorization records, quadratic residue checks, roots and discrete logarithm jobs.

The principal relationships are:

    prime_moduli
         |
         +---- factorizations
         |          |
         |          +---- prime_factor_powers
         |
         +---- quadratic_residue_checks
         |          |
         |          +---- modular_roots
         |
         +---- discrete_log_jobs
                    |
                    +---- dlog_baby_steps

**Prime registry**

`prime_moduli` stores prime moduli and verification metadata.

The registry represents an external primality assertion. Database registration itself does not establish primality.

**Factorization records**

`factorizations` stores an integer and its completeness status.

`prime_factor_powers` stores the individual prime-power components.

Deferred constraint triggers verify that complete factorizations reconstruct the original integer:

\[
N=\prod_i p_i^{e_i}
\]

**Quadratic residue records**

`quadratic_residue_checks` records the evaluated Legendre symbol.

A trigger computes the symbol rather than trusting an arbitrary supplied classification.

`modular_roots` stores the roots calculated by Tonelli-Shanks.

A database trigger checks every inserted root against the original modular equation.

**Discrete logarithm jobs**

`discrete_log_jobs` stores the mathematical parameters, computational policy, execution state and result.

`dlog_baby_steps` provides an indexed lookup table for BSGS.

The primary key:

\[
(job\_id,residue\_value)
\]

supports efficient giant-step matching.

The `solve_discrete_log_job` procedure locks the requested job, verifies group-order information, builds baby steps and searches giant steps.

The procedure records one of three mathematical outcomes:

- `SOLVED`
- `NO_SOLUTION`
- `FAILED`

Database exceptions are captured and associated with the failed computation.

The views support computational eligibility checks, result retrieval and activity aggregation.

The database implementation uses numeric intermediate arithmetic for modular multiplication and exponentiation to reduce overflow risks.

## 7. Realistic Computational Scenario

All five implementations use the following example.

The prime modulus is:

\[
p=1019
\]

The multiplicative group has order:

\[
p-1=1018=2\cdot509
\]

The base is:

\[
g=2
\]

Its exact multiplicative order is 1018.

A known exponent is:

\[
x=137
\]

The corresponding target is:

\[
h=2^{137}\bmod1019
\]

The discrete logarithm computation attempts to recover:

\[
x=\log_2(h)\pmod{1019}
\]

Pohlig-Hellman decomposes the group order into:

\[
2^1\cdot509^1
\]

It solves the corresponding smaller subgroup problems and combines the results using CRT.

The recovered exponent must satisfy:

\[
2^{137}\bmod1019=h
\]

The quadratic-residue demonstration uses:

\[
56^2\bmod1019=79
\]

Its two square roots are:

\[
56,\quad963
\]

A second demonstration evaluates 2 modulo 1019, which is a quadratic nonresidue for this selected prime.

These examples provide reproducible inputs for checking the implementations against one another.

## 8. Validation and Failure Handling

The implementations explicitly handle mathematical conditions that can invalidate a computation.

| Condition | Expected behavior |
|---|---|
| Modulus less than two | Reject |
| Negative modular exponent | Reject |
| Composite field modulus | Reject |
| Non-invertible modular value | Raise an error |
| Zero multiplicative-group base | Reject |
| Nonresidue passed to square-root algorithm | Return no roots |
| Incorrect multiplicative order | Reject |
| Incorrect prime-power decomposition | Reject |
| Target outside declared subgroup | Return no solution |
| BSGS memory budget exceeded | Reject computation |
| Computed exponent fails verification | Raise an error |
| Duplicate computation identifier | Reject |
| Invalid job state transition | Reject |

Mathematical validity and execution success are different concepts.

A discrete logarithm job may execute correctly and still produce `NO_SOLUTION` because the target does not belong to the subgroup generated by the base.

A `FAILED` state indicates an execution or validation failure rather than an ordinary mathematical absence of a solution.

## 9. Performance Characteristics

| Algorithm | Expected computational complexity |
|---|---|
| Extended Euclidean algorithm | \(O(\log n)\) arithmetic iterations |
| Binary modular exponentiation | \(O(\log e)\) modular multiplications |
| Miller-Rabin | \(O(t\log n)\) modular multiplications, up to witness-dependent factors |
| Pollard Rho | Randomized; influenced by the smallest prime factor |
| Legendre symbol | \(O(\log p)\) modular multiplications |
| Tonelli-Shanks | Prime-field dependent; polynomial in the bit length |
| Multiplicative order | Depends on factorization of \(p-1\) |
| BSGS | \(O(\sqrt n)\) time and memory |
| Pohlig-Hellman | Depends on subgroup prime-power factors and their BSGS subproblems |
| Chinese Remainder Theorem | Polynomial in the number and bit lengths of moduli |

Important resource considerations include:

- Baby-step tables can consume substantial memory.
- Factorization performance degrades on difficult composite inputs.
- Large integer representations consume more memory than fixed-width integers.
- Repeated modular exponentiation can dominate computational time.
- PostgreSQL procedures are appropriate for bounded database computations, not unlimited computational workloads.

## 10. Security and Cryptographic Considerations

Discrete logarithms are central to several cryptographic constructions.

Their difficulty depends on the underlying group and its parameters.

An important distinction is that a large modulus alone does not automatically guarantee a difficult discrete logarithm.

The order of the selected group matters.

Pohlig-Hellman illustrates why groups with easily factorable orders can be unsuitable for cryptographic applications.

A cryptographic group should have an appropriate large prime-order subgroup, alongside suitable parameter validation.

The supplied implementations are mathematical learning and computational analysis tools, not production cryptographic libraries.

They do not implement constant-time arithmetic.

Potential security concerns include:

- Variable execution time dependent on input values.
- Memory consumption from lookup tables.
- Computational denial of service through expensive factorization requests.
- Insufficient validation of externally supplied parameters.
- Randomized factorization procedures with unpredictable runtime.
- Exposure of sensitive exponents through logs or diagnostic outputs.

Production systems require independently verified group parameters, carefully controlled computation budgets and cryptographic implementations designed to resist timing and other side-channel attacks.

## 11. Educational and Technical Outcomes

The project connects several important concepts:

- Modular arithmetic provides the computational foundation.
- Quadratic characters classify elements of prime fields.
- Tonelli-Shanks constructs modular square roots.
- Miller-Rabin identifies probable primes.
- Pollard Rho decomposes composite integers.
- Multiplicative order establishes subgroup structure.
- BSGS solves bounded discrete-logarithm problems.
- Pohlig-Hellman exploits group-order factorization.
- CRT reconstructs results from prime-power components.
- Database constraints and application-level policies preserve computational integrity.

The five implementations demonstrate how the same mathematical problems can be represented using dynamic-language data structures, event-driven services, fixed-width systems programming, immutable enterprise domain models and relational database operations.
