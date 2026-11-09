"use strict";

/*
 * Conditional Distributions
 *
 * Event-driven conditional probability analysis using Node.js 18+.
 *
 * Features:
 * - Joint probability distribution using Maps.
 * - Conditional PMF and marginal distributions.
 * - Conditional expectation and variance.
 * - Bivariate normal conditional density.
 * - Conditional CDF.
 * - Law of total expectation and variance.
 * - Asynchronous analysis and event reporting.
 * - JSON persistence.
 */

const fs = require("node:fs/promises");
const { EventEmitter } = require("node:events");

class DistributionError extends Error {
    constructor(message) {
        super(message);
        this.name = "DistributionError";
    }
}

function assertFinite(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new DistributionError(`${name} must be finite.`);
    }
}

function encodeKey(value) {
    return JSON.stringify(value);
}

class JointDistribution {
    constructor(rows) {
        if (!Array.isArray(rows) || rows.length === 0) {
            throw new DistributionError("Joint distribution cannot be empty.");
        }

        this.joint = new Map();
        this.xValues = new Map();
        this.yValues = new Map();

        for (const row of rows) {
            if (!row || !("x" in row) || !("y" in row)) {
                throw new DistributionError("Each row requires x and y.");
            }

            assertFinite(row.probability, "Probability");

            if (row.probability < 0) {
                throw new DistributionError("Negative probabilities are invalid.");
            }

            const key = `${encodeKey(row.x)}|${encodeKey(row.y)}`;

            if (this.joint.has(key)) {
                throw new DistributionError("Duplicate joint outcome.");
            }

            this.joint.set(key, {
                x: row.x,
                y: row.y,
                probability: row.probability
            });

            this.xValues.set(encodeKey(row.x), row.x);
            this.yValues.set(encodeKey(row.y), row.y);
        }

        const total = [...this.joint.values()]
            .reduce((sum, row) => sum + row.probability, 0);

        if (Math.abs(total - 1) > 1e-10) {
            throw new DistributionError(
                `Joint probabilities must sum to 1. Found ${total}.`
            );
        }
    }

    marginal(variable, value) {
        if (variable !== "x" && variable !== "y") {
            throw new DistributionError("Variable must be x or y.");
        }

        let result = 0;

        for (const row of this.joint.values()) {
            if (Object.is(row[variable], value)) {
                result += row.probability;
            }
        }

        return result;
    }

    conditional(variable, value) {
        if (variable !== "x" && variable !== "y") {
            throw new DistributionError("Variable must be x or y.");
        }

        const fixedVariable = variable === "x" ? "y" : "x";
        const denominator = this.marginal(variable, value);

        if (denominator <= 0) {
            throw new DistributionError(
                "Conditioning event has zero probability."
            );
        }

        const result = new Map();

        for (const row of this.joint.values()) {
            if (Object.is(row[variable], value)) {
                const key = encodeKey(row[fixedVariable]);

                result.set(
                    row[fixedVariable],
                    (result.get(row[fixedVariable]) || 0)
                    + row.probability / denominator
                );
            }
        }

        return result;
    }

    static expectation(pmf) {
        let result = 0;

        for (const [value, probability] of pmf) {
            assertFinite(value, "Outcome");
            result += value * probability;
        }

        return result;
    }

    static variance(pmf) {
        const mean = this.expectation(pmf);

        let result = 0;

        for (const [value, probability] of pmf) {
            result += (value - mean) ** 2 * probability;
        }

        return Math.max(0, result);
    }

    statistics(variable, value) {
        const pmf = this.conditional(variable, value);

        return Object.freeze({
            conditioningVariable: variable,
            conditioningValue: value,
            conditioningProbability: this.marginal(variable, value),
            conditionalPMF: Object.fromEntries(pmf),
            conditionalExpectation: JointDistribution.expectation(pmf),
            conditionalVariance: JointDistribution.variance(pmf)
        });
    }

    totalExpectationOfY() {
        let result = 0;

        for (const x of this.xValues.values()) {
            const probability = this.marginal("x", x);

            if (probability === 0) continue;

            const pmf = this.conditional("x", x);

            result += probability * JointDistribution.expectation(pmf);
        }

        return result;
    }

    totalVarianceOfY() {
        let expectedConditionalVariance = 0;
        const conditionalMeans = [];

        for (const x of this.xValues.values()) {
            const probability = this.marginal("x", x);

            if (probability === 0) continue;

            const pmf = this.conditional("x", x);

            const mean = JointDistribution.expectation(pmf);
            const variance = JointDistribution.variance(pmf);

            expectedConditionalVariance += probability * variance;

            conditionalMeans.push({ mean, probability });
        }

        const overallMean = conditionalMeans.reduce(
            (sum, item) => sum + item.mean * item.probability,
            0
        );

        const varianceOfMeans = conditionalMeans.reduce(
            (sum, item) =>
                sum + item.probability * (item.mean - overallMean) ** 2,
            0
        );

        return expectedConditionalVariance + varianceOfMeans;
    }
}

class BivariateNormal {
    constructor(muX, muY, sigmaX, sigmaY, rho) {
        [muX, muY, sigmaX, sigmaY, rho].forEach(
            (value, index) =>
                assertFinite(value, `Parameter ${index}`)
        );

        if (sigmaX <= 0 || sigmaY <= 0) {
            throw new DistributionError(
                "Standard deviations must be positive."
            );
        }

        if (rho <= -1 || rho >= 1) {
            throw new DistributionError(
                "Correlation must be strictly between -1 and 1."
            );
        }

        this.muX = muX;
        this.muY = muY;
        this.sigmaX = sigmaX;
        this.sigmaY = sigmaY;
        this.rho = rho;

        Object.freeze(this);
    }

    conditionalMean(x) {
        assertFinite(x, "Conditioning value");

        return this.muY
            + this.rho * this.sigmaY / this.sigmaX
            * (x - this.muX);
    }

    conditionalVariance() {
        return this.sigmaY ** 2 * (1 - this.rho ** 2);
    }

    conditionalDensity(y, x) {
        assertFinite(y, "Evaluation value");

        const mean = this.conditionalMean(x);
        const variance = this.conditionalVariance();

        return Math.exp(
            -((y - mean) ** 2) / (2 * variance)
        ) / Math.sqrt(2 * Math.PI * variance);
    }

    conditionalCDF(y, x) {
        assertFinite(y, "Evaluation value");

        const z = (y - this.conditionalMean(x))
            / Math.sqrt(this.conditionalVariance());

        // Numerical approximation of the standard normal CDF.
        const sign = z < 0 ? -1 : 1;
        const absoluteZ = Math.abs(z) / Math.sqrt(2);

        const t = 1 / (1 + 0.3275911 * absoluteZ);

        const erf = 1 - (
            (
                (
                    (
                        1.061405429 * t
                        - 1.453152027
                    ) * t
                    + 1.421413741
                ) * t
                - 0.284496736
            ) * t
            + 0.254829592
        ) * t * Math.exp(-absoluteZ ** 2);

        return Math.max(0, Math.min(1, 0.5 * (1 + sign * erf)));
    }
}

class ConditionalAnalysisService extends EventEmitter {
    constructor(distribution) {
        super();

        this.distribution = distribution;
        this.history = [];
    }

    async analyze(variable, value) {
        // Yield to the event loop to support asynchronous consumers.
        await new Promise(resolve => setImmediate(resolve));

        try {
            const result = this.distribution.statistics(variable, value);

            const event = Object.freeze({
                timestamp: new Date().toISOString(),
                result
            });

            this.history.push(event);

            this.emit("analysis-completed", event);

            return event;
        } catch (error) {
            this.emit("analysis-failed", error);
            throw error;
        }
    }

    async analyzeMany(variable, values) {
        if (!Array.isArray(values)) {
            throw new DistributionError("Values must be an array.");
        }

        // Sequential execution avoids unnecessary concurrent work
        // against the same service history.
        const results = [];

        for (const value of values) {
            results.push(await this.analyze(variable, value));
        }

        return results;
    }
}

async function main() {
    const rows = [
        { x: 0, y: 0, probability: 0.10 },
        { x: 0, y: 1, probability: 0.10 },
        { x: 0, y: 2, probability: 0.05 },
        { x: 1, y: 0, probability: 0.05 },
        { x: 1, y: 1, probability: 0.20 },
        { x: 1, y: 2, probability: 0.15 },
        { x: 2, y: 0, probability: 0.05 },
        { x: 2, y: 1, probability: 0.10 },
        { x: 2, y: 2, probability: 0.20 }
    ];

    const joint = new JointDistribution(rows);
    const service = new ConditionalAnalysisService(joint);

    service.on("analysis-completed", event => {
        console.log(
            `Completed analysis for X=${event.result.conditioningValue}`
        );
    });

    service.on("analysis-failed", error => {
        console.error("Analysis failed:", error.message);
    });

    console.log("\nCONDITIONAL DISTRIBUTIONS\n");

    const results = await service.analyzeMany("x", [0, 1, 2]);

    for (const event of results) {
        const result = event.result;

        console.log({
            x: result.conditioningValue,
            probability: result.conditioningProbability,
            pmf: result.conditionalPMF,
            expectation: result.conditionalExpectation,
            variance: result.conditionalVariance
        });
    }

    console.log("\nLaw of total expectation");

    const expectedY = joint.totalExpectationOfY();

    console.log("E[Y] = E[E[Y|X]] =", expectedY);

    console.log("\nLaw of total variance");

    console.log(
        "Var(Y) =",
        joint.totalVarianceOfY()
    );

    const normal = new BivariateNormal(
        10, 50, 2, 8, 0.75
    );

    const x = 12;
    const y = 58;

    console.log("\nCONTINUOUS CONDITIONAL DISTRIBUTION");

    console.log({
        conditionalMean: normal.conditionalMean(x),
        conditionalVariance: normal.conditionalVariance(),
        conditionalDensity: normal.conditionalDensity(y, x),
        conditionalCDF: normal.conditionalCDF(y, x)
    });

    const output = {
        discrete: results.map(event => event.result),
        continuous: {
            conditionalMean: normal.conditionalMean(x),
            conditionalVariance: normal.conditionalVariance(),
            density: normal.conditionalDensity(y, x)
        }
    };

    await fs.writeFile(
        "conditional_distribution_results.json",
        JSON.stringify(output, null, 2),
        { encoding: "utf8", mode: 0o600 }
    );

    console.log("\nResults saved successfully.");

    // Validate mathematical identities.
    const marginalExpectation = [...joint.yValues.values()]
        .reduce(
            (sum, value) => sum + value * joint.marginal("y", value),
            0
        );

    if (Math.abs(marginalExpectation - expectedY) > 1e-10) {
        throw new Error("Law of total expectation validation failed.");
    }

    console.log("Mathematical validation passed.");

    try {
        await service.analyze("x", 99);
    } catch (error) {
        console.log("Expected failure:", error.message);
    }
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
