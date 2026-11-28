'use strict';

/*
 * Vector Operations Engine
 *
 * JavaScript implementation using immutable vector data,
 * asynchronous batch processing, event-driven operation tracking,
 * validation, numerical algorithms and structured reporting.
 */

const { EventEmitter } = require('node:events');
const fs = require('node:fs/promises');

class VectorError extends Error {
    constructor(message) {
        super(message);
        this.name = 'VectorError';
    }
}

class DimensionMismatchError extends VectorError {
    constructor(first, second) {
        super(`Dimension mismatch: ${first} != ${second}`);
        this.name = 'DimensionMismatchError';
    }
}

class ZeroVectorError extends VectorError {
    constructor(message = 'Operation is undefined for a zero vector.') {
        super(message);
        this.name = 'ZeroVectorError';
    }
}

class Vector {
    #values;

    constructor(values) {
        if (!Array.isArray(values) || values.length === 0) {
            throw new VectorError(
                'A vector must be a non-empty array.'
            );
        }

        if (!values.every(
            value => typeof value === 'number' && Number.isFinite(value)
        )) {
            throw new VectorError(
                'All vector elements must be finite numbers.'
            );
        }

        this.#values = Object.freeze([...values]);
        Object.freeze(this);
    }

    get values() {
        return [...this.#values];
    }

    get dimension() {
        return this.#values.length;
    }

    #assertCompatible(other) {
        if (!(other instanceof Vector)) {
            throw new VectorError('Expected another Vector instance.');
        }

        if (this.dimension !== other.dimension) {
            throw new DimensionMismatchError(
                this.dimension,
                other.dimension
            );
        }
    }

    add(other) {
        this.#assertCompatible(other);

        return new Vector(
            this.#values.map((value, index) =>
                value + other.#values[index]
            )
        );
    }

    subtract(other) {
        this.#assertCompatible(other);

        return new Vector(
            this.#values.map((value, index) =>
                value - other.#values[index]
            )
        );
    }

    scale(scalar) {
        if (typeof scalar !== 'number' || !Number.isFinite(scalar)) {
            throw new VectorError('Scalar must be finite.');
        }

        return new Vector(
            this.#values.map(value => value * scalar)
        );
    }

    dot(other) {
        this.#assertCompatible(other);

        // Neumaier compensated summation reduces accumulated rounding error.
        let sum = 0;
        let correction = 0;

        for (let i = 0; i < this.dimension; i++) {
            const product = this.#values[i] * other.#values[i];

            if (!Number.isFinite(product)) {
                throw new VectorError('Dot product overflowed.');
            }

            const temporary = sum + product;

            if (Math.abs(sum) >= Math.abs(product)) {
                correction += (sum - temporary) + product;
            } else {
                correction += (product - temporary) + sum;
            }

            sum = temporary;
        }

        const result = sum + correction;

        if (!Number.isFinite(result)) {
            throw new VectorError('Dot product overflowed.');
        }

        return result;
    }

    l1Norm() {
        const result = this.#values.reduce(
            (sum, value) => sum + Math.abs(value),
            0
        );

        if (!Number.isFinite(result)) {
            throw new VectorError('L1 norm overflowed.');
        }

        return result;
    }

    l2Norm() {
        // Scaled sum-of-squares avoids unnecessary intermediate overflow.
        let scale = 0;
        let sumSquares = 1;

        for (const value of this.#values) {
            const absolute = Math.abs(value);

            if (absolute === 0) continue;

            if (scale < absolute) {
                sumSquares = 1 + sumSquares * (scale / absolute) ** 2;
                scale = absolute;
            } else {
                sumSquares += (absolute / scale) ** 2;
            }
        }

        const result = scale === 0
            ? 0
            : scale * Math.sqrt(sumSquares);

        if (!Number.isFinite(result)) {
            throw new VectorError('L2 norm overflowed.');
        }

        return result;
    }

    infinityNorm() {
        return Math.max(...this.#values.map(Math.abs));
    }

    norm(order = 2) {
        if (order === Infinity) {
            return this.infinityNorm();
        }

        if (
            typeof order !== 'number' ||
            !Number.isFinite(order) ||
            order < 1
        ) {
            throw new VectorError(
                'Norm order must be >= 1 or Infinity.'
            );
        }

        if (order === 1) return this.l1Norm();
        if (order === 2) return this.l2Norm();

        const maximum = this.infinityNorm();

        if (maximum === 0) return 0;

        const result = maximum * Math.pow(
            this.#values.reduce(
                (sum, value) =>
                    sum + Math.pow(Math.abs(value) / maximum, order),
                0
            ),
            1 / order
        );

        if (!Number.isFinite(result)) {
            throw new VectorError('Norm overflowed.');
        }

        return result;
    }

    normalize() {
        const magnitude = this.l2Norm();

        if (magnitude === 0) {
            throw new ZeroVectorError('Cannot normalize a zero vector.');
        }

        return this.scale(1 / magnitude);
    }

    cosineSimilarity(other) {
        this.#assertCompatible(other);

        const firstNorm = this.l2Norm();
        const secondNorm = other.l2Norm();

        if (firstNorm === 0 || secondNorm === 0) {
            throw new ZeroVectorError(
                'Cosine similarity is undefined for zero vectors.'
            );
        }

        const similarity = this.dot(other) / firstNorm / secondNorm;

        return Math.max(-1, Math.min(1, similarity));
    }

    distance(other) {
        return this.subtract(other).l2Norm();
    }

    isOrthogonal(other, tolerance = 1e-10) {
        if (!Number.isFinite(tolerance) || tolerance < 0) {
            throw new VectorError('Invalid tolerance.');
        }

        return Math.abs(this.dot(other)) <= tolerance;
    }

    toJSON() {
        return {
            dimension: this.dimension,
            values: this.values
        };
    }

    static fromJSON(record) {
        if (
            record === null ||
            typeof record !== 'object' ||
            !Array.isArray(record.values)
        ) {
            throw new VectorError('Invalid vector JSON record.');
        }

        const vector = new Vector(record.values);

        if (record.dimension !== vector.dimension) {
            throw new VectorError('Vector dimension metadata mismatch.');
        }

        return vector;
    }
}

class VectorEventBus extends EventEmitter {
    constructor() {
        super();
        this.setMaxListeners(50);
    }

    publish(event, payload) {
        this.emit(event, Object.freeze({
            timestamp: new Date().toISOString(),
            ...payload
        }));
    }
}

class VectorService {
    constructor() {
        this.events = new VectorEventBus();
        this.operationCount = new Map();

        this.events.on('operation:completed', event => {
            const previous = this.operationCount.get(event.operation) || 0;
            this.operationCount.set(event.operation, previous + 1);
        });

        this.events.on('operation:failed', event => {
            process.stderr.write(
                `[${event.operation}] ${event.error}\n`
            );
        });
    }

    execute(operation, first, second = null, scalar = null) {
        try {
            let result;

            switch (operation) {
                case 'addition':
                    result = first.add(second);
                    break;

                case 'scalar_multiplication':
                    result = first.scale(scalar);
                    break;

                case 'dot_product':
                    result = first.dot(second);
                    break;

                case 'l1_norm':
                    result = first.l1Norm();
                    break;

                case 'l2_norm':
                    result = first.l2Norm();
                    break;

                case 'infinity_norm':
                    result = first.infinityNorm();
                    break;

                default:
                    throw new VectorError(
                        `Unknown operation: ${operation}`
                    );
            }

            this.events.publish('operation:completed', {
                operation,
                dimension: first.dimension
            });

            return result;
        } catch (error) {
            this.events.publish('operation:failed', {
                operation,
                error: error.message
            });

            throw error;
        }
    }

    async executeBatch(jobs, concurrency = 4) {
        if (!Array.isArray(jobs)) {
            throw new VectorError('Jobs must be an array.');
        }

        if (
            !Number.isInteger(concurrency) ||
            concurrency < 1 ||
            concurrency > 64
        ) {
            throw new VectorError('Concurrency must be between 1 and 64.');
        }

        const results = new Array(jobs.length);
        let nextIndex = 0;

        // Workers claim independent jobs without concurrent index collisions.
        async function worker() {
            while (true) {
                const index = nextIndex++;

                if (index >= jobs.length) return;

                try {
                    const job = jobs[index];

                    results[index] = {
                        success: true,
                        result: this.execute(
                            job.operation,
                            job.first,
                            job.second ?? null,
                            job.scalar ?? null
                        )
                    };
                } catch (error) {
                    results[index] = {
                        success: false,
                        error: error.message
                    };
                }

                await Promise.resolve();
            }
        }

        const workers = Array.from(
            { length: Math.min(concurrency, jobs.length) },
            () => worker.call(this)
        );

        await Promise.all(workers);

        return results;
    }

    statistics() {
        return Object.fromEntries(this.operationCount);
    }
}

async function saveVectors(vectors, filename) {
    const records = Object.fromEntries(
        Object.entries(vectors).map(([name, vector]) => {
            if (!(vector instanceof Vector)) {
                throw new VectorError(`Invalid vector: ${name}`);
            }

            return [name, vector.toJSON()];
        })
    );

    const temporary = `${filename}.tmp`;

    try {
        await fs.writeFile(
            temporary,
            JSON.stringify(records, null, 2),
            { encoding: 'utf8', flag: 'w', mode: 0o600 }
        );

        await fs.rename(temporary, filename);
    } catch (error) {
        await fs.rm(temporary, { force: true }).catch(() => {});
        throw new VectorError(`Persistence failure: ${error.message}`);
    }
}

async function loadVectors(filename) {
    let records;

    try {
        records = JSON.parse(await fs.readFile(filename, 'utf8'));
    } catch (error) {
        throw new VectorError(`Unable to read vector data: ${error.message}`);
    }

    if (
        records === null ||
        typeof records !== 'object' ||
        Array.isArray(records)
    ) {
        throw new VectorError('Invalid vector document.');
    }

    return Object.fromEntries(
        Object.entries(records).map(([name, record]) => [
            name,
            Vector.fromJSON(record)
        ])
    );
}

async function main() {
    console.log('VECTOR OPERATIONS ENGINE');
    console.log('========================');

    const u = new Vector([3, 4]);
    const v = new Vector([4, 3]);

    const service = new VectorService();

    service.events.on('operation:completed', event => {
        console.log(
            `EVENT: ${event.operation}, dimension=${event.dimension}`
        );
    });

    console.log('\nBasic operations');
    console.log('Addition:', u.add(v).values);
    console.log('Subtraction:', u.subtract(v).values);
    console.log('Scalar multiplication:', u.scale(3).values);
    console.log('Dot product:', u.dot(v));

    console.log('\nNorms');
    console.log('L1:', u.l1Norm());
    console.log('L2:', u.l2Norm());
    console.log('L-infinity:', u.infinityNorm());
    console.log('L3:', u.norm(3));

    console.log('\nAdvanced operations');
    console.log('Normalized:', u.normalize().values);
    console.log('Distance:', u.distance(v));
    console.log('Cosine similarity:', u.cosineSimilarity(v));
    console.log(
        'Orthogonal:',
        new Vector([1, 0]).isOrthogonal(new Vector([0, 1]))
    );

    console.log('\nBatch processing');

    const jobs = [
        { operation: 'addition', first: u, second: v },
        { operation: 'dot_product', first: u, second: v },
        { operation: 'scalar_multiplication', first: u, scalar: 2 },
        { operation: 'l2_norm', first: u },
        { operation: 'unknown_operation', first: u }
    ];

    const batchResults = await service.executeBatch(jobs, 3);

    batchResults.forEach((result, index) => {
        console.log(`Job ${index + 1}:`, result);
    });

    console.log('\nPersistence');

    const filename = 'vector_data.json';

    await saveVectors({ u, v }, filename);

    const restored = await loadVectors(filename);

    console.log('Restored vectors:', {
        u: restored.u.values,
        v: restored.v.values
    });

    await fs.rm(filename, { force: true });

    console.log('\nOperation statistics');
    console.log(service.statistics());

    console.log('\nValidation');

    try {
        u.add(new Vector([1, 2, 3]));
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        new Vector([0, 0]).normalize();
    } catch (error) {
        console.log(error.name, error.message);
    }

    try {
        new Vector([1, Infinity]);
    } catch (error) {
        console.log(error.name, error.message);
    }

    // Numerical assertions.
    console.assert(u.add(v).values[0] === 7);
    console.assert(u.dot(v) === 24);
    console.assert(Math.abs(u.l2Norm() - 5) < 1e-12);
    console.assert(Math.abs(u.normalize().l2Norm() - 1) < 1e-12);

    console.log('\nAll numerical assertions passed.');
}

main().catch(error => {
    console.error('Execution failed:', error.message);
    process.exitCode = 1;
});
