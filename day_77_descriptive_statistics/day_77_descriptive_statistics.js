"use strict";

/*
 * Descriptive Statistics Engine
 *
 * Implements:
 * - Event-driven observation ingestion
 * - Mean, median and multimodal mode
 * - Population and sample variance
 * - Standard deviation
 * - Quantiles and percentiles
 * - Interquartile range
 * - Outlier detection
 * - Frequency distributions
 * - Streaming Welford calculations
 * - Asynchronous CSV processing
 * - JSON report generation
 *
 * Runtime: Node.js 18+
 *
 * Run:
 * node descriptive_statistics.js
 * node descriptive_statistics.js measurements.csv
 */

const fs = require("node:fs");
const readline = require("node:readline");
const { EventEmitter } = require("node:events");

class StatisticsError extends Error {
    constructor(message) {
        super(message);
        this.name = "StatisticsError";
    }
}

const VarianceType = Object.freeze({
    POPULATION: "population",
    SAMPLE: "sample"
});

function validateNumber(value) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new StatisticsError(
            `Invalid numeric observation: ${value}`
        );
    }

    return value;
}

function interpolate(sorted, probability) {
    if (
        !Number.isFinite(probability) ||
        probability < 0 ||
        probability > 1
    ) {
        throw new StatisticsError(
            "Probability must be between 0 and 1."
        );
    }

    const position = (sorted.length - 1) * probability;
    const lower = Math.floor(position);
    const upper = Math.ceil(position);

    if (lower === upper) {
        return sorted[lower];
    }

    const fraction = position - lower;

    return sorted[lower] * (1 - fraction)
        + sorted[upper] * fraction;
}

class StatisticsEngine extends EventEmitter {
    #observations = [];
    #frequencies = new Map();

    #count = 0;
    #mean = 0;
    #m2 = 0;
    #minimum = Infinity;
    #maximum = -Infinity;

    constructor(name, options = {}) {
        super();

        if (typeof name !== "string" || !name.trim()) {
            throw new StatisticsError(
                "Dataset name must be a non-empty string."
            );
        }

        this.name = name;
        this.maxObservations = options.maxObservations ?? 1_000_000;

        if (
            !Number.isSafeInteger(this.maxObservations) ||
            this.maxObservations < 1
        ) {
            throw new StatisticsError(
                "Invalid maximum observation count."
            );
        }
    }

    add(value) {
        validateNumber(value);

        if (this.#count >= this.maxObservations) {
            throw new StatisticsError(
                "Maximum observation limit reached."
            );
        }

        // Welford's algorithm updates mean and squared deviations
        // without repeatedly summing large squared values.
        this.#count++;

        const delta = value - this.#mean;
        this.#mean += delta / this.#count;

        const delta2 = value - this.#mean;
        this.#m2 += delta * delta2;

        this.#minimum = Math.min(this.#minimum, value);
        this.#maximum = Math.max(this.#maximum, value);

        this.#observations.push(value);

        this.#frequencies.set(
            value,
            (this.#frequencies.get(value) || 0) + 1
        );

        this.emit("observation", {
            value,
            count: this.#count,
            runningMean: this.#mean
        });

        return this;
    }

    addBatch(values) {
        if (!Array.isArray(values)) {
            throw new StatisticsError(
                "Batch input must be an array."
            );
        }

        // Validate the entire batch before changing state.
        const validated = values.map(validateNumber);

        if (
            this.#count + validated.length >
            this.maxObservations
        ) {
            throw new StatisticsError(
                "Batch exceeds maximum observation count."
            );
        }

        for (const value of validated) {
            this.add(value);
        }

        return this;
    }

    #requireData() {
        if (this.#count === 0) {
            throw new StatisticsError(
                "No observations available."
            );
        }
    }

    get count() {
        return this.#count;
    }

    get mean() {
        this.#requireData();
        return this.#mean;
    }

    get median() {
        this.#requireData();

        const sorted = [...this.#observations].sort(
            (a, b) => a - b
        );

        const middle = Math.floor(sorted.length / 2);

        return sorted.length % 2
            ? sorted[middle]
            : (sorted[middle - 1] + sorted[middle]) / 2;
    }

    get mode() {
        this.#requireData();

        let maximum = 0;
        const modes = [];

        for (const [value, frequency] of this.#frequencies) {
            if (frequency > maximum) {
                maximum = frequency;
                modes.length = 0;
                modes.push(value);
            } else if (frequency === maximum) {
                modes.push(value);
            }
        }

        return maximum === 1 ? [] : modes.sort((a, b) => a - b);
    }

    variance(type = VarianceType.POPULATION) {
        this.#requireData();

        if (
            type !== VarianceType.POPULATION &&
            type !== VarianceType.SAMPLE
        ) {
            throw new StatisticsError(
                "Unknown variance type."
            );
        }

        const denominator =
            type === VarianceType.SAMPLE
                ? this.#count - 1
                : this.#count;

        if (denominator <= 0) {
            throw new StatisticsError(
                "Sample variance requires at least two observations."
            );
        }

        return this.#m2 / denominator;
    }

    standardDeviation(type = VarianceType.POPULATION) {
        return Math.sqrt(this.variance(type));
    }

    quantile(probability) {
        this.#requireData();

        const sorted = [...this.#observations].sort(
            (a, b) => a - b
        );

        return interpolate(sorted, probability);
    }

    percentile(percentage) {
        if (
            !Number.isFinite(percentage) ||
            percentage < 0 ||
            percentage > 100
        ) {
            throw new StatisticsError(
                "Percentage must be between 0 and 100."
            );
        }

        return this.quantile(percentage / 100);
    }

    get quartiles() {
        return {
            q1: this.quantile(0.25),
            q2: this.quantile(0.50),
            q3: this.quantile(0.75)
        };
    }

    get interquartileRange() {
        return this.quantile(0.75) - this.quantile(0.25);
    }

    outliers(multiplier = 1.5) {
        if (
            !Number.isFinite(multiplier) ||
            multiplier < 0
        ) {
            throw new StatisticsError(
                "Invalid outlier multiplier."
            );
        }

        const q1 = this.quantile(0.25);
        const q3 = this.quantile(0.75);
        const iqr = q3 - q1;

        const lower = q1 - multiplier * iqr;
        const upper = q3 + multiplier * iqr;

        return this.#observations.filter(
            value => value < lower || value > upper
        );
    }

    get frequencyDistribution() {
        return Object.fromEntries(
            [...this.#frequencies.entries()]
                .sort((a, b) => a[0] - b[0])
        );
    }

    get minimum() {
        this.#requireData();
        return this.#minimum;
    }

    get maximum() {
        this.#requireData();
        return this.#maximum;
    }

    report() {
        this.#requireData();

        return {
            dataset: this.name,
            count: this.count,
            minimum: this.minimum,
            maximum: this.maximum,
            range: this.maximum - this.minimum,
            mean: this.mean,
            median: this.median,
            mode: this.mode,
            populationVariance: this.variance(),
            sampleVariance: this.count > 1
                ? this.variance(VarianceType.SAMPLE)
                : null,
            populationStandardDeviation:
                this.standardDeviation(),
            sampleStandardDeviation: this.count > 1
                ? this.standardDeviation(VarianceType.SAMPLE)
                : null,
            quartiles: this.quartiles,
            interquartileRange: this.interquartileRange,
            percentiles: {
                p10: this.percentile(10),
                p25: this.percentile(25),
                p50: this.percentile(50),
                p75: this.percentile(75),
                p90: this.percentile(90),
                p95: this.percentile(95)
            },
            outliers: this.outliers(),
            frequencyDistribution: this.frequencyDistribution
        };
    }
}

async function importCSV(filepath, columnIndex = 0) {
    const input = fs.createReadStream(filepath, {
        encoding: "utf8"
    });

    const reader = readline.createInterface({
        input,
        crlfDelay: Infinity
    });

    let headerSkipped = false;
    let lineNumber = 0;

    const values = [];

    try {
        for await (const line of reader) {
            lineNumber++;

            if (!headerSkipped) {
                headerSkipped = true;
                continue;
            }

            if (!line.trim()) {
                continue;
            }

            const fields = line.split(",");
            const raw = fields[columnIndex]?.trim();

            if (!raw) {
                throw new StatisticsError(
                    `Missing value at line ${lineNumber}.`
                );
            }

            const value = Number(raw);

            validateNumber(value);
            values.push(value);
        }
    } catch (error) {
        reader.close();
        input.destroy();
        throw error;
    }

    return values;
}

async function main() {
    const filepath = process.argv[2];

    let observations;

    if (filepath) {
        observations = await importCSV(filepath, 0);
    } else {
        observations = [
            12, 15, 18, 20, 15, 22, 25, 18,
            30, 35, 18, 40, 45, 50, 55, 60
        ];
    }

    const engine = new StatisticsEngine(
        "Operational Performance Measurements",
        { maxObservations: 100_000 }
    );

    engine.on("observation", event => {
        if (event.count % 5 === 0) {
            console.log(
                `Processed ${event.count} observations; ` +
                `running mean: ${event.runningMean.toFixed(2)}`
            );
        }
    });

    // Batch validation occurs before the dataset is modified.
    engine.addBatch(observations);

    const result = engine.report();

    console.log("\nDescriptive Statistics Report");
    console.log(JSON.stringify(result, null, 2));

    fs.writeFileSync(
        "statistics_report.json",
        JSON.stringify(result, null, 2),
        { encoding: "utf8", flag: "w" }
    );

    console.log("\nReport saved to statistics_report.json");

    // Edge-case validation.
    const single = new StatisticsEngine("Single Observation");
    single.add(25);

    console.log("Single observation mean:", single.mean);

    try {
        single.variance(VarianceType.SAMPLE);
    } catch (error) {
        console.log("Expected validation:", error.message);
    }
}

main().catch(error => {
    console.error("Analysis failed:", error.message);
    process.exitCode = 1;
});
