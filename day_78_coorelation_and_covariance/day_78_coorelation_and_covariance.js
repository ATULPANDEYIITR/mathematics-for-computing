"use strict";

/*
 * Correlation and Covariance Analysis Engine
 *
 * Node.js 18+
 *
 * Features:
 * - Pearson correlation
 * - Sample and population covariance
 * - Covariance and correlation matrices
 * - Event-driven statistical analysis
 * - Asynchronous dataset processing
 * - Missing-value policies
 * - Correlation threshold monitoring
 * - Dataset validation
 * - Analysis snapshots
 *
 * No third-party dependencies.
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class StatisticalError extends Error {
    constructor(message) {
        super(message);
        this.name = "StatisticalError";
    }
}

class ValidationError extends StatisticalError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class InsufficientDataError extends StatisticalError {
    constructor(message) {
        super(message);
        this.name = "InsufficientDataError";
    }
}

const MissingPolicy = Object.freeze({
    REJECT: "reject",
    PAIRWISE: "pairwise",
    LISTWISE: "listwise"
});

function validateNumber(value, label) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value)
    ) {
        throw new ValidationError(
            `${label} must be a finite number.`
        );
    }
}

function compensatedSum(values) {
    // Neumaier summation reduces floating-point accumulation error.
    let sum = 0;
    let correction = 0;

    for (const value of values) {
        const next = sum + value;

        if (Math.abs(sum) >= Math.abs(value)) {
            correction += (sum - next) + value;
        } else {
            correction += (value - next) + sum;
        }

        sum = next;
    }

    return sum + correction;
}

function mean(values) {
    if (values.length === 0) {
        throw new InsufficientDataError(
            "Cannot calculate the mean of an empty array."
        );
    }

    return compensatedSum(values) / values.length;
}

function variance(values, sample = true) {
    const minimum = sample ? 2 : 1;

    if (values.length < minimum) {
        throw new InsufficientDataError(
            `At least ${minimum} observations are required.`
        );
    }

    const average = mean(values);

    const squared = values.map(
        value => (value - average) ** 2
    );

    return compensatedSum(squared) /
        (values.length - (sample ? 1 : 0));
}

function covariance(x, y, sample = true) {
    if (x.length !== y.length) {
        throw new ValidationError(
            "Observation counts must match."
        );
    }

    const minimum = sample ? 2 : 1;

    if (x.length < minimum) {
        throw new InsufficientDataError(
            "Insufficient paired observations."
        );
    }

    const mx = mean(x);
    const my = mean(y);

    const products = x.map(
        (value, index) =>
            (value - mx) * (y[index] - my)
    );

    return compensatedSum(products) /
        (x.length - (sample ? 1 : 0));
}

function pearson(x, y) {
    if (x.length !== y.length || x.length < 2) {
        throw new ValidationError(
            "Pearson correlation requires at least two matched observations."
        );
    }

    const mx = mean(x);
    const my = mean(y);

    const dx = x.map(value => value - mx);
    const dy = y.map(value => value - my);

    const numerator = compensatedSum(
        dx.map((value, index) => value * dy[index])
    );

    const sumXX = compensatedSum(dx.map(v => v * v));
    const sumYY = compensatedSum(dy.map(v => v * v));

    if (sumXX === 0 || sumYY === 0) {
        throw new ValidationError(
            "Correlation is undefined for constant variables."
        );
    }

    return Math.max(
        -1,
        Math.min(
            1,
            numerator / Math.sqrt(sumXX * sumYY)
        )
    );
}

function correlationStrength(value) {
    const magnitude = Math.abs(value);

    if (magnitude >= 0.90) return "Very strong";
    if (magnitude >= 0.70) return "Strong";
    if (magnitude >= 0.40) return "Moderate";
    if (magnitude >= 0.20) return "Weak";

    return "Negligible";
}

class Dataset {
    constructor(name, columns) {
        if (
            typeof name !== "string" ||
            name.trim().length === 0
        ) {
            throw new ValidationError(
                "Dataset name is required."
            );
        }

        if (
            !columns ||
            typeof columns !== "object" ||
            Array.isArray(columns)
        ) {
            throw new ValidationError(
                "Columns must be an object."
            );
        }

        const entries = Object.entries(columns);

        if (entries.length < 2) {
            throw new ValidationError(
                "At least two variables are required."
            );
        }

        const lengths = new Set();

        for (const [name, values] of entries) {
            if (!name.trim() || !Array.isArray(values)) {
                throw new ValidationError(
                    "Each variable must have a name and an array."
                );
            }

            lengths.add(values.length);

            for (const value of values) {
                if (value !== null && value !== undefined) {
                    validateNumber(value, name);
                }
            }
        }

        if (lengths.size !== 1) {
            throw new ValidationError(
                "All variable arrays must have equal lengths."
            );
        }

        if (entries[0][1].length < 2) {
            throw new InsufficientDataError(
                "At least two observation positions are required."
            );
        }

        this.name = name;
        this.columns = new Map(
            entries.map(([key, values]) => [
                key,
                Object.freeze([...values])
            ])
        );

        Object.freeze(this);
    }
}

class CorrelationAnalyzer {
    constructor(dataset, policy = MissingPolicy.REJECT) {
        if (!(dataset instanceof Dataset)) {
            throw new ValidationError(
                "A valid Dataset instance is required."
            );
        }

        if (!Object.values(MissingPolicy).includes(policy)) {
            throw new ValidationError(
                "Unknown missing-value policy."
            );
        }

        this.dataset = dataset;
        this.policy = policy;
    }

    getPairs(first, second) {
        const x = this.dataset.columns.get(first);
        const y = this.dataset.columns.get(second);

        if (!x || !y) {
            throw new ValidationError(
                "Unknown variable supplied."
            );
        }

        const completeIndexes = [];

        if (this.policy === MissingPolicy.LISTWISE) {
            for (let i = 0; i < x.length; i++) {
                const complete = [...this.dataset.columns.values()]
                    .every(values =>
                        values[i] !== null &&
                        values[i] !== undefined
                    );

                if (complete) completeIndexes.push(i);
            }
        }

        const resultX = [];
        const resultY = [];

        for (let i = 0; i < x.length; i++) {
            if (
                this.policy === MissingPolicy.LISTWISE &&
                !completeIndexes.includes(i)
            ) {
                continue;
            }

            const a = x[i];
            const b = y[i];

            if (a == null || b == null) {
                if (this.policy === MissingPolicy.REJECT) {
                    throw new ValidationError(
                        "Missing observations are not allowed."
                    );
                }

                continue;
            }

            resultX.push(a);
            resultY.push(b);
        }

        return { x: resultX, y: resultY };
    }

    analyzePair(first, second, sample = true) {
        const { x, y } = this.getPairs(first, second);

        const cov = covariance(x, y, sample);

        let corr = null;

        if (
            new Set(x).size > 1 &&
            new Set(y).size > 1
        ) {
            corr = pearson(x, y);
        }

        return Object.freeze({
            first,
            second,
            observations: x.length,
            covariance: cov,
            correlation: corr,
            strength: corr === null
                ? "Undefined"
                : correlationStrength(corr)
        });
    }

    buildMatrix(metric) {
        const names = [...this.dataset.columns.keys()];
        const matrix = {};

        for (const name of names) {
            matrix[name] = {};
        }

        for (let i = 0; i < names.length; i++) {
            for (let j = i; j < names.length; j++) {
                const first = names[i];
                const second = names[j];

                const result = this.analyzePair(
                    first,
                    second,
                    true
                );

                const value = metric === "covariance"
                    ? result.covariance
                    : result.correlation;

                matrix[first][second] = value;
                matrix[second][first] = value;
            }
        }

        return matrix;
    }

    getHighCorrelations(threshold = 0.80) {
        if (
            !Number.isFinite(threshold) ||
            threshold <= 0 ||
            threshold > 1
        ) {
            throw new ValidationError(
                "Threshold must be between zero and one."
            );
        }

        const matrix = this.buildMatrix("correlation");
        const names = Object.keys(matrix);
        const pairs = [];

        for (let i = 0; i < names.length; i++) {
            for (let j = i + 1; j < names.length; j++) {
                const value = matrix[names[i]][names[j]];

                if (
                    value !== null &&
                    Math.abs(value) >= threshold
                ) {
                    pairs.push({
                        first: names[i],
                        second: names[j],
                        correlation: value
                    });
                }
            }
        }

        return pairs;
    }

    describe() {
        const result = {};

        for (const [name, raw] of this.dataset.columns) {
            const values = raw.filter(v => v != null);

            if (values.length === 0) {
                result[name] = { observations: 0 };
                continue;
            }

            const sorted = [...values].sort((a, b) => a - b);

            const median = sorted.length % 2 === 0
                ? (
                    sorted[sorted.length / 2 - 1] +
                    sorted[sorted.length / 2]
                ) / 2
                : sorted[Math.floor(sorted.length / 2)];

            result[name] = {
                observations: values.length,
                missing: raw.length - values.length,
                mean: mean(values),
                median,
                variance: values.length >= 2
                    ? variance(values)
                    : null,
                minimum: Math.min(...values),
                maximum: Math.max(...values)
            };
        }

        return result;
    }

    async analyzeAsync() {
        // Yield control so large analysis workflows do not monopolize
        // the current event loop.
        await new Promise(resolve => setImmediate(resolve));

        return {
            dataset: this.dataset.name,
            statistics: this.describe(),
            covarianceMatrix: this.buildMatrix("covariance"),
            correlationMatrix: this.buildMatrix("correlation"),
            highCorrelations: this.getHighCorrelations()
        };
    }
}

class AnalysisService extends EventEmitter {
    constructor() {
        super();
        this.jobs = new Map();
        this.nextJobId = 1;
    }

    async submit(dataset, policy = MissingPolicy.REJECT) {
        const id = this.nextJobId++;

        const job = {
            id,
            status: "PENDING",
            submittedAt: new Date().toISOString(),
            result: null,
            error: null
        };

        this.jobs.set(id, job);
        this.emit("submitted", { id });

        try {
            job.status = "RUNNING";
            this.emit("started", { id });

            const analyzer = new CorrelationAnalyzer(
                dataset,
                policy
            );

            const result = await analyzer.analyzeAsync();

            job.status = "COMPLETED";
            job.result = result;

            this.emit("completed", { id, result });

        } catch (error) {
            job.status = "FAILED";
            job.error = error.message;

            this.emit("failed", {
                id,
                message: error.message
            });
        }

        return job;
    }

    getJob(id) {
        const job = this.jobs.get(id);

        if (!job) {
            throw new ValidationError(
                `Unknown analysis job: ${id}`
            );
        }

        return job;
    }
}

async function saveReport(path, report) {
    const serialized = JSON.stringify(report, null, 2);

    // Exclusive creation prevents accidental report replacement.
    await fs.writeFile(path, serialized, {
        encoding: "utf8",
        flag: "wx",
        mode: 0o600
    });
}

function runTests() {
    const x = [1, 2, 3, 4];
    const y = [2, 4, 6, 8];
    const z = [8, 6, 4, 2];

    if (Math.abs(pearson(x, y) - 1) > 1e-12) {
        throw new Error("Positive correlation test failed.");
    }

    if (Math.abs(pearson(x, z) + 1) > 1e-12) {
        throw new Error("Negative correlation test failed.");
    }

    if (Math.abs(variance(x) - 1.6666666667) > 1e-9) {
        throw new Error("Variance test failed.");
    }

    if (Math.abs(covariance(x, y) - 3.3333333333) > 1e-9) {
        throw new Error("Covariance test failed.");
    }

    let failed = false;

    try {
        pearson([1, 1, 1], [2, 3, 4]);
    } catch (error) {
        failed = error instanceof ValidationError;
    }

    if (!failed) {
        throw new Error("Constant-variable test failed.");
    }

    console.log("All JavaScript statistical tests passed.");
}

async function main() {
    const service = new AnalysisService();

    service.on("submitted", event =>
        console.log(`Job ${event.id}: submitted`)
    );

    service.on("started", event =>
        console.log(`Job ${event.id}: running`)
    );

    service.on("completed", event =>
        console.log(`Job ${event.id}: completed`)
    );

    service.on("failed", event =>
        console.error(`Job ${event.id}: ${event.message}`)
    );

    const dataset = new Dataset(
        "Portfolio Risk Analysis",
        {
            Equity_A: [10, 12, 14, 16, 18, 20],
            Equity_B: [8, 10, 12, 14, 16, 18],
            Bonds: [20, 19, 21, 18, 22, 17],
            Gold: [15, 17, 14, 18, 13, 19],
            Market_Index: [11, 13, 15, 17, 19, 21]
        }
    );

    console.log("\nCORRELATION AND COVARIANCE ENGINE");
    console.log("=================================");

    const job = await service.submit(dataset);

    if (job.status !== "COMPLETED") {
        throw new StatisticalError(job.error);
    }

    const report = job.result;

    console.log("\nDESCRIPTIVE STATISTICS");
    console.log(JSON.stringify(report.statistics, null, 2));

    console.log("\nCOVARIANCE MATRIX");
    console.table(report.covarianceMatrix);

    console.log("\nCORRELATION MATRIX");
    console.table(report.correlationMatrix);

    console.log("\nHIGH CORRELATION PAIRS");
    console.table(report.highCorrelations);

    const missingDataset = new Dataset(
        "Missing Data Example",
        {
            A: [1, 2, null, 4, 5],
            B: [2, 4, 6, null, 10]
        }
    );

    const pairwise = new CorrelationAnalyzer(
        missingDataset,
        MissingPolicy.PAIRWISE
    );

    console.log("\nPAIRWISE MISSING-VALUE ANALYSIS");
    console.log(pairwise.analyzePair("A", "B"));

    runTests();

    console.log("\nAnalysis completed.");
}

main().catch(error => {
    console.error("Fatal analysis error:", error.message);
    process.exitCode = 1;
});
