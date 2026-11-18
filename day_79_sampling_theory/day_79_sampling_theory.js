'use strict';

/**
 * Sampling Theory Engine
 *
 * Node.js 18+
 * No external dependencies.
 *
 * Features:
 * - Random sampling
 * - Stratified allocation
 * - Systematic sampling
 * - Sample-size planning
 * - Representation diagnostics
 * - Asynchronous sampling workflow
 * - Event-driven audit trail
 */

const { EventEmitter } = require('node:events');
const { randomInt } = require('node:crypto');

class SamplingError extends Error {
    constructor(message, code = 'SAMPLING_ERROR') {
        super(message);
        this.name = 'SamplingError';
        this.code = code;
    }
}

class Population {
    #records;
    #index;

    constructor(records) {
        if (!Array.isArray(records) || records.length === 0) {
            throw new SamplingError(
                'Population must be a non-empty array.',
                'EMPTY_POPULATION'
            );
        }

        this.#records = records.map(record =>
            Object.freeze({ ...record })
        );

        this.#index = new Map();

        for (const record of this.#records) {
            if (!Number.isInteger(record.id) || record.id <= 0) {
                throw new SamplingError('Invalid record ID.');
            }

            if (this.#index.has(record.id)) {
                throw new SamplingError('Duplicate record ID.');
            }

            if (
                typeof record.stratum !== 'string' ||
                record.stratum.trim() === ''
            ) {
                throw new SamplingError('Invalid stratum.');
            }

            if (
                typeof record.value !== 'number' ||
                !Number.isFinite(record.value)
            ) {
                throw new SamplingError('Invalid numeric outcome.');
            }

            this.#index.set(record.id, record);
        }
    }

    get size() {
        return this.#records.length;
    }

    get records() {
        return [...this.#records];
    }

    getById(id) {
        return this.#index.get(id);
    }
}

class RandomSource {
    constructor(seed = 2026) {
        if (!Number.isSafeInteger(seed)) {
            throw new SamplingError('Seed must be a safe integer.');
        }

        this.state = seed >>> 0;
    }

    next() {
        // Mulberry32 deterministic pseudorandom generator.
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

    integer(maxExclusive) {
        if (!Number.isInteger(maxExclusive) || maxExclusive <= 0) {
            throw new SamplingError('Invalid random integer limit.');
        }

        return Math.floor(this.next() * maxExclusive);
    }

    shuffle(items) {
        const result = [...items];

        for (let i = result.length - 1; i > 0; i--) {
            const j = this.integer(i + 1);
            [result[i], result[j]] = [result[j], result[i]];
        }

        return result;
    }
}

class SampleResult {
    constructor(method, records, populationSize, seed) {
        this.method = method;
        this.records = Object.freeze([...records]);
        this.populationSize = populationSize;
        this.sampleSize = records.length;
        this.seed = seed;

        Object.freeze(this);
    }
}

class SamplingPlanner {
    static validateSize(populationSize, sampleSize) {
        if (
            !Number.isInteger(sampleSize) ||
            sampleSize < 1 ||
            sampleSize > populationSize
        ) {
            throw new SamplingError(
                'Sample size must be an integer between 1 and N.',
                'INVALID_SAMPLE_SIZE'
            );
        }
    }

    static random(population, n, seed = 42) {
        SamplingPlanner.validateSize(population.size, n);

        const rng = new RandomSource(seed);

        const selected = rng
            .shuffle(population.records)
            .slice(0, n);

        return new SampleResult(
            'SIMPLE_RANDOM',
            selected,
            population.size,
            seed
        );
    }

    static allocateProportionally(groups, n) {
        const entries = [...groups.entries()]
            .sort(([a], [b]) => a.localeCompare(b));

        const H = entries.length;
        const N = entries.reduce(
            (total, [, members]) => total + members.length,
            0
        );

        if (n < H) {
            throw new SamplingError(
                'Sample size cannot represent every stratum.'
            );
        }

        const allocations = entries.map(([name, members]) => {
            const raw = n * members.length / N;

            return {
                name,
                capacity: members.length,
                raw,
                count: Math.floor(raw),
                remainder: raw - Math.floor(raw)
            };
        });

        for (const item of allocations) {
            if (item.count === 0) {
                item.count = 1;
            }
        }

        while (
            allocations.reduce((sum, x) => sum + x.count, 0) > n
        ) {
            const candidates = allocations
                .filter(x => x.count > 1)
                .sort((a, b) => a.remainder - b.remainder);

            if (candidates.length === 0) {
                throw new SamplingError('Allocation is infeasible.');
            }

            candidates[0].count--;
        }

        while (
            allocations.reduce((sum, x) => sum + x.count, 0) < n
        ) {
            const candidates = allocations
                .filter(x => x.count < x.capacity)
                .sort((a, b) => {
                    if (b.remainder !== a.remainder) {
                        return b.remainder - a.remainder;
                    }
                    return b.capacity - a.capacity;
                });

            if (candidates.length === 0) {
                throw new SamplingError('Allocation capacity exceeded.');
            }

            candidates[0].count++;
            candidates[0].remainder = -1;
        }

        return allocations;
    }

    static stratified(population, n, seed = 42) {
        SamplingPlanner.validateSize(population.size, n);

        const groups = new Map();

        for (const record of population.records) {
            if (!groups.has(record.stratum)) {
                groups.set(record.stratum, []);
            }

            groups.get(record.stratum).push(record);
        }

        const allocation = SamplingPlanner.allocateProportionally(
            groups,
            n
        );

        const rng = new RandomSource(seed);
        const selected = [];

        for (const item of allocation) {
            const members = groups.get(item.name);

            selected.push(
                ...rng.shuffle(members).slice(0, item.count)
            );
        }

        return new SampleResult(
            'STRATIFIED',
            rng.shuffle(selected),
            population.size,
            seed
        );
    }

    static systematic(population, n, seed = 42) {
        SamplingPlanner.validateSize(population.size, n);

        const rng = new RandomSource(seed);
        const records = population.records;
        const interval = population.size / n;
        const start = rng.next() * interval;

        const selected = [];

        for (let i = 0; i < n; i++) {
            const index = Math.min(
                records.length - 1,
                Math.floor(start + i * interval)
            );

            selected.push(records[index]);
        }

        return new SampleResult(
            'SYSTEMATIC',
            selected,
            population.size,
            seed
        );
    }
}

class StatisticalAnalysis {
    static mean(values) {
        if (values.length === 0) {
            throw new SamplingError('Empty sample.');
        }

        return values.reduce((sum, x) => sum + x, 0) / values.length;
    }

    static variance(values) {
        if (values.length < 2) {
            throw new SamplingError(
                'At least two observations are required.'
            );
        }

        const average = this.mean(values);

        return values.reduce(
            (sum, x) => sum + (x - average) ** 2,
            0
        ) / (values.length - 1);
    }

    static standardError(values, populationSize = null) {
        const n = values.length;
        let result = Math.sqrt(this.variance(values) / n);

        if (populationSize !== null) {
            if (
                !Number.isInteger(populationSize) ||
                populationSize < n
            ) {
                throw new SamplingError('Invalid population size.');
            }

            result *= Math.sqrt(
                (populationSize - n) / (populationSize - 1)
            );
        }

        return result;
    }

    static confidenceInterval(
        values,
        populationSize,
        z = 1.96
    ) {
        if (z <= 0 || !Number.isFinite(z)) {
            throw new SamplingError('Invalid critical value.');
        }

        const average = this.mean(values);
        const se = this.standardError(values, populationSize);
        const margin = z * se;

        return Object.freeze({
            mean: average,
            standardError: se,
            margin,
            lower: average - margin,
            upper: average + margin
        });
    }

    static representation(population, sample) {
        const calculate = records => {
            const counts = new Map();

            for (const record of records) {
                counts.set(
                    record.stratum,
                    (counts.get(record.stratum) || 0) + 1
                );
            }

            const result = new Map();

            for (const [name, count] of counts) {
                result.set(name, count / records.length);
            }

            return result;
        };

        const actual = calculate(population.records);
        const observed = calculate(sample.records);

        const all = new Set([
            ...actual.keys(),
            ...observed.keys()
        ]);

        return Object.fromEntries(
            [...all].sort().map(name => [
                name,
                (observed.get(name) || 0) -
                (actual.get(name) || 0)
            ])
        );
    }
}

class SampleSizeCalculator {
    static proportion({
        populationSize = null,
        z = 1.96,
        margin = 0.05,
        proportion = 0.5
    } = {}) {
        if (
            z <= 0 ||
            margin <= 0 ||
            margin >= 1 ||
            proportion <= 0 ||
            proportion >= 1
        ) {
            throw new SamplingError('Invalid sample-size parameters.');
        }

        const n0 = (
            z * z * proportion * (1 - proportion)
        ) / (margin * margin);

        if (populationSize === null) {
            return Math.ceil(n0);
        }

        if (!Number.isInteger(populationSize) || populationSize <= 0) {
            throw new SamplingError('Invalid population size.');
        }

        if (populationSize === 1) {
            return 1;
        }

        return Math.min(
            populationSize,
            Math.ceil(
                n0 / (1 + (n0 - 1) / populationSize)
            )
        );
    }

    static recruitmentTarget(required, responseRate) {
        if (
            !Number.isInteger(required) ||
            required <= 0 ||
            responseRate <= 0 ||
            responseRate > 1
        ) {
            throw new SamplingError('Invalid recruitment parameters.');
        }

        return Math.ceil(required / responseRate);
    }
}

class SamplingWorkflow extends EventEmitter {
    #population;
    #completed = new Map();

    constructor(population) {
        super();
        this.#population = population;
    }

    async execute(method, sampleSize, seed = 42) {
        if (this.#completed.has(method)) {
            throw new SamplingError(
                `Workflow ${method} has already completed.`
            );
        }

        this.emit('sampling:started', {
            method,
            sampleSize,
            populationSize: this.#population.size
        });

        try {
            // Yield control to the event loop for workflow integration.
            await new Promise(resolve => setImmediate(resolve));

            let result;

            switch (method) {
                case 'random':
                    result = SamplingPlanner.random(
                        this.#population,
                        sampleSize,
                        seed
                    );
                    break;

                case 'stratified':
                    result = SamplingPlanner.stratified(
                        this.#population,
                        sampleSize,
                        seed
                    );
                    break;

                case 'systematic':
                    result = SamplingPlanner.systematic(
                        this.#population,
                        sampleSize,
                        seed
                    );
                    break;

                default:
                    throw new SamplingError('Unknown sampling method.');
            }

            this.#completed.set(method, result);

            this.emit('sampling:completed', {
                method,
                sampleSize: result.sampleSize
            });

            return result;
        } catch (error) {
            this.emit('sampling:failed', {
                method,
                error: error.message
            });

            throw error;
        }
    }
}

function buildPopulation(size = 1000) {
    const rng = new RandomSource(2026);

    const departments = [
        'Engineering',
        'Finance',
        'Operations',
        'Research'
    ];

    const weights = [40, 20, 25, 15];

    return Array.from({ length: size }, (_, index) => {
        const selection = rng.next() * 100;
        let cumulative = 0;
        let stratum = departments[departments.length - 1];

        for (let i = 0; i < departments.length; i++) {
            cumulative += weights[i];

            if (selection < cumulative) {
                stratum = departments[i];
                break;
            }
        }

        return {
            id: index + 1,
            stratum,
            value: Number(
                (
                    35 +
                    rng.next() * 20 +
                    rng.next() * 15
                ).toFixed(2)
            )
        };
    });
}

async function main() {
    const population = new Population(buildPopulation());

    const workflow = new SamplingWorkflow(population);

    workflow.on('sampling:started', event => {
        console.log('\nStarted:', event);
    });

    workflow.on('sampling:completed', event => {
        console.log('Completed:', event);
    });

    workflow.on('sampling:failed', event => {
        console.error('Failed:', event);
    });

    const required = SampleSizeCalculator.proportion({
        populationSize: population.size,
        margin: 0.05,
        proportion: 0.5
    });

    console.log('\nPopulation:', population.size);
    console.log('Required sample:', required);

    console.log(
        'Recruitment target:',
        SampleSizeCalculator.recruitmentTarget(required, 0.85)
    );

    const results = await Promise.all([
        workflow.execute('random', 100, 17),
        workflow.execute('stratified', 100, 17),
        workflow.execute('systematic', 100, 17)
    ]);

    for (const result of results) {
        const values = result.records.map(x => x.value);

        console.log(`\nMethod: ${result.method}`);

        console.log(
            'Estimate:',
            StatisticalAnalysis.confidenceInterval(
                values,
                population.size
            )
        );

        console.log(
            'Representation differences:',
            StatisticalAnalysis.representation(
                population,
                result
            )
        );
    }

    // Cryptographically secure selection for applications requiring
    // unpredictable selection. This is separate from seeded simulation.
    const secureIndex = randomInt(population.size);

    console.log('\nSecure random population index:', secureIndex);

    try {
        SamplingPlanner.random(population, population.size + 1);
    } catch (error) {
        console.log('Validation correctly rejected invalid sample:', error.message);
    }
}

main().catch(error => {
    console.error('Application failure:', error.message);
    process.exitCode = 1;
});
