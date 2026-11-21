'use strict';

/*
 * Statistical Tests: t-test, z-test, chi-square, and ANOVA.
 *
 * Node.js implementation emphasizing asynchronous experiment processing,
 * immutable observations, policy validation, and event-driven reporting.
 *
 * Run: node statistical_tests.js
 */

const { EventEmitter } = require('node:events');

class StatisticalError extends Error {
    constructor(message) {
        super(message);
        this.name = 'StatisticalError';
    }
}

const Statistics = {
    validateAlpha(alpha) {
        if (!(alpha > 0 && alpha < 1)) {
            throw new StatisticalError('Alpha must be between zero and one.');
        }
    },

    sample(values, name = 'sample') {
        if (!Array.isArray(values) || values.length < 2) {
            throw new StatisticalError(`${name} requires at least two observations.`);
        }

        const result = values.map(Number);

        if (result.some(x => !Number.isFinite(x))) {
            throw new StatisticalError(`${name} contains invalid observations.`);
        }

        return Object.freeze(result);
    },

    mean(values) {
        return values.reduce((a, b) => a + b, 0) / values.length;
    },

    variance(values) {
        const avg = this.mean(values);
        return values.reduce((sum, x) => sum + (x - avg) ** 2, 0)
            / (values.length - 1);
    },

    logGamma(z) {
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
                - this.logGamma(1 - z);
        }

        z -= 1;
        let x = 0.9999999999998099;

        coefficients.forEach((c, i) => {
            x += c / (z + i + 1);
        });

        const t = z + coefficients.length - 0.5;

        return 0.5 * Math.log(2 * Math.PI)
            + (z + 0.5) * Math.log(t) - t + Math.log(x);
    },

    betaFraction(a, b, x) {
        const qab = a + b;
        const qap = a + 1;
        const qam = a - 1;
        let c = 1;
        let d = 1 - qab * x / qap;

        if (Math.abs(d) < 1e-300) d = 1e-300;

        d = 1 / d;
        let h = d;

        for (let m = 1; m <= 10000; m++) {
            const m2 = 2 * m;

            let aa = m * (b - m) * x
                / ((qam + m2) * (a + m2));

            d = 1 + aa * d;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = 1 + aa / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;
            h *= d * c;

            aa = -(a + m) * (qab + m) * x
                / ((a + m2) * (qap + m2));

            d = 1 + aa * d;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = 1 + aa / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;
            const delta = d * c;
            h *= delta;

            if (Math.abs(delta - 1) < 3e-14) {
                return h;
            }
        }

        throw new StatisticalError('Beta fraction failed to converge.');
    },

    betaRegularized(x, a, b) {
        if (a <= 0 || b <= 0 || x < 0 || x > 1) {
            throw new StatisticalError('Invalid beta parameters.');
        }

        if (x === 0) return 0;
        if (x === 1) return 1;

        const bt = Math.exp(
            this.logGamma(a + b)
            - this.logGamma(a)
            - this.logGamma(b)
            + a * Math.log(x)
            + b * Math.log1p(-x)
        );

        let result;

        if (x < (a + 1) / (a + b + 2)) {
            result = bt * this.betaFraction(a, b, x) / a;
        } else {
            result = 1 - bt * this.betaFraction(b, a, 1 - x) / b;
        }

        return Math.max(0, Math.min(1, result));
    },

    gammaQ(a, x) {
        if (a <= 0 || x < 0) {
            throw new StatisticalError('Invalid gamma parameters.');
        }

        if (x === 0) return 1;

        const gln = this.logGamma(a);

        if (x < a + 1) {
            let ap = a;
            let term = 1 / a;
            let sum = term;

            for (let i = 0; i < 10000; i++) {
                ap++;
                term *= x / ap;
                sum += term;

                if (Math.abs(term) < Math.abs(sum) * 3e-14) {
                    return Math.max(
                        0,
                        Math.min(1, 1 - sum * Math.exp(-x + a * Math.log(x) - gln))
                    );
                }
            }

            throw new StatisticalError('Gamma series did not converge.');
        }

        let b = x + 1 - a;
        let c = 1e300;
        let d = 1 / b;
        let h = d;

        for (let i = 1; i <= 10000; i++) {
            const an = -i * (i - a);
            b += 2;

            d = an * d + b;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = b + an / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;
            const delta = d * c;
            h *= delta;

            if (Math.abs(delta - 1) < 3e-14) {
                return Math.max(
                    0,
                    Math.min(1, Math.exp(-x + a * Math.log(x) - gln) * h)
                );
            }
        }

        throw new StatisticalError('Gamma continued fraction failed.');
    },

    normalCDF(z) {
        const sign = z < 0 ? -1 : 1;
        const x = Math.abs(z) / Math.sqrt(2);

        const t = 1 / (1 + 0.3275911 * x);

        const erf = 1 - (
            (((((1.061405429 * t - 1.453152027) * t)
                + 1.421413741) * t - 0.284496736) * t
                + 0.254829592) * t
        ) * Math.exp(-x * x);

        return 0.5 * (1 + sign * erf);
    },

    normalTwoSided(z) {
        return 2 * (1 - this.normalCDF(Math.abs(z)));
    },

    tPValue(t, df) {
        return this.betaRegularized(
            df / (df + t * t),
            df / 2,
            0.5
        );
    },

    chiSquareP(statistic, df) {
        return this.gammaQ(df / 2, statistic / 2);
    },

    fPValue(statistic, df1, df2) {
        return this.betaRegularized(
            df2 / (df2 + df1 * statistic),
            df2 / 2,
            df1 / 2
        );
    },

    criticalT(df, alpha) {
        return this.inverse(
            x => 1 - this.tPValue(x, df) / 2,
            1 - alpha / 2,
            0,
            1e7
        );
    },

    inverse(fn, probability, low, high) {
        for (let i = 0; i < 150; i++) {
            const mid = (low + high) / 2;

            if (fn(mid) < probability) low = mid;
            else high = mid;
        }

        return (low + high) / 2;
    },

    result(name, statistic, pValue, df, alpha, effectSize = null) {
        return Object.freeze({
            name,
            statistic,
            pValue,
            degreesOfFreedom: df,
            alpha,
            rejectNull: pValue < alpha,
            effectSize
        });
    },

    oneSampleT(data, reference, alpha = 0.05) {
        this.validateAlpha(alpha);

        const x = this.sample(data);
        const avg = this.mean(x);
        const s = Math.sqrt(this.variance(x));
        const se = s / Math.sqrt(x.length);

        if (se === 0) {
            throw new StatisticalError('Zero variance.');
        }

        const t = (avg - reference) / se;
        const df = x.length - 1;

        return this.result(
            'One-sample t-test',
            t,
            this.tPValue(t, df),
            df,
            alpha,
            (avg - reference) / s
        );
    },

    independentT(first, second, alpha = 0.05) {
        this.validateAlpha(alpha);

        const a = this.sample(first, 'First group');
        const b = this.sample(second, 'Second group');

        const difference = this.mean(a) - this.mean(b);
        const va = this.variance(a);
        const vb = this.variance(b);

        // Welch's unequal-variance test.
        const x = va / a.length;
        const y = vb / b.length;
        const se2 = x + y;

        if (se2 === 0) {
            throw new StatisticalError('Zero combined variance.');
        }

        const df = se2 ** 2 / (
            x ** 2 / (a.length - 1)
            + y ** 2 / (b.length - 1)
        );

        const statistic = difference / Math.sqrt(se2);

        return this.result(
            'Welch independent t-test',
            statistic,
            this.tPValue(statistic, df),
            df,
            alpha
        );
    },

    pairedT(before, after, alpha = 0.05) {
        if (!Array.isArray(before) || !Array.isArray(after)
            || before.length !== after.length) {
            throw new StatisticalError('Paired arrays must have equal lengths.');
        }

        const differences = after.map((value, i) => value - before[i]);

        return this.oneSampleT(differences, 0, alpha);
    },

    zTest(sampleMean, populationMean, populationSD, n, alpha = 0.05) {
        this.validateAlpha(alpha);

        if (populationSD <= 0 || n <= 0) {
            throw new StatisticalError('Invalid population standard deviation or sample size.');
        }

        const statistic = (
            sampleMean - populationMean
        ) / (populationSD / Math.sqrt(n));

        return this.result(
            'One-sample z-test',
            statistic,
            this.normalTwoSided(statistic),
            null,
            alpha
        );
    },

    chiSquareIndependence(table, alpha = 0.05) {
        this.validateAlpha(alpha);

        if (!Array.isArray(table) || table.length < 2) {
            throw new StatisticalError('At least two rows are required.');
        }

        const columns = table[0].length;

        if (columns < 2 || table.some(row => row.length !== columns)) {
            throw new StatisticalError('Invalid contingency table dimensions.');
        }

        if (table.some(row => row.some(x => !Number.isFinite(x) || x < 0))) {
            throw new StatisticalError('Invalid frequency.');
        }

        const rowTotals = table.map(row => row.reduce((a, b) => a + b, 0));
        const colTotals = Array.from({ length: columns }, (_, j) =>
            table.reduce((sum, row) => sum + row[j], 0)
        );

        const total = rowTotals.reduce((a, b) => a + b, 0);

        if (total <= 0) throw new StatisticalError('Empty contingency table.');

        let statistic = 0;

        table.forEach((row, i) => {
            row.forEach((observed, j) => {
                const expected = rowTotals[i] * colTotals[j] / total;

                if (expected <= 0) {
                    throw new StatisticalError('Zero expected frequency.');
                }

                statistic += (observed - expected) ** 2 / expected;
            });
        });

        const df = (table.length - 1) * (columns - 1);

        return this.result(
            'Chi-square independence',
            statistic,
            this.chiSquareP(statistic, df),
            df,
            alpha,
            Math.sqrt(statistic / (total * Math.min(table.length - 1, columns - 1)))
        );
    },

    anova(groups, alpha = 0.05) {
        this.validateAlpha(alpha);

        if (!Array.isArray(groups) || groups.length < 2) {
            throw new StatisticalError('ANOVA requires at least two groups.');
        }

        const samples = groups.map((g, i) => this.sample(g, `Group ${i + 1}`));

        const totalN = samples.reduce((sum, g) => sum + g.length, 0);
        const grandMean = samples.reduce(
            (sum, g) => sum + g.reduce((a, b) => a + b, 0),
            0
        ) / totalN;

        let ssBetween = 0;
        let ssWithin = 0;

        for (const group of samples) {
            const avg = this.mean(group);

            ssBetween += group.length * (avg - grandMean) ** 2;

            for (const x of group) {
                ssWithin += (x - avg) ** 2;
            }
        }

        const df1 = samples.length - 1;
        const df2 = totalN - samples.length;

        const msWithin = ssWithin / df2;

        if (msWithin === 0) {
            throw new StatisticalError('Within-group variance is zero.');
        }

        const f = (ssBetween / df1) / msWithin;

        return this.result(
            'One-way ANOVA',
            f,
            this.fPValue(f, df1, df2),
            df2,
            alpha,
            ssBetween / (ssBetween + ssWithin)
        );
    }
};


class Experiment extends EventEmitter {
    #experiments = new Map();

    register(id, testFunction, metadata = {}) {
        if (!id || this.#experiments.has(id)) {
            throw new StatisticalError('Experiment ID must be unique.');
        }

        if (typeof testFunction !== 'function') {
            throw new StatisticalError('A valid test function is required.');
        }

        this.#experiments.set(id, Object.freeze({
            id,
            testFunction,
            metadata: Object.freeze({ ...metadata })
        }));

        this.emit('registered', { id });
    }

    async execute(id) {
        const experiment = this.#experiments.get(id);

        if (!experiment) {
            throw new StatisticalError(`Unknown experiment: ${id}`);
        }

        this.emit('started', { id });

        try {
            // Isolate the experiment's result from other experiment state.
            const result = await Promise.resolve(
                experiment.testFunction()
            );

            this.emit('completed', { id, result });

            return Object.freeze({
                id,
                metadata: experiment.metadata,
                result
            });
        } catch (error) {
            this.emit('failed', { id, error: error.message });
            throw error;
        }
    }

    async executeAll(concurrency = 3) {
        if (!Number.isInteger(concurrency) || concurrency < 1) {
            throw new StatisticalError('Concurrency must be a positive integer.');
        }

        const ids = [...this.#experiments.keys()];
        const results = [];
        const errors = [];

        // Bounded execution avoids unbounded task creation.
        for (let i = 0; i < ids.length; i += concurrency) {
            const batch = ids.slice(i, i + concurrency);

            const outcomes = await Promise.allSettled(
                batch.map(id => this.execute(id))
            );

            outcomes.forEach((outcome, index) => {
                if (outcome.status === 'fulfilled') {
                    results.push(outcome.value);
                } else {
                    errors.push({
                        id: batch[index],
                        error: outcome.reason.message
                    });
                }
            });
        }

        return Object.freeze({
            results: Object.freeze(results),
            errors: Object.freeze(errors)
        });
    }
}


async function main() {
    const manager = new Experiment();

    manager.on('registered', event =>
        console.log(`Registered: ${event.id}`)
    );

    manager.on('started', event =>
        console.log(`Executing: ${event.id}`)
    );

    manager.on('completed', event =>
        console.log(`Completed: ${event.id}`)
    );

    manager.on('failed', event =>
        console.error(`Failed: ${event.id}: ${event.error}`)
    );

    manager.register(
        'production-quality',
        () => Statistics.oneSampleT(
            [51, 53, 49, 52, 55, 50, 54, 52],
            50
        ),
        { domain: 'quality-control', method: 'one-sample-t' }
    );

    manager.register(
        'treatment-comparison',
        () => Statistics.independentT(
            [68, 70, 72, 65, 71, 69, 67],
            [75, 78, 74, 80, 77, 76, 79]
        ),
        { domain: 'clinical-research', method: 'welch-t' }
    );

    manager.register(
        'before-after',
        () => Statistics.pairedT(
            [70, 72, 68, 75, 71, 69],
            [74, 76, 72, 78, 75, 73]
        ),
        { domain: 'performance', method: 'paired-t' }
    );

    manager.register(
        'population-mean',
        () => Statistics.zTest(102, 100, 10, 100),
        { domain: 'sampling', method: 'z-test' }
    );

    manager.register(
        'customer-preferences',
        () => Statistics.chiSquareIndependence([
            [40, 20],
            [30, 50]
        ]),
        { domain: 'market-research', method: 'chi-square' }
    );

    manager.register(
        'three-production-lines',
        () => Statistics.anova([
            [18, 20, 19, 21, 17],
            [24, 25, 23, 26, 22],
            [29, 30, 28, 31, 27]
        ]),
        { domain: 'manufacturing', method: 'anova' }
    );

    const report = await manager.executeAll(2);

    console.log('\nEXPERIMENT REPORT');

    for (const item of report.results) {
        const r = item.result;

        console.log({
            experiment: item.id,
            test: r.name,
            statistic: Number(r.statistic.toFixed(6)),
            pValue: Number(r.pValue.toFixed(8)),
            df: r.degreesOfFreedom,
            decision: r.rejectNull ? 'Reject H0' : 'Fail to reject H0'
        });
    }

    console.log('\nFailures:', report.errors);

    if (Math.abs(Statistics.normalCDF(0) - 0.5) > 1e-5) {
        throw new Error('Normal distribution validation failed.');
    }

    if (Statistics.chiSquareP(0, 2) !== 1) {
        throw new Error('Chi-square validation failed.');
    }

    console.log('Numerical validation passed.');
}

main().catch(error => {
    console.error('Execution failed:', error.message);
    process.exitCode = 1;
});
