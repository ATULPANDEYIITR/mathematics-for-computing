/*
 * Recurrence Proofs
 * =================
 *
 * This standalone JavaScript file demonstrates:
 *
 * - recursive definitions
 * - recurrence relations
 * - recursive algorithms
 * - induction-oriented verification
 * - strong induction
 * - structural induction
 * - recurrence expansion
 * - divide-and-conquer algorithms
 * - memoization
 * - recurrence-based complexity analysis
 * - edge cases and implementation trade-offs
 *
 * The examples run in Node.js without external packages.
 */

"use strict";

// -----------------------------------------------------------------------------
// Section 1: Recursive definitions
// -----------------------------------------------------------------------------

function factorial(n) {
    /*
     * Mathematical definition:
     *
     *   0! = 1
     *   n! = n(n-1)! for n >= 1
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("factorial requires a non-negative integer");
    }

    if (n === 0) {
        return 1;
    }

    return n * factorial(n - 1);
}


function fibonacciRecursive(n) {
    /*
     * Direct recursive definition:
     *
     *   F(0) = 0
     *   F(1) = 1
     *   F(n) = F(n-1) + F(n-2)
     *
     * The recurrence causes repeated computation.
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("Fibonacci index must be non-negative");
    }

    if (n === 0 || n === 1) {
        return n;
    }

    return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
}


function fibonacciMemoized(n, memo = new Map()) {
    /*
     * Memoization does not change the mathematical recurrence.
     * It changes the computational behavior by caching previously computed
     * subproblems.
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("Fibonacci index must be non-negative");
    }

    if (n < 2) {
        return n;
    }

    if (memo.has(n)) {
        return memo.get(n);
    }

    const value =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    memo.set(n, value);
    return value;
}


function fibonacciIterative(n) {
    /*
     * The same recurrence can be implemented iteratively.
     * Only two preceding values are required.
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("Fibonacci index must be non-negative");
    }

    let previous = 0;
    let current = 1;

    for (let index = 0; index < n; index += 1) {
        [previous, current] = [current, previous + current];
    }

    return previous;
}


// -----------------------------------------------------------------------------
// Section 2: Recursive sequences and closed forms
// -----------------------------------------------------------------------------

function arithmeticRecursive(n, first = 3, difference = 5) {
    /*
     * Recurrence:
     *
     *   a(0) = first
     *   a(n) = a(n-1) + difference
     *
     * Closed form:
     *
     *   a(n) = first + n*difference
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n === 0) {
        return first;
    }

    return arithmeticRecursive(n - 1, first, difference) + difference;
}


function arithmeticClosedForm(n, first = 3, difference = 5) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    return first + n * difference;
}


function triangularRecursive(n) {
    /*
     * Recursive definition:
     *
     *   T(0) = 0
     *   T(n) = T(n-1) + n
     *
     * Closed form:
     *
     *   T(n) = n(n+1)/2
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n === 0) {
        return 0;
    }

    return triangularRecursive(n - 1) + n;
}


function triangularClosedForm(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    return (n * (n + 1)) / 2;
}


function powerOfTwoRecursive(n) {
    /*
     * Recurrence:
     *
     *   P(0) = 1
     *   P(n) = 2P(n-1)
     *
     * Hence P(n) = 2^n.
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n === 0) {
        return 1;
    }

    return 2 * powerOfTwoRecursive(n - 1);
}


function powerOfTwoClosedForm(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    return 2 ** n;
}


// -----------------------------------------------------------------------------
// Section 3: Towers of Hanoi recurrence
// -----------------------------------------------------------------------------

function hanoiMoveCount(n) {
    /*
     * H(0) = 0
     * H(n) = 2H(n-1) + 1
     *
     * Closed form:
     * H(n) = 2^n - 1
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("number of disks must be non-negative");
    }

    if (n === 0) {
        return 0;
    }

    return 2 * hanoiMoveCount(n - 1) + 1;
}


function hanoiClosedForm(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("number of disks must be non-negative");
    }

    return 2 ** n - 1;
}


// -----------------------------------------------------------------------------
// Section 4: Recurrence expansion
// -----------------------------------------------------------------------------

function expandTriangularRecurrence(n) {
    /*
     * Expand:
     *
     *   T(n) = T(n-1) + n
     *
     * until reaching T(0).
     */
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be non-negative");
    }

    const lines = [`T(${n})`];

    if (n === 0) {
        lines.push("= 0");
        return lines;
    }

    for (let current = n; current >= 1; current -= 1) {
        const remaining = current - 1;

        if (remaining === 0) {
            lines.push(`= T(0) + ${current}`);
        } else {
            const terms = [];
            for (let value = remaining + 1; value <= n; value += 1) {
                terms.push(String(value));
            }
            lines.push(`= T(${remaining}) + ${terms.join(" + ")}`);
        }
    }

    lines.push(`= 1 + 2 + ... + ${n}`);
    lines.push(`= ${n}(${n} + 1)/2`);

    return lines;
}


// -----------------------------------------------------------------------------
// Section 5: Binary search
// -----------------------------------------------------------------------------

function binarySearchRecursive(values, target, left = 0, right = values.length - 1) {
    /*
     * Recurrence:
     *
     *   T(n) = T(n/2) + O(1)
     *
     * Therefore:
     *
     *   T(n) = O(log n)
     */
    if (left > right) {
        return -1;
    }

    const middle = left + Math.floor((right - left) / 2);

    if (values[middle] === target) {
        return middle;
    }

    if (values[middle] < target) {
        return binarySearchRecursive(values, target, middle + 1, right);
    }

    return binarySearchRecursive(values, target, left, middle - 1);
}


function binarySearchIterative(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}


// -----------------------------------------------------------------------------
// Section 6: Merge sort
// -----------------------------------------------------------------------------

function merge(left, right) {
    const result = [];
    let leftIndex = 0;
    let rightIndex = 0;

    while (leftIndex < left.length && rightIndex < right.length) {
        if (left[leftIndex] <= right[rightIndex]) {
            result.push(left[leftIndex]);
            leftIndex += 1;
        } else {
            result.push(right[rightIndex]);
            rightIndex += 1;
        }
    }

    while (leftIndex < left.length) {
        result.push(left[leftIndex]);
        leftIndex += 1;
    }

    while (rightIndex < right.length) {
        result.push(right[rightIndex]);
        rightIndex += 1;
    }

    return result;
}


function mergeSort(values) {
    /*
     * Recurrence:
     *
     *   T(n) = 2T(n/2) + O(n)
     *
     * The two recursive calls produce the subproblems, while merge() performs
     * linear work at the current level.
     *
     * Result:
     *   T(n) = O(n log n)
     */
    if (values.length <= 1) {
        return [...values];
    }

    const middle = Math.floor(values.length / 2);
    const left = mergeSort(values.slice(0, middle));
    const right = mergeSort(values.slice(middle));

    return merge(left, right);
}


// -----------------------------------------------------------------------------
// Section 7: Quicksort and recurrence dependence on partition quality
// -----------------------------------------------------------------------------

function quicksort(values) {
    /*
     * Balanced partition:
     *
     *   T(n) = 2T(n/2) + O(n)
     *   => O(n log n)
     *
     * Extremely unbalanced partition:
     *
     *   T(n) = T(n-1) + O(n)
     *   => O(n^2)
     *
     * The recurrence therefore depends on the partition structure.
     */
    const result = [...values];

    function partition(low, high) {
        const pivot = result[high];
        let smallerIndex = low - 1;

        for (let index = low; index < high; index += 1) {
            if (result[index] <= pivot) {
                smallerIndex += 1;
                [result[smallerIndex], result[index]] =
                    [result[index], result[smallerIndex]];
            }
        }

        [result[smallerIndex + 1], result[high]] =
            [result[high], result[smallerIndex + 1]];

        return smallerIndex + 1;
    }

    function sort(low, high) {
        if (low >= high) {
            return;
        }

        const pivotIndex = partition(low, high);
        sort(low, pivotIndex - 1);
        sort(pivotIndex + 1, high);
    }

    sort(0, result.length - 1);
    return result;
}


// -----------------------------------------------------------------------------
// Section 8: Induction-oriented verification
// -----------------------------------------------------------------------------

class InductionProof {
    /*
     * This class models the three useful components of a basic induction
     * argument:
     *
     * 1. Proposition P(n)
     * 2. Base case
     * 3. Inductive implication P(n) -> P(n+1)
     *
     * Finite execution can test these conditions for selected values, but
     * finite testing is not itself a proof over infinitely many integers.
     */
    constructor(name, baseCase, proposition, implication) {
        this.name = name;
        this.baseCase = baseCase;
        this.proposition = proposition;
        this.implication = implication;
    }

    verifyBaseCase() {
        return this.proposition(this.baseCase);
    }

    verifyInductiveSteps(start, limit) {
        for (let n = start; n <= limit; n += 1) {
            if (this.proposition(n) && !this.implication(n)) {
                return false;
            }
        }

        return true;
    }
}


function buildTriangularInductionProof() {
    /*
     * Proposition:
     *
     *   P(n): T(n) = n(n+1)/2
     *
     * Base:
     *
     *   T(0) = 0
     *
     * Inductive step:
     *
     *   Assume T(n) = n(n+1)/2.
     *
     *   T(n+1)
     *     = T(n) + (n+1)
     *     = n(n+1)/2 + (n+1)
     *     = (n+1)(n+2)/2
     */
    const proposition = (n) =>
        triangularRecursive(n) === triangularClosedForm(n);

    const implication = (n) => {
        const assumedValue = n * (n + 1) / 2;
        const derivedNext = assumedValue + (n + 1);
        const expectedNext = (n + 1) * (n + 2) / 2;

        return derivedNext === expectedNext;
    };

    return new InductionProof(
        "T(n) = n(n+1)/2",
        0,
        proposition,
        implication
    );
}


function verifyPowerOfTwoInduction(limit = 50) {
    /*
     * Proposition:
     *
     *   P(n): P(n) = 2^n
     *
     * The inductive transformation is:
     *
     *   P(n+1) = 2P(n)
     *           = 2(2^n)
     *           = 2^(n+1)
     */
    if (powerOfTwoRecursive(0) !== 1) {
        return false;
    }

    for (let n = 0; n < limit; n += 1) {
        const assumed = 2 ** n;
        const derived = 2 * assumed;
        const expected = 2 ** (n + 1);

        if (derived !== expected) {
            return false;
        }
    }

    return true;
}


// -----------------------------------------------------------------------------
// Section 9: Strong induction
// -----------------------------------------------------------------------------

function canComposeFromTwoAndThree(n) {
    /*
     * A recursive characterization:
     *
     *   P(n) = P(n-2) OR P(n-3)
     *
     * This naturally refers to multiple smaller values. A strong-induction
     * proof can use all previously established cases.
     */
    if (!Number.isInteger(n) || n < 0) {
        return false;
    }

    const memo = new Map([[0, true]]);

    function solve(value) {
        if (value < 0) {
            return false;
        }

        if (memo.has(value)) {
            return memo.get(value);
        }

        const result = solve(value - 2) || solve(value - 3);
        memo.set(value, result);
        return result;
    }

    return solve(n);
}


function verifyStrongInductionComposition(limit = 50) {
    for (let n = 2; n <= limit; n += 1) {
        if (!canComposeFromTwoAndThree(n)) {
            return false;
        }
    }

    return true;
}


// -----------------------------------------------------------------------------
// Section 10: Structural induction on binary trees
// -----------------------------------------------------------------------------

class TreeNode {
    constructor(value, left = null, right = null) {
        this.value = value;
        this.left = left;
        this.right = right;
    }
}


function treeSize(node) {
    /*
     * Recursive definition:
     *
     *   size(empty) = 0
     *   size(node) = 1 + size(left) + size(right)
     */
    if (node === null) {
        return 0;
    }

    return 1 + treeSize(node.left) + treeSize(node.right);
}


function treeHeight(node) {
    /*
     * Recursive definition:
     *
     *   height(empty) = 0
     *   height(node) = 1 + max(height(left), height(right))
     */
    if (node === null) {
        return 0;
    }

    return 1 + Math.max(treeHeight(node.left), treeHeight(node.right));
}


function countLeaves(node) {
    if (node === null) {
        return 0;
    }

    if (node.left === null && node.right === null) {
        return 1;
    }

    return countLeaves(node.left) + countLeaves(node.right);
}


function countInternalNodes(node) {
    if (node === null) {
        return 0;
    }

    if (node.left === null && node.right === null) {
        return 0;
    }

    return (
        1 +
        countInternalNodes(node.left) +
        countInternalNodes(node.right)
    );
}


function verifyTreeIdentity(node) {
    /*
     * Structural proposition:
     *
     *   number of nodes = number of leaves + number of internal nodes
     *
     * The proof follows the recursive structure of the tree.
     */
    return treeSize(node) === countLeaves(node) + countInternalNodes(node);
}


function createSampleTree() {
    return new TreeNode(
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
}


// -----------------------------------------------------------------------------
// Section 11: Recurrence tree
// -----------------------------------------------------------------------------

function recurrenceTreeCost(n, branchingFactor = 2, shrinkFactor = 2, work = 1) {
    /*
     * Recurrence:
     *
     *   T(n) = bT(floor(n/s)) + c
     *
     * This function literally evaluates the recurrence for small inputs.
     */
    if (n <= 1) {
        return work;
    }

    if (branchingFactor < 1) {
        throw new RangeError("branchingFactor must be positive");
    }

    if (shrinkFactor < 2) {
        throw new RangeError("shrinkFactor must be at least 2");
    }

    const smaller = Math.max(1, Math.floor(n / shrinkFactor));

    return (
        branchingFactor *
            recurrenceTreeCost(
                smaller,
                branchingFactor,
                shrinkFactor,
                work
            ) +
        work
    );
}


// -----------------------------------------------------------------------------
// Section 12: Master Theorem helper
// -----------------------------------------------------------------------------

function masterTheoremCase(a, b, d) {
    /*
     * For:
     *
     *   T(n) = aT(n/b) + Theta(n^d)
     *
     * let p = log_b(a).
     *
     * Case 1: d < p
     *   Theta(n^p)
     *
     * Case 2: d = p
     *   Theta(n^p log n)
     *
     * Case 3: d > p
     *   Theta(n^d), assuming the theorem's regularity condition.
     */
    if (!Number.isInteger(a) || a <= 0) {
        throw new RangeError("a must be a positive integer");
    }

    if (!Number.isInteger(b) || b <= 1) {
        throw new RangeError("b must be an integer greater than 1");
    }

    const p = Math.log(a) / Math.log(b);
    const epsilon = 1e-12;

    if (d < p - epsilon) {
        return `Case 1: Theta(n^${p.toFixed(4)})`;
    }

    if (Math.abs(d - p) <= epsilon) {
        return `Case 2: Theta(n^${p.toFixed(4)} log n)`;
    }

    return `Case 3: Theta(n^${d.toFixed(4)})`;
}


// -----------------------------------------------------------------------------
// Section 13: Memoization call-count experiment
// -----------------------------------------------------------------------------

function fibonacciCallCount(n) {
    let calls = 0;

    function fib(value) {
        calls += 1;

        if (value < 2) {
            return value;
        }

        return fib(value - 1) + fib(value - 2);
    }

    return {
        value: fib(n),
        calls
    };
}


function fibonacciMemoizedCallCount(n) {
    let calls = 0;
    const memo = new Map();

    function fib(value) {
        calls += 1;

        if (memo.has(value)) {
            return memo.get(value);
        }

        if (value < 2) {
            memo.set(value, value);
            return value;
        }

        const result = fib(value - 1) + fib(value - 2);
        memo.set(value, result);
        return result;
    }

    return {
        value: fib(n),
        calls
    };
}


// -----------------------------------------------------------------------------
// Section 14: Substitution-style finite verification
// -----------------------------------------------------------------------------

function mergeSortRecurrenceCost(n) {
    /*
     * Exact toy recurrence:
     *
     *   T(n) = 2T(floor(n/2)) + n
     *
     * with T(1) = 1.
     *
     * The purpose is to test a candidate asymptotic upper bound on finite
     * inputs, not to replace symbolic proof.
     */
    const memo = new Map();

    function recurrence(value) {
        if (value <= 1) {
            return 1;
        }

        if (memo.has(value)) {
            return memo.get(value);
        }

        const result =
            2 * recurrence(Math.floor(value / 2)) + value;

        memo.set(value, result);
        return result;
    }

    return recurrence(n);
}


function verifyMergeSortUpperBound(n, constant = 2) {
    const actual = mergeSortRecurrenceCost(n);
    const bound = constant * n * Math.log2(n + 1);

    return actual <= bound;
}


// -----------------------------------------------------------------------------
// Section 15: Validation and edge cases
// -----------------------------------------------------------------------------

function runEdgeCaseChecks() {
    console.assert(factorial(0) === 1);
    console.assert(fibonacciRecursive(0) === 0);
    console.assert(fibonacciRecursive(1) === 1);
    console.assert(triangularRecursive(0) === 0);
    console.assert(powerOfTwoRecursive(0) === 1);
    console.assert(hanoiMoveCount(0) === 0);

    console.assert(binarySearchIterative([], 10) === -1);
    console.assert(binarySearchRecursive([], 10) === -1);

    console.assert(JSON.stringify(mergeSort([])) === "[]");
    console.assert(JSON.stringify(mergeSort([42])) === "[42]");

    let factorialErrorObserved = false;

    try {
        factorial(-1);
    } catch (error) {
        factorialErrorObserved = error instanceof RangeError;
    }

    console.assert(factorialErrorObserved);
}


// -----------------------------------------------------------------------------
// Section 16: Cross-check recursive definitions against closed forms
// -----------------------------------------------------------------------------

function runMathematicalIdentityChecks() {
    for (let n = 0; n <= 20; n += 1) {
        console.assert(
            arithmeticRecursive(n) === arithmeticClosedForm(n)
        );

        console.assert(
            triangularRecursive(n) === triangularClosedForm(n)
        );

        console.assert(
            powerOfTwoRecursive(n) === powerOfTwoClosedForm(n)
        );

        console.assert(
            hanoiMoveCount(n) === hanoiClosedForm(n)
        );
    }

    for (let n = 0; n <= 20; n += 1) {
        console.assert(
            fibonacciRecursive(n) === fibonacciMemoized(n)
        );

        console.assert(
            fibonacciMemoized(n) === fibonacciIterative(n)
        );
    }
}


// -----------------------------------------------------------------------------
// Section 17: Algorithm correctness checks
// -----------------------------------------------------------------------------

function runAlgorithmChecks() {
    const values = [12, 3, 19, 5, 7, 1, 10, 4];
    const expected = [...values].sort((a, b) => a - b);

    console.assert(
        JSON.stringify(mergeSort(values)) === JSON.stringify(expected)
    );

    console.assert(
        JSON.stringify(quicksort(values)) === JSON.stringify(expected)
    );

    for (const target of expected) {
        const recursiveIndex = binarySearchRecursive(expected, target);
        const iterativeIndex = binarySearchIterative(expected, target);

        console.assert(expected[recursiveIndex] === target);
        console.assert(expected[iterativeIndex] === target);
    }

    console.assert(binarySearchRecursive(expected, 100) === -1);
    console.assert(binarySearchIterative(expected, 100) === -1);
}


// -----------------------------------------------------------------------------
// Section 18: Induction and structural verification
// -----------------------------------------------------------------------------

function runInductionChecks() {
    const triangularProof = buildTriangularInductionProof();

    console.assert(triangularProof.verifyBaseCase());
    console.assert(
        triangularProof.verifyInductiveSteps(0, 100)
    );

    console.assert(verifyPowerOfTwoInduction(50));
    console.assert(verifyStrongInductionComposition(100));

    const tree = createSampleTree();

    console.assert(verifyTreeIdentity(tree));
    console.assert(verifyTreeIdentity(null));
}


// -----------------------------------------------------------------------------
// Section 19: Output
// -----------------------------------------------------------------------------

function printSequenceExamples() {
    console.log("\nRECURSIVELY DEFINED SEQUENCES");
    console.log("-".repeat(72));

    for (let n = 0; n <= 7; n += 1) {
        console.log(
            `n=${String(n).padStart(2)} | ` +
            `arithmetic=${String(arithmeticRecursive(n)).padStart(4)} | ` +
            `2^n=${String(powerOfTwoRecursive(n)).padStart(4)} | ` +
            `triangular=${String(triangularRecursive(n)).padStart(3)}`
        );
    }
}


function printRecurrenceExpansion() {
    console.log("\nRECURRENCE EXPANSION");
    console.log("-".repeat(72));

    for (const line of expandTriangularRecurrence(5)) {
        console.log(line);
    }
}


function printFibonacciExperiment() {
    console.log("\nFIBONACCI CALL-COUNT EXPERIMENT");
    console.log("-".repeat(72));

    for (let n = 5; n <= 10; n += 1) {
        const naive = fibonacciCallCount(n);
        const memoized = fibonacciMemoizedCallCount(n);

        console.log(
            `n=${String(n).padStart(2)} | ` +
            `value=${String(naive.value).padStart(4)} | ` +
            `naive calls=${String(naive.calls).padStart(5)} | ` +
            `memoized calls=${String(memoized.calls).padStart(3)}`
        );
    }
}


function printAlgorithmExamples() {
    console.log("\nDIVIDE-AND-CONQUER ALGORITHMS");
    console.log("-".repeat(72));

    const values = [12, 3, 19, 5, 7, 1, 10, 4];

    console.log(`Original:    ${JSON.stringify(values)}`);
    console.log(`Merge sort:  ${JSON.stringify(mergeSort(values))}`);
    console.log(`Quicksort:   ${JSON.stringify(quicksort(values))}`);

    const sorted = [...values].sort((a, b) => a - b);

    console.log(`Search 10:   ${binarySearchIterative(sorted, 10)}`);
    console.log(
        `Search 10 recursive: ${binarySearchRecursive(sorted, 10)}`
    );
}


function printInductionExamples() {
    console.log("\nINDUCTION-BASED VERIFICATION");
    console.log("-".repeat(72));

    const proof = buildTriangularInductionProof();

    console.log(`Proposition: ${proof.name}`);
    console.log(`Base case: ${proof.verifyBaseCase()}`);
    console.log(
        `Inductive implication checked through n=100: ` +
        `${proof.verifyInductiveSteps(0, 100)}`
    );
    console.log(
        `Power-of-two induction: ${verifyPowerOfTwoInduction()}`
    );
    console.log(
        `Strong induction through 100: ` +
        `${verifyStrongInductionComposition(100)}`
    );
}


function printTreeExamples() {
    console.log("\nSTRUCTURAL INDUCTION ON A BINARY TREE");
    console.log("-".repeat(72));

    const tree = createSampleTree();

    console.log(`Tree size: ${treeSize(tree)}`);
    console.log(`Tree height: ${treeHeight(tree)}`);
    console.log(`Leaves: ${countLeaves(tree)}`);
    console.log(`Internal nodes: ${countInternalNodes(tree)}`);
    console.log(
        `Nodes = leaves + internal nodes: ${verifyTreeIdentity(tree)}`
    );
}


function printMasterTheoremExamples() {
    console.log("\nMASTER THEOREM CLASSIFICATION");
    console.log("-".repeat(72));

    const examples = [
        [1, 2, 0],
        [2, 2, 1],
        [4, 2, 1],
        [2, 4, 1]
    ];

    for (const [a, b, d] of examples) {
        console.log(
            `T(n) = ${a}T(n/${b}) + Theta(n^${d}) -> ` +
            `${masterTheoremCase(a, b, d)}`
        );
    }
}


function printRecurrenceTreeExamples() {
    console.log("\nRECURRENCE-TREE EXAMPLES");
    console.log("-".repeat(72));

    for (const n of [1, 2, 4, 8, 16]) {
        const cost = recurrenceTreeCost(n, 2, 2, 1);
        console.log(`n=${String(n).padStart(2)} -> cost=${cost}`);
    }
}


function printSubstitutionChecks() {
    console.log("\nSUBSTITUTION-STYLE FINITE CHECKS");
    console.log("-".repeat(72));

    for (const n of [2, 4, 8, 16, 32, 64]) {
        console.log(
            `n=${String(n).padStart(2)} | ` +
            `T(n) <= 2n log2(n+1): ` +
            `${verifyMergeSortUpperBound(n)}`
        );
    }
}


// -----------------------------------------------------------------------------
// Section 20: Main
// -----------------------------------------------------------------------------

function main() {
    runEdgeCaseChecks();
    runMathematicalIdentityChecks();
    runAlgorithmChecks();
    runInductionChecks();

    console.log("RECURRENCE PROOFS: EXECUTABLE STUDY PROGRAM");
    console.log("=".repeat(72));

    printSequenceExamples();
    printRecurrenceExpansion();
    printFibonacciExperiment();
    printAlgorithmExamples();
    printInductionExamples();
    printTreeExamples();
    printMasterTheoremExamples();
    printRecurrenceTreeExamples();
    printSubstitutionChecks();

    console.log("\nAll executable checks passed.");
}


main();
