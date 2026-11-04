"use strict";

/*
 * EXPECTED VALUE AND MOMENTS
 *
 * JavaScript implementation focused on:
 * - Financial risk evaluation
 * - Probability-weighted cash flows
 * - Expected value and variance
 * - Standard deviation
 * - Raw and central moments
 * - Skewness and kurtosis
 * - Conditional expectation
 * - Joint distributions
 * - Monte Carlo simulation
 * - Event-driven statistical processing
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProbabilityError";
    }
}

class Distribution {
    constructor(name, outcomes, tolerance = 1e-9) {
        if (typeof name !== "string" || !name.trim()) {
            throw new TypeError("Distribution name is required.");
        }

        if (!Array.isArray(outcomes) || outcomes.length === 0) {
            throw new ProbabilityError("Outcomes cannot be empty.");
        }

        if (!Number.isFinite(tolerance) || tolerance <= 0) {
            throw new ProbabilityError("Invalid tolerance.");
        }

        this.name = name;
        this.tolerance = tolerance;

        this.outcomes = Object.freeze(
            outcomes.map((item) => {
                if (
                    !Number.isFinite(item.value) ||
                    !Number.isFinite(item.probability)
                ) {
                    throw new ProbabilityError(
                        "Outcome values and probabilities must be finite."
                    );
                }

                if (item.probability < 0 || item.probability > 1) {
                    throw new ProbabilityError(
                        "Probability must be between 0 and 1."
                    );
                }

                return Object.freeze({
                    value: item.value,
                    probability: item.probability
                });
            })
        );

        const total = this.outcomes.reduce(
            (sum, item) => sum + item.probability,
            0
        );

        if (Math.abs(total - 1) > tolerance) {
            throw new ProbabilityError(
                `Probabilities must sum to 1. Received ${total}.`
            );
        }
    }

    expectation(transform = (value) => value) {
        let result = 0;

        for (const item of this.outcomes) {
            const transformed = transform(item.value);

            if (!Number.isFinite(transformed)) {
                throw new Error("Transformation produced an invalid value.");
            }

            result += transformed * item.probability;
        }

        return result;
    }

    mean() {
        return this.expectation();
    }

    rawMoment(order) {
        if (!Number.isInteger(order) || order < 0) {
            throw new RangeError("Moment order must be non-negative.");
        }

        return this.expectation((value) => value ** order);
    }

    centralMoment(order) {
        if (!Number.isInteger(order) || order < 0) {
            throw new RangeError("Moment order must be non-negative.");
        }

        const mean = this.mean();

        return this.expectation(
            (value) => (value - mean) ** order
        );
    }

    variance() {
        return Math.max(0, this.centralMoment(2));
    }

    standardDeviation() {
        return Math.sqrt(this.variance());
    }

    skewness() {
        const variance = this.variance();

        if (variance === 0) return null;

        return this.centralMoment(3) / variance ** 1.5;
    }

    kurtosis() {
        const variance = this.variance();

        if (variance === 0) return null;

        return this.centralMoment(4) / variance ** 2;
    }

    probabilityWhere(predicate) {
        if (typeof predicate !== "function") {
            throw new TypeError("A predicate function is required.");
        }

        return this.outcomes.reduce(
            (sum, item) =>
                sum + (predicate(item.value) ? item.probability : 0),
            0
        );
    }

    conditionalExpectation(predicate) {
        const probability = this.probabilityWhere(predicate);

        if (probability <= this.tolerance) {
            throw new ProbabilityError(
                "Conditional event has zero probability."
            );
        }

        return this.outcomes.reduce(
            (sum, item) =>
                sum + (
                    predicate(item.value)
                        ? item.value * item.probability
                        : 0
                ),
            0
        ) / probability;
    }

    describe() {
        return Object.freeze({
            name: this.name,
            expectedValue: this.mean(),
            variance: this.variance(),
            standardDeviation: this.standardDeviation(),
            skewness: this.skewness(),
            kurtosis: this.kurtosis(),
            rawMoments: Object.fromEntries(
                [1, 2, 3, 4].map(
                    (order) => [order, this.rawMoment(order)]
                )
            ),
            centralMoments: Object.fromEntries(
                [1, 2, 3, 4].map(
                    (order) => [order, this.centralMoment(order)]
                )
            )
        });
    }
}

class JointDistribution {
    constructor(records) {
        if (!Array.isArray(records) || records.length === 0) {
            throw new ProbabilityError("Joint records cannot be empty.");
        }

        this.records = records.map((record) => {
            const { x, y, probability } = record;

            if (![x, y, probability].every(Number.isFinite)) {
                throw new ProbabilityError("Invalid joint record.");
            }

            if (probability < 0 || probability > 1) {
                throw new ProbabilityError("Invalid joint probability.");
            }

            return Object.freeze({ x, y, probability });
        });

        const total = this.records.reduce(
            (sum, record) => sum + record.probability,
            0
        );

        if (Math.abs(total - 1) > 1e-9) {
            throw new ProbabilityError(
                "Joint probabilities must sum to 1."
            );
        }
    }

    covariance() {
        const meanX = this.records.reduce(
            (sum, r) => sum + r.x * r.probability,
            0
        );

        const meanY = this.records.reduce(
            (sum, r) => sum + r.y * r.probability,
            0
        );

        return this.records.reduce(
            (sum, r) =>
                sum + (
                    (r.x - meanX) *
                    (r.y - meanY) *
                    r.probability
                ),
            0
        );
    }

    correlation() {
        const meanX = this.records.reduce(
            (sum, r) => sum + r.x * r.probability,
            0
        );

        const meanY = this.records.reduce(
            (sum, r) => sum + r.y * r.probability,
            0
        );

        const varianceX = this.records.reduce(
            (sum, r) => sum + (r.x - meanX) ** 2 * r.probability,
            0
        );

        const varianceY = this.records.reduce(
            (sum, r) => sum + (r.y - meanY) ** 2 * r.probability,
            0
        );

        if (varianceX === 0 || varianceY === 0) {
            return null;
        }

        return this.covariance() /
            Math.sqrt(varianceX * varianceY);
    }
}

class RandomGenerator {
    constructor(seed = 123456789) {
        this.state = seed >>> 0;
    }

    next() {
        // Deterministic linear congruential generator.
        this.state = (
            Math.imul(1664525, this.state) + 1013904223
        ) >>> 0;

        return this.state / 4294967296;
    }
}

class MonteCarloEngine {
    constructor(distribution, seed = 12345) {
        this.distribution = distribution;
        this.random = new RandomGenerator(seed);
    }

    run(trials) {
        if (!Number.isSafeInteger(trials) || trials <= 0) {
            throw new RangeError("Trials must be a positive safe integer.");
        }

        const cumulative = [];
        let probability = 0;

        for (const item of this.distribution.outcomes) {
            probability += item.probability;
            cumulative.push({
                limit: probability,
                value: item.value
            });
        }

        let sum = 0;
        let sumSquares = 0;

        for (let i = 0; i < trials; i++) {
            const randomValue = this.random.next();

            const selected = cumulative.find(
                (item) => randomValue < item.limit
            ) || cumulative[cumulative.length - 1];

            sum += selected.value;
            sumSquares += selected.value ** 2;
        }

        const mean = sum / trials;
        const variance = Math.max(
            0,
            sumSquares / trials - mean ** 2
        );

        return Object.freeze({
            trials,
            estimatedMean: mean,
            theoreticalMean: this.distribution.mean(),
            absoluteError: Math.abs(
                mean - this.distribution.mean()
            ),
            estimatedVariance: variance,
            estimatedStandardDeviation: Math.sqrt(variance)
        });
    }
}

class RiskAssessmentService extends EventEmitter {
    constructor() {
        super();
        this.results = new Map();
    }

    async assess(distribution, simulationTrials = 50000) {
        if (!(distribution instanceof Distribution)) {
            throw new TypeError("A valid Distribution is required.");
        }

        const result = distribution.describe();

        const simulation = new MonteCarloEngine(
            distribution
        ).run(simulationTrials);

        const report = Object.freeze({
            ...result,
            simulation
        });

        this.results.set(distribution.name, report);

        this.emit("assessmentCompleted", report);

        return report;
    }

    getReport(name) {
        return this.results.get(name) || null;
    }
}

async function main() {
    console.log("EXPECTED VALUE AND MOMENTS");
    console.log("=".repeat(55));

    const die = new Distribution(
        "Fair Die",
        Array.from({ length: 6 }, (_, i) => ({
            value: i + 1,
            probability: 1 / 6
        }))
    );

    const investment = new Distribution(
        "Investment Risk",
        [
            { value: -1000, probability: 0.10 },
            { value: -200, probability: 0.20 },
            { value: 300, probability: 0.40 },
            { value: 1000, probability: 0.20 },
            { value: 2500, probability: 0.10 }
        ]
    );

    const service = new RiskAssessmentService();

    service.on("assessmentCompleted", (report) => {
        console.log(`\nAssessment completed: ${report.name}`);
    });

    const dieReport = await service.assess(die, 100000);
    const investmentReport = await service.assess(investment, 100000);

    console.log("\nDie statistics:");
    console.log(JSON.stringify(dieReport, null, 2));

    console.log("\nInvestment statistics:");
    console.log(JSON.stringify(investmentReport, null, 2));

    console.log(
        "\nProbability of positive investment return:",
        investment.probabilityWhere((value) => value > 0)
    );

    console.log(
        "Conditional expected positive return:",
        investment.conditionalExpectation((value) => value > 0)
    );

    const joint = new JointDistribution([
        { x: 10, y: 20, probability: 0.20 },
        { x: 20, y: 30, probability: 0.30 },
        { x: 30, y: 20, probability: 0.10 },
        { x: 40, y: 50, probability: 0.40 }
    ]);

    console.log("\nJoint distribution:");
    console.log("Covariance:", joint.covariance());
    console.log("Correlation:", joint.correlation());

    console.log("\nEdge cases:");

    const constant = new Distribution(
        "Constant",
        [{ value: 50, probability: 1 }]
    );

    console.log("Constant variance:", constant.variance());
    console.log("Constant skewness:", constant.skewness());

    try {
        new Distribution("Invalid", [
            { value: 1, probability: 0.4 },
            { value: 2, probability: 0.3 }
        ]);
    } catch (error) {
        console.log("Validation correctly rejected:", error.message);
    }

    try {
        investment.conditionalExpectation(
            (value) => value > 10000
        );
    } catch (error) {
        console.log("Conditional failure handled:", error.message);
    }

    console.log("\nAll demonstrations completed.");
}

main().catch((error) => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
