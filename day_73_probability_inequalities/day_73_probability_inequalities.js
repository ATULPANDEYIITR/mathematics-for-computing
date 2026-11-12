"use strict";

/*
 * Probability Inequalities: Markov, Chebyshev, Jensen, and Chernoff.
 *
 * Event-driven probability analysis and asynchronous experiment processing.
 * Runtime: Node.js 18+
 * Dependencies: None.
 */

const { EventEmitter } = require("node:events");
const { performance } = require("node:perf_hooks");

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProbabilityError";
    }
}

class Distribution {
    constructor(values, probabilities) {
        if (!Array.isArray(values) || values.length === 0) {
            throw new ProbabilityError("Values must be a nonempty array.");
        }

        if (!Array.isArray(probabilities) ||
            values.length !== probabilities.length) {
            throw new ProbabilityError("Distribution dimensions do not match.");
        }

        if (!values.every(Number.isFinite)) {
            throw new ProbabilityError("Values must be finite.");
        }

        if (!probabilities.every(
            p => Number.isFinite(p) && p >= 0
        )) {
            throw new ProbabilityError(
                "Probabilities must be finite and nonnegative."
            );
        }

        const total = probabilities.reduce((a, b) => a + b, 0);

        if (Math.abs(total - 1) > 1e-10) {
            throw new ProbabilityError(
                "Probabilities must sum to one."
            );
        }

        this.values = Object.freeze([...values]);
        this.probabilities = Object.freeze(
            probabilities.map(p => p / total)
        );

        Object.freeze(this);
    }

    expectation(fn = x => x) {
        const result = this.values.reduce(
            (sum, x, i) => sum + this.probabilities[i] * fn(x),
            0
        );

        if (!Number.isFinite(result)) {
            throw new ProbabilityError("Invalid expectation.");
        }

        return result;
    }

    get mean() {
        return this.expectation();
    }

    get variance() {
        const mu = this.mean;

        return this.expectation(x => (x - mu) ** 2);
    }

    probability(predicate) {
        return this.values.reduce(
            (sum, x, i) =>
                sum + (predicate(x) ? this.probabilities[i] : 0),
            0
        );
    }

    sample(count, seed = 12345) {
        if (!Number.isSafeInteger(count) || count <= 0) {
            throw new ProbabilityError("Invalid sample count.");
        }

        // Deterministic pseudo-random generator for reproducible experiments.
        let state = seed >>> 0;

        const random = () => {
            state = (1664525 * state + 1013904223) >>> 0;
            return state / 4294967296;
        };

        const cumulative = [];
        let total = 0;

        for (const p of this.probabilities) {
            total += p;
            cumulative.push(total);
        }

        const result = [];

        for (let i = 0; i < count; i++) {
            const value = random();
            let index = cumulative.findIndex(x => value < x);

            if (index === -1) {
                index = cumulative.length - 1;
            }

            result.push(this.values[index]);
        }

        return result;
    }
}

function markov(distribution, threshold) {
    if (distribution.values.some(x => x < 0)) {
        throw new ProbabilityError(
            "Markov requires a nonnegative random variable."
        );
    }

    if (!Number.isFinite(threshold) || threshold <= 0) {
        throw new ProbabilityError("Threshold must be positive.");
    }

    return Math.min(1, distribution.mean / threshold);
}

function chebyshev(distribution, deviation) {
    if (!Number.isFinite(deviation) || deviation <= 0) {
        throw new ProbabilityError("Deviation must be positive.");
    }

    return Math.min(
        1,
        distribution.variance / (deviation * deviation)
    );
}

function jensen(distribution, convexFunction) {
    if (typeof convexFunction !== "function") {
        throw new ProbabilityError("A function is required.");
    }

    const left = convexFunction(distribution.mean);
    const right = distribution.expectation(convexFunction);

    if (!Number.isFinite(left) || !Number.isFinite(right)) {
        throw new ProbabilityError("Function produced invalid output.");
    }

    return Object.freeze({
        functionAtMean: left,
        meanOfFunction: right,
        holds: left <= right + 1e-10,
        difference: right - left
    });
}

function logSumExp(values) {
    const maximum = Math.max(...values);

    if (maximum === -Infinity) {
        return -Infinity;
    }

    return maximum + Math.log(
        values.reduce(
            (sum, value) => sum + Math.exp(value - maximum),
            0
        )
    );
}

function logMGF(distribution, lambda) {
    if (!Number.isFinite(lambda)) {
        throw new ProbabilityError("Lambda must be finite.");
    }

    const terms = distribution.values
        .map((x, i) => {
            const p = distribution.probabilities[i];
            return p === 0 ? -Infinity : Math.log(p) + lambda * x;
        })
        .filter(Number.isFinite);

    const result = logSumExp(terms);

    if (!Number.isFinite(result)) {
        throw new ProbabilityError("MGF overflow or invalid result.");
    }

    return result;
}

function chernoff(distribution, threshold, options = {}) {
    const {
        lambdaMax = 20,
        steps = 2000
    } = options;

    if (!Number.isFinite(threshold) ||
        !Number.isFinite(lambdaMax) ||
        lambdaMax <= 0 ||
        !Number.isSafeInteger(steps) ||
        steps < 1) {
        throw new ProbabilityError("Invalid Chernoff parameters.");
    }

    let bestBound = 1;
    let bestLambda = 0;

    for (let i = 0; i <= steps; i++) {
        const lambda = lambdaMax * i / steps;

        const exponent =
            logMGF(distribution, lambda) - lambda * threshold;

        const bound = exponent < -745
            ? 0
            : Math.min(1, Math.exp(exponent));

        if (bound < bestBound) {
            bestBound = bound;
            bestLambda = lambda;
        }
    }

    return Object.freeze({
        threshold,
        bound: bestBound,
        optimalLambda: bestLambda,
        exactProbability: distribution.probability(
            x => x >= threshold
        )
    });
}

function binomialDistribution(n, p) {
    if (!Number.isSafeInteger(n) || n < 0 || n > 1000) {
        throw new ProbabilityError("Invalid number of trials.");
    }

    if (!Number.isFinite(p) || p < 0 || p > 1) {
        throw new ProbabilityError("Probability must be in [0, 1].");
    }

    const probabilities = new Array(n + 1).fill(0);

    // Recurrence avoids repeated factorial calculations.
    if (p === 0) {
        probabilities[0] = 1;
    } else if (p === 1) {
        probabilities[n] = 1;
    } else {
        probabilities[0] = Math.pow(1 - p, n);

        for (let k = 1; k <= n; k++) {
            probabilities[k] =
                probabilities[k - 1] *
                (n - k + 1) / k *
                p / (1 - p);
        }
    }

    return new Distribution(
        Array.from({ length: n + 1 }, (_, i) => i),
        probabilities
    );
}

class ProbabilityEngine extends EventEmitter {
    constructor() {
        super();
        this.experiments = new Map();
        this.running = false;
    }

    register(name, distribution) {
        if (typeof name !== "string" || name.trim() === "") {
            throw new ProbabilityError("Experiment name is required.");
        }

        if (!(distribution instanceof Distribution)) {
            throw new ProbabilityError("Invalid distribution.");
        }

        if (this.experiments.has(name)) {
            throw new ProbabilityError("Experiment already exists.");
        }

        this.experiments.set(name, distribution);
        this.emit("registered", { name });
    }

    async evaluate(name, threshold) {
        if (this.running) {
            throw new ProbabilityError(
                "Concurrent batch execution is not permitted."
            );
        }

        const distribution = this.experiments.get(name);

        if (!distribution) {
            throw new ProbabilityError("Experiment not found.");
        }

        this.running = true;
        const started = performance.now();

        try {
            // Yield to the event loop instead of blocking the caller.
            await new Promise(resolve => setImmediate(resolve));

            const result = {
                name,
                threshold,
                mean: distribution.mean,
                variance: distribution.variance,
                markov: distribution.values.every(x => x >= 0)
                    ? markov(distribution, threshold)
                    : null,
                chebyshev: chebyshev(
                    distribution,
                    Math.abs(threshold - distribution.mean) || 1e-12
                ),
                exactProbability: distribution.probability(
                    x => x >= threshold
                ),
                chernoff: chernoff(distribution, threshold)
            };

            result.durationMs = performance.now() - started;

            this.emit("evaluated", result);
            return Object.freeze(result);
        } catch (error) {
            this.emit("failed", { name, message: error.message });
            throw error;
        } finally {
            this.running = false;
        }
    }

    async evaluateAll(threshold) {
        const results = [];

        for (const name of this.experiments.keys()) {
            results.push(await this.evaluate(name, threshold));
        }

        return results;
    }
}

async function main() {
    const engine = new ProbabilityEngine();

    engine.on("registered", event => {
        console.log(`Registered: ${event.name}`);
    });

    engine.on("evaluated", event => {
        console.log(
            `Evaluated ${event.name} in ${event.durationMs.toFixed(3)} ms`
        );
    });

    engine.on("failed", event => {
        console.error(`Failed ${event.name}: ${event.message}`);
    });

    const operationalRisk = new Distribution(
        [0, 1, 2, 3, 4, 5],
        [0.05, 0.10, 0.20, 0.30, 0.20, 0.15]
    );

    engine.register("operational-risk", operationalRisk);
    engine.register("binomial-failures", binomialDistribution(30, 0.5));

    const results = await engine.evaluateAll(4);

    console.log("\nPROBABILITY REPORT");

    for (const result of results) {
        console.log(`\nExperiment: ${result.name}`);
        console.log(`Mean: ${result.mean.toFixed(5)}`);
        console.log(`Variance: ${result.variance.toFixed(5)}`);
        console.log(`Markov: ${result.markov}`);
        console.log(`Chebyshev: ${result.chebyshev}`);
        console.log(`Exact probability: ${result.exactProbability}`);
        console.log(`Chernoff: ${result.chernoff.bound}`);
    }

    console.log("\nJENSEN VALIDATION");

    const jensenResult = jensen(
        operationalRisk,
        x => x * x
    );

    console.log(jensenResult);

    console.log("\nEDGE CASE VALIDATION");

    try {
        markov(operationalRisk, 0);
    } catch (error) {
        console.log(error.message);
    }

    try {
        engine.register("invalid", new Distribution([1, 2], [0.2, 0.2]));
    } catch (error) {
        console.log(error.message);
    }
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
