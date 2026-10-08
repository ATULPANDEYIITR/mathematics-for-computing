"use strict";

/*
 * Recurrence Relations Laboratory
 *
 * This Node.js-compatible program models linear recurrences and focuses on
 * distinctions between homogeneous and non-homogeneous forms.
 *
 * Run with:
 *   node recurrence_relations.js
 */

// -----------------------------------------------------------------------------
// Basic recurrence engine
// -----------------------------------------------------------------------------

class LinearRecurrence {
    constructor(coefficients, initialTerms, forcing = () => 0) {
        if (!Array.isArray(coefficients) || coefficients.length === 0) {
            throw new Error("A recurrence needs at least one coefficient.");
        }

        if (coefficients.length !== initialTerms.length) {
            throw new Error(
                "The number of initial terms must equal the recurrence order."
            );
        }

        if (!coefficients.every(Number.isFinite)) {
            throw new Error("All recurrence coefficients must be finite numbers.");
        }

        this.coefficients = [...coefficients];
        this.initialTerms = [...initialTerms];
        this.forcing = forcing;
    }

    get order() {
        return this.coefficients.length;
    }

    isHomogeneous(sampleSize = 12) {
        return Array.from(
            { length: sampleSize },
            (_, n) => this.forcing(n)
        ).every(value => value === 0);
    }

    nextTerm(history, n) {
        if (history.length < this.order) {
            throw new Error("Insufficient history for this recurrence.");
        }

        let value = 0;

        for (let i = 0; i < this.order; i++) {
            value += this.coefficients[i] *
                history[history.length - i - 1];
        }

        return value + this.forcing(n);
    }

    generate(count) {
        if (!Number.isInteger(count) || count < 0) {
            throw new Error("count must be a non-negative integer.");
        }

        const terms = this.initialTerms.slice(0, count);

        while (terms.length < count) {
            terms.push(this.nextTerm(terms, terms.length));
        }

        return terms;
    }
}

// -----------------------------------------------------------------------------
// Fundamental examples
// -----------------------------------------------------------------------------

function demonstrateLinearRecurrence() {
    printTitle("Linear recurrence");

    const recurrence = new LinearRecurrence(
        [1],
        [2],
        () => 3
    );

    console.log("a_n = a_(n-1) + 3");
    console.log(recurrence.generate(10));
}

function demonstrateFibonacci() {
    printTitle("Homogeneous recurrence");

    const fibonacci = new LinearRecurrence(
        [1, 1],
        [0, 1]
    );

    console.log("F_n = F_(n-1) + F_(n-2)");
    console.log(fibonacci.generate(15));
}

function demonstrateNonHomogeneous() {
    printTitle("Non-homogeneous recurrence");

    const recurrence = new LinearRecurrence(
        [2],
        [1],
        n => n
    );

    console.log("a_n = 2a_(n-1) + n");
    console.log(recurrence.generate(10));
}

// -----------------------------------------------------------------------------
// Event-driven recurrence processing
// -----------------------------------------------------------------------------

class RecurrenceMonitor {
    constructor(recurrence) {
        this.recurrence = recurrence;
        this.listeners = new Map();
    }

    on(eventName, handler) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(handler);
    }

    emit(eventName, payload) {
        const handlers = this.listeners.get(eventName) || [];

        for (const handler of handlers) {
            handler(payload);
        }
    }

    run(count) {
        const terms = this.recurrence.initialTerms.slice(0, count);

        this.emit("started", {
            count,
            order: this.recurrence.order
        });

        while (terms.length < count) {
            const n = terms.length;
            const value = this.recurrence.nextTerm(terms, n);

            if (!Number.isFinite(value)) {
                this.emit("failure", {
                    index: n,
                    reason: "Non-finite recurrence result"
                });
                throw new Error(`Recurrence failed at n=${n}.`);
            }

            terms.push(value);

            this.emit("term", {
                index: n,
                value
            });
        }

        this.emit("completed", {
            count: terms.length,
            lastValue: terms.at(-1)
        });

        return terms;
    }
}

function demonstrateEventDrivenProcessing() {
    printTitle("Event-driven recurrence processing");

    const recurrence = new LinearRecurrence(
        [1, 1],
        [0, 1]
    );

    const monitor = new RecurrenceMonitor(recurrence);

    monitor.on("started", event => {
        console.log(
            `Started order-${event.order} recurrence for ${event.count} terms.`
        );
    });

    monitor.on("term", event => {
        if (event.index < 8) {
            console.log(`a_${event.index} = ${event.value}`);
        }
    });

    monitor.on("completed", event => {
        console.log(
            `Completed with last value ${event.lastValue}.`
        );
    });

    monitor.run(12);
}

// -----------------------------------------------------------------------------
// Memoized recurrence evaluator
// -----------------------------------------------------------------------------

function memoizedFibonacci() {
    const cache = new Map([
        [0, 0],
        [1, 1]
    ]);

    function fibonacci(n) {
        if (!Number.isInteger(n) || n < 0) {
            throw new Error("n must be a non-negative integer.");
        }

        if (cache.has(n)) {
            return cache.get(n);
        }

        const value = fibonacci(n - 1) + fibonacci(n - 2);
        cache.set(n, value);
        return value;
    }

    return fibonacci;
}

function demonstrateMemoization() {
    printTitle("Memoized evaluation");

    const fibonacci = memoizedFibonacci();

    console.log("F_10 =", fibonacci(10));
    console.log("F_50 =", fibonacci(50));

    /*
     * JavaScript Number values are IEEE-754 floating-point numbers. Exact
     * integer recurrence calculations eventually exceed Number's safe integer
     * range, so BigInt is appropriate when exact large terms are required.
     */
}

// -----------------------------------------------------------------------------
// BigInt recurrence implementation
// -----------------------------------------------------------------------------

function bigIntRecurrence(coefficients, initialTerms, forcing = () => 0n, count) {
    if (coefficients.length !== initialTerms.length) {
        throw new Error("Order and initial-term count do not match.");
    }

    const terms = initialTerms.map(BigInt);

    while (terms.length < count) {
        let value = 0n;
        const n = terms.length;

        for (let i = 0; i < coefficients.length; i++) {
            value += BigInt(coefficients[i]) *
                terms[terms.length - i - 1];
        }

        value += BigInt(forcing(n));
        terms.push(value);
    }

    return terms;
}

function demonstrateBigInt() {
    printTitle("Exact large recurrence values");

    const terms = bigIntRecurrence(
        [1, 1],
        [0n, 1n],
        () => 0n,
        101
    );

    console.log("F_100 =", terms[100].toString());
}

// -----------------------------------------------------------------------------
// Matrix operations
// -----------------------------------------------------------------------------

function identityMatrix(size) {
    return Array.from(
        { length: size },
        (_, row) =>
            Array.from(
                { length: size },
                (_, column) => row === column ? 1 : 0
            )
    );
}

function multiplyMatrices(a, b) {
    if (a.length === 0 || b.length === 0) {
        throw new Error("Matrices cannot be empty.");
    }

    if (a[0].length !== b.length) {
        throw new Error("Incompatible matrix dimensions.");
    }

    const result = Array.from(
        { length: a.length },
        () => Array(b[0].length).fill(0)
    );

    for (let i = 0; i < a.length; i++) {
        for (let k = 0; k < b.length; k++) {
            if (a[i][k] === 0) {
                continue;
            }

            for (let j = 0; j < b[0].length; j++) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    return result;
}

function powerMatrix(matrix, exponent) {
    if (!Number.isInteger(exponent) || exponent < 0) {
        throw new Error("Exponent must be a non-negative integer.");
    }

    const size = matrix.length;

    if (
        size === 0 ||
        matrix.some(row => row.length !== size)
    ) {
        throw new Error("Matrix must be square.");
    }

    let result = identityMatrix(size);
    let base = matrix.map(row => [...row]);

    while (exponent > 0) {
        if (exponent % 2 === 1) {
            result = multiplyMatrices(result, base);
        }

        base = multiplyMatrices(base, base);
        exponent = Math.floor(exponent / 2);
    }

    return result;
}

function companionMatrix(coefficients) {
    const order = coefficients.length;

    const matrix = Array.from(
        { length: order },
        () => Array(order).fill(0)
    );

    matrix[0] = [...coefficients];

    for (let row = 1; row < order; row++) {
        matrix[row][row - 1] = 1;
    }

    return matrix;
}

function nthHomogeneousTerm(coefficients, initialTerms, n) {
    const order = coefficients.length;

    if (n < 0) {
        throw new Error("n must be non-negative.");
    }

    if (initialTerms.length !== order) {
        throw new Error("Initial terms must match recurrence order.");
    }

    if (n < order) {
        return initialTerms[n];
    }

    const transition = companionMatrix(coefficients);
    const exponent = n - order + 1;
    const transitionPower = powerMatrix(transition, exponent);

    const state = initialTerms
        .slice()
        .reverse()
        .map(value => [value]);

    return multiplyMatrices(transitionPower, state)[0][0];
}

function demonstrateMatrixEvaluation() {
    printTitle("Fast homogeneous recurrence evaluation");

    const coefficients = [1, 1];
    const initialTerms = [0, 1];

    for (const n of [10, 20, 50]) {
        console.log(`F_${n} = ${nthHomogeneousTerm(
            coefficients,
            initialTerms,
            n
        )}`);
    }
}

// -----------------------------------------------------------------------------
// Characteristic equation support for second-order recurrences
// -----------------------------------------------------------------------------

function quadraticCharacteristicRoots(c1, c2) {
    /*
     * For a_n = c1*a_(n-1) + c2*a_(n-2),
     * the characteristic polynomial is
     *
     * r^2 - c1*r - c2 = 0.
     */
    const discriminant = c1 * c1 + 4 * c2;

    if (discriminant < 0) {
        return null;
    }

    const root = Math.sqrt(discriminant);

    return [
        (c1 + root) / 2,
        (c1 - root) / 2
    ];
}

function demonstrateCharacteristicEquation() {
    printTitle("Characteristic equation");

    const c1 = 3;
    const c2 = -2;

    console.log("Recurrence: a_n = 3a_(n-1) - 2a_(n-2)");
    console.log(
        "Characteristic polynomial: r^2 - 3r + 2"
    );
    console.log(
        "Roots:",
        quadraticCharacteristicRoots(c1, c2)
    );
}

// -----------------------------------------------------------------------------
// Sequence validation
// -----------------------------------------------------------------------------

function validateSequence(sequence, coefficients, forcing = () => 0) {
    const mismatches = [];

    for (let n = coefficients.length; n < sequence.length; n++) {
        let expected = forcing(n);

        for (let i = 0; i < coefficients.length; i++) {
            expected += coefficients[i] *
                sequence[n - i - 1];
        }

        if (expected !== sequence[n]) {
            mismatches.push({
                index: n,
                expected,
                actual: sequence[n]
            });
        }
    }

    return mismatches;
}

function demonstrateValidation() {
    printTitle("Sequence validation");

    const fibonacci = [0, 1, 1, 2, 3, 5, 8, 13];

    console.log(
        "Valid Fibonacci sequence:",
        validateSequence(fibonacci, [1, 1])
    );

    const corrupted = [...fibonacci];
    corrupted[5] = 99;

    console.log(
        "Corrupted sequence:",
        validateSequence(corrupted, [1, 1])
    );
}

// -----------------------------------------------------------------------------
// Non-homogeneous practical model
// -----------------------------------------------------------------------------

function simulateDemand({
    initialDemand,
    growthRate,
    seasonalAdjustment,
    periods
}) {
    if (!Number.isFinite(initialDemand) || initialDemand < 0) {
        throw new Error("Initial demand must be non-negative.");
    }

    if (!Number.isFinite(growthRate)) {
        throw new Error("growthRate must be finite.");
    }

    const demand = [initialDemand];

    for (let n = 1; n < periods; n++) {
        const next =
            growthRate * demand.at(-1) +
            seasonalAdjustment(n);

        if (!Number.isFinite(next) || next < 0) {
            throw new Error(
                `Invalid demand value at period ${n}: ${next}`
            );
        }

        demand.push(next);
    }

    return demand;
}

async function demonstrateAsyncForecast() {
    printTitle("Asynchronous recurrence processing");

    /*
     * A real application might obtain external observations between periods.
     * The delay here represents an asynchronous data boundary rather than
     * changing the mathematical recurrence itself.
     */
    const demand = await simulateAsyncDemand();

    console.log("Forecast:", demand);
}

async function simulateAsyncDemand() {
    const demand = [100];

    for (let n = 1; n < 6; n++) {
        await Promise.resolve();

        const seasonalEffect = n % 2 === 0 ? 15 : -5;
        const next = 1.08 * demand.at(-1) + seasonalEffect;

        demand.push(Number(next.toFixed(4)));
    }

    return demand;
}

// -----------------------------------------------------------------------------
// Error handling
// -----------------------------------------------------------------------------

function demonstrateFailureConditions() {
    printTitle("Failure conditions");

    const operations = [
        [
            "empty coefficients",
            () => new LinearRecurrence([], [])
        ],
        [
            "wrong initial-term count",
            () => new LinearRecurrence([1, 1], [1])
        ],
        [
            "negative count",
            () => new LinearRecurrence([1], [1]).generate(-2)
        ],
        [
            "invalid matrix exponent",
            () => powerMatrix([[1]], -1)
        ]
    ];

    for (const [name, operation] of operations) {
        try {
            operation();
        } catch (error) {
            console.log(`${name}: rejected -> ${error.message}`);
        }
    }
}

// -----------------------------------------------------------------------------
// Utility
// -----------------------------------------------------------------------------

function printTitle(title) {
    console.log(`\n${"=".repeat(78)}`);
    console.log(title);
    console.log("=".repeat(78));
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

async function main() {
    printTitle("RECURRENCE RELATIONS LABORATORY");

    demonstrateLinearRecurrence();
    demonstrateFibonacci();
    demonstrateNonHomogeneous();
    demonstrateEventDrivenProcessing();
    demonstrateMemoization();
    demonstrateBigInt();
    demonstrateMatrixEvaluation();
    demonstrateCharacteristicEquation();
    demonstrateValidation();

    printTitle("Practical non-homogeneous demand model");

    console.log(
        simulateDemand({
            initialDemand: 1000,
            growthRate: 1.04,
            seasonalAdjustment: n => n % 3 === 0 ? -40 : 20,
            periods: 10
        })
    );

    await demonstrateAsyncForecast();
    demonstrateFailureConditions();

    printTitle("Completed");
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
