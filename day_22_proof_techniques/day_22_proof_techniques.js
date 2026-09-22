/*
 * Proof Techniques
 * =================
 *
 * This executable study demonstrates:
 *   1. Direct proof
 *   2. Proof by contradiction
 *   3. Proof by contrapositive
 *   4. Proof by cases
 *
 * The examples progress from propositional logic to mathematical
 * proof structures, counterexamples, divisibility, parity, modular
 * arithmetic, validation, testing, and a realistic proof-oriented
 * verification engine.
 *
 * Run with:
 *   node proof_techniques.js
 */

"use strict";


// -----------------------------------------------------------------------------
// SECTION 1: LOGICAL FOUNDATIONS
// -----------------------------------------------------------------------------

function implication(p, q) {
    // P -> Q is false only when P is true and Q is false.
    return !p || q;
}

function biconditional(p, q) {
    // P <-> Q is true when both propositions have the same truth value.
    return p === q;
}

function printTruthTable() {
    console.log("\nTRUTH TABLE: P -> Q");
    console.log("----------------------");
    console.log("P       Q       P -> Q");

    for (const p of [false, true]) {
        for (const q of [false, true]) {
            console.log(
                `${String(p).padEnd(7)}${String(q).padEnd(8)}${implication(p, q)}`
            );
        }
    }
}

printTruthTable();


// -----------------------------------------------------------------------------
// SECTION 2: PREDICATES AND DEFINITIONS
// -----------------------------------------------------------------------------

function isEven(n) {
    return Number.isInteger(n) && n % 2 === 0;
}

function isOdd(n) {
    return Number.isInteger(n) && n % 2 !== 0;
}

function divides(divisor, value) {
    if (!Number.isInteger(divisor) || !Number.isInteger(value)) {
        return false;
    }

    if (divisor === 0) {
        return value === 0;
    }

    return value % divisor === 0;
}

function verifyFiniteDomain(predicate, values) {
    const counterexamples = values.filter((value) => !predicate(value));

    return {
        validOnTestedDomain: counterexamples.length === 0,
        counterexamples
    };
}

console.log("\nFINITE DOMAIN TESTING");

const nonNegativeSquares = verifyFiniteDomain(
    (n) => n * n >= 0,
    Array.from({ length: 41 }, (_, index) => index - 20)
);

console.log(nonNegativeSquares);


// -----------------------------------------------------------------------------
// SECTION 3: DIRECT PROOF
// -----------------------------------------------------------------------------

function directProofEvenSum(a, b) {
    /*
     * Claim:
     *   If a and b are even, then a + b is even.
     *
     * Write:
     *   a = 2m
     *   b = 2n
     *
     * Therefore:
     *   a + b = 2m + 2n
     *         = 2(m + n)
     *
     * Since m + n is an integer, the sum is even.
     */
    if (!isEven(a) || !isEven(b)) {
        throw new Error("Both values must be even.");
    }

    const m = a / 2;
    const n = b / 2;
    const result = 2 * (m + n);

    if (result !== a + b || !isEven(result)) {
        throw new Error("Direct proof verification failed.");
    }

    return result;
}

console.log("\nDIRECT PROOF: EVEN + EVEN");

for (const [a, b] of [[2, 8], [-10, 6], [0, 14]]) {
    console.log(`${a} + ${b} = ${directProofEvenSum(a, b)}`);
}


function directProofOddProduct(a, b) {
    /*
     * Claim:
     *   The product of two odd integers is odd.
     *
     * Let:
     *   a = 2m + 1
     *   b = 2n + 1
     *
     * Then:
     *   ab = (2m + 1)(2n + 1)
     *      = 4mn + 2m + 2n + 1
     *      = 2(2mn + m + n) + 1.
     */
    if (!isOdd(a) || !isOdd(b)) {
        throw new Error("Both values must be odd.");
    }

    const m = (a - 1) / 2;
    const n = (b - 1) / 2;

    const coefficient = 2 * m * n + m + n;
    const result = 2 * coefficient + 1;

    if (result !== a * b || !isOdd(result)) {
        throw new Error("Odd product proof verification failed.");
    }

    return result;
}

console.log("\nDIRECT PROOF: ODD × ODD");

for (const [a, b] of [[3, 5], [-3, 7], [1, 9]]) {
    console.log(`${a} × ${b} = ${directProofOddProduct(a, b)}`);
}


// -----------------------------------------------------------------------------
// SECTION 4: DIVISIBILITY
// -----------------------------------------------------------------------------

function directDivisibilityProof(a, b, divisor) {
    /*
     * Claim:
     *   If d | a and d | b, then d | (a + b).
     *
     * Let:
     *   a = dm
     *   b = dn
     *
     * Then:
     *   a + b = d(m + n).
     */
    if (!Number.isInteger(a) ||
        !Number.isInteger(b) ||
        !Number.isInteger(divisor) ||
        divisor === 0) {
        throw new Error("All values must be integers and divisor must be nonzero.");
    }

    if (!divides(divisor, a) || !divides(divisor, b)) {
        throw new Error("The divisor must divide both inputs.");
    }

    const m = a / divisor;
    const n = b / divisor;
    const result = divisor * (m + n);

    return {
        result,
        divisible: divides(divisor, result),
        decomposition: `${a} + ${b} = ${divisor} × (${m} + ${n})`
    };
}

console.log("\nDIVISIBILITY DIRECT PROOF");
console.log(directDivisibilityProof(12, 30, 6));


// -----------------------------------------------------------------------------
// SECTION 5: CONTRAPOSITIVE
// -----------------------------------------------------------------------------

function contrapositiveValues(p, q) {
    /*
     * Original:
     *   P -> Q
     *
     * Contrapositive:
     *   not Q -> not P
     *
     * These two implications always have identical truth values.
     */
    return {
        original: implication(p, q),
        contrapositive: implication(!q, !p)
    };
}

console.log("\nCONTRAPOSITIVE EQUIVALENCE");

for (const p of [false, true]) {
    for (const q of [false, true]) {
        const result = contrapositiveValues(p, q);

        console.log({
            p,
            q,
            original: result.original,
            contrapositive: result.contrapositive,
            equivalent: result.original === result.contrapositive
        });
    }
}


function proveEvenSquareContrapositive(n) {
    /*
     * Claim:
     *   If n² is even, then n is even.
     *
     * Contrapositive:
     *   If n is odd, then n² is odd.
     *
     * Assume n = 2k + 1:
     *
     *   n² = (2k + 1)²
     *      = 4k² + 4k + 1
     *      = 2(2k² + 2k) + 1.
     *
     * Therefore n² is odd.
     */
    if (!Number.isInteger(n)) {
        throw new Error("n must be an integer.");
    }

    if (isOdd(n)) {
        const k = (n - 1) / 2;
        const square = 4 * k * k + 4 * k + 1;

        return {
            case: "odd n",
            k,
            square,
            squareIsOdd: isOdd(square)
        };
    }

    return {
        case: "even n",
        square: n * n,
        implicationConclusion: isEven(n * n) ? isEven(n) : "hypothesis false"
    };
}

console.log("\nCONTRAPOSITIVE: n² EVEN -> n EVEN");

for (let n = -5; n <= 5; n++) {
    console.log(n, proveEvenSquareContrapositive(n));
}


// -----------------------------------------------------------------------------
// SECTION 6: CONTRADICTION
// -----------------------------------------------------------------------------

function contradictionEvenAndOdd(n) {
    /*
     * Suppose an integer is both even and odd.
     *
     * Then:
     *   n = 2a
     *   n = 2b + 1
     *
     * Hence:
     *   2a = 2b + 1
     *
     * and:
     *   2(a - b) = 1,
     *
     * which is impossible because the left side is even.
     */
    const assumedContradiction = isEven(n) && isOdd(n);

    return {
        assumptionPossible: assumedContradiction,
        contradictionReached: !assumedContradiction
    };
}

console.log("\nCONTRADICTION: INTEGER CANNOT BE BOTH EVEN AND ODD");

for (const n of [-4, -1, 0, 1, 4]) {
    console.log(n, contradictionEvenAndOdd(n));
}


function gcd(a, b) {
    /*
     * Euclid's algorithm is used here to support the reduced-fraction
     * structure in the irrationality example.
     */
    a = Math.abs(a);
    b = Math.abs(b);

    while (b !== 0) {
        [a, b] = [b, a % b];
    }

    return a;
}


function reducedFraction(numerator, denominator) {
    if (!Number.isInteger(numerator) ||
        !Number.isInteger(denominator) ||
        denominator === 0) {
        throw new Error("Invalid fraction.");
    }

    const divisor = gcd(numerator, denominator);

    return {
        numerator: numerator / divisor,
        denominator: denominator / divisor
    };
}


function squareRootTwoContradictionStructure() {
    /*
     * Classic contradiction proof:
     *
     * Assume sqrt(2) = a/b in lowest terms.
     *
     * Then:
     *   a² = 2b²
     *
     * Therefore a² is even and a is even.
     *
     * Let:
     *   a = 2k.
     *
     * Substitution gives:
     *   b² = 2k²,
     *
     * so b is even.
     *
     * Thus a and b share a factor of 2, contradicting lowest terms.
     *
     * JavaScript floating-point arithmetic is not used to establish
     * irrationality because numerical approximation is not a proof.
     */
    return [
        "Assume sqrt(2) = a/b in lowest terms.",
        "Square both sides: a² = 2b².",
        "Therefore a² is even, so a is even.",
        "Write a = 2k.",
        "Substitution gives b² = 2k².",
        "Therefore b is even.",
        "Both a and b are even, contradicting lowest terms.",
        "Therefore sqrt(2) is irrational."
    ];
}

console.log("\nSQRT(2) CONTRADICTION PROOF");
for (const step of squareRootTwoContradictionStructure()) {
    console.log("•", step);
}


// -----------------------------------------------------------------------------
// SECTION 7: PROOF BY CASES
// -----------------------------------------------------------------------------

function squareParityByCases(n) {
    /*
     * Every integer is either even or odd.
     *
     * Case 1:
     *   n = 2k
     *   n² = 4k² = 2(2k²), hence n² is even.
     *
     * Case 2:
     *   n = 2k + 1
     *   n² = 4k² + 4k + 1
     *      = 2(2k² + 2k) + 1,
     *   hence n² is odd.
     */
    if (!Number.isInteger(n)) {
        throw new Error("n must be an integer.");
    }

    if (isEven(n)) {
        const k = n / 2;
        const square = 4 * k * k;

        return {
            case: "even",
            square,
            squareParity: "even"
        };
    }

    const k = (n - 1) / 2;
    const square = 4 * k * k + 4 * k + 1;

    return {
        case: "odd",
        square,
        squareParity: "odd"
    };
}

console.log("\nPROOF BY CASES: SQUARE PARITY");

for (let n = -8; n <= 8; n++) {
    console.log(n, squareParityByCases(n));
}


// -----------------------------------------------------------------------------
// SECTION 8: MODULAR CASE ANALYSIS
// -----------------------------------------------------------------------------

function squareRemainderModThree(n) {
    /*
     * There are exactly three residue cases:
     *
     * Case 0: n = 3k
     *   n² ≡ 0 (mod 3)
     *
     * Case 1: n = 3k + 1
     *   n² ≡ 1 (mod 3)
     *
     * Case 2: n = 3k + 2
     *   n² ≡ 1 (mod 3)
     *
     * Therefore a square is never congruent to 2 modulo 3.
     */
    const remainder = ((n % 3) + 3) % 3;

    switch (remainder) {
        case 0:
            return 0;
        case 1:
            return 1;
        case 2:
            return 1;
        default:
            throw new Error("Invalid remainder.");
    }
}

console.log("\nTHREE CASES: SQUARES MODULO 3");

for (let n = -12; n <= 12; n++) {
    console.log(
        `n=${n}, n mod 3=${((n % 3) + 3) % 3}, n² mod 3=${squareRemainderModThree(n)}`
    );
}


// -----------------------------------------------------------------------------
// SECTION 9: ABSOLUTE VALUE AND CASES
// -----------------------------------------------------------------------------

function absoluteValueByCases(x) {
    /*
     * Case 1: x >= 0, so |x| = x.
     * Case 2: x < 0, so |x| = -x.
     */
    return x >= 0 ? x : -x;
}

console.log("\nABSOLUTE VALUE BY CASES");

for (const value of [-10.5, -1, -0, 0, 3.75]) {
    console.log(`|${value}| = ${absoluteValueByCases(value)}`);
}


// -----------------------------------------------------------------------------
// SECTION 10: SIGN ANALYSIS BY CASES
// -----------------------------------------------------------------------------

function classifyProduct(a, b) {
    /*
     * Four sign cases:
     *
     * positive × positive -> positive
     * positive × negative -> negative
     * negative × positive -> negative
     * negative × negative -> positive
     *
     * Zero forms boundary cases and must not be incorrectly classified
     * as positive or negative.
     */
    if (a === 0 || b === 0) {
        return "zero";
    }

    if (a > 0 && b > 0) {
        return "positive";
    }

    if (a > 0 && b < 0) {
        return "negative";
    }

    if (a < 0 && b > 0) {
        return "negative";
    }

    return "positive";
}

console.log("\nSIGN CASE ANALYSIS");

for (const [a, b] of [
    [2, 3],
    [2, -3],
    [-2, 3],
    [-2, -3],
    [0, -4]
]) {
    console.log(`${a} × ${b} -> ${classifyProduct(a, b)}`);
}


// -----------------------------------------------------------------------------
// SECTION 11: CONVERSE, INVERSE, CONTRAPOSITIVE
// -----------------------------------------------------------------------------

function converse(p, q) {
    return implication(q, p);
}

function inverse(p, q) {
    return implication(!p, !q);
}

function logicalForms(p, q) {
    return {
        original: implication(p, q),
        converse: converse(p, q),
        inverse: inverse(p, q),
        contrapositive: implication(!q, !p)
    };
}

console.log("\nLOGICAL FORMS");

const forms = logicalForms(true, false);
console.log(forms);

console.log(
    "\nThe original implication and contrapositive are equivalent. " +
    "The converse and inverse generally require separate proof."
);


// -----------------------------------------------------------------------------
// SECTION 12: COUNTEREXAMPLES
// -----------------------------------------------------------------------------

function findCounterexample(predicate, values) {
    for (const value of values) {
        if (!predicate(value)) {
            return value;
        }
    }

    return null;
}

const falseClaimCounterexample = findCounterexample(
    (n) => n * n < n,
    Array.from({ length: 21 }, (_, index) => index - 10)
);

console.log("\nCOUNTEREXAMPLE");

console.log(
    "False claim: n² < n for every integer n."
);

console.log(
    "Counterexample:",
    falseClaimCounterexample
);


// -----------------------------------------------------------------------------
// SECTION 13: EXISTENTIAL WITNESSES
// -----------------------------------------------------------------------------

function findWitness(predicate, values) {
    for (const value of values) {
        if (predicate(value)) {
            return value;
        }
    }

    return null;
}

const witness = findWitness(
    (n) => n * n === 49,
    Array.from({ length: 41 }, (_, index) => index - 20)
);

console.log("\nEXISTENTIAL STATEMENT");

console.log(
    "There exists an integer n such that n² = 49.",
    "Witness:",
    witness
);


// -----------------------------------------------------------------------------
// SECTION 14: VACUOUS TRUTH
// -----------------------------------------------------------------------------

function vacuousImplication(values) {
    /*
     * Statement:
     *
     *   For every x,
     *   if x > 10 and x < 5,
     *   then x² > 0.
     *
     * The hypothesis is impossible. Therefore there cannot be a counterexample
     * where the hypothesis is true and the conclusion is false.
     */
    for (const x of values) {
        const hypothesis = x > 10 && x < 5;
        const conclusion = x * x > 0;

        if (hypothesis && !conclusion) {
            return false;
        }
    }

    return true;
}

console.log(
    "\nVACUOUS TRUTH:",
    vacuousImplication(
        Array.from({ length: 201 }, (_, index) => index - 100)
    )
);


// -----------------------------------------------------------------------------
// SECTION 15: STRUCTURED PROOF OBJECTS
// -----------------------------------------------------------------------------

class ProofStep {
    constructor(statement, reason) {
        this.statement = statement;
        this.reason = reason;
    }
}

class Proof {
    constructor(title, method) {
        this.title = title;
        this.method = method;
        this.steps = [];
    }

    addStep(statement, reason) {
        this.steps.push(new ProofStep(statement, reason));
    }

    display() {
        console.log(`\n${this.title}`);
        console.log(`Method: ${this.method}`);

        this.steps.forEach((step, index) => {
            console.log(`${index + 1}. ${step.statement}`);
            console.log(`   Reason: ${step.reason}`);
        });
    }
}

const oddSumProof = new Proof(
    "The sum of two odd integers is even",
    "Direct proof"
);

oddSumProof.addStep(
    "Let a and b be odd integers.",
    "Hypothesis"
);

oddSumProof.addStep(
    "a = 2m + 1 for some integer m.",
    "Definition of odd"
);

oddSumProof.addStep(
    "b = 2n + 1 for some integer n.",
    "Definition of odd"
);

oddSumProof.addStep(
    "a + b = 2m + 2n + 2 = 2(m + n + 1).",
    "Algebra"
);

oddSumProof.addStep(
    "a + b is even.",
    "Definition of even"
);

oddSumProof.display();


// -----------------------------------------------------------------------------
// SECTION 16: FINITE PROOF TESTING
// -----------------------------------------------------------------------------

function bruteForceVerify(predicate, start, end) {
    /*
     * Complexity:
     *   O(n)
     *
     * where n is the number of tested integers.
     *
     * This is testing, not a replacement for proof over an infinite domain.
     */
    for (let n = start; n <= end; n++) {
        if (!predicate(n)) {
            return false;
        }
    }

    return true;
}

console.log("\nFINITE TESTING");

console.log(
    "n² >= 0 over [-100000, 100000]:",
    bruteForceVerify((n) => n * n >= 0, -100000, 100000)
);

console.log(
    "A finite test can find counterexamples but cannot by itself prove " +
    "a universal statement over an infinite set."
);


// -----------------------------------------------------------------------------
// SECTION 17: ASYNCHRONOUS PROOF-VERIFICATION PIPELINE
// -----------------------------------------------------------------------------

function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function asynchronousProofCheck() {
    /*
     * JavaScript's asynchronous model is useful when a larger application
     * must process independent verification tasks without blocking.
     *
     * The mathematics remains synchronous in meaning; the asynchronous
     * behavior is an implementation concern.
     */
    const tasks = [
        {
            name: "Even + even is even",
            predicate: () => directProofEvenSum(14, 22) === 36
        },
        {
            name: "Odd × odd is odd",
            predicate: () => directProofOddProduct(5, 7) === 35
        },
        {
            name: "Square parity",
            predicate: () => squareParityByCases(-11).squareParity === "odd"
        }
    ];

    const results = await Promise.all(
        tasks.map(async (task) => {
            await delay(1);

            try {
                return {
                    name: task.name,
                    passed: Boolean(task.predicate())
                };
            } catch (error) {
                return {
                    name: task.name,
                    passed: false,
                    error: error.message
                };
            }
        })
    );

    console.log("\nASYNC VERIFICATION PIPELINE");
    console.table(results);

    return results;
}


// -----------------------------------------------------------------------------
// SECTION 18: VALIDATION
// -----------------------------------------------------------------------------

function validateInteger(value, name = "value") {
    if (!Number.isInteger(value)) {
        throw new TypeError(`${name} must be an integer.`);
    }

    return true;
}

function validateNonZeroInteger(value, name = "value") {
    validateInteger(value, name);

    if (value === 0) {
        throw new RangeError(`${name} must not be zero.`);
    }

    return true;
}

console.log("\nVALIDATION");

try {
    validateNonZeroInteger(0, "divisor");
} catch (error) {
    console.log("Expected validation error:", error.message);
}

try {
    validateInteger(3.14, "n");
} catch (error) {
    console.log("Expected validation error:", error.message);
}


// -----------------------------------------------------------------------------
// SECTION 19: TEST SUITE
// -----------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    for (const p of [false, true]) {
        for (const q of [false, true]) {
            const result = contrapositiveValues(p, q);

            assert(
                result.original === result.contrapositive,
                "Contrapositive equivalence"
            );

            assert(
                result.original === implication(p, q),
                "Implication calculation"
            );
        }
    }

    for (let n = -100; n <= 100; n++) {
        assert(
            isEven(n) !== isOdd(n),
            "Every integer has exactly one parity"
        );

        const squareCase = squareParityByCases(n);

        assert(
            squareCase.square === n * n,
            "Case-based square calculation"
        );

        assert(
            squareRemainderModThree(n) ===
            (((n * n) % 3) + 3) % 3,
            "Square modulo 3"
        );
    }

    for (let a = -20; a <= 20; a += 2) {
        for (let b = -20; b <= 20; b += 2) {
            assert(
                directProofEvenSum(a, b) === a + b,
                "Even sum"
            );
        }
    }

    for (let a = -19; a <= 19; a += 2) {
        for (let b = -19; b <= 19; b += 2) {
            assert(
                directProofOddProduct(a, b) === a * b,
                "Odd product"
            );
        }
    }

    const counterexample = findCounterexample(
        (n) => n * n >= 0,
        Array.from({ length: 101 }, (_, index) => index - 50)
    );

    assert(counterexample === null, "Squares are nonnegative.");

    for (const value of [-8.5, -1, 0, 4.25]) {
        assert(
            absoluteValueByCases(value) === Math.abs(value),
            "Absolute value cases"
        );
    }

    console.log("\nAll synchronous tests passed.");
}


// -----------------------------------------------------------------------------
// SECTION 20: MAIN
// -----------------------------------------------------------------------------

async function main() {
    runTests();
    await asynchronousProofCheck();

    console.log("\nPROOF TECHNIQUE REFERENCE");
    console.log("-----------------------------------------------");
    console.log("Direct:        Assume P, derive Q.");
    console.log("Contrapositive: Assume not Q, derive not P.");
    console.log("Contradiction: Assume P and not Q, derive impossibility.");
    console.log("Cases:         Partition possibilities and prove each case.");
    console.log(
        "\nProgram execution complete."
    );
}

main().catch((error) => {
    console.error("Program terminated with an error:", error);
    process.exitCode = 1;
});
