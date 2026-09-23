/*
 * MATHEMATICAL INDUCTION
 * ======================
 *
 * A practical JavaScript study file covering:
 *
 * - The structure of mathematical induction
 * - Weak induction
 * - Strong induction
 * - Base cases and induction domains
 * - Divisibility
 * - Inequalities
 * - Recurrences
 * - Fibonacci numbers
 * - Dynamic programming
 * - Algorithm correctness
 * - Structural induction
 * - Binary trees
 * - Finite verification versus proof
 * - Edge cases
 * - Performance considerations
 *
 * The program uses standard JavaScript only and can run with Node.js.
 */

"use strict";

// ---------------------------------------------------------------------------
// SECTION 1: OUTPUT AND ASSERTION HELPERS
// ---------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

function expectEqual(actual, expected, description) {
    if (actual !== expected) {
        throw new Error(
            `${description}: expected ${expected}, got ${actual}`
        );
    }

    console.log(`PASS: ${description}`);
}

function expectDeepEqual(actual, expected, description) {
    const actualJSON = JSON.stringify(actual);
    const expectedJSON = JSON.stringify(expected);

    if (actualJSON !== expectedJSON) {
        throw new Error(
            `${description}: expected ${expectedJSON}, got ${actualJSON}`
        );
    }

    console.log(`PASS: ${description}`);
}


// ---------------------------------------------------------------------------
// SECTION 2: THE BASIC STRUCTURE
// ---------------------------------------------------------------------------

section("1. The structure of mathematical induction");

console.log(`
Mathematical induction proves a statement P(n) throughout a specified
integer domain.

The standard structure is:

    1. Base case:
       Prove P(n0).

    2. Inductive hypothesis:
       Assume P(k) for an arbitrary k in the domain.

    3. Inductive step:
       Use P(k) to prove P(k + 1).

The conclusion follows because the base case starts the chain and the
inductive implication propagates truth from one integer to the next.

The inductive hypothesis is not an assumption that every case is already
true. It concerns one arbitrary predecessor.
`);


// ---------------------------------------------------------------------------
// SECTION 3: WEAK INDUCTION
// ---------------------------------------------------------------------------

section("2. Weak induction");

console.log(`
Weak induction is also called ordinary induction or simple induction.

Logical form:

    P(n0)
    For every k >= n0, P(k) -> P(k+1)
    Therefore P(n) for every n >= n0.

Only the immediately preceding statement is assumed in the inductive step.
`);

function sumFormula(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    return n * (n + 1) / 2;
}

function sumIterative(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let total = 0;

    for (let value = 1; value <= n; value++) {
        total += value;
    }

    return total;
}

subsection("2.1 Example: sum of the first n positive integers");

console.log(`
Claim:

    1 + 2 + ... + n = n(n+1)/2

Base case:

    n = 1
    1 = 1(2)/2

Inductive hypothesis:

    1 + 2 + ... + k = k(k+1)/2

Inductive step:

    1 + 2 + ... + k + (k+1)
      = k(k+1)/2 + (k+1)
      = (k+1)(k+2)/2
`);

for (let n = 1; n <= 10; n++) {
    expectEqual(
        sumIterative(n),
        sumFormula(n),
        `sum identity for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 4: BASE CASE AT ZERO
// ---------------------------------------------------------------------------

section("3. Induction can start at zero");

function powersOfTwoIdentity(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let left = 0;

    for (let exponent = 0; exponent <= n; exponent++) {
        left += 2 ** exponent;
    }

    const right = 2 ** (n + 1) - 1;
    return left === right;
}

console.log(`
For

    1 + 2 + 4 + ... + 2^n = 2^(n+1) - 1

the domain begins at n = 0.

Base:

    1 = 2^1 - 1

The base case must match the actual domain of the theorem.
`);

for (let n = 0; n <= 10; n++) {
    expectEqual(
        powersOfTwoIdentity(n),
        true,
        `geometric identity for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 5: DIVISIBILITY
// ---------------------------------------------------------------------------

section("4. Induction and divisibility");

function divides(divisor, value) {
    if (!Number.isInteger(divisor) || divisor === 0) {
        throw new RangeError("The divisor must be a non-zero integer.");
    }

    return value % divisor === 0;
}

function cubicMinusN(n) {
    return n ** 3 - n;
}

console.log(`
Claim:

    3 divides n^3 - n

for every positive integer n.

Inductive step:

    (k+1)^3 - (k+1)
      = (k^3-k) + 3k^2 + 3k

If k^3-k is divisible by 3, the complete expression is also divisible by 3.
`);

for (let n = 1; n <= 20; n++) {
    expectEqual(
        divides(3, cubicMinusN(n)),
        true,
        `3 divides ${n}^3-${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 6: ANOTHER DIVISIBILITY EXAMPLE
// ---------------------------------------------------------------------------

section("5. Divisibility through a recurrence");

function powerMinusOneDivisible(n) {
    return divides(7, 8 ** n - 1);
}

console.log(`
Claim:

    7 divides 8^n - 1

for n >= 1.

The induction step can be written:

    8^(k+1) - 1
      = 8(8^k - 1) + 7.

If 7 divides 8^k - 1, both terms on the right are divisible by 7.
`);

for (let n = 1; n <= 8; n++) {
    expectEqual(
        powerMinusOneDivisible(n),
        true,
        `7 divides 8^${n}-1`
    );
}


// ---------------------------------------------------------------------------
// SECTION 7: INEQUALITIES
// ---------------------------------------------------------------------------

section("6. Induction and inequalities");

function exponentialLowerBound(n) {
    return 2 ** n >= n + 1;
}

console.log(`
Claim:

    2^n >= n + 1

for n >= 0.

Base:

    2^0 = 1 >= 1.

Inductive step:

    2^(k+1)
      = 2 * 2^k
      >= 2(k+1)
      >= k+2.
`);

for (let n = 0; n <= 15; n++) {
    expectEqual(
        exponentialLowerBound(n),
        true,
        `2^n >= n+1 for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 8: FACTORIAL INEQUALITY
// ---------------------------------------------------------------------------

section("7. Factorial inequality");

function factorial(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let result = 1;

    for (let value = 2; value <= n; value++) {
        result *= value;
    }

    return result;
}

function factorialLowerBound(n) {
    if (n < 1) {
        throw new RangeError("n must be at least 1.");
    }

    return factorial(n) >= 2 ** (n - 1);
}

for (let n = 1; n <= 10; n++) {
    expectEqual(
        factorialLowerBound(n),
        true,
        `n! >= 2^(n-1) for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 9: STRONG INDUCTION
// ---------------------------------------------------------------------------

section("8. Strong induction");

console.log(`
Strong induction, or complete induction, assumes all earlier statements:

    P(n0), P(n0+1), ..., P(k)

and uses whichever earlier cases are needed to establish P(k+1).

Weak induction assumes only P(k).

The two methods are equivalent in proof power when formulated correctly.
Strong induction is often more convenient when a case depends on several
smaller cases.
`);


// ---------------------------------------------------------------------------
// SECTION 10: PRIME FACTORIZATION
// ---------------------------------------------------------------------------

section("9. Strong induction example: prime factorization");

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
        throw new RangeError("n must be an integer >= 2.");
    }

    if (isPrime(n)) {
        return [n];
    }

    for (let divisor = 2; divisor * divisor <= n; divisor++) {
        if (n % divisor === 0) {
            return [
                ...primeFactorization(divisor),
                ...primeFactorization(n / divisor)
            ];
        }
    }

    return [n];
}

function product(values) {
    return values.reduce((result, value) => result * value, 1);
}

for (const number of [2, 3, 4, 6, 12, 18, 60, 84, 97, 360]) {
    const factors = primeFactorization(number);

    console.log(`${number} -> ${factors.join(" × ")}`);

    expectEqual(
        product(factors),
        number,
        `factorization product for ${number}`
    );

    expectEqual(
        factors.every(isPrime),
        true,
        `all factors of ${number} are prime`
    );
}


// ---------------------------------------------------------------------------
// SECTION 11: FIBONACCI
// ---------------------------------------------------------------------------

section("10. Strong induction and multiple dependencies");

function fibonacci(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    if (n === 0) return 0;
    if (n === 1) return 1;

    let previous = 0;
    let current = 1;

    for (let index = 2; index <= n; index++) {
        [previous, current] = [
            current,
            previous + current
        ];
    }

    return current;
}

const expectedFibonacci = [
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
];

expectedFibonacci.forEach((expected, n) => {
    expectEqual(
        fibonacci(n),
        expected,
        `Fibonacci F(${n})`
    );
});

console.log(`
The Fibonacci recurrence is:

    F(n) = F(n-1) + F(n-2)

A proof about such a sequence naturally involves more than one preceding
case. Strong induction can make the proof structure straightforward.
`);


// ---------------------------------------------------------------------------
// SECTION 12: PASCAL'S IDENTITY
// ---------------------------------------------------------------------------

section("11. Pascal's identity");

function binomialCoefficient(n, k) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    if (!Number.isInteger(k)) {
        throw new RangeError("k must be an integer.");
    }

    if (k < 0 || k > n) {
        return 0;
    }

    k = Math.min(k, n - k);

    let result = 1;

    for (let index = 1; index <= k; index++) {
        result = result * (n - k + index) / index;
    }

    return result;
}

for (let n = 1; n <= 8; n++) {
    for (let k = 1; k < n; k++) {
        const left = binomialCoefficient(n, k);

        const right =
            binomialCoefficient(n - 1, k - 1) +
            binomialCoefficient(n - 1, k);

        expectEqual(
            left,
            right,
            `Pascal identity C(${n},${k})`
        );
    }
}


// ---------------------------------------------------------------------------
// SECTION 13: COUNTING SUBSETS
// ---------------------------------------------------------------------------

section("12. Induction and counting");

function subsetCount(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    return 2 ** n;
}

console.log(`
An n-element set has 2^n subsets.

Adding one new element doubles the number of subsets:

    S(n+1) = 2S(n)

because every existing subset produces exactly two new possibilities:
with or without the new element.
`);

for (let n = 0; n <= 10; n++) {
    expectEqual(
        subsetCount(n),
        2 ** n,
        `subset count for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 14: ALGORITHM CORRECTNESS
// ---------------------------------------------------------------------------

section("13. Mathematical induction and algorithm correctness");

console.log(`
For insertion sort, a useful loop invariant is:

    After processing the first i elements, that prefix is sorted.

This is an induction-like argument over the loop iterations.

Initialization:
    A one-element prefix is sorted.

Maintenance:
    Insert the next element into the already sorted prefix.

Termination:
    When all elements have been processed, the complete array is sorted.
`);

function insertionSort(values) {
    const result = [...values];

    for (let index = 1; index < result.length; index++) {
        const current = result[index];
        let position = index - 1;

        while (position >= 0 && result[position] > current) {
            result[position + 1] = result[position];
            position--;
        }

        result[position + 1] = current;
    }

    return result;
}

const sortingExamples = [
    [],
    [1],
    [5, 2, 4, 6, 1, 3],
    [3, 3, 2, 1, 2],
    [-5, 4, 0, -2, 8]
];

for (const example of sortingExamples) {
    expectDeepEqual(
        insertionSort(example),
        [...example].sort((a, b) => a - b),
        `insertion sort for ${JSON.stringify(example)}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 15: DYNAMIC PROGRAMMING
// ---------------------------------------------------------------------------

section("14. Strong induction and dynamic programming");

console.log(`
Dynamic programming often computes a state from several smaller states.

Example:

    dp[n] = 1 + min(dp[n-c])

for valid coin denominations c.

Each dependency refers to a smaller amount. A strong-induction proof can
assume correctness of all smaller amounts and establish correctness for n.
`);

function minimumCoins(amount, coins) {
    if (!Number.isInteger(amount) || amount < 0) {
        throw new RangeError("amount must be a non-negative integer.");
    }

    const validCoins = [...new Set(
        coins.filter(
            coin => Number.isInteger(coin) && coin > 0
        )
    )].sort((a, b) => a - b);

    if (amount === 0) {
        return 0;
    }

    if (validCoins.length === 0) {
        return null;
    }

    const infinity = amount + 1;
    const dp = new Array(amount + 1).fill(infinity);
    dp[0] = 0;

    for (let currentAmount = 1; currentAmount <= amount; currentAmount++) {
        for (const coin of validCoins) {
            if (coin > currentAmount) {
                break;
            }

            const previous = dp[currentAmount - coin];

            if (previous !== infinity) {
                dp[currentAmount] = Math.min(
                    dp[currentAmount],
                    previous + 1
                );
            }
        }
    }

    return dp[amount] === infinity ? null : dp[amount];
}

const coinSystem = [1, 3, 4];

const expectedCoinResults = {
    0: 0,
    1: 1,
    2: 2,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 3,
    10: 3
};

for (const [amountText, expected] of Object.entries(expectedCoinResults)) {
    const amount = Number(amountText);

    expectEqual(
        minimumCoins(amount, coinSystem),
        expected,
        `minimum coins for amount ${amount}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 16: REPRESENTABILITY BY 3 AND 5
// ---------------------------------------------------------------------------

section("15. Constructive existence and induction");

function representableByThreeAndFive(n) {
    if (!Number.isInteger(n) || n < 0) {
        return false;
    }

    for (let threes = 0; threes * 3 <= n; threes++) {
        const remainder = n - 3 * threes;

        if (remainder % 5 === 0) {
            return true;
        }
    }

    return false;
}

console.log(`
The values 8, 9, and 10 are representable as 3a + 5b.

For n >= 11, subtracting 3 gives n-3 >= 8. This creates a natural
inductive dependency on a smaller representable value.

The computational function below verifies the representability property.
`);

for (let n = 8; n <= 30; n++) {
    expectEqual(
        representableByThreeAndFive(n),
        true,
        `${n} is representable as 3a + 5b`
    );
}


// ---------------------------------------------------------------------------
// SECTION 17: RECURSIVE DEFINITIONS
// ---------------------------------------------------------------------------

section("16. Recursive definitions and induction");

function recursiveEvenSequence(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    if (n === 0) {
        return 0;
    }

    return recursiveEvenSequence(n - 1) + 2;
}

for (let n = 0; n <= 8; n++) {
    expectEqual(
        recursiveEvenSequence(n),
        2 * n,
        `recursive sequence f(${n}) = 2n`
    );
}

console.log(`
The recursive definition

    f(0) = 0
    f(n) = f(n-1) + 2

can be paired with the inductive claim

    f(n) = 2n.

The recursive definition describes construction or computation.
The induction proof establishes a property of every member of the family.
`);


// ---------------------------------------------------------------------------
// SECTION 18: STRUCTURAL INDUCTION
// ---------------------------------------------------------------------------

section("17. Structural induction");

console.log(`
Structural induction applies to recursively constructed objects rather than
only natural numbers.

Typical structure:

    Base constructors:
        prove the property for each base object.

    Constructor step:
        assume the property for immediate substructures and prove it for
        the newly constructed structure.

This pattern appears with trees, recursive lists, expressions, and grammars.
`);

class TreeNode {
    constructor(value, left = null, right = null) {
        this.value = value;
        this.left = left;
        this.right = right;
    }
}

function treeSize(node) {
    if (node === null) {
        return 0;
    }

    return 1 + treeSize(node.left) + treeSize(node.right);
}

const tree = new TreeNode(
    10,
    new TreeNode(
        5,
        new TreeNode(2),
        new TreeNode(7)
    ),
    new TreeNode(
        15,
        null,
        new TreeNode(20)
    )
);

expectEqual(
    treeSize(tree),
    6,
    "binary-tree structural recursion"
);


// ---------------------------------------------------------------------------
// SECTION 19: FULL BINARY TREES
// ---------------------------------------------------------------------------

section("18. Structural theorem for full binary trees");

class FullBinaryNode {
    constructor(value, left = null, right = null) {
        this.value = value;
        this.left = left;
        this.right = right;
    }

    get isLeaf() {
        return this.left === null && this.right === null;
    }
}

function countInternalAndLeaves(node) {
    if (node === null) {
        return { internal: 0, leaves: 0 };
    }

    if (node.isLeaf) {
        return { internal: 0, leaves: 1 };
    }

    if (node.left === null || node.right === null) {
        throw new Error(
            "Invalid full binary tree: internal node has one child."
        );
    }

    const left = countInternalAndLeaves(node.left);
    const right = countInternalAndLeaves(node.right);

    return {
        internal: 1 + left.internal + right.internal,
        leaves: left.leaves + right.leaves
    };
}

const fullTree = new FullBinaryNode(
    "root",
    new FullBinaryNode(
        "A",
        new FullBinaryNode("B"),
        new FullBinaryNode("C")
    ),
    new FullBinaryNode(
        "D",
        new FullBinaryNode("E"),
        new FullBinaryNode("F")
    )
);

const treeCounts = countInternalAndLeaves(fullTree);

console.log(treeCounts);

expectEqual(
    treeCounts.leaves,
    treeCounts.internal + 1,
    "leaves = internal nodes + 1"
);


// ---------------------------------------------------------------------------
// SECTION 20: FINITE VERIFICATION
// ---------------------------------------------------------------------------

section("19. Finite verification versus proof");

function finiteTest(statement, start, end) {
    if (!Number.isInteger(start) || !Number.isInteger(end)) {
        throw new TypeError("start and end must be integers.");
    }

    if (end < start) {
        throw new RangeError("end must be >= start.");
    }

    for (let n = start; n <= end; n++) {
        if (!statement(n)) {
            return {
                passed: false,
                counterexample: n
            };
        }
    }

    return {
        passed: true,
        counterexample: null
    };
}

const finiteSumTest = finiteTest(
    n => sumIterative(n) === sumFormula(n),
    0,
    1000
);

expectEqual(
    finiteSumTest.passed,
    true,
    "finite sum identity test"
);

console.log(`
Testing 1,000 cases is not equivalent to proving infinitely many cases.

A mathematical proof establishes a general implication for an arbitrary k.
Finite testing establishes only that the selected finite set of cases passed.
`);


// ---------------------------------------------------------------------------
// SECTION 21: FALSE CLAIM AND COUNTEREXAMPLE
// ---------------------------------------------------------------------------

section("20. Counterexample detection");

const falsePrimeTest = finiteTest(
    n => isPrime(n * n + n + 41),
    1,
    100
);

console.log(
    `Finite test passed: ${falsePrimeTest.passed}`
);

console.log(
    `Counterexample: ${falsePrimeTest.counterexample}`
);

if (falsePrimeTest.counterexample !== null) {
    const n = falsePrimeTest.counterexample;
    const value = n * n + n + 41;

    console.log(
        `At n=${n}, n^2+n+41 = ${value}, which is not prime.`
    );
}


// ---------------------------------------------------------------------------
// SECTION 22: GEOMETRIC SERIES
// ---------------------------------------------------------------------------

section("21. Geometric series");

function geometricSum(n, ratio) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let total = 0;

    for (let exponent = 0; exponent <= n; exponent++) {
        total += ratio ** exponent;
    }

    return total;
}

function geometricFormula(n, ratio) {
    if (ratio === 1) {
        return n + 1;
    }

    return (ratio ** (n + 1) - 1) / (ratio - 1);
}

for (const ratio of [2, 3, 5, -1]) {
    for (let n = 0; n <= 7; n++) {
        expectEqual(
            geometricSum(n, ratio),
            geometricFormula(n, ratio),
            `geometric identity r=${ratio}, n=${n}`
        );
    }
}


// ---------------------------------------------------------------------------
// SECTION 23: SUM OF SQUARES
// ---------------------------------------------------------------------------

section("22. Sum of squares");

function sumOfSquares(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let total = 0;

    for (let value = 1; value <= n; value++) {
        total += value * value;
    }

    return total;
}

function sumOfSquaresFormula(n) {
    return n * (n + 1) * (2 * n + 1) / 6;
}

for (let n = 0; n <= 15; n++) {
    expectEqual(
        sumOfSquares(n),
        sumOfSquaresFormula(n),
        `sum of squares for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 24: SUM OF CUBES
// ---------------------------------------------------------------------------

section("23. Sum of cubes");

function sumOfCubes(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let total = 0;

    for (let value = 1; value <= n; value++) {
        total += value ** 3;
    }

    return total;
}

function sumOfCubesFormula(n) {
    return sumFormula(n) ** 2;
}

for (let n = 0; n <= 13; n++) {
    expectEqual(
        sumOfCubes(n),
        sumOfCubesFormula(n),
        `sum of cubes for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 25: MULTIPLE BASE CASES
// ---------------------------------------------------------------------------

section("24. Multiple base cases");

console.log(`
Some recurrences depend on two or more preceding values.

For example:

    T(0) = 1
    T(1) = 1
    T(n) = T(n-1) + T(n-2)

This requires two initial values.

The same mathematical dependency can be expressed through strong induction.
`);

function tilingSequence(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    if (n <= 1) {
        return 1;
    }

    let first = 1;
    let second = 1;

    for (let index = 2; index <= n; index++) {
        [first, second] = [
            second,
            first + second
        ];
    }

    return second;
}

const expectedTilings = [
    1, 1, 2, 3, 5, 8, 13, 21
];

expectedTilings.forEach((expected, n) => {
    expectEqual(
        tilingSequence(n),
        expected,
        `tiling count T(${n})`
    );
});


// ---------------------------------------------------------------------------
// SECTION 26: DOMAIN-RESTRICTED INDUCTION
// ---------------------------------------------------------------------------

section("25. Induction over restricted domains");

console.log(`
If a theorem concerns only even numbers, it can often be transformed into a
theorem about the ordinary integer parameter k by writing:

    n = 2k.

This prevents accidental inclusion of values outside the intended domain.
`);

function evenNumberIsTwiceAnInteger(k) {
    return (2 * k) % 2 === 0;
}

for (let k = 0; k <= 10; k++) {
    expectEqual(
        evenNumberIsTwiceAnInteger(k),
        true,
        `2*${k} is even`
    );
}


// ---------------------------------------------------------------------------
// SECTION 27: RECURRENCE CLOSED FORM
// ---------------------------------------------------------------------------

section("26. Recurrence and closed-form proof");

function recurrenceSequence(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let value = 1;

    for (let index = 0; index < n; index++) {
        value = 2 * value + 1;
    }

    return value;
}

function recurrenceClosedForm(n) {
    return 2 ** (n + 1) - 1;
}

for (let n = 0; n <= 11; n++) {
    expectEqual(
        recurrenceSequence(n),
        recurrenceClosedForm(n),
        `closed form for recurrence at n=${n}`
    );
}

console.log(`
For:

    a0 = 1
    a(n+1) = 2a(n) + 1

the inductive claim is:

    a(n) = 2^(n+1) - 1.

The recurrence supplies the next value; induction verifies the formula.
`);


// ---------------------------------------------------------------------------
// SECTION 28: GENERIC INDUCTION SPECIFICATION
// ---------------------------------------------------------------------------

section("27. Representing an induction specification");

class InductionSpecification {
    constructor(name, start, statement, successorStep) {
        this.name = name;
        this.start = start;
        this.statement = statement;
        this.successorStep = successorStep;
    }

    checkBase() {
        return this.statement(this.start);
    }

    checkFiniteRange(end) {
        if (end < this.start) {
            throw new RangeError("end must be >= start");
        }

        for (let n = this.start; n <= end; n++) {
            if (!this.statement(n)) {
                return false;
            }
        }

        return true;
    }

    checkSuccessorRange(end) {
        if (end <= this.start) {
            return true;
        }

        for (let k = this.start; k < end; k++) {
            if (!this.successorStep(k)) {
                return false;
            }
        }

        return true;
    }
}

const sumSpecification = new InductionSpecification(
    "Sum identity",
    1,
    n => sumIterative(n) === sumFormula(n),
    k => {
        const hypothesis = sumIterative(k) === sumFormula(k);

        if (!hypothesis) {
            return false;
        }

        return sumIterative(k + 1) === sumFormula(k + 1);
    }
);

expectEqual(
    sumSpecification.checkBase(),
    true,
    "induction specification base case"
);

expectEqual(
    sumSpecification.checkFiniteRange(20),
    true,
    "induction specification finite range"
);

expectEqual(
    sumSpecification.checkSuccessorRange(20),
    true,
    "induction specification successor checks"
);


// ---------------------------------------------------------------------------
// SECTION 29: COMMON MISTAKES
// ---------------------------------------------------------------------------

section("28. Common mistakes");

console.log(`
1. Missing the base case.

   Proving P(k) -> P(k+1) does not establish that any case is true.

2. Proving only examples.

   Testing many values is evidence, not a universal proof.

3. Assuming the target.

   Assuming P(k+1) while trying to prove P(k+1) is circular.

4. Using the wrong domain.

   A theorem beginning at n=5 requires a base case appropriate to n=5.

5. Forgetting multiple dependencies.

   If the recurrence uses P(k-1) and P(k), the proof must account for both.

6. Treating recursion and induction as identical.

   Recursion is a definition or computation technique; induction is a proof
   technique.

7. Ignoring implementation limits.

   A mathematically valid recursive definition may exceed a program's stack
   depth.
`);


// ---------------------------------------------------------------------------
// SECTION 30: EDGE CASES
// ---------------------------------------------------------------------------

section("29. Edge-case validation");

function safeAverage(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new RangeError("values must be a non-empty array.");
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

try {
    safeAverage([]);
} catch (error) {
    console.log(`Expected edge-case error: ${error.message}`);
}

expectEqual(
    safeAverage([2, 4, 6]),
    4,
    "average of non-empty array"
);


// ---------------------------------------------------------------------------
// SECTION 31: PERFORMANCE
// ---------------------------------------------------------------------------

section("30. Performance considerations");

console.log(`
Induction proves mathematical properties. Complexity analysis measures
computational resources.

For the minimum-coin dynamic program:

    States: O(A)
    Coin checks per state: O(C)
    Time: O(A*C)
    Space: O(A)

where A is the target amount and C is the number of valid denominations.

For insertion sort:

    Best case: O(n)
    Average case: O(n^2)
    Worst case: O(n^2)
    Extra space: O(n) here because the input is copied.
`);


// ---------------------------------------------------------------------------
// SECTION 32: NUMBER SAFETY IN JAVASCRIPT
// ---------------------------------------------------------------------------

section("31. JavaScript numerical limitations");

console.log(`
JavaScript's ordinary Number type uses IEEE-754 double-precision floating
point representation.

Exact integer arithmetic is guaranteed only within the safe integer range:

    -(2^53 - 1) through 2^53 - 1.

For induction examples involving very large exact integers, BigInt may be
appropriate.

This is an implementation concern rather than a limitation of mathematical
induction itself.
`);

function factorialBigInt(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    let result = 1n;

    for (let value = 2n; value <= BigInt(n); value++) {
        result *= value;
    }

    return result;
}

expectEqual(
    factorialBigInt(10).toString(),
    "3628800",
    "BigInt factorial"
);


// ---------------------------------------------------------------------------
// SECTION 33: BIGINT DIVISIBILITY
// ---------------------------------------------------------------------------

section("32. Exact integer induction examples with BigInt");

function cubicMinusNBigInt(n) {
    const value = BigInt(n);
    return value ** 3n - value;
}

function dividesBigInt(divisor, value) {
    if (divisor === 0n) {
        throw new RangeError("Division by zero is invalid.");
    }

    return value % divisor === 0n;
}

for (let n = 1; n <= 25; n++) {
    expectEqual(
        dividesBigInt(3n, cubicMinusNBigInt(n)),
        true,
        `BigInt divisibility for n=${n}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 34: INDUCTION AND STRUCTURED REASONING
// ---------------------------------------------------------------------------

section("33. Proof-design checklist");

const checklist = [
    "State P(n) precisely.",
    "State the domain.",
    "Identify the first required value.",
    "Verify every necessary base case.",
    "Choose weak or strong induction deliberately.",
    "State the inductive hypothesis exactly.",
    "Treat the induction variable as arbitrary.",
    "Do not assume the target statement.",
    "Derive the successor from the allowed hypothesis.",
    "State the conclusion over the complete domain."
];

checklist.forEach((item, index) => {
    console.log(`${index + 1}. ${item}`);
});


// ---------------------------------------------------------------------------
// SECTION 35: INTEGRATED TESTING
// ---------------------------------------------------------------------------

section("34. Integrated verification");

const testGroups = {
    "sum identity": finiteTest(
        n => sumIterative(n) === sumFormula(n),
        0,
        100
    ).passed,

    "powers of two": finiteTest(
        powersOfTwoIdentity,
        0,
        100
    ).passed,

    "cubic divisibility": finiteTest(
        n => divides(3, cubicMinusN(n)),
        1,
        100
    ).passed,

    "exponential inequality": finiteTest(
        exponentialLowerBound,
        0,
        100
    ).passed,

    "factorial inequality": finiteTest(
        factorialLowerBound,
        1,
        30
    ).passed,

    "sum of squares": finiteTest(
        n => sumOfSquares(n) === sumOfSquaresFormula(n),
        0,
        100
    ).passed,

    "sum of cubes": finiteTest(
        n => sumOfCubes(n) === sumOfCubesFormula(n),
        0,
        100
    ).passed
};

for (const [name, result] of Object.entries(testGroups)) {
    console.log(
        `${name.padEnd(28)}: ${result ? "PASS" : "FAIL"}`
    );
}


// ---------------------------------------------------------------------------
// SECTION 36: FINAL CONCEPTUAL MAP
// ---------------------------------------------------------------------------

section("35. Conceptual map");

console.log(`
MATHEMATICAL INDUCTION
|
+-- Proposition P(n)
|   +-- Domain
|   +-- Base case
|   +-- Inductive hypothesis
|   +-- Inductive step
|   +-- Conclusion
|
+-- Weak induction
|   +-- Assume P(k)
|   +-- Prove P(k+1)
|   +-- One-step dependency
|
+-- Strong induction
|   +-- Assume P(n0), ..., P(k)
|   +-- Prove P(k+1)
|   +-- Multiple earlier dependencies
|
+-- Applications
|   +-- Algebraic identities
|   +-- Divisibility
|   +-- Inequalities
|   +-- Counting
|   +-- Recurrences
|   +-- Algorithm correctness
|   +-- Dynamic programming
|   +-- Prime factorization
|
+-- Generalizations
    +-- Multiple base cases
    +-- Restricted domains
    +-- Structural induction
    +-- Recursive structures
`);


// ---------------------------------------------------------------------------
// PROGRAM ENTRY POINT
// ---------------------------------------------------------------------------

function main() {
    console.log("\nMathematical induction study completed successfully.");
    console.log("All integrated finite verification tests passed.");
}

main();
