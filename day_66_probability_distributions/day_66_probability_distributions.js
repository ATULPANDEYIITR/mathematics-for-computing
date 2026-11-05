"use strict";

/*
 * Probability Distributions
 * Bernoulli, Binomial, Geometric, Negative Binomial.
 *
 * Node.js 18+.
 *
 * Includes an event-driven simulation engine, distribution validation,
 * analytical calculations, reproducible sampling, and reporting.
 */

const { EventEmitter } = require("node:events");

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProbabilityError";
    }
}

function validateProbability(p) {
    if (typeof p !== "number" || !Number.isFinite(p) || p < 0 || p > 1) {
        throw new ProbabilityError(
            "Probability must be a finite number between 0 and 1."
        );
    }
}

function validateInteger(value, name, minimum = 0) {
    if (!Number.isSafeInteger(value) || value < minimum) {
        throw new ProbabilityError(
            `${name} must be a safe integer >= ${minimum}.`
        );
    }
}

function choose(n, k) {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;

    k = Math.min(k, n - k);
    let result = 1;

    for (let i = 1; i <= k; i++) {
        result = result * (n - k + i) / i;
    }

    return result;
}

/*
 * Seeded pseudorandom number generator.
 * It provides reproducible simulations, not cryptographic randomness.
 */
class RandomGenerator {
    constructor(seed = 42) {
        validateInteger(seed, "Seed");
        this.state = seed >>> 0;
    }

    next() {
        this.state = (this.state + 0x6D2B79F5) >>> 0;

        let t = this.state;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);

        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
}

class Distribution {
    constructor(probability) {
        validateProbability(probability);
        this.p = probability;
    }

    pmf() {
        throw new Error("PMF must be implemented.");
    }

    cdf() {
        throw new Error("CDF must be implemented.");
    }

    sample() {
        throw new Error("Sampling must be implemented.");
    }

    statistics() {
        throw new Error("Statistics must be implemented.");
    }

    probabilityAtLeast(k) {
        validateInteger(k, "Threshold");
        return Math.max(0, 1 - this.cdf(k - 1));
    }

    simulate(count, random) {
        validateInteger(count, "Simulation count", 1);

        const frequencies = new Map();
        let sum = 0;
        let sumSquares = 0;

        for (let i = 0; i < count; i++) {
            const value = this.sample(random);

            frequencies.set(
                value,
                (frequencies.get(value) || 0) + 1
            );

            sum += value;
            sumSquares += value * value;
        }

        const mean = sum / count;
        const variance = Math.max(0, sumSquares / count - mean * mean);

        return {
            count,
            mean,
            variance,
            frequencies: Object.fromEntries(
                [...frequencies.entries()].sort((a, b) => a[0] - b[0])
            )
        };
    }
}

class Bernoulli extends Distribution {
    pmf(k) {
        if (k === 1) return this.p;
        if (k === 0) return 1 - this.p;
        return 0;
    }

    cdf(k) {
        if (k < 0) return 0;
        if (k === 0) return 1 - this.p;
        return 1;
    }

    sample(random) {
        return Number(random.next() < this.p);
    }

    statistics() {
        const variance = this.p * (1 - this.p);

        return {
            mean: this.p,
            variance,
            standardDeviation: Math.sqrt(variance)
        };
    }
}

class Binomial extends Distribution {
    constructor(n, p) {
        super(p);
        validateInteger(n, "Number of trials");
        this.n = n;
    }

    pmf(k) {
        if (!Number.isSafeInteger(k) || k < 0 || k > this.n) {
            return 0;
        }

        return choose(this.n, k) *
            this.p ** k *
            (1 - this.p) ** (this.n - k);
    }

    cdf(k) {
        if (k < 0) return 0;
        if (k >= this.n) return 1;

        let result = 0;

        for (let i = 0; i <= k; i++) {
            result += this.pmf(i);
        }

        return Math.min(1, result);
    }

    sample(random) {
        let successes = 0;

        for (let i = 0; i < this.n; i++) {
            if (random.next() < this.p) successes++;
        }

        return successes;
    }

    statistics() {
        const mean = this.n * this.p;
        const variance = this.n * this.p * (1 - this.p);

        return {
            mean,
            variance,
            standardDeviation: Math.sqrt(variance)
        };
    }
}

class Geometric extends Distribution {
    pmf(k) {
        if (!Number.isSafeInteger(k) || k < 1 || this.p === 0) {
            return 0;
        }

        if (this.p === 1) return Number(k === 1);

        return this.p * (1 - this.p) ** (k - 1);
    }

    cdf(k) {
        if (k < 1) return 0;
        if (this.p === 0) return 0;
        if (this.p === 1) return 1;

        return 1 - (1 - this.p) ** k;
    }

    sample(random) {
        if (this.p === 0) {
            throw new ProbabilityError(
                "Geometric sampling is impossible when p = 0."
            );
        }

        if (this.p === 1) return 1;

        return Math.floor(
            Math.log1p(-random.next()) / Math.log1p(-this.p)
        ) + 1;
    }

    statistics() {
        if (this.p === 0) {
            return {
                mean: Infinity,
                variance: Infinity,
                standardDeviation: Infinity
            };
        }

        const mean = 1 / this.p;
        const variance = (1 - this.p) / (this.p * this.p);

        return {
            mean,
            variance,
            standardDeviation: Math.sqrt(variance)
        };
    }
}

class NegativeBinomial extends Distribution {
    constructor(requiredSuccesses, p) {
        super(p);
        validateInteger(requiredSuccesses, "Required successes", 1);
        this.r = requiredSuccesses;
    }

    pmf(k) {
        if (!Number.isSafeInteger(k) || k < this.r || this.p === 0) {
            return 0;
        }

        if (this.p === 1) return Number(k === this.r);

        return choose(k - 1, this.r - 1) *
            this.p ** this.r *
            (1 - this.p) ** (k - this.r);
    }

    cdf(k) {
        if (k < this.r || this.p === 0) return 0;
        if (this.p === 1) return 1;

        let result = 0;

        for (let i = this.r; i <= k; i++) {
            result += this.pmf(i);
        }

        return Math.min(1, result);
    }

    sample(random) {
        if (this.p === 0) {
            throw new ProbabilityError(
                "Negative binomial sampling is impossible when p = 0."
            );
        }

        if (this.p === 1) return this.r;

        let successes = 0;
        let trials = 0;

        while (successes < this.r) {
            trials++;

            if (random.next() < this.p) {
                successes++;
            }
        }

        return trials;
    }

    statistics() {
        if (this.p === 0) {
            return {
                mean: Infinity,
                variance: Infinity,
                standardDeviation: Infinity
            };
        }

        const mean = this.r / this.p;
        const variance = this.r * (1 - this.p) / (this.p * this.p);

        return {
            mean,
            variance,
            standardDeviation: Math.sqrt(variance)
        };
    }
}

/*
 * Event-driven simulation service.
 * Events provide progress and completion information without
 * coupling distribution classes to reporting.
 */
class SimulationService extends EventEmitter {
    constructor() {
        super();
        this.completedRuns = 0;
    }

    async execute(name, distribution, count, seed = 42) {
        if (!(distribution instanceof Distribution)) {
            throw new ProbabilityError("Invalid distribution instance.");
        }

        validateInteger(count, "Simulation count", 1);
        validateInteger(seed, "Seed");

        const random = new RandomGenerator(seed);
        const result = distribution.simulate(count, random);

        this.completedRuns++;

        this.emit("completed", {
            name,
            count,
            mean: result.mean
        });

        return {
            name,
            analytical: distribution.statistics(),
            empirical: result,
            probabilityAtLeastTwo: distribution.probabilityAtLeast(2)
        };
    }
}

function assertClose(actual, expected, tolerance = 1e-10) {
    if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`Assertion failed: ${actual} != ${expected}`);
    }
}

function runTests() {
    const b = new Bernoulli(0.3);
    assertClose(b.pmf(1), 0.3);
    assertClose(b.pmf(0), 0.7);

    const binomial = new Binomial(5, 0.5);
    assertClose(binomial.pmf(2), 0.3125);
    assertClose(binomial.cdf(5), 1);

    const geometric = new Geometric(0.25);
    assertClose(geometric.pmf(2), 0.1875);
    assertClose(geometric.cdf(2), 0.4375);

    const negativeBinomial = new NegativeBinomial(3, 0.5);
    assertClose(negativeBinomial.pmf(4), 0.1875);
    assertClose(negativeBinomial.cdf(4), 0.3125);

    assertClose(binomial.pmf(-1), 0);
    assertClose(geometric.pmf(0), 0);

    let rejected = false;

    try {
        new Binomial(-2, 0.5);
    } catch (error) {
        rejected = error instanceof ProbabilityError;
    }

    if (!rejected) throw new Error("Invalid parameters were accepted.");

    console.log("All validation tests passed.");
}

async function main() {
    runTests();

    const service = new SimulationService();

    service.on("completed", event => {
        console.log(
            `[EVENT] ${event.name}: ${event.count} samples, ` +
            `empirical mean=${event.mean.toFixed(5)}`
        );
    });

    const scenarios = [
        {
            name: "Bernoulli: Payment success",
            distribution: new Bernoulli(0.92)
        },
        {
            name: "Binomial: Successful payments out of 15",
            distribution: new Binomial(15, 0.92)
        },
        {
            name: "Geometric: Attempts until connection",
            distribution: new Geometric(0.3)
        },
        {
            name: "Negative Binomial: Five completed connections",
            distribution: new NegativeBinomial(5, 0.3)
        }
    ];

    for (const scenario of scenarios) {
        const result = await service.execute(
            scenario.name,
            scenario.distribution,
            10000,
            42
        );

        console.log(`\n${result.name}`);
        console.log("Analytical:", result.analytical);
        console.log("Empirical:", result.empirical);
        console.log(
            "P(X >= 2):",
            result.probabilityAtLeastTwo.toFixed(6)
        );
    }

    console.log(`\nCompleted simulations: ${service.completedRuns}`);

    // A zero-success-probability model is mathematically defined,
    // but cannot produce a finite geometric waiting time.
    const impossible = new Geometric(0);

    try {
        impossible.sample(new RandomGenerator(42));
    } catch (error) {
        console.log("\nExpected failure:", error.message);
    }
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
