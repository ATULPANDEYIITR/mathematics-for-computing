"use strict";

/*
 * MULTIVARIATE STATISTICS
 * Event-driven statistical analysis using Node.js standard libraries.
 *
 * Features:
 * - Multiple regression
 * - Online covariance estimation
 * - Multivariate distributions
 * - Mahalanobis distance
 * - Multivariate normal sampling
 * - Event-driven statistical monitoring
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class StatisticalError extends Error {}
class ValidationError extends StatisticalError {}

function validateMatrix(matrix) {
    if (!Array.isArray(matrix) || matrix.length === 0) {
        throw new ValidationError("Matrix cannot be empty.");
    }

    if (!Array.isArray(matrix[0]) || matrix[0].length === 0) {
        throw new ValidationError("Matrix rows cannot be empty.");
    }

    const width = matrix[0].length;

    for (const row of matrix) {
        if (!Array.isArray(row) || row.length !== width) {
            throw new ValidationError("Matrix must be rectangular.");
        }

        for (const value of row) {
            if (!Number.isFinite(value)) {
                throw new ValidationError("Non-finite matrix value.");
            }
        }
    }

    return matrix.map(row => [...row]);
}

function transpose(matrix) {
    return matrix[0].map((_, j) => matrix.map(row => row[j]));
}

function multiply(a, b) {
    a = validateMatrix(a);
    b = validateMatrix(b);

    if (a[0].length !== b.length) {
        throw new ValidationError("Incompatible matrix dimensions.");
    }

    return a.map(row =>
        b[0].map((_, j) =>
            row.reduce((sum, value, k) => sum + value * b[k][j], 0)
        )
    );
}

function solveLinearSystem(matrix, vector) {
    const a = validateMatrix(matrix);
    const n = a.length;

    if (a[0].length !== n || vector.length !== n) {
        throw new ValidationError("Invalid linear system dimensions.");
    }

    if (vector.some(value => !Number.isFinite(value))) {
        throw new ValidationError("Invalid right-hand side.");
    }

    const augmented = a.map((row, i) => [...row, vector[i]]);

    for (let col = 0; col < n; col++) {
        let pivot = col;

        for (let row = col + 1; row < n; row++) {
            if (
                Math.abs(augmented[row][col]) >
                Math.abs(augmented[pivot][col])
            ) {
                pivot = row;
            }
        }

        if (Math.abs(augmented[pivot][col]) < 1e-12) {
            throw new StatisticalError("Singular matrix.");
        }

        [augmented[col], augmented[pivot]] =
            [augmented[pivot], augmented[col]];

        const divisor = augmented[col][col];

        for (let j = col; j <= n; j++) {
            augmented[col][j] /= divisor;
        }

        for (let row = 0; row < n; row++) {
            if (row === col) continue;

            const factor = augmented[row][col];

            for (let j = col; j <= n; j++) {
                augmented[row][j] -= factor * augmented[col][j];
            }
        }
    }

    return augmented.map(row => row[n]);
}

class OnlineCovariance {
    /*
     * Multivariate Welford algorithm.
     * Updates means and cross-products without retaining observations.
     * Memory complexity: O(p^2).
     */

    constructor(dimension) {
        if (!Number.isInteger(dimension) || dimension < 1) {
            throw new ValidationError("Invalid dimension.");
        }

        this.dimension = dimension;
        this.count = 0;
        this.mean = Array(dimension).fill(0);
        this.crossProducts = Array.from(
            { length: dimension },
            () => Array(dimension).fill(0)
        );
    }

    add(observation) {
        if (
            !Array.isArray(observation) ||
            observation.length !== this.dimension ||
            observation.some(v => !Number.isFinite(v))
        ) {
            throw new ValidationError("Invalid observation.");
        }

        this.count++;

        const delta = observation.map(
            (value, i) => value - this.mean[i]
        );

        for (let i = 0; i < this.dimension; i++) {
            this.mean[i] += delta[i] / this.count;
        }

        const deltaAfter = observation.map(
            (value, i) => value - this.mean[i]
        );

        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                this.crossProducts[i][j] +=
                    delta[i] * deltaAfter[j];
            }
        }
    }

    covariance() {
        if (this.count < 2) {
            throw new StatisticalError(
                "At least two observations are required."
            );
        }

        return this.crossProducts.map(row =>
            row.map(value => value / (this.count - 1))
        );
    }

    correlation() {
        const covariance = this.covariance();

        return covariance.map((row, i) =>
            row.map((value, j) => {
                const denominator = Math.sqrt(
                    covariance[i][i] * covariance[j][j]
                );

                if (denominator === 0) {
                    throw new StatisticalError(
                        "Correlation undefined for constant variable."
                    );
                }

                return value / denominator;
            })
        );
    }
}

function cholesky(matrix) {
    const a = validateMatrix(matrix);
    const n = a.length;

    if (a[0].length !== n) {
        throw new ValidationError("Matrix must be square.");
    }

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            if (Math.abs(a[i][j] - a[j][i]) > 1e-10) {
                throw new ValidationError("Matrix must be symmetric.");
            }
        }
    }

    const lower = Array.from(
        { length: n },
        () => Array(n).fill(0)
    );

    for (let i = 0; i < n; i++) {
        for (let j = 0; j <= i; j++) {
            let sum = a[i][j];

            for (let k = 0; k < j; k++) {
                sum -= lower[i][k] * lower[j][k];
            }

            if (i === j) {
                if (sum <= 0) {
                    throw new StatisticalError(
                        "Covariance matrix is not positive definite."
                    );
                }

                lower[i][j] = Math.sqrt(sum);
            } else {
                lower[i][j] = sum / lower[j][j];
            }
        }
    }

    return lower;
}

function mahalanobisDistance(observation, mean, covariance) {
    if (
        observation.length !== mean.length ||
        observation.length !== covariance.length
    ) {
        throw new ValidationError("Dimension mismatch.");
    }

    const lower = cholesky(covariance);
    const difference = observation.map(
        (value, i) => value - mean[i]
    );

    const whitened = [];

    for (let i = 0; i < difference.length; i++) {
        let value = difference[i];

        for (let j = 0; j < i; j++) {
            value -= lower[i][j] * whitened[j];
        }

        whitened.push(value / lower[i][i]);
    }

    return Math.sqrt(
        whitened.reduce((sum, value) => sum + value * value, 0)
    );
}

function multivariateNormalDensity(observation, mean, covariance) {
    const lower = cholesky(covariance);

    if (observation.length !== mean.length) {
        throw new ValidationError("Dimension mismatch.");
    }

    const distance = mahalanobisDistance(
        observation, mean, covariance
    );

    const logDeterminant = 2 * lower.reduce(
        (sum, row, i) => sum + Math.log(row[i]), 0
    );

    const n = mean.length;

    return Math.exp(
        -0.5 * n * Math.log(2 * Math.PI)
        -0.5 * logDeterminant
        -0.5 * distance ** 2
    );
}

class MultipleRegression {
    constructor(features, target) {
        this.features = validateMatrix(features);
        this.target = [...target];

        if (this.features.length !== target.length) {
            throw new ValidationError("Observation counts differ.");
        }

        if (target.some(value => !Number.isFinite(value))) {
            throw new ValidationError("Invalid target values.");
        }

        this.n = features.length;
        this.p = features[0].length;

        if (this.n <= this.p + 1) {
            throw new ValidationError(
                "Insufficient observations for regression."
            );
        }

        this.fit();
    }

    fit() {
        const design = this.features.map(
            row => [1, ...row]
        );

        const xt = transpose(design);
        const xtx = multiply(xt, design);

        const xty = xt.map(column =>
            column.reduce(
                (sum, value, i) => sum + value * this.target[i],
                0
            )
        );

        this.coefficients = solveLinearSystem(xtx, xty);

        this.predictions = design.map(row =>
            row.reduce(
                (sum, value, i) =>
                    sum + value * this.coefficients[i],
                0
            )
        );

        this.residuals = this.target.map(
            (value, i) => value - this.predictions[i]
        );

        const mean = this.target.reduce(
            (sum, value) => sum + value, 0
        ) / this.n;

        const ssResidual = this.residuals.reduce(
            (sum, value) => sum + value ** 2, 0
        );

        const ssTotal = this.target.reduce(
            (sum, value) => sum + (value - mean) ** 2, 0
        );

        if (ssTotal === 0) {
            throw new StatisticalError(
                "R-squared undefined for constant target."
            );
        }

        this.rSquared = 1 - ssResidual / ssTotal;

        this.adjustedRSquared =
            1 - (1 - this.rSquared) *
            (this.n - 1) / (this.n - this.p - 1);

        this.rmse = Math.sqrt(ssResidual / this.n);
        this.residualVariance =
            ssResidual / (this.n - this.p - 1);
    }

    predict(features) {
        const x = validateMatrix(features);

        if (x[0].length !== this.p) {
            throw new ValidationError("Feature dimension mismatch.");
        }

        return x.map(row =>
            this.coefficients[0] +
            row.reduce(
                (sum, value, i) =>
                    sum + value * this.coefficients[i + 1],
                0
            )
        );
    }

    report() {
        return {
            coefficients: this.coefficients,
            rSquared: this.rSquared,
            adjustedRSquared: this.adjustedRSquared,
            rmse: this.rmse,
            residualVariance: this.residualVariance
        };
    }
}

class StatisticalMonitor extends EventEmitter {
    /*
     * Event-driven monitoring separates data collection from
     * statistical analysis and downstream alert handling.
     */

    constructor(dimension, threshold) {
        super();

        if (!Number.isFinite(threshold) || threshold <= 0) {
            throw new ValidationError("Invalid distance threshold.");
        }

        this.statistics = new OnlineCovariance(dimension);
        this.threshold = threshold;
        this.ready = false;
    }

    ingest(observation) {
        this.statistics.add(observation);

        this.emit("observation", {
            count: this.statistics.count
        });

        if (this.statistics.count >= 10) {
            this.ready = true;
        }

        if (!this.ready) return null;

        const covariance = this.statistics.covariance();

        const distance = mahalanobisDistance(
            observation,
            this.statistics.mean,
            covariance
        );

        const event = {
            observation,
            distance,
            threshold: this.threshold,
            anomalous: distance > this.threshold
        };

        this.emit(
            event.anomalous ? "anomaly" : "normal",
            event
        );

        return event;
    }
}

function createRandomGenerator(seed) {
    let state = seed >>> 0;

    return () => {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 4294967296;
    };
}

function normalRandom(random) {
    const u1 = Math.max(random(), Number.MIN_VALUE);
    const u2 = random();

    return Math.sqrt(-2 * Math.log(u1)) *
        Math.cos(2 * Math.PI * u2);
}

function generateMultivariateNormal(mean, covariance, count, seed = 42) {
    if (!Number.isInteger(count) || count <= 0) {
        throw new ValidationError("Sample count must be positive.");
    }

    const lower = cholesky(covariance);
    const random = createRandomGenerator(seed);

    return Array.from({ length: count }, () => {
        const z = mean.map(() => normalRandom(random));

        return mean.map((value, i) =>
            value + lower[i].slice(0, i + 1).reduce(
                (sum, coefficient, j) =>
                    sum + coefficient * z[j],
                0
            )
        );
    });
}

async function saveReport(report, filename) {
    // Prevent accidental path traversal through caller-controlled names.
    if (
        typeof filename !== "string" ||
        !/^[a-zA-Z0-9_-]+\.json$/.test(filename)
    ) {
        throw new ValidationError("Invalid report filename.");
    }

    await fs.writeFile(
        filename,
        JSON.stringify(report, null, 2),
        { encoding: "utf8", flag: "w" }
    );
}

async function main() {
    console.log("MULTIVARIATE STATISTICS");
    console.log("=======================");

    const features = [
        [10, 2], [12, 3], [14, 4], [16, 3],
        [18, 5], [20, 6], [22, 5], [24, 7],
        [26, 8], [28, 7], [30, 9], [32, 10]
    ];

    const target = [
        40, 44, 49, 50, 57, 63,
        65, 72, 78, 80, 87, 94
    ];

    const regression = new MultipleRegression(features, target);

    console.log("\n1. REGRESSION");
    console.log(regression.report());
    console.log("Prediction:", regression.predict([[25, 6]]));

    console.log("\n2. ONLINE COVARIANCE");

    const accumulator = new OnlineCovariance(2);

    features.forEach(row => accumulator.add(row));

    console.log("Mean:", accumulator.mean);
    console.log("Covariance:", accumulator.covariance());
    console.log("Correlation:", accumulator.correlation());

    console.log("\n3. MULTIVARIATE DISTRIBUTION");

    const mean = [50, 60];

    const covariance = [
        [100, 30],
        [30, 144]
    ];

    const observation = [55, 65];

    console.log(
        "Mahalanobis distance:",
        mahalanobisDistance(observation, mean, covariance)
    );

    console.log(
        "Probability density:",
        multivariateNormalDensity(observation, mean, covariance)
    );

    console.log("\n4. RANDOM SAMPLING");

    const samples = generateMultivariateNormal(
        mean, covariance, 1000
    );

    console.log("Sample count:", samples.length);

    console.log("\n5. EVENT-DRIVEN MONITORING");

    const monitor = new StatisticalMonitor(2, 4);

    monitor.on("observation", event => {
        if (event.count === 10) {
            console.log("Monitoring initialized.");
        }
    });

    monitor.on("anomaly", event => {
        console.log(
            "Anomaly detected:",
            event.distance.toFixed(4)
        );
    });

    monitor.on("normal", () => {
        // Normal observations do not require additional processing.
    });

    for (const row of samples.slice(0, 30)) {
        monitor.ingest(row);
    }

    console.log("\n6. REPORT EXPORT");

    await saveReport({
        regression: regression.report(),
        mean: accumulator.mean,
        covariance: accumulator.covariance(),
        sampleCount: samples.length
    }, "multivariate_report.json");

    console.log("Report written successfully.");

    console.log("\n7. FAILURE VALIDATION");

    try {
        cholesky([[1, 2], [2, 1]]);
    } catch (error) {
        console.log("Invalid covariance rejected:", error.message);
    }

    try {
        new MultipleRegression([[1], [2]], [3, 4]);
    } catch (error) {
        console.log("Insufficient data rejected:", error.message);
    }

    if (!(regression.rSquared > 0 && regression.rSquared <= 1)) {
        throw new StatisticalError("Regression validation failed.");
    }

    console.log("\nAll statistical checks completed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
