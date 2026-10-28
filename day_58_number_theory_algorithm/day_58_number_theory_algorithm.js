"use strict";

/*
 * Number-theory algorithms implemented as a small event-driven service.
 * Node.js standard-library features are used so the file has no dependencies.
 */

const crypto = require("node:crypto");
const { EventEmitter } = require("node:events");

class NumberTheoryError extends Error {
    constructor(message) {
        super(message);
        this.name = "NumberTheoryError";
    }
}

function validateModulus(modulus) {
    if (!Number.isSafeInteger(modulus) || modulus <= 0) {
        throw new NumberTheoryError("Modulus must be a positive safe integer.");
    }
}

function gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);

    while (b !== 0) {
        [a, b] = [b, a % b];
    }

    return a;
}

function extendedGcd(a, b) {
    let oldR = a;
    let r = b;
    let oldX = 1;
    let x = 0;
    let oldY = 0;
    let y = 1;

    while (r !== 0) {
        const q = Math.trunc(oldR / r);

        [oldR, r] = [r, oldR - q * r];
        [oldX, x] = [x, oldX - q * x];
        [oldY, y] = [y, oldY - q * y];
    }

    if (oldR < 0) {
        return [-oldR, -oldX, -oldY];
    }

    return [oldR, oldX, oldY];
}

function modPow(base, exponent, modulus) {
    validateModulus(modulus);

    if (!Number.isSafeInteger(exponent) || exponent < 0) {
        throw new NumberTheoryError(
            "Exponent must be a non-negative safe integer."
        );
    }

    let result = 1n;
    let b = BigInt(base) % BigInt(modulus);
    let e = BigInt(exponent);
    const m = BigInt(modulus);

    while (e > 0n) {
        if ((e & 1n) === 1n) {
            result = (result * b) % m;
        }

        b = (b * b) % m;
        e >>= 1n;
    }

    return Number(result);
}

function modPowBigInt(base, exponent, modulus) {
    if (modulus <= 0n) {
        throw new NumberTheoryError("Modulus must be positive.");
    }

    if (exponent < 0n) {
        throw new NumberTheoryError("Exponent must be non-negative.");
    }

    let result = 1n % modulus;
    let b = ((base % modulus) + modulus) % modulus;
    let e = exponent;

    while (e > 0n) {
        if ((e & 1n) === 1n) {
            result = (result * b) % modulus;
        }

        b = (b * b) % modulus;
        e >>= 1n;
    }

    return result;
}

function isPrimeTrial(n) {
    if (!Number.isSafeInteger(n) || n < 2) {
        return false;
    }

    if (n === 2 || n === 3) {
        return true;
    }

    if (n % 2 === 0) {
        return false;
    }

    for (let divisor = 3; divisor * divisor <= n; divisor += 2) {
        if (n % divisor === 0) {
            return false;
        }
    }

    return true;
}

function randomBigIntBelow(limit) {
    if (limit <= 0n) {
        throw new NumberTheoryError("Random bound must be positive.");
    }

    const bits = limit.toString(2).length;
    const bytes = Math.ceil(bits / 8);

    while (true) {
        const buffer = crypto.randomBytes(bytes);
        let value = 0n;

        for (const byte of buffer) {
            value = (value << 8n) | BigInt(byte);
        }

        const mask = (1n << BigInt(bits)) - 1n;
        value &= mask;

        if (value < limit) {
            return value;
        }
    }
}

function isPrimeMillerRabin(n, rounds = 16) {
    n = BigInt(n);

    if (n < 2n) {
        return false;
    }

    const smallPrimes = [
        2n, 3n, 5n, 7n, 11n, 13n, 17n, 19n, 23n, 29n, 31n, 37n
    ];

    for (const p of smallPrimes) {
        if (n === p) {
            return true;
        }

        if (n % p === 0n) {
            return false;
        }
    }

    let d = n - 1n;
    let s = 0;

    while ((d & 1n) === 0n) {
        d >>= 1n;
        s++;
    }

    for (let round = 0; round < rounds; round++) {
        const a = randomBigIntBelow(n - 3n) + 2n;
        let x = modPowBigInt(a, d, n);

        if (x === 1n || x === n - 1n) {
            continue;
        }

        let witnessPassed = false;

        for (let r = 1; r < s; r++) {
            x = (x * x) % n;

            if (x === n - 1n) {
                witnessPassed = true;
                break;
            }
        }

        if (!witnessPassed) {
            return false;
        }
    }

    return true;
}

function modularInverse(a, modulus) {
    validateModulus(modulus);

    const [g, x] = extendedGcd(a, modulus);

    if (g !== 1) {
        throw new NumberTheoryError(
            `${a} has no modular inverse modulo ${modulus}.`
        );
    }

    return ((x % modulus) + modulus) % modulus;
}

function factorize(n) {
    if (!Number.isSafeInteger(n) || n <= 0) {
        throw new NumberTheoryError(
            "Factorization requires a positive safe integer."
        );
    }

    const factors = new Map();
    let remaining = n;

    let exponent = 0;
    while (remaining % 2 === 0 && remaining > 1) {
        exponent++;
        remaining /= 2;
    }

    if (exponent > 0) {
        factors.set(2, exponent);
    }

    for (let divisor = 3; divisor * divisor <= remaining; divisor += 2) {
        exponent = 0;

        while (remaining % divisor === 0) {
            exponent++;
            remaining /= divisor;
        }

        if (exponent > 0) {
            factors.set(divisor, exponent);
        }
    }

    if (remaining > 1) {
        factors.set(remaining, (factors.get(remaining) || 0) + 1);
    }

    return factors;
}

class NumberTheoryService extends EventEmitter {
    constructor() {
        super();
        this.metrics = {
            powerOperations: 0,
            primalityOperations: 0,
            rejectedOperations: 0
        };
    }

    async modularPower(base, exponent, modulus) {
        try {
            const result = modPow(base, exponent, modulus);
            this.metrics.powerOperations++;
            this.emit("completed", {
                operation: "modularPower",
                base,
                exponent,
                modulus,
                result
            });
            return result;
        } catch (error) {
            this.metrics.rejectedOperations++;
            this.emit("rejected", {
                operation: "modularPower",
                error: error.message
            });
            throw error;
        }
    }

    async primalityTest(value) {
        try {
            const result = isPrimeMillerRabin(BigInt(value));
            this.metrics.primalityOperations++;
            this.emit("completed", {
                operation: "primalityTest",
                value: String(value),
                result
            });
            return result;
        } catch (error) {
            this.metrics.rejectedOperations++;
            this.emit("rejected", {
                operation: "primalityTest",
                error: error.message
            });
            throw error;
        }
    }
}

async function main() {
    const service = new NumberTheoryService();

    service.on("completed", event => {
        console.log(
            `[completed] ${event.operation}`,
            event.result !== undefined ? `=> ${event.result}` : ""
        );
    });

    service.on("rejected", event => {
        console.log(`[rejected] ${event.operation}: ${event.error}`);
    });

    console.log("NUMBER THEORY ALGORITHMS");
    console.log("=".repeat(70));

    console.log("\n1. GCD");
    console.log("gcd(252, 105) =", gcd(252, 105));

    console.log("\n2. Fast modular exponentiation");
    const power = await service.modularPower(3, 100, 13);
    if (power !== 9) {
        throw new Error("Unexpected modular exponentiation result.");
    }

    console.log("\n3. BigInt modular exponentiation");
    const largePower = modPowBigInt(
        12345678901234567890n,
        987654321n,
        1000000007n
    );
    console.log("large result =", largePower.toString());

    console.log("\n4. Primality testing");
    for (const value of [1n, 2n, 17n, 97n, 100n, 104729n]) {
        const result = await service.primalityTest(value);
        console.log(`${value}: ${result}`);
    }

    console.log("\n5. Factorization");
    const factors = factorize(360);
    console.log(
        [...factors.entries()]
            .map(([prime, exponent]) => `${prime}^${exponent}`)
            .join(" * ")
    );

    console.log("\n6. Modular inverse");
    const inverse = modularInverse(7, 26);
    console.log("7^-1 mod 26 =", inverse);
    if ((7 * inverse) % 26 !== 1) {
        throw new Error("Modular inverse validation failed.");
    }

    console.log("\n7. Asynchronous batch evaluation");
    const values = [101n, 103n, 107n, 109n, 111n];

    const results = await Promise.all(
        values.map(async value => ({
            value,
            prime: await service.primalityTest(value)
        }))
    );

    console.table(results);

    console.log("\n8. Failure handling");
    try {
        await service.modularPower(2, -1, 7);
    } catch (error) {
        if (!(error instanceof NumberTheoryError)) {
            throw error;
        }
    }

    try {
        modularInverse(6, 15);
    } catch (error) {
        if (!(error instanceof NumberTheoryError)) {
            throw error;
        }
    }

    console.log("\nMetrics");
    console.log(service.metrics);
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
