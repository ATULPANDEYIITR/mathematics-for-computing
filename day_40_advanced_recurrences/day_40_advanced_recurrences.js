"use strict";

/*
 * Advanced recurrence analysis in JavaScript.
 *
 * This file focuses on event-driven evaluation of recurrence trees,
 * memoization, symbolic classification, and safe numerical reporting.
 * Run with Node.js 18 or later.
 */

class RecurrenceModel {
    constructor({ name, a, b, combineCost, baseCost = 1 }) {
        if (!Number.isSafeInteger(a) || a < 1) {
            throw new RangeError("a must be a positive safe integer");
        }
        if (!Number.isSafeInteger(b) || b <= 1) {
            throw new RangeError("b must be an integer greater than one");
        }
        if (typeof combineCost !== "function") {
            throw new TypeError("combineCost must be a function");
        }
        if (!Number.isSafeInteger(baseCost) || baseCost < 0) {
            throw new RangeError("baseCost must be a nonnegative safe integer");
        }

        this.name = name;
        this.a = a;
        this.b = b;
        this.combineCost = combineCost;
        this.baseCost = baseCost;
        this.memo = new Map();
    }

    validateSize(n) {
        if (!Number.isSafeInteger(n) || n < 1) {
            throw new RangeError("n must be a positive safe integer");
        }
    }

    cost(n) {
        this.validateSize(n);

        const evaluate = (size) => {
            if (size <= 1) return this.baseCost;
            if (this.memo.has(size)) return this.memo.get(size);

            const combine = this.combineCost(size);
            if (!Number.isSafeInteger(combine) || combine < 0) {
                throw new RangeError(
                    "Combine cost must be a nonnegative safe integer"
                );
            }

            const childSize = Math.ceil(size / this.b);
            const childCost = evaluate(childSize);
            const result = this.a * childCost + combine;

            if (!Number.isSafeInteger(result)) {
                throw new RangeError(
                    "Cost exceeds JavaScript's safe integer range"
                );
            }

            this.memo.set(size, result);
            return result;
        };

        return evaluate(n);
    }

    tree(n) {
        this.validateSize(n);

        const levels = [];
        let nodes = 1;
        let size = n;
        let depth = 0;

        while (size > 1) {
            const workPerNode = this.combineCost(size);
            const aggregate = nodes * workPerNode;

            levels.push({
                depth,
                nodes,
                size,
                workPerNode,
                aggregate
            });

            nodes *= this.a;
            if (!Number.isSafeInteger(nodes)) {
                throw new RangeError("Tree node count exceeds safe integers");
            }

            size = Math.floor(size / this.b);
            depth += 1;
        }

        levels.push({
            depth,
            nodes,
            size: 1,
            workPerNode: this.baseCost,
            aggregate: nodes * this.baseCost
        });

        return levels;
    }
}

function masterClassification(a, b, power) {
    if (!Number.isFinite(a) || !Number.isInteger(a) || a < 1) {
        throw new RangeError("a must be a positive integer");
    }
    if (!Number.isFinite(b) || !Number.isInteger(b) || b <= 1) {
        throw new RangeError("b must be an integer greater than one");
    }
    if (!Number.isFinite(power) || power < 0) {
        throw new RangeError("power must be finite and nonnegative");
    }

    const critical = Math.log(a) / Math.log(b);
    const epsilon = 1e-10;

    if (power < critical - epsilon) {
        return {
            case: 1,
            complexity: `Theta(n^${critical.toFixed(4)})`,
            interpretation: "Leaf work dominates."
        };
    }

    if (Math.abs(power - critical) <= epsilon) {
        return {
            case: 2,
            complexity: `Theta(n^${critical.toFixed(4)} log n)`,
            interpretation: "Every level contributes the same asymptotic order."
        };
    }

    return {
        case: 3,
        complexity: `Theta(n^${power})`,
        interpretation:
            "Nonrecursive work dominates when the regularity condition holds."
    };
}

function summarizeTree(model, n) {
    const levels = model.tree(n);
    const totalWork = levels.reduce((sum, level) => sum + level.aggregate, 0);

    return {
        recurrence: model.name,
        n,
        depth: levels.length - 1,
        levels,
        totalWork
    };
}

function displayTree(summary) {
    console.log(`\n${summary.recurrence}, n=${summary.n}`);
    console.table(
        summary.levels.map(({ depth, nodes, size, aggregate }) => ({
            depth,
            nodes,
            subproblemSize: size,
            aggregateWork: aggregate
        }))
    );
    console.log(`Aggregate tree-model work: ${summary.totalWork}`);
}

function createMergeSortModel() {
    return new RecurrenceModel({
        name: "Merge-sort cost model",
        a: 2,
        b: 2,
        combineCost: n => n
    });
}

function createBinarySearchModel() {
    return new RecurrenceModel({
        name: "Binary-search cost model",
        a: 1,
        b: 2,
        combineCost: () => 1
    });
}

function simulateReviewableBuildPipeline() {
    /*
     * A build pipeline can split a large test suite into parallel shards.
     * Each shard recursively splits until it reaches a manageable batch.
     * The fixed per-level overhead represents scheduling and aggregation.
     */
    const pipeline = new RecurrenceModel({
        name: "Parallel test-sharding pipeline",
        a: 4,
        b: 2,
        combineCost: () => 12,
        baseCost: 5
    });

    return summarizeTree(pipeline, 32);
}

async function processRecurrenceJobs(jobs) {
    /*
     * Promise.all preserves input ordering even when individual jobs
     * complete at different times. Invalid jobs reject the aggregate.
     */
    return Promise.all(
        jobs.map(async ({ model, size }) => {
            await Promise.resolve();
            return {
                name: model.name,
                size,
                cost: model.cost(size)
            };
        })
    );
}

async function main() {
    console.log("Master Theorem classifications");

    for (const example of [
        { a: 2, b: 2, power: 1 },
        { a: 1, b: 2, power: 0 },
        { a: 2, b: 2, power: 2 },
        { a: 4, b: 2, power: 1 }
    ]) {
        const result = masterClassification(
            example.a,
            example.b,
            example.power
        );
        console.log(
            `a=${example.a}, b=${example.b}, p=${example.power}:`,
            result
        );
    }

    const mergeSort = createMergeSortModel();
    const binarySearch = createBinarySearchModel();

    displayTree(summarizeTree(mergeSort, 16));
    displayTree(summarizeTree(binarySearch, 16));
    displayTree(simulateReviewableBuildPipeline());

    console.log("\nAsynchronous recurrence jobs");
    const results = await processRecurrenceJobs([
        { model: mergeSort, size: 32 },
        { model: binarySearch, size: 32 }
    ]);
    console.table(results);

    console.log("\nValidation and numerical limitations");
    try {
        masterClassification(2, 1, 1);
    } catch (error) {
        console.error(`Invalid recurrence rejected: ${error.message}`);
    }

    try {
        mergeSort.cost(-5);
    } catch (error) {
        console.error(`Invalid input rejected: ${error.message}`);
    }

    console.log(
        "Floating-point logarithms are approximations. " +
        "Symbolic asymptotic claims still require mathematical proof."
    );
}

main().catch(error => {
    console.error("Recurrence analysis failed:", error.message);
    process.exitCode = 1;
});
