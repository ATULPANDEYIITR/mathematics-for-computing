"use strict";

/*
 * Combinations: binomial coefficients and Pascal's triangle.
 *
 * This implementation emphasizes JavaScript-specific concerns:
 * Number's safe-integer boundary, BigInt for exact large coefficients,
 * event-driven workflow, lazy generation, validation, and practical
 * subset selection.
 *
 * Run with:
 *   node combinations.js
 */

function validateNAndR(n, r) {
    if (!Number.isInteger(n) || !Number.isInteger(r)) {
        throw new TypeError("n and r must be integers");
    }

    if (n < 0) {
        throw new RangeError("n must be non-negative");
    }

    if (r < 0 || r > n) {
        throw new RangeError("r must satisfy 0 <= r <= n");
    }
}

function combinationNumber(n, r) {
    validateNAndR(n, r);

    r = Math.min(r, n - r);
    let result = 1;

    for (let i = 1; i <= r; i += 1) {
        result *= (n - r + i) / i;
    }

    if (!Number.isSafeInteger(result)) {
        throw new RangeError(
            "The result exceeds JavaScript's exact Number integer range; use combinationBigInt()."
        );
    }

    return result;
}

function combinationBigInt(n, r) {
    validateNAndR(n, r);

    r = Math.min(r, n - r);

    let result = 1n;

    for (let i = 1; i <= r; i += 1) {
        result = (result * BigInt(n - r + i)) / BigInt(i);
    }

    return result;
}

function pascalRow(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("row index must be a non-negative integer");
    }

    const row = [1n];

    for (let r = 1; r <= n; r += 1) {
        row.push((row[r - 1] * BigInt(n - r + 1)) / BigInt(r));
    }

    return row;
}

function* pascalTriangle(rows) {
    if (!Number.isInteger(rows) || rows < 0) {
        throw new RangeError("rows must be a non-negative integer");
    }

    let current = [1n];

    for (let rowIndex = 0; rowIndex < rows; rowIndex += 1) {
        yield current;

        const next = new Array(current.length + 1).fill(1n);

        for (let index = 1; index < current.length; index += 1) {
            next[index] = current[index - 1] + current[index];
        }

        current = next;
    }
}

function chooseSubsets(items, size) {
    if (!Array.isArray(items)) {
        throw new TypeError("items must be an array");
    }

    if (!Number.isInteger(size) || size < 0 || size > items.length) {
        throw new RangeError("size must satisfy 0 <= size <= items.length");
    }

    const output = [];
    const current = [];

    function backtrack(start) {
        if (current.length === size) {
            output.push([...current]);
            return;
        }

        const remaining = size - current.length;
        const finalStart = items.length - remaining;

        for (let index = start; index <= finalStart; index += 1) {
            current.push(items[index]);
            backtrack(index + 1);
            current.pop();
        }
    }

    backtrack(0);
    return output;
}

function evaluateReviewCommitteePolicy(availableReviewers, requiredApprovals) {
    /*
     * This is a combinatorial policy calculation, not a GitHub API call.
     * It answers how many distinct reviewer committees of the required
     * size could theoretically be formed from an eligible reviewer pool.
     */
    if (requiredApprovals < 0 || requiredApprovals > availableReviewers) {
        throw new RangeError("Invalid reviewer requirement");
    }

    return combinationBigInt(availableReviewers, requiredApprovals);
}

class CombinationEventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
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
}

class CombinatorialWorkflow {
    constructor() {
        this.events = new CombinationEventBus();
        this.state = {
            calculations: 0,
            generatedSubsets: 0
        };
    }

    calculate(n, r) {
        const value = combinationBigInt(n, r);
        this.state.calculations += 1;

        this.events.emit("calculated", {
            n,
            r,
            value
        });

        return value;
    }

    enumerate(items, size) {
        const subsets = chooseSubsets(items, size);
        this.state.generatedSubsets += subsets.length;

        this.events.emit("subsetsGenerated", {
            itemCount: items.length,
            subsetSize: size,
            count: subsets.length
        });

        return subsets;
    }
}

function verifyIdentities(n) {
    const symmetry = [];
    const row = pascalRow(n);

    for (let r = 0; r <= n; r += 1) {
        symmetry.push(row[r] === row[n - r]);
    }

    const symmetryHolds = symmetry.every(Boolean);
    const rowSum = row.reduce((sum, value) => sum + value, 0n);
    const expectedSum = 2n ** BigInt(n);

    let pascalHolds = true;

    for (let r = 1; r < n; r += 1) {
        const current = combinationBigInt(n, r);
        const adjacent = combinationBigInt(n - 1, r - 1)
            + combinationBigInt(n - 1, r);

        if (current !== adjacent) {
            pascalHolds = false;
            break;
        }
    }

    return {
        symmetryHolds,
        rowSumHolds: rowSum === expectedSum,
        pascalHolds
    };
}

function demonstrateSafeIntegerBoundary() {
    console.log("\nJavaScript integer precision");

    const safe = combinationNumber(52, 5);
    console.log(`C(52,5) as Number: ${safe}`);

    const exact = combinationBigInt(100, 50);
    console.log(`C(100,50) as BigInt: ${exact}`);
    console.log(`Exact decimal digits: ${exact.toString().length}`);
}

function demonstratePascal() {
    console.log("\nPascal's triangle");

    for (const row of pascalTriangle(8)) {
        console.log(row.map(value => value.toString()).join(" "));
    }
}

function demonstrateSubsetSelection(workflow) {
    console.log("\nReviewer committee combinations");

    const reviewers = [
        "Asha",
        "Bharat",
        "Chen",
        "Divya",
        "Ethan",
        "Fatima"
    ];

    const required = 3;
    const committees = workflow.enumerate(reviewers, required);

    console.log(`Eligible reviewers: ${reviewers.length}`);
    console.log(`Required committee size: ${required}`);
    console.log(`Generated committees: ${committees.length}`);
    console.log(
        `Expected C(n,r): ${evaluateReviewCommitteePolicy(
            reviewers.length,
            required
        )}`
    );

    for (const committee of committees.slice(0, 5)) {
        console.log(`  ${committee.join(", ")}`);
    }
}

function runTests() {
    for (let n = 0; n <= 25; n += 1) {
        for (let r = 0; r <= n; r += 1) {
            const coefficient = combinationBigInt(n, r);
            const rowValue = pascalRow(n)[r];

            if (coefficient !== rowValue) {
                throw new Error(`Mismatch at C(${n},${r})`);
            }

            if (coefficient !== combinationBigInt(n, n - r)) {
                throw new Error(`Symmetry failure at C(${n},${r})`);
            }
        }

        const row = pascalRow(n);
        const rowSum = row.reduce((sum, value) => sum + value, 0n);

        if (rowSum !== 2n ** BigInt(n)) {
            throw new Error(`Row sum failure at row ${n}`);
        }
    }

    const subsets = chooseSubsets(["A", "B", "C", "D"], 2);

    if (subsets.length !== 6) {
        throw new Error("Subset enumeration failure");
    }

    console.log("\nSelf-tests: all passed");
}

function main() {
    console.log("COMBINATIONS, BINOMIAL COEFFICIENTS, AND PASCAL'S TRIANGLE");
    console.log("=".repeat(62));

    const workflow = new CombinatorialWorkflow();

    workflow.events.on("calculated", ({ n, r, value }) => {
        console.log(`Calculated C(${n},${r}) = ${value}`);
    });

    workflow.events.on("subsetsGenerated", event => {
        console.log(
            `Event: generated ${event.count} subsets of size ${event.subsetSize}`
        );
    });

    workflow.calculate(10, 4);
    workflow.calculate(20, 10);

    demonstratePascal();
    demonstrateSubsetSelection(workflow);
    demonstrateSafeIntegerBoundary();

    console.log("\nIdentity checks");
    console.log(verifyIdentities(15));

    console.log("\nWorkflow counters");
    console.log(workflow.state);

    runTests();
}

try {
    main();
} catch (error) {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
}
