"use strict";

/*
 * Chinese Remainder Theorem toolkit.
 *
 * The implementation uses BigInt so that modular products and CRT
 * constructions do not silently lose precision beyond Number.MAX_SAFE_INTEGER.
 */

class CRTError extends Error {}

class Congruence {
    constructor(remainder, modulus) {
        this.modulus = BigInt(modulus);
        if (this.modulus <= 1n) {
            throw new CRTError("Modulus must be greater than 1.");
        }

        const r = BigInt(remainder);
        this.remainder = ((r % this.modulus) + this.modulus) % this.modulus;
    }
}

class CRTResult {
    constructor(remainder, modulus) {
        this.remainder = remainder;
        this.modulus = modulus;
    }

    contains(value) {
        const v = BigInt(value);
        return ((v - this.remainder) % this.modulus + this.modulus) % this.modulus === 0n;
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

function extendedGcd(a, b) {
    let oldR = a < 0n ? -a : a;
    let r = b < 0n ? -b : b;
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

    if (a < 0n) oldS = -oldS;
    if (b < 0n) oldT = -oldT;

    return { gcd: oldR, x: oldS, y: oldT };
}

function modInverse(a, modulus) {
    const { gcd: g, x } = extendedGcd(a, modulus);
    if (g !== 1n) {
        throw new CRTError("Modular inverse does not exist.");
    }
    return ((x % modulus) + modulus) % modulus;
}

function arePairwiseCoprime(system) {
    for (let i = 0; i < system.length; i++) {
        for (let j = i + 1; j < system.length; j++) {
            if (gcd(system[i].modulus, system[j].modulus) !== 1n) {
                return false;
            }
        }
    }
    return true;
}

function solveCoprimeCRT(system) {
    if (system.length === 0) {
        throw new CRTError("The system cannot be empty.");
    }

    if (!arePairwiseCoprime(system)) {
        throw new CRTError("Moduli must be pairwise coprime.");
    }

    const modulus = system.reduce((product, c) => product * c.modulus, 1n);
    let value = 0n;

    for (const c of system) {
        const partial = modulus / c.modulus;
        const inverse = modInverse(partial % c.modulus, c.modulus);
        value += c.remainder * partial * inverse;
    }

    return new CRTResult(
        ((value % modulus) + modulus) % modulus,
        modulus
    );
}

function mergeCongruences(a, b) {
    const g = gcd(a.modulus, b.modulus);
    const difference = b.remainder - a.remainder;

    if (difference % g !== 0n) {
        throw new CRTError("Congruences are inconsistent.");
    }

    const m1 = a.modulus / g;
    const m2 = b.modulus / g;
    const rhs = difference / g;

    const inverse = modInverse(
        ((m1 % m2) + m2) % m2,
        m2
    );

    const k = ((rhs * inverse) % m2 + m2) % m2;
    const combinedModulus = a.modulus * m2;
    const combinedValue =
        ((a.remainder + a.modulus * k) % combinedModulus + combinedModulus)
        % combinedModulus;

    return new CRTResult(combinedValue, combinedModulus);
}

function solveGeneralCRT(system) {
    if (system.length === 0) {
        throw new CRTError("The system cannot be empty.");
    }

    let result = new CRTResult(system[0].remainder, system[0].modulus);

    for (let i = 1; i < system.length; i++) {
        result = mergeCongruences(
            new Congruence(result.remainder, result.modulus),
            system[i]
        );
    }

    return result;
}

function modPow(base, exponent, modulus) {
    if (modulus <= 1n) {
        throw new CRTError("Modulus must be greater than 1.");
    }
    if (exponent < 0n) {
        throw new CRTError("Exponent must be non-negative.");
    }

    base = ((base % modulus) + modulus) % modulus;
    let result = 1n;

    while (exponent > 0n) {
        if (exponent & 1n) {
            result = (result * base) % modulus;
        }
        base = (base * base) % modulus;
        exponent >>= 1n;
    }

    return result;
}

async function evaluateChecks(checks) {
    /*
     * Promise.all models independent status checks.
     * A failed check becomes a structured result rather than crashing
     * the complete evaluation.
     */
    const results = await Promise.all(
        checks.map(async ({ name, delay, passed }) => {
            await new Promise(resolve => setTimeout(resolve, delay));
            return { name, passed };
        })
    );

    return {
        passed: results.every(check => check.passed),
        results
    };
}

async function main() {
    const system = [
        new Congruence(2n, 3n),
        new Congruence(3n, 5n),
        new Congruence(2n, 7n)
    ];

    const result = solveCoprimeCRT(system);
    console.log(`Coprime CRT: x ≡ ${result.remainder} (mod ${result.modulus})`);

    const compatible = [
        new Congruence(2n, 6n),
        new Congruence(8n, 9n)
    ];

    const generalized = solveGeneralCRT(compatible);
    console.log(
        `Generalized CRT: x ≡ ${generalized.remainder} (mod ${generalized.modulus})`
    );

    try {
        solveGeneralCRT([
            new Congruence(1n, 4n),
            new Congruence(2n, 6n)
        ]);
    } catch (error) {
        console.log(`Expected failure: ${error.message}`);
    }

    const checks = await evaluateChecks([
        { name: "unit-tests", delay: 15, passed: true },
        { name: "security-scan", delay: 10, passed: true },
        { name: "integration-tests", delay: 20, passed: false }
    ]);

    console.log("\nConcurrent status evaluation:");
    for (const check of checks.results) {
        console.log(`  ${check.name}: ${check.passed ? "PASS" : "FAIL"}`);
    }
    console.log(`All checks passed: ${checks.passed}`);

    // CRT is useful for recombining independently computed modular results.
    const p = 61n;
    const q = 53n;
    const privateExponent = 2753n;
    const ciphertext = 2790n;

    const mP = modPow(ciphertext, privateExponent % (p - 1n), p);
    const mQ = modPow(ciphertext, privateExponent % (q - 1n), q);

    const recombined = solveCoprimeCRT([
        new Congruence(mP, p),
        new Congruence(mQ, q)
    ]);

    const direct = modPow(ciphertext, privateExponent, p * q);

    if (recombined.remainder !== direct) {
        throw new CRTError("CRT recombination verification failed.");
    }

    console.log(`\nRSA-style recombination verified: ${recombined.remainder}`);
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
