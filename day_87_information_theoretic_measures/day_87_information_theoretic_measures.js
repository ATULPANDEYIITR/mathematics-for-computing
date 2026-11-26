'use strict';

/*
 * Information-Theoretic Measures
 *
 * Mutual Information, Conditional Entropy, Information Gain.
 *
 * Runtime: Node.js 18+
 * Dependencies: None.
 *
 * Includes:
 * - Shannon entropy
 * - Joint entropy
 * - Conditional entropy
 * - Mutual information
 * - Conditional mutual information
 * - Information gain
 * - Feature selection
 * - Event-driven analysis
 * - Asynchronous dataset processing
 * - Mathematical validation
 */

const fs = require('node:fs/promises');
const EventEmitter = require('node:events');

const EPSILON = 1e-12;

class InformationTheoryError extends Error {
    constructor(message) {
        super(message);
        this.name = 'InformationTheoryError';
    }
}

class DatasetValidationError extends InformationTheoryError {
    constructor(message) {
        super(message);
        this.name = 'DatasetValidationError';
    }
}

class DistributionValidationError extends InformationTheoryError {
    constructor(message) {
        super(message);
        this.name = 'DistributionValidationError';
    }
}

function validateBase(base) {
    if (
        typeof base !== 'number' ||
        !Number.isFinite(base) ||
        base <= 0 ||
        Math.abs(base - 1) < EPSILON
    ) {
        throw new RangeError(
            'Logarithm base must be positive and different from 1.'
        );
    }
}

function validateValues(values, name = 'Values') {
    if (!Array.isArray(values) || values.length === 0) {
        throw new DatasetValidationError(
            `${name} must be a non-empty array.`
        );
    }

    for (const value of values) {
        if (
            value === undefined ||
            value === null ||
            typeof value === 'number' && !Number.isFinite(value)
        ) {
            throw new DatasetValidationError(
                `${name} contains an invalid observation.`
            );
        }

        if (
            !['string', 'number', 'boolean', 'bigint'].includes(typeof value)
        ) {
            throw new DatasetValidationError(
                `${name} must contain primitive categorical values.`
            );
        }
    }
}

function validateColumns(first, second) {
    validateValues(first, 'First column');
    validateValues(second, 'Second column');

    if (first.length !== second.length) {
        throw new DatasetValidationError(
            'Columns must have identical lengths.'
        );
    }
}

function validateTriple(x, y, z) {
    validateColumns(x, y);
    validateColumns(x, z);
    validateColumns(y, z);
}

function distribution(values) {
    validateValues(values);

    const counts = new Map();

    for (const value of values) {
        counts.set(value, (counts.get(value) || 0) + 1);
    }

    const total = values.length;

    return new Map(
        [...counts.entries()].map(
            ([value, count]) => [value, count / total]
        )
    );
}

function entropy(values, base = 2) {
    validateBase(base);

    const probabilities = distribution(values);

    let result = 0;

    for (const probability of probabilities.values()) {
        if (probability > 0) {
            result -= probability *
                Math.log(probability) / Math.log(base);
        }
    }

    return result;
}

function jointEntropy(x, y, base = 2) {
    validateBase(base);
    validateColumns(x, y);

    const counts = new Map();

    for (let i = 0; i < x.length; i++) {
        const key = JSON.stringify([x[i], y[i]]);
        counts.set(key, (counts.get(key) || 0) + 1);
    }

    let result = 0;

    for (const count of counts.values()) {
        const probability = count / x.length;

        result -= probability *
            Math.log(probability) / Math.log(base);
    }

    return result;
}

function conditionalEntropy(y, x, base = 2) {
    validateBase(base);
    validateColumns(x, y);

    const groups = new Map();

    for (let i = 0; i < x.length; i++) {
        if (!groups.has(x[i])) {
            groups.set(x[i], []);
        }

        groups.get(x[i]).push(y[i]);
    }

    let result = 0;

    for (const group of groups.values()) {
        const weight = group.length / x.length;

        result += weight * entropy(group, base);
    }

    return result;
}

function mutualInformation(x, y, base = 2) {
    validateBase(base);
    validateColumns(x, y);

    return Math.max(
        0,
        entropy(y, base) - conditionalEntropy(y, x, base)
    );
}

function informationGain(target, feature, base = 2) {
    return mutualInformation(feature, target, base);
}

function conditionalMutualInformation(x, y, z, base = 2) {
    validateBase(base);
    validateTriple(x, y, z);

    const yGivenZ = conditionalEntropy(y, z, base);

    const combinedXZ = x.map(
        (value, index) => `${typeof value}:${String(value)}|${typeof z[index]}:${String(z[index])}`
    );

    const combinedY = y.map(
        (value, index) => `${typeof value}:${String(value)}|${typeof z[index]}:${String(z[index])}`
    );

    return Math.max(
        0,
        yGivenZ - conditionalEntropy(combinedY, combinedXZ, base)
    );
}

function normalizedMutualInformation(x, y) {
    validateColumns(x, y);

    const hx = entropy(x);
    const hy = entropy(y);
    const denominator = hx + hy;

    if (denominator <= EPSILON) {
        return 1;
    }

    return 2 * mutualInformation(x, y) / denominator;
}

function validateProbabilityMap(probabilities) {
    if (
        !(probabilities instanceof Map) ||
        probabilities.size === 0
    ) {
        throw new DistributionValidationError(
            'Probability map must be a non-empty Map.'
        );
    }

    let total = 0;

    for (const [key, probability] of probabilities) {
        if (
            key === undefined ||
            typeof probability !== 'number' ||
            !Number.isFinite(probability) ||
            probability < 0
        ) {
            throw new DistributionValidationError(
                'Invalid probability entry.'
            );
        }

        total += probability;
    }

    if (Math.abs(total - 1) > EPSILON) {
        throw new DistributionValidationError(
            `Probabilities must sum to 1. Received ${total}.`
        );
    }
}

class InformationEngine {
    constructor(features, target) {
        if (
            !features ||
            typeof features !== 'object' ||
            Array.isArray(features)
        ) {
            throw new DatasetValidationError(
                'Features must be an object.'
            );
        }

        validateValues(target, 'Target');

        this.target = Object.freeze([...target]);
        this.features = new Map();

        for (const [name, values] of Object.entries(features)) {
            if (!name.trim()) {
                throw new DatasetValidationError(
                    'Feature names cannot be empty.'
                );
            }

            validateColumns(values, target);

            this.features.set(
                name,
                Object.freeze([...values])
            );
        }

        if (this.features.size === 0) {
            throw new DatasetValidationError(
                'At least one feature is required.'
            );
        }
    }

    analyze(name) {
        if (!this.features.has(name)) {
            throw new RangeError(`Unknown feature: ${name}`);
        }

        const feature = this.features.get(name);

        const targetEntropy = entropy(this.target);
        const remainingEntropy = conditionalEntropy(
            this.target,
            feature
        );

        const gain = Math.max(
            0,
            targetEntropy - remainingEntropy
        );

        return Object.freeze({
            feature: name,
            targetEntropy,
            conditionalEntropy: remainingEntropy,
            mutualInformation: mutualInformation(
                feature,
                this.target
            ),
            informationGain: gain,
            normalizedMutualInformation: normalizedMutualInformation(
                feature,
                this.target
            )
        });
    }

    rankFeatures() {
        return [...this.features.keys()]
            .map(name => this.analyze(name))
            .sort(
                (a, b) =>
                    b.informationGain - a.informationGain ||
                    a.feature.localeCompare(b.feature)
            );
    }

    selectFeatures(minimumGain = 0) {
        if (
            typeof minimumGain !== 'number' ||
            !Number.isFinite(minimumGain) ||
            minimumGain < 0
        ) {
            throw new RangeError(
                'Minimum gain must be a non-negative finite number.'
            );
        }

        return this.rankFeatures()
            .filter(result => result.informationGain >= minimumGain)
            .map(result => result.feature);
    }
}

class AnalysisPipeline extends EventEmitter {
    constructor(engine) {
        super();

        if (!(engine instanceof InformationEngine)) {
            throw new TypeError(
                'Pipeline requires an InformationEngine.'
            );
        }

        this.engine = engine;
        this.running = false;
        this.lastResult = null;
    }

    async execute() {
        if (this.running) {
            throw new InformationTheoryError(
                'Analysis is already running.'
            );
        }

        this.running = true;

        this.emit('started', {
            observations: this.engine.target.length
        });

        try {
            // Yield to the event loop so listeners and other
            // application tasks can execute.
            await new Promise(resolve => setImmediate(resolve));

            const results = this.engine.rankFeatures();

            this.lastResult = Object.freeze(results);

            this.emit('completed', {
                count: results.length,
                results
            });

            return results;
        } catch (error) {
            this.emit('failed', error);
            throw error;
        } finally {
            this.running = false;
        }
    }
}

async function exportResults(results, filename) {
    if (!Array.isArray(results)) {
        throw new TypeError('Results must be an array.');
    }

    const safeFilename = String(filename);

    if (
        safeFilename.length === 0 ||
        safeFilename.includes('\0')
    ) {
        throw new TypeError('Invalid output filename.');
    }

    const serialized = JSON.stringify(
        {
            generatedAt: new Date().toISOString(),
            measure: 'information_gain',
            features: results
        },
        null,
        2
    );

    // Exclusive creation prevents accidental overwriting.
    const handle = await fs.open(
        safeFilename,
        'wx',
        0o600
    );

    try {
        await handle.writeFile(serialized, 'utf8');
    } finally {
        await handle.close();
    }
}

function runTests() {
    const fairCoin = ['H', 'T', 'H', 'T'];

    console.assert(
        Math.abs(entropy(fairCoin) - 1) < EPSILON
    );

    console.assert(
        entropy(['A', 'A', 'A']) === 0
    );

    const x = [0, 0, 1, 1];
    const y = [0, 0, 1, 1];

    console.assert(
        Math.abs(mutualInformation(x, y) - 1) < EPSILON
    );

    console.assert(
        Math.abs(conditionalEntropy(y, x)) < EPSILON
    );

    console.assert(
        Math.abs(jointEntropy(x, y) - 1) < EPSILON
    );

    const independentX = [0, 0, 1, 1];
    const independentY = [0, 1, 0, 1];

    console.assert(
        Math.abs(mutualInformation(
            independentX,
            independentY
        )) < EPSILON
    );

    console.assert(
        Math.abs(normalizedMutualInformation(x, y) - 1) <
        EPSILON
    );

    validateProbabilityMap(
        new Map([
            ['A', 0.5],
            ['B', 0.5]
        ])
    );

    console.log('Mathematical validation tests passed.');
}

async function main() {
    runTests();

    const target = [
        'No', 'No', 'Yes', 'Yes',
        'Yes', 'No', 'Yes', 'No',
        'Yes', 'Yes', 'Yes', 'Yes',
        'Yes', 'No'
    ];

    const features = {
        Outlook: [
            'Sunny', 'Sunny', 'Overcast', 'Rain',
            'Rain', 'Rain', 'Overcast', 'Sunny',
            'Sunny', 'Rain', 'Sunny', 'Overcast',
            'Overcast', 'Rain'
        ],

        Temperature: [
            'Hot', 'Hot', 'Hot', 'Mild',
            'Cool', 'Cool', 'Cool', 'Mild',
            'Cool', 'Mild', 'Mild', 'Mild',
            'Hot', 'Mild'
        ],

        Humidity: [
            'High', 'High', 'High', 'High',
            'Normal', 'Normal', 'Normal', 'High',
            'Normal', 'Normal', 'Normal', 'High',
            'Normal', 'High'
        ],

        Wind: [
            'Weak', 'Strong', 'Weak', 'Weak',
            'Weak', 'Strong', 'Strong', 'Weak',
            'Weak', 'Weak', 'Strong', 'Strong',
            'Weak', 'Strong'
        ]
    };

    const engine = new InformationEngine(features, target);
    const pipeline = new AnalysisPipeline(engine);

    pipeline.on('started', event => {
        console.log(
            `Processing ${event.observations} observations.`
        );
    });

    pipeline.on('completed', event => {
        console.log(
            `Completed analysis of ${event.count} features.`
        );
    });

    pipeline.on('failed', error => {
        console.error('Pipeline failure:', error.message);
    });

    const results = await pipeline.execute();

    console.log('\nFeature ranking');

    console.table(
        results.map(result => ({
            Feature: result.feature,
            'H(Y)': result.targetEntropy.toFixed(5),
            'H(Y|X)': result.conditionalEntropy.toFixed(5),
            'MI': result.mutualInformation.toFixed(5),
            'IG': result.informationGain.toFixed(5),
            'NMI': result.normalizedMutualInformation.toFixed(5)
        }))
    );

    console.log(
        '\nBest feature:',
        results[0]?.feature
    );

    console.log(
        'Selected features:',
        engine.selectFeatures(0.05)
    );

    const output = 'information_analysis.json';

    try {
        await exportResults(results, output);
        console.log(`Results exported to ${output}.`);
    } catch (error) {
        console.error(
            `Export failed: ${error.message}`
        );
    }

    const cmi = conditionalMutualInformation(
        [0, 0, 1, 1],
        [0, 1, 0, 1],
        [0, 0, 1, 1]
    );

    console.log(
        '\nConditional mutual information:',
        cmi.toFixed(5)
    );
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
