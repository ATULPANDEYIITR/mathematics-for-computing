'use strict';

const crypto = require('node:crypto');

class RSAError extends Error {}

function gcd(a, b) {
    a = BigInt(a);
    b = BigInt(b);

    while (b !== 0n) {
        [a, b] = [b, a % b];
    }
    return a < 0n ? -a : a;
}

function extendedGcd(a, b) {
    let oldR = BigInt(a);
    let r = BigInt(b);
    let oldS = 1n;
    let s = 0n;
    let oldT = 0n;
    let t = 1n;

    while (r !== 0n) {
        const q = oldR / r;
        [oldR, r] = [r, oldR - q * r];
        [oldS, s] = [s, oldS - q * s];
        [oldT, t] = [t, oldT - q * t];
    }

    return { gcd: oldR, x: oldS, y: oldT };
}

function modInverse(a, modulus) {
    modulus = BigInt(modulus);
    if (modulus <= 1n) {
        throw new RSAError('Modulus must be greater than one.');
    }

    a = ((BigInt(a) % modulus) + modulus) % modulus;
    const result = extendedGcd(a, modulus);

    if (result.gcd !== 1n) {
        throw new RSAError('Modular inverse does not exist.');
    }

    return ((result.x % modulus) + modulus) % modulus;
}

function modPow(base, exponent, modulus) {
    base = BigInt(base);
    exponent = BigInt(exponent);
    modulus = BigInt(modulus);

    if (modulus <= 0n || exponent < 0n) {
        throw new RSAError('Invalid modular exponentiation arguments.');
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

function randomBigIntBelow(limit) {
    if (limit <= 0n) {
        throw new RSAError('Random upper bound must be positive.');
    }

    const bytes = Math.ceil(limit.toString(2).length / 8);

    while (true) {
        const buffer = crypto.randomBytes(bytes);
        let value = 0n;

        for (const byte of buffer) {
            value = (value << 8n) | BigInt(byte);
        }

        if (value < limit) {
            return value;
        }
    }
}

function isProbablePrime(n, rounds = 20) {
    n = BigInt(n);

    if (n < 2n) return false;

    const smallPrimes = [
        2n, 3n, 5n, 7n, 11n, 13n, 17n, 19n, 23n, 29n, 31n, 37n
    ];

    if (smallPrimes.includes(n)) return true;
    for (const p of smallPrimes) {
        if (n % p === 0n) return false;
    }

    let d = n - 1n;
    let s = 0;

    while (d % 2n === 0n) {
        d /= 2n;
        s++;
    }

    for (let i = 0; i < rounds; i++) {
        const a = 2n + randomBigIntBelow(n - 3n);
        let x = modPow(a, d, n);

        if (x === 1n || x === n - 1n) continue;

        let witnessPassed = false;

        for (let r = 1; r < s; r++) {
            x = (x * x) % n;
            if (x === n - 1n) {
                witnessPassed = true;
                break;
            }
        }

        if (!witnessPassed) return false;
    }

    return true;
}

function randomOddCandidate(bits) {
    const byteCount = Math.ceil(bits / 8);
    const buffer = crypto.randomBytes(byteCount);

    let value = 0n;
    for (const byte of buffer) {
        value = (value << 8n) | BigInt(byte);
    }

    const excessBits = BigInt(byteCount * 8 - bits);
    if (excessBits > 0n) {
        value &= (1n << BigInt(bits)) - 1n;
    }

    value |= 1n << BigInt(bits - 1);
    value |= 1n;

    return value;
}

function generatePrime(bits = 128) {
    if (bits < 16) {
        throw new RSAError('Prime size must be at least 16 bits.');
    }

    while (true) {
        const candidate = randomOddCandidate(bits);
        if (isProbablePrime(candidate)) return candidate;
    }
}

class RSAKeyPair {
    constructor(p, q, e, d) {
        this.p = p;
        this.q = q;
        this.n = p * q;
        this.phi = (p - 1n) * (q - 1n);
        this.e = e;
        this.d = d;
    }

    validate() {
        if (this.p * this.q !== this.n) {
            throw new RSAError('Invalid modulus.');
        }

        if (gcd(this.e, this.phi) !== 1n) {
            throw new RSAError('e is not coprime to phi(n).');
        }

        if ((this.e * this.d) % this.phi !== 1n) {
            throw new RSAError('d is not the inverse of e modulo phi(n).');
        }
    }

    encrypt(message) {
        message = BigInt(message);

        if (message < 0n || message >= this.n) {
            throw new RSAError('Message must satisfy 0 <= m < n.');
        }

        return modPow(message, this.e, this.n);
    }

    decrypt(ciphertext) {
        ciphertext = BigInt(ciphertext);

        if (ciphertext < 0n || ciphertext >= this.n) {
            throw new RSAError('Ciphertext must satisfy 0 <= c < n.');
        }

        return modPow(ciphertext, this.d, this.n);
    }

    decryptCRT(ciphertext) {
        ciphertext = BigInt(ciphertext);

        if (ciphertext < 0n || ciphertext >= this.n) {
            throw new RSAError('Ciphertext must satisfy 0 <= c < n.');
        }

        const dp = this.d % (this.p - 1n);
        const dq = this.d % (this.q - 1n);

        const mp = modPow(ciphertext, dp, this.p);
        const mq = modPow(ciphertext, dq, this.q);
        const qInverse = modInverse(this.q, this.p);

        const h = ((mp - mq) * qInverse) % this.p;
        return (mq + ((h + this.p) % this.p) * this.q) % this.n;
    }
}

function generateKeyPair(bits = 128) {
    const e = 65537n;

    while (true) {
        const p = generatePrime(bits);
        const q = generatePrime(bits);

        if (p === q) continue;

        const phi = (p - 1n) * (q - 1n);
        if (gcd(e, phi) !== 1n) continue;

        const d = modInverse(e, phi);
        const keys = new RSAKeyPair(p, q, e, d);
        keys.validate();
        return keys;
    }
}

function bufferToInteger(buffer) {
    let value = 0n;

    for (const byte of buffer) {
        value = (value << 8n) | BigInt(byte);
    }

    return value;
}

function integerToBuffer(value) {
    value = BigInt(value);

    if (value < 0n) {
        throw new RSAError('Cannot convert a negative integer.');
    }

    if (value === 0n) return Buffer.from([0]);

    let hex = value.toString(16);
    if (hex.length % 2) hex = `0${hex}`;

    return Buffer.from(hex, 'hex');
}

async function evaluatePolicy(message, keys) {
    return new Promise((resolve, reject) => {
        setImmediate(() => {
            try {
                const numericMessage = bufferToInteger(Buffer.from(message, 'utf8'));

                if (numericMessage >= keys.n) {
                    throw new RSAError('Message is too large for the demonstration modulus.');
                }

                const ciphertext = keys.encrypt(numericMessage);
                const recovered = keys.decryptCRT(ciphertext);

                resolve({
                    ciphertext,
                    recoveredText: integerToBuffer(recovered).toString('utf8')
                });
            } catch (error) {
                reject(error);
            }
        });
    });
}

async function main() {
    console.log('RSA mathematical model');

    const mathResult = modPow(7n, 560n, 561n);
    console.log(`7^560 mod 561 = ${mathResult}`);

    const inverse = modInverse(17n, 3120n);
    console.log(`17^-1 mod 3120 = ${inverse}`);

    if (mathResult !== 1n || inverse !== 2753n) {
        throw new RSAError('Fundamental arithmetic validation failed.');
    }

    const keys = generateKeyPair(128);

    console.log('\nKey parameters');
    console.log(`p   = ${keys.p}`);
    console.log(`q   = ${keys.q}`);
    console.log(`n   = ${keys.n}`);
    console.log(`phi = ${keys.phi}`);
    console.log(`e   = ${keys.e}`);
    console.log(`d   = ${keys.d}`);

    const message = 123456789n;
    const ciphertext = keys.encrypt(message);
    const recovered = keys.decrypt(ciphertext);
    const crtRecovered = keys.decryptCRT(ciphertext);

    console.log('\nInteger operation');
    console.log(`message    = ${message}`);
    console.log(`ciphertext = ${ciphertext}`);
    console.log(`decrypted  = ${recovered}`);
    console.log(`CRT        = ${crtRecovered}`);

    if (recovered !== message || crtRecovered !== message) {
        throw new RSAError('RSA round-trip validation failed.');
    }

    const result = await evaluatePolicy('RSA', keys);

    console.log('\nAsynchronous processing');
    console.log(`recovered text = ${result.recoveredText}`);

    try {
        keys.encrypt(keys.n);
    } catch (error) {
        console.log(`Expected validation failure: ${error.message}`);
    }
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
