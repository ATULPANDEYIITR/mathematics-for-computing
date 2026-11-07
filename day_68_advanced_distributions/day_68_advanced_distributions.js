"use strict";

/*
 * Advanced Distributions
 * Poisson, Gamma, Beta, and Chi-square.
 *
 * Runtime: Node.js 18+
 * No third-party packages required.
 *
 * Implements numerical probability functions, simulation,
 * Bayesian updating, statistical validation and hypothesis testing.
 */

const EPSILON = 1e-12;
const MAX_ITERATIONS = 10000;

class StatisticalError extends Error {
    constructor(message) {
        super(message);
        this.name = "StatisticalError";
    }
}

function positive(value, name) {
    if (!Number.isFinite(value) || value <= 0) {
        throw new StatisticalError(`${name} must be finite and positive.`);
    }
}

function nonnegative(value, name) {
    if (!Number.isFinite(value) || value < 0) {
        throw new StatisticalError(`${name} must be finite and nonnegative.`);
    }
}

function probability(value, name = "Probability") {
    if (!Number.isFinite(value) || value < 0 || value > 1) {
        throw new StatisticalError(`${name} must be between zero and one.`);
    }
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

    if (!Number.isFinite(z) || z <= 0) {
        throw new StatisticalError("Log-gamma requires a positive finite input.");
    }

    if (z < 0.5) {
        return Math.log(Math.PI)
            - Math.log(Math.sin(Math.PI * z))
            - logGamma(1 - z);
    }

    z -= 1;

    let x = 0.9999999999998099;

    coefficients.forEach((coefficient, i) => {
        x += coefficient / (z + i + 1);
    });

    const t = z + coefficients.length - 0.5;

    return 0.9189385332046727
        + (z + 0.5) * Math.log(t)
        - t
        + Math.log(x);
}

function regularizedGammaP(a, x) {
    positive(a, "Shape");
    nonnegative(x, "x");

    if (x === 0) return 0;
    if (x === Infinity) return 1;

    const factor = Math.exp(
        a * Math.log(x) - x - logGamma(a)
    );

    if (x < a + 1) {
        let term = 1 / a;
        let sum = term;
        let current = a;

        for (let i = 0; i < MAX_ITERATIONS; i++) {
            current++;
            term *= x / current;
            sum += term;

            if (Math.abs(term) <= Math.abs(sum) * EPSILON) {
                return Math.min(1, Math.max(0, factor * sum));
            }
        }

        throw new Error("Gamma series did not converge.");
    }

    let b = x + 1 - a;
    let c = 1e300;
    let d = 1 / b;
    let h = d;

    for (let i = 1; i <= MAX_ITERATIONS; i++) {
        const an = -i * (i - a);
        b += 2;

        d = an * d + b;
        if (Math.abs(d) < 1e-300) d = 1e-300;

        c = b + an / c;
        if (Math.abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;

        const delta = d * c;
        h *= delta;

        if (Math.abs(delta - 1) <= EPSILON) {
            return Math.min(1, Math.max(0, 1 - factor * h));
        }
    }

    throw new Error("Gamma continued fraction did not converge.");
}

function betaFraction(a, b, x) {
    const qab = a + b;
    const qap = a + 1;
    const qam = a - 1;

    let c = 1;
    let d = 1 - qab * x / qap;

    if (Math.abs(d) < 1e-300) d = 1e-300;

    d = 1 / d;

    let h = d;

    for (let m = 1; m <= MAX_ITERATIONS; m++) {
        const m2 = 2 * m;

        let term = m * (b - m) * x
            / ((qam + m2) * (a + m2));

        d = 1 + term * d;
        if (Math.abs(d) < 1e-300) d = 1e-300;

        c = 1 + term / c;
        if (Math.abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;
        h *= d * c;

        term = -(a + m) * (qab + m) * x
            / ((a + m2) * (qap + m2));

        d = 1 + term * d;
        if (Math.abs(d) < 1e-300) d = 1e-300;

        c = 1 + term / c;
        if (Math.abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;

        const delta = d * c;
        h *= delta;

        if (Math.abs(delta - 1) <= EPSILON) {
            return h;
        }
    }

    throw new Error("Beta continued fraction did not converge.");
}

function regularizedBeta(x, a, b) {
    positive(a, "Alpha");
    positive(b, "Beta");

    if (!Number.isFinite(x) || x < 0 || x > 1) {
        throw new StatisticalError("x must be between zero and one.");
    }

    if (x === 0) return 0;
    if (x === 1) return 1;

    const factor = Math.exp(
        logGamma(a + b) - logGamma(a) - logGamma(b)
        + a * Math.log(x) + b * Math.log1p(-x)
    );

    const result = x < (a + 1) / (a + b + 2)
        ? factor * betaFraction(a, b, x) / a
        : 1 - factor * betaFraction(b, a, 1 - x) / b;

    return Math.min(1, Math.max(0, result));
}

class RandomSource {
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        // Deterministic xorshift32 generator for reproducible examples.
        let x = this.state;
        x ^= x << 13;
        x ^= x >>> 17;
        x ^= x << 5;
        this.state = x >>> 0;

        return this.state / 4294967296;
    }

    normal() {
        const u1 = Math.max(this.next(), Number.MIN_VALUE);
        const u2 = this.next();

        return Math.sqrt(-2 * Math.log(u1))
            * Math.cos(2 * Math.PI * u2);
    }

    gamma(shape, scale = 1) {
        positive(shape, "Gamma shape");
        positive(scale, "Gamma scale");

        if (shape < 1) {
            return this.gamma(shape + 1, scale)
                * Math.pow(this.next(), 1 / shape);
        }

        const d = shape - 1 / 3;
        const c = 1 / Math.sqrt(9 * d);

        for (let i = 0; i < 100000; i++) {
            const x = this.normal();
            const v0 = 1 + c * x;

            if (v0 <= 0) continue;

            const v = v0 ** 3;
            const u = this.next();

            if (
                u < 1 - 0.0331 * x ** 4
                || Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))
            ) {
                return scale * d * v;
            }
        }

        throw new Error("Gamma sampling did not converge.");
    }

    beta(a, b) {
        const x = this.gamma(a);
        const y = this.gamma(b);
        return x / (x + y);
    }

    poisson(rate) {
        positive(rate, "Poisson rate");

        if (rate < 30) {
            const limit = Math.exp(-rate);
            let product = 1;
            let count = 0;

            do {
                count++;
                product *= this.next();
            } while (product > limit);

            return count - 1;
        }

        // PTRS transformed rejection for larger rates.
        const sqrtRate = Math.sqrt(rate);
        const b = 0.931 + 2.53 * sqrtRate;
        const a = -0.059 + 0.02483 * b;
        const inverseAlpha = 1.1239 + 1.1328 / (b - 3.4);
        const vr = 0.9277 - 3.6224 / (b - 2);

        for (let i = 0; i < 100000; i++) {
            const u = this.next() - 0.5;
            const v = this.next();
            const us = 0.5 - Math.abs(u);

            if (us <= 0) continue;

            const k = Math.floor(
                (2 * a / us + b) * u + rate + 0.43
            );

            if (us >= 0.07 && v <= vr && k >= 0) return k;

            if (k < 0 || (us < 0.013 && v > us)) continue;

            const lhs = Math.log(
                v * inverseAlpha / (a / (us * us) + b)
            );

            const rhs = -rate + k * Math.log(rate) - logGamma(k + 1);

            if (lhs <= rhs) return k;
        }

        throw new Error("Poisson sampling did not converge.");
    }
}

class PoissonDistribution {
    constructor(rate) {
        positive(rate, "Lambda");
        this.rate = rate;
    }

    pmf(k) {
        if (!Number.isSafeInteger(k)) {
            throw new StatisticalError("Count must be a safe integer.");
        }

        if (k < 0) return 0;

        return Math.exp(
            k * Math.log(this.rate)
            - this.rate
            - logGamma(k + 1)
        );
    }

    cdf(k) {
        if (!Number.isSafeInteger(k)) {
            throw new StatisticalError("Count must be a safe integer.");
        }

        return k < 0 ? 0 : regularizedGammaP(k + 1, this.rate);
    }

    get mean() { return this.rate; }
    get variance() { return this.rate; }

    sample(rng) {
        return rng.poisson(this.rate);
    }
}

class GammaDistribution {
    constructor(shape, scale) {
        positive(shape, "Shape");
        positive(scale, "Scale");

        this.shape = shape;
        this.scale = scale;
    }

    pdf(x) {
        if (x < 0) return 0;

        if (x === 0) {
            if (this.shape < 1) return Infinity;
            if (this.shape === 1) return 1 / this.scale;
            return 0;
        }

        return Math.exp(
            (this.shape - 1) * Math.log(x)
            - x / this.scale
            - logGamma(this.shape)
            - this.shape * Math.log(this.scale)
        );
    }

    cdf(x) {
        return x <= 0
            ? 0
            : regularizedGammaP(this.shape, x / this.scale);
    }

    get mean() { return this.shape * this.scale; }

    get variance() {
        return this.shape * this.scale ** 2;
    }

    sample(rng) {
        return rng.gamma(this.shape, this.scale);
    }
}

class BetaDistribution {
    constructor(alpha, beta) {
        positive(alpha, "Alpha");
        positive(beta, "Beta");

        this.alpha = alpha;
        this.beta = beta;
    }

    pdf(x) {
        if (x < 0 || x > 1) return 0;

        const logNormalizer = logGamma(this.alpha + this.beta)
            - logGamma(this.alpha)
            - logGamma(this.beta);

        if (x === 0) {
            if (this.alpha < 1) return Infinity;
            if (this.alpha > 1) return 0;
            return Math.exp(logNormalizer);
        }

        if (x === 1) {
            if (this.beta < 1) return Infinity;
            if (this.beta > 1) return 0;
            return Math.exp(logNormalizer);
        }

        return Math.exp(
            (this.alpha - 1) * Math.log(x)
            + (this.beta - 1) * Math.log1p(-x)
            + logNormalizer
        );
    }

    cdf(x) {
        return regularizedBeta(x, this.alpha, this.beta);
    }

    get mean() {
        return this.alpha / (this.alpha + this.beta);
    }

    get variance() {
        const total = this.alpha + this.beta;

        return this.alpha * this.beta
            / (total * total * (total + 1));
    }

    sample(rng) {
        return rng.beta(this.alpha, this.beta);
    }
}

class ChiSquareDistribution {
    constructor(df) {
        positive(df, "Degrees of freedom");
        this.df = df;
    }

    pdf(x) {
        if (x < 0) return 0;

        if (x === 0) {
            if (this.df < 2) return Infinity;
            if (this.df === 2) return 0.5;
            return 0;
        }

        return Math.exp(
            (this.df / 2 - 1) * Math.log(x)
            - x / 2
            - this.df / 2 * Math.log(2)
            - logGamma(this.df / 2)
        );
    }

    cdf(x) {
        return x <= 0 ? 0 : regularizedGammaP(this.df / 2, x / 2);
    }

    get mean() { return this.df; }
    get variance() { return 2 * this.df; }

    sample(rng) {
        return rng.gamma(this.df / 2, 2);
    }
}

function chiSquareGoodnessOfFit(observed, expected, alpha = 0.05) {
    if (
        !Array.isArray(observed)
        || !Array.isArray(expected)
        || observed.length < 2
        || observed.length !== expected.length
    ) {
        throw new StatisticalError("Frequency arrays must have equal lengths.");
    }

    probability(alpha, "Alpha");

    if (alpha === 0 || alpha === 1) {
        throw new StatisticalError("Alpha must be strictly between zero and one.");
    }

    if (observed.some(x => !Number.isSafeInteger(x) || x < 0)) {
        throw new StatisticalError("Observed counts must be nonnegative integers.");
    }

    if (expected.some(x => !Number.isFinite(x) || x < 5)) {
        throw new StatisticalError("Expected frequencies must be at least five.");
    }

    const observedTotal = observed.reduce((a, b) => a + b, 0);
    const expectedTotal = expected.reduce((a, b) => a + b, 0);

    if (
        Math.abs(observedTotal - expectedTotal)
        > 1e-9 * Math.max(1, observedTotal)
    ) {
        throw new StatisticalError("Frequency totals must match.");
    }

    const statistic = observed.reduce(
        (sum, value, i) => sum + (value - expected[i]) ** 2 / expected[i],
        0
    );

    const df = observed.length - 1;

    const pValue = 1 - regularizedGammaP(df / 2, statistic / 2);

    return Object.freeze({
        statistic,
        degreesOfFreedom: df,
        pValue,
        alpha,
        rejectNull: pValue < alpha
    });
}

function summarize(distribution, rng, count = 10000) {
    if (!Number.isSafeInteger(count) || count <= 0) {
        throw new StatisticalError("Sample size must be a positive integer.");
    }

    const samples = Array.from(
        { length: count },
        () => distribution.sample(rng)
    );

    const mean = samples.reduce((sum, x) => sum + x, 0) / count;

    const variance = samples.reduce(
        (sum, x) => sum + (x - mean) ** 2,
        0
    ) / count;

    return {
        count,
        empiricalMean: mean,
        empiricalVariance: variance,
        theoreticalMean: distribution.mean,
        theoreticalVariance: distribution.variance,
        minimum: Math.min(...samples),
        maximum: Math.max(...samples)
    };
}

async function runExperiment(name, distribution, rng) {
    // Event-driven execution permits independent experiments to run concurrently.
    await Promise.resolve();

    return {
        name,
        theoreticalMean: distribution.mean,
        theoreticalVariance: distribution.variance,
        simulation: summarize(distribution, rng)
    };
}

async function main() {
    const rng = new RandomSource(42);

    const distributions = new Map([
        ["Poisson", new PoissonDistribution(4.5)],
        ["Gamma", new GammaDistribution(3, 2)],
        ["Beta", new BetaDistribution(2, 5)],
        ["Chi-square", new ChiSquareDistribution(4)]
    ]);

    console.log("ADVANCED DISTRIBUTIONS");
    console.log("======================");

    for (const [name, distribution] of distributions) {
        console.log(`\n${name}`);
        console.log(`Mean: ${distribution.mean.toFixed(6)}`);
        console.log(`Variance: ${distribution.variance.toFixed(6)}`);

        for (const x of [0.5, 1, 2, 4, 8]) {
            const density = name === "Poisson"
                ? distribution.pmf(Math.floor(x))
                : distribution.pdf(x);

            console.log(
                `x=${x}: density=${density.toFixed(8)}, `
                + `CDF=${distribution.cdf(name === "Poisson" ? Math.floor(x) : x).toFixed(8)}`
            );
        }
    }

    console.log("\nBAYESIAN CONVERSION RATE");
    const prior = new BetaDistribution(2, 2);

    const successes = 45;
    const failures = 55;

    const posterior = new BetaDistribution(
        prior.alpha + successes,
        prior.beta + failures
    );

    console.log("Prior mean:", prior.mean);
    console.log("Posterior mean:", posterior.mean);
    console.log("P(rate <= 0.5):", posterior.cdf(0.5));

    console.log("\nPARALLEL SIMULATION REPORT");

    const reports = await Promise.all(
        [...distributions.entries()].map(([name, distribution]) =>
            runExperiment(name, distribution, rng)
        )
    );

    reports.forEach(report => {
        console.log(`\n${report.name}`);
        console.log(report.simulation);
    });

    console.log("\nCHI-SQUARE GOODNESS OF FIT");

    const result = chiSquareGoodnessOfFit(
        [48, 32, 15, 5],
        [50, 30, 15, 5]
    );

    console.log(result);

    if (result.rejectNull) {
        console.log("Reject the null hypothesis.");
    } else {
        console.log("Insufficient evidence to reject the null hypothesis.");
    }

    console.log("\nVALIDATION TESTS");

    if (new PoissonDistribution(4).pmf(0) <= 0) {
        throw new Error("Poisson PMF test failed.");
    }

    if (Math.abs(new BetaDistribution(2, 5).mean - 2 / 7) > 1e-10) {
        throw new Error("Beta mean test failed.");
    }

    if (Math.abs(new ChiSquareDistribution(4).variance - 8) > 1e-10) {
        throw new Error("Chi-square variance test failed.");
    }

    if (regularizedBeta(1, 2, 5) !== 1) {
        throw new Error("Beta boundary test failed.");
    }

    console.log("All tests passed.");
}

main().catch(error => {
    console.error("Experiment failed:", error.message);
    process.exitCode = 1;
});
