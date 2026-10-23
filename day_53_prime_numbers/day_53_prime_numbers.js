"use strict";

/*
 * Prime-number analysis using JavaScript-specific facilities:
 * BigInt is used for exact integer factorization beyond Number's
 * safe-integer range, while typed arrays make sieve storage compact.
 */

function isPrime(n) {
    if (!Number.isSafeInteger(n) || n < 2) {
        return false;
    }
    if (n === 2) {
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

function primeFactorization(n) {
    if (!Number.isSafeInteger(n) || n < 2) {
        throw new RangeError("n must be an integer >= 2 and <= Number.MAX_SAFE_INTEGER");
    }

    const factors = new Map();
    let value = n;

    while (value % 2 === 0) {
        factors.set(2, (factors.get(2) || 0) + 1);
        value /= 2;
    }

    for (let divisor = 3; divisor * divisor <= value; divisor += 2) {
        while (value % divisor === 0) {
            factors.set(divisor, (factors.get(divisor) || 0) + 1);
            value /= divisor;
        }
    }

    if (value > 1) {
        factors.set(value, (factors.get(value) || 0) + 1);
    }

    return factors;
}

function bigIntPrimeFactorization(input) {
    let n;

    try {
        n = BigInt(input);
    } catch {
        throw new TypeError("Input must represent an integer");
    }

    if (n < 2n) {
        throw new RangeError("n must be >= 2");
    }

    const factors = new Map();

    const addFactor = (prime) => {
        factors.set(prime, (factors.get(prime) || 0n) + 1n);
    };

    while (n % 2n === 0n) {
        addFactor(2n);
        n /= 2n;
    }

    let divisor = 3n;

    while (divisor * divisor <= n) {
        while (n % divisor === 0n) {
            addFactor(divisor);
            n /= divisor;
        }
        divisor += 2n;
    }

    if (n > 1n) {
        addFactor(n);
    }

    return factors;
}

function formatFactors(factors) {
    return [...factors.entries()]
        .map(([prime, exponent]) => {
            const p = String(prime);
            const e = String(exponent);
            return exponent === 1 || exponent === 1n ? p : `${p}^${e}`;
        })
        .join(" × ");
}

function sieve(limit) {
    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("limit must be a non-negative integer");
    }

    if (limit < 2) {
        return [];
    }

    const composite = new Uint8Array(limit + 1);
    composite[0] = 1;
    composite[1] = 1;

    for (let candidate = 2; candidate * candidate <= limit; candidate++) {
        if (composite[candidate] === 0) {
            for (
                let multiple = candidate * candidate;
                multiple <= limit;
                multiple += candidate
            ) {
                composite[multiple] = 1;
            }
        }
    }

    const primes = [];

    for (let n = 2; n <= limit; n++) {
        if (composite[n] === 0) {
            primes.push(n);
        }
    }

    return primes;
}

function segmentedSieve(low, high) {
    if (!Number.isInteger(low) || !Number.isInteger(high) || low > high) {
        throw new RangeError("Require integer low <= high");
    }

    if (high < 2) {
        return [];
    }

    low = Math.max(low, 2);

    const basePrimes = sieve(Math.floor(Math.sqrt(high)));
    const composite = new Uint8Array(high - low + 1);

    for (const prime of basePrimes) {
        const first = Math.max(
            prime * prime,
            Math.ceil(low / prime) * prime
        );

        for (let multiple = first; multiple <= high; multiple += prime) {
            composite[multiple - low] = 1;
        }
    }

    const result = [];

    for (let i = 0; i < composite.length; i++) {
        if (composite[i] === 0) {
            result.push(low + i);
        }
    }

    return result;
}

function primeGaps(primes) {
    const gaps = [];

    for (let i = 1; i < primes.length; i++) {
        gaps.push(primes[i] - primes[i - 1]);
    }

    return gaps;
}

function analyzeDistribution(limit) {
    const primes = sieve(limit);
    const gaps = primeGaps(primes);

    const largestGap = gaps.length ? Math.max(...gaps) : 0;
    const averageGap = gaps.length
        ? gaps.reduce((sum, gap) => sum + gap, 0) / gaps.length
        : 0;

    return Object.freeze({
        limit,
        primeCount: primes.length,
        density: primes.length / limit,
        estimatedDensity: 1 / Math.log(limit),
        largestGap,
        averageGap,
        primes
    });
}

async function analyzeInBatches(limit, batchSize, onBatch) {
    if (!Number.isInteger(limit) || limit < 2) {
        throw new RangeError("limit must be >= 2");
    }

    if (!Number.isInteger(batchSize) || batchSize < 1) {
        throw new RangeError("batchSize must be positive");
    }

    for (let start = 2; start <= limit; start += batchSize) {
        const end = Math.min(start + batchSize - 1, limit);
        const primes = segmentedSieve(start, end);

        await onBatch({
            start,
            end,
            primes
        });

        // Yield to the event loop so a large analysis does not monopolize Node.js.
        await new Promise(resolve => setImmediate(resolve));
    }
}

function verifyFactorization(input, factors) {
    const value = BigInt(input);
    let reconstructed = 1n;

    for (const [prime, exponent] of factors.entries()) {
        if (prime < 2n || exponent < 1n) {
            return false;
        }

        for (let i = 0n; i < exponent; i++) {
            reconstructed *= prime;
        }
    }

    return reconstructed === value;
}

async function main() {
    const numbers = [84, 360, 9973, 1000000];

    console.log("Prime factorization");
    console.log("-------------------");

    for (const number of numbers) {
        const factors = primeFactorization(number);
        console.log(`${number} = ${formatFactors(factors)}`);
    }

    const largeNumber = "100000000000000000000000000000000000000";
    const largeFactors = bigIntPrimeFactorization(largeNumber);

    console.log("\nBigInt factorization");
    console.log("--------------------");
    console.log(`${largeNumber} = ${formatFactors(largeFactors)}`);
    console.log(`Verified: ${verifyFactorization(largeNumber, largeFactors)}`);

    console.log("\nSieve");
    console.log("-----");
    console.log(sieve(50));

    console.log("\nSegmented sieve");
    console.log("---------------");
    console.log(segmentedSieve(1000000, 1000200));

    console.log("\nPrime distribution");
    console.log("------------------");
    const analysis = analyzeDistribution(10000);
    console.log(`π(${analysis.limit}) = ${analysis.primeCount}`);
    console.log(`Empirical density = ${analysis.density.toFixed(6)}`);
    console.log(`1 / ln(n) = ${analysis.estimatedDensity.toFixed(6)}`);
    console.log(`Average gap = ${analysis.averageGap.toFixed(4)}`);
    console.log(`Largest gap = ${analysis.largestGap}`);

    console.log("\nAsynchronous segmented analysis");
    console.log("-------------------------------");

    let discovered = 0;

    await analyzeInBatches(5000, 1000, async ({ start, end, primes }) => {
        discovered += primes.length;
        console.log(`[${start}, ${end}] -> ${primes.length} primes`);
    });

    console.log(`Total primes discovered: ${discovered}`);
}

main().catch(error => {
    console.error(`Prime analysis failed: ${error.message}`);
    process.exitCode = 1;
});
