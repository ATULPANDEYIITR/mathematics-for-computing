# Rainbow Tables and Password Attacks

## 1. Technical Scope

This project examines password security through four connected areas:

- Password attack classification and attack mechanics.
- Rainbow-table construction, chain reduction and lookup.
- Password hashing, salt management and credential verification.
- Authentication governance, security policies and defensive auditing.

The implementations distinguish between attacks against password hashes and attacks against authentication systems.

The laboratory uses synthetic passwords and restricted demonstration datasets. It does not connect to external authentication services or process real credential databases.

## 2. Password Attack Fundamentals

A password attack attempts to obtain unauthorized access by exploiting weak passwords, exposed credentials, inadequate password storage or weaknesses in authentication controls.

### 2.1 Attack classifications

| Attack | Mechanism | Primary defensive control |
|---|---|---|
| Dictionary attack | Tests selected password candidates | Compromised-password screening and adaptive hashing |
| Brute-force attack | Searches a defined password space | Strong passwords and expensive password verification |
| Rainbow-table attack | Uses precomputed hash chains | Unique salts and adaptive password hashing |
| Password spraying | Tests a small password set across multiple accounts | Cross-account detection and MFA |
| Credential stuffing | Reuses exposed username-password combinations | MFA and credential compromise detection |
| Phishing | Deceives users into disclosing authentication secrets | Phishing-resistant authentication |

These attacks have different operational characteristics.

Dictionary, brute-force and rainbow-table attacks can target password hashes obtained through a data exposure. Password spraying and credential stuffing target authentication systems. Phishing targets the user and authentication process.

A password-storage defense does not independently prevent phishing, while rate limiting does not eliminate the consequences of an exposed password database.

## 3. Rainbow Tables

### 3.1 Definition

A rainbow table is a precomputed structure used to reduce the repeated computation required when searching for passwords corresponding to unsalted hashes.

It uses chains rather than storing every password-hash pair.

A chain alternates between two operations:

1. Hashing a candidate password.
2. Applying a reduction function that maps the hash into a candidate password.

The reduction function is not a cryptographic inverse. It maps a hash into a selected password search space.

### 3.2 Chain construction

A simplified chain has the following structure:

`P0 → H(P0) → R0 → P1 → H(P1) → R1 → P2`

Where:

- `P` represents a candidate password.
- `H` represents a hash function.
- `R` represents a position-dependent reduction function.

The table stores the starting password and the final endpoint rather than every intermediate value.

### 3.3 Lookup mechanics

To search for a target hash:

1. Begin at a possible chain position.
2. Apply the corresponding reduction function.
3. Continue reconstructing the possible remaining chain.
4. Check whether the resulting endpoint exists in the table.
5. If an endpoint matches, regenerate the chain from its stored starting value.
6. Verify whether an intermediate hash matches the target.

Regenerating the chain is necessary because an endpoint match alone does not prove that the target hash occurs within the chain.

### 3.4 Chain collisions and limitations

Rainbow tables have several limitations:

| Limitation | Technical effect |
|---|---|
| Chain merging | Different starting values can converge to the same chain |
| Reduction collisions | Different hashes can map to the same candidate |
| Incomplete coverage | Some passwords may not appear in stored chains |
| Search-space growth | Larger password spaces require more storage and computation |
| Algorithm dependence | Tables are specific to their hashing and reduction configuration |
| Salt dependence | Different salts require different precomputation |

Rainbow tables trade storage against computation. They are not universal password-recovery databases.

### 3.5 Python implementation

The Python implementation provides a complete synthetic rainbow-table workflow.

`SyntheticRainbowTable` contains:

- A finite candidate alphabet.
- A fixed password length.
- A configurable chain length.
- A position-dependent reduction function.
- Endpoint storage using a dictionary.
- Chain reconstruction and target verification.

The implementation uses SHA-256 for its restricted demonstration hash function.

The candidate space contains only three-character values from a four-character alphabet. This makes the experiment bounded and suitable for examining chain mechanics.

The implementation also handles malformed hexadecimal hashes, invalid dimensions and incomplete table coverage.

### 3.6 C++17 and Java implementations

The C++17 and Java programs use FNV-1a as a deterministic synthetic digest for the rainbow-table experiment.

This deliberately differs from the Python SHA-256 implementation.

FNV-1a is a non-cryptographic hash function. Its use in these demonstrations does not make it suitable for password storage or actual password security assessment.

The C++ implementation uses STL containers and explicit domain structures.

The Java implementation uses immutable records, collection-based endpoint storage and `Optional` for unsuccessful lookup results.

## 4. Password Hashing and Salt Management

### 4.1 Hashing versus encryption

Password hashing and encryption serve different purposes.

| Property | Encryption | Password hashing |
|---|---|---|
| Reversible | Yes, with the appropriate key | No |
| Primary purpose | Protect recoverable information | Verify passwords |
| Secret key | Generally required | Not required for ordinary salted password hashing |
| Password verification | Decrypt and compare, if applicable | Recompute and compare derived values |

Passwords should not be stored as plaintext or encrypted in a manner that makes routine password recovery possible.

A password-storage system should retain a suitable password-derived value and the parameters required for verification.

### 4.2 Why unsalted hashes are vulnerable

A conventional fast hash function can produce the same digest whenever it receives the same input.

For example:

`SHA256(password) = identical digest for identical input`

If two users select the same password, their unsalted hashes will match.

An attacker with an exposed password database can use previously computed hash values to identify repeated or weak passwords.

Fast general-purpose hashes are designed for efficient computation. This property makes them unsuitable as the sole password-storage mechanism.

### 4.3 Salt

A salt is a unique random value associated with a password credential.

Password storage becomes:

`Stored hash = KDF(password, salt, parameters)`

A salt:

- Prevents identical passwords from producing identical stored values when salts differ.
- Makes precomputed rainbow tables specific to a particular salt.
- Reduces the value of precomputation across different accounts.
- Does not make a weak password intrinsically strong.
- Does not replace an adaptive password hashing algorithm.

Salts are not encryption keys and normally do not need to remain secret.

### 4.4 Adaptive password hashing

The implementations distinguish three important password-hashing mechanisms.

| Algorithm | Mechanism | Main characteristic |
|---|---|---|
| PBKDF2 | Repeated password-based key derivation | Configurable computational cost |
| Argon2id | Memory-hard password derivation | Designed to increase memory and computational costs |
| scrypt | Memory-intensive password derivation | Makes large-scale parallel computation more expensive |

Argon2id is a strong general-purpose choice for new password-storage systems.

PBKDF2 remains useful where compatibility or applicable standards require it.

The Python and JavaScript examples use PBKDF2-HMAC-SHA256. The Java 17 implementation uses the JCA `SecretKeyFactory` interface with `PBEKeySpec`.

The C++ demonstration intentionally avoids implementing a production cryptographic password-storage algorithm.

## 5. Python Security Laboratory

The Python file combines password-security concepts into a small simulation environment.

### Main components

| Component | Responsibility |
|---|---|
| `AttackType` | Classifies six password attack categories |
| `SecurityPolicy` | Validates password length and character requirements |
| `PasswordHasher` | Generates salted PBKDF2-HMAC-SHA256 credentials |
| `PasswordRecord` | Stores username, salt, derived hash and iteration count |
| `SyntheticRainbowTable` | Constructs and searches restricted hash chains |
| `PasswordSecurityLab` | Coordinates registration and synthetic auditing |
| `AuditResult` | Records the outcome of a candidate audit |

### Important mechanisms

The password hasher uses `secrets.token_bytes()` for salt generation.

The verification process recomputes the PBKDF2-derived value and compares it using `hmac.compare_digest()`.

The account registration workflow checks:

- Duplicate usernames.
- Empty usernames.
- Common passwords.
- Minimum password length.
- Maximum password length.
- Required character categories.

The audit component tests a limited candidate list against a synthetic unsalted SHA-256 digest.

This makes it possible to compare the behavior of a fast hash with a salted adaptive password-storage mechanism.

### Error handling

Invalid password policies and malformed hash inputs are rejected through explicit exceptions.

The rainbow-table lookup returns `None` when the target is not covered by the stored chains.

Assertions verify successful synthetic recovery and salt isolation.

## 6. JavaScript Event-Driven Security Model

The JavaScript implementation focuses on asynchronous password processing and authentication events.

### Architecture

`SecurityPolicy` validates password requirements.

`PasswordHasher` provides asynchronous PBKDF2 processing through Node.js cryptographic functionality.

`SyntheticRainbowTable` models restricted chain construction and endpoint lookup.

`AuthenticationService` coordinates registration and login operations.

`Account` maintains account status and failed-attempt counters.

`SecurityEventBus` publishes security events through Node.js `EventEmitter`.

`PasswordAudit` stores synthetic audit results.

### Event-driven authentication

The authentication workflow generates events for:

- Account registration.
- Successful authentication.
- Failed authentication.
- Account locking.
- Rejected authentication.

The event bus separates authentication decisions from event reporting.

For example, a failed login increments the account's failure counter. Reaching the configured threshold transitions the account from `ACTIVE` to `LOCKED`.

A locked account cannot authenticate successfully until an authorized recovery process changes its state.

### Asynchronous password processing

PBKDF2 uses Node.js asynchronous cryptographic processing.

This avoids deliberately performing expensive password derivation as synchronous application work.

The implementation uses `crypto.timingSafeEqual()` for derived-key comparison.

The comparison is performed only after validating the expected buffer lengths.

### Operational considerations

An enterprise implementation should also apply:

- Distributed rate limiting.
- Authentication concurrency controls.
- Centralized event collection.
- Account recovery verification.
- Session invalidation after compromise.
- Monitoring for repeated failures across accounts.

The in-memory account map is intended for demonstration. Production deployments require durable storage and concurrency-safe account updates.

## 7. C++17 Repository-Independent Security Engine

The C++ program emphasizes explicit data structures, validation and state management.

### Domain structures

| Structure or class | Responsibility |
|---|---|
| `AttackType` | Defines attack classifications |
| `AccountStatus` | Represents account state |
| `PasswordPolicy` | Evaluates password requirements |
| `SyntheticHash` | Produces a deterministic educational digest |
| `SyntheticRainbowTable` | Maintains chain endpoints and performs lookup |
| `PasswordRecord` | Represents synthetic credential metadata |
| `DemonstrationCredentialStore` | Simulates credential registration and verification |
| `Account` | Maintains authentication state |
| `GovernanceEngine` | Aggregates security findings |

### STL usage

The implementation uses:

- `unordered_map` for credential and endpoint lookup.
- `unordered_set` for common-password detection.
- `vector` for audit findings and validation errors.
- `optional` for unsuccessful rainbow-table lookup.
- `enum class` for explicit domain states.

The use of `unordered_map` provides average constant-time key lookup, subject to hash distribution and collision behavior.

### Account state transitions

The authentication account follows these transitions:

`ACTIVE → LOCKED`

`ACTIVE → DISABLED`

A successful authentication resets the failure counter.

A failed authentication increments it.

Reaching the configured threshold locks the account.

The model does not permit a disabled account to transition automatically into another state.

### Cryptographic limitation

The demonstration credential store uses a synthetic deterministic digest.

It is intentionally unsuitable for real credential storage.

Its purpose is to make salt and state-management relationships visible without introducing a custom cryptographic implementation.

## 8. Java 17 Enterprise Domain Model

The Java implementation emphasizes domain modeling, immutable credential metadata and service boundaries.

### Domain types

| Type | Responsibility |
|---|---|
| `AttackType` | Enumerates password attack categories |
| `AccountStatus` | Defines account states |
| `AuthenticationStatus` | Defines authentication outcomes |
| `PasswordPolicy` | Immutable password validation rules |
| `PasswordCredential` | Immutable password-derived credential metadata |
| `AuthenticationResult` | Represents a login decision |
| `SecurityFinding` | Represents an audit result |
| `Account` | Maintains account-specific state |

### Password hashing

`PasswordHasher` uses:

- `SecureRandom` for unique salt generation.
- `PBEKeySpec` for password character input.
- `SecretKeyFactory` for PBKDF2-HMAC-SHA256 derivation.
- `MessageDigest.isEqual()` for derived-key comparison.

The password credential record returns defensive copies of its byte arrays.

This prevents callers from modifying the stored salt or derived key through exposed array references.

### Service boundaries

`AuthenticationService` handles:

1. Username validation.
2. Common-password rejection.
3. Password-policy evaluation.
4. Credential generation.
5. Account registration.
6. Authentication verification.
7. Failure counting.
8. Account locking.

`SecurityAuditService` separately maintains findings grouped by attack type.

This separation makes authentication decisions independent of reporting behavior.

### Failure handling

The Java implementation distinguishes:

- Invalid credentials.
- Locked accounts.
- Disabled accounts.
- Invalid password-policy configurations.
- Cryptographic processing failures.

It uses explicit domain enums instead of representing all failures through ambiguous Boolean values.

## 9. PostgreSQL Security Architecture

The PostgreSQL implementation models an organizational password-security assessment system.

It stores credential metadata and security events rather than implementing password derivation inside SQL.

### 9.1 Relational structure

The primary relationship is:

`Organizations`

`    └── Password Policies`

`    └── Security Accounts`

`            └── Password Credentials`

`            └── Authentication Events`

`    └── Security Assessments`

`            └── Attack Executions`

`                    └── Attack Catalog`

`                    └── Security Findings`

### 9.2 Main tables

| Table | Purpose |
|---|---|
| `organizations` | Identifies assessment organizations |
| `security_assessments` | Stores security assessment scope and lifecycle |
| `security_accounts` | Stores account identity and status |
| `password_credentials` | Stores password-hash metadata |
| `organization_salts` | Enforces salt uniqueness within an organization |
| `password_policies` | Stores account security requirements |
| `attack_catalog` | Defines attack classifications and controls |
| `attack_executions` | Records synthetic assessment execution |
| `security_findings` | Stores security weaknesses and remediation |
| `authentication_events` | Stores authentication outcomes |

### 9.3 Database constraints

The schema uses primary keys, foreign keys, unique constraints and check constraints.

Important validations include:

- Password salts must have sufficient length.
- Derived credential values must meet minimum storage length.
- PBKDF2 iteration counts must meet the configured minimum.
- Argon2id parameters must meet the schema's minimum configuration.
- Failed authentication counts cannot be negative.
- Assessment completion cannot precede its start.
- Successful findings resolution requires a resolution timestamp.
- Disabled accounts cannot be reactivated through ordinary account updates.

These constraints provide database-level protection against invalid application data.

### 9.4 Credential storage

The `password_credentials` table stores:

- Hash algorithm.
- Salt.
- Derived password hash.
- Iteration count.
- Memory parameter.
- Parallelism parameter.
- Key length.

The actual password derivation should occur in a trusted application or cryptographic service.

The database should never receive plaintext passwords for routine storage.

The sample byte sequences are synthetic demonstration values and must not be interpreted as valid production credentials.

### 9.5 Salt uniqueness

The `organization_salts` table uses a composite primary key:

`(organization_id, salt_fingerprint)`

This prevents accidental reuse of a salt within the same organization.

The trigger registers a credential's salt after insertion.

Production systems should generate salts using a cryptographically secure random-number generator and consider a globally unique salt policy where appropriate.

### 9.6 Authentication state management

The `record_authentication_attempt()` function:

1. Retrieves the account and active password policy.
2. Locks the account row using `FOR UPDATE`.
3. Checks the current account state.
4. Resets the failure counter after successful authentication.
5. Increments the counter after unsuccessful authentication.
6. Locks the account when the configured threshold is reached.
7. Records the authentication outcome.

The row-level lock prevents concurrent transactions from independently reading and overwriting the same failure counter.

The function must be called inside a transaction so the state change and event record remain consistent.

### 9.7 Indexing

The database defines indexes for:

- Organization assessment history.
- Assessment execution status.
- Open security findings.
- Account authentication history.
- Active password-policy lookup.

These indexes target actual retrieval and reporting operations.

Additional indexes should be based on measured query performance rather than added indiscriminately.

## 10. Understanding the Relationship Between Salts and Rainbow Tables

The central security distinction is that rainbow tables rely on repeated hash computation across a reusable password search space.

Consider two users choosing the same password:

Without salts:

`H(password) = H(password)`

With unique salts:

`KDF(password, salt_A) ≠ KDF(password, salt_B)`

The second arrangement prevents a single precomputed table from being directly reused across differently salted credentials.

A salt does not stop an attacker from testing candidates against an individual exposed credential.

Adaptive hashing addresses that remaining weakness by increasing the computational and, where applicable, memory cost of each password verification.

This distinction is essential:

| Control | Main protection |
|---|---|
| Unique salt | Prevents reusable precomputed hash tables across credentials |
| Adaptive password hashing | Increases the cost of each password guess |
| Strong passwords | Increases the difficulty of candidate discovery |
| MFA | Reduces the impact of password compromise |
| Rate limiting | Restricts online authentication attempts |
| Phishing-resistant authentication | Reduces credential theft through deceptive authentication requests |

## 11. Edge Cases and Failure Conditions

The implementations account for several important conditions.

| Condition | Expected behavior |
|---|---|
| Empty password | Registration or hashing rejected |
| Short password | Password-policy rejection |
| Excessively long password | Validation rejection |
| Common password | Registration rejected |
| Duplicate username | Registration rejected |
| Reused salt | Database uniqueness violation |
| Invalid hexadecimal hash | Rainbow-table lookup rejected |
| Missing table endpoint | Lookup returns no result |
| Merged rainbow chains | Effective coverage decreases |
| Incorrect password | Authentication rejected |
| Repeated failed logins | Account locked at configured threshold |
| Disabled account | Authentication denied |
| Invalid hashing parameters | Credential creation rejected |
| Missing active database policy | Authentication transaction fails |

## 12. Security Limitations and Production Considerations

These implementations are educational models rather than complete identity-management systems.

The following limitations are important.

### Password hashing

- Use Argon2id where supported.
- Use appropriate PBKDF2 or scrypt parameters when required.
- Benchmark parameters on production hardware.
- Reassess hashing parameters as hardware capabilities change.
- Never implement a custom production password hash.

### Authentication security

- Add MFA, preferably phishing-resistant authentication.
- Apply rate limits at account, network and system levels.
- Detect password spraying across multiple accounts.
- Detect credential stuffing using risk signals.
- Secure password-reset and recovery workflows.
- Protect session tokens and invalidate compromised sessions.

### Database security

- Restrict access to credential tables.
- Use parameterized SQL.
- Encrypt database connections.
- Protect backups and replicas.
- Prevent password values from entering logs.
- Audit access to credential records.
- Separate application privileges from database administration privileges.

### Rainbow-table limitations

The synthetic implementations use small candidate spaces and deterministic demonstration functions.

Their successful lookups do not establish that a real password database is vulnerable.

The C++17 and Java demonstrations use a non-cryptographic digest and must not be interpreted as production cryptographic implementations.

The PostgreSQL schema stores credential metadata and security events. It does not perform password derivation.

## 13. Performance and Complexity

Let:

- `N` represent the number of candidate passwords.
- `L` represent rainbow-table chain length.
- `T` represent the number of stored chains.
- `C` represent the cost of one password-hashing operation.

| Operation | Approximate complexity |
|---|---|
| Synthetic rainbow-table construction | O(N × L) |
| Rainbow-table endpoint lookup | O(L²) hash/reduction steps in the basic lookup procedure |
| Dictionary audit | O(N × C) |
| Hash-map endpoint retrieval | Average O(1) |
| Account lookup in a hash map | Average O(1) |
| PostgreSQL indexed account lookup | Typically O(log n) |
| Authentication password verification | O(C) |
| Account failure-counter update | Row-level transactional update |

The rainbow-table lookup can require substantial chain reconstruction even when an endpoint is found.

The table's storage savings come from retaining chain endpoints instead of every intermediate password-hash pair.

Password verification deliberately uses a higher computational cost than ordinary application hashing.

## 14. Running the Implementations

### Python

Requirements: Python 3.10 or later.

Save the first implementation as `password_security.py`.

Run:

`python password_security.py`

Only Python standard-library modules are used.

### JavaScript

Requirements: Node.js 18 or later.

Save the second implementation as `password_security.js`.

Run:

`node password_security.js`

Only Node.js standard-library modules are used.

### C++17

Save the third implementation as `password_security.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic password_security.cpp -o password_security`

Run:

`./password_security`

On Windows PowerShell:

`.\password_security.exe`

### Java 17

Save the fourth implementation as `PasswordSecurityEnterprise.java`.

Compile:

`javac PasswordSecurityEnterprise.java`

Run:

`java PasswordSecurityEnterprise`

The program uses Java 17 standard-library cryptographic facilities.

### PostgreSQL

Requirements: PostgreSQL 15 or later.

Save the fifth implementation as `password_security.sql`.

Execute:

`psql -U postgres -d postgres -f password_security.sql`

The script creates the `password_security` schema, tables, enumerated types, indexes, triggers, functions, views and synthetic sample records.

The SQL transaction commits the complete assessment dataset together.

## 15. Educational Outcomes

The five implementations provide complementary perspectives:

| Implementation | Primary technical perspective |
|---|---|
| Python | Rainbow-table simulation, validation and password-security auditing |
| JavaScript | Asynchronous hashing, event-driven authentication and account locking |
| C++17 | Data structures, synthetic hash chains and explicit state transitions |
| Java 17 | Enterprise domain modeling and secure password verification |
| PostgreSQL | Relational security governance, transactional authentication and audit reporting |

The most important engineering distinction is between preventing password reuse attacks, protecting stored password credentials and securing live authentication workflows.

A defensible password-security architecture requires all three.
