# Vector Operations: Mathematical Computation and Numerical Engineering

## 1. Project Overview

This project implements fundamental and advanced vector operations using Python, JavaScript, C++17, Java 17 and PostgreSQL.

A vector is an ordered collection of numerical components representing a mathematical quantity in a coordinate space.

For an n-dimensional vector:

\[
\mathbf{u}=(u_1,u_2,\ldots,u_n)
\]

The implementations cover four central operations:

- Vector addition
- Scalar multiplication
- Dot product
- Vector norms

They also implement normalization, Euclidean distance, cosine similarity and orthogonality testing.

Each implementation uses a different engineering approach. Python emphasizes mathematical modeling and validation. JavaScript introduces asynchronous batch processing and event-driven execution. C++17 emphasizes efficient numerical computation and memory management. Java 17 introduces enterprise-oriented services, immutable domain objects and concurrent processing. PostgreSQL provides relational storage, numerical functions, constraints and execution auditing.

## 2. Mathematical Foundations

### 2.1 Vector Representation

An n-dimensional vector contains n numerical components.

\[
\mathbf{u}=
\begin{bmatrix}
u_1\\
u_2\\
\vdots\\
u_n
\end{bmatrix}
\]

The dimension determines the number of components.

For example:

\[
\mathbf{u}=(3,4)
\]

is a two-dimensional vector, while:

\[
\mathbf{v}=(4,3,2)
\]

is a three-dimensional vector.

Operations involving two vectors generally require equal dimensions.

### 2.2 Vector Addition

Vector addition combines corresponding components.

For two vectors:

\[
\mathbf{u}=(u_1,u_2,\ldots,u_n)
\]

\[
\mathbf{v}=(v_1,v_2,\ldots,v_n)
\]

their sum is:

\[
\mathbf{u}+\mathbf{v}
=
(u_1+v_1,u_2+v_2,\ldots,u_n+v_n)
\]

Example:

\[
(3,4)+(4,3)=(7,7)
\]

The operation requires equal dimensions.

Its time complexity is:

\[
O(n)
\]

Its additional result storage is:

\[
O(n)
\]

### 2.3 Scalar Multiplication

Scalar multiplication multiplies every vector component by the same numerical value.

For scalar \(c\):

\[
c\mathbf{u}
=
(cu_1,cu_2,\ldots,cu_n)
\]

Example:

\[
3(3,4)=(9,12)
\]

A positive scalar changes the magnitude without reversing the direction.

A negative scalar reverses the direction.

A zero scalar produces the zero vector.

The computational complexity is \(O(n)\).

### 2.4 Dot Product

The dot product produces a scalar from two vectors.

\[
\mathbf{u}\cdot\mathbf{v}
=
\sum_{i=1}^{n}u_iv_i
\]

Example:

\[
\mathbf{u}=(3,4)
\]

\[
\mathbf{v}=(4,3)
\]

\[
\mathbf{u}\cdot\mathbf{v}
=
(3\times4)+(4\times3)
\]

\[
=24
\]

The dot product has several mathematical properties:

| Property | Expression |
|---|---|
| Commutativity | \(u\cdot v=v\cdot u\) |
| Distributivity | \(u\cdot(v+w)=u\cdot v+u\cdot w\) |
| Scalar multiplication | \((cu)\cdot v=c(u\cdot v)\) |
| Self-product | \(u\cdot u=\|u\|_2^2\) |
| Orthogonality | \(u\cdot v=0\) |

The operation requires equal dimensions and has \(O(n)\) time complexity.

### 2.5 Vector Norms

A norm measures the magnitude of a vector.

It must satisfy non-negativity, definiteness, absolute homogeneity and the triangle inequality.

Three important norms are implemented.

#### L1 norm

The L1 norm is the sum of the absolute values of the components.

\[
\|\mathbf{u}\|_1
=
\sum_{i=1}^{n}|u_i|
\]

For \((3,4)\):

\[
\|\mathbf{u}\|_1=3+4=7
\]

It is also called the Manhattan norm.

#### L2 norm

The L2 norm measures Euclidean magnitude.

\[
\|\mathbf{u}\|_2
=
\sqrt{\sum_{i=1}^{n}u_i^2}
\]

For \((3,4)\):

\[
\|\mathbf{u}\|_2
=
\sqrt{9+16}=5
\]

This is the standard geometric length of a vector.

#### L-infinity norm

The infinity norm identifies the largest absolute component.

\[
\|\mathbf{u}\|_\infty
=
\max_i|u_i|
\]

For \((3,4)\):

\[
\|\mathbf{u}\|_\infty=4
\]

#### General L-p norm

For \(p\geq1\):

\[
\|\mathbf{u}\|_p
=
\left(
\sum_{i=1}^{n}|u_i|^p
\right)^{1/p}
\]

The infinity norm is the limiting case as \(p\) approaches infinity.

The implementations support L1, L2, infinity and general finite p-norm calculations.

## 3. Additional Mathematical Operations

### 3.1 Normalization

Normalization converts a nonzero vector into a unit vector.

\[
\hat{\mathbf{u}}
=
\frac{\mathbf{u}}{\|\mathbf{u}\|_2}
\]

For:

\[
\mathbf{u}=(3,4)
\]

the normalized vector is:

\[
\hat{\mathbf{u}}=
\left(\frac35,\frac45\right)
\]

Its Euclidean norm equals one.

The zero vector cannot be normalized because division by its magnitude is undefined.

### 3.2 Euclidean Distance

The distance between two vectors is the Euclidean norm of their difference.

\[
d(\mathbf{u},\mathbf{v})
=
\|\mathbf{u}-\mathbf{v}\|_2
\]

For the example vectors:

\[
\mathbf{u}=(3,4)
\]

\[
\mathbf{v}=(4,3)
\]

\[
d(\mathbf{u},\mathbf{v})
=
\sqrt{(-1)^2+1^2}
=
\sqrt2
\]

### 3.3 Cosine Similarity

Cosine similarity measures the angular relationship between two nonzero vectors.

\[
\cos(\theta)
=
\frac{\mathbf{u}\cdot\mathbf{v}}
{\|\mathbf{u}\|_2\|\mathbf{v}\|_2}
\]

Its value lies between -1 and 1, subject to floating-point rounding.

| Value | Interpretation |
|---|---|
| 1 | Same direction |
| 0 | Orthogonal vectors |
| -1 | Opposite directions |

Cosine similarity is undefined if either vector is zero.

### 3.4 Orthogonality

Two vectors are orthogonal when their dot product equals zero.

\[
\mathbf{u}\cdot\mathbf{v}=0
\]

For numerical computation, an absolute tolerance is used:

\[
|\mathbf{u}\cdot\mathbf{v}|\leq\epsilon
\]

This prevents small floating-point errors from incorrectly classifying mathematically orthogonal vectors.

## 4. Numerical Example

The implementations use the following vectors:

\[
\mathbf{u}=(3,4)
\]

\[
\mathbf{v}=(4,3)
\]

| Operation | Result |
|---|---|
| Addition | (7, 7) |
| Subtraction | (-1, 1) |
| Scalar multiplication, 3u | (9, 12) |
| Dot product | 24 |
| L1 norm of u | 7 |
| L2 norm of u | 5 |
| Infinity norm of u | 4 |
| L2 normalization of u | (0.6, 0.8) |
| Euclidean distance | 1.414214 |
| Cosine similarity | 0.96 |

These results provide common numerical reference values for testing all five implementations.

## 5. Python Implementation

**Source file:** `vector_operations.py`

The Python implementation uses an immutable dataclass-based vector model.

### Main components

| Component | Responsibility |
|---|---|
| `Vector` | Stores and computes vector values |
| `VectorError` | Base numerical exception |
| `DimensionMismatchError` | Handles incompatible dimensions |
| `ZeroVectorError` | Handles undefined zero-vector operations |
| `VectorOperation` | Enumerates supported operations |
| `VectorEngine` | Provides operation dispatch and comparison |
| `save_vectors()` | Persists vector records |
| `load_vectors()` | Restores and validates vector records |

### Engineering decisions

The vector is represented using a tuple rather than a mutable list.

This prevents accidental modification after construction.

The implementation uses `math.fsum()` for accurate summation and `math.hypot()` for stable Euclidean magnitude calculations.

The general p-norm uses maximum-component scaling to reduce intermediate overflow.

JSON persistence stores both the components and dimension metadata. The loader checks their consistency before accepting a record.

The assertion section verifies addition, dot product, normalization and orthogonality.

## 6. JavaScript Implementation

**Source file:** `vector_operations.js`

The JavaScript implementation emphasizes event-driven processing and asynchronous execution.

### Main components

| Component | Responsibility |
|---|---|
| `Vector` | Immutable numerical representation |
| `VectorEventBus` | Publishes operation events |
| `VectorService` | Executes operations and processes batches |
| `executeBatch()` | Runs multiple independent calculations |
| `saveVectors()` | Persists vector records |
| `loadVectors()` | Validates and restores records |

### Event-driven execution

Two principal events are supported:

- `operation:completed`
- `operation:failed`

Successful operations update an operation counter.

Failed operations publish error information without silently converting an unsuccessful calculation into a valid result.

### Asynchronous batch processing

The batch service uses asynchronous workers and a configurable concurrency limit.

Each job produces an independent result record.

A failed calculation does not invalidate the results of other jobs.

The output retains the original job ordering.

The batch implementation demonstrates concurrency management without introducing external npm dependencies.

The numerical implementation also uses compensated summation for dot products and scaled sum-of-squares calculations for Euclidean norms.

## 7. C++17 Implementation

**Source file:** `vector_operations.cpp`

The C++ implementation emphasizes numerical computation, typed domain modeling and standard-library algorithms.

### Main components

| Component | Responsibility |
|---|---|
| `Vector` | Owns vector components |
| `VectorError` | Handles numerical errors |
| `DimensionMismatchError` | Enforces dimensional compatibility |
| `ZeroVectorError` | Rejects undefined operations |
| `NormType` | Selects a norm |
| `VectorStatistics` | Groups norm measurements |
| `VectorCalculator` | Coordinates calculations and reporting |

### Memory and performance

The implementation uses `std::vector<double>` for dynamic storage.

Vectors own their component data, and references to components are exposed as constant references.

Result-producing operations allocate their own output storage.

The dot product accumulates using `long double` to improve intermediate precision on platforms that support extended precision.

The Euclidean norm uses `std::hypot()` iteratively to reduce intermediate overflow risk.

### Complexity

| Operation | Time complexity | Result storage |
|---|---:|---:|
| Addition | O(n) | O(n) |
| Subtraction | O(n) | O(n) |
| Scalar multiplication | O(n) | O(n) |
| Dot product | O(n) | O(1) |
| L1 norm | O(n) | O(1) |
| L2 norm | O(n) | O(1) |
| Infinity norm | O(n) | O(1) |
| Normalization | O(n) | O(n) |

The program also demonstrates calculations involving 10,000 components.

## 8. Java 17 Implementation

**Source file:** `VectorOperations.java`

The Java implementation models vector calculations as an enterprise-oriented numerical service.

### Domain types

| Type | Purpose |
|---|---|
| `Vector` | Immutable numerical object |
| `Operation` | Enumerates available operations |
| `VectorStatistics` | Groups norm measurements |
| `CalculationResult` | Represents successful or failed execution |
| `VectorService` | Provides the calculation service |
| `VectorException` | Base application exception |
| `DimensionMismatchException` | Represents incompatible dimensions |
| `ZeroVectorException` | Represents undefined zero-vector operations |

### Immutability

The vector uses a private final array.

The constructor copies incoming data.

The component accessor returns a defensive copy.

These measures prevent external modification of the vector's internal numerical state.

### Service architecture

The service uses explicit operation types and validates the required arguments before performing calculations.

This separates mathematical computation from application-level operation dispatch.

### Concurrent calculations

`CompletableFuture` and `ExecutorService` provide asynchronous batch norm calculations.

The implementation uses a fixed-size thread pool.

A batch calculation produces a structured result for each vector.

Individual failures are represented through `CalculationResult` instead of terminating the entire batch.

The executor is explicitly shut down after processing.

## 9. PostgreSQL Implementation

**Source file:** `vector_operations.sql`

The PostgreSQL implementation provides relational storage and reusable numerical functions.

It uses a dedicated schema named `vector_lab`.

### Database architecture

The principal relationships are:

    vector_lab
        |
        +-- vectors
        |     |
        |     +-- vector_id
        |     +-- vector_name
        |     +-- dimension
        |     +-- components
        |
        +-- operation_types
        |     |
        |     +-- operation_id
        |     +-- operation_code
        |
        +-- vector_operations
        |     |
        |     +-- operation_id
        |     +-- first_vector_id
        |     +-- second_vector_id
        |     +-- result_vector_id
        |     +-- execution_status
        |
        +-- operation_audit
              |
              +-- operation_record_id
              +-- previous_status
              +-- new_status

### Vector storage

The `vectors` table stores numerical components in PostgreSQL `DOUBLE PRECISION[]` arrays.

The dimension column records the expected number of components.

A check constraint enforces one-dimensional, one-based arrays whose cardinality matches the declared dimension.

The `validate_vector()` function performs additional checks for empty arrays and non-finite components.

### Numerical functions

| Function | Operation |
|---|---|
| `vector_add()` | Element-wise addition |
| `vector_scale()` | Scalar multiplication |
| `vector_dot()` | Dot product |
| `vector_l1_norm()` | L1 norm |
| `vector_l2_norm()` | L2 norm |
| `vector_infinity_norm()` | Infinity norm |
| `vector_normalize()` | Unit-vector calculation |
| `vector_cosine_similarity()` | Cosine similarity |

These functions provide reusable database-level numerical operations.

### Operation execution

The `execute_vector_operation()` procedure coordinates numerical computation and records successful execution.

The operation catalog separates the mathematical operation definition from individual execution records.

The status field represents execution state.

The audit trigger records insertion and status transitions.

### Database integrity

The schema uses:

- Primary keys for entity identification.
- Foreign keys for relational consistency.
- Unique constraints for vector names and operation codes.
- Check constraints for dimensions and execution states.
- Indexes for dimension filtering, execution reporting and vector lookup.
- Triggers for operation auditing.

### Transaction handling

The script demonstrates savepoints and rollback.

The transaction example inserts a temporary vector, calculates its norm and then rolls back the insertion.

The complete script executes within an explicit transaction.

The operation procedure propagates numerical failures to its caller. A caller that needs to retain failed-operation audit records must handle those failures in a separate transaction boundary.

## 10. Distinctions Between the Four Core Operations

The four central operations have different input and output types.

| Operation | Input | Output | Main purpose |
|---|---|---|---|
| Addition | Two equal-dimensional vectors | Vector | Combine components |
| Scalar multiplication | Vector and scalar | Vector | Change magnitude and possibly direction |
| Dot product | Two equal-dimensional vectors | Scalar | Measure directional relationship |
| Norm | One vector | Scalar | Measure magnitude |

These operations are mathematically related but not interchangeable.

For example, addition produces a new vector, while the dot product produces a scalar.

A norm measures magnitude, while scalar multiplication changes the components of the vector.

## 11. Validation and Edge Cases

All implementations account for important mathematical and computational restrictions.

| Condition | Expected behavior |
|---|---|
| Empty vector | Reject |
| Different dimensions | Reject binary operation |
| NaN component | Reject |
| Infinite component | Reject |
| Infinite scalar | Reject |
| Zero vector normalization | Reject |
| Zero-vector cosine similarity | Reject |
| Invalid norm order | Reject |
| Floating-point overflow | Report failure |
| Nearly orthogonal vectors | Apply tolerance |
| High-dimensional vectors | Process dynamically |

### Floating-point limitations

Floating-point arithmetic cannot represent every real number exactly.

For example:

\[
0.1+0.2\neq0.3
\]

in ordinary binary floating-point arithmetic.

Consequently, numerical comparisons should generally use tolerances instead of exact equality.

The implementations use stable norm calculations and, where appropriate, compensated or extended-precision accumulation.

These techniques reduce numerical error but cannot eliminate every possible rounding error or overflow condition.

## 12. Performance Considerations

For two vectors of dimension n, the fundamental operations require linear time.

The main performance factors are:

- Number of components.
- Allocation of intermediate vectors.
- Floating-point precision.
- Memory locality.
- Batch concurrency.
- Serialization overhead.
- Database array processing.

For repeated high-dimensional calculations, allocating new result arrays for every operation can increase memory pressure.

A production numerical system may use reusable buffers, specialized matrix operations, parallel numerical kernels or hardware-accelerated libraries.

Parallel processing is particularly useful when many independent vectors must be evaluated.

Parallelizing a single small dot product may introduce more scheduling overhead than computational benefit.

## 13. Security and Data Integrity

The implementations validate numerical inputs before computation.

They avoid accepting non-finite values as valid vector components.

The PostgreSQL implementation uses typed parameters and relational constraints rather than dynamically constructing SQL statements.

JSON persistence validates the structure and dimension metadata of stored vectors.

Production deployments should also enforce appropriate filesystem permissions, database roles, connection restrictions, input-size limits and resource quotas.

Vector dimensions should be bounded according to the application's operational requirements because excessively large inputs can consume substantial memory and processing time.

## 14. Execution Instructions

### Python

File: `vector_operations.py`

Run using Python 3.10 or later:

`python vector_operations.py`

No third-party package is required.

### JavaScript

File: `vector_operations.js`

Run using Node.js 18 or later:

`node vector_operations.js`

The implementation uses Node.js built-in modules.

### C++17

File: `vector_operations.cpp`

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic vector_operations.cpp -o vector_operations`

Run:

`./vector_operations`

### Java 17

File: `VectorOperations.java`

Compile:

`javac --release 17 VectorOperations.java`

Run:

`java VectorOperations`

### PostgreSQL

File: `vector_operations.sql`

Execute against PostgreSQL 14 or later:

`psql -U postgres -d your_database -f vector_operations.sql`

The database user must have permission to create schemas, tables, functions, procedures and triggers.

The script uses PostgreSQL array types and built-in numerical functions. It does not require the `pgvector` extension.

## 15. Verification Matrix

The following reference calculations can be used to verify the implementations.

| Test | Expected result |
|---|---|
| (3,4) + (4,3) | (7,7) |
| 3 × (3,4) | (9,12) |
| (3,4) · (4,3) | 24 |
| L1 norm of (3,4) | 7 |
| L2 norm of (3,4) | 5 |
| Infinity norm of (3,4) | 4 |
| Normalization of (3,4) | (0.6,0.8) |
| Distance between (3,4) and (4,3) | √2 |
| Cosine similarity | 0.96 |
| Dot product of (1,0) and (0,1) | 0 |
| L2 norm of (0,0) | 0 |

The numerical implementations use these cases to establish consistency across programming languages and the relational database layer.
