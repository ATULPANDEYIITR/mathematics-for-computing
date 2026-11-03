"use strict";

/*
 * Random Variables: Discrete and Continuous Distributions
 *
 * Node.js implementation demonstrating:
 * - Discrete probability mass functions.
 * - Continuous probability density functions.
 * - Cumulative distribution functions.
 * - Binomial, normal, and uniform distributions.
 * - Event-driven observation processing.
 * - Asynchronous sampling and online statistical monitoring.
 *
 * No npm dependencies are required.
 */

class DistributionError extends Error {
    constructor(message) {
        super(message);
        this.name = "DistributionError";
    }
}

function requireFinite(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new DistributionError(`${name} must be a finite number.`);
    }
    return value;
}

function requireCdfInput(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
        throw new DistributionError("CDF input must be a number other than NaN.");
    }
    return value;
}

function requireProbability(value, name = "probability") {
    requireFinite(value, name);

    if (value < 0 || value > 1) {
        throw new DistributionError(`${name} must be between 0 and 1.`);
    }

    return value;
}

function requireRandomSource(rng) {
    if (typeof rng !== "function") {
        throw new TypeError("Random source must be a function.");
    }

    const value = rng();

    if (typeof value !== "number" || value < 0 || value >= 1) {
        throw new DistributionError(
            "Random source must return a number in [0, 1)."
        );
    }

    return value;
}

/*
 * A deterministic generator for repeatable simulation runs.
 * It is not intended for security-sensitive or cryptographic use.
 */
function seededRandom(seed) {
    let state = seed >>> 0;

    return function nextRandom() {
        state += 0x6D2B79F5;

        let value = state;
        value = Math.imul(value ^ (value >>> 15), value | 1);
        value ^= value + Math.imul(value ^ (value >>> 7), value | 61);

        return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
}

/* Numerical approximation of the error function. */
function erf(value) {
    const sign = value < 0 ? -1 : 1;
    const absolute = Math.abs(value);
    const t = 1 / (1 + 0.5 * absolute);

    const polynomial = t * Math.exp(
        -absolute * absolute - 1.26551223 +
        t * (
            1.00002368 +
            t * (
                0.37409196 +
                t * (
                    0.09678418 +
                    t * (
                        -0.18628806 +
                        t * (
                            0.27886807 +
                            t * (
                                -1.13520398 +
                                t * (
                                    1.48851587 +
                                    t * (
                                        -0.82215223 +
                                        t * 0.17087277
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    );

    return sign * (1 - polynomial);
}

class DiscreteDistribution {
    constructor(entries) {
        if (!Array.isArray(entries) || entries.length === 0) {
            throw new DistributionError("A non-empty entry array is required.");
        }

        const seen = new Set();

        const outcomes = entries.map((entry) => {
            if (
                entry === null ||
                typeof entry !== "object" ||
                Array.isArray(entry)
            ) {
                throw new DistributionError("Each outcome must be an object.");
            }

            const value = requireFinite(entry.value, "Outcome");
            const probability = requireProbability(entry.probability);

            if (seen.has(value)) {
                throw new DistributionError(`Duplicate outcome: ${value}`);
            }

            seen.add(value);
            return Object.freeze({ value, probability });
        });

        outcomes.sort((a, b) => a.value - b.value);

        const total = outcomes.reduce(
            (sum, item) => sum + item.probability,
            0
        );

        if (Math.abs(total - 1) > 1e-9) {
            throw new DistributionError(
                `Probabilities must sum to 1. Current total: ${total}`
            );
        }

        this.outcomes = Object.freeze(outcomes);

        this.mass = new Map(
            outcomes.map(({ value, probability }) => [value, probability])
        );

        this.cumulative = [];
        let runningTotal = 0;

        for (const outcome of outcomes) {
            runningTotal += outcome.probability;
            this.cumulative.push(runningTotal);
        }

        this.cumulative[this.cumulative.length - 1] = 1;

        this._mean = outcomes.reduce(
            (sum, item) => sum + item.value * item.probability,
            0
        );

        this._variance = outcomes.reduce(
            (sum, item) =>
                sum + item.probability * (item.value - this._mean) ** 2,
            0
        );
    }

    get mean() {
        return this._mean;
    }

    get variance() {
        return this._variance;
    }

    pmf(value) {
        requireCdfInput(value);

        if (!Number.isFinite(value)) {
            return 0;
        }

        return this.mass.get(value) ?? 0;
    }

    cdf(value) {
        requireCdfInput(value);

        let left = 0;
        let right = this.outcomes.length;

        // Find the first outcome strictly greater than the requested value.
        while (left < right) {
            const middle = Math.floor((left + right) / 2);

            if (this.outcomes[middle].value <= value) {
                left = middle + 1;
            } else {
                right = middle;
            }
        }

        return left === 0 ? 0 : this.cumulative[left - 1];
    }

    sample(rng = Math.random) {
        const draw = requireRandomSource(rng);

        let left = 0;
        let right = this.cumulative.length;

        // Binary search gives O(log n) sampling after O(n log n) setup.
        while (left < right) {
            const middle = Math.floor((left + right) / 2);

            if (this.cumulative[middle] >= draw) {
                right = middle;
            } else {
                left = middle + 1;
            }
        }

        return this.outcomes[Math.min(left, this.outcomes.length - 1)].value;
    }
}

class NormalDistribution {
    constructor(mean, standardDeviation) {
        this.mu = requireFinite(mean, "Normal mean");
        this.sigma = requireFinite(
            standardDeviation,
            "Normal standard deviation"
        );

        if (this.sigma <= 0) {
            throw new DistributionError(
                "Normal standard deviation must be positive."
            );
        }
    }

    get mean() {
        return this.mu;
    }

    get variance() {
        return this.sigma ** 2;
    }

    pdf(value) {
        requireCdfInput(value);

        if (!Number.isFinite(value)) {
            return 0;
        }

        const z = (value - this.mu) / this.sigma;

        return Math.exp(-0.5 * z * z) /
            (this.sigma * Math.sqrt(2 * Math.PI));
    }

    cdf(value) {
        requireCdfInput(value);

        if (value === Infinity) return 1;
        if (value === -Infinity) return 0;

        const z = (value - this.mu) / (this.sigma * Math.sqrt(2));
        return 0.5 * (1 + erf(z));
    }

    sample(rng = Math.random) {
        // Box-Muller transformation generates standard normal observations.
        let first = requireRandomSource(rng);
        const second = requireRandomSource(rng);

        // Avoid log(0).
        if (first === 0) {
            first = Number.MIN_VALUE;
        }

        const standardNormal =
            Math.sqrt(-2 * Math.log(first)) *
            Math.cos(2 * Math.PI * second);

        return this.mu + this.sigma * standardNormal;
    }
}

class UniformDistribution {
    constructor(lower, upper) {
        this.lower = requireFinite(lower, "Lower bound");
        this.upper = requireFinite(upper, "Upper bound");

        if (this.lower >= this.upper) {
            throw new DistributionError(
                "Uniform lower bound must be below the upper bound."
            );
        }
    }

    get mean() {
        return (this.lower + this.upper) / 2;
    }

    get variance() {
        return (this.upper - this.lower) ** 2 / 12;
    }

    pdf(value) {
        requireCdfInput(value);

        return value >= this.lower && value <= this.upper
            ? 1 / (this.upper - this.lower)
            : 0;
    }

    cdf(value) {
        requireCdfInput(value);

        if (value <= this.lower) return 0;
        if (value >= this.upper) return 1;

        return (value - this.lower) / (this.upper - this.lower);
    }

    sample(rng = Math.random) {
        const draw = requireRandomSource(rng);
        return this.lower + draw * (this.upper - this.lower);
    }
}

function binomialDistribution(trials, probability) {
    if (!Number.isInteger(trials) || trials < 0 || trials > 1000) {
        throw new DistributionError(
            "trials must be an integer between 0 and 1000."
        );
    }

    const p = requireProbability(probability, "success probability");
    const outcomes = [];

    if (p === 0) {
        return new DiscreteDistribution([
            { value: 0, probability: 1 }
        ]);
    }

    if (p === 1) {
        return new DiscreteDistribution([
            { value: trials, probability: 1 }
        ]);
    }

    // Recurrence avoids repeatedly calculating factorials.
    let currentProbability = (1 - p) ** trials;

    for (let k = 0; k <= trials; k++) {
        outcomes.push({
            value: k,
            probability: currentProbability
        });

        if (k < trials) {
            currentProbability *=
                ((trials - k) / (k + 1)) * (p / (1 - p));
        }
    }

    return new DiscreteDistribution(outcomes);
}

/*
 * EventBus separates the production of observations from their consumers.
 * A listener can be registered or removed without changing the distribution.
 */
class EventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (typeof eventName !== "string" || eventName.trim() === "") {
            throw new TypeError("Event name must be a non-empty string.");
        }

        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        const subscribers = this.listeners.get(eventName);
        subscribers.add(listener);

        return () => {
            subscribers.delete(listener);

            if (subscribers.size === 0) {
                this.listeners.delete(eventName);
            }
        };
    }

    emit(eventName, payload) {
        const subscribers = this.listeners.get(eventName);

        if (!subscribers) {
            return;
        }

        // Copy to allow listeners to unsubscribe while an event is processed.
        for (const listener of [...subscribers]) {
            listener(payload);
        }
    }
}

class OnlineStatistics {
    constructor() {
        this.count = 0;
        this.mean = 0;
        this.m2 = 0;
        this.exceedances = 0;
    }

    observe(value, threshold) {
        requireFinite(value, "Observation");
        requireFinite(threshold, "Threshold");

        this.count += 1;

        const delta = value - this.mean;
        this.mean += delta / this.count;

        const deltaAfterUpdate = value - this.mean;
        this.m2 += delta * deltaAfterUpdate;

        if (value > threshold) {
            this.exceedances += 1;
        }
    }

    get sampleVariance() {
        return this.count < 2 ? 0 : this.m2 / (this.count - 1);
    }

    get empiricalTailProbability() {
        return this.count === 0 ? 0 : this.exceedances / this.count;
    }
}

class ProbabilityMonitor {
    constructor(eventBus, variableName, threshold) {
        this.variableName = variableName;
        this.threshold = requireFinite(threshold, "Threshold");
        this.statistics = new OnlineStatistics();

        this.unsubscribe = eventBus.on("observation", (event) => {
            if (
                event &&
                event.variable === this.variableName &&
                Number.isFinite(event.value)
            ) {
                this.statistics.observe(event.value, this.threshold);
            }
        });
    }

    close() {
        this.unsubscribe();
    }
}

/* Asynchronous stream allows consumers to process observations incrementally. */
async function* sampleStream(distribution, count, rng) {
    if (!Number.isInteger(count) || count < 1) {
        throw new DistributionError("Sample count must be a positive integer.");
    }

    for (let index = 0; index < count; index++) {
        yield distribution.sample(rng);
    }
}

async function run() {
    const sampleCount = Number(process.argv[2] ?? 20000);

    if (
        !Number.isInteger(sampleCount) ||
        sampleCount < 1 ||
        sampleCount > 5_000_000
    ) {
        throw new RangeError(
            "Sample count must be an integer between 1 and 5,000,000."
        );
    }

    const rng = seededRandom(20261103);

    // X = number of failed requests among four independent requests.
    const failures = binomialDistribution(4, 0.10);

    console.log("1. DISCRETE RANDOM VARIABLE");
    console.log("X = failed requests among four requests");

    for (const outcome of failures.outcomes) {
        console.log(
            `P(X = ${outcome.value}) = ${outcome.probability.toFixed(6)}`
        );
    }

    console.log(`P(X = 2)  = ${failures.pmf(2).toFixed(6)}`);
    console.log(`P(X <= 2) = ${failures.cdf(2).toFixed(6)}`);
    console.log(`E[X]      = ${failures.mean.toFixed(6)}`);
    console.log(`Var(X)    = ${failures.variance.toFixed(6)}`);

    // Y = normally distributed API response time in milliseconds.
    const latency = new NormalDistribution(120, 25);

    console.log("\n2. CONTINUOUS NORMAL RANDOM VARIABLE");
    console.log(`PDF at 150 ms = ${latency.pdf(150).toFixed(8)}`);
    console.log(`CDF at 150 ms = ${latency.cdf(150).toFixed(6)}`);
    console.log(
        `P(Y > 180 ms) = ${(1 - latency.cdf(180)).toFixed(6)}`
    );

    // Z = uniform sensor measurement error.
    const sensorError = new UniformDistribution(-2, 2);

    console.log("\n3. CONTINUOUS UNIFORM RANDOM VARIABLE");
    console.log(`Mean = ${sensorError.mean.toFixed(4)}`);
    console.log(`Variance = ${sensorError.variance.toFixed(4)}`);
    console.log(`PDF at 0 = ${sensorError.pdf(0).toFixed(4)}`);
    console.log(`CDF at 1 = ${sensorError.cdf(1).toFixed(4)}`);

    // Separate producers and consumers through event-driven monitoring.
    const eventBus = new EventBus();

    const failureMonitor = new ProbabilityMonitor(
        eventBus,
        "failed_requests",
        1
    );

    const latencyMonitor = new ProbabilityMonitor(
        eventBus,
        "api_latency_ms",
        180
    );

    try {
        for await (const value of sampleStream(
            failures,
            sampleCount,
            rng
        )) {
            eventBus.emit("observation", {
                variable: "failed_requests",
                value
            });
        }

        for await (const value of sampleStream(
            latency,
            sampleCount,
            rng
        )) {
            eventBus.emit("observation", {
                variable: "api_latency_ms",
                value
            });
        }

        console.log("\n4. EVENT-DRIVEN MONITORING");
        console.log(`Observations per variable = ${sampleCount}`);

        console.log(
            `Empirical P(X > 1) = ${
                failureMonitor.statistics.empiricalTailProbability.toFixed(6)
            }`
        );

        console.log(
            `Empirical P(Y > 180) = ${
                latencyMonitor.statistics.empiricalTailProbability.toFixed(6)
            }`
        );

        console.log(
            `Empirical latency mean = ${
                latencyMonitor.statistics.mean.toFixed(4)
            } ms`
        );

        console.log(
            `Empirical latency variance = ${
                latencyMonitor.statistics.sampleVariance.toFixed(4)
            }`
        );
    } finally {
        failureMonitor.close();
        latencyMonitor.close();
    }

    // Mathematical checks detect implementation regressions.
    if (Math.abs(failures.cdf(4) - 1) > 1e-9) {
        throw new Error("Discrete CDF must approach 1 at its maximum outcome.");
    }

    if (Math.abs(latency.cdf(120) - 0.5) > 1e-6) {
        throw new Error("Normal CDF symmetry check failed.");
    }

    if (sensorError.cdf(-2) !== 0 || sensorError.cdf(2) !== 1) {
        throw new Error("Uniform CDF boundary check failed.");
    }

    console.log("\n5. VALIDATION");
    console.log("All distribution checks passed.");
    console.log(
        "The seeded generator supports repeatable simulation, not cryptography."
    );
}

run().catch((error) => {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
});
