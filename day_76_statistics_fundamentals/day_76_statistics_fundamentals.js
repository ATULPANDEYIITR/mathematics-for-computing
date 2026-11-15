"use strict";

/*
 * Statistics Fundamentals
 *
 * Event-driven statistical sampling and analysis engine.
 * Demonstrates:
 * - Population and sample distinctions
 * - Parameters and statistics
 * - Descriptive statistics
 * - Reproducible sampling
 * - Stratified and systematic sampling
 * - Sampling distribution simulation
 * - Confidence intervals
 * - Sample-size determination
 * - Asynchronous processing and event auditing
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only
 */

const fs = require("node:fs/promises");
const { EventEmitter } = require("node:events");

// ============================================================
// 1. VALIDATION
// ============================================================

function validateNumber(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new TypeError(`${name} must be a finite number.`);
    }
}

function validateObservations(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new Error("Observations must be a non-empty array.");
    }

    values.forEach((value, index) => {
        validateNumber(value, `Observation ${index}`);
    });
}

function validateSampleSize(n, N) {
    if (!Number.isInteger(n) || n < 1 || n > N) {
        throw new RangeError("Sample size must be between 1 and N.");
    }
}

// ============================================================
// 2. REPRODUCIBLE RANDOM NUMBER GENERATOR
// ============================================================

class RandomGenerator {
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        // Mulberry32 provides reproducible pseudorandom values.
        let t = this.state += 0x6D2B79F5;

        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);

        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    integer(maxExclusive) {
        if (!Number.isInteger(maxExclusive) || maxExclusive <= 0) {
            throw new RangeError("Maximum must be positive.");
        }

        return Math.floor(this.next() * maxExclusive);
    }

    shuffle(items) {
        const result = [...items];

        for (let i = result.length - 1; i > 0; i--) {
            const j = this.integer(i + 1);
            [result[i], result[j]] = [result[j], result[i]];
        }

        return result;
    }
}

// ============================================================
// 3. POPULATION MODEL
// ============================================================

class Population {
    #units;
    #unitMap;

    constructor(units) {
        if (!Array.isArray(units) || units.length === 0) {
            throw new Error("Population cannot be empty.");
        }

        this.#unitMap = new Map();

        for (const unit of units) {
            if (
                !unit.id ||
                !unit.stratum ||
                !unit.cluster
            ) {
                throw new Error("Every unit requires an ID, stratum and cluster.");
            }

            validateNumber(unit.value, "Population value");

            if (this.#unitMap.has(unit.id)) {
                throw new Error(`Duplicate population ID: ${unit.id}`);
            }

            this.#unitMap.set(
                unit.id,
                Object.freeze({ ...unit })
            );
        }

        this.#units = Object.freeze([...this.#unitMap.values()]);
    }

    get size() {
        return this.#units.length;
    }

    get units() {
        return this.#units;
    }

    get values() {
        return this.#units.map(unit => unit.value);
    }

    groupBy(field) {
        if (!["stratum", "cluster"].includes(field)) {
            throw new Error("Unsupported grouping field.");
        }

        const groups = new Map();

        for (const unit of this.#units) {
            const key = unit[field];

            if (!groups.has(key)) {
                groups.set(key, []);
            }

            groups.get(key).push(unit);
        }

        return groups;
    }

    parameters() {
        const values = this.values;

        return Object.freeze({
            populationSize: this.size,
            populationMean: Statistics.mean(values),
            populationVariance: Statistics.variance(values, false),
            populationStandardDeviation: Statistics.std(values, false),
            populationTotal: values.reduce((a, b) => a + b, 0)
        });
    }
}

// ============================================================
// 4. STATISTICAL OPERATIONS
// ============================================================

class Statistics {
    static mean(values) {
        validateObservations(values);

        // Compensated summation reduces floating-point error.
        let sum = 0;
        let correction = 0;

        for (const value of values) {
            const adjusted = value - correction;
            const next = sum + adjusted;
            correction = (next - sum) - adjusted;
            sum = next;
        }

        return sum / values.length;
    }

    static median(values) {
        validateObservations(values);

        const sorted = [...values].sort((a, b) => a - b);
        const middle = Math.floor(sorted.length / 2);

        return sorted.length % 2
            ? sorted[middle]
            : (sorted[middle - 1] + sorted[middle]) / 2;
    }

    static variance(values, sample = true) {
        validateObservations(values);

        if (sample && values.length < 2) {
            throw new Error("Sample variance requires at least two values.");
        }

        const mean = this.mean(values);
        const denominator = sample
            ? values.length - 1
            : values.length;

        return values.reduce(
            (total, value) => total + (value - mean) ** 2,
            0
        ) / denominator;
    }

    static std(values, sample = true) {
        return Math.sqrt(this.variance(values, sample));
    }

    static quantile(values, probability) {
        validateObservations(values);

        if (probability < 0 || probability > 1) {
            throw new RangeError("Probability must be between 0 and 1.");
        }

        const sorted = [...values].sort((a, b) => a - b);
        const position = (sorted.length - 1) * probability;
        const lower = Math.floor(position);
        const upper = Math.ceil(position);

        return sorted[lower] +
            (sorted[upper] - sorted[lower]) * (position - lower);
    }

    static describe(values) {
        validateObservations(values);

        return Object.freeze({
            count: values.length,
            mean: this.mean(values),
            median: this.median(values),
            variance: this.variance(values, values.length > 1),
            minimum: Math.min(...values),
            maximum: Math.max(...values),
            standardDeviation: this.std(values, values.length > 1)
        });
    }
}

// ============================================================
// 5. SAMPLING SERVICE
// ============================================================

class SamplingService {
    constructor(population, seed = 42) {
        this.population = population;
        this.random = new RandomGenerator(seed);
        this.seed = seed;
    }

    createSample(units, method) {
        const ids = new Set();

        for (const unit of units) {
            if (ids.has(unit.id)) {
                throw new Error("Duplicate unit in selected sample.");
            }

            ids.add(unit.id);
        }

        return Object.freeze({
            method,
            seed: this.seed,
            populationSize: this.population.size,
            size: units.length,
            units: Object.freeze([...units])
        });
    }

    simpleRandom(n) {
        validateSampleSize(n, this.population.size);

        return this.createSample(
            this.random.shuffle(this.population.units).slice(0, n),
            "simple_random"
        );
    }

    systematic(n) {
        validateSampleSize(n, this.population.size);

        const units = this.population.units;

        if (n === units.length) {
            return this.createSample(units, "systematic");
        }

        const interval = units.length / n;
        const start = this.random.next() * interval;

        const selected = Array.from(
            { length: n },
            (_, i) => units[Math.min(
                Math.floor(start + i * interval),
                units.length - 1
            )]
        );

        return this.createSample(selected, "systematic");
    }

    stratified(n) {
        validateSampleSize(n, this.population.size);

        const strata = this.population.groupBy("stratum");
        const groups = [...strata.entries()];

        if (n < groups.length) {
            throw new Error("Sample must cover every stratum.");
        }

        const allocations = groups.map(([name, units]) => ({
            name,
            units,
            exact: n * units.length / this.population.size,
            count: Math.floor(n * units.length / this.population.size)
        }));

        let remaining = n - allocations.reduce(
            (total, item) => total + item.count,
            0
        );

        allocations.sort(
            (a, b) =>
                (b.exact - b.count) - (a.exact - a.count)
        );

        for (const allocation of allocations) {
            if (remaining === 0) break;

            if (allocation.count < allocation.units.length) {
                allocation.count++;
                remaining--;
            }
        }

        if (remaining !== 0) {
            throw new Error("Stratified allocation failed.");
        }

        const selected = allocations.flatMap(item =>
            this.random.shuffle(item.units).slice(0, item.count)
        );

        return this.createSample(selected, "stratified");
    }
}

// ============================================================
// 6. INFERENCE
// ============================================================

class Inference {
    static standardError(sample, finiteCorrection = true) {
        const values = sample.units.map(unit => unit.value);
        const n = values.length;

        if (n < 2) {
            throw new Error("At least two observations are required.");
        }

        let se = Statistics.std(values, true) / Math.sqrt(n);

        if (finiteCorrection && n < sample.populationSize) {
            se *= Math.sqrt(
                (sample.populationSize - n) /
                (sample.populationSize - 1)
            );
        }

        return se;
    }

    static confidenceInterval(sample, confidence = 0.95) {
        const criticalValues = new Map([
            [0.90, 1.645],
            [0.95, 1.960],
            [0.99, 2.576]
        ]);

        if (!criticalValues.has(confidence)) {
            throw new Error("Unsupported confidence level.");
        }

        const values = sample.units.map(unit => unit.value);
        const se = this.standardError(sample);

        const mean = Statistics.mean(values);
        const margin = criticalValues.get(confidence) * se;

        return Object.freeze({
            mean,
            lower: mean - margin,
            upper: mean + margin,
            confidence,
            standardError: se
        });
    }

    static requiredSampleSize({
        populationStd,
        margin,
        z = 1.96,
        populationSize = null
    }) {
        validateNumber(populationStd, "Population standard deviation");
        validateNumber(margin, "Margin");
        validateNumber(z, "Z-score");

        if (populationStd < 0 || margin <= 0 || z <= 0) {
            throw new Error("Invalid sample-size parameters.");
        }

        if (populationSize !== null &&
            (!Number.isInteger(populationSize) || populationSize <= 0)) {
            throw new Error("Population size must be a positive integer.");
        }

        if (populationStd === 0) return 1;

        const n0 = (z * populationStd / margin) ** 2;

        if (populationSize === null) {
            return Math.ceil(n0);
        }

        const adjusted = n0 >= populationSize
            ? populationSize
            : n0 / (1 + (n0 - 1) / populationSize);

        return Math.min(populationSize, Math.ceil(adjusted));
    }
}

// ============================================================
// 7. EVENT-DRIVEN SAMPLING PIPELINE
// ============================================================

class SamplingPipeline extends EventEmitter {
    constructor(population, service) {
        super();

        this.population = population;
        this.service = service;
        this.history = [];
        this.processing = false;
    }

    async execute(method, size) {
        if (this.processing) {
            throw new Error("A sampling operation is already running.");
        }

        this.processing = true;

        try {
            this.emit("sampling:started", { method, size });

            // Yield to the Node.js event loop before processing.
            await new Promise(resolve => setImmediate(resolve));

            if (typeof this.service[method] !== "function") {
                throw new Error("Unsupported sampling method.");
            }

            const sample = this.service[method](size);
            const statistics = Statistics.describe(
                sample.units.map(unit => unit.value)
            );

            const result = Object.freeze({
                sample,
                statistics
            });

            this.history.push({
                method,
                size: sample.size,
                completedAt: new Date().toISOString()
            });

            this.emit("sampling:completed", result);

            return result;
        } catch (error) {
            this.emit("sampling:failed", {
                method,
                message: error.message
            });

            throw error;
        } finally {
            this.processing = false;
        }
    }
}

// ============================================================
// 8. SAMPLING DISTRIBUTION SIMULATION
// ============================================================

async function simulateSamplingDistribution(
    population,
    sampleSize,
    repetitions = 1000
) {
    if (!Number.isInteger(repetitions) || repetitions < 100) {
        throw new RangeError("At least 100 repetitions are required.");
    }

    const estimates = [];

    for (let i = 0; i < repetitions; i++) {
        const engine = new SamplingService(population, i + 1);
        const sample = engine.simpleRandom(sampleSize);

        estimates.push(
            Statistics.mean(sample.units.map(unit => unit.value))
        );

        if (i % 100 === 0) {
            await new Promise(resolve => setImmediate(resolve));
        }
    }

    return Object.freeze({
        repetitions,
        samplingDistributionMean: Statistics.mean(estimates),
        samplingDistributionStd: Statistics.std(estimates, true),
        estimates
    });
}

// ============================================================
// 9. APPLICATION
// ============================================================

function buildPopulation() {
    const departments = ["Technology", "Mathematics", "Physics"];
    const units = [];

    departments.forEach((department, group) => {
        for (let i = 1; i <= 30; i++) {
            units.push({
                id: `${group + 1}-${String(i).padStart(3, "0")}`,
                value: 50 + group * 10 + i * 0.8 + (i % 5) * 2,
                stratum: department,
                cluster: `CLASS-${Math.ceil(i / 10)}`
            });
        }
    });

    return new Population(units);
}

async function main() {
    const population = buildPopulation();

    const samplingService = new SamplingService(population, 42);
    const pipeline = new SamplingPipeline(population, samplingService);

    pipeline.on("sampling:started", event => {
        process.stdout.write(
            `Starting ${event.method}, n=${event.size}\n`
        );
    });

    pipeline.on("sampling:completed", result => {
        process.stdout.write(
            `Completed: sample mean = ${result.statistics.mean.toFixed(3)}\n`
        );
    });

    pipeline.on("sampling:failed", error => {
        process.stderr.write(`Sampling failed: ${error.message}\n`);
    });

    console.log("\nPOPULATION PARAMETERS");
    console.log(population.parameters());

    const results = {};

    for (const method of [
        "simpleRandom",
        "systematic",
        "stratified"
    ]) {
        const result = await pipeline.execute(method, 20);

        results[method] = {
            statistics: result.statistics,
            sampleIds: result.sample.units.map(unit => unit.id)
        };

        if (method === "simpleRandom") {
            results.confidenceInterval =
                Inference.confidenceInterval(result.sample);
        }
    }

    const distribution = await simulateSamplingDistribution(
        population,
        20,
        1000
    );

    results.samplingDistribution = {
        repetitions: distribution.repetitions,
        mean: distribution.samplingDistributionMean,
        standardDeviation: distribution.samplingDistributionStd
    };

    results.requiredSampleSize = Inference.requiredSampleSize({
        populationStd: 15,
        margin: 3,
        z: 1.96,
        populationSize: population.size
    });

    // Atomic replacement avoids leaving a partially written report.
    const temporaryPath = "statistics_report.json.tmp";
    const finalPath = "statistics_report.json";

    await fs.writeFile(
        temporaryPath,
        JSON.stringify({
            population: population.parameters(),
            results,
            audit: pipeline.history
        }, null, 2),
        { encoding: "utf8", mode: 0o600 }
    );

    await fs.rename(temporaryPath, finalPath);

    console.log("\nSAMPLE SIZE:", results.requiredSampleSize);
    console.log("\nSAMPLING DISTRIBUTION:", results.samplingDistribution);
    console.log("\nReport written to:", finalPath);

    // Validate an invalid sample size.
    try {
        samplingService.simpleRandom(population.size + 1);
    } catch (error) {
        console.log("Expected validation:", error.message);
    }
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
