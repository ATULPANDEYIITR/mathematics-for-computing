# Pigeonhole Principle: Basic, Generalized, and Computing Applications

## Scope

The pigeonhole principle is a counting principle used to establish that a
collision, repetition, or concentration must occur when a finite collection of
objects is mapped into a smaller finite collection of categories.

The basic statement is:

> If more objects are placed into fewer containers, at least one container
> contains more than one object.

The generalized form is stronger. If `n` objects are distributed among `k`
containers, then at least one container contains at least

`ceil(n / k)`

objects.

This repository treats the principle as a computing reasoning technique rather
than only as a mathematical definition. Hash tables, finite identifiers,
memory representations, modular arithmetic, load distribution, categorical
signatures, and duplicate detection all involve mappings into finite spaces.

The six deliverables use different implementation perspectives:

| File | Technical perspective |
|---|---|
| Python | Mathematical utilities, simulations, hash buckets, finite state spaces, duplicate detection, and computing case studies |
| JavaScript | Event-driven and asynchronous models, hash storage, finite identifiers, load balancing, and probabilistic experiments |
| C++ | A storage-partition case study using classes, STL containers, hashing, modular classification, and explicit complexity analysis |
| Java | An enterprise artifact-distribution service using records, enums, interfaces, policy objects, validation, and immutable results |
| SQL | A PostgreSQL relational model for partitions, artifacts, assignments, occupancy guarantees, constraints, indexes, transactions, and analytical queries |
| README | Conceptual and implementation-level explanation of the complete learning artifact |

---

## Core Mathematical Mechanism

The principle becomes useful when a problem can be expressed as a mapping:

`objects -> finite categories`

The objects may be students, requests, identifiers, files, records, integers,
cache entries, hash keys, logical states, or computational outputs.

The containers may be months, servers, partitions, residue classes, identifier
values, bit patterns, hash buckets, or categorical combinations.

The identity of the objects and the meaning of the containers are not enough by
themselves. The important question is whether every object must be assigned to
one of a finite number of available categories.

If there are 13 students and 12 months, the 13 students are the objects and the
12 months are the containers. Since 13 exceeds 12, at least two students share
a birth month.

No probability calculation is necessary. The result follows from counting.

---

## Basic Pigeonhole Principle

The basic form can be written as:

`n > k => some container contains at least 2 objects`

where:

- `n` is the number of objects
- `k` is the number of containers

A collision is therefore guaranteed whenever the object count is greater than
the available container count.

This distinction is important in computing. A finite identifier space does not
remain unique merely because an identifier-generation algorithm usually
produces distinct values. Once more objects need unique identifiers than the
space can represent, uniqueness is mathematically impossible.

For example, three decimal digits provide:

`10^3 = 1000`

possible identifiers.

The assignment of 1001 distinct objects to those 1000 possible identifier
values must contain a duplicate.

The principle does not specify which identifier will be duplicated. It only
establishes that some duplication must occur.

---

## Generalized Pigeonhole Principle

For `n` objects and `k` containers:

`some container has at least ceil(n / k) objects`

For example, distributing 1001 objects across 16 containers gives:

`ceil(1001 / 16) = 63`

Therefore at least one container must contain at least 63 objects.

The guarantee is a lower bound on the largest occupancy. It does not mean that
every container contains 63 objects.

A balanced distribution might contain occupancies such as:

`63, 63, 63, 63, 63, 63, 63, 63, 63, 62, 62, 62, 62, 62, 62, 62`

The exact distribution depends on the allocation mechanism, but no assignment
can make the largest occupancy smaller than 63.

The implementations use this form repeatedly because computing systems often
distribute large numbers of objects across finite resources.

---

## Reverse Form: Guaranteeing a Target Occupancy

A useful rearrangement asks a different question:

> How many objects are required to guarantee that some container contains at
> least `t` objects?

If there are `k` containers, each container could contain at most `t - 1`
objects without reaching the target.

Therefore the largest number of objects that can avoid the target is:

`k(t - 1)`

One additional object forces the target:

`k(t - 1) + 1`

For 16 containers and a target occupancy of 20:

`16(20 - 1) + 1 = 305`

Thus 305 objects guarantee that at least one container contains 20 objects.

This reverse form is useful when setting capacity thresholds, evaluating finite
identifier systems, and designing partitioning schemes.

---

## Pigeonhole Reasoning in Computing

Computing systems constantly map large or unbounded logical domains into finite
representations.

Examples include:

- arbitrary strings mapped into finite hash buckets
- records mapped into database partitions
- requests mapped onto a finite server pool
- integers mapped into residue classes
- logical states mapped into finite bit patterns
- records classified by a finite combination of categorical attributes
- objects assigned finite identifiers
- data items mapped into fixed-size cache partitions

The important relationship is:

`large logical space -> finite representation space`

Once the input space is larger than the representation space, collisions are
unavoidable if every input must receive a representation.

A hash function can distribute values well, but it cannot create more distinct
outputs than the number of values in its output space.

---

## Hash Buckets

A hash table is a direct computing application.

Suppose a system has 64 buckets. Every key is assigned to one of those 64
buckets.

If 10,000 keys are stored, the generalized pigeonhole principle guarantees:

`ceil(10000 / 64) = 157`

Therefore at least one bucket contains at least 157 keys.

A high-quality hash function can make the distribution close to balanced, but
it cannot make the maximum occupancy smaller than 157.

The Python implementation demonstrates this using SHA-256-derived bucket
indices. The hash function is used to create a realistic deterministic
assignment, while the mathematical guarantee is calculated independently.

The JavaScript implementation builds a `BucketStore` class around `Map`
instances. This shows the distinction between the mathematical bucket space
and the implementation mechanism used to store entries.

The C++ implementation uses `std::hash` and `std::vector` partitions. The
observed distribution is allowed to differ from the ideal balanced
distribution, while the pigeonhole lower bound remains valid.

---

## Hash Collisions Are Not Hash Failures

A collision means that two different inputs map to the same finite output
bucket or value.

For a hash function with a finite output space, collisions are mathematically
unavoidable when enough distinct inputs are considered.

A collision is therefore not automatically a defect in the hash function.

The engineering question is how collisions are handled.

Common hash-table mechanisms include:

- separate chaining
- open addressing
- linear probing
- quadratic probing
- double hashing

The pigeonhole principle establishes the existence of collisions. It does not
choose the collision-resolution strategy.

A cryptographic hash may have a very large output space and strong resistance
properties, but it still has a finite output space.

---

## Finite Identifier Spaces

Suppose an identifier contains four hexadecimal characters.

Each character has 16 possible values, giving:

`16^4 = 65,536`

possible identifiers.

Assigning 65,537 objects to this space forces a duplicate.

The important design distinction is between:

- a large identifier space
- a guaranteed globally unique identifier
- a practically collision-resistant identifier
- a database-enforced uniqueness constraint

These are not equivalent.

A system may use a large random or cryptographic identifier to make accidental
collisions extremely unlikely. A database `UNIQUE` constraint can enforce
uniqueness for values actually stored in that database. Neither changes the
finite-space argument.

---

## Bit Patterns and Representation

A `b`-bit field has:

`2^b`

possible bit patterns.

An 8-bit field has 256 possible patterns.

If a system needs to distinguish 257 states, 8 bits cannot encode every state
uniquely.

At least two logical states must share a representation if all 257 states are
forced into the 256-pattern space.

The implementations calculate the minimum number of bits required for a
specified number of states.

This is a direct application of the pigeonhole principle to digital
representation.

The principle becomes especially useful when reasoning about:

- protocol fields
- finite state encodings
- compact database codes
- machine identifiers
- enum representations
- serialization formats
- cache state codes

---

## Modular Arithmetic

Integers can be classified according to their remainder modulo `k`.

There are exactly `k` possible residue classes:

`0, 1, 2, ..., k - 1`

If 50 integers are classified modulo 7, some residue class must contain at
least:

`ceil(50 / 7) = 8`

integers.

The Python, JavaScript, C++, Java, and SQL implementations demonstrate this
classification.

This technique is useful in algorithmic reasoning because many apparently
different integers become members of a small finite set of residue classes.

---

## Duplicate Detection

Duplicate detection is one of the most direct computational manifestations of
the principle.

When values are inserted into a finite or explicitly bounded namespace,
a duplicate becomes unavoidable once the number of required unique values
exceeds the namespace capacity.

The code implementations use appropriate data structures rather than
enumerating every possible pair.

Python uses dictionaries and sets.

JavaScript uses `Set` and `Map`.

C++ uses `std::unordered_map` and `std::set`.

Java uses `HashMap`, `HashSet`, and `Optional`.

SQL uses grouping and `HAVING COUNT(*) > 1` for analytical duplicate detection
and a `UNIQUE` constraint for database-level enforcement.

The distinction is important:

`detecting duplicates` and `preventing duplicates` are different operations.

A query can identify duplicates in imported data. A uniqueness constraint can
prevent duplicates from being persisted.

---

## Load Distribution

Suppose 23 requests must be assigned across five servers.

The generalized pigeonhole principle gives:

`ceil(23 / 5) = 5`

Therefore some server must receive at least five requests.

A perfectly balanced distribution is:

`5, 5, 5, 4, 4`

The principle says that a maximum load of four is impossible.

It does not say which server receives five requests.

The JavaScript implementation uses an event-driven `RequestRouter` and assigns
requests to the currently least-loaded server. The C++ and Java examples use
different approaches to represent the same underlying counting constraint.

This illustrates an important engineering point: an allocation algorithm can
optimize a distribution while still being subject to a mathematical lower
bound.

---

## Categorical Signatures

A system may classify records using several finite categorical attributes.

Suppose a record has:

- 3 departments
- 4 regions
- 3 priorities

The number of possible complete signatures is:

`3 × 4 × 3 = 36`

If 37 records are assigned to these signatures, two records must share the
same complete signature.

The signature itself is a container.

The records are the objects.

This reasoning appears in data analysis, indexing, classification, feature
engineering, partition keys, and state compression.

The important condition is that the complete combination is treated as the
container identity. Sharing only one attribute does not constitute a collision
of the complete signature.

---

## C++ Case Study

The C++ program treats the principle as part of a storage-partition analysis
system.

`PartitionStore` represents a finite collection of storage partitions. Each
artifact is assigned to a partition using `std::hash`.

The program deliberately compares two different distributions.

The first is an explicitly balanced distribution. This represents the best
possible attempt to minimize the largest partition.

The second is the actual result of a hash-based allocation. Its occupancy can
be less balanced.

This distinction makes the mathematical guarantee precise:

- the balanced distribution demonstrates the lower bound;
- the hash distribution demonstrates an actual implementation;
- the difference between the two is an implementation effect, not a failure
  of the pigeonhole principle.

The program also uses modular arithmetic, finite identifier spaces, bit
patterns, duplicate detection, target occupancy calculations, validation, and
a random experiment contrasting probability with deterministic guarantees.

---

## Java Enterprise Model

The Java program models an artifact-distribution service.

The domain includes:

`Artifact`

An immutable record representing a stored artifact.

`Partition`

An immutable record representing a storage partition and its state.

`PartitionState`

An enum separating `AVAILABLE`, `DRAINING`, and `OFFLINE` partitions.

`OccupancyPolicy`

An interface defining the mathematical policy independently from the storage
service.

`GeneralizedPigeonholePolicy`

An implementation of the mathematical formulas.

`ArtifactDistributionService`

A service that uses only available partitions and creates an immutable
distribution result.

This separation is deliberate. The mathematical rule should not depend on the
details of storage assignment.

A partition can be unavailable while still existing in the domain. Therefore
the number of eligible containers is different from the total number of
physical partitions.

That distinction is important in real systems. A pigeonhole calculation must
use the actual set of containers participating in the mapping.

---

## JavaScript Event-Driven Model

The JavaScript implementation emphasizes runtime behavior.

`BucketStore` models hash-based storage using arrays of `Map` objects.

`RequestRouter` extends Node.js `EventEmitter`. Every assignment emits a
`requestAssigned` event, demonstrating how a computing workflow can react to
the allocation of objects into finite resources.

The asynchronous batch function uses `async` and `await` to model a processing
pipeline without requiring an external service.

The generator function for finite identifiers provides a concrete enumeration
of a small identifier space. This is useful for understanding the exact size
of a finite domain before applying the pigeonhole argument.

The JavaScript implementation therefore focuses on event-driven and
runtime-oriented representations rather than reproducing the object-oriented
Java domain model.

---

## Python Implementation

The Python script provides the broadest mathematical and experimental toolkit.

The central functions are:

`minimum_guaranteed_collision`

Calculates `ceil(n / k)`.

`objects_needed_for_at_least`

Calculates `k(t - 1) + 1`.

`occupancy_table`

Converts explicit assignments into occupancy counts.

`bucket_for_key`

Maps a string into a finite hash bucket.

`first_duplicate`

Detects the first repeated value with dictionary-based tracking.

`adversarial_distribution`

Creates the most balanced possible distribution for a fixed number of objects
and containers.

`random_bucket_experiment`

Shows the distinction between a probabilistic collision and a deterministic
pigeonhole guarantee.

The script also includes validation and failure handling. Zero containers are
rejected because `n / 0` is undefined and because a mapping into zero
containers is not a valid assignment model for the scenarios being studied.

---

## SQL Data Model

The PostgreSQL script models the computing domain relationally.

### `partition_pool`

Represents the finite set of containers.

The `state` check constraint distinguishes available, draining, and offline
partitions.

### `artifact`

Represents the objects being assigned.

The `artifact_key` column has a `UNIQUE` constraint so that the database can
enforce identifier uniqueness.

### `artifact_assignment`

Represents the actual object-to-container mapping.

The foreign keys guarantee that both the artifact and partition exist.

The `UNIQUE (artifact_id)` constraint prevents one artifact from being
assigned to multiple partitions simultaneously.

### `occupancy_snapshot`

Stores mathematical occupancy calculations.

The check constraint validates the generalized pigeonhole formula directly:

`ceil(object_count / container_count)`

The target formula is also validated:

`container_count * (target_occupancy - 1) + 1`

This demonstrates how a mathematical invariant can be represented as a
database integrity condition.

---

## SQL Constraints and Mathematical Guarantees

Database constraints and pigeonhole guarantees serve different purposes.

A pigeonhole guarantee is a mathematical statement about any valid mapping
from objects to containers.

A database constraint enforces an application or data-integrity rule on stored
records.

For example:

`UNIQUE (artifact_id)`

prevents an artifact from having multiple assignment rows.

The pigeonhole principle does not prevent such a database state. It only
reasons about how many objects are distributed among containers.

The SQL implementation therefore combines the two mechanisms instead of
treating them as interchangeable.

---

## SQL Indexing

The assignment table has an index on `partition_id`.

This supports queries that group or filter assignments by partition.

The artifact table has an index on `repository_name`, which supports
repository-level filtering and aggregation.

The uniqueness constraint on `artifact_key` also creates an appropriate
unique index in PostgreSQL.

Indexes do not change the pigeonhole calculation. They affect how efficiently
the database retrieves and validates the information used by the calculation.

---

## SQL Transactions

The SQL script contains a transaction demonstrating assignment integrity.

An attempt to assign the same artifact to another partition conflicts with the
unique assignment constraint.

The transaction is rolled back so that the demonstration does not alter the
consistent dataset.

This illustrates the difference between:

`mathematical impossibility`

and

`database-enforced invalid state`.

The pigeonhole principle proves that certain distributions must have a
collision. The database decides which domain relationships are legal and
enforces those rules.

---

## Deterministic Guarantee Versus Probability

One of the most important distinctions is between certainty and probability.

With 366 people and 365 possible birth days, a shared birthday is guaranteed
under the ordinary one-birthday-per-person model.

With 23 people and 365 possible days, a shared birthday is not guaranteed.
It is merely possible and, under a random model, has a substantial probability.

The implementations include random experiments to demonstrate this
difference.

The experiment cannot prove the pigeonhole principle. The principle is
already deterministic.

The experiment only illustrates how collisions can occur before they become
mathematically forced.

---

## Adversarial and Balanced Distributions

Suppose 23 objects are assigned to five containers.

The most balanced distribution is:

`5, 5, 5, 4, 4`

The maximum occupancy is five.

Because:

`ceil(23 / 5) = 5`

this distribution reaches the theoretical lower bound.

This is important for algorithm design.

If an allocation algorithm claims that it can always keep every container at
four objects in this situation, the claim is mathematically impossible.

The pigeonhole principle can therefore serve as a lower-bound proof when
evaluating algorithms and resource allocation strategies.

---

## Common Reasoning Errors

A frequent error is confusing "more objects than containers" with "large
probability of collision."

More objects than containers gives a deterministic guarantee.

Fewer objects than containers means only that a collision is not forced.
A collision may still occur.

Another error is using the wrong number of containers.

If six physical servers exist but two are offline and cannot receive requests,
a request-distribution calculation should use four eligible servers.

Another error is interpreting `ceil(n / k)` as the occupancy of every
container. It is a lower bound on the largest occupancy.

Another error is assuming that a better hash function removes collisions.
A hash function can improve distribution quality but cannot eliminate
collisions from a finite output space when the input domain is sufficiently
large.

---

## Edge Cases

The implementations explicitly address several boundary conditions.

For zero objects and a positive number of containers, the guaranteed occupancy
is zero.

For exactly as many objects as containers, a collision is not forced. A
one-to-one distribution is possible.

For one more object than containers, a collision becomes guaranteed.

For zero containers, the allocation model is invalid and the implementations
raise an error instead of attempting division.

For target occupancy `t = 1`, one object is sufficient to guarantee that some
container contains at least one object, assuming at least one valid container
exists.

These cases are useful because the formulas become easier to understand when
their boundary behavior is explicit.

---

## Performance Considerations

The direct generalized formula is constant time:

`O(1)`

It does not require constructing the objects or enumerating assignments.

Counting actual bucket occupancy requires processing the objects:

`O(n)`

where `n` is the number of assigned objects.

Maintaining a set or hash map for duplicate detection typically provides
expected `O(n)` time with `O(n)` additional memory.

An explicit array of bucket counts requires `O(k)` space for `k` containers.

The mathematical lower bound is therefore often much cheaper to calculate than
the actual distribution that it describes.

---

## Security and Systems Considerations

Finite-space reasoning is relevant to security because many security mechanisms
operate over bounded domains.

Examples include:

- truncated hashes
- finite authentication codes
- session identifiers
- nonce spaces
- short verification tokens
- finite protocol fields
- bounded state identifiers

A finite output space creates a theoretical collision limit.

Security engineering must distinguish a mathematical collision guarantee from
the practical probability of an attacker finding or exploiting a collision.

A larger namespace can make accidental or adversarial collisions harder, but
the underlying finite-space constraint remains.

Database uniqueness constraints, collision-resistant constructions, sufficient
identifier sizes, and careful state management address different parts of the
problem.

---

## Practical Interpretation

The pigeonhole principle is most useful when a computing problem can be
reframed as:

`How many distinct objects must be represented?`

versus:

`How many distinct categories or representations are available?`

If the object space exceeds the category space, some repetition is forced.

If the object count is only moderately smaller than the category count, a
collision may still be likely, but a deterministic proof requires a stronger
counting relationship.

This makes the principle useful for proving limits before implementing an
algorithm.

---

## Relationship Between the Implementations

The six artifacts intentionally use different technical representations of the
same mathematical foundation.

The Python program emphasizes executable experimentation and reusable
mathematical functions.

The JavaScript program emphasizes runtime behavior, event-driven processing,
asynchronous execution, hash storage, and finite identifier generation.

The C++ program treats the principle as a systems-level partitioning case
study and separates theoretical distributions from actual hash assignments.

The Java program models an enterprise service in which mathematical policy is
represented independently from domain objects and operational partition state.

The SQL script moves the problem into a relational environment where actual
assignments, integrity constraints, indexes, transactions, and mathematical
snapshots can coexist.

The core principle remains unchanged, but the implementation consequences
differ according to the computational environment.

---

## Key Distinctions

| Question | Pigeonhole interpretation |
|---|---|
| Are objects greater than containers? | A collision is guaranteed |
| How large must the largest container be? | At least `ceil(n / k)` |
| How many objects force occupancy `t`? | `k(t - 1) + 1` |
| Can a good hash eliminate all finite-space collisions? | No |
| Can a collision occur before it is guaranteed? | Yes |
| Does the principle identify the exact colliding object? | No |
| Does it prescribe a collision-resolution algorithm? | No |
| Does it measure actual distribution quality? | No |
| Can it establish a lower bound for an allocation algorithm? | Yes |
| Does it depend on programming language? | No |
| Can the principle be enforced by a database constraint? | The mathematical fact cannot be enforced, but related data-integrity rules can be |

---

## Final Technical Perspective

The pigeonhole principle is a compact mathematical tool with broad computing
applications.

Its practical value comes from converting vague questions about collisions,
duplicates, capacity, representation, and concentration into precise finite
counting problems.

The basic form proves that more objects than containers force repetition.

The generalized form quantifies the minimum possible maximum occupancy.

The reverse form determines how many objects are required to force a specified
occupancy threshold.

In computing, these results apply to hash buckets, identifiers, bit patterns,
modular classes, partitions, load balancing, categorical signatures, and
duplicate detection.

The implementations demonstrate the same principle at several abstraction
levels: mathematical functions, runtime data structures, systems-oriented
algorithms, enterprise domain models, and relational database constraints.
