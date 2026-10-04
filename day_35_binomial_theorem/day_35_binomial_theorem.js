/**
 * Binomial Theorem
 *
 * Practical JavaScript implementation covering:
 * - finite binomial expansion
 * - coefficient extraction
 * - Pascal triangle
 * - binomial identities
 * - polynomial convolution
 * - generalized binomial series
 * - combinatorial counting
 * - binomial probability
 *
 * Node.js 18+.
 *
 * BigInt is used for exact integer coefficients because JavaScript Number
 * cannot represent arbitrarily large integers exactly.
 */

"use strict";

// -----------------------------------------------------------------------------
// Exact finite binomial coefficients
// -----------------------------------------------------------------------------

function validateNonNegativeInteger(value, name) {
    if (!Number.isInteger(value) || value < 0) {
        throw new RangeError(`${name} must be a non-negative integer`);
    }
}

function binomialCoefficient(n, k) {
    validateNonNegativeInteger(n, "n");
    validateNonNegativeInteger(k, "k");

    if (k > n) return 0n;

    // Symmetry minimizes the number of multiplicative iterations.
    const effectiveK = Math.min(k, n - k);

    let result = 1n;

    for (let i = 1; i <= effectiveK; i++) {
        result = (result * BigInt(n - effectiveK + i)) / BigInt(i);
    }

    return result;
}

function binomialRow(n) {
    validateNonNegativeInteger(n, "n");

    return Array.from(
        { length: n + 1 },
        (_, k) => binomialCoefficient(n, k)
    );
}

// -----------------------------------------------------------------------------
// Finite expansion
// -----------------------------------------------------------------------------

function expandBinomial(n, a = 1n, b = 1n) {
    validateNonNegativeInteger(n, "n");

    const terms = [];

    for (let k = 0; k <= n; k++) {
        const coefficient =
            binomialCoefficient(n, k) *
            (a ** BigInt(n - k)) *
            (b ** BigInt(k));

        terms.push({
            power: k,
            coefficient
        });
    }

    return terms;
}

function formatPolynomial(terms, variable = "x") {
    const pieces = [];

    for (const { power, coefficient } of terms) {
        if (coefficient === 0n) continue;

        const negative = coefficient < 0n;
        const magnitude = negative ? -coefficient : coefficient;

        let body;

        if (power === 0) {
            body = magnitude.toString();
        } else if (power === 1) {
            body = magnitude === 1n
                ? variable
                : `${magnitude}${variable}`;
        } else {
            body = magnitude === 1n
                ? `${variable}^${power}`
                : `${magnitude}${variable}^${power}`;
        }

        if (pieces.length === 0) {
            pieces.push(negative ? `-${body}` : body);
        } else {
            pieces.push(`${negative ? "-" : "+"} ${body}`);
        }
    }

    return pieces.join(" ") || "0";
}

// -----------------------------------------------------------------------------
// Pascal triangle
// -----------------------------------------------------------------------------

function pascalTriangle(rows) {
    validateNonNegativeInteger(rows, "rows");

    const triangle = [];

    for (let r = 0; r < rows; r++) {
        triangle.push(binomialRow(r));
    }

    return triangle;
}

// -----------------------------------------------------------------------------
// Coefficient extraction
// -----------------------------------------------------------------------------

function coefficientOfX(n, k, a = 1n, b = 1n) {
    validateNonNegativeInteger(n, "n");
    validateNonNegativeInteger(k, "k");

    if (k > n) return 0n;

    return (
        binomialCoefficient(n, k) *
        (a ** BigInt(n - k)) *
        (b ** BigInt(k))
    );
}

// -----------------------------------------------------------------------------
// Identities
// -----------------------------------------------------------------------------

function verifyPascalIdentity(n, k) {
    if (n <= 0 || k < 0 || k > n) {
        throw new RangeError("Require n > 0 and 0 <= k <= n");
    }

    return (
        binomialCoefficient(n, k) ===
        binomialCoefficient(n - 1, k - 1) +
        binomialCoefficient(n - 1, k)
    );
}

function verifySymmetry(n, k) {
    if (k < 0 || k > n) {
        throw new RangeError("Require 0 <= k <= n");
    }

    return (
        binomialCoefficient(n, k) ===
        binomialCoefficient(n, n - k)
    );
}

function verifyVandermonde(r, s, n) {
    validateNonNegativeInteger(r, "r");
    validateNonNegativeInteger(s, "s");
    validateNonNegativeInteger(n, "n");

    let left = 0n;

    for (let k = 0; k <= n; k++) {
        if (k <= r && n - k <= s) {
            left +=
                binomialCoefficient(r, k) *
                binomialCoefficient(s, n - k);
        }
    }

    return left === binomialCoefficient(r + s, n);
}

// -----------------------------------------------------------------------------
// Polynomial multiplication
// -----------------------------------------------------------------------------

function multiplyPolynomials(left, right) {
    const result = Array(left.length + right.length - 1).fill(0n);

    // Coefficients combine by convolution: every term from the first
    // polynomial multiplies every compatible term from the second.
    for (let i = 0; i < left.length; i++) {
        for (let j = 0; j < right.length; j++) {
            result[i + j] += left[i] * right[j];
        }
    }

    return result;
}

function polynomialTerms(coefficients) {
    return coefficients.map((coefficient, power) => ({
        power,
        coefficient
    }));
}

// -----------------------------------------------------------------------------
// Generalized binomial theorem
// -----------------------------------------------------------------------------

function generalizedCoefficient(alpha, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer");
    }

    let coefficient = 1;

    for (let j = 0; j < k; j++) {
        coefficient *= (alpha - j) / (j + 1);
    }

    return coefficient;
}

function generalizedBinomialSeries(alpha, x, terms) {
    if (!Number.isInteger(terms) || terms <= 0) {
        throw new RangeError("terms must be a positive integer");
    }

    if (!Number.isFinite(alpha) || !Number.isFinite(x)) {
        throw new TypeError("alpha and x must be finite numbers");
    }

    // For non-integer alpha, the ordinary generalized series has its
    // convergence interval |x| < 1.
    if (!Number.isInteger(alpha) && Math.abs(x) >= 1) {
        throw new RangeError(
            "The generalized binomial series requires |x| < 1 "
            + "for a non-integer exponent."
        );
    }

    let coefficient = 1;
    let power = 1;
    let sum = 1;

    for (let k = 1; k < terms; k++) {
        coefficient *= (alpha - (k - 1)) / k;
        power *= x;
        sum += coefficient * power;
    }

    return sum;
}

// -----------------------------------------------------------------------------
// Event-driven workflow for an expansion request
// -----------------------------------------------------------------------------

class ExpansionEngine {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) ?? [];

        for (const listener of listeners) {
            listener(payload);
        }
    }

    expand(n, a = 1n, b = 1n) {
        this.emit("expansionStarted", { n, a, b });

        try {
            const terms = expandBinomial(n, a, b);

            this.emit("expansionCompleted", {
                n,
                termCount: terms.length
            });

            return terms;
        } catch (error) {
            this.emit("expansionFailed", {
                message: error.message
            });

            throw error;
        }
    }
}

// -----------------------------------------------------------------------------
// Combinatorial application
// -----------------------------------------------------------------------------

function countBinaryStrings(length, ones) {
    validateNonNegativeInteger(length, "length");
    validateNonNegativeInteger(ones, "ones");

    if (ones > length) return 0n;

    // Selecting the positions occupied by ones gives C(length, ones).
    return binomialCoefficient(length, ones);
}

// -----------------------------------------------------------------------------
// Binomial probability
// -----------------------------------------------------------------------------

function binomialProbability(n, k, p) {
    validateNonNegativeInteger(n, "n");
    validateNonNegativeInteger(k, "k");

    if (k > n) return 0;

    if (!Number.isFinite(p) || p < 0 || p > 1) {
        throw new RangeError("p must be between 0 and 1");
    }

    return (
        Number(binomialCoefficient(n, k)) *
        p ** k *
        (1 - p) ** (n - k)
    );
}

function binomialDistribution(n, p) {
    validateNonNegativeInteger(n, "n");

    return Array.from(
        { length: n + 1 },
        (_, k) => binomialProbability(n, k, p)
    );
}

// -----------------------------------------------------------------------------
// Demonstration
// -----------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("BINOMIAL THEOREM - JAVASCRIPT IMPLEMENTATION");
    console.log("=".repeat(72));

    console.log("\nFinite expansion");
    const expansion = expandBinomial(5);
    console.log("(1 + x)^5 =", formatPolynomial(expansion));

    const scaledExpansion = expandBinomial(4, 2n, 3n);
    console.log("(2 + 3x)^4 =", formatPolynomial(scaledExpansion));

    console.log("\nExact coefficients with BigInt");
    console.log("C(50, 25) =", binomialCoefficient(50, 25).toString());

    console.log("\nCoefficient extraction");
    console.log(
        "[x^4](1+x)^10 =",
        coefficientOfX(10, 4).toString()
    );
    console.log(
        "[x^3](2+5x)^7 =",
        coefficientOfX(7, 3, 2n, 5n).toString()
    );

    console.log("\nPascal triangle");
    for (const row of pascalTriangle(7)) {
        console.log(row.map(value => value.toString()).join(" "));
    }

    console.log("\nIdentity checks");
    console.log("Pascal identity:", verifyPascalIdentity(15, 6));
    console.log("Symmetry:", verifySymmetry(15, 6));
    console.log("Vandermonde:", verifyVandermonde(8, 7, 6));

    console.log("\nPolynomial convolution");
    const polynomialA = [1n, 2n];       // 1 + 2x
    const polynomialB = [3n, 4n, 1n];  // 3 + 4x + x^2
    const product = multiplyPolynomials(polynomialA, polynomialB);
    console.log(
        "(1 + 2x)(3 + 4x + x^2) =",
        formatPolynomial(polynomialTerms(product))
    );

    console.log("\nGeneralized binomial theorem");
    const alpha = 0.5;
    const x = 0.25;

    console.log(
        "(1 + 0.25)^(1/2) approximation =",
        generalizedBinomialSeries(alpha, x, 20)
    );
    console.log(
        "Math.sqrt(1.25) reference =",
        Math.sqrt(1.25)
    );

    console.log("\nEvent-driven expansion engine");
    const engine = new ExpansionEngine();

    engine.on("expansionStarted", event => {
        console.log(
            `Expansion started: (a + bx)^${event.n}, `
            + `a=${event.a}, b=${event.b}`
        );
    });

    engine.on("expansionCompleted", event => {
        console.log(
            `Expansion completed with ${event.termCount} terms`
        );
    });

    engine.on("expansionFailed", event => {
        console.error("Expansion failed:", event.message);
    });

    const eventDrivenTerms = engine.expand(3, 2n, 5n);
    console.log(formatPolynomial(eventDrivenTerms));

    console.log("\nCombinatorial interpretation");
    console.log(
        "12-bit strings containing exactly 5 ones:",
        countBinaryStrings(12, 5).toString()
    );

    console.log("\nBinomial probability");
    const probabilities = binomialDistribution(10, 0.4);

    probabilities.forEach((value, k) => {
        console.log(`P(X=${k}) = ${value.toFixed(8)}`);
    });

    console.log(
        "Probability total =",
        probabilities.reduce((sum, value) => sum + value, 0).toFixed(12)
    );

    console.log("\nEdge-case behavior");
    console.log("C(10, 20) =", binomialCoefficient(10, 20).toString());
    console.log("(1+x)^0 =", formatPolynomial(expandBinomial(0)));

    try {
        generalizedBinomialSeries(0.5, 1.2, 10);
    } catch (error) {
        console.log("Rejected divergent generalized-series request:", error.message);
    }

    console.log("\nImplementation considerations");
    console.log(
        "BigInt provides exact finite integer coefficients; Number is used "
        + "for generalized real-valued approximations."
    );
    console.log(
        "Large BigInt calculations can consume substantial memory and CPU, "
        + "so untrusted n values should be bounded in production."
    );
}

main();
