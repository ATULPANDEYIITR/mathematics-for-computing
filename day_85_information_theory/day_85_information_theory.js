"use strict";

/*
 * Information Theory: Event-Driven Probability Analysis
 *
 * Covers:
 * - Self-information
 * - Shannon entropy and uncertainty
 * - Joint and conditional entropy
 * - Mutual information
 * - Cross-entropy and KL divergence
 * - Probability estimation
 * - Huffman coding
 * - Streaming observations and event-driven updates
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

class InformationTheoryError extends Error {
    constructor(message) {
        super(message);
        this.name = "InformationTheoryError";
    }
}

function validateProbability(value) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0 ||
        value > 1
    ) {
        throw new InformationTheoryError(
            "Probability must be a finite number between 0 and 1."
        );
    }

    return value;
}

function validateDistribution(distribution) {
    if (
        !(distribution instanceof Map) ||
        distribution.size === 0
    ) {
        throw new InformationTheoryError(
            "A non-empty Map is required."
        );
    }

    let total = 0;

    for (const [symbol, probability] of distribution) {
        if (symbol === undefined || symbol === null) {
            throw new InformationTheoryError("Invalid outcome.");
        }

        total += validateProbability(probability);
    }

    if (Math.abs(total - 1) > 1e-9) {
        throw new InformationTheoryError(
            `Probabilities must sum to 1. Received ${total}.`
        );
    }

    return distribution;
}

function selfInformation(probability, base = 2) {
    validateProbability(probability);

    if (!Number.isFinite(base) || base <= 0 || base === 1) {
        throw new InformationTheoryError("Invalid logarithm base.");
    }

    if (probability === 0) {
        return Infinity;
    }

    return -Math.log(probability) / Math.log(base);
}

function entropy(distribution, base = 2) {
    validateDistribution(distribution);

    if (!Number.isFinite(base) || base <= 0 || base === 1) {
        throw new InformationTheoryError("Invalid logarithm base.");
    }

    let result = 0;

    for (const probability of distribution.values()) {
        if (probability > 0) {
            result -= probability * Math.log(probability) / Math.log(base);
        }
    }

    return result;
}

function marginalDistribution(joint, axis) {
    if (axis !== 0 && axis !== 1) {
        throw new InformationTheoryError("Axis must be 0 or 1.");
    }

    validateDistribution(joint);

    const result = new Map();

    for (const [pair, probability] of joint) {
        if (!Array.isArray(pair) || pair.length !== 2) {
            throw new InformationTheoryError(
                "Joint outcomes must be two-element arrays."
            );
        }

        const symbol = pair[axis];
        result.set(symbol, (result.get(symbol) || 0) + probability);
    }

    return result;
}

function conditionalEntropy(joint, givenAxis = 1) {
    if (givenAxis !== 0 && givenAxis !== 1) {
        throw new InformationTheoryError("Axis must be 0 or 1.");
    }

    const conditioned = marginalDistribution(joint, givenAxis);
    let result = 0;

    for (const [symbol, groupProbability] of conditioned) {
        const conditional = new Map();

        for (const [pair, probability] of joint) {
            if (Object.is(pair[givenAxis], symbol)) {
                conditional.set(
                    pair[1 - givenAxis],
                    probability / groupProbability
                );
            }
        }

        result += groupProbability * entropy(conditional);
    }

    return result;
}

function mutualInformation(joint) {
    const hx = entropy(marginalDistribution(joint, 0));
    const hy = entropy(marginalDistribution(joint, 1));
    const hxy = entropy(joint);

    return Math.max(0, hx + hy - hxy);
}

function crossEntropy(actual, predicted) {
    validateDistribution(actual);
    validateDistribution(predicted);

    if (
        actual.size !== predicted.size ||
        [...actual.keys()].some(key => !predicted.has(key))
    ) {
        throw new InformationTheoryError(
            "Distribution outcomes must match."
        );
    }

    let result = 0;

    for (const [symbol, probability] of actual) {
        if (probability === 0) continue;

        const q = predicted.get(symbol);

        if (q === 0) return Infinity;

        result -= probability * Math.log2(q);
    }

    return result;
}

function klDivergence(actual, predicted) {
    validateDistribution(actual);
    validateDistribution(predicted);

    if (
        actual.size !== predicted.size ||
        [...actual.keys()].some(key => !predicted.has(key))
    ) {
        throw new InformationTheoryError(
            "Distribution outcomes must match."
        );
    }

    let result = 0;

    for (const [symbol, probability] of actual) {
        if (probability === 0) continue;

        const q = predicted.get(symbol);

        if (q === 0) return Infinity;

        result += probability * Math.log2(probability / q);
    }

    return Math.max(0, result);
}

class MinHeap {
    constructor() {
        this.items = [];
    }

    push(item) {
        this.items.push(item);

        let index = this.items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.items[parent].weight <= item.weight) break;

            this.items[index] = this.items[parent];
            index = parent;
        }

        this.items[index] = item;
    }

    pop() {
        if (this.items.length === 0) {
            throw new InformationTheoryError("Heap is empty.");
        }

        const root = this.items[0];
        const last = this.items.pop();

        if (this.items.length === 0) return root;

        let index = 0;

        while (true) {
            let smallest = index;
            const left = index * 2 + 1;
            const right = left + 1;

            if (
                left < this.items.length &&
                this.items[left].weight < this.items[smallest].weight
            ) {
                smallest = left;
            }

            if (
                right < this.items.length &&
                this.items[right].weight < this.items[smallest].weight
            ) {
                smallest = right;
            }

            if (smallest === index) break;

            this.items[index] = this.items[smallest];
            index = smallest;
        }

        this.items[index] = last;
        return root;
    }

    get size() {
        return this.items.length;
    }
}

function huffmanCodes(distribution) {
    validateDistribution(distribution);

    const heap = new MinHeap();
    let order = 0;

    for (const [symbol, probability] of distribution) {
        heap.push({
            symbol,
            weight: probability,
            order: order++,
            left: null,
            right: null
        });
    }

    if (heap.size === 1) {
        return new Map([[heap.pop().symbol, "0"]]);
    }

    while (heap.size > 1) {
        const left = heap.pop();
        const right = heap.pop();

        heap.push({
            symbol: null,
            weight: left.weight + right.weight,
            order: order++,
            left,
            right
        });
    }

    const codes = new Map();

    function traverse(node, prefix) {
        if (node.symbol !== null) {
            codes.set(node.symbol, prefix);
            return;
        }

        traverse(node.left, prefix + "0");
        traverse(node.right, prefix + "1");
    }

    traverse(heap.pop(), "");

    return codes;
}

function estimateDistribution(observations) {
    if (!Array.isArray(observations) || observations.length === 0) {
        throw new InformationTheoryError(
            "Observations must be a non-empty array."
        );
    }

    const counts = new Map();

    for (const item of observations) {
        counts.set(item, (counts.get(item) || 0) + 1);
    }

    const total = observations.length;
    const probabilities = new Map();

    for (const [symbol, count] of counts) {
        probabilities.set(symbol, count / total);
    }

    return probabilities;
}

function smoothDistribution(observations, vocabulary, alpha = 1) {
    if (
        !Array.isArray(vocabulary) ||
        vocabulary.length === 0 ||
        new Set(vocabulary).size !== vocabulary.length
    ) {
        throw new InformationTheoryError(
            "Vocabulary must contain unique outcomes."
        );
    }

    if (!Number.isFinite(alpha) || alpha <= 0) {
        throw new InformationTheoryError("Alpha must be positive.");
    }

    const counts = new Map(vocabulary.map(symbol => [symbol, 0]));

    for (const observation of observations) {
        if (!counts.has(observation)) {
            throw new InformationTheoryError(
                "Observation outside vocabulary."
            );
        }

        counts.set(observation, counts.get(observation) + 1);
    }

    const denominator = observations.length + alpha * vocabulary.length;

    return new Map(
        [...counts].map(([symbol, count]) => [
            symbol,
            (count + alpha) / denominator
        ])
    );
}

/*
 * Event-driven entropy monitor.
 * The monitor maintains counts and emits updates after each observation.
 * Counts can be reset without recreating the event listeners.
 */
class EntropyMonitor extends EventEmitter {
    constructor() {
        super();
        this.counts = new Map();
        this.total = 0;
        this.version = 0;
    }

    observe(symbol) {
        if (symbol === undefined || symbol === null) {
            throw new InformationTheoryError("Invalid observation.");
        }

        this.counts.set(
            symbol,
            (this.counts.get(symbol) || 0) + 1
        );

        this.total++;
        this.version++;

        const probabilities = new Map(
            [...this.counts].map(([key, count]) => [
                key,
                count / this.total
            ])
        );

        const result = {
            version: this.version,
            observations: this.total,
            entropy: entropy(probabilities),
            normalizedEntropy:
                this.counts.size <= 1
                    ? 0
                    : entropy(probabilities) /
                      Math.log2(this.counts.size)
        };

        this.emit("observation", Object.freeze(result));

        return result;
    }

    snapshot() {
        if (this.total === 0) {
            return {
                observations: 0,
                entropy: 0,
                distribution: new Map()
            };
        }

        const distribution = new Map(
            [...this.counts].map(([symbol, count]) => [
                symbol,
                count / this.total
            ])
        );

        return {
            observations: this.total,
            entropy: entropy(distribution),
            distribution
        };
    }

    reset() {
        this.counts.clear();
        this.total = 0;
        this.version++;

        this.emit("reset", this.version);
    }
}

async function processObservationStream(
    observations,
    monitor,
    batchSize = 100
) {
    if (!Array.isArray(observations)) {
        throw new InformationTheoryError("Expected an array.");
    }

    if (!Number.isInteger(batchSize) || batchSize < 1) {
        throw new InformationTheoryError("Invalid batch size.");
    }

    const results = [];

    for (let start = 0; start < observations.length; start += batchSize) {
        const batch = observations.slice(start, start + batchSize);

        for (const symbol of batch) {
            results.push(monitor.observe(symbol));
        }

        // Yield to the event loop between batches.
        await new Promise(resolve => setImmediate(resolve));
    }

    return results;
}

async function main() {
    console.log("INFORMATION THEORY ENGINE");
    console.log("=".repeat(55));

    const distribution = new Map([
        ["A", 0.5],
        ["B", 0.25],
        ["C", 0.125],
        ["D", 0.125]
    ]);

    console.log("\n1. SELF-INFORMATION");

    for (const [symbol, probability] of distribution) {
        console.log(
            `${symbol}: ${selfInformation(probability).toFixed(4)} bits`
        );
    }

    console.log("\n2. ENTROPY");
    console.log("Shannon entropy:", entropy(distribution).toFixed(4));
    console.log(
        "Maximum entropy:",
        Math.log2(distribution.size).toFixed(4)
    );

    const joint = new Map([
        [["Sunny", "Hot"], 0.3],
        [["Sunny", "Cold"], 0.2],
        [["Rainy", "Hot"], 0.1],
        [["Rainy", "Cold"], 0.4]
    ]);

    console.log("\n3. JOINT AND CONDITIONAL ENTROPY");
    console.log("H(X,Y):", entropy(joint).toFixed(4));
    console.log(
        "H(X|Y):",
        conditionalEntropy(joint, 1).toFixed(4)
    );
    console.log("I(X;Y):", mutualInformation(joint).toFixed(4));

    const actual = new Map([
        ["A", 0.5],
        ["B", 0.3],
        ["C", 0.2]
    ]);

    const predicted = new Map([
        ["A", 0.4],
        ["B", 0.4],
        ["C", 0.2]
    ]);

    console.log("\n4. DISTRIBUTION COMPARISON");
    console.log("Cross-entropy:", crossEntropy(actual, predicted));
    console.log("KL divergence:", klDivergence(actual, predicted));

    console.log("\n5. HUFFMAN CODING");

    const codes = huffmanCodes(distribution);

    for (const [symbol, code] of codes) {
        console.log(`${symbol}: ${code}`);
    }

    const expectedLength = [...codes].reduce(
        (total, [symbol, code]) =>
            total + distribution.get(symbol) * code.length,
        0
    );

    console.log("Expected code length:", expectedLength.toFixed(4));

    console.log("\n6. EVENT-DRIVEN ENTROPY MONITOR");

    const monitor = new EntropyMonitor();

    monitor.on("observation", event => {
        if (event.observations % 2 === 0) {
            console.log(
                `Observations=${event.observations}, ` +
                `H=${event.entropy.toFixed(4)} bits`
            );
        }
    });

    const observations = [
        "success", "success", "failure",
        "success", "failure", "success"
    ];

    await processObservationStream(observations, monitor, 2);

    console.log("\nFinal monitor state:", monitor.snapshot());

    console.log("\n7. LAPLACE SMOOTHING");

    const smoothed = smoothDistribution(
        observations,
        ["success", "failure", "unknown"],
        1
    );

    console.log(Object.fromEntries(smoothed));

    console.log("\n8. VALIDATION");

    try {
        entropy(new Map([
            ["A", 0.7],
            ["B", 0.7]
        ]));
    } catch (error) {
        console.log("Rejected invalid distribution:", error.message);
    }

    try {
        selfInformation(-0.2);
    } catch (error) {
        console.log("Rejected invalid probability:", error.message);
    }

    console.log("\n9. INTEGRITY CHECKS");

    if (Math.abs(entropy(distribution) - 1.75) > 1e-9) {
        throw new Error("Entropy invariant failed.");
    }

    if (klDivergence(actual, actual) > 1e-9) {
        throw new Error("KL divergence invariant failed.");
    }

    if (expectedLength + 1e-9 < entropy(distribution)) {
        throw new Error("Source coding bound violated.");
    }

    console.log("All information-theoretic checks passed.");

    // Generate a unique execution identifier without using it as a secret.
    console.log(
        "Execution ID:",
        crypto.randomUUID()
    );
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
