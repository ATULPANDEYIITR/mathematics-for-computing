"use strict";

/*
 * Advanced Probability
 *
 * Event-driven stochastic process engine.
 *
 * Concepts:
 * - Finite-state Markov chains
 * - Stationary distributions
 * - Ergodicity and periodicity
 * - Martingale differences
 * - Conditional expectations
 * - Online statistical estimation
 * - Asynchronous simulation
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");

// ============================================================
// 1. ERRORS AND NUMERICAL UTILITIES
// ============================================================

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProbabilityError";
    }
}

function assertFinite(value, name) {
    if (!Number.isFinite(value)) {
        throw new ProbabilityError(`${name} must be finite.`);
    }
}

function normalize(weights) {
    if (!Array.isArray(weights) || weights.length === 0) {
        throw new ProbabilityError("Weights cannot be empty.");
    }

    weights.forEach((weight, index) => {
        assertFinite(weight, `Weight ${index}`);

        if (weight < 0) {
            throw new ProbabilityError("Negative weight.");
        }
    });

    const total = weights.reduce((a, b) => a + b, 0);

    if (total <= 0) {
        throw new ProbabilityError("Total weight must be positive.");
    }

    return weights.map(weight => weight / total);
}

function dot(a, b) {
    if (a.length !== b.length) {
        throw new ProbabilityError("Vector dimensions differ.");
    }

    return a.reduce((sum, value, index) =>
        sum + value * b[index], 0);
}

function maxDifference(a, b) {
    return Math.max(
        ...a.map((value, index) => Math.abs(value - b[index]))
    );
}

// ============================================================
// 2. REPRODUCIBLE RANDOM NUMBER GENERATOR
// ============================================================

class RandomGenerator {
    constructor(seed = 2026) {
        this.state = seed >>> 0;
    }

    next() {
        // Mulberry32 deterministic pseudorandom generator.
        let value = this.state += 0x6D2B79F5;

        value = Math.imul(value ^ value >>> 15, value | 1);
        value ^= value + Math.imul(value ^ value >>> 7, value | 61);

        return ((value ^ value >>> 14) >>> 0) / 4294967296;
    }

    categorical(probabilities) {
        const value = this.next();
        let cumulative = 0;

        for (let index = 0; index < probabilities.length; index++) {
            cumulative += probabilities[index];

            if (value < cumulative) {
                return index;
            }
        }

        return probabilities.length - 1;
    }
}

// ============================================================
// 3. MARKOV CHAIN DOMAIN MODEL
// ============================================================

class MarkovModel {
    constructor(states, transitionMatrix) {
        if (!Array.isArray(states) || states.length === 0) {
            throw new ProbabilityError("States cannot be empty.");
        }

        if (new Set(states).size !== states.length) {
            throw new ProbabilityError("State names must be unique.");
        }

        if (transitionMatrix.length !== states.length) {
            throw new ProbabilityError("Matrix dimensions differ.");
        }

        this.states = Object.freeze([...states]);

        this.index = new Map(
            states.map((state, position) => [state, position])
        );

        this.matrix = transitionMatrix.map((row, i) => {
            if (!Array.isArray(row) || row.length !== states.length) {
                throw new ProbabilityError(`Invalid matrix row ${i}.`);
            }

            row.forEach((value, j) => {
                assertFinite(value, `P(${i},${j})`);

                if (value < 0 || value > 1) {
                    throw new ProbabilityError("Invalid transition.");
                }
            });

            const total = row.reduce((a, b) => a + b, 0);

            if (Math.abs(total - 1) > 1e-10) {
                throw new ProbabilityError(
                    `Transition row ${i} does not sum to one.`
                );
            }

            return Object.freeze([...row]);
        });

        Object.freeze(this.matrix);
    }

    get size() {
        return this.states.length;
    }

    getIndex(state) {
        if (!this.index.has(state)) {
            throw new ProbabilityError(`Unknown state: ${state}`);
        }

        return this.index.get(state);
    }

    transition(stateIndex, rng) {
        if (!Number.isInteger(stateIndex) ||
            stateIndex < 0 ||
            stateIndex >= this.size) {
            throw new ProbabilityError("Invalid state index.");
        }

        return rng.categorical(this.matrix[stateIndex]);
    }

    multiply(distribution) {
        if (distribution.length !== this.size) {
            throw new ProbabilityError("Distribution dimension mismatch.");
        }

        return Array.from({ length: this.size }, (_, destination) =>
            distribution.reduce(
                (sum, probability, source) =>
                    sum + probability * this.matrix[source][destination],
                0
            )
        );
    }

    stationary(tolerance = 1e-12, maxIterations = 100000) {
        if (tolerance <= 0 || maxIterations <= 0) {
            throw new ProbabilityError("Invalid iteration parameters.");
        }

        let current = Array(this.size).fill(1 / this.size);

        for (let iteration = 1; iteration <= maxIterations; iteration++) {
            const next = this.multiply(current);
            const error = maxDifference(current, next);

            current = next;

            if (error < tolerance) {
                return {
                    distribution: current,
                    iterations: iteration,
                    converged: true,
                    residual: error
                };
            }
        }

        const residual = maxDifference(current, this.multiply(current));

        return {
            distribution: current,
            iterations: maxIterations,
            converged: false,
            residual
        };
    }

    reachable(start) {
        const visited = new Set([start]);
        const queue = [start];

        for (let position = 0; position < queue.length; position++) {
            const current = queue[position];

            this.matrix[current].forEach((probability, destination) => {
                if (probability > 0 && !visited.has(destination)) {
                    visited.add(destination);
                    queue.push(destination);
                }
            });
        }

        return visited;
    }

    isIrreducible() {
        return this.states.every((_, state) =>
            this.reachable(state).size === this.size
        );
    }

    period(start = 0) {
        const distances = new Array(this.size).fill(-1);
        const queue = [start];

        distances[start] = 0;

        for (let position = 0; position < queue.length; position++) {
            const current = queue[position];

            this.matrix[current].forEach((probability, destination) => {
                if (probability > 0 && distances[destination] === -1) {
                    distances[destination] = distances[current] + 1;
                    queue.push(destination);
                }
            });
        }

        if (distances.some(distance => distance < 0)) {
            throw new ProbabilityError(
                "Period requires an irreducible chain."
            );
        }

        const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);

        let result = 0;

        this.matrix.forEach((row, source) => {
            row.forEach((probability, destination) => {
                if (probability > 0) {
                    const difference = Math.abs(
                        distances[source] + 1 - distances[destination]
                    );

                    result = gcd(result, difference);
                }
            });
        });

        return result;
    }

    classify() {
        if (!this.isIrreducible()) {
            return "reducible";
        }

        return this.period() === 1
            ? "ergodic"
            : "irreducible_periodic";
    }
}

// ============================================================
// 4. MARTINGALE REWARD PROCESS
// ============================================================

class MartingaleProcess {
    constructor(model, rewardFunction) {
        this.model = model;
        this.rewardFunction = rewardFunction;

        this.conditionalMeans = model.matrix.map((row, state) =>
            row.reduce(
                (sum, probability, destination) =>
                    sum + probability *
                    rewardFunction(state, destination),
                0
            )
        );
    }

    increment(source, destination) {
        return this.rewardFunction(source, destination)
            - this.conditionalMeans[source];
    }

    verifyConditionalExpectations(tolerance = 1e-10) {
        return this.model.matrix.every((row, source) => {
            const expected = row.reduce(
                (sum, probability, destination) =>
                    sum + probability *
                    this.increment(source, destination),
                0
            );

            return Math.abs(expected) < tolerance;
        });
    }

    buildPath(path) {
        if (!Array.isArray(path) || path.length < 2) {
            throw new ProbabilityError("Path is too short.");
        }

        let cumulative = 0;
        const values = [0];

        for (let i = 0; i < path.length - 1; i++) {
            const source = path[i];
            const destination = path[i + 1];

            if (!Number.isInteger(source) ||
                !Number.isInteger(destination) ||
                source < 0 || destination < 0 ||
                source >= this.model.size ||
                destination >= this.model.size ||
                this.model.matrix[source][destination] <= 0) {
                throw new ProbabilityError("Invalid observed transition.");
            }

            cumulative += this.increment(source, destination);
            values.push(cumulative);
        }

        return values;
    }
}

// ============================================================
// 5. ONLINE STATISTICS
// ============================================================

class OnlineStatistics {
    constructor(size) {
        this.visits = new Array(size).fill(0);
        this.transitions = new Map();
        this.total = 0;
    }

    record(source, destination) {
        this.visits[destination]++;
        this.total++;

        const key = `${source}:${destination}`;

        this.transitions.set(
            key,
            (this.transitions.get(key) || 0) + 1
        );
    }

    distribution() {
        if (this.total === 0) {
            return this.visits.map(() => 0);
        }

        return this.visits.map(value => value / this.total);
    }
}

// ============================================================
// 6. EVENT-DRIVEN ASYNCHRONOUS SIMULATOR
// ============================================================

class StochasticSimulator extends EventEmitter {
    constructor(model, seed = 2026) {
        super();

        this.model = model;
        this.rng = new RandomGenerator(seed);
        this.statistics = new OnlineStatistics(model.size);
        this.id = randomUUID();
        this.running = false;
        this.stepNumber = 0;
    }

    async run(initialState, steps, batchSize = 1000) {
        if (this.running) {
            throw new ProbabilityError("Simulation is already running.");
        }

        if (!Number.isInteger(initialState) ||
            initialState < 0 ||
            initialState >= this.model.size) {
            throw new ProbabilityError("Invalid initial state.");
        }

        if (!Number.isInteger(steps) || steps < 0 ||
            !Number.isInteger(batchSize) || batchSize <= 0) {
            throw new ProbabilityError("Invalid simulation parameters.");
        }

        this.running = true;

        let current = initialState;

        try {
            this.emit("started", {
                id: this.id,
                initialState,
                steps
            });

            for (let i = 0; i < steps; i++) {
                const following = this.model.transition(current, this.rng);

                this.statistics.record(current, following);

                current = following;
                this.stepNumber++;

                this.emit("transition", {
                    step: this.stepNumber,
                    state: current,
                    label: this.model.states[current]
                });

                // Yield control periodically to avoid blocking Node.js.
                if ((i + 1) % batchSize === 0) {
                    await new Promise(resolve => setImmediate(resolve));

                    this.emit("progress", {
                        completed: i + 1,
                        total: steps
                    });
                }
            }

            const result = {
                id: this.id,
                steps: this.stepNumber,
                finalState: current,
                empiricalDistribution: this.statistics.distribution(),
                transitions: Object.fromEntries(this.statistics.transitions)
            };

            this.emit("completed", result);

            return result;
        } catch (error) {
            this.emit("failed", error);
            throw error;
        } finally {
            this.running = false;
        }
    }
}

// ============================================================
// 7. EXPERIMENT
// ============================================================

async function main() {
    const model = new MarkovModel(
        ["Sunny", "Cloudy", "Rainy"],
        [
            [0.70, 0.20, 0.10],
            [0.25, 0.50, 0.25],
            [0.20, 0.30, 0.50]
        ]
    );

    console.log("ADVANCED PROBABILITY");
    console.log("====================");

    console.log("\nStationary distribution:");

    const stationary = model.stationary();

    if (!stationary.converged) {
        throw new Error("Stationary iteration failed.");
    }

    console.table(
        model.states.map((state, index) => ({
            state,
            probability: stationary.distribution[index]
        }))
    );

    console.log("Iterations:", stationary.iterations);
    console.log("Classification:", model.classify());
    console.log("Period:", model.period());

    // Conditional reward and martingale difference.
    const reward = (source, destination) => destination - source;

    const martingale = new MartingaleProcess(model, reward);

    console.log(
        "\nConditional expectations valid:",
        martingale.verifyConditionalExpectations()
    );

    // Subscribe to selected simulation events.
    const simulator = new StochasticSimulator(model, 2026);

    simulator.on("started", event => {
        console.log("\nSimulation started:", event.id);
    });

    simulator.on("progress", event => {
        console.log(
            `Progress: ${event.completed}/${event.total}`
        );
    });

    simulator.on("failed", error => {
        console.error("Simulation failed:", error.message);
    });

    const result = await simulator.run(0, 100000, 10000);

    console.log("\nEmpirical distribution:");

    console.table(
        model.states.map((state, index) => ({
            state,
            probability: result.empiricalDistribution[index]
        }))
    );

    console.log(
        "Maximum distribution error:",
        maxDifference(
            stationary.distribution,
            result.empiricalDistribution
        )
    );

    // Verify martingale behavior on an observed path.
    const path = [0, 1, 2, 1, 0, 0, 2, 1];

    const martingaleValues = martingale.buildPath(path);

    console.log("\nMartingale path:", martingaleValues);

    // Periodic chain.
    const periodic = new MarkovModel(
        ["A", "B"],
        [
            [0, 1],
            [1, 0]
        ]
    );

    console.log("\nPeriodic chain:");
    console.log("Period:", periodic.period());
    console.log("Classification:", periodic.classify());
    console.log(
        "Power iteration:",
        periodic.stationary(1e-12, 100).converged
    );

    // Reducible chain.
    const reducible = new MarkovModel(
        ["A", "B"],
        [
            [0.8, 0.2],
            [0, 1]
        ]
    );

    console.log("\nReducible chain:", reducible.classify());

    console.log("\nExperiment completed.");
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
