# Linear Algebra Foundations: Scalars, Vectors, Vector Notation and Vector Spaces

## 1. Technical Scope

Linear algebra studies mathematical objects called vectors, the operations performed on them, and the structures in which those operations are defined.

The foundation begins with two distinct mathematical concepts:

- **Scalars:** Individual numerical values belonging to a field.
- **Vectors:** Ordered collections of scalar components belonging to a vector space.

A vector space provides the mathematical rules that make vector addition and scalar multiplication consistent.

This implementation focuses on finite-dimensional real coordinate spaces, particularly:

- \(\mathbb{R}^2\)
- \(\mathbb{R}^3\)
- General finite-dimensional \(\mathbb{R}^n\)

The five implementations approach these concepts through numerical computation, immutable data structures, matrix algorithms, domain modeling and relational data management.

## 2. Mathematical Foundations

### 2.1 Scalars

A scalar is a single element of a field.

The real numbers, denoted by \(\mathbb{R}\), form the scalar field used throughout these implementations.

Examples include:

\[
a=3,\quad b=2,\quad c=-5,\quad d=0.5
\]

Two fundamental scalar operations are addition and multiplication:

\[
a+b
\]

\[
a\times b
\]

The real numbers satisfy important algebraic properties:

| Property | Mathematical expression |
|---|---|
| Addition closure | \(a+b\in\mathbb{R}\) |
| Multiplication closure | \(ab\in\mathbb{R}\) |
| Additive identity | \(a+0=a\) |
| Multiplicative identity | \(a\times1=a\) |
| Additive inverse | \(a+(-a)=0\) |
| Addition commutativity | \(a+b=b+a\) |
| Multiplication commutativity | \(ab=ba\) |
| Distributivity | \(a(b+c)=ab+ac\) |

The field supplies the scalars used in vector operations.

A scalar is not itself equivalent to a vector, although a scalar can be represented as a one-component vector when working in \(\mathbb{R}^1\).

### 2.2 Vectors

A vector is an ordered collection of components.

A vector in an \(n\)-dimensional real coordinate space is written as:

\[
\mathbf{v}=
\begin{bmatrix}
v_1\\
v_2\\
\vdots\\
v_n
\end{bmatrix}
\]

Each component belongs to \(\mathbb{R}\).

For example:

\[
\mathbf{u}=
\begin{bmatrix}
2\\
3
\end{bmatrix}
\]

\[
\mathbf{v}=
\begin{bmatrix}
4\\
1
\end{bmatrix}
\]

Both vectors belong to \(\mathbb{R}^2\).

The ordering of components matters. Consequently, \((2,3)\) and \((3,2)\) represent different vectors.

A vector has the following characteristics:

- Components: The individual scalar values.
- Dimension: The number of components.
- Position in a coordinate system: Its representation relative to an established coordinate basis.
- Magnitude: A numerical measure of its length when a norm is defined.
- Direction: Its orientation in a geometric interpretation.

A vector's components depend on the selected coordinate basis. The underlying mathematical vector can remain unchanged when its coordinate representation changes.

### 2.3 Vector Notation

Several notations represent the same vector.

| Notation | Example |
|---|---|
| Bold lowercase | \(\mathbf{v}\) |
| Arrow notation | \(\vec{v}\) |
| Column notation | \(\begin{bmatrix}2\\3\end{bmatrix}\) |
| Tuple notation | \((2,3)\) |
| Component notation | \((v_1,v_2)\) |

The implementations use tuple-like or list-like representations internally.

For example, the Python representation `(2.0, 3.0)` corresponds to:

\[
\mathbf{v}=
\begin{bmatrix}
2\\
3
\end{bmatrix}
\]

The representation preserves component order and provides an explicit dimension.

### 2.4 Vector Addition

Two vectors can be added when they belong to the same coordinate space.

Let:

\[
\mathbf{u}=
\begin{bmatrix}
2\\
3
\end{bmatrix},
\qquad
\mathbf{v}=
\begin{bmatrix}
4\\
1
\end{bmatrix}
\]

Then:

\[
\mathbf{u}+\mathbf{v}
=
\begin{bmatrix}
2+4\\
3+1
\end{bmatrix}
=
\begin{bmatrix}
6\\
4
\end{bmatrix}
\]

Vector addition is component-wise.

Its important properties include:

**Closure**

\[
\mathbf{u}+\mathbf{v}\in V
\]

**Commutativity**

\[
\mathbf{u}+\mathbf{v}
=
\mathbf{v}+\mathbf{u}
\]

**Associativity**

\[
(\mathbf{u}+\mathbf{v})+\mathbf{w}
=
\mathbf{u}+(\mathbf{v}+\mathbf{w})
\]

**Additive identity**

\[
\mathbf{u}+\mathbf{0}=\mathbf{u}
\]

**Additive inverse**

\[
\mathbf{u}+(-\mathbf{u})=\mathbf{0}
\]

Vectors with different dimensions cannot be added under ordinary coordinate-wise vector addition.

For example, adding an element of \(\mathbb{R}^2\) to an element of \(\mathbb{R}^3\) is undefined.

### 2.5 Scalar Multiplication

Scalar multiplication multiplies every component of a vector by the same scalar.

For:

\[
\mathbf{u}=
\begin{bmatrix}
2\\
3
\end{bmatrix}
\]

and scalar \(a=3\):

\[
a\mathbf{u}
=
3
\begin{bmatrix}
2\\
3
\end{bmatrix}
=
\begin{bmatrix}
6\\
9
\end{bmatrix}
\]

Other cases include:

\[
0\mathbf{u}=\mathbf{0}
\]

\[
1\mathbf{u}=\mathbf{u}
\]

\[
(-1)\mathbf{u}=-\mathbf{u}
\]

Scalar multiplication satisfies:

\[
a(b\mathbf{u})=(ab)\mathbf{u}
\]

\[
1\mathbf{u}=\mathbf{u}
\]

\[
a(\mathbf{u}+\mathbf{v})
=
a\mathbf{u}+a\mathbf{v}
\]

\[
(a+b)\mathbf{u}
=
a\mathbf{u}+b\mathbf{u}
\]

These properties are essential to the definition of a vector space.

### 2.6 Dot Product

The dot product combines two vectors of equal dimension into a scalar.

For:

\[
\mathbf{u}=
\begin{bmatrix}
u_1\\
u_2\\
\vdots\\
u_n
\end{bmatrix}
\]

and:

\[
\mathbf{v}=
\begin{bmatrix}
v_1\\
v_2\\
\vdots\\
v_n
\end{bmatrix}
\]

the dot product is:

\[
\mathbf{u}\cdot\mathbf{v}
=
\sum_{i=1}^{n}u_iv_i
\]

For the example vectors:

\[
\mathbf{u}=
\begin{bmatrix}
2\\3
\end{bmatrix},
\qquad
\mathbf{v}=
\begin{bmatrix}
4\\1
\end{bmatrix}
\]

\[
\mathbf{u}\cdot\mathbf{v}
=
(2)(4)+(3)(1)=11
\]

The dot product is useful for measuring alignment and calculating vector magnitudes.

### 2.7 Vector Norm

The Euclidean norm measures the length of a vector.

It is defined as:

\[
\|\mathbf{v}\|_2
=
\sqrt{\sum_{i=1}^{n}v_i^2}
\]

For:

\[
\mathbf{u}=
\begin{bmatrix}
2\\3
\end{bmatrix}
\]

the magnitude is:

\[
\|\mathbf{u}\|_2
=
\sqrt{2^2+3^2}
=
\sqrt{13}
\]

A normalized vector has unit length:

\[
\hat{\mathbf{u}}
=
\frac{\mathbf{u}}{\|\mathbf{u}\|}
\]

The zero vector cannot be normalized because division by zero is undefined.

The implementations explicitly reject this operation.

## 3. Vector Spaces

### 3.1 Definition

A vector space \(V\) over a field \(F\) is a nonempty set equipped with:

1. Vector addition.
2. Scalar multiplication.

These operations must satisfy the vector-space axioms.

The field supplies the permissible scalars.

In these implementations:

\[
F=\mathbb{R}
\]

and:

\[
V=\mathbb{R}^n
\]

The coordinate vector space \(\mathbb{R}^n\) consists of all ordered \(n\)-tuples of real numbers.

For example:

\[
\mathbb{R}^2
=
\{(x,y)\mid x,y\in\mathbb{R}\}
\]

\[
\mathbb{R}^3
=
\{(x,y,z)\mid x,y,z\in\mathbb{R}\}
\]

The dimension determines the number of independent coordinate directions.

### 3.2 Vector-Space Axioms

A real vector space must satisfy the following ten properties.

| Axiom | Requirement |
|---|---|
| Addition closure | \(\mathbf{u}+\mathbf{v}\in V\) |
| Addition commutativity | \(\mathbf{u}+\mathbf{v}=\mathbf{v}+\mathbf{u}\) |
| Addition associativity | \((\mathbf{u}+\mathbf{v})+\mathbf{w}=\mathbf{u}+(\mathbf{v}+\mathbf{w})\) |
| Zero vector | There exists \(\mathbf{0}\in V\) such that \(\mathbf{u}+\mathbf{0}=\mathbf{u}\) |
| Additive inverse | Every \(\mathbf{u}\) has \(-\mathbf{u}\in V\) |
| Scalar closure | \(a\mathbf{u}\in V\) |
| Scalar associativity | \(a(b\mathbf{u})=(ab)\mathbf{u}\) |
| Scalar identity | \(1\mathbf{u}=\mathbf{u}\) |
| Scalar distributivity over vectors | \(a(\mathbf{u}+\mathbf{v})=a\mathbf{u}+a\mathbf{v}\) |
| Scalar distributivity over scalars | \((a+b)\mathbf{u}=a\mathbf{u}+b\mathbf{u}\) |

For \(\mathbb{R}^n\), component-wise addition and scalar multiplication satisfy these axioms.

The programs implement representative operations and validation mechanisms. They do not perform a formal symbolic proof of every axiom for arbitrary mathematical structures.

### 3.3 Zero Vector

The zero vector contains only zero components.

For \(\mathbb{R}^3\):

\[
\mathbf{0}=
\begin{bmatrix}
0\\0\\0
\end{bmatrix}
\]

It satisfies:

\[
\mathbf{u}+\mathbf{0}=\mathbf{u}
\]

The zero vector belongs to every vector space.

### 3.4 Subspaces

A subspace is a subset of a vector space that is itself a vector space under the same addition and scalar multiplication operations.

A nonempty subset \(W\) of \(V\) is a subspace when:

- It contains the zero vector.
- It is closed under vector addition.
- It is closed under scalar multiplication.

For example, the subset:

\[
W=
\left\{
\begin{bmatrix}
x\\0
\end{bmatrix}
\mid x\in\mathbb{R}
\right\}
\]

is a subspace of \(\mathbb{R}^2\).

It represents the horizontal coordinate axis.

A subset consisting only of vectors with a fixed nonzero second component is not a subspace because it does not contain the zero vector.

Subspace testing is related to closure, but it also requires nonemptiness and the relevant additive structure.

## 4. Linear Combinations, Span and Basis

### 4.1 Linear Combinations

A linear combination is an expression constructed by multiplying vectors by scalars and adding the results.

For vectors \(\mathbf{v}_1,\ldots,\mathbf{v}_k\):

\[
\mathbf{w}
=
a_1\mathbf{v}_1+
a_2\mathbf{v}_2+
\cdots+
a_k\mathbf{v}_k
\]

The coefficients \(a_i\) belong to the scalar field.

For example:

\[
\mathbf{u}=
\begin{bmatrix}
2\\3
\end{bmatrix},
\qquad
\mathbf{v}=
\begin{bmatrix}
4\\1
\end{bmatrix}
\]

Then:

\[
2\mathbf{u}+3\mathbf{v}
=
2
\begin{bmatrix}
2\\3
\end{bmatrix}
+
3
\begin{bmatrix}
4\\1
\end{bmatrix}
\]

\[
=
\begin{bmatrix}
4\\6
\end{bmatrix}
+
\begin{bmatrix}
12\\3
\end{bmatrix}
=
\begin{bmatrix}
16\\9
\end{bmatrix}
\]

The implementations validate the relationship between the number of vectors and the number of coefficients.

### 4.2 Span

The span of a collection of vectors is the set of all possible linear combinations of those vectors.

It is written as:

\[
\operatorname{span}
(\mathbf{v}_1,\ldots,\mathbf{v}_k)
\]

For the standard coordinate vectors:

\[
\mathbf{e}_1=
\begin{bmatrix}
1\\0
\end{bmatrix},
\qquad
\mathbf{e}_2=
\begin{bmatrix}
0\\1
\end{bmatrix}
\]

their span is:

\[
\operatorname{span}(\mathbf{e}_1,\mathbf{e}_2)
=
\mathbb{R}^2
\]

Every vector in \(\mathbb{R}^2\) can be represented using these two vectors.

The rank of a collection of vectors determines the dimension of its span.

### 4.3 Linear Independence

A collection of vectors is linearly independent if the equation:

\[
a_1\mathbf{v}_1+
a_2\mathbf{v}_2+
\cdots+
a_k\mathbf{v}_k
=
\mathbf{0}
\]

has only the trivial solution:

\[
a_1=a_2=\cdots=a_k=0
\]

For example:

\[
\mathbf{e}_1=
\begin{bmatrix}
1\\0
\end{bmatrix},
\qquad
\mathbf{e}_2=
\begin{bmatrix}
0\\1
\end{bmatrix}
\]

are linearly independent.

By contrast:

\[
\mathbf{a}=
\begin{bmatrix}
1\\2
\end{bmatrix},
\qquad
\mathbf{b}=
\begin{bmatrix}
2\\4
\end{bmatrix}
\]

are linearly dependent because:

\[
\mathbf{b}=2\mathbf{a}
\]

The second vector contributes no new independent direction.

### 4.4 Matrix Rank

A set of vectors can be interpreted as the columns of a matrix.

For example:

\[
A=
\begin{bmatrix}
1&2\\
2&4
\end{bmatrix}
\]

The second column is twice the first column.

Therefore:

\[
\operatorname{rank}(A)=1
\]

The rank represents the number of linearly independent columns.

The implementations use Gaussian elimination with partial pivoting to estimate matrix rank.

The general procedure is:

1. Construct a matrix from the vector components.
2. Identify a nonzero pivot.
3. Exchange rows when a better pivot is available.
4. Eliminate entries below the pivot.
5. Continue through the remaining columns.
6. Count the independent pivot rows.

Partial pivoting improves numerical stability by choosing a large available pivot.

### 4.5 Basis

A basis is a linearly independent collection of vectors that spans the entire vector space.

The standard basis of \(\mathbb{R}^2\) is:

\[
\mathcal{B}=
\left\{
\begin{bmatrix}
1\\0
\end{bmatrix},
\begin{bmatrix}
0\\1
\end{bmatrix}
\right\}
\]

The standard basis of \(\mathbb{R}^3\) is:

\[
\mathcal{B}=
\left\{
\begin{bmatrix}
1\\0\\0
\end{bmatrix},
\begin{bmatrix}
0\\1\\0
\end{bmatrix},
\begin{bmatrix}
0\\0\\1
\end{bmatrix}
\right\}
\]

For a finite-dimensional coordinate space \(\mathbb{R}^n\), a collection of exactly \(n\) linearly independent vectors forms a basis.

A basis provides a coordinate system for representing every vector in the space.

The basis is not necessarily unique.

## 5. Implementation Architecture

### 5.1 Python: Mathematical Modeling and Simulation

The Python implementation emphasizes mathematical clarity and reusable operations.

| Component | Responsibility |
|---|---|
| `Scalar` | Represents a finite real scalar |
| `Vector` | Stores immutable ordered components |
| `VectorSpace` | Defines a real coordinate space |
| `matrix_rank()` | Calculates the rank of a vector collection |
| `are_linearly_independent()` | Evaluates independence |
| `is_basis()` | Checks basis eligibility |

The `Vector` class uses a tuple to prevent accidental modification of components.

The implementation uses:

- Dataclasses for immutable mathematical objects.
- Type annotations for clearer interfaces.
- Exceptions for invalid dimensions and scalars.
- Generator expressions for component-wise calculations.
- Assertions for numerical verification.

The Gaussian elimination implementation treats vectors as matrix columns.

A tolerance is used when identifying zero-valued pivots because floating-point arithmetic can introduce small numerical errors.

The program runs using the Python standard library.

### 5.2 JavaScript: Event-Driven Vector Workspace

The JavaScript implementation introduces an event-driven architecture.

Its primary components are:

| Component | Responsibility |
|---|---|
| `Scalar` | Encapsulates real scalar values |
| `Vector` | Provides immutable vector operations |
| `VectorSpace` | Validates membership in \(\mathbb{R}^n\) |
| `VectorWorkspace` | Executes and reports computations |
| `matrixRank()` | Calculates matrix rank |
| `processBatch()` | Executes multiple independent jobs |

The implementation uses private class fields to protect internal vector components.

`Object.freeze()` prevents mutation of exposed arrays and domain objects.

The workspace extends Node.js `EventEmitter`.

It publishes two event types:

- `computed`: A calculation completed successfully.
- `operationFailed`: An operation encountered a failure.

The asynchronous batch processor uses `Promise.all()` to process independent calculations while preserving their input order.

An individual failed job produces a failure result without preventing the other jobs from completing.

This architecture separates mathematical operations from the application layer that coordinates them.

### 5.3 C++17: Computational Linear Algebra

The C++ implementation emphasizes explicit domain modeling and efficient numerical computation.

Its main components are:

| Component | Responsibility |
|---|---|
| `Scalar` | Validated real scalar |
| `Vector` | Component storage and arithmetic |
| `VectorSpace` | Dimension enforcement |
| `matrixRank()` | Gaussian elimination |
| `linearlyIndependent()` | Independence evaluation |
| `isBasis()` | Basis validation |

The vector class uses `std::vector<double>` for dynamic component storage.

Constant-reference access avoids unnecessary copies when reading vector components.

`std::vector::at()` performs bounds-checked component access.

Exceptions distinguish invalid scalar values from dimension mismatches.

The rank implementation uses row swapping and partial pivoting.

This is important because elimination without pivoting can produce unstable calculations when a pivot is zero or very small.

### 5.4 Java 17: Enterprise Domain Modeling

The Java implementation separates mathematical entities from application services.

Its architecture includes:

- Immutable `Scalar` records.
- An immutable `Vector` domain object.
- A `VectorSpace` record.
- A `LinearCombination` record.
- A `Basis` record.
- A `RankCalculator` interface.
- A `GaussianEliminationRankCalculator` implementation.
- A `VectorSpaceService` application service.

The `RankCalculator` interface allows the numerical rank implementation to be replaced without changing the application service.

The service is responsible for:

- Validating vector-space membership.
- Executing vector addition.
- Performing scalar multiplication.
- Evaluating linear combinations.
- Calculating matrix rank.
- Checking linear independence.
- Determining whether a candidate collection forms a basis.

The basis creation method returns `Optional<Basis>` because a candidate collection may fail basis validation.

This avoids representing an invalid basis as a successfully constructed domain object.

The design distinguishes mathematical domain rules from application-level orchestration.

### 5.5 PostgreSQL: Relational Representation

The PostgreSQL implementation stores mathematical objects using relational structures.

The principal entities are:

| Table | Purpose |
|---|---|
| `vector_spaces` | Defines coordinate spaces and dimensions |
| `vectors` | Stores vector identities |
| `vector_components` | Stores ordered scalar components |
| `scalars` | Stores named scalar values |
| `operation_history` | Records evaluated operations |

The primary relationships are:

- A vector space can contain multiple vectors.
- A vector belongs to one vector space.
- A vector contains multiple ordered components.
- An operation can reference one or two existing vectors.

The relational model separates vector identity from component storage.

This allows individual vector components to be queried, aggregated and validated independently.

The database uses primary keys, foreign keys, unique constraints, check constraints, domains, indexes, views, functions and triggers.

The `vector_catalog` view combines vector metadata with component information.

The `validate_complete_vector()` function determines whether a vector has all expected components.

The `validate_component_position()` trigger prevents inserting a component outside its vector's declared dimension.

The norm, dot product, vector addition and scalar multiplication functions perform numerical operations directly within PostgreSQL.

The reporting queries evaluate component counts, norms, dot products, linear combinations and two-dimensional basis eligibility.

The database stores incomplete vectors as identifiable records so that their invalid state can be reported rather than silently treating them as valid mathematical objects.

## 6. Mathematical Concepts and Their Implementation Relationships

| Mathematical concept | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Real scalar | `Scalar` | `Scalar` | `Scalar` | `Scalar` record | `real_scalar` |
| Vector | `Vector` | `Vector` | `Vector` | `Vector` | `vectors` |
| Components | Tuple | Frozen array | STL vector | Immutable list | `vector_components` |
| Vector space | `VectorSpace` | `VectorSpace` | `VectorSpace` | `VectorSpace` record | `vector_spaces` |
| Addition | Operator overload | `add()` | Operator overload | `add()` | `vector_addition()` |
| Scalar multiplication | `scale()` | `scale()` | `scale()` | `scale()` | `vector_scalar_multiplication()` |
| Dot product | `dot()` | `dot()` | `dot()` | `dot()` | `vector_dot_product()` |
| Norm | `norm()` | `norm()` | `norm()` | `norm()` | `vector_norm()` |
| Linear combination | `linear_combination()` | `linearCombination()` | `linearCombination()` | `combine()` | CTE |
| Matrix rank | `matrix_rank()` | `matrixRank()` | `matrixRank()` | Rank service | Basis evaluation query |
| Basis validation | `is_basis()` | `isBasis()` | `isBasis()` | `createBasis()` | Determinant query |

## 7. Worked Computational Examples

The implementations use a consistent mathematical example.

Let:

\[
\mathbf{u}=
\begin{bmatrix}
2\\3
\end{bmatrix}
\]

\[
\mathbf{v}=
\begin{bmatrix}
4\\1
\end{bmatrix}
\]

### Vector addition

\[
\mathbf{u}+\mathbf{v}
=
\begin{bmatrix}
6\\4
\end{bmatrix}
\]

### Vector subtraction

\[
\mathbf{u}-\mathbf{v}
=
\begin{bmatrix}
-2\\2
\end{bmatrix}
\]

### Scalar multiplication

\[
3\mathbf{u}
=
\begin{bmatrix}
6\\9
\end{bmatrix}
\]

### Dot product

\[
\mathbf{u}\cdot\mathbf{v}=11
\]

### Norm

\[
\|\mathbf{u}\|_2=\sqrt{13}
\]

### Linear combination

\[
2\mathbf{u}+3\mathbf{v}
=
\begin{bmatrix}
16\\9
\end{bmatrix}
\]

### Standard basis

\[
\mathbf{e}_1=
\begin{bmatrix}
1\\0
\end{bmatrix}
\]

\[
\mathbf{e}_2=
\begin{bmatrix}
0\\1
\end{bmatrix}
\]

The standard basis has rank two and spans \(\mathbb{R}^2\).

## 8. Validation and Numerical Reliability

### 8.1 Dimension Validation

Vector operations require compatible dimensions.

The implementations reject:

\[
\begin{bmatrix}
1\\2
\end{bmatrix}
+
\begin{bmatrix}
1\\2\\3
\end{bmatrix}
\]

This prevents invalid component-wise calculations.

### 8.2 Scalar Validation

Scalars and vector components must be finite real numerical values.

The implementations reject:

- NaN.
- Positive infinity.
- Negative infinity.
- Invalid numeric types where applicable.

### 8.3 Floating-Point Precision

Computer arithmetic generally represents real values using finite-precision floating-point formats.

Consequently, exact equality is not always suitable for numerical algorithms.

A tolerance is used:

\[
|a-b|\leq\epsilon
\]

The sample implementations use:

\[
\epsilon=10^{-9}
\]

This is a practical demonstration value, not a universal tolerance.

The appropriate tolerance depends on the magnitude of the input, the numerical method, accumulated rounding errors and the precision requirements of the application.

### 8.4 Gaussian Elimination Limitations

The rank calculations use partial pivoting and a fixed absolute tolerance.

This approach is appropriate for the small educational examples included here.

It does not provide the numerical robustness of advanced singular-value decomposition or rank-revealing QR decomposition.

For ill-conditioned matrices, a fixed absolute tolerance can produce misleading rank estimates.

The mathematical rank of a matrix is exact, whereas the numerical rank is an approximation determined by a numerical threshold.

### 8.5 Zero-Vector Normalization

For the zero vector:

\[
\|\mathbf{0}\|=0
\]

Normalization requires division by the magnitude.

Therefore:

\[
\frac{\mathbf{0}}{\|\mathbf{0}\|}
\]

is undefined.

Every implementation explicitly rejects this operation.

## 9. Complexity and Performance

Let:

- \(n\) represent vector dimension.
- \(k\) represent the number of vectors.
- \(m\) represent the number of matrix rows.

| Operation | Time complexity | Main consideration |
|---|---:|---|
| Scalar addition | \(O(1)\) | Constant-time arithmetic |
| Vector addition | \(O(n)\) | Processes every component |
| Vector subtraction | \(O(n)\) | Processes every component |
| Scalar multiplication | \(O(n)\) | Processes every component |
| Dot product | \(O(n)\) | Component-wise multiplication and accumulation |
| Euclidean norm | \(O(n)\) | Dot product followed by square root |
| Linear combination | \(O(kn)\) | Processes all vector components |
| Vector equality | \(O(n)\) | Compares corresponding components |
| Gaussian elimination | \(O(mk\min(m,k))\) | Pivot selection and row elimination |
| Basis validation | Rank-dependent | Requires dimension and independence checks |

For square \(n\times n\) matrices, Gaussian elimination has cubic time complexity:

\[
O(n^3)
\]

Vector operations generally require linear memory in the vector dimension.

Matrix rank calculation requires storage proportional to the matrix size:

\[
O(mk)
\]

The implementations prioritize clear numerical behavior and correctness for moderate input sizes rather than highly optimized large-scale numerical computation.

## 10. Security and Data Integrity

Although basic linear algebra is a mathematical subject, software implementations still require appropriate engineering controls.

Important considerations include:

- Validate numerical input before computation.
- Reject NaN and infinite values.
- Enforce consistent vector dimensions.
- Avoid mutable shared numerical state.
- Preserve component ordering.
- Handle invalid operations explicitly.
- Use database constraints to protect relational integrity.
- Avoid exposing unvalidated numerical data to downstream systems.
- Use transactions when related database changes must succeed together.
- Apply suitable database permissions to prevent unauthorized modification.

The PostgreSQL implementation uses foreign keys to maintain relationships between spaces, vectors and components.

Its trigger protects component-index validity.

A complete vector is checked before numerical functions operate on it.

One important database limitation is that component completeness is checked when a vector is used, rather than enforced immediately when the vector record is created. This permits incomplete records to be retained for validation and reporting.

For a production database, permissions, transaction isolation and concurrency behavior must also be considered. In particular, the component-validation functions should be used with an appropriate transaction strategy if concurrent modifications are possible.

## 11. Execution Requirements

| Deliverable | Runtime | External dependencies |
|---|---|---|
| Python | Python 3.10 or later | None |
| JavaScript | Node.js 18 or later | None |
| C++17 | C++17-compatible compiler | None |
| Java | Java 17 | None |
| PostgreSQL | PostgreSQL 14 or later | None |

The implementations are independent.

Each program defines its own mathematical domain objects and performs its own validation and calculations.

The PostgreSQL script creates its objects inside the `linear_algebra` schema and executes its sample operations within a transaction.

## 12. Important Mathematical Distinctions

The following concepts are related but should not be treated as interchangeable.

| Concept | Meaning |
|---|---|
| Scalar | A single element of a field |
| Vector | An element of a vector space |
| Component | A scalar coordinate of a vector |
| Dimension of a vector | Number of its components in a coordinate representation |
| Dimension of a vector space | Number of vectors in any basis of a finite-dimensional vector space |
| Vector addition | Operation combining two compatible vectors |
| Scalar multiplication | Operation scaling a vector by a field element |
| Vector space | A set satisfying the vector-space axioms |
| Linear combination | A sum of scalar multiples of vectors |
| Span | The set of all linear combinations of a collection |
| Linear independence | Absence of nontrivial linear dependencies |
| Basis | An independent spanning collection |
| Rank | Dimension of the span of a collection of vectors |

A particularly important distinction concerns vector dimension and vector-space dimension.

In \(\mathbb{R}^3\), every vector has three components. The vector space itself has dimension three because its basis contains three independent vectors.

The dimension of a vector is a representation property, while the dimension of a finite-dimensional vector space is a structural mathematical property.

## 13. Limitations of the Implementations

These implementations focus on introductory finite-dimensional real coordinate spaces.

They do not provide a complete implementation of every mathematical structure associated with linear algebra.

The principal limitations are:

1. Only the real scalar field is implemented.
2. Complex vector spaces are not included.
3. General abstract vector spaces are not modeled.
4. Matrix storage and operations are limited to rank evaluation and vector-related calculations.
5. The numerical rank algorithms use fixed absolute tolerances.
6. The Python, JavaScript, C++17 and Java implementations do not implement symbolic algebra.
7. The PostgreSQL basis-evaluation query uses a determinant test for selected two-dimensional vector pairs rather than a general matrix-rank engine.
8. The SQL implementation does not provide automatic normalization or a generalized vector-space subspace engine.
9. Database completeness validation occurs when vectors are evaluated rather than at initial vector registration.
10. The examples are designed for mathematical learning and computational verification, not as a replacement for specialized numerical libraries in large-scale scientific workloads.

The central mathematical relationship remains consistent across all five implementations:

\[
\boxed{
\text{Scalar Field}
\longrightarrow
\text{Vector Operations}
\longrightarrow
\text{Vector Space}
}
\]

Linear combinations, independence, span and basis build on this foundation and establish the mathematical structure needed for more advanced linear algebra.
