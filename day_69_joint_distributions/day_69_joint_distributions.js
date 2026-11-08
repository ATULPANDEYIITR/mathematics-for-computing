"use strict";

/*
 * Joint Distributions
 *
 * Implements:
 * - Discrete joint PMF
 * - Marginal PMFs
 * - Conditional PMFs
 * - Expected values and variances
 * - Covariance and correlation
 * - Independence testing
 * - Continuous bivariate normal PDF
 *
 * Runtime: Node.js 18+
 * No external dependencies.
 */

const assert = require("node:assert/strict");

class DistributionError extends Error {
    constructor(message) {
        super(message);
        this.name = "DistributionError";
    }
}

class JointDistribution {
    constructor(outcomes, tolerance = 1e-10) {
        if (!Array.isArray(outcomes) || outcomes.length === 0) {
            throw new DistributionError(
                "At least one joint outcome is required."
            );
        }

        if (!Number.isFinite(tolerance) || tolerance < 0) {
            throw new DistributionError("Invalid tolerance.");
        }

        this.tolerance = tolerance;
        this.pmf = new Map();

        let total = 0;

        for (const outcome of outcomes) {
            const { x, y, probability } = outcome ?? {};

            if (
                !Number.isFinite(x) ||
                !Number.isFinite(y) ||
                !Number.isFinite(probability)
            ) {
                throw new DistributionError(
                    "Outcome values must be finite numbers."
                );
            }

            if (probability < 0) {
                throw new DistributionError(
                    "Probability cannot be negative."
                );
            }

            const key = JSON.stringify([x, y]);

            if (this.pmf.has(key)) {
                throw new DistributionError(
                    `Duplicate outcome: (${x}, ${y})`
                );
            }

            this.pmf.set(key, {
                x,
                y,
                probability
            });

            total += probability;
        }

        if (Math.abs(total - 1) > tolerance) {
            throw new DistributionError(
                `Probability total must equal 1. Found ${total}.`
            );
        }

        // Normalize small floating-point discrepancies.
        for (const [key, outcome] of this.pmf) {
            this.pmf.set(key, {
                ...outcome,
                probability: outcome.probability / total
            });
        }
    }

    getJointProbability(x, y) {
        return this.pmf.get(JSON.stringify([x, y]))?.probability ?? 0;
    }

    calculateMarginal(variable) {
        if (!["x", "y"].includes(variable)) {
            throw new DistributionError(
                "Variable must be x or y."
            );
        }

        const result = new Map();

        for (const outcome of this.pmf.values()) {
            const value = outcome[variable];

            result.set(
                value,
                (result.get(value) ?? 0) + outcome.probability
            );
        }

        return new Map(
            [...result.entries()].sort((a, b) => a[0] - b[0])
        );
    }

    marginalX() {
        return this.calculateMarginal("x");
    }

    marginalY() {
        return this.calculateMarginal("y");
    }

    conditionalDistribution(conditionVariable, conditionValue) {
        if (!["x", "y"].includes(conditionVariable)) {
            throw new DistributionError("Invalid conditioning variable.");
        }

        const targetVariable = conditionVariable === "x" ? "y" : "x";
        const marginal = this.calculateMarginal(conditionVariable);
        const denominator = marginal.get(conditionValue) ?? 0;

        if (denominator === 0) {
            throw new DistributionError(
                "Conditional distribution is undefined."
            );
        }

        const result = new Map();

        for (const outcome of this.pmf.values()) {
            if (outcome[conditionVariable] !== conditionValue) {
                continue;
            }

            const target = outcome[targetVariable];

            result.set(
                target,
                (result.get(target) ?? 0) +
                outcome.probability / denominator
            );
        }

        return result;
    }

    conditionalYGivenX(x) {
        return this.conditionalDistribution("x", x);
    }

    conditionalXGivenY(y) {
        return this.conditionalDistribution("y", y);
    }

    static expectation(distribution) {
        let result = 0;

        for (const [value, probability] of distribution) {
            result += value * probability;
        }

        return result;
    }

    expectedX() {
        return JointDistribution.expectation(this.marginalX());
    }

    expectedY() {
        return JointDistribution.expectation(this.marginalY());
    }

    static variance(distribution) {
        const mean = JointDistribution.expectation(distribution);

        let result = 0;

        for (const [value, probability] of distribution) {
            result += probability * (value - mean) ** 2;
        }

        return result;
    }

    varianceX() {
        return JointDistribution.variance(this.marginalX());
    }

    varianceY() {
        return JointDistribution.variance(this.marginalY());
    }

    expectedXY() {
        let result = 0;

        for (const outcome of this.pmf.values()) {
            result += (
                outcome.x *
                outcome.y *
                outcome.probability
            );
        }

        return result;
    }

    covariance() {
        return this.expectedXY() - this.expectedX() * this.expectedY();
    }

    correlation() {
        const denominator = Math.sqrt(
            this.varianceX() * this.varianceY()
        );

        if (denominator === 0) {
            throw new DistributionError(
                "Correlation is undefined for zero variance."
            );
        }

        return this.covariance() / denominator;
    }

    isIndependent(tolerance = 1e-9) {
        const marginalX = this.marginalX();
        const marginalY = this.marginalY();

        for (const [x, px] of marginalX) {
            for (const [y, py] of marginalY) {
                const actual = this.getJointProbability(x, y);
                const expected = px * py;

                if (Math.abs(actual - expected) > tolerance) {
                    return false;
                }
            }
        }

        return true;
    }

    report() {
        console.log("\nJoint PMF");

        for (const outcome of this.pmf.values()) {
            console.log(
                `P(X=${outcome.x}, Y=${outcome.y}) = ` +
                outcome.probability.toFixed(4)
            );
        }

        console.log("\nMarginal X:", Object.fromEntries(this.marginalX()));
        console.log("Marginal Y:", Object.fromEntries(this.marginalY()));

        console.log("\nConditional P(Y | X=1):",
            Object.fromEntries(this.conditionalYGivenX(1)));

        console.log("\nStatistical measures");

        console.log("E[X]:", this.expectedX().toFixed(6));
        console.log("E[Y]:", this.expectedY().toFixed(6));
        console.log("Var(X):", this.varianceX().toFixed(6));
        console.log("Var(Y):", this.varianceY().toFixed(6));
        console.log("E[XY]:", this.expectedXY().toFixed(6));
        console.log("Covariance:", this.covariance().toFixed(6));
        console.log("Correlation:", this.correlation().toFixed(6));
        console.log("Independent:", this.isIndependent());
    }
}

class BivariateNormal {
    constructor({
        meanX,
        meanY,
        sigmaX,
        sigmaY,
        rho
    }) {
        const values = [meanX, meanY, sigmaX, sigmaY, rho];

        if (!values.every(Number.isFinite)) {
            throw new DistributionError(
                "Parameters must be finite."
            );
        }

        if (sigmaX <= 0 || sigmaY <= 0) {
            throw new DistributionError(
                "Standard deviations must be positive."
            );
        }

        if (rho <= -1 || rho >= 1) {
            throw new DistributionError(
                "Correlation must be between -1 and 1."
            );
        }

        Object.assign(this, {
            meanX,
            meanY,
            sigmaX,
            sigmaY,
            rho
        });

        Object.freeze(this);
    }

    pdf(x, y) {
        if (!Number.isFinite(x) || !Number.isFinite(y)) {
            throw new DistributionError(
                "PDF evaluation requires finite inputs."
            );
        }

        const zx = (x - this.meanX) / this.sigmaX;
        const zy = (y - this.meanY) / this.sigmaY;

        const exponent = -(
            zx ** 2 -
            2 * this.rho * zx * zy +
            zy ** 2
        ) / (2 * (1 - this.rho ** 2));

        const denominator =
            2 * Math.PI *
            this.sigmaX *
            this.sigmaY *
            Math.sqrt(1 - this.rho ** 2);

        return Math.exp(exponent) / denominator;
    }

    marginalXPDF(x) {
        const z = (x - this.meanX) / this.sigmaX;

        return Math.exp(-0.5 * z ** 2) /
            (this.sigmaX * Math.sqrt(2 * Math.PI));
    }

    marginalYPDF(y) {
        const z = (y - this.meanY) / this.sigmaY;

        return Math.exp(-0.5 * z ** 2) /
            (this.sigmaY * Math.sqrt(2 * Math.PI));
    }

    covariance() {
        return this.rho * this.sigmaX * this.sigmaY;
    }
}

class DistributionEventEmitter {
    constructor() {
        this.listeners = new Map();
    }

    on(event, callback) {
        if (typeof callback !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }

        this.listeners.get(event).add(callback);
    }

    emit(event, payload) {
        for (const callback of this.listeners.get(event) ?? []) {
            callback(payload);
        }
    }

    removeAllListeners() {
        this.listeners.clear();
    }
}

async function runAnalysis() {
    const emitter = new DistributionEventEmitter();

    emitter.on("analysis-completed", (result) => {
        console.log("\nEvent:", result.message);
    });

    const distribution = new JointDistribution([
        { x: 0, y: 0, probability: 0.10 },
        { x: 0, y: 1, probability: 0.15 },
        { x: 1, y: 0, probability: 0.20 },
        { x: 1, y: 1, probability: 0.30 },
        { x: 2, y: 0, probability: 0.05 },
        { x: 2, y: 1, probability: 0.20 }
    ]);

    distribution.report();

    const normal = new BivariateNormal({
        meanX: 70,
        meanY: 75,
        sigmaX: 10,
        sigmaY: 12,
        rho: 0.65
    });

    console.log("\nContinuous Joint Distribution");
    console.log("Joint PDF:", normal.pdf(70, 75).toFixed(8));
    console.log("Marginal X PDF:", normal.marginalXPDF(70).toFixed(8));
    console.log("Marginal Y PDF:", normal.marginalYPDF(75).toFixed(8));
    console.log("Covariance:", normal.covariance().toFixed(4));

    emitter.emit("analysis-completed", {
        message: "Joint distribution analysis completed."
    });

    emitter.removeAllListeners();
}

function runTests() {
    const independent = new JointDistribution([
        { x: 0, y: 0, probability: 0.25 },
        { x: 0, y: 1, probability: 0.25 },
        { x: 1, y: 0, probability: 0.25 },
        { x: 1, y: 1, probability: 0.25 }
    ]);

    assert.ok(Math.abs(independent.expectedX() - 0.5) < 1e-10);
    assert.ok(Math.abs(independent.expectedY() - 0.5) < 1e-10);
    assert.ok(Math.abs(independent.varianceX() - 0.25) < 1e-10);
    assert.ok(Math.abs(independent.covariance()) < 1e-10);
    assert.equal(independent.isIndependent(), true);

    const dependent = new JointDistribution([
        { x: 0, y: 0, probability: 0.5 },
        { x: 1, y: 1, probability: 0.5 }
    ]);

    assert.equal(dependent.isIndependent(), false);
    assert.ok(Math.abs(dependent.correlation() - 1) < 1e-10);

    assert.throws(() => new JointDistribution([
        { x: 0, y: 0, probability: 0.4 },
        { x: 1, y: 1, probability: 0.4 }
    ]), DistributionError);

    assert.throws(
        () => independent.conditionalYGivenX(5),
        DistributionError
    );

    assert.throws(
        () => new BivariateNormal({
            meanX: 0,
            meanY: 0,
            sigmaX: 1,
            sigmaY: 1,
            rho: 1
        }),
        DistributionError
    );

    console.log("\nAll JavaScript tests passed.");
}

async function main() {
    try {
        await runAnalysis();
        runTests();
    } catch (error) {
        console.error(
            `[ANALYSIS ERROR] ${error.name}: ${error.message}`
        );
        process.exitCode = 1;
    }
}

main();
