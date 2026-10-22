'use strict';

/*
 * Euclidean Algorithm Case Study
 *
 * Focus:
 * - GCD through remainder reduction
 * - Extended Euclidean algorithm
 * - Bézout identity
 * - Modular inverses
 * - Linear Diophantine equations
 * - Event-driven policy evaluation of arithmetic operations
 *
 * Node.js 18+ is recommended because BigInt is used for exact integer
 * arithmetic beyond JavaScript's safe Number range.
 */

class ArithmeticError extends Error {}

class ExtendedGCDResult {
    constructor(a, b, gcd, x, y) {
        this.a = a;
        this.b = b;
        this.gcd = gcd;
        this.x = x;
        this.y = y;
    }

    bezoutValue() {
        return this.a * this.x + this.b * this.y;
    }

    isValid() {
        return this.bezoutValue() === this.gcd;
    }
}

class EuclideanAlgorithm {
    static validateInteger(value, name) {
        if (typeof value !== 'bigint') {
            throw new TypeError(`${name} must be a BigInt`);
        }
    }

    static abs(value) {
        return value < 0n ? -value : value;
    }

    static gcd(a, b) {
        this.validateInteger(a, 'a');
        this.validateInteger(b, 'b');

        let x = this.abs(a);
        let y = this.abs(b);

        while (y !== 0n) {
            [x, y] = [y, x % y];
        }

        return x;
    }

    static extendedGCD(a, b) {
        this.validateInteger(a, 'a');
        this.validateInteger(b, 'b');

        const originalA = a;
        const originalB = b;

        let oldR = this.abs(a);
        let r = this.abs(b);
        let oldS = 1n;
        let s = 0n;
        let oldT = 0n;
        let t = 1n;

        while (r !== 0n) {
            const quotient = oldR / r;

            [oldR, r] = [r, oldR - quotient * r];
            [oldS, s] = [s, oldS - quotient * s];
            [oldT, t] = [t, oldT - quotient * t];
        }

        const x = a >= 0n ? oldS : -oldS;
        const y = b >= 0n ? oldT : -oldT;

        const result = new ExtendedGCDResult(
            originalA,
            originalB,
            oldR,
            x,
            y
        );

        if (!result.isValid()) {
            throw new ArithmeticError('Bézout invariant violated');
        }

        return result;
    }

    static mod(value, modulus) {
        const result = value % modulus;
        return result < 0n ? result + modulus : result;
    }

    static modularInverse(value, modulus) {
        this.validateInteger(value, 'value');
        this.validateInteger(modulus, 'modulus');

        if (modulus <= 1n) {
            throw new RangeError('modulus must be greater than 1');
        }

        const result = this.extendedGCD(value, modulus);

        if (result.gcd !== 1n) {
            throw new ArithmeticError(
                `No modular inverse: gcd(${value}, ${modulus}) = ${result.gcd}`
            );
        }

        return this.mod(result.x, modulus);
    }

    static solveLinearDiophantine(a, b, c) {
        this.validateInteger(a, 'a');
        this.validateInteger(b, 'b');
        this.validateInteger(c, 'c');

        if (a === 0n && b === 0n) {
            if (c === 0n) {
                return { x: 0n, y: 0n, gcd: 0n };
            }

            throw new ArithmeticError('No solution exists');
        }

        const result = this.extendedGCD(a, b);

        if (c % result.gcd !== 0n) {
            throw new ArithmeticError(
                `gcd(${a}, ${b}) does not divide ${c}`
            );
        }

        const factor = c / result.gcd;

        return {
            x: result.x * factor,
            y: result.y * factor,
            gcd: result.gcd
        };
    }
}

class ArithmeticEventBus {
    constructor() {
        this.handlers = new Map();
    }

    on(eventName, handler) {
        if (!this.handlers.has(eventName)) {
            this.handlers.set(eventName, []);
        }

        this.handlers.get(eventName).push(handler);
    }

    emit(eventName, payload) {
        const handlers = this.handlers.get(eventName) || [];

        for (const handler of handlers) {
            handler(payload);
        }
    }
}

class ArithmeticService {
    constructor(eventBus) {
        this.eventBus = eventBus;
    }

    calculateGCD(a, b) {
        this.eventBus.emit('operation.started', {
            operation: 'gcd',
            a,
            b
        });

        try {
            const result = EuclideanAlgorithm.gcd(a, b);

            this.eventBus.emit('operation.completed', {
                operation: 'gcd',
                result
            });

            return result;
        } catch (error) {
            this.eventBus.emit('operation.failed', {
                operation: 'gcd',
                error: error.message
            });
            throw error;
        }
    }

    calculateInverse(value, modulus) {
        this.eventBus.emit('operation.started', {
            operation: 'modular-inverse',
            value,
            modulus
        });

        try {
            const result = EuclideanAlgorithm.modularInverse(
                value,
                modulus
            );

            this.eventBus.emit('operation.completed', {
                operation: 'modular-inverse',
                result
            });

            return result;
        } catch (error) {
            this.eventBus.emit('operation.failed', {
                operation: 'modular-inverse',
                error: error.message
            });
            throw error;
        }
    }
}

function formatResult(value) {
    return typeof value === 'bigint' ? value.toString() : String(value);
}

function runExamples() {
    const eventBus = new ArithmeticEventBus();

    eventBus.on('operation.started', event => {
        console.log(
            `[START] ${event.operation}:`,
            Object.fromEntries(
                Object.entries(event)
                    .filter(([key]) => key !== 'operation')
                    .map(([key, value]) => [key, formatResult(value)])
            )
        );
    });

    eventBus.on('operation.completed', event => {
        console.log(
            `[DONE] ${event.operation}: ${formatResult(event.result)}`
        );
    });

    eventBus.on('operation.failed', event => {
        console.log(
            `[FAIL] ${event.operation}: ${event.error}`
        );
    });

    const service = new ArithmeticService(eventBus);

    console.log('GCD');
    console.log('---');

    const gcdValue = service.calculateGCD(1071n, 462n);
    console.log(`gcd(1071, 462) = ${gcdValue}`);

    console.log('\nExtended Euclidean algorithm');
    console.log('----------------------------');

    const extended = EuclideanAlgorithm.extendedGCD(240n, 46n);

    console.log(`gcd = ${extended.gcd}`);
    console.log(`x = ${extended.x}`);
    console.log(`y = ${extended.y}`);
    console.log(
        `240(${extended.x}) + 46(${extended.y}) = ${extended.bezoutValue()}`
    );

    console.log('\nModular inverse');
    console.log('---------------');

    const inverse = service.calculateInverse(17n, 3120n);
    console.log(`17^(-1) mod 3120 = ${inverse}`);
    console.log(`verification = ${(17n * inverse) % 3120n}`);

    console.log('\nLinear Diophantine equation');
    console.log('---------------------------');

    const solution = EuclideanAlgorithm.solveLinearDiophantine(
        35n,
        15n,
        10n
    );

    console.log(`35x + 15y = 10`);
    console.log(`x = ${solution.x}`);
    console.log(`y = ${solution.y}`);
    console.log(
        `verification = ${35n * solution.x + 15n * solution.y}`
    );

    console.log('\nLarge integer example');
    console.log('---------------------');

    const largeA = 2n ** 200n + 12345n;
    const largeB = 2n ** 150n + 6789n;
    console.log(
        `gcd(2^200 + 12345, 2^150 + 6789) = ${
            service.calculateGCD(largeA, largeB)
        }`
    );

    console.log('\nFailure handling');
    console.log('----------------');

    try {
        service.calculateInverse(6n, 15n);
    } catch (error) {
        console.log(`Handled invalid inverse: ${error.message}`);
    }

    try {
        EuclideanAlgorithm.solveLinearDiophantine(
            6n,
            10n,
            7n
        );
    } catch (error) {
        console.log(`Handled unsolvable equation: ${error.message}`);
    }
}

function runSelfTests() {
    const cases = [
        [0n, 0n],
        [0n, 1n],
        [1n, 0n],
        [48n, 18n],
        [-48n, 18n],
        [1071n, 462n],
        [270n, 192n]
    ];

    for (const [a, b] of cases) {
        const result = EuclideanAlgorithm.extendedGCD(a, b);

        if (result.gcd !== EuclideanAlgorithm.gcd(a, b)) {
            throw new Error(`GCD mismatch for ${a}, ${b}`);
        }

        if (!result.isValid()) {
            throw new Error(`Bézout identity failed for ${a}, ${b}`);
        }
    }

    const inverse = EuclideanAlgorithm.modularInverse(3n, 11n);

    if (inverse !== 4n) {
        throw new Error('Known modular inverse test failed');
    }

    console.log('\nSelf-tests: PASS');
}

runExamples();
runSelfTests();
