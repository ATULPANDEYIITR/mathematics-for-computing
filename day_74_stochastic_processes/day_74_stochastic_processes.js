"use strict";

/*
 * STOCHASTIC PROCESSES
 * Event-driven Markov chain and random-walk simulation.
 * Runtime: Node.js 18+
 */

const fs = require("node:fs/promises");
const { EventEmitter } = require("node:events");

class StochasticError extends Error {}
class ValidationError extends StochasticError {}
class SimulationError extends StochasticError {}

const ProcessState = Object.freeze({
    CREATED: "CREATED",
    RUNNING: "RUNNING",
    COMPLETED: "COMPLETED",
    ABSORBED: "ABSORBED",
    FAILED: "FAILED"
});

function validateProbability(value) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0 ||
        value > 1
    ) {
        throw new ValidationError(
            `Invalid probability: ${value}`
        );
    }
}

function validateSteps(steps) {
    if (!Number.isSafeInteger(steps) || steps < 0) {
        throw new ValidationError(
            "Steps must be a non-negative safe integer."
        );
    }
}

/*
 * Seeded random generator.
 * A separate generator per experiment ensures reproducibility.
 */
class RandomGenerator {
    constructor(seed = 42) {
        if (!Number.isSafeInteger(seed)) {
            throw new ValidationError("Seed must be a safe integer.");
        }

        this.state = seed >>> 0;
    }

    next() {
        this.state = (this.state + 0x6D2B79F5) >>> 0;

        let value = this.state;

        value = Math.imul(
            value ^ (value >>> 15),
            value | 1
        );

        value ^= value + Math.imul(
            value ^ (value >>> 7),
            value | 61
        );

        return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    }

    integer(maximum) {
        if (!Number.isSafeInteger(maximum) || maximum <= 0) {
            throw new ValidationError("Invalid random integer limit.");
        }

        return Math.floor(this.next() * maximum);
    }
}

class TransitionModel {
    constructor(configuration) {
        if (
            configuration === null ||
            typeof configuration !== "object" ||
            Object.keys(configuration).length === 0
        ) {
            throw new ValidationError("Transition model cannot be empty.");
        }

        this.matrix = new Map();

        for (const [source, destinations] of Object.entries(configuration)) {
            if (
                typeof source !== "string" ||
                source.trim() === "" ||
                destinations === null ||
                typeof destinations !== "object" ||
                Object.keys(destinations).length === 0
            ) {
                throw new ValidationError("Invalid transition definition.");
            }

            const edges = new Map();
            let total = 0;

            for (const [destination, probability] of Object.entries(destinations)) {
                validateProbability(probability);

                edges.set(destination, probability);
                total += probability;
            }

            if (Math.abs(total - 1) > 1e-9) {
                throw new ValidationError(
                    `Probabilities from ${source} sum to ${total}.`
                );
            }

            this.matrix.set(source, edges);
        }

        for (const edges of this.matrix.values()) {
            for (const destination of edges.keys()) {
                if (!this.matrix.has(destination)) {
                    throw new ValidationError(
                        `Undefined destination: ${destination}`
                    );
                }
            }
        }

        Object.freeze(this);
    }

    get states() {
        return [...this.matrix.keys()];
    }

    isAbsorbing(state) {
        const edges = this.matrix.get(state);

        if (!edges) {
            throw new ValidationError(`Unknown state: ${state}`);
        }

        return (
            edges.size === 1 &&
            Math.abs(edges.get(state) - 1) < 1e-9
        );
    }

    transition(state, random) {
        const edges = this.matrix.get(state);

        if (!edges) {
            throw new ValidationError(`Unknown state: ${state}`);
        }

        const value = random.next();
        let cumulative = 0;

        for (const [destination, probability] of edges) {
            cumulative += probability;

            if (value < cumulative) {
                return destination;
            }
        }

        // Protect against floating-point accumulation at the upper bound.
        return [...edges.keys()].at(-1);
    }

    getTransitionMatrix() {
        const states = this.states;

        return states.map(source =>
            states.map(destination =>
                this.matrix.get(source).get(destination) || 0
            )
        );
    }
}

class SimulationEngine extends EventEmitter {
    constructor(model) {
        super();

        if (!(model instanceof TransitionModel)) {
            throw new ValidationError("A transition model is required.");
        }

        this.model = model;
        this.activeRuns = new Set();
    }

    async run({
        initialState,
        steps,
        seed = 42,
        delay = 0,
        signal = null
    }) {
        validateSteps(steps);

        if (!this.model.matrix.has(initialState)) {
            throw new ValidationError("Unknown initial state.");
        }

        if (!Number.isFinite(delay) || delay < 0 || delay > 10000) {
            throw new ValidationError("Delay must be between 0 and 10000 ms.");
        }

        const runId = `${seed}-${Date.now()}-${this.activeRuns.size}`;

        if (this.activeRuns.has(runId)) {
            throw new SimulationError("Duplicate simulation identifier.");
        }

        this.activeRuns.add(runId);

        const random = new RandomGenerator(seed);
        const path = [initialState];

        let current = initialState;
        let status = ProcessState.RUNNING;

        this.emit("started", {
            runId,
            initialState,
            steps
        });

        try {
            for (let index = 0; index < steps; index++) {
                if (signal?.aborted) {
                    throw new SimulationError("Simulation cancelled.");
                }

                if (this.model.isAbsorbing(current)) {
                    status = ProcessState.ABSORBED;
                    break;
                }

                const previous = current;
                current = this.model.transition(current, random);

                path.push(current);

                const event = Object.freeze({
                    runId,
                    step: index + 1,
                    previous,
                    current
                });

                this.emit("transition", event);

                if (delay > 0) {
                    await new Promise(resolve =>
                        setTimeout(resolve, delay)
                    );
                }
            }

            if (
                status === ProcessState.RUNNING &&
                this.model.isAbsorbing(current)
            ) {
                status = ProcessState.ABSORBED;
            } else if (status === ProcessState.RUNNING) {
                status = ProcessState.COMPLETED;
            }

            const result = Object.freeze({
                runId,
                initialState,
                finalState: current,
                path: Object.freeze([...path]),
                stepsExecuted: path.length - 1,
                status,
                seed
            });

            this.emit("completed", result);

            return result;
        } catch (error) {
            status = ProcessState.FAILED;

            this.emit("failed", {
                runId,
                status,
                message: error.message
            });

            throw error;
        } finally {
            this.activeRuns.delete(runId);
        }
    }
}

class RandomWalkAnalyzer {
    constructor(upProbability = 0.5) {
        validateProbability(upProbability);
        this.upProbability = upProbability;
    }

    simulate({
        start = 0,
        steps,
        lower = null,
        upper = null,
        seed = 42
    }) {
        validateSteps(steps);

        if (!Number.isSafeInteger(start)) {
            throw new ValidationError("Starting position must be an integer.");
        }

        if (
            lower !== null &&
            !Number.isSafeInteger(lower)
        ) {
            throw new ValidationError("Lower boundary must be an integer.");
        }

        if (
            upper !== null &&
            !Number.isSafeInteger(upper)
        ) {
            throw new ValidationError("Upper boundary must be an integer.");
        }

        if (
            lower !== null &&
            upper !== null &&
            lower >= upper
        ) {
            throw new ValidationError("Invalid boundaries.");
        }

        if (
            (lower !== null && start < lower) ||
            (upper !== null && start > upper)
        ) {
            throw new ValidationError("Starting position outside boundaries.");
        }

        const random = new RandomGenerator(seed);
        const path = [start];

        let position = start;

        for (let i = 0; i < steps; i++) {
            if (
                position === lower ||
                position === upper
            ) {
                break;
            }

            position += random.next() < this.upProbability ? 1 : -1;
            path.push(position);
        }

        return Object.freeze({
            path: Object.freeze(path),
            finalPosition: position,
            stepsExecuted: path.length - 1,
            absorbed: position === lower || position === upper
        });
    }
}

class StatisticalAnalyzer {
    static analyze(values) {
        if (!Array.isArray(values) || values.length === 0) {
            throw new ValidationError("A non-empty numeric array is required.");
        }

        if (!values.every(Number.isFinite)) {
            throw new ValidationError("All observations must be finite.");
        }

        const count = values.length;
        const mean = values.reduce((a, b) => a + b, 0) / count;

        const variance = values.reduce(
            (sum, value) => sum + (value - mean) ** 2,
            0
        ) / count;

        const sorted = [...values].sort((a, b) => a - b);

        return Object.freeze({
            count,
            mean,
            populationVariance: variance,
            standardDeviation: Math.sqrt(variance),
            minimum: sorted[0],
            maximum: sorted[count - 1],
            median: (
                count % 2 === 0
                    ? (sorted[count / 2 - 1] + sorted[count / 2]) / 2
                    : sorted[Math.floor(count / 2)]
            )
        });
    }
}

async function monteCarloAbsorption({
    model,
    initialState,
    absorbingState,
    experiments = 1000,
    maximumSteps = 100,
    seed = 42
}) {
    if (!Number.isSafeInteger(experiments) || experiments <= 0) {
        throw new ValidationError("Experiments must be positive.");
    }

    validateSteps(maximumSteps);

    if (!model.isAbsorbing(absorbingState)) {
        throw new ValidationError("Target must be absorbing.");
    }

    const engine = new SimulationEngine(model);
    const random = new RandomGenerator(seed);

    let successes = 0;
    const times = [];

    for (let i = 0; i < experiments; i++) {
        const experimentSeed = random.integer(2147483647);

        const result = await engine.run({
            initialState,
            steps: maximumSteps,
            seed: experimentSeed
        });

        if (result.finalState === absorbingState) {
            successes++;
            times.push(result.stepsExecuted);
        }
    }

    const probability = successes / experiments;
    const standardError = Math.sqrt(
        probability * (1 - probability) / experiments
    );

    return {
        experiments,
        successes,
        estimatedProbability: probability,
        standardError,
        confidenceInterval95: [
            Math.max(0, probability - 1.96 * standardError),
            Math.min(1, probability + 1.96 * standardError)
        ],
        meanAbsorptionTime: times.length
            ? times.reduce((a, b) => a + b, 0) / times.length
            : null
    };
}

function createReliabilityModel() {
    return new TransitionModel({
        OPERATIONAL: {
            OPERATIONAL: 0.65,
            DEGRADED: 0.25,
            FAILED: 0.10
        },
        DEGRADED: {
            OPERATIONAL: 0.30,
            DEGRADED: 0.40,
            FAILED: 0.30
        },
        FAILED: {
            FAILED: 1.0
        }
    });
}

async function main() {
    console.log("STOCHASTIC PROCESSES LABORATORY");
    console.log("================================");

    const weather = new TransitionModel({
        SUNNY: {
            SUNNY: 0.70,
            CLOUDY: 0.20,
            RAINY: 0.10
        },
        CLOUDY: {
            SUNNY: 0.30,
            CLOUDY: 0.40,
            RAINY: 0.30
        },
        RAINY: {
            SUNNY: 0.20,
            CLOUDY: 0.30,
            RAINY: 0.50
        }
    });

    const engine = new SimulationEngine(weather);

    engine.on("transition", event => {
        console.log(
            `Step ${event.step}: ${event.previous} -> ${event.current}`
        );
    });

    const weatherResult = await engine.run({
        initialState: "SUNNY",
        steps: 12,
        seed: 42
    });

    console.log("\nWeather result:", weatherResult);

    const walk = new RandomWalkAnalyzer(0.55);

    const walkResult = walk.simulate({
        start: 0,
        steps: 100,
        lower: -5,
        upper: 5,
        seed: 42
    });

    console.log("\nRandom walk:", walkResult);

    const reliability = createReliabilityModel();

    const reliabilityResult = await monteCarloAbsorption({
        model: reliability,
        initialState: "OPERATIONAL",
        absorbingState: "FAILED",
        experiments: 2000,
        maximumSteps: 100,
        seed: 12345
    });

    console.log("\nReliability analysis:", reliabilityResult);

    const statistics = StatisticalAnalyzer.analyze(
        walkResult.path
    );

    console.log("\nPath statistics:", statistics);

    const report = {
        weatherResult,
        walkResult,
        reliabilityResult,
        pathStatistics: statistics
    };

    await fs.writeFile(
        "stochastic_report.json",
        JSON.stringify(report, null, 2),
        { encoding: "utf8", mode: 0o600 }
    );

    console.log("\nReport saved to stochastic_report.json");
}

async function runTests() {
    const model = new TransitionModel({
        A: { A: 0.5, B: 0.5 },
        B: { A: 0.25, B: 0.75 }
    });

    const engine = new SimulationEngine(model);

    const first = await engine.run({
        initialState: "A",
        steps: 20,
        seed: 10
    });

    const second = await engine.run({
        initialState: "A",
        steps: 20,
        seed: 10
    });

    if (JSON.stringify(first.path) !== JSON.stringify(second.path)) {
        throw new Error("Deterministic simulation test failed.");
    }

    const walk = new RandomWalkAnalyzer(1.0);

    const result = walk.simulate({
        start: 0,
        steps: 10,
        lower: -2,
        upper: 2,
        seed: 1
    });

    if (result.finalPosition !== 2 || !result.absorbed) {
        throw new Error("Absorbing random walk test failed.");
    }

    const analysis = StatisticalAnalyzer.analyze([1, 2, 3, 4, 5]);

    if (analysis.mean !== 3 || analysis.populationVariance !== 2) {
        throw new Error("Statistical analysis test failed.");
    }

    let invalidRejected = false;

    try {
        new TransitionModel({
            A: { A: 0.8, B: 0.8 },
            B: { B: 1.0 }
        });
    } catch (error) {
        invalidRejected = error instanceof ValidationError;
    }

    if (!invalidRejected) {
        throw new Error("Invalid transition matrix was accepted.");
    }

    console.log("All JavaScript validation tests passed.");
}

if (require.main === module) {
    runTests()
        .then(main)
        .catch(error => {
            console.error("Execution failed:", error.message);
            process.exitCode = 1;
        });
}

module.exports = {
    RandomGenerator,
    TransitionModel,
    SimulationEngine,
    RandomWalkAnalyzer,
    StatisticalAnalyzer,
    monteCarloAbsorption,
    ProcessState,
    ValidationError
};
