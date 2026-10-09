/**
 * Recurrence Relations and Computational Complexity:
 * P, NP, NP-Completeness, and Polynomial-Time Reductions
 *
 * Node.js 18+.
 *
 * The JavaScript perspective emphasizes:
 * - event-driven execution
 * - immutable decision results
 * - asynchronous policy evaluation
 * - recursive versus iterative computation
 * - certificate verification
 * - a 3-SAT -> CLIQUE reduction
 * - merge eligibility as a complexity-policy example
 */

"use strict";

// -----------------------------------------------------------------------------
// Recurrence relations
// -----------------------------------------------------------------------------

function factorialRecursive(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n <= 1) return 1;
    return n * factorialRecursive(n - 1);
}

function fibonacciRecursive(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (n <= 1) return n;
    return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
}

function fibonacciMemoized(n, memo = new Map([[0, 0], [1, 1]])) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    if (memo.has(n)) return memo.get(n);

    const value =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    memo.set(n, value);
    return value;
}

function fibonacciIterative(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer");
    }

    let previous = 0;
    let current = 1;

    for (let i = 0; i < n; i++) {
        [previous, current] = [current, previous + current];
    }

    return previous;
}

// -----------------------------------------------------------------------------
// Complexity-aware algorithms
// -----------------------------------------------------------------------------

function binarySearch(sortedValues, target) {
    let low = 0;
    let high = sortedValues.length - 1;

    while (low <= high) {
        const middle = Math.floor((low + high) / 2);

        if (sortedValues[middle] === target) {
            return middle;
        }

        if (sortedValues[middle] < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }

    return -1;
}

function mergeSort(values) {
    if (values.length <= 1) {
        return [...values];
    }

    const middle = Math.floor(values.length / 2);
    const left = mergeSort(values.slice(0, middle));
    const right = mergeSort(values.slice(middle));

    const result = [];
    let i = 0;
    let j = 0;

    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) {
            result.push(left[i++]);
        } else {
            result.push(right[j++]);
        }
    }

    result.push(...left.slice(i));
    result.push(...right.slice(j));

    return result;
}

// -----------------------------------------------------------------------------
// SAT representation
// -----------------------------------------------------------------------------

class Literal {
    constructor(variable, positive = true) {
        if (typeof variable !== "string" || variable.length === 0) {
            throw new TypeError("Literal variable must be a non-empty string");
        }

        this.variable = variable;
        this.positive = positive;
        Object.freeze(this);
    }

    evaluate(assignment) {
        if (!assignment.has(this.variable)) {
            throw new Error(`Missing assignment for ${this.variable}`);
        }

        const value = assignment.get(this.variable);
        return this.positive ? value : !value;
    }

    key() {
        return `${this.positive ? "" : "¬"}${this.variable}`;
    }
}

class Clause {
    constructor(literals) {
        if (!Array.isArray(literals) || literals.length === 0) {
            throw new TypeError("A clause requires at least one literal");
        }

        this.literals = Object.freeze([...literals]);
        Object.freeze(this);
    }

    evaluate(assignment) {
        return this.literals.some(literal => literal.evaluate(assignment));
    }
}

class CNFFormula {
    constructor(variables, clauses) {
        this.variables = Object.freeze([...variables]);
        this.clauses = Object.freeze([...clauses]);
        Object.freeze(this);
    }

    evaluate(assignment) {
        const suppliedVariables = new Set(assignment.keys());

        if (
            suppliedVariables.size !== this.variables.length ||
            this.variables.some(variable => !suppliedVariables.has(variable))
        ) {
            throw new Error("Assignment does not match formula variables");
        }

        return this.clauses.every(clause => clause.evaluate(assignment));
    }
}

function* booleanAssignments(variables) {
    /*
     * Generator functions provide a memory-efficient way to enumerate
     * certificates. The generator still performs 2^n work in the worst case.
     */
    const total = 2 ** variables.length;

    for (let mask = 0; mask < total; mask++) {
        const assignment = new Map();

        for (let i = 0; i < variables.length; i++) {
            assignment.set(
                variables[i],
                Boolean(mask & (1 << i))
            );
        }

        yield assignment;
    }
}

function solveSAT(formula) {
    for (const assignment of booleanAssignments(formula.variables)) {
        if (formula.evaluate(assignment)) {
            return assignment;
        }
    }

    return null;
}

function verifySATCertificate(formula, assignment) {
    return formula.evaluate(assignment);
}

// -----------------------------------------------------------------------------
// CLIQUE
// -----------------------------------------------------------------------------

class Graph {
    constructor(vertices, edges) {
        this.vertices = new Set(vertices);
        this.edges = new Set();

        for (const [u, v] of edges) {
            if (u === v) {
                throw new Error("Simple graphs cannot contain self-loops");
            }

            if (!this.vertices.has(u) || !this.vertices.has(v)) {
                throw new Error("Edge endpoint does not exist");
            }

            this.edges.add(Graph.edgeKey(u, v));
        }
    }

    static edgeKey(u, v) {
        return u < v ? `${u}:${v}` : `${v}:${u}`;
    }

    adjacent(u, v) {
        return this.edges.has(Graph.edgeKey(u, v));
    }
}

function verifyClique(graph, candidate) {
    const vertices = [...candidate];

    if (new Set(vertices).size !== vertices.length) {
        return false;
    }

    if (vertices.some(vertex => !graph.vertices.has(vertex))) {
        return false;
    }

    for (let i = 0; i < vertices.length; i++) {
        for (let j = i + 1; j < vertices.length; j++) {
            if (!graph.adjacent(vertices[i], vertices[j])) {
                return false;
            }
        }
    }

    return true;
}

// -----------------------------------------------------------------------------
// 3-SAT -> CLIQUE reduction
// -----------------------------------------------------------------------------

function reduce3SATToClique(formula) {
    if (formula.clauses.some(clause => clause.literals.length !== 3)) {
        throw new Error("The reduction expects exactly three literals per clause");
    }

    const vertices = [];
    const edges = [];
    const metadata = new Map();

    let vertexId = 0;

    formula.clauses.forEach((clause, clauseIndex) => {
        clause.literals.forEach(literal => {
            const id = vertexId++;
            vertices.push(id);
            metadata.set(id, {
                clauseIndex,
                literal
            });
        });
    });

    for (let u = 0; u < vertices.length; u++) {
        for (let v = u + 1; v < vertices.length; v++) {
            const first = metadata.get(vertices[u]);
            const second = metadata.get(vertices[v]);

            if (first.clauseIndex === second.clauseIndex) {
                continue;
            }

            const contradictory =
                first.literal.variable === second.literal.variable &&
                first.literal.positive !== second.literal.positive;

            if (!contradictory) {
                edges.push([vertices[u], vertices[v]]);
            }
        }
    }

    return {
        graph: new Graph(vertices, edges),
        targetSize: formula.clauses.length,
        metadata
    };
}

function combinations(values, size) {
    const result = [];

    function build(start, current) {
        if (current.length === size) {
            result.push([...current]);
            return;
        }

        for (let i = start; i < values.length; i++) {
            current.push(values[i]);
            build(i + 1, current);
            current.pop();
        }
    }

    build(0, []);
    return result;
}

function findClique(reduction) {
    const candidates = combinations(
        [...reduction.graph.vertices],
        reduction.targetSize
    );

    for (const candidate of candidates) {
        if (verifyClique(reduction.graph, candidate)) {
            return candidate;
        }
    }

    return null;
}

// -----------------------------------------------------------------------------
// SUBSET SUM certificate verification
// -----------------------------------------------------------------------------

function verifySubsetSum(numbers, target, selectedIndices) {
    const seen = new Set();

    for (const index of selectedIndices) {
        if (
            !Number.isInteger(index) ||
            index < 0 ||
            index >= numbers.length ||
            seen.has(index)
        ) {
            return false;
        }

        seen.add(index);
    }

    return selectedIndices.reduce(
        (sum, index) => sum + numbers[index],
        0
    ) === target;
}

// -----------------------------------------------------------------------------
// Event-driven asynchronous complexity policy
// -----------------------------------------------------------------------------

class ComplexityPolicyEngine {
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

    async evaluateProblem(problem) {
        this.emit("evaluationStarted", problem);

        // Promise.resolve().then() places evaluation into the microtask queue,
        // making the event-driven flow explicit without external dependencies.
        const result = await Promise.resolve().then(() => {
            if (problem.type === "SAT") {
                const certificate = problem.certificate;

                return {
                    accepted: certificate instanceof Map &&
                        verifySATCertificate(problem.formula, certificate),
                    verificationClass: "polynomial-time certificate verification"
                };
            }

            if (problem.type === "CLIQUE") {
                return {
                    accepted: verifyClique(
                        problem.graph,
                        problem.certificate
                    ),
                    verificationClass: "polynomial-time certificate verification"
                };
            }

            throw new Error(`Unsupported problem type: ${problem.type}`);
        });

        this.emit("evaluationCompleted", {
            problem,
            result
        });

        return result;
    }
}

// -----------------------------------------------------------------------------
// Demonstrations
// -----------------------------------------------------------------------------

function demonstrateRecurrences() {
    console.log("\n=== Recurrence Relations ===");

    console.log("5! =", factorialRecursive(5));
    console.log("Naive Fibonacci F(10) =", fibonacciRecursive(10));
    console.log("Memoized Fibonacci F(35) =", fibonacciMemoized(35));
    console.log("Iterative Fibonacci F(35) =", fibonacciIterative(35));

    console.log(
        "Merge-sort recurrence: T(n) = 2T(n/2) + Θ(n) = Θ(n log n)"
    );
}

function demonstratePolynomialAlgorithms() {
    console.log("\n=== Polynomial-Time Algorithms ===");

    const values = Array.from({ length: 100_000 }, (_, i) => i * 2);

    console.log(
        "Binary search index:",
        binarySearch(values, 88_888)
    );

    console.log(
        "Merge sort:",
        mergeSort([42, 7, 19, 2, 31, 11, 5])
    );

    console.log(
        "Binary search performs logarithmically many comparisons because "
        + "each iteration discards roughly half of the remaining range."
    );
}

function demonstrateSAT() {
    console.log("\n=== SAT Certificate ===");

    const formula = new CNFFormula(
        ["x", "y", "z"],
        [
            new Clause([
                new Literal("x"),
                new Literal("y"),
                new Literal("z", false)
            ]),
            new Clause([
                new Literal("x", false),
                new Literal("y"),
                new Literal("z")
            ]),
            new Clause([
                new Literal("x"),
                new Literal("y", false),
                new Literal("z")
            ])
        ]
    );

    const certificate = solveSAT(formula);

    console.log(
        "SAT certificate:",
        certificate
            ? Object.fromEntries(certificate)
            : "UNSAT"
    );

    if (certificate) {
        console.log(
            "Verification result:",
            verifySATCertificate(formula, certificate)
        );
    }
}

function demonstrateCliqueAndReduction() {
    console.log("\n=== 3-SAT -> CLIQUE ===");

    const formula = new CNFFormula(
        ["a", "b", "c"],
        [
            new Clause([
                new Literal("a"),
                new Literal("b"),
                new Literal("c")
            ]),
            new Clause([
                new Literal("a", false),
                new Literal("b"),
                new Literal("c", false)
            ]),
            new Clause([
                new Literal("a"),
                new Literal("b", false),
                new Literal("c")
            ])
        ]
    );

    const reduction = reduce3SATToClique(formula);
    const clique = findClique(reduction);

    console.log(
        "Reduced graph vertices:",
        reduction.graph.vertices.size
    );

    console.log(
        "Required clique size:",
        reduction.targetSize
    );

    console.log(
        "Clique:",
        clique
    );

    if (clique) {
        console.log(
            "Clique literals:",
            clique.map(
                vertex => reduction.metadata.get(vertex).literal.key()
            )
        );
    }
}

async function demonstrateEventDrivenVerification() {
    console.log("\n=== Event-Driven Certificate Verification ===");

    const formula = new CNFFormula(
        ["p", "q"],
        [
            new Clause([
                new Literal("p"),
                new Literal("q")
            ]),
            new Clause([
                new Literal("p", false),
                new Literal("q")
            ])
        ]
    );

    const certificate = new Map([
        ["p", false],
        ["q", true]
    ]);

    const engine = new ComplexityPolicyEngine();

    engine.on("evaluationStarted", problem => {
        console.log(`Started ${problem.type} certificate verification`);
    });

    engine.on("evaluationCompleted", event => {
        console.log(
            "Completed:",
            event.result
        );
    });

    await engine.evaluateProblem({
        type: "SAT",
        formula,
        certificate
    });
}

async function main() {
    demonstrateRecurrences();
    demonstratePolynomialAlgorithms();
    demonstrateSAT();
    demonstrateCliqueAndReduction();
    await demonstrateEventDrivenVerification();

    console.log("\n=== Complexity Boundary ===");
    for (const variables of [10, 20, 30, 40]) {
        console.log(
            `${variables} Boolean variables -> ${2 ** variables} assignments`
        );
    }

    console.log(
        "\nP contains decision problems solvable in polynomial time. "
        + "NP contains decision problems whose proposed solutions can be "
        + "verified in polynomial time. NP-completeness additionally requires "
        + "NP membership and NP-hardness under polynomial-time reductions."
    );

    console.log(
        "A polynomial reduction transforms every instance of a source problem "
        + "into an equivalent instance of a target problem within polynomial time."
    );

    // Demonstrate SUBSET SUM verification separately because its certificate
    // is naturally represented by selected input positions.
    console.log(
        "SUBSET SUM certificate valid:",
        verifySubsetSum([3, 7, 11, 14, 19], 25, [1, 3])
    );
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
