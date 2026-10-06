"use strict";

/*
 * Inclusion-Exclusion Principle
 *
 * This file uses JavaScript-specific mechanisms to model overlapping
 * populations, event-driven set analysis, divisibility counting,
 * probability, and derangements.
 *
 * Run with:
 *     node inclusion_exclusion.js
 */

// -----------------------------------------------------------------------------
// Basic set operations
// -----------------------------------------------------------------------------

function intersection(setA, setB) {
    const smaller = setA.size <= setB.size ? setA : setB;
    const larger = setA.size <= setB.size ? setB : setA;
    const result = new Set();

    for (const value of smaller) {
        if (larger.has(value)) {
            result.add(value);
        }
    }

    return result;
}

function union(setA, setB) {
    return new Set([...setA, ...setB]);
}

function inclusionExclusionUnion(sets) {
    if (sets.length === 0) {
        return 0;
    }

    let total = 0;
    const setCount = sets.length;

    for (let mask = 1; mask < 2 ** setCount; mask++) {
        let currentIntersection = null;
        let selectedCount = 0;

        for (let index = 0; index < setCount; index++) {
            if ((mask & (1 << index)) !== 0) {
                selectedCount++;

                currentIntersection =
                    currentIntersection === null
                        ? new Set(sets[index])
                        : intersection(currentIntersection, sets[index]);
            }
        }

        const size = currentIntersection.size;

        if (selectedCount % 2 === 1) {
            total += size;
        } else {
            total -= size;
        }
    }

    return total;
}

// -----------------------------------------------------------------------------
// Exact-category analysis
// -----------------------------------------------------------------------------

function classifyThreeSets(universe, a, b, c) {
    const unionABC = new Set([...a, ...b, ...c]);

    const onlyA = [...a].filter(
        value => !b.has(value) && !c.has(value)
    ).length;

    const onlyB = [...b].filter(
        value => !a.has(value) && !c.has(value)
    ).length;

    const onlyC = [...c].filter(
        value => !a.has(value) && !b.has(value)
    ).length;

    const exactlyTwo = [...unionABC].filter(value => {
        let membership = 0;
        if (a.has(value)) membership++;
        if (b.has(value)) membership++;
        if (c.has(value)) membership++;
        return membership === 2;
    }).length;

    const exactlyThree = [...unionABC].filter(
        value => a.has(value) && b.has(value) && c.has(value)
    ).length;

    return {
        onlyA,
        onlyB,
        onlyC,
        exactlyTwo,
        exactlyThree,
        atLeastOne: unionABC.size,
        none: [...universe].filter(value => !unionABC.has(value)).length
    };
}

// -----------------------------------------------------------------------------
// Divisibility application
// -----------------------------------------------------------------------------

function gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);

    while (b !== 0) {
        [a, b] = [b, a % b];
    }

    return a;
}

function lcm(a, b) {
    if (a === 0 || b === 0) {
        return 0;
    }

    return Math.abs((a / gcd(a, b)) * b);
}

function countMultiples(limit, divisors) {
    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("limit must be a non-negative integer");
    }

    const uniqueDivisors = [...new Set(divisors)];

    if (uniqueDivisors.some(
        divisor => !Number.isInteger(divisor) || divisor <= 0
    )) {
        throw new RangeError("Every divisor must be a positive integer");
    }

    let result = 0;

    for (let mask = 1; mask < 2 ** uniqueDivisors.length; mask++) {
        let commonMultiple = 1;
        let selected = 0;

        for (let index = 0; index < uniqueDivisors.length; index++) {
            if ((mask & (1 << index)) !== 0) {
                selected++;
                commonMultiple = lcm(commonMultiple, uniqueDivisors[index]);
            }
        }

        if (commonMultiple <= limit) {
            const contribution = Math.floor(limit / commonMultiple);
            result += selected % 2 === 1
                ? contribution
                : -contribution;
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// Probability
// -----------------------------------------------------------------------------

function probabilityUnion(pA, pB, pAB) {
    for (const probability of [pA, pB, pAB]) {
        if (probability < 0 || probability > 1) {
            throw new RangeError("Probability must be between 0 and 1");
        }
    }

    if (pAB > Math.min(pA, pB)) {
        throw new RangeError("Intersection probability is invalid");
    }

    return pA + pB - pAB;
}

// -----------------------------------------------------------------------------
// Derangements
// -----------------------------------------------------------------------------

function factorial(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let result = 1n;

    for (let value = 2n; value <= BigInt(n); value++) {
        result *= value;
    }

    return result;
}

function binomial(n, k) {
    if (k < 0 || k > n) {
        return 0n;
    }

    let result = 1n;
    const effectiveK = Math.min(k, n - k);

    for (let i = 1; i <= effectiveK; i++) {
        result = (result * BigInt(n - effectiveK + i)) / BigInt(i);
    }

    return result;
}

function derangements(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let result = 0n;

    for (let k = 0; k <= n; k++) {
        const term = binomial(n, k) * factorial(n - k);
        result += k % 2 === 0 ? term : -term;
    }

    return result;
}

// -----------------------------------------------------------------------------
// Event-driven workflow
// -----------------------------------------------------------------------------

class SetAnalysisEventBus {
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
}

class InclusionExclusionAnalyzer {
    constructor(eventBus = new SetAnalysisEventBus()) {
        this.eventBus = eventBus;
    }

    analyze(sets) {
        const directUnion = sets.reduce(
            (result, current) => union(result, current),
            new Set()
        );

        const calculatedUnion = inclusionExclusionUnion(sets);

        const result = {
            numberOfSets: sets.length,
            directUnionSize: directUnion.size,
            inclusionExclusionSize: calculatedUnion,
            consistent: directUnion.size === calculatedUnion
        };

        this.eventBus.emit("analysisCompleted", result);

        return result;
    }
}

// -----------------------------------------------------------------------------
// Practical survey model
// -----------------------------------------------------------------------------

function makeRange(start, end) {
    const values = new Set();

    for (let value = start; value <= end; value++) {
        values.add(value);
    }

    return values;
}

function runSurveyCase() {
    const universe = makeRange(1, 1000);

    const python = new Set();
    const javascript = new Set();
    const sql = new Set();

    // Construct deterministic overlapping populations for a reproducible case.
    for (let student = 1; student <= 1000; student++) {
        if (student <= 620) python.add(student);
        if (student >= 291 && student <= 830) javascript.add(student);
        if (student >= 441 && student <= 920) sql.add(student);
    }

    const analyzer = new InclusionExclusionAnalyzer();

    analyzer.eventBus.on("analysisCompleted", result => {
        console.log(
            `Analysis completed: ${result.inclusionExclusionSize} ` +
            `students belong to at least one set.`
        );
    });

    const analysis = analyzer.analyze([python, javascript, sql]);
    const categories = classifyThreeSets(universe, python, javascript, sql);

    console.log("Survey analysis:", analysis);
    console.log("Mutually exclusive categories:", categories);
}

// -----------------------------------------------------------------------------
// Assertions
// -----------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    const A = new Set([1, 2, 3, 4]);
    const B = new Set([3, 4, 5, 6]);
    const C = new Set([4, 6, 7]);

    assert(
        inclusionExclusionUnion([A, B, C]) === 7,
        "three-set union should equal seven"
    );

    assert(
        countMultiples(100, [2, 3]) === 67,
        "multiples of 2 or 3 should total 67"
    );

    assert(
        countMultiples(100, [2, 3, 5]) === 74,
        "multiples of 2, 3, or 5 should total 74"
    );

    assert(
        Math.abs(probabilityUnion(0.5, 1 / 3, 1 / 6) - 2 / 3) < 1e-12,
        "probability union should be two-thirds"
    );

    assert(derangements(0) === 1n, "D(0) should equal one");
    assert(derangements(4) === 9n, "D(4) should equal nine");
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

function main() {
    runTests();

    console.log("INCLUSION-EXCLUSION PRINCIPLE");
    console.log("=".repeat(72));

    const A = new Set([1, 2, 3, 4, 5]);
    const B = new Set([4, 5, 6, 7]);

    console.log("\nTwo-set overlap");
    console.log("A size:", A.size);
    console.log("B size:", B.size);
    console.log("A intersection B:", intersection(A, B).size);
    console.log("A union B:", inclusionExclusionUnion([A, B]));

    console.log("\nDivisibility");
    console.log(
        "Numbers from 1 through 100 divisible by 2, 3, or 5:",
        countMultiples(100, [2, 3, 5])
    );

    console.log("\nDerangements");
    for (let n = 1; n <= 7; n++) {
        console.log(`D(${n}) = ${derangements(n)}`);
    }

    console.log("\nSurvey case");
    runSurveyCase();

    console.log("\nComplexity");
    console.log(
        "General inclusion-exclusion enumerates every non-empty subset " +
        "of the input sets, requiring O(2^n) intersection combinations. " +
        "Specialized arithmetic applications can reduce the effective " +
        "work by exploiting divisibility structure."
    );
}

main();
