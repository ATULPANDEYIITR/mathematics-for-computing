"use strict";

/*
 * Central Limit Theorem: Event-Driven Sampling Simulation
 *
 * Features:
 * - Multiple population distributions
 * - Seeded pseudo-random number generation
 * - Streaming sample-mean calculations
 * - Welford online variance estimation
 * - Batch-based asynchronous Monte Carlo execution
 * - Normal approximation diagnostics
 * - Confidence interval evaluation
 * - Bootstrap approximation
 * - EventEmitter-based simulation monitoring
 * - JSON reporting using Node.js standard libraries
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");

const OUTPUT_DIR = path.join(process.cwd(), "clt_js_results");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class SeededRandom {
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        this.state = (
            Math.imul(1664525, this.state) + 1013904223
        ) >>> 0;

        return this.state / 4294967296;
    }

    exponential(rate = 1) {
        if (!(rate > 0)) {
            throw new ValidationError("Rate must be positive.");
        }

        return -Math.log(1 - this.next()) / rate;
    }

    normal() {
        const u1 = Math.max(this.next(), Number.MIN_VALUE);
        const u2 = this.next();

        return Math.sqrt(-2 * Math.log(u1)) *
            Math.cos(2 * Math.PI * u2);
    }

    integer(max) {
        return Math.floor(this.next() * max);
    }
}

class Population {
    constructor(name, generator, size = 10000, seed = 42) {
        if (!name || typeof generator !== "function") {
            throw new ValidationError("Invalid population definition.");
        }

        if (!Number.isInteger(size) || size < 2) {
            throw new ValidationError("Population size must be >= 2.");
        }

        const rng = new SeededRandom(seed);

        this.name = name;
        this.values = Array.from(
            { length: size },
            () => generator(rng)
        );

        if (this.values.some(x => !Number.isFinite(x))) {
            throw new ValidationError("Population contains invalid values.");
        }

        this.mean = this.values.reduce((a, b) => a + b, 0) / size;

        this.variance = this.values.reduce(
            (sum, x) => sum + (x - this.mean) ** 2,
            0
        ) / size;

        this.standardDeviation = Math.sqrt(this.variance);
    }
}

class OnlineStatistics {
    constructor() {
        this.count = 0;
        this.mean = 0;
        this.m2 = 0;
        this.minimum = Infinity;
        this.maximum = -Infinity;
    }

    add(value) {
        if (!Number.isFinite(value)) {
            throw new ValidationError("Statistic must be finite.");
        }

        this.count++;

        const delta = value - this.mean;
        this.mean += delta / this.count;
        this.m2 += delta * (value - this.mean);

        this.minimum = Math.min(this.minimum, value);
        this.maximum = Math.max(this.maximum, value);
    }

    get variance() {
        return this.count > 1 ? this.m2 / (this.count - 1) : 0;
    }

    get standardDeviation() {
        return Math.sqrt(this.variance);
    }
}

class SamplingEngine extends EventEmitter {
    constructor(population, seed = 42) {
        super();

        if (!(population instanceof Population)) {
            throw new ValidationError("Population object required.");
        }

        this.population = population;
        this.rng = new SeededRandom(seed);
        this.completedTrials = 0;
    }

    validate(n, repetitions) {
        if (!Number.isInteger(n) || n < 1) {
            throw new ValidationError("Sample size must be positive.");
        }

        if (!Number.isInteger(repetitions) || repetitions < 2) {
            throw new ValidationError("At least two trials are required.");
        }
    }

    sampleMean(n) {
        const values = this.population.values;
        let total = 0;

        // Sampling with replacement: every draw is independent.
        for (let i = 0; i < n; i++) {
            total += values[this.rng.integer(values.length)];
        }

        return total / n;
    }

    theoreticalStandardError(n) {
        return this.population.standardDeviation / Math.sqrt(n);
    }

    async simulate({
        sampleSize,
        repetitions = 5000,
        batchSize = 500,
        yieldEveryBatch = true
    }) {
        this.validate(sampleSize, repetitions);

        if (!Number.isInteger(batchSize) || batchSize < 1) {
            throw new ValidationError("Batch size must be positive.");
        }

        const statistics = new OnlineStatistics();
        const means = [];

        this.completedTrials = 0;

        while (this.completedTrials < repetitions) {
            const currentBatch = Math.min(
                batchSize,
                repetitions - this.completedTrials
            );

            for (let i = 0; i < currentBatch; i++) {
                const mean = this.sampleMean(sampleSize);

                means.push(mean);
                statistics.add(mean);
            }

            this.completedTrials += currentBatch;

            this.emit("progress", {
                completed: this.completedTrials,
                total: repetitions,
                percentage: 100 * this.completedTrials / repetitions
            });

            if (yieldEveryBatch) {
                await new Promise(resolve => setImmediate(resolve));
            }
        }

        const theoreticalSE = this.theoreticalStandardError(sampleSize);

        return {
            population: this.population.name,
            sampleSize,
            repetitions,
            populationMean: this.population.mean,
            populationSD: this.population.standardDeviation,
            empiricalMean: statistics.mean,
            empiricalSD: statistics.standardDeviation,
            theoreticalSE,
            relativeSEError: theoreticalSE === 0
                ? 0
                : Math.abs(
                    statistics.standardDeviation - theoreticalSE
                ) / theoreticalSE,
            samplingMeans: means
        };
    }
}

function normalCDF(x) {
    // Abramowitz-Stegun approximation.
    const sign = x < 0 ? -1 : 1;
    const z = Math.abs(x) / Math.sqrt(2);

    const t = 1 / (1 + 0.3275911 * z);

    const coefficients = [
        0.254829592,
        -0.284496736,
        1.421413741,
        -1.453152027,
        1.061405429
    ];

    let polynomial = coefficients[4];

    for (let i = 3; i >= 0; i--) {
        polynomial = polynomial * t + coefficients[i];
    }

    const erf = sign * (
        1 - polynomial * t * Math.exp(-z * z)
    );

    return 0.5 * (1 + erf);
}

function evaluateNormalApproximation(result) {
    const {
        samplingMeans,
        populationMean,
        theoreticalSE
    } = result;

    if (theoreticalSE === 0) {
        return {
            ksDistance: 0,
            interpretation: "Degenerate distribution"
        };
    }

    const ordered = [...samplingMeans].sort((a, b) => a - b);
    const n = ordered.length;
    let maximumDistance = 0;

    for (let i = 0; i < n; i++) {
        const z = (ordered[i] - populationMean) / theoreticalSE;
        const expected = normalCDF(z);

        maximumDistance = Math.max(
            maximumDistance,
            Math.abs((i + 1) / n - expected),
            Math.abs(i / n - expected)
        );
    }

    return {
        ksDistance: maximumDistance,
        interpretation: "Empirical distance from theoretical normal model"
    };
}

function confidenceInterval(mean, standardError, z = 1.96) {
    if (
        !Number.isFinite(mean) ||
        !Number.isFinite(standardError) ||
        standardError < 0 ||
        z <= 0
    ) {
        throw new ValidationError("Invalid interval parameters.");
    }

    return {
        lower: mean - z * standardError,
        upper: mean + z * standardError
    };
}

function bootstrapInterval(sample, repetitions = 2000, seed = 99) {
    if (!Array.isArray(sample) || sample.length < 2) {
        throw new ValidationError("Bootstrap needs at least two values.");
    }

    if (sample.some(x => !Number.isFinite(x))) {
        throw new ValidationError("Bootstrap data must be finite.");
    }

    if (!Number.isInteger(repetitions) || repetitions < 100) {
        throw new ValidationError("At least 100 bootstrap trials required.");
    }

    const rng = new SeededRandom(seed);
    const means = [];

    for (let i = 0; i < repetitions; i++) {
        let sum = 0;

        for (let j = 0; j < sample.length; j++) {
            sum += sample[rng.integer(sample.length)];
        }

        means.push(sum / sample.length);
    }

    means.sort((a, b) => a - b);

    return {
        lower: quantile(means, 0.025),
        upper: quantile(means, 0.975)
    };
}

function quantile(sorted, probability) {
    if (
        !Array.isArray(sorted) ||
        sorted.length === 0 ||
        probability < 0 ||
        probability > 1
    ) {
        throw new ValidationError("Invalid quantile input.");
    }

    const position = (sorted.length - 1) * probability;
    const lower = Math.floor(position);
    const fraction = position - lower;

    if (lower + 1 >= sorted.length) {
        return sorted[lower];
    }

    return sorted[lower] * (1 - fraction) +
        sorted[lower + 1] * fraction;
}

function measureCoverage(population, sampleSize, repetitions, seed = 123) {
    const rng = new SeededRandom(seed);
    let covered = 0;

    for (let i = 0; i < repetitions; i++) {
        let sum = 0;
        let sumSquares = 0;

        for (let j = 0; j < sampleSize; j++) {
            const value = population.values[
                rng.integer(population.values.length)
            ];

            sum += value;
            sumSquares += value * value;
        }

        const mean = sum / sampleSize;

        const sampleVariance = sampleSize > 1
            ? (sumSquares - sum * sum / sampleSize) /
              (sampleSize - 1)
            : 0;

        const se = Math.sqrt(sampleVariance / sampleSize);
        const interval = confidenceInterval(mean, se);

        if (
            interval.lower <= population.mean &&
            population.mean <= interval.upper
        ) {
            covered++;
        }
    }

    return covered / repetitions;
}

async function saveReport(results) {
    await fs.mkdir(OUTPUT_DIR, { recursive: true });

    const destination = path.join(
        OUTPUT_DIR,
        "sampling_distribution_report.json"
    );

    const safeResults = results.map(({ samplingMeans, ...item }) => item);

    await fs.writeFile(
        destination,
        JSON.stringify(safeResults, null, 2),
        { encoding: "utf8", flag: "w" }
    );

    console.log(`Report saved: ${destination}`);
}

async function main() {
    const populationDefinitions = [
        {
            name: "Bernoulli",
            generator: rng => rng.next() < 0.3 ? 1 : 0
        },
        {
            name: "Exponential",
            generator: rng => rng.exponential(1)
        },
        {
            name: "Uniform",
            generator: rng => rng.next() * 100
        },
        {
            name: "HighlySkewed",
            generator: rng => rng.exponential(0.5) ** 1.5
        }
    ];

    const sampleSizes = [2, 5, 10, 30, 50, 100];
    const results = [];

    for (const definition of populationDefinitions) {
        const population = new Population(
            definition.name,
            definition.generator
        );

        console.log(`\nPopulation: ${population.name}`);
        console.log(`Mean: ${population.mean.toFixed(4)}`);
        console.log(`SD: ${population.standardDeviation.toFixed(4)}`);

        for (const n of sampleSizes) {
            const engine = new SamplingEngine(population, 42 + n);

            engine.on("progress", event => {
                if (event.completed === event.total) {
                    console.log(`Completed ${event.total} trials.`);
                }
            });

            const result = await engine.simulate({
                sampleSize: n,
                repetitions: 3000,
                batchSize: 500
            });

            const diagnostics = evaluateNormalApproximation(result);

            const coverage = measureCoverage(
                population, n, 1000, 100 + n
            );

            const record = {
                population: result.population,
                sampleSize: n,
                repetitions: result.repetitions,
                empiricalMean: result.empiricalMean,
                theoreticalMean: result.populationMean,
                empiricalSD: result.empiricalSD,
                theoreticalSE: result.theoreticalSE,
                relativeSEError: result.relativeSEError,
                ksDistance: diagnostics.ksDistance,
                confidenceIntervalCoverage: coverage
            };

            results.push(record);

            console.log(
                `n=${n} | ` +
                `Empirical SE=${result.empiricalSD.toFixed(4)} | ` +
                `Theoretical SE=${result.theoreticalSE.toFixed(4)} | ` +
                `KS=${diagnostics.ksDistance.toFixed(4)} | ` +
                `Coverage=${coverage.toFixed(3)}`
            );
        }
    }

    const examplePopulation = new Population(
        "BootstrapExample",
        rng => rng.exponential(1),
        1000,
        77
    );

    const observedSample = Array.from(
        { length: 50 },
        () => examplePopulation.values[
            Math.floor(Math.random() * examplePopulation.values.length)
        ]
    );

    console.log("\nBootstrap percentile interval:");
    console.log(bootstrapInterval(observedSample));

    await saveReport(results);
}

function runTests() {
    const rng = new SeededRandom(42);

    console.assert(rng.next() >= 0 && rng.next() < 1);

    console.assert(Math.abs(normalCDF(0) - 0.5) < 0.001);

    const stats = new OnlineStatistics();
    [1, 2, 3, 4, 5].forEach(x => stats.add(x));

    console.assert(Math.abs(stats.mean - 3) < 1e-10);
    console.assert(Math.abs(stats.variance - 2.5) < 1e-10);

    const interval = confidenceInterval(100, 5);

    console.assert(interval.lower < 100);
    console.assert(interval.upper > 100);

    let rejected = false;

    try {
        new Population("invalid", () => NaN);
    } catch (error) {
        rejected = error instanceof ValidationError;
    }

    console.assert(rejected);
}

runTests();

main().catch(error => {
    console.error("Simulation failed:", error.message);
    process.exitCode = 1;
});
