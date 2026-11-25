'use strict';

/*
 * Entropy and Cross-Entropy Analysis
 *
 * JavaScript implementation using:
 * - Map-based probability distributions
 * - Event-driven observations
 * - Online frequency estimation
 * - Shannon entropy
 * - Cross-entropy
 * - KL divergence
 * - Classification loss
 * - Asynchronous batch evaluation
 * - Probability smoothing
 *
 * Runtime: Node.js 18+
 */

const fs = require('node:fs/promises');

class ProbabilityError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ProbabilityError';
    }
}

class ProbabilityDistribution {
    constructor(name, entries) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new ProbabilityError(
                'Distribution name must be non-empty.'
            );
        }

        if (!(entries instanceof Map) || entries.size === 0) {
            throw new ProbabilityError(
                'A non-empty Map is required.'
            );
        }

        const normalized = new Map();
        let total = 0;

        for (const [event, probability] of entries) {
            if (typeof event !== 'string' || !event.trim()) {
                throw new ProbabilityError(
                    'Event names must be non-empty strings.'
                );
            }

            if (
                typeof probability !== 'number' ||
                !Number.isFinite(probability) ||
                probability < 0 ||
                probability > 1
            ) {
                throw new ProbabilityError(
                    `Invalid probability for ${event}.`
                );
            }

            normalized.set(event, probability);
            total += probability;
        }

        if (Math.abs(total - 1) > 1e-10) {
            throw new ProbabilityError(
                `Probabilities must sum to 1. Received ${total}.`
            );
        }

        this.name = name;
        this.entries = normalized;
        Object.freeze(this);
    }

    get events() {
        return [...this.entries.keys()];
    }

    get size() {
        return this.entries.size;
    }

    probability(event) {
        return this.entries.get(event) ?? 0;
    }

    toJSON() {
        return Object.fromEntries(this.entries);
    }
}

function validateCompatible(p, q) {
    if (p.size !== q.size) {
        throw new ProbabilityError(
            'Distribution dimensions do not match.'
        );
    }

    for (const event of p.events) {
        if (!q.entries.has(event)) {
            throw new ProbabilityError(
                `Missing event in predicted distribution: ${event}`
            );
        }
    }
}

function entropy(distribution) {
    let result = 0;

    for (const probability of distribution.entries.values()) {
        if (probability > 0) {
            result -= probability * Math.log2(probability);
        }
    }

    return result;
}

function crossEntropy(actual, predicted) {
    validateCompatible(actual, predicted);

    let result = 0;

    for (const event of actual.events) {
        const p = actual.probability(event);
        const q = predicted.probability(event);

        if (p === 0) continue;
        if (q === 0) return Infinity;

        result -= p * Math.log2(q);
    }

    return result;
}

function klDivergence(actual, predicted) {
    validateCompatible(actual, predicted);

    let result = 0;

    for (const event of actual.events) {
        const p = actual.probability(event);
        const q = predicted.probability(event);

        if (p === 0) continue;
        if (q === 0) return Infinity;

        result += p * Math.log2(p / q);
    }

    return Math.max(0, result);
}

function smooth(distribution, alpha = 0.01) {
    if (!Number.isFinite(alpha) || alpha <= 0) {
        throw new ProbabilityError(
            'Alpha must be positive and finite.'
        );
    }

    const denominator = 1 + distribution.size * alpha;
    const entries = new Map();

    for (const [event, probability] of distribution.entries) {
        entries.set(
            event,
            (probability + alpha) / denominator
        );
    }

    return new ProbabilityDistribution(
        `${distribution.name}_smoothed`,
        entries
    );
}

function binaryEntropy(p) {
    if (!Number.isFinite(p) || p < 0 || p > 1) {
        throw new ProbabilityError(
            'Binary probability must belong to [0, 1].'
        );
    }

    if (p === 0 || p === 1) return 0;

    return -p * Math.log2(p) -
        (1 - p) * Math.log2(1 - p);
}

function conditionalEntropy(joint) {
    if (!Array.isArray(joint) || joint.length === 0) {
        throw new ProbabilityError(
            'Joint probability matrix cannot be empty.'
        );
    }

    const columns = joint[0].length;

    if (
        columns === 0 ||
        joint.some(row => !Array.isArray(row) ||
            row.length !== columns)
    ) {
        throw new ProbabilityError(
            'Joint matrix must be rectangular.'
        );
    }

    let total = 0;
    const marginalX = new Array(joint.length).fill(0);
    const marginalY = new Array(columns).fill(0);

    for (let i = 0; i < joint.length; i++) {
        for (let j = 0; j < columns; j++) {
            const value = joint[i][j];

            if (
                !Number.isFinite(value) ||
                value < 0 ||
                value > 1
            ) {
                throw new ProbabilityError(
                    'Invalid joint probability.'
                );
            }

            total += value;
            marginalX[i] += value;
            marginalY[j] += value;
        }
    }

    if (Math.abs(total - 1) > 1e-10) {
        throw new ProbabilityError(
            'Joint probabilities must sum to 1.'
        );
    }

    let jointEntropy = 0;
    let xEntropy = 0;
    let yEntropy = 0;

    const H = p => p > 0 ? -p * Math.log2(p) : 0;

    for (const row of joint) {
        for (const probability of row) {
            jointEntropy += H(probability);
        }
    }

    for (const probability of marginalX) {
        xEntropy += H(probability);
    }

    for (const probability of marginalY) {
        yEntropy += H(probability);
    }

    return {
        jointEntropy,
        xEntropy,
        yEntropy,
        conditionalYGivenX: Math.max(
            0,
            jointEntropy - xEntropy
        ),
        mutualInformation: Math.max(
            0,
            xEntropy + yEntropy - jointEntropy
        )
    };
}

/*
 * Online frequency estimation.
 * The counter maintains counts instead of storing
 * every observation in memory.
 */
class OnlineEstimator {
    constructor(events) {
        if (!Array.isArray(events) || events.length === 0) {
            throw new ProbabilityError(
                'At least one event is required.'
            );
        }

        this.counts = new Map();

        for (const event of events) {
            if (typeof event !== 'string' || !event.trim()) {
                throw new ProbabilityError(
                    'Invalid event name.'
                );
            }

            if (this.counts.has(event)) {
                throw new ProbabilityError(
                    `Duplicate event: ${event}`
                );
            }

            this.counts.set(event, 0);
        }

        this.total = 0;
    }

    observe(event) {
        if (!this.counts.has(event)) {
            throw new ProbabilityError(
                `Unknown event: ${event}`
            );
        }

        this.counts.set(
            event,
            this.counts.get(event) + 1
        );

        this.total++;
    }

    distribution(alpha = 0) {
        if (!Number.isFinite(alpha) || alpha < 0) {
            throw new ProbabilityError(
                'Alpha must be non-negative.'
            );
        }

        const denominator =
            this.total + alpha * this.counts.size;

        if (denominator === 0) {
            throw new ProbabilityError(
                'Cannot estimate an empty sample without smoothing.'
            );
        }

        const probabilities = new Map();

        for (const [event, count] of this.counts) {
            probabilities.set(
                event,
                (count + alpha) / denominator
            );
        }

        return new ProbabilityDistribution(
            'online_estimate',
            probabilities
        );
    }
}

/*
 * Event-driven evaluation.
 * Consumers subscribe to metric updates.
 */
class MetricEngine {
    constructor() {
        this.listeners = new Map();
    }

    on(event, callback) {
        if (typeof callback !== 'function') {
            throw new TypeError('Listener must be a function.');
        }

        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }

        this.listeners.get(event).add(callback);

        return () => this.listeners.get(event)?.delete(callback);
    }

    emit(event, data) {
        const callbacks = this.listeners.get(event);

        if (!callbacks) return;

        for (const callback of callbacks) {
            try {
                callback(data);
            } catch (error) {
                process.stderr.write(
                    `Listener error: ${error.message}\n`
                );
            }
        }
    }

    evaluate(actual, predicted) {
        const result = {
            entropy: entropy(actual),
            crossEntropy: crossEntropy(actual, predicted),
            klDivergence: klDivergence(actual, predicted)
        };

        this.emit('evaluation', result);

        return result;
    }
}

async function evaluateBatch(engine, samples) {
    if (!Array.isArray(samples)) {
        throw new TypeError('Samples must be an array.');
    }

    // Process in bounded batches to avoid creating an
    // unnecessarily large number of pending operations.
    const results = [];

    for (let i = 0; i < samples.length; i += 100) {
        const batch = samples.slice(i, i + 100);

        const batchResults = await Promise.all(
            batch.map(async sample => {
                return engine.evaluate(
                    sample.actual,
                    sample.predicted
                );
            })
        );

        results.push(...batchResults);
    }

    return results;
}

async function main() {
    const actual = new ProbabilityDistribution(
        'actual',
        new Map([
            ['A', 0.5],
            ['B', 0.3],
            ['C', 0.2]
        ])
    );

    const predicted = new ProbabilityDistribution(
        'predicted',
        new Map([
            ['A', 0.4],
            ['B', 0.4],
            ['C', 0.2]
        ])
    );

    const engine = new MetricEngine();

    const unsubscribe = engine.on(
        'evaluation',
        result => {
            console.log('Metric event received:', result);
        }
    );

    console.log('\nDistribution analysis:');

    const result = engine.evaluate(actual, predicted);

    console.log({
        ...result,
        entropyPlusKL:
            result.entropy + result.klDivergence
    });

    console.log('\nBinary entropy:');

    for (const p of [0, 0.1, 0.25, 0.5, 0.75, 1]) {
        console.log(p, binaryEntropy(p));
    }

    console.log('\nJoint distribution:');

    const joint = [
        [0.4, 0.1],
        [0.1, 0.4]
    ];

    console.log(conditionalEntropy(joint));

    console.log('\nOnline estimation:');

    const estimator = new OnlineEstimator(['A', 'B', 'C']);

    for (const event of ['A', 'A', 'B', 'C', 'A', 'B']) {
        estimator.observe(event);
    }

    console.log(estimator.distribution().toJSON());

    console.log('\nSmoothed distribution:');

    const sparse = new ProbabilityDistribution(
        'sparse',
        new Map([
            ['A', 1],
            ['B', 0],
            ['C', 0]
        ])
    );

    console.log(smooth(sparse, 0.1).toJSON());

    console.log('\nAsynchronous batch evaluation:');

    const batch = await evaluateBatch(engine, [
        { actual, predicted },
        { actual, predicted: smooth(predicted, 0.01) }
    ]);

    console.log(`Processed ${batch.length} evaluations.`);

    // Save results using the Node.js filesystem API.
    await fs.writeFile(
        'entropy_results.json',
        JSON.stringify(
            {
                metrics: result,
                jointAnalysis: conditionalEntropy(joint),
                onlineEstimate: estimator.distribution().toJSON()
            },
            null,
            2
        ),
        'utf8'
    );

    unsubscribe();

    // Numerical invariants.
    console.assert(Math.abs(
        crossEntropy(actual, predicted) -
        entropy(actual) -
        klDivergence(actual, predicted)
    ) < 1e-9);

    console.assert(klDivergence(actual, actual) < 1e-10);
    console.assert(Math.abs(binaryEntropy(0.5) - 1) < 1e-10);

    console.log('\nAll numerical checks passed.');
    console.log('Results saved to entropy_results.json.');
}

main().catch(error => {
    console.error('Execution failed:', error.message);
    process.exitCode = 1;
});
