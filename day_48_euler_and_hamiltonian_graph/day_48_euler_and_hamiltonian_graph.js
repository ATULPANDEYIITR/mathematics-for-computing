"use strict";

/*
 * Euler and Hamiltonian graph analysis using JavaScript.
 * Run with Node.js 18+.
 *
 * Euler algorithms operate on edges; Hamiltonian algorithms operate on
 * vertices. The distinction is fundamental to the implementations below.
 */

class UndirectedGraph {
    constructor(vertices, edges) {
        if (new Set(vertices).size !== vertices.length) {
            throw new Error("Vertex identifiers must be unique.");
        }

        this.vertices = [...vertices];
        this.adjacency = new Map(vertices.map(v => [v, []]));
        this.edges = [];

        const edgeKeys = new Set();

        for (const [u, v] of edges) {
            if (!this.adjacency.has(u) || !this.adjacency.has(v)) {
                throw new Error(`Unknown vertex in edge ${u}-${v}.`);
            }
            if (u === v) {
                throw new Error("Self-loops are not supported.");
            }

            // Canonical edge keys make duplicate detection independent
            // of the endpoint order in this undirected graph.
            const key = JSON.stringify([u, v].sort());
            if (edgeKeys.has(key)) {
                throw new Error(`Duplicate undirected edge ${u}-${v}.`);
            }

            edgeKeys.add(key);
            this.edges.push([u, v]);
            this.adjacency.get(u).push(v);
            this.adjacency.get(v).push(u);
        }
    }

    degree(vertex) {
        this.assertVertex(vertex);
        return this.adjacency.get(vertex).length;
    }

    assertVertex(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }
    }

    connectedIgnoringIsolated() {
        const active = this.vertices.filter(v => this.degree(v) > 0);
        if (active.length === 0) return true;

        const visited = new Set();
        const stack = [active[0]];

        while (stack.length > 0) {
            const u = stack.pop();
            if (visited.has(u)) continue;
            visited.add(u);

            for (const v of this.adjacency.get(u)) {
                if (!visited.has(v)) stack.push(v);
            }
        }

        return active.every(v => visited.has(v));
    }

    hasEulerTrail() {
        if (!this.connectedIgnoringIsolated()) return false;
        const oddCount = this.vertices.filter(v => this.degree(v) % 2).length;
        return oddCount === 0 || oddCount === 2;
    }

    hasEulerCircuit() {
        return (
            this.connectedIgnoringIsolated() &&
            this.vertices.every(v => this.degree(v) % 2 === 0)
        );
    }

    eulerTrail() {
        if (!this.hasEulerTrail()) return null;
        if (this.edges.length === 0) return this.vertices.slice(0, 1);

        const odd = this.vertices.filter(v => this.degree(v) % 2);
        const start = odd.length ? odd[0] :
            this.vertices.find(v => this.degree(v) > 0);

        // Store edge indices, not just neighbor vertices. This guarantees
        // that every edge is used exactly once.
        const indexed = new Map(this.vertices.map(v => [v, []]));
        this.edges.forEach(([u, v], id) => {
            indexed.get(u).push([v, id]);
            indexed.get(v).push([u, id]);
        });

        const used = new Set();
        const stack = [start];
        const result = [];

        while (stack.length) {
            const u = stack[stack.length - 1];
            const list = indexed.get(u);

            while (list.length && used.has(list[list.length - 1][1])) {
                list.pop();
            }

            if (!list.length) {
                result.push(stack.pop());
            } else {
                const [v, edgeId] = list.pop();
                if (!used.has(edgeId)) {
                    used.add(edgeId);
                    stack.push(v);
                }
            }
        }

        return used.size === this.edges.length ? result.reverse() : null;
    }

    isHamiltonianPath(path) {
        if (!Array.isArray(path) || path.length !== this.vertices.length) {
            return false;
        }
        if (new Set(path).size !== path.length) return false;
        if (!this.vertices.every(v => path.includes(v))) return false;

        return path.slice(1).every((v, i) =>
            this.adjacency.get(path[i]).includes(v)
        );
    }

    isHamiltonianCycle(cycle) {
        if (this.vertices.length < 3 || !this.isHamiltonianPath(cycle)) {
            return false;
        }
        return this.adjacency.get(cycle[cycle.length - 1]).includes(cycle[0]);
    }

    findHamiltonianPath() {
        if (this.vertices.length === 0) return [];

        const path = [];
        const visited = new Set();

        const search = u => {
            path.push(u);
            visited.add(u);

            if (path.length === this.vertices.length) return true;

            for (const v of this.adjacency.get(u)) {
                if (!visited.has(v) && search(v)) return true;
            }

            visited.delete(u);
            path.pop();
            return false;
        };

        for (const start of this.vertices) {
            if (search(start)) return path.slice();
        }
        return null;
    }

    findHamiltonianCycle() {
        if (this.vertices.length < 3) return null;

        // Fixing the first vertex removes equivalent cycle rotations.
        const start = this.vertices[0];
        const path = [start];
        const visited = new Set([start]);

        const search = u => {
            if (path.length === this.vertices.length) {
                return this.adjacency.get(u).includes(start);
            }

            for (const v of this.adjacency.get(u)) {
                if (visited.has(v)) continue;

                visited.add(v);
                path.push(v);
                if (search(v)) return true;
                path.pop();
                visited.delete(v);
            }
            return false;
        };

        return search(start) ? path.slice() : null;
    }
}

function verifyEulerTrail(graph, trail) {
    if (trail === null) return false;
    if (graph.edges.length === 0) return trail.length <= 1;

    const remaining = new Map();
    graph.edges.forEach(([u, v]) => {
        const key = JSON.stringify([u, v].sort());
        remaining.set(key, (remaining.get(key) || 0) + 1);
    });

    if (trail.length !== graph.edges.length + 1) return false;

    for (let i = 0; i < trail.length - 1; i++) {
        const key = JSON.stringify([trail[i], trail[i + 1]].sort());
        const count = remaining.get(key) || 0;
        if (count === 0) return false;
        remaining.set(key, count - 1);
    }

    return [...remaining.values()].every(count => count === 0);
}

function reportGraph(name, graph) {
    console.log(`\n${name}`);
    console.log("Degrees:", Object.fromEntries(
        graph.vertices.map(v => [v, graph.degree(v)])
    ));
    console.log("Euler trail:", graph.eulerTrail());
    console.log("Euler circuit exists:", graph.hasEulerCircuit());
    console.log("Hamiltonian path:", graph.findHamiltonianPath());
    console.log("Hamiltonian cycle:", graph.findHamiltonianCycle());
}

function runTests() {
    const square = new UndirectedGraph(
        ["A", "B", "C", "D"],
        [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]
    );

    console.assert(square.hasEulerCircuit());
    console.assert(verifyEulerTrail(square, square.eulerTrail()));
    console.assert(square.isHamiltonianCycle(square.findHamiltonianCycle()));

    const tail = new UndirectedGraph(
        ["A", "B", "C", "D"],
        [["A", "B"], ["B", "C"], ["C", "A"], ["C", "D"]]
    );

    console.assert(tail.hasEulerTrail());
    console.assert(!tail.hasEulerCircuit());
    console.assert(tail.findHamiltonianPath() !== null);
    console.assert(tail.findHamiltonianCycle() === null);

    const disconnected = new UndirectedGraph(
        ["A", "B", "C", "D"],
        [["A", "B"], ["C", "D"]]
    );
    console.assert(!disconnected.hasEulerTrail());

    let rejected = false;
    try {
        new UndirectedGraph(["A", "B"], [["A", "B"], ["B", "A"]]);
    } catch {
        rejected = true;
    }
    console.assert(rejected);

    console.log("Graph tests completed.");
}

function main() {
    runTests();

    reportGraph(
        "Square: Euler circuit and Hamiltonian cycle",
        new UndirectedGraph(
            ["A", "B", "C", "D"],
            [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]
        )
    );

    reportGraph(
        "Complete graph K4",
        new UndirectedGraph(
            ["A", "B", "C", "D"],
            [
                ["A", "B"], ["A", "C"], ["A", "D"],
                ["B", "C"], ["B", "D"], ["C", "D"]
            ]
        )
    );
}

main();
