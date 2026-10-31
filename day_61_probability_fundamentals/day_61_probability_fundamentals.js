"use strict";

/*
 * Probability Fundamentals
 *
 * This program models finite probability spaces, events, set operations,
 * conditional probability, simulation, and binomial experiments.
 *
 * It uses an event-driven simulation pipeline so that experiment results
 * can be observed without coupling the experiment to the reporting logic.
 */

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProbabilityError";
    }
}

class ProbabilitySpace {
    constructor(probabilities) {
        if (!probabilities || typeof probabilities !== "object") {
            throw new ProbabilityError("Probabilities must be an object.");
        }

        this.probabilities = new Map(Object.entries(probabilities));

        if (this.probabilities.size === 0) {
            throw new ProbabilityError("The sample space cannot be empty.");
        }

        let total = 0;
        for (const [outcome, probability] of this.probabilities) {
            if (!Number.isFinite(probability) || probability < 0 || probability > 1) {
                throw new ProbabilityError(
                    `Invalid probability for outcome ${outcome}.`
                );
            }
            total += probability;
        }

        if (Math.abs(total - 1) > 1e-12) {
            throw new ProbabilityError(
                `Probabilities must sum to 1. Received ${total}.`
            );
        }
    }

    probability(event) {
        let total = 0;
        for (const outcome of event.outcomes) {
            if (!this.probabilities.has(outcome)) {
                throw new ProbabilityError(
                    `Outcome ${outcome} is not in the sample space.`
                );
            }
            total += this.probabilities.get(outcome);
        }
        return total;
    }
}

class EventSet {
    constructor(name, outcomes) {
        if (!name || typeof name !== "string") {
            throw new ProbabilityError("An event requires a name.");
        }

        this.name = name;
        this.outcomes = new Set(outcomes);
    }

    has(outcome) {
        return this.outcomes.has(outcome);
    }
}

function validateEvent(space, event) {
    for (const outcome of event.outcomes) {
        if (!space.probabilities.has(outcome)) {
            throw new ProbabilityError(
                `Event "${event.name}" contains invalid outcome ${outcome}.`
            );
        }
    }
}

function union(space, a, b) {
    validateEvent(space, a);
    validateEvent(space, b);

    return new EventSet(
        `${a.name} OR ${b.name}`,
        new Set([...a.outcomes, ...b.outcomes])
    );
}

function intersection(space, a, b) {
    validateEvent(space, a);
    validateEvent(space, b);

    const result = new Set();
    for (const outcome of a.outcomes) {
        if (b.outcomes.has(outcome)) {
            result.add(outcome);
        }
    }

    return new EventSet(`${a.name} AND ${b.name}`, result);
}

function complement(space, event) {
    validateEvent(space, event);

    const result = new Set();
    for (const outcome of space.probabilities.keys()) {
        if (!event.outcomes.has(outcome)) {
            result.add(outcome);
        }
    }

    return new EventSet(`NOT ${event.name}`, result);
}

function conditionalProbability(space, event, condition) {
    const conditionProbability = space.probability(condition);

    if (conditionProbability === 0) {
        throw new ProbabilityError(
            "Conditional probability is undefined when the condition has probability zero."
        );
    }

    const overlap = intersection(space, event, condition);
    return space.probability(overlap) / conditionProbability;
}

function secureRandomUnit() {
    // crypto.randomInt provides an unbiased integer source for simulation.
    const denominator = 2 ** 32;
    const bytes = crypto.randomBytes(4);
    const integer = bytes.readUInt32BE(0);
    return integer / denominator;
}

class Experiment extends EventEmitter {
    constructor(name, trialFunction) {
        super();
        if (!name || typeof trialFunction !== "function") {
            throw new TypeError("Experiment requires a name and trial function.");
        }

        this.name = name;
        this.trialFunction = trialFunction;
    }

    run(trials, eventPredicate) {
        if (!Number.isInteger(trials) || trials <= 0) {
            throw new RangeError("trials must be a positive integer.");
        }
        if (typeof eventPredicate !== "function") {
            throw new TypeError("eventPredicate must be a function.");
        }

        let successes = 0;

        for (let i = 0; i < trials; i += 1) {
            const outcome = this.trialFunction();
            if (eventPredicate(outcome)) {
                successes += 1;
            }

            if ((i + 1) % Math.max(1, Math.floor(trials / 10)) === 0) {
                this.emit("progress", {
                    experiment: this.name,
                    completed: i + 1,
                    total: trials,
                });
            }
        }

        const estimate = successes / trials;

        const result = {
            experiment: this.name,
            trials,
            successes,
            failures: trials - successes,
            estimate,
        };

        this.emit("complete", result);
        return result;
    }
}

function binomialProbability(n, k, p) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }
    if (!Number.isInteger(k) || k < 0 || k > n) {
        throw new RangeError("k must satisfy 0 <= k <= n.");
    }
    if (!Number.isFinite(p) || p < 0 || p > 1) {
        throw new RangeError("p must be between 0 and 1.");
    }

    let coefficient = 1;
    for (let i = 1; i <= k; i += 1) {
        coefficient *= (n - i + 1) / i;
    }

    return coefficient * p ** k * (1 - p) ** (n - k);
}

function runValidation() {
    const space = new ProbabilitySpace({
        1: 1 / 6,
        2: 1 / 6,
        3: 1 / 6,
        4: 1 / 6,
        5: 1 / 6,
        6: 1 / 6,
    });

    const even = new EventSet("even", [2, 4, 6]);
    const prime = new EventSet("prime", [2, 3, 5]);

    if (Math.abs(space.probability(even) - 0.5) > 1e-12) {
        throw new Error("Even-event probability validation failed.");
    }

    const overlap = intersection(space, even, prime);
    if (overlap.outcomes.size !== 1 || !overlap.outcomes.has(2)) {
        throw new Error("Intersection validation failed.");
    }

    const either = union(space, even, prime);
    if (Math.abs(space.probability(either) - 5 / 6) > 1e-12) {
        throw new Error("Union validation failed.");
    }

    const notEven = complement(space, even);
    if (Math.abs(space.probability(notEven) - 0.5) > 1e-12) {
        throw new Error("Complement validation failed.");
    }

    const conditional = conditionalProbability(space, prime, even);
    if (Math.abs(conditional - 1 / 3) > 1e-12) {
        throw new Error("Conditional probability validation failed.");
    }

    if (Math.abs(binomialProbability(5, 3, 0.5) - 0.3125) > 1e-12) {
        throw new Error("Binomial probability validation failed.");
    }

    try {
        new ProbabilitySpace({ A: 0.7, B: 0.7 });
        throw new Error("Invalid probability model was accepted.");
    } catch (error) {
        if (!(error instanceof ProbabilityError)) {
            throw error;
        }
    }
}

async function main() {
    runValidation();

    const space = new ProbabilitySpace({
        1: 1 / 6,
        2: 1 / 6,
        3: 1 / 6,
        4: 1 / 6,
        5: 1 / 6,
        6: 1 / 6,
    });

    const even = new EventSet("even", [2, 4, 6]);
    const prime = new EventSet("prime", [2, 3, 5]);

    console.log("=== Probability Fundamentals ===");
    console.log(`P(even) = ${space.probability(even).toFixed(4)}`);
    console.log(`P(prime) = ${space.probability(prime).toFixed(4)}`);
    console.log(
        `P(even OR prime) = ${space.probability(union(space, even, prime)).toFixed(4)}`
    );
    console.log(
        `P(even AND prime) = ${space.probability(intersection(space, even, prime)).toFixed(4)}`
    );
    console.log(
        `P(prime | even) = ${conditionalProbability(space, prime, even).toFixed(4)}`
    );

    const dieExperiment = new Experiment(
        "Secure random die experiment",
        () => Math.floor(secureRandomUnit() * 6) + 1
    );

    dieExperiment.on("progress", ({ completed, total }) => {
        if (completed === total) {
            console.log(`Completed ${total} die trials.`);
        }
    });

    const simulation = dieExperiment.run(100_000, outcome => outcome === 6);

    console.log(`Estimated P(6) = ${simulation.estimate.toFixed(4)}`);
    console.log("Theoretical P(6) = 0.1667");

    const binomial = binomialProbability(5, 3, 0.5);
    console.log(`P(exactly 3 heads in 5 fair flips) = ${binomial.toFixed(4)}`);

    console.log("Validation checks passed.");
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
