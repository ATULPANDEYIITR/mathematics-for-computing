"use strict";

/*
 * Statistical Estimation Engine
 *
 * Event-driven estimation service supporting:
 * - Point estimates
 * - Sampling distributions
 * - Maximum likelihood estimation
 * - Confidence intervals
 * - Bootstrap resampling
 * - Estimator quality metrics
 * - Asynchronous batch processing
 * - Input validation and structured results
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class EstimationError extends Error {
    constructor(message) {
        super(message);
        this.name = "EstimationError";
    }
}

const IntervalMethod = Object.freeze({
    NORMAL: "normal",
    T: "student_t",
    WILSON: "wilson",
    BOOTSTRAP: "bootstrap"
});

function validateSample(data) {
    if (!Array.isArray(data) || data.length === 0) {
        throw new EstimationError("Sample must be a non-empty array.");
    }

    if (!data.every(
        value => typeof value === "number" && Number.isFinite(value)
    )) {
        throw new EstimationError("All observations must be finite numbers.");
    }

    return [...data];
}

function validateConfidence(confidence) {
    if (
        typeof confidence !== "number" ||
        confidence <= 0 ||
        confidence >= 1
    ) {
        throw new EstimationError(
            "Confidence level must be between zero and one."
        );
    }
}

function mean(data) {
    const values = validateSample(data);

    return values.reduce((sum, value) => sum + value, 0)
        / values.length;
}

function variance(data, unbiased = true) {
    const values = validateSample(data);

    if (unbiased && values.length < 2) {
        throw new EstimationError(
            "At least two observations are required."
        );
    }

    const average = mean(values);

    const sumSquares = values.reduce(
        (sum, value) => sum + (value - average) ** 2,
        0
    );

    return sumSquares / (
        unbiased ? values.length - 1 : values.length
    );
}

function standardDeviation(data) {
    return Math.sqrt(variance(data));
}

function proportion(data) {
    const values = validateSample(data);

    if (!values.every(value => value === 0 || value === 1)) {
        throw new EstimationError(
            "Proportion estimation requires binary observations."
        );
    }

    return mean(values);
}

function normalQuantile(p) {
    if (!(p > 0 && p < 1)) {
        throw new EstimationError("Invalid probability.");
    }

    const a = [
        -39.69683028665376,
        220.9460984245205,
        -275.9285104469687,
        138.3577518672690,
        -30.66479806614716,
        2.506628277459239
    ];

    const b = [
        -54.47609879822406,
        161.5858368580409,
        -155.6989798598866,
        66.80131188771972,
        -13.28068155288572
    ];

    const c = [
        -0.007784894002430293,
        -0.3223964580411365,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783
    ];

    const d = [
        0.007784695709041462,
        0.3224671290700398,
        2.445134137142996,
        3.754408661907416
    ];

    const low = 0.02425;
    const high = 1 - low;

    if (p < low || p > high) {
        const q = Math.sqrt(
            -2 * Math.log(p < low ? p : 1 - p)
        );

        const numerator = c.reduce(
            (sum, value, index) =>
                sum + value * q ** (5 - index),
            0
        );

        const denominator = d.reduce(
            (sum, value, index) =>
                sum + value * q ** (3 - index),
            1
        );

        const result = numerator / denominator;

        return p < low ? result : -result;
    }

    const q = p - 0.5;
    const r = q * q;

    const numerator = a.reduce(
        (sum, value, index) =>
            sum + value * q * r ** (2 - index),
        0
    );

    const denominator = b.reduce(
        (sum, value, index) =>
            sum + value * r ** (2 - index),
        1
    );

    return numerator / denominator;
}

function logGamma(z) {
    const coefficients = [
        676.5203681218851,
        -1259.1392167224028,
        771.3234287776531,
        -176.6150291621406,
        12.507343278686905,
        -0.13857109526572012,
        9.984369578019572e-6,
        1.5056327351493116e-7
    ];

    if (z < 0.5) {
        return Math.log(Math.PI)
            - Math.log(Math.sin(Math.PI * z))
            - logGamma(1 - z);
    }

    z -= 1;

    let x = 0.99999999999980993;

    coefficients.forEach((coefficient, index) => {
        x += coefficient / (z + index + 1);
    });

    const t = z + coefficients.length - 0.5;

    return 0.5 * Math.log(2 * Math.PI)
        + (z + 0.5) * Math.log(t)
        - t
        + Math.log(x);
}

function betaFraction(a, b, x) {
    const tiny = 1e-300;
    const epsilon = 3e-14;

    const qab = a + b;
    const qap = a + 1;
    const qam = a - 1;

    let c = 1;
    let d = 1 - qab * x / qap;

    if (Math.abs(d) < tiny) d = tiny;

    d = 1 / d;

    let h = d;

    for (let m = 1; m <= 300; m++) {
        const m2 = 2 * m;

        let aa = m * (b - m) * x
            / ((qam + m2) * (a + m2));

        d = 1 + aa * d;
        if (Math.abs(d) < tiny) d = tiny;

        c = 1 + aa / c;
        if (Math.abs(c) < tiny) c = tiny;

        d = 1 / d;
        h *= d * c;

        aa = -(a + m) * (qab + m) * x
            / ((a + m2) * (qap + m2));

        d = 1 + aa * d;
        if (Math.abs(d) < tiny) d = tiny;

        c = 1 + aa / c;
        if (Math.abs(c) < tiny) c = tiny;

        d = 1 / d;

        const delta = d * c;
        h *= delta;

        if (Math.abs(delta - 1) < epsilon) {
            return h;
        }
    }

    throw new EstimationError("Beta fraction did not converge.");
}

function regularizedBeta(x, a, b) {
    if (x <= 0) return 0;
    if (x >= 1) return 1;

    const bt = Math.exp(
        logGamma(a + b)
        - logGamma(a)
        - logGamma(b)
        + a * Math.log(x)
        + b * Math.log1p(-x)
    );

    if (x < (a + 1) / (a + b + 2)) {
        return bt * betaFraction(a, b, x) / a;
    }

    return 1 - bt * betaFraction(b, a, 1 - x) / b;
}

function studentTCDF(t, degrees) {
    const x = degrees / (degrees + t * t);

    const beta = regularizedBeta(
        x,
        degrees / 2,
        0.5
    );

    return t >= 0 ? 1 - beta / 2 : beta / 2;
}

function studentTQuantile(p, degrees) {
    if (degrees < 1 || !(p > 0 && p < 1)) {
        throw new EstimationError("Invalid Student's t parameters.");
    }

    if (p === 0.5) return 0;

    if (p < 0.5) {
        return -studentTQuantile(1 - p, degrees);
    }

    let lower = 0;
    let upper = 1;

    while (studentTCDF(upper, degrees) < p) {
        upper *= 2;

        if (upper > 1e12) {
            throw new EstimationError("Unable to bracket quantile.");
        }
    }

    for (let i = 0; i < 150; i++) {
        const middle = (lower + upper) / 2;

        if (studentTCDF(middle, degrees) < p) {
            lower = middle;
        } else {
            upper = middle;
        }
    }

    return (lower + upper) / 2;
}

function createInterval(parameter, estimate, margin, confidence, method) {
    return Object.freeze({
        parameter,
        estimate,
        lower: estimate - margin,
        upper: estimate + margin,
        width: 2 * margin,
        confidence,
        method
    });
}

function meanInterval(data, confidence = 0.95, method = IntervalMethod.T) {
    const values = validateSample(data);
    validateConfidence(confidence);

    if (values.length < 2) {
        throw new EstimationError("At least two observations are required.");
    }

    const estimate = mean(values);
    const standardError = standardDeviation(values)
        / Math.sqrt(values.length);

    let critical;

    if (method === IntervalMethod.T) {
        critical = studentTQuantile(
            (1 + confidence) / 2,
            values.length - 1
        );
    } else if (method === IntervalMethod.NORMAL) {
        critical = normalQuantile((1 + confidence) / 2);
    } else {
        throw new EstimationError("Unsupported mean interval method.");
    }

    return createInterval(
        "population_mean",
        estimate,
        critical * standardError,
        confidence,
        method
    );
}

function wilsonInterval(data, confidence = 0.95) {
    const p = proportion(data);
    const n = data.length;

    validateConfidence(confidence);

    const z = normalQuantile((1 + confidence) / 2);
    const z2 = z * z;

    const denominator = 1 + z2 / n;

    const center = (p + z2 / (2 * n)) / denominator;

    const margin = z * Math.sqrt(
        p * (1 - p) / n + z2 / (4 * n * n)
    ) / denominator;

    return Object.freeze({
        parameter: "population_proportion",
        estimate: p,
        lower: Math.max(0, center - margin),
        upper: Math.min(1, center + margin),
        confidence,
        method: IntervalMethod.WILSON
    });
}

class SeededRandom {
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        this.state = (
            1664525 * this.state + 1013904223
        ) >>> 0;

        return this.state / 4294967296;
    }

    integer(maximum) {
        return Math.floor(this.next() * maximum);
    }
}

async function bootstrapInterval(
    data,
    confidence = 0.95,
    repetitions = 5000,
    seed = 42
) {
    const values = validateSample(data);
    validateConfidence(confidence);

    if (!Number.isInteger(repetitions) || repetitions < 100) {
        throw new EstimationError(
            "At least 100 bootstrap repetitions are required."
        );
    }

    const rng = new SeededRandom(seed);
    const estimates = [];

    for (let repetition = 0; repetition < repetitions; repetition++) {
        const sample = Array.from(
            { length: values.length },
            () => values[rng.integer(values.length)]
        );

        estimates.push(mean(sample));

        // Yield periodically to prevent long event-loop blocking.
        if (repetition % 500 === 0) {
            await new Promise(resolve => setImmediate(resolve));
        }
    }

    estimates.sort((a, b) => a - b);

    const alpha = 1 - confidence;

    const lowerIndex = Math.floor(
        alpha / 2 * repetitions
    );

    const upperIndex = Math.min(
        repetitions - 1,
        Math.floor((1 - alpha / 2) * repetitions)
    );

    return Object.freeze({
        parameter: "population_mean",
        estimate: mean(values),
        lower: estimates[lowerIndex],
        upper: estimates[upperIndex],
        confidence,
        method: IntervalMethod.BOOTSTRAP,
        repetitions
    });
}

function exponentialMLE(data) {
    const values = validateSample(data);

    if (values.some(value => value < 0)) {
        throw new EstimationError("Observations cannot be negative.");
    }

    const average = mean(values);

    if (average <= 0) {
        throw new EstimationError("MLE is undefined for an all-zero sample.");
    }

    return Object.freeze({
        parameter: "exponential_rate",
        estimate: 1 / average,
        method: "maximum_likelihood"
    });
}

class EstimationRegistry extends EventEmitter {
    constructor() {
        super();
        this.estimators = new Map();
        this.results = new Map();
    }

    register(name, estimator) {
        if (typeof name !== "string" || !name.trim()) {
            throw new EstimationError("Estimator name is required.");
        }

        if (typeof estimator !== "function") {
            throw new EstimationError("Estimator must be a function.");
        }

        if (this.estimators.has(name)) {
            throw new EstimationError("Estimator already registered.");
        }

        this.estimators.set(name, estimator);
        this.emit("registered", { name });
    }

    async execute(name, data) {
        const estimator = this.estimators.get(name);

        if (!estimator) {
            throw new EstimationError(`Unknown estimator: ${name}`);
        }

        const values = validateSample(data);

        this.emit("estimationStarted", {
            name,
            sampleSize: values.length
        });

        try {
            const result = await Promise.resolve(estimator(values));

            if (typeof result !== "number" || !Number.isFinite(result)) {
                throw new EstimationError(
                    "Estimator returned an invalid result."
                );
            }

            const record = Object.freeze({
                name,
                estimate: result,
                sampleSize: values.length,
                timestamp: new Date().toISOString()
            });

            this.results.set(name, record);

            this.emit("estimationCompleted", record);

            return record;
        } catch (error) {
            this.emit("estimationFailed", {
                name,
                message: error.message
            });

            throw error;
        }
    }
}

function evaluateEstimator(
    estimator,
    trueValue,
    repetitions = 2000,
    sampleSize = 30,
    seed = 42
) {
    if (
        typeof estimator !== "function" ||
        !Number.isFinite(trueValue) ||
        repetitions < 2 ||
        sampleSize < 1
    ) {
        throw new EstimationError("Invalid evaluation parameters.");
    }

    const rng = new SeededRandom(seed);

    // Box-Muller transformation produces normal observations.
    function normalRandom() {
        const u1 = Math.max(rng.next(), Number.MIN_VALUE);
        const u2 = rng.next();

        return Math.sqrt(-2 * Math.log(u1))
            * Math.cos(2 * Math.PI * u2);
    }

    const estimates = [];

    for (let i = 0; i < repetitions; i++) {
        const sample = Array.from(
            { length: sampleSize },
            () => trueValue + 2 * normalRandom()
        );

        estimates.push(estimator(sample));
    }

    const average = mean(estimates);

    const bias = average - trueValue;

    const estimatorVariance = variance(estimates, false);

    const mse = estimates.reduce(
        (sum, value) => sum + (value - trueValue) ** 2,
        0
    ) / repetitions;

    return Object.freeze({
        repetitions,
        sampleSize,
        trueValue,
        average,
        bias,
        variance: estimatorVariance,
        mse
    });
}

async function main() {
    const registry = new EstimationRegistry();

    registry.on("estimationCompleted", result => {
        console.log("Estimation completed:", result.name);
    });

    registry.on("estimationFailed", error => {
        console.error("Estimation failed:", error);
    });

    registry.register("arithmetic_mean", mean);
    registry.register("unbiased_variance", data => variance(data));

    const observations = [
        48.2, 51.1, 49.5, 52.3, 47.8,
        50.6, 53.0, 49.9, 51.7, 48.9,
        52.1, 50.3
    ];

    console.log("\nPOINT ESTIMATION");

    const meanResult = await registry.execute(
        "arithmetic_mean",
        observations
    );

    const varianceResult = await registry.execute(
        "unbiased_variance",
        observations
    );

    console.log(meanResult);
    console.log(varianceResult);

    console.log("\nINTERVAL ESTIMATION");

    console.log(
        "Student t:",
        meanInterval(observations)
    );

    console.log(
        "Normal:",
        meanInterval(observations, 0.95, IntervalMethod.NORMAL)
    );

    console.log(
        "Bootstrap:",
        await bootstrapInterval(observations)
    );

    const binary = [
        1, 1, 0, 1, 0, 1, 1, 0, 1, 1,
        0, 1, 0, 1, 1, 1, 0, 1, 0, 1
    ];

    console.log("\nPROPORTION ESTIMATION");
    console.log("Estimate:", proportion(binary));
    console.log("Wilson interval:", wilsonInterval(binary));

    console.log("\nEXPONENTIAL DISTRIBUTION MLE");

    console.log(
        exponentialMLE([1.2, 0.8, 2.1, 1.5, 0.9, 1.7])
    );

    console.log("\nESTIMATOR EVALUATION");

    console.log(
        evaluateEstimator(
            mean,
            50,
            2000,
            30
        )
    );

    const report = {
        mean: meanResult,
        variance: varianceResult,
        confidenceInterval: meanInterval(observations),
        proportionInterval: wilsonInterval(binary)
    };

    await fs.writeFile(
        "estimation_results.json",
        JSON.stringify(report, null, 2),
        { encoding: "utf8", mode: 0o600 }
    );

    console.log("\nResults saved to estimation_results.json");
}

async function runTests() {
    const sample = [10, 12, 13, 15, 16];

    console.assert(Math.abs(mean(sample) - 13.2) < 1e-10);

    console.assert(
        Math.abs(variance(sample) - 5.7) < 1e-10
    );

    console.assert(
        meanInterval(sample).lower < 13.2
    );

    console.assert(
        meanInterval(sample).upper > 13.2
    );

    console.assert(
        Math.abs(proportion([1, 0, 1, 1]) - 0.75) < 1e-10
    );

    console.assert(
        studentTQuantile(0.975, 9) > 2.2
    );

    console.assert(
        studentTQuantile(0.975, 9) < 2.3
    );

    let rejected = false;

    try {
        variance([5]);
    } catch (error) {
        rejected = error instanceof EstimationError;
    }

    if (!rejected) {
        throw new Error("Single-observation variance test failed.");
    }

    console.log("All JavaScript tests passed.");
}

if (require.main === module) {
    runTests()
        .then(main)
        .catch(error => {
            console.error(error);
            process.exitCode = 1;
        });
}

module.exports = {
    mean,
    variance,
    standardDeviation,
    proportion,
    meanInterval,
    wilsonInterval,
    bootstrapInterval,
    exponentialMLE,
    evaluateEstimator,
    studentTQuantile,
    EstimationRegistry,
    EstimationError
};
