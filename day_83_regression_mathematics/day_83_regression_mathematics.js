"use strict";

/*
 * Regression Mathematics
 * Simple Linear Regression, Least Squares and Residual Analysis.
 *
 * Runtime: Node.js 18+
 *
 * Features:
 * - OLS regression
 * - Online observation collection
 * - Event-driven model updates
 * - Residual analysis
 * - Prediction
 * - Model quality metrics
 * - Asynchronous dataset processing
 * - Input validation
 * - Regression invariants
 */

const EventEmitter = require("node:events");

class RegressionError extends Error {
    constructor(message) {
        super(message);
        this.name = "RegressionError";
    }
}

class ValidationError extends RegressionError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class ModelStateError extends RegressionError {
    constructor(message) {
        super(message);
        this.name = "ModelStateError";
    }
}

function validateNumber(value, field) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value)
    ) {
        throw new ValidationError(
            `${field} must be a finite number.`
        );
    }

    return value;
}

class Observation {
    constructor(x, y) {
        this.x = validateNumber(x, "X");
        this.y = validateNumber(y, "Y");

        Object.freeze(this);
    }
}

class RegressionDataset extends EventEmitter {
    #observations = [];
    #version = 0;
    #maxObservations;

    constructor(maxObservations = 1000000) {
        super();

        if (
            !Number.isInteger(maxObservations) ||
            maxObservations < 3
        ) {
            throw new ValidationError(
                "Maximum observation count must be at least 3."
            );
        }

        this.#maxObservations = maxObservations;
    }

    add(x, y) {
        if (
            this.#observations.length >= this.#maxObservations
        ) {
            throw new ValidationError(
                "Dataset capacity exceeded."
            );
        }

        const observation = new Observation(x, y);

        this.#observations.push(observation);
        this.#version++;

        this.emit("observationAdded", {
            observation,
            version: this.#version,
            count: this.#observations.length
        });

        return this.#version;
    }

    addBatch(rows) {
        if (!Array.isArray(rows)) {
            throw new ValidationError(
                "Batch must be an array."
            );
        }

        if (
            this.#observations.length + rows.length >
            this.#maxObservations
        ) {
            throw new ValidationError(
                "Batch exceeds dataset capacity."
            );
        }

        // Validate the entire batch before modifying state.
        const validated = rows.map(
            row => new Observation(row.x, row.y)
        );

        this.#observations.push(...validated);

        if (validated.length > 0) {
            this.#version++;

            this.emit("batchAdded", {
                count: validated.length,
                version: this.#version
            });
        }

        return this.#version;
    }

    get snapshot() {
        return Object.freeze({
            version: this.#version,
            observations: Object.freeze([
                ...this.#observations
            ])
        });
    }

    get count() {
        return this.#observations.length;
    }

    clear() {
        this.#observations = [];
        this.#version++;

        this.emit("datasetCleared", {
            version: this.#version
        });
    }
}

class RegressionModel {
    constructor(parameters) {
        Object.assign(this, parameters);
        Object.freeze(this);
    }

    predict(x) {
        validateNumber(x, "Prediction input");

        const prediction =
            this.intercept + this.slope * x;

        if (!Number.isFinite(prediction)) {
            throw new RegressionError(
                "Prediction exceeded numeric limits."
            );
        }

        return prediction;
    }

    predictBatch(values) {
        if (!Array.isArray(values)) {
            throw new ValidationError(
                "Prediction batch must be an array."
            );
        }

        return values.map(x => this.predict(x));
    }

    equation() {
        const operator = this.slope >= 0 ? "+" : "-";

        return (
            `y = ${this.intercept.toFixed(6)} ` +
            `${operator} ${Math.abs(this.slope).toFixed(6)}x`
        );
    }

    getResiduals() {
        return this.residuals.map(
            (residual, index) => Object.freeze({
                observation: index + 1,
                actual: this.actualValues[index],
                fitted: this.fittedValues[index],
                residual,
                squaredResidual: residual ** 2
            })
        );
    }
}

class OrdinaryLeastSquares {
    constructor(dataset) {
        if (!(dataset instanceof RegressionDataset)) {
            throw new ValidationError(
                "A valid RegressionDataset is required."
            );
        }

        this.dataset = dataset;
        this.currentModel = null;
    }

    fit() {
        // Use a snapshot to prevent inconsistent reads.
        const snapshot = this.dataset.snapshot;
        const observations = snapshot.observations;

        const n = observations.length;

        if (n < 3) {
            throw new ModelStateError(
                "At least three observations are required."
            );
        }

        let sumX = 0;
        let sumY = 0;

        for (const observation of observations) {
            sumX += observation.x;
            sumY += observation.y;
        }

        const meanX = sumX / n;
        const meanY = sumY / n;

        let sxx = 0;
        let sxy = 0;

        for (const observation of observations) {
            const dx = observation.x - meanX;
            const dy = observation.y - meanY;

            sxx += dx * dx;
            sxy += dx * dy;
        }

        if (
            !Number.isFinite(sxx) ||
            !Number.isFinite(sxy) ||
            sxx <= 0
        ) {
            throw new RegressionError(
                "Independent variable has no usable variance."
            );
        }

        const slope = sxy / sxx;
        const intercept = meanY - slope * meanX;

        if (
            !Number.isFinite(slope) ||
            !Number.isFinite(intercept)
        ) {
            throw new RegressionError(
                "Invalid regression coefficients."
            );
        }

        const actualValues = [];
        const fittedValues = [];
        const residuals = [];

        let sse = 0;
        let sst = 0;
        let ssr = 0;
        let absoluteError = 0;
        let residualSum = 0;

        for (const observation of observations) {
            const fitted =
                intercept + slope * observation.x;

            const residual =
                observation.y - fitted;

            if (
                !Number.isFinite(fitted) ||
                !Number.isFinite(residual)
            ) {
                throw new RegressionError(
                    "Invalid fitted value or residual."
                );
            }

            actualValues.push(observation.y);
            fittedValues.push(fitted);
            residuals.push(residual);

            sse += residual ** 2;
            sst += (observation.y - meanY) ** 2;
            ssr += (fitted - meanY) ** 2;

            absoluteError += Math.abs(residual);
            residualSum += residual;
        }

        if (!Number.isFinite(sst) || sst <= 0) {
            throw new RegressionError(
                "R-squared is undefined for constant Y."
            );
        }

        const rSquared = 1 - sse / sst;

        const metrics = Object.freeze({
            sse,
            ssr,
            sst,
            rSquared,
            rmse: Math.sqrt(sse / n),
            mae: absoluteError / n,
            residualMean: residualSum / n,
            residualStandardDeviation:
                Math.sqrt(sse / (n - 2))
        });

        if (
            Math.abs(
                (sse + ssr) - sst
            ) > 1e-8 * Math.max(1, sst)
        ) {
            throw new RegressionError(
                "OLS sum-of-squares invariant failed."
            );
        }

        const model = new RegressionModel({
            slope,
            intercept,
            meanX,
            meanY,
            observationCount: n,
            datasetVersion: snapshot.version,
            metrics,
            actualValues: Object.freeze(actualValues),
            fittedValues: Object.freeze(fittedValues),
            residuals: Object.freeze(residuals)
        });

        this.currentModel = model;

        return model;
    }

    async fitAsync() {
        return new Promise((resolve, reject) => {
            setImmediate(() => {
                try {
                    resolve(this.fit());
                } catch (error) {
                    reject(error);
                }
            });
        });
    }
}

async function processStream(dataset, asyncIterable) {
    if (
        !asyncIterable ||
        typeof asyncIterable[Symbol.asyncIterator] !== "function"
    ) {
        throw new ValidationError(
            "An asynchronous iterable is required."
        );
    }

    let processed = 0;

    for await (const row of asyncIterable) {
        dataset.add(row.x, row.y);
        processed++;
    }

    return processed;
}

async function* observationStream(rows) {
    for (const row of rows) {
        await new Promise(resolve => setImmediate(resolve));
        yield row;
    }
}

function printReport(model) {
    console.log("\nSIMPLE LINEAR REGRESSION");
    console.log("=".repeat(60));

    console.log("Equation:", model.equation());
    console.log("Slope:", model.slope.toFixed(6));
    console.log("Intercept:", model.intercept.toFixed(6));
    console.log("Observations:", model.observationCount);
    console.log("Dataset version:", model.datasetVersion);

    console.log("\nMODEL METRICS");

    for (const [key, value] of Object.entries(model.metrics)) {
        console.log(`${key.padEnd(30)} ${value.toFixed(8)}`);
    }

    console.log("\nRESIDUAL ANALYSIS");
    console.table(model.getResiduals());

    console.log("\nPREDICTIONS");

    for (const x of [6, 7, 8, 10]) {
        console.log(
            `X = ${x}, predicted Y = ${model.predict(x).toFixed(4)}`
        );
    }
}

async function runTests() {
    const dataset = new RegressionDataset(100);

    dataset.addBatch([
        { x: 1, y: 3 },
        { x: 2, y: 5 },
        { x: 3, y: 7 },
        { x: 4, y: 9 },
        { x: 5, y: 11 }
    ]);

    const regression = new OrdinaryLeastSquares(dataset);
    const model = await regression.fitAsync();

    console.assert(
        Math.abs(model.slope - 2) < 1e-10,
        "Slope test failed."
    );

    console.assert(
        Math.abs(model.intercept - 1) < 1e-10,
        "Intercept test failed."
    );

    console.assert(
        Math.abs(model.metrics.rSquared - 1) < 1e-10,
        "R-squared test failed."
    );

    console.assert(
        Math.abs(model.predict(6) - 13) < 1e-10,
        "Prediction test failed."
    );

    // Event-driven observation tracking.
    let eventCount = 0;

    dataset.on("observationAdded", () => {
        eventCount++;
    });

    dataset.add(6, 13);

    if (eventCount !== 1) {
        throw new RegressionError(
            "Event handling test failed."
        );
    }

    // Constant X must not produce a regression model.
    const invalidDataset = new RegressionDataset();

    invalidDataset.addBatch([
        { x: 5, y: 2 },
        { x: 5, y: 4 },
        { x: 5, y: 6 }
    ]);

    try {
        new OrdinaryLeastSquares(invalidDataset).fit();

        throw new RegressionError(
            "Constant X validation test failed."
        );
    } catch (error) {
        if (!(error instanceof RegressionError)) {
            throw error;
        }
    }

    console.log("\nAll JavaScript tests passed.");
}

async function main() {
    const dataset = new RegressionDataset();

    const rows = [
        { x: 1, y: 2.1 },
        { x: 2, y: 3.9 },
        { x: 3, y: 6.2 },
        { x: 4, y: 7.8 },
        { x: 5, y: 10.1 },
        { x: 6, y: 11.9 },
        { x: 7, y: 14.2 },
        { x: 8, y: 15.8 }
    ];

    dataset.on("batchAdded", event => {
        console.log(
            `Dataset updated: ${event.count} observations.`
        );
    });

    await processStream(
        dataset,
        observationStream(rows)
    );

    const regression = new OrdinaryLeastSquares(dataset);
    const model = await regression.fitAsync();

    printReport(model);

    await runTests();
}

main().catch(error => {
    console.error(
        `${error.name}: ${error.message}`
    );

    process.exitCode = 1;
});
