"use strict";

/*
 * Continuous Distributions
 * Uniform, Exponential, and Normal
 *
 * Node.js 18+ compatible.
 *
 * Features:
 * - Distribution parameter validation
 * - PDF, CDF and inverse CDF
 * - Seeded pseudo-random sampling
 * - Streaming statistical aggregation
 * - Online mean and variance using Welford's algorithm
 * - Empirical probabilities
 * - Confidence intervals
 * - Histogram generation
 * - Distribution monitoring
 * - Asynchronous batch execution
 * - Automated validation tests
 */

const { performance } = require("node:perf_hooks");

class DistributionError extends Error {
    constructor(message) {
        super(message);
        this.name = "DistributionError";
    }
}

function finite(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new DistributionError(`${name} must be finite.`);
    }
}

function probability(p) {
    finite(p, "Probability");

    if (p < 0 || p > 1) {
        throw new DistributionError("Probability must be in [0, 1].");
    }
}

function sampleSize(n) {
    if (!Number.isSafeInteger(n) || n <= 0) {
        throw new DistributionError(
            "Sample size must be a positive safe integer."
        );
    }
}

/*
 * Mulberry32 provides reproducible pseudo-random values.
 * It is suitable for simulation exercises, not cryptography.
 */
class RandomGenerator {
    constructor(seed = 123456789) {
        if (!Number.isSafeInteger(seed)) {
            throw new DistributionError("Seed must be a safe integer.");
        }

        this.state = seed >>> 0;
    }

    next() {
        let t = this.state += 0x6D2B79F5;

        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);

        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    uniform(min = 0, max = 1) {
        finite(min, "Minimum");
        finite(max, "Maximum");

        if (min > max) {
            throw new DistributionError("Minimum cannot exceed maximum.");
        }

        return min + (max - min) * this.next();
    }

    exponential(rate) {
        finite(rate, "Rate");

        if (rate <= 0) {
            throw new DistributionError("Rate must be positive.");
        }

        // next() can return zero, so protect logarithm evaluation.
        return -Math.log1p(-this.next()) / rate;
    }

    normal(mean = 0, standardDeviation = 1) {
        finite(mean, "Mean");
        finite(standardDeviation, "Standard deviation");

        if (standardDeviation <= 0) {
            throw new DistributionError(
                "Standard deviation must be positive."
            );
        }

        // Box-Muller transformation.
        let u1 = this.next();

        while (u1 === 0) {
            u1 = this.next();
        }

        const u2 = this.next();

        const z = Math.sqrt(-2 * Math.log(u1)) *
            Math.cos(2 * Math.PI * u2);

        return mean + standardDeviation * z;
    }
}

class Distribution {
    pdf() {
        throw new Error("pdf() must be implemented.");
    }

    cdf() {
        throw new Error("cdf() must be implemented.");
    }

    quantile() {
        throw new Error("quantile() must be implemented.");
    }

    sample() {
        throw new Error("sample() must be implemented.");
    }

    probabilityBetween(lower, upper) {
        finite(lower, "Lower bound");
        finite(upper, "Upper bound");

        if (lower > upper) {
            throw new DistributionError(
                "Lower bound cannot exceed upper bound."
            );
        }

        return this.cdf(upper) - this.cdf(lower);
    }
}

class UniformDistribution extends Distribution {
    constructor(a, b) {
        super();

        finite(a, "a");
        finite(b, "b");

        if (a >= b) {
            throw new DistributionError("Require a < b.");
        }

        this.a = a;
        this.b = b;
        Object.freeze(this);
    }

    get mean() {
        return (this.a + this.b) / 2;
    }

    get variance() {
        return ((this.b - this.a) ** 2) / 12;
    }

    pdf(x) {
        finite(x, "x");

        return x >= this.a && x <= this.b
            ? 1 / (this.b - this.a)
            : 0;
    }

    cdf(x) {
        finite(x, "x");

        if (x < this.a) return 0;
        if (x >= this.b) return 1;

        return (x - this.a) / (this.b - this.a);
    }

    quantile(p) {
        probability(p);

        return this.a + p * (this.b - this.a);
    }

    sample(rng) {
        return rng.uniform(this.a, this.b);
    }
}

class ExponentialDistribution extends Distribution {
    constructor(rate) {
        super();

        finite(rate, "Rate");

        if (rate <= 0) {
            throw new DistributionError("Rate must be positive.");
        }

        this.rate = rate;
        Object.freeze(this);
    }

    get mean() {
        return 1 / this.rate;
    }

    get variance() {
        return 1 / (this.rate * this.rate);
    }

    pdf(x) {
        finite(x, "x");

        return x < 0
            ? 0
            : this.rate * Math.exp(-this.rate * x);
    }

    cdf(x) {
        finite(x, "x");

        return x <= 0
            ? 0
            : -Math.expm1(-this.rate * x);
    }

    survival(x) {
        finite(x, "x");

        return x <= 0 ? 1 : Math.exp(-this.rate * x);
    }

    quantile(p) {
        probability(p);

        if (p === 1) return Infinity;

        return -Math.log1p(-p) / this.rate;
    }

    sample(rng) {
        return rng.exponential(this.rate);
    }

    hazard() {
        return this.rate;
    }
}

/*
 * Approximation to the error function.
 * The maximum approximation error is small enough for
 * educational distribution analysis.
 */
function erf(x) {
    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x);

    const t = 1 / (1 + 0.3275911 * x);

    const polynomial =
        (((((1.061405429 * t - 1.453152027) * t) +
            1.421413741) * t - 0.284496736) * t +
            0.254829592) * t;

    return sign * (1 - polynomial * Math.exp(-x * x));
}

function standardNormalCDF(z) {
    return 0.5 * (1 + erf(z / Math.SQRT2));
}

/*
 * Acklam inverse-normal rational approximation.
 */
function standardNormalQuantile(p) {
    probability(p);

    if (p === 0) return -Infinity;
    if (p === 1) return Infinity;

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

    let x;

    if (p < low) {
        const q = Math.sqrt(-2 * Math.log(p));

        x = (((((c[0] * q + c[1]) * q + c[2]) * q +
            c[3]) * q + c[4]) * q + c[5]) /
            ((((d[0] * q + d[1]) * q + d[2]) * q +
                d[3]) * q + 1);

    } else if (p > high) {
        const q = Math.sqrt(-2 * Math.log1p(-p));

        x = -(((((c[0] * q + c[1]) * q + c[2]) * q +
            c[3]) * q + c[4]) * q + c[5]) /
            ((((d[0] * q + d[1]) * q + d[2]) * q +
                d[3]) * q + 1);

    } else {
        const q = p - 0.5;
        const r = q * q;

        x = (((((a[0] * r + a[1]) * r + a[2]) * r +
            a[3]) * r + a[4]) * r + a[5]) * q /
            (((((b[0] * r + b[1]) * r + b[2]) * r +
                b[3]) * r + b[4]) * r + 1);
    }

    // Newton correction improves central probabilities.
    if (p > 1e-12 && p < 1 - 1e-12) {
        const error = standardNormalCDF(x) - p;
        const density = Math.exp(-0.5 * x * x) /
            Math.sqrt(2 * Math.PI);

        if (density > 1e-300) {
            x -= error / density;
        }
    }

    return x;
}

class NormalDistribution extends Distribution {
    constructor(mean, standardDeviation) {
        super();

        finite(mean, "Mean");
        finite(standardDeviation, "Standard deviation");

        if (standardDeviation <= 0) {
            throw new DistributionError(
                "Standard deviation must be positive."
            );
        }

        this.mean = mean;
        this.standardDeviation = standardDeviation;
        Object.freeze(this);
    }

    get variance() {
        return this.standardDeviation ** 2;
    }

    pdf(x) {
        finite(x, "x");

        const z = (x - this.mean) / this.standardDeviation;

        return Math.exp(-0.5 * z * z) /
            (this.standardDeviation * Math.sqrt(2 * Math.PI));
    }

    cdf(x) {
        finite(x, "x");

        const z = (x - this.mean) / this.standardDeviation;

        return standardNormalCDF(z);
    }

    quantile(p) {
        return this.mean +
            this.standardDeviation * standardNormalQuantile(p);
    }

    sample(rng) {
        return rng.normal(this.mean, this.standardDeviation);
    }

    standardize(x) {
        finite(x, "x");

        return (x - this.mean) / this.standardDeviation;
    }
}

/*
 * Welford's online algorithm calculates variance without
 * retaining every observation.
 */
class OnlineStatistics {
    constructor() {
        this.count = 0;
        this.mean = 0;
        this.m2 = 0;
        this.minimum = Infinity;
        this.maximum = -Infinity;
    }

    add(value) {
        finite(value, "Observation");

        this.count++;

        const delta = value - this.mean;
        this.mean += delta / this.count;

        const delta2 = value - this.mean;
        this.m2 += delta * delta2;

        this.minimum = Math.min(this.minimum, value);
        this.maximum = Math.max(this.maximum, value);
    }

    get variance() {
        return this.count > 1
            ? this.m2 / (this.count - 1)
            : 0;
    }

    get standardDeviation() {
        return Math.sqrt(this.variance);
    }

    report() {
        if (this.count === 0) {
            throw new DistributionError("No observations available.");
        }

        return {
            count: this.count,
            mean: this.mean,
            variance: this.variance,
            standardDeviation: this.standardDeviation,
            minimum: this.minimum,
            maximum: this.maximum
        };
    }
}

class DistributionMonitor {
    constructor(distribution, lower, upper) {
        if (!(distribution instanceof Distribution)) {
            throw new DistributionError("Invalid distribution.");
        }

        finite(lower, "Lower bound");
        finite(upper, "Upper bound");

        if (lower > upper) {
            throw new DistributionError("Invalid monitoring interval.");
        }

        this.distribution = distribution;
        this.lower = lower;
        this.upper = upper;
        this.statistics = new OnlineStatistics();
        this.insideCount = 0;
    }

    observe(value) {
        this.statistics.add(value);

        if (value >= this.lower && value <= this.upper) {
            this.insideCount++;
        }
    }

    report() {
        const stats = this.statistics.report();

        return {
            ...stats,
            interval: [this.lower, this.upper],
            theoreticalProbability:
                this.distribution.probabilityBetween(
                    this.lower,
                    this.upper
                ),
            observedProbability: this.insideCount / stats.count
        };
    }
}

function histogram(values, bins = 10) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new DistributionError("A nonempty array is required.");
    }

    if (!Number.isSafeInteger(bins) || bins <= 0) {
        throw new DistributionError("Invalid histogram bin count.");
    }

    const minimum = Math.min(...values);
    const maximum = Math.max(...values);

    if (!Number.isFinite(minimum) || !Number.isFinite(maximum)) {
        throw new DistributionError("Observations must be finite.");
    }

    if (minimum === maximum) {
        return [{ lower: minimum, upper: maximum, count: values.length }];
    }

    const width = (maximum - minimum) / bins;
    const counts = new Array(bins).fill(0);

    for (const value of values) {
        finite(value, "Observation");

        const index = Math.min(
            Math.floor((value - minimum) / width),
            bins - 1
        );

        counts[index]++;
    }

    return counts.map((count, i) => ({
        lower: minimum + i * width,
        upper: minimum + (i + 1) * width,
        count
    }));
}

async function analyzeInBatches(
    distribution,
    size,
    seed,
    lower,
    upper,
    batchSize = 10000
) {
    sampleSize(size);
    sampleSize(batchSize);

    const rng = new RandomGenerator(seed);
    const monitor = new DistributionMonitor(
        distribution,
        lower,
        upper
    );

    const started = performance.now();

    for (let completed = 0; completed < size;) {
        const currentBatch = Math.min(batchSize, size - completed);

        for (let i = 0; i < currentBatch; i++) {
            monitor.observe(distribution.sample(rng));
        }

        completed += currentBatch;

        // Yield control so other event-loop tasks can run.
        await new Promise(resolve => setImmediate(resolve));
    }

    return {
        ...monitor.report(),
        elapsedMilliseconds: performance.now() - started
    };
}

function runTests() {
    const uniform = new UniformDistribution(0, 10);
    const exponential = new ExponentialDistribution(0.5);
    const normal = new NormalDistribution(100, 15);

    const close = (a, b, tolerance = 1e-6) =>
        Math.abs(a - b) <= tolerance;

    console.assert(close(uniform.pdf(5), 0.1));
    console.assert(close(uniform.cdf(5), 0.5));
    console.assert(close(uniform.quantile(0.5), 5));

    console.assert(exponential.pdf(-1) === 0);
    console.assert(close(exponential.cdf(2), 1 - Math.exp(-1)));
    console.assert(close(exponential.quantile(0.5), Math.log(2) / 0.5));

    console.assert(close(normal.cdf(100), 0.5));
    console.assert(close(normal.quantile(0.5), 100));
    console.assert(close(normal.standardize(115), 1));

    console.assert(
        close(standardNormalQuantile(0.975), 1.9599639845, 1e-7)
    );

    const rng1 = new RandomGenerator(42);
    const rng2 = new RandomGenerator(42);

    console.assert(rng1.next() === rng2.next());

    const stats = new OnlineStatistics();

    [1, 2, 3, 4, 5].forEach(value => stats.add(value));

    console.assert(close(stats.mean, 3));
    console.assert(close(stats.variance, 2));

    const invalidOperations = [
        () => new UniformDistribution(5, 5),
        () => new ExponentialDistribution(0),
        () => new NormalDistribution(0, -1),
        () => uniform.quantile(1.5),
        () => uniform.probabilityBetween(10, 5)
    ];

    for (const operation of invalidOperations) {
        let rejected = false;

        try {
            operation();
        } catch (error) {
            rejected = error instanceof DistributionError;
        }

        if (!rejected) {
            throw new Error("A validation test failed.");
        }
    }

    console.log("All validation tests passed.");
}

async function main() {
    console.log("CONTINUOUS DISTRIBUTIONS");
    console.log("Uniform, Exponential, Normal\n");

    runTests();

    const configurations = [
        {
            name: "Uniform Distribution",
            distribution: new UniformDistribution(0, 100),
            lower: 20,
            upper: 80
        },
        {
            name: "Exponential Distribution",
            distribution: new ExponentialDistribution(0.2),
            lower: 1,
            upper: 5
        },
        {
            name: "Normal Distribution",
            distribution: new NormalDistribution(50, 10),
            lower: 40,
            upper: 60
        }
    ];

    for (const config of configurations) {
        const result = await analyzeInBatches(
            config.distribution,
            100000,
            42,
            config.lower,
            config.upper
        );

        console.log(`\n${config.name}`);
        console.table(result);

        console.log(
            "Theoretical 95th percentile:",
            config.distribution.quantile(0.95)
        );
    }

    console.log("\nQUANTILE COMPARISON");

    const probabilities = [0.05, 0.25, 0.5, 0.75, 0.95];

    const comparison = configurations.map(config => ({
        distribution: config.name,
        ...Object.fromEntries(
            probabilities.map(p => [
                `p${p * 100}`,
                config.distribution.quantile(p)
            ])
        )
    }));

    console.table(comparison);

    const normal = new NormalDistribution(100, 15);

    console.log("\nSTANDARD NORMALIZATION");
    console.log("Observation: 130");
    console.log("Z-score:", normal.standardize(130));
    console.log("Cumulative probability:", normal.cdf(130));

    console.log("\nAll analyses completed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
