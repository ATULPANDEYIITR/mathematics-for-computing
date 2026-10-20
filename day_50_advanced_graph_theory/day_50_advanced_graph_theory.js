"use strict";

/*
 * Advanced Graph Theory:
 * Planarity, graph isomorphism, graph minors, and extremal concepts.
 *
 * Executable with Node.js 18+.
 */

class Graph {
    constructor(vertices = []) {
        this.vertices = new Set(vertices);
        this.adjacency = new Map();

        for (const vertex of this.vertices) {
            this.adjacency.set(vertex, new Set());
        }
    }

    addVertex(vertex) {
        if (!this.vertices.has(vertex)) {
            this.vertices.add(vertex);
            this.adjacency.set(vertex, new Set());
        }
    }

    addEdge(u, v) {
        if (u === v) {
            throw new Error("Self-loops are not allowed in simple graphs.");
        }

        this.addVertex(u);
        this.addVertex(v);
        this.adjacency.get(u).add(v);
        this.adjacency.get(v).add(u);
    }

    removeEdge(u, v) {
        this.adjacency.get(u)?.delete(v);
        this.adjacency.get(v)?.delete(u);
    }

    hasEdge(u, v) {
        return this.adjacency.get(u)?.has(v) ?? false;
    }

    degree(vertex) {
        const neighbors = this.adjacency.get(vertex);
        if (!neighbors) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }
        return neighbors.size;
    }

    edges() {
        const result = [];
        const seen = new Set();

        for (const u of this.vertices) {
            for (const v of this.adjacency.get(u)) {
                const key = [u, v].sort().join("\0");
                if (!seen.has(key)) {
                    seen.add(key);
                    result.push([u, v]);
                }
            }
        }

        return result;
    }

    copy() {
        const result = new Graph(this.vertices);

        for (const [u, v] of this.edges()) {
            result.addEdge(u, v);
        }

        return result;
    }

    contractEdge(u, v) {
        if (!this.hasEdge(u, v)) {
            throw new Error(`Cannot contract absent edge ${u}-${v}.`);
        }

        const result = this.copy();
        const merged = `(${u}+${v})`;
        const neighbors = new Set([
            ...result.adjacency.get(u),
            ...result.adjacency.get(v)
        ]);

        neighbors.delete(u);
        neighbors.delete(v);

        result.adjacency.delete(u);
        result.adjacency.delete(v);
        result.vertices.delete(u);
        result.vertices.delete(v);

        for (const neighbor of result.vertices) {
            result.adjacency.get(neighbor).delete(u);
            result.adjacency.get(neighbor).delete(v);
        }

        result.addVertex(merged);

        for (const neighbor of neighbors) {
            if (neighbor !== merged) {
                result.addEdge(merged, neighbor);
            }
        }

        return result;
    }
}

function completeGraph(n) {
    if (!Number.isInteger(n) || n < 0) {
        throw new Error("n must be a non-negative integer.");
    }

    const graph = new Graph(
        Array.from({ length: n }, (_, i) => String(i))
    );

    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            graph.addEdge(String(i), String(j));
        }
    }

    return graph;
}

function completeBipartiteGraph(left, right) {
    if (!Number.isInteger(left) || !Number.isInteger(right) ||
        left < 1 || right < 1) {
        throw new Error("Partition sizes must be positive integers.");
    }

    const graph = new Graph();

    for (let i = 0; i < left; i++) {
        graph.addVertex(`L${i}`);
    }

    for (let j = 0; j < right; j++) {
        graph.addVertex(`R${j}`);
    }

    for (let i = 0; i < left; i++) {
        for (let j = 0; j < right; j++) {
            graph.addEdge(`L${i}`, `R${j}`);
        }
    }

    return graph;
}

function cycleGraph(n) {
    if (n < 3) {
        throw new Error("A simple cycle requires at least three vertices.");
    }

    const graph = new Graph(
        Array.from({ length: n }, (_, i) => String(i))
    );

    for (let i = 0; i < n; i++) {
        graph.addEdge(String(i), String((i + 1) % n));
    }

    return graph;
}

function degreeSignature(graph) {
    return [...graph.vertices]
        .map(vertex => graph.degree(vertex))
        .sort((a, b) => b - a)
        .join(",");
}

function areIsomorphic(first, second) {
    if (first.vertices.size !== second.vertices.size) return false;
    if (first.edges().length !== second.edges().length) return false;
    if (degreeSignature(first) !== degreeSignature(second)) return false;

    const firstVertices = [...first.vertices].sort(
        (a, b) => secondDegreePriority(first, b) - secondDegreePriority(first, a)
    );

    const candidatesByDegree = new Map();

    for (const vertex of second.vertices) {
        const degree = second.degree(vertex);

        if (!candidatesByDegree.has(degree)) {
            candidatesByDegree.set(degree, []);
        }

        candidatesByDegree.get(degree).push(vertex);
    }

    const mapping = new Map();
    const used = new Set();

    function secondDegreePriority(graph, vertex) {
        return graph.degree(vertex);
    }

    function compatible(u, candidate) {
        for (const [mappedU, mappedV] of mapping.entries()) {
            if (
                first.hasEdge(u, mappedU) !==
                second.hasEdge(candidate, mappedV)
            ) {
                return false;
            }
        }

        return true;
    }

    function search(index) {
        if (index === firstVertices.length) {
            return true;
        }

        const u = firstVertices[index];
        const candidates = candidatesByDegree.get(first.degree(u)) ?? [];

        for (const candidate of candidates) {
            if (used.has(candidate)) continue;
            if (!compatible(u, candidate)) continue;

            mapping.set(u, candidate);
            used.add(candidate);

            if (search(index + 1)) {
                return true;
            }

            used.delete(candidate);
            mapping.delete(u);
        }

        return false;
    }

    return search(0);
}

function isBipartite(graph) {
    const color = new Map();

    for (const source of graph.vertices) {
        if (color.has(source)) continue;

        color.set(source, 0);
        const queue = [source];

        while (queue.length > 0) {
            const current = queue.shift();

            for (const neighbor of graph.adjacency.get(current)) {
                if (!color.has(neighbor)) {
                    color.set(neighbor, 1 - color.get(current));
                    queue.push(neighbor);
                } else if (color.get(neighbor) === color.get(current)) {
                    return false;
                }
            }
        }
    }

    return true;
}

function eulerPlanarBound(graph) {
    const n = graph.vertices.size;
    const m = graph.edges().length;

    return n < 3 || m <= 3 * n - 6;
}

function bipartitePlanarBound(graph) {
    const n = graph.vertices.size;
    const m = graph.edges().length;

    return n < 3 || !isBipartite(graph) || m <= 2 * n - 4;
}

function hasK5Subgraph(graph) {
    const vertices = [...graph.vertices];

    for (let a = 0; a < vertices.length; a++) {
        for (let b = a + 1; b < vertices.length; b++) {
            for (let c = b + 1; c < vertices.length; c++) {
                for (let d = c + 1; d < vertices.length; d++) {
                    for (let e = d + 1; e < vertices.length; e++) {
                        const selected = [
                            vertices[a], vertices[b], vertices[c],
                            vertices[d], vertices[e]
                        ];

                        let complete = true;

                        for (let i = 0; i < selected.length; i++) {
                            for (let j = i + 1; j < selected.length; j++) {
                                if (!graph.hasEdge(selected[i], selected[j])) {
                                    complete = false;
                                }
                            }
                        }

                        if (complete) return true;
                    }
                }
            }
        }
    }

    return false;
}

function planarityAssessment(graph) {
    if (graph.vertices.size <= 4) {
        return {
            planar: true,
            reason: "Every simple graph with at most four vertices is planar."
        };
    }

    if (!eulerPlanarBound(graph)) {
        return {
            planar: false,
            reason: "The graph violates m <= 3n - 6."
        };
    }

    if (!bipartitePlanarBound(graph)) {
        return {
            planar: false,
            reason: "The bipartite graph violates m <= 2n - 4."
        };
    }

    if (hasK5Subgraph(graph)) {
        return {
            planar: false,
            reason: "The graph contains K5 as a subgraph."
        };
    }

    return {
        planar: null,
        reason:
            "Necessary bounds pass and no K5 certificate was found; " +
            "a general planarity algorithm is required for an exact result."
    };
}

class GraphPolicyEngine {
    constructor() {
        this.listeners = new Set();
        this.queue = [];
    }

    on(eventName, listener) {
        this.listeners.add({ eventName, listener });
        return () => {
            for (const item of this.listeners) {
                if (item.eventName === eventName && item.listener === listener) {
                    this.listeners.delete(item);
                }
            }
        };
    }

    emit(eventName, payload) {
        for (const item of this.listeners) {
            if (item.eventName === eventName) {
                item.listener(payload);
            }
        }
    }

    enqueue(operation) {
        if (typeof operation !== "function") {
            throw new TypeError("Queued operation must be callable.");
        }

        this.queue.push(operation);
    }

    async process() {
        while (this.queue.length > 0) {
            const operation = this.queue.shift();

            try {
                const result = await operation();
                this.emit("completed", result);
            } catch (error) {
                this.emit("failed", error);
            }
        }
    }
}

async function main() {
    const cycle = cycleGraph(5);
    const k5 = completeGraph(5);
    const k33 = completeBipartiteGraph(3, 3);

    console.log("Advanced Graph Theory");
    console.log("=====================");
    console.log();

    console.log("Graph isomorphism");
    console.log("-----------------");

    const renamedCycle = new Graph(["A", "B", "C", "D", "E"]);
    for (const [u, v] of [
        ["A", "C"],
        ["C", "E"],
        ["E", "B"],
        ["B", "D"],
        ["D", "A"]
    ]) {
        renamedCycle.addEdge(u, v);
    }

    console.log(
        "C5 and renamed C5 are isomorphic:",
        areIsomorphic(cycle, renamedCycle)
    );

    console.log();
    console.log("Planarity evidence");
    console.log("------------------");

    for (const [name, graph] of [
        ["C5", cycle],
        ["K5", k5],
        ["K3,3", k33]
    ]) {
        console.log(name, planarityAssessment(graph));
    }

    console.log();
    console.log("Minor operation");
    console.log("---------------");

    const dense = completeGraph(6);
    const contracted = dense.contractEdge("0", "1");

    console.log(
        "K6 vertices:",
        dense.vertices.size,
        "edges:",
        dense.edges().length
    );

    console.log(
        "After contracting 0-1, vertices:",
        contracted.vertices.size,
        "edges:",
        contracted.edges().length
    );

    console.log();
    console.log("Extremal bounds");
    console.log("---------------");

    for (let n = 3; n <= 8; n++) {
        const completeEdges = n * (n - 1) / 2;
        const planarBound = 3 * n - 6;

        console.log(
            `n=${n}: complete=${completeEdges}, planar simple-graph bound=${planarBound}`
        );
    }

    console.log();
    console.log("Event-driven graph analysis");
    console.log("---------------------------");

    const engine = new GraphPolicyEngine();

    engine.on("completed", result => {
        console.log("Analysis completed:", result);
    });

    engine.on("failed", error => {
        console.error("Analysis failed:", error.message);
    });

    engine.enqueue(async () => ({
        graph: "K3,3",
        bipartite: isBipartite(k33),
        edgeCount: k33.edges().length,
        planarNecessaryBound: bipartitePlanarBound(k33)
    }));

    engine.enqueue(async () => {
        if (k5.edges().length < 0) {
            throw new Error("Impossible graph state.");
        }

        return {
            graph: "K5",
            assessment: planarityAssessment(k5)
        };
    });

    await engine.process();

    console.log();
    console.log("Complexity and scope");
    console.log("--------------------");
    console.log("* Adjacency sets provide efficient edge membership.");
    console.log("* Exact isomorphism backtracking is exponential in the worst case.");
    console.log("* Brute-force subgraph detection is combinatorial.");
    console.log("* Edge contraction is polynomial for one operation.");
    console.log("* Euler bounds are necessary conditions, not a complete planarity test.");
    console.log("* Production graph systems should use a dedicated linear-time planarity algorithm.");
}

main().catch(error => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
