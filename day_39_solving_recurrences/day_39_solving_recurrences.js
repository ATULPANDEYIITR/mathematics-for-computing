/*
 * Solving Recurrences
 * ====================
 *
 * This file approaches recurrence solving through JavaScript-specific
 * execution patterns:
 *
 * - Iterative recurrence evaluation
 * - Repeated substitution represented as a trace
 * - Closed-form validation
 * - Characteristic equations for second-order recurrences
 * - Review of distinct and repeated characteristic roots
 * - Non-homogeneous recurrence evaluation
 * - Event-driven recurrence evaluation
 * - Memoization and matrix exponentiation
 *
 * The program runs with Node.js and uses no external dependencies.
 */

"use strict";

// ---------------------------------------------------------------------------
// Generic recurrence evaluation
// ---------------------------------------------------------------------------

function evaluateRecurrence(baseValues, recurrence, targetN) {
    if (!Number.isInteger(targetN) || targetN < 0) {
        throw new RangeError("targetN must be a non-negative integer");
    }

    if (!Array.isArray(baseValues) || baseValues.length === 0) {
        throw new TypeError("baseValues must contain at least one value");
    }

    const values = [...baseValues];

    if (targetN < values.length) {
        return values[targetN];
    }

    for (let n = values.length; n <= targetN; n += 1) {
        values.push(recurrence(n, values));
    }

    return values[targetN];
}


// ---------------------------------------------------------------------------
// Iteration and repeated substitution
//
// T(n) = T(n - 1) + n
//
// Iterating exposes the accumulated sum:
//
// T(n) = T(0) + 1 + 2 + ... + n
// ---------------------------------------------------------------------------

function triangularRecurrence(n, values) {
    return values[n - 1] + n;
}

function triangularClosedForm(n, initial = 0) {
    return initial + (n * (n + 1)) / 2;
}

function buildSequence(baseValue, count, recurrence) {
    if (!Number.isInteger(count) || count < 1) {
        throw new RangeError("count must be a positive integer");
    }

    const values = [baseValue];

    for (let n = 1; n < count; n += 1) {
        values.push(recurrence(n, values));
    }

    return values;
}


// ---------------------------------------------------------------------------
// Explicit substitution trace
//
// This is useful when learning how repeated expansion exposes a pattern.
// ---------------------------------------------------------------------------

function substitutionTrace(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    const trace = [];

    for (let level = 0; level <= n; level += 1) {
        const remaining = n - level;

        if (remaining === 0) {
            trace.push("T(0)");
        } else {
            trace.push(`T(${remaining}) + ${level} accumulated terms`);
        }
    }

    return trace;
}


// ---------------------------------------------------------------------------
// First-order recurrence
//
// T(n) = aT(n-1) + b
//
// For a != 1:
// T(n) = a^n*T(0) + b(a^n-1)/(a-1)
//
// For a = 1:
// T(n) = T(0) + bn
// ---------------------------------------------------------------------------

function firstOrderClosedForm(n, a, b, initial) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (a === 1) {
        return initial + b * n;
    }

    return initial * a ** n + b * (a ** n - 1) / (a - 1);
}

function verifyFirstOrder(n, a, b, initial) {
    const values = buildSequence(
        initial,
        n + 1,
        (index, previous) => a * previous[index - 1] + b
    );

    return values.every(
        (value, index) =>
            Math.abs(value - firstOrderClosedForm(index, a, b, initial)) < 1e-9
    );
}


// ---------------------------------------------------------------------------
// Characteristic equation support
//
// For:
//
// T(n) = pT(n-1) + qT(n-2)
//
// the characteristic polynomial is:
//
// r^2 - pr - q = 0
//
// JavaScript's complex-number support is not built into Number, so this
// demonstration handles real roots directly and reports complex roots
// separately when needed.
// ---------------------------------------------------------------------------

function characteristicRoots(p, q) {
    const discriminant = p * p + 4 * q;

    if (discriminant >= 0) {
        const root = Math.sqrt(discriminant);

        return {
            type: "real",
            roots: [
                (p + root) / 2,
                (p - root) / 2
            ]
        };
    }

    const imaginary = Math.sqrt(-discriminant) / 2;

    return {
        type: "complex",
        roots: [
            { real: p / 2, imaginary },
            { real: p / 2, imaginary: -imaginary }
        ]
    };
}


// ---------------------------------------------------------------------------
// Distinct characteristic roots
//
// T(n) = C1*r1^n + C2*r2^n
//
// C1 and C2 come from T(0) and T(1).
// ---------------------------------------------------------------------------

function distinctRootCoefficients(r1, r2, initial0, initial1) {
    if (r1 === r2) {
        throw new Error("The roots must be distinct.");
    }

    const c1 = (initial1 - initial0 * r2) / (r1 - r2);
    const c2 = initial0 - c1;

    return { c1, c2 };
}

function distinctRootSolution(n, r1, r2, initial0, initial1) {
    const { c1, c2 } = distinctRootCoefficients(
        r1,
        r2,
        initial0,
        initial1
    );

    return c1 * r1 ** n + c2 * r2 ** n;
}


// ---------------------------------------------------------------------------
// Repeated root
//
// If:
//
// (r - lambda)^2 = 0
//
// then:
//
// T(n) = (C1 + C2*n)lambda^n
//
// The n multiplier distinguishes the repeated-root solution from the
// distinct-root case.
// ---------------------------------------------------------------------------

function repeatedRootSolution(n, root, initial0, initial1) {
    if (root === 0) {
        if (n === 0) return initial0;
        if (n === 1) return initial1;
        return 0;
    }

    const c1 = initial0;
    const c2 = initial1 / root - c1;

    return (c1 + c2 * n) * root ** n;
}


// ---------------------------------------------------------------------------
// Non-homogeneous recurrence
//
// T(n) = aT(n-1) + f
//
// For constant f and a != 1:
//
// particular solution = f/(1-a)
//
// total solution = homogeneous + particular
// ---------------------------------------------------------------------------

function nonHomogeneousClosedForm(n, a, forcing, initial) {
    if (a === 1) {
        return initial + forcing * n;
    }

    const particular = forcing / (1 - a);
    const homogeneousConstant = initial - particular;

    return homogeneousConstant * a ** n + particular;
}

function buildNonHomogeneousSequence(n, a, forcing, initial) {
    return buildSequence(
        initial,
        n + 1,
        (index, values) => a * values[index - 1] + forcing
    );
}


// ---------------------------------------------------------------------------
// Memoized Fibonacci
//
// The recursive definition itself creates overlapping subproblems.
// Memoization stores already-computed states so each n is evaluated once.
// ---------------------------------------------------------------------------

function memoizedFibonacci(n, cache = new Map([[0, 0], [1, 1]])) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (cache.has(n)) {
        return cache.get(n);
    }

    const value =
        memoizedFibonacci(n - 1, cache) +
        memoizedFibonacci(n - 2, cache);

    cache.set(n, value);
    return value;
}


// ---------------------------------------------------------------------------
// BigInt Fibonacci
//
// Number loses integer precision beyond 2^53 - 1. BigInt avoids that issue
// for exact recurrence values.
// ---------------------------------------------------------------------------

function fibonacciBigInt(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let previous = 0n;
    let current = 1n;

    for (let i = 0; i < n; i += 1) {
        [previous, current] = [current, previous + current];
    }

    return previous;
}


// ---------------------------------------------------------------------------
// Matrix multiplication and exponentiation
//
// [F(n+1)]   [1 1]^n [1]
// [F(n)  ] = [1 0]   [0]
//
// Binary exponentiation reduces matrix-power operations to O(log n).
// BigInt keeps the resulting Fibonacci value exact.
// ---------------------------------------------------------------------------

function multiplyMatrices(a, b) {
    return [
        [
            a[0][0] * b[0][0] + a[0][1] * b[1][0],
            a[0][0] * b[0][1] + a[0][1] * b[1][1]
        ],
        [
            a[1][0] * b[0][0] + a[1][1] * b[1][0],
            a[1][0] * b[0][1] + a[1][1] * b[1][1]
        ]
    ];
}

function matrixPower(matrix, exponent) {
    let result = [
        [1n, 0n],
        [0n, 1n]
    ];

    let base = matrix;
    let power = exponent;

    while (power > 0) {
        if (power % 2 === 1) {
            result = multiplyMatrices(result, base);
        }

        base = multiplyMatrices(base, base);
        power = Math.floor(power / 2);
    }

    return result;
}

function fibonacciLogarithmic(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n === 0) {
        return 0n;
    }

    const matrix = matrixPower(
        [
            [1n, 1n],
            [1n, 0n]
        ],
        n
    );

    return matrix[0][1];
}


// ---------------------------------------------------------------------------
// Event-driven recurrence evaluator
//
// EventEmitter is useful when recurrence computation feeds other components,
// such as logging, monitoring, visualization, or a pipeline.
// ---------------------------------------------------------------------------

class RecurrenceEmitter {
    constructor(initialValue, transition) {
        if (typeof transition !== "function") {
            throw new TypeError("transition must be a function");
        }

        this.values = [initialValue];
        this.transition = transition;
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("listener must be a function");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }

    run(targetN) {
        if (!Number.isInteger(targetN) || targetN < 0) {
            throw new RangeError("targetN must be non-negative");
        }

        while (this.values.length <= targetN) {
            const n = this.values.length;
            const next = this.transition(n, this.values);

            if (!Number.isFinite(next)) {
                throw new Error(`Non-finite recurrence value at n=${n}`);
            }

            this.values.push(next);

            this.emit("computed", {
                n,
                value: next
            });
        }

        this.emit("complete", {
            targetN,
            value: this.values[targetN]
        });

        return this.values[targetN];
    }
}


// ---------------------------------------------------------------------------
// Validation utilities
// ---------------------------------------------------------------------------

function assertAlmostEqual(actual, expected, message) {
    if (Math.abs(actual - expected) > 1e-9) {
        throw new Error(
            `${message}: expected ${expected}, received ${actual}`
        );
    }
}

function validateSecondOrder(values, p, q) {
    const errors = [];

    for (let n = 2; n < values.length; n += 1) {
        const expected = p * values[n - 1] + q * values[n - 2];

        if (values[n] !== expected) {
            errors.push({
                n,
                actual: values[n],
                expected
            });
        }
    }

    return {
        valid: errors.length === 0,
        errors
    };
}


// ---------------------------------------------------------------------------
// Main demonstration
// ---------------------------------------------------------------------------

function main() {
    console.log("SOLVING RECURRENCES");
    console.log("===================");

    console.log("\nIteration and substitution");
    console.log("--------------------------");

    const triangularValues = buildSequence(
        0,
        9,
        triangularRecurrence
    );

    triangularValues.forEach((value, n) => {
        assertAlmostEqual(
            value,
            triangularClosedForm(n),
            `Triangular recurrence failed at n=${n}`
        );
    });

    console.table(
        triangularValues.map((value, n) => ({
            n,
            recurrence: value,
            closedForm: triangularClosedForm(n)
        }))
    );

    console.log("\nSubstitution trace");
    substitutionTrace(5).forEach((line, index) => {
        console.log(`Expansion ${index}: ${line}`);
    });

    console.log("\nFirst-order recurrence");
    console.log("----------------------");

    const firstOrderParameters = {
        a: 2,
        b: 3,
        initial: 5
    };

    const firstOrderValues = buildSequence(
        firstOrderParameters.initial,
        8,
        (n, values) =>
            firstOrderParameters.a * values[n - 1] +
            firstOrderParameters.b
    );

    console.log(firstOrderValues);

    for (let n = 0; n < firstOrderValues.length; n += 1) {
        assertAlmostEqual(
            firstOrderValues[n],
            firstOrderClosedForm(
                n,
                firstOrderParameters.a,
                firstOrderParameters.b,
                firstOrderParameters.initial
            ),
            `First-order formula failed at n=${n}`
        );
    }

    console.log(
        "Closed form verified:",
        verifyFirstOrder(
            12,
            firstOrderParameters.a,
            firstOrderParameters.b,
            firstOrderParameters.initial
        )
    );

    console.log("\nCharacteristic equation");
    console.log("-----------------------");

    const fibonacciRoots = characteristicRoots(1, 1);
    console.log("For T(n)=T(n-1)+T(n-2):", fibonacciRoots);

    const recurrenceValues = buildSequence(
        1,
        10,
        (n, values) => values[n - 1] + values[n - 2]
    );

    const validation = validateSecondOrder(recurrenceValues, 1, 1);
    console.log("Fibonacci recurrence valid:", validation.valid);

    const distinctRoots = distinctRootCoefficients(2, 3, 1, 4);
    console.log(
        "For roots 2 and 3, coefficients:",
        distinctRoots
    );

    for (let n = 0; n < recurrenceValues.length; n += 1) {
        const value = distinctRootSolution(
            n,
            2,
            3,
            1,
            4
        );

        if (n < 2) {
            continue;
        }

        const expected = 5 * recurrenceValues[n - 1] -
            6 * recurrenceValues[n - 2];

        assertAlmostEqual(
            value,
            expected,
            `Distinct-root solution failed at n=${n}`
        );
    }

    console.log("\nRepeated characteristic root");
    console.log("----------------------------");

    const repeatedValues = buildSequence(
        2,
        9,
        (n, values) => {
            if (n === 1) {
                return 8;
            }
            return 4 * values[n - 1] - 4 * values[n - 2];
        }
    );

    console.log(repeatedValues);

    repeatedValues.forEach((value, n) => {
        assertAlmostEqual(
            value,
            repeatedRootSolution(n, 2, 2, 8),
            `Repeated-root solution failed at n=${n}`
        );
    });

    console.log("\nNon-homogeneous recurrence");
    console.log("--------------------------");

    const nonHomogeneous = buildNonHomogeneousSequence(
        10,
        3,
        4,
        2
    );

    console.log(nonHomogeneous);

    nonHomogeneous.forEach((value, n) => {
        assertAlmostEqual(
            value,
            nonHomogeneousClosedForm(n, 3, 4, 2),
            `Non-homogeneous formula failed at n=${n}`
        );
    });

    console.log("\nMemoization and exact arithmetic");
    console.log("--------------------------------");

    console.log("Fibonacci F(40):", memoizedFibonacci(40));
    console.log("Fibonacci F(100) using BigInt:", fibonacciBigInt(100));

    console.log("\nLogarithmic matrix exponentiation");
    console.log("---------------------------------");

    const matrixResult = fibonacciLogarithmic(100);
    console.log("Fibonacci F(100):", matrixResult.toString());

    if (matrixResult !== fibonacciBigInt(100)) {
        throw new Error("Matrix and iterative Fibonacci results differ.");
    }

    console.log("Exact matrix result verified.");

    console.log("\nEvent-driven recurrence evaluation");
    console.log("----------------------------------");

    const emitter = new RecurrenceEmitter(
        1,
        (n, values) => values[n - 1] + n
    );

    emitter.on("computed", ({ n, value }) => {
        console.log(`Computed T(${n}) = ${value}`);
    });

    emitter.on("complete", ({ targetN, value }) => {
        console.log(`Completed through T(${targetN}) = ${value}`);
    });

    emitter.run(5);

    console.log("\nAll recurrence demonstrations completed successfully.");
}

main();
