"use strict";

/*
 * HYPOTHESIS TESTING
 *
 * Event-driven statistical testing and decision evaluation.
 *
 * Features:
 * - Null and alternative hypotheses
 * - One-sample Z-tests
 * - Two-sided and one-sided p-values
 * - Statistical significance
 * - Confidence intervals
 * - Bonferroni correction
 * - Sequential experiment state management
 * - Asynchronous test execution
 * - Validation and event-driven reporting
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");

const Alternative = Object.freeze({
    TWO_SIDED: "two-sided",
    GREATER: "greater",
    LESS: "less"
});

const ExperimentState = Object.freeze({
    CREATED: "CREATED",
    RUNNING: "RUNNING",
    COMPLETED: "COMPLETED",
    FAILED: "FAILED"
});

class StatisticalError extends Error {
    constructor(message) {
        super(message);
        this.name = "StatisticalError";
    }
}

function validateProbability(value, name) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value <= 0 ||
        value >= 1
    ) {
        throw new StatisticalError(
            `${name} must be between 0 and 1.`
        );
    }
}

function validateObservations(observations) {
    if (!Array.isArray(observations) || observations.length < 2) {
        throw new StatisticalError(
            "At least two observations are required."
        );
    }

    for (const value of observations) {
        if (!Number.isFinite(value)) {
            throw new StatisticalError(
                "All observations must be finite numbers."
            );
        }
    }
}

function normalCDF(z) {
    // Abramowitz-Stegun approximation.
    const sign = z < 0 ? -1 : 1;
    const x = Math.abs(z);

    const t = 1 / (1 + 0.2316419 * x);

    const polynomial =
        t * (
            0.319381530 +
            t * (
                -0.356563782 +
                t * (
                    1.781477937 +
                    t * (
                        -1.821255978 +
                        t * 1.330274429
                    )
                )
            )
        );

    const density =
        Math.exp(-0.5 * x * x) /
        Math.sqrt(2 * Math.PI);

    const positiveCDF = 1 - density * polynomial;

    return sign === 1 ? positiveCDF : 1 - positiveCDF;
}

function calculatePValue(z, alternative) {
    switch (alternative) {
        case Alternative.TWO_SIDED:
            return Math.min(
                1,
                2 * (1 - normalCDF(Math.abs(z)))
            );

        case Alternative.GREATER:
            return 1 - normalCDF(z);

        case Alternative.LESS:
            return normalCDF(z);

        default:
            throw new StatisticalError(
                "Unsupported alternative hypothesis."
            );
    }
}

function calculateCriticalZ(alpha) {
    // Binary search for the upper standard-normal quantile.
    let low = 0;
    let high = 10;
    const target = alpha / 2;

    for (let i = 0; i < 80; i++) {
        const mid = (low + high) / 2;

        if (1 - normalCDF(mid) > target) {
            low = mid;
        } else {
            high = mid;
        }
    }

    return (low + high) / 2;
}

class HypothesisTest {
    constructor({
        nullMean,
        sigma,
        alpha = 0.05,
        alternative = Alternative.TWO_SIDED
    }) {
        if (!Number.isFinite(nullMean)) {
            throw new StatisticalError(
                "Null mean must be finite."
            );
        }

        if (!Number.isFinite(sigma) || sigma <= 0) {
            throw new StatisticalError(
                "Population standard deviation must be positive."
            );
        }

        validateProbability(alpha, "Alpha");

        if (!Object.values(Alternative).includes(alternative)) {
            throw new StatisticalError(
                "Invalid alternative hypothesis."
            );
        }

        this.nullMean = nullMean;
        this.sigma = sigma;
        this.alpha = alpha;
        this.alternative = alternative;
    }

    execute(observations) {
        validateObservations(observations);

        const n = observations.length;

        const mean =
            observations.reduce((sum, x) => sum + x, 0) / n;

        const standardError = this.sigma / Math.sqrt(n);

        const z = (
            mean - this.nullMean
        ) / standardError;

        const pValue = calculatePValue(
            z,
            this.alternative
        );

        const critical = calculateCriticalZ(this.alpha);

        const margin = critical * standardError;

        return Object.freeze({
            sampleSize: n,
            sampleMean: mean,
            nullMean: this.nullMean,
            standardError,
            zStatistic: z,
            pValue,
            alpha: this.alpha,
            alternative: this.alternative,
            confidenceInterval: Object.freeze([
                mean - margin,
                mean + margin
            ]),
            significant: pValue <= this.alpha,
            decision: pValue <= this.alpha
                ? "REJECT_NULL"
                : "FAIL_TO_REJECT_NULL"
        });
    }
}

class MultipleTesting {
    static bonferroni(pValues, alpha = 0.05) {
        validateProbability(alpha, "Alpha");

        if (!Array.isArray(pValues) || pValues.length === 0) {
            throw new StatisticalError(
                "At least one p-value is required."
            );
        }

        for (const p of pValues) {
            if (!Number.isFinite(p) || p < 0 || p > 1) {
                throw new StatisticalError(
                    "Invalid p-value."
                );
            }
        }

        const threshold = alpha / pValues.length;

        return pValues.map((p, index) => ({
            test: index + 1,
            originalPValue: p,
            adjustedPValue: Math.min(
                1,
                p * pValues.length
            ),
            threshold,
            significant: p <= threshold
        }));
    }
}

class Experiment extends EventEmitter {
    constructor(id, test, observations) {
        super();

        if (!id || typeof id !== "string") {
            throw new StatisticalError(
                "Experiment ID is required."
            );
        }

        this.id = id;
        this.test = test;
        this.observations = Object.freeze([...observations]);
        this.state = ExperimentState.CREATED;
        this.result = null;
        this.error = null;
    }

    async run() {
        if (this.state !== ExperimentState.CREATED) {
            throw new StatisticalError(
                "Experiment can only run once."
            );
        }

        this.state = ExperimentState.RUNNING;
        this.emit("started", { id: this.id });

        try {
            // Promise boundary allows asynchronous orchestration.
            const result = await Promise.resolve().then(
                () => this.test.execute(this.observations)
            );

            this.result = result;
            this.state = ExperimentState.COMPLETED;

            this.emit("completed", {
                id: this.id,
                result
            });

            return result;
        } catch (error) {
            this.error = error.message;
            this.state = ExperimentState.FAILED;

            this.emit("failed", {
                id: this.id,
                error: error.message
            });

            throw error;
        }
    }
}

class ExperimentRegistry {
    constructor() {
        this.experiments = new Map();
    }

    register(experiment) {
        if (!(experiment instanceof Experiment)) {
            throw new StatisticalError(
                "Invalid experiment object."
            );
        }

        if (this.experiments.has(experiment.id)) {
            throw new StatisticalError(
                "Duplicate experiment ID."
            );
        }

        this.experiments.set(experiment.id, experiment);
    }

    get(id) {
        return this.experiments.get(id) ?? null;
    }

    async executeAll() {
        const experiments = [...this.experiments.values()];

        // Independent experiments can execute concurrently.
        return Promise.allSettled(
            experiments.map(experiment => experiment.run())
        );
    }

    report() {
        return [...this.experiments.values()].map(experiment => ({
            id: experiment.id,
            state: experiment.state,
            pValue: experiment.result?.pValue ?? null,
            decision: experiment.result?.decision ?? null
        }));
    }
}

async function main() {
    const observations = [
        104, 108, 102, 107, 105,
        110, 106, 103, 109, 107,
        105, 108, 111, 104, 106,
        109, 107, 105, 110, 108
    ];

    const test = new HypothesisTest({
        nullMean: 100,
        sigma: 8,
        alpha: 0.05,
        alternative: Alternative.TWO_SIDED
    });

    const experiment = new Experiment(
        "MANUFACTURING-QUALITY-001",
        test,
        observations
    );

    experiment.on("started", event => {
        console.log("Experiment started:", event.id);
    });

    experiment.on("completed", event => {
        console.log("Experiment completed:", event.id);
        console.log("P-value:", event.result.pValue);
        console.log("Decision:", event.result.decision);
    });

    experiment.on("failed", event => {
        console.error("Experiment failed:", event.error);
    });

    const registry = new ExperimentRegistry();

    registry.register(experiment);

    await registry.executeAll();

    console.log("\nEXPERIMENT REGISTRY");
    console.table(registry.report());

    console.log("\nMULTIPLE TESTING");
    console.table(
        MultipleTesting.bonferroni(
            [0.001, 0.018, 0.032, 0.12, 0.40],
            0.05
        )
    );

    console.log("\nVALIDATION");

    try {
        new HypothesisTest({
            nullMean: 100,
            sigma: -2
        });
    } catch (error) {
        console.log("Invalid configuration rejected:", error.message);
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error("Application error:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    Alternative,
    ExperimentState,
    HypothesisTest,
    MultipleTesting,
    Experiment,
    ExperimentRegistry,
    normalCDF,
    calculatePValue
};
