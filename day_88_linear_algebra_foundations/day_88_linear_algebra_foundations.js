"use strict";

/*
 * Linear Algebra Foundations
 * Event-driven vector workspace using JavaScript and Node.js.
 *
 * Features:
 * - Scalar and vector validation
 * - Immutable vector operations
 * - Vector-space operations
 * - Linear combinations
 * - Linear independence and basis evaluation
 * - Event-driven computation
 * - Asynchronous batch processing
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class LinearAlgebraError extends Error {
    constructor(message) {
        super(message);
        this.name = "LinearAlgebraError";
    }
}

class DimensionError extends LinearAlgebraError {
    constructor(message) {
        super(message);
        this.name = "DimensionError";
    }
}

class ValidationError extends LinearAlgebraError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

const TOLERANCE = 1e-9;

function validateScalar(value) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value)
    ) {
        throw new ValidationError(
            "A scalar must be a finite real number."
        );
    }

    return value;
}

class Scalar {
    #value;

    constructor(value) {
        this.#value = validateScalar(value);
        Object.freeze(this);
    }

    get value() {
        return this.#value;
    }

    add(other) {
        return new Scalar(this.#value + other.value);
    }

    multiply(other) {
        return new Scalar(this.#value * other.value);
    }

    toString() {
        return String(this.#value);
    }
}

class Vector {
    #components;

    constructor(components) {
        if (!Array.isArray(components) || components.length === 0) {
            throw new DimensionError(
                "A vector requires at least one component."
            );
        }

        this.#components = Object.freeze(
            components.map(validateScalar)
        );

        Object.freeze(this);
    }

    get components() {
        return this.#components;
    }

    get dimension() {
        return this.#components.length;
    }

    assertCompatible(other) {
        if (!(other instanceof Vector)) {
            throw new ValidationError("Expected a Vector instance.");
        }

        if (this.dimension !== other.dimension) {
            throw new DimensionError(
                `Cannot combine R^${this.dimension} and R^${other.dimension}.`
            );
        }
    }

    add(other) {
        this.assertCompatible(other);

        return new Vector(
            this.#components.map(
                (value, index) => value + other.#components[index]
            )
        );
    }

    subtract(other) {
        this.assertCompatible(other);

        return new Vector(
            this.#components.map(
                (value, index) => value - other.#components[index]
            )
        );
    }

    scale(scalar) {
        validateScalar(scalar);

        return new Vector(
            this.#components.map(value => value * scalar)
        );
    }

    dot(other) {
        this.assertCompatible(other);

        return this.#components.reduce(
            (sum, value, index) =>
                sum + value * other.#components[index],
            0
        );
    }

    norm() {
        return Math.sqrt(this.dot(this));
    }

    normalize() {
        const magnitude = this.norm();

        if (magnitude <= TOLERANCE) {
            throw new LinearAlgebraError(
                "Cannot normalize the zero vector."
            );
        }

        return this.scale(1 / magnitude);
    }

    isZero() {
        return this.#components.every(
            value => Math.abs(value) <= TOLERANCE
        );
    }

    equals(other) {
        this.assertCompatible(other);

        return this.#components.every(
            (value, index) =>
                Math.abs(value - other.#components[index]) <= TOLERANCE
        );
    }

    toString() {
        return `(${this.#components.join(", ")})`;
    }

    toJSON() {
        return {
            notation: this.toString(),
            dimension: this.dimension,
            components: [...this.#components]
        };
    }
}

class VectorSpace {
    constructor(dimension, field = "R") {
        if (!Number.isSafeInteger(dimension) || dimension <= 0) {
            throw new DimensionError(
                "Vector-space dimension must be a positive integer."
            );
        }

        if (field !== "R") {
            throw new ValidationError(
                "Only the real field R is supported."
            );
        }

        this.dimension = dimension;
        this.field = field;
        Object.freeze(this);
    }

    validate(vector) {
        if (!(vector instanceof Vector)) {
            throw new ValidationError("Expected a Vector.");
        }

        if (vector.dimension !== this.dimension) {
            throw new DimensionError(
                `Expected a vector in R^${this.dimension}.`
            );
        }

        return true;
    }

    zero() {
        return new Vector(
            Array(this.dimension).fill(0)
        );
    }

    add(a, b) {
        this.validate(a);
        this.validate(b);
        return a.add(b);
    }

    multiply(scalar, vector) {
        this.validate(vector);
        return vector.scale(scalar);
    }

    linearCombination(vectors, coefficients) {
        if (
            !Array.isArray(vectors) ||
            !Array.isArray(coefficients) ||
            vectors.length !== coefficients.length
        ) {
            throw new ValidationError(
                "Vectors and coefficients must have equal lengths."
            );
        }

        return vectors.reduce(
            (result, vector, index) => {
                this.validate(vector);
                return result.add(
                    vector.scale(coefficients[index])
                );
            },
            this.zero()
        );
    }
}

/*
 * Gaussian elimination with partial pivoting.
 * Input vectors are interpreted as matrix columns.
 */
function matrixRank(vectors) {
    if (vectors.length === 0) {
        return 0;
    }

    if (!vectors.every(vector => vector instanceof Vector)) {
        throw new ValidationError("All inputs must be vectors.");
    }

    const dimension = vectors[0].dimension;

    if (!vectors.every(v => v.dimension === dimension)) {
        throw new DimensionError(
            "All vectors must have the same dimension."
        );
    }

    const matrix = Array.from(
        { length: dimension },
        (_, row) => vectors.map(v => v.components[row])
    );

    const rows = dimension;
    const columns = vectors.length;

    let rank = 0;

    for (let col = 0; col < columns && rank < rows; col++) {
        let pivot = rank;

        for (let row = rank + 1; row < rows; row++) {
            if (
                Math.abs(matrix[row][col]) >
                Math.abs(matrix[pivot][col])
            ) {
                pivot = row;
            }
        }

        if (Math.abs(matrix[pivot][col]) <= TOLERANCE) {
            continue;
        }

        [matrix[rank], matrix[pivot]] =
            [matrix[pivot], matrix[rank]];

        const pivotValue = matrix[rank][col];

        for (let row = rank + 1; row < rows; row++) {
            const factor = matrix[row][col] / pivotValue;

            for (let j = col; j < columns; j++) {
                matrix[row][j] -= factor * matrix[rank][j];
            }
        }

        rank++;
    }

    return rank;
}

function isBasis(vectors, space) {
    if (!vectors.every(v => space.validate(v))) {
        return false;
    }

    return (
        vectors.length === space.dimension &&
        matrixRank(vectors) === space.dimension
    );
}

/*
 * Event-driven workspace.
 * Consumers can subscribe to computation and failure events.
 */
class VectorWorkspace extends EventEmitter {
    constructor(space) {
        super();

        if (!(space instanceof VectorSpace)) {
            throw new ValidationError("A VectorSpace is required.");
        }

        this.space = space;
        this.operationsCompleted = 0;
    }

    execute(operation, vectors, coefficients = []) {
        try {
            const result = this.space.linearCombination(
                vectors,
                coefficients
            );

            this.operationsCompleted++;

            const event = Object.freeze({
                operation,
                result,
                sequence: this.operationsCompleted
            });

            this.emit("computed", event);

            return result;
        } catch (error) {
            this.emit("operationFailed", {
                operation,
                message: error.message
            });

            throw error;
        }
    }

    async processBatch(jobs) {
        if (!Array.isArray(jobs)) {
            throw new ValidationError("Jobs must be an array.");
        }

        // Preserve job order while isolating individual failures.
        return Promise.all(
            jobs.map(async (job, index) => {
                await Promise.resolve();

                try {
                    const result = this.execute(
                        `batch-${index + 1}`,
                        job.vectors,
                        job.coefficients
                    );

                    return {
                        success: true,
                        index,
                        result: result.toJSON()
                    };
                } catch (error) {
                    return {
                        success: false,
                        index,
                        error: error.message
                    };
                }
            })
        );
    }
}

async function main() {
    console.log("LINEAR ALGEBRA FOUNDATIONS");
    console.log("=".repeat(55));

    // Scalars
    const alpha = new Scalar(3);
    const beta = new Scalar(2);

    console.log("\n1. SCALARS");
    console.log("alpha + beta =", alpha.add(beta).value);
    console.log("alpha * beta =", alpha.multiply(beta).value);

    // Vector notation
    const u = new Vector([2, 3]);
    const v = new Vector([4, 1]);

    console.log("\n2. VECTORS");
    console.log("u =", u.toString());
    console.log("v =", v.toString());
    console.log("Dimension =", u.dimension);
    console.log("u + v =", u.add(v).toString());
    console.log("u - v =", u.subtract(v).toString());

    // Scalar multiplication
    console.log("\n3. SCALAR MULTIPLICATION");
    console.log("3u =", u.scale(3).toString());
    console.log("(-2)u =", u.scale(-2).toString());

    // Inner product
    console.log("\n4. INNER PRODUCT");
    console.log("u . v =", u.dot(v));
    console.log("||u|| =", u.norm());
    console.log("Unit vector =", u.normalize().toString());

    // Vector-space behavior
    const space = new VectorSpace(2);

    console.log("\n5. VECTOR SPACE R^2");
    console.log("Zero =", space.zero().toString());
    console.log(
        "Additive identity =",
        u.add(space.zero()).toString()
    );
    console.log(
        "Scalar closure =",
        space.multiply(5, u).toString()
    );

    // Linear combination
    console.log("\n6. LINEAR COMBINATION");
    console.log(
        "2u + 3v =",
        space.linearCombination([u, v], [2, 3]).toString()
    );

    // Basis
    console.log("\n7. LINEAR INDEPENDENCE");

    const e1 = new Vector([1, 0]);
    const e2 = new Vector([0, 1]);

    console.log("Rank =", matrixRank([e1, e2]));
    console.log("Standard basis =", isBasis([e1, e2], space));

    const dependent = [
        new Vector([1, 2]),
        new Vector([2, 4])
    ];

    console.log("Dependent rank =", matrixRank(dependent));

    // Event-driven execution
    console.log("\n8. EVENT-DRIVEN WORKSPACE");

    const workspace = new VectorWorkspace(space);

    workspace.on("computed", event => {
        console.log(
            `Computed operation ${event.sequence}:`,
            event.result.toString()
        );
    });

    workspace.on("operationFailed", event => {
        console.error("Failed:", event.message);
    });

    workspace.execute("linear-combination", [u, v], [2, 3]);

    // Asynchronous batch processing
    console.log("\n9. ASYNCHRONOUS BATCH PROCESSING");

    const results = await workspace.processBatch([
        {
            vectors: [u, v],
            coefficients: [1, 1]
        },
        {
            vectors: [e1, e2],
            coefficients: [5, 7]
        },
        {
            vectors: [u, new Vector([1, 2, 3])],
            coefficients: [1, 2]
        }
    ]);

    for (const result of results) {
        console.log(result);
    }

    // Assertions
    console.log("\n10. VALIDATION");

    assert.equal(u.dot(v), 11);
    assert.equal(matrixRank([e1, e2]), 2);
    assert.equal(matrixRank(dependent), 1);
    assert.ok(isBasis([e1, e2], space));
    assert.ok(u.add(space.zero()).equals(u));

    assert.throws(
        () => new Vector([Infinity]),
        ValidationError
    );

    assert.throws(
        () => u.add(new Vector([1, 2, 3])),
        DimensionError
    );

    assert.throws(
        () => space.zero().normalize(),
        LinearAlgebraError
    );

    console.log("All assertions passed.");
    console.log(
        "Successful workspace operations:",
        workspace.operationsCompleted
    );
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
