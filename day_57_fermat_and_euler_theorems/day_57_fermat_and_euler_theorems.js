'use strict';

const crypto = require('node:crypto');

function validatePositiveInteger(value, name) {
    if (typeof value !== 'bigint' || value <= 0n) {
        throw new TypeError(`${name} must be a positive BigInt`);
    }
}

function gcd(a, b) {
    a = a < 0n ? -a : a;
    b = b < 0n ? -b : b;

    while (b !== 0n) {
        [a, b] = [b, a % b];
    }
    return a;
}

function modPow(base, exponent, modulus) {
    validatePositiveInteger(modulus, 'modulus');

    if (exponent < 0n) {
        throw new RangeError('exponent must be non-negative');
    }

    let result = 1n % modulus;
    base = ((base % modulus) + modulus) % modulus;

    while (exponent > 0n) {
        if (exponent & 1n) {
            result = (result * base) % modulus;
        }
        base = (base * base) % modulus;
        exponent >>= 1n;
    }

    return result;
}

function isPrime(n) {
    if (n < 2n) return false;
    if (n === 2n) return true;
    if (n % 2n === 0n) return false;

    for (let divisor = 3n; divisor * divisor <= n; divisor += 2n) {
        if (n % divisor === 0n) return false;
    }

    return true;
}

function phi(n) {
    validatePositiveInteger(n, 'n');

    let result = n;
    let value = n;

    if (value % 2n === 0n) {
        result -= result / 2n;
        while (value % 2n === 0n) value /= 2n;
    }

    for (let factor = 3n; factor * factor <= value; factor += 2n) {
        if (value % factor === 0n) {
            result -= result / factor;
            while (value % factor === 0n) value /= factor;
        }
    }

    if (value > 1n) {
        result -= result / value;
    }

    return result;
}

function fermatCheck(a, p) {
    if (!isPrime(p)) {
        throw new RangeError('Fermat check requires a prime modulus');
    }

    if (a % p === 0n) return false;

    return modPow(a, p - 1n, p) === 1n;
}

function eulerCheck(a, n) {
    if (gcd(a, n) !== 1n) return false;
    return modPow(a, phi(n), n) === 1n;
}

function extendedGcd(a, b) {
    let oldR = a;
    let r = b;
    let oldS = 1n;
    let s = 0n;

    while (r !== 0n) {
        const quotient = oldR / r;
        [oldR, r] = [r, oldR - quotient * r];
        [oldS, s] = [s, oldS - quotient * s];
    }

    return { gcd: oldR, coefficient: oldS };
}

function modularInverse(a, modulus) {
    if (modulus <= 1n) {
        throw new RangeError('modulus must be greater than 1');
    }

    const { gcd: divisor, coefficient } =
        extendedGcd(((a % modulus) + modulus) % modulus, modulus);

    if (divisor !== 1n) {
        throw new Error('modular inverse does not exist');
    }

    return ((coefficient % modulus) + modulus) % modulus;
}

function inverseUsingEuler(a, n) {
    if (gcd(a, n) !== 1n) {
        throw new Error('a and n must be coprime');
    }

    return modPow(a, phi(n) - 1n, n);
}

class RepositoryMathDemo {
    constructor(name) {
        this.name = name;
        this.events = new Map();
    }

    record(event, data) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event).push({
            timestamp: new Date().toISOString(),
            data
        });
    }

    async evaluate(a, n) {
        await new Promise(resolve => setImmediate(resolve));

        const coprime = gcd(a, n) === 1n;
        const result = {
            a,
            n,
            phi: phi(n),
            coprime,
            eulerTheorem: coprime ? eulerCheck(a, n) : false
        };

        this.record('evaluation', result);
        return result;
    }
}

async function main() {
    console.log('=== Euler Phi Function ===');
    for (const n of [1n, 2n, 5n, 8n, 12n, 36n]) {
        console.log(`phi(${n}) = ${phi(n)}`);
    }

    console.log('\n=== Fermat Little Theorem ===');
    for (const p of [5n, 7n, 11n, 13n]) {
        const value = modPow(3n, p - 1n, p);
        console.log(`3^(${p - 1n}) mod ${p} = ${value}`);
        if (!fermatCheck(3n, p)) {
            throw new Error(`Fermat theorem failed for p=${p}`);
        }
    }

    console.log('\n=== Euler Theorem ===');
    const cases = [[5n, 8n], [5n, 9n], [7n, 12n], [11n, 15n]];

    for (const [a, n] of cases) {
        const result = await new RepositoryMathDemo('number-theory').evaluate(a, n);
        console.log(result);
    }

    console.log('\n=== Modular Inverses ===');
    for (const [a, n] of [[3n, 10n], [7n, 40n], [11n, 26n]]) {
        const direct = modularInverse(a, n);
        const euler = inverseUsingEuler(a, n);
        console.log(`${a}^-1 mod ${n}: direct=${direct}, Euler=${euler}`);
        if (direct !== euler) throw new Error('inverse mismatch');
    }

    console.log('\n=== RSA-Style Modular Workflow ===');
    const p = 61n;
    const q = 53n;
    const n = p * q;
    const phiN = (p - 1n) * (q - 1n);
    const e = 17n;
    const d = modularInverse(e, phiN);
    const message = 65n;

    const ciphertext = modPow(message, e, n);
    const recovered = modPow(ciphertext, d, n);

    console.log(`n=${n}`);
    console.log(`phi(n)=${phiN}`);
    console.log(`e=${e}`);
    console.log(`d=${d}`);
    console.log(`ciphertext=${ciphertext}`);
    console.log(`recovered=${recovered}`);

    if (recovered !== message) {
        throw new Error('RSA-style recovery failed');
    }

    console.log('\n=== Failure Handling ===');

    try {
        fermatCheck(3n, 15n);
    } catch (error) {
        console.log(`Composite modulus rejected: ${error.message}`);
    }

    try {
        modularInverse(6n, 15n);
    } catch (error) {
        console.log(`Non-invertible value rejected: ${error.message}`);
    }

    // Node's crypto module is used only to provide a secure random audit identifier.
    // BigInt modular arithmetic itself is deterministic and suitable for exact integer work.
    const auditId = crypto.randomBytes(8).toString('hex');
    console.log(`Audit identifier: ${auditId}`);

    console.log('\nSecurity note: these routines illustrate number-theoretic mechanisms.'
        + ' Production cryptography should use vetted cryptographic implementations and'
        + ' secure parameter sizes rather than textbook RSA-style arithmetic.');
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
