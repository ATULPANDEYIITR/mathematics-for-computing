/*
 * Discrete Mathematical Structures in Computer Science
 *
 * This executable JavaScript file complements the Python implementation by
 * emphasizing JavaScript's:
 * - Set and Map objects
 * - first-class functions
 * - closures
 * - higher-order functions
 * - object-oriented modeling
 * - recursion
 * - graph algorithms
 * - asynchronous execution
 * - validation and error handling
 * - practical web/application-oriented data processing
 *
 * Run with:
 *   node discrete_mathematical_structures.js
 */

"use strict";

// ============================================================================
// 1. BASIC SET THEORY
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n--- " + title + " ---");
}

section("1. SETS");

const setA = new Set([1, 2, 3, 4]);
const setB = new Set([3, 4, 5, 6]);

function union(first, second) {
    return new Set([...first, ...second]);
}

function intersection(first, second) {
    return new Set([...first].filter(value => second.has(value)));
}

function difference(first, second) {
    return new Set([...first].filter(value => !second.has(value)));
}

function symmetricDifference(first, second) {
    return union(difference(first, second), difference(second, first));
}

function isSubset(subset, superset) {
    return [...subset].every(value => superset.has(value));
}

console.log("A =", [...setA]);
console.log("B =", [...setB]);
console.log("A ∪ B =", [...union(setA, setB)]);
console.log("A ∩ B =", [...intersection(setA, setB)]);
console.log("A - B =", [...difference(setA, setB)]);
console.log("A △ B =", [...symmetricDifference(setA, setB)]);
console.log("{1,2} ⊆ A =", isSubset(new Set([1, 2]), setA));

// Set removes duplicates automatically.
const duplicateValues = new Set([1, 1, 1, 2, 2, 3]);
console.log("Duplicate values represented as a set:", [...duplicateValues]);


// ============================================================================
// 2. POWER SET AND CARTESIAN PRODUCT
// ============================================================================

subsection("Power Set");

function powerSet(values) {
    const items = [...values];
    const result = [];

    for (let mask = 0; mask < (1 << items.length); mask++) {
        const subset = [];

        for (let index = 0; index < items.length; index++) {
            if (mask & (1 << index)) {
                subset.push(items[index]);
            }
        }

        result.push(new Set(subset));
    }

    return result;
}

const smallSet = new Set(["A", "B", "C"]);
const powers = powerSet(smallSet);

console.log(
    "Number of subsets:",
    powers.length,
    "expected:",
    2 ** smallSet.size
);

console.assert(powers.length === 2 ** smallSet.size);


subsection("Cartesian Product");

function cartesianProduct(first, second) {
    const result = [];

    for (const left of first) {
        for (const right of second) {
            result.push([left, right]);
        }
    }

    return result;
}

const product = cartesianProduct(
    new Set(["A", "B"]),
    new Set([1, 2, 3])
);

console.log("A × B =", product);


// ============================================================================
// 3. RELATIONS
// ============================================================================

section("3. RELATIONS");

function pairKey(first, second) {
    return JSON.stringify([first, second]);
}

function relationFromPairs(pairs) {
    return new Set(pairs.map(([first, second]) => pairKey(first, second)));
}

function relationContains(relation, first, second) {
    return relation.has(pairKey(first, second));
}

function isReflexive(domain, relation) {
    return [...domain].every(
        value => relationContains(relation, value, value)
    );
}

function isSymmetric(relationPairs, relation) {
    return relationPairs.every(
        ([first, second]) => relationContains(relation, second, first)
    );
}

function isAntisymmetric(relationPairs, relation) {
    return relationPairs.every(
        ([first, second]) =>
            first === second ||
            !relationContains(relation, second, first)
    );
}

function isTransitive(relationPairs, relation) {
    for (const [first, second] of relationPairs) {
        for (const [middle, last] of relationPairs) {
            if (
                second === middle &&
                !relationContains(relation, first, last)
            ) {
                return false;
            }
        }
    }

    return true;
}

const domain = new Set([1, 2, 3]);

const lessEqualPairs = [
    [1, 1],
    [1, 2],
    [1, 3],
    [2, 2],
    [2, 3],
    [3, 3]
];

const lessEqualRelation = relationFromPairs(lessEqualPairs);

console.log(
    "Reflexive:",
    isReflexive(domain, lessEqualRelation)
);

console.log(
    "Symmetric:",
    isSymmetric(lessEqualPairs, lessEqualRelation)
);

console.log(
    "Antisymmetric:",
    isAntisymmetric(lessEqualPairs, lessEqualRelation)
);

console.log(
    "Transitive:",
    isTransitive(lessEqualPairs, lessEqualRelation)
);


// ============================================================================
// 4. EQUIVALENCE RELATIONS
// ============================================================================

section("4. EQUIVALENCE RELATIONS");

function moduloRelation(values, modulus) {
    if (!Number.isInteger(modulus) || modulus <= 0) {
        throw new RangeError("Modulus must be a positive integer.");
    }

    const pairs = [];

    for (const first of values) {
        for (const second of values) {
            if (first % modulus === second % modulus) {
                pairs.push([first, second]);
            }
        }
    }

    return pairs;
}

function groupEquivalenceClasses(values, pairs) {
    const classes = new Map();

    for (const value of values) {
        const representative = pairs.find(
            ([first, second]) =>
                first === value && second === value
        );

        if (!representative) {
            continue;
        }

        const key = value % 3;

        if (!classes.has(key)) {
            classes.set(key, []);
        }

        classes.get(key).push(value);
    }

    return classes;
}

const moduloValues = new Set([0, 1, 2, 3, 4, 5, 6, 7]);
const moduloPairs = moduloRelation(moduloValues, 3);
const moduloRelationSet = relationFromPairs(moduloPairs);

console.log(
    "Modulo-3 relation is reflexive:",
    isReflexive(moduloValues, moduloRelationSet)
);

console.log(
    "Modulo-3 relation is symmetric:",
    isSymmetric(moduloPairs, moduloRelationSet)
);

console.log(
    "Modulo-3 relation is transitive:",
    isTransitive(moduloPairs, moduloRelationSet)
);

console.log(
    "Equivalence classes:",
    [...groupEquivalenceClasses(moduloValues, moduloPairs).entries()]
);


// ============================================================================
// 5. FUNCTIONS
// ============================================================================

section("5. FUNCTIONS");

function square(number) {
    return number * number;
}

const cube = number => number ** 3;

console.log("square(7) =", square(7));
console.log("cube(4) =", cube(4));


// A finite mathematical function can be represented by Map.
const finiteFunction = new Map([
    ["a", 1],
    ["b", 4],
    ["c", 9]
]);

console.log("Finite function:", [...finiteFunction.entries()]);


function isInjective(mapping) {
    const outputs = new Set(mapping.values());
    return outputs.size === mapping.size;
}

function isSurjective(mapping, codomain) {
    const image = new Set(mapping.values());

    return (
        image.size === codomain.size &&
        [...codomain].every(value => image.has(value))
    );
}

function isBijective(mapping, codomain) {
    return isInjective(mapping) && isSurjective(mapping, codomain);
}

const bijection = new Map([
    ["A", 10],
    ["B", 20],
    ["C", 30]
]);

const bijectionCodomain = new Set([10, 20, 30]);

console.log("Injective:", isInjective(bijection));
console.log(
    "Surjective:",
    isSurjective(bijection, bijectionCodomain)
);
console.log(
    "Bijective:",
    isBijective(bijection, bijectionCodomain)
);

console.assert(isBijective(bijection, bijectionCodomain));


// ============================================================================
// 6. FUNCTION COMPOSITION AND CLOSURES
// ============================================================================

section("6. COMPOSITION AND CLOSURES");

function compose(first, second) {
    return value => first(second(value));
}

const addTen = value => value + 10;
const double = value => value * 2;

const composed = compose(addTen, double);

console.log("(addTen ∘ double)(5) =", composed(5));


// Closures retain access to variables from their lexical environment.
function createMultiplier(factor) {
    return value => value * factor;
}

const multiplyByFive = createMultiplier(5);
console.log("Closure multiplyByFive(8) =", multiplyByFive(8));


// Higher-order functions accept or return functions.
const numbers = [1, 2, 3, 4, 5];

const squares = numbers.map(square);
const evenNumbers = numbers.filter(number => number % 2 === 0);
const total = numbers.reduce((sum, number) => sum + number, 0);

console.log("Squares:", squares);
console.log("Even numbers:", evenNumbers);
console.log("Sum:", total);


// ============================================================================
// 7. PROPOSITIONAL LOGIC
// ============================================================================

section("7. PROPOSITIONAL LOGIC");

function implies(p, q) {
    return !p || q;
}

function iff(p, q) {
    return p === q;
}

console.log("p=true, q=false");
console.log("p AND q:", true && false);
console.log("p OR q:", true || false);
console.log("NOT p:", !true);
console.log("p -> q:", implies(true, false));
console.log("p <-> q:", iff(true, false));


function truthTableTwoVariables(expression) {
    const table = [];

    for (const p of [false, true]) {
        for (const q of [false, true]) {
            table.push({
                p,
                q,
                result: expression(p, q)
            });
        }
    }

    return table;
}

console.table(
    truthTableTwoVariables((p, q) => implies(p, q))
);


function isTautology(expression, variableCount) {
    const totalAssignments = 2 ** variableCount;

    for (let mask = 0; mask < totalAssignments; mask++) {
        const assignment = [];

        for (let index = 0; index < variableCount; index++) {
            assignment.push(Boolean(mask & (1 << index)));
        }

        if (!expression(...assignment)) {
            return false;
        }
    }

    return true;
}

function isContradiction(expression, variableCount) {
    const totalAssignments = 2 ** variableCount;

    for (let mask = 0; mask < totalAssignments; mask++) {
        const assignment = [];

        for (let index = 0; index < variableCount; index++) {
            assignment.push(Boolean(mask & (1 << index)));
        }

        if (expression(...assignment)) {
            return false;
        }
    }

    return true;
}

const excludedMiddle = p => p || !p;
const contradiction = p => p && !p;

console.log(
    "p ∨ ¬p is tautological:",
    isTautology(excludedMiddle, 1)
);

console.log(
    "p ∧ ¬p is contradictory:",
    isContradiction(contradiction, 1)
);

console.assert(isTautology(excludedMiddle, 1));
console.assert(isContradiction(contradiction, 1));


// ============================================================================
// 8. PREDICATE LOGIC
// ============================================================================

section("8. PREDICATE LOGIC");

const integerDomain = Array.from(
    { length: 10 },
    (_, index) => index + 1
);

const positive = value => value > 0;
const even = value => value % 2 === 0;

console.log(
    "∀x positive:",
    integerDomain.every(positive)
);

console.log(
    "∃x even:",
    integerDomain.some(even)
);

console.log(
    "Even witnesses:",
    integerDomain.filter(even)
);


// ============================================================================
// 9. BOOLEAN ALGEBRA
// ============================================================================

section("9. BOOLEAN ALGEBRA");

function distributiveLeft(p, q, r) {
    return (p && q) || (p && r);
}

function distributiveRight(p, q, r) {
    return p && (q || r);
}

for (const p of [false, true]) {
    for (const q of [false, true]) {
        for (const r of [false, true]) {
            console.assert(
                distributiveLeft(p, q, r) ===
                distributiveRight(p, q, r)
            );
        }
    }
}

console.log("Boolean distributive law verified.");


// ============================================================================
// 10. RECURSION AND MEMOIZATION
// ============================================================================

section("10. RECURSION");

function factorial(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError(
            "Factorial requires a non-negative integer."
        );
    }

    if (number === 0) {
        return 1;
    }

    return number * factorial(number - 1);
}

console.log("5! =", factorial(5));


// Naive recursion repeats work.
function fibonacciNaive(index) {
    if (!Number.isInteger(index) || index < 0) {
        throw new RangeError(
            "Fibonacci index must be a non-negative integer."
        );
    }

    if (index <= 1) {
        return index;
    }

    return (
        fibonacciNaive(index - 1) +
        fibonacciNaive(index - 2)
    );
}


// Memoization stores previously calculated results.
function fibonacciMemoized() {
    const cache = new Map([
        [0, 0],
        [1, 1]
    ]);

    function calculate(index) {
        if (cache.has(index)) {
            return cache.get(index);
        }

        const value =
            calculate(index - 1) +
            calculate(index - 2);

        cache.set(index, value);
        return value;
    }

    return calculate;
}

const fibonacciFast = fibonacciMemoized();

console.log(
    "Naive Fibonacci sequence:",
    Array.from({ length: 10 }, (_, i) => fibonacciNaive(i))
);

console.log(
    "Memoized Fibonacci(40):",
    fibonacciFast(40)
);


// ============================================================================
// 11. GRAPH THEORY
// ============================================================================

section("11. GRAPH THEORY");

class Graph {
    constructor() {
        // Map gives explicit adjacency-list representation.
        this.adjacency = new Map();
    }

    addVertex(vertex) {
        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, new Set());
        }
    }

    addUndirectedEdge(first, second) {
        this.addVertex(first);
        this.addVertex(second);

        this.adjacency.get(first).add(second);
        this.adjacency.get(second).add(first);
    }

    neighbors(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }

        return this.adjacency.get(vertex);
    }

    bfs(start) {
        if (!this.adjacency.has(start)) {
            throw new Error(`Unknown vertex: ${start}`);
        }

        const queue = [start];
        let queueIndex = 0;
        const visited = new Set([start]);
        const order = [];

        while (queueIndex < queue.length) {
            const current = queue[queueIndex++];
            order.push(current);

            for (const neighbor of this.neighbors(current)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return order;
    }

    dfs(start) {
        if (!this.adjacency.has(start)) {
            throw new Error(`Unknown vertex: ${start}`);
        }

        const stack = [start];
        const visited = new Set();
        const order = [];

        while (stack.length > 0) {
            const current = stack.pop();

            if (visited.has(current)) {
                continue;
            }

            visited.add(current);
            order.push(current);

            for (const neighbor of this.neighbors(current)) {
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }

        return order;
    }
}

const graph = new Graph();

[
    ["A", "B"],
    ["A", "C"],
    ["B", "D"],
    ["C", "D"],
    ["D", "E"]
].forEach(([first, second]) => {
    graph.addUndirectedEdge(first, second);
});

console.log("BFS:", graph.bfs("A"));
console.log("DFS:", graph.dfs("A"));


// ============================================================================
// 12. TOPOLOGICAL SORT
// ============================================================================

section("12. TOPOLOGICAL ORDERING");

function topologicalSort(vertices, edges) {
    const adjacency = new Map();
    const indegree = new Map();

    for (const vertex of vertices) {
        adjacency.set(vertex, []);
        indegree.set(vertex, 0);
    }

    for (const [source, target] of edges) {
        if (!adjacency.has(source) || !adjacency.has(target)) {
            throw new Error("Edge references an unknown vertex.");
        }

        adjacency.get(source).push(target);
        indegree.set(target, indegree.get(target) + 1);
    }

    const queue = [];

    for (const [vertex, degree] of indegree) {
        if (degree === 0) {
            queue.push(vertex);
        }
    }

    const result = [];

    while (queue.length > 0) {
        const current = queue.shift();
        result.push(current);

        for (const neighbor of adjacency.get(current)) {
            indegree.set(
                neighbor,
                indegree.get(neighbor) - 1
            );

            if (indegree.get(neighbor) === 0) {
                queue.push(neighbor);
            }
        }
    }

    if (result.length !== vertices.length) {
        throw new Error("Directed graph contains a cycle.");
    }

    return result;
}

const courseVertices = [
    "Sets",
    "Relations",
    "Logic",
    "Algorithms",
    "Databases"
];

const courseEdges = [
    ["Sets", "Relations"],
    ["Relations", "Databases"],
    ["Logic", "Algorithms"],
    ["Algorithms", "Databases"]
];

console.log(
    "Course dependency order:",
    topologicalSort(courseVertices, courseEdges)
);


// ============================================================================
// 13. OBJECT-ORIENTED MATHEMATICAL STRUCTURE
// ============================================================================

section("13. OBJECT-ORIENTED MODELING");

class FiniteFunction {
    constructor(mapping, codomain) {
        if (!(mapping instanceof Map)) {
            throw new TypeError("Mapping must be a Map.");
        }

        if (!(codomain instanceof Set)) {
            throw new TypeError("Codomain must be a Set.");
        }

        this.mapping = mapping;
        this.codomain = codomain;
    }

    isInjective() {
        return new Set(this.mapping.values()).size === this.mapping.size;
    }

    isSurjective() {
        const image = new Set(this.mapping.values());

        return (
            image.size === this.codomain.size &&
            [...this.codomain].every(value => image.has(value))
        );
    }

    isBijective() {
        return this.isInjective() && this.isSurjective();
    }

    inverse() {
        if (!this.isBijective()) {
            throw new Error(
                "An inverse function requires a bijection."
            );
        }

        const inverseMap = new Map();

        for (const [input, output] of this.mapping) {
            inverseMap.set(output, input);
        }

        return inverseMap;
    }
}

const finiteBijection = new FiniteFunction(
    new Map([
        ["x", 10],
        ["y", 20],
        ["z", 30]
    ]),
    new Set([10, 20, 30])
);

console.log("Injective:", finiteBijection.isInjective());
console.log("Surjective:", finiteBijection.isSurjective());
console.log("Bijective:", finiteBijection.isBijective());
console.log("Inverse:", [
    ...finiteBijection.inverse().entries()
]);


// ============================================================================
// 14. COUNTING
// ============================================================================

section("14. COUNTING");

function factorialIterative(number) {
    if (!Number.isInteger(number) || number < 0) {
        throw new RangeError("Invalid factorial input.");
    }

    let result = 1;

    for (let i = 2; i <= number; i++) {
        result *= i;
    }

    return result;
}

function permutationCount(n, r) {
    if (
        !Number.isInteger(n) ||
        !Number.isInteger(r) ||
        n < 0 ||
        r < 0 ||
        r > n
    ) {
        throw new RangeError(
            "Require n >= 0 and 0 <= r <= n."
        );
    }

    return factorialIterative(n) /
        factorialIterative(n - r);
}

function combinationCount(n, r) {
    if (
        !Number.isInteger(n) ||
        !Number.isInteger(r) ||
        n < 0 ||
        r < 0 ||
        r > n
    ) {
        throw new RangeError(
            "Require n >= 0 and 0 <= r <= n."
        );
    }

    return permutationCount(n, r) /
        factorialIterative(r);
}

console.log("P(5,2) =", permutationCount(5, 2));
console.log("C(5,2) =", combinationCount(5, 2));


// ============================================================================
// 15. DATABASE RELATIONS
// ============================================================================

section("15. DATABASE RELATIONS");

const students = new Map([
    ["S01", { name: "Atul", department: "CS" }],
    ["S02", { name: "Mira", department: "Math" }],
    ["S03", { name: "Ravi", department: "CS" }]
]);

const courses = new Map([
    ["C01", "Algorithms"],
    ["C02", "Logic"],
    ["C03", "Databases"]
]);

const enrollments = [
    ["S01", "C01"],
    ["S01", "C03"],
    ["S02", "C02"],
    ["S03", "C01"]
];

function validateEnrollments(
    studentTable,
    courseTable,
    enrollmentRelation
) {
    return enrollmentRelation.every(
        ([studentId, courseId]) =>
            studentTable.has(studentId) &&
            courseTable.has(courseId)
    );
}

console.log(
    "Foreign-key relation valid:",
    validateEnrollments(
        students,
        courses,
        enrollments
    )
);


// ============================================================================
// 16. ASYNCHRONOUS LOGIC AND STATE TRANSITIONS
// ============================================================================

section("16. ASYNCHRONOUS STATE TRANSITIONS");

/*
 * JavaScript applications often model real systems where state changes occur
 * asynchronously. The mathematical structure is still a relation:
 *
 * currentState -> nextState
 *
 * Only permitted transitions are accepted.
 */

const allowedTransitions = new Map([
    ["created", new Set(["queued", "cancelled"])],
    ["queued", new Set(["processing", "cancelled"])],
    ["processing", new Set(["completed", "failed"])],
    ["failed", new Set(["queued"])],
    ["completed", new Set()],
    ["cancelled", new Set()]
]);

function canTransition(from, to) {
    if (!allowedTransitions.has(from)) {
        throw new Error(`Unknown state: ${from}`);
    }

    return allowedTransitions.get(from).has(to);
}

async function transition(currentState, nextState) {
    await Promise.resolve();

    if (!canTransition(currentState, nextState)) {
        throw new Error(
            `Invalid transition: ${currentState} -> ${nextState}`
        );
    }

    return nextState;
}

async function runStateMachine() {
    let state = "created";

    state = await transition(state, "queued");
    state = await transition(state, "processing");
    state = await transition(state, "completed");

    console.log("Final state:", state);

    try {
        await transition(state, "processing");
    } catch (error) {
        console.log("Expected transition error:", error.message);
    }
}


// ============================================================================
// 17. SECURITY-RELEVANT LOGIC MODEL
// ============================================================================

section("17. SECURITY POLICY AS LOGIC");

function accessAllowed(user) {
    /*
     * The rule is:
     *
     * authenticated AND accountActive AND
     * requestedPermission belongs to effectivePermissions
     *
     * This is a direct application of predicate and propositional logic.
     */
    return (
        user.authenticated === true &&
        user.accountActive === true &&
        user.permissions.has(user.requestedPermission)
    );
}

const users = [
    {
        name: "Alice",
        authenticated: true,
        accountActive: true,
        requestedPermission: "delete",
        permissions: new Set(["read", "write", "delete"])
    },
    {
        name: "Bob",
        authenticated: true,
        accountActive: true,
        requestedPermission: "delete",
        permissions: new Set(["read", "write"])
    },
    {
        name: "Carol",
        authenticated: false,
        accountActive: true,
        requestedPermission: "read",
        permissions: new Set(["read"])
    }
];

for (const user of users) {
    console.log(
        user.name,
        "access:",
        accessAllowed(user)
    );
}


// ============================================================================
// 18. PERFORMANCE COMPARISON
// ============================================================================

section("18. PERFORMANCE CONSIDERATIONS");

function findWithArray(values, target) {
    return values.includes(target);
}

function findWithSet(values, target) {
    return values.has(target);
}

const largeArray = Array.from(
    { length: 100000 },
    (_, index) => index
);

const largeSet = new Set(largeArray);

console.time("Array membership");
for (let i = 0; i < 1000; i++) {
    findWithArray(largeArray, 99999);
}
console.timeEnd("Array membership");

console.time("Set membership");
for (let i = 0; i < 1000; i++) {
    findWithSet(largeSet, 99999);
}
console.timeEnd("Set membership");

console.log(
    "Set membership is typically O(1) average-case, while array search is O(n)."
);


// ============================================================================
// 19. EDGE CASES
// ============================================================================

section("19. EDGE CASES");

try {
    factorial(-1);
} catch (error) {
    console.log("Expected factorial error:", error.message);
}

try {
    const nonBijection = new FiniteFunction(
        new Map([
            ["a", 1],
            ["b", 1]
        ]),
        new Set([1])
    );

    nonBijection.inverse();
} catch (error) {
    console.log("Expected inverse error:", error.message);
}

try {
    topologicalSort(
        ["A", "B"],
        [
            ["A", "B"],
            ["B", "A"]
        ]
    );
} catch (error) {
    console.log("Expected cycle error:", error.message);
}


// ============================================================================
// 20. EXECUTABLE ASSERTIONS
// ============================================================================

section("20. VALIDATION TESTS");

console.assert(
    [...union(new Set([1, 2]), new Set([2, 3]))]
        .sort()
        .join(",") === "1,2,3"
);

console.assert(
    [...intersection(new Set([1, 2]), new Set([2, 3]))]
        .join(",") === "2"
);

console.assert(
    isSubset(
        new Set([1, 2]),
        new Set([1, 2, 3])
    )
);

console.assert(
    isTautology(
        p => p || !p,
        1
    )
);

console.assert(
    isContradiction(
        p => p && !p,
        1
);

console.assert(factorial(5) === 120);
console.assert(fibonacciFast(10) === 55);
console.assert(combinationCount(5, 2) === 10);

console.log("Synchronous validation tests passed.");


// The asynchronous section is intentionally executed at the end.
runStateMachine()
    .then(() => {
        console.log("\nAll discrete-structure demonstrations completed.");
    })
    .catch(error => {
        console.error("Unexpected asynchronous error:", error);
        process.exitCode = 1;
    });
