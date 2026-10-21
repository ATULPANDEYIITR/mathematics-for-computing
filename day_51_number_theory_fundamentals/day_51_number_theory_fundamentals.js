"use strict";

/*
 * Topic: Number Theory Fundamentals
 * Focus: divisibility, primes, composites, factors, and greatest common divisor.
 *
 * Node.js 18+ is sufficient. No external packages are required.
 */

class NumberTheoryError extends Error {
    constructor(message) {
        super(message);
        this.name = "NumberTheoryError";
    }
}

function validateInteger(n, name = "n") {
    if (!Number.isSafeInteger(n)) {
        throw new NumberTheoryError(
            `${name} must be a JavaScript safe integer.`
        );
    }
}

function validatePositiveInteger(n, name = "n") {
    validateInteger(n, name);
    if (n <= 0) {
        throw new NumberTheoryError(`${name} must be positive.`);
    }
}

function divides(divisor, value) {
    validateInteger(divisor, "divisor");
    validateInteger(value, "value");

    if (divisor === 0) {
        throw new NumberTheoryError("Zero cannot be a divisor.");
    }

    return value % divisor === 0;
}

function getDivisors(n) {
    validatePositiveInteger(n);

    const result = [];
    const limit = Math.floor(Math.sqrt(n));

    for (let candidate = 1; candidate <= limit; candidate++) {
        if (n % candidate === 0) {
            result.push(candidate);

            const paired = n / candidate;
            if (paired !== candidate) {
                result.push(paired);
            }
        }
    }

    return result.sort((a, b) => a - b);
}

function isPrime(n) {
    validateInteger(n);

    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;

    const limit = Math.floor(Math.sqrt(n));

    for (let candidate = 3; candidate <= limit; candidate += 2) {
        if (n % candidate === 0) {
            return false;
        }
    }

    return true;
}

function isComposite(n) {
    validatePositiveInteger(n);
    return n > 1 && !isPrime(n);
}

function primeFactorization(n) {
    validatePositiveInteger(n);

    const factors = new Map();
    let remaining = n;

    while (remaining % 2 === 0 && remaining > 1) {
        factors.set(2, (factors.get(2) || 0) + 1);
        remaining /= 2;
    }

    for (let candidate = 3;
         candidate * candidate <= remaining;
         candidate += 2) {
        while (remaining % candidate === 0) {
            factors.set(candidate, (factors.get(candidate) || 0) + 1);
            remaining /= candidate;
        }
    }

    if (remaining > 1) {
        factors.set(remaining, (factors.get(remaining) || 0) + 1);
    }

    return factors;
}

function gcd(a, b) {
    validateInteger(a, "a");
    validateInteger(b, "b");

    a = Math.abs(a);
    b = Math.abs(b);

    if (a === 0 && b === 0) {
        throw new NumberTheoryError("gcd(0, 0) is undefined.");
    }

    // Euclid's algorithm repeatedly replaces (a, b) with (b, a mod b).
    while (b !== 0) {
        [a, b] = [b, a % b];
    }

    return a;
}

function gcdMany(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new NumberTheoryError("A non-empty array is required.");
    }

    return values.reduce((current, value) => gcd(current, value), 0);
}

function lcm(a, b) {
    validateInteger(a, "a");
    validateInteger(b, "b");

    if (a === 0 || b === 0) return 0;

    const result = Math.abs((a / gcd(a, b)) * b);

    if (!Number.isSafeInteger(result)) {
        throw new NumberTheoryError(
            "LCM exceeds JavaScript's safe integer range."
        );
    }

    return result;
}

function areCoprime(a, b) {
    return gcd(a, b) === 1;
}

function classify(n) {
    validateInteger(n);

    if (n < 0) return "negative integer";
    if (n === 0) return "zero";
    if (n === 1) return "unit";
    return isPrime(n) ? "prime" : "composite";
}

function formatFactorization(factors) {
    return [...factors.entries()]
        .map(([prime, exponent]) =>
            exponent === 1 ? `${prime}` : `${prime}^${exponent}`
        )
        .join(" × ");
}

function createProfile(n) {
    validatePositiveInteger(n);

    return Object.freeze({
        value: n,
        classification: classify(n),
        divisors: Object.freeze(getDivisors(n)),
        primeFactorization: formatFactorization(primeFactorization(n))
    });
}

function runRepositoryStyleAnalysis(numbers) {
    /*
     * Array.map is used for independent number analysis. Array.filter then
     * identifies prime values without mutating the source collection.
     */
    const profiles = numbers.map(createProfile);
    const primes = numbers.filter(isPrime);

    return { profiles, primes };
}

function main() {
    console.log("NUMBER THEORY FUNDAMENTALS");
    console.log("=".repeat(72));

    const numbers = [1, 2, 12, 17, 36, 97, 100];
    const analysis = runRepositoryStyleAnalysis(numbers);

    for (const profile of analysis.profiles) {
        console.log(
            `${profile.value}: ${profile.classification}; ` +
            `divisors=[${profile.divisors.join(", ")}]; ` +
            `factorization=${profile.primeFactorization}`
        );
    }

    console.log("\nDIVISIBILITY");
    console.log(`3 divides 36: ${divides(3, 36)}`);
    console.log(`5 divides 36: ${divides(5, 36)}`);

    console.log("\nGREATEST COMMON DIVISOR");
    for (const [a, b] of [[252, 105], [48, 18], [101, 23]]) {
        console.log(`gcd(${a}, ${b}) = ${gcd(a, b)}`);
    }

    console.log("\nMULTI-VALUE GCD");
    const values = [84, 126, 210];
    const common = gcdMany(values);
    console.log(`gcd(${values.join(", ")}) = ${common}`);

    console.log("\nCOPRIMALITY AND LCM");
    console.log(`35 and 64 are coprime: ${areCoprime(35, 64)}`);
    console.log(`lcm(12, 18) = ${lcm(12, 18)}`);

    console.log("\nERROR HANDLING");
    const invalidOperations = [
        ["divides(0, 10)", () => divides(0, 10)],
        ["getDivisors(0)", () => getDivisors(0)],
        ["primeFactorization(-8)", () => primeFactorization(-8)],
        ["gcd(0, 0)", () => gcd(0, 0)]
    ];

    for (const [description, operation] of invalidOperations) {
        try {
            operation();
        } catch (error) {
            if (error instanceof NumberTheoryError) {
                console.log(`${description}: rejected -> ${error.message}`);
            } else {
                throw error;
            }
        }
    }

    /*
     * JavaScript Number is limited to exact integers through 2^53 - 1.
     * Production systems needing larger exact integers should use BigInt and
     * explicitly validate that values are not mixed with Number arithmetic.
     */
    const safeLarge = 600851475143;
    console.log("\nLARGER FACTORIZATION");
    console.log(
        `${safeLarge} -> ${formatFactorization(primeFactorization(safeLarge))}`
    );
}

main();
