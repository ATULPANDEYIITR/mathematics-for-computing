"use strict";

/*
 * Advanced Number Theory
 *
 * JavaScript implementation using:
 * - BigInt arithmetic
 * - Miller-Rabin primality testing
 * - Pollard Rho factorization
 * - Legendre symbols
 * - Tonelli-Shanks
 * - Baby-Step Giant-Step
 * - Pohlig-Hellman
 * - Chinese Remainder Theorem
 * - Event-driven computation jobs
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");

const MAX_BSGS_ENTRIES = 2_000_000;

class NumberTheoryError extends Error {}
class ComputationLimitError extends Error {}

function positiveMod(value, modulus) {
    if (modulus <= 0n) {
        throw new NumberTheoryError("Modulus must be positive.");
    }

    return ((value % modulus) + modulus) % modulus;
}

function modularPower(base, exponent, modulus) {
    if (modulus <= 0n || exponent < 0n) {
        throw new NumberTheoryError("Invalid modular exponentiation.");
    }

    base = positiveMod(base, modulus);

    let result = 1n % modulus;

    while (exponent > 0n) {
        if (exponent & 1n) {
            result = result * base % modulus;
        }

        base = base * base % modulus;
        exponent >>= 1n;
    }

    return result;
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
    let oldR = a;
    let r = b;
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

    return [oldR, oldS, oldT];
}

function modularInverse(a, modulus) {
    if (modulus <= 1n) {
        throw new NumberTheoryError("Invalid inverse modulus.");
    }

    const [g, x] = extendedGcd(positiveMod(a, modulus), modulus);

    if (g !== 1n) {
        throw new NumberTheoryError("Modular inverse does not exist.");
    }

    return positiveMod(x, modulus);
}

const SMALL_PRIMES = [
    2n, 3n, 5n, 7n, 11n, 13n,
    17n, 19n, 23n, 29n, 31n, 37n
];

const DETERMINISTIC_64_BIT_BASES = [
    2n, 325n, 9375n, 28178n,
    450775n, 9780504n, 1795265022n
];

function randomBelow(limit) {
    if (limit <= 0n) {
        throw new NumberTheoryError("Random range must be positive.");
    }

    const bitLength = limit.toString(2).length;
    const byteLength = Math.ceil(bitLength / 8);
    const excessBits = byteLength * 8 - bitLength;

    while (true) {
        const bytes = crypto.randomBytes(byteLength);

        if (excessBits > 0) {
            bytes[0] &= 0xff >>> excessBits;
        }

        const value = BigInt(`0x${bytes.toString("hex")}`);

        if (value < limit) {
            return value;
        }
    }
}

function isProbablePrime(n, rounds = 16) {
    if (n < 2n) {
        return false;
    }

    for (const p of SMALL_PRIMES) {
        if (n === p) return true;
        if (n % p === 0n) return false;
    }

    if (rounds < 1) {
        throw new NumberTheoryError("Invalid primality-test round count.");
    }

    let d = n - 1n;
    let s = 0;

    while (d % 2n === 0n) {
        d /= 2n;
        s++;
    }

    const bases = n < (1n << 64n)
        ? DETERMINISTIC_64_BIT_BASES
        : Array.from(
            { length: rounds },
            () => randomBelow(n - 3n) + 2n
        );

    for (const witness of bases) {
        const a = positiveMod(witness, n);

        if (a < 2n) continue;

        let x = modularPower(a, d, n);

        if (x === 1n || x === n - 1n) continue;

        let accepted = false;

        for (let r = 1; r < s; r++) {
            x = x * x % n;

            if (x === n - 1n) {
                accepted = true;
                break;
            }
        }

        if (!accepted) return false;
    }

    return true;
}

function pollardRho(n, maxIterations = 250_000) {
    if (n % 2n === 0n) return 2n;
    if (n % 3n === 0n) return 3n;

    while (true) {
        let x = randomBelow(n - 3n) + 2n;
        let y = x;
        const c = randomBelow(n - 1n) + 1n;
        let divisor = 1n;

        for (let i = 0; i < maxIterations; i++) {
            const f = value =>
                (value * value + c) % n;

            x = f(x);
            y = f(f(y));

            divisor = gcd(x - y, n);

            if (divisor === 1n) continue;
            if (divisor !== n) return divisor;

            break;
        }
    }
}

function factorInteger(number) {
    if (number < 1n) {
        throw new NumberTheoryError("Factorization requires a positive integer.");
    }

    const factors = new Map();

    if (number === 1n) return factors;

    const stack = [number];

    while (stack.length > 0) {
        const current = stack.pop();

        if (current === 1n) continue;

        if (isProbablePrime(current)) {
            factors.set(
                current,
                (factors.get(current) || 0) + 1
            );
            continue;
        }

        const divisor = pollardRho(current);

        if (divisor === 1n || divisor === current) {
            throw new Error("Pollard Rho failed to split an integer.");
        }

        stack.push(divisor);
        stack.push(current / divisor);
    }

    return new Map(
        [...factors.entries()].sort((a, b) =>
            a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0
        )
    );
}

function legendreSymbol(a, p) {
    if (p === 2n || !isProbablePrime(p)) {
        throw new NumberTheoryError("An odd prime modulus is required.");
    }

    a = positiveMod(a, p);

    if (a === 0n) return 0;

    return modularPower(a, (p - 1n) / 2n, p) === 1n ? 1 : -1;
}

function tonelliShanks(a, p) {
    if (p === 2n) {
        return [positiveMod(a, 2n)];
    }

    if (!isProbablePrime(p)) {
        throw new NumberTheoryError("Modulus must be prime.");
    }

    a = positiveMod(a, p);

    if (a === 0n) return [0n];
    if (legendreSymbol(a, p) !== 1) return [];

    if (p % 4n === 3n) {
        const root = modularPower(a, (p + 1n) / 4n, p);

        return [...new Set([
            root.toString(),
            positiveMod(-root, p).toString()
        ])].map(BigInt).sort((x, y) => x < y ? -1 : 1);
    }

    let q = p - 1n;
    let s = 0;

    while (q % 2n === 0n) {
        q /= 2n;
        s++;
    }

    let z = 2n;

    while (legendreSymbol(z, p) !== -1) {
        z++;
    }

    let c = modularPower(z, q, p);
    let x = modularPower(a, (q + 1n) / 2n, p);
    let t = modularPower(a, q, p);
    let m = s;

    while (t !== 1n) {
        let i = 1;
        let value = t * t % p;

        while (i < m && value !== 1n) {
            value = value * value % p;
            i++;
        }

        if (i === m) {
            throw new Error("Tonelli-Shanks invariant failed.");
        }

        const b = modularPower(c, 1n << BigInt(m - i - 1), p);
        const b2 = b * b % p;

        x = x * b % p;
        t = t * b2 % p;
        c = b2;
        m = i;
    }

    const other = positiveMod(-x, p);
    const roots = [...new Set([x.toString(), other.toString()])]
        .map(BigInt)
        .sort((left, right) => left < right ? -1 : 1);

    if (roots.some(root => root * root % p !== a)) {
        throw new Error("Root verification failed.");
    }

    return roots;
}

function exactMultiplicativeOrder(base, p) {
    if (!isProbablePrime(p)) {
        throw new NumberTheoryError("Modulus must be prime.");
    }

    base = positiveMod(base, p);

    if (base === 0n) {
        throw new NumberTheoryError("Zero has no multiplicative order.");
    }

    let order = p - 1n;

    for (const prime of factorInteger(order).keys()) {
        while (
            order % prime === 0n &&
            modularPower(base, order / prime, p) === 1n
        ) {
            order /= prime;
        }
    }

    return order;
}

function ceilSqrt(n) {
    let x = BigInt(Math.floor(Math.sqrt(Number(n))));

    while (x * x < n) x++;
    while ((x - 1n) * (x - 1n) >= n) x--;

    return x;
}

function babyStepGiantStep(
    base,
    target,
    modulus,
    order,
    maxEntries = MAX_BSGS_ENTRIES
) {
    if (modulus <= 1n || order <= 0n) {
        throw new NumberTheoryError("Invalid discrete logarithm parameters.");
    }

    const m = ceilSqrt(order);

    if (m > BigInt(maxEntries)) {
        throw new ComputationLimitError("BSGS memory limit exceeded.");
    }

    base = positiveMod(base, modulus);
    target = positiveMod(target, modulus);

    const babySteps = new Map();
    let value = 1n;

    for (let j = 0n; j < m; j++) {
        if (!babySteps.has(value.toString())) {
            babySteps.set(value.toString(), j);
        }

        value = value * base % modulus;
    }

    const giantFactor = modularInverse(
        modularPower(base, m, modulus),
        modulus
    );

    let gamma = target;
    const giantCount = (order + m - 1n) / m;

    for (let i = 0n; i <= giantCount; i++) {
        const key = gamma.toString();

        if (babySteps.has(key)) {
            const candidate = i * m + babySteps.get(key);

            if (
                candidate < order &&
                modularPower(base, candidate, modulus) === target
            ) {
                return candidate;
            }
        }

        gamma = gamma * giantFactor % modulus;
    }

    return null;
}

function chineseRemainder(residues, moduli) {
    if (
        residues.length === 0 ||
        residues.length !== moduli.length
    ) {
        throw new NumberTheoryError("Invalid CRT input.");
    }

    let result = 0n;
    let product = 1n;

    for (let i = 0; i < residues.length; i++) {
        const modulus = moduli[i];

        if (modulus <= 1n || gcd(product, modulus) !== 1n) {
            throw new NumberTheoryError("CRT moduli must be coprime.");
        }

        const correction = positiveMod(
            (residues[i] - result) *
            modularInverse(product, modulus),
            modulus
        );

        result += product * correction;
        product *= modulus;
        result = positiveMod(result, product);
    }

    return result;
}

function pohligHellman(
    base,
    target,
    p,
    order,
    maxEntries = MAX_BSGS_ENTRIES
) {
    if (!isProbablePrime(p)) {
        throw new NumberTheoryError("Prime modulus required.");
    }

    if (order <= 0n || order > p - 1n) {
        throw new NumberTheoryError("Invalid group order.");
    }

    base = positiveMod(base, p);
    target = positiveMod(target, p);

    if (base === 0n) {
        throw new NumberTheoryError("Base cannot be zero.");
    }

    if (modularPower(base, order, p) !== 1n) {
        throw new NumberTheoryError("Incorrect group order.");
    }

    const factorization = factorInteger(order);

    for (const prime of factorization.keys()) {
        if (
            modularPower(base, order / prime, p) === 1n
        ) {
            throw new NumberTheoryError("Order is not exact.");
        }
    }

    if (modularPower(target, order, p) !== 1n) {
        return null;
    }

    const residues = [];
    const moduli = [];

    for (const [q, exponent] of factorization) {
        let primePower = 1n;

        for (let i = 0; i < exponent; i++) {
            primePower *= q;
        }

        const g = modularPower(base, order / primePower, p);
        const h = modularPower(target, order / primePower, p);

        const digitBase = modularPower(g, primePower / q, p);

        let x = 0n;
        let qPower = 1n;

        for (let k = 0; k < exponent; k++) {
            const inversePartial = modularInverse(
                modularPower(g, x, p),
                p
            );

            const correction = h * inversePartial % p;

            const digitTarget = modularPower(
                correction,
                primePower / (qPower * q),
                p
            );

            const digit = babyStepGiantStep(
                digitBase,
                digitTarget,
                p,
                q,
                maxEntries
            );

            if (digit === null) return null;

            x += digit * qPower;
            qPower *= q;
        }

        residues.push(x);
        moduli.push(primePower);
    }

    const answer = chineseRemainder(residues, moduli) % order;

    if (modularPower(base, answer, p) !== target) {
        throw new Error("Pohlig-Hellman verification failed.");
    }

    return answer;
}

/*
 * The event layer separates mathematical computation from
 * job creation, completion notification, and result storage.
 *
 * setImmediate yields to the Node.js event loop. The algorithms
 * themselves still execute on the main thread; intensive production
 * workloads should use worker_threads.
 */
class NumberTheoryWorkbench extends EventEmitter {
    constructor(options = {}) {
        super();

        this.maxEntries = options.maxEntries ?? MAX_BSGS_ENTRIES;
        this.jobs = new Map();
        this.nextJobId = 1;
    }

    async analyzeQuadraticResidue(value, prime) {
        await new Promise(resolve => setImmediate(resolve));

        const symbol = legendreSymbol(value, prime);
        const roots = tonelliShanks(value, prime);

        const report = Object.freeze({
            value: positiveMod(value, prime),
            prime,
            symbol,
            isResidue: symbol >= 0,
            roots: Object.freeze(roots)
        });

        this.emit("quadratic-residue:completed", report);

        return report;
    }

    async factor(number) {
        await new Promise(resolve => setImmediate(resolve));

        const factors = factorInteger(number);

        const report = {
            number,
            factors: Object.fromEntries(
                [...factors.entries()].map(
                    ([prime, exponent]) => [
                        prime.toString(),
                        exponent
                    ]
                )
            )
        };

        this.emit("factorization:completed", report);

        return report;
    }

    async solveDiscreteLog(base, target, prime, order) {
        const jobId = this.nextJobId++;

        const job = {
            id: jobId,
            base,
            target,
            prime,
            order,
            status: "PENDING",
            result: null,
            error: null,
            createdAt: new Date().toISOString()
        };

        this.jobs.set(jobId, job);

        this.emit("job:created", { ...job });

        await new Promise(resolve => setImmediate(resolve));

        job.status = "RUNNING";
        this.emit("job:running", { id: jobId });

        try {
            job.result = pohligHellman(
                base,
                target,
                prime,
                order,
                this.maxEntries
            );

            job.status = job.result === null
                ? "NO_SOLUTION"
                : "SOLVED";

            this.emit("job:completed", {
                id: job.id,
                status: job.status,
                result: job.result
            });
        } catch (error) {
            job.status = "FAILED";
            job.error = error.message;

            this.emit("job:failed", {
                id: job.id,
                error: job.error
            });

            throw error;
        }

        return Object.freeze({ ...job });
    }

    getJob(jobId) {
        const job = this.jobs.get(jobId);

        if (!job) {
            throw new NumberTheoryError("Unknown computation job.");
        }

        return Object.freeze({ ...job });
    }
}

function runTests() {
    assert.equal(modularPower(7n, 128n, 13n), 9n);
    assert.equal(modularInverse(3n, 11n), 4n);
    assert.equal(gcd(84n, 30n), 6n);

    assert.equal(isProbablePrime(1019n), true);
    assert.equal(isProbablePrime(104060n), false);

    const factors = factorInteger(600851475143n);

    let reconstructed = 1n;

    for (const [prime, exponent] of factors) {
        reconstructed *= prime ** BigInt(exponent);
        assert.equal(isProbablePrime(prime), true);
    }

    assert.equal(reconstructed, 600851475143n);

    assert.equal(legendreSymbol(56n * 56n, 1019n), 1);
    assert.equal(legendreSymbol(0n, 1019n), 0);
    assert.equal(legendreSymbol(2n, 1019n), -1);

    assert.deepEqual(
        tonelliShanks(56n * 56n, 1019n),
        [56n, 963n]
    );

    assert.deepEqual(tonelliShanks(2n, 1019n), []);
    assert.deepEqual(tonelliShanks(5n, 2n), [1n]);

    const order = exactMultiplicativeOrder(2n, 1019n);

    assert.equal(order, 1018n);

    const secret = 137n;
    const target = modularPower(2n, secret, 1019n);

    assert.equal(
        pohligHellman(2n, target, 1019n, order),
        secret
    );

    assert.equal(
        pohligHellman(2n, 0n, 1019n, order),
        null
    );
}

async function main() {
    runTests();

    const workbench = new NumberTheoryWorkbench();

    workbench.on("quadratic-residue:completed", report => {
        console.log("\nResidue event:", report);
    });

    workbench.on("factorization:completed", report => {
        console.log("\nFactorization event:", report);
    });

    workbench.on("job:completed", event => {
        console.log("\nDiscrete logarithm event:", {
            jobId: event.id,
            status: event.status,
            result: event.result
        });
    });

    const p = 1019n;
    const base = 2n;
    const order = exactMultiplicativeOrder(base, p);
    const secret = 137n;
    const target = modularPower(base, secret, p);

    console.log("ADVANCED NUMBER THEORY");
    console.log("======================");
    console.log("Prime modulus:", p.toString());
    console.log("Multiplicative order:", order.toString());

    await workbench.analyzeQuadraticResidue(
        56n * 56n,
        p
    );

    await workbench.analyzeQuadraticResidue(2n, p);

    await workbench.factor(600851475143n);

    const job = await workbench.solveDiscreteLog(
        base,
        target,
        p,
        order
    );

    console.log("\nFinal job state:", job.status);
    console.log("Recovered exponent:", job.result.toString());

    console.log("\nAll JavaScript mathematical tests passed.");
    console.log(
        "Security: BigInt operations are not guaranteed to be "
        + "constant-time and should not process production secrets."
    );
}

if (require.main === module) {
    main().catch(error => {
        console.error("Execution failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    modularPower,
    modularInverse,
    isProbablePrime,
    factorInteger,
    legendreSymbol,
    tonelliShanks,
    exactMultiplicativeOrder,
    babyStepGiantStep,
    chineseRemainder,
    pohligHellman,
    NumberTheoryWorkbench
};
