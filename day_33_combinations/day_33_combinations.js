"use strict";

/*
 * Combinations: binomial coefficients, combinations, and Pascal's triangle.
 *
 * This Node.js program uses JavaScript-specific features such as BigInt,
 * generators, iterators, Sets, Maps, event-driven processing, and asynchronous
 * workflow simulation to model combinatorial computation.
 *
 * Run with:
 *   node combinations.js
 *
 * BigInt is required because ordinary JavaScript Number values cannot represent
 * every large integer exactly.
 */

// ---------------------------------------------------------------------------
// Validation and exact arithmetic
// ---------------------------------------------------------------------------

function validateNK(n, k) {
    if (!Number.isSafeInteger(n) || !Number.isSafeInteger(k)) {
        throw new TypeError("n and k must be safe integers");
    }

    if (n < 0) {
        throw new RangeError("n must be non-negative");
    }

    if (k < 0 || k > n) {
        throw new RangeError("k must satisfy 0 <= k <= n");
    }
}

function factorialBigInt(n) {
    if (!Number.isSafeInteger(n) || n < 0) {
        throw new RangeError("factorial requires a non-negative safe integer");
    }

    let result = 1n;

    for (let value = 2; value <= n; value++) {
        result *= BigInt(value);
    }

    return result;
}

function combinationFactorial(n, k) {
    validateNK(n, k);

    const numerator = factorialBigInt(n);
    const denominator = factorialBigInt(k) * factorialBigInt(n - k);

    return numerator / denominator;
}

function combinationMultiplicative(n, k) {
    validateNK(n, k);

    k = Math.min(k, n - k);

    let result = 1n;

    for (let i = 1; i <= k; i++) {
        result = result * BigInt(n - k + i) / BigInt(i);
    }

    return result;
}

// ---------------------------------------------------------------------------
// Pascal's triangle
// ---------------------------------------------------------------------------

function pascalRow(n) {
    if (!Number.isSafeInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative safe integer");
    }

    const row = [1n];

    for (let k = 1; k <= n; k++) {
        row.push(row[row.length - 1] * BigInt(n - k + 1) / BigInt(k));
    }

    return row;
}

function buildPascalTriangle(rowCount) {
    if (!Number.isSafeInteger(rowCount) || rowCount < 0) {
        throw new RangeError("rowCount must be non-negative");
    }

    const triangle = [];

    for (let rowIndex = 0; rowIndex < rowCount; rowIndex++) {
        if (rowIndex === 0) {
            triangle.push([1n]);
            continue;
        }

        const previous = triangle[rowIndex - 1];
        const current = [1n];

        for (let i = 0; i < previous.length - 1; i++) {
            current.push(previous[i] + previous[i + 1]);
        }

        current.push(1n);
        triangle.push(current);
    }

    return triangle;
}

function displayPascalTriangle(rowCount) {
    const triangle = buildPascalTriangle(rowCount);

    if (triangle.length === 0) {
        return;
    }

    const lastRow = triangle[triangle.length - 1]
        .map(value => value.toString())
        .join(" ");

    const width = lastRow.length;

    for (const row of triangle) {
        const text = row.map(value => value.toString()).join(" ");
        console.log(text.padStart(Math.floor((width + text.length) / 2)));
    }
}

// ---------------------------------------------------------------------------
// Generator-based combination enumeration
// ---------------------------------------------------------------------------

function* combinations(values, k) {
    if (!Number.isInteger(k) || k < 0 || k > values.length) {
        throw new RangeError("k must satisfy 0 <= k <= values.length");
    }

    const selected = [];

    function* search(start) {
        if (selected.length === k) {
            yield [...selected];
            return;
        }

        const needed = k - selected.length;
        const lastStart = values.length - needed;

        for (let index = start; index <= lastStart; index++) {
            selected.push(values[index]);

            yield* search(index + 1);

            selected.pop();
        }
    }

    yield* search(0);
}

function collectCombinationStatistics(values, k) {
    let count = 0;
    let longest = "";

    for (const selection of combinations(values, k)) {
        count++;

        const representation = selection.join(" + ");

        if (representation.length > longest.length) {
            longest = representation;
        }
    }

    return { count, longest };
}

// ---------------------------------------------------------------------------
// Review of duplicate input semantics
// ---------------------------------------------------------------------------

function uniqueCombinations(values, k) {
    /*
     * A normal positional combination treats duplicate values at different
     * positions as distinct choices. This function instead treats equal values
     * as the same value, which is useful when the input represents a multiset
     * and duplicate outputs are undesirable.
     */
    const uniqueValues = [...new Set(values)].sort();

    return combinations(uniqueValues, k);
}

// ---------------------------------------------------------------------------
// Event-driven coefficient processing
// ---------------------------------------------------------------------------

class CombinationEngine {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, handler) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(handler);

        return () => {
            this.listeners.get(eventName)?.delete(handler);
        };
    }

    emit(eventName, payload) {
        const handlers = this.listeners.get(eventName) ?? [];

        for (const handler of handlers) {
            handler(payload);
        }
    }

    calculate(n, k) {
        this.emit("calculationStarted", { n, k });

        try {
            const value = combinationMultiplicative(n, k);

            this.emit("calculationCompleted", {
                n,
                k,
                value
            });

            return value;
        } catch (error) {
            this.emit("calculationFailed", {
                n,
                k,
                error
            });

            throw error;
        }
    }
}

// ---------------------------------------------------------------------------
// Memoized recursive computation
// ---------------------------------------------------------------------------

function memoizedCombination(n, k, memo = new Map()) {
    validateNK(n, k);

    k = Math.min(k, n - k);

    if (k === 0) {
        return 1n;
    }

    const key = `${n},${k}`;

    if (memo.has(key)) {
        return memo.get(key);
    }

    const value =
        memoizedCombination(n - 1, k - 1, memo) +
        memoizedCombination(n - 1, k, memo);

    memo.set(key, value);

    return value;
}

// ---------------------------------------------------------------------------
// Binomial theorem
// ---------------------------------------------------------------------------

function evaluateBinomialExpansion(a, b, n) {
    if (!Number.isSafeInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative safe integer");
    }

    let total = 0n;
    const bigA = BigInt(a);
    const bigB = BigInt(b);

    for (let k = 0; k <= n; k++) {
        const coefficient = combinationMultiplicative(n, k);

        total +=
            coefficient *
            bigA ** BigInt(n - k) *
            bigB ** BigInt(k);
    }

    return total;
}

// ---------------------------------------------------------------------------
// Exact hypergeometric probability
// ---------------------------------------------------------------------------

function gcdBigInt(a, b) {
    a = a < 0n ? -a : a;
    b = b < 0n ? -b : b;

    while (b !== 0n) {
        const remainder = a % b;
        a = b;
        b = remainder;
    }

    return a;
}

function reduceFraction(numerator, denominator) {
    const divisor = gcdBigInt(numerator, denominator);

    return {
        numerator: numerator / divisor,
        denominator: denominator / divisor
    };
}

function hypergeometricProbability(
    populationSize,
    successCount,
    draws,
    desiredSuccesses
) {
    if (
        !Number.isSafeInteger(populationSize) ||
        !Number.isSafeInteger(successCount) ||
        !Number.isSafeInteger(draws) ||
        !Number.isSafeInteger(desiredSuccesses)
    ) {
        throw new TypeError("all probability parameters must be safe integers");
    }

    if (populationSize < 0) {
        throw new RangeError("populationSize must be non-negative");
    }

    if (successCount < 0 || successCount > populationSize) {
        throw new RangeError("successCount must be within the population");
    }

    if (draws < 0 || draws > populationSize) {
        throw new RangeError("draws must be within the population");
    }

    const failures = populationSize - successCount;
    const remainingDraws = draws - desiredSuccesses;

    if (
        desiredSuccesses < 0 ||
        desiredSuccesses > successCount ||
        remainingDraws < 0 ||
        remainingDraws > failures
    ) {
        return { numerator: 0n, denominator: 1n };
    }

    const numerator =
        combinationMultiplicative(successCount, desiredSuccesses) *
        combinationMultiplicative(failures, remainingDraws);

    const denominator = combinationMultiplicative(populationSize, draws);

    return reduceFraction(numerator, denominator);
}

// ---------------------------------------------------------------------------
// Identity verification
// ---------------------------------------------------------------------------

function verifyIdentities(limit) {
    const failures = [];

    for (let n = 0; n <= limit; n++) {
        for (let k = 0; k <= n; k++) {
            const coefficient = combinationMultiplicative(n, k);

            if (coefficient !== combinationMultiplicative(n, n - k)) {
                failures.push(`symmetry failed at ${n},${k}`);
            }

            if (n > 0 && k > 0 && k < n) {
                const pascalValue =
                    combinationMultiplicative(n - 1, k - 1) +
                    combinationMultiplicative(n - 1, k);

                if (coefficient !== pascalValue) {
                    failures.push(`Pascal identity failed at ${n},${k}`);
                }
            }
        }

        const rowSum = pascalRow(n).reduce(
            (sum, coefficient) => sum + coefficient,
            0n
        );

        if (rowSum !== 2n ** BigInt(n)) {
            failures.push(`row-sum identity failed at ${n}`);
        }
    }

    return failures;
}

// ---------------------------------------------------------------------------
// Asynchronous audit workflow
// ---------------------------------------------------------------------------

async function auditCombinationRequests(requests) {
    const engine = new CombinationEngine();

    engine.on("calculationStarted", ({ n, k }) => {
        console.log(`  starting C(${n}, ${k})`);
    });

    engine.on("calculationCompleted", ({ n, k, value }) => {
        console.log(`  completed C(${n}, ${k}) = ${value}`);
    });

    engine.on("calculationFailed", ({ n, k, error }) => {
        console.log(`  rejected C(${n}, ${k}): ${error.message}`);
    });

    /*
     * The timeout represents an asynchronous service boundary. The arithmetic
     * remains synchronous and exact, while request handling is event-driven.
     */
    const results = [];

    for (const request of requests) {
        await new Promise(resolve => setTimeout(resolve, 5));

        try {
            results.push({
                ...request,
                value: engine.calculate(request.n, request.k)
            });
        } catch (error) {
            results.push({
                ...request,
                error: error.message
            });
        }
    }

    return results;
}

// ---------------------------------------------------------------------------
// Main demonstration
// ---------------------------------------------------------------------------

async function main() {
    console.log("COMBINATIONS AND BINOMIAL COEFFICIENTS");
    console.log("=====================================\n");

    console.log("=== Exact binomial coefficients ===");

    for (const [n, k] of [[5, 2], [10, 3], [20, 10], [52, 5]]) {
        const factorialValue = combinationFactorial(n, k);
        const multiplicativeValue = combinationMultiplicative(n, k);

        console.log(
            `C(${n}, ${k}) = ${multiplicativeValue} ` +
            `(methods agree: ${factorialValue === multiplicativeValue})`
        );
    }

    console.log("\n=== Pascal's triangle ===");
    displayPascalTriangle(9);

    console.log("\n=== Generator-based combination enumeration ===");

    const technologies = ["Python", "JavaScript", "C++", "SQL", "Rust"];
    const statistics = collectCombinationStatistics(technologies, 3);

    console.log(`Generated combinations: ${statistics.count}`);
    console.log(`Longest textual representation: ${statistics.longest}`);

    console.log("\n=== Unique-value combination behavior ===");

    const duplicateInput = ["API", "API", "Database", "Cache"];
    console.log(
        [...uniqueCombinations(duplicateInput, 2)]
            .map(selection => selection.join(" + "))
            .join("\n")
    );

    console.log("\n=== Binomial theorem ===");

    const direct = (2n + 3n) ** 5n;
    const expanded = evaluateBinomialExpansion(2, 3, 5);

    console.log(`(2 + 3)^5 = ${direct}`);
    console.log(`Expansion result = ${expanded}`);

    console.log("\n=== Hypergeometric probability ===");

    const probability = hypergeometricProbability(20, 5, 4, 2);

    console.log(
        `P(X=2) = ${probability.numerator}/${probability.denominator}`
    );

    console.log(
        `Decimal approximation = ${
            Number(probability.numerator) / Number(probability.denominator)
        }`
    );

    console.log("\n=== Memoized computation ===");
    console.log(`C(30, 15) = ${memoizedCombination(30, 15)}`);

    console.log("\n=== Identity verification ===");

    const identityFailures = verifyIdentities(30);

    if (identityFailures.length === 0) {
        console.log("Symmetry, Pascal recurrence, and row-sum identities: PASS");
    } else {
        console.log("Identity failures:");
        console.log(identityFailures.join("\n"));
    }

    console.log("\n=== Event-driven asynchronous audit ===");

    await auditCombinationRequests([
        { n: 12, k: 4 },
        { n: 25, k: 12 },
        { n: 10, k: 11 }
    ]);

    console.log("\n=== Edge cases ===");

    for (const [n, k] of [[0, 0], [10, 0], [10, 10], [10, 1], [10, 9]]) {
        console.log(`C(${n}, ${k}) = ${combinationMultiplicative(n, k)}`);
    }

    console.log("\n=== Invalid input ===");

    try {
        combinationMultiplicative(5, 8);
    } catch (error) {
        console.log(`Invalid coefficient rejected: ${error.message}`);
    }

    console.log("\n=== Computational considerations ===");
    console.log(
        "BigInt preserves exact integer coefficients beyond Number's safe-integer range."
    );
    console.log(
        "The multiplicative method performs O(min(k, n-k)) arithmetic iterations."
    );
    console.log(
        "Generating every combination is output-sensitive because each result must be materialized or consumed."
    );
    console.log(
        "For security-sensitive systems, validate bounds before accepting requests that could force enormous computations."
    );
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
