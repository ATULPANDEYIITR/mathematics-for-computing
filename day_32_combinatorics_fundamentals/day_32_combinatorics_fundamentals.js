'use strict';

/*
 * Combinatorics Fundamentals
 *
 * This Node.js program demonstrates counting through JavaScript-specific
 * structures and event-driven processing.
 *
 * Main ideas:
 *   - Sum rule for mutually exclusive alternatives
 *   - Product rule for sequential choices
 *   - Dependent choices
 *   - Event-driven counting of repository-style configuration requests
 *   - Permutations and combinations
 *   - Restricted identifiers
 *   - Inclusion-exclusion
 *   - Validation and BigInt for large exact counts
 *
 * Run with:
 *   node combinatorics.js
 */


// -----------------------------------------------------------------------------
// Validation
// -----------------------------------------------------------------------------

function assertNonNegativeInteger(value, name) {
    if (!Number.isInteger(value)) {
        throw new TypeError(`${name} must be an integer.`);
    }

    if (value < 0) {
        throw new RangeError(`${name} cannot be negative.`);
    }
}

function assertPositiveInteger(value, name) {
    if (!Number.isInteger(value) || value <= 0) {
        throw new RangeError(`${name} must be a positive integer.`);
    }
}


// -----------------------------------------------------------------------------
// Sum rule
// -----------------------------------------------------------------------------

function sumRule(...counts) {
    counts.forEach((count, index) => {
        assertNonNegativeInteger(count, `counts[${index}]`);
    });

    return counts.reduce((total, count) => total + count, 0);
}

function demonstrateSumRule() {
    console.log('\n=== Sum Rule ===');

    // A request selects exactly one deployment route. Routes are mutually
    // exclusive, so the counts are added.
    const cloudRoutes = 5;
    const privateRoutes = 3;
    const edgeRoutes = 2;

    const totalRoutes = sumRule(
        cloudRoutes,
        privateRoutes,
        edgeRoutes
    );

    console.log('Exclusive deployment routes:', totalRoutes);
}


// -----------------------------------------------------------------------------
// Product rule
// -----------------------------------------------------------------------------

function productRule(...counts) {
    counts.forEach((count, index) => {
        assertNonNegativeInteger(count, `counts[${index}]`);
    });

    return counts.reduce((total, count) => total * count, 1);
}

function demonstrateProductRule() {
    console.log('\n=== Product Rule ===');

    // A deployment plan selects an environment, a region, and a window.
    // Every complete selection contains one choice from each stage.
    const environments = 3;
    const regions = 4;
    const windows = 6;

    const plans = productRule(
        environments,
        regions,
        windows
    );

    console.log('Complete deployment plans:', plans);
}


// -----------------------------------------------------------------------------
// Explicit Cartesian product
// -----------------------------------------------------------------------------

function cartesianProduct(...collections) {
    if (collections.length === 0) {
        return [[]];
    }

    return collections.reduce(
        (partialResults, currentCollection) => {
            const nextResults = [];

            for (const prefix of partialResults) {
                for (const item of currentCollection) {
                    nextResults.push([...prefix, item]);
                }
            }

            return nextResults;
        },
        [[]]
    );
}

function demonstrateCartesianProduct() {
    console.log('\n=== Cartesian Product ===');

    const environments = ['development', 'staging'];
    const regions = ['India', 'Europe'];
    const deploymentModes = ['rolling', 'blue-green'];

    const configurations = cartesianProduct(
        environments,
        regions,
        deploymentModes
    );

    for (const configuration of configurations) {
        console.log(' ', configuration.join(' / '));
    }

    const expectedCount = productRule(
        environments.length,
        regions.length,
        deploymentModes.length
    );

    if (configurations.length !== expectedCount) {
        throw new Error('Cartesian-product verification failed.');
    }
}


// -----------------------------------------------------------------------------
// Dependent choices
// -----------------------------------------------------------------------------

function countDistinctAssignments(totalPeople, positions) {
    assertNonNegativeInteger(totalPeople, 'totalPeople');
    assertNonNegativeInteger(positions, 'positions');

    if (positions > totalPeople) {
        throw new RangeError(
            'The number of positions cannot exceed the available people.'
        );
    }

    let result = 1;

    for (let position = 0; position < positions; position += 1) {
        result *= totalPeople - position;
    }

    return result;
}

function demonstrateDependentChoices() {
    console.log('\n=== Dependent Choices ===');

    // Selecting the first distinct reviewer leaves one fewer person for the
    // second reviewer.
    const reviewers = 6;
    const reviewPositions = 2;

    const assignments = countDistinctAssignments(
        reviewers,
        reviewPositions
    );

    console.log('Ordered distinct reviewer assignments:', assignments);
}


// -----------------------------------------------------------------------------
// BigInt factorial and combinations
// -----------------------------------------------------------------------------

function factorialBigInt(n) {
    assertNonNegativeInteger(n, 'n');

    let result = 1n;

    for (let value = 2n; value <= BigInt(n); value += 1n) {
        result *= value;
    }

    return result;
}

function permutationBigInt(n, r) {
    assertNonNegativeInteger(n, 'n');
    assertNonNegativeInteger(r, 'r');

    if (r > n) {
        throw new RangeError('r cannot exceed n.');
    }

    let result = 1n;

    for (let value = 0; value < r; value += 1) {
        result *= BigInt(n - value);
    }

    return result;
}

function combinationBigInt(n, r) {
    assertNonNegativeInteger(n, 'n');
    assertNonNegativeInteger(r, 'r');

    if (r > n) {
        throw new RangeError('r cannot exceed n.');
    }

    // C(n,r) = C(n,n-r), which reduces the number of multiplication steps.
    const k = Math.min(r, n - r);

    let numerator = 1n;
    let denominator = 1n;

    for (let i = 1; i <= k; i += 1) {
        numerator *= BigInt(n - k + i);
        denominator *= BigInt(i);
    }

    return numerator / denominator;
}

function demonstrateLargeExactCounts() {
    console.log('\n=== Exact Large Counts ===');

    // JavaScript Number is floating-point. BigInt avoids loss of integer
    // precision when combinatorial values become very large.
    const arrangements = permutationBigInt(100, 8);
    const committees = combinationBigInt(100, 5);

    console.log('P(100, 8):', arrangements.toString());
    console.log('C(100, 5):', committees.toString());

    const factorialValue = factorialBigInt(20);
    console.log('20!:', factorialValue.toString());
}


// -----------------------------------------------------------------------------
// Restricted identifier counting
// -----------------------------------------------------------------------------

function countIdentifier({
    letterPositions,
    digitPositions,
    firstDigitNonZero = false,
    allCharactersDistinct = false
}) {
    assertNonNegativeInteger(letterPositions, 'letterPositions');
    assertNonNegativeInteger(digitPositions, 'digitPositions');

    if (letterPositions + digitPositions === 0) {
        return 1n;
    }

    if (!allCharactersDistinct) {
        const firstDigitChoices = firstDigitNonZero ? 9 : 10;

        if (digitPositions === 0) {
            return 26n ** BigInt(letterPositions);
        }

        let result = 26n ** BigInt(letterPositions);

        result *= BigInt(firstDigitChoices);

        if (digitPositions > 1) {
            result *= 10n ** BigInt(digitPositions - 1);
        }

        return result;
    }

    // With distinct characters, letter and digit pools are separate. This
    // implementation assumes letters and digits cannot overlap as character
    // values, which is true for the two alphabets.
    if (letterPositions > 26 || digitPositions > 10) {
        return 0n;
    }

    let result = 1n;

    for (let i = 0; i < letterPositions; i += 1) {
        result *= BigInt(26 - i);
    }

    if (digitPositions > 0) {
        result *= BigInt(firstDigitNonZero ? 9 : 10);

        for (let i = 1; i < digitPositions; i += 1) {
            result *= BigInt(10 - i);
        }
    }

    return result;
}

function demonstrateIdentifierCounting() {
    console.log('\n=== Restricted Identifier Counting ===');

    const unrestricted = countIdentifier({
        letterPositions: 2,
        digitPositions: 3
    });

    const nonZeroStart = countIdentifier({
        letterPositions: 2,
        digitPositions: 3,
        firstDigitNonZero: true
    });

    console.log(
        'Two letters followed by three digits:',
        unrestricted.toString()
    );

    console.log(
        'Same structure with a non-zero first digit:',
        nonZeroStart.toString()
    );
}


// -----------------------------------------------------------------------------
// Inclusion-exclusion
// -----------------------------------------------------------------------------

function unionOfTwoSets(firstCount, secondCount, intersectionCount) {
    assertNonNegativeInteger(firstCount, 'firstCount');
    assertNonNegativeInteger(secondCount, 'secondCount');
    assertNonNegativeInteger(intersectionCount, 'intersectionCount');

    if (intersectionCount > firstCount ||
        intersectionCount > secondCount) {
        throw new RangeError(
            'The intersection cannot exceed either set.'
        );
    }

    return firstCount + secondCount - intersectionCount;
}

function demonstrateInclusionExclusion() {
    console.log('\n=== Inclusion-Exclusion ===');

    // Developers can belong to both skill groups. Adding the groups directly
    // would count the shared population twice.
    const pythonDevelopers = 80;
    const sqlDevelopers = 65;
    const bothSkills = 35;

    const union = unionOfTwoSets(
        pythonDevelopers,
        sqlDevelopers,
        bothSkills
    );

    console.log(
        'Developers with Python or SQL knowledge:',
        union
    );
}


// -----------------------------------------------------------------------------
// Event-driven counting model
// -----------------------------------------------------------------------------

class CountingEventBus {
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

class ConfigurationCounter {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.accepted = 0;
        this.rejected = 0;

        eventBus.on('configuration:selected', () => {
            this.accepted += 1;
        });

        eventBus.on('configuration:rejected', () => {
            this.rejected += 1;
        });
    }

    summary() {
        return {
            accepted: this.accepted,
            rejected: this.rejected
        };
    }
}

function demonstrateEventDrivenCounting() {
    console.log('\n=== Event-Driven Counting ===');

    const bus = new CountingEventBus();
    const counter = new ConfigurationCounter(bus);

    const requests = [
        {
            environment: 'production',
            region: 'India',
            window: 'night'
        },
        {
            environment: 'staging',
            region: 'Europe',
            window: 'morning'
        },
        {
            environment: 'production',
            region: 'US',
            window: 'night'
        },
        {
            environment: 'unknown',
            region: 'India',
            window: 'night'
        }
    ];

    const validEnvironments = new Set([
        'production',
        'staging'
    ]);

    const validRegions = new Set([
        'India',
        'Europe',
        'US'
    ]);

    const validWindows = new Set([
        'morning',
        'night'
    ]);

    for (const request of requests) {
        const valid =
            validEnvironments.has(request.environment) &&
            validRegions.has(request.region) &&
            validWindows.has(request.window);

        if (valid) {
            bus.emit('configuration:selected', request);
        } else {
            bus.emit('configuration:rejected', request);
        }
    }

    console.log(counter.summary());
}


// -----------------------------------------------------------------------------
// Grid path counting
// -----------------------------------------------------------------------------

function gridPathCount(rightMoves, downMoves) {
    assertNonNegativeInteger(rightMoves, 'rightMoves');
    assertNonNegativeInteger(downMoves, 'downMoves');

    return combinationBigInt(
        rightMoves + downMoves,
        rightMoves
    );
}

function demonstrateGridPaths() {
    console.log('\n=== Grid Path Counting ===');

    const paths = gridPathCount(6, 4);

    console.log(
        'Shortest paths requiring six right moves and four down moves:',
        paths.toString()
    );
}


// -----------------------------------------------------------------------------
// Asynchronous counting pipeline
// -----------------------------------------------------------------------------

function fetchChoiceCount(sourceName, count, delayMs) {
    return new Promise((resolve, reject) => {
        if (!Number.isInteger(count) || count < 0) {
            reject(
                new RangeError(
                    `Invalid choice count from ${sourceName}.`
                )
            );
            return;
        }

        setTimeout(() => {
            resolve({
                sourceName,
                count
            });
        }, delayMs);
    });
}

async function demonstrateAsyncCounting() {
    console.log('\n=== Asynchronous Choice Collection ===');

    // Promise.all models independent data sources being collected before the
    // product rule is applied. The final multiplication happens only after
    // every stage has supplied a validated count.
    const [environmentData, regionData, windowData] =
        await Promise.all([
            fetchChoiceCount('environment-service', 3, 10),
            fetchChoiceCount('region-service', 5, 5),
            fetchChoiceCount('window-service', 4, 15)
        ]);

    const total = productRule(
        environmentData.count,
        regionData.count,
        windowData.count
    );

    console.log(
        'Asynchronously collected configuration count:',
        total
    );
}


// -----------------------------------------------------------------------------
// Counting decision model
// -----------------------------------------------------------------------------

function identifyCountingRule({
    exclusiveAlternatives,
    sequentialStages,
    changingAvailability
}) {
    if (exclusiveAlternatives && !sequentialStages) {
        return 'Sum rule';
    }

    if (sequentialStages && changingAvailability) {
        return 'Product rule with dependent stage counts';
    }

    if (sequentialStages) {
        return 'Product rule';
    }

    return 'Inspect overlap or restrictions before counting.';
}

function demonstrateRuleSelection() {
    console.log('\n=== Counting Rule Selection ===');

    console.log(
        identifyCountingRule({
            exclusiveAlternatives: true,
            sequentialStages: false,
            changingAvailability: false
        })
    );

    console.log(
        identifyCountingRule({
            exclusiveAlternatives: false,
            sequentialStages: true,
            changingAvailability: false
        })
    );

    console.log(
        identifyCountingRule({
            exclusiveAlternatives: false,
            sequentialStages: true,
            changingAvailability: true
        })
    );
}


// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

function runTests() {
    console.log('\n=== Tests ===');

    if (sumRule(2, 3, 4) !== 9) {
        throw new Error('Sum rule test failed.');
    }

    if (productRule(2, 3, 4) !== 24) {
        throw new Error('Product rule test failed.');
    }

    if (countDistinctAssignments(5, 2) !== 20) {
        throw new Error('Dependent-choice test failed.');
    }

    if (combinationBigInt(5, 2) !== 10n) {
        throw new Error('Combination test failed.');
    }

    if (permutationBigInt(5, 2) !== 20n) {
        throw new Error('Permutation test failed.');
    }

    if (unionOfTwoSets(70, 50, 20) !== 100) {
        throw new Error('Inclusion-exclusion test failed.');
    }

    if (gridPathCount(4, 3) !== 35n) {
        throw new Error('Grid-path test failed.');
    }

    let rejected = false;

    try {
        productRule(4, -1);
    } catch {
        rejected = true;
    }

    if (!rejected) {
        throw new Error('Negative counts must be rejected.');
    }

    console.log('All tests passed.');
}


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

async function main() {
    console.log('='.repeat(72));
    console.log('COMBINATORICS FUNDAMENTALS');
    console.log('Counting Principles, Sum Rule, Product Rule');
    console.log('='.repeat(72));

    demonstrateSumRule();
    demonstrateProductRule();
    demonstrateCartesianProduct();
    demonstrateDependentChoices();
    demonstrateLargeExactCounts();
    demonstrateIdentifierCounting();
    demonstrateInclusionExclusion();
    demonstrateEventDrivenCounting();
    demonstrateGridPaths();
    demonstrateRuleSelection();

    await demonstrateAsyncCounting();

    runTests();

    console.log('\n=== Precision Note ===');
    console.log(
        'BigInt is used for exact large combinatorial integers because '
        + 'JavaScript Number cannot represent every large integer exactly.'
    );
}

main().catch((error) => {
    console.error('Program failed:', error.message);
    process.exitCode = 1;
});
