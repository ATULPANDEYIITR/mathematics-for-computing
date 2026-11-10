"use strict";

/**
 * Law of Large Numbers: Event-driven simulation and convergence analysis.
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 *
 * Features:
 * - Weak and strong laws.
 * - Distribution-specific random sampling.
 * - EventEmitter-based experiment monitoring.
 * - Asynchronous Monte Carlo execution.
 * - Chebyshev probability bounds.
 * - Reproducible pseudorandom generator.
 * - Online statistical aggregation.
 * - JSON report persistence.
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class SeededRandom {
    constructor(seed = 42) {
        this.state = seed >>> 0;

        if (this.state === 0) {
            this.state = 1;
        }
    }

    next() {
        // Mulberry32 deterministic pseudorandom generator.
        let t = this.state += 0x6D2B79F5;

        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);

        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    normal() {
        // Box-Muller transform with zero-input protection.
        const u1 = Math.max(this.next(), Number.MIN_VALUE);
        const u2 = this.next();

        return Math.sqrt(-2 * Math.log(u1)) *
            Math.cos(2 * Math.PI * u2);
    }
}

const Distributions = Object.freeze({
    BERNOULLI: Object.freeze({
        name: "Bernoulli(0.5)",
        mean: 0.5,
        variance: 0.25,
        sample: rng => rng.next() < 0.5 ? 1 : 0
    }),

    UNIFORM: Object.freeze({
        name: "Uniform(0,1)",
        mean: 0.5,
        variance: 1 / 12,
        sample: rng => rng.next()
    }),

    NORMAL: Object.freeze({
        name: "Normal(0,1)",
        mean: 0,
        variance: 1,
        sample: rng => rng.normal()
    })
});

function validateConfig(config) {
    if (!Object.values(Distributions).includes(config.distribution)) {
        throw new ValidationError("Unsupported distribution.");
    }

    if (!Array.isArray(config.sampleSizes) ||
        config.sampleSizes.length === 0) {
        throw new ValidationError("Sample sizes must be a nonempty array.");
    }

    let previous = 0;

    for (const n of config.sampleSizes) {
        if (!Number.isSafeInteger(n) || n <= previous) {
            throw new ValidationError(
                "Sample sizes must be positive, unique, and increasing."
            );
        }
        previous = n;
    }

    if (!Number.isSafeInteger(config.trials) || config.trials <= 0) {
        throw new ValidationError("Trials must be positive.");
    }

    if (!Number.isFinite(config.epsilon) || config.epsilon <= 0) {
        throw new ValidationError("Tolerance must be positive and finite.");
    }

    if (!Number.isSafeInteger(config.seed)) {
        throw new ValidationError("Seed must be a safe integer.");
    }
}

class OnlineStatistics {
    constructor() {
        this.count = 0;
        this.mean = 0;
        this.m2 = 0;
    }

    add(value) {
        if (!Number.isFinite(value)) {
            throw new ValidationError("Observation must be finite.");
        }

        this.count++;

        const delta = value - this.mean;
        this.mean += delta / this.count;
        const delta2 = value - this.mean;

        this.m2 += delta * delta2;
    }

    get variance() {
        return this.count > 1 ? this.m2 / (this.count - 1) : 0;
    }
}

class MonteCarloEngine extends EventEmitter {
    constructor() {
        super();
        this.activeExperiments = new Map();
    }

    async runWeakLaw(config) {
        validateConfig(config);

        const id = randomUUID();
        const controller = new AbortController();

        this.activeExperiments.set(id, controller);

        const distribution = config.distribution;
        const rng = new SeededRandom(config.seed);
        const results = [];

        this.emit("started", {
            id,
            distribution: distribution.name
        });

        try {
            for (const n of config.sampleSizes) {
                if (controller.signal.aborted) {
                    throw new Error("Experiment cancelled.");
                }

                const errors = new OnlineStatistics();
                const squaredErrors = new OnlineStatistics();
                let deviations = 0;

                for (let trial = 0; trial < config.trials; trial++) {
                    let sum = 0;

                    for (let i = 0; i < n; i++) {
                        sum += distribution.sample(rng);
                    }

                    const error = Math.abs(
                        sum / n - distribution.mean
                    );

                    errors.add(error);
                    squaredErrors.add(error * error);

                    if (error >= config.epsilon) {
                        deviations++;
                    }
                }

                const result = Object.freeze({
                    sampleSize: n,
                    trials: config.trials,
                    meanAbsoluteError: errors.mean,
                    meanSquaredError: squaredErrors.mean,
                    observedProbability: deviations / config.trials,
                    chebyshevBound: Math.min(
                        1,
                        distribution.variance /
                        (n * config.epsilon ** 2)
                    )
                });

                results.push(result);

                this.emit("sample-completed", {
                    id,
                    result
                });

                // Yield to the event loop between sample-size groups.
                await new Promise(resolve => setImmediate(resolve));
            }

            const report = Object.freeze({
                experimentId: id,
                law: "Weak Law of Large Numbers",
                distribution: distribution.name,
                populationMean: distribution.mean,
                populationVariance: distribution.variance,
                epsilon: config.epsilon,
                results
            });

            this.emit("completed", report);
            return report;
        } catch (error) {
            this.emit("failed", {
                id,
                message: error.message
            });
            throw error;
        } finally {
            this.activeExperiments.delete(id);
        }
    }

    cancelExperiment(id) {
        const controller = this.activeExperiments.get(id);

        if (!controller) {
            return false;
        }

        controller.abort();
        return true;
    }
}

function runStrongLaw(distribution, sampleSizes, seed) {
    const rng = new SeededRandom(seed);
    const checkpoints = new Set(sampleSizes);
    const maximum = Math.max(...sampleSizes);

    let sum = 0;
    const observations = [];

    for (let n = 1; n <= maximum; n++) {
        sum += distribution.sample(rng);

        if (checkpoints.has(n)) {
            const sampleMean = sum / n;

            observations.push({
                sampleSize: n,
                sampleMean,
                populationMean: distribution.mean,
                absoluteError: Math.abs(
                    sampleMean - distribution.mean
                )
            });
        }
    }

    return {
        law: "Strong Law of Large Numbers",
        distribution: distribution.name,
        observations
    };
}

async function saveReport(report, filename) {
    const destination = path.resolve(filename);
    const temporary = `${destination}.${randomUUID()}.tmp`;

    try {
        await fs.writeFile(
            temporary,
            JSON.stringify(report, null, 2),
            {
                encoding: "utf8",
                flag: "wx",
                mode: 0o600
            }
        );

        await fs.rename(temporary, destination);
    } catch (error) {
        await fs.rm(temporary, { force: true }).catch(() => {});
        throw error;
    }
}

async function main() {
    const config = {
        distribution: Distributions.BERNOULLI,
        sampleSizes: [10, 50, 100, 500, 1000, 5000, 10000],
        trials: 1000,
        epsilon: 0.05,
        seed: 42
    };

    const engine = new MonteCarloEngine();

    engine.on("started", event => {
        console.log(`Started experiment ${event.id}`);
        console.log(`Distribution: ${event.distribution}`);
    });

    engine.on("sample-completed", event => {
        const r = event.result;

        console.log(
            `N=${String(r.sampleSize).padStart(6)} ` +
            `MAE=${r.meanAbsoluteError.toFixed(6)} ` +
            `P=${r.observedProbability.toFixed(6)} ` +
            `Bound=${r.chebyshevBound.toFixed(6)}`
        );
    });

    engine.on("failed", event => {
        console.error(`Experiment ${event.id} failed: ${event.message}`);
    });

    const weakLaw = await engine.runWeakLaw(config);

    const strongLaw = runStrongLaw(
        config.distribution,
        config.sampleSizes,
        config.seed + 100
    );

    console.log("\nSTRONG LAW OBSERVATIONS");

    for (const row of strongLaw.observations) {
        console.log(
            `N=${row.sampleSize} ` +
            `Mean=${row.sampleMean.toFixed(6)} ` +
            `Error=${row.absoluteError.toFixed(6)}`
        );
    }

    const comparison = {};

    for (const [key, distribution] of Object.entries(Distributions)) {
        if (distribution === config.distribution) {
            comparison[key] = weakLaw;
            continue;
        }

        comparison[key] = await engine.runWeakLaw({
            ...config,
            distribution,
            seed: config.seed + key.length
        });
    }

    const report = {
        generatedAt: new Date().toISOString(),
        weakLaw,
        strongLaw,
        comparison
    };

    await saveReport(report, "lln_results_js.json");

    console.log("\nReport saved to lln_results_js.json");
}

main().catch(error => {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
});
